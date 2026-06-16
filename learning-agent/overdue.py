"""overdue.py — ONE definition of "overdue" for the whole product (Epic: real-overdue, STORY-001).

Replaces three inconsistent notions that exist today:
  - the trainer UI's status-string match (`status === 'Overdue'`),
  - the compliance report's "In Progress with <20% complete" proxy,
  - the learner roster's per-track date check.

A learner is overdue when they have NOT completed an assignment whose due date has passed —
evaluated at end-of-day (23:59:59) of the due date in the district's timezone.

Pure + defensive: never raises (a bad date or missing tzdata falls back to a naive date
compare), so it is safe to call from request handlers.
"""
from __future__ import annotations

from datetime import datetime, date, time

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover - very old runtimes
    ZoneInfo = None

DEFAULT_TZ = "America/Chicago"


def _zone(tz: str):
    if ZoneInfo is None:
        return None
    for candidate in (tz or DEFAULT_TZ, DEFAULT_TZ):
        try:
            return ZoneInfo(candidate)
        except Exception:
            continue
    return None


def _parse_date(s) -> date | None:
    try:
        parts = str(s).split("-")
        return date(int(parts[0]), int(parts[1]), int(parts[2]))
    except Exception:
        return None


def is_overdue(completed: bool, due_date, now: datetime | None = None, tz: str = DEFAULT_TZ) -> bool:
    """True iff the work is not complete AND the due date has passed.

    completed            -> never overdue.
    due_date None/blank  -> never overdue (no deadline set).
    else                 -> overdue when `now` is past end-of-day of due_date in `tz`.
    Falls back to a naive date comparison when timezone data is unavailable.
    """
    if completed:
        return False
    due = _parse_date(due_date)
    if due is None:
        return False
    zone = _zone(tz)
    if zone is not None:
        now = now.astimezone(zone) if now is not None else datetime.now(zone)
        return now > datetime.combine(due, time(23, 59, 59), tzinfo=zone)
    now_date = (now or datetime.now()).date()
    return now_date > due
