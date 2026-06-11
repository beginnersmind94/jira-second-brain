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

BASE = Path(__file__).resolve().parent
QUIZZES = BASE / "quizzes"
QUIZZES.mkdir(parents=True, exist_ok=True)

PROVENANCE = ("ai_grounded", "human_edited", "manual_grounded", "manual_unverified")
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

def verify_question(q: dict, source_text: str) -> dict:
    """Set q['grounded'] from whether its source_quote is a VERBATIM substring of the
    current source. Adjusts provenance honestly: a manual question that gains a valid
    span upgrades to manual_grounded; any question that LOSES its span (e.g. after an
    edit, or after the source drifted) is demoted to manual_unverified. Mutates + returns q."""
    quote = (q.get("source_quote") or "").strip()
    matched = bool(quote) and _norm(quote) in _norm(source_text)
    prov = q.get("provenance") or "manual_unverified"
    if matched:
        q["grounded"] = True
        if prov == "manual_unverified":
            q["provenance"] = "manual_grounded"
    else:
        q["grounded"] = False
        if prov in ("ai_grounded", "manual_grounded"):
            # had grounding, lost it (edit or drift): demote, force re-verification
            q["provenance"] = "human_edited" if prov == "ai_grounded" else "manual_unverified"
        if prov == "human_edited":
            q["provenance"] = "manual_unverified"
    return q


def validate_shape(q: dict) -> list[str]:
    errs: list[str] = []
    if not (q.get("stem") or "").strip():
        errs.append("empty question stem")
    opts = q.get("options") or []
    if len(opts) != 4 or any(not (str(o).strip()) for o in opts):
        errs.append("must have exactly 4 non-empty options")
    ai = q.get("answer_index")
    if not isinstance(ai, int) or not (0 <= ai < 4):
        errs.append("answer_index must be 0–3")
    return errs


def _dedupe_warnings(questions: list[dict]) -> list[str]:
    warns: list[str] = []
    seen_stem: dict[str, int] = {}
    seen_quote: dict[str, int] = {}
    for i, q in enumerate(questions):
        s = _norm(q.get("stem", ""))
        qt = _norm(q.get("source_quote", ""))
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
    """Map a question from the grounded generator (_grounded_quiz / icn_quiz shape:
    {q, options, answer, explanation, source_quote, excerpt_id|chunk_id}) into the
    quiz-store question shape."""
    return {
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
    return {"stem": "", "options": ["", "", "", ""], "answer_index": 0, "explanation": "",
            "source_quote": "", "source_ref": "", "provenance": "manual_unverified",
            "grounded": False, "sme_verified": False}


def score_quiz(quiz: dict, answers: list) -> dict:
    """Score a taker submission. Returns per-question correctness + the source span that
    proves the right answer (the trust payoff: every answer is explained from the source)."""
    qs = quiz.get("questions") or []
    results = []
    correct = 0
    for i, q in enumerate(qs):
        chosen = answers[i] if i < len(answers) and isinstance(answers[i], int) else None
        right = q.get("answer_index", 0)
        ok = chosen == right
        correct += 1 if ok else 0
        results.append({
            "stem": q.get("stem", ""), "chosen": chosen, "answer_index": right, "correct": ok,
            "options": q.get("options", []), "explanation": q.get("explanation", ""),
            "source_quote": q.get("source_quote", ""), "grounded": bool(q.get("grounded")),
        })
    total = len(qs)
    return {"correct": correct, "total": total,
            "pct": round(100 * correct / total) if total else 0, "results": results}
