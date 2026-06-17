"""Tests for OPS-3 — Regulatory compliance calendar store.

Run from learning-agent/ with:
    ..\\..\\learning-agent\\.venv\\Scripts\\python.exe -m pytest tests/test_deadline_store.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import deadline_store as ds  # noqa: E402


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr(ds, "_DATA_DIR",       tmp_path)
    monkeypatch.setattr(ds, "_DEADLINES_FILE", tmp_path / "regulatory-dates.json")
    yield


# ── Test 1: add_deadline round-trip ──────────────────────────────────────────

def test_add_deadline_round_trip():
    dl = ds.add_deadline(
        title="USDA NSLP annual training",
        date="2026-09-30",
        module="Nutrition",
        scope="federal",
    )
    assert dl["title"] == "USDA NSLP annual training"
    assert dl["date"] == "2026-09-30"
    assert dl["scope"] == "federal"
    assert dl["id"]

    results = ds.get_deadlines()
    assert len(results) == 1
    assert results[0]["id"] == dl["id"]


# ── Test 2: validation errors ─────────────────────────────────────────────────

def test_add_deadline_validation():
    with pytest.raises(ValueError, match="title"):
        ds.add_deadline(title="", date="2026-09-30")

    with pytest.raises(ValueError, match="date"):
        ds.add_deadline(title="Some deadline", date="09/30/2026")  # wrong format

    with pytest.raises(ValueError, match="scope"):
        ds.add_deadline(title="Some deadline", date="2026-09-30", scope="galaxy")


# ── Test 3: upcoming_only filter ─────────────────────────────────────────────

def test_upcoming_only_filter():
    ds.add_deadline("Past deadline",   date="2025-01-01")
    ds.add_deadline("Future deadline", date="2027-12-31")

    all_dl = ds.get_deadlines(upcoming_only=False, today="2026-06-14")
    assert len(all_dl) == 2

    upcoming = ds.get_deadlines(upcoming_only=True, today="2026-06-14")
    assert len(upcoming) == 1
    assert upcoming[0]["title"] == "Future deadline"


# ── Test 4: days_until + delete ───────────────────────────────────────────────

def test_days_until_and_delete():
    assert ds.days_until("2026-06-24", today="2026-06-14") == 10
    assert ds.days_until("2026-06-10", today="2026-06-14") == -4

    dl = ds.add_deadline("Temp date", date="2026-12-31")
    deleted = ds.delete_deadline(dl["id"])
    assert deleted is True
    assert ds.get_deadlines() == []
    # Second delete returns False.
    assert ds.delete_deadline(dl["id"]) is False
