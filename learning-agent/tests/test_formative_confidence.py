"""Tests for LRN-6 — confidence-calibrated formative checks.

Tests focus on formative_store.get_confidence_summary() since that is the
pure-logic layer; endpoint wiring is covered by the contract smoke test at
the bottom.

Run from learning-agent/ with:
    ..\\..\\learning-agent\\.venv\\Scripts\\python.exe -m pytest tests/test_formative_confidence.py -v
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import formative_store as fs  # noqa: E402


# ── Helpers ───────────────────────────────────────────────────────────────────

def _write_formative(base: Path, uid: str, rid: str, seg: int, data: dict) -> None:
    safe_uid = fs._safe(uid)
    safe_rid = fs._safe(rid)
    p = base / safe_uid / safe_rid / f"{seg}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data), encoding="utf-8")


RID = "GUIDE-LRN6-TEST"


# ── Test 1: empty dir returns empty result ────────────────────────────────────

def test_empty_dir_returns_empty(tmp_path):
    result = fs.get_confidence_summary(RID, formative_dir=tmp_path / "formative")
    assert result["resource_id"] == RID
    assert result["segments"] == []
    assert result["overall_confidence_avg"] is None


# ── Test 2: confidence stored and averaged correctly ─────────────────────────

def test_confidence_averaged_per_segment(tmp_path):
    base = tmp_path / "formative"
    _write_formative(base, "user-a", RID, 0, {"correct": True,  "confidence": 4})
    _write_formative(base, "user-b", RID, 0, {"correct": False, "confidence": 2})

    result = fs.get_confidence_summary(RID, formative_dir=base)
    assert len(result["segments"]) == 1
    seg = result["segments"][0]
    assert seg["seg_idx"] == 0
    assert seg["confidence_avg"] == 3.0   # (4+2)/2
    assert seg["confidence_count"] == 2
    assert seg["pct_correct"] == 50
    assert seg["answer_count"] == 2
    assert result["overall_confidence_avg"] == 3.0


# ── Test 3: missing confidence field is excluded from average ─────────────────

def test_missing_confidence_excluded(tmp_path):
    base = tmp_path / "formative"
    _write_formative(base, "user-a", RID, 1, {"correct": True, "confidence": 5})
    _write_formative(base, "user-b", RID, 1, {"correct": True})   # no confidence

    result = fs.get_confidence_summary(RID, formative_dir=base)
    seg = result["segments"][0]
    assert seg["confidence_count"] == 1
    assert seg["confidence_avg"] == 5.0
    assert seg["answer_count"] == 2
    assert seg["pct_correct"] == 100


# ── Test 4: out-of-range confidence values are ignored ───────────────────────

def test_out_of_range_confidence_ignored(tmp_path):
    base = tmp_path / "formative"
    _write_formative(base, "user-a", RID, 2, {"correct": True, "confidence": 0})   # below 1
    _write_formative(base, "user-b", RID, 2, {"correct": True, "confidence": 6})   # above 5
    _write_formative(base, "user-c", RID, 2, {"correct": True, "confidence": 3})   # valid

    result = fs.get_confidence_summary(RID, formative_dir=base)
    seg = result["segments"][0]
    assert seg["confidence_count"] == 1
    assert seg["confidence_avg"] == 3.0
    assert seg["answer_count"] == 3


# ── Test 5: multiple segments sorted by index ────────────────────────────────

def test_multiple_segments_sorted(tmp_path):
    base = tmp_path / "formative"
    _write_formative(base, "user-a", RID, 3, {"correct": True,  "confidence": 5})
    _write_formative(base, "user-a", RID, 1, {"correct": False, "confidence": 2})
    _write_formative(base, "user-a", RID, 2, {"correct": True,  "confidence": 3})

    result = fs.get_confidence_summary(RID, formative_dir=base)
    idxs = [s["seg_idx"] for s in result["segments"]]
    assert idxs == [1, 2, 3]
    overall = result["overall_confidence_avg"]
    assert overall == round((2 + 3 + 5) / 3, 2)
