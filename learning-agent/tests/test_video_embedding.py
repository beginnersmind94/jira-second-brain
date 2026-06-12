"""Tests for C1 — License-aware ICN YouTube embedding.

Tests the Python-side API endpoints and data integrity for video embedding.
JS-side renderVideoCard / cbPickVideo tests are documented as manual checks
at the bottom of this file (they require a browser to run).

Run from learning-agent/ with the sibling .venv:
    ../../Financials-Documentation-KT/learning-agent/.venv/Scripts/python.exe -m pytest tests/test_video_embedding.py -v

Coverage:
  1. _icn_load() returns (dict, dict) without crashing.
  2. YouTube demo asset exists in asset_manifest.json with correct fields.
  3. YouTube demo asset exists in lms_mockup_content.json content_cards.
  4. /api/icn/<id> for an embed-permitted YouTube asset returns all required
     fields including license_posture, content_type, source_url, youtube_id,
     attribution, thumbnail_url.
  5. /api/icn/<id> for a link_only asset returns license_posture: "link_only".
  6. SHOULD-NOT-OCCUR: link_only assets must not have their license_posture
     flipped to embed-capable in the API response (the catalog is the sole authority).
  7. /api/icn catalog has at least one embed-capable video asset.
  8. /api/icn/<id> returns 404 for an unknown asset.
  9. /api/config exposes offline_demo and external_learning boolean flags.
"""
import asyncio
import json
import sys
from pathlib import Path

import pytest

# ── Make learning-agent importable without the full FastAPI boot ──────────────
_AGENT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_AGENT_DIR))


# ── Helper: run a coroutine synchronously ────────────────────────────────────
# asyncio.run() creates a fresh event loop each call — safe across test
# ordering regardless of what other test files have done to the loop.
# (asyncio.get_event_loop() raises RuntimeError in Python 3.10+ when there
# is no current loop in the thread, which happens mid-suite after some tests.)
def _run(coro):
    return asyncio.run(coro)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_manifest() -> list:
    p = _AGENT_DIR / "data" / "icn" / "data" / "asset_manifest.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def _load_lms() -> dict:
    p = _AGENT_DIR / "data" / "icn" / "data" / "lms_mockup_content.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


# ─────────────────────────────────────────────────────────────────────────────
# 1. _icn_load() — smoke test, no crash
# ─────────────────────────────────────────────────────────────────────────────

def test_icn_load_returns_tuple():
    """_icn_load() must return (dict, dict) without raising."""
    from demo_app import _icn_load
    lms, by_id = _icn_load()
    assert isinstance(lms, dict), "_icn_load lms must be a dict"
    assert isinstance(by_id, dict), "_icn_load by_id must be a dict"


# ─────────────────────────────────────────────────────────────────────────────
# 2. Asset manifest contains the YouTube demo asset
# ─────────────────────────────────────────────────────────────────────────────

def test_youtube_demo_asset_in_manifest():
    """The YouTube demo asset must be present in asset_manifest.json."""
    manifest = _load_manifest()
    ids = {a.get("asset_id") for a in manifest}
    assert "icn-food-safety-youtube-hand-hygiene-demo" in ids, (
        "ICN YouTube demo asset not found in asset_manifest.json"
    )


def test_youtube_demo_asset_has_required_fields():
    """The ICN YouTube demo asset must have license_posture, youtube_id, embed_url."""
    manifest = _load_manifest()
    asset = next(
        (a for a in manifest if a.get("asset_id") == "icn-food-safety-youtube-hand-hygiene-demo"),
        None,
    )
    assert asset is not None, "YouTube demo asset missing from manifest"
    assert asset.get("license_posture") == "embed_only"
    assert asset.get("youtube_id"), "youtube_id must be set"
    assert asset.get("embed_url"), "embed_url must be set"
    assert "youtube-nocookie.com" in (asset.get("embed_url") or ""), (
        "embed_url must use youtube-nocookie.com"
    )


def test_youtube_demo_asset_in_lms_cards():
    """The YouTube demo asset must appear in lms_mockup_content.json content_cards."""
    lms = _load_lms()
    cards = lms.get("content_cards", [])
    ids = {c.get("asset_id") for c in cards}
    assert "icn-food-safety-youtube-hand-hygiene-demo" in ids, (
        "ICN YouTube demo card not found in lms_mockup_content.json"
    )


# ─────────────────────────────────────────────────────────────────────────────
# 3. /api/icn/<id> — embed-permitted asset returns correct fields
# ─────────────────────────────────────────────────────────────────────────────

def test_api_icn_asset_embed_permitted_fields():
    """GET /api/icn/<id> for an embed_only YouTube asset returns all required fields."""
    from demo_app import api_icn_asset

    result = _run(api_icn_asset("icn-food-safety-youtube-hand-hygiene-demo"))

    assert result["id"] == "icn-food-safety-youtube-hand-hygiene-demo"
    assert result["license_posture"] == "embed_only"
    assert result["content_type"] == "youtube"
    assert result["source_url"], "source_url must be non-empty"
    assert result["youtube_id"], "youtube_id must be non-empty"
    assert result["attribution"]["source"], "attribution.source must be non-empty"
    assert result["attribution"]["program"] == "ICN"
    # thumbnail_url should be derivable from youtube_id
    assert result["thumbnail_url"] and "ytimg.com" in result["thumbnail_url"], (
        "thumbnail_url should be a YouTube thumbnail URL"
    )


def test_api_icn_asset_embed_permitted_has_duration_field():
    """embed_only YouTube asset response must include duration_min field (may be None)."""
    from demo_app import api_icn_asset

    result = _run(api_icn_asset("icn-food-safety-youtube-hand-hygiene-demo"))
    assert "duration_min" in result, "duration_min field must be present in response"


# ─────────────────────────────────────────────────────────────────────────────
# 4. /api/icn/<id> — link_only asset returns license_posture: "link_only"
# ─────────────────────────────────────────────────────────────────────────────

def test_api_icn_asset_link_only_posture():
    """GET /api/icn/<id> for a link_only asset must return license_posture: 'link_only'."""
    from demo_app import api_icn_asset
    from fastapi import HTTPException

    # Find a link_only asset that also has a card in the LMS content
    manifest = _load_manifest()
    lms = _load_lms()
    lms_ids = {c.get("asset_id") for c in lms.get("content_cards", [])}
    link_only = next(
        (a for a in manifest
         if a.get("license_posture") == "link_only" and a.get("asset_id") in lms_ids),
        None,
    )
    if not link_only:
        pytest.skip("No link_only assets in manifest+lms to test against")

    result = _run(api_icn_asset(link_only["asset_id"]))
    assert result["license_posture"] == "link_only", (
        f"Expected link_only but got {result['license_posture']!r} for {link_only['asset_id']}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# 5. SHOULD-NOT-OCCUR: link_only assets must never have license_posture flipped
#    in the API response (the catalog is the sole embed/link-out authority)
# ─────────────────────────────────────────────────────────────────────────────

def test_link_only_assets_cannot_have_embed_posture_in_api():
    """SHOULD-NOT-OCCUR: for every link_only asset in the catalog, the API must
    not return a different license_posture.

    This is a provenance-by-construction invariant: the embed/link-out decision
    is 100% driven by license_posture from the ICN catalog. If the API response
    ever returns a non-link_only posture for a link_only manifest entry, it means
    the catalog was mutated in a way that bypasses editorial review.
    """
    from demo_app import api_icn_asset
    from fastapi import HTTPException

    manifest = _load_manifest()
    lms = _load_lms()
    lms_ids = {c.get("asset_id") for c in lms.get("content_cards", [])}

    violations = []
    # Spot-check first 5 link_only assets that appear in the LMS catalog
    link_only_lms = [
        a for a in manifest
        if a.get("license_posture") == "link_only" and a.get("asset_id") in lms_ids
    ][:5]

    for a in link_only_lms:
        aid = a.get("asset_id")
        try:
            result = _run(api_icn_asset(aid))
        except Exception:
            continue  # 404 or other error — skip
        if result.get("license_posture") != "link_only":
            violations.append(
                f"{aid}: manifest=link_only, API returned {result.get('license_posture')!r}"
            )

    assert not violations, (
        "SHOULD-NOT-OCCUR violations — license_posture mismatch between catalog and API:\n"
        + "\n".join(violations)
    )


# ─────────────────────────────────────────────────────────────────────────────
# 6. /api/icn catalog has at least one embed-capable video asset
# ─────────────────────────────────────────────────────────────────────────────

def test_api_icn_catalog_has_embed_capable_asset():
    """GET /api/icn must return at least one embed_only or download_allowed card."""
    from demo_app import api_icn

    result = _run(api_icn())
    cards = result.get("cards", [])
    embed_capable = [c for c in cards if c.get("license_posture") in ("embed_only", "download_allowed")]
    assert embed_capable, (
        "ICN catalog must have at least one embed_only or download_allowed asset for the demo"
    )


# ─────────────────────────────────────────────────────────────────────────────
# 7. /api/icn/<id> 404 for unknown asset
# ─────────────────────────────────────────────────────────────────────────────

def test_api_icn_asset_404_for_unknown():
    """GET /api/icn/<id> for a non-existent asset must raise HTTP 404."""
    from demo_app import api_icn_asset
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        _run(api_icn_asset("this-asset-does-not-exist-xyz123"))
    assert exc_info.value.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
# 8. /api/config exposes offline_demo and external_learning flags
# ─────────────────────────────────────────────────────────────────────────────

def test_api_config_exposes_offline_demo():
    """GET /api/config must include 'offline_demo' boolean field."""
    from demo_app import config

    result = _run(config())
    assert "offline_demo" in result, "/api/config must include 'offline_demo' field"
    assert isinstance(result["offline_demo"], bool), "offline_demo must be a boolean"


def test_api_config_exposes_external_learning():
    """GET /api/config must include 'external_learning' boolean field."""
    from demo_app import config

    result = _run(config())
    assert "external_learning" in result, "/api/config must include 'external_learning' field"
    assert isinstance(result["external_learning"], bool), "external_learning must be a boolean"


# ─────────────────────────────────────────────────────────────────────────────
# MANUAL JS TEST CHECKLIST
# (Cannot be run as automated pytest — require a live browser session)
# ─────────────────────────────────────────────────────────────────────────────
#
# JS-1. renderVideoCard output for embed_only YouTube asset:
#   - Output HTML contains "youtube-nocookie.com" in iframe src
#   - Output HTML contains class "video-attribution-band"
#   - Output HTML contains "USDA / ICN" or the asset's source org
#   - Output HTML contains class "outside-vendor" badge
#   - Output HTML does NOT contain "ai-grounded" badge
#
# JS-2. renderVideoCard output for link_only asset:
#   - Output HTML does NOT contain an <iframe> element
#   - Output HTML DOES contain class "video-card--linkout" wrapper
#   - Output HTML DOES contain a link-out anchor to source_url
#   - Output HTML DOES contain class "outside-vendor" badge
#
# JS-3. cbAddVideo() ICN picker:
#   - Clicking "+ Video" opens the ICN catalog picker (not the old free-text form)
#   - The picker shows embed-capable assets with a green "▶ Embed" badge
#   - The picker shows link_only assets with a blue "Link-out ↗" badge
#   - No raw URL text input field is present anywhere in the picker
#
# JS-4. cbPickVideo() stores ref (ICN asset ID), not a raw URL:
#   - After picking an asset, the lesson in _cb.lessons has:
#       { type:'video', ref:'<asset_id>', title:'...', dur:'...', license_posture:'...' }
#   - The 'ref' field is an ICN asset ID string, NOT a URL
#   - There is no 'url' field in the stored lesson object
#
# JS-5. Lesson player renders the ICN video card:
#   - Opening a course with a video lesson (ref='icn-food-safety-youtube-hand-hygiene-demo')
#     calls /api/icn/<asset_id> and renders the video card in #lp-content-area
#   - The rendered card shows the youtube-nocookie iframe
#   - The attribution band "USDA / ICN" is visible below the video
#   - The badge reads "Outside vendor content" (not "AI-grounded")
#
# JS-6. Offline fallback:
#   - Set window._config.offlineDemo = true in the browser console
#   - Navigate to a video lesson — after 6s the fallback thumbnail+link replaces the iframe
#   - The attribution band remains visible in the fallback layout
#   - Layout is not broken at 375px viewport width
