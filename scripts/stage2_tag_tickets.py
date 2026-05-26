"""Stage 2 / Workstream 1.3 — top-down tagging of all in-scope tickets.

Reads tickets_in_scope.csv + epic_enrichment.csv from --stage2-dir and the curated
category definitions from curated_categories.md. For every ticket, produces a
JSON record with:
  primary_category, secondary_category, confidence, other_reason, cs_source

Mechanical fields (customer_reported_via_cs, touches_other_modules,
other_modules_list) are computed in the host script — not from the LLM.

Uses prompt caching so the curated-categories system message is billed once per
batch series. Batches of 25 tickets per call (so each request fits well under
output-size limits and a single batch failure rerun is cheap).

Usage:
  ANTHROPIC_API_KEY=sk-ant-... python stage2_tag_tickets.py \
    --stage2-dir <dir> \
    --out <ticket_categories.csv> \
    [--model claude-sonnet-4-6]
    [--batch-size 25]
    [--limit N]               # for dry runs
    [--resume]                # resume from existing output
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

try:
    import anthropic
except ImportError as e:
    print("ERROR: 'anthropic' package not installed. pip install anthropic", file=sys.stderr)
    raise SystemExit(1) from e


VALID_CATEGORIES = {
    "Item Onboarding — Wizard",
    "Item Onboarding — Bulk Tools",
    "Recipe Authoring",
    "Menu Items, VMI & POS Configuration",
    "Nutrients, Contributions & Allergens",
    "Units, Pack Sizes & Serving Measures",
    "List Pages, Search, Filters & Navigation",
    "UI/UX Polish, Copy & Visual Defects",
    "Reports & Data Exports",
    "Inventory Sync & Publishing",
    "Configuration",
    "USDA & Regulatory Updates",
    "Other",
}
VALID_CONFIDENCE = {"high", "medium", "low"}
VALID_CS_SOURCE = {"implementation", "live_customer", "unclear", None}


def build_system_prompt(curated_md: str) -> str:
    """System prompt: curated category definitions + tagging rules. Cached."""
    return (
        "You are a categorization analyst tagging Jira tickets from the Item Management "
        "module of a child-nutrition software product. Tickets are Bugs (unintended issues) "
        "and Stories (planned work) drawn from a single curated working corpus.\n\n"
        "You will be given batches of tickets. For each, you assign one primary problem-space "
        "category from a fixed list of 12, optionally a secondary category, a confidence level, "
        "and (for tickets whose issue_key starts with 'PCS-') a cs_source label.\n\n"
        "RULES:\n"
        "1. Categories describe the problem space, not the work type. A 500-error bug on the "
        "Bulk Item tool is 'Item Onboarding — Bulk Tools', not 'API Errors'. A regression bug "
        "in the Recipe page is 'Recipe Authoring', not 'Regressions'.\n"
        "2. There is no 'Migration' category. PCS-* tickets are tagged by problem space, with "
        "their provenance captured separately via cs_source.\n"
        "3. Use 'Other' sparingly — only when no category fits. Provide other_reason when so.\n"
        "4. Confidence: 'high' if the ticket is clearly in one category, 'medium' if it spans "
        "two and you're picking the dominant one, 'low' if you're guessing from sparse text.\n"
        "5. cs_source applies ONLY when issue_key starts with 'PCS-'. Otherwise return null.\n"
        "   - 'SC Implementation' or 'District X - <implementation issue>' in title → implementation\n"
        "   - References to production use, live customers, post-go-live → live_customer\n"
        "   - Otherwise → unclear\n\n"
        "OUTPUT FORMAT: JSON array, one record per ticket, in the same order as input. "
        "Each record: {\"issue_key\": str, \"primary_category\": str, "
        "\"secondary_category\": str|null, \"confidence\": \"high\"|\"medium\"|\"low\", "
        "\"other_reason\": str|null, \"cs_source\": \"implementation\"|\"live_customer\"|\"unclear\"|null}\n"
        "Return ONLY the JSON array, nothing else. No prose, no code fences.\n\n"
        "=== CURATED CATEGORY DEFINITIONS ===\n\n"
        f"{curated_md}\n"
    )


def trim(text: str, n: int) -> str:
    if not isinstance(text, str):
        return ""
    text = text.replace("\n", " ").strip()
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def render_batch(rows: list[dict]) -> str:
    out = ["Tag the following batch of tickets. Return JSON array of records, "
           "one per ticket, in the same order as listed.\n"]
    for r in rows:
        out.append(f"---\nISSUE_KEY: {r['issue_key']}")
        out.append(f"TYPE: {r['issue_type']}")
        epic = r.get("associated_epic_name") or "(none)"
        out.append(f"EPIC: {epic}")
        out.append(f"TITLE: {trim(r.get('summary'), 220)}")
        desc = trim(r.get("description"), 600)
        if desc:
            out.append(f"DESCRIPTION: {desc}")
        ac = trim(r.get("acceptance_criteria"), 300)
        if ac:
            out.append(f"ACCEPTANCE CRITERIA: {ac}")
    out.append("---")
    return "\n".join(out)


def parse_response(text: str, batch_keys: list[str]) -> list[dict]:
    text = text.strip()
    # Tolerate fenced or prefixed responses
    m = re.search(r"\[\s*\{.*\}\s*\]", text, re.DOTALL)
    if m:
        text = m.group(0)
    try:
        records = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"could not parse JSON: {e}\n--- response was ---\n{text[:1500]}") from e
    if not isinstance(records, list):
        raise ValueError(f"expected a list, got {type(records).__name__}")
    if len(records) != len(batch_keys):
        raise ValueError(f"expected {len(batch_keys)} records, got {len(records)}")
    cleaned = []
    for rec, key in zip(records, batch_keys):
        if rec.get("issue_key") != key:
            # Best effort: trust positional alignment but log mismatch
            rec["issue_key"] = key
        pc = rec.get("primary_category")
        if pc not in VALID_CATEGORIES:
            rec["primary_category"] = "Other"
            rec["other_reason"] = f"invalid_category={pc!r}; " + (rec.get("other_reason") or "")
        sc = rec.get("secondary_category")
        if sc is not None and sc not in VALID_CATEGORIES:
            rec["secondary_category"] = None
        conf = rec.get("confidence")
        if conf not in VALID_CONFIDENCE:
            rec["confidence"] = "low"
        cs = rec.get("cs_source")
        if cs not in VALID_CS_SOURCE:
            rec["cs_source"] = None
        cleaned.append(rec)
    return cleaned


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage2-dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--curated", default=None, type=Path,
                        help="Path to curated_categories.md (defaults to stage2-dir/curated_categories.md)")
    parser.add_argument("--model", default="claude-sonnet-4-6")
    parser.add_argument("--batch-size", type=int, default=25)
    parser.add_argument("--limit", type=int, default=None,
                        help="Tag only the first N tickets (for dry runs).")
    parser.add_argument("--resume", action="store_true",
                        help="Skip tickets already present in --out.")
    parser.add_argument("--max-output-tokens", type=int, default=4096)
    parser.add_argument("--retry", type=int, default=2)
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set in environment.", file=sys.stderr)
        return 1

    curated_path = args.curated or (args.stage2_dir / "curated_categories.md")
    curated_md = curated_path.read_text(encoding="utf-8")
    print(f"[load] curated definitions: {curated_path} ({len(curated_md):,} chars)", flush=True)

    tickets = pd.read_csv(args.stage2_dir / "tickets_in_scope.csv", low_memory=False)
    enrich = pd.read_csv(args.stage2_dir / "epic_enrichment.csv")
    df = tickets.merge(enrich[["issue_key", "associated_epic_name"]], on="issue_key", how="left")
    if args.limit:
        df = df.head(args.limit)
    print(f"[load] {len(df):,} tickets to tag", flush=True)

    # Resume support
    already_tagged: set[str] = set()
    if args.resume and args.out.exists():
        existing = pd.read_csv(args.out)
        already_tagged = set(existing["issue_key"].tolist())
        print(f"[resume] {len(already_tagged):,} tickets already tagged in {args.out}", flush=True)
    pending = df[~df["issue_key"].isin(already_tagged)].reset_index(drop=True)
    print(f"[plan] tagging {len(pending):,} tickets in batches of {args.batch_size}", flush=True)

    if len(pending) == 0:
        print("[plan] nothing to do", flush=True)
        return 0

    client = anthropic.Anthropic()
    system_prompt = build_system_prompt(curated_md)

    out_path = args.out
    write_header = not (args.resume and out_path.exists() and out_path.stat().st_size > 0)
    out_f = out_path.open("a", encoding="utf-8", newline="")
    writer = csv.DictWriter(out_f, fieldnames=[
        "issue_key", "primary_category", "secondary_category",
        "confidence", "other_reason", "cs_source",
    ])
    if write_header:
        writer.writeheader()

    total_in = 0
    total_out = 0
    total_cache_read = 0
    total_cache_create = 0
    n_batches = (len(pending) + args.batch_size - 1) // args.batch_size
    t0 = time.time()

    for i in range(0, len(pending), args.batch_size):
        batch_idx = i // args.batch_size + 1
        chunk = pending.iloc[i: i + args.batch_size]
        rows = chunk.to_dict("records")
        keys = [r["issue_key"] for r in rows]
        user_msg = render_batch(rows)

        for attempt in range(1, args.retry + 2):
            try:
                resp = client.messages.create(
                    model=args.model,
                    max_tokens=args.max_output_tokens,
                    system=[{
                        "type": "text",
                        "text": system_prompt,
                        "cache_control": {"type": "ephemeral"},
                    }],
                    messages=[{"role": "user", "content": user_msg}],
                )
                text = "".join(block.text for block in resp.content if hasattr(block, "text"))
                records = parse_response(text, keys)
                break
            except (ValueError, anthropic.APIError) as e:
                print(f"[batch {batch_idx}/{n_batches}] attempt {attempt} failed: {e}", flush=True)
                if attempt > args.retry:
                    raise
                time.sleep(2 ** attempt)

        for rec in records:
            writer.writerow({
                "issue_key": rec["issue_key"],
                "primary_category": rec["primary_category"],
                "secondary_category": rec.get("secondary_category"),
                "confidence": rec["confidence"],
                "other_reason": rec.get("other_reason"),
                "cs_source": rec.get("cs_source"),
            })
        out_f.flush()

        u = resp.usage
        total_in += u.input_tokens
        total_out += u.output_tokens
        total_cache_read += getattr(u, "cache_read_input_tokens", 0) or 0
        total_cache_create += getattr(u, "cache_creation_input_tokens", 0) or 0

        elapsed = time.time() - t0
        rate = (i + len(rows)) / elapsed if elapsed > 0 else 0
        eta = (len(pending) - (i + len(rows))) / rate if rate > 0 else 0
        print(
            f"[batch {batch_idx}/{n_batches}] +{len(rows)} tagged "
            f"(in={u.input_tokens}, cache_read={total_cache_read - (total_cache_read - (getattr(u, 'cache_read_input_tokens', 0) or 0))}, "
            f"out={u.output_tokens})  elapsed={elapsed:.0f}s  eta={eta:.0f}s",
            flush=True,
        )

    out_f.close()

    print(f"\n[totals] input={total_in:,} cache_read={total_cache_read:,} "
          f"cache_create={total_cache_create:,} output={total_out:,}", flush=True)
    print(f"[done] {out_path}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
