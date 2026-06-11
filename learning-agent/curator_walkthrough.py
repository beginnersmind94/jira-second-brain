"""Throwaway, hardcoded curator walkthrough — the customer-obsession probe (commit 1, parallel).

Answers the only question that decides whether the bank beats a Word doc:
  cold start → a 10-question, source-cited "cooling food" quiz, exported to PDF + QTI,
  in UNDER 15 MINUTES?

This is deliberately hardcoded (one topic, compliance lane) and disposable. It exercises
the real path: cross-asset chunk pull → generate → THREE-CHECK GATE (lane+verbatim+support)
→ cull → export-with-citation. Not production code; a stopwatch.

Run:  python curator_walkthrough.py
"""
import asyncio
import json
import re
import sys
import time
import xml.sax.saxutils as sx
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import qbank_gate
from qbank_gate import gate_question, llm_support_judge, _norm

BASE = Path(__file__).parent
CHUNKS = BASE / "data" / "icn" / "chunks" / "chunks.jsonl"
OUT = BASE / "drafts" / "qbank_walkthrough"
TOPIC = "food_safety"           # chunk topic tag (hardcoded for the probe)
TOPIC_LABEL = "Food Safety"     # display name
LANE = "compliance"
TARGET_QUESTIONS = 10
TARGET_MINUTES = 15

_GEN_SYS = (
    "You write multiple-choice quiz questions for school-nutrition staff, grounded ONLY in "
    "provided source excerpts. Each question: a clear stem, EXACTLY 4 options, one correct. "
    "For each you MUST include 'source_quote' (a short verbatim span copied EXACTLY from one "
    "excerpt that proves the correct answer) and 'chunk_id' (the excerpt it came from). Never "
    "use outside knowledge. OUTPUT ONLY this JSON: "
    '{"questions":[{"q":"...","options":["..","..","..",".."],"answer":0,'
    '"source_quote":"...","chunk_id":"..."}]}'
)


def _parse_json(text):
    m = re.search(r"\{[\s\S]*\}", text or "")
    if not m:
        return {}
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return {}


async def _generate(excerpts_text, n):
    from claude_agent_sdk import ClaudeAgentOptions, query, AssistantMessage, TextBlock
    opts = ClaudeAgentOptions(model="claude-sonnet-4-6", system_prompt=_GEN_SYS,
                              allowed_tools=[], disallowed_tools=[], tools=[], max_turns=2)
    prompt = (f"Write {n} questions on '{TOPIC_LABEL}', grounded ONLY in these excerpts.\n\n"
              f"EXCERPTS:\n{excerpts_text}\n\nEmit ONLY the JSON.")
    parts = []
    async for m in query(prompt=prompt, options=opts):
        if isinstance(m, AssistantMessage):
            for b in m.content:
                if isinstance(b, TextBlock):
                    parts.append(b.text)
    return _parse_json("\n".join(parts)).get("questions", [])


def _load_topic_chunks(topic):
    """Cross-asset pull: every chunk tagged with the topic, across all assets."""
    chunks, assets = [], set()
    for line in CHUNKS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        c = json.loads(line)
        topics = c.get("topics") or []
        if isinstance(topics, str):
            topics = [topics]
        if any(topic.lower() in str(t).lower() for t in topics) and len((c.get("text") or "")) >= 60:
            chunks.append(c)
            assets.add(c.get("asset_id"))
    return chunks, assets


def _qti(quiz):
    """Minimal QTI-ish XML — proves the citation RIDES the export to the LMS."""
    items = []
    for i, q in enumerate(quiz, 1):
        choices = "".join(
            f'<simpleChoice identifier="c{j}">{sx.escape(o)}</simpleChoice>'
            for j, o in enumerate(q["options"]))
        cite = (f'{sx.escape(q["source_quote"])} — Source: {sx.escape(q.get("source_label","ICN/USDA"))}'
                f', {sx.escape(str(q.get("locator","")))}')
        items.append(
            f'<assessmentItem identifier="q{i}" title="{sx.escape(TOPIC)} Q{i}">'
            f'<responseDeclaration identifier="RESPONSE" cardinality="single" baseType="identifier">'
            f'<correctResponse><value>c{q["answer"]}</value></correctResponse></responseDeclaration>'
            f'<itemBody><choiceInteraction responseIdentifier="RESPONSE" maxChoices="1">'
            f'<prompt>{sx.escape(q["q"])}</prompt>{choices}</choiceInteraction></itemBody>'
            f'<rubricBlock view="author"><p>{cite}</p></rubricBlock></assessmentItem>')
    return '<?xml version="1.0" encoding="UTF-8"?>\n<assessmentTest>' + "".join(items) + "</assessmentTest>"


def _html(quiz):
    rows = []
    for i, q in enumerate(quiz, 1):
        opts = "".join(f"<li{' style=font-weight:700' if j==q['answer'] else ''}>{sx.escape(o)}</li>"
                       for j, o in enumerate(q["options"]))
        rows.append(
            f"<h3>{i}. {sx.escape(q['q'])}</h3><ol type='A'>{opts}</ol>"
            f"<p style='font-size:12px;color:#555'><em>“{sx.escape(q['source_quote'])}”</em><br>"
            f"Source: {sx.escape(q.get('source_label','ICN / USDA'))}, {sx.escape(str(q.get('locator','')))}</p>")
    return f"<h1>{TOPIC_LABEL}: Staff Quiz</h1>" + "".join(rows)


async def main():
    t0 = time.monotonic()
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"[0:00] COLD START — building a {TARGET_QUESTIONS}-question '{TOPIC_LABEL}' quiz…")

    chunks, assets = _load_topic_chunks(TOPIC)
    print(f"[{_t(t0)}] pulled {len(chunks)} chunks across {len(assets)} assets (cross-asset).")
    if not chunks:
        print("no chunks for topic — abort"); return 1

    by_cid, excerpts, total = {}, [], 0
    for c in chunks:
        by_cid[c["chunk_id"]] = c
        excerpts.append(f"[{c['chunk_id']}] {c['text'].strip()}")
        total += len(c["text"])
        if total > 16000:
            break

    raw = await _generate("\n\n".join(excerpts), TARGET_QUESTIONS + 3)  # over-generate; gate culls
    print(f"[{_t(t0)}] generated {len(raw)} draft questions; running 3-check gate…")

    spans = {f"{LANE}:{cid}": {"span_id": f"{LANE}:{cid}", "lane": LANE, "text": by_cid[cid]["text"]}
             for cid in by_cid}
    kept = []
    for q in raw:
        cid = q.get("chunk_id")
        src = by_cid.get(cid)
        if not src:
            continue
        qd = {"lane": LANE, "stem": q.get("q", ""), "options": q.get("options", []),
              "correct_index": q.get("answer", 0), "cite_span_id": f"{LANE}:{cid}",
              "quote": q.get("source_quote", "")}
        v = await gate_question(qd, spans, judge=llm_support_judge)
        if v["verdict"] == "pass":
            q["source_label"] = src.get("source_org", "ICN / USDA")
            q["locator"] = f"p.{src['page']}" if src.get("page") else (src.get("source_url") or "")
            kept.append(q)
        if len(kept) >= TARGET_QUESTIONS:
            break
    print(f"[{_t(t0)}] gate kept {len(kept)}/{len(raw)} (rejected {len(raw)-len(kept)} cross-lane/non-verbatim/unsupported).")

    (OUT / "quiz.html").write_text(_html(kept), encoding="utf-8")
    (OUT / "quiz.qti.xml").write_text(_qti(kept), encoding="utf-8")
    pdf_ok = "—"
    try:
        import pdf_export
        (OUT / "quiz.pdf").write_bytes(pdf_export.render_html_to_pdf(_html(kept)))
        pdf_ok = str(OUT / "quiz.pdf")
    except Exception as e:
        pdf_ok = f"(pdf skipped: {e})"

    mins = (time.monotonic() - t0) / 60
    print(f"\n[{_t(t0)}] EXPORTED → {OUT}")
    print(f"   • quiz.html  • quiz.qti.xml (citation rides each item's rubricBlock)  • {pdf_ok}")
    print(f"\nCOLD-START → EXPORT: {mins:.1f} min  (target < {TARGET_MINUTES} min) — "
          f"{'✅ BEATS the Word doc' if mins < TARGET_MINUTES else '❌ too slow'}")
    return 0


def _t(t0):
    s = int(time.monotonic() - t0)
    return f"{s//60}:{s%60:02d}"


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
