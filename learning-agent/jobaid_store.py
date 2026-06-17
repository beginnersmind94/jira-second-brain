"""jobaid_store.py — Printable job aid store for AUTH-3.

Storage layout:
    data/job-aids/<safe-rid>.json

Each record:
    {resource_id, html, qr_data_uri, generated_at}

`html` is a self-contained printable HTML string (no external deps).
`qr_data_uri` is the SVG data-URI for the deep-link QR code embedded in the aid.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

_JOB_AIDS_DIR = Path(__file__).resolve().parent / "data" / "job-aids"


def _safe(s: str) -> str:
    return re.sub(r"[^\w\-]", "_", s)[:80]


def _record_path(rid: str) -> Path:
    return _JOB_AIDS_DIR / f"{_safe(rid)}.json"


def get_job_aid(rid: str) -> dict | None:
    """Return stored job-aid record or None."""
    p = _record_path(rid)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def save_job_aid(rid: str, html: str, qr_data_uri: str = "") -> dict:
    """Persist a job aid.  Returns the saved record.

    Raises ValueError if html is empty.
    """
    if not html or not html.strip():
        raise ValueError("html must not be empty")

    record: dict = {
        "resource_id":  rid,
        "html":         html,
        "qr_data_uri":  qr_data_uri,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    _JOB_AIDS_DIR.mkdir(parents=True, exist_ok=True)
    _record_path(rid).write_text(
        json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return record


def delete_job_aid(rid: str) -> bool:
    """Remove job-aid record.  Returns True if a file was deleted."""
    p = _record_path(rid)
    if p.exists():
        p.unlink()
        return True
    return False
