"""Tests for AUTH-2 — voice narration store.

Run from learning-agent/ with:
    ..\\..\\learning-agent\\.venv\\Scripts\\python.exe -m pytest tests/test_narration_store.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import narration_store as ns  # noqa: E402


# ── Fixture ───────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr(ns, "_NARRATION_DIR", tmp_path / "narration")
    yield


RID  = "GUIDE-AUTH2-TEST"
SEGS = [
    {"index": 0, "audio_url": "data:audio/wav;base64,AAAA", "duration_seconds": 12.5},
    {"index": 1, "audio_url": "data:audio/wav;base64,BBBB", "duration_seconds": 8.0},
]


# ── Test 1: get_narration returns None when no record exists ──────────────────

def test_get_narration_missing_returns_none():
    assert ns.get_narration(RID) is None


# ── Test 2: save_narration creates a well-formed record ──────────────────────

def test_save_narration_record_fields():
    record = ns.save_narration(RID, SEGS, stub=True)
    assert record["resource_id"] == RID
    assert record["stub"] is True
    assert len(record["segments"]) == 2
    seg = record["segments"][0]
    assert seg["index"] == 0
    assert seg["audio_url"] == "data:audio/wav;base64,AAAA"
    assert seg["duration_seconds"] == 12.5
    assert seg["stub"] is True
    assert "generated_at" in record


# ── Test 3: round-trip — save then get returns the same data ──────────────────

def test_save_then_get_round_trips():
    ns.save_narration(RID, SEGS, stub=True)
    result = ns.get_narration(RID)
    assert result is not None
    assert len(result["segments"]) == 2
    assert result["segments"][1]["audio_url"] == "data:audio/wav;base64,BBBB"


# ── Test 4: save_narration rejects empty segments list ────────────────────────

def test_save_narration_rejects_empty_segments():
    with pytest.raises(ValueError, match="empty"):
        ns.save_narration(RID, [])


# ── Test 5: delete_narration removes the record ───────────────────────────────

def test_delete_narration_removes_file():
    ns.save_narration(RID, SEGS)
    assert ns.get_narration(RID) is not None

    deleted = ns.delete_narration(RID)
    assert deleted is True
    assert ns.get_narration(RID) is None

    # Second delete is a no-op that returns False.
    assert ns.delete_narration(RID) is False


# ── Test 6: second save overwrites the first ──────────────────────────────────

def test_save_narration_overwrites():
    ns.save_narration(RID, SEGS, stub=True)
    new_segs = [{"index": 0, "audio_url": "https://cdn.example.com/nar.mp3", "duration_seconds": 30.0}]
    ns.save_narration(RID, new_segs, stub=False)

    result = ns.get_narration(RID)
    assert len(result["segments"]) == 1
    assert result["segments"][0]["audio_url"] == "https://cdn.example.com/nar.mp3"
    assert result["stub"] is False
