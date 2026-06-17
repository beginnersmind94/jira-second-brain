"""Tests for AUTH-3 — printable job aid store.

Run from learning-agent/ with:
    ..\\..\\learning-agent\\.venv\\Scripts\\python.exe -m pytest tests/test_jobaid_store.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import jobaid_store as js  # noqa: E402


# ── Fixture ───────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr(js, "_JOB_AIDS_DIR", tmp_path / "job-aids")
    yield


RID  = "GUIDE-AUTH3-TEST"
HTML = "<html><body><h1>Job Aid</h1><p>Step one.</p></body></html>"
QR   = "data:image/svg+xml;base64,AAAA"


# ── Test 1: get_job_aid returns None when no record ───────────────────────────

def test_get_job_aid_missing_returns_none():
    assert js.get_job_aid(RID) is None


# ── Test 2: save_job_aid creates a well-formed record ────────────────────────

def test_save_job_aid_record_fields():
    record = js.save_job_aid(RID, HTML, QR)
    assert record["resource_id"] == RID
    assert record["html"] == HTML
    assert record["qr_data_uri"] == QR
    assert "generated_at" in record


# ── Test 3: round-trip — save then get returns the same content ───────────────

def test_save_then_get_round_trips():
    js.save_job_aid(RID, HTML, QR)
    result = js.get_job_aid(RID)
    assert result is not None
    assert result["html"] == HTML
    assert result["qr_data_uri"] == QR


# ── Test 4: save_job_aid rejects empty HTML ───────────────────────────────────

def test_save_job_aid_rejects_empty_html():
    with pytest.raises(ValueError, match="empty"):
        js.save_job_aid(RID, "   ")


# ── Test 5: delete_job_aid removes record; second call returns False ──────────

def test_delete_job_aid():
    js.save_job_aid(RID, HTML)
    assert js.get_job_aid(RID) is not None

    assert js.delete_job_aid(RID) is True
    assert js.get_job_aid(RID) is None
    assert js.delete_job_aid(RID) is False
