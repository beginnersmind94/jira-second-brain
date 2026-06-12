"""flashcard_store.py — Persistence + verbatim gate + drift detection for guide flashcard decks.

Mirror of quiz_store.py.  Every deck is grounded-by-construction the SAME way guides and quizzes
are: each card carries a verbatim ``source_quote`` that must be a substring of the published guide
HTML (citation comments stripped) the deck was built from.  The deterministic verbatim gate is the
machine floor; human approval is the human floor — this mirrors the guide pipeline exactly.

Per-card provenance:
  ai_grounded   — AI-made, source_quote verbatim in guide HTML at generation time  -> grounded
  manual        — hand-authored card; grounded iff source_quote still verbatim      -> grounded iff True

Card types (B2 spec):
  procedural    — "What do you do when X?" — preferred; tests a workflow
  definitional  — "What is X?" — allowed but second-priority

Drift: ``source_content_hash`` is stamped at creation.  When the underlying guide is edited or
regenerated its hash changes — ``check_drift()`` detects this, reverts the deck to ``"draft"``,
and the deck disappears from course pickers until re-approved.  This is the same policy as
quiz_store.py (an approved quiz drops back to draft on source drift).

Gating invariants (enforced by construction, not convention):
  - ``create_deck()`` only accepts cards whose ``source_quote`` is a verbatim substring of the
    guide HTML (citation comments pre-stripped).  Non-matching cards are dropped silently; the
    caller's response shows ``generated`` / ``kept`` / ``dropped`` counts.
  - ``create_deck()`` raises ValueError when fewer than 3 cards survive gating (mirrors the
    quiz-store minimum).
  - ``approve_deck()`` re-runs the verbatim gate against the CURRENT guide HTML, re-computes the
    hash, and blocks approval if any card fails.  It also blocks if the deck has fewer than 3
    surviving cards.
  - ``status`` defaults to ``"draft"`` and can only reach ``"approved"`` through ``approve_deck()``;
    there is no auto-approval code path.
  - Guide must be approved (``approved: true``) before a deck can be generated from it.  This
    check is enforced in the endpoint layer (``demo_app.py``), not here -- this module trusts that
    the HTML it receives came from an approved guide.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
import uuid
from pathlib import Path

BASE = Path(__file__).resolve().parent
FLASHCARDS_DIR = BASE / "data" / "flashcards"
FLASHCARDS_DIR.mkdir(parents=True, exist_ok=True)

MIN_CARDS = 3

# Source-comment regex -- same as app.py / scorm_export.py.
_SOURCE_COMMENT_RE = re.compile(r"<!--\s*Source:[\s\S]*?-->")


# ── Normalisation helpers (identical to quiz_store._norm) ────────────────────

def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip().lower()


def source_hash(text: str) -> str:
    """SHA-256 of normalised text, first 16 hex chars -- same as quiz_store."""
    return hashlib.sha256(_norm(text).encode("utf-8")).hexdigest()[:16]


def strip_source_comments(html: str) -> str:
    """Remove <!-- Source: ... --> comments so the verbatim gate works against
    the visible guide text, not the citation metadata."""
    return _SOURCE_COMMENT_RE.sub("", html)


# ── ID helpers ────────────────────────────────────────────────────────────────

def _new_deck_id() -> str:
    date_part = time.strftime("%Y%m%d")
    return f"deck-{date_part}-{uuid.uuid4().hex[:8]}"


def _deck_path(deck_id: str) -> Path:
    return FLASHCARDS_DIR / f"{deck_id}.json"


# ── Low-level I/O ─────────────────────────────────────────────────────────────

def _write_deck(deck: dict) -> dict:
    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    deck["updated_at"] = now
    deck.setdefault("created_at", now)
    _deck_path(deck["id"]).write_text(
        json.dumps(deck, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return deck


def _read_deck(deck_id: str) -> dict | None:
    p = _deck_path(deck_id)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


# ── Public API ────────────────────────────────────────────────────────────────

def create_deck(
    source_rid: str,
    title: str,
    cards: list[dict],
    guide_html: str,
) -> dict:
    """Validate cards against the guide HTML, build a deck, persist and return it.

    Each card in ``cards`` must have:
      - ``front``:        the question / scenario
      - ``back``:         the answer / correct procedure
      - ``source_quote``: a verbatim span from ``guide_html`` (citation-stripped)
      - ``section``:      (optional) guide section this card was drawn from
      - ``card_type``:    ``"procedural"`` or ``"definitional"``

    Cards whose ``source_quote`` is not a verbatim substring of (citation-stripped)
    ``guide_html`` are silently dropped.

    Raises:
        ValueError: if fewer than MIN_CARDS cards survive gating.
    """
    clean_html = strip_source_comments(guide_html)
    norm_source = _norm(clean_html)

    kept: list[dict] = []
    dropped = 0
    for i, raw in enumerate(cards):
        front = (raw.get("front") or "").strip()
        back = (raw.get("back") or "").strip()
        quote = (raw.get("source_quote") or "").strip()
        if not (front and back and quote):
            dropped += 1
            continue
        if _norm(quote) not in norm_source:
            dropped += 1
            continue
        kept.append({
            "id": f"card-{i + 1}",
            "front": front,
            "back": back,
            "source_quote": quote,
            "section": (raw.get("section") or "").strip(),
            "card_type": (raw.get("card_type") or "procedural").strip(),
            "grounded": True,
        })

    if len(kept) < MIN_CARDS:
        raise ValueError(
            f"insufficient verifiable cards: {len(kept)} survived gating "
            f"(need at least {MIN_CARDS}); {dropped} dropped"
        )

    deck = {
        "id": _new_deck_id(),
        "title": title or f"Flashcards -- {source_rid}",
        "source_resource_id": source_rid,
        "source_content_hash": source_hash(clean_html),
        "cards": kept,
        "status": "draft",   # NEVER auto-approved
        "approved_at": None,
        "provenance": "ai_grounded",
        "generated": len(cards),
        "kept": len(kept),
        "dropped": dropped,
    }
    return _write_deck(deck)


def get_deck(deck_id: str) -> dict | None:
    """Load a deck from disk.  Returns None if not found."""
    return _read_deck(deck_id)


def list_decks(status: str | None = None) -> list[dict]:
    """Return all decks, optionally filtered by status, sorted newest-first."""
    out = []
    for p in sorted(
        FLASHCARDS_DIR.glob("deck-*.json"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    ):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if status and d.get("status") != status:
            continue
        out.append({
            "id": d.get("id"),
            "title": d.get("title"),
            "status": d.get("status", "draft"),
            "source_resource_id": d.get("source_resource_id"),
            "source_content_hash": d.get("source_content_hash"),
            "total_cards": len(d.get("cards") or []),
            "provenance": d.get("provenance"),
            "created_at": d.get("created_at"),
            "updated_at": d.get("updated_at"),
        })
    return out


def check_drift(deck_id: str, guide_html: str) -> dict:
    """Compare the deck's ``source_content_hash`` to the current guide HTML.

    If the guide has changed since the deck was built, the deck is reverted to
    ``"draft"`` and persisted.  This enforces the trust invariant: an approved
    deck built against stale guide content must not remain approved.

    Returns:
        {
            "drifted": bool,
            "hash_was": str,
            "hash_now": str,
            "status_after": "draft" | "approved",
        }
    """
    deck = _read_deck(deck_id)
    if not deck:
        raise KeyError(f"deck '{deck_id}' not found")

    clean_html = strip_source_comments(guide_html)
    hash_now = source_hash(clean_html)
    hash_was = deck.get("source_content_hash", "")

    drifted = bool(hash_was) and hash_was != hash_now

    if drifted and deck.get("status") == "approved":
        deck["status"] = "draft"
        deck["approved_at"] = None
        _write_deck(deck)

    return {
        "drifted": drifted,
        "hash_was": hash_was,
        "hash_now": hash_now,
        "status_after": deck.get("status", "draft"),
    }


def approve_deck(deck_id: str, guide_html: str) -> dict:
    """Re-run the verbatim gate against the CURRENT guide HTML and flip the deck
    to ``"approved"`` if all cards still pass.

    The gate is re-run against the current HTML regardless of the stored hash --
    this means an approved deck is always live-verified before the approval flag
    is written.

    Raises:
        KeyError: if deck not found.
        ValueError: if any card fails the gate or fewer than MIN_CARDS survive.
    """
    deck = _read_deck(deck_id)
    if not deck:
        raise KeyError(f"deck '{deck_id}' not found")

    clean_html = strip_source_comments(guide_html)
    norm_source = _norm(clean_html)

    failed: list[str] = []
    for card in deck.get("cards") or []:
        quote = (card.get("source_quote") or "").strip()
        if not quote or _norm(quote) not in norm_source:
            card["grounded"] = False
            failed.append(card.get("id", "?"))
        else:
            card["grounded"] = True

    surviving = [c for c in (deck.get("cards") or []) if c.get("grounded")]
    if failed:
        _write_deck(deck)   # persist updated grounded flags
        raise ValueError(
            f"gate failed: {len(failed)} card(s) no longer verifiable "
            f"({', '.join(failed)})"
        )
    if len(surviving) < MIN_CARDS:
        raise ValueError(
            f"insufficient verifiable cards after gate: {len(surviving)} "
            f"(need at least {MIN_CARDS})"
        )

    deck["status"] = "approved"
    deck["approved_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    deck["source_content_hash"] = source_hash(clean_html)
    return _write_deck(deck)


def delete_deck(deck_id: str) -> bool:
    """Delete a deck from disk.  Returns True if deleted, False if not found."""
    p = _deck_path(deck_id)
    if p.exists():
        p.unlink()
        return True
    return False
