"""Tests for D6 — Mobile + performance pass.

Run from learning-agent/ with:
    python -m pytest eval/test_mobile_perf.py -v

Test inventory (5 cases):

  TC-D6-01: GET /resources/{rid}/html returns HTML that does NOT contain "<!-- Source:" comments
             (SHOULD-NOT-OCCUR pin — citation stripping must hold; reuses D1 server path)
  TC-D6-02: static/index.html contains the string "_playerLoadMs"
             (structural pin — D6 performance SLA measurement wired in)
  TC-D6-03: static/index.html contains a ".trainer-lazy" CSS class definition
             (structural pin — trainer lazy-hide is present)
  TC-D6-04: static/index.html contains the string "cp_swipe_hint_shown"
             (structural pin — swipe hint session-guard is present)
  TC-D6-05: static/index.html contains a "focus-visible" CSS rule
             (structural pin — WCAG 2.1 AA focus ring was not accidentally dropped)

All tests are deterministic and offline — no SDK, no LLM calls.
Tests TC-D6-02 through TC-D6-05 are pure file-read assertions against the SPA source.
TC-D6-01 optionally exercises the live server when it can be imported.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Make learning-agent/ importable regardless of cwd.
_LA_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_LA_ROOT))

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _index_html_text() -> str:
    """Return the full text of static/index.html (the SPA source)."""
    p = _LA_ROOT / "static" / "index.html"
    if not p.exists():
        pytest.skip("static/index.html not found — run from learning-agent/")
    return p.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# TC-D6-01  HTML endpoint strips <!-- Source: --> comments
# ---------------------------------------------------------------------------

def test_d6_01_html_endpoint_strips_source_comments():
    """GET /resources/{rid}/html must not expose raw citation comments.

    This is a SHOULD-NOT-OCCUR pin: if the endpoint leaks <!-- Source: NXT-...
    comments, learner-facing HTML contains internal audit trail data.  The D1
    server strips them before serving; this test confirms the strip is still in
    place for any approved resource that can be found in the demo library.
    """
    try:
        import demo_app  # noqa: F401 — imported for side-effects (routes registered)
        from demo_app import app
        from fastapi.testclient import TestClient
    except Exception as exc:
        pytest.skip(f"demo_app not importable in this env: {exc}")

    client = TestClient(app, raise_server_exceptions=False)

    # Discover any approved resource id via the /api/modules endpoint.
    resp = client.get("/api/modules", headers={"X-Demo-User": "sam-trainer"})
    if resp.status_code != 200:
        pytest.skip(f"/api/modules returned {resp.status_code} — server not ready")

    modules = resp.json().get("modules", [])
    rid = next(
        (m["id"] for m in modules if not str(m.get("id", "")).startswith("icn-")),
        None,
    )
    if rid is None:
        pytest.skip("No non-ICN approved resource found in demo library")

    html_resp = client.get(
        f"/resources/{rid}/html",
        headers={"X-Demo-User": "john-cashier"},
    )
    if html_resp.status_code == 404:
        pytest.skip(f"Resource {rid!r} has no HTML render (404)")
    assert html_resp.status_code == 200, (
        f"Expected 200 from /resources/{rid}/html, got {html_resp.status_code}"
    )
    body = html_resp.text
    assert "<!-- Source:" not in body, (
        "SHOULD-NOT-OCCUR: /resources/{rid}/html contains raw <!-- Source: --> "
        "citation comments — strip step is broken"
    )


# ---------------------------------------------------------------------------
# TC-D6-02  _playerLoadMs is wired into the SPA
# ---------------------------------------------------------------------------

def test_d6_02_player_load_ms_present():
    """static/index.html must contain the _playerLoadMs assignment.

    This is the D6 performance SLA measurement: after player-load is measured,
    window._playerLoadMs is set and a console.warn fires if >3000ms.
    If this string is absent the SLA instrumentation was dropped.
    """
    src = _index_html_text()
    assert "_playerLoadMs" in src, (
        "static/index.html does not contain '_playerLoadMs' — "
        "D6 player-load SLA measurement is missing"
    )


# ---------------------------------------------------------------------------
# TC-D6-03  .trainer-lazy CSS is defined
# ---------------------------------------------------------------------------

def test_d6_03_trainer_lazy_css_present():
    """static/index.html must define the .trainer-lazy CSS class.

    This class is toggled onto trainer-only sections when the learner path is
    active, hiding them immediately and preventing unnecessary DOM cost on the
    cashier / director path.
    """
    src = _index_html_text()
    assert ".trainer-lazy" in src, (
        "static/index.html does not define '.trainer-lazy' CSS — "
        "D6 trainer lazy-hide is missing"
    )


# ---------------------------------------------------------------------------
# TC-D6-04  Swipe-hint session guard is present
# ---------------------------------------------------------------------------

def test_d6_04_swipe_hint_guard_present():
    """static/index.html must reference the cp_swipe_hint_shown localStorage key.

    The swipe hint is shown once per session (auto-dismissed after 3s) and then
    suppressed via localStorage.  If this key is absent the guard is broken and
    the hint will flash on every player open.
    """
    src = _index_html_text()
    assert "cp_swipe_hint_shown" in src, (
        "static/index.html does not contain 'cp_swipe_hint_shown' — "
        "D6 swipe-hint one-time session guard is missing"
    )


# ---------------------------------------------------------------------------
# TC-D6-05  focus-visible CSS rule is present (WCAG 2.1 AA)
# ---------------------------------------------------------------------------

def test_d6_05_focus_visible_rule_present():
    """static/index.html must contain a focus-visible CSS rule.

    WCAG 2.1 SC 2.4.7 requires a visible keyboard focus indicator.  The D6
    pass adds / verifies a :focus-visible rule covering buttons, inputs, links,
    and [tabindex] elements.  If this string is absent the AA focus ring was
    accidentally removed.
    """
    src = _index_html_text()
    assert "focus-visible" in src, (
        "static/index.html does not contain any 'focus-visible' CSS rule — "
        "WCAG 2.1 AA keyboard focus indicator is missing"
    )
