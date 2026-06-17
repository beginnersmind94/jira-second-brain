"""rules_store.py — Assignment rules engine for OPS-2.

A rule: if a district matches `criteria`, auto-assign `action.modules` to it.

Storage layout:
    data/rules/rules.json         — active rule records
    data/rules/audit.jsonl        — append-only log of every rule application

Rule record schema:
    {id, label, criteria: {role_tags?: [str], district_ids?: [str]},
     action: {assign_modules: [str]}, created_at, active}

criteria:
  role_tags    — match districts whose learner role_tags overlap
  district_ids — explicit allowlist (empty = match all)

A district matches if BOTH non-empty criterion lists are satisfied (AND logic).
Empty criteria dict = matches all districts (use sparingly — label it clearly).
"""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path

_RULES_DIR   = Path(__file__).resolve().parent / "data" / "rules"
_RULES_FILE  = _RULES_DIR / "rules.json"
_AUDIT_FILE  = _RULES_DIR / "audit.jsonl"


# ── I/O ───────────────────────────────────────────────────────────────────────

def _read() -> list[dict]:
    if not _RULES_FILE.exists():
        return []
    try:
        return json.loads(_RULES_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _write(rules: list[dict]) -> None:
    _RULES_DIR.mkdir(parents=True, exist_ok=True)
    _RULES_FILE.write_text(json.dumps(rules, indent=2, ensure_ascii=False), encoding="utf-8")


def _append_audit(entry: dict) -> None:
    _RULES_DIR.mkdir(parents=True, exist_ok=True)
    with _AUDIT_FILE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ── Public API ────────────────────────────────────────────────────────────────

def add_rule(
    label: str,
    assign_modules: list[str],
    role_tags: list[str] | None = None,
    district_ids: list[str] | None = None,
) -> dict:
    """Create a new assignment rule.

    Raises ValueError if label is empty or assign_modules is empty.
    """
    label = label.strip()
    if not label:
        raise ValueError("label must not be empty")
    if not assign_modules:
        raise ValueError("assign_modules must contain at least one module id")

    rule: dict = {
        "id":         str(uuid.uuid4()),
        "label":      label,
        "criteria": {
            **({"role_tags": list(role_tags)} if role_tags else {}),
            **({"district_ids": list(district_ids)} if district_ids else {}),
        },
        "action": {"assign_modules": list(assign_modules)},
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "active":     True,
    }
    rules = _read()
    rules.append(rule)
    _write(rules)
    return rule


def get_rules(active_only: bool = False) -> list[dict]:
    """Return rules, newest-first.  Pass active_only=True to skip deactivated rules."""
    rules = _read()
    if active_only:
        rules = [r for r in rules if r.get("active", True)]
    return sorted(rules, key=lambda r: r.get("created_at", ""), reverse=True)


def delete_rule(rule_id: str) -> bool:
    """Deactivate a rule (soft-delete — preserved in audit trail).

    Returns True if found and deactivated, False if not found.
    """
    rules = _read()
    for r in rules:
        if r.get("id") == rule_id:
            r["active"] = False
            _write(rules)
            return True
    return False


def dry_run(rule_id: str, districts: list[dict]) -> dict:
    """Preview which districts a rule would match and what would be assigned.

    districts: list of {id, role_tags?: [str]} dicts describing candidates.

    Returns:
        {rule_id, matches: [{district_id, would_assign: [module_id]}], unmatched: [district_id]}

    Raises ValueError if rule not found or inactive.
    """
    rules = _read()
    rule = next((r for r in rules if r.get("id") == rule_id), None)
    if rule is None:
        raise ValueError(f"rule {rule_id!r} not found")
    if not rule.get("active", True):
        raise ValueError(f"rule {rule_id!r} is inactive")

    criteria      = rule.get("criteria", {})
    modules       = rule["action"]["assign_modules"]
    req_roles     = set(criteria.get("role_tags", []))
    req_districts = set(criteria.get("district_ids", []))

    matches: list[dict] = []
    unmatched: list[str] = []

    for d in districts:
        did = d.get("id", "")
        d_roles = set(d.get("role_tags", []))
        role_ok     = (not req_roles)     or bool(req_roles & d_roles)
        district_ok = (not req_districts) or (did in req_districts)
        if role_ok and district_ok:
            matches.append({"district_id": did, "would_assign": list(modules)})
        else:
            unmatched.append(did)

    return {"rule_id": rule_id, "matches": matches, "unmatched": unmatched}


def apply_rule(rule_id: str, districts: list[dict]) -> dict:
    """Apply a rule to a list of districts and write an audit entry.

    Same semantics as dry_run but also appends to audit.jsonl.
    Returns the same shape as dry_run with an added applied_at timestamp.
    """
    result = dry_run(rule_id, districts)
    if result["matches"]:
        _append_audit({
            "rule_id":    rule_id,
            "matches":    result["matches"],
            "applied_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        })
    result["applied_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    return result


def get_audit_log() -> list[dict]:
    """Return all audit entries, newest-first."""
    if not _AUDIT_FILE.exists():
        return []
    entries: list[dict] = []
    try:
        for line in _AUDIT_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    except (json.JSONDecodeError, OSError):
        return []
    return list(reversed(entries))
