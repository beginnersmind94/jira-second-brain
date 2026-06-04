"""End-to-end smoke test: Generator → (optional) Evaluator.

Examples:
    # Default — happy path, micro-guide, good transcript
    python smoke_test.py

    # Stress test — bad transcript designed to trigger Evaluator FAIL
    python smoke_test.py --transcript data/sample-eligibility-stress-test-bad.md

    # Skip the Evaluator pass
    python smoke_test.py --no-eval
"""
import argparse
import asyncio
import json
import re
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
from claude_agent_sdk import (
    AssistantMessage,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ThinkingBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
    query,
)

load_dotenv()

from agent_sdk import build_options, build_user_prompt
from evaluator_sdk import build_evaluator_options, build_evaluator_prompt


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--transcript", default="data/sample-eligibility-income-survey-training.md",
                   help="path to transcript (.md), relative to learning-agent/")
    p.add_argument("--module", default="Eligibility",
                   help="module name as it appears in the NXT Module field")
    p.add_argument("--template", default="micro-guide", choices=["long-form", "micro-guide", "tldr"])
    p.add_argument("--no-eval", action="store_true", help="skip the Evaluator pass")
    p.add_argument("--out", default=None, help="override output filename (default derives from transcript stem)")
    return p.parse_args()


async def run_generator(transcript_path: Path, module: str, template: str):
    print(f"=== GENERATOR ===  module={module}  template={template}")
    print(f"Transcript: {transcript_path}\n")
    t0 = time.time()
    options = build_options(template)
    prompt = build_user_prompt(str(transcript_path), module, template)

    text_parts: list[str] = []
    tool_calls: list[str] = []
    result_meta = {}

    async for message in query(prompt=prompt, options=options):
        elapsed = time.time() - t0
        if isinstance(message, SystemMessage):
            print(f"[{elapsed:6.1f}s] system/{getattr(message, 'subtype', '?')}")
        elif isinstance(message, AssistantMessage):
            for block in (message.content or []):
                if isinstance(block, ToolUseBlock):
                    name = block.name.split("__")[-1]
                    tool_calls.append(name)
                    args_preview = str(block.input)[:80]
                    print(f"[{elapsed:6.1f}s] tool_call → {name}({args_preview})")
                elif isinstance(block, TextBlock):
                    text_parts.append(block.text)
                    snippet = block.text[:80].replace("\n", " ")
                    print(f"[{elapsed:6.1f}s] text: {snippet}…")
        elif isinstance(message, UserMessage):
            for block in (message.content or []):
                if isinstance(block, ToolResultBlock):
                    content = block.content
                    if isinstance(content, list):
                        text = " ".join(c.get("text", "") if isinstance(c, dict) else str(c) for c in content)
                    else:
                        text = str(content)
                    first = text.split("\n")[0][:100]
                    tag = "ERR" if text.startswith("ERROR:") else "ok"
                    print(f"[{elapsed:6.1f}s] tool_result ({tag}): {first}")
        elif isinstance(message, ResultMessage):
            result_meta = {
                "cost_usd": getattr(message, "total_cost_usd", None),
                "num_turns": getattr(message, "num_turns", None),
                "duration_ms": getattr(message, "duration_ms", None),
            }
            print(f"[{elapsed:6.1f}s] RESULT: {result_meta}")

    raw_html = "\n".join(text_parts).strip()
    fence = re.search(r"```(?:html)?\s*([\s\S]*?)```", raw_html)
    if fence:
        raw_html = fence.group(1).strip()
    h_match = re.search(r"<h[1-2]\b", raw_html, flags=re.I)
    if h_match:
        cleaned_html = raw_html[h_match.start():].strip()
    else:
        cleaned_html = raw_html

    return raw_html, cleaned_html, tool_calls, result_meta, time.time() - t0


async def run_evaluator(draft_html: str, transcript_text: str, module: str, template: str):
    print(f"\n=== EVALUATOR ===")
    t0 = time.time()
    options = build_evaluator_options()
    prompt = build_evaluator_prompt(draft_html, transcript_text, template, module)
    prompt += "\n\n=== RAW DRAFT WITH SOURCE COMMENTS ===\n" + draft_html[:20000]

    text_parts: list[str] = []
    tool_calls: list[str] = []
    result_meta = {}

    async for message in query(prompt=prompt, options=options):
        elapsed = time.time() - t0
        if isinstance(message, SystemMessage):
            print(f"[{elapsed:6.1f}s] eval/system/{getattr(message, 'subtype', '?')}")
        elif isinstance(message, AssistantMessage):
            for block in (message.content or []):
                if isinstance(block, ToolUseBlock):
                    name = block.name.split("__")[-1]
                    tool_calls.append(name)
                    print(f"[{elapsed:6.1f}s] eval tool_call → {name}({str(block.input)[:80]})")
                elif isinstance(block, TextBlock):
                    text_parts.append(block.text)
        elif isinstance(message, UserMessage):
            for block in (message.content or []):
                if isinstance(block, ToolResultBlock):
                    content = block.content
                    if isinstance(content, list):
                        text = " ".join(c.get("text", "") if isinstance(c, dict) else str(c) for c in content)
                    else:
                        text = str(content)
                    print(f"[{elapsed:6.1f}s] eval tool_result: {text.split(chr(10))[0][:100]}")
        elif isinstance(message, ResultMessage):
            result_meta = {
                "cost_usd": getattr(message, "total_cost_usd", None),
                "num_turns": getattr(message, "num_turns", None),
            }
            print(f"[{elapsed:6.1f}s] eval RESULT: {result_meta}")

    raw = "\n".join(text_parts).strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
    if fence:
        raw = fence.group(1).strip()
    start, end = raw.find("{"), raw.rfind("}")
    eval_data = None
    if start >= 0 and end > start:
        try:
            eval_data = json.loads(raw[start:end + 1])
        except json.JSONDecodeError:
            pass

    return eval_data, raw, tool_calls, result_meta, time.time() - t0


async def main():
    args = parse_args()
    transcript_path = (Path(__file__).parent / args.transcript).resolve()
    if not transcript_path.exists():
        print(f"ERROR: transcript not found: {transcript_path}")
        sys.exit(1)

    stem = args.out or transcript_path.stem
    out_html = Path(__file__).parent / f"smoke_{stem}.html"
    out_eval = Path(__file__).parent / f"smoke_{stem}.eval.json"

    try:
        raw_html, cleaned_html, tool_calls, gen_meta, gen_secs = await run_generator(
            transcript_path, args.module, args.template
        )
    except Exception as e:
        print(f"\n!!! Generator FAILED: {e!r}")
        sys.exit(1)

    if not cleaned_html:
        print("\nFAILED: no HTML produced by Generator")
        sys.exit(1)

    out_html.write_text(cleaned_html, encoding="utf-8")
    print(f"\nDraft written to: {out_html}")
    print(f"  raw_html chars: {len(raw_html)}  cleaned_html chars: {len(cleaned_html)}")

    if args.no_eval:
        print(f"\n✓ Generator OK ({gen_secs:.1f}s). Skipping Evaluator.")
        return

    transcript_text = transcript_path.read_text(encoding="utf-8")
    try:
        eval_data, raw_eval, eval_tool_calls, eval_meta, eval_secs = await run_evaluator(
            cleaned_html, transcript_text, args.module, args.template
        )
    except Exception as e:
        print(f"\n!!! Evaluator FAILED: {e!r}")
        sys.exit(1)

    if eval_data is None:
        eval_data = {
            "verdict": "error",
            "summary": "Could not parse Evaluator output as JSON.",
            "raw_excerpt": raw_eval[:600],
        }

    out_eval.write_text(json.dumps(eval_data, indent=2), encoding="utf-8")
    print(f"\nEvaluation written to: {out_eval}")

    verdict = (eval_data.get("verdict") or "").lower()
    print(f"\n{'=' * 60}")
    print(f"FINAL VERDICT: {verdict.upper()}")
    print(f"  {eval_data.get('summary', '')}")
    if "word_count" in eval_data:
        print(f"  estimated word count: {eval_data['word_count']}")
    print(f"  generator: {gen_secs:.1f}s · evaluator: {eval_secs:.1f}s · total: {gen_secs + eval_secs:.1f}s")
    print(f"  cost: gen ${gen_meta.get('cost_usd', 0):.4f} + eval ${eval_meta.get('cost_usd', 0):.4f}")
    print(f"{'=' * 60}")
    for check in (eval_data.get("checks") or []):
        mark = "✓" if check.get("status") == "ok" else "⚠" if check.get("status") == "warn" else "✗"
        print(f"  {mark} {check.get('name'):28s} {check.get('detail', '')[:80]}")


if __name__ == "__main__":
    asyncio.run(main())
