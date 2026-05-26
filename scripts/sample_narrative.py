"""Generate a 20-ticket narrative sample for the highest-volume component.

Reads the cleaned outputs and writes a markdown sample to verify text quality
before clustering work begins. Per spec: if it reads well, the cleaning is done;
if it reads thin or generic, revisit Step 4.
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path

import pandas as pd


def excerpt(text: str, n: int = 280) -> str:
    if not isinstance(text, str):
        return ""
    s = text.strip()
    if len(s) <= n:
        return s
    cut = s[:n]
    last_period = cut.rfind(". ")
    if last_period >= n // 2:
        return cut[: last_period + 1]
    last_space = cut.rfind(" ")
    if last_space >= n // 2:
        return cut[:last_space] + "…"
    return cut + "…"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cleaned-dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--n", type=int, default=20)
    parser.add_argument("--component", default=None,
                        help="Override component (default: top by pain_page_candidate count)")
    args = parser.parse_args()

    tickets = pd.read_csv(args.cleaned_dir / "tickets_clean.csv", low_memory=False)
    flags = pd.read_csv(args.cleaned_dir / "candidate_artifact_flags.csv")

    df = tickets.merge(flags, on="issue_key", how="left")
    pain = df[df["pain_page_candidate"]].copy()

    if args.component:
        component = args.component
    else:
        # Skip the catch-all top-level "Item Management" component — on this corpus
        # it covers ~91% of analytic tickets and isn't a meaningful sub-module.
        # Default to the largest sub-module-shaped component instead.
        catch_all = {"Item Management"}
        ranked = pain["component_primary"].value_counts()
        candidates = [c for c in ranked.index if c not in catch_all]
        component = candidates[0] if candidates else ranked.idxmax()
    print(f"sample component: {component}", flush=True)

    sub = pain[pain["component_primary"] == component].copy()
    print(f"pain_page_candidates in {component}: {len(sub)}", flush=True)

    # Stratify a little: take a mix of resolved + open + linger to surface variety
    random.seed(7)
    pieces = []
    for bucket_label, bucket in [
        ("linger", sub[sub["linger_candidate"]]),
        ("rejected/duplicate", sub[sub["dismissal_candidate"]]),
        ("resolved", sub[sub["lifecycle"] == "resolved"]),
        ("done_no_timestamp", sub[sub["lifecycle"] == "done_no_timestamp"]),
        ("open/in_progress", sub[sub["lifecycle"].isin(["open", "in_progress"])]),
    ]:
        if not len(bucket):
            continue
        take = min(4, len(bucket))
        sample = bucket.sample(n=take, random_state=7)
        sample["__bucket"] = bucket_label
        pieces.append(sample)

    chosen = pd.concat(pieces).drop_duplicates("issue_key").head(args.n)
    if len(chosen) < args.n:
        # top up randomly
        extra = sub[~sub["issue_key"].isin(chosen["issue_key"])].sample(
            n=min(args.n - len(chosen), len(sub) - len(chosen)), random_state=7
        )
        extra["__bucket"] = "filler"
        chosen = pd.concat([chosen, extra]).head(args.n)

    out_lines: list[str] = []
    out_lines.append(f"# Sample narrative — component `{component}`")
    out_lines.append("")
    out_lines.append(f"_Drawn from `pain_page_candidate` rows in this component "
                     f"(total={len(sub)}). Sample size = {len(chosen)}._")
    out_lines.append("")
    out_lines.append("Use this to judge whether `text_blob` carries enough "
                     "narrative signal to support pain pages without revisiting Step 4.")
    out_lines.append("")

    for i, (_, row) in enumerate(chosen.iterrows(), start=1):
        out_lines.append(f"## {i}. `{row['issue_key']}` — {row['summary']}")
        out_lines.append("")
        out_lines.append(
            f"- **type:** {row['issue_type']}  ·  **lifecycle:** {row['lifecycle']}  "
            f"·  **closure_confidence:** {row['closure_confidence']}  "
            f"·  **bucket:** {row.get('__bucket', '')}"
        )
        if pd.notna(row.get("priority")):
            out_lines.append(f"- **priority:** {row['priority']}")
        if pd.notna(row.get("duration_resolved_days")):
            out_lines.append(
                f"- **resolved in:** {row['duration_resolved_days']:.1f} days"
                + (f"  (P90 threshold = {row['linger_threshold_for_type']:.1f})"
                   if pd.notna(row.get("linger_threshold_for_type")) else "")
            )
        if pd.notna(row.get("unresolved_age_days")):
            out_lines.append(f"- **open for:** {row['unresolved_age_days']:.0f} days")
        if pd.notna(row.get("description")) and str(row["description"]).strip():
            out_lines.append("")
            out_lines.append("> " + excerpt(str(row["description"])).replace("\n", "\n> "))
        elif pd.notna(row.get("text_blob_full_evidence")):
            out_lines.append("")
            out_lines.append("> " + excerpt(str(row["text_blob_full_evidence"])).replace("\n", "\n> "))
        out_lines.append("")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(out_lines), encoding="utf-8")
    print(f"wrote {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
