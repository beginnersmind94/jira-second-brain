"""Tests for overdue.is_overdue (Epic: real-overdue, STORY-001).

Deterministic: every case passes an explicit tz-aware `now`, so results don't depend on the
wall clock or on tzdata being present (the tz and naive-fallback paths agree on these cases).
"""
from datetime import datetime, timezone

from overdue import is_overdue

UTC = timezone.utc


def test_completed_is_never_overdue():
    assert is_overdue(True, "2026-06-30", now=datetime(2026, 7, 15, 12, tzinfo=UTC)) is False


def test_no_due_date_is_never_overdue():
    assert is_overdue(False, None, now=datetime(2026, 7, 15, 12, tzinfo=UTC)) is False
    assert is_overdue(False, "", now=datetime(2026, 7, 15, 12, tzinfo=UTC)) is False


def test_past_deadline_not_complete_is_overdue():
    assert is_overdue(False, "2026-06-30", now=datetime(2026, 7, 15, 12, tzinfo=UTC)) is True


def test_future_deadline_is_not_overdue():
    assert is_overdue(False, "2026-12-31", now=datetime(2026, 6, 15, 12, tzinfo=UTC)) is False


def test_same_day_before_end_of_day_is_not_overdue():
    # Noon UTC on the due date = ~07:00 in America/Chicago, before end-of-day → not overdue.
    assert is_overdue(False, "2026-06-30", now=datetime(2026, 6, 30, 12, tzinfo=UTC)) is False


def test_day_after_deadline_is_overdue():
    assert is_overdue(False, "2026-06-30", now=datetime(2026, 7, 1, 12, tzinfo=UTC)) is True


def test_garbage_date_never_crashes():
    assert is_overdue(False, "not-a-date", now=datetime(2026, 7, 15, 12, tzinfo=UTC)) is False
