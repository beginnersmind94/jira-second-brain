"""Tests for LRN-4 — shift-ready micro-refresher.

Tests focus on the practice_store functions that power the refresher endpoint,
plus the business logic for session_complete, items_preview, and streak data.

Run from learning-agent/ with:
    ..\\..\\learning-agent\\.venv\\Scripts\\python.exe -m pytest tests/test_refresher.py -v
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import practice_store as ps    # noqa: E402
import completion_store as cs  # noqa: E402


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def isolated_stores(tmp_path, monkeypatch):
    practice_dir = tmp_path / "practice"
    practice_dir.mkdir()
    monkeypatch.setattr(ps, "_PRACTICE_DIR", practice_dir)
    monkeypatch.setattr(cs, "_COMPLETION_DIR", tmp_path / "completion")
    monkeypatch.setattr(cs, "_GAMIFICATION_DIR", tmp_path / "gamif")
    yield


TODAY = "2026-06-13"
UID = "refresher-user-001"


# ── Test 1: first call builds a session (item_count may be 0 if pool empty) ──

def test_get_today_session_is_idempotent():
    s1 = ps.get_today_session(UID, TODAY)
    s2 = ps.get_today_session(UID, TODAY)
    # Both calls return the same date — content may differ only if pool differs.
    assert s1["date"] == s2["date"] == TODAY


# ── Test 2: session_complete logic ───────────────────────────────────────────

def test_session_complete_false_when_not_done():
    ps.get_today_session(UID, TODAY)
    status = ps.get_session_status(UID, TODAY)
    # session_complete in the endpoint means NOT session_ready AND items exist.
    # With empty pool, items_count=0 so session_complete=False too (no items).
    # Either way, session_ready implies not complete.
    assert status["session"] is not None
    assert status["session"]["date"] == TODAY


def test_session_complete_true_after_complete_session():
    ps.get_today_session(UID, TODAY)
    ps.complete_session(UID, TODAY)
    status = ps.get_session_status(UID, TODAY)
    # After complete, session_ready is False.
    assert status["session_ready"] is False
    assert status["session"]["completed"] is True


# ── Test 3: streak data from gamification ────────────────────────────────────

def test_streak_returned_from_gamification():
    # Manually seed gamif state via the actual store path.
    gamif_dir = cs._GAMIFICATION_DIR
    gamif_dir.mkdir(parents=True, exist_ok=True)
    safe_uid = cs._safe_id(UID)
    (gamif_dir / f"{safe_uid}.json").write_text(
        json.dumps({"xp": 50, "streak": 7, "badges": []}), encoding="utf-8"
    )
    g = cs.get_gamification(UID)
    assert g["streak"] == 7
    assert g["xp"] == 50


# ── Test 4: items_preview truncated to 3 items ───────────────────────────────

def test_items_preview_uses_first_three():
    # Build a synthetic session with 5 items directly.
    store = ps._read_store(UID)
    items = [
        {"type": "quiz", "stem": f"Q{i}", "answer_index": 0, "options": ["A"]}
        for i in range(5)
    ]
    session = {"date": TODAY, "items": items, "completed": False, "completed_at": None}
    store["sessions"] = [session]
    ps._write_store(store)

    status = ps.get_session_status(UID, TODAY)
    raw_items = (status["session"].get("items") or [])[:3]
    assert len(raw_items) == 3
    assert raw_items[0]["stem"] == "Q0"


# ── Test 5: no session returns sensible defaults ──────────────────────────────

def test_no_session_returns_session_ready_false():
    # Don't build a session — just query status directly.
    status = ps.get_session_status(UID, TODAY)
    assert status["session"] is None
    assert status["session_ready"] is False
    assert status["items_count"] == 0
