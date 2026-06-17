"""Tests for AUTH-1 — multilingual lesson translation store.

Run from learning-agent/ with:
    ..\\..\\learning-agent\\.venv\\Scripts\\python.exe -m pytest tests/test_translation_store.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import translation_store as ts  # noqa: E402


# ── Fixture ───────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr(ts, "_TRANSLATIONS_DIR", tmp_path / "translations")
    yield


RID  = "GUIDE-AUTH1-TEST"
SEGS = [
    {"index": 0, "body_html": "<p>Step one.</p>"},
    {"index": 1, "body_html": "<p>Step two.</p>"},
]


# ── Test 1: get_translation returns None when nothing stored ──────────────────

def test_get_translation_missing_returns_none():
    assert ts.get_translation(RID, "es") is None


# ── Test 2: save_translation creates a well-formed record ────────────────────

def test_save_translation_record_fields():
    record = ts.save_translation(RID, "es", SEGS, stub=True)
    assert record["resource_id"] == RID
    assert record["lang"] == "es"
    assert record["stub"] is True
    assert len(record["segments"]) == 2
    assert record["segments"][0] == {"index": 0, "body_html": "<p>Step one.</p>"}
    assert "generated_at" in record


# ── Test 3: round-trip — save then get returns the same record ────────────────

def test_save_then_get_round_trips():
    ts.save_translation(RID, "fr", SEGS, stub=True)
    result = ts.get_translation(RID, "fr")
    assert result is not None
    assert result["lang"] == "fr"
    assert len(result["segments"]) == 2


# ── Test 4: lang='en' is rejected ────────────────────────────────────────────

def test_save_translation_rejects_en():
    with pytest.raises(ValueError, match="reserved"):
        ts.save_translation(RID, "en", SEGS)


# ── Test 5: invalid lang codes are rejected ───────────────────────────────────

@pytest.mark.parametrize("bad_lang", ["123", "e n", "a" * 11, ""])
def test_save_translation_rejects_invalid_lang(bad_lang):
    with pytest.raises(ValueError):
        ts.save_translation(RID, bad_lang, SEGS)


# ── Test 6: list_languages returns sorted lang codes ─────────────────────────

def test_list_languages_sorted():
    ts.save_translation(RID, "zh", SEGS)
    ts.save_translation(RID, "es", SEGS)
    ts.save_translation(RID, "fr", SEGS)

    langs = ts.list_languages(RID)
    codes = [l["lang"] for l in langs]
    assert codes == sorted(codes)
    assert set(codes) == {"es", "fr", "zh"}


# ── Test 7: overwrite — second save replaces the first ───────────────────────

def test_save_translation_overwrites():
    ts.save_translation(RID, "es", SEGS, stub=True)
    new_segs = [{"index": 0, "body_html": "<p>Updated.</p>"}]
    ts.save_translation(RID, "es", new_segs, stub=False)

    result = ts.get_translation(RID, "es")
    assert len(result["segments"]) == 1
    assert result["segments"][0]["body_html"] == "<p>Updated.</p>"
    assert result["stub"] is False
