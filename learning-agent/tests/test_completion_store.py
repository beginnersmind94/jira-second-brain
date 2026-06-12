"""Tests for completion_store.py — durable per-learner completion records.

Run from learning-agent/ with the sibling .venv:
    ..\\..\\learning-agent\\.venv\\Scripts\\python.exe -m pytest tests/test_completion_store.py -v

These tests use a temporary directory so they never touch the real
data/completion/ directory.  Each test function gets a fresh store.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Make the learning-agent dir importable when pytest runs from elsewhere.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import completion_store as cs  # noqa: E402


# ── Fixture: isolated data dir per test ──────────────────────────────────────

@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    """Redirect CompletionStore file I/O to a temp directory for test isolation."""
    monkeypatch.setattr(cs, "_COMPLETION_DIR", tmp_path / "completion")
    yield tmp_path / "completion"


# ── Helper constants ──────────────────────────────────────────────────────────

USER_A = "user-alice-001"
USER_B = "user-bob-002"
DEMO_USER = "demo-user-001"          # triggers seed fallback
TRACK_1 = "track-20260612-abc123"
TRACK_2 = "track-20260612-xyz789"
MODULES = ["GUIDE-001", "GUIDE-002", "GUIDE-003", "GUIDE-004", "GUIDE-005"]


# ── Test 1: initial progress is zero for non-demo users ──────────────────────

def test_initial_progress_zero_for_real_user():
    progress = cs.get_progress(USER_A, TRACK_1, module_ids=MODULES)
    assert progress["modules_done"] == []
    assert progress["pct"] == 0
    assert progress["certified"] is False
    assert progress["cert_issued_at"] is None


# ── Test 2: demo seed fallback (40% done on first access) ────────────────────

def test_demo_seed_fallback_applies_for_demo_user():
    progress = cs.get_progress(DEMO_USER, TRACK_1, module_ids=MODULES)
    # Expect 40% of 5 modules = 2 modules done.
    expected_done_count = max(1, len(MODULES) * 40 // 100)
    assert len(progress["modules_done"]) == expected_done_count
    assert progress["pct"] == round(100 * expected_done_count / len(MODULES))
    assert progress["certified"] is False


# ── Test 3: demo seed does NOT apply without module_ids ──────────────────────

def test_demo_user_no_seed_without_module_ids():
    progress = cs.get_progress(DEMO_USER, TRACK_1)
    # No module_ids -> can't seed, return zeroed record.
    assert progress["modules_done"] == []
    assert progress["pct"] == 0


# ── Test 4: set_module_done marks a module and recalculates pct ──────────────

def test_set_module_done_marks_and_recalculates():
    progress = cs.set_module_done(USER_A, TRACK_1, "GUIDE-001", module_ids=MODULES)
    assert "GUIDE-001" in progress["modules_done"]
    assert progress["pct"] == 20   # 1/5 = 20%


def test_set_module_done_multiple_modules():
    cs.set_module_done(USER_A, TRACK_1, "GUIDE-001", module_ids=MODULES)
    cs.set_module_done(USER_A, TRACK_1, "GUIDE-002", module_ids=MODULES)
    progress = cs.set_module_done(USER_A, TRACK_1, "GUIDE-003", module_ids=MODULES)
    assert set(progress["modules_done"]) == {"GUIDE-001", "GUIDE-002", "GUIDE-003"}
    assert progress["pct"] == 60   # 3/5 = 60%


# ── Test 5: set_module_done is idempotent ────────────────────────────────────

def test_set_module_done_idempotent():
    cs.set_module_done(USER_A, TRACK_1, "GUIDE-001", module_ids=MODULES)
    progress = cs.set_module_done(USER_A, TRACK_1, "GUIDE-001", module_ids=MODULES)
    assert progress["modules_done"].count("GUIDE-001") == 1
    assert progress["pct"] == 20


# ── Test 6: pct calculation edge cases ───────────────────────────────────────

def test_pct_calculation_empty_track():
    progress = cs.get_progress(USER_A, TRACK_1, module_ids=[])
    assert progress["pct"] == 0


def test_pct_calculation_all_done():
    for mid in MODULES:
        cs.set_module_done(USER_A, TRACK_1, mid, module_ids=MODULES)
    progress = cs.get_progress(USER_A, TRACK_1, module_ids=MODULES)
    assert progress["pct"] == 100


# ── Test 7: cert issuance ────────────────────────────────────────────────────

def test_issue_certificate_returns_cert():
    cert = cs.issue_certificate(
        USER_A, TRACK_1, "Alice Smith",
        track_title="New Cashier Onboarding",
        product="SchoolCafe",
        role="Cashier",
        modules=5,
    )
    assert cert["id"].startswith("cert-")
    assert cert["learner_name"] == "Alice Smith"
    assert cert["track_id"] == TRACK_1
    assert cert["track_title"] == "New Cashier Onboarding"
    assert cert["issued_at"]


def test_issue_certificate_marks_progress_certified():
    cs.issue_certificate(USER_A, TRACK_1, "Alice Smith")
    progress = cs.get_progress(USER_A, TRACK_1)
    assert progress["certified"] is True
    assert progress["cert_issued_at"] is not None


# ── Test 8: get_certificate round-trip ───────────────────────────────────────

def test_get_certificate_round_trip():
    cert = cs.issue_certificate(USER_A, TRACK_1, "Alice Smith", track_title="Track One")
    cert_id = cert["id"]
    retrieved = cs.get_certificate(cert_id)
    assert retrieved is not None
    assert retrieved["id"] == cert_id
    assert retrieved["learner_name"] == "Alice Smith"
    assert retrieved["track_title"] == "Track One"


def test_get_certificate_nonexistent_returns_none():
    result = cs.get_certificate("cert-does-not-exist-000000")
    assert result is None


# ── Test 9: get_all_progress returns all stored tracks ───────────────────────

def test_get_all_progress_multiple_tracks():
    cs.set_module_done(USER_A, TRACK_1, "GUIDE-001", module_ids=MODULES)
    cs.set_module_done(USER_A, TRACK_2, "GUIDE-002", module_ids=MODULES)
    all_progress = cs.get_all_progress(USER_A)
    # Both track records should appear (keyed by safe-ified track id).
    assert len(all_progress) == 2


def test_get_all_progress_empty_for_new_user():
    result = cs.get_all_progress("user-brand-new-999")
    assert result == {}


# ── Test 10: progress is isolated per user ───────────────────────────────────

def test_progress_isolated_per_user():
    cs.set_module_done(USER_A, TRACK_1, "GUIDE-001", module_ids=MODULES)
    progress_b = cs.get_progress(USER_B, TRACK_1, module_ids=MODULES)
    # User B's progress must not include User A's completed module.
    assert "GUIDE-001" not in progress_b["modules_done"]
    assert progress_b["pct"] == 0


# ── Test 11: disk persistence (write then read fresh) ────────────────────────

def test_round_trip_persistence(isolated_store):
    """Progress written by set_module_done must be readable by get_progress."""
    cs.set_module_done(USER_A, TRACK_1, "GUIDE-003", module_ids=MODULES)
    cs.set_module_done(USER_A, TRACK_1, "GUIDE-005", module_ids=MODULES)

    # Verify the JSON file exists on disk.
    safe_uid = cs._safe_id(USER_A)
    safe_tid = cs._safe_id(TRACK_1)
    disk_path = isolated_store / safe_uid / f"{safe_tid}.json"
    assert disk_path.exists(), f"progress file not written: {disk_path}"

    raw = json.loads(disk_path.read_text(encoding="utf-8"))
    assert set(raw["modules_done"]) == {"GUIDE-003", "GUIDE-005"}

    # Re-read through the store (simulating a server restart).
    fresh = cs.get_progress(USER_A, TRACK_1, module_ids=MODULES)
    assert set(fresh["modules_done"]) == {"GUIDE-003", "GUIDE-005"}
    assert fresh["pct"] == 40   # 2/5
