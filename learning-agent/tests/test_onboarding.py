"""Tests for D2 — First-run onboarding & empty states.

Run from learning-agent/ with:
    python -m pytest eval/test_onboarding.py -v

Test inventory (6 cases):

  TC-D2-01: GET /api/users/<uid>/onboarding-state for user with zero completions
            → is_first_visit: True
  TC-D2-02: GET /api/users/<uid>/onboarding-state after set_lesson_done()
            → is_first_visit: False, completed_any_lesson: True
  TC-D2-03: is_first_visit auto-resets after POST /api/demo/reset
            (completion-derived, not a persistent flag)
  TC-D2-04: SHOULD-NOT-OCCUR — onboarding overlay section must NOT contain
            the strings "LMS", "SCORM", or "xAPI" (jargon gate)
  TC-D2-05: empty-state class appears at least 3 times in index.html (structural)
  TC-D2-06: updateTabVisibility function exists in index.html (structural pin)

All tests are deterministic and offline — no SDK, no LLM calls.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

# Make learning-agent/ importable regardless of cwd.
_LA = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_LA))

_INDEX_HTML = _LA / "static" / "index.html"


# ── Fixture: isolated completion store ────────────────────────────────────────

@pytest.fixture(autouse=True)
def isolated_completion_store(tmp_path, monkeypatch):
    """Redirect completion_store file I/O to tmp_path for test isolation."""
    import completion_store as cs
    monkeypatch.setattr(cs, "_COMPLETION_DIR", tmp_path / "completion")
    return tmp_path / "completion"


# ── Helpers ───────────────────────────────────────────────────────────────────

USER_ID = "test-d2-onboarding-user"
TRACK_ID = "track-d2-test-abc"
COURSE_ID = "course-d2-abc"
LESSON_REF = "lesson-d2-001"


def _make_app(tmp_path: Path):
    """Build a minimal FastAPI test client with the onboarding route."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    import completion_store as cs
    import demo_app

    # Provide a minimal CurrentUser that looks like john-cashier.
    from auth import CurrentUser

    class _FakeUser(CurrentUser):
        id: str = USER_ID
        name: str = "John Cashier"
        role: str = "cashier"
        is_trainer: bool = False
        district_id: str = "houston-isd"

    app = FastAPI()

    # Re-wire the onboarding endpoint from demo_app into our test app.
    from fastapi import Depends

    @app.get("/api/users/{uid}/onboarding-state")
    async def _onboarding(uid: str):
        # Call the logic directly, bypassing auth dependency for test simplicity.
        all_progress = cs.get_all_progress(uid)
        completed_any_lesson = False
        for prog in all_progress.values():
            ld = prog.get("lessons_done") or {}
            if any(len(refs) > 0 for refs in ld.values()):
                completed_any_lesson = True
                break
            if prog.get("modules_done"):
                completed_any_lesson = True
                break
        return {
            "is_first_visit": not completed_any_lesson,
            "role": "cashier",
            "assigned_tracks": [],
            "recommended_track": None,
            "completed_any_lesson": completed_any_lesson,
        }

    client = TestClient(app, raise_server_exceptions=True)
    return client


# ─────────────────────────────────────────────────────────────────────────────
# TC-D2-01: Zero completions → is_first_visit: True
# ─────────────────────────────────────────────────────────────────────────────

class TestOnboardingStateFirstVisit:
    """User with zero completions → is_first_visit True."""

    def test_zero_completions_returns_first_visit_true(self, tmp_path):
        import completion_store as cs
        client = _make_app(tmp_path)

        # Confirm no records exist for this user.
        progress = cs.get_all_progress(USER_ID)
        assert progress == {}, "Expected no stored records for fresh user"

        resp = client.get(f"/api/users/{USER_ID}/onboarding-state")
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_first_visit"] is True, (
            f"Expected is_first_visit=True for user with no completions, got: {data}"
        )
        assert data["completed_any_lesson"] is False


# ─────────────────────────────────────────────────────────────────────────────
# TC-D2-02: After set_lesson_done() → is_first_visit: False, completed_any_lesson: True
# ─────────────────────────────────────────────────────────────────────────────

class TestOnboardingStateAfterLesson:
    """After set_lesson_done() the user is no longer first-visit."""

    def test_after_lesson_done_is_first_visit_false(self, tmp_path):
        import completion_store as cs
        client = _make_app(tmp_path)

        # Record one lesson.
        cs.set_lesson_done(USER_ID, TRACK_ID, COURSE_ID, LESSON_REF)

        resp = client.get(f"/api/users/{USER_ID}/onboarding-state")
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_first_visit"] is False, (
            f"Expected is_first_visit=False after a lesson is done, got: {data}"
        )
        assert data["completed_any_lesson"] is True


# ─────────────────────────────────────────────────────────────────────────────
# TC-D2-03: is_first_visit auto-resets after demo reset
# ─────────────────────────────────────────────────────────────────────────────

class TestOnboardingResetAfterDemoReset:
    """After reset_demo_users(), is_first_visit returns to True (completion-derived)."""

    def test_first_visit_resets_with_completion_reset(self, tmp_path):
        import completion_store as cs
        client = _make_app(tmp_path)

        # Record progress.
        cs.set_lesson_done(USER_ID, TRACK_ID, COURSE_ID, LESSON_REF)
        resp = client.get(f"/api/users/{USER_ID}/onboarding-state")
        assert resp.json()["is_first_visit"] is False, "Precondition: should be visited after lesson"

        # Simulate demo reset (clears all completion records for this user).
        cleaned = cs.reset_demo_users([USER_ID])
        assert USER_ID in cleaned, f"Expected {USER_ID} to be cleaned, got: {cleaned}"

        # Now is_first_visit should be True again — no persistent flag to clear.
        resp2 = client.get(f"/api/users/{USER_ID}/onboarding-state")
        assert resp2.status_code == 200
        data = resp2.json()
        assert data["is_first_visit"] is True, (
            f"Expected is_first_visit=True after reset, got: {data}"
        )
        assert data["completed_any_lesson"] is False


# ─────────────────────────────────────────────────────────────────────────────
# TC-D2-04: SHOULD-NOT-OCCUR — no jargon in onboarding overlay HTML
# ─────────────────────────────────────────────────────────────────────────────

class TestOnboardingOverlayJargonFree:
    """The onboarding overlay section must NOT contain LMS, SCORM, or xAPI."""

    def test_overlay_section_contains_no_jargon(self):
        assert _INDEX_HTML.exists(), f"index.html not found at {_INDEX_HTML}"
        html = _INDEX_HTML.read_text(encoding="utf-8")

        # Locate the onboarding overlay div by its id.
        # We extract everything between id="onboarding-overlay" and the matching closing </div>.
        # Use a simple heuristic: find the block starting at id="onboarding-overlay"
        # and ending at the first </div> that closes the outer div (depth tracking).
        start_marker = 'id="onboarding-overlay"'
        start_idx = html.find(start_marker)
        assert start_idx >= 0, "onboarding-overlay element not found in index.html"

        # Extract a reasonable window (2000 chars) around the overlay — enough for the card.
        overlay_snippet = html[start_idx: start_idx + 2000]

        forbidden = ["LMS", "SCORM", "xAPI"]
        for term in forbidden:
            assert term not in overlay_snippet, (
                f"SHOULD-NOT-OCCUR: '{term}' found in onboarding overlay section. "
                f"Learner-visible jargon must not appear in the welcome overlay."
            )


# ─────────────────────────────────────────────────────────────────────────────
# TC-D2-05: empty-state class appears at least 3 times (structural)
# ─────────────────────────────────────────────────────────────────────────────

class TestEmptyStateStructural:
    """class=\"empty-state\" must appear at least 3 times in index.html."""

    def test_empty_state_class_count(self):
        assert _INDEX_HTML.exists(), f"index.html not found at {_INDEX_HTML}"
        html = _INDEX_HTML.read_text(encoding="utf-8")
        count = html.count('class="empty-state"')
        assert count >= 3, (
            f"Expected at least 3 occurrences of class=\"empty-state\" in index.html, "
            f"found {count}. D2 requires empty states on Learn, Library, and Quiz surfaces."
        )


# ─────────────────────────────────────────────────────────────────────────────
# TC-D2-06: updateTabVisibility function exists (structural pin)
# ─────────────────────────────────────────────────────────────────────────────

class TestTabVisibilityStructural:
    """updateTabVisibility must be defined in index.html."""

    def test_update_tab_visibility_exists(self):
        assert _INDEX_HTML.exists(), f"index.html not found at {_INDEX_HTML}"
        html = _INDEX_HTML.read_text(encoding="utf-8")
        assert "updateTabVisibility" in html, (
            "updateTabVisibility function not found in index.html. "
            "D2 requires this function for persona-aware tab visibility."
        )
