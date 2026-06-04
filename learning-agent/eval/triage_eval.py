"""Edit-triage classifier eval — separate FPR / FNR, FNR is the gated metric.

The review gate's triage router tags each AI-assisted edit `stylistic`
(wording/format — fast-path to approve) or `substantive` (a claim/number/label/
step may have changed — read closely). It is ADVISORY: the deterministic
grounding gate re-runs after every edit regardless, so the router can never
weaken grounding. This eval measures *routing quality*, not grounding.

Structured the way Anthropic structures their Claude Code "auto mode" classifier
eval (How we built Claude Code auto mode, Mar 2026): report two rates separately
and weight toward the dangerous one.

  • FNR — under-trigger: a SUBSTANTIVE edit mislabeled `stylistic`. This is the
    dangerous direction (a changed claim fast-paths). **Gated metric.**
  • FPR — over-trigger: a STYLISTIC edit mislabeled `substantive`. Only costs an
    extra (free) check — tracked as friction, not failure.

Usage:
    python -m eval.triage_eval            # OFFLINE: validate dataset + scorer
                                          #   via oracle + degenerate baselines
                                          #   (no SDK / no auth needed)
    python -m eval.triage_eval --live     # run the REAL classifier (needs auth);
                                          #   exit non-zero if FNR > gate
    python -m eval.triage_eval --live --fnr-gate 0.0 --trials 1

Dataset: eval/triage_cases.jsonl  (balanced; `source` tags synthetic vs real).
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import revise

CASES_PATH = Path(__file__).resolve().parent / "triage_cases.jsonl"
LABELS = ("stylistic", "substantive")
SAFE_DEFAULT = "substantive"  # what the router emits when unsure / unparseable


# ── data ──────────────────────────────────────────────────────────────────────
def load_cases() -> list[dict]:
    cases = []
    for line in CASES_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        c = json.loads(line)
        assert c["gold"] in LABELS, f"{c['id']}: bad gold {c['gold']!r}"
        cases.append(c)
    return cases


# ── scoring ─────────────────────────────────────────────────────────────────
def score(cases: list[dict], preds: list[str]) -> dict:
    """Confusion matrix + FPR/FNR. 'substantive' is the positive class (must-catch)."""
    n_sub = sum(1 for c in cases if c["gold"] == "substantive")
    n_sty = sum(1 for c in cases if c["gold"] == "stylistic")
    fn = fp = tp = tn = 0
    misses = []  # the dangerous ones: substantive called stylistic
    overs = []   # stylistic called substantive
    for c, p in zip(cases, preds):
        g = c["gold"]
        if g == "substantive" and p == "substantive":
            tp += 1
        elif g == "substantive" and p == "stylistic":
            fn += 1
            misses.append(c["id"])
        elif g == "stylistic" and p == "stylistic":
            tn += 1
        elif g == "stylistic" and p == "substantive":
            fp += 1
            overs.append(c["id"])
    fnr = (fn / n_sub) if n_sub else 0.0
    fpr = (fp / n_sty) if n_sty else 0.0
    acc = ((tp + tn) / len(cases)) if cases else 0.0
    return {
        "n": len(cases), "n_substantive": n_sub, "n_stylistic": n_sty,
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "fnr": round(fnr, 4), "fpr": round(fpr, 4), "accuracy": round(acc, 4),
        "under_trigger_ids": misses, "over_trigger_ids": overs,
    }


def source_split(cases: list[dict]) -> dict:
    out: dict[str, int] = {}
    for c in cases:
        out[c.get("source", "unknown")] = out.get(c.get("source", "unknown"), 0) + 1
    return out


def print_report(title: str, cases: list[dict], preds: list[str], rep: dict) -> None:
    print(f"\n── {title} ──")
    print(f"  cases={rep['n']}  (substantive={rep['n_substantive']}, stylistic={rep['n_stylistic']})")
    print(f"  FNR (under-trigger · DANGEROUS · gated): {rep['fnr']:.2%}   "
          f"[{rep['fn']}/{rep['n_substantive']} substantive edits mislabeled stylistic]")
    print(f"  FPR (over-trigger · friction · tracked): {rep['fpr']:.2%}   "
          f"[{rep['fp']}/{rep['n_stylistic']} stylistic edits mislabeled substantive]")
    print(f"  accuracy={rep['accuracy']:.2%}")
    if rep["under_trigger_ids"]:
        print(f"  ⚠ UNDER-TRIGGERS (let a claim through): {', '.join(rep['under_trigger_ids'])}")
    if rep["over_trigger_ids"]:
        print(f"  over-triggers (extra check): {', '.join(rep['over_trigger_ids'])}")


# ── predictors ────────────────────────────────────────────────────────────────
def predict_oracle(cases):           return [c["gold"] for c in cases]
def predict_always_substantive(cs):  return ["substantive"] * len(cs)
def predict_always_stylistic(cs):    return ["stylistic"] * len(cs)


async def _run_text(prompt: str, options) -> str:
    """Run the tool-less triage classifier to completion; return final text."""
    from claude_agent_sdk import AssistantMessage, TextBlock, query
    parts: list[str] = []
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in (message.content or []):
                if isinstance(block, TextBlock):
                    parts.append(block.text)
    return "\n".join(parts).strip()


async def predict_live(cases: list[dict], concurrency: int = 4) -> list[str]:
    """Run the REAL triage classifier (revise.build_triage_*). Needs Claude auth."""
    opts = revise.build_triage_options()
    sem = asyncio.Semaphore(concurrency)

    async def one(c):
        async with sem:
            try:
                text = await _run_text(revise.build_triage_prompt(c["instruction"], c["ops"]), opts)
                parsed = revise.parse_json(text) or {}
                cls = parsed.get("classification")
                return cls if cls in LABELS else SAFE_DEFAULT
            except Exception:
                return SAFE_DEFAULT  # unparseable / error → safe default (substantive)

    return list(await asyncio.gather(*(one(c) for c in cases)))


# ── main ───────────────────────────────────────────────────────────────────────
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="run the real classifier (needs auth)")
    ap.add_argument("--fnr-gate", type=float, default=0.0,
                    help="max acceptable FNR in --live mode (default 0.0 — this is a curated clear-cut set)")
    ap.add_argument("--concurrency", type=int, default=4)
    args = ap.parse_args()

    cases = load_cases()
    print(f"Triage eval — {len(cases)} cases; source split: {source_split(cases)}")
    if all(c.get("source") == "synthetic" for c in cases):
        print("  NOTE: all cases are synthetic. Collect REAL reviewer edits from usage "
              "logs and add them (Anthropic: evaluate on real traffic, not only synthetic).")

    if not args.live:
        # Offline: prove the dataset + scorer with an oracle and the degenerate baselines.
        # (No SDK / no auth.) These assertions guard the eval itself.
        oracle = predict_oracle(cases)
        rep_o = score(cases, oracle)
        print_report("ORACLE (gold = pred; sanity floor)", cases, oracle, rep_o)
        assert rep_o["fnr"] == 0 and rep_o["fpr"] == 0, "scorer broken: oracle must be perfect"

        sub = predict_always_substantive(cases)
        rep_s = score(cases, sub)
        print_report("BASELINE always-'substantive' (exposes no-discrimination)", cases, sub, rep_s)
        assert rep_s["fnr"] == 0 and rep_s["fpr"] == 1.0, "always-substantive must be FNR=0, FPR=1"

        sty = predict_always_stylistic(cases)
        rep_t = score(cases, sty)
        print_report("BASELINE always-'stylistic' (worst case: misses everything)", cases, sty, rep_t)
        assert rep_t["fnr"] == 1.0 and rep_t["fpr"] == 0, "always-stylistic must be FNR=1, FPR=0"

        print("\nOFFLINE OK — dataset balanced, scorer correct (FNR/FPR computed as specified).")
        print("Run `python -m eval.triage_eval --live` to score the real classifier (needs auth).")
        return 0

    # Live: score the real classifier.
    preds = asyncio.run(predict_live(cases, concurrency=args.concurrency))
    rep = score(cases, preds)
    print_report("LIVE classifier (revise.build_triage_*)", cases, preds, rep)
    if rep["fnr"] > args.fnr_gate:
        print(f"\nFAIL — FNR {rep['fnr']:.2%} exceeds gate {args.fnr_gate:.2%} "
              f"(under-trigger is the dangerous direction).")
        return 1
    print(f"\nPASS — FNR {rep['fnr']:.2%} within gate {args.fnr_gate:.2%}. "
          f"(FPR {rep['fpr']:.2%} is friction-only.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
