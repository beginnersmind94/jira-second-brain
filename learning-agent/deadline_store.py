"""deadline_store.py — Regulatory compliance calendar for OPS-3.

Storage:
    data/regulatory-dates.json — list of deadline records

Each deadline record:
    {id, title, date (YYYY-MM-DD), module, scope, notes, created_at}

scope: "federal" | "state" | "district"
"""
from __future__ import annotations

import json
import re
import time
import uuid
from pathlib import Path

_DATA_DIR     = Path(__file__).resolve().parent / "data"
_DEADLINES_FILE = _DATA_DIR / "regulatory-dates.json"

_DATE_RE  = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_VALID_SCOPE = {"federal", "state", "district"}


# ── I/O ───────────────────────────────────────────────────────────────────────

def _read() -> list[dict]:
    if not _DEADLINES_FILE.exists():
        return []
    try:
        return json.loads(_DEADLINES_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _write(deadlines: list[dict]) -> None:
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    _DEADLINES_FILE.write_text(
        json.dumps(deadlines, indent=2, ensure_ascii=False), encoding="utf-8"
    )


# ── Public API ────────────────────────────────────────────────────────────────

def add_deadline(
    title: str,
    date: str,
    module: str = "",
    scope: str = "federal",
    notes: str = "",
) -> dict:
    """Add a regulatory deadline.

    Raises ValueError for empty title, invalid date format, or unknown scope.
    """
    title = title.strip()
    if not title:
        raise ValueError("title must not be empty")
    if not _DATE_RE.match(date):
        raise ValueError(f"date must be YYYY-MM-DD, got {date!r}")
    if scope not in _VALID_SCOPE:
        raise ValueError(f"scope must be one of {_VALID_SCOPE}")

    rec: dict = {
        "id":         str(uuid.uuid4()),
        "title":      title,
        "date":       date,
        "module":     module,
        "scope":      scope,
        "notes":      notes,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    deadlines = _read()
    deadlines.append(rec)
    _write(deadlines)
    return rec


def get_deadlines(upcoming_only: bool = False, today: str | None = None) -> list[dict]:
    """Return deadlines sorted by date ascending.

    upcoming_only: if True, exclude deadlines whose date < today.
    today: override today's date (YYYY-MM-DD) for testing.
    """
    today = today or time.strftime("%Y-%m-%d")
    deadlines = _read()
    if upcoming_only:
        deadlines = [d for d in deadlines if d.get("date", "") >= today]
    return sorted(deadlines, key=lambda d: d.get("date", ""))


def delete_deadline(deadline_id: str) -> bool:
    """Remove a deadline by id. Returns True if found and removed."""
    deadlines = _read()
    before = len(deadlines)
    deadlines = [d for d in deadlines if d.get("id") != deadline_id]
    if len(deadlines) == before:
        return False
    _write(deadlines)
    return True


def days_until(date: str, today: str | None = None) -> int:
    """Return number of calendar days from today to date (negative if past)."""
    from datetime import date as _date
    today_str = today or time.strftime("%Y-%m-%d")
    y0, m0, d0 = map(int, today_str.split("-"))
    y1, m1, d1 = map(int, date.split("-"))
    return (_date(y1, m1, d1) - _date(y0, m0, d0)).days
