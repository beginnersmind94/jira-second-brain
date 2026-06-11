"""Jaime-facing dashboard rollup — the boring, defensible release readout (wiki §14.3).

This is the EVAL-WIKI.md §14.3 ("Dashboard rollup Jaime should see") rollup. It does
NOT compute any metric itself: it imports the three single-dimension layers already in
this package and prints the exact lines §14.3 lists, in §14.3 order. The whole point of
the §14.3 dashboard is that it is *boring* — one line per dimension, the dangerous number
first, raw agreement NEVER as the headline (§6 / §12.3 / §15 "what not to say").

Sources, one line each (kept SEPARATE per the §8 / §11.3 "do not merge" rule — coverage
and source-quality are independent single-dimension graders; neither touches the §10
should-FAIL scorer, and this rollup does not fold them together either, it just lays
their already-separate numbers side by side):
  • eval.scoring      → false-negative rate on should-FAIL [n/N], pass^3, confabulation
                        rate, over-refusal rate            (§10 trial-log scorer)
  • eval.coverage     → coverage P0/P1, guides held in DRAFT for missing P0   (§11.1)
  • eval.source_quality → authority score /5, guides held in DRAFT on source quality,
                        flagged low-authority claims        (§11.2)

Each layer reads its OWN synthetic fixture (data/qbank/{judge_run,coverage_fixture,
source_fixture}.jsonl). The §14.3 "broken citation rate" line has no backing fixture in
this repo — the §8.3/§12.3 citation-verifiability grader is unbuilt — so it is printed
honestly as `n/a (no fixture)` rather than fabricated. Per §0: when the doc names an
artifact the repo lacks, the real artifact (its absence) wins; do not invent one.

STDLIB-ONLY, house style of eval/triage_eval.py: NO SDK, NO pandas/numpy, NO model/live
calls, NO server. This is a pure display rollup over the other modules' pure-stdlib
scorers, so `python -m eval.report` runs anywhere and always exits 0 — a dashboard
REPORTS the gate decisions, it is not itself a gate (the per-dimension modules own the
exit-code gates: `python -m eval.scoring --run ... --fn-gate`, `eval.coverage --gate-on`,
`eval.source_quality --live`). Use --gate to make the rollup itself fail when the
headline FN rate exceeds a threshold (off by default).

Usage:
    python -m eval.report                 # print the §14.3 dashboard off the synthetic
                                          #   fixtures (always exit 0; stdlib, no SDK)
    python -m eval.report --gate          # also FAIL (exit 1) if headline FN rate > 0
    python -m eval.report --fn-gate 0.05  # ... with a non-zero FN threshold

NOTE: every fixture under data/qbank/ is SYNTHETIC (labeled per-row). These numbers prove
the rollup wiring, not real safety — replace with SME-owned fixtures before quoting any
line to a stakeholder (§7 gold set, §11.1.1, §11.2.1).
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from eval import coverage as coverage_mod
from eval import scoring as scoring_mod
from eval import source_quality as source_quality_mod
from eval import source_faithfulness as faithfulness_mod


# ── helpers ─────────────────────────────────────────────────────────────────────
def _pct(x) -> str:
    """Percent or 'n/a' (None or NaN → n/a). Mirrors the sibling modules' formatters."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "n/a"
    return f"{x:.1%}"


def _pct0(x) -> str:
    """Whole-percent variant for coverage lines (matches eval.coverage._pct)."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "n/a"
    return f"{x:.0%}"


# ── rollup ────────────────────────────────────────────────────────────────────
def collect() -> dict:
    """Run the three single-dimension layers on their fixtures and gather the §14.3
    numbers. NO model calls — every layer is a pure-stdlib scorer over an existing
    fixture (the LLM judge is an INPUT one layer down, §10 / wiki §4). The layers stay
    separate (§11.3 do-not-merge); this only reads their outputs."""
    # §10 should-FAIL scorer over the trial log (the dangerous-direction headline).
    run_rows = scoring_mod.load_run()
    fail = scoring_mod.fail_class_metrics(run_rows)
    passk = scoring_mod.passk_report(run_rows)
    abst = scoring_mod.abstention_rates(run_rows)

    # §11.1 coverage grader (P0/P1 + the hard P0 gate). Independent of the scorer.
    cov_rows = coverage_mod.load_rows()
    cov_report = coverage_mod.grade_all(cov_rows)
    cov_roll = coverage_mod.overall_lines(cov_rows)
    cov_draft = {g: r for g, r in cov_report.items() if r["gate"] == "DRAFT"}

    # §11.2 source-quality grader (authority /5 + low-authority flag gate). Independent.
    src_rows = source_quality_mod.load_rows()
    src = source_quality_mod.grade(src_rows)

    # §14.3 "Top draft reasons" — aggregate the reasons the two GATING graders actually
    # emit on these fixtures (missing P0 from coverage; flagged low-authority / below-floor
    # from source-quality). Reported as observed counts, not the wiki's static example list,
    # so the line traces to real draft decisions (§10 diagnostic-slice spirit, §12.4 "every
    # DRAFT decision reports the reason").
    draft_reasons: dict[str, int] = {}
    for r in cov_draft.values():
        if r["missing_p0_facts"]:
            draft_reasons["missing P0 fact"] = draft_reasons.get("missing P0 fact", 0) + 1
    for gid in src["draft_guides"]:
        v = src["per_guide"][gid]
        if v["flagged_claims"]:
            draft_reasons["low-authority citation (higher source existed)"] = \
                draft_reasons.get("low-authority citation (higher source existed)", 0) + 1
        if any("MIN_AUTHORITY" in reason for reason in v["draft_reasons"]):
            draft_reasons["avg authority below SME floor"] = \
                draft_reasons.get("avg authority below SME floor", 0) + 1

    total_draft = len(cov_draft) + len(src["draft_guides"])

    # Source-faithfulness (guide CLAIM vs its CITED span): fixture stats only here. The live
    # FN-rate needs the semantic judge (--live), so the dashboard reports it as n/a rather
    # than fabricate — same honesty as the broken-citation line (§0 real-artifact-wins).
    faith_rows = faithfulness_mod.load_rows()
    faith = {"n": len(faith_rows),
             "n_over": sum(1 for r in faith_rows if r["gold"] == "over_reach")}

    return {
        "fail": fail, "passk": passk, "abst": abst, "faith": faith,
        "cov_roll": cov_roll, "cov_draft": cov_draft, "cov_report": cov_report,
        "src": src,
        "draft_reasons": draft_reasons,
        "total_draft": total_draft,
        "n_run_rows": len(run_rows),
    }


def print_dashboard(d: dict) -> None:
    """Print the §14.3 dashboard, in §14.3 order. Boring and defensible by design.

    The §14.3 spec block, line for line:
        False-negative rate on should-FAIL: 0.0% [0/N]
        pass^3: 100.0%
        Confabulation rate: 0.0%
        Over-refusal rate: X.X%
        Coverage: 100% P0 / YY% P1
        Authority score: Z.Z/5
        Guides held in DRAFT: N
        Top draft reasons: missing P0, stale source, low-authority citation, cross-lane
        Broken citation rate: 0.0%
    "Do NOT show raw agreement as the headline." — we never print agreement here.
    """
    fail, passk, abst = d["fail"], d["passk"], d["abst"]
    cov_roll, src = d["cov_roll"], d["src"]
    km = passk["k_min"]

    print("\n" + "=" * 66)
    print("  EVAL DASHBOARD — release readiness (wiki §14.3)")
    print("  Source fixtures: data/qbank/{judge_run,coverage_fixture,source_fixture}.jsonl")
    print("  ALL SYNTHETIC — proves wiring, not real safety (replace per §7/§11.x).")
    print("=" * 66)

    # 1) HEADLINE — the dangerous direction, first and alone (§3 / §6.1 / §15).
    print(f"  False-negative rate on should-FAIL: {_pct(fail['fn_rate'])} "
          f"[{fail['false_neg_n']}/{fail['should_fail_n']}]   "
          f"← the ONE number; raw agreement is NEVER the headline (§6/§12.3)")
    if fail["false_neg_ids"]:
        print(f"      ⚠ leaked items: {', '.join(fail['false_neg_ids'])}")

    # 2) pass^k consistency (the honest gate number, not pass@k) (§6.2 / §10.3).
    print(f"  pass^{km}: {_pct(passk[f'pass^{km}'])}   "
          f"(pass@{km}={_pct(passk[f'pass@{km}'])} shown only as the contrast NOT to ship on)")
    if passk["under_k_items"]:
        print(f"      ⚠ {len(passk['under_k_items'])} item(s) ran < k={km} trials "
              f"({', '.join(passk['under_k_items'])}) — §10.5 isolation gap")

    # 3) + 4) Abstention, two rates, the dangerous one labeled (§6.3 / §10.4).
    print(f"  Confabulation rate: {_pct(abst['confabulation_rate'])}   ← unrecoverable (§4.5.3)")
    print(f"  Over-refusal rate:  {_pct(abst['over_refusal_rate'])}   ← recoverable")

    # 5) Coverage P0/P1 (§11.1).
    print(f"  Coverage: {_pct0(cov_roll['p0_overall'])} P0 "
          f"[{cov_roll['n_p0']} facts] / {_pct0(cov_roll['p1_overall'])} P1 "
          f"[{cov_roll['n_p1']} facts]")

    # 6) Authority score /5 (§11.2).
    print(f"  Authority score: {src['overall_authority']:.1f}/5 "
          f"(across {src['n_mapped']} mapped cited sources; "
          f"{src['total_flagged_claims']} flagged low-authority claim(s))")
    if src["n_unmapped"]:
        print(f"      ⚠ {src['n_unmapped']} citation(s) with unmapped source_type "
              f"{src['unmapped_types']} — EXCLUDED, not scored 0 (§11.2.1)")

    # 7) Guides held in DRAFT — split by which independent gate held them (§11.3).
    print(f"  Guides held in DRAFT: {d['total_draft']}   "
          f"(coverage: {len(d['cov_draft'])}  ·  source-quality: {len(src['draft_guides'])})")
    if d["cov_draft"]:
        for gid, r in d["cov_draft"].items():
            miss = (", missing P0: " + ", ".join(r["missing_p0_facts"])) if r["missing_p0_facts"] else ""
            print(f"      [coverage]       {gid} ({r['guide_type']}, "
                  f"P0 {_pct0(r['P0_frac'])} / P1 {_pct0(r['P1_frac'])}{miss})")
    for gid in sorted(src["draft_guides"]):
        reasons = "; ".join(src["per_guide"][gid]["draft_reasons"])
        print(f"      [source-quality] {gid} ({reasons})")

    # 8) Top draft reasons — observed on these fixtures, ranked (§12.4 reason-per-DRAFT).
    if d["draft_reasons"]:
        ranked = sorted(d["draft_reasons"].items(), key=lambda kv: (-kv[1], kv[0]))
        joined = ", ".join(f"{reason} (x{n})" for reason, n in ranked)
        print(f"  Top draft reasons: {joined}")
    else:
        print("  Top draft reasons: none (no guide held in DRAFT)")

    # 9) Source-faithfulness (guide CLAIM within its CITED span) — the seam the verbatim
    # gate AND the quiz<->guide gate both miss: a claim can cite a real verbatim span yet
    # over-reach/reframe it. The real Q4 drift from the Inventory Distribution run is a
    # regression row in the fixture. Live FN-rate needs the semantic judge (--live).
    f = d["faith"]
    print(f"  Source-faithfulness (guide claim within cited span): fixture {f['n']} rows, "
          f"{f['n_over']} over-reach incl. the real Q4 drift; live FN-rate n/a "
          f"— `python -m eval.source_faithfulness --live`")

    # 10) Broken citation rate — §8.3/§12.3 citation-verifiability grader is UNBUILT and
    # has no fixture in this repo. Print honestly rather than fabricate (§0 real-artifact
    # wins; cite-or-cut). The wiki's static example reasons (stale source, cross-lane) are
    # likewise not graded here — only coverage (§11.1) and source-quality (§11.2) gate.
    print("  Broken citation rate: n/a (no citation-verifiability fixture; "
          "§8.3/§12.3 grader unbuilt)")
    print("=" * 66)


# ── main ──────────────────────────────────────────────────────────────────────
def main() -> int:
    ap = argparse.ArgumentParser(
        description="Jaime dashboard rollup over eval.scoring + eval.coverage + "
                    "eval.source_quality (wiki §14.3). Stdlib; no model calls.")
    ap.add_argument("--gate", action="store_true",
                    help="make the rollup itself FAIL (exit 1) if the headline should-FAIL "
                         "FN rate exceeds --fn-gate (off by default — a dashboard reports; "
                         "the per-dimension modules own the real exit-code gates).")
    ap.add_argument("--fn-gate", type=float, default=0.0,
                    help="FN-rate threshold used only with --gate (default 0.0).")
    args = ap.parse_args()

    print("Eval dashboard rollup (§14.3) — reading the three single-dimension layers' "
          "SYNTHETIC fixtures (no model calls, no SDK, no server).")
    d = collect()
    print_dashboard(d)

    fn_rate = d["fail"]["fn_rate"] or 0.0
    if args.gate:
        if fn_rate > args.fn_gate:
            print(f"\nFAIL — headline FN rate {fn_rate:.2%} exceeds --fn-gate "
                  f"{args.fn_gate:.2%} (a bad claim was waved through — unrecoverable, §3).")
            return 1
        print(f"\nPASS — headline FN rate {fn_rate:.2%} within --fn-gate {args.fn_gate:.2%}.")
        return 0

    # Default: pure display. Exit 0 regardless — the gating lives in the sibling modules.
    print("\nDashboard printed (display only; exit 0). The per-dimension exit-code gates:")
    print("  python -m eval.scoring --run data/qbank/judge_run.jsonl --fn-gate 0.0")
    print("  python -m eval.coverage --gate-on")
    print("  python -m eval.source_quality --live")
    print("NOTE: every number above is from SYNTHETIC fixtures — wiring proof, not a "
          "safety claim. Replace with SME-owned fixtures (§7/§11.1.1/§11.2.1) first.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
