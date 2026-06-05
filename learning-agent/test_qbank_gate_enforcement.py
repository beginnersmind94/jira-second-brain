"""Proof the gate works — run BEFORE building generation.

Headline: a `needs_human` item cannot reach the bank — enforced independently at
(1) the deterministic commit_to_bank guard and (2) the PreToolUse hook. Also covers
the state machine, the human callback, and the adversarial triage case (a true-substring
quote that fails semantic support is routed to a human, not auto-approved).

Run:  python test_qbank_gate_enforcement.py
"""
import asyncio
import sys
import tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import qbank_curation as core
from qbank_curation import (Stores, TRANSITIONS, AUTO_APPROVED, NEEDS_HUMAN,
                            HUMAN_APPROVED, COMMITTED, PENDING_REVIEW, score_candidate)
import qbank_gate_hooks as gate
from qbank_gate_hooks import commit_gate_hook, make_human_callback, COMMIT_TOOL
from claude_agent_sdk import PermissionResultAllow, PermissionResultDeny

PASS, FAIL = "  ✓", "  ✗ FAIL:"
fails = 0
def check(cond, msg):
    global fails
    print((PASS if cond else FAIL), msg)
    fails += not cond


async def main():
    tmp = Stores(Path(tempfile.mkdtemp(prefix="qbank_test_")))
    gate.configure(tmp)

    print("\n[1] A needs_human item CANNOT reach the bank")
    risky = {"id": "q-risky", "stem": "Q?", "options": ["a","b","c","d"], "correct_index": 0,
             "confidence": 0.40, "support_ok": True, "topic": "cooling"}
    core.add_candidate(tmp, risky)
    core.triage(tmp, "q-risky")
    check(tmp.load_pending()["q-risky"]["status"] == NEEDS_HUMAN, "low-confidence candidate triaged to needs_human")

    # (a) deterministic guard
    r = core.commit_to_bank(tmp, "q-risky")
    check(not r["ok"], f"commit_to_bank() refuses it deterministically ({r.get('error')})")
    # (b) PreToolUse hook
    out = await commit_gate_hook({"tool_name": COMMIT_TOOL, "tool_input": {"item_id": "q-risky"}}, None, {})
    decision = out.get("hookSpecificOutput", {}).get("permissionDecision")
    check(decision == "deny", f"PreToolUse hook DENIES it independently (permissionDecision={decision})")
    check("q-risky" not in tmp.bank_ids(), "nothing was written to the bank")

    print("\n[2] Only the human path promotes needs_human → committable")
    core.human_decide(tmp, "q-risky", approve=True, by="tester")
    check(tmp.load_pending()["q-risky"]["status"] == HUMAN_APPROVED, "human approve → human_approved")
    out = await commit_gate_hook({"tool_name": COMMIT_TOOL, "tool_input": {"item_id": "q-risky"}}, None, {})
    check(out.get("hookSpecificOutput", {}).get("permissionDecision") == "allow", "hook now ALLOWS the approved item")
    check(core.commit_to_bank(tmp, "q-risky")["ok"], "commit_to_bank() now succeeds")
    check("q-risky" in tmp.bank_ids(), "item is now in the bank")

    print("\n[3] State machine forbids illegal jumps")
    check((PENDING_REVIEW, COMMITTED) not in TRANSITIONS, "pending_review → committed is NOT a legal transition")
    check((NEEDS_HUMAN, AUTO_APPROVED) not in TRANSITIONS, "needs_human → auto_approved is NOT legal (no auto-promote)")
    check(TRANSITIONS.get((NEEDS_HUMAN, HUMAN_APPROVED)) == "human", "needs_human → human_approved is human-only")

    print("\n[4] Adversarial triage: true-substring quote that FAILS semantic support")
    adv = {"id": "q-adv", "confidence": 0.95, "support_ok": False, "topic": "hot holding"}
    v = score_candidate(adv)
    check(v["route"] == NEEDS_HUMAN and "weak_support" in v["reasons"],
          f"high-confidence but unsupported → needs_human, reasons={v['reasons']}")
    clean = {"id": "q-clean", "confidence": 0.92, "support_ok": True, "topic": "cooling"}
    check(score_candidate(clean)["route"] == AUTO_APPROVED, "clean candidate → auto_approved")
    sens = {"id": "q-sens", "confidence": 0.98, "support_ok": True, "topic": "allergens and anaphylaxis"}
    check(score_candidate(sens)["route"] == NEEDS_HUMAN, "sensitive topic forces human review even at high confidence")

    print("\n[5] canUseTool human callback")
    core.add_candidate(tmp, {"id": "q-cb", "confidence": 0.3, "support_ok": True, "topic": "x"})
    core.triage(tmp, "q-cb")
    cb_yes = make_human_callback(tmp, lambda item: (True, "looks fine"))
    res = await cb_yes(COMMIT_TOOL, {"item_id": "q-cb"}, {})
    check(isinstance(res, PermissionResultAllow) and tmp.load_pending()["q-cb"]["status"] == HUMAN_APPROVED,
          "callback approve → Allow + status human_approved")
    core.add_candidate(tmp, {"id": "q-cb2", "confidence": 0.3, "support_ok": True, "topic": "x"})
    core.triage(tmp, "q-cb2")
    cb_no = make_human_callback(tmp, lambda item: (False, "off-policy"))
    res = await cb_no(COMMIT_TOOL, {"item_id": "q-cb2"}, {})
    check(isinstance(res, PermissionResultDeny) and tmp.load_pending()["q-cb2"]["status"] == "rejected",
          "callback deny → Deny + status rejected")

    print("\n[6] Audit trail recorded every decision")
    events = {e["event"] for e in tmp.read_audit()}
    need = {"candidate_added", "sent_to_human", "human_approved", "committed", "hook_denied_commit", "rejected"}
    check(need <= events, f"audit log contains {sorted(need & events)}")

    print()
    if fails:
        print(f"❌ {fails} checks FAILED — gate is not sound.")
        return 1
    print("✅ All gate checks passed. No question reaches the bank without passing the gate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
