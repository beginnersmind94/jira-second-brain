"""quiz_store.py — persistence + QA/grounding gate + drift detection for the Quiz Builder.

A quiz is grounded-by-construction the SAME way guides are: every question carries a
verbatim `source_quote` that must be a substring of the SOURCE CONTENT the quiz was built
from. The deterministic QA gate is the machine floor; SME approval is the human floor —
this mirrors the guide pipeline (demo.validate_citations + approve_resource) exactly, so
the trust guarantee ("never present an AI claim that isn't traceable") extends to quizzes.

Per-question provenance (honest badge — never let a manual question masquerade as grounded):
  ai_grounded       AI-made, source_quote verbatim in source            -> grounded
  human_edited      author edited an AI question; re-verified on save    -> grounded iff quote still verbatim
  manual_grounded   author wrote it + a span that IS verbatim in source  -> grounded
  manual_unverified author wrote it, no verifiable span                  -> NOT grounded; needs explicit
                    SME sign-off (sme_verified=true) before a quiz can be approved.

Question types (B1):
  mcq      — multiple-choice (original); 4 options, answer_index 0–3.
  tf       — True/False; correct (bool), source_span, distractor_basis.
  fitb     — Fill-in-the-blank; stem with "___", answer, source_sentence.
  ordering — Step-ordering; steps list, correct_order, source_quote.

  All types are subject to the same approval gate: no question is approved unless it is
  grounded (i.e. its primary span is a verbatim substring of the current source content)
  or SME-signed-off (sme_verified=true).

Drift: `source_content_hash` is stamped at build time. When the underlying guide/asset is
edited or regenerated, the hash no longer matches the live source — the quiz is flagged
stale and (by policy) an approved quiz drops back to draft. The eval agent
(`eval/quiz_qa_agent.py`) is the monitor; `qa_gate()` here is the gate that prevents a
drifted/ungrounded quiz from being approved in the first place.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
import uuid
from pathlib import Path

import qbank_gate

BASE = Path(__file__).resolve().parent
QUIZZES = BASE / "quizzes"
QUIZZES.mkdir(parents=True, exist_ok=True)

PROVENANCE = ("ai_grounded", "human_edited", "manual_grounded", "manual_unverified")
# All recognised question types. MCQ is the original; the rest are B1 additions.
QUESTION_TYPES = ("mcq", "tf", "fitb", "ordering")
MIN_Q, MAX_Q = 3, 10


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip().lower()


def source_hash(text: str) -> str:
    return hashlib.sha256(_norm(text).encode("utf-8")).hexdigest()[:16]


def _slug(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9\-]+", "-", text or "").strip("-").lower()
    return s[:40] or "quiz"


def new_quiz_id(source_id: str = "") -> str:
    return f"quiz-{_slug(source_id)}-{uuid.uuid4().hex[:6]}"


def quiz_path(qid: str) -> Path:
    return QUIZZES / f"{qid}.json"


def save_quiz(quiz: dict, *, now: str | None = None) -> dict:
    quiz["updated_at"] = now or time.strftime("%Y-%m-%dT%H:%M:%S")
    quiz.setdefault("created_at", quiz["updated_at"])
    quiz_path(quiz["id"]).write_text(json.dumps(quiz, indent=2, ensure_ascii=False), encoding="utf-8")
    return quiz


def load_quiz(qid: str) -> dict | None:
    p = quiz_path(qid)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def list_quizzes() -> list[dict]:
    out = []
    for p in sorted(QUIZZES.glob("quiz-*.json")):
        try:
            q = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        qs = q.get("questions") or []
        out.append({
            "id": q.get("id"), "title": q.get("title"), "status": q.get("status", "draft"),
            "source_type": q.get("source_type"), "source_id": q.get("source_id"),
            "source_label": q.get("source_label"), "total": len(qs),
            "grounded": sum(1 for x in qs if x.get("grounded")),
            "manual_unverified": sum(1 for x in qs if not x.get("grounded")),
            "stale": bool(q.get("stale")), "updated_at": q.get("updated_at"),
        })
    out.sort(key=lambda r: r.get("updated_at") or "", reverse=True)
    return out


def delete_quiz(qid: str) -> bool:
    p = quiz_path(qid)
    if p.exists():
        p.unlink()
        return True
    return False


# ── Grounding (the keystone) ──────────────────────────────────────────────────

def _primary_span(q: dict) -> str:
    """Return the primary verbatim span for this question, regardless of type.

    For MCQ and TF: source_quote (MCQ) or source_span (TF).
    For FITB: source_sentence (the full verbatim sentence).
    For ORDERING: source_quote (the workflow section that contains all steps).

    This is the span the grounding gate checks for drift/verbatim correctness.
    """
    qtype = (q.get("type") or "mcq").lower()
    if qtype == "tf":
        return (q.get("source_span") or q.get("source_quote") or "").strip()
    if qtype == "fitb":
        return (q.get("source_sentence") or "").strip()
    # mcq and ordering both use source_quote
    return (q.get("source_quote") or "").strip()


def verify_question(q: dict, source_text: str) -> dict:
    """Set q['grounded'] from whether its primary span is a VERBATIM substring of the
    current source. For B1 types (tf, fitb, ordering) also runs the type-specific gate
    from qbank_gate to catch structural violations (e.g. FITB blank is paraphrased).

    Adjusts provenance honestly: a manual question that gains a valid span upgrades to
    manual_grounded; any question that LOSES its span (e.g. after an edit, or after the
    source drifted) is demoted to manual_unverified. Mutates + returns q.
    """
    qtype = (q.get("type") or "mcq").lower()
    prov = q.get("provenance") or "manual_unverified"

    if qtype in ("tf", "fitb", "ordering"):
        # Run the deterministic per-type gate.
        gate_result = qbank_gate.gate_question_by_type(q, source_text)
        matched = gate_result["pass"]
        if matched:
            q["grounded"] = True
            if prov == "manual_unverified":
                q["provenance"] = "manual_grounded"
        else:
            q["grounded"] = False
            q.setdefault("gate_reason", gate_result["reason"])
            if prov in ("ai_grounded", "manual_grounded"):
                q["provenance"] = "human_edited" if prov == "ai_grounded" else "manual_unverified"
            if prov == "human_edited":
                q["provenance"] = "manual_unverified"
        return q

    # MCQ (and unknown types): fall back to simple verbatim substring check on source_quote.
    span = _primary_span(q)
    matched = bool(span) and _norm(span) in _norm(source_text)
    if matched:
        q["grounded"] = True
        if prov == "manual_unverified":
            q["provenance"] = "manual_grounded"
    else:
        q["grounded"] = False
        if prov in ("ai_grounded", "manual_grounded"):
            q["provenance"] = "human_edited" if prov == "ai_grounded" else "manual_unverified"
        if prov == "human_edited":
            q["provenance"] = "manual_unverified"
    return q


def validate_shape(q: dict) -> list[str]:
    """Shape validation per question type. Returns list of error strings (empty = ok)."""
    errs: list[str] = []
    qtype = (q.get("type") or "mcq").lower()

    if qtype == "mcq":
        if not (q.get("stem") or "").strip():
            errs.append("MCQ: empty question stem")
        opts = q.get("options") or []
        if len(opts) != 4 or any(not (str(o).strip()) for o in opts):
            errs.append("MCQ: must have exactly 4 non-empty options")
        ai = q.get("answer_index")
        if not isinstance(ai, int) or not (0 <= ai < 4):
            errs.append("MCQ: answer_index must be 0–3")

    elif qtype == "tf":
        if not (q.get("stem") or "").strip():
            errs.append("TF: empty question stem")
        if not isinstance(q.get("correct"), bool):
            errs.append("TF: 'correct' must be true or false (boolean)")
        if not (q.get("source_span") or "").strip():
            errs.append("TF: missing source_span")
        # FALSE questions must have distractor_basis.transform == 'negation'
        if q.get("correct") is False:
            db = q.get("distractor_basis") or {}
            if (db.get("transform") or "").lower() != "negation":
                errs.append("TF(FALSE): distractor_basis.transform must be 'negation'")

    elif qtype == "fitb":
        stem = q.get("stem") or ""
        if "___" not in stem:
            errs.append("FITB: stem must contain '___' as the blank marker")
        if not (q.get("answer") or "").strip():
            errs.append("FITB: missing answer")
        if not (q.get("source_sentence") or "").strip():
            errs.append("FITB: missing source_sentence")

    elif qtype == "ordering":
        steps = q.get("steps") or []
        if len(steps) < 2:
            errs.append("ORDERING: need at least 2 steps")
        co = q.get("correct_order") or []
        if len(co) != len(steps):
            errs.append("ORDERING: correct_order length must match steps length")
        if sorted(co) != list(range(len(steps))):
            errs.append("ORDERING: correct_order must be a permutation of 0..N-1")
        if not (q.get("source_quote") or "").strip():
            errs.append("ORDERING: missing source_quote")

    else:
        errs.append(f"unknown question type '{qtype}'")

    return errs


def _dedupe_warnings(questions: list[dict]) -> list[str]:
    warns: list[str] = []
    seen_stem: dict[str, int] = {}
    seen_quote: dict[str, int] = {}
    for i, q in enumerate(questions):
        s = _norm(q.get("stem", ""))
        qt = _norm(_primary_span(q))
        if s and s in seen_stem:
            warns.append(f"Q{i + 1} duplicates Q{seen_stem[s] + 1} (same stem)")
        elif s:
            seen_stem[s] = i
        if qt and qt in seen_quote:
            warns.append(f"Q{i + 1} reuses the same source span as Q{seen_quote[qt] + 1}")
        elif qt:
            seen_quote[qt] = i
    return warns


def qa_gate(quiz: dict, source_text: str) -> dict:
    """Deterministic QA. Mutates each question's grounded/provenance against the CURRENT
    source, then returns a report. `ok` is False (approval blocked) if any blocking issue.

    Handles all question types (mcq, tf, fitb, ordering) through verify_question() which
    dispatches to the appropriate gate in qbank_gate.py.

    Blocking: count < MIN_Q or > MAX_Q; any shape error; any not-grounded question that
    isn't SME-signed-off. Warnings (non-blocking): dedupe; source drift (hash mismatch)."""
    qs = quiz.get("questions") or []
    blocking: list[str] = []
    warnings: list[str] = []

    if len(qs) < MIN_Q:
        blocking.append(f"need at least {MIN_Q} questions (have {len(qs)})")
    if len(qs) > MAX_Q:
        blocking.append(f"at most {MAX_Q} questions (have {len(qs)})")

    for i, q in enumerate(qs):
        for e in validate_shape(q):
            blocking.append(f"Q{i + 1}: {e}")
        verify_question(q, source_text)
        if not q.get("grounded") and not q.get("sme_verified"):
            blocking.append(f"Q{i + 1}: manual question not source-verified — needs SME sign-off")

    warnings += _dedupe_warnings(qs)

    drifted = bool(quiz.get("source_content_hash")) and quiz["source_content_hash"] != source_hash(source_text)
    if drifted:
        warnings.append("source content changed since this quiz was built — questions re-checked against the new source")

    return {
        "ok": not blocking,
        "blocking": blocking,
        "warnings": warnings,
        "total": len(qs),
        "grounded": sum(1 for q in qs if q.get("grounded")),
        "manual_unverified": sum(1 for q in qs if not q.get("grounded")),
        "drifted": drifted,
    }


# ── Construction ──────────────────────────────────────────────────────────────

def map_generated_question(g: dict) -> dict:
    """Map a question from the grounded generator into the quiz-store question shape.

    Handles both the original MCQ shape ({q, options, answer, explanation, source_quote,
    excerpt_id|chunk_id}) and the B1 type shapes (type field present, type-specific fields).
    """
    qtype = (g.get("type") or "mcq").lower()

    if qtype == "tf":
        return {
            "type": "tf",
            "stem": g.get("stem") or g.get("q") or "",
            "correct": bool(g.get("correct")),
            "source_span": (g.get("source_span") or g.get("source_quote") or "").strip(),
            "distractor_basis": g.get("distractor_basis") or {},
            "section": g.get("section") or g.get("source_ref") or "",
            "explanation": g.get("explanation", ""),
            "provenance": "ai_grounded",
            "grounded": True,
            "sme_verified": False,
        }

    if qtype == "fitb":
        return {
            "type": "fitb",
            "stem": g.get("stem") or g.get("q") or "",
            "answer": (g.get("answer") or "").strip(),
            "source_sentence": (g.get("source_sentence") or g.get("source_quote") or "").strip(),
            "section": g.get("section") or g.get("source_ref") or "",
            "explanation": g.get("explanation", ""),
            "provenance": "ai_grounded",
            "grounded": True,
            "sme_verified": False,
        }

    if qtype == "ordering":
        steps = list(g.get("steps") or [])
        correct_order = list(g.get("correct_order") or list(range(len(steps))))
        return {
            "type": "ordering",
            "prompt": g.get("prompt") or "Put these steps in the correct order:",
            "steps": steps,
            "correct_order": correct_order,
            "source_quote": (g.get("source_quote") or "").strip(),
            "section": g.get("section") or g.get("source_ref") or "",
            "explanation": g.get("explanation", ""),
            "provenance": "ai_grounded",
            "grounded": True,
            "sme_verified": False,
        }

    # Default: MCQ (original shape)
    return {
        "type": "mcq",
        "stem": g.get("q") or g.get("stem") or "",
        "options": list(g.get("options") or [])[:4],
        "answer_index": int(g.get("answer", g.get("answer_index", 0)) or 0),
        "explanation": g.get("explanation", ""),
        "source_quote": (g.get("source_quote") or "").strip(),
        "source_ref": g.get("excerpt_id") or g.get("chunk_id") or g.get("source_ref") or "",
        "provenance": "ai_grounded",
        "grounded": True,
        "sme_verified": False,
    }


def build_quiz(*, source_type: str, source_id: str, source_label: str, title: str,
               generated_questions: list[dict], source_text: str) -> dict:
    """Assemble a new draft quiz from generator output and stamp the source hash."""
    quiz = {
        "id": new_quiz_id(source_id),
        "title": title or f"Quiz — {source_label or source_id}",
        "status": "draft",
        "source_type": source_type,
        "source_id": source_id,
        "source_label": source_label,
        "source_content_hash": source_hash(source_text),
        "questions": [map_generated_question(g) for g in generated_questions],
        "stale": False,
    }
    for q in quiz["questions"]:
        verify_question(q, source_text)
    return save_quiz(quiz)


def blank_question() -> dict:
    """Blank MCQ question (unchanged from original — manual questions default to MCQ)."""
    return {"type": "mcq", "stem": "", "options": ["", "", "", ""], "answer_index": 0,
            "explanation": "", "source_quote": "", "source_ref": "",
            "provenance": "manual_unverified", "grounded": False, "sme_verified": False}


def _score_tf(q: dict, submitted) -> dict:
    """Score a True/False submission. submitted: bool or 'true'/'false' string."""
    if isinstance(submitted, str):
        submitted = submitted.lower().strip() == "true"
    correct_val = q.get("correct")
    ok = (submitted is True) == (correct_val is True)
    return {
        "type": "tf", "correct": ok, "submitted": submitted,
        "correct_answer": correct_val,
        "source_quote": q.get("source_span") or q.get("source_span") or "",
        "section": q.get("section", ""),
        "explanation": q.get("explanation", ""),
        "grounded": bool(q.get("grounded")),
    }


def _score_fitb(q: dict, submitted) -> dict:
    """Score a Fill-in-the-blank submission. Case-insensitive strip comparison."""
    submitted_str = str(submitted or "").strip()
    answer = (q.get("answer") or "").strip()
    ok = submitted_str.lower() == answer.lower()
    return {
        "type": "fitb", "correct": ok, "submitted": submitted_str,
        "correct_answer": answer,
        "source_quote": q.get("source_sentence") or "",
        "section": q.get("section", ""),
        "explanation": q.get("explanation", ""),
        "grounded": bool(q.get("grounded")),
    }


def _score_ordering(q: dict, submitted) -> dict:
    """Score a step-ordering submission. submitted: list of ints (user's claimed order).
    Each element is the index into q['steps'] that the user placed at that position.
    Compared against correct_order."""
    correct_order = list(q.get("correct_order") or [])
    steps = list(q.get("steps") or [])
    if not isinstance(submitted, list):
        submitted = []
    # Normalise to ints
    try:
        sub_ints = [int(x) for x in submitted]
    except (TypeError, ValueError):
        sub_ints = []
    ok = sub_ints == correct_order
    # Per-step correctness (for UI highlighting)
    step_results = []
    for pos, step in enumerate(steps):
        if pos < len(sub_ints):
            expected_at_pos = correct_order[pos] if pos < len(correct_order) else None
            step_results.append({
                "step": step,
                "placed_at": sub_ints[pos] if pos < len(sub_ints) else None,
                "correct_pos": correct_order.index(pos) if pos in correct_order else None,
                "correct": sub_ints[pos] == correct_order[pos] if pos < len(sub_ints) and pos < len(correct_order) else False,
            })
    return {
        "type": "ordering", "correct": ok, "submitted": sub_ints,
        "correct_order": correct_order,
        "step_results": step_results,
        "source_quote": q.get("source_quote") or "",
        "section": q.get("section", ""),
        "explanation": q.get("explanation", ""),
        "grounded": bool(q.get("grounded")),
    }


def score_quiz(quiz: dict, answers: list) -> dict:
    """Score a taker submission. Returns per-question correctness + the source span that
    proves the right answer (the trust payoff: every answer is explained from the source).

    Handles all question types: mcq, tf, fitb, ordering. The `answers` list is parallel
    to the quiz's questions list. Each element is type-appropriate:
      mcq:      int (option index)
      tf:       bool or 'true'/'false'
      fitb:     str
      ordering: list[int]
    """
    qs = quiz.get("questions") or []
    results = []
    correct_count = 0
    for i, q in enumerate(qs):
        ans = answers[i] if i < len(answers) else None
        qtype = (q.get("type") or "mcq").lower()

        if qtype == "tf":
            r = _score_tf(q, ans)
        elif qtype == "fitb":
            r = _score_fitb(q, ans)
        elif qtype == "ordering":
            r = _score_ordering(q, ans)
        else:
            # MCQ (default)
            chosen = ans if isinstance(ans, int) else None
            right = q.get("answer_index", 0)
            ok = chosen == right
            r = {
                "type": "mcq", "correct": ok, "chosen": chosen, "answer_index": right,
                "options": q.get("options", []), "explanation": q.get("explanation", ""),
                "source_quote": q.get("source_quote", ""), "grounded": bool(q.get("grounded")),
            }

        r["stem"] = q.get("stem", q.get("prompt", ""))
        if r.get("correct"):
            correct_count += 1
        results.append(r)

    total = len(qs)
    return {"correct": correct_count, "total": total,
            "pct": round(100 * correct_count / total) if total else 0, "results": results}
