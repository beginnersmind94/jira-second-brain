"""translation_store.py — Per-resource lesson translations for AUTH-1.

Storage layout:
    data/translations/<safe-rid>/<lang>.json

Each record:
    {resource_id, lang, segments: [{index, body_html}], generated_at, stub}

`stub: true` marks demo-mode translations produced by the stub translator.
Production MT (BLD-3) sets `stub: false`.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

_TRANSLATIONS_DIR = Path(__file__).resolve().parent / "data" / "translations"
_LANG_RE = re.compile(r"^[a-zA-Z]{2,10}$")


def _safe(s: str) -> str:
    return re.sub(r"[^\w\-]", "_", s)[:80]


def _record_path(rid: str, lang: str) -> Path:
    return _TRANSLATIONS_DIR / _safe(rid) / f"{lang.lower()}.json"


def get_translation(rid: str, lang: str) -> dict | None:
    """Return stored translation record or None if not found."""
    p = _record_path(rid, lang)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def save_translation(rid: str, lang: str, segments: list[dict], *, stub: bool = True) -> dict:
    """Persist translated segments.  Returns the saved record.

    `segments` must be a list of {index: int, body_html: str}.
    Raises ValueError for invalid lang code.
    """
    lang = lang.strip().lower()
    if not _LANG_RE.match(lang):
        raise ValueError(f"invalid lang code: {lang!r} — use ISO 639-1 (2-10 alpha chars)")
    if lang == "en":
        raise ValueError("lang 'en' is reserved for the original; translations must be non-EN")

    record: dict = {
        "resource_id":  rid,
        "lang":         lang,
        "segments":     [{"index": s["index"], "body_html": s["body_html"]} for s in segments],
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "stub":         stub,
    }
    dest = _record_path(rid, lang)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    return record


def list_languages(rid: str) -> list[dict]:
    """Return available translation languages for a resource.

    Each entry: {lang, generated_at, stub}.
    Sorted alphabetically by lang.
    """
    lang_dir = _TRANSLATIONS_DIR / _safe(rid)
    if not lang_dir.exists():
        return []
    results = []
    for p in sorted(lang_dir.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            results.append({
                "lang":         data.get("lang", p.stem),
                "generated_at": data.get("generated_at", ""),
                "stub":         data.get("stub", True),
            })
        except (json.JSONDecodeError, OSError):
            continue
    return results
