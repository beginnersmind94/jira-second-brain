"""Tests for GET /api/districts/{isd}/compliance-report (JSON) and /pdf (PDF).

Run from learning-agent/ with the sibling .venv:
    ../../learning-agent/.venv/Scripts/python.exe -m pytest tests/test_compliance_export.py -v

These tests mount a minimal FastAPI app that re-registers only the compliance
routes so they run fast and isolated from the LLM SDK, ICN, and other heavy
imports. The helpers under test (_build_compliance_report, _compliance_status,
_roster_for, _DISTRICTS, _ROLE_TRACK, _COMPLIANCE_NOTE, _COMPLIANCE_DUE) are
imported directly from demo_app, which does not perform any network calls at
import time.
"""
import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Make learning-agent dir importable when pytest is invoked from a different cwd.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import the internal helpers we want to test in isolation.
from demo_app import (  # noqa: E402
    _COMPLIANCE_DUE,
    _COMPLIANCE_NOTE,
    _DISTRICTS,
    _ROLE_TRACK,
    _build_compliance_report,
    _compliance_status,
    compliance_report_json,
    compliance_report_pdf,
)


# ── Minimal app fixture ───────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def client():
    """Thin FastAPI app exposing only the two compliance endpoints."""
    mini = FastAPI()
    mini.add_api_route(
        "/api/districts/{isd}/compliance-report",
        compliance_report_json,
        methods=["GET"],
    )
    mini.add_api_route(
        "/api/districts/{isd}/compliance-report/pdf",
        compliance_report_pdf,
        methods=["GET"],
    )
    return TestClient(mini)


# ── Helper: first known district ID ──────────────────────────────────────────

_KNOWN_ISD = _DISTRICTS[0]["id"]   # e.g. "houston-isd"
_KNOWN_NAME = _DISTRICTS[0]["name"]


# ── 1. JSON response shape ────────────────────────────────────────────────────

def test_json_response_shape(client):
    """Response includes all required top-level keys with correct types."""
    r = client.get(f"/api/districts/{_KNOWN_ISD}/compliance-report")
    assert r.status_code == 200, r.text
    body = r.json()

    assert body["district"] == _KNOWN_NAME
    assert body["due_date"] == _COMPLIANCE_DUE
    assert isinstance(body["report_date"], str) and len(body["report_date"]) == 10  # YYYY-MM-DD

    s = body["summary"]
    assert set(s.keys()) == {"total", "complete", "in_progress", "not_started", "overdue"}
    assert s["total"] > 0
    assert s["complete"] + s["in_progress"] + s["not_started"] <= s["total"]
    assert s["overdue"] <= s["in_progress"]   # overdue is a subset of in-progress

    assert isinstance(body["staff"], list) and len(body["staff"]) == s["total"]
    first = body["staff"][0]
    assert set({"name", "role", "track", "completion_pct", "status", "last_active"}).issubset(first.keys())


# ── 2. DEMO DATA note is always present ──────────────────────────────────────

def test_demo_data_note_present(client):
    """Every JSON response carries the seeded-data caveat in the 'note' field."""
    for d in _DISTRICTS:
        r = client.get(f"/api/districts/{d['id']}/compliance-report")
        assert r.status_code == 200
        body = r.json()
        assert body.get("note") == _COMPLIANCE_NOTE, (
            f"District {d['id']} missing or wrong note: {body.get('note')!r}"
        )


# ── 3. Unknown district returns 404 ──────────────────────────────────────────

def test_unknown_district_404(client):
    """A district ID that doesn't exist in the seeded data returns HTTP 404."""
    r = client.get("/api/districts/nonexistent-isd-xyz/compliance-report")
    assert r.status_code == 404
    assert "not found" in r.json()["detail"].lower()


def test_unknown_district_pdf_404(client):
    """The PDF endpoint also returns 404 for an unknown district."""
    r = client.get("/api/districts/nonexistent-isd-xyz/compliance-report/pdf")
    assert r.status_code == 404


# ── 4. Summary arithmetic is internally consistent ───────────────────────────

def test_summary_counts_consistent(client):
    """For every district, summary totals must be internally consistent."""
    for d in _DISTRICTS:
        r = client.get(f"/api/districts/{d['id']}/compliance-report")
        assert r.status_code == 200
        body = r.json()
        s = body["summary"]
        # complete + in_progress + not_started should equal total
        accounted = s["complete"] + s["in_progress"] + s["not_started"]
        assert accounted == s["total"], (
            f"District {d['id']}: complete({s['complete']}) + "
            f"in_progress({s['in_progress']}) + not_started({s['not_started']}) "
            f"= {accounted} != total({s['total']})"
        )
        # overdue is a strict subset of in_progress
        assert s["overdue"] <= s["in_progress"]


# ── 5. PDF response is a valid PDF binary ────────────────────────────────────

def test_pdf_response_is_pdf(client):
    """The /pdf endpoint returns application/pdf with valid PDF magic bytes."""
    r = client.get(f"/api/districts/{_KNOWN_ISD}/compliance-report/pdf")
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith("application/pdf")
    assert r.content[:4] == b"%PDF", "Response does not start with PDF magic bytes"
    cd = r.headers.get("content-disposition", "")
    assert "attachment" in cd and ".pdf" in cd


# ── 6. _compliance_status normalises known + unknown values ──────────────────

def test_compliance_status_mapping():
    """_compliance_status maps seeded strings to report labels; unknown pass through."""
    assert _compliance_status("Completed")   == "Complete"
    assert _compliance_status("In progress") == "In Progress"
    assert _compliance_status("Not started") == "Not Started"
    assert _compliance_status("Overdue")     == "Overdue"   # pass-through
    assert _compliance_status("")            == ""           # pass-through


# ── 7. _build_compliance_report returns {} for missing district ───────────────

def test_build_report_empty_dict_for_unknown():
    """_build_compliance_report returns an empty dict (not an exception) when the ISD is unknown."""
    result = _build_compliance_report("this-does-not-exist")
    assert result == {}


# ── 8. Role → track mapping is applied ───────────────────────────────────────

def test_role_track_mapping_applied(client):
    """Staff rows should carry the role-mapped track name where applicable."""
    r = client.get(f"/api/districts/{_KNOWN_ISD}/compliance-report")
    body = r.json()
    for row in body["staff"]:
        if row["role"] in _ROLE_TRACK:
            assert row["track"] == _ROLE_TRACK[row["role"]], (
                f"Expected {_ROLE_TRACK[row['role']]!r} for role {row['role']!r}, "
                f"got {row['track']!r}"
            )


# ── 9. All seeded districts are serviced ─────────────────────────────────────

def test_all_districts_return_200(client):
    """Every entry in _DISTRICTS resolves to a 200 from the JSON endpoint."""
    for d in _DISTRICTS:
        r = client.get(f"/api/districts/{d['id']}/compliance-report")
        assert r.status_code == 200, f"District {d['id']} returned {r.status_code}"
        assert r.json()["district"] == d["name"]
