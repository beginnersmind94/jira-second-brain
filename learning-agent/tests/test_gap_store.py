"""Tests for OPS-1 — Content gap analysis store.

Run from learning-agent/ with:
    ..\\..\\learning-agent\\.venv\\Scripts\\python.exe -m pytest tests/test_gap_store.py -v
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import gap_store as gs  # noqa: E402


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr(gs, "_GAPS_DIR",      tmp_path / "gaps")
    monkeypatch.setattr(gs, "_GAPS_FILE",     tmp_path / "gaps" / "gaps.json")
    monkeypatch.setattr(gs, "_REFUSALS_FILE", tmp_path / "gaps" / "lrn1-refusals.jsonl")
    yield


# ── Test 1: add_gap round-trip ────────────────────────────────────────────────

def test_add_gap_round_trip():
    gap = gs.add_gap("refusal", "How do I reset my PIN?", module="Cashier")
    assert gap["type"] == "refusal"
    assert gap["status"] == "open"
    assert gap["module"] == "Cashier"
    assert gap["id"]

    gaps = gs.get_gaps()
    assert len(gaps) == 1
    assert gaps[0]["id"] == gap["id"]


# ── Test 2: resolve_gap marks status ─────────────────────────────────────────

def test_resolve_gap():
    g = gs.add_gap("coverage_gap", "Meal count export is undocumented")
    updated = gs.resolve_gap(g["id"])
    assert updated is not None
    assert updated["status"] == "resolved"

    open_gaps = gs.get_gaps(status="open")
    assert not any(x["id"] == g["id"] for x in open_gaps)


# ── Test 3: add_gap rejects unknown type + empty description ─────────────────

def test_add_gap_validation():
    with pytest.raises(ValueError, match="unknown gap type"):
        gs.add_gap("ghost", "some description")

    with pytest.raises(ValueError, match="description must not be empty"):
        gs.add_gap("refusal", "   ")


# ── Test 4: log_refusal ingested as gap on next get_gaps ─────────────────────

def test_log_refusal_ingested():
    gs.log_refusal("What is the free-reduced meal threshold?", module="Reports")
    gs.log_refusal("How do I export a USDA claim?", module="Reports")

    # get_gaps triggers ingestion of the refusal log.
    gaps = gs.get_gaps(status="open")
    assert len(gaps) == 2
    assert all(g["type"] == "refusal" for g in gaps)
    assert all(g["source"] == "lrn1-refusal-log" for g in gaps)

    # Re-calling get_gaps does not double-ingest.
    gaps2 = gs.get_gaps(status="open")
    assert len(gaps2) == 2
