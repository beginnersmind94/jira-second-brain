"""eval/test_roster_assignment.py — STORY-003 Roster & Assignment tests (C3 agent).

Coverage:
  T1  Bulk assign by role — POST /api/tracks/{tid}/assign, audience_type=role
  T2  Bulk assign by district — audience_type=district
  T3  Individual assign — POST /api/tracks/{tid}/assign/user/{uid}  (idempotent)
  T4  Individual unassign — DELETE /api/tracks/{tid}/assign/user/{uid}
  T5  Unassign preserves completion record (completion_store not cleared)
  T6  Draft-track-not-assignable — 409 on both bulk and individual assign
  T7  Past-due date warns (assignment still persisted — warn, don't block)
  T8  Nudge throttle — second nudge-all-overdue within 60 s returns throttled=True
  T9  Tenancy — director (dana-director) sees only own district roster
  T10 Cashier 403 on bulk assign, individual assign, and roster endpoints
  T11 Unassigned view — GET /api/tracks/{tid}/unassigned returns learners with no rule
  T12 Nudge single learner — POST /api/roster/{tid}/nudge with user_ids
  T13 Remove assignment by index — DELETE /api/tracks/{tid}/assign/{idx}
  T14 Duplicate user-level assign is idempotent (no second entry added)

Run:
    python -m pytest learning-agent/eval/test_roster_assignment.py -v
  or from learning-agent/:
    python -m pytest eval/test_roster_assignment.py -v
"""
from __future__ import annotations

import json
import sys
import tempfile
import time
from datetime import date, timedelta
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_LA   = _HERE.parent
if str(_LA) not in sys.path:
    sys.path.insert(0, str(_LA))

from fastapi.testclient import TestClient

# ── Shared helpers ─────────────────────────────────────────────────────────────

def _make_client():
    import demo_app
    return TestClient(demo_app.app, raise_server_exceptions=True)


def _trainer_headers():
    return {"X-Demo-User": "sam-trainer"}


def _director_headers():
    return {"X-Demo-User": "dana-director"}


def _cashier_headers():
    return {"X-Demo-User": "john-cashier"}


def _create_track(client, status="published"):
    """Create a track and optionally publish it; return the track dict."""
    r = client.post(
        "/api/tracks",
        json={"title": "S3 Test Track", "description": "", "product": "SchoolCafé", "role_tags": ["Cashier"]},
        headers=_trainer_headers(),
    )
    assert r.status_code == 200, r.text
    track = r.json()
    if status == "published":
        # Need at least one module to publish, but the publish endpoint's guard
        # is on module_ids. We'll patch the track directly via the store.
        import modules_store as _ms
        t = _ms.load_track(track["id"])
        # Publish directly by setting status (bypass the empty-guard for test isolation).
        t["status"] = "published"
        _ms.save_track(t)
        track["status"] = "published"
    return track


# ── T1: Bulk assign by role ───────────────────────────────────────────────────

def test_t1_bulk_assign_role():
    """Bulk assign all Cashiers → persists audience_type=role assignment."""
    client = _make_client()
    track  = _create_track(client, status="published")
    tid    = track["id"]
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    r = client.post(
        f"/api/tracks/{tid}/assign",
        json={"audience_type": "role", "audience_value": "Cashier", "due_date": tomorrow},
        headers=_trainer_headers(),
    )
    assert r.status_code == 200, r.text
    body = r.json()
    asns = body.get("assignments") or []
    assert any(a["audience_type"] == "role" and a["audience_value"] == "Cashier" for a in asns), \
        f"Expected role=Cashier assignment, got: {asns}"

    # Assignment survives reload.
    r2 = client.get(f"/api/tracks/{tid}/assignments", headers=_trainer_headers())
    assert r2.status_code == 200
    assert any(a["audience_type"] == "role" and a["audience_value"] == "Cashier" for a in r2.json()["assignments"])


# ── T2: Bulk assign by district ───────────────────────────────────────────────

def test_t2_bulk_assign_district():
    """Bulk assign entire district → audience_type=district."""
    client = _make_client()
    track  = _create_track(client, status="published")
    tid    = track["id"]

    r = client.post(
        f"/api/tracks/{tid}/assign",
        json={"audience_type": "district", "audience_value": "district"},
        headers=_trainer_headers(),
    )
    assert r.status_code == 200, r.text
    asns = r.json().get("assignments") or []
    assert any(a["audience_type"] == "district" for a in asns), f"Expected district assignment, got: {asns}"


# ── T3: Individual assign (idempotent) ────────────────────────────────────────

def test_t3_individual_assign_idempotent():
    """Individual assign john-cashier twice → only one entry, updated timestamp."""
    client = _make_client()
    track  = _create_track(client, status="published")
    tid    = track["id"]
    uid    = "john-cashier-s3-test"
    due1   = (date.today() + timedelta(days=7)).isoformat()
    due2   = (date.today() + timedelta(days=14)).isoformat()

    r1 = client.post(f"/api/tracks/{tid}/assign/user/{uid}",
                     json={"due_date": due1}, headers=_trainer_headers())
    assert r1.status_code == 200, r1.text

    r2 = client.post(f"/api/tracks/{tid}/assign/user/{uid}",
                     json={"due_date": due2}, headers=_trainer_headers())
    assert r2.status_code == 200, r2.text

    # Exactly one user-level assignment for this uid.
    asns = r2.json().get("assignments") or []
    user_asns = [a for a in asns if a["audience_type"] == "user" and a["audience_value"] == uid]
    assert len(user_asns) == 1, f"Expected 1 user-level entry, got {len(user_asns)}: {asns}"
    # Updated due_date.
    assert user_asns[0]["due_date"] == due2, f"Expected due_date={due2}, got {user_asns[0]['due_date']}"


# ── T4: Individual unassign ───────────────────────────────────────────────────

def test_t4_individual_unassign():
    """Individual unassign removes user-level entry, leaves others intact."""
    client = _make_client()
    track  = _create_track(client, status="published")
    tid    = track["id"]
    uid    = "s3-unassign-test-user"

    # Assign.
    r_a = client.post(f"/api/tracks/{tid}/assign/user/{uid}",
                      json={}, headers=_trainer_headers())
    assert r_a.status_code == 200, r_a.text

    # Verify present.
    r_l = client.get(f"/api/tracks/{tid}/assignments", headers=_trainer_headers())
    user_asns = [a for a in r_l.json()["assignments"] if a["audience_type"] == "user" and a["audience_value"] == uid]
    assert len(user_asns) == 1, "Assignment should be present before unassign"

    # Unassign.
    r_d = client.delete(f"/api/tracks/{tid}/assign/user/{uid}", headers=_trainer_headers())
    assert r_d.status_code == 200, r_d.text
    d = r_d.json()
    assert d.get("completion_retained") is True, "completion_retained must be True"

    # Verify gone.
    remaining = [a for a in d.get("assignments", []) if a["audience_type"] == "user" and a["audience_value"] == uid]
    assert len(remaining) == 0, f"User entry should be removed, found: {remaining}"


# ── T5: Unassign preserves completion record ──────────────────────────────────

def test_t5_unassign_preserves_completion():
    """completion_store is NOT touched by unassign — progress survives removal."""
    client  = _make_client()
    track   = _create_track(client, status="published")
    tid     = track["id"]
    uid     = "s3-completion-test"

    # Write a completion record directly.
    import completion_store as cs
    import modules_store as _ms
    t = _ms.load_track(tid)
    module_ids = t.get("module_ids") or []
    # Set pct to something non-zero.
    with tempfile.TemporaryDirectory() as tmpdir:
        original_completion_dir = cs._COMPLETION_DIR
        cs._COMPLETION_DIR = Path(tmpdir) / "completion"
        cs._COMPLETION_DIR.mkdir()
        try:
            # Write a minimal completion entry.
            progress_before = cs.set_module_done(uid, tid, "dummy-module", module_ids=["dummy-module"])
            pct_before = progress_before.get("pct", 0)

            # Assign then unassign.
            client.post(f"/api/tracks/{tid}/assign/user/{uid}", json={}, headers=_trainer_headers())
            r_d = client.delete(f"/api/tracks/{tid}/assign/user/{uid}", headers=_trainer_headers())
            assert r_d.status_code == 200

            # Completion record must still be there.
            progress_after = cs.get_progress(uid, tid, module_ids=["dummy-module"])
            assert progress_after is not None, "completion record must exist after unassign"
            assert progress_after.get("pct") == pct_before, \
                f"Progress changed after unassign: before={pct_before} after={progress_after.get('pct')}"
        finally:
            cs._COMPLETION_DIR = original_completion_dir


# ── T6: Draft track not assignable ────────────────────────────────────────────

def test_t6_draft_track_not_assignable():
    """Assigning a draft track (bulk or individual) returns 409."""
    client = _make_client()
    track  = _create_track(client, status="draft")  # stays draft
    tid    = track["id"]

    # Bulk assign.
    r_bulk = client.post(
        f"/api/tracks/{tid}/assign",
        json={"audience_type": "role", "audience_value": "Cashier"},
        headers=_trainer_headers(),
    )
    assert r_bulk.status_code == 409, f"Expected 409 for draft bulk assign, got {r_bulk.status_code}: {r_bulk.text}"
    assert "draft" in r_bulk.text.lower(), f"Expected 'draft' in error message: {r_bulk.text}"

    # Individual assign.
    r_ind = client.post(
        f"/api/tracks/{tid}/assign/user/test-uid",
        json={},
        headers=_trainer_headers(),
    )
    assert r_ind.status_code == 409, f"Expected 409 for draft individual assign, got {r_ind.status_code}: {r_ind.text}"


# ── T7: Past-due date warns, doesn't block ────────────────────────────────────

def test_t7_past_due_warns_does_not_block():
    """A past due_date: assignment is accepted (200), not rejected.
    SHOULD-NOT-OCCUR: if the server rejects a past due date, the 'warn don't block' rule fails.
    """
    client    = _make_client()
    track     = _create_track(client, status="published")
    tid       = track["id"]
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    r = client.post(
        f"/api/tracks/{tid}/assign",
        json={"audience_type": "role", "audience_value": "Cashier", "due_date": yesterday},
        headers=_trainer_headers(),
    )
    assert r.status_code == 200, (
        f"SHOULD-NOT-OCCUR: past due date should not block assign, got {r.status_code}: {r.text}"
    )
    asns = r.json().get("assignments") or []
    assert any(a.get("due_date") == yesterday for a in asns), \
        f"Past-due assignment not persisted: {asns}"


# ── T8: Nudge throttle ────────────────────────────────────────────────────────

def test_t8_nudge_all_overdue_throttled():
    """Second call to nudge-all-overdue within 60 s returns throttled=True.
    SHOULD-NOT-OCCUR: if the second call is not throttled, the spam guard is broken.
    """
    import demo_app
    client = _make_client()
    track  = _create_track(client, status="published")
    tid    = track["id"]

    # Set a past due_date to create overdue rows.
    import modules_store as _ms
    t = _ms.load_track(tid)
    t["due_date"] = (date.today() - timedelta(days=5)).isoformat()
    _ms.save_track(t)

    # Clear any prior throttle state for this track.
    demo_app._nudge_all_last.pop(tid, None)

    r1 = client.post(f"/api/roster/{tid}/nudge-all-overdue", headers=_trainer_headers())
    assert r1.status_code == 200, r1.text
    d1 = r1.json()
    assert d1.get("throttled") is False, f"First call must not be throttled: {d1}"
    assert "last_nudged_at" in d1, "Response must include last_nudged_at"

    # Immediate second call must be throttled.
    r2 = client.post(f"/api/roster/{tid}/nudge-all-overdue", headers=_trainer_headers())
    assert r2.status_code == 200, r2.text
    d2 = r2.json()
    assert d2.get("throttled") is True, (
        f"SHOULD-NOT-OCCUR: second nudge-all-overdue within throttle window must be throttled, got: {d2}"
    )
    assert d2.get("nudged") == 0, f"Throttled call must nudge 0 learners, got: {d2}"


# ── T9: Tenancy — director sees only own district ─────────────────────────────

def test_t9_tenancy_director_scope():
    """Director (dana-director) can read roster for their district; 403 for other district."""
    import demo_app
    client = _make_client()
    track  = _create_track(client, status="published")
    tid    = track["id"]

    # dana-director district is houston-isd in the demo.
    r_ok = client.get(f"/api/roster/{tid}?isd=houston-isd", headers=_director_headers())
    assert r_ok.status_code == 200, f"Director must be able to read own district roster: {r_ok.text}"

    # Cross-district access: any other district ID should 403.
    r_deny = client.get(f"/api/roster/{tid}?isd=dallas-isd", headers=_director_headers())
    assert r_deny.status_code == 403, (
        f"SHOULD-NOT-OCCUR: director must not access another district's roster, got {r_deny.status_code}"
    )


# ── T10: Cashier 403 on assign + roster ───────────────────────────────────────

def test_t10_cashier_403():
    """Cashier (john-cashier) gets 403 on all assign and roster-write endpoints."""
    client = _make_client()
    track  = _create_track(client, status="published")
    tid    = track["id"]

    # Bulk assign.
    r_bulk = client.post(
        f"/api/tracks/{tid}/assign",
        json={"audience_type": "role", "audience_value": "Cashier"},
        headers=_cashier_headers(),
    )
    assert r_bulk.status_code == 403, f"Cashier bulk assign must be 403, got {r_bulk.status_code}"

    # Individual assign.
    r_ind = client.post(
        f"/api/tracks/{tid}/assign/user/some-uid",
        json={},
        headers=_cashier_headers(),
    )
    assert r_ind.status_code == 403, f"Cashier individual assign must be 403, got {r_ind.status_code}"

    # Roster read.
    r_roster = client.get(f"/api/roster/{tid}", headers=_cashier_headers())
    assert r_roster.status_code == 403, f"Cashier roster read must be 403, got {r_roster.status_code}"

    # Nudge.
    r_nudge = client.post(f"/api/roster/{tid}/nudge-all-overdue", headers=_cashier_headers())
    assert r_nudge.status_code == 403, f"Cashier nudge-all must be 403, got {r_nudge.status_code}"

    # Individual unassign.
    r_unasgn = client.delete(f"/api/tracks/{tid}/assign/user/some-uid", headers=_cashier_headers())
    assert r_unasgn.status_code == 403, f"Cashier unassign must be 403, got {r_unasgn.status_code}"


# ── T11: Unassigned view ──────────────────────────────────────────────────────

def test_t11_unassigned_view():
    """GET /api/tracks/{tid}/unassigned returns learners with no assignment."""
    client = _make_client()
    track  = _create_track(client, status="published")
    tid    = track["id"]

    # No assignments → at least some unassigned learners in the seeded pool.
    r = client.get(f"/api/tracks/{tid}/unassigned", headers=_trainer_headers())
    assert r.status_code == 200, r.text
    d = r.json()
    assert "unassigned" in d, f"Response must have 'unassigned' key: {d}"
    ua = d["unassigned"]
    assert isinstance(ua, list), "unassigned must be a list"
    # With no assignments, a seeded pool of 28 rows are all unassigned.
    assert len(ua) > 0, "With no assignments, there should be unassigned learners"

    # After a whole-district assignment, unassigned list should be empty.
    client.post(
        f"/api/tracks/{tid}/assign",
        json={"audience_type": "district", "audience_value": "district"},
        headers=_trainer_headers(),
    )
    r2 = client.get(f"/api/tracks/{tid}/unassigned", headers=_trainer_headers())
    assert r2.status_code == 200
    ua2 = r2.json()["unassigned"]
    assert len(ua2) == 0, f"After district-wide assignment, unassigned should be empty, got {len(ua2)}"


# ── T12: Nudge single learner ─────────────────────────────────────────────────

def test_t12_nudge_one():
    """POST /api/roster/{tid}/nudge with user_ids records a nudge entry."""
    import nudge_store as _ns
    client = _make_client()
    track  = _create_track(client, status="published")
    tid    = track["id"]
    uid    = "s3-nudge-one-test"

    r = client.post(
        f"/api/roster/{tid}/nudge",
        json={"user_ids": [uid]},
        headers=_trainer_headers(),
    )
    assert r.status_code == 200, r.text
    d = r.json()
    assert d.get("nudged") == 1, f"Expected nudged=1, got {d}"

    # Nudge record persisted.
    entry = _ns.get_nudge_state(tid, uid)
    assert entry is not None, "Nudge entry must be persisted to disk"
    assert entry["user_id"] == uid


# ── T13: Remove assignment by index ──────────────────────────────────────────

def test_t13_remove_assignment_by_index():
    """DELETE /api/tracks/{tid}/assign/{idx} removes the entry at that index."""
    client = _make_client()
    track  = _create_track(client, status="published")
    tid    = track["id"]

    # Add two assignments.
    client.post(f"/api/tracks/{tid}/assign",
                json={"audience_type": "role", "audience_value": "Cashier"},
                headers=_trainer_headers())
    client.post(f"/api/tracks/{tid}/assign",
                json={"audience_type": "role", "audience_value": "Site Manager"},
                headers=_trainer_headers())

    r_list = client.get(f"/api/tracks/{tid}/assignments", headers=_trainer_headers())
    asns = r_list.json()["assignments"]
    assert len(asns) >= 2, "Need at least 2 assignments for this test"

    # Remove index 0.
    r_del = client.delete(f"/api/tracks/{tid}/assign/0", headers=_trainer_headers())
    assert r_del.status_code == 200, r_del.text
    remaining = r_del.json()["assignments"]
    assert len(remaining) == len(asns) - 1, \
        f"Expected {len(asns)-1} assignments after removal, got {len(remaining)}"

    # Cashier: 403 on delete.
    r_cashier = client.delete(f"/api/tracks/{tid}/assign/0", headers=_cashier_headers())
    assert r_cashier.status_code == 403


# ── T14: Duplicate user-level assign is idempotent ───────────────────────────

def test_t14_duplicate_user_assign_idempotent():
    """SHOULD-NOT-OCCUR: assigning the same uid twice must NOT create two entries."""
    client = _make_client()
    track  = _create_track(client, status="published")
    tid    = track["id"]
    uid    = "s3-dup-test-uid"

    for _ in range(3):
        client.post(f"/api/tracks/{tid}/assign/user/{uid}",
                    json={}, headers=_trainer_headers())

    r = client.get(f"/api/tracks/{tid}/assignments", headers=_trainer_headers())
    user_asns = [a for a in r.json()["assignments"]
                 if a["audience_type"] == "user" and a["audience_value"] == uid]
    assert len(user_asns) == 1, (
        f"SHOULD-NOT-OCCUR: duplicate assign created {len(user_asns)} entries for uid={uid}"
    )


# ── Runner ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        test_t1_bulk_assign_role,
        test_t2_bulk_assign_district,
        test_t3_individual_assign_idempotent,
        test_t4_individual_unassign,
        test_t5_unassign_preserves_completion,
        test_t6_draft_track_not_assignable,
        test_t7_past_due_warns_does_not_block,
        test_t8_nudge_all_overdue_throttled,
        test_t9_tenancy_director_scope,
        test_t10_cashier_403,
        test_t11_unassigned_view,
        test_t12_nudge_one,
        test_t13_remove_assignment_by_index,
        test_t14_duplicate_user_assign_idempotent,
    ]
    passed = failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
            passed += 1
        except Exception as exc:
            print(f"FAIL {t.__name__}: {exc}")
            failed += 1
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{len(tests)} passed" + (f", {failed} failed" if failed else ""))
    if failed:
        sys.exit(1)
