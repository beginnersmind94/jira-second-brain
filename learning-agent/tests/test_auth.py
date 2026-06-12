"""Tests for auth.py — the SSO/identity scaffold.

Run from learning-agent/ with the sibling .venv:
    ../../learning-agent/.venv/Scripts/python.exe -m pytest tests/test_auth.py -v

Tests cover:
  - Each named demo persona returns correct field values
  - Default (no header, no query param) falls back to john-cashier
  - X-Demo-User header takes effect
  - ?demo_user= query-param fallback
  - Unknown persona key falls back to john-cashier
  - Production stub _get_sso_user() returns None (not yet wired)
  - CurrentUser dataclass fields are present and typed correctly
"""
import sys
from pathlib import Path

import pytest

# ── Make auth importable without the full demo_app boot sequence ───────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from auth import CurrentUser, _get_sso_user, get_current_user, _DEMO_PERSONAS, _DEFAULT_PERSONA_KEY


# ── Minimal Request stub ───────────────────────────────────────────────────────
class _FakeRequest:
    """Minimal stub that satisfies get_current_user(request: Request) without
    needing a live FastAPI/Starlette app. Mimics only .headers and .query_params."""

    def __init__(self, headers: dict | None = None, query_params: dict | None = None):
        self.headers = headers or {}
        self.query_params = query_params or {}


# ── CurrentUser dataclass ──────────────────────────────────────────────────────


def test_current_user_has_all_required_fields():
    """CurrentUser must expose id, name, role, district_id, districts, is_trainer."""
    u = CurrentUser(
        id="u-001", name="Test User", role="Cashier",
        district_id="houston-isd", districts=[], is_trainer=False,
    )
    assert u.id == "u-001"
    assert u.name == "Test User"
    assert u.role == "Cashier"
    assert u.district_id == "houston-isd"
    assert u.districts == []
    assert u.is_trainer is False


def test_current_user_districts_defaults_to_empty_list():
    """districts field has a default of [] so it is never None."""
    u = CurrentUser(id="x", name="X", role="Cashier", district_id="d1")
    assert u.districts == []


# ── Demo personas ─────────────────────────────────────────────────────────────


def test_john_cashier_persona():
    """X-Demo-User: john-cashier → John Doe, Cashier, Houston ISD, not a trainer."""
    req = _FakeRequest(headers={"X-Demo-User": "john-cashier"})
    u = get_current_user(req)
    assert u.name == "John Doe"
    assert u.role == "Cashier"
    assert u.district_id == "houston-isd"
    assert u.is_trainer is False
    assert u.districts == []


def test_dana_director_persona():
    """X-Demo-User: dana-director → Dana Reyes, CN Director, Houston ISD, not a trainer."""
    req = _FakeRequest(headers={"X-Demo-User": "dana-director"})
    u = get_current_user(req)
    assert u.name == "Dana Reyes"
    assert u.role == "CN Director"
    assert u.district_id == "houston-isd"
    assert u.is_trainer is False


def test_sam_trainer_persona():
    """X-Demo-User: sam-trainer → Sam Rivera, Trainer, no home district, multi-district."""
    req = _FakeRequest(headers={"X-Demo-User": "sam-trainer"})
    u = get_current_user(req)
    assert u.name == "Sam Rivera"
    assert u.role == "Trainer"
    assert u.district_id is None
    assert u.is_trainer is True
    assert "houston-isd" in u.districts
    assert "aldine-isd" in u.districts
    assert "klein-isd" in u.districts


# ── Fallback / default behaviour ──────────────────────────────────────────────


def test_no_header_defaults_to_john_cashier():
    """No X-Demo-User header and no query param → default persona (john-cashier)."""
    req = _FakeRequest()
    u = get_current_user(req)
    default = _DEMO_PERSONAS[_DEFAULT_PERSONA_KEY]
    assert u.name == default.name
    assert u.role == default.role
    assert u.district_id == default.district_id


def test_unknown_persona_key_falls_back_to_default():
    """An unrecognised header value falls back to the default persona."""
    req = _FakeRequest(headers={"X-Demo-User": "nobody-known"})
    u = get_current_user(req)
    default = _DEMO_PERSONAS[_DEFAULT_PERSONA_KEY]
    assert u.name == default.name


def test_query_param_demo_user_is_accepted():
    """?demo_user= query param is accepted when the header is absent."""
    req = _FakeRequest(query_params={"demo_user": "dana-director"})
    u = get_current_user(req)
    assert u.name == "Dana Reyes"
    assert u.role == "CN Director"


def test_header_takes_precedence_over_query_param():
    """When both header and query param are present, the header wins.
    (SSO always takes priority over both; this tests the demo-bypass ordering.)
    """
    req = _FakeRequest(
        headers={"X-Demo-User": "sam-trainer"},
        query_params={"demo_user": "john-cashier"},
    )
    u = get_current_user(req)
    assert u.role == "Trainer"  # header wins


# ── Production SSO stub ───────────────────────────────────────────────────────


def test_production_sso_stub_returns_none():
    """_get_sso_user() must return None until the real SSO is implemented.
    Returning None causes get_current_user() to fall through to the demo bypass,
    so the demo never breaks when the hook isn't wired yet."""
    req = _FakeRequest()
    result = _get_sso_user(req)
    assert result is None


def test_get_current_user_returns_current_user_instance():
    """get_current_user() always returns a CurrentUser, never None."""
    req = _FakeRequest()
    u = get_current_user(req)
    assert isinstance(u, CurrentUser)
