"""Tests for Track Assignment and Enrollment Rules.

Run: python -m pytest test_assignments.py -v
"""
import pytest
from fastapi.testclient import TestClient

from projects import TRAINER_COOKIE, TRAINER_TOKEN, DIRECTOR_COOKIE, DIRECTOR_TOKEN

TRAINER_COOKIES = {TRAINER_COOKIE: TRAINER_TOKEN}
DIRECTOR_COOKIES = {DIRECTOR_COOKIE: DIRECTOR_TOKEN}


@pytest.fixture(autouse=True)
def clean_state(tmp_path, monkeypatch):
    """Wipe in-memory project/assignment/rule storage; redirect tracks to a temp dir."""
    import projects
    import modules_store
    projects._reset_for_tests()
    monkeypatch.setattr(modules_store, "TRACKS_DIR", tmp_path / "tracks")
    (tmp_path / "tracks").mkdir()


@pytest.fixture
def client():
    from demo_app import app
    return TestClient(app)


# ── Shared helpers ─────────────────────────────────────────────────────────────

def _make_project_with_users(client):
    """Create a project → 2 sites → 4 users (2 Cashiers, 1 Site Manager, 1 CN Director).
    Returns (pid, users_list, sites_list)."""
    resp = client.post("/api/projects", json={
        "name": "Test District", "product": "SchoolCafé", "go_live_date": "2026-12-01",
    })
    assert resp.status_code == 200
    pid = resp.json()["project"]["id"]

    sites_csv = "site_name,address\nLincoln,123 Main St\nWashington,456 Oak Ave"
    client.post(
        f"/api/projects/{pid}/sites/import?mode=commit",
        files={"file": ("s.csv", sites_csv.encode(), "text/csv")},
    )

    users_csv = (
        "employee_id,full_name,email,role,site_name\n"
        "E1,Alice Cashier,alice@test.com,Cashier,Lincoln\n"
        "E2,Bob Manager,bob@test.com,Site Manager,Lincoln\n"
        "E3,Carol Director,carol@test.com,CN Director,Washington\n"
        "E4,Dan Cashier,dan@test.com,Cashier,Washington"
    )
    client.post(
        f"/api/projects/{pid}/users/import?mode=commit",
        files={"file": ("u.csv", users_csv.encode(), "text/csv")},
    )

    import projects as p
    proj = p._PROJECTS[pid]
    users = list(proj["users"].values())
    sites = list(proj["sites"].values())
    return pid, users, sites


def _make_published_track(client):
    """Create a track with one module and publish it. Returns track_id."""
    resp = client.post("/api/tracks", json={"title": "Test Track"})
    assert resp.status_code == 200
    tid = resp.json()["id"]
    client.put(f"/api/tracks/{tid}/modules", json={"module_ids": ["GUIDE-001"]})
    client.post(f"/api/tracks/{tid}/publish")
    return tid


# ── Tests ──────────────────────────────────────────────────────────────────────

class TestManualAssign:
    def test_manual_assign_creates_rows(self, client):
        pid, users, _ = _make_project_with_users(client)
        tid = _make_published_track(client)
        user_ids = [u["id"] for u in users[:2]]

        resp = client.post(
            f"/api/projects/{pid}/assignments",
            json={"track_id": tid, "user_ids": user_ids},
            cookies=TRAINER_COOKIES,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert data["created"] == 2

        rows = client.get(f"/api/projects/{pid}/assignments").json()["assignments"]
        assert len(rows) == 2
        assert all(r["track_id"] == tid for r in rows)
        assert all(r["status"] == "NOT_STARTED" for r in rows)


class TestRulePreviewAndCommit:
    def test_rule_preview_matches_commit(self, client):
        pid, users, _ = _make_project_with_users(client)
        tid = _make_published_track(client)

        # Preview: Cashiers only → Alice + Dan = 2
        prev = client.post(
            f"/api/projects/{pid}/enrollment-rules/preview",
            json={"role_filter": ["Cashier"], "site_filter": []},
        )
        assert prev.status_code == 200
        assert prev.json()["preview_count"] == 2

        # Commit: enrolled count must match the preview
        commit = client.post(
            f"/api/projects/{pid}/enrollment-rules",
            json={"track_id": tid, "role_filter": ["Cashier"]},
            cookies=TRAINER_COOKIES,
        )
        assert commit.status_code == 200
        data = commit.json()
        assert data["enrolled"] == prev.json()["preview_count"]

        rows = client.get(f"/api/projects/{pid}/assignments").json()["assignments"]
        assert len(rows) == data["enrolled"]


class TestRuleIdempotent:
    def test_rule_idempotent(self, client):
        pid, _, _ = _make_project_with_users(client)
        tid = _make_published_track(client)

        payload = {"track_id": tid, "role_filter": ["Cashier"]}

        r1 = client.post(
            f"/api/projects/{pid}/enrollment-rules",
            json=payload, cookies=TRAINER_COOKIES,
        ).json()
        assert r1["enrolled"] == 2

        # Same rule again — no new enrollments
        r2 = client.post(
            f"/api/projects/{pid}/enrollment-rules",
            json=payload, cookies=TRAINER_COOKIES,
        ).json()
        assert r2["enrolled"] == 0

        # Table still has exactly 2 rows (not 4)
        rows = client.get(f"/api/projects/{pid}/assignments").json()["assignments"]
        assert len(rows) == 2


class TestAssignmentTableFilters:
    def test_assignment_table_filters(self, client):
        pid, users, _ = _make_project_with_users(client)
        t1 = _make_published_track(client)
        t2 = _make_published_track(client)

        cashiers = [u["id"] for u in users if u["role"] == "Cashier"]
        mgrs = [u["id"] for u in users if u["role"] == "Site Manager"]

        client.post(
            f"/api/projects/{pid}/assignments",
            json={"track_id": t1, "user_ids": cashiers},
            cookies=TRAINER_COOKIES,
        )
        client.post(
            f"/api/projects/{pid}/assignments",
            json={"track_id": t2, "user_ids": mgrs},
            cookies=TRAINER_COOKIES,
        )

        # Filter by track_id
        by_t1 = client.get(
            f"/api/projects/{pid}/assignments?track_id={t1}"
        ).json()["assignments"]
        assert len(by_t1) == len(cashiers)
        assert all(r["track_id"] == t1 for r in by_t1)

        # Filter by status (all are NOT_STARTED)
        by_ns = client.get(
            f"/api/projects/{pid}/assignments?status=NOT_STARTED"
        ).json()["assignments"]
        assert len(by_ns) == len(cashiers) + len(mgrs)

        # No filter — all rows
        all_rows = client.get(f"/api/projects/{pid}/assignments").json()["assignments"]
        assert len(all_rows) == len(cashiers) + len(mgrs)


class TestDirectorCannotAssign:
    def test_director_cannot_assign(self, client):
        pid, users, _ = _make_project_with_users(client)
        tid = _make_published_track(client)

        resp = client.post(
            f"/api/projects/{pid}/assignments",
            json={"track_id": tid, "user_ids": [users[0]["id"]]},
            cookies=DIRECTOR_COOKIES,
        )
        assert resp.status_code == 403

    def test_director_cannot_create_rule(self, client):
        pid, _, _ = _make_project_with_users(client)
        tid = _make_published_track(client)

        resp = client.post(
            f"/api/projects/{pid}/enrollment-rules",
            json={"track_id": tid, "role_filter": ["Cashier"]},
            cookies=DIRECTOR_COOKIES,
        )
        assert resp.status_code == 403
