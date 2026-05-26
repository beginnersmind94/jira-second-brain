"""Append a JSON batch buffer to ticket_categories_raw.csv and report distribution.

Usage:
  python stage2_append_batch.py --buffer <path> --csv <path> [--label "batch N"]
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--buffer", required=True, type=Path)
    ap.add_argument("--csv", required=True, type=Path)
    ap.add_argument("--label", default="batch")
    args = ap.parse_args()

    records = json.loads(args.buffer.read_text(encoding="utf-8"))
    fieldnames = ["issue_key", "primary_category", "secondary_category",
                  "confidence", "other_reason", "cs_source"]

    with args.csv.open("a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        for r in records:
            w.writerow({k: r.get(k, "") for k in fieldnames})

    cats = Counter(r["primary_category"] for r in records)
    confs = Counter(r["confidence"] for r in records)
    pcs_n = sum(1 for r in records if r["issue_key"].startswith("PCS-"))
    cs_dist = Counter(r["cs_source"] or "(null)" for r in records if r["issue_key"].startswith("PCS-"))
    others = [r for r in records if r["primary_category"] == "Other"]
    lows = [r for r in records if r["confidence"] == "low"]

    print(f"=== {args.label}: wrote {len(records)} records to {args.csv.name} ===")
    print()
    print("Primary category distribution:")
    for cat, n in cats.most_common():
        print(f"  {n:>3}  {cat}")
    print()
    print(f"Confidence: high={confs.get('high',0)} medium={confs.get('medium',0)} low={confs.get('low',0)}")
    print(f"Other rate: {cats.get('Other',0)/len(records):.1%}")
    print(f"PCS-* in batch: {pcs_n}")
    if pcs_n:
        print("cs_source distribution within PCS-*:")
        for k, v in cs_dist.most_common():
            print(f"  {v:>3}  {k}")

    if others:
        print()
        print("Other tickets:")
        for r in others:
            print(f"  - {r['issue_key']}: {r.get('other_reason') or '(no reason)'}")

    if lows:
        print()
        print(f"Low-confidence tickets ({len(lows)}):")
        for r in lows:
            print(f"  - {r['issue_key']} -> {r['primary_category']}"
                  + (f" ({r.get('other_reason') or ''})" if r.get('other_reason') else ""))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
