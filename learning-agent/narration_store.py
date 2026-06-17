"""narration_store.py — Per-resource segment narration audio stubs for AUTH-2.

Storage layout:
    data/narration/<safe-rid>.json

Each record:
    {resource_id, segments: [{index, audio_url, duration_seconds, stub}], generated_at, stub}

`stub: true` marks demo-mode narration where `audio_url` is a data-URI placeholder.
Production TTS (e.g. Azure Cognitive Services) sets `stub: false` and supplies real URLs.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

_NARRATION_DIR = Path(__file__).resolve().parent / "data" / "narration"


def _safe(s: str) -> str:
    return re.sub(r"[^\w\-]", "_", s)[:80]


def _record_path(rid: str) -> Path:
    return _NARRATION_DIR / f"{_safe(rid)}.json"


def get_narration(rid: str) -> dict | None:
    """Return stored narration record or None."""
    p = _record_path(rid)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def save_narration(rid: str, segments: list[dict], *, stub: bool = True) -> dict:
    """Persist narration metadata.  Returns the saved record.

    Each item in `segments` must contain:
        {index: int, audio_url: str, duration_seconds: float}
    """
    if not segments:
        raise ValueError("segments must not be empty")

    record: dict = {
        "resource_id":  rid,
        "segments":     [
            {
                "index":            int(s["index"]),
                "audio_url":        str(s["audio_url"]),
                "duration_seconds": float(s.get("duration_seconds", 0)),
                "stub":             stub,
            }
            for s in segments
        ],
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "stub":         stub,
    }
    _NARRATION_DIR.mkdir(parents=True, exist_ok=True)
    _record_path(rid).write_text(
        json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return record


def delete_narration(rid: str) -> bool:
    """Remove narration record.  Returns True if a file was deleted."""
    p = _record_path(rid)
    if p.exists():
        p.unlink()
        return True
    return False
