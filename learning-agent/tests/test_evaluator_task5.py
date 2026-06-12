"""Tests for the LLM Evaluator (Task 5) and retry routing logic.

Covers:
    1. EvaluatorVerdict parsing from raw evaluator JSON.
    2. Failure-type routing — each check name routes to the right retry_task.
    3. Retry loop routing (run_with_evaluator) using a mock that controls verdicts.
    4. Max-retry exhaustion and unresolved-log emission.
    5. Evaluator exception handling (non-fatal; best result returned).
    6. TaskResult.start_from propagation in run_tasks_1_4.

Run from learning-agent/ with:
    python -m pytest tests/test_evaluator_task5.py -v
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import asyncio

import pytest

# Make learning-agent importable regardless of cwd.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from evaluator_runner import (
    MAX_RETRIES,
    EvaluatorVerdict,
    _write_attempt_log,
    _write_unresolved_log,
    run_with_evaluator,
)
from agent_tasks import TaskResult, _extract_json


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _verdict(verdict_str: str, checks: list[dict] | None = None,
             failure_type: str | None = None, retry_task: int | None = None) -> dict:
    """Build a minimal raw evaluator JSON dict."""
    return {
        "verdict": verdict_str,
        "summary": f"Test verdict: {verdict_str}",
        "word_count": 500,
        "checks": checks or [],
        "failure_type": failure_type,
        "retry_task": retry_task,
    }


def _task_result(html: str = "<h1>Test</h1>") -> TaskResult:
    return TaskResult(task1={}, task2={}, task3={}, draft_html=html, usages=[], start_from=1)


# ─────────────────────────────────────────────────────────────────────────────
# 1. EvaluatorVerdict parsing
# ─────────────────────────────────────────────────────────────────────────────

class TestEvaluatorVerdictParsing:
    def test_pass_verdict(self):
        v = EvaluatorVerdict(_verdict("pass"))
        assert v.pass_ is True
        assert v.verdict == "pass"
        assert v.failure_type is None
        assert v.retry_task is None

    def test_warn_verdict_is_pass(self):
        v = EvaluatorVerdict(_verdict("warn"))
        assert v.pass_ is True
        assert v.verdict == "warn"
        assert v.failure_type is None
        assert v.retry_task is None

    def test_fail_verdict(self):
        v = EvaluatorVerdict(_verdict("fail"))
        assert v.pass_ is False
        assert v.verdict == "fail"

    def test_explicit_failure_type_and_retry_task(self):
        v = EvaluatorVerdict(_verdict("fail", failure_type="task2", retry_task=2))
        assert v.failure_type == "task2"
        assert v.retry_task == 2

    def test_to_dict_has_required_keys(self):
        v = EvaluatorVerdict(_verdict("pass"))
        d = v.to_dict()
        for key in ("pass", "verdict", "failure_type", "retry_task",
                    "failure_reason", "summary", "word_count", "checks"):
            assert key in d, f"missing key: {key}"

    def test_unknown_verdict_treated_as_fail(self):
        v = EvaluatorVerdict({"verdict": "unknown_garbage"})
        assert v.pass_ is False

    def test_empty_dict_graceful(self):
        v = EvaluatorVerdict({})
        assert v.pass_ is False
        assert v.verdict == "fail"


# ─────────────────────────────────────────────────────────────────────────────
# 2. Failure-type routing from check names
# ─────────────────────────────────────────────────────────────────────────────

class TestFailureTypeDerivation:
    """When the evaluator JSON does NOT include explicit failure_type/retry_task,
    the class derives them from the failing check names."""

    def _failing_check(self, name: str) -> dict:
        return {"name": name, "status": "fail", "detail": "test"}

    def test_citation_check_routes_to_task3(self):
        checks = [self._failing_check("Citation spot-check")]
        v = EvaluatorVerdict({"verdict": "fail", "checks": checks, "word_count": 0})
        assert v.failure_type == "task3"
        assert v.retry_task == 3

    def test_template_fit_routes_to_task4(self):
        checks = [self._failing_check("Template fit")]
        v = EvaluatorVerdict({"verdict": "fail", "checks": checks, "word_count": 0})
        assert v.failure_type == "task4"
        assert v.retry_task == 4

    def test_length_budget_routes_to_task4(self):
        checks = [self._failing_check("Length budget")]
        v = EvaluatorVerdict({"verdict": "fail", "checks": checks, "word_count": 0})
        assert v.failure_type == "task4"
        assert v.retry_task == 4

    def test_source_grounding_routes_to_task3(self):
        checks = [self._failing_check("Source grounding")]
        v = EvaluatorVerdict({"verdict": "fail", "checks": checks, "word_count": 0})
        assert v.failure_type == "task3"
        assert v.retry_task == 3

    def test_discrepancy_handling_routes_to_task3(self):
        checks = [self._failing_check("Discrepancy handling")]
        v = EvaluatorVerdict({"verdict": "fail", "checks": checks, "word_count": 0})
        assert v.failure_type == "task3"
        assert v.retry_task == 3

    def test_no_failing_checks_defaults_to_task4(self):
        """No check is explicitly fail → default routing is task4."""
        v = EvaluatorVerdict({"verdict": "fail", "checks": [], "word_count": 0})
        assert v.failure_type == "task4"
        assert v.retry_task == 4

    def test_explicit_routing_overrides_derivation(self):
        """Explicit failure_type in JSON overrides check-name derivation."""
        checks = [self._failing_check("Template fit")]  # would route to task4
        v = EvaluatorVerdict({
            "verdict": "fail", "checks": checks,
            "failure_type": "task1", "retry_task": 1,  # explicit override
        })
        assert v.failure_type == "task1"
        assert v.retry_task == 1

    def test_failure_reason_includes_check_details(self):
        checks = [
            {"name": "Template fit", "status": "fail", "detail": "Missing 'Purpose' section"},
        ]
        v = EvaluatorVerdict({"verdict": "fail", "checks": checks})
        assert "Missing 'Purpose' section" in v.failure_reason


# ─────────────────────────────────────────────────────────────────────────────
# 3. Retry loop routing — run_with_evaluator
# ─────────────────────────────────────────────────────────────────────────────

class TestRetryLoop:
    """Tests for the orchestration loop in run_with_evaluator().

    run_tasks_1_4 and run_evaluator are both mocked so these tests are fast
    and deterministic — no LLM calls, no network.

    Async tests are run via asyncio.run() so no pytest-asyncio plugin is needed.
    """

    TR = _task_result("<h1>Draft</h1>")  # shared mock task result

    def test_passes_on_first_attempt(self):
        """When evaluator passes immediately, only 1 attempt is made."""
        mock_t14 = AsyncMock(return_value=self.TR)
        mock_eval = AsyncMock(return_value=(EvaluatorVerdict(_verdict("pass")), None))

        async def _run():
            with (
                patch("evaluator_runner.run_tasks_1_4", mock_t14),
                patch("evaluator_runner.run_evaluator", mock_eval),
            ):
                return await run_with_evaluator(
                    transcript_path="/tmp/t.md",
                    transcript_text="transcript text",
                    module="Eligibility",
                    template="micro-guide",
                )

        result, verdict, log = asyncio.run(_run())

        assert verdict.pass_ is True
        assert len(log) == 1
        assert log[0]["attempt"] == 1

    def test_retries_from_correct_task_on_task3_failure(self):
        """Evaluator fails with task3 → second run starts from Task 3."""
        call_count = 0

        async def _mock_eval(task_result, transcript_text, template, module):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return EvaluatorVerdict(_verdict("fail", failure_type="task3", retry_task=3)), None
            return EvaluatorVerdict(_verdict("pass")), None

        async def _run():
            with (
                patch("evaluator_runner.run_tasks_1_4", AsyncMock(return_value=self.TR)),
                patch("evaluator_runner.run_evaluator", side_effect=_mock_eval),
            ):
                return await run_with_evaluator(
                    transcript_path="/tmp/t.md",
                    transcript_text="text",
                    module="Eligibility",
                    template="micro-guide",
                )

        result, verdict, log = asyncio.run(_run())

        assert verdict.pass_ is True
        assert len(log) == 2
        assert log[0]["verdict"] == "fail"
        assert log[0]["failure_type"] == "task3"
        assert log[1]["start_from"] == 3
        assert log[1]["verdict"] == "pass"

    def test_retries_from_task4_on_template_violation(self):
        """Template fit failure → retry from Task 4 only (cheapest fix)."""
        call_count = 0

        async def _mock_eval(task_result, transcript_text, template, module):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                checks = [{"name": "Template fit", "status": "fail", "detail": "too long"}]
                return EvaluatorVerdict({"verdict": "fail", "checks": checks}), None
            return EvaluatorVerdict(_verdict("pass")), None

        async def _run():
            with (
                patch("evaluator_runner.run_tasks_1_4", AsyncMock(return_value=self.TR)),
                patch("evaluator_runner.run_evaluator", side_effect=_mock_eval),
            ):
                return await run_with_evaluator(
                    transcript_path="/tmp/t.md",
                    transcript_text="text",
                    module="Eligibility",
                    template="micro-guide",
                )

        result, verdict, log = asyncio.run(_run())

        assert verdict.pass_ is True
        assert log[1]["start_from"] == 4

    def test_exhausts_max_retries_and_returns_best(self):
        """After MAX_RETRIES failures, returns the best (last) draft + logs unresolved."""
        always_fail = EvaluatorVerdict(_verdict(
            "fail",
            checks=[{"name": "Citation spot-check", "status": "fail", "detail": "fabricated"}],
        ))

        async def _run(logs_dir):
            with (
                patch("evaluator_runner.run_tasks_1_4", AsyncMock(return_value=self.TR)),
                patch("evaluator_runner.run_evaluator",
                      AsyncMock(return_value=(always_fail, None))),
            ):
                return await run_with_evaluator(
                    transcript_path="/tmp/t.md",
                    transcript_text="text",
                    module="Eligibility",
                    template="micro-guide",
                    logs_dir=logs_dir,
                    resource_id="test-rid",
                )

        with tempfile.TemporaryDirectory() as tmpdir:
            logs_dir = Path(tmpdir)
            result, verdict, log = asyncio.run(_run(logs_dir))

            assert len(log) == MAX_RETRIES
            assert all(e["verdict"] == "fail" for e in log)
            assert result is not None
            assert result.draft_html == "<h1>Draft</h1>"

            unresolved = logs_dir / "test-rid-unresolved.json"
            assert unresolved.exists()
            data = json.loads(unresolved.read_text(encoding="utf-8"))
            assert data["resource_id"] == "test-rid"
            assert str(MAX_RETRIES) in data["message"]

    def test_evaluator_exception_is_nonfatal(self):
        """If the evaluator itself throws, the loop accepts the draft as a warn."""
        async def _run():
            with (
                patch("evaluator_runner.run_tasks_1_4", AsyncMock(return_value=self.TR)),
                patch("evaluator_runner.run_evaluator",
                      AsyncMock(side_effect=RuntimeError("SDK connection failed"))),
            ):
                return await run_with_evaluator(
                    transcript_path="/tmp/t.md",
                    transcript_text="text",
                    module="Eligibility",
                    template="micro-guide",
                )

        result, verdict, log = asyncio.run(_run())

        assert verdict is not None
        assert result is not None


# ─────────────────────────────────────────────────────────────────────────────
# 4. TaskResult.start_from propagation
# ─────────────────────────────────────────────────────────────────────────────

class TestTaskResultStartFrom:
    """TaskResult.start_from records which task the run began from."""

    def test_default_start_from_is_1(self):
        r = TaskResult(task1={}, task2={}, task3={}, draft_html="", usages=[])
        assert r.start_from == 1

    def test_explicit_start_from(self):
        r = TaskResult(task1={}, task2={}, task3={}, draft_html="", usages=[], start_from=3)
        assert r.start_from == 3

    def test_run_tasks_1_4_raises_without_prior_when_start_from_gt1(self):
        """run_tasks_1_4(start_from=2) without prior= must raise ValueError."""
        from agent_tasks import run_tasks_1_4

        async def _run():
            return await run_tasks_1_4("/tmp/t.md", "Eligibility", "micro-guide", start_from=2)

        with pytest.raises(ValueError, match="prior must be supplied"):
            asyncio.run(_run())


# ─────────────────────────────────────────────────────────────────────────────
# 5. _extract_json helper
# ─────────────────────────────────────────────────────────────────────────────

class TestExtractJson:
    def test_plain_json(self):
        text = '{"verdict": "pass", "checks": []}'
        assert _extract_json(text) == {"verdict": "pass", "checks": []}

    def test_json_with_prose_prefix(self):
        text = 'Here is the result:\n{"verdict": "fail"}'
        r = _extract_json(text)
        assert r is not None
        assert r["verdict"] == "fail"

    def test_json_in_markdown_fence(self):
        text = "```json\n{\"verdict\": \"warn\"}\n```"
        r = _extract_json(text)
        assert r is not None
        assert r["verdict"] == "warn"

    def test_returns_none_for_no_json(self):
        assert _extract_json("no json here at all") is None

    def test_returns_none_for_empty_string(self):
        assert _extract_json("") is None


# ─────────────────────────────────────────────────────────────────────────────
# 6. Log helpers (unit — no I/O mocking needed, uses tempdir)
# ─────────────────────────────────────────────────────────────────────────────

class TestLogHelpers:
    def test_write_attempt_log_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logs_dir = Path(tmpdir)
            _write_attempt_log(logs_dir, "rid-001", [{"attempt": 1, "verdict": "pass"}])
            p = logs_dir / "rid-001-eval.jsonl"
            assert p.exists()
            lines = p.read_text(encoding="utf-8").strip().splitlines()
            assert len(lines) == 1
            entry = json.loads(lines[0])
            assert entry["resource_id"] == "rid-001"
            assert len(entry["attempts"]) == 1

    def test_write_attempt_log_appends(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logs_dir = Path(tmpdir)
            _write_attempt_log(logs_dir, "rid-002", [{"attempt": 1}])
            _write_attempt_log(logs_dir, "rid-002", [{"attempt": 1}, {"attempt": 2}])
            p = logs_dir / "rid-002-eval.jsonl"
            lines = p.read_text(encoding="utf-8").strip().splitlines()
            assert len(lines) == 2  # each call appends one line

    def test_write_unresolved_log(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logs_dir = Path(tmpdir)
            v = EvaluatorVerdict(_verdict("fail", failure_type="task4", retry_task=4))
            _write_unresolved_log(logs_dir, "rid-003", [{"attempt": 1}, {"attempt": 2}], v)
            p = logs_dir / "rid-003-unresolved.json"
            assert p.exists()
            data = json.loads(p.read_text(encoding="utf-8"))
            assert data["resource_id"] == "rid-003"
            assert data["final_verdict"]["failure_type"] == "task4"
            assert len(data["attempts"]) == 2

    def test_write_unresolved_log_with_none_verdict(self):
        """None verdict should not crash the log writer."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logs_dir = Path(tmpdir)
            _write_unresolved_log(logs_dir, "rid-004", [], None)
            p = logs_dir / "rid-004-unresolved.json"
            assert p.exists()
            data = json.loads(p.read_text(encoding="utf-8"))
            assert data["final_verdict"] == {}
