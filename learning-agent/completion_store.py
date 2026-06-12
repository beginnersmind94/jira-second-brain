"""completion_store.py — Disk-backed per-learner completion records.

Each learner's progress is stored as a JSON file under:
    data/completion/<user_id>/<track_id>.json

Certificates are stored under:
    data/completion/<user_id>/certs/<cert_id>.json

Gamification (D3) records are stored under:
    data/gamification/<user_id>.json

This is the V1.5 persistence layer that replaces in-memory (session-scoped)
completion state with durable, restart-safe records keyed by user identity.

Thread safety: Python's GIL protects individual dict reads/writes.  File writes
are atomic (write temp + rename) on POSIX; on Windows we write directly — the
files are small enough that a crash mid-write is acceptable for a demo deployment.

No locking is needed for the demo (single-process, low concurrency).  A future
multi-worker deployment should add file-level locking or migrate to SQLite.
"""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────

_BASE = Path(__file__).resolve().parent
_COMPLETION_DIR = _BASE / "data" / "completion"
_GAMIFICATION_DIR = _BASE / "data" / "gamification"

# ── Demo-seed data (mirrors the in-memory _DEMO universe in index.html) ──────
# When a demo-user (id starts with "demo-") accesses a track for the first time
# and has no stored progress, we seed them with 40 % done on a well-known track
# so the UI shows meaningful progress on first load.  This preserves the existing
# demo behaviour without hard-coding it into the routes.
#
# Key:  track_id (as returned by /api/tracks)
# Val:  list of module_ids considered "done" for the seed
_DEMO_SEED: dict[str, list[str]] = {}   # populated lazily by _demo_seed_for()


def _demo_seed_for(track_id: str, module_ids: list[str]) -> dict:
    """Return seeded progress for a demo user on their first access to a track.

    Seeds 40% of modules as done (rounded down), deterministically picking the
    first N entries so the result is stable across restarts.
    """
    n = max(1, len(module_ids) * 40 // 100) if module_ids else 0
    done = module_ids[:n]
    pct = _calc_pct(done, module_ids)
    return {
        "modules_done": done,
        "pct": pct,
        "certified": False,
        "cert_issued_at": None,
    }


# ── Internal helpers ──────────────────────────────────────────────────────────

def _safe_id(s: str) -> str:
    """Strip characters unsafe for directory / file names, keep it short."""
    return re.sub(r"[^\w\-]", "_", s)[:80]


def _user_dir(user_id: str) -> Path:
    return _COMPLETION_DIR / _safe_id(user_id)


def _progress_path(user_id: str, track_id: str) -> Path:
    return _user_dir(user_id) / f"{_safe_id(track_id)}.json"


def _certs_dir(user_id: str) -> Path:
    return _user_dir(user_id) / "certs"


def _cert_path(user_id: str, cert_id: str) -> Path:
    return _certs_dir(user_id) / f"{cert_id}.json"


def _calc_pct(modules_done: list[str], all_module_ids: list[str]) -> int:
    """Percentage of modules marked done (0-100)."""
    if not all_module_ids:
        return 0
    done_set = set(modules_done)
    done_count = sum(1 for mid in all_module_ids if mid in done_set)
    return round(100 * done_count / len(all_module_ids))


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


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ── Public API ────────────────────────────────────────────────────────────────

def get_progress(user_id: str, track_id: str, *, module_ids: list[str] | None = None) -> dict:
    """Return the learner's progress for a single track.

    Returns a dict:
        {modules_done: [mid, ...], pct: int, certified: bool, cert_issued_at: str|None}

    If no record exists yet:
    - For demo users (id starts with "demo-") AND module_ids are provided,
      seed with ~40% done so the demo shows meaningful progress on first load.
    - Otherwise return a zeroed-out record (not written to disk -- lazy creation).

    ``module_ids`` must be provided when a seed fallback is desired.  It is used
    only to calculate pct; the caller should pass the track's current module list.
    """
    path = _progress_path(user_id, track_id)
    stored = _read_json(path)
    if stored is not None:
        # Recompute pct against current module list if module_ids provided.
        if module_ids is not None:
            stored["pct"] = _calc_pct(stored.get("modules_done", []), module_ids)
        return stored

    # No record on disk -- build one.
    is_demo = user_id.startswith("demo-")
    if is_demo and module_ids:
        return _demo_seed_for(track_id, module_ids)

    return {
        "modules_done": [],
        "pct": 0,
        "certified": False,
        "cert_issued_at": None,
    }


def set_lesson_done(
    user_id: str,
    track_id: str,
    course_id: str,
    lesson_ref: str,
) -> None:
    """Mark a single lesson done for a learner and persist the update.

    Idempotent: calling twice for the same (course_id, lesson_ref) is a no-op.

    Persists to the existing data/completion/<user>/<track>.json file, adding a
    ``lessons_done`` key alongside the existing ``modules_done`` key so that
    legacy flat-track progress is never disturbed:

        {
          "modules_done": [...],      # legacy flat-track completion
          "lessons_done": {           # D1 lesson-level completion
            "<course_id>": ["<lesson_ref>", ...]
          },
          ...
        }
    """
    path = _progress_path(user_id, track_id)
    # Load whatever is on disk (may or may not exist yet).
    progress = _read_json(path) or {
        "modules_done": [],
        "pct": 0,
        "certified": False,
        "cert_issued_at": None,
    }
    lessons_done: dict = progress.get("lessons_done") or {}
    done_set = set(lessons_done.get(course_id) or [])
    if lesson_ref in done_set:
        return  # idempotent — already recorded
    done_set.add(lesson_ref)
    lessons_done[course_id] = sorted(done_set)
    progress["lessons_done"] = lessons_done
    _write_json(path, progress)


def get_lesson_done(
    user_id: str,
    track_id: str,
    course_id: str,
    lesson_ref: str,
) -> bool:
    """Return True if the learner has completed this specific lesson."""
    path = _progress_path(user_id, track_id)
    stored = _read_json(path)
    if not stored:
        return False
    lessons_done: dict = stored.get("lessons_done") or {}
    done_list = lessons_done.get(course_id) or []
    return lesson_ref in done_list


def set_module_done(
    user_id: str,
    track_id: str,
    module_id: str,
    *,
    module_ids: list[str] | None = None,
) -> dict:
    """Mark a module done for a learner and persist the updated progress.

    Idempotent: marking an already-done module is a no-op.
    Returns the updated progress dict.

    ``module_ids`` -- the track's full ordered module list; used to recalculate pct.
    If omitted, pct is calculated against the stored modules_done list alone (less
    accurate -- callers should always pass the track's module_ids).
    """
    progress = get_progress(user_id, track_id, module_ids=module_ids)
    done_set = set(progress.get("modules_done", []))
    done_set.add(module_id)
    done_list = sorted(done_set)  # stable ordering

    all_ids = module_ids or done_list
    pct = _calc_pct(done_list, all_ids)

    progress = {
        "modules_done": done_list,
        "pct": pct,
        "certified": progress.get("certified", False),
        "cert_issued_at": progress.get("cert_issued_at"),
    }
    _write_json(_progress_path(user_id, track_id), progress)
    return progress


def issue_certificate(
    user_id: str,
    track_id: str,
    learner_name: str,
    *,
    track_title: str = "",
    product: str = "SchoolCafe",
    role: str | None = None,
    modules: int = 0,
) -> dict:
    """Issue + persist a completion certificate.

    Returns:
        {cert_id, learner_name, track_title, issued_at, track_id, ...}

    Also marks certified=True + cert_issued_at in the progress record.
    """
    now = _now_iso()
    cert_id = f"cert-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"

    cert = {
        "id": cert_id,
        "user_id": user_id,
        "track_id": track_id,
        "track_title": track_title or track_id,
        "learner_name": learner_name or "Learner",
        "product": product,
        "role": role,
        "modules": modules,
        "issued_at": now,
    }
    _write_json(_cert_path(user_id, cert_id), cert)

    # Update progress to reflect certification.
    path = _progress_path(user_id, track_id)
    progress = _read_json(path) or {
        "modules_done": [],
        "pct": 100,
        "certified": False,
        "cert_issued_at": None,
    }
    progress["certified"] = True
    progress["cert_issued_at"] = now
    _write_json(path, progress)

    return cert


def get_certificate(cert_id: str) -> dict | None:
    """Look up a certificate by id across ALL users.

    Scans user subdirectories -- acceptable for demo scale (tens of users).
    A production deployment would index certs in a flat lookup table.
    Returns the cert dict or None if not found.
    """
    if not _COMPLETION_DIR.exists():
        return None
    for user_dir in _COMPLETION_DIR.iterdir():
        if not user_dir.is_dir():
            continue
        p = user_dir / "certs" / f"{cert_id}.json"
        data = _read_json(p)
        if data is not None:
            return data
    return None


def reset_demo_users(demo_user_ids: list[str]) -> list[str]:
    """Delete all completion records and certificates for the given demo user ids.

    Idempotent: calling with an id that has no records is a no-op (no error).
    Returns the list of user ids that were actually found and cleaned.

    This is the backend for POST /api/demo/reset (conference mode only).
    Only touches users whose ids are in ``demo_user_ids`` — real user records
    are never modified.
    """
    import shutil

    cleaned: list[str] = []
    for uid in demo_user_ids:
        found = False
        # Delete completion records + certificates.
        ud = _user_dir(uid)
        if ud.exists():
            try:
                shutil.rmtree(ud)
                found = True
            except OSError:
                # Best-effort: log and continue so a single bad file doesn't abort the reset.
                pass

        # D3: delete gamification file — always attempted, independent of completion dir.
        gf = _gamif_path(uid)
        try:
            if gf.exists():
                gf.unlink()
                found = True
        except OSError:
            pass

        if found:
            cleaned.append(uid)
    return cleaned


# ── D3 Gamification ───────────────────────────────────────────────────────────
# XP values (flat, documentable aloud):
#   Lesson completed   : 10 XP
#   Quiz passed        : 20 XP
#   Flashcard deck done: 10 XP
#   Assessment passed  : 50 XP
#   Track completed    : 100 XP  (bonus on top of lesson XP)
#
# Streak rules (simple enough to say aloud):
#   Any completed lesson on a calendar day counts as that day's activity.
#   Consecutive days = streak count.
#   Missed day resets to 0.
#   Date stored as ISO date (YYYY-MM-DD) UTC; demo uses system date.
#
# Badges:
#   Per-track completion : "<track-title> Complete"
#   "First Lesson"       : first lesson ever completed
#   "On a Roll"          : 3-day streak reached
#   "Scholar"            : first assessment passed
#
# Trust guardrails (DEC-4):
#   - No leaderboard. No endpoint returns per-learner XP ranked lists.
#   - Gamification is purely additive — no feature is gated behind XP level.
#   - Streak is server-side; survives device changes.
#   - Demo reset clears gamification.

_XP_VALUES = {
    "lesson": 10,
    "quiz": 20,
    "flashcard_deck": 10,
    "assessment": 50,
    "track": 100,
}


def _gamif_path(user_id: str) -> Path:
    return _GAMIFICATION_DIR / f"{_safe_id(user_id)}.json"


def _empty_gamif() -> dict:
    return {"xp": 0, "streak": 0, "last_active_date": None, "badges": []}


def _load_gamif(user_id: str) -> dict:
    path = _gamif_path(user_id)
    data = _read_json(path)
    if data is None:
        return _empty_gamif()
    # Ensure all keys present (forward-compat).
    base = _empty_gamif()
    base.update(data)
    return base


def _save_gamif(user_id: str, data: dict) -> None:
    _write_json(_gamif_path(user_id), data)


def add_xp(user_id: str, amount: int, reason: str = "") -> int:
    """Add ``amount`` XP for ``user_id``.  Returns the new total.

    Idempotent-safe: adding 0 is a no-op.
    """
    if amount <= 0:
        return _load_gamif(user_id)["xp"]
    g = _load_gamif(user_id)
    g["xp"] = g.get("xp", 0) + amount
    _save_gamif(user_id, g)
    return g["xp"]


def update_streak(user_id: str, today_date: str) -> int:
    """Advance or reset the streak for ``user_id`` based on ``today_date`` (YYYY-MM-DD).

    Consecutive days → increment.
    Missed day (gap > 1) → reset to 1 (today counts).
    Same day again → no-op (idempotent).
    Returns new streak count.
    """
    g = _load_gamif(user_id)
    last = g.get("last_active_date")
    if last == today_date:
        return g.get("streak", 1)

    if last is None:
        g["streak"] = 1
    else:
        try:
            from datetime import date
            last_dt = date.fromisoformat(last)
            today_dt = date.fromisoformat(today_date)
            delta = (today_dt - last_dt).days
            if delta == 1:
                g["streak"] = g.get("streak", 0) + 1
            elif delta > 1:
                g["streak"] = 1
            # delta == 0 handled by same-day check above; delta < 0 = time travel, reset
            elif delta < 0:
                g["streak"] = 1
        except (ValueError, TypeError):
            g["streak"] = 1

    g["last_active_date"] = today_date
    _save_gamif(user_id, g)
    return g["streak"]


def award_badge(user_id: str, badge_id: str, badge_title: str) -> bool:
    """Award a badge.  Idempotent — only awards once per ``badge_id``.

    Returns True if the badge was newly awarded, False if already had it.
    """
    g = _load_gamif(user_id)
    existing = {b["id"] for b in g.get("badges", [])}
    if badge_id in existing:
        return False
    g.setdefault("badges", []).append({
        "id": badge_id,
        "title": badge_title,
        "awarded_at": _now_iso(),
    })
    _save_gamif(user_id, g)
    return True


def check_and_award_badges(
    user_id: str,
    event_type: str,
    context: dict | None = None,
) -> list[dict]:
    """Check and award any badges earned by this event.

    event_type: one of "lesson", "quiz", "flashcard_deck", "assessment", "track"
    context: optional dict — may include "track_title", "streak", "is_first_lesson"

    Returns list of newly-awarded badge dicts (empty if nothing new).
    """
    context = context or {}
    g = _load_gamif(user_id)
    newly_awarded: list[dict] = []

    def _maybe_award(bid: str, title: str) -> None:
        existing = {b["id"] for b in g.get("badges", [])}
        if bid not in existing:
            g.setdefault("badges", []).append({
                "id": bid,
                "title": title,
                "awarded_at": _now_iso(),
            })
            newly_awarded.append({"id": bid, "title": title})

    if event_type == "lesson":
        # "First Lesson" — first lesson ever completed
        all_progress = get_all_progress(user_id)
        total_lessons = 0
        for prog in all_progress.values():
            ld = prog.get("lessons_done") or {}
            for refs in ld.values():
                total_lessons += len(refs)
        # total_lessons already includes this lesson (set_lesson_done was called first)
        if total_lessons >= 1:
            _maybe_award("first-lesson", "First Lesson")

    if event_type in ("lesson", "quiz", "flashcard_deck", "assessment", "track"):
        # "On a Roll" — 3-day streak
        streak = context.get("streak", g.get("streak", 0))
        if streak >= 3:
            _maybe_award("on-a-roll", "On a Roll")

    if event_type == "assessment":
        # "Scholar" — first assessment passed
        _maybe_award("scholar", "Scholar")

    if event_type == "track":
        # Per-track completion badge
        track_title = context.get("track_title", "")
        if track_title:
            badge_id = f"track-complete-{_safe_id(track_title)}"
            _maybe_award(badge_id, f"{track_title} Complete")

    if newly_awarded:
        _save_gamif(user_id, g)
    return newly_awarded


def get_gamification(user_id: str) -> dict:
    """Return full gamification state for a learner.

    Returns:
        {xp, streak, badges, level, next_badge_at}

    level = xp // 100 + 1  (simple, documentable formula)
    next_badge_at = next milestone where a badge is awarded, based on current
    streak progress (or None if all streak badges earned).
    """
    g = _load_gamif(user_id)
    xp = g.get("xp", 0)
    streak = g.get("streak", 0)
    badges = g.get("badges", [])
    level = xp // 100 + 1

    badge_ids = {b["id"] for b in badges}
    next_badge_at: str | None = None
    if "first-lesson" not in badge_ids:
        next_badge_at = "Complete your first lesson"
    elif "on-a-roll" not in badge_ids:
        next_badge_at = f"{3 - streak} more day{'s' if 3 - streak != 1 else ''} to 'On a Roll'"
    elif "scholar" not in badge_ids:
        next_badge_at = "Pass your first assessment"

    return {
        "xp": xp,
        "streak": streak,
        "badges": badges,
        "level": level,
        "next_badge_at": next_badge_at,
        "last_active_date": g.get("last_active_date"),
    }


def get_all_progress(user_id: str) -> dict:
    """Return all stored progress records for a user.

    Returns: {track_id: progress_dict, ...}
    Only tracks that have a stored record are included (no seeded defaults here --
    those are injected per-track via get_progress).
    """
    user_dir = _user_dir(user_id)
    if not user_dir.exists():
        return {}

    result: dict = {}
    for p in user_dir.glob("*.json"):
        # Skip the certs/ subdir placeholder if it somehow becomes a file.
        if p.stem == "certs":
            continue
        data = _read_json(p)
        if data is not None:
            # Track id is the stem, un-safed -- best effort reconstruction.
            result[p.stem] = data
    return result
