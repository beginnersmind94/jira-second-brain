"""assessment_store.py — Persistence for Skill Assessment / Track Exam (B3).

Assessments are assembled from approved questions that already live in the quiz
store (data/quizzes/*.json).  The assessment entity stores *pointers* to those
questions — "<quiz_id>:<question_index>" — and resolves them to full question
objects at taker-time.  This means:

  1. Only approved questions are ever served (drift-safe: if a quiz loses
     approval after assembly the question is silently skipped).
  2. There is no second copy of question text — one source of truth.
  3. Source quotes are NEVER included in `get_questions()` output; they are
     added only in the attempt result (withheld during a timed attempt).

Assessment schema  (data/assessments/<id>.json):
    {
      "id": "assessment-YYYYMMDD-<uuid8>",
      "title": "string",
      "track_id": "<track this assessment belongs to>",
      "question_ids": ["<quiz_id>:<question_index>", ...],
      "time_limit_min": 15,
      "pass_pct": 70,
      "attempts_allowed": 3,
      "status": "draft",            # "draft" | "published"
      "created_at": "<ISO8601>",
      "updated_at": "<ISO8601>"
    }

Attempt records  (data/assessment-attempts/<user_id>/<aid>/<attempt_N>.json):
    {
      "user_id": "<uid>",
      "assessment_id": "<aid>",
      "attempt_number": N,
      "answers": {"<question_id_ptr>": <answer_value>, ...},
      "score_pct": 88,
      "passed": true,
      "submitted_at": "<ISO8601>"
    }
"""
from __future__ import annotations

import json
import random
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Resolve relative to this file so it works from any cwd.
_BASE = Path(__file__).resolve().parent
_ASSESS_DIR = _BASE / "data" / "assessments"
_ATTEMPTS_DIR = _BASE / "data" / "assessment-attempts"
_QUIZZES_DIR = _BASE / "quizzes"   # quiz_store.QUIZZES (same path)

_ASSESS_DIR.mkdir(parents=True, exist_ok=True)
_ATTEMPTS_DIR.mkdir(parents=True, exist_ok=True)


# ── Internal helpers ──────────────────────────────────────────────────────────

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


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


def _new_id() -> str:
    date_part = datetime.now().strftime("%Y%m%d")
    return f"assessment-{date_part}-{uuid.uuid4().hex[:8]}"


def _assess_path(aid: str) -> Path:
    return _ASSESS_DIR / f"{aid}.json"


def _load_quiz_raw(qid: str) -> dict | None:
    return _read_json(_QUIZZES_DIR / f"{qid}.json")


def _safe_uid(uid: str) -> str:
    return re.sub(r"[^\w\-]", "_", uid)[:80]


# ── Assessment CRUD ───────────────────────────────────────────────────────────

def create_assessment(
    *,
    title: str,
    track_id: str,
    question_ids: list[str],
    time_limit_min: int = 15,
    pass_pct: int = 70,
    attempts_allowed: int = 3,
) -> dict:
    """Create and persist a new draft assessment."""
    now = _now_iso()
    assessment = {
        "id": _new_id(),
        "title": title or "Untitled Assessment",
        "track_id": track_id or "",
        "question_ids": list(question_ids),
        "time_limit_min": max(1, int(time_limit_min)),
        "pass_pct": max(1, min(100, int(pass_pct))),
        "attempts_allowed": max(1, int(attempts_allowed)),
        "status": "draft",
        "created_at": now,
        "updated_at": now,
    }
    _write_json(_assess_path(assessment["id"]), assessment)
    return assessment


def get_assessment(aid: str) -> dict | None:
    return _read_json(_assess_path(aid))


def list_assessments(*, track_id: str = "") -> list[dict]:
    out: list[dict] = []
    for p in sorted(_ASSESS_DIR.glob("assessment-*.json"), key=lambda f: f.stat().st_mtime, reverse=True):
        a = _read_json(p)
        if a is None:
            continue
        if track_id and a.get("track_id") != track_id:
            continue
        out.append(a)
    return out


def save_assessment(assessment: dict) -> dict:
    assessment["updated_at"] = _now_iso()
    _write_json(_assess_path(assessment["id"]), assessment)
    return assessment


def update_assessment(aid: str, updates: dict) -> dict | None:
    a = get_assessment(aid)
    if a is None:
        return None
    if a.get("status") == "published":
        # Only allow non-structural updates on published assessments.
        for field in ("title", "time_limit_min", "pass_pct", "attempts_allowed"):
            if field in updates:
                a[field] = updates[field]
    else:
        for field in ("title", "track_id", "question_ids", "time_limit_min", "pass_pct", "attempts_allowed"):
            if field in updates:
                a[field] = updates[field]
    return save_assessment(a)


def publish_assessment(aid: str) -> tuple[dict | None, str | None]:
    """Publish an assessment. Returns (assessment, error_msg).

    Requires ≥3 questions from currently approved quizzes.
    """
    a = get_assessment(aid)
    if a is None:
        return None, "assessment not found"
    resolved = get_questions(a, include_source_quotes=False)
    if len(resolved) < 3:
        return None, f"need at least 3 approved questions (resolved {len(resolved)} from approved quizzes)"
    a["status"] = "published"
    return save_assessment(a), None


def delete_assessment(aid: str) -> bool:
    p = _assess_path(aid)
    if p.exists():
        p.unlink()
        return True
    return False


# ── Question resolution (the drift-safe query) ───────────────────────────────

def _strip_source_quotes(q: dict) -> dict:
    """Return a copy of q with source quote fields removed (withheld during attempt)."""
    strip_fields = ("source_quote", "source_span", "source_sentence")
    return {k: v for k, v in q.items() if k not in strip_fields}


def get_questions(
    assessment: dict,
    *,
    include_source_quotes: bool = False,
) -> list[dict]:
    """Resolve assessment question_ids to full question objects.

    Skips any pointer whose source quiz is no longer approved (drift-safe).
    Source quotes are stripped unless include_source_quotes=True.

    Each returned question object includes an extra field:
        "_ptr": "<quiz_id>:<question_index>"
    so the scorer can re-look up provenance for the attempt record.
    """
    resolved: list[dict] = []
    for ptr in (assessment.get("question_ids") or []):
        parts = ptr.split(":", 1)
        if len(parts) != 2:
            continue
        qid, idx_str = parts
        try:
            idx = int(idx_str)
        except ValueError:
            continue

        quiz = _load_quiz_raw(qid)
        if quiz is None:
            continue
        if quiz.get("status") != "approved":
            continue  # quiz lost approval → silently skip (trust guardrail #1)

        questions = quiz.get("questions") or []
        if idx < 0 or idx >= len(questions):
            continue

        q = dict(questions[idx])
        q["_ptr"] = ptr
        if not include_source_quotes:
            q = _strip_source_quotes(q)
        resolved.append(q)
    return resolved


# ── Auto-assembly ─────────────────────────────────────────────────────────────

def auto_assemble(
    *,
    track_id: str,
    n: int = 8,
    course_ids: list[str] | None = None,
) -> tuple[dict | None, str | None]:
    """Pick N approved questions across the track's courses/lessons.

    Aims for type diversity: ≥1 MCQ, ≥1 TF, ≥1 FITB when available.
    Returns (assessment_dict, error_msg).
    Errors if fewer than 3 approved questions exist (min to publish).

    course_ids: if provided, only pull quizzes referenced by those courses.
                If None/empty, pull ALL approved quizzes (fallback for demo).
    """
    from quiz_store import QUESTION_TYPES  # type: ignore[import]

    # Collect approved questions grouped by type.
    pools: dict[str, list[tuple[str, int, dict]]] = {t: [] for t in QUESTION_TYPES}

    # Walk quizzes
    quiz_paths = sorted(_QUIZZES_DIR.glob("quiz-*.json"))
    for qp in quiz_paths:
        quiz = _read_json(qp)
        if quiz is None or quiz.get("status") != "approved":
            continue
        for i, q in enumerate(quiz.get("questions") or []):
            qtype = (q.get("type") or "mcq").lower()
            if qtype not in pools:
                qtype = "mcq"
            pools[qtype].append((quiz["id"], i, q))

    all_candidates: list[tuple[str, int, dict]] = []
    for t in QUESTION_TYPES:
        all_candidates.extend(pools[t])

    if len(all_candidates) < 3:
        return None, (
            f"only {len(all_candidates)} approved question(s) available — need at least 3"
        )

    # Shuffle each pool separately for diversity, then assemble.
    selected: list[tuple[str, int, dict]] = []
    remaining_n = n

    # Ensure type diversity: take 1 from each type if available.
    for qtype in QUESTION_TYPES:
        if not pools[qtype] or remaining_n <= 0:
            continue
        bucket = list(pools[qtype])
        random.shuffle(bucket)
        selected.append(bucket[0])
        pools[qtype] = bucket[1:]
        remaining_n -= 1

    # Fill remainder from the full shuffled pool (minus already-selected).
    selected_ptrs = {(qid, idx) for qid, idx, _ in selected}
    remainder_pool = [
        item for item in all_candidates
        if (item[0], item[1]) not in selected_ptrs
    ]
    random.shuffle(remainder_pool)
    for item in remainder_pool[:remaining_n]:
        selected.append(item)

    # Cap at n
    selected = selected[:n]

    question_ids = [f"{qid}:{idx}" for qid, idx, _ in selected]
    title = f"Track Assessment — {track_id}"

    assessment = create_assessment(
        title=title,
        track_id=track_id,
        question_ids=question_ids,
        time_limit_min=15,
        pass_pct=70,
        attempts_allowed=3,
    )
    return assessment, None


# ── Attempt persistence ───────────────────────────────────────────────────────

def _attempt_dir(user_id: str, aid: str) -> Path:
    return _ATTEMPTS_DIR / _safe_uid(user_id) / aid


def count_attempts(user_id: str, aid: str) -> int:
    d = _attempt_dir(user_id, aid)
    if not d.exists():
        return 0
    return sum(1 for p in d.glob("attempt_*.json") if p.is_file())


def get_attempts(user_id: str, aid: str) -> list[dict]:
    d = _attempt_dir(user_id, aid)
    if not d.exists():
        return []
    attempts: list[dict] = []
    for p in sorted(d.glob("attempt_*.json")):
        a = _read_json(p)
        if a:
            attempts.append(a)
    return attempts


def has_passing_attempt(user_id: str, aid: str, pass_pct: int) -> bool:
    for attempt in get_attempts(user_id, aid):
        if attempt.get("score_pct", 0) >= pass_pct:
            return True
    return False


def save_attempt(
    *,
    user_id: str,
    assessment_id: str,
    answers: dict[str, Any],
    score_pct: float,
    passed: bool,
    per_question: list[dict],
) -> dict:
    """Persist an attempt record and return it (without source quotes — those are
    in per_question which was generated by the scorer)."""
    n = count_attempts(user_id, assessment_id) + 1
    now = _now_iso()
    attempt = {
        "user_id": user_id,
        "assessment_id": assessment_id,
        "attempt_number": n,
        "answers": answers,
        "score_pct": round(float(score_pct)),
        "passed": bool(passed),
        "submitted_at": now,
    }
    p = _attempt_dir(user_id, assessment_id) / f"attempt_{n}.json"
    _write_json(p, attempt)
    return attempt


# ── Scoring ───────────────────────────────────────────────────────────────────

def score_attempt(
    assessment: dict,
    answers: dict[str, Any],
) -> tuple[float, bool, list[dict]]:
    """Score a taker's answers against the assessment's resolved questions.

    answers: {<ptr>: <answer_value>}
    Returns: (score_pct, passed, per_question_list_with_source_quotes)

    Source quotes ARE included in the returned per_question list — they will be
    revealed in the results screen (only after submission, not during the attempt).
    """
    from quiz_store import score_quiz  # type: ignore[import]

    resolved = get_questions(assessment, include_source_quotes=True)
    if not resolved:
        return 0.0, False, []

    # Build a quiz-shaped dict so we can reuse quiz_store.score_quiz.
    # score_quiz takes a list parallel to quiz.questions.
    answers_list: list[Any] = []
    for q in resolved:
        ptr = q.get("_ptr", "")
        ans = answers.get(ptr)
        answers_list.append(ans)

    # Synthesise a minimal quiz dict.
    synthetic_quiz = {"questions": resolved}
    result = score_quiz(synthetic_quiz, answers_list)

    correct = result.get("correct", 0)
    total = result.get("total", len(resolved))
    pct = round(100 * correct / total) if total else 0
    passed = pct >= assessment.get("pass_pct", 70)

    # Attach the _ptr back onto each per-question result for the UI.
    per_question = result.get("results", [])
    for i, r in enumerate(per_question):
        if i < len(resolved):
            r["_ptr"] = resolved[i].get("_ptr", "")

    return float(pct), passed, per_question
