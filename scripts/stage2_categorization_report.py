"""Stage 2 / Workstream 1.4 + 1.5 — finalize ticket_categories.csv and write
categorization_report.md.

Reads:
  stage2/tickets_in_scope.csv
  stage2/epic_enrichment.csv
  stage2/ticket_categories_raw.csv  (LLM output from stage2_tag_tickets.py)

Writes:
  stage2/ticket_categories.csv          (final, with mechanical fields joined)
  stage2/categorization_report.md       (validation surface)

Hard gates:
  - Other rate < 10% overall → halt
  - Other rate < 15% within Bugs → halt
  - cs_source == 'unclear' rate < 30% within PCS-* subset → halt
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


CATCH_ALL_COMPONENT = "Item Management"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage2-dir", required=True, type=Path)
    parser.add_argument("--raw", default=None, type=Path,
                        help="LLM raw output (default: stage2-dir/ticket_categories_raw.csv)")
    args = parser.parse_args()

    raw_path = args.raw or (args.stage2_dir / "ticket_categories_raw.csv")
    tickets = pd.read_csv(args.stage2_dir / "tickets_in_scope.csv", low_memory=False)
    enrich = pd.read_csv(args.stage2_dir / "epic_enrichment.csv")
    raw = pd.read_csv(raw_path)

    print(f"tickets in scope: {len(tickets)}, raw tags: {len(raw)}", flush=True)
    if len(tickets) != len(raw):
        print(f"WARNING: tags/scope size mismatch — {len(tickets) - len(raw)} tickets missing", flush=True)

    df = tickets.merge(raw, on="issue_key", how="left").merge(
        enrich[["issue_key", "associated_epic_name", "epic_link_path"]],
        on="issue_key", how="left",
    )

    # Mechanical fields
    df["customer_reported_via_cs"] = df["issue_key"].astype(str).str.startswith("PCS-")

    def parse_components(s) -> list[str]:
        if not isinstance(s, str) or not s:
            return []
        return [c for c in s.split("|") if c]

    components = df["components_all"].map(parse_components)
    df["other_modules_list"] = components.map(
        lambda lst: "|".join([c for c in lst if c != CATCH_ALL_COMPONENT])
    )
    n_other_components = components.map(lambda lst: sum(1 for c in lst if c != CATCH_ALL_COMPONENT))
    is_inv_sync_cat = df["primary_category"] == "Inventory Sync & Publishing"
    df["touches_other_modules"] = (n_other_components > 0) | is_inv_sync_cat

    # Sanity: cs_source should be null when not PCS-*
    bad_cs = df[(~df["customer_reported_via_cs"]) & df["cs_source"].notna()]
    if len(bad_cs):
        print(f"normalizing cs_source on {len(bad_cs)} non-PCS rows (LLM returned a value)", flush=True)
        df.loc[~df["customer_reported_via_cs"], "cs_source"] = pd.NA

    # Output schema
    final = pd.DataFrame({
        "issue_key": df["issue_key"],
        "issue_type": df["issue_type"],
        "primary_category": df["primary_category"],
        "secondary_category": df["secondary_category"],
        "category_confidence": df["confidence"],
        "other_reason": df["other_reason"],
        "customer_reported_via_cs": df["customer_reported_via_cs"],
        "cs_source": df["cs_source"],
        "touches_other_modules": df["touches_other_modules"],
        "other_modules_list": df["other_modules_list"],
    })
    final_path = args.stage2_dir / "ticket_categories.csv"
    final.to_csv(final_path, index=False, encoding="utf-8")
    print(f"wrote {final_path}: {final.shape}", flush=True)

    # ----------------------- Validation report ---------------------------
    report = []
    report.append("# Categorization report (Stage 2 / Workstream 1.5)")
    report.append("")
    report.append(f"_Generated {datetime.now(timezone.utc).isoformat()}_")
    report.append(f"- Source: `{raw_path.name}`")
    report.append(f"- Total tickets tagged: **{len(final):,}** "
                  f"(Bug={int((final['issue_type']=='Bug').sum())}, "
                  f"Story={int((final['issue_type']=='Story').sum())})")
    report.append("")

    # Per-category distribution
    report.append("## Per-category distribution")
    report.append("")
    report.append("| primary_category | total | bugs | stories | bug:story |")
    report.append("| --- | ---: | ---: | ---: | ---: |")
    cat_counts = final.groupby(["primary_category", "issue_type"]).size().unstack(fill_value=0)
    cat_counts["total"] = cat_counts.sum(axis=1)
    cat_counts = cat_counts.sort_values("total", ascending=False)
    for cat, row in cat_counts.iterrows():
        bugs = int(row.get("Bug", 0))
        stories = int(row.get("Story", 0))
        ratio = f"{bugs / stories:.1f}:1" if stories > 0 else (f"{bugs}:0" if bugs > 0 else "—")
        report.append(f"| {cat} | {int(row['total'])} | {bugs} | {stories} | {ratio} |")
    report.append("")

    # Confidence distribution
    report.append("## Confidence distribution")
    report.append("")
    report.append("| category_confidence | count | % |")
    report.append("| --- | ---: | ---: |")
    for k, v in final["category_confidence"].value_counts().items():
        report.append(f"| {k} | {int(v)} | {v / len(final):.1%} |")
    report.append("")

    # Other rate gates
    other_total = float((final["primary_category"] == "Other").mean())
    other_bug_rate = float(
        (final[final["issue_type"] == "Bug"]["primary_category"] == "Other").mean()
    )
    other_total_n = int((final["primary_category"] == "Other").sum())
    other_bug_n = int(((final["issue_type"] == "Bug") & (final["primary_category"] == "Other")).sum())

    report.append("## Other-rate gates")
    report.append("")
    report.append(f"- Overall: **{other_total:.1%}** ({other_total_n} of {len(final)}) "
                  f"— gate: <10% — {'**PASS**' if other_total < 0.10 else '**FAIL**'}")
    report.append(f"- Bugs only: **{other_bug_rate:.1%}** ({other_bug_n} of "
                  f"{int((final['issue_type']=='Bug').sum())}) "
                  f"— gate: <15% — {'**PASS**' if other_bug_rate < 0.15 else '**FAIL**'}")
    report.append("")

    # Top other_reason values
    other_reasons = final[final["primary_category"] == "Other"]["other_reason"].dropna()
    if len(other_reasons):
        report.append("### Top `other_reason` values")
        report.append("")
        report.append("| reason | count |")
        report.append("| --- | ---: |")
        for reason, n in Counter(other_reasons).most_common(15):
            short = reason if len(str(reason)) <= 100 else str(reason)[:97] + "..."
            report.append(f"| {short} | {n} |")
        report.append("")

    # cs_source gate
    pcs = final[final["customer_reported_via_cs"]]
    if len(pcs):
        unclear_rate = float((pcs["cs_source"] == "unclear").mean())
        unclear_n = int((pcs["cs_source"] == "unclear").sum())
        report.append("## CS-source gate")
        report.append("")
        report.append(f"- PCS-* tickets: **{len(pcs)}**")
        report.append(f"- `cs_source == 'unclear'`: **{unclear_n}** ({unclear_rate:.1%}) — "
                      f"gate: <30% — {'**PASS**' if unclear_rate < 0.30 else '**FAIL**'}")
        report.append("")
        report.append("### `cs_source` distribution within PCS-*")
        report.append("")
        report.append("| cs_source | count | % |")
        report.append("| --- | ---: | ---: |")
        for k, v in pcs["cs_source"].value_counts(dropna=False).items():
            label = "(null)" if pd.isna(k) else k
            report.append(f"| {label} | {int(v)} | {v / len(pcs):.1%} |")
        report.append("")

    # customer_reported_via_cs rate by category
    report.append("## Customer-reported rate by category")
    report.append("")
    report.append("Per-category rate of `customer_reported_via_cs == True` — surfaces which "
                  "problem spaces are most live-customer-driven.")
    report.append("")
    report.append("| primary_category | total | cs-reported | rate |")
    report.append("| --- | ---: | ---: | ---: |")
    for cat in cat_counts.index:
        sub = final[final["primary_category"] == cat]
        n = len(sub)
        cs_n = int(sub["customer_reported_via_cs"].sum())
        rate = cs_n / n if n else 0.0
        report.append(f"| {cat} | {n} | {cs_n} | {rate:.1%} |")
    report.append("")

    # touches_other_modules cross-tab
    report.append("## `touches_other_modules` rate by category")
    report.append("")
    report.append("| primary_category | total | touches_other | rate |")
    report.append("| --- | ---: | ---: | ---: |")
    for cat in cat_counts.index:
        sub = final[final["primary_category"] == cat]
        n = len(sub)
        tom_n = int(sub["touches_other_modules"].sum())
        rate = tom_n / n if n else 0.0
        report.append(f"| {cat} | {n} | {tom_n} | {rate:.1%} |")
    report.append("")

    # Top 3 Epics per category
    report.append("## Top 3 Epics per category")
    report.append("")
    df_epics = final.merge(enrich[["issue_key", "associated_epic_name"]], on="issue_key", how="left")
    for cat in cat_counts.index:
        sub = df_epics[df_epics["primary_category"] == cat]
        if not len(sub):
            continue
        epic_counts = sub["associated_epic_name"].dropna().value_counts().head(3)
        if not len(epic_counts):
            report.append(f"### {cat}")
            report.append("- _no Epic associations_")
            continue
        report.append(f"### {cat}")
        for ep, n in epic_counts.items():
            ep_short = ep if len(str(ep)) <= 80 else str(ep)[:77] + "..."
            report.append(f"- **{int(n)}** · {ep_short}")
        report.append("")

    # Per-category sample of 5 tickets for spot-check
    report.append("## Per-category samples (5 tickets each)")
    report.append("")
    df_samples = final.merge(
        tickets[["issue_key", "summary"]], on="issue_key", how="left"
    )
    for cat in cat_counts.index:
        sub = df_samples[df_samples["primary_category"] == cat]
        if not len(sub):
            continue
        report.append(f"### {cat} ({len(sub)} tickets)")
        report.append("")
        sample = sub.sample(min(5, len(sub)), random_state=11)
        for _, r in sample.iterrows():
            t = str(r.get("summary", ""))[:120]
            cf = r.get("category_confidence", "")
            sc = r.get("secondary_category")
            sc_str = f" → 2nd: _{sc}_" if pd.notna(sc) and sc else ""
            report.append(f"- `{r['issue_key']}` ({r['issue_type']}, {cf}){sc_str} — {t}")
        report.append("")

    out_path = args.stage2_dir / "categorization_report.md"
    out_path.write_text("\n".join(report), encoding="utf-8")
    print(f"wrote {out_path}", flush=True)

    # Summary print
    print(f"\nOther rate overall: {other_total:.1%} (gate <10%): "
          f"{'PASS' if other_total < 0.10 else 'FAIL'}")
    print(f"Other rate Bugs:    {other_bug_rate:.1%} (gate <15%): "
          f"{'PASS' if other_bug_rate < 0.15 else 'FAIL'}")
    if len(pcs):
        unclear_rate = float((pcs["cs_source"] == "unclear").mean())
        print(f"cs_source unclear:  {unclear_rate:.1%} (gate <30%): "
              f"{'PASS' if unclear_rate < 0.30 else 'FAIL'}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
