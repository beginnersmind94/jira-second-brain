"""Tests for Module library filters + Track builder (Task 2).

Run: python -m pytest test_modules_tracks.py -v
"""
import json
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

# Trainer identity header so publish endpoints (trainer-only) don't 403.
_TRAINER_HEADERS = {"X-Demo-User": "sam-trainer"}


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
        resp = client.post(f"/api/tracks/{tid}/publish", headers=_TRAINER_HEADERS)
        assert resp.status_code == 409
        assert resp.json()["detail"]["error"] == "no_modules"

    def test_publish_with_modules_succeeds(self, client):
        create_resp = client.post("/api/tracks", json={"title": "Full Track"})
        tid = create_resp.json()["id"]
        client.put(f"/api/tracks/{tid}/modules", json={"module_ids": ["GUIDE-001"]})
        resp = client.post(f"/api/tracks/{tid}/publish", headers=_TRAINER_HEADERS)
        assert resp.status_code == 200
        assert resp.json()["status"] == "published"

    def test_published_track_appears_in_list(self, client):
        create_resp = client.post("/api/tracks", json={"title": "Visible Track"})
        tid = create_resp.json()["id"]
        client.put(f"/api/tracks/{tid}/modules", json={"module_ids": ["GUIDE-001"]})
        client.post(f"/api/tracks/{tid}/publish", headers=_TRAINER_HEADERS)
        list_resp = client.get("/api/tracks")
        ids = [t["id"] for t in list_resp.json()["tracks"]]
        assert tid in ids


# ── test_quiz_cite_must_reference_track_module ────────────────────────────────

class TestQuizCiteMustReferenceTrackModule:
    """The track builder enforces that quiz questions cite a module IN the track.
    This is implemented in the frontend (dropdown is restricted to track modules),
    and tested here at the API level: attaching a quiz stores the quiz_id correctly."""

    @pytest.fixture(autouse=True)
    def _isolate_stores(self, tmp_path, monkeypatch):
        """Redirect every dir this class writes to into tmp so the test is hermetic.

        ``clean_tracks`` (module-level autouse) already redirects ``TRACKS_DIR``;
        this adds the quiz and course dirs. Without it, ``quiz_store.save_quiz``
        wrote to the real ``quizzes/`` dir AND inherited whatever global another
        test file left behind — e.g. ``eval/test_assessment_store.py`` raw-assigns
        ``quiz_store.QUIZZES`` to a ``TemporaryDirectory`` and never restores it,
        so by the time this test ran the global pointed at a since-deleted dir and
        ``save_quiz`` raised ``FileNotFoundError``. Owning the dir makes the test
        pass regardless of run order.
        """
        import quiz_store
        import course_store
        quizzes = tmp_path / "quizzes"
        courses = tmp_path / "courses"
        quizzes.mkdir()
        courses.mkdir()
        monkeypatch.setattr(quiz_store, "QUIZZES", quizzes)
        monkeypatch.setattr(course_store, "COURSES_DIR", courses)

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


# ── test_course_based_track_expansion ────────────────────────────────────────
#
# These tests cover the data-integrity fix for the Track Builder course_ids bug:
#   1. A course-based track expands to its real lessons (not empty).
#   2. PUT /api/tracks/:id/modules on a course-based track returns 409 (fork guard).
#   3. A module-based (legacy) track still works unchanged (regression).
#   4. A course-based track with lessons can be published (publish guard updated).

class TestCourseBasedTrackExpansion:
    """Verify that the builder correctly reads and protects course-based tracks."""

    @pytest.fixture(autouse=True)
    def _seed_course(self, tmp_path, monkeypatch):
        """Create one approved guide + one course with two lessons in temp storage."""
        import modules_store
        import course_store

        # Redirect COURSES_DIR to temp so we don't touch real data/courses/.
        monkeypatch.setattr(course_store, "COURSES_DIR", tmp_path / "courses")
        (tmp_path / "courses").mkdir()

        # Create a minimal published/metadata dir with one approved guide.
        pub_meta = tmp_path / "pub_meta"
        pub_meta.mkdir()
        guide_meta = {
            "id": "GUIDE-TEST-01",
            "title": "Test Guide One",
            "module": "POS",
            "status": "approved",
            "approved": True,
            "origin": "internal",
        }
        (pub_meta / "GUIDE-TEST-01.json").write_text(
            json.dumps(guide_meta), encoding="utf-8"
        )

        # Point course_store's pub_meta dir at our temp one.
        monkeypatch.setattr(course_store, "_PUB_META_DIR", pub_meta)

        # Create a course with two lessons (one guide, one exercise).
        course = course_store.create_course(
            title="Test Course",
            product="SchoolCafé",
            role_tags=["Cashier"],
            lessons=[
                {"type": "guide", "ref": "GUIDE-TEST-01", "title": "Lesson A", "duration_est": 5},
                {"type": "exercise", "ref": "ex-001", "title": "Lesson B", "duration_est": 3},
            ],
        )
        # Force to published so tests can use it.
        course["status"] = "published"
        course_store.save_course(course)
        self._course_id = course["id"]

    def _make_course_track(self, client) -> str:
        """Create a course-based track (with course_ids, no module_ids) and return its id."""
        import modules_store

        track = modules_store.create_track(title="Course-Based Track")
        track["course_ids"] = [self._course_id]
        track["module_ids"] = []
        modules_store.save_track(track)
        return track["id"]

    # ── T1: course-based track expands to real lessons (not empty) ────────────

    def test_course_track_expands_to_real_modules(self, client):
        """GET /api/tracks/:id on a course-based track must return non-empty modules."""
        tid = self._make_course_track(client)
        resp = client.get(f"/api/tracks/{tid}")
        assert resp.status_code == 200
        data = resp.json()
        modules = data.get("modules") or []
        assert len(modules) >= 2, (
            f"Expected at least 2 modules from course expansion, got {len(modules)}: {modules}"
        )
        # Each stub carries _from_courses so the builder knows it's read-only.
        for m in modules:
            assert m.get("_from_courses") is True, (
                f"Module stub missing _from_courses flag: {m}"
            )

    def test_course_track_lesson_refs_present(self, client):
        """The expanded modules must reference the actual lesson refs."""
        tid = self._make_course_track(client)
        resp = client.get(f"/api/tracks/{tid}")
        data = resp.json()
        refs = [m["id"] for m in (data.get("modules") or [])]
        assert "GUIDE-TEST-01" in refs, f"Expected GUIDE-TEST-01 in expanded refs, got {refs}"
        assert "ex-001" in refs, f"Expected ex-001 in expanded refs, got {refs}"

    # ── T2: PUT /api/tracks/:id/modules on course-based track → 409 (fork guard)

    def test_put_modules_on_course_track_returns_409(self, client):
        """Writing module_ids on a course-based track must be rejected."""
        tid = self._make_course_track(client)
        resp = client.put(f"/api/tracks/{tid}/modules", json={"module_ids": ["GUIDE-001"]})
        assert resp.status_code == 409, (
            f"Expected 409 to prevent forking composition, got {resp.status_code}"
        )
        detail = resp.json().get("detail") or {}
        assert detail.get("error") == "course_based_track", (
            f"Expected error='course_based_track', got {detail}"
        )

    def test_put_modules_on_course_track_does_not_write_module_ids(self, client):
        """After a rejected PUT, the on-disk track must still have empty module_ids."""
        import modules_store
        tid = self._make_course_track(client)
        client.put(f"/api/tracks/{tid}/modules", json={"module_ids": ["GUIDE-001"]})
        # Reload from disk and verify module_ids was NOT written.
        on_disk = modules_store.load_track(tid)
        assert (on_disk.get("module_ids") or []) == [], (
            f"module_ids was written on disk after 409-guarded PUT: {on_disk.get('module_ids')}"
        )

    # ── T3: module-based (legacy) track still works (regression) ─────────────

    def test_legacy_module_track_still_works(self, client):
        """A track with only module_ids (no course_ids) must still expand correctly."""
        create_resp = client.post("/api/tracks", json={"title": "Legacy Module Track"})
        tid = create_resp.json()["id"]
        # Use real module ids from the actual data.
        from modules_store import list_modules
        mods = list_modules()["modules"]
        if not mods:
            pytest.skip("No modules in library — cannot test legacy expansion")
        ids = [mods[0]["id"]]
        client.put(f"/api/tracks/{tid}/modules", json={"module_ids": ids})
        get_resp = client.get(f"/api/tracks/{tid}")
        assert get_resp.status_code == 200
        expanded = get_resp.json().get("modules") or []
        assert [m["id"] for m in expanded] == ids, (
            f"Legacy module_ids expansion broken: expected {ids}, got {[m['id'] for m in expanded]}"
        )

    def test_legacy_track_put_modules_still_accepted(self, client):
        """PUT /api/tracks/:id/modules on a module-based (no course_ids) track must succeed."""
        create_resp = client.post("/api/tracks", json={"title": "Legacy PUT Test"})
        tid = create_resp.json()["id"]
        resp = client.put(f"/api/tracks/{tid}/modules", json={"module_ids": ["GUIDE-001"]})
        assert resp.status_code == 200, (
            f"Legacy PUT /modules should still return 200, got {resp.status_code}"
        )
        assert resp.json()["module_ids"] == ["GUIDE-001"]

    # ── T4: course-based track with lessons can be published ─────────────────

    def test_course_track_with_courses_can_be_published(self, client):
        """POST /api/tracks/:id/publish on a course-based track with course_ids must succeed."""
        tid = self._make_course_track(client)
        resp = client.post(f"/api/tracks/{tid}/publish", headers=_TRAINER_HEADERS)
        assert resp.status_code == 200, (
            f"Expected publish to succeed for course-based track, got {resp.status_code}: {resp.text}"
        )
        assert resp.json()["status"] == "published"

    def test_empty_track_still_blocked_from_publish(self, client):
        """A track with neither module_ids nor course_ids must still be blocked from publishing."""
        create_resp = client.post("/api/tracks", json={"title": "Truly Empty Track"})
        tid = create_resp.json()["id"]
        resp = client.post(f"/api/tracks/{tid}/publish", headers=_TRAINER_HEADERS)
        assert resp.status_code == 409
        assert resp.json()["detail"]["error"] == "no_modules"


# ── test_set_track_courses ───────────────────────────────────────────────────
#
# The composition spine: PUT /api/tracks/:id/courses is how a trainer composes /
# reorders the courses that make up a track (the write-side of the course expansion
# the learner player reads). These tests pin that it persists, expands, rejects
# phantom courses, is trainer-gated, and won't blank a legacy module-based track.

class TestSetTrackCourses:
    @pytest.fixture(autouse=True)
    def _seed_courses(self, tmp_path, monkeypatch):
        import course_store
        monkeypatch.setattr(course_store, "COURSES_DIR", tmp_path / "courses")
        (tmp_path / "courses").mkdir()
        self._cs = course_store
        self._c1 = course_store.create_course(title="Working the Line", lessons=[])["id"]
        self._c2 = course_store.create_course(title="Closing Out the Day", lessons=[])["id"]

    def _new_track(self, client) -> str:
        return client.post("/api/tracks", json={"title": "Cashier Path", "role_tags": ["Cashier"]}).json()["id"]

    def test_set_courses_persists_and_expands(self, client):
        tid = self._new_track(client)
        r = client.put(f"/api/tracks/{tid}/courses",
                       json={"course_ids": [self._c1]}, headers=_TRAINER_HEADERS)
        assert r.status_code == 200, r.text
        assert r.json()["course_ids"] == [self._c1]
        # GET now expands real courses (not the implicit module shim).
        g = client.get(f"/api/tracks/{tid}", headers=_TRAINER_HEADERS).json()
        assert [c["id"] for c in g.get("courses", [])] == [self._c1]

    def test_reorder_courses(self, client):
        tid = self._new_track(client)
        client.put(f"/api/tracks/{tid}/courses",
                   json={"course_ids": [self._c1, self._c2]}, headers=_TRAINER_HEADERS)
        r = client.put(f"/api/tracks/{tid}/courses",
                       json={"course_ids": [self._c2, self._c1]}, headers=_TRAINER_HEADERS)
        assert r.json()["course_ids"] == [self._c2, self._c1]

    def test_phantom_course_rejected(self, client):
        tid = self._new_track(client)
        r = client.put(f"/api/tracks/{tid}/courses",
                       json={"course_ids": ["course-does-not-exist"]}, headers=_TRAINER_HEADERS)
        assert r.status_code == 422
        assert "course-does-not-exist" in r.text

    def test_requires_trainer(self, client):
        tid = self._new_track(client)
        r = client.put(f"/api/tracks/{tid}/courses",
                       json={"course_ids": [self._c1]}, headers={"X-Demo-User": "john-cashier"})
        assert r.status_code == 403

    def test_track_not_found(self, client):
        r = client.put("/api/tracks/track-nope/courses",
                       json={"course_ids": []}, headers=_TRAINER_HEADERS)
        assert r.status_code == 404

    def test_empty_courses_on_module_track_rejected(self, client):
        """Setting empty courses on a legacy module-based track must not blank it."""
        import modules_store
        track = modules_store.create_track(title="Legacy Module Track")
        track["module_ids"] = ["GUIDE-001"]
        modules_store.save_track(track)
        r = client.put(f"/api/tracks/{track['id']}/courses",
                       json={"course_ids": []}, headers=_TRAINER_HEADERS)
        assert r.status_code == 422
        assert r.json()["detail"]["error"] == "would_orphan_modules"
