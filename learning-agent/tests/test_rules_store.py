"""Tests for OPS-2 — Assignment rules engine.

Run from learning-agent/ with:
    ..\\..\\learning-agent\\.venv\\Scripts\\python.exe -m pytest tests/test_rules_store.py -v
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import rules_store as rs  # noqa: E402


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr(rs, "_RULES_DIR",  tmp_path / "rules")
    monkeypatch.setattr(rs, "_RULES_FILE", tmp_path / "rules" / "rules.json")
    monkeypatch.setattr(rs, "_AUDIT_FILE", tmp_path / "rules" / "audit.jsonl")
    yield


# ── Test 1: add_rule round-trip ───────────────────────────────────────────────

def test_add_rule_round_trip():
    rule = rs.add_rule(
        label="Cashier onboarding",
        assign_modules=["GUIDE-001", "GUIDE-002"],
        role_tags=["Cashier"],
    )
    assert rule["label"] == "Cashier onboarding"
    assert rule["action"]["assign_modules"] == ["GUIDE-001", "GUIDE-002"]
    assert rule["criteria"]["role_tags"] == ["Cashier"]
    assert rule["active"] is True

    rules = rs.get_rules()
    assert len(rules) == 1
    assert rules[0]["id"] == rule["id"]


# ── Test 2: delete_rule soft-deletes ─────────────────────────────────────────

def test_delete_rule_soft():
    r = rs.add_rule("Temp rule", assign_modules=["GUIDE-003"])
    deleted = rs.delete_rule(r["id"])
    assert deleted is True

    active = rs.get_rules(active_only=True)
    assert not any(x["id"] == r["id"] for x in active)

    # Still present when active_only=False.
    all_rules = rs.get_rules()
    assert any(x["id"] == r["id"] for x in all_rules)


# ── Test 3: validation errors ─────────────────────────────────────────────────

def test_add_rule_validation():
    with pytest.raises(ValueError, match="label"):
        rs.add_rule("", assign_modules=["GUIDE-001"])

    with pytest.raises(ValueError, match="assign_modules"):
        rs.add_rule("Valid label", assign_modules=[])


# ── Test 4: dry_run matches correct districts ─────────────────────────────────

def test_dry_run_role_filter():
    rule = rs.add_rule("Cashier pack", assign_modules=["GUIDE-010"], role_tags=["Cashier"])

    districts = [
        {"id": "d-1", "role_tags": ["Cashier", "Manager"]},
        {"id": "d-2", "role_tags": ["Manager"]},
        {"id": "d-3", "role_tags": ["Cashier"]},
    ]
    result = rs.dry_run(rule["id"], districts)

    matched_ids = {m["district_id"] for m in result["matches"]}
    assert matched_ids == {"d-1", "d-3"}
    assert "d-2" in result["unmatched"]
    # dry_run must NOT write an audit entry.
    assert rs.get_audit_log() == []


# ── Test 5: apply_rule writes audit log ──────────────────────────────────────

def test_apply_rule_writes_audit():
    rule = rs.add_rule("All-hands pack", assign_modules=["GUIDE-020"])  # no criteria = match all
    districts = [{"id": "d-alpha"}, {"id": "d-beta"}]

    result = rs.apply_rule(rule["id"], districts)
    assert len(result["matches"]) == 2
    assert "applied_at" in result

    log = rs.get_audit_log()
    assert len(log) == 1
    assert log[0]["rule_id"] == rule["id"]
    assert len(log[0]["matches"]) == 2
