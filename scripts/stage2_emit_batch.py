"""Emit a single batch of in-scope tickets in compact form for inline tagging.

Usage:
  python stage2_emit_batch.py --stage2-dir <dir> --batch N --batch-size 50

Prints to stdout. The order is deterministic — sorted by issue_key — so resume
and ad-hoc batch re-runs land on the same tickets.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def trim(s, n: int) -> str:
    if not isinstance(s, str):
        return ""
    s = s.replace("\n", " ").strip()
    if len(s) <= n:
        return s
    return s[: n - 1].rstrip() + "…"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage2-dir", required=True, type=Path)
    ap.add_argument("--batch", type=int, required=True, help="1-indexed batch number")
    ap.add_argument("--batch-size", type=int, default=50)
    args = ap.parse_args()

    tickets = pd.read_csv(args.stage2_dir / "tickets_in_scope.csv", low_memory=False)
    enrich = pd.read_csv(args.stage2_dir / "epic_enrichment.csv")
    df = tickets.merge(
        enrich[["issue_key", "associated_epic_name"]], on="issue_key", how="left"
    )
    df = df.sort_values("issue_key", kind="stable").reset_index(drop=True)
    n_total = len(df)
    n_batches = (n_total + args.batch_size - 1) // args.batch_size

    if args.batch < 1 or args.batch > n_batches:
        print(f"ERROR: batch {args.batch} out of range (1..{n_batches})")
        return 1

    start = (args.batch - 1) * args.batch_size
    end = min(start + args.batch_size, n_total)
    batch = df.iloc[start:end]

    print(f"# Batch {args.batch}/{n_batches}  (rows {start+1}-{end} of {n_total})")
    print(f"# Issue keys in this batch: {len(batch)}")
    print()

    for _, r in batch.iterrows():
        ek = r["issue_key"]
        ity = r["issue_type"]
        ep = r.get("associated_epic_name")
        if not isinstance(ep, str) or not ep:
            ep = "(none)"
        title = trim(r.get("summary"), 220)
        desc = trim(r.get("description"), 600)
        ac = trim(r.get("acceptance_criteria"), 300)
        is_pcs = "PCS" if str(ek).startswith("PCS-") else ""

        print(f"[{ek}] [{ity}] [{is_pcs}] [Epic: {ep}]")
        print(f"  TITLE: {title}")
        if desc:
            print(f"  DESC:  {desc}")
        if ac:
            print(f"  AC:    {ac}")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
