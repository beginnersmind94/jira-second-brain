"""Stage 2 / Workstream 0 — Epic enrichment.

Reads the v1 cleaned dataset and produces:
  tickets_in_scope.csv
  epic_enrichment.csv
  epic_enrichment_report.md
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

RELEVANT_BUG_LINK_TYPES = {"Relates", "Blocks", "Cloners", "Caused by", "Caused"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cleaned-dir", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    print("[load] reading cleaned inputs", flush=True)
    tickets = pd.read_csv(args.cleaned_dir / "tickets_clean.csv", low_memory=False)
    links = pd.read_csv(args.cleaned_dir / "ticket_links_long.csv")
    print(f"   tickets: {tickets.shape}", flush=True)
    print(f"   links:   {links.shape}", flush=True)

    # ---- 0.1 Filter to working corpus -------------------------------------
    in_scope = tickets[tickets["issue_type"].isin({"Bug", "Story"})].copy()
    in_scope.to_csv(args.out_dir / "tickets_in_scope.csv", index=False, encoding="utf-8")
    print(f"[0.1] tickets_in_scope.csv: {in_scope.shape}", flush=True)

    # ---- 0.2 Story → Epic via parent_key ----------------------------------
    epics = tickets[tickets["issue_type"] == "Epic"][["issue_key", "summary"]]
    epic_lookup = dict(zip(epics["issue_key"], epics["summary"]))
    print(f"[0.2] Epics in corpus: {len(epics)}", flush=True)

    stories = in_scope[in_scope["issue_type"] == "Story"].copy()
    stories["associated_story_key"] = pd.NA
    stories["associated_epic_key"] = stories["parent_key"]
    stories["associated_epic_name"] = stories["parent_key"].map(epic_lookup)
    stories["epic_link_path"] = stories["associated_epic_key"].where(
        stories["associated_epic_key"].notna(), other=None
    ).map(lambda v: "direct_parent" if pd.notna(v) else "none")
    stories["linked_story_count"] = 0

    n_stories = len(stories)
    n_stories_epic_in_corpus = int(stories["associated_epic_name"].notna().sum())
    n_stories_epic_any = int(stories["associated_epic_key"].notna().sum())
    print(f"[0.2] Stories with parent_key set: {n_stories_epic_any}/{n_stories} "
          f"({n_stories_epic_any / n_stories:.1%})", flush=True)
    print(f"[0.2]   ...with parent Epic in corpus (name resolved): "
          f"{n_stories_epic_in_corpus}/{n_stories} "
          f"({n_stories_epic_in_corpus / n_stories:.1%})", flush=True)

    # ---- 0.3 Bug → Story → Epic -------------------------------------------
    bugs = in_scope[in_scope["issue_type"] == "Bug"].copy()
    story_keys = set(in_scope[in_scope["issue_type"] == "Story"]["issue_key"])

    relevant_links = links[
        links["link_type"].isin(RELEVANT_BUG_LINK_TYPES)
        & links["source_issue_key"].isin(bugs["issue_key"])
        & links["linked_issue_key"].isin(story_keys)
    ]
    bug_to_linked_stories: dict[str, list[str]] = (
        relevant_links.groupby("source_issue_key")["linked_issue_key"]
        .agg(lambda x: sorted(set(x)))
        .to_dict()
    )

    story_created = dict(
        zip(stories["issue_key"], pd.to_datetime(stories["created_at"], utc=True, errors="coerce"))
    )
    story_to_epic_key = dict(zip(stories["issue_key"], stories["associated_epic_key"]))
    story_to_epic_name = dict(zip(stories["issue_key"], stories["associated_epic_name"]))

    def pick_originating_story(bug_key: str) -> str | None:
        linked = bug_to_linked_stories.get(bug_key, [])
        if not linked:
            return None
        if len(linked) == 1:
            return linked[0]
        # Earliest-created Story wins
        return min(linked, key=lambda s: story_created.get(s, pd.Timestamp.max))

    bugs["associated_story_key"] = bugs["issue_key"].map(pick_originating_story)
    bugs["associated_epic_key"] = bugs["associated_story_key"].map(story_to_epic_key)
    bugs["associated_epic_name"] = bugs["associated_story_key"].map(story_to_epic_name)
    bugs["linked_story_count"] = bugs["issue_key"].map(
        lambda k: len(bug_to_linked_stories.get(k, []))
    )
    bugs["epic_link_path"] = bugs["associated_epic_key"].apply(
        lambda v: "via_linked_story" if pd.notna(v) else "none"
    )

    n_bugs = len(bugs)
    n_bugs_with_story = int(bugs["associated_story_key"].notna().sum())
    n_bugs_with_epic_in_corpus = int(bugs["associated_epic_name"].notna().sum())
    n_bugs_with_epic_any = int(bugs["associated_epic_key"].notna().sum())
    print(f"[0.3] Bugs with linked Story (Relates/Blocks/Cloners): "
          f"{n_bugs_with_story}/{n_bugs} ({n_bugs_with_story / n_bugs:.1%})", flush=True)
    print(f"[0.3]   ...with Epic resolved (name in corpus): "
          f"{n_bugs_with_epic_in_corpus}/{n_bugs} ({n_bugs_with_epic_in_corpus / n_bugs:.1%})", flush=True)

    # ---- 0.4 Combine and write --------------------------------------------
    cols = [
        "issue_key", "associated_story_key", "associated_epic_key",
        "associated_epic_name", "epic_link_path", "linked_story_count",
    ]
    enrichment = pd.concat([bugs[cols], stories[cols]], ignore_index=True)
    # Sort to match in_scope order
    enrichment = enrichment.set_index("issue_key").reindex(
        in_scope["issue_key"].values
    ).reset_index()
    enrichment.to_csv(args.out_dir / "epic_enrichment.csv", index=False, encoding="utf-8")
    print(f"[0.4] epic_enrichment.csv: {enrichment.shape}", flush=True)

    # ---- Coverage report --------------------------------------------------
    epic_counts = enrichment["associated_epic_name"].dropna().value_counts()
    top_epics = epic_counts.head(10)

    bugs_with_multi = bugs[bugs["linked_story_count"] > 1].sort_values(
        "linked_story_count", ascending=False
    )

    overall_epic_cov = float(enrichment["associated_epic_key"].notna().mean())
    bug_decoration_warning = ""
    if (n_bugs_with_epic_in_corpus / n_bugs) < 0.20:
        bug_decoration_warning = (
            "**WARNING:** Bug→Epic coverage (resolved-in-corpus) is below 20%. "
            "Epic context is decorative for Bugs in this corpus, not load-bearing. "
            "Use it as a lens, not the spine of pain pages.\n"
        )

    with (args.out_dir / "epic_enrichment_report.md").open("w", encoding="utf-8") as f:
        f.write("# Epic enrichment report (Stage 2 / Workstream 0)\n\n")
        f.write(f"_Generated {datetime.now(timezone.utc).isoformat()}_\n\n")
        f.write(f"- Source: `{args.cleaned_dir.name}/tickets_clean.csv` + `ticket_links_long.csv`\n")
        f.write(f"- Working corpus (Bug + Story): **{len(in_scope):,}** rows\n\n")

        f.write("## Coverage\n\n")
        f.write("### Stories\n\n")
        f.write(f"- With `parent_key` set: **{n_stories_epic_any}** / {n_stories} "
                f"(**{n_stories_epic_any / n_stories:.1%}**)\n")
        f.write(f"- With Epic name resolved (parent Epic also in this export): "
                f"**{n_stories_epic_in_corpus}** / {n_stories} "
                f"(**{n_stories_epic_in_corpus / n_stories:.1%}**)\n")
        f.write(f"- Stories whose `parent_key` points outside this export: "
                f"**{n_stories_epic_any - n_stories_epic_in_corpus}**\n\n")

        f.write("### Bugs\n\n")
        f.write(f"- With at least one Story linked via Relates/Blocks/Cloners: "
                f"**{n_bugs_with_story}** / {n_bugs} "
                f"(**{n_bugs_with_story / n_bugs:.1%}**)\n")
        f.write(f"- With Epic name resolved: **{n_bugs_with_epic_in_corpus}** / {n_bugs} "
                f"(**{n_bugs_with_epic_in_corpus / n_bugs:.1%}**)\n\n")

        if bug_decoration_warning:
            f.write(bug_decoration_warning + "\n")
        else:
            f.write(f"Bug→Epic coverage exceeds the 20% load-bearing threshold "
                    f"({n_bugs_with_epic_in_corpus / n_bugs:.1%}). Epic context is genuinely useful for Bugs.\n\n")

        f.write("### Combined\n\n")
        f.write(f"- Tickets in working corpus with any Epic association "
                f"(`associated_epic_key` set): **{int(enrichment['associated_epic_key'].notna().sum()):,}** "
                f"({overall_epic_cov:.1%})\n\n")

        f.write("### Link path distribution\n\n")
        f.write("| epic_link_path | count |\n| --- | ---: |\n")
        for k, v in enrichment["epic_link_path"].value_counts().items():
            f.write(f"| {k} | {int(v)} |\n")

        f.write("\n## Top 10 Epics by associated-ticket count\n\n")
        f.write("| epic_name | tickets |\n| --- | ---: |\n")
        for name, n in top_epics.items():
            short = name if len(str(name)) <= 80 else str(name)[:77] + "..."
            f.write(f"| {short} | {int(n)} |\n")

        f.write("\n## Bugs with multiple linked Stories (top 10)\n\n")
        f.write("Originating Story is picked as the earliest-created. The full linked-Story list "
                "is preserved in the count column for traceability.\n\n")
        f.write("| bug | linked_story_count | originating_story (earliest) | epic_name |\n")
        f.write("| --- | ---: | --- | --- |\n")
        for _, row in bugs_with_multi.head(10).iterrows():
            ek = row.get("issue_key", "")
            n = int(row.get("linked_story_count", 0))
            sk = row.get("associated_story_key") or "(none)"
            en = row.get("associated_epic_name") or "(none)"
            en_short = en if len(str(en)) <= 60 else str(en)[:57] + "..."
            f.write(f"| {ek} | {n} | {sk} | {en_short} |\n")

        f.write("\n## How `epic_link_path` is assigned\n\n")
        f.write("- `direct_parent` — Story's `parent_key` resolves to an Epic\n")
        f.write("- `via_linked_story` — Bug has at least one Story linked through "
                "Relates/Blocks/Cloners (earliest-created Story wins on ties)\n")
        f.write("- `none` — neither path produced an Epic association\n")

        f.write("\n## Definition-of-done for Workstream 0\n\n")
        cov_ok = overall_epic_cov >= 0.0  # always emit; report is the gate
        f.write(f"- `tickets_in_scope.csv` exists with {len(in_scope)} rows: **True**\n")
        f.write(f"- `epic_enrichment.csv` exists with one row per in-scope ticket: "
                f"**{len(enrichment) == len(in_scope)}**\n")
        f.write(f"- Story→Epic coverage acknowledged: "
                f"**{n_stories_epic_any / n_stories:.1%}** of Stories carry parent_key\n")
        f.write(f"- Bug→Epic coverage acknowledged: "
                f"**{n_bugs_with_epic_in_corpus / n_bugs:.1%}** of Bugs resolve to a named Epic "
                f"(threshold: 20%; status: "
                f"**{'load-bearing' if (n_bugs_with_epic_in_corpus / n_bugs) >= 0.20 else 'decorative'}**)\n")

    print("[done]", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
