"""Diagnostic SCORING layer over an existing judge_run.jsonl — stdlib, no model calls.

This is the wiki's §10 scoring layer (EVAL-WIKI.md "12. Reference implementation —
scoring layer", whose in-body subsections are §10.1–§10.6; gates it cites are §4.5.x).
The wiki's reference code is pandas; this module is the STDLIB port in the house style
of eval/triage_eval.py / eval/judge_eval.py so `python -m eval.scoring` runs anywhere
(NO SDK, NO pandas/numpy, in-module offline self-test, exit-code gate).

It consumes judge verdicts that ALREADY exist — one row per (claim, cited-span) TRIAL —
and computes the metrics the doc mandates. It makes NO model calls: per §10 / wiki §4,
"LLM-as-a-judge is an evaluation method, not a metric" — the judge is an INPUT here.

What it complements vs. eval/judge_eval.py (read this — they are two different layers):
  • eval/judge_eval.py is the GOLD-SET judge scorer. Its input is judge_gold_set.jsonl
    (per-item: ground_truth_support supported|unsupported); it has a `--live` path that
    actually CALLS the LLM judge (qbank_gate.llm_support_judge) and gates FNR on the
    'unsupported' class. It measures *the judge's discrimination on one trial each*.
  • THIS module is the TRIAL-LOG scorer one layer up. Its input is judge_run.jsonl, a
    log of judge verdicts across k≥3 TRIALS per item (gold_label/judge_label ∈
    PASS|FAIL|ABSTAIN / PASS|FAIL|UNKNOWN). It re-derives the headline FN rate AND adds
    what a single-trial scorer cannot: diagnostic SLICES (FN by gate, FN by neg_class),
    pass^k vs pass@k consistency (k≥3), and the two abstention rates. It makes NO calls.
  Same dangerous event (gold=FAIL, judge=PASS); different granularity and inputs. The two
  schemas deliberately DIFFER (judge_gold_set.jsonl ≠ judge_run.jsonl) — do not unify them.

Headline (§6.1 / §3): the false-negative rate on the should-FAIL class.
    FN = gold FAIL & judge PASS   (a bad claim waved through — unrecoverable, §3 table)
    fn_rate = FN / should_fail_n  ← the ONE number Jaime hears (§12.3). Never raw agreement.

Usage:
    python -m eval.scoring                 # OFFLINE: validate scorer on a SEEDED synthetic
                                           #   judge_run via oracle + a known-FN case + a
                                           #   <k-trials warning (stdlib only — NO SDK)
    python -m eval.scoring --run <path>    # score a real judge_run.jsonl (still NO calls)
    python -m eval.scoring --run <path> --fn-gate 0.0   # exit non-zero if fn_rate > gate

Dataset: data/qbank/judge_run.jsonl (sample synthetic trial log; real SME-owned log later).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Wiki §10.1 names data/qbank/judge_run.jsonl; real repo dir is data/qbank/ (exact match,
# §0 real-artifact-wins). eval/ is the real package (singular) — wiki §12.1 'evals/' loses.
RUN_PATH = Path(__file__).resolve().parent.parent / "data" / "qbank" / "judge_run.jsonl"

GATES = ("verify", "lane_match", "support")              # §10.1 / §4 three gates
GOLD_LABELS = ("PASS", "FAIL", "ABSTAIN")                # §10.1 SME ground truth (§3)
JUDGE_LABELS = ("PASS", "FAIL", "UNKNOWN")               # §10.1 judge output (§6.4 abstain)
K_MIN = 3                                                # §10.3 / §6.2 pass^k floor (k≥3)


# ── data ──────────────────────────────────────────────────────────────────────
def load_run(path: Path = RUN_PATH) -> list[dict]:
    """Load + validate a judge_run.jsonl trial log (one row per (claim,cited-span) trial).

    Schema (§10.1): gate, neg_class, gold_label, judge_label, item_id, trial_id.
    `_comment` lines (synthetic-fixture labels) are skipped.
    """
    assert path.exists(), f"judge_run not found: {path}"
    rows: list[dict] = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        if "_comment" in r and "gold_label" not in r:
            continue  # synthetic-label header line, not a trial row
        rid = r.get("item_id", f"line{i}")
        assert r.get("gate") in GATES, f"{rid}: bad gate {r.get('gate')!r}"
        assert r.get("gold_label") in GOLD_LABELS, \
            f"{rid}: bad gold_label {r.get('gold_label')!r}"
        assert r.get("judge_label") in JUDGE_LABELS, \
            f"{rid}: bad judge_label {r.get('judge_label')!r}"
        assert r.get("item_id"), f"line{i}: missing item_id"
        assert r.get("trial_id") is not None, f"{rid}: missing trial_id"
        rows.append(r)
    assert rows, "judge_run is empty"
    return rows


# ── §10.2 headline metric: precision/recall on should-FAIL (never raw agreement) ──
def fail_class_metrics(rows: list[dict]) -> dict:
    """§6.1/§4: should-FAIL confusion + headline fn_rate. Positive class = should-FAIL.

    The dangerous event (§3): gold FAIL & judge PASS — a bad claim waved through.
    A should-FAIL item the judge FAILs OR UNKNOWNs is CAUGHT (UNKNOWN declines to wave
    it through — §10.5 safe-fail). The precision counterpart is a should-PASS item the
    judge FAILs (over-block).
    """
    should_fail = [r for r in rows if r["gold_label"] == "FAIL"]
    should_pass = [r for r in rows if r["gold_label"] == "PASS"]
    sf = len(should_fail)
    fn = sum(1 for r in should_fail if r["judge_label"] == "PASS")   # leaked
    tp = sf - fn                                                      # caught (FAIL or UNKNOWN)
    fp = sum(1 for r in should_pass if r["judge_label"] == "FAIL")   # over-blocked should-PASS
    return {
        "should_fail_n": sf,
        "false_neg_n": fn,
        "fn_rate": round(fn / sf, 4) if sf else None,                # HEADLINE (None if no should-FAIL rows)
        "recall_fail": round(tp / sf, 4) if sf else None,
        "precision_fail": round(tp / (tp + fp), 4) if (tp + fp) else None,
        "false_neg_ids": sorted({r["item_id"] for r in should_fail if r["judge_label"] == "PASS"}),
    }


def _slice(rows: list[dict], key: str) -> dict:
    """FN-rate breakdown by a metadata column (§10.2 slices). Returns {value: metrics}."""
    groups: dict[str, list[dict]] = {}
    for r in rows:
        groups.setdefault(str(r.get(key, "?")), []).append(r)
    return {val: fail_class_metrics(grp) for val, grp in sorted(groups.items())}


# ── §10.3 pass^k consistency (k≥3) ──────────────────────────────────────────────
def _trial_pass(row: dict) -> bool:
    """§6/§10.5 rule: a trial passes iff the judge verdict is correct, EXCEPT judge
    UNKNOWN counts as a pass ONLY on should-FAIL items (it correctly declined to wave a
    bad claim through). On should-PASS / should-ABSTAIN items, UNKNOWN is a NON-pass."""
    if row["judge_label"] == "UNKNOWN":
        return row["gold_label"] == "FAIL"
    return row["judge_label"] == row["gold_label"]


def passk_report(rows: list[dict], k_min: int = K_MIN) -> dict:
    """Per-item pass^k (all k trials pass) and pass@k (any trial passes), k≥3.

    pass@k is computed ONLY to show the contrast Jaime should NOT be sold on (§10.3).
    Warns (does not silently average) when an item ran < k_min trials — §10.5: missing
    trials are a signal, not noise.
    """
    by_item: dict[str, list[dict]] = {}
    for r in rows:
        by_item.setdefault(r["item_id"], []).append(r)

    items = sorted(by_item)
    all_pass = {it: all(_trial_pass(r) for r in by_item[it]) for it in items}
    any_pass = {it: any(_trial_pass(r) for r in by_item[it]) for it in items}
    k_per_item = {it: len({r["trial_id"] for r in by_item[it]}) for it in items}
    under_k = sorted(it for it in items if k_per_item[it] < k_min)

    n = len(items)
    return {
        "items": n,
        "k_min": k_min,
        f"pass^{k_min}": round(sum(all_pass.values()) / n, 4) if n else None,   # the number Jaime hears
        f"pass@{k_min}": round(sum(any_pass.values()) / n, 4) if n else None,   # contrast only — do not ship on this
        "under_k_items": under_k,                                              # §10.5 isolation/coverage gap
        "k_per_item": k_per_item,
    }


# ── §10.4 abstention quality (two rates, tracked separately) ─────────────────────
def abstention_rates(rows: list[dict]) -> dict:
    """§6.3/§10.4: confabulation vs over-refusal, the doc's recoverability asymmetry.

    confabulation_rate = of should-ABSTAIN items, fraction the judge answered PASS
                         (unrecoverable — defend only a small number, §4.5.3).
    over_refusal_rate  = of answerable items (gold != ABSTAIN), fraction judge UNKNOWN'd
                         (recoverable — annoying, not dangerous).
    """
    abstain = [r for r in rows if r["gold_label"] == "ABSTAIN"]
    answerable = [r for r in rows if r["gold_label"] != "ABSTAIN"]
    confab = sum(1 for r in abstain if r["judge_label"] == "PASS")
    over = sum(1 for r in answerable if r["judge_label"] == "UNKNOWN")
    return {
        "abstain_n": len(abstain),
        "confabulation_rate": round(confab / len(abstain), 4) if abstain else None,
        "answerable_n": len(answerable),
        "over_refusal_rate": round(over / len(answerable), 4) if answerable else None,
    }


# ── report ──────────────────────────────────────────────────────────────────────
def _fmt_pct(x) -> str:
    return "n/a" if x is None else f"{x:.1%}"


def print_report(title: str, rows: list[dict]) -> None:
    head = fail_class_metrics(rows)
    pk = passk_report(rows)
    ab = abstention_rates(rows)
    print(f"\n── {title} ──")
    print(f"  trials={len(rows)}  items={pk['items']}  "
          f"(should_fail rows={head['should_fail_n']})")
    # HEADLINE — one number for Jaime (§12.3). Never raw agreement (§6 / §12.3).
    print(f"  HEADLINE false-negative rate on should-FAIL: {_fmt_pct(head['fn_rate'])} "
          f"[{head['false_neg_n']}/{head['should_fail_n']}]   "
          f"recall_fail={_fmt_pct(head['recall_fail'])}  precision_fail={_fmt_pct(head['precision_fail'])}")
    if head["false_neg_ids"]:
        print(f"  ⚠ FALSE NEGATIVES (bad claim waved through): {', '.join(head['false_neg_ids'])}")

    # SLICE 1 — by gate (§10.2). verify & lane_match must sit at ~0 FN; nonzero there means
    # something BROKE (regression), NOT "the judge needs calibration" (§1 / §10.5).
    print("  FN rate by gate (verify/lane_match ~0 = healthy; nonzero = a gate broke):")
    for g, m in _slice(rows, "gate").items():
        print(f"      {g:<11} fn_rate={_fmt_pct(m['fn_rate'])} [{m['false_neg_n']}/{m['should_fail_n']}]")

    # SLICE 2 — by negative class (§10.2 / §7.1 adversarial families). Tells you WHICH family
    # leaks so you add the right critiques (§5.3) instead of staring at one number.
    print("  FN rate by negative class (which adversarial family leaks):")
    sf_rows = [r for r in rows if r["gold_label"] == "FAIL"]
    for nc, m in _slice(sf_rows, "neg_class").items():
        print(f"      {nc:<22} fn_rate={_fmt_pct(m['fn_rate'])} [{m['false_neg_n']}/{m['should_fail_n']}]")

    # §10.3 consistency.
    km = pk["k_min"]
    caret = pk[f"pass^{km}"]
    at = pk[f"pass@{km}"]
    print(f"  Consistency (k≥{km}):  pass^{km}={_fmt_pct(caret)} "
          f"(the honest gate number)   pass@{km}={_fmt_pct(at)} (contrast only)")
    if pk["under_k_items"]:
        print(f"  ⚠ WARNING: {len(pk['under_k_items'])} item(s) ran < k={pk['k_min']} trials "
              f"({', '.join(pk['under_k_items'])}) — isolation/coverage gap (§10.5); "
              f"investigate before trusting the score.")

    # §10.4 abstention.
    print(f"  Confabulation rate (should-abstain answered PASS): {_fmt_pct(ab['confabulation_rate'])} "
          f"← unrecoverable (§4.5.3)")
    print(f"  Over-refusal rate (answerable judged UNKNOWN):     {_fmt_pct(ab['over_refusal_rate'])} "
          f"← recoverable")


# ── offline self-test fixture (SYNTHETIC; mirrors §12.2 minimum test cases) ──────
def _synthetic_run() -> list[dict]:
    """SYNTHETIC seeded judge_run used by the offline self-test (no SDK, no I/O).

    Engineered so the scorer's own behavior is asserted (an ORACLE-clean item, a KNOWN
    false negative, an abstention pair, and a <k-trials item that must warn). The on-disk
    data/qbank/judge_run.jsonl is the file-backed twin of this and is also clearly labeled
    synthetic. These rows cover the §12.2 minimum-test-case matrix:
      should-FAIL+PASS→FN · should-FAIL+FAIL→caught · should-FAIL+UNKNOWN→safe-pass ·
      should-PASS+UNKNOWN→non-pass · should-ABSTAIN+PASS→confabulation · <3 trials→warn.
    """
    rows: list[dict] = []

    def trio(item_id, gate, neg_class, gold, judges):
        for t, j in enumerate(judges, 1):
            rows.append({"_synthetic": True, "item_id": item_id, "gate": gate,
                         "neg_class": neg_class, "gold_label": gold,
                         "judge_label": j, "trial_id": t})

    # should-PASS positive, judge always PASS  → clean, pass^3
    trio("SYN-pos-1", "support", "positive", "PASS", ["PASS", "PASS", "PASS"])
    # should-FAIL caught every trial (FAIL / UNKNOWN are both "caught") → pass^3, no FN
    trio("SYN-fail-caught", "support", "plausible_unsupported", "FAIL", ["FAIL", "UNKNOWN", "FAIL"])
    # should-FAIL LEAKED on ≥1 trial (judge PASS) → KNOWN false negative; breaks pass^3
    trio("SYN-fail-leak", "support", "near_miss_paraphrase", "FAIL", ["FAIL", "PASS", "FAIL"])
    # should-ABSTAIN answered PASS → confabulation increments
    trio("SYN-abstain-confab", "support", "should_abstain", "ABSTAIN", ["PASS", "UNKNOWN", "UNKNOWN"])
    # answerable should-PASS judged UNKNOWN → over-refusal + a NON-pass trial
    trio("SYN-pass-overrefuse", "support", "positive", "PASS", ["PASS", "UNKNOWN", "PASS"])
    # deterministic gate rows (sliced separately; healthy = 0 FN)
    trio("SYN-lane-ok", "lane_match", "cross_lane", "FAIL", ["FAIL", "FAIL", "FAIL"])
    # item with < k trials → pass^k must WARN
    rows.append({"_synthetic": True, "item_id": "SYN-under-k", "gate": "verify",
                 "neg_class": "positive", "gold_label": "PASS", "judge_label": "PASS", "trial_id": 1})
    return rows


def _self_test() -> None:
    """Assert the scorer on the synthetic fixture. Guards the eval itself so a metric bug
    can't hide behind a green run (mirrors triage_eval/judge_eval offline baselines)."""
    rows = _synthetic_run()

    # ORACLE: drop the one engineered leak → every should-FAIL caught, fn_rate must be 0.
    oracle = [dict(r, judge_label=("FAIL" if r["gold_label"] == "FAIL" else r["judge_label"]))
              for r in rows]
    om = fail_class_metrics(oracle)
    print_report("ORACLE (every should-FAIL caught; sanity floor)", oracle)
    assert om["fn_rate"] == 0.0, f"scorer broken: oracle fn_rate must be 0, got {om['fn_rate']}"

    # REAL synthetic run: the engineered leak must surface as exactly one FN item.
    rm = fail_class_metrics(rows)
    print_report("SYNTHETIC judge_run (one engineered leak + an abstention case)", rows)
    assert rm["false_neg_n"] == 1, f"expected exactly 1 false negative, got {rm['false_neg_n']}"
    assert rm["false_neg_ids"] == ["SYN-fail-leak"], rm["false_neg_ids"]
    assert rm["fn_rate"] is not None and rm["fn_rate"] > 0, "leak must drive fn_rate > 0"

    # pass^k: the leaked item breaks pass^3; pass@3 stays high → the exact contrast §10.3 warns about.
    pk = passk_report(rows)
    assert pk[f"pass^{K_MIN}"] < pk[f"pass@{K_MIN}"], \
        "pass^k must be < pass@k when an item is inconsistent (the §10.3 contrast)"
    # SYN-fail-leak (1 leaked trial) and SYN-abstain-confab (PASS on abstain) and
    # SYN-pass-overrefuse (UNKNOWN on should-PASS) are the three non-pass^k items.
    assert pk[f"pass^{K_MIN}"] == round(4 / 7, 4), f"unexpected pass^k {pk[f'pass^{K_MIN}']}"

    # <k-trials warning fires for exactly the one under-k item.
    assert pk["under_k_items"] == ["SYN-under-k"], pk["under_k_items"]

    # §10.5 safe-fail: should-FAIL + UNKNOWN is a PASS trial; should-PASS + UNKNOWN is NOT.
    assert _trial_pass({"gold_label": "FAIL", "judge_label": "UNKNOWN"}) is True
    assert _trial_pass({"gold_label": "PASS", "judge_label": "UNKNOWN"}) is False
    assert _trial_pass({"gold_label": "ABSTAIN", "judge_label": "UNKNOWN"}) is False

    # Abstention rates: one confabulation (PASS on the abstain item), one over-refusal.
    ab = abstention_rates(rows)
    assert ab["confabulation_rate"] is not None and ab["confabulation_rate"] > 0, \
        "should-abstain answered PASS must register confabulation"
    assert ab["over_refusal_rate"] is not None and ab["over_refusal_rate"] > 0, \
        "answerable judged UNKNOWN must register over-refusal"


# ── main ──────────────────────────────────────────────────────────────────────
def main() -> int:
    ap = argparse.ArgumentParser(description="Diagnostic scoring layer over judge_run.jsonl "
                                             "(stdlib; no model calls). Wiki §10.")
    ap.add_argument("--run", type=Path, default=None,
                    help="score a real judge_run.jsonl (default: run the offline self-test "
                         "on a seeded synthetic run — no file needed)")
    ap.add_argument("--fn-gate", type=float, default=0.0,
                    help="max acceptable should-FAIL false-negative rate (default 0.0 — "
                         "an FN ships a wrong fact). Applies only with --run.")
    args = ap.parse_args()

    if args.run is None:
        # OFFLINE: prove the scorer with the seeded synthetic fixture. Stdlib only, no SDK.
        print("Scoring layer (§10) — OFFLINE self-test on a SYNTHETIC seeded judge_run "
              "(no model calls, no SDK).")
        _self_test()
        print("\nOFFLINE OK — headline fn_rate, gate/neg_class slices, pass^k vs pass@k, "
              "and abstention rates all computed and asserted as specified (§10.1–§10.5).")
        print(f"Run `python -m eval.scoring --run {RUN_PATH}` to score the sample log, or "
              f"point --run at a real judge_run.jsonl.")
        return 0

    # Score a judge_run.jsonl (still NO model calls — the judge is an input here).
    rows = load_run(args.run)
    syn = any(r.get("_synthetic") or r.get("synthetic") for r in rows)
    print(f"Scoring layer (§10) — {len(rows)} trial rows from {args.run}"
          + ("  [SYNTHETIC sample]" if syn else ""))
    print_report(f"judge_run: {args.run.name}", rows)

    head = fail_class_metrics(rows)
    pk = passk_report(rows)
    fn_rate = head["fn_rate"] or 0.0
    failed = False
    if fn_rate > args.fn_gate:
        print(f"\nFAIL — should-FAIL fn_rate {fn_rate:.2%} exceeds gate {args.fn_gate:.2%} "
              f"(a bad claim was waved through — unrecoverable, §3).")
        failed = True
    if pk["under_k_items"]:
        print(f"FAIL — {len(pk['under_k_items'])} item(s) ran < k={pk['k_min']} trials; "
              f"a publish-gate reading needs k≥{pk['k_min']} (§10.3/§6.2).")
        failed = True
    if failed:
        return 1
    print(f"\nPASS — fn_rate {fn_rate:.2%} within gate {args.fn_gate:.2%}; "
          f"every item ran ≥{pk['k_min']} trials. (Over-refusal is tracked, not gated.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
