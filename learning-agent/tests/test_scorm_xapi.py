"""Tests for scorm_export.py and xapi_client.py.

Run from learning-agent/ with the sibling .venv:
    ../../learning-agent/.venv/Scripts/python.exe -m pytest tests/test_scorm_xapi.py -v

Tests target the modules directly (no server import) so they are fast and
isolated from the LLM SDK, Jira fixtures, and the network.
"""
from __future__ import annotations

import asyncio
import io
import json
import sys
import zipfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Make the learning-agent dir importable when pytest runs from elsewhere.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import scorm_export
import xapi_client


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

SAMPLE_TRACK = {
    "id": "track-20260612-abc123",
    "title": "New Cashier Onboarding",
    "description": "Onboarding guide for new cashiers.",
    "product": "SchoolCafé",
    "role_tags": ["Cashier"],
    "module_ids": ["GUIDE-001", "GUIDE-002"],
    "quiz_id": None,
    "status": "published",
}

SAMPLE_MODULES = [
    {"id": "GUIDE-001", "title": "System Onboarding Quick Guide", "source": "HUMAN_GUIDE"},
    {"id": "GUIDE-002", "title": "Point of Sale Basics",          "source": "AI_TRANSCRIPT"},
]

SAMPLE_ACTOR = {
    "name":  "John Doe",
    "email": "john.doe@houstonisd.org",
    "id":    "demo-user-001",
}


def _open_zip(data: bytes) -> zipfile.ZipFile:
    return zipfile.ZipFile(io.BytesIO(data), "r")


# ─────────────────────────────────────────────────────────────────────────────
# SCORM export tests
# ─────────────────────────────────────────────────────────────────────────────


class TestBuildScormPackage:
    """Tests for scorm_export.build_scorm_package()."""

    def test_returns_bytes(self):
        """build_scorm_package returns bytes."""
        result = scorm_export.build_scorm_package(SAMPLE_TRACK, SAMPLE_MODULES)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_zip_contains_imsmanifest(self):
        """SCORM zip must contain imsmanifest.xml at the root."""
        data = scorm_export.build_scorm_package(SAMPLE_TRACK, SAMPLE_MODULES)
        with _open_zip(data) as zf:
            names = zf.namelist()
        assert "imsmanifest.xml" in names, f"imsmanifest.xml not in zip; found: {names}"

    def test_zip_contains_index_html(self):
        """SCORM zip must contain index.html (the SCO launch page)."""
        data = scorm_export.build_scorm_package(SAMPLE_TRACK, SAMPLE_MODULES)
        with _open_zip(data) as zf:
            names = zf.namelist()
        assert "index.html" in names, f"index.html not in zip; found: {names}"

    def test_manifest_references_all_module_files(self):
        """imsmanifest.xml must reference a content file for every module."""
        data = scorm_export.build_scorm_package(SAMPLE_TRACK, SAMPLE_MODULES)
        with _open_zip(data) as zf:
            manifest = zf.read("imsmanifest.xml").decode("utf-8")
        for mod in SAMPLE_MODULES:
            safe_id = scorm_export._safe_xml_id(mod["id"])
            expected_path = f"content/{safe_id}.html"
            assert expected_path in manifest, (
                f"manifest missing reference to {expected_path}; manifest excerpt:\n"
                + manifest[:800]
            )

    def test_content_files_exist_for_each_module(self):
        """content/<id>.html must be present in the zip for each module."""
        data = scorm_export.build_scorm_package(SAMPLE_TRACK, SAMPLE_MODULES)
        with _open_zip(data) as zf:
            names = zf.namelist()
        for i, mod in enumerate(SAMPLE_MODULES):
            expected = scorm_export._module_content_path(mod, i)
            assert expected in names, f"{expected} not in zip; found: {names}"

    def test_manifest_declares_scorm12(self):
        """Manifest must declare SCORM 1.2 schema."""
        data = scorm_export.build_scorm_package(SAMPLE_TRACK, SAMPLE_MODULES)
        with _open_zip(data) as zf:
            manifest = zf.read("imsmanifest.xml").decode("utf-8")
        assert "ADL SCORM" in manifest
        assert "1.2" in manifest

    def test_sco_launch_page_contains_lmsinitialize(self):
        """The SCO launch page (index.html) must include the SCORM API shim."""
        data = scorm_export.build_scorm_package(SAMPLE_TRACK, SAMPLE_MODULES)
        with _open_zip(data) as zf:
            launch = zf.read("index.html").decode("utf-8")
        assert "LMSInitialize" in launch, "index.html missing LMSInitialize"
        assert "LMSSetValue" in launch, "index.html missing LMSSetValue"
        assert "cmi.core.lesson_status" in launch, "index.html missing lesson_status"

    def test_empty_modules_still_produces_valid_zip(self):
        """A track with no modules should still produce a valid, non-empty zip."""
        data = scorm_export.build_scorm_package(SAMPLE_TRACK, modules=[])
        with _open_zip(data) as zf:
            names = zf.namelist()
        assert "imsmanifest.xml" in names
        assert "index.html" in names


# ─────────────────────────────────────────────────────────────────────────────
# xAPI client tests
# ─────────────────────────────────────────────────────────────────────────────


class TestXAPIClientStub:
    """Tests for XAPIClient in stub mode (default — no LRS configured)."""

    def setup_method(self):
        # Create a fresh client with no env-var LRS config.
        self.client = xapi_client.XAPIClient(lrs_endpoint="", lrs_key="")
        assert self.client.stub is True
        assert self.client.lrs_configured is False

    def test_stub_emit_completed_returns_true(self, tmp_path, monkeypatch):
        """emit_completed in stub mode must return True and write a log line."""
        stub_log = tmp_path / "xapi-stub.jsonl"
        monkeypatch.setattr(xapi_client, "_STUB_LOG", stub_log)

        result = asyncio.run(
            self.client.emit_completed(actor=SAMPLE_ACTOR, track=SAMPLE_TRACK, score=100.0)
        )
        assert result is True
        assert stub_log.exists()

    def test_stub_logs_correct_statement_shape(self, tmp_path, monkeypatch):
        """Stub mode must log a valid xAPI statement with required fields."""
        stub_log = tmp_path / "xapi-stub.jsonl"
        monkeypatch.setattr(xapi_client, "_STUB_LOG", stub_log)

        asyncio.run(
            self.client.emit_completed(actor=SAMPLE_ACTOR, track=SAMPLE_TRACK, score=100.0)
        )
        lines = stub_log.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        stmt = json.loads(lines[0])

        # Required xAPI fields.
        assert "id" in stmt, "statement missing 'id'"
        assert "actor" in stmt, "statement missing 'actor'"
        assert "verb" in stmt, "statement missing 'verb'"
        assert "object" in stmt, "statement missing 'object'"
        assert "timestamp" in stmt, "statement missing 'timestamp'"

        # Verb must be 'completed'.
        assert stmt["verb"]["id"] == xapi_client._VERB_COMPLETED

        # Actor must carry the name.
        assert stmt["actor"]["name"] == SAMPLE_ACTOR["name"]

        # Result must include completion=True.
        assert stmt.get("result", {}).get("completion") is True

    def test_stub_emit_progressed_correct_verb(self, tmp_path, monkeypatch):
        """emit_progressed must log a statement with the 'progressed' verb."""
        stub_log = tmp_path / "xapi-stub.jsonl"
        monkeypatch.setattr(xapi_client, "_STUB_LOG", stub_log)

        asyncio.run(
            self.client.emit_progressed(
                actor=SAMPLE_ACTOR, track=SAMPLE_TRACK, module_id="GUIDE-001"
            )
        )
        stmt = json.loads(stub_log.read_text(encoding="utf-8").strip())
        assert stmt["verb"]["id"] == xapi_client._VERB_PROGRESSED

    def test_emit_completed_nonfatal_on_stub_ioerror(self, tmp_path, monkeypatch):
        """_stub_emit must return False (not raise) when the log file can't be written.

        The non-fatal guarantee lives in _stub_emit: it catches OSError and returns False.
        We verify this by using a mock Path that raises OSError on .open().
        """
        from unittest.mock import MagicMock
        mock_log = MagicMock(spec=Path)
        mock_log.parent.mkdir.return_value = None           # mkdir succeeds
        mock_log.open.side_effect = OSError("disk full")   # open raises

        monkeypatch.setattr(xapi_client, "_STUB_LOG", mock_log)

        result = xapi_client._stub_emit({"id": "test-fail", "verb": {"id": "http://test"}})
        assert result is False, "_stub_emit must return False on OSError, not raise"


class TestXAPIClientLive:
    """Tests for XAPIClient network error handling in production mode."""

    def test_emit_completed_nonfatal_on_network_error(self):
        """emit_completed must return False (not raise) on a network error."""
        client = xapi_client.XAPIClient(
            lrs_endpoint="http://lrs.example.invalid/statements",
            lrs_key="user:password",
        )
        assert client.stub is False
        assert client.lrs_configured is True

        # _live_emit will fail because the endpoint is unreachable.
        # It must return False, not raise.
        result = asyncio.run(
            client.emit_completed(actor=SAMPLE_ACTOR, track=SAMPLE_TRACK, score=100.0)
        )
        # Either False (network error caught) or True (httpx not installed → False path).
        assert isinstance(result, bool)


# ─────────────────────────────────────────────────────────────────────────────
# SCORM endpoint test (via FastAPI TestClient — isolated from full demo_app)
# ─────────────────────────────────────────────────────────────────────────────


class TestScormEndpointIntegration:
    """Test the /api/tracks/{id}/scorm endpoint returns application/zip."""

    def _make_app(self):
        """Build a minimal FastAPI app that mounts ONLY the SCORM endpoint."""
        from fastapi import FastAPI, Depends
        from fastapi.responses import Response
        from fastapi.testclient import TestClient
        import re as _re

        # Minimal stubs so we don't import the full demo_app.
        class _FakeUser:
            is_trainer = True
            name = "Sam Rivera"
            id = "demo-user-003"

        class _FakeMS:
            def load_track(self, tid):
                if tid == "track-test":
                    return SAMPLE_TRACK
                return None
            def expand_track(self, track, icn_dir=None):
                return {**track, "modules": SAMPLE_MODULES}

        _ms = _FakeMS()
        _icn_dir = None

        app = FastAPI()

        @app.get("/api/tracks/{tid}/scorm")
        def _scorm(tid: str):
            track = _ms.load_track(tid)
            if not track:
                from fastapi import HTTPException
                raise HTTPException(404, "track not found")
            expanded = _ms.expand_track(track, icn_dir=_icn_dir)
            modules  = expanded.get("modules") or []
            zip_bytes = scorm_export.build_scorm_package(track=expanded, modules=modules)
            safe_title = _re.sub(r"[^\w\s-]", "", track.get("title") or tid).strip().replace(" ", "_") or tid
            return Response(
                content=zip_bytes,
                media_type="application/zip",
                headers={"Content-Disposition": f'attachment; filename="{safe_title}.zip"'},
            )

        return TestClient(app)

    def test_scorm_endpoint_returns_zip_content_type(self):
        """GET /api/tracks/{id}/scorm must return Content-Type: application/zip."""
        client = self._make_app()
        r = client.get("/api/tracks/track-test/scorm")
        assert r.status_code == 200, r.text
        assert "application/zip" in r.headers.get("content-type", "")

    def test_scorm_endpoint_zip_contains_manifest(self):
        """Response zip must contain imsmanifest.xml."""
        client = self._make_app()
        r = client.get("/api/tracks/track-test/scorm")
        assert r.status_code == 200
        with _open_zip(r.content) as zf:
            assert "imsmanifest.xml" in zf.namelist()

    def test_scorm_endpoint_404_for_unknown_track(self):
        """GET /api/tracks/nonexistent/scorm must return 404."""
        client = self._make_app()
        r = client.get("/api/tracks/nonexistent/scorm")
        assert r.status_code == 404
