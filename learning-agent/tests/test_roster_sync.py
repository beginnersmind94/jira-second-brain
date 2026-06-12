"""
Tests for roster_sync.py — RosterSyncClient (stub mode).

Run from learning-agent/ with the sibling .venv:
    ../../learning-agent/.venv/Scripts/python.exe -m pytest tests/test_roster_sync.py -v

All tests run fully offline in stub mode (no real credentials, no network calls).
"""
import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

# Make learning-agent importable when pytest is invoked from elsewhere.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from roster_sync import RosterSyncClient, _seeded_roster, _WRITEBACK_LOG


# ── Helpers ───────────────────────────────────────────────────────────────────


def _run(coro):
    """Run a coroutine synchronously (avoids asyncio.run() nesting issues)."""
    return asyncio.get_event_loop().run_until_complete(coro)


@pytest.fixture(autouse=True)
def clean_writeback_log(tmp_path, monkeypatch):
    """Redirect the writeback log to a temp file so tests don't touch the real log."""
    fake_log = tmp_path / "writeback-stub.jsonl"
    monkeypatch.setattr("roster_sync._WRITEBACK_LOG", fake_log)
    yield fake_log


@pytest.fixture
def stub_client():
    """RosterSyncClient with no credentials -> always stub mode."""
    return RosterSyncClient(api_url="", api_key="")


@pytest.fixture
def prod_client():
    """RosterSyncClient with fake credentials -> production mode (network mocked)."""
    return RosterSyncClient(api_url="https://api.schoolcafe.example.com", api_key="test-key-abc")


# ── 1. is_stub property ───────────────────────────────────────────────────────


def test_is_stub_when_no_credentials():
    client = RosterSyncClient(api_url="", api_key="")
    assert client.is_stub is True


def test_is_stub_false_when_both_credentials_set():
    client = RosterSyncClient(api_url="https://api.example.com", api_key="secret")
    assert client.is_stub is False


def test_is_stub_true_when_only_url_set():
    client = RosterSyncClient(api_url="https://api.example.com", api_key="")
    assert client.is_stub is True


def test_is_stub_true_when_only_key_set():
    client = RosterSyncClient(api_url="", api_key="secret")
    assert client.is_stub is True


# ── 2. Stub roster responses ──────────────────────────────────────────────────


def test_stub_get_district_roster_returns_list(stub_client):
    roster = _run(stub_client.get_district_roster("houston-isd"))
    assert isinstance(roster, list)
    assert len(roster) >= 18   # seeded minimum is 18


def test_stub_roster_contains_required_fields(stub_client):
    roster = _run(stub_client.get_district_roster("dallas-isd"))
    for member in roster:
        for field in ("id", "name", "role", "site", "email"):
            assert field in member, f"Missing field '{field}' in roster entry: {member}"


def test_stub_roster_is_deterministic(stub_client):
    """Same district ID always produces the same roster (seeded RNG)."""
    roster_a = _run(stub_client.get_district_roster("austin-isd"))
    roster_b = _run(stub_client.get_district_roster("austin-isd"))
    assert roster_a == roster_b


def test_stub_roster_differs_by_district(stub_client):
    """Different districts produce different rosters."""
    houston = _run(stub_client.get_district_roster("houston-isd"))
    dallas  = _run(stub_client.get_district_roster("dallas-isd"))
    # Names will differ between the two deterministic sets
    assert {m["name"] for m in houston} != {m["name"] for m in dallas}


# ── 3. Writeback log format ───────────────────────────────────────────────────


def test_stub_sync_completion_returns_true(stub_client):
    result = _run(stub_client.sync_completion("houston-isd", "user-001", "track-abc", 75, False))
    assert result is True


def test_stub_sync_completion_writes_jsonl(stub_client, clean_writeback_log):
    _run(stub_client.sync_completion("dallas-isd", "user-007", "track-xyz", 50, False))
    assert clean_writeback_log.exists()
    lines = [l for l in clean_writeback_log.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["district_id"] == "dallas-isd"
    assert record["learner_id"] == "user-007"
    assert record["track_id"] == "track-xyz"
    assert record["completion_pct"] == 50
    assert record["certified"] is False
    assert "at" in record  # ISO timestamp present


def test_stub_sync_completion_certified_flag(stub_client, clean_writeback_log):
    _run(stub_client.sync_completion("austin-isd", "user-042", "track-cert", 100, True))
    lines = [l for l in clean_writeback_log.read_text(encoding="utf-8").splitlines() if l.strip()]
    record = json.loads(lines[0])
    assert record["certified"] is True
    assert record["completion_pct"] == 100


def test_stub_writeback_appends_multiple_records(stub_client, clean_writeback_log):
    """Each sync_completion call appends a new line (log is append-only)."""
    _run(stub_client.sync_completion("houston-isd", "u1", "t1", 25, False))
    _run(stub_client.sync_completion("houston-isd", "u2", "t1", 100, True))
    lines = [l for l in clean_writeback_log.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(lines) == 2
    r1, r2 = json.loads(lines[0]), json.loads(lines[1])
    assert r1["learner_id"] == "u1"
    assert r2["learner_id"] == "u2"
    assert r2["certified"] is True


# ── 4. Non-fatal failure handling ────────────────────────────────────────────


def test_stub_sync_updates_last_sync_timestamp(stub_client, clean_writeback_log):
    """last_sync is None before any call, then set after a successful sync."""
    assert stub_client.status()["last_sync"] is None
    _run(stub_client.sync_completion("houston-isd", "u1", "t1", 10, False))
    assert stub_client.status()["last_sync"] is not None


def test_status_reports_stub_true_when_no_creds(stub_client):
    s = stub_client.status()
    assert s["stub"] is True
    assert s["env_configured"] is False
    assert s["last_sync"] is None


def test_status_reports_env_configured_for_prod_client(prod_client):
    s = prod_client.status()
    assert s["stub"] is False
    assert s["env_configured"] is True


def test_prod_client_roster_falls_back_on_httpx_import_error(prod_client):
    """If httpx is missing in production mode, stub roster is returned (non-fatal)."""
    import builtins
    real_import = builtins.__import__

    def _block_httpx(name, *args, **kwargs):
        if name == "httpx":
            raise ImportError("httpx not installed")
        return real_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=_block_httpx):
        roster = _run(prod_client.get_district_roster("houston-isd"))
    # Falls back to seeded data -- should be a non-empty list
    assert isinstance(roster, list)
    assert len(roster) > 0


# ── 5. sync_completion called after cert issuance (integration smoke) ─────────


def test_sync_completion_called_with_certified_true_on_cert(stub_client, clean_writeback_log):
    """Smoke test that certified=True records are written with completion_pct=100."""
    _run(stub_client.sync_completion("cy-fair-isd", "cashier-99", "new-cashier-track", 100, certified=True))
    lines = [l for l in clean_writeback_log.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(lines) == 1
    rec = json.loads(lines[0])
    assert rec["certified"] is True
    assert rec["completion_pct"] == 100
    assert rec["track_id"] == "new-cashier-track"
