"""Falsification test for the question-bank gate (build order: commit 1).

Runs the three-check gate against the adversarial fixture and asserts every case
reaches its expected verdict. This is the one thing we are trying to falsify:
that the gate refuses cross-lane and semantically-inverted citations.

Run:  python test_qbank_gate.py
(asyncio.run uses the Windows ProactorEventLoop, so the SDK judge can spawn.)
"""
import asyncio
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import qbank_gate
from qbank_gate import gate_question, llm_support_judge

FIXTURE = Path(__file__).parent / "data" / "qbank" / "adversarial_fixture.json"


async def main() -> int:
    cases = json.loads(FIXTURE.read_text(encoding="utf-8"))["cases"]
    print(f"Running gate against {len(cases)} adversarial cases…\n")
    rows, failures = [], 0
    for c in cases:
        spans_by_id = {s["span_id"]: s for s in c["spans"]}
        res = await gate_question(c["question"], spans_by_id, judge=llm_support_judge)
        ok = res["verdict"] == c["expect"]
        failures += not ok
        checks = f"lane={res['lane_ok']} verbatim={res['verbatim_ok']} support={res['support_ok']}"
        rows.append((("PASS" if ok else "XXXX"), c["name"], c["expect"], res["verdict"], checks,
                     "; ".join(res["reasons"])[:90]))

    w = max(len(r[1]) for r in rows)
    print(f"{'test':5} {'case':<{w}}  {'want':<8} {'got':<8} checks")
    print("-" * (w + 60))
    for mark, name, want, got, checks, reason in rows:
        print(f"{mark:5} {name:<{w}}  {want:<8} {got:<8} {checks}")
        if reason:
            print(f"{'':5} {'':<{w}}  └─ {reason}")
    print()
    if failures:
        print(f"❌ {failures}/{len(cases)} cases did NOT reach expected verdict — gate is unsound.")
        return 1
    print(f"✅ All {len(cases)} cases reached expected verdict. Lane purity + semantic-support hold.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
