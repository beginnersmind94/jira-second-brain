"""Tests for tenancy.py — multi-tenant district-access enforcement.

These tests are pure-unit: they import only tenancy.py and auth.py (CurrentUser).
No FastAPI app, no database, no network. Each test is deterministic.

Coverage targets (>= 10 cases):
  TC-01  Trainer access to own district — allowed
  TC-02  Trainer access to a second assigned district — allowed
  TC-03  Trainer access to unassigned district — 403
  TC-04  Learner access to own district — allowed
  TC-05  Learner access to another district — 403
  TC-06  CN Director access to own district — allowed
  TC-07  CN Director access to another district — 403
  TC-08  filter_to_accessible_districts for trainer — returns subset
  TC-09  filter_to_accessible_districts for learner — returns only own ISD
  TC-10  filter_to_accessible_districts empty input list
  TC-11  get_user_districts for trainer returns full book
  TC-12  get_user_districts for learner returns single-element list
  TC-13  get_user_districts with no district_id and not trainer — returns []
  TC-14  assert_district_access with empty isd — no-op, never raises
  TC-15  403 response body contains machine-readable error code
"""
from __future__ import annotations

import pytest
from fastapi import HTTPException

from auth import CurrentUser
from tenancy import assert_district_access, filter_to_accessible_districts, get_user_districts

# ── Fixture users ──────────────────────────────────────────────────────────────

def _trainer(*districts: str) -> CurrentUser:
    """Trainer with the given book of business (district ids)."""
    return CurrentUser(
        id="trainer-001",
        name="Sam Trainer",
        role="Trainer",
        district_id=districts[0] if districts else None,
        districts=list(districts),
        is_trainer=True,
    )


def _learner(district_id: str) -> CurrentUser:
    """Learner (or CN Director) scoped to a single district."""
    return CurrentUser(
        id="learner-001",
        name="Jo Learner",
        role="Cashier",
        district_id=district_id,
        districts=[],  # learners don't populate districts list
        is_trainer=False,
    )


def _director(district_id: str) -> CurrentUser:
    return CurrentUser(
        id="director-001",
        name="Dana Director",
        role="CN Director",
        district_id=district_id,
        districts=[],
        is_trainer=False,
    )


# ── TC-01  Trainer access to own (first) district ─────────────────────────────
def test_trainer_can_access_own_district():
    user = _trainer("houston-isd", "dallas-isd")
    # Should not raise.
    assert_district_access(user, "houston-isd")


# ── TC-02  Trainer access to a second district in their book ──────────────────
def test_trainer_can_access_second_district():
    user = _trainer("houston-isd", "dallas-isd", "austin-isd")
    assert_district_access(user, "austin-isd")


# ── TC-03  Trainer access to unassigned district → 403 ───────────────────────
def test_trainer_denied_unassigned_district():
    user = _trainer("houston-isd", "dallas-isd")
    with pytest.raises(HTTPException) as exc_info:
        assert_district_access(user, "austin-isd")
    assert exc_info.value.status_code == 403


# ── TC-04  Learner access to own district ─────────────────────────────────────
def test_learner_can_access_own_district():
    user = _learner("houston-isd")
    assert_district_access(user, "houston-isd")


# ── TC-05  Learner access to another district → 403 ──────────────────────────
def test_learner_denied_other_district():
    user = _learner("houston-isd")
    with pytest.raises(HTTPException) as exc_info:
        assert_district_access(user, "dallas-isd")
    assert exc_info.value.status_code == 403


# ── TC-06  CN Director access to own district ─────────────────────────────────
def test_director_can_access_own_district():
    user = _director("dallas-isd")
    assert_district_access(user, "dallas-isd")


# ── TC-07  CN Director access to another district → 403 ──────────────────────
def test_director_denied_other_district():
    user = _director("dallas-isd")
    with pytest.raises(HTTPException) as exc_info:
        assert_district_access(user, "houston-isd")
    assert exc_info.value.status_code == 403


# ── TC-08  filter_to_accessible_districts for trainer ─────────────────────────
def test_filter_trainer_returns_intersection():
    user = _trainer("houston-isd", "dallas-isd")
    result = filter_to_accessible_districts(user, ["houston-isd", "austin-isd", "dallas-isd"])
    assert result == ["houston-isd", "dallas-isd"]


# ── TC-09  filter_to_accessible_districts for learner ─────────────────────────
def test_filter_learner_returns_only_own():
    user = _learner("houston-isd")
    result = filter_to_accessible_districts(user, ["houston-isd", "dallas-isd", "austin-isd"])
    assert result == ["houston-isd"]


# ── TC-10  filter_to_accessible_districts empty input list ────────────────────
def test_filter_empty_input_returns_empty():
    user = _trainer("houston-isd", "dallas-isd")
    assert filter_to_accessible_districts(user, []) == []


# ── TC-11  get_user_districts for trainer returns full book ───────────────────
def test_get_user_districts_trainer():
    user = _trainer("houston-isd", "dallas-isd", "austin-isd")
    districts = get_user_districts(user)
    assert set(districts) == {"houston-isd", "dallas-isd", "austin-isd"}


# ── TC-12  get_user_districts for learner returns single-element list ─────────
def test_get_user_districts_learner():
    user = _learner("cy-fair-isd")
    assert get_user_districts(user) == ["cy-fair-isd"]


# ── TC-13  get_user_districts no district_id non-trainer → empty list ─────────
def test_get_user_districts_no_district():
    user = CurrentUser(
        id="anon-001",
        name="Anon",
        role="Learner",
        district_id=None,
        districts=[],
        is_trainer=False,
    )
    assert get_user_districts(user) == []


# ── TC-14  assert_district_access empty isd is a no-op ───────────────────────
def test_assert_empty_isd_is_noop():
    # A learner should NOT get 403 when no specific district is requested.
    user = _learner("houston-isd")
    # All of these should be silent no-ops:
    assert_district_access(user, "")
    assert_district_access(user, "   ")
    assert_district_access(user, None)  # type: ignore[arg-type]


# ── TC-15  403 body contains machine-readable error code ─────────────────────
def test_403_body_has_error_code():
    user = _learner("houston-isd")
    with pytest.raises(HTTPException) as exc_info:
        assert_district_access(user, "dallas-isd")
    detail = exc_info.value.detail
    assert isinstance(detail, dict), "detail should be a dict for machine-readable errors"
    assert detail.get("error") == "district_access_denied"
    # Human-readable message must mention the requested district.
    assert "dallas-isd" in detail.get("detail", "")


# ── TC-16  filter preserves input order ───────────────────────────────────────
def test_filter_preserves_order():
    user = _trainer("cy-fair-isd", "austin-isd", "houston-isd")
    isds = ["houston-isd", "cy-fair-isd", "austin-isd"]
    result = filter_to_accessible_districts(user, isds)
    assert result == isds  # same order as input


# ── TC-17  Trainer with empty book can't access any district ──────────────────
def test_trainer_empty_book_denied():
    user = _trainer()  # no districts
    with pytest.raises(HTTPException) as exc_info:
        assert_district_access(user, "houston-isd")
    assert exc_info.value.status_code == 403


# ── TC-18  filter_to_accessible_districts for director ────────────────────────
def test_filter_director_returns_only_own():
    user = _director("austin-isd")
    result = filter_to_accessible_districts(user, ["houston-isd", "austin-isd"])
    assert result == ["austin-isd"]
