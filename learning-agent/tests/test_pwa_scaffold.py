"""Tests for PLT-1 — Offline PWA scaffold.

Verifies that all required PWA artefacts are present and correctly wired.

Run from learning-agent/ with:
    ..\\..\\learning-agent\\.venv\\Scripts\\python.exe -m pytest tests/test_pwa_scaffold.py -v
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

STATIC = Path(__file__).resolve().parent.parent / "static"
HTML   = STATIC / "index.html"


# ── Test 1: manifest.json is valid with required PWA fields ──────────────────

def test_manifest_valid():
    manifest_path = STATIC / "manifest.json"
    assert manifest_path.exists(), "static/manifest.json must exist"

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert "name" in manifest,      "manifest must have 'name'"
    assert "start_url" in manifest, "manifest must have 'start_url'"
    assert "display" in manifest,   "manifest must have 'display'"
    assert isinstance(manifest.get("icons"), list) and manifest["icons"], \
        "manifest must have at least one icon"
    # Each icon must have src and sizes.
    for icon in manifest["icons"]:
        assert "src" in icon and "sizes" in icon


# ── Test 2: sw.js exists and declares required event listeners ────────────────

def test_sw_has_required_listeners():
    sw_path = STATIC / "sw.js"
    assert sw_path.exists(), "static/sw.js must exist"

    src = sw_path.read_text(encoding="utf-8")
    assert "addEventListener('install'" in src,  "sw.js must handle 'install'"
    assert "addEventListener('activate'" in src, "sw.js must handle 'activate'"
    assert "addEventListener('fetch'" in src,    "sw.js must handle 'fetch'"


# ── Test 3: index.html registers the service worker ──────────────────────────

def test_sw_registered_in_html():
    src = HTML.read_text(encoding="utf-8")
    assert "serviceWorker" in src,          "index.html must reference serviceWorker"
    assert "serviceWorker.register" in src, "index.html must call serviceWorker.register()"
    assert "/sw.js" in src,                 "index.html must register /sw.js (root scope)"


# ── Test 4: offline banner + IDB queue are wired in index.html ───────────────

def test_offline_infrastructure_in_html():
    src = HTML.read_text(encoding="utf-8")
    assert "offline-banner" in src,       "index.html must contain #offline-banner element"
    assert "_offlineQueuePush" in src,    "index.html must define _offlineQueuePush()"
    assert "_offlineQueueFlush" in src,   "index.html must define _offlineQueueFlush()"
    assert "window.addEventListener('offline'" in src or \
           "addEventListener('offline'" in src, \
        "index.html must listen for the 'offline' window event"
    assert "rel=\"manifest\"" in src, "index.html must link to the web app manifest"
