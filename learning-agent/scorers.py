"""Rubric scorers for the Quality dashboard — Coverage, Clarity, Structure.

These replace the seeded _DEMO values for resources that have gone through the
generation pipeline (Task 1–4 + Evaluator). Grounding remains a separate, hard-
enforced gate (validate_citations); these three are advisory measurements.

All three return int 1–5 or None when not enough data is available.

Architecture note (CLAUDE.md §Enforcement vs documentation):
    - score_coverage: reads evaluator check results (advisory LLM output) + Task 2
      plan (unexplained omissions). Neither is hard-enforced — both are advisory.
    - score_clarity: deterministic heuristics on the draft HTML (no LLM call).
      This is the cheapest scorer and the only one that runs always.
    - score_structure: deterministic heading presence check (no LLM call).
"""
from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from evaluator_runner import EvaluatorVerdict
    from agent_tasks import TaskResult

# ─────────────────────────────────────────────────────────────────────────────
# Template targets (word counts and required section headings)
# From CLAUDE.md §Template Definitions.
# ─────────────────────────────────────────────────────────────────────────────

# Approximate word-count targets per template type.
_TEMPLATE_WORD_TARGETS: dict[str, int] = {
    "long-form": 4000,
    "micro-guide": 800,
    "micro": 800,          # alias used in some meta JSON
    "tldr": 200,
    "release-notes": 400,  # not a formal template type but may appear in fixtures
}

# Required section headings for each template type.
# These are the heading labels from CLAUDE.md §Template Definitions.
# Matching is case-insensitive substring — "overview" matches any <h*> containing it.
_REQUIRED_HEADINGS: dict[str, list[str]] = {
    "long-form": [
        "overview",
        "roles",
        "prerequisites",
        "workflow",
        "troubleshoot",
        "sources",
    ],
    "micro-guide": [
        "purpose",
        "before you start",
        "workflow",
        "related",
    ],
    "micro": [
        "purpose",
        "before you start",
        "workflow",
        "related",
    ],
    "tldr": [
        "what this module does",
        "key features",
        "who uses",
        "workflow",
        "gotcha",
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _extract_headings(draft_html: str) -> list[str]:
    """Return a list of normalised heading texts found in the draft HTML."""
    pattern = re.compile(r"<h[1-6][^>]*>(.*?)</h[1-6]>", re.IGNORECASE | re.DOTALL)
    headings = []
    for m in pattern.finditer(draft_html or ""):
        # Strip any inner HTML tags (e.g. <strong>) to get plain text.
        text = re.sub(r"<[^>]+>", "", m.group(1))
        # Decode common HTML entities.
        for a, b in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                     ("&quot;", '"'), ("&#39;", "'"), ("&nbsp;", " ")):
            text = text.replace(a, b)
        headings.append(text.strip().lower())
    return headings


def _count_words(draft_html: str) -> int:
    """Rough word count on draft HTML: strip tags, split on whitespace."""
    if not draft_html:
        return 0
    # Remove <!-- Source: ... --> citation comments (they don't count as content words).
    text = re.sub(r"<!--.*?-->", " ", draft_html, flags=re.DOTALL)
    # Remove HTML tags.
    text = re.sub(r"<[^>]+>", " ", text)
    # Decode entities.
    for a, b in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                 ("&quot;", '"'), ("&#39;", "'"), ("&nbsp;", " ")):
        text = text.replace(a, b)
    return len(text.split())


def _clamp(value: float, lo: int = 1, hi: int = 5) -> int:
    """Clamp a float to [lo, hi] and return as int."""
    return max(lo, min(hi, round(value)))


# ─────────────────────────────────────────────────────────────────────────────
# score_coverage
# ─────────────────────────────────────────────────────────────────────────────

def score_coverage(
    task_result: "TaskResult | None",
    evaluator_verdict: "EvaluatorVerdict | None",
) -> int | None:
    """Derive a 1–5 coverage score from the evaluator verdict + Task 2 plan.

    Algorithm:
      1. Look for coverage-related checks in evaluator_verdict.checks.
         - "pass" -> base 5, "warn" -> base 3, "fail" -> base 1.
         - If no coverage check exists, the evaluator didn't measure coverage.
      2. Count unexplained omissions in task_result.task2 (the content plan).
         - Each feature in "omitted" that has no "reason" field docks 1 point.
      3. If neither source is available, return None (not measured).

    Returns int 1–5 or None.
    """
    base: int | None = None

    # Step 1: evaluator checks
    if evaluator_verdict is not None:
        checks = evaluator_verdict.checks or []
        coverage_checks = [
            c for c in checks
            if any(kw in (c.get("name") or "").lower()
                   for kw in ("coverage", "omission", "completeness"))
        ]
        if coverage_checks:
            # If any fail -> 1; if any warn -> 3; all pass -> 5.
            statuses = {c.get("status", "").lower() for c in coverage_checks}
            if "fail" in statuses:
                base = 1
            elif "warn" in statuses:
                base = 3
            else:
                base = 5

    # Step 2: unexplained omissions from Task 2 plan
    unexplained = 0
    if task_result is not None:
        plan = getattr(task_result, "task2", None) or {}
        omitted = plan.get("omitted") or []
        for item in omitted:
            reason = (item.get("reason") or "").strip()
            if not reason:
                unexplained += 1

    if base is None and unexplained == 0 and task_result is None and evaluator_verdict is None:
        return None

    # If base is still None (no coverage check found) but we have task_result data,
    # start from 5 and dock for omissions.
    if base is None:
        if task_result is None:
            return None   # no data at all
        base = 5

    score = base - unexplained
    return _clamp(score)


# ─────────────────────────────────────────────────────────────────────────────
# score_clarity
# ─────────────────────────────────────────────────────────────────────────────

def score_clarity(draft_html: str, template_type: str = "") -> int:
    """Derive a 1–5 clarity score from heuristics on the draft HTML. No LLM call.

    Algorithm:
      1. Word count vs template target (+/- 20% -> 5, +/- 50% -> 3, > 2x -> 1).
      2. Each [TO VERIFY] marker docks 0.5 (capped at -2).
      3. Each [AMBIGUOUS] marker docks 0.25 (capped at -1).

    Returns int 1–5. Always returns a value (defaults to 3 when no template is
    known, rather than returning None — clarity has some content even then).
    """
    if not draft_html:
        return 1

    # Step 1: word count ratio
    word_count = _count_words(draft_html)
    target = _TEMPLATE_WORD_TARGETS.get((template_type or "").lower(), 0)
    if target > 0 and word_count > 0:
        ratio = word_count / target
        if ratio <= 0.2 or ratio > 2.0:
            length_score = 1
        elif 0.5 <= ratio <= 1.5:
            # Within 50% either way -> score 5; inside 20% -> stays 5.
            length_score = 5
        else:
            # Between 20%-50% off in either direction -> score 3.
            length_score = 3
    else:
        # Unknown template or empty — neutral
        length_score = 3

    # Step 2: [TO VERIFY] markers
    to_verify_count = len(re.findall(r"\[TO VERIFY\]", draft_html, re.IGNORECASE))
    to_verify_dock = min(to_verify_count * 0.5, 2.0)

    # Step 3: [AMBIGUOUS] markers
    ambiguous_count = len(re.findall(r"\[AMBIGUOUS", draft_html, re.IGNORECASE))
    ambiguous_dock = min(ambiguous_count * 0.25, 1.0)

    raw = length_score - to_verify_dock - ambiguous_dock
    return _clamp(raw)


# ─────────────────────────────────────────────────────────────────────────────
# score_structure
# ─────────────────────────────────────────────────────────────────────────────

def score_structure(draft_html: str, template_type: str = "") -> int:
    """Derive a 1–5 structure score by checking required section headings.

    Required headings come from CLAUDE.md §Template Definitions. Each required
    heading is matched as a case-insensitive substring of an <h*> element's text.

    Algorithm:
      - All required headings present -> 5
      - 1 required heading missing -> 3
      - 2+ required headings missing -> 1
      - Unknown template type (no requirements defined) -> 3 (neutral)
      - Empty draft -> 1

    Returns int 1–5.
    """
    if not draft_html:
        return 1

    required = _REQUIRED_HEADINGS.get((template_type or "").lower())
    if not required:
        # Unknown template — no headings to check, neutral score.
        return 3

    found_headings = _extract_headings(draft_html)
    missing = 0
    for req in required:
        req_lower = req.lower()
        if not any(req_lower in h for h in found_headings):
            missing += 1

    if missing == 0:
        return 5
    if missing == 1:
        return 3
    return 1


# ─────────────────────────────────────────────────────────────────────────────
# Convenience: compute all four rubric scores at once
# ─────────────────────────────────────────────────────────────────────────────

def compute_scores(
    draft_html: str,
    template_type: str,
    grounding_score: int | None,
    task_result: "TaskResult | None" = None,
    evaluator_verdict: "EvaluatorVerdict | None" = None,
) -> dict[str, int | None]:
    """Return the full rubric dict ready for persistence in draft metadata JSON.

    Keys: "grounding" (passed in), "coverage", "clarity", "structure".
    Values: int 1–5 or None when not measured.
    """
    return {
        "grounding": grounding_score,
        "coverage": score_coverage(task_result, evaluator_verdict),
        "clarity": score_clarity(draft_html, template_type),
        "structure": score_structure(draft_html, template_type),
    }
