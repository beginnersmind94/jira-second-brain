"""comment_store.py — Peer knowledge-board comments for LRN-5.

Comments are stored per-resource:
    data/comments/<safe-rid>.json   → list of comment objects

Each comment:
    {id, resource_id, author_id, author_name, body, pinned, created_at}

Writes are append-only (delete not supported in V1).
Pinning flips `pinned: true` on an existing comment — pinned comments are
returned first in list output.
"""
from __future__ import annotations

import json
import re
import time
import uuid
from pathlib import Path

_COMMENTS_DIR = Path(__file__).resolve().parent / "data" / "comments"
_MAX_BODY = 1000   # hard cap — no novellas
_MAX_PER_RESOURCE = 200  # storage safety valve


def _safe(s: str) -> str:
    return re.sub(r"[^\w\-]", "_", s)[:80]


def _comments_path(rid: str) -> Path:
    return _COMMENTS_DIR / f"{_safe(rid)}.json"


def _read(rid: str) -> list[dict]:
    p = _comments_path(rid)
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _write(rid: str, comments: list[dict]) -> None:
    _COMMENTS_DIR.mkdir(parents=True, exist_ok=True)
    _comments_path(rid).write_text(
        json.dumps(comments, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def list_comments(rid: str) -> list[dict]:
    """Return comments for a resource, pinned first then chronological."""
    comments = _read(rid)
    return sorted(comments, key=lambda c: (not c.get("pinned", False), c.get("created_at", "")))


def add_comment(rid: str, author_id: str, author_name: str, body: str) -> dict:
    """Append a new comment. Returns the created comment dict.

    Raises ValueError if body is empty or over _MAX_BODY chars.
    Raises OverflowError if the resource already has _MAX_PER_RESOURCE comments.
    """
    body = body.strip()
    if not body:
        raise ValueError("comment body must not be empty")
    if len(body) > _MAX_BODY:
        raise ValueError(f"comment body exceeds {_MAX_BODY} character limit")

    comments = _read(rid)
    if len(comments) >= _MAX_PER_RESOURCE:
        raise OverflowError(f"resource has reached the {_MAX_PER_RESOURCE}-comment limit")

    comment: dict = {
        "id":          str(uuid.uuid4()),
        "resource_id": rid,
        "author_id":   author_id,
        "author_name": author_name,
        "body":        body,
        "pinned":      False,
        "created_at":  time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    comments.append(comment)
    _write(rid, comments)
    return comment


def pin_comment(comment_id: str, rid: str) -> dict | None:
    """Toggle pin on a comment. Returns the updated comment or None if not found."""
    comments = _read(rid)
    for c in comments:
        if c.get("id") == comment_id:
            c["pinned"] = not c.get("pinned", False)
            _write(rid, comments)
            return c
    return None
