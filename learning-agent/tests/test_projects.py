"""Acceptance tests for the Projects flow (projects.py).

Run from learning-agent/ with the sibling .venv:
    ../../learning-agent/.venv/Scripts/python.exe -m pytest tests/test_projects.py -v

These tests target the router directly (mounted on a fresh FastAPI() app) to
keep them fast and isolated from the rest of demo_app.py's import surface
(LLM SDK, Jira fixtures, etc.). The actual demo_app.py wires the SAME router
the SAME way (include_router), so this is a faithful integration test.
"""
import io
import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Make the learning-agent dir importable when pytest is invoked from elsewhere.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import projects  # noqa: E402


@pytest.fixture
def client():
    """Fresh FastAPI app + projects router + clean in-memory store per test."""
    app = FastAPI()
    app.include_router(projects.router)
    projects._reset_for_tests()
    return TestClient(app)


# Helpers ───────────────────────────────────────────────────────────────────
def _make_project(client, name="Demo ISD", product="SchoolCafé", go_live="2026-08-15"):
    r = client.post("/api/projects",
                    json={"name": name, "product": product, "go_live_date": go_live})
    assert r.status_code == 200, r.text
    return r.json()["project"]


def _csv_bytes(text: str) -> bytes:
    return text.encode("utf-8")


SITES_CSV_GOOD = """site_name,address
Lincoln Elementary,1200 Lincoln Ave
Hamilton High School,3300 Hamilton Pkwy
Carver Early Learning Center,410 Carver Ln
"""

USERS_CSV_GOOD = """employee_id,full_name,email,role,site_name
E1001,Maria Garcia,maria.garcia@demoisd.org,CN Director,Hamilton High School
E1002,Carlos Davis,carlos.davis@demoisd.org,Site Manager,Lincoln Elementary
E1003,Linda Wilson,linda.wilson@demoisd.org,Cashier,Hamilton High School
E1004,Wei Khan,wei.khan@demoisd.org,Cashier,Carver Early Learning Center
"""


# 1. ──────────────────────────────────────────────────────────────────────
def test_project_create(client):
    """Create project: name + product + go_live_date → 200 + project payload."""
    # happy path
    r = client.post("/api/projects",
                    json={"name": "Demo ISD", "product": "SchoolCafé",
                          "go_live_date": "2026-08-15"})
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    proj = body["project"]
    assert proj["name"] == "Demo ISD"
    assert proj["product"] == "SchoolCafé"
    assert proj["go_live_date"] == "2026-08-15"
    assert proj["site_count"] == 0 and proj["user_count"] == 0
    assert proj["id"].startswith("p-")
    assert proj["created_at"]
    assert proj["sites_imported_at"] is None
    assert proj["users_imported_at"] is None

    # validation: missing fields → 400 with field-level errors
    r2 = client.post("/api/projects",
                     json={"name": "", "product": "", "go_live_date": "not-a-date"})
    assert r2.status_code == 400
    errs = r2.json()["detail"]["errors"]
    assert "name" in errs and "product" in errs and "go_live_date" in errs


# 2. ──────────────────────────────────────────────────────────────────────
def test_sites_import_happy_path(client):
    """Sites import: required cols pass → preview shows rows + 0 errors → commit creates Site rows."""
    proj = _make_project(client)
    pid = proj["id"]

    # Preview
    r = client.post(
        f"/api/projects/{pid}/sites/import?mode=preview",
        files={"file": ("sites.csv", _csv_bytes(SITES_CSV_GOOD), "text/csv")},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["ok"] is True
    assert body["mode"] == "preview"
    assert body["columns_ok"] is True
    assert body["summary"] == {"total_rows": 3, "rows_with_errors": 0}
    assert all(row["_errors"] == [] for row in body["rows"])
    # Nothing persisted yet
    dash = client.get(f"/api/projects/{pid}").json()
    assert dash["counts"]["total_sites"] == 0

    # Commit
    r2 = client.post(
        f"/api/projects/{pid}/sites/import?mode=commit",
        files={"file": ("sites.csv", _csv_bytes(SITES_CSV_GOOD), "text/csv")},
    )
    assert r2.status_code == 200
    assert r2.json()["ok"] is True
    assert r2.json()["mode"] == "commit"

    dash = client.get(f"/api/projects/{pid}").json()
    assert dash["counts"]["total_sites"] == 3
    names = sorted(s["name"] for s in dash["sites"])
    assert names == ["Carver Early Learning Center", "Hamilton High School", "Lincoln Elementary"]
    assert dash["project"]["sites_imported_at"] is not None

    # Required-column failure → ok:false, columns_ok:false, no rows
    bad = "name,addr\nFoo,Bar\n"
    r3 = client.post(
        f"/api/projects/{pid}/sites/import?mode=commit",
        files={"file": ("bad.csv", _csv_bytes(bad), "text/csv")},
    )
    assert r3.status_code == 200
    assert r3.json()["ok"] is False
    assert r3.json()["columns_ok"] is False
    assert any("site_name" in m for m in r3.json()["errors_summary"])
    # Existing data unchanged
    assert client.get(f"/api/projects/{pid}").json()["counts"]["total_sites"] == 3


# 3. ──────────────────────────────────────────────────────────────────────
def test_users_import_unknown_site_blocks(client):
    """Users import: a row whose site_name doesn't match an imported site is
    blocked with a row-level error message, and the commit is rejected."""
    proj = _make_project(client)
    pid = proj["id"]

    # Seed sites (we omit "Franklin High School" deliberately)
    client.post(f"/api/projects/{pid}/sites/import?mode=commit",
                files={"file": ("s.csv", _csv_bytes(SITES_CSV_GOOD), "text/csv")})

    users_csv = """employee_id,full_name,email,role,site_name
E2001,Sarah Lee,sarah.lee@demoisd.org,CN Director,Hamilton High School
E2002,Diego Tran,diego.tran@demoisd.org,Cashier,Franklin High School
"""
    # Preview surfaces the row-level error
    r = client.post(f"/api/projects/{pid}/users/import?mode=preview",
                    files={"file": ("u.csv", _csv_bytes(users_csv), "text/csv")})
    body = r.json()
    assert body["ok"] is False
    assert body["columns_ok"] is True
    assert body["summary"]["rows_with_errors"] == 1
    bad_row = next(row for row in body["rows"] if row["employee_id"] == "E2002")
    assert any('unknown site' in e.lower() for e in bad_row["_errors"])
    good_row = next(row for row in body["rows"] if row["employee_id"] == "E2001")
    assert good_row["_errors"] == []

    # Commit attempt with the same bad CSV is also blocked — no rows written.
    r2 = client.post(f"/api/projects/{pid}/users/import?mode=commit",
                     files={"file": ("u.csv", _csv_bytes(users_csv), "text/csv")})
    assert r2.json()["ok"] is False
    assert r2.json()["mode"] == "preview"  # falls back to preview shape when blocked
    assert client.get(f"/api/projects/{pid}").json()["counts"]["total_users"] == 0


# 4. ──────────────────────────────────────────────────────────────────────
def test_dashboard_counts(client):
    """Dashboard reports counts by role, total_users, total_sites, sites with
    user_count + by_role breakdown, and an empty tracks panel."""
    proj = _make_project(client)
    pid = proj["id"]
    client.post(f"/api/projects/{pid}/sites/import?mode=commit",
                files={"file": ("s.csv", _csv_bytes(SITES_CSV_GOOD), "text/csv")})
    client.post(f"/api/projects/{pid}/users/import?mode=commit",
                files={"file": ("u.csv", _csv_bytes(USERS_CSV_GOOD), "text/csv")})

    dash = client.get(f"/api/projects/{pid}").json()
    assert dash["counts"]["total_sites"] == 3
    assert dash["counts"]["total_users"] == 4
    assert dash["counts"]["by_role"] == {"Cashier": 2, "Site Manager": 1, "CN Director": 1}
    # site-level breakdown
    by_name = {s["name"]: s for s in dash["sites"]}
    assert by_name["Hamilton High School"]["user_count"] == 2  # 1 CN Director + 1 Cashier
    assert by_name["Hamilton High School"]["by_role"]["CN Director"] == 1
    assert by_name["Hamilton High School"]["by_role"]["Cashier"] == 1
    assert by_name["Lincoln Elementary"]["user_count"] == 1
    assert by_name["Carver Early Learning Center"]["user_count"] == 1
    # tracks panel intentionally empty (Task 3 hook)
    assert dash["tracks"] == []
    # roster timestamps stamped
    assert dash["project"]["sites_imported_at"]
    assert dash["project"]["users_imported_at"]


# Auth sanity (bonus, low-cost; not in the 4 required cases) ───────────────
def test_mock_login_sets_cookie(client):
    r = client.post("/api/auth/login")
    assert r.status_code == 200
    assert r.json()["user"]["name"] == "Sam Rivera"
    # cookie returned
    assert "lc_trainer" in r.cookies
    # subsequent /api/me reads it
    me = client.get("/api/me")
    assert me.json()["signed_in"] is True
    assert me.json()["user"]["name"] == "Sam Rivera"


# Status lifecycle ─────────────────────────────────────────────────────────
def test_default_status_planning(client):
    """A freshly-created project defaults to PLANNING (acceptance 6)."""
    proj = _make_project(client)
    assert proj["status"] == "PLANNING"
    assert proj["status_changed_at"]
    assert proj["can_assign_tracks"] is False
    assert proj["can_director_access"] is False
    assert proj["is_archived"] is False


def test_status_transition_persists(client):
    """Status dropdown allows manual transition to any other status
    (acceptance 7) and the new value persists across GETs."""
    proj = _make_project(client)
    pid = proj["id"]

    r = client.post(f"/api/projects/{pid}/status", json={"status": "ONBOARDING"})
    assert r.status_code == 200
    assert r.json()["project"]["status"] == "ONBOARDING"
    assert r.json()["project"]["can_assign_tracks"] is True

    # Persists on subsequent fetch.
    assert client.get(f"/api/projects/{pid}").json()["project"]["status"] == "ONBOARDING"

    # Walk through all valid statuses.
    for s in ("LIVE", "ARCHIVED", "PLANNING"):
        r2 = client.post(f"/api/projects/{pid}/status", json={"status": s})
        assert r2.status_code == 200, r2.text
        assert r2.json()["project"]["status"] == s

    # Invalid status rejected.
    bad = client.post(f"/api/projects/{pid}/status", json={"status": "in_progress"})
    assert bad.status_code == 400
    assert "status" in bad.json()["detail"]["errors"]

    # Lowercase auto-uppercased (forgiving input).
    ok = client.post(f"/api/projects/{pid}/status", json={"status": "live"})
    assert ok.status_code == 200 and ok.json()["project"]["status"] == "LIVE"


def test_status_helpers_truth_table():
    """Helper truth tables — the canonical source of behavior gating for
    the parallel track-assignment + Director-login work that imports these."""
    from projects import can_assign_tracks, can_director_access, is_archived

    # can_assign_tracks: ONBOARDING + LIVE only
    assert can_assign_tracks("PLANNING") is False    # too early
    assert can_assign_tracks("ONBOARDING") is True
    assert can_assign_tracks("LIVE") is True
    assert can_assign_tracks("ARCHIVED") is False    # read-only

    # can_director_access: LIVE + ARCHIVED (archived = read-only view)
    assert can_director_access("PLANNING") is False
    assert can_director_access("ONBOARDING") is False  # acceptance 9
    assert can_director_access("LIVE") is True         # acceptance 9
    assert can_director_access("ARCHIVED") is True     # read-only viewing

    # is_archived
    assert is_archived("ARCHIVED") is True
    for s in ("PLANNING", "ONBOARDING", "LIVE"):
        assert is_archived(s) is False
