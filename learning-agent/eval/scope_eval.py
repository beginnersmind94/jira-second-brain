"""Scope-resolution eval — calibration of the intent agent's MODULE decision.

The intent agent's most dangerous error is the DP9 failure: confidently resolving a
request to the WRONG module (or grounding a not-built area on some present module's
tickets). That produces a verified-looking guide about the wrong feature. So, exactly
like the triage classifier's FNR, the gated metric here is the **wrong-module rate**:
how often the agent commits to a confident module it should not have.

Three case kinds (balanced so a degenerate "always pick a module" agent is exposed):
  - `module`     — a clear request; the agent SHOULD resolve the named module.
  - `ambiguous`  — no clear module; the agent SHOULD ask a clarifying question.
  - `no_fixture` — a real product area with no grounded data; the agent SHOULD refuse
                   (NOT map it onto a present module).

Outcomes from the resolver: resolved a module / asked (clarify) / refused.
  - **wrong_module (DANGEROUS · gated):** committed to a module that's wrong —
    a `module` case resolved to the wrong one, OR an `ambiguous`/`no_fixture` case
    resolved to *any* module (it should have asked/refused).
  - **correct:** module→right module; ambiguous→asked; no_fixture→refused.
  - **over_ask / over_refuse (friction · tracked):** asked/refused a clear module case,
    or refused an ambiguous one — conservative, not dangerous.

Usage:
    python -m eval.scope_eval           # OFFLINE: oracle + degenerate baseline (no auth)
    python -m eval.scope_eval --live    # run the real resolver; non-zero exit if wrong_module > gate
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import intent_agent

CASES_PATH = Path(__file__).resolve().parent / "scope_cases.jsonl"
# The modules that have offline fixtures (must match demo_app.AVAILABLE_MODULES).
AVAILABLE = ["Account Management", "Accountability", "Eligibility", "Insights",
             "Inventory", "Item Management", "Menu Planning"]


def load_cases() -> list[dict]:
    out = []
    for line in CASES_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def classify(case: dict, decision: dict) -> str:
    """decision = {module|None, asked:bool, refused:bool} -> outcome label."""
    mod = decision.get("module")
    asked = decision.get("asked")
    refused = decision.get("refused")
    kind = case["kind"]
    if kind == "module":
        if mod == case["expect"]:
            return "correct"
        if mod:                      # resolved a DIFFERENT module
            return "wrong_module"
        return "over_ask" if asked else "over_refuse"   # conservative miss
    if kind == "ambiguous":
        if asked:
            return "correct"
        if mod:                      # guessed a module on an ambiguous request
            return "wrong_module"
        return "over_refuse"
    # no_fixture
    if refused:
        return "correct"
    if mod:                          # grounded a not-built area onto a present module
        return "wrong_module"
    return "correct"                 # asked instead of refused — still didn't ground wrongly


def score(cases, decisions) -> dict:
    labels = [classify(c, d) for c, d in zip(cases, decisions)]
    n = len(cases)
    tally = {}
    for lb in labels:
        tally[lb] = tally.get(lb, 0) + 1
    wrong = tally.get("wrong_module", 0)
    friction = tally.get("over_ask", 0) + tally.get("over_refuse", 0)
    return {
        "n": n, "tally": tally,
        "wrong_module": wrong,
        "wrong_module_rate": round(wrong / n, 4) if n else 0.0,   # gated, dangerous
        "friction": friction,
        "friction_rate": round(friction / n, 4) if n else 0.0,    # tracked
        "correct": tally.get("correct", 0),
        "accuracy": round(tally.get("correct", 0) / n, 4) if n else 0.0,
        "wrong_ids": [c["id"] for c, lb in zip(cases, labels) if lb == "wrong_module"],
        "labels": dict(zip([c["id"] for c in cases], labels)),
    }


def report(title, rep):
    print(f"\n── {title} ──")
    print(f"  cases={rep['n']}  tally={rep['tally']}")
    print(f"  WRONG-MODULE rate (DANGEROUS · gated): {rep['wrong_module_rate']:.2%}  [{rep['wrong_module']}/{rep['n']}]")
    print(f"  friction rate (over-ask/refuse · tracked): {rep['friction_rate']:.2%}")
    print(f"  accuracy={rep['accuracy']:.2%}")
    if rep["wrong_ids"]:
        print(f"  ⚠ wrong-module on: {', '.join(rep['wrong_ids'])}")


# ── predictors ────────────────────────────────────────────────────────────────
def predict_oracle(cases):
    out = []
    for c in cases:
        if c["kind"] == "module":
            out.append({"module": c["expect"], "asked": False, "refused": False})
        elif c["kind"] == "ambiguous":
            out.append({"module": None, "asked": True, "refused": False})
        else:
            out.append({"module": None, "asked": False, "refused": True})
    return out


def predict_always_first_module(cases):
    return [{"module": AVAILABLE[0], "asked": False, "refused": False} for _ in cases]


async def predict_live(cases, concurrency=4):
    opts = intent_agent.build_resolver_options()
    sem = asyncio.Semaphore(concurrency)
    from claude_agent_sdk import AssistantMessage, TextBlock, query

    async def one(c):
        async with sem:
            parts = []
            try:
                async for m in query(prompt=intent_agent.build_resolver_prompt(c["request"], AVAILABLE),
                                     options=opts):
                    if isinstance(m, AssistantMessage):
                        for b in (m.content or []):
                            if isinstance(b, TextBlock):
                                parts.append(b.text)
                j = intent_agent.parse_json("\n".join(parts)) or {}
            except Exception:
                j = {}
            mod = j.get("module")
            if mod not in AVAILABLE:
                mod = None
            return {"module": mod, "asked": bool(j.get("ambiguous")), "refused": bool(j.get("refused"))}

    return list(await asyncio.gather(*(one(c) for c in cases)))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--wrong-gate", type=float, default=0.0, help="max wrong-module rate in --live (default 0.0)")
    args = ap.parse_args()
    cases = load_cases()
    kinds = {}
    for c in cases:
        kinds[c["kind"]] = kinds.get(c["kind"], 0) + 1
    print(f"Scope eval — {len(cases)} cases; kinds: {kinds}")

    if not args.live:
        o = score(cases, predict_oracle(cases)); report("ORACLE (sanity floor)", o)
        assert o["wrong_module"] == 0 and o["accuracy"] == 1.0, "scorer broken: oracle must be perfect"
        b = score(cases, predict_always_first_module(cases))
        report("BASELINE always-pick-first-module (exposes guessing)", b)
        assert b["wrong_module"] > 0, "degenerate baseline must produce wrong-module hits"
        print("\nOFFLINE OK — scorer correct; wrong-module is the gated dangerous metric.")
        print("Run `python -m eval.scope_eval --live` to score the real resolver (needs auth).")
        return 0

    decisions = asyncio.run(predict_live(cases))
    rep = score(cases, decisions)
    report("LIVE resolver (intent_agent.build_resolver_*)", rep)
    if rep["wrong_module_rate"] > args.wrong_gate:
        print(f"\nFAIL — wrong-module {rep['wrong_module_rate']:.2%} exceeds gate {args.wrong_gate:.2%} (the dangerous direction).")
        return 1
    print(f"\nPASS — wrong-module {rep['wrong_module_rate']:.2%} within gate {args.wrong_gate:.2%}. "
          f"(friction {rep['friction_rate']:.2%} is tracked, not gated.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
