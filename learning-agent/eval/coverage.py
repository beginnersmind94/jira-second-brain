"""Coverage grader — required-facts-present %, P0/P1 thresholds, hard P0 gate.

Single-dimension grader from EVAL-WIKI.md §8.4 + the §13.1 reference
implementation (in-body header §11.1). Per the §11.3 / §10.6 "do not merge"
rule this is INDEPENDENT of the §10 should-FAIL support scorer (eval/judge_eval.py)
and of the source-quality grader (§11.2): coverage answers one question only —
"did the guide include the facts a new hire needs?" — and never touches the
should-FAIL leakage metric.

Coverage asks: required facts are defined per role × workflow (§8.4), each tagged
P0 (job-critical) or P1 (supporting). The gate is per-guide-type (§11.1):

  guide_type   P0 threshold   P1 threshold   gate behavior
  long_form    100%           report only    publish on P0 alone
  micro        100%           80%            publish only if P0 AND P1 clear
  tldr         100%           report only    publish on P0 alone

Hard rule (§8.4 / §11.1): **any missing P0 fact → DRAFT**, regardless of every
other score. Partial credit (the present-fraction per priority) is reported for
diagnostics (§6.4), never as a bypass.

This adapts the wiki's pandas reference (§11.1) to PURE STDLIB so it runs
anywhere, mirroring eval/triage_eval.py's house style: an in-module offline
self-test (oracle + degenerate baselines + exit-code gate) and NO SDK / pandas /
numpy. The wiki's `pd.read_json(lines=True)` + `groupby(...).apply` become a
plain JSONL reader + dict aggregation; `np.nan` becomes float('nan').

`is_present` is an INPUT (§11.1.1): upstream a fact-matching judge or a
deterministic anchor/string check decides presence. This grader only aggregates
it — it does not compute presence and does not call a model.

NOTE — two different coverage artifacts, do not conflate:
  • THIS module implements the EVAL-WIKI §8.4/§11.1 guide-level schema
    (guide_id / guide_type / role_scope / workflow / fact_id / priority /
    is_present), the one wired to the three §14.2 gate cases.
  • docs/EVAL-COVERAGE-METHOD.md specs a richer per-topic SME keypoint-list method
    (severity, safety-critical slice) for generated quiz/study-sets. Same spirit,
    different schema and granularity; that one is unbuilt.

Usage:
    python -m eval.coverage          # OFFLINE: validate fixture + grader via an
                                      #   oracle (authored gate decisions) + two
                                      #   degenerate baselines. No SDK / no auth.
    python -m eval.coverage --fixture data/qbank/coverage_fixture.jsonl
    python -m eval.coverage --gate-on  # exit nonzero if ANY guide gates DRAFT
                                      #   (release-gate mode over a real fixture)

Fixture: data/qbank/coverage_fixture.jsonl  (synthetic today; `_synthetic:true`
per row. Real role × workflow required-fact lists are SME-owned, §11.1.1 /
EVAL-COVERAGE-METHOD.md §2, and come later).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FIXTURE_PATH = Path(__file__).resolve().parent.parent / "data" / "qbank" / "coverage_fixture.jsonl"

GUIDE_TYPES = ("long_form", "micro", "tldr")
PRIORITIES = ("P0", "P1")

# Per-guide-type thresholds (§8.4 / §11.1). None = priority reported, never gated.
COVERAGE_THRESHOLDS = {
    "long_form": {"P0": 1.00, "P1": None},   # 100% P0; P1 not gated
    "micro":     {"P0": 1.00, "P1": 0.80},   # 100% P0, 80% P1
    "tldr":      {"P0": 1.00, "P1": None},   # 100% P0 only
}

# The three EVAL-WIKI §14.2 minimum cases this fixture must reproduce. The offline
# oracle asserts the grader returns exactly these gate decisions — this is the
# §12.4 "prove the dangerous direction is counted" unit test (a missing P0 must
# force DRAFT even when everything else is green).
EXPECTED_GATES = {
    "cov-longform-missing-p0": "DRAFT",    # §14.2: long-form missing a P0 → DRAFT
    "cov-micro-p1-short":      "DRAFT",    # §14.2: micro 100% P0 / 70% P1 → DRAFT
    "cov-tldr-p1-zero":        "PUBLISH",  # §14.2: tldr 100% P0 / 0% P1 → PUBLISH
    "cov-longform-clean":      "PUBLISH",  # long-form 100% P0, partial P1 (report-only)
    "cov-micro-clean":         "PUBLISH",  # micro 100% P0 / 90% P1 (≥80%)
    "cov-tldr-no-p1":          "PUBLISH",  # tldr 100% P0, zero P1 rows (empty bucket ok)
}


# ── data ──────────────────────────────────────────────────────────────────────
def load_rows(path: Path = FIXTURE_PATH) -> list[dict]:
    """Read the JSONL fixture. Skips the leading `_comment` metadata line and any
    blank lines; validates the schema of each data row."""
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        if "_comment" in obj and "guide_id" not in obj:
            continue  # synthetic-label / provenance metadata line, not a data row
        for field in ("guide_id", "guide_type", "role_scope", "workflow", "fact_id", "priority", "is_present"):
            assert field in obj, f"row missing {field!r}: {obj}"
        assert obj["guide_type"] in GUIDE_TYPES, f"{obj['fact_id']}: bad guide_type {obj['guide_type']!r}"
        assert obj["priority"] in PRIORITIES, f"{obj['fact_id']}: bad priority {obj['priority']!r}"
        assert isinstance(obj["is_present"], bool), f"{obj['fact_id']}: is_present must be bool"
        rows.append(obj)
    return rows


def group_by_guide(rows: list[dict]) -> dict[str, list[dict]]:
    """Stdlib stand-in for the wiki's `coverage.groupby('guide_id')`."""
    out: dict[str, list[dict]] = {}
    for r in rows:
        out.setdefault(r["guide_id"], []).append(r)
    return out


# ── scoring ─────────────────────────────────────────────────────────────────
def coverage_grade(guide_rows: list[dict]) -> dict:
    """Grade one guide. Stdlib port of the wiki §11.1 `coverage_grade`.

    Returns present/total/frac per priority (partial credit, §6.4), the list of
    missing P0 fact_ids, and the binary gate ∈ {PUBLISH, DRAFT}.
    """
    guide_type = guide_rows[0]["guide_type"]
    # All rows for a guide must agree on guide_type (a mixed guide is a fixture bug).
    assert all(r["guide_type"] == guide_type for r in guide_rows), \
        f"{guide_rows[0]['guide_id']}: mixed guide_type within one guide"
    thresholds = COVERAGE_THRESHOLDS[guide_type]

    out: dict = {"guide_id": guide_rows[0]["guide_id"], "guide_type": guide_type}
    missing_p0: list[str] = []
    gate_pass = True

    for prio in PRIORITIES:
        sub = [r for r in guide_rows if r["priority"] == prio]
        n = len(sub)
        present = sum(1 for r in sub if r["is_present"])
        frac = (present / n) if n else float("nan")   # partial credit (§6.4)
        out[f"{prio}_present"] = present
        out[f"{prio}_total"] = n
        out[f"{prio}_frac"] = frac

        req = thresholds[prio]
        if req is not None and n:
            if frac < req:
                gate_pass = False
            if prio == "P0":
                missing_p0 = [r["fact_id"] for r in sub if not r["is_present"]]
        elif prio == "P0":
            # P0 always has a threshold in every guide type; this branch is defensive.
            missing_p0 = [r["fact_id"] for r in sub if not r["is_present"]]

    # §8.4 / §11.1 hard rule: ANY missing P0 fact → DRAFT, regardless of other scores.
    if missing_p0:
        gate_pass = False

    out["missing_p0_facts"] = missing_p0
    out["gate"] = "PUBLISH" if gate_pass else "DRAFT"
    return out


def grade_all(rows: list[dict]) -> dict[str, dict]:
    """Per-guide coverage report, keyed by guide_id (deterministic order)."""
    grouped = group_by_guide(rows)
    return {gid: coverage_grade(grouped[gid]) for gid in grouped}


def overall_lines(rows: list[dict]) -> dict:
    """Jaime-facing dashboard rollup (§11.1 / §12.3): critical vs supporting %."""
    p0 = [r for r in rows if r["priority"] == "P0"]
    p1 = [r for r in rows if r["priority"] == "P1"]
    crit = (sum(r["is_present"] for r in p0) / len(p0)) if p0 else float("nan")
    supp = (sum(r["is_present"] for r in p1) / len(p1)) if p1 else float("nan")
    return {"p0_overall": crit, "p1_overall": supp, "n_p0": len(p0), "n_p1": len(p1)}


def _pct(x: float) -> str:
    return "n/a" if (isinstance(x, float) and math.isnan(x)) else f"{x:.0%}"


# ── report ────────────────────────────────────────────────────────────────────
def print_report(rows: list[dict], report: dict[str, dict]) -> None:
    roll = overall_lines(rows)
    print(f"\nCoverage — {len(report)} guides, {len(rows)} required facts")
    print(f"  Coverage: {_pct(roll['p0_overall'])} on critical (P0) workflows "
          f"[{roll['n_p0']} facts], {_pct(roll['p1_overall'])} on supporting (P1) "
          f"workflows [{roll['n_p1']} facts]")
    n_draft = sum(1 for r in report.values() if r["gate"] == "DRAFT")
    print(f"  Guides held in DRAFT: {n_draft}/{len(report)}")
    print("\n  per-guide:")
    for gid in report:
        r = report[gid]
        line = (f"    {r['gate']:<7} {gid:<26} ({r['guide_type']:<9}) "
                f"P0 {r['P0_present']}/{r['P0_total']} ({_pct(r['P0_frac'])})  "
                f"P1 {r['P1_present']}/{r['P1_total']} ({_pct(r['P1_frac'])})")
        print(line)
        if r["missing_p0_facts"]:
            print(f"            ⚠ missing P0 (forces DRAFT): {', '.join(r['missing_p0_facts'])}")


# ── offline self-test ───────────────────────────────────────────────────────
def _with_presence(rows: list[dict], value: bool) -> list[dict]:
    """Degenerate baseline helper: copy rows with every is_present forced to `value`."""
    return [{**r, "is_present": value} for r in rows]


def offline_selftest(rows: list[dict]) -> int:
    """Prove the fixture + grader against an oracle and two degenerate baselines.
    No SDK / no auth. These assertions guard the grader itself (mirrors
    triage_eval.py's oracle + always-X baselines)."""
    report = grade_all(rows)
    print_report(rows, report)

    # ORACLE — authored gate decisions (incl. the three §14.2 cases) must match.
    # This is the dangerous-direction unit test: a missing P0 forces DRAFT even
    # when other scores are green; a satisfied P0/P1 publishes.
    print("\n── ORACLE (authored gate decisions; incl. §14.2 cases) ──")
    mismatches = []
    for gid, want in EXPECTED_GATES.items():
        assert gid in report, f"oracle references unknown guide {gid!r} — fixture drift"
        got = report[gid]["gate"]
        flag = "ok" if got == want else "MISMATCH"
        print(f"    {flag:<8} {gid:<26} expected {want:<7} got {got}")
        if got != want:
            mismatches.append((gid, want, got))
    assert not mismatches, f"gate decisions disagree with §14.2 oracle: {mismatches}"

    # Spot-check the §14.2 partial-credit semantics explicitly (not just the gate).
    micro = report["cov-micro-p1-short"]
    assert micro["P0_frac"] == 1.0, "micro-p1-short must be 100% P0"
    assert abs(micro["P1_frac"] - 0.70) < 1e-9, f"micro-p1-short P1 must be 70%, got {micro['P1_frac']}"
    tldr0 = report["cov-tldr-p1-zero"]
    assert tldr0["P0_frac"] == 1.0 and tldr0["P1_frac"] == 0.0, "tldr-p1-zero must be 100% P0 / 0% P1"
    lf = report["cov-longform-missing-p0"]
    assert lf["missing_p0_facts"], "longform-missing-p0 must name ≥1 missing P0 fact"
    tnp = report["cov-tldr-no-p1"]
    assert math.isnan(tnp["P1_frac"]), "tldr-no-p1 must have NaN P1 frac (empty bucket, §11.1.1)"

    # BASELINE all-present → every guide PUBLISH (proves no spurious DRAFT).
    all_present = grade_all(_with_presence(rows, True))
    print("\n── BASELINE all-present (every required fact covered) ──")
    bad = [g for g, r in all_present.items() if r["gate"] != "PUBLISH"]
    print(f"    DRAFT guides: {len(bad)} (expected 0)")
    assert not bad, f"all-present must PUBLISH every guide; these gated DRAFT: {bad}"

    # BASELINE all-absent → every guide DRAFT (proves the P0 hard rule fires;
    # exposes a grader that ignores presence — the no-discrimination check).
    all_absent = grade_all(_with_presence(rows, False))
    print("\n── BASELINE all-absent (no required fact covered) ──")
    pub = [g for g, r in all_absent.items() if r["gate"] != "DRAFT"]
    print(f"    PUBLISH guides: {len(pub)} (expected 0)")
    assert not pub, f"all-absent must hold every guide in DRAFT; these published: {pub}"

    print("\nOFFLINE OK — fixture valid, gate decisions match the §14.2 oracle, "
          "partial credit + empty-bucket handled, degenerate baselines correct.")
    return 0


# ── main ───────────────────────────────────────────────────────────────────────
def main() -> int:
    ap = argparse.ArgumentParser(description="Coverage grader (EVAL-WIKI §8.4/§11.1).")
    ap.add_argument("--fixture", type=Path, default=FIXTURE_PATH,
                    help="JSONL of required facts (default: data/qbank/coverage_fixture.jsonl)")
    ap.add_argument("--gate-on", action="store_true",
                    help="release-gate mode: exit nonzero if ANY guide gates DRAFT")
    args = ap.parse_args()

    rows = load_rows(args.fixture)
    if all(r.get("_synthetic") for r in rows):
        print("NOTE: every row is synthetic. Real role × workflow required-fact lists "
              "are SME-owned (§11.1.1 / EVAL-COVERAGE-METHOD.md §2) — collect those before "
              "trusting coverage % as a release signal.")

    if not args.gate_on:
        # Default: offline self-test (oracle + degenerate baselines). No SDK.
        return offline_selftest(rows)

    # Release-gate mode over a (real) fixture: any DRAFT guide fails the run.
    report = grade_all(rows)
    print_report(rows, report)
    draft = {g: r for g, r in report.items() if r["gate"] == "DRAFT"}
    if draft:
        print(f"\nFAIL — {len(draft)} guide(s) held in DRAFT "
              f"(missing P0 or below P1 threshold): {', '.join(draft)}")
        return 1
    print(f"\nPASS — all {len(report)} guide(s) clear the coverage gate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
