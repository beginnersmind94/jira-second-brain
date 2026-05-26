"""Stage 2 / Workstream 1.1 sampling — produce 200 stratified tickets for category proposal.

Stratification:
  - ~60% Bugs / ~40% Stories
  - prefer pain_page_candidate==True where applicable
  - spread across at least 4 distinct sprint_latest values

Output: sample_for_categories.json
  list of records with: issue_key, issue_type, summary, description,
  acceptance_criteria, sprint_latest, associated_epic_name,
  pain_page_candidate
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import pandas as pd


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cleaned-dir", required=True, type=Path)
    parser.add_argument("--stage2-dir", required=True, type=Path)
    parser.add_argument("--n", type=int, default=200)
    parser.add_argument("--seed", type=int, default=11)
    args = parser.parse_args()

    tickets = pd.read_csv(args.cleaned_dir / "tickets_clean.csv", low_memory=False)
    flags = pd.read_csv(args.cleaned_dir / "candidate_artifact_flags.csv")
    enrich = pd.read_csv(args.stage2_dir / "epic_enrichment.csv")

    df = (
        tickets.merge(flags[["issue_key", "pain_page_candidate"]], on="issue_key", how="left")
               .merge(enrich[["issue_key", "associated_epic_name"]], on="issue_key", how="left")
    )
    df = df[df["issue_type"].isin({"Bug", "Story"})].copy()
    print(f"in-scope: {len(df)}", flush=True)

    n_bugs_target = int(round(args.n * 0.60))
    n_stories_target = args.n - n_bugs_target

    def stratified_sample(sub: pd.DataFrame, k: int, seed: int) -> pd.DataFrame:
        # Bucket by sprint_latest to ensure ≥4 distinct sprints when possible.
        sub = sub.copy()
        sub["__sprint_bucket"] = sub["sprint_latest"].fillna("(no sprint)")
        sprints = sub["__sprint_bucket"].value_counts()
        # Try to lift pain candidates first
        candidate_mask = sub["pain_page_candidate"].fillna(False).astype(bool)
        # 70% of the slot from pain candidates if available
        n_pain = min(int(round(k * 0.70)), int(candidate_mask.sum()))
        n_other = k - n_pain
        rng = random.Random(seed)

        def take_balanced_across_sprints(pool: pd.DataFrame, want: int) -> pd.DataFrame:
            if pool.empty or want <= 0:
                return pool.iloc[0:0]
            buckets = pool.groupby("__sprint_bucket", group_keys=False)
            # Round-robin across buckets so we span sprints
            per_bucket: dict[str, list[int]] = {}
            for name, grp in buckets:
                per_bucket[name] = grp.index.tolist()
                rng.shuffle(per_bucket[name])
            chosen: list[int] = []
            order = list(per_bucket.keys())
            rng.shuffle(order)
            i = 0
            while len(chosen) < want and any(per_bucket.values()):
                key = order[i % len(order)]
                if per_bucket[key]:
                    chosen.append(per_bucket[key].pop())
                i += 1
                if i > 20000:
                    break
            return pool.loc[chosen[:want]]

        pain_sample = take_balanced_across_sprints(sub[candidate_mask], n_pain)
        other_sample = take_balanced_across_sprints(
            sub[~candidate_mask & ~sub.index.isin(pain_sample.index)], n_other
        )
        out = pd.concat([pain_sample, other_sample])
        if len(out) < k:
            extra_pool = sub[~sub.index.isin(out.index)]
            out = pd.concat([out, take_balanced_across_sprints(extra_pool, k - len(out))])
        return out.head(k)

    bugs = df[df["issue_type"] == "Bug"]
    stories = df[df["issue_type"] == "Story"]
    bug_sample = stratified_sample(bugs, n_bugs_target, seed=args.seed)
    story_sample = stratified_sample(stories, n_stories_target, seed=args.seed + 1)

    sample = pd.concat([bug_sample, story_sample]).reset_index(drop=True)
    print(f"sampled: {len(sample)} (bugs={len(bug_sample)}, stories={len(story_sample)})", flush=True)
    print(f"distinct sprint_latest values represented: "
          f"{sample['sprint_latest'].nunique(dropna=False)}", flush=True)

    records = []
    for _, row in sample.iterrows():
        records.append({
            "issue_key": row["issue_key"],
            "issue_type": row["issue_type"],
            "summary": row.get("summary") or "",
            "description": row.get("description") if pd.notna(row.get("description")) else "",
            "acceptance_criteria": row.get("acceptance_criteria") if pd.notna(row.get("acceptance_criteria")) else "",
            "sprint_latest": row.get("sprint_latest") if pd.notna(row.get("sprint_latest")) else None,
            "associated_epic_name": row.get("associated_epic_name") if pd.notna(row.get("associated_epic_name")) else None,
            "pain_page_candidate": bool(row.get("pain_page_candidate", False)),
        })

    out_path = args.stage2_dir / "sample_for_categories.json"
    out_path.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {out_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
