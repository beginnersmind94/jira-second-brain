"""nudge_store.py — Disk-backed nudge records per track.

Nudge records are stored under:
    data/nudges/<track_id>.json

Schema:
    {
      "track_id": "track-cashier-onboard",
      "nudges": [
        {"user_id": "john-cashier", "nudged_at": "2026-06-13T10:00:00+00:00", "nudged_by": "dana-director"}
      ]
    }

Rules:
- A nudge record represents intent to send a reminder; actual delivery is simulated.
  Do NOT claim SMS/email integration exists.
- One record per (user_id, track_id) since last completion — adding a duplicate
  user_id is idempotent (updates the timestamp, does not create a second entry).
- reset_demo_nudges() clears nudge files for demo users (called from demo reset).

Thread safety: same note as completion_store.py — single-process demo; GIL
sufficient for these small files.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

_BASE = Path(__file__).resolve().parent
_NUDGE_DIR = _BASE / "data" / "nudges"


def _safe_id(s: str) -> str:
    return re.sub(r"[^\w\-]", "_", s)[:80]


def _nudge_path(track_id: str) -> Path:
    return _NUDGE_DIR / f"{_safe_id(track_id)}.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


# ── Public API ────────────────────────────────────────────────────────────────


def get_nudges(track_id: str) -> list[dict]:
    """Return all nudge records for a track (empty list if none).

    Each entry: {user_id, nudged_at, nudged_by}
    """
    path = _nudge_path(track_id)
    data = _read_json(path)
    if data is None:
        return []
    return list(data.get("nudges") or [])


def add_nudge(track_id: str, user_id: str, nudged_by: str) -> dict:
    """Record a nudge for (track_id, user_id). Idempotent — updates timestamp.

    Returns the nudge entry: {user_id, nudged_at, nudged_by}
    """
    path = _nudge_path(track_id)
    data = _read_json(path) or {"track_id": track_id, "nudges": []}
    nudges: list[dict] = list(data.get("nudges") or [])

    now = _now_iso()
    for entry in nudges:
        if entry.get("user_id") == user_id:
            entry["nudged_at"] = now
            entry["nudged_by"] = nudged_by
            _write_json(path, {**data, "nudges": nudges})
            return dict(entry)

    new_entry = {"user_id": user_id, "nudged_at": now, "nudged_by": nudged_by}
    nudges.append(new_entry)
    _write_json(path, {**data, "nudges": nudges})
    return dict(new_entry)


def add_nudges_batch(track_id: str, user_ids: list[str], nudged_by: str) -> list[dict]:
    """Record nudges for multiple users. Idempotent per user_id.

    Returns list of nudge entries added/updated.
    """
    return [add_nudge(track_id, uid, nudged_by) for uid in user_ids]


def get_nudge_state(track_id: str, user_id: str) -> dict | None:
    """Return the nudge entry for (track_id, user_id), or None if not nudged."""
    for entry in get_nudges(track_id):
        if entry.get("user_id") == user_id:
            return entry
    return None


def clear_nudge(track_id: str, user_id: str) -> None:
    """Remove a nudge record for a user (e.g. after they complete the track).

    No-op if no record exists.
    """
    path = _nudge_path(track_id)
    data = _read_json(path)
    if data is None:
        return
    nudges = [e for e in (data.get("nudges") or []) if e.get("user_id") != user_id]
    _write_json(path, {**data, "nudges": nudges})


def reset_demo_nudges(demo_user_ids: list[str]) -> int:
    """Remove nudge entries for the given demo user ids across all track files.

    Called from POST /api/demo/reset to restore a pristine demo state.
    Returns the number of entries removed.
    """
    if not _NUDGE_DIR.exists():
        return 0
    uid_set = set(demo_user_ids)
    removed = 0
    for path in _NUDGE_DIR.glob("*.json"):
        data = _read_json(path)
        if data is None:
            continue
        before = data.get("nudges") or []
        after = [e for e in before if e.get("user_id") not in uid_set]
        removed += len(before) - len(after)
        if len(after) != len(before):
            _write_json(path, {**data, "nudges": after})
    return removed
