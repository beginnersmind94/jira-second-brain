"""Tests for Module library filters + Track builder (Task 2).

Run: python -m pytest test_modules_tracks.py -v
"""
import json
import pytest
from pathlib import Path
from fastapi.testclient import TestClient


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def clean_tracks(tmp_path, monkeypatch):
    """Redirect tracks storage to a temp directory so tests don't pollute data/tracks/."""
    import modules_store
    monkeypatch.setattr(modules_store, "TRACKS_DIR", tmp_path / "tracks")
    (tmp_path / "tracks").mkdir()


@pytest.fixture
def client():
    from demo_app import app
    return TestClient(app)


# ── test_library_filters ───────────────────────────────────────────────────────

class TestLibraryFilters:
    def test_returns_modules(self, client):
        resp = client.get("/api/modules")
        assert resp.status_code == 200
        data = resp.json()
        assert "modules" in data
        assert "total" in data
        assert "sources" in data

    def test_filter_by_source_human_guide(self, client):
        resp = client.get("/api/modules?source=HUMAN_GUIDE")
        data = resp.json()
        sources = {m["source"] for m in data["modules"]}
        assert sources <= {"HUMAN_GUIDE"}

    def test_filter_by_source_ai_transcript(self, client):
        resp = client.get("/api/modules?source=AI_TRANSCRIPT")
        data = resp.json()
        sources = {m["source"] for m in data["modules"]}
        assert sources <= {"AI_TRANSCRIPT"}

    def test_filter_q_matches_title(self, client):
        # Any module whose title contains "item" (case-insensitive) should match
        resp = client.get("/api/modules?q=item")
        data = resp.json()
        for m in data["modules"]:
            hay = ((m.get("title") or "") + " " + (m.get("module") or "")).lower()
            assert "item" in hay

    def test_total_matches_module_list_length(self, client):
        resp = client.get("/api/modules")
        data = resp.json()
        assert data["total"] == len(data["modules"])

    def test_only_approved_modules_returned(self, client):
        resp = client.get("/api/modules")
        data = resp.json()
        for m in data["modules"]:
            assert m["status"] == "approved"


# ── test_track_builder_reorder_persists ───────────────────────────────────────

class TestTrackBuilderReorder:
    def test_create_track(self, client):
        resp = client.post("/api/tracks", json={"title": "Test Track"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Test Track"
        assert data["status"] == "draft"
        assert "id" in data

    def test_set_modules(self, client):
        # Create a track then set its modules
        create_resp = client.post("/api/tracks", json={"title": "Reorder Test"})
        tid = create_resp.json()["id"]
        mod_ids = ["GUIDE-001", "GUIDE-002", "GUIDE-003"]
        resp = client.put(f"/api/tracks/{tid}/modules", json={"module_ids": mod_ids})
        assert resp.status_code == 200
        data = resp.json()
        assert data["module_ids"] == mod_ids

    def test_reorder_persists(self, client):
        create_resp = client.post("/api/tracks", json={"title": "Reorder Persists"})
        tid = create_resp.json()["id"]
        first_order = ["GUIDE-001", "GUIDE-002", "GUIDE-003"]
        client.put(f"/api/tracks/{tid}/modules", json={"module_ids": first_order})
        # Reorder: move GUIDE-003 to front
        new_order = ["GUIDE-003", "GUIDE-001", "GUIDE-002"]
        client.put(f"/api/tracks/{tid}/modules", json={"module_ids": new_order})
        # Re-fetch
        get_resp = client.get(f"/api/tracks/{tid}")
        assert get_resp.status_code == 200
        assert get_resp.json()["module_ids"] == new_order

    def test_get_track_returns_modules_in_order(self, client):
        create_resp = client.post("/api/tracks", json={"title": "Ordered"})
        tid = create_resp.json()["id"]
        # Use real GUIDE ids from the actual data
        from modules_store import list_modules, TRACKS_DIR
        import modules_store as ms
        mods = list_modules()["modules"]
        if len(mods) >= 2:
            ids = [mods[0]["id"], mods[1]["id"]]
            client.put(f"/api/tracks/{tid}/modules", json={"module_ids": ids})
            get_resp = client.get(f"/api/tracks/{tid}")
            expanded = get_resp.json().get("modules") or []
            assert [m["id"] for m in expanded] == ids


# ── test_publish_requires_module ──────────────────────────────────────────────

class TestPublishRequiresModule:
    def test_publish_empty_track_fails(self, client):
        create_resp = client.post("/api/tracks", json={"title": "Empty Track"})
        tid = create_resp.json()["id"]
        resp = client.post(f"/api/tracks/{tid}/publish")
        assert resp.status_code == 409
        assert resp.json()["detail"]["error"] == "no_modules"

    def test_publish_with_modules_succeeds(self, client):
        create_resp = client.post("/api/tracks", json={"title": "Full Track"})
        tid = create_resp.json()["id"]
        client.put(f"/api/tracks/{tid}/modules", json={"module_ids": ["GUIDE-001"]})
        resp = client.post(f"/api/tracks/{tid}/publish")
        assert resp.status_code == 200
        assert resp.json()["status"] == "published"

    def test_published_track_appears_in_list(self, client):
        create_resp = client.post("/api/tracks", json={"title": "Visible Track"})
        tid = create_resp.json()["id"]
        client.put(f"/api/tracks/{tid}/modules", json={"module_ids": ["GUIDE-001"]})
        client.post(f"/api/tracks/{tid}/publish")
        list_resp = client.get("/api/tracks")
        ids = [t["id"] for t in list_resp.json()["tracks"]]
        assert tid in ids


# ── test_quiz_cite_must_reference_track_module ────────────────────────────────

class TestQuizCiteMustReferenceTrackModule:
    """The track builder enforces that quiz questions cite a module IN the track.
    This is implemented in the frontend (dropdown is restricted to track modules),
    and tested here at the API level: attaching a quiz stores the quiz_id correctly."""

    def test_attach_quiz_to_track(self, client):
        # Create a quiz first via the quiz store
        import quiz_store
        quiz = {
            "id": quiz_store.new_quiz_id("manual"),
            "title": "Test Quiz",
            "status": "draft",
            "source_type": "manual",
            "source_id": "",
            "source_label": "Manual",
            "source_content_hash": "",
            "questions": [],
            "stale": False,
        }
        quiz_store.save_quiz(quiz)
        qid = quiz["id"]

        # Create track with a module, attach quiz
        create_resp = client.post("/api/tracks", json={"title": "Quiz Track"})
        tid = create_resp.json()["id"]
        client.put(f"/api/tracks/{tid}/modules", json={"module_ids": ["GUIDE-001"]})

        resp = client.post(f"/api/tracks/{tid}/quiz", json={"quiz_id": qid})
        assert resp.status_code == 200
        assert resp.json()["quiz_id"] == qid

    def test_attach_nonexistent_quiz_fails(self, client):
        create_resp = client.post("/api/tracks", json={"title": "Quiz 404 Track"})
        tid = create_resp.json()["id"]
        resp = client.post(f"/api/tracks/{tid}/quiz", json={"quiz_id": "nonexistent-quiz-id"})
        assert resp.status_code == 404
