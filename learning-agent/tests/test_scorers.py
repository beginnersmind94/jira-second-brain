"""Tests for learning-agent/scorers.py.

Runs with the project venv:
    python -m pytest tests/test_scorers.py -v

All stubs use types.SimpleNamespace so the tests have zero SDK dependencies.
"""
from __future__ import annotations

import sys
import os
import types

# Ensure scorers.py is importable when running from the learning-agent dir.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from scorers import (
    _clamp,
    _count_words,
    _extract_headings,
    compute_scores,
    score_clarity,
    score_coverage,
    score_structure,
)


# ─────────────────────────────────────────────────────────────────────────────
# Stub builders
# ─────────────────────────────────────────────────────────────────────────────

def _verdict(checks: list[dict]) -> types.SimpleNamespace:
    """Build a minimal EvaluatorVerdict stub."""
    return types.SimpleNamespace(checks=checks)


def _task_result(omitted: list[dict] | None = None) -> types.SimpleNamespace:
    """Build a minimal TaskResult stub with a task2 content plan."""
    plan: dict = {}
    if omitted is not None:
        plan["omitted"] = omitted
    return types.SimpleNamespace(task2=plan)


# ─────────────────────────────────────────────────────────────────────────────
# _extract_headings
# ─────────────────────────────────────────────────────────────────────────────

class TestExtractHeadings:
    def test_basic_h2(self):
        html = "<h2>Overview</h2><p>text</p>"
        assert _extract_headings(html) == ["overview"]

    def test_strips_inner_tags(self):
        html = "<h3><strong>Key Features</strong></h3>"
        assert _extract_headings(html) == ["key features"]

    def test_multiple_headings(self):
        html = "<h1>A</h1><h2>B</h2><h3>C</h3>"
        assert _extract_headings(html) == ["a", "b", "c"]


# ─────────────────────────────────────────────────────────────────────────────
# _count_words
# ─────────────────────────────────────────────────────────────────────────────

class TestCountWords:
    def test_empty_returns_zero(self):
        assert _count_words("") == 0

    def test_strips_html_tags(self):
        html = "<p>Hello world</p>"
        assert _count_words(html) == 2

    def test_strips_citation_comments(self):
        # Citation comments must NOT count as content words.
        html = "<p>Hello</p><!-- Source: NXT-1 AC: \"verbatim text here\" -->"
        assert _count_words(html) == 1

    def test_plain_word_count(self):
        html = "<p>one two three four five</p>"
        assert _count_words(html) == 5


# ─────────────────────────────────────────────────────────────────────────────
# score_coverage
# ─────────────────────────────────────────────────────────────────────────────

class TestScoreCoverage:
    def test_both_none_returns_none(self):
        assert score_coverage(None, None) is None

    def test_evaluator_pass_returns_5(self):
        v = _verdict([{"name": "coverage_check", "status": "pass"}])
        assert score_coverage(None, v) == 5

    def test_evaluator_warn_returns_3(self):
        v = _verdict([{"name": "omission_check", "status": "warn"}])
        assert score_coverage(None, v) == 3

    def test_evaluator_fail_returns_1(self):
        v = _verdict([{"name": "completeness_check", "status": "fail"}])
        assert score_coverage(None, v) == 1

    def test_non_coverage_check_ignored(self):
        # A check named "grounding_check" does NOT count as a coverage check.
        v = _verdict([{"name": "grounding_check", "status": "fail"}])
        # No coverage check found -> fall through to task_result path.
        # task_result is None -> return None.
        assert score_coverage(None, v) is None

    def test_task_result_no_omissions_returns_5(self):
        tr = _task_result(omitted=[])
        assert score_coverage(tr, None) == 5

    def test_task_result_one_unexplained_omission_docks_1(self):
        tr = _task_result(omitted=[{"feature": "X"}])  # no "reason"
        assert score_coverage(tr, None) == 4

    def test_task_result_explained_omission_does_not_dock(self):
        tr = _task_result(omitted=[{"feature": "X", "reason": "out of scope for micro"}])
        assert score_coverage(tr, None) == 5

    def test_evaluator_pass_plus_unexplained_omissions_docks(self):
        v = _verdict([{"name": "coverage_check", "status": "pass"}])
        tr = _task_result(omitted=[{"feature": "A"}, {"feature": "B"}])
        # base 5, dock 2 -> 3
        assert score_coverage(tr, v) == 3

    def test_score_clamped_to_1(self):
        v = _verdict([{"name": "coverage_check", "status": "fail"}])
        tr = _task_result(omitted=[{"feature": "A"}, {"feature": "B"}, {"feature": "C"}])
        # base 1, dock 3 -> -2 -> clamped to 1
        assert score_coverage(tr, v) == 1


# ─────────────────────────────────────────────────────────────────────────────
# score_clarity
# ─────────────────────────────────────────────────────────────────────────────

class TestScoreClarity:
    def test_empty_html_returns_1(self):
        assert score_clarity("") == 1

    def test_none_html_returns_1(self):
        assert score_clarity(None) == 1  # type: ignore[arg-type]

    def test_unknown_template_neutral_length(self):
        # Unknown template type -> length_score=3; no markers -> score 3.
        html = "<p>" + " ".join(["word"] * 50) + "</p>"
        assert score_clarity(html, "unknown-template") == 3

    def test_on_target_long_form_returns_5(self):
        # ~4000 words for long-form -> ratio 1.0 -> length_score=5.
        html = "<p>" + " ".join(["word"] * 4000) + "</p>"
        assert score_clarity(html, "long-form") == 5

    def test_over_2x_long_form_returns_1(self):
        # >8000 words for long-form -> ratio >2 -> length_score=1.
        html = "<p>" + " ".join(["word"] * 9000) + "</p>"
        assert score_clarity(html, "long-form") == 1

    def test_under_0_2_returns_1(self):
        # <800 words for long-form (target 4000, 20%=800) -> score 1.
        # Use 100 words -> ratio=0.025 -> length_score=1.
        html = "<p>" + " ".join(["word"] * 100) + "</p>"
        assert score_clarity(html, "long-form") == 1

    def test_to_verify_markers_dock_score(self):
        # On-target tldr (200 words) then 4 [TO VERIFY] markers.
        html = "<p>" + " ".join(["word"] * 200) + " [TO VERIFY] [TO VERIFY] [TO VERIFY] [TO VERIFY]</p>"
        # length_score=5, dock = min(4*0.5, 2.0)=2.0 -> 3
        assert score_clarity(html, "tldr") == 3

    def test_ambiguous_markers_dock_score(self):
        html = "<p>" + " ".join(["word"] * 200) + " [AMBIGUOUS — x]</p>"
        # length_score=5, ambiguous dock=0.25 -> 4.75 -> 5 (rounded)
        result = score_clarity(html, "tldr")
        assert result == 5

    def test_to_verify_capped_at_2(self):
        # 10 [TO VERIFY] markers -> dock=min(5.0, 2.0)=2.0.
        markers = " ".join(["[TO VERIFY]"] * 10)
        html = "<p>" + " ".join(["word"] * 800) + " " + markers + "</p>"
        # length_score=5 (800 words, micro target 800), dock 2 -> 3
        result = score_clarity(html, "micro")
        assert result == 3

    def test_score_clamped_to_min_1(self):
        # Force length_score=1 and markers to try to go below 1.
        html = "<p>x</p> [TO VERIFY] [TO VERIFY] [TO VERIFY] [TO VERIFY] [TO VERIFY]"
        result = score_clarity(html, "long-form")
        assert result == 1


# ─────────────────────────────────────────────────────────────────────────────
# score_structure
# ─────────────────────────────────────────────────────────────────────────────

class TestScoreStructure:
    def test_empty_html_returns_1(self):
        assert score_structure("") == 1

    def test_unknown_template_returns_3(self):
        html = "<h2>Overview</h2>"
        assert score_structure(html, "unknown") == 3

    def test_all_required_headings_present_long_form_returns_5(self):
        html = """
        <h2>Overview</h2>
        <h2>Roles and Permissions</h2>
        <h2>Prerequisites</h2>
        <h2>Full Workflows</h2>
        <h2>Troubleshooting</h2>
        <h2>Sources</h2>
        """
        assert score_structure(html, "long-form") == 5

    def test_one_missing_heading_returns_3(self):
        html = """
        <h2>Overview</h2>
        <h2>Roles and Permissions</h2>
        <h2>Prerequisites</h2>
        <h2>Full Workflows</h2>
        <h2>Troubleshooting</h2>
        """
        # Missing "sources" -> 3
        assert score_structure(html, "long-form") == 3

    def test_two_missing_headings_returns_1(self):
        html = """
        <h2>Overview</h2>
        <h2>Roles and Permissions</h2>
        <h2>Prerequisites</h2>
        """
        # Missing workflow, troubleshoot, sources -> 1
        assert score_structure(html, "long-form") == 1

    def test_micro_guide_all_present(self):
        html = """
        <h2>Purpose</h2>
        <h2>Before You Start</h2>
        <h2>Workflows</h2>
        <h2>Related Content</h2>
        """
        assert score_structure(html, "micro-guide") == 5

    def test_tldr_all_present(self):
        html = """
        <h2>What This Module Does</h2>
        <h2>Key Features</h2>
        <h2>Who Uses This</h2>
        <h2>Common Workflows</h2>
        <h2>Important Gotchas</h2>
        """
        assert score_structure(html, "tldr") == 5

    def test_case_insensitive_match(self):
        # Headings should be matched case-insensitively.
        html = "<h2>OVERVIEW</h2><h2>ROLES</h2><h2>PREREQUISITES</h2><h2>WORKFLOW</h2><h2>TROUBLESHOOT</h2><h2>SOURCES</h2>"
        assert score_structure(html, "long-form") == 5

    def test_micro_alias_same_as_micro_guide(self):
        html = """
        <h2>Purpose</h2>
        <h2>Before You Start</h2>
        <h2>Workflows</h2>
        <h2>Related Content</h2>
        """
        assert score_structure(html, "micro") == score_structure(html, "micro-guide")


# ─────────────────────────────────────────────────────────────────────────────
# compute_scores
# ─────────────────────────────────────────────────────────────────────────────

class TestComputeScores:
    def _full_micro_html(self) -> str:
        return (
            "<h2>Purpose</h2>"
            "<p>" + " ".join(["word"] * 800) + "</p>"
            "<h2>Before You Start</h2><h2>Workflows</h2><h2>Related Content</h2>"
        )

    def test_returns_dict_with_four_keys(self):
        result = compute_scores("<p>hello</p>", "micro", grounding_score=5)
        assert set(result.keys()) == {"grounding", "coverage", "clarity", "structure"}

    def test_grounding_passthrough(self):
        result = compute_scores("<p>hello</p>", "micro", grounding_score=3)
        assert result["grounding"] == 3

    def test_grounding_none_allowed(self):
        result = compute_scores("<p>hello</p>", "micro", grounding_score=None)
        assert result["grounding"] is None

    def test_coverage_none_when_no_evaluator_no_task(self):
        result = compute_scores("<p>hello</p>", "micro", grounding_score=5)
        assert result["coverage"] is None

    def test_full_pipeline_scores_all_present(self):
        html = self._full_micro_html()
        v = _verdict([{"name": "coverage_check", "status": "pass"}])
        tr = _task_result(omitted=[])
        result = compute_scores(html, "micro", grounding_score=5, task_result=tr, evaluator_verdict=v)
        assert result["grounding"] == 5
        assert result["coverage"] == 5
        assert result["clarity"] == 5
        assert result["structure"] == 5

    def test_all_scores_in_range(self):
        result = compute_scores("<p>word</p>", "long-form", grounding_score=4)
        for key in ("clarity", "structure"):
            assert 1 <= result[key] <= 5
