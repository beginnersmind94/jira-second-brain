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
"""
import re

VALID_LANES = ("product", "compliance")


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


async def llm_support_judge(quote: str, stem: str, correct_answer: str) -> dict:
    """Real semantic judge via the Claude Agent SDK. Returns {ok, reason}."""
    from claude_agent_sdk import ClaudeAgentOptions, query, AssistantMessage, TextBlock
    sys_prompt = (
        "You are a strict grounding judge for a training quiz. Given a SOURCE quote and a "
        "quiz STEM with its PROPOSED CORRECT ANSWER, decide ONLY whether the source quote, "
        "read literally, supports that this answer is correct. Watch for: inversions (a "
        "minimum stated as a maximum or vice-versa), number/unit mismatches, and claims the "
        "quote does not actually make. If the quote does not clearly and literally support "
        "the answer, say NO. Reply with exactly YES or NO on the first line, then a one-line reason."
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
    """Run the three-check gate on one question. Returns a verdict dict.
    `judge` is injectable so tests can stub the semantic step if desired."""
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
