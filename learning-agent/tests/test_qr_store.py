"""Tests for PLT-2 — QR code generation + scan analytics store.

Run from learning-agent/ with:
    ..\\..\\learning-agent\\.venv\\Scripts\\python.exe -m pytest tests/test_qr_store.py -v
"""
from __future__ import annotations

import base64
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import qr_store as qs  # noqa: E402


# ── Fixture ───────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr(qs, "_DATA_DIR", tmp_path)
    monkeypatch.setattr(qs, "_ANALYTICS", tmp_path / "qr-analytics.jsonl")
    yield


# ── Test 1: gen_qr_svg returns a valid data-URI ───────────────────────────────

def test_gen_qr_svg_returns_data_uri():
    result = qs.gen_qr_svg("https://example.com/lesson/GUIDE-001")
    assert result.startswith("data:image/svg+xml;base64,")
    # Base64 payload decodes to valid SVG.
    payload = result.split(",", 1)[1]
    svg = base64.b64decode(payload).decode()
    assert "<svg" in svg
    assert "</svg>" in svg


# ── Test 2: same URL always produces the same QR (deterministic) ──────────────

def test_gen_qr_svg_is_deterministic():
    url = "/?lesson=GUIDE-PLT2"
    assert qs.gen_qr_svg(url) == qs.gen_qr_svg(url)


# ── Test 3: different URLs produce different QR patterns ─────────────────────

def test_gen_qr_svg_differs_by_url():
    a = qs.gen_qr_svg("/?lesson=GUIDE-001")
    b = qs.gen_qr_svg("/?lesson=GUIDE-002")
    assert a != b


# ── Test 4: scan analytics round-trip ────────────────────────────────────────

def test_qr_analytics_round_trip():
    # Empty initially.
    assert qs.get_analytics() == []

    url_a = "/?lesson=GUIDE-001"
    url_b = "/?lesson=GUIDE-002"

    qs.record_qr_scan(url_a)
    qs.record_qr_scan(url_a)
    qs.record_qr_scan(url_b)

    results = qs.get_analytics()
    counts  = {r["url"]: r["count"] for r in results}

    assert counts[url_a] == 2
    assert counts[url_b] == 1
    # Sorted by count descending — url_a first.
    assert results[0]["url"] == url_a
