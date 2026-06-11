"""Semantic-support judge eval — separate FPR / FNR, FNR is the gated metric.

The question-bank gate's third check (`qbank_gate.llm_support_judge`) is an LLM
judge: given a SOURCE quote and a quiz STEM + PROPOSED CORRECT ANSWER, does the
quote — read literally — support that answer? It catches what verbatim/lane checks
cannot: inversions (a minimum stated as a maximum), number/unit swaps, qualifier
drops, over-claims, and on-topic-but-non-responsive answers. This eval measures the
*judge's* discrimination, not the deterministic checks ahead of it.

Structured like the triage / scope evals (and Anthropic's Claude Code classifier
work): report two rates separately and weight toward the dangerous one.

  • FNR — the DANGEROUS miss: an actually-UNSUPPORTED case judged "supported". That
    is a defective question (inverted rule, swapped number, dropped qualifier) waved
    into `verified`. **Gated metric** (default --fnr-gate 0.0).
      FNR = (# unsupported judged supported) / (# unsupported)
  • FPR — over-rejection: an actually-SUPPORTED case judged "unsupported". Costs a
    good question, but never ships a wrong fact — tracked as friction, not failure.
      FPR = (# supported judged unsupported) / (# supported)

"supported" is the judge's affirmative output; "unsupported" is the negative. We map
`qbank_gate.llm_support_judge`'s `{"ok": True}` → "supported", `{"ok": False}` →
"unsupported". When the judge errors or is unparseable in --live, we count it as
"unsupported" (the safe direction — it can only add a friction false positive, never
a dangerous false negative).

Usage:
    python -m eval.judge_eval            # OFFLINE: validate dataset + scorer via an
                                         #   oracle + two degenerate baselines
                                         #   (stdlib only — NO SDK / no auth)
    python -m eval.judge_eval --live     # run the REAL judge (needs auth);
                                         #   exit non-zero if FNR > gate
    python -m eval.judge_eval --live --fnr-gate 0.0 --concurrency 4

Dataset: eval/judge_gold_set.jsonl. Each line carries:
    id, lane, source_anchor, quote, stem, answer (the proposed correct answer),
    ground_truth_support ("supported" | "unsupported"), defect_type, rationale.
Some cases are synthetic EVAL FIXTURES (product-lane, sourced from demo fixtures and
labeled "Synthetic EVAL FIXTURE" in their rationale); the rest are grounded in real
ICN workbook / Jira-fixture quotes. `source` provenance is in each case's rationale.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

GOLD_PATH = Path(__file__).resolve().parent / "judge_gold_set.jsonl"
LABELS = ("supported", "unsupported")
# What the scorer counts a judge result as when --live errors / is unparseable.
# "unsupported" is safe: it can only manufacture a (friction) false positive, never
# a (dangerous) false negative.
SAFE_DEFAULT = "unsupported"


# ── data ────────────────────────────────────────────────────────────────────────
def load_cases() -> list[dict]:
    """Load + validate the gold set. Asserts well-formed, non-empty, both labels."""
    assert GOLD_PATH.exists(), f"gold set not found: {GOLD_PATH}"
    cases: list[dict] = []
    for i, line in enumerate(GOLD_PATH.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        c = json.loads(line)
        cid = c.get("id", f"line{i}")
        assert c.get("ground_truth_support") in LABELS, \
            f"{cid}: bad ground_truth_support {c.get('ground_truth_support')!r}"
        for field in ("quote", "stem", "answer"):
            assert c.get(field), f"{cid}: missing/empty required field {field!r}"
        cases.append(c)
    assert cases, "gold set is empty"
    present = {c["ground_truth_support"] for c in cases}
    assert present == set(LABELS), \
        f"gold set must contain BOTH labels; found only {sorted(present)}"
    return cases


# ── scoring ───────────────────────────────────────────────────────────────────
def score(cases: list[dict], preds: list[str]) -> dict:
    """Confusion matrix + FNR/FPR.

    Positive class (must-catch) = an UNSUPPORTED case the judge must NOT pass.
    The dangerous error is an unsupported case judged "supported" → FALSE NEGATIVE.
    """
    n_unsup = sum(1 for c in cases if c["ground_truth_support"] == "unsupported")
    n_sup = sum(1 for c in cases if c["ground_truth_support"] == "supported")
    fn = fp = tp = tn = 0
    fn_ids = []  # DANGEROUS: unsupported judged supported (a bad question waved in)
    fp_ids = []  # friction: supported judged unsupported (a good question rejected)
    for c, p in zip(cases, preds):
        g = c["ground_truth_support"]
        if g == "unsupported" and p == "unsupported":
            tp += 1                       # correctly caught the defective case
        elif g == "unsupported" and p == "supported":
            fn += 1                       # MISS — defective case passed
            fn_ids.append(c["id"])
        elif g == "supported" and p == "supported":
            tn += 1                       # correctly accepted a good case
        elif g == "supported" and p == "unsupported":
            fp += 1                       # over-rejected a good case
            fp_ids.append(c["id"])
    fnr = (fn / n_unsup) if n_unsup else 0.0
    fpr = (fp / n_sup) if n_sup else 0.0
    agree = ((tp + tn) / len(cases)) if cases else 0.0
    return {
        "n": len(cases), "n_unsupported": n_unsup, "n_supported": n_sup,
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "fnr": round(fnr, 4), "fpr": round(fpr, 4), "agreement": round(agree, 4),
        "false_negative_ids": fn_ids, "false_positive_ids": fp_ids,
    }


def defect_split(cases: list[dict]) -> dict:
    out: dict[str, int] = {}
    for c in cases:
        key = c.get("defect_type") or "supported(control)"
        out[key] = out.get(key, 0) + 1
    return out


def print_report(title: str, rep: dict) -> None:
    print(f"\n── {title} ──")
    print(f"  cases={rep['n']}  (unsupported={rep['n_unsupported']}, supported={rep['n_supported']})")
    print(f"  FNR (unsupported judged 'supported' · DANGEROUS · gated): {rep['fnr']:.2%}   "
          f"[{rep['fn']}/{rep['n_unsupported']}]")
    print(f"  FPR (supported judged 'unsupported' · friction · tracked): {rep['fpr']:.2%}   "
          f"[{rep['fp']}/{rep['n_supported']}]")
    print(f"  agreement={rep['agreement']:.2%}")
    if rep["false_negative_ids"]:
        print(f"  ⚠ FALSE NEGATIVES (defective question waved in): {', '.join(rep['false_negative_ids'])}")
    if rep["false_positive_ids"]:
        print(f"  false positives (good question rejected): {', '.join(rep['false_positive_ids'])}")


# ── predictors ────────────────────────────────────────────────────────────────
def predict_oracle(cases):            return [c["ground_truth_support"] for c in cases]
def predict_always_supported(cases):  return ["supported"] * len(cases)
def predict_always_unsupported(cs):   return ["unsupported"] * len(cs)


async def predict_live(cases: list[dict], concurrency: int = 4) -> list[str]:
    """Run the REAL semantic-support judge (qbank_gate.llm_support_judge). Needs auth.

    The judge sees exactly what the gate gives it — (quote, stem, correct_answer) —
    mirroring qbank_gate.gate_question's third check. The gold set's `answer` field
    IS the proposed correct answer. `{"ok": True}` → "supported".
    """
    import qbank_gate
    sem = asyncio.Semaphore(concurrency)

    async def one(c):
        async with sem:
            try:
                verdict = await qbank_gate.llm_support_judge(c["quote"], c["stem"], c["answer"])
                return "supported" if verdict.get("ok") else "unsupported"
            except Exception:
                return SAFE_DEFAULT  # error/unparseable → safe (can only add a false positive)

    return list(await asyncio.gather(*(one(c) for c in cases)))


# ── main ──────────────────────────────────────────────────────────────────────
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="run the real judge (needs auth)")
    ap.add_argument("--fnr-gate", type=float, default=0.0,
                    help="max acceptable FNR in --live mode (default 0.0 — these are "
                         "clear-cut, deliberately-labeled cases; any miss ships a wrong fact)")
    ap.add_argument("--concurrency", type=int, default=4)
    args = ap.parse_args()

    cases = load_cases()
    print(f"Judge eval — {len(cases)} cases; defect split: {defect_split(cases)}")

    if not args.live:
        # Offline: prove the dataset + scorer with an oracle and two degenerate
        # baselines. Stdlib only — no SDK, no auth. These assertions guard the eval
        # itself, so a model failure can't hide behind a broken scorer.
        oracle = predict_oracle(cases)
        rep_o = score(cases, oracle)
        print_report("ORACLE (pred = label; sanity floor)", rep_o)
        assert rep_o["fnr"] == 0.0 and rep_o["fpr"] == 0.0, "scorer broken: oracle must be perfect"

        sup = predict_always_supported(cases)
        rep_s = score(cases, sup)
        print_report("BASELINE always-'supported' (rubber-stamp: catches nothing)", rep_s)
        assert rep_s["fnr"] == 1.0 and rep_s["fpr"] == 0.0, \
            "always-'supported' must be FNR=1.0 (every unsupported case waved in), FPR=0.0"

        unsup = predict_always_unsupported(cases)
        rep_u = score(cases, unsup)
        print_report("BASELINE always-'unsupported' (reject-all: passes nothing)", rep_u)
        assert rep_u["fnr"] == 0.0 and rep_u["fpr"] == 1.0, \
            "always-'unsupported' must be FNR=0.0, FPR=1.0 (every supported case rejected)"

        print("\nOFFLINE OK — gold set well-formed (both labels present), scorer correct "
              "(FNR/FPR computed as specified).")
        print("Run `python -m eval.judge_eval --live` to score the real judge "
              "(qbank_gate.llm_support_judge; needs auth).")
        return 0

    # Live: score the real judge.
    preds = asyncio.run(predict_live(cases, concurrency=args.concurrency))
    rep = score(cases, preds)
    print_report("LIVE judge (qbank_gate.llm_support_judge)", rep)
    if rep["fnr"] > args.fnr_gate:
        print(f"\nFAIL — FNR {rep['fnr']:.2%} exceeds gate {args.fnr_gate:.2%} "
              f"(an unsupported case judged 'supported' ships a wrong fact).")
        return 1
    print(f"\nPASS — FNR {rep['fnr']:.2%} within gate {args.fnr_gate:.2%}. "
          f"(FPR {rep['fpr']:.2%} is friction-only.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
