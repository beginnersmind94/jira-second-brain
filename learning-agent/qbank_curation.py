"""Question-bank curation core — the state machine + the gated writer + triage scorer.

Deterministic, SDK-free, unit-testable. The SDK wiring (PreToolUse hook + canUseTool
human callback + the commit_to_bank tool) lives in qbank_gate_hooks.py and calls into here.

State machine:
    pending_review ──triage clean──▶ auto_approved ──┐
                  └─triage flags──▶ needs_human ──human approve──▶ human_approved ──┤
                                              └────human deny────▶ rejected (terminal) │
                                                                                       ▼
                                                              commit_to_bank ──▶ committed (terminal)

HARD RULES enforced here (and again, independently, by the PreToolUse hook):
  • The bank is append-only and ONLY commit_to_bank() writes to it.
  • commit_to_bank() refuses any item whose status is not auto_approved or human_approved.
  • needs_human can ONLY become human_approved via the human path — never auto-promoted.
  • Every decision is written to an append-only audit log with timestamp + reason + rule.
  • Model output is untrusted: it can propose candidates, never flip a status or commit.
"""
from __future__ import annotations

import json
import statistics
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# ── Statuses & legal transitions ──────────────────────────────────────────────
PENDING_REVIEW = "pending_review"
AUTO_APPROVED = "auto_approved"
NEEDS_HUMAN = "needs_human"
HUMAN_APPROVED = "human_approved"
REJECTED = "rejected"        # terminal
COMMITTED = "committed"      # terminal

COMMITTABLE = (AUTO_APPROVED, HUMAN_APPROVED)   # the ONLY statuses commit_to_bank accepts
TERMINAL = (REJECTED, COMMITTED)

# Allowed transitions, tagged with WHO may make them. "system" = deterministic triage;
# "human" = the canUseTool approval callback only; "commit" = commit_to_bank only.
TRANSITIONS = {
    (PENDING_REVIEW, AUTO_APPROVED): "system",
    (PENDING_REVIEW, NEEDS_HUMAN): "system",
    (NEEDS_HUMAN, HUMAN_APPROVED): "human",
    (NEEDS_HUMAN, REJECTED): "human",
    (AUTO_APPROVED, COMMITTED): "commit",
    (HUMAN_APPROVED, COMMITTED): "commit",
}


class GateError(Exception):
    """Raised when an illegal transition or a non-committable commit is attempted."""


# ── Config (thresholds + sensitive topics are config-driven, not hardcoded) ────
@dataclass
class TriageConfig:
    confidence_threshold: float = 0.75
    sensitive_topics: tuple = ("allergens", "anaphylaxis", "medical", "choking",
                               "religious dietary law", "student PII")
    outlier_z: float = 1.5      # flag a candidate this many stdev BELOW batch-mean confidence


DEFAULT_CONFIG = TriageConfig()


# ── Stores: pending (mutable dict), bank (append-only), audit (append-only) ────
@dataclass
class Stores:
    root: Path
    def __post_init__(self):
        self.root.mkdir(parents=True, exist_ok=True)
    @property
    def pending(self): return self.root / "pending.json"
    @property
    def bank(self): return self.root / "bank.jsonl"
    @property
    def audit(self): return self.root / "audit.jsonl"

    def load_pending(self) -> dict:
        return json.loads(self.pending.read_text(encoding="utf-8")) if self.pending.exists() else {}

    def save_pending(self, d: dict) -> None:
        self.pending.write_text(json.dumps(d, indent=2), encoding="utf-8")

    def append_bank(self, item: dict) -> None:
        with self.bank.open("a", encoding="utf-8") as f:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    def bank_ids(self) -> set:
        if not self.bank.exists():
            return set()
        return {json.loads(l)["id"] for l in self.bank.read_text(encoding="utf-8").splitlines() if l.strip()}

    def audit_log(self, event: str, item_id: str, reason: str = "", rule: str = "") -> None:
        rec = {"at": datetime.now().isoformat(timespec="seconds"), "event": event,
               "item_id": item_id, "reason": reason, "rule": rule}
        with self.audit.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def read_audit(self) -> list:
        if not self.audit.exists():
            return []
        return [json.loads(l) for l in self.audit.read_text(encoding="utf-8").splitlines() if l.strip()]


# ── Triage scorer — pure, auditable, unit-testable (judgment OUT of the prompt) ─
def score_candidate(item: dict, batch: list | None = None, config: TriageConfig = DEFAULT_CONFIG) -> dict:
    """Compute {risk, confidence, reasons[], route} from precomputed SIGNALS on the item:
        confidence : float 0..1   (model's self-reported confidence at generation)
        support_ok : bool         (the semantic gate's verdict: does the quote support stem+answer?)
        topic      : str
    `support_ok` is supplied by the deterministic+semantic gate (qbank_gate.py), NOT judged
    here — so this function stays pure and testable. Any reason → needs_human."""
    reasons: list[str] = []
    conf = float(item.get("confidence", 0.0))

    if conf < config.confidence_threshold:
        reasons.append("low_confidence")
    topic = (item.get("topic") or "").lower()
    if any(s.lower() in topic for s in config.sensitive_topics):
        reasons.append("sensitive_topic")
    if item.get("support_ok") is False:           # true-substring-but-unsupported lands here
        reasons.append("weak_support")
    if batch:
        confs = [float(b.get("confidence", 0.0)) for b in batch if b.get("confidence") is not None]
        if len(confs) >= 3:
            mean, sd = statistics.mean(confs), (statistics.pstdev(confs) or 0.0)
            if sd > 0 and conf < mean - config.outlier_z * sd:
                reasons.append("statistical_outlier")

    return {"risk": "high" if reasons else "low", "confidence": conf,
            "reasons": reasons, "route": NEEDS_HUMAN if reasons else AUTO_APPROVED}


# ── Lifecycle operations (each logs to the audit trail) ────────────────────────
def add_candidate(stores: Stores, item: dict) -> str:
    """Generation deposits a candidate as pending_review. NEVER reaches the bank here."""
    p = stores.load_pending()
    item = {**item, "status": PENDING_REVIEW}
    p[item["id"]] = item
    stores.save_pending(p)
    stores.audit_log("candidate_added", item["id"], rule="generate")
    return item["id"]


def triage(stores: Stores, item_id: str, batch: list | None = None,
           config: TriageConfig = DEFAULT_CONFIG) -> dict:
    """System transition: pending_review → auto_approved | needs_human (with reasons)."""
    p = stores.load_pending()
    item = p[item_id]
    if item["status"] != PENDING_REVIEW:
        raise GateError(f"triage requires pending_review, got {item['status']}")
    verdict = score_candidate(item, batch, config)
    item["status"] = verdict["route"]
    item["triage"] = verdict
    p[item_id] = item
    stores.save_pending(p)
    if verdict["route"] == AUTO_APPROVED:
        stores.audit_log("auto_approved", item_id, rule="triage_clean")
    else:
        stores.audit_log("sent_to_human", item_id, reason=",".join(verdict["reasons"]), rule="triage_flagged")
    return verdict


def human_decide(stores: Stores, item_id: str, approve: bool, by: str, reason: str = "") -> str:
    """The ONLY path out of needs_human. Invoked by the canUseTool human callback."""
    p = stores.load_pending()
    item = p[item_id]
    if item["status"] != NEEDS_HUMAN:
        raise GateError(f"human_decide requires needs_human, got {item['status']}")
    item["status"] = HUMAN_APPROVED if approve else REJECTED
    item["human"] = {"by": by, "reason": reason, "at": datetime.now().isoformat(timespec="seconds")}
    p[item_id] = item
    stores.save_pending(p)
    stores.audit_log("human_approved" if approve else "rejected", item_id,
                     reason=reason, rule=f"human:{by}")
    return item["status"]


def commit_to_bank(stores: Stores, item_id: str) -> dict:
    """The ONE gated writer to the bank. Refuses anything not in COMMITTABLE.
    This is the deterministic guard; the PreToolUse hook is the independent SDK-layer guard."""
    p = stores.load_pending()
    item = p.get(item_id)
    if not item:
        stores.audit_log("commit_denied", item_id, reason="unknown_item", rule="commit_guard")
        return {"ok": False, "error": "unknown item"}
    if item["status"] not in COMMITTABLE:
        stores.audit_log("commit_denied", item_id, reason=f"status={item['status']}", rule="commit_guard")
        return {"ok": False, "error": f"status '{item['status']}' is not committable "
                f"(must be {' or '.join(COMMITTABLE)})"}
    item["status"] = COMMITTED
    item["committed_at"] = datetime.now().isoformat(timespec="seconds")
    p[item_id] = item
    stores.save_pending(p)
    stores.append_bank(item)
    stores.audit_log("committed", item_id, rule="commit_to_bank")
    return {"ok": True, "item_id": item_id}
