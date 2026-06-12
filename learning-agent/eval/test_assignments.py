"""eval/test_assignments.py — Deterministic tests for A3: track assignments, due dates,
prerequisite locks.

Test coverage per the A3 spec:
  T1  POST /api/tracks/{tid}/assign -> assignment persists in track JSON, survives reload
  T2  GET /api/tracks/{tid} for a cashier user with a cashier-role assignment ->
      response includes due_date and days_remaining
  T3  is_overdue: True when due_date is in the past and track not complete
      (SHOULD-NOT-OCCUR: past-due must not show as on-time)
  T4  is_overdue: False when track is complete even if due_date passed
  T5  Prerequisite lock: track with unfulfilled prereq -> GET returns locked: true
  T6  Assignment with audience_type: "role" = "Manager" doesn't surface to a cashier
      user's track response (SHOULD-NOT-OCCUR: wrong audience must not see due date)

All tests are deterministic, no SDK calls, no network.

Run:
    python -m pytest learning-agent/eval/test_assignments.py -v
  or from learning-agent/:
    python eval/test_assignments.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

# Allow running directly from learning-agent/ or via pytest from repo root.
_HERE = Path(__file__).resolve().parent
_LA = _HERE.parent
if str(_LA) not in sys.path:
    sys.path.insert(0, str(_LA))

import modules_store as ms
import completion_store as cs
from auth import CurrentUser

# ── Helpers ───────────────────────────────────────────────────────────────────

def _cashier_user() -> CurrentUser:
    return CurrentUser(
        id="test-cashier-001",
        name="Test Cashier",
        role="Cashier",
        district_id="houston-isd",
        districts=[],
        is_trainer=False,
    )

def _manager_user() -> CurrentUser:
    return CurrentUser(
        id="test-manager-001",
        name="Test Manager",
        role="Site Manager",
        district_id="houston-isd",
        districts=[],
        is_trainer=False,
    )

def _trainer_user() -> CurrentUser:
    return CurrentUser(
        id="test-trainer-001",
        name="Test Trainer",
        role="Trainer",
        district_id=None,
        districts=["houston-isd"],
        is_trainer=True,
    )

def _make_track(tmp_dir: Path, *, assignments=None, prerequisites=None) -> dict:
    """Create a minimal track JSON in the temp dir and return it."""
    original_tracks_dir = ms.TRACKS_DIR
    ms.TRACKS_DIR = tmp_dir
    try:
        track = ms.create_track(
            title="Test Onboarding",
            description="",
            product="SchoolCafé",
            role_tags=["Cashier"],
        )
        if assignments is not None:
            track["assignments"] = assignments
        if prerequisites is not None:
            track["prerequisites"] = prerequisites
        ms.save_track(track)
        return track
    finally:
        ms.TRACKS_DIR = original_tracks_dir

def _load_track(tmp_dir: Path, tid: str) -> dict:
    original = ms.TRACKS_DIR
    ms.TRACKS_DIR = tmp_dir
    try:
        return ms.load_track(tid)
    finally:
        ms.TRACKS_DIR = original

# Import the helper functions from demo_app (pure functions — no FastAPI overhead).
# We import them directly so the tests are deterministic + no server needed.
def _import_demo_app_helpers():
    """Import the A3 helper functions from demo_app without starting the ASGI app."""
    import importlib, demo_app as _da
    return (
        _da._find_applicable_assignment,
        _da._assignment_due_fields,
        _da._check_prerequisites,
    )


# ── T1: POST assign -> persists in track JSON, survives reload ────────────────

def test_t1_assignment_persists():
    """An assignment added via _find_applicable_assignment helpers is persisted
    to disk and survives a reload (mirrors what POST /api/tracks/{tid}/assign does)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        original = ms.TRACKS_DIR
        ms.TRACKS_DIR = tmp_path
        try:
            track = ms.create_track("Persist Test", role_tags=["Cashier"])
            tid = track["id"]

            # Simulate what the POST endpoint does: append assignment + save.
            new_assignment = {
                "audience_type": "role",
                "audience_value": "Cashier",
                "district": "houston-isd",
                "due_date": "2026-07-31",
                "assigned_at": "2026-06-13T00:00:00",
                "assigned_by": "test-trainer-001",
            }
            track["assignments"] = [new_assignment]
            ms.save_track(track)

            # Reload from disk.
            reloaded = ms.load_track(tid)
            assert reloaded is not None, "track must be reloadable after assignment"
            assignments = reloaded.get("assignments") or []
            assert len(assignments) == 1, f"expected 1 assignment, got {len(assignments)}"
            a = assignments[0]
            assert a["audience_type"] == "role"
            assert a["audience_value"] == "Cashier"
            assert a["due_date"] == "2026-07-31"
        finally:
            ms.TRACKS_DIR = original
    print("T1 PASS: assignment persists in track JSON and survives reload")


# ── T2: GET for cashier user with cashier-role assignment -> due_date + days_remaining ──

def test_t2_due_fields_for_matching_role():
    """_find_applicable_assignment matches a role assignment for a cashier user,
    and _assignment_due_fields returns the correct due_date + days_remaining."""
    find_fn, due_fn, _ = _import_demo_app_helpers()

    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    assignments = [
        {
            "audience_type": "role",
            "audience_value": "Cashier",
            "district": "houston-isd",
            "due_date": tomorrow,
            "assigned_at": "2026-06-13T00:00:00",
            "assigned_by": "trainer",
        }
    ]
    user = _cashier_user()
    matched = find_fn(assignments, user)
    assert matched is not None, "cashier assignment must match cashier user"
    assert matched["due_date"] == tomorrow

    progress = {"certified": False, "pct": 50}
    fields = due_fn(matched, progress)
    assert fields["due_date"] == tomorrow
    assert fields["days_remaining"] == 1, (
        f"days_remaining should be 1 (due tomorrow), got {fields['days_remaining']}"
    )
    assert fields["is_overdue"] is False, "due tomorrow must not be overdue"
    print("T2 PASS: cashier role assignment surfaces due_date and days_remaining=1")


# ── T3: is_overdue True when past due and not complete ────────────────────────
# SHOULD-NOT-OCCUR: past-due must not show as on-time (is_overdue must be True)

def test_t3_is_overdue_true_when_past_due_and_not_complete():
    """SHOULD-NOT-OCCUR guard: a track past its due date AND not complete must
    report is_overdue=True. If is_overdue is False here, the overdue logic is broken."""
    _, due_fn, _ = _import_demo_app_helpers()

    yesterday = (date.today() - timedelta(days=1)).isoformat()
    assignment = {
        "audience_type": "role",
        "audience_value": "Cashier",
        "due_date": yesterday,
    }
    progress = {"certified": False, "pct": 40}
    fields = due_fn(assignment, progress)

    assert fields["is_overdue"] is True, (
        f"SHOULD-NOT-OCCUR: past-due incomplete track shows is_overdue={fields['is_overdue']} "
        "(expected True)"
    )
    assert fields["days_remaining"] < 0, (
        f"days_remaining must be negative for past due, got {fields['days_remaining']}"
    )
    print("T3 PASS: is_overdue=True for past-due incomplete track")


# ── T4: is_overdue False when track is complete even if due_date passed ────────

def test_t4_is_overdue_false_when_complete():
    """A track that is certified (or 100% done) must NOT be marked overdue even if
    the due date has passed."""
    _, due_fn, _ = _import_demo_app_helpers()

    yesterday = (date.today() - timedelta(days=5)).isoformat()
    assignment = {
        "audience_type": "role",
        "audience_value": "Cashier",
        "due_date": yesterday,
    }

    # Test both certified=True and pct=100.
    for progress in [{"certified": True, "pct": 100}, {"certified": False, "pct": 100}]:
        fields = due_fn(assignment, progress)
        assert fields["is_overdue"] is False, (
            f"completed track must not be overdue (progress={progress}), "
            f"got is_overdue={fields['is_overdue']}"
        )
    print("T4 PASS: is_overdue=False for completed track even past due date")


# ── T5: Prerequisite lock — unfulfilled prereq -> locked: True ───────────────

def test_t5_prerequisite_lock():
    """A track with prerequisites: [prereq_tid] where the prerequisite is not
    complete for the user returns locked=True from _check_prerequisites."""
    _, _, check_prereqs_fn = _import_demo_app_helpers()

    prereq_tid = "track-prereq-001"
    track = {
        "id": "track-test-001",
        "title": "Advanced Track",
        "prerequisites": [prereq_tid],
    }
    all_tracks = [
        {"id": prereq_tid, "title": "Foundation Track"},
        track,
    ]

    # User has no completion record for prereq -> get_progress returns pct=0.
    user_id = "test-user-no-prereq"

    with tempfile.TemporaryDirectory() as tmp:
        original_completion_dir = cs._COMPLETION_DIR
        cs._COMPLETION_DIR = Path(tmp) / "completion"
        cs._COMPLETION_DIR.mkdir(parents=True, exist_ok=True)
        try:
            lock_state = check_prereqs_fn(track, user_id, all_tracks)
        finally:
            cs._COMPLETION_DIR = original_completion_dir

    assert lock_state is not None, "lock_state must not be None when prereq is incomplete"
    assert lock_state.get("locked") is True, (
        f"expected locked=True, got {lock_state}"
    )
    locked_by = lock_state.get("locked_by") or {}
    assert locked_by.get("track_id") == prereq_tid, (
        f"locked_by.track_id must be '{prereq_tid}', got {locked_by.get('track_id')}"
    )
    assert locked_by.get("title") == "Foundation Track", (
        f"locked_by.title must be 'Foundation Track', got {locked_by.get('title')}"
    )
    print("T5 PASS: unfulfilled prerequisite returns locked=True with correct locked_by")


# ── T6: Role=Manager assignment does NOT surface to a cashier user ─────────────
# SHOULD-NOT-OCCUR: wrong audience must not see due date

def test_t6_wrong_role_assignment_not_surfaced():
    """SHOULD-NOT-OCCUR guard: an assignment for role='Site Manager' must NOT match
    a cashier user. If it does, wrong learners would see incorrect due dates."""
    find_fn, due_fn, _ = _import_demo_app_helpers()

    next_week = (date.today() + timedelta(days=7)).isoformat()
    assignments = [
        {
            "audience_type": "role",
            "audience_value": "Site Manager",
            "due_date": next_week,
            "assigned_at": "2026-06-13T00:00:00",
            "assigned_by": "trainer",
        }
    ]
    user = _cashier_user()
    matched = find_fn(assignments, user)
    assert matched is None, (
        f"SHOULD-NOT-OCCUR: Site Manager assignment matched cashier user "
        f"(got matched={matched})"
    )

    # Also verify: due_fields with no matching assignment returns due_date=None.
    fields = due_fn(None, {"certified": False, "pct": 0})
    assert fields["due_date"] is None, (
        f"due_date must be None when no assignment matches, got {fields['due_date']}"
    )
    assert fields["is_overdue"] is False
    print("T6 PASS: Site Manager assignment does not surface to cashier user")


# ── Runner ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        test_t1_assignment_persists,
        test_t2_due_fields_for_matching_role,
        test_t3_is_overdue_true_when_past_due_and_not_complete,
        test_t4_is_overdue_false_when_complete,
        test_t5_prerequisite_lock,
        test_t6_wrong_role_assignment_not_surfaced,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as exc:
            print(f"FAIL {t.__name__}: {exc}")
            failed += 1
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{len(tests)} passed" + (f", {failed} failed" if failed else ""))
    if failed:
        sys.exit(1)
