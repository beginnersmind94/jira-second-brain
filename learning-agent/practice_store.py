"""practice_store.py — Spaced-repetition daily practice sessions.

D4 — Practice mode (Wave 3, ANC Jul 13 demo).

Each learner gets a JSON file at ``data/practice/<user_id>.json`` containing:
  - ``sessions``     — list of daily sessions (date, 5 items, completion flag)
  - ``review_queue`` — items that were answered incorrectly; scheduled for review

Trust guardrails (enforced here, not by convention):
  1. ``build_session()`` ONLY includes items from decks/quizzes whose
     ``status == "approved"``.  A drift event that un-approves a deck removes it
     from future sessions automatically — the check happens at build time.
  2. Source quotes are carried on every item so the UI can show them after each
     practice card (practice is still a learning+verification moment).
  3. No practice items are invented — the pool is only real approved items from
     real approved content.  ``build_session()`` never generates questions.

Scheduling follows a simple SM-2-style policy:
  - Missed questions go to ``review_queue`` with ``next_review = today + 1 day``.
  - ``build_session()`` first pulls overdue review items, then fills remaining
    slots from the approved pool.
  - Items seen in the last 7 days are de-duplicated (not repeated 2 days running).
  - Session size is capped at 5 items (or all available if < 5).
"""
from __future__ import annotations

import json
import random
import re
from datetime import date, timedelta
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

_BASE = Path(__file__).resolve().parent
_PRACTICE_DIR = _BASE / "data" / "practice"
_PRACTICE_DIR.mkdir(parents=True, exist_ok=True)

_FLASHCARDS_DIR = _BASE / "data" / "flashcards"
_QUIZZES_DIR = _BASE / "quizzes"

MAX_SESSION_SIZE = 5
DEDUP_WINDOW_DAYS = 7


# ── Helpers ───────────────────────────────────────────────────────────────────

def _practice_path(user_id: str) -> Path:
    safe = re.sub(r"[^\w\-]", "_", user_id)[:80]
    return _PRACTICE_DIR / f"{safe}.json"


def _read_store(user_id: str) -> dict:
    p = _practice_path(user_id)
    if not p.exists():
        return {"user_id": user_id, "sessions": [], "review_queue": []}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"user_id": user_id, "sessions": [], "review_queue": []}


def _write_store(store: dict) -> None:
    _practice_path(store["user_id"]).write_text(
        json.dumps(store, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _today_str(today_date: str | None = None) -> str:
    if today_date:
        return today_date
    return date.today().isoformat()


def _date_add(d: str, days: int) -> str:
    """Add ``days`` to an ISO-8601 date string and return the result."""
    return (date.fromisoformat(d) + timedelta(days=days)).isoformat()


# ── Pool loading — APPROVED content only ─────────────────────────────────────

def _load_approved_flashcard_items() -> list[dict]:
    """Return all cards from APPROVED flashcard decks as practice items.

    TRUST INVARIANT: only decks with ``status == "approved"`` are included.
    A drifted deck that has been reverted to draft is automatically excluded.
    """
    items: list[dict] = []
    if not _FLASHCARDS_DIR.exists():
        return items
    for p in sorted(_FLASHCARDS_DIR.glob("deck-*.json")):
        try:
            deck = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        # TRUST GATE: only approved decks.
        if deck.get("status") != "approved":
            continue
        deck_id = deck.get("id", p.stem)
        for card in deck.get("cards") or []:
            # Only grounded cards carry a verifiable source quote.
            if card.get("grounded") is False:
                continue
            items.append({
                "type": "flashcard",
                "deck_id": deck_id,
                "card_id": card.get("id", ""),
                "front": card.get("front", ""),
                "back": card.get("back", ""),
                "source_quote": card.get("source_quote", ""),
                "section": card.get("section", ""),
            })
    return items


def _load_approved_quiz_items() -> list[dict]:
    """Return all questions from APPROVED quizzes as practice items.

    TRUST INVARIANT: only quizzes with ``status == "approved"`` are included.
    Only grounded or SME-verified questions are included.
    """
    items: list[dict] = []
    if not _QUIZZES_DIR.exists():
        return items
    for p in sorted(_QUIZZES_DIR.glob("quiz-*.json")):
        try:
            quiz = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        # TRUST GATE: only approved quizzes.
        if quiz.get("status") != "approved":
            continue
        quiz_id = quiz.get("id", p.stem)
        for idx, q in enumerate(quiz.get("questions") or []):
            # Only include grounded or SME-verified questions.
            if not (q.get("grounded") or q.get("sme_verified")):
                continue
            # Primary source span varies by question type.
            sq = (
                q.get("source_quote")
                or q.get("source_span")
                or q.get("source_sentence")
                or ""
            )
            items.append({
                "type": "question",
                "quiz_id": quiz_id,
                "question_idx": idx,
                "stem": q.get("stem") or q.get("prompt") or "",
                "qtype": q.get("type", "mcq"),
                "source_quote": sq,
                # Full question data carried so the UI can render any type.
                "question_data": q,
            })
    return items


def _recent_item_keys(sessions: list[dict], today: str) -> set[str]:
    """Return a set of item keys seen in the last DEDUP_WINDOW_DAYS days."""
    cutoff = _date_add(today, -DEDUP_WINDOW_DAYS)
    seen: set[str] = set()
    for session in sessions:
        session_date = session.get("date", "")
        if session_date < cutoff:
            continue
        for item in session.get("items") or []:
            seen.add(_item_key(item))
    return seen


def _item_key(item: dict) -> str:
    """Stable string key for an item (used for dedup)."""
    if item.get("type") == "flashcard":
        return f"flashcard:{item.get('deck_id')}:{item.get('card_id')}"
    return f"question:{item.get('quiz_id')}:{item.get('question_idx')}"


# ── Public API ────────────────────────────────────────────────────────────────

def get_today_session(user_id: str, today_date: str | None = None) -> dict:
    """Return today's session, building one if it doesn't exist yet.

    Idempotent — calling twice on the same date returns the same session.
    """
    today = _today_str(today_date)
    store = _read_store(user_id)
    # Look for an existing session for today.
    for session in store["sessions"]:
        if session.get("date") == today:
            return session
    # Not found — build one.
    return build_session(user_id, today, tracks=None)


def build_session(
    user_id: str,
    today_date: str | None = None,
    tracks: list[str] | None = None,
) -> dict:
    """Build (or rebuild) today's 5-item practice session for the learner.

    Algorithm:
    1. Pull overdue review items (``next_review <= today``) — up to 5.
    2. Fill remaining slots from the approved pool (flashcards + quiz questions).
    3. De-duplicate against items seen in the last 7 days.
    4. Cap at MAX_SESSION_SIZE (5) items.

    The ``tracks`` parameter is accepted but currently unused for filtering —
    the pool includes all approved content.  A future version can filter by
    the user's enrolled tracks.

    Returns the newly-built session dict (also persisted to disk).
    """
    today = _today_str(today_date)
    store = _read_store(user_id)
    recent_keys = _recent_item_keys(store["sessions"], today)

    # ── Step 1: pull overdue review items ───────────────────────────────────
    overdue: list[dict] = [
        e for e in (store.get("review_queue") or [])
        if e.get("next_review", "9999") <= today
    ]
    # Remove overdue items from the queue (consumed into this session).
    store["review_queue"] = [
        e for e in (store.get("review_queue") or [])
        if e.get("next_review", "9999") > today
    ]

    session_items: list[dict] = []
    for entry in overdue[:MAX_SESSION_SIZE]:
        item = {k: v for k, v in entry.items() if k not in ("missed_at", "next_review")}
        session_items.append(item)

    # ── Step 2: fill from approved pool ─────────────────────────────────────
    slots_remaining = MAX_SESSION_SIZE - len(session_items)
    if slots_remaining > 0:
        pool = _load_approved_flashcard_items() + _load_approved_quiz_items()
        used_keys = {_item_key(i) for i in session_items}
        candidates = [
            item for item in pool
            if _item_key(item) not in used_keys
            and _item_key(item) not in recent_keys
        ]
        random.shuffle(candidates)
        session_items.extend(candidates[:slots_remaining])

    # ── Step 3: serialize items (strip heavy question_data from flashcards) ─
    clean_items: list[dict] = []
    for item in session_items:
        if item.get("type") == "flashcard":
            clean_items.append({
                "type": "flashcard",
                "deck_id": item["deck_id"],
                "card_id": item["card_id"],
                "front": item.get("front", ""),
                "back": item.get("back", ""),
                "source_quote": item.get("source_quote", ""),
                "section": item.get("section", ""),
            })
        else:
            clean_items.append(item)

    session: dict = {
        "date": today,
        "items": clean_items,
        "completed": False,
        "completed_at": None,
    }

    # Persist: replace any existing today-entry, then append.
    store["sessions"] = [s for s in store["sessions"] if s.get("date") != today]
    store["sessions"].append(session)
    _write_store(store)

    return session


def complete_session(user_id: str, today_date: str | None = None) -> dict:
    """Mark today's session as completed.

    Fires D3 streak credit non-fatally if ``gamification_store`` is available.

    Returns the updated session dict.
    """
    today = _today_str(today_date)
    store = _read_store(user_id)

    updated: dict | None = None
    for session in store["sessions"]:
        if session.get("date") == today:
            session["completed"] = True
            session["completed_at"] = today
            updated = session
            break

    if updated is None:
        # No session for today yet — create a minimal completed record.
        updated = {
            "date": today,
            "items": [],
            "completed": True,
            "completed_at": today,
        }
        store["sessions"].append(updated)

    _write_store(store)

    # ── D3 streak hook (non-fatal; D3 not yet built) ─────────────────────────
    try:
        import gamification_store as _gam  # type: ignore  # D3 module
        _gam.update_streak(user_id, today)
    except ImportError:
        pass
    except Exception:
        pass

    return updated


def add_to_review_queue(user_id: str, item: dict, today_date: str | None = None) -> None:
    """Add a missed item to the review queue with ``next_review = today + 1 day``.

    Idempotent: adding the same item twice on the same day is a no-op.
    """
    today = _today_str(today_date)
    store = _read_store(user_id)
    key = _item_key(item)

    for entry in store.get("review_queue") or []:
        if _item_key(entry) == key:
            return  # Already queued.

    # Strip heavy question_data before persisting to the queue.
    entry: dict = {
        k: v for k, v in item.items() if k not in ("question_data",)
    }
    entry["missed_at"] = today
    entry["next_review"] = _date_add(today, 1)
    store.setdefault("review_queue", []).append(entry)
    _write_store(store)


def get_session_status(user_id: str, today_date: str | None = None) -> dict:
    """Return a summary of today's session status without building a new session.

    Returns:
        {
            session: dict | None,
            session_ready: bool,
            items_count: int,
            queue_count: int,
        }
    """
    today = _today_str(today_date)
    store = _read_store(user_id)

    session: dict | None = None
    for s in store["sessions"]:
        if s.get("date") == today:
            session = s
            break

    queue_count = len([
        e for e in (store.get("review_queue") or [])
        if e.get("next_review", "9999") <= today
    ])

    if session is None:
        return {
            "session": None,
            "session_ready": False,
            "items_count": 0,
            "queue_count": queue_count,
        }

    items_count = len(session.get("items") or [])
    session_ready = items_count > 0 and not session.get("completed", False)

    return {
        "session": session,
        "session_ready": session_ready,
        "items_count": items_count,
        "queue_count": queue_count,
    }
