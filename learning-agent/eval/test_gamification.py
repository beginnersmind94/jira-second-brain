"""eval/test_gamification.py — D3 Gamification test suite (6 tests).

Tests:
  1. add_xp() accumulates correctly; persists and survives reload
  2. update_streak() — consecutive days advance; missing a day resets to 1
     SHOULD-NOT-OCCUR: gap must not maintain streak
  3. award_badge() is idempotent — calling twice for same badge_id awards only once
  4. check_and_award_badges() awards "First Lesson" on first lesson completion
  5. reset_demo_users() clears gamification data
     SHOULD-NOT-OCCUR: post-reset XP must be 0
  6. GET /api/users/{uid}/gamification returns correct values after a lesson completion

Run: python -m pytest learning-agent/eval/test_gamification.py -v
  OR from learning-agent/: python -m pytest eval/test_gamification.py -v
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

# ── Path bootstrap ────────────────────────────────────────────────────────────
# Allow running from the repo root OR from learning-agent/.
_HERE = Path(__file__).resolve().parent
_LA = _HERE.parent  # learning-agent/
if str(_LA) not in sys.path:
    sys.path.insert(0, str(_LA))

import completion_store as cs  # noqa: E402  (import after path setup)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def isolated_gamif_dir(tmp_path, monkeypatch):
    """Redirect _GAMIFICATION_DIR and _COMPLETION_DIR to a temp directory so
    tests never touch real data/ files and are fully isolated from each other."""
    gamif_dir = tmp_path / "gamification"
    gamif_dir.mkdir()
    comp_dir = tmp_path / "completion"
    comp_dir.mkdir()
    monkeypatch.setattr(cs, "_GAMIFICATION_DIR", gamif_dir)
    monkeypatch.setattr(cs, "_COMPLETION_DIR", comp_dir)
    yield


TEST_UID = "test-learner-001"


# ── Test 1: add_xp accumulates and persists ───────────────────────────────────

def test_add_xp_accumulates_and_persists():
    """add_xp() adds XP; the total persists and survives a simulated reload."""
    # Start from zero.
    total = cs.add_xp(TEST_UID, 10, reason="lesson")
    assert total == 10, f"Expected 10 XP, got {total}"

    total = cs.add_xp(TEST_UID, 20, reason="quiz")
    assert total == 30, f"Expected 30 XP after quiz, got {total}"

    total = cs.add_xp(TEST_UID, 50, reason="assessment")
    assert total == 80, f"Expected 80 XP after assessment, got {total}"

    # Simulate reload: read the JSON directly and check it matches.
    path = cs._gamif_path(TEST_UID)
    assert path.exists(), "Gamification file should exist after add_xp"
    raw = json.loads(path.read_text(encoding="utf-8"))
    assert raw["xp"] == 80, f"Persisted XP should be 80, got {raw['xp']}"

    # get_gamification() reads from disk — confirms reload survives.
    state = cs.get_gamification(TEST_UID)
    assert state["xp"] == 80, f"get_gamification XP should be 80, got {state['xp']}"


# ── Test 2: update_streak consecutive/missing day logic ──────────────────────

def test_update_streak_consecutive_and_reset():
    """Consecutive days advance the streak; a missing day resets it to 1.

    SHOULD-NOT-OCCUR assertion: a day gap must NOT maintain the streak.
    """
    # Day 1.
    streak = cs.update_streak(TEST_UID, "2026-06-10")
    assert streak == 1, f"First day streak should be 1, got {streak}"

    # Day 2 — consecutive → advance.
    streak = cs.update_streak(TEST_UID, "2026-06-11")
    assert streak == 2, f"Second consecutive day should give streak 2, got {streak}"

    # Day 3 — consecutive → advance.
    streak = cs.update_streak(TEST_UID, "2026-06-12")
    assert streak == 3, f"Third consecutive day should give streak 3, got {streak}"

    # Same day again — idempotent, no change.
    streak = cs.update_streak(TEST_UID, "2026-06-12")
    assert streak == 3, f"Same day repeat should keep streak 3, got {streak}"

    # SHOULD-NOT-OCCUR: skip a day — must reset to 1, not maintain 3 or increment.
    streak = cs.update_streak(TEST_UID, "2026-06-14")  # gap: Jun 12 → Jun 14
    assert streak == 1, (
        f"SHOULD-NOT-OCCUR: day gap must reset streak to 1, but got {streak}. "
        "A gap must never maintain or advance the streak."
    )


# ── Test 3: award_badge idempotency ──────────────────────────────────────────

def test_award_badge_idempotent():
    """award_badge() is idempotent — calling twice for same badge_id awards only once."""
    first = cs.award_badge(TEST_UID, "first-lesson", "First Lesson")
    assert first is True, "First award_badge call should return True (newly awarded)"

    second = cs.award_badge(TEST_UID, "first-lesson", "First Lesson")
    assert second is False, "Second award_badge call for same id should return False"

    # Only one badge in the store.
    state = cs.get_gamification(TEST_UID)
    badges = state["badges"]
    assert len(badges) == 1, f"Should have exactly 1 badge, got {len(badges)}"
    assert badges[0]["id"] == "first-lesson"

    # Calling with different id — does award.
    cs.award_badge(TEST_UID, "on-a-roll", "On a Roll")
    state = cs.get_gamification(TEST_UID)
    assert len(state["badges"]) == 2, "Second distinct badge should be awarded"


# ── Test 4: check_and_award_badges gives "First Lesson" on first completion ──

def test_check_and_award_badges_first_lesson():
    """check_and_award_badges() awards 'First Lesson' badge on first lesson completion."""
    # Seed one lesson as done so get_all_progress() reflects it.
    cs.set_lesson_done(TEST_UID, "track-001", "course-001", "lesson-001")

    newly = cs.check_and_award_badges(TEST_UID, "lesson", context={"streak": 1})

    badge_ids = [b["id"] for b in newly]
    assert "first-lesson" in badge_ids, (
        f"'First Lesson' badge should be awarded on first lesson completion. "
        f"Got newly_awarded={newly}"
    )

    # Idempotency: second lesson completion should NOT re-award First Lesson.
    cs.set_lesson_done(TEST_UID, "track-001", "course-001", "lesson-002")
    newly2 = cs.check_and_award_badges(TEST_UID, "lesson", context={"streak": 1})
    badge_ids2 = [b["id"] for b in newly2]
    assert "first-lesson" not in badge_ids2, (
        "'First Lesson' must not be awarded a second time"
    )


# ── Test 5: reset_demo_users clears gamification ─────────────────────────────

def test_reset_demo_users_clears_gamification():
    """reset_demo_users() deletes gamification files.

    SHOULD-NOT-OCCUR assertion: post-reset XP must be 0.
    """
    # Set up XP and a badge.
    cs.add_xp(TEST_UID, 30, reason="lesson")
    cs.award_badge(TEST_UID, "first-lesson", "First Lesson")

    state_before = cs.get_gamification(TEST_UID)
    assert state_before["xp"] == 30, "Pre-reset XP should be 30"
    assert len(state_before["badges"]) == 1, "Pre-reset should have 1 badge"

    # Reset.
    cleaned = cs.reset_demo_users([TEST_UID])
    # Note: reset_demo_users deletes the completion dir; gamif file is separate.
    # Gamif file deletion is triggered even if completion dir doesn't exist.

    # SHOULD-NOT-OCCUR: XP after reset must be 0.
    state_after = cs.get_gamification(TEST_UID)
    assert state_after["xp"] == 0, (
        f"SHOULD-NOT-OCCUR: post-reset XP must be 0, got {state_after['xp']}. "
        "reset_demo_users() must delete the gamification file."
    )
    assert len(state_after["badges"]) == 0, (
        f"Post-reset badges must be empty, got {state_after['badges']}"
    )
    assert state_after["streak"] == 0, (
        f"Post-reset streak must be 0, got {state_after['streak']}"
    )


# ── Test 6: GET /api/users/{uid}/gamification integration ────────────────────

def test_gamification_endpoint_after_lesson(monkeypatch):
    """GET /api/users/{uid}/gamification returns correct values after a lesson completion.

    Tests the full server-side path: set_lesson_done → add_xp → update_streak
    → check_and_award_badges → get_gamification.

    This test does NOT spin up the FastAPI server; it calls the store functions
    directly in the same sequence the endpoint handler calls them, then verifies
    get_gamification() returns the expected payload shape and values.
    """
    from datetime import date
    today = date.today().isoformat()

    # Simulate what the /api/tracks/{tid}/lesson-progress handler does.
    already_done = cs.get_lesson_done(TEST_UID, "track-x", "course-x", "lesson-x")
    assert already_done is False, "Lesson should not be done yet"

    cs.set_lesson_done(TEST_UID, "track-x", "course-x", "lesson-x")

    # Gamification hook sequence (mirrors demo_app.py).
    new_xp = cs.add_xp(TEST_UID, 10, reason="lesson")
    streak = cs.update_streak(TEST_UID, today)
    newly = cs.check_and_award_badges(TEST_UID, "lesson", context={"streak": streak})

    # get_gamification() — what the endpoint returns.
    state = cs.get_gamification(TEST_UID)

    # Shape assertions.
    assert "xp" in state, "Response must include 'xp'"
    assert "streak" in state, "Response must include 'streak'"
    assert "badges" in state, "Response must include 'badges'"
    assert "level" in state, "Response must include 'level'"

    # Value assertions.
    assert state["xp"] == 10, f"XP should be 10 after one lesson, got {state['xp']}"
    assert state["streak"] >= 1, f"Streak should be ≥1 after activity, got {state['streak']}"
    assert state["level"] >= 1, f"Level should be ≥1, got {state['level']}"

    # "First Lesson" badge should appear.
    badge_ids = [b["id"] for b in state["badges"]]
    assert "first-lesson" in badge_ids, (
        f"'First Lesson' badge must appear in gamification state after first lesson. "
        f"badges={state['badges']}"
    )

    # Level formula: xp // 100 + 1.
    expected_level = state["xp"] // 100 + 1
    assert state["level"] == expected_level, (
        f"Level formula broken: xp={state['xp']}, expected level {expected_level}, "
        f"got {state['level']}"
    )
