"""gap_store.py — Content gap analysis store for OPS-1.

Storage layout:
    data/gaps/gaps.json         — detected gap records
    data/gaps/lrn1-refusals.jsonl — stub refusal log (LRN-1 AI assistant feed)

Each gap record:
    {id, type, description, module, source, detected_at, status}

Gap types:
  "refusal"         — a learner asked a question that no approved content could answer
  "missing_module"  — a topic mentioned in trainer notes with no corresponding guide
  "coverage_gap"    — a ticket exists in Jira but no guide covers it yet

status: "open" | "resolved"
"""
from __future__ import annotations

import json
import re
import time
import uuid
from pathlib import Path

_GAPS_DIR      = Path(__file__).resolve().parent / "data" / "gaps"
_GAPS_FILE     = _GAPS_DIR / "gaps.json"
_REFUSALS_FILE = _GAPS_DIR / "lrn1-refusals.jsonl"

_VALID_TYPES   = {"refusal", "missing_module", "coverage_gap"}
_VALID_STATUS  = {"open", "resolved"}


# ── Internal I/O ──────────────────────────────────────────────────────────────

def _read_gaps() -> list[dict]:
    if not _GAPS_FILE.exists():
        return []
    try:
        return json.loads(_GAPS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _write_gaps(gaps: list[dict]) -> None:
    _GAPS_DIR.mkdir(parents=True, exist_ok=True)
    _GAPS_FILE.write_text(json.dumps(gaps, indent=2, ensure_ascii=False), encoding="utf-8")


def _read_refusals() -> list[dict]:
    if not _REFUSALS_FILE.exists():
        return []
    results = []
    try:
        for line in _REFUSALS_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                results.append(json.loads(line))
    except (json.JSONDecodeError, OSError):
        pass
    return results


# ── Public API ────────────────────────────────────────────────────────────────

def add_gap(
    gap_type: str,
    description: str,
    module: str = "",
    source: str = "",
) -> dict:
    """Record a new gap.  Returns the created record.

    Raises ValueError for unknown gap_type or empty description.
    """
    if gap_type not in _VALID_TYPES:
        raise ValueError(f"unknown gap type {gap_type!r}; expected one of {_VALID_TYPES}")
    description = description.strip()
    if not description:
        raise ValueError("description must not be empty")

    gap: dict = {
        "id":          str(uuid.uuid4()),
        "type":        gap_type,
        "description": description,
        "module":      module,
        "source":      source,
        "detected_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "status":      "open",
    }
    gaps = _read_gaps()
    gaps.append(gap)
    _write_gaps(gaps)
    return gap


def get_gaps(status: str | None = None) -> list[dict]:
    """Return gap records, optionally filtered by status.

    Also ingests any new LRN-1 refusal events that haven't been added yet.
    Returned list is sorted newest-first.
    """
    _ingest_refusals()
    gaps = _read_gaps()
    if status:
        gaps = [g for g in gaps if g.get("status") == status]
    return sorted(gaps, key=lambda g: g.get("detected_at", ""), reverse=True)


def resolve_gap(gap_id: str) -> dict | None:
    """Mark a gap as resolved.  Returns the updated record or None if not found."""
    gaps = _read_gaps()
    for g in gaps:
        if g.get("id") == gap_id:
            g["status"] = "resolved"
            _write_gaps(gaps)
            return g
    return None


def log_refusal(question: str, module: str = "") -> None:
    """Stub LRN-1 feed: append a refusal event to the JSONL log.

    Called by the AI assistant (LRN-1) when a learner question can't be
    answered from approved content.  The event is ingested as a 'refusal'
    gap on the next call to get_gaps().
    """
    _GAPS_DIR.mkdir(parents=True, exist_ok=True)
    entry = json.dumps({
        "question":   question,
        "module":     module,
        "logged_at":  time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_ingested":  False,
    })
    with _REFUSALS_FILE.open("a", encoding="utf-8") as fh:
        fh.write(entry + "\n")


# ── Private: refusal ingestor ─────────────────────────────────────────────────

def _ingest_refusals() -> None:
    """Convert un-ingested refusal log entries into gap records (idempotent)."""
    if not _REFUSALS_FILE.exists():
        return

    lines  = _REFUSALS_FILE.read_text(encoding="utf-8").splitlines()
    rewrite = False
    new_gaps: list[dict] = []
    updated_lines: list[str] = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            updated_lines.append(line)
            continue

        if entry.get("_ingested"):
            updated_lines.append(line)
            continue

        # Create a gap record for this refusal.
        new_gaps.append({
            "id":          str(uuid.uuid4()),
            "type":        "refusal",
            "description": f"Learner question not answered: {entry.get('question', '')[:200]}",
            "module":      entry.get("module", ""),
            "source":      "lrn1-refusal-log",
            "detected_at": entry.get("logged_at", time.strftime("%Y-%m-%dT%H:%M:%S")),
            "status":      "open",
        })
        entry["_ingested"] = True
        updated_lines.append(json.dumps(entry))
        rewrite = True

    if new_gaps:
        existing = _read_gaps()
        _write_gaps(existing + new_gaps)

    if rewrite:
        _REFUSALS_FILE.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")
