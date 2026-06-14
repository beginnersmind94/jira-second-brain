"""formative_store.py — Aggregate formative check results for LRN-6.

Formative files are written per-learner by the segment-check POST endpoint:
    data/formative/<uid>/<rid>/<segment_index>.json

Each file stores: question_id, correct, answered_at, and (LRN-6) confidence (1–5).
This module only reads and aggregates — it never writes.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

_FORMATIVE_DIR = Path(__file__).resolve().parent / "data" / "formative"


def _safe(s: str) -> str:
    return re.sub(r"[^\w\-]", "_", s)[:80]


def get_confidence_summary(rid: str, formative_dir: Path | None = None) -> dict:
    """Aggregate confidence + correctness for all learners who attempted this resource.

    Reads data/formative/<uid>/<rid>/<seg_idx>.json files.
    Returns per-segment averages and an overall confidence average.

    Args:
        rid: resource id (e.g. "GUIDE-001")
        formative_dir: override base dir (used in tests for isolation)

    Returns::
        {
            "resource_id": str,
            "segments": [
                {
                    "seg_idx": int,
                    "confidence_avg": float | None,   # None if no confidence recorded
                    "confidence_count": int,           # learners who gave a confidence rating
                    "pct_correct": int,                # 0–100
                    "answer_count": int,               # total answer submissions
                }
            ],
            "overall_confidence_avg": float | None,
        }
    """
    base = formative_dir or _FORMATIVE_DIR
    safe_rid = _safe(rid)
    segments: dict[int, dict] = {}

    if not base.exists():
        return {"resource_id": rid, "segments": [], "overall_confidence_avg": None}

    for user_dir in base.iterdir():
        if not user_dir.is_dir():
            continue
        rid_dir = user_dir / safe_rid
        if not rid_dir.is_dir():
            continue
        for seg_file in rid_dir.glob("*.json"):
            try:
                seg_idx = int(seg_file.stem)
                data = json.loads(seg_file.read_text(encoding="utf-8"))
            except (ValueError, json.JSONDecodeError, OSError):
                continue

            if seg_idx not in segments:
                segments[seg_idx] = {"confidence_vals": [], "correct_count": 0, "total": 0}
            entry = segments[seg_idx]
            entry["total"] += 1
            if data.get("correct"):
                entry["correct_count"] += 1
            conf = data.get("confidence")
            if isinstance(conf, (int, float)) and 1 <= conf <= 5:
                entry["confidence_vals"].append(float(conf))

    result_segs: list[dict] = []
    all_conf: list[float] = []
    for seg_idx in sorted(segments):
        entry = segments[seg_idx]
        vals = entry["confidence_vals"]
        avg = round(sum(vals) / len(vals), 2) if vals else None
        if avg is not None:
            all_conf.extend(vals)
        pct = round(100 * entry["correct_count"] / entry["total"]) if entry["total"] else 0
        result_segs.append({
            "seg_idx": seg_idx,
            "confidence_avg": avg,
            "confidence_count": len(vals),
            "pct_correct": pct,
            "answer_count": entry["total"],
        })

    overall = round(sum(all_conf) / len(all_conf), 2) if all_conf else None
    return {
        "resource_id": rid,
        "segments": result_segs,
        "overall_confidence_avg": overall,
    }
