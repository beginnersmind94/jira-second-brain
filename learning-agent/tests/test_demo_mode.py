"""Tests for G4 — Conference demo mode flag + pristine reset.

Run from learning-agent/ with:
    python -m pytest eval/test_demo_mode.py -v

Test inventory (per the G4 spec):
  1. CONFERENCE_MODE=False  → POST /api/demo/reset returns 403  (SHOULD-NOT-OCCUR)
  2. CONFERENCE_MODE=True   → POST /api/demo/reset clears demo user completion files;
                               subsequent /api/tracks/<id> for john-cashier shows 0% progress
  3. completion_store.reset_demo_users — progress file gone; idempotent (no error on missing)
  4. GET /api/config returns conferenceMode: true when DEMO_MODE=conference is set
  5. PDF export in conference mode does NOT contain "DEMO DATA" watermark text;
     in default mode DOES contain it

All tests are deterministic and offline — no SDK, no Jira, no LLM calls.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Make learning-agent/ importable regardless of cwd.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# ---------------------------------------------------------------------------
# Test 3 — completion_store.reset_demo_users (pure unit, no server)
# ---------------------------------------------------------------------------

class TestResetDemoUsers:
    """Unit tests for completion_store.reset_demo_users().

    These run fully offline against a temp directory, exercising the real logic
    without touching the live data/completion/ tree.
    """

    def _make_store(self, tmp: Path, user_id: str, track_id: str = "track-001"):
        """Write a fake progress file for user_id under tmp."""
        import re
        safe_user = re.sub(r"[^\w\-]", "_", user_id)[:80]
        safe_track = re.sub(r"[^\w\-]", "_", track_id)[:80]
        ud = tmp / safe_user
        ud.mkdir(parents=True, exist_ok=True)
        pf = ud / f"{safe_track}.json"
        pf.write_text(json.dumps({"modules_done": ["m1"], "pct": 50}), encoding="utf-8")
        return pf

    def test_resets_listed_users(self, tmp_path):
        """Calling reset_demo_users deletes all files for the listed user ids."""
        import completion_store as cs

        # Patch _COMPLETION_DIR to point at our temp directory.
        with patch.object(cs, "_COMPLETION_DIR", tmp_path):
            pf = self._make_store(tmp_path, "demo-user-001")
            assert pf.exists(), "precondition: file must exist"

            cleaned = cs.reset_demo_users(["demo-user-001"])

        assert "demo-user-001" in cleaned
        assert not pf.exists(), "progress file should be deleted"
        assert not pf.parent.exists(), "user directory should be removed"

    def test_idempotent_on_missing_user(self, tmp_path):
        """Calling reset_demo_users for a user that has no files is a no-op (no error)."""
        import completion_store as cs

        with patch.object(cs, "_COMPLETION_DIR", tmp_path):
            # User has no files.
            cleaned = cs.reset_demo_users(["demo-user-999"])

        # Should return empty list (nothing to clean) without raising.
        assert cleaned == []

    def test_does_not_touch_other_users(self, tmp_path):
        """Only the listed user ids are deleted; other users' files are untouched."""
        import completion_store as cs

        with patch.object(cs, "_COMPLETION_DIR", tmp_path):
            pf_target = self._make_store(tmp_path, "demo-user-001")
            pf_bystander = self._make_store(tmp_path, "demo-user-002")

            cs.reset_demo_users(["demo-user-001"])

        assert not pf_target.parent.exists(), "target user deleted"
        assert pf_bystander.exists(), "bystander user untouched"

    def test_cleans_certs_subdir(self, tmp_path):
        """reset_demo_users removes the entire user tree including certs/."""
        import completion_store as cs

        with patch.object(cs, "_COMPLETION_DIR", tmp_path):
            pf = self._make_store(tmp_path, "demo-user-001")
            certs_dir = pf.parent / "certs"
            certs_dir.mkdir(parents=True, exist_ok=True)
            cert = certs_dir / "cert-abc123.json"
            cert.write_text("{}", encoding="utf-8")

            cleaned = cs.reset_demo_users(["demo-user-001"])

        assert "demo-user-001" in cleaned
        assert not pf.parent.exists(), "entire user directory (including certs) deleted"


# ---------------------------------------------------------------------------
# Server-side tests — mount a minimal FastAPI app
# ---------------------------------------------------------------------------

def _make_mini_app(conference_mode: bool):
    """Return a (TestClient, app) tuple with CONFERENCE_MODE patched."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    import demo_app

    # Patch the module-level flag before importing route handlers.
    with patch.object(demo_app, "CONFERENCE_MODE", conference_mode):
        mini = FastAPI()
        mini.add_api_route("/api/demo/reset", demo_app.demo_reset, methods=["POST"])
        mini.add_api_route("/api/config", demo_app.config, methods=["GET"])
        client = TestClient(mini, raise_server_exceptions=True)
    return client


# Test 1 — reset returns 403 when not in conference mode (SHOULD-NOT-OCCUR gate)
class TestResetGate:
    def test_reset_returns_403_when_not_conference_mode(self):
        """POST /api/demo/reset must return 403 outside of conference mode.

        This is a SHOULD-NOT-OCCUR test (the cardinal security gate for this feature):
        the reset endpoint must be unreachable in normal/production operation.
        """
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        import demo_app

        with patch.object(demo_app, "CONFERENCE_MODE", False):
            mini = FastAPI()
            mini.add_api_route("/api/demo/reset", demo_app.demo_reset, methods=["POST"])
            client = TestClient(mini, raise_server_exceptions=False)
            resp = client.post("/api/demo/reset")

        assert resp.status_code == 403, (
            f"Expected 403 when CONFERENCE_MODE=False, got {resp.status_code}. "
            "The reset endpoint must be gated — this is a SHOULD-NOT-OCCUR security gate."
        )
        body = resp.json()
        assert body.get("detail", {}).get("error") == "conference_mode_only"

    def test_reset_returns_200_when_conference_mode(self, tmp_path):
        """POST /api/demo/reset returns 200 ok when CONFERENCE_MODE=True."""
        import completion_store as cs
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        import demo_app

        with (
            patch.object(demo_app, "CONFERENCE_MODE", True),
            patch.object(cs, "_COMPLETION_DIR", tmp_path),
            patch.object(demo_app, "_cs", cs),
        ):
            mini = FastAPI()
            mini.add_api_route("/api/demo/reset", demo_app.demo_reset, methods=["POST"])
            client = TestClient(mini, raise_server_exceptions=True)
            resp = client.post("/api/demo/reset")

        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert "reset_at" in data
        assert "elapsed_ms" in data
        assert isinstance(data["users_reset"], list)


# Test 2 — reset clears demo user completion; track shows 0% progress after
class TestResetClearsProgress:
    def test_progress_is_zero_after_reset(self, tmp_path):
        """After reset_demo_users, get_progress returns 0% (no seed without module_ids)."""
        import completion_store as cs

        with patch.object(cs, "_COMPLETION_DIR", tmp_path):
            # Write a progress record for john-cashier's demo user id.
            cs._write_json(
                cs._progress_path("demo-user-001", "track-test"),
                {"modules_done": ["m1", "m2"], "pct": 100, "certified": True, "cert_issued_at": "2026-01-01"}
            )
            assert cs.get_progress("demo-user-001", "track-test")["pct"] == 100

            # Reset.
            cs.reset_demo_users(["demo-user-001"])

            # After reset, no stored record → zeroed out (not seeded because no module_ids).
            prog = cs.get_progress("demo-user-001", "track-test")

        assert prog["pct"] == 0
        assert prog["modules_done"] == []
        assert prog["certified"] is False


# Test 4 — /api/config exposes conferenceMode correctly
class TestApiConfig:
    def test_config_conference_mode_true(self):
        """GET /api/config returns conferenceMode: true when DEMO_MODE=conference."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        import demo_app

        # Keep the patch active for the duration of the actual HTTP call.
        with patch.object(demo_app, "CONFERENCE_MODE", True):
            mini = FastAPI()
            mini.add_api_route("/api/config", demo_app.config, methods=["GET"])
            client = TestClient(mini, raise_server_exceptions=True)
            resp = client.get("/api/config")

        assert resp.status_code == 200
        data = resp.json()
        assert data["conferenceMode"] is True
        assert data["demoMode"] == "conference"

    def test_config_conference_mode_false(self):
        """GET /api/config returns conferenceMode: false in default mode."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        import demo_app

        with patch.object(demo_app, "CONFERENCE_MODE", False):
            mini = FastAPI()
            mini.add_api_route("/api/config", demo_app.config, methods=["GET"])
            client = TestClient(mini, raise_server_exceptions=True)
            resp = client.get("/api/config")

        assert resp.status_code == 200
        data = resp.json()
        assert data["conferenceMode"] is False
        assert data["demoMode"] == "default"


# Test 5 — PDF watermark behaviour
class TestPdfWatermark:
    """Verify that the compliance PDF watermark is gated by CONFERENCE_MODE.

    We test the gating logic in demo_app without calling render_html_to_pdf
    (that requires pymupdf and is tested in test_compliance_export.py). Instead
    we verify that the banner value passed to render_html_to_pdf is None in
    conference mode and non-None in default mode, by patching the renderer.

    The compliance_report_pdf route does `from pdf_export import render_html_to_pdf`
    inside the function body, so we patch the `pdf_export` module in sys.modules
    and set CONFERENCE_MODE on demo_app before the request is made.
    """

    def _run_pdf_route(self, conference_mode: bool) -> "str | None":
        """Return the banner string passed to render_html_to_pdf, or None."""
        import types
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        import demo_app

        captured: dict = {}

        def fake_render(html, banner=None):
            captured["banner"] = banner
            return b"%PDF-1.4 fake"

        fake_pdf_mod = types.ModuleType("pdf_export")
        fake_pdf_mod.render_html_to_pdf = fake_render  # type: ignore[attr-defined]

        with (
            patch.object(demo_app, "CONFERENCE_MODE", conference_mode),
            patch.dict("sys.modules", {"pdf_export": fake_pdf_mod}),
        ):
            mini = FastAPI()
            mini.add_api_route(
                "/api/districts/{isd}/compliance-report/pdf",
                demo_app.compliance_report_pdf,
                methods=["GET"],
            )
            client = TestClient(mini, raise_server_exceptions=True)
            client.get("/api/districts/houston-isd/compliance-report/pdf")

        return captured.get("banner")

    def test_no_watermark_in_conference_mode(self):
        """In conference mode, the PDF banner (watermark) is None — no stamp."""
        banner = self._run_pdf_route(conference_mode=True)
        assert banner is None, (
            f"Expected no watermark in conference mode, but got banner={banner!r}"
        )

    def test_watermark_present_in_default_mode(self):
        """In default mode, the PDF banner contains 'DEMO DATA'."""
        banner = self._run_pdf_route(conference_mode=False)
        assert banner is not None, "Expected a watermark in default mode, got None"
        assert "DEMO DATA" in banner, (
            f"Expected 'DEMO DATA' in the watermark banner, got: {banner!r}"
        )
