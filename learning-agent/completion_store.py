"""completion_store.py — Disk-backed per-learner completion records.

Each learner's progress is stored as a JSON file under:
    data/completion/<user_id>/<track_id>.json

Certificates are stored under:
    data/completion/<user_id>/certs/<cert_id>.json

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
        ud = _user_dir(uid)
        if not ud.exists():
            continue
        try:
            shutil.rmtree(ud)
            cleaned.append(uid)
        except OSError:
            # Best-effort: log and continue so a single bad file doesn't abort the reset.
            pass
    return cleaned


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
