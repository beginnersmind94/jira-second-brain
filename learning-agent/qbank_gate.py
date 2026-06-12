"""Question-bank grounding gate — the falsifiable keystone (build order: commit 1).

A banked question reaches `verified` only if ALL THREE pass, in this order:

  1. lane-match   (deterministic): the cited span's lane == the question's lane.
                  Purity's backstop — a POS (product) question can NEVER be grounded
                  in a food-safety (compliance) span even when they share a word like
                  "item" or "temperature". The lane is the first segment of every
                  span_id ("product:..." / "compliance:..."), so it's read, not inferred.

  2. verbatim     (deterministic): the quote is a verbatim substring of the immutable
                  source span. Catches fabricated / hallucinated quotes.

  3. support      (semantic, LLM judge): does the quote actually SUPPORT this stem+answer?
                  Catches the inversion verbatim cannot: "held at 135°F or higher" is a
                  MINIMUM; a stem asking the MAXIMUM with answer "135°F" is verbatim-true
                  yet semantically false. This is a GATE failure, not a generator-quality
                  issue, so it lives here — not in a separate eval.

Deterministic checks run first (free); the LLM judge runs only when they pass, so
cross-lane and fabricated-quote questions are rejected with zero model calls.

New question types (B1 — grounded question types beyond MCQ):
  Each type has a dedicated gate function (_gate_tf, _gate_fitb, _gate_ordering).
  A question that fails its gate is DROPPED (not modified) — same as MCQ behaviour.

  True/False (_gate_tf):
    source_span must appear verbatim in content (normalised whitespace).
    For FALSE questions, source_span is the REAL (true) span; the stem is a mechanical
    negation of it. The gate verifies the real span is present — it does NOT invent a
    negated span, and it does NOT introduce any uncited product claim.

  Fill-in-the-blank (_gate_fitb):
    stem.replace("___", answer) must reconstruct a verbatim substring of content
    (whitespace-normalised). This proves the blank is a verbatim word/phrase, not invented.

  Step-ordering (_gate_ordering):
    Every step in `steps` must appear verbatim as a substring in `source_quote`, AND
    `source_quote` itself must appear verbatim in content. Correct order is their
    appearance order in source_quote (the canonical source, not reconstruction).

  Gate failure = DROP. The caller (quiz_store.verify_question / _grounded_quiz)
  is responsible for discarding dropped questions; these functions only report pass/fail.
"""
import re

VALID_LANES = ("product", "compliance")

# Question types recognised by this module (B1 additions).
QUESTION_TYPES = ("mcq", "tf", "fitb", "ordering")


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip().lower()


def lane_of_span_id(span_id: str) -> str:
    """Lane is the first ':'-segment of the span_id. Source of truth for purity."""
    return (span_id or "").split(":", 1)[0].strip().lower()


def check_lane(question: dict, span: dict) -> bool:
    """Cited span's lane must equal the question's lane. We check BOTH the span's
    declared lane field and the lane encoded in its id — they must agree and match."""
    q_lane = (question.get("lane") or "").lower()
    span_lane = (span.get("lane") or "").lower()
    id_lane = lane_of_span_id(span.get("span_id", ""))
    return q_lane in VALID_LANES and span_lane == id_lane == q_lane


def check_verbatim(quote: str, span: dict) -> bool:
    nq = _norm(quote)
    return bool(nq) and nq in _norm(span.get("text", ""))


# ── B1: Deterministic per-type gate functions ─────────────────────────────────
# Each returns {"pass": bool, "reason": str}.  Callers DROP on fail.

def _gate_tf(question: dict, content: str) -> dict:
    """Gate for True/False questions.

    The source_span must appear verbatim (normalised) in content.
    For TRUE questions, the stem IS the source_span (or a reformatting of it).
    For FALSE questions, source_span is the real/true span; the stem is a mechanical
    negation. In both cases the gate ONLY checks source_span — it cannot validate
    that the negation is well-formed (that is a generation-time concern), but it
    does guarantee that the underlying span exists in the source.
    """
    source_span = (question.get("source_span") or "").strip()
    if not source_span:
        return {"pass": False, "reason": "TF: missing source_span"}
    nc = _norm(content)
    ns = _norm(source_span)
    if not ns:
        return {"pass": False, "reason": "TF: source_span is empty after normalisation"}
    if ns not in nc:
        return {"pass": False, "reason": "TF: source_span not found verbatim in content"}
    # For a FALSE question, the distractor_basis must be present and declare 'negation'.
    correct = question.get("correct")
    if correct is False:
        db = question.get("distractor_basis") or {}
        transform = (db.get("transform") or "").lower()
        if transform != "negation":
            return {"pass": False,
                    "reason": "TF(FALSE): distractor_basis.transform must be 'negation'; "
                              "other transforms are not valid (they could introduce uncited claims)"}
    return {"pass": True, "reason": "ok"}


def _gate_fitb(question: dict, content: str) -> dict:
    """Gate for Fill-in-the-blank questions.

    stem.replace('___', answer) must reconstruct a verbatim substring of content
    (normalised whitespace). This proves both that the blank target is a real span and
    that the surrounding sentence was not paraphrased.
    """
    stem = (question.get("stem") or "")
    answer = (question.get("answer") or "").strip()
    if "___" not in stem:
        return {"pass": False, "reason": "FITB: stem must contain '___' as the blank marker"}
    if not answer:
        return {"pass": False, "reason": "FITB: answer is empty"}
    reconstructed = stem.replace("___", answer)
    nr = _norm(reconstructed)
    nc = _norm(content)
    if not nr:
        return {"pass": False, "reason": "FITB: reconstructed sentence is empty after normalisation"}
    if nr not in nc:
        return {"pass": False,
                "reason": "FITB: stem.replace('___', answer) does not appear verbatim in content "
                          "(blank may be paraphrased or sentence is not from the source)"}
    return {"pass": True, "reason": "ok"}


def _gate_ordering(question: dict, content: str) -> dict:
    """Gate for Step-ordering questions.

    Every step in `steps` must appear verbatim (as a substring) in `source_quote`,
    AND `source_quote` itself must appear verbatim in content. This ensures:
    - Steps are real, not invented.
    - The ordering source is in the guide.
    - No step was imported from outside the cited section.
    """
    source_quote = (question.get("source_quote") or "").strip()
    steps = question.get("steps") or []
    if not source_quote:
        return {"pass": False, "reason": "ORDERING: missing source_quote"}
    if len(steps) < 2:
        return {"pass": False, "reason": "ORDERING: need at least 2 steps to order"}
    nsq = _norm(source_quote)
    nc = _norm(content)
    if nsq not in nc:
        return {"pass": False, "reason": "ORDERING: source_quote not found verbatim in content"}
    for i, step in enumerate(steps):
        ns = _norm(str(step))
        if not ns:
            return {"pass": False, "reason": f"ORDERING: step {i} is empty"}
        if ns not in nsq:
            return {"pass": False,
                    "reason": f"ORDERING: step {i} ({str(step)[:60]!r}) not found verbatim in source_quote "
                              "(invented step or taken from outside the cited section)"}
    return {"pass": True, "reason": "ok"}


def gate_question_by_type(question: dict, content: str) -> dict:
    """Route to the correct deterministic gate based on question type.
    Returns {"pass": bool, "reason": str}.  Callers DROP on fail.

    MCQ questions are not handled here (they use the 3-step span-based gate in
    gate_question() which also runs the LLM support judge). This function is the
    deterministic-only gate for the three B1 types; it is called by quiz_store
    verify_question() and by the scoring / approval paths.
    """
    qtype = (question.get("type") or "mcq").lower()
    if qtype == "tf":
        return _gate_tf(question, content)
    if qtype == "fitb":
        return _gate_fitb(question, content)
    if qtype == "ordering":
        return _gate_ordering(question, content)
    # Unknown type: fail safely rather than silently pass.
    if qtype != "mcq":
        return {"pass": False, "reason": f"Unknown question type '{qtype}'"}
    return {"pass": True, "reason": "mcq — handled by gate_question()"}


async def llm_support_judge(quote: str, stem: str, correct_answer: str) -> dict:
    """Real semantic judge via the Claude Agent SDK. Returns {ok, reason}."""
    from claude_agent_sdk import ClaudeAgentOptions, query, AssistantMessage, TextBlock
    sys_prompt = (
        "You are a strict grounding judge for a training quiz. Given a SOURCE quote and a "
        "quiz STEM with its PROPOSED CORRECT ANSWER, decide whether the source quote, read "
        "literally, supports that this answer is correct AS THE ANSWER TO THIS STEM. Two "
        "conditions must BOTH hold: (1) the quote supports the answer's claim, and (2) the "
        "answer is RESPONSIVE to what the stem actually asks. Watch for: inversions (a "
        "minimum stated as a maximum or vice-versa); number/unit mismatches; claims the "
        "quote does not make; and ROLE/ACTOR mismatch — when the stem asks WHO (or what) "
        "does, causes, or performs something, the quote must show the named party actually "
        "does it, not merely that the party benefits from it, receives it, is affected by "
        "it, or is mentioned nearby. In particular, 'allows / enables / lets / permits "
        "[party] to do X' grants that party a capability or benefit — it does NOT make "
        "them the party responsible for producing or originating X. A statement that is "
        "true and quote-supported but does "
        "not answer THIS stem is NOT support. If either condition fails, say NO. Reply with "
        "exactly YES or NO on the first line, then a one-line reason."
    )
    prompt = (f'SOURCE: "{quote}"\n\nSTEM: {stem}\nPROPOSED CORRECT ANSWER: {correct_answer}\n\n'
              f"Does the source literally support this answer?")
    opts = ClaudeAgentOptions(model="claude-sonnet-4-6", system_prompt=sys_prompt,
                              allowed_tools=[], disallowed_tools=[], tools=[], max_turns=1)
    parts = []
    async for m in query(prompt=prompt, options=opts):
        if isinstance(m, AssistantMessage):
            for b in m.content:
                if isinstance(b, TextBlock):
                    parts.append(b.text)
    text = "\n".join(parts).strip()
    ok = text.upper().lstrip().startswith("Y")
    return {"ok": ok, "reason": text[:200]}


async def gate_question(q: dict, spans_by_id: dict, judge=llm_support_judge) -> dict:
    """Run the three-check gate on one MCQ question. Returns a verdict dict.
    `judge` is injectable so tests can stub the semantic step if desired.

    For non-MCQ types use gate_question_by_type() which is deterministic-only."""
    res = {"lane_ok": False, "verbatim_ok": None, "support_ok": None,
           "verdict": "fail", "reasons": []}
    span = spans_by_id.get(q.get("cite_span_id"))
    if not span:
        res["reasons"].append(f"cited span '{q.get('cite_span_id')}' not found")
        return res

    res["lane_ok"] = check_lane(q, span)
    if not res["lane_ok"]:
        res["reasons"].append(
            f"CROSS-LANE: question lane '{q.get('lane')}' != span lane "
            f"'{span.get('lane')}' (span {span.get('span_id')})")
        return res  # hard stop — no model call

    res["verbatim_ok"] = check_verbatim(q.get("quote", ""), span)
    if not res["verbatim_ok"]:
        res["reasons"].append("quote is not a verbatim substring of the source span")
        return res  # hard stop — no model call

    correct = (q.get("options") or [None])[q.get("correct_index", 0)]
    verdict = await judge(q.get("quote", ""), q.get("stem", ""), correct)
    res["support_ok"] = bool(verdict.get("ok"))
    if not res["support_ok"]:
        res["reasons"].append("SEMANTIC: quote does not support stem+answer — " + verdict.get("reason", ""))
    res["verdict"] = "pass" if res["support_ok"] else "fail"
    return res
