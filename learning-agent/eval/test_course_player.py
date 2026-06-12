"""Tests for D1 — Unified course player backend.

Run from learning-agent/ with:
    python -m pytest eval/test_course_player.py -v

Test inventory (6 cases — maps to the D1 spec):

  TC-D1-01: POST /api/tracks/{tid}/lesson-progress  →  200, progress persists
  TC-D1-02: set_lesson_done() is idempotent (calling twice = no duplicate, no error)
  TC-D1-03: GET /resources/{rid}/html returns HTML string (no plain-text, not a redirect)
  TC-D1-SHOULD-NOT-OCCUR: returned HTML must NOT contain "<!-- Source:" comments
  TC-D1-05: GET /api/tracks/{tid} for a legacy flat track synthesises courses with _implicit: true
  TC-D1-06: Lesson-level progress survives a simulated server restart (disk persistence)

All tests are deterministic and offline — no SDK, no LLM calls, no real disk writes outside tmp_path.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Make learning-agent/ importable regardless of cwd.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# ── Fixture: isolated completion store ───────────────────────────────────────

@pytest.fixture(autouse=True)
def isolated_completion_store(tmp_path, monkeypatch):
    """Redirect completion_store file I/O to tmp_path for test isolation."""
    import completion_store as cs
    monkeypatch.setattr(cs, "_COMPLETION_DIR", tmp_path / "completion")
    return tmp_path / "completion"


# ── Helpers ──────────────────────────────────────────────────────────────────

USER_ID = "demo-user-course-player-test"
TRACK_ID = "track-d1-test-00000a"
COURSE_ID = "course-d1-abc"
LESSON_REF = "lesson-guide-001"


# ─────────────────────────────────────────────────────────────────────────────
# TC-D1-01: POST /api/tracks/{tid}/lesson-progress → 200, progress persists
# ─────────────────────────────────────────────────────────────────────────────

class TestLessonProgressEndpoint:
    """The lesson-progress endpoint accepts valid requests and persists them."""

    def _make_app(self, tmp_path: Path):
        """Build a minimal FastAPI app with the lesson-progress route + its dependencies."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        import completion_store as cs
        import demo_app
        import modules_store as ms

        # Build a minimal real track on disk (in a temp tracks dir).
        tracks_dir = tmp_path / "tracks"
        tracks_dir.mkdir(parents=True, exist_ok=True)
        track = {
            "id": TRACK_ID,
            "title": "Test Track",
            "module_ids": [LESSON_REF],
            "status": "published",
        }
        (tracks_dir / f"{TRACK_ID}.json").write_text(
            json.dumps(track), encoding="utf-8"
        )

        # Fake current user for auth bypass.
        fake_user = MagicMock()
        fake_user.id = USER_ID

        mini = FastAPI()
        mini.add_api_route(
            "/api/tracks/{tid}/lesson-progress",
            demo_app.api_mark_lesson_done,
            methods=["POST"],
        )

        def override_user():
            return fake_user

        from demo_app import get_current_user
        mini.dependency_overrides[get_current_user] = override_user

        with (
            patch.object(ms, "TRACKS_DIR", tracks_dir),
            patch.object(demo_app, "_ms", ms),
            patch.object(demo_app, "_cs", cs),
        ):
            client = TestClient(mini, raise_server_exceptions=True)
            yield client

    def test_valid_lesson_progress_returns_200(self, tmp_path):
        """POST with valid course_id + lesson_ref returns 200 and ok: true."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        import completion_store as cs
        import demo_app
        import modules_store as ms

        tracks_dir = tmp_path / "tracks"
        tracks_dir.mkdir(parents=True, exist_ok=True)
        track = {"id": TRACK_ID, "title": "T", "module_ids": [LESSON_REF], "status": "published"}
        (tracks_dir / f"{TRACK_ID}.json").write_text(json.dumps(track), encoding="utf-8")

        fake_user = MagicMock()
        fake_user.id = USER_ID

        mini = FastAPI()
        mini.add_api_route(
            "/api/tracks/{tid}/lesson-progress",
            demo_app.api_mark_lesson_done,
            methods=["POST"],
        )
        from demo_app import get_current_user
        mini.dependency_overrides[get_current_user] = lambda: fake_user

        with (
            patch.object(ms, "TRACKS_DIR", tracks_dir),
            patch.object(demo_app, "_ms", ms),
            patch.object(demo_app, "_cs", cs),
        ):
            client = TestClient(mini, raise_server_exceptions=True)
            resp = client.post(
                f"/api/tracks/{TRACK_ID}/lesson-progress",
                json={"course_id": COURSE_ID, "lesson_ref": LESSON_REF},
            )

        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        body = resp.json()
        assert body["ok"] is True
        assert body["course_id"] == COURSE_ID
        assert body["lesson_ref"] == LESSON_REF

    def test_lesson_progress_persists_to_completion_store(self, tmp_path, isolated_completion_store):
        """After a valid POST, completion_store records the lesson as done."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        import completion_store as cs
        import demo_app
        import modules_store as ms

        tracks_dir = tmp_path / "tracks"
        tracks_dir.mkdir(parents=True, exist_ok=True)
        track = {"id": TRACK_ID, "title": "T", "module_ids": [LESSON_REF], "status": "published"}
        (tracks_dir / f"{TRACK_ID}.json").write_text(json.dumps(track), encoding="utf-8")

        fake_user = MagicMock()
        fake_user.id = USER_ID

        mini = FastAPI()
        mini.add_api_route(
            "/api/tracks/{tid}/lesson-progress",
            demo_app.api_mark_lesson_done,
            methods=["POST"],
        )
        from demo_app import get_current_user
        mini.dependency_overrides[get_current_user] = lambda: fake_user

        with (
            patch.object(ms, "TRACKS_DIR", tracks_dir),
            patch.object(demo_app, "_ms", ms),
            patch.object(demo_app, "_cs", cs),
        ):
            client = TestClient(mini, raise_server_exceptions=True)
            client.post(
                f"/api/tracks/{TRACK_ID}/lesson-progress",
                json={"course_id": COURSE_ID, "lesson_ref": LESSON_REF},
            )

        # Read the progress file directly from disk.
        assert cs.get_lesson_done(USER_ID, TRACK_ID, COURSE_ID, LESSON_REF), (
            "Lesson was not persisted after POST /lesson-progress"
        )

    def test_missing_fields_returns_400(self, tmp_path):
        """POST with missing course_id or lesson_ref returns 400."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        import completion_store as cs
        import demo_app
        import modules_store as ms

        tracks_dir = tmp_path / "tracks"
        tracks_dir.mkdir(parents=True, exist_ok=True)
        track = {"id": TRACK_ID, "title": "T", "module_ids": [], "status": "published"}
        (tracks_dir / f"{TRACK_ID}.json").write_text(json.dumps(track), encoding="utf-8")

        fake_user = MagicMock()
        fake_user.id = USER_ID

        mini = FastAPI()
        mini.add_api_route(
            "/api/tracks/{tid}/lesson-progress",
            demo_app.api_mark_lesson_done,
            methods=["POST"],
        )
        from demo_app import get_current_user
        mini.dependency_overrides[get_current_user] = lambda: fake_user

        with (
            patch.object(ms, "TRACKS_DIR", tracks_dir),
            patch.object(demo_app, "_ms", ms),
            patch.object(demo_app, "_cs", cs),
        ):
            client = TestClient(mini, raise_server_exceptions=False)
            resp = client.post(
                f"/api/tracks/{TRACK_ID}/lesson-progress",
                json={"course_id": COURSE_ID},  # lesson_ref omitted
            )

        assert resp.status_code == 400, f"Expected 400, got {resp.status_code}"


# ─────────────────────────────────────────────────────────────────────────────
# TC-D1-02: set_lesson_done() is idempotent
# ─────────────────────────────────────────────────────────────────────────────

class TestSetLessonDoneIdempotent:
    """set_lesson_done() — calling twice does not duplicate the ref or raise an error."""

    def test_idempotent_second_call_is_noop(self):
        import completion_store as cs

        cs.set_lesson_done(USER_ID, TRACK_ID, COURSE_ID, LESSON_REF)
        cs.set_lesson_done(USER_ID, TRACK_ID, COURSE_ID, LESSON_REF)  # second call

        path = cs._progress_path(USER_ID, TRACK_ID)
        raw = json.loads(path.read_text(encoding="utf-8"))
        refs = raw["lessons_done"][COURSE_ID]
        assert refs.count(LESSON_REF) == 1, (
            f"Expected exactly 1 entry for {LESSON_REF!r}; got {refs}"
        )

    def test_idempotent_does_not_raise(self):
        import completion_store as cs

        # Should not raise even if called many times.
        for _ in range(5):
            cs.set_lesson_done(USER_ID, TRACK_ID, COURSE_ID, LESSON_REF)

        assert cs.get_lesson_done(USER_ID, TRACK_ID, COURSE_ID, LESSON_REF) is True

    def test_multiple_distinct_lessons_coexist(self):
        import completion_store as cs

        refs = ["lesson-a", "lesson-b", "lesson-c"]
        for ref in refs:
            cs.set_lesson_done(USER_ID, TRACK_ID, COURSE_ID, ref)

        for ref in refs:
            assert cs.get_lesson_done(USER_ID, TRACK_ID, COURSE_ID, ref), (
                f"Expected lesson {ref!r} to be marked done"
            )


# ─────────────────────────────────────────────────────────────────────────────
# TC-D1-03: GET /resources/{rid}/html returns HTML string
# TC-D1-SHOULD-NOT-OCCUR: response must NOT contain <!-- Source: comments
# ─────────────────────────────────────────────────────────────────────────────

class TestResourceHtmlEndpoint:
    """GET /resources/{rid}/html — citation-stripped inline HTML for the course player."""

    def _make_html_app(self, tmp_path: Path, *, has_source_comments: bool = True):
        """Write a fake resource + meta and return a TestClient for resource_html."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        import demo_app

        # Build a fake resource HTML file with source comments.
        rid = "GUIDE-TEST-001"
        html_content = """<h1>Test Guide</h1>
<!-- Source: NXT-1234 AC: "verbatim quote here" -->
<p>This is a paragraph.</p>
<!-- Source: NXT-5678 RN: "another quote" -->
<p>Another paragraph.</p>""" if has_source_comments else "<h1>Test Guide</h1><p>No comments.</p>"

        drafts_dir = tmp_path / "drafts"
        drafts_dir.mkdir(parents=True, exist_ok=True)
        html_file = drafts_dir / f"{rid}.html"
        html_file.write_text(html_content, encoding="utf-8")

        meta_file = drafts_dir / f"{rid}-meta.json"
        meta_file.write_text(
            json.dumps({"id": rid, "title": "Test Guide", "approved": True}),
            encoding="utf-8",
        )

        def fake_resolve(r):
            if r == rid:
                return html_file, meta_file, "approved"
            return None

        def fake_read_meta(p):
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                return {}

        mini = FastAPI()
        mini.add_api_route(
            "/resources/{rid}/html",
            demo_app.resource_html,
            methods=["GET"],
        )

        from fastapi.responses import HTMLResponse  # noqa: F401

        with (
            patch.object(demo_app.prod, "_resolve_resource", fake_resolve),
            patch.object(demo_app.prod, "_read_meta", fake_read_meta),
        ):
            client = TestClient(mini, raise_server_exceptions=True)
            yield client, rid

    def test_endpoint_returns_html_string(self, tmp_path):
        """GET /resources/{rid}/html responds with 200 and HTML content-type."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        import demo_app

        rid = "GUIDE-TEST-001"
        html_file = tmp_path / f"{rid}.html"
        html_file.write_text("<h1>Hello</h1>", encoding="utf-8")
        meta_file = tmp_path / f"{rid}-meta.json"
        meta_file.write_text(json.dumps({"id": rid, "approved": True}), encoding="utf-8")

        mini = FastAPI()
        mini.add_api_route("/resources/{rid}/html", demo_app.resource_html, methods=["GET"])

        with (
            patch.object(demo_app.prod, "_resolve_resource", lambda r: (html_file, meta_file, "approved") if r == rid else None),
            patch.object(demo_app.prod, "_read_meta", lambda p: {"id": rid, "approved": True}),
            patch.object(demo_app, "CONFERENCE_MODE", True),
        ):
            client = TestClient(mini, raise_server_exceptions=True)
            resp = client.get(f"/resources/{rid}/html")

        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        assert "text/html" in resp.headers.get("content-type", ""), (
            "Expected text/html content-type"
        )
        assert "Hello" in resp.text, "Guide content should be present in response"

    def test_unknown_resource_returns_404(self, tmp_path):
        """GET /resources/{rid}/html returns 404 for unknown resource id."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        import demo_app

        mini = FastAPI()
        mini.add_api_route("/resources/{rid}/html", demo_app.resource_html, methods=["GET"])

        with patch.object(demo_app.prod, "_resolve_resource", lambda r: None):
            client = TestClient(mini, raise_server_exceptions=False)
            resp = client.get("/resources/GUIDE-DOES-NOT-EXIST/html")

        assert resp.status_code == 404

    # ── TC-D1-SHOULD-NOT-OCCUR ──────────────────────────────────────────────
    def test_SHOULD_NOT_OCCUR_no_source_comments_in_response(self, tmp_path):
        """SHOULD-NOT-OCCUR: <!-- Source: --> citation comments must NEVER appear in the
        response served to learners.

        This is the cardinal trust guardrail for the /html endpoint — learners must
        never see internal citation metadata. The test fails the suite if even one
        comment slips through.
        """
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        import demo_app

        rid = "GUIDE-CITE-001"
        html_with_citations = (
            "<h1>Guide</h1>\n"
            '<!-- Source: NXT-1234 AC: "verbatim text" -->\n'
            "<p>Body paragraph.</p>\n"
            '<!-- Source: NXT-5678 RN: "release note" -->\n'
        )
        html_file = tmp_path / f"{rid}.html"
        html_file.write_text(html_with_citations, encoding="utf-8")
        meta_file = tmp_path / f"{rid}-meta.json"
        meta_file.write_text(json.dumps({"id": rid, "approved": True}), encoding="utf-8")

        mini = FastAPI()
        mini.add_api_route("/resources/{rid}/html", demo_app.resource_html, methods=["GET"])

        with (
            patch.object(demo_app.prod, "_resolve_resource", lambda r: (html_file, meta_file, "approved") if r == rid else None),
            patch.object(demo_app.prod, "_read_meta", lambda p: {"id": rid, "approved": True}),
            patch.object(demo_app, "CONFERENCE_MODE", True),
        ):
            client = TestClient(mini, raise_server_exceptions=True)
            resp = client.get(f"/resources/{rid}/html")

        assert resp.status_code == 200
        assert "<!-- Source:" not in resp.text, (
            "SHOULD-NOT-OCCUR: citation comment found in /html response — "
            "_strip_source_comments() must be applied before serving to learners.\n"
            f"Response snippet: {resp.text[:400]!r}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# TC-D1-05: GET /api/tracks/{tid} for a legacy flat track synthesises courses
#            with _implicit: true
# ─────────────────────────────────────────────────────────────────────────────

class TestA1CourseShim:
    """Legacy flat tracks (module_ids only, no course_ids) get an implicit courses array."""

    def test_flat_track_gets_implicit_courses(self, tmp_path):
        """GET /api/tracks/{tid} on a flat-track (module_ids only) returns a courses
        array with a single course whose _implicit key is True.
        """
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        import demo_app
        import modules_store as ms

        tracks_dir = tmp_path / "tracks"
        tracks_dir.mkdir(parents=True, exist_ok=True)
        flat_track = {
            "id": TRACK_ID,
            "title": "Flat Legacy Track",
            "module_ids": ["GUIDE-001", "GUIDE-002"],
            "status": "published",
            # Crucially: NO course_ids key.
        }
        (tracks_dir / f"{TRACK_ID}.json").write_text(
            json.dumps(flat_track), encoding="utf-8"
        )

        fake_user = MagicMock()
        fake_user.id = USER_ID

        mini = FastAPI()
        mini.add_api_route("/api/tracks/{tid}", demo_app.api_get_track, methods=["GET"])
        from demo_app import get_current_user
        mini.dependency_overrides[get_current_user] = lambda: fake_user

        with (
            patch.object(ms, "TRACKS_DIR", tracks_dir),
            patch.object(demo_app, "_ms", ms),
            patch.object(demo_app, "_cs", __import__("completion_store")),
            patch.object(demo_app, "_ICN_DIR", None),
        ):
            client = TestClient(mini, raise_server_exceptions=True)
            resp = client.get(
                f"/api/tracks/{TRACK_ID}",
                headers={"X-Demo-User": USER_ID},
            )

        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert "courses" in data, "Response must contain a 'courses' key"
        assert len(data["courses"]) >= 1, "At least one course must be synthesised"
        first_course = data["courses"][0]
        assert first_course.get("_implicit") is True, (
            f"Expected _implicit: true on synthesised course, got: {first_course}"
        )

    def test_flat_track_implicit_lessons_match_module_ids(self, tmp_path):
        """The synthesised course's lessons should correspond to the track's module_ids."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        import demo_app
        import modules_store as ms

        module_ids = ["GUIDE-AAA", "GUIDE-BBB"]
        tracks_dir = tmp_path / "tracks"
        tracks_dir.mkdir(parents=True, exist_ok=True)
        (tracks_dir / f"{TRACK_ID}.json").write_text(
            json.dumps({"id": TRACK_ID, "title": "T", "module_ids": module_ids, "status": "published"}),
            encoding="utf-8",
        )

        fake_user = MagicMock()
        fake_user.id = USER_ID

        mini = FastAPI()
        mini.add_api_route("/api/tracks/{tid}", demo_app.api_get_track, methods=["GET"])
        from demo_app import get_current_user
        mini.dependency_overrides[get_current_user] = lambda: fake_user

        with (
            patch.object(ms, "TRACKS_DIR", tracks_dir),
            patch.object(demo_app, "_ms", ms),
            patch.object(demo_app, "_cs", __import__("completion_store")),
            patch.object(demo_app, "_ICN_DIR", None),
        ):
            client = TestClient(mini, raise_server_exceptions=True)
            resp = client.get(f"/api/tracks/{TRACK_ID}", headers={"X-Demo-User": USER_ID})

        assert resp.status_code == 200
        lessons = resp.json()["courses"][0]["lessons"]
        lesson_refs = [l.get("ref") for l in lessons]
        assert lesson_refs == module_ids, (
            f"Synthesised lesson refs {lesson_refs} should match module_ids {module_ids}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# TC-D1-06: Lesson-level progress survives a simulated server restart
# ─────────────────────────────────────────────────────────────────────────────

class TestLessonProgressDiskPersistence:
    """Lesson completion records written by set_lesson_done() survive a reload
    (simulating a server restart — read fresh from disk, no in-memory state)."""

    def test_progress_readable_after_cold_read(self, isolated_completion_store):
        """Write a lesson done, then read it back via get_lesson_done() with a
        fresh import — simulates a server restart reading from disk."""
        import completion_store as cs

        cs.set_lesson_done(USER_ID, TRACK_ID, COURSE_ID, LESSON_REF)

        # Verify the JSON file exists on disk at the expected path.
        safe_uid = cs._safe_id(USER_ID)
        safe_tid = cs._safe_id(TRACK_ID)
        disk_path = isolated_completion_store / safe_uid / f"{safe_tid}.json"
        assert disk_path.exists(), f"Progress file not written at {disk_path}"

        raw = json.loads(disk_path.read_text(encoding="utf-8"))
        assert "lessons_done" in raw, "lessons_done key must be present on disk"
        assert LESSON_REF in raw["lessons_done"].get(COURSE_ID, []), (
            f"{LESSON_REF!r} not found in on-disk lessons_done[{COURSE_ID!r}]"
        )

        # Re-read via get_lesson_done (does NOT use in-memory state).
        result = cs.get_lesson_done(USER_ID, TRACK_ID, COURSE_ID, LESSON_REF)
        assert result is True, "get_lesson_done() should return True after cold read"

    def test_module_done_coexists_with_lesson_done(self, isolated_completion_store):
        """set_lesson_done() must not clobber existing modules_done data."""
        import completion_store as cs

        # Write module-level progress first.
        cs.set_module_done(USER_ID, TRACK_ID, "MODULE-001",
                           module_ids=["MODULE-001", "MODULE-002"])

        # Now mark a lesson done.
        cs.set_lesson_done(USER_ID, TRACK_ID, COURSE_ID, LESSON_REF)

        # Both must coexist.
        progress = cs.get_progress(USER_ID, TRACK_ID, module_ids=["MODULE-001", "MODULE-002"])
        assert "MODULE-001" in progress["modules_done"], "module-level progress must survive lesson write"
        assert cs.get_lesson_done(USER_ID, TRACK_ID, COURSE_ID, LESSON_REF), "lesson done must also be set"

    def test_multiple_courses_persist_independently(self):
        """Lesson completion across different courses is tracked independently."""
        import completion_store as cs

        course_a, course_b = "course-aaa", "course-bbb"
        ref_a, ref_b = "lesson-a1", "lesson-b1"

        cs.set_lesson_done(USER_ID, TRACK_ID, course_a, ref_a)
        cs.set_lesson_done(USER_ID, TRACK_ID, course_b, ref_b)

        assert cs.get_lesson_done(USER_ID, TRACK_ID, course_a, ref_a)
        assert cs.get_lesson_done(USER_ID, TRACK_ID, course_b, ref_b)
        # Cross-check: lesson_a not in course_b and vice-versa.
        assert not cs.get_lesson_done(USER_ID, TRACK_ID, course_b, ref_a)
        assert not cs.get_lesson_done(USER_ID, TRACK_ID, course_a, ref_b)
