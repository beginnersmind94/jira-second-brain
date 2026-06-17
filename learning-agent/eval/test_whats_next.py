"""eval/test_whats_next.py — Deterministic trust tests for "What's Next for You".

The "What's Next for You" shelf is a post-completion page of EXTERNAL link-outs
(financial wellness · professional development · career credentials). Its whole
trust posture is: link + credit, never reproduce; no product claims; data-driven
from one JSON config. These tests pin that posture so a future edit can't quietly
turn a link-out into reproduced vendor content or smuggle a cost item past the
"ask your district" framing.

Core tests read data/whats-next.json directly — no server, no LLM, fully
deterministic. One optional test hits the live server on :8001 and SKIPS if it is
not running.

Run:
    python -m pytest learning-agent/eval/test_whats_next.py -v
  or from learning-agent/:
    python eval/test_whats_next.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

CONFIG_PATH = Path(__file__).resolve().parent.parent / "data" / "whats-next.json"

# Keys a resource is ALLOWED to carry. Anything else (content/html/body/embed/…)
# would be a vector for reproducing vendor content inline — the trust violation
# this feature exists to avoid.
_ALLOWED_RESOURCE_KEYS = {"name", "url", "description", "free", "ask_district", "spanish", "tags"}
# Keys that, if ever present, mean someone tried to embed vendor content.
_FORBIDDEN_RESOURCE_KEYS = {"content", "html", "body", "text", "markdown", "embed", "iframe", "src"}

_EXPECTED_TIER_IDS = ["financial-wellness", "professional-development", "career-credentials"]
_ALLOWED_ICONS = {"shelter", "grow", "horizon"}
_ALLOWED_VARIANTS = {"green", "stamp", "warn"}
# The two cost-bearing benefits the brief flags with "ask your district".
_ASK_DISTRICT_NAMES = {"SmartDollar by Ramsey Solutions", "SNA Certificate Program"}


@pytest.fixture(scope="module")
def cfg() -> dict:
    assert CONFIG_PATH.exists(), f"config missing: {CONFIG_PATH}"
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def _resources(cfg: dict):
    for tier in cfg.get("tiers", []):
        for r in tier.get("resources", []):
            yield tier, r


# ── WN1: config integrity ─────────────────────────────────────────────────────

def test_wn1_config_loads_and_has_spine(cfg):
    assert cfg.get("version"), "version missing"
    assert cfg.get("product_name"), "product_name missing"
    gate = cfg.get("gate") or {}
    assert gate.get("track_id"), "gate.track_id missing (completion trigger)"
    assert gate.get("track_title"), "gate.track_title missing"


# ── WN2: exactly the three tiers, in the brief's order ────────────────────────

def test_wn2_three_tiers_in_order(cfg):
    ids = [t.get("id") for t in cfg.get("tiers", [])]
    assert ids == _EXPECTED_TIER_IDS, f"tiers must be {_EXPECTED_TIER_IDS}, got {ids}"


# ── WN3: header framing is present and PrimeroEdge-is-the-pipe honest ─────────

def test_wn3_header_framing(cfg):
    h = cfg.get("header") or {}
    for k in ("eyebrow_complete", "eyebrow_preview", "heading", "subhead_complete",
              "subhead_preview", "partner_badge"):
        assert h.get(k), f"header.{k} missing"
    badge = h["partner_badge"].lower()
    assert "external partners" in badge, "partner badge must credit external partners"
    assert "not provided" in badge, "partner badge must disclaim the product is not the provider"


# ── WN4: every resource is an external link-out, never reproduced content ─────

def test_wn4_resources_are_external_linkouts(cfg):
    seen = 0
    for tier, r in _resources(cfg):
        seen += 1
        assert r.get("name"), "resource missing name"
        assert r.get("description"), f"{r.get('name')} missing description"
        url = r.get("url", "")
        assert url.startswith("https://"), f"{r['name']} url must be external https, got {url!r}"
        # No content-reproduction vectors.
        extra = set(r) - _ALLOWED_RESOURCE_KEYS
        assert not extra, f"{r['name']} has unexpected keys (content-reproduction risk): {extra}"
        assert not (set(r) & _FORBIDDEN_RESOURCE_KEYS), f"{r['name']} embeds vendor content"
    assert seen >= 6, f"expected the full shelf, found only {seen} resources"


def test_wn4b_no_link_points_at_our_own_product(cfg):
    for _tier, r in _resources(cfg):
        host = r["url"].split("/")[2].lower()
        assert "localhost" not in host and "127.0.0.1" not in host, f"{r['name']} links internally"
        assert not host.endswith("cybersoft.net"), f"{r['name']} links to our own product, not an external partner"


# ── WN5: only the two cost items carry "ask your district" ────────────────────

def test_wn5_ask_district_only_on_cost_items(cfg):
    flagged = {r["name"] for _t, r in _resources(cfg) if r.get("ask_district")}
    assert flagged == _ASK_DISTRICT_NAMES, (
        f"ask_district must be exactly {_ASK_DISTRICT_NAMES} (the cost-bearing benefits), got {flagged}"
    )
    # Free resources must never carry the ask-district friction.
    for _t, r in _resources(cfg):
        if r.get("free"):
            assert not r.get("ask_district"), f"{r['name']} is free; it must not ask the district"


# ── WN6: pictographic tier icons are valid and distinct ───────────────────────

def test_wn6_icons_and_variants(cfg):
    icons, variants = [], []
    for t in cfg.get("tiers", []):
        assert t.get("icon") in _ALLOWED_ICONS, f"tier {t.get('id')} icon {t.get('icon')!r} not in {_ALLOWED_ICONS}"
        assert t.get("variant") in _ALLOWED_VARIANTS, f"tier {t.get('id')} variant invalid"
        assert t.get("title") and t.get("framing"), f"tier {t.get('id')} missing title/framing"
        icons.append(t["icon"]); variants.append(t["variant"])
    assert len(set(icons)) == 3, "each tier needs a distinct icon"
    assert len(set(variants)) == 3, "each tier needs a distinct color variant"


# ── WN7: the specific resources the brief named are all present ───────────────

def test_wn7_named_resources_present(cfg):
    by_name = {r["name"]: r for _t, r in _resources(cfg)}
    expected = {
        "SmartDollar by Ramsey Solutions": "ramseysolutions.com",
        "USDA Professional Standards Training Tracker": "fns.usda.gov",
        "Institute of Child Nutrition (ICN) Free Training": "theicn.org",
        "SNA Certificate Program": "schoolnutrition.org",
        "Google Career Certificates": "grow.google",
        "IBM & Meta Professional Certificates": "coursera.org",
        "Coursera Financial Aid": "coursera.org",
    }
    for name, domain in expected.items():
        assert name in by_name, f"missing brief resource: {name}"
        assert domain in by_name[name]["url"], f"{name} url should point at {domain}"
    # SmartDollar must advertise Spanish support (the brief calls this out).
    assert by_name["SmartDollar by Ramsey Solutions"].get("spanish") is True


# ── WN8 (optional): live server returns the same config ───────────────────────

def test_wn8_live_endpoint_matches_config(cfg):
    requests = pytest.importorskip("requests")
    try:
        resp = requests.get(
            "http://localhost:8001/api/whats-next",
            headers={"X-Demo-User": "john-cashier"},
            timeout=5,
        )
    except Exception as e:  # noqa: BLE001 — server not running is a skip, not a fail
        pytest.skip(f"server not running on :8001 ({e})")
    assert resp.status_code == 200
    live = resp.json()
    assert [t["id"] for t in live.get("tiers", [])] == _EXPECTED_TIER_IDS
    assert live.get("product_name") == cfg.get("product_name")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
