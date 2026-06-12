"""Evaluator runner — Task 5 + retry loop.

This module wires together:
    1. The LLM Evaluator (Task 5): a separate Claude Agent SDK query() that
       grades the draft against template fit, plan alignment, and source grounding.
    2. A structured verdict with failure-type routing (which task to retry).
    3. A retry loop (max 3 attempts) that re-runs from the failing task forward.
    4. Log emission for unresolved issues after max retries.

Architecture notes (from CLAUDE.md):
    - The LLM evaluator is ADVISORY. The deterministic `validate_citations` gate
      (demo_d / demo_app) is the hard floor and is NOT replaced or weakened here.
    - The evaluator runs as a fifth query() call in a separate ClaudeAgentOptions
      instance from the generator — different model context, different tool set.
    - The edit-triage classifier remains a thin classifier (Haiku-class), not this
      full agent.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)

from agent_tasks import TaskResult, _extract_json, run_tasks_1_4
from evaluator_sdk import EVALUATOR_PROMPT, build_evaluator_options, build_evaluator_prompt

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Verdict schema
# ─────────────────────────────────────────────────────────────────────────────

class EvaluatorVerdict:
    """Parsed output from the LLM evaluator (Task 5).

    Schema:
        pass_  (bool)  — True when all checks pass / warn (no hard fails)
        failure_type   — "task1" | "task2" | "task3" | "task4" | None
        retry_task     — int (1-4) the pipeline should retry from, or None
        failure_reason — human-readable explanation of the failure
        checks         — list of per-check dicts from the evaluator
        word_count     — estimated word count from the evaluator
        verdict        — raw "pass" | "warn" | "fail" string
        raw            — the full evaluator JSON response
    """

    def __init__(self, raw: dict):
        self.raw = raw
        self.verdict: str = raw.get("verdict", "fail")
        self.pass_: bool = self.verdict in ("pass", "warn")
        self.checks: list[dict] = raw.get("checks", [])
        self.word_count: int = raw.get("word_count", 0)
        self.summary: str = raw.get("summary", "")
        # The evaluator may include failure routing via an extended schema.
        # If it doesn't, we derive it from the checks.
        self.failure_type: str | None = raw.get("failure_type") or self._derive_failure_type()
        self.retry_task: int | None = raw.get("retry_task") or self._derive_retry_task()
        self.failure_reason: str = raw.get("failure_reason") or self._derive_failure_reason()

    def _failing_checks(self) -> list[dict]:
        return [c for c in self.checks if c.get("status") == "fail"]

    def _derive_failure_reason(self) -> str:
        fails = self._failing_checks()
        if not fails:
            return self.summary or "No specific failure reason."
        return "; ".join(c.get("detail", c.get("name", "?")) for c in fails[:3])

    def _derive_failure_type(self) -> str | None:
        """Infer which task caused the failure from the failing check names."""
        if self.pass_:
            return None
        fails = {c.get("name", "").lower() for c in self._failing_checks()}
        # Citation spot-check failures (fabricated quotes) → Task 3 missed them
        if any("citation" in f or "fabricated" in f for f in fails):
            return "task3"
        # Template fit / length → Task 4 (generation) problem
        if any("template" in f or "length" in f or "budget" in f for f in fails):
            return "task4"
        # Grounding / discrepancy handling → Task 3 / Task 4
        if any("grounding" in f or "discrepancy" in f or "unverifiable" in f for f in fails):
            return "task3"
        # Default: generation issue
        return "task4"

    def _derive_retry_task(self) -> int | None:
        """Map failure_type to the task number to retry from."""
        if self.pass_:
            return None
        mapping = {"task1": 1, "task2": 2, "task3": 3, "task4": 4}
        return mapping.get(self.failure_type or "")

    def to_dict(self) -> dict:
        return {
            "pass": self.pass_,
            "verdict": self.verdict,
            "failure_type": self.failure_type,
            "retry_task": self.retry_task,
            "failure_reason": self.failure_reason,
            "summary": self.summary,
            "word_count": self.word_count,
            "checks": self.checks,
        }

    def __repr__(self) -> str:
        return (
            f"EvaluatorVerdict(verdict={self.verdict!r}, pass_={self.pass_}, "
            f"failure_type={self.failure_type!r}, retry_task={self.retry_task})"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Task 5 — LLM Evaluator
# ─────────────────────────────────────────────────────────────────────────────

_EXTENDED_EVALUATOR_PROMPT = (
    EVALUATOR_PROMPT.rstrip()
    + """

ROUTING EXTENSION — add these two fields to your JSON output (after the existing schema):

  "failure_type": "task1"|"task2"|"task3"|"task4"|null,
  "retry_task": 1|2|3|4|null

Routing rules (use these when verdict is "fail"):
| Failure cause                              | failure_type | retry_task |
|--------------------------------------------|-------------|------------|
| Draft discusses features NOT in transcript | "task1"      | 1          |
| Wrong priority — low-pri got full depth    | "task2"      | 2          |
| Unverified claim, fabricated citation      | "task3"      | 3          |
| Wrong structure, length violation, missing sections | "task4" | 4     |

When verdict is "pass" or "warn" set both fields to null.
If multiple failures, pick the EARLIEST failing task (the root cause).
"""
)


async def run_evaluator(
    task_result: TaskResult,
    transcript_text: str,
    template: str,
    module: str,
) -> tuple[EvaluatorVerdict, Any]:
    """Task 5: Grade the draft with an independent LLM query.

    Uses the demo evaluator options (offline tool: read_ticket served from fixture)
    if available, otherwise falls back to the prod evaluator options.

    Returns (EvaluatorVerdict, usage).
    """
    # Build options with the extended prompt that includes routing fields.
    try:
        # Prefer demo evaluator options (reads from offline fixture, faster)
        from demo import read_ticket as demo_read_ticket
        from claude_agent_sdk import create_sdk_mcp_server as _cms
        _EVAL_SRV = "evaluator_tools_runner"
        _eval_mcp = _cms(name=_EVAL_SRV, version="1.0.0", tools=[demo_read_ticket])
        options = ClaudeAgentOptions(
            model="claude-sonnet-4-6",
            system_prompt=_EXTENDED_EVALUATOR_PROMPT,
            mcp_servers={_EVAL_SRV: _eval_mcp},
            allowed_tools=[f"mcp__{_EVAL_SRV}__read_ticket"],
            disallowed_tools=[
                "Read", "Write", "Edit", "Bash", "PowerShell", "Glob", "Grep",
                "WebFetch", "WebSearch", "Task", "TaskCreate", "TaskGet",
                "TaskList", "TaskUpdate", "TaskOutput", "TaskStop",
                "NotebookEdit", "Skill", "AskUserQuestion",
            ],
            tools=[],
            max_turns=10,
        )
    except Exception:
        # Fallback: prod evaluator (uses real Jira read_ticket tool)
        from evaluator_sdk import build_evaluator_options as _build
        options = ClaudeAgentOptions(
            model="claude-sonnet-4-6",
            system_prompt=_EXTENDED_EVALUATOR_PROMPT,
            mcp_servers=_build().mcp_servers,
            allowed_tools=_build().allowed_tools,
            disallowed_tools=_build().disallowed_tools,
            tools=[],
            max_turns=10,
        )

    prompt = build_evaluator_prompt(
        draft_html=task_result.draft_html,
        transcript_text=transcript_text,
        template=template,
        module=module,
    )

    parts: list[str] = []
    usage = None
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in (message.content or []):
                if isinstance(block, TextBlock):
                    parts.append(block.text)
        elif isinstance(message, ResultMessage):
            usage = getattr(message, "usage", None)

    raw_text = "\n".join(parts).strip()
    raw_dict = _extract_json(raw_text) or {
        "verdict": "fail",
        "summary": f"Evaluator produced unparseable output: {raw_text[:200]}",
        "checks": [],
    }
    return EvaluatorVerdict(raw_dict), usage


# ─────────────────────────────────────────────────────────────────────────────
# Retry loop (max 3 attempts)
# ─────────────────────────────────────────────────────────────────────────────

MAX_RETRIES = 3


async def run_with_evaluator(
    transcript_path: str,
    transcript_text: str,
    module: str,
    template: str,
    *,
    logs_dir: Path | None = None,
    resource_id: str = "",
) -> tuple[TaskResult, EvaluatorVerdict, list[dict]]:
    """Run Tasks 1–4 + Evaluator (Task 5) with up to MAX_RETRIES total attempts.

    Retry routing: when the evaluator fails, re-run from the identified failing
    task forward (not from Task 1 every time — that's expensive and often wrong).

    Args:
        transcript_path:  path to the uploaded transcript file.
        transcript_text:  full text of the transcript (for evaluator grading).
        module:           Jira/product module name.
        template:         one of "long-form", "micro-guide", "tldr".
        logs_dir:         directory to write per-run eval logs (optional).
        resource_id:      used for log file naming.

    Returns:
        (best_task_result, final_verdict, attempt_log)

    The caller is responsible for running `validate_citations` (the deterministic
    gate) on best_task_result.draft_html — this function does NOT replace that.
    """
    attempt_log: list[dict] = []
    best_result: TaskResult | None = None
    best_verdict: EvaluatorVerdict | None = None

    prior: TaskResult | None = None
    start_from = 1

    for attempt in range(1, MAX_RETRIES + 1):
        attempt_entry: dict[str, Any] = {
            "attempt": attempt,
            "start_from": start_from,
            "started_at": datetime.now().isoformat(timespec="seconds"),
        }

        # ── Run Tasks 1–4 (or subset on retry) ────────────────────────────────
        try:
            result = await run_tasks_1_4(
                transcript_path=transcript_path,
                module=module,
                template=template,
                start_from=start_from,
                prior=prior,
            )
        except Exception as exc:
            logger.error("Tasks 1-4 failed on attempt %d: %s", attempt, exc)
            attempt_entry["error"] = f"Tasks 1-4 failed: {exc}"
            attempt_entry["verdict"] = "error"
            attempt_log.append(attempt_entry)
            break

        # ── Task 5: Evaluator ──────────────────────────────────────────────────
        try:
            verdict, eval_usage = await run_evaluator(
                task_result=result,
                transcript_text=transcript_text,
                template=template,
                module=module,
            )
        except Exception as exc:
            logger.error("Evaluator failed on attempt %d: %s", attempt, exc)
            # Evaluator failure is non-fatal — accept the draft and log it
            verdict = EvaluatorVerdict({
                "verdict": "warn",
                "summary": f"Evaluator threw an exception: {exc}",
                "checks": [],
                "failure_type": None,
                "retry_task": None,
            })
            eval_usage = None

        attempt_entry["verdict"] = verdict.verdict
        attempt_entry["pass"] = verdict.pass_
        attempt_entry["failure_type"] = verdict.failure_type
        attempt_entry["retry_task"] = verdict.retry_task
        attempt_entry["failure_reason"] = verdict.failure_reason
        attempt_entry["finished_at"] = datetime.now().isoformat(timespec="seconds")
        attempt_log.append(attempt_entry)

        # Keep the best result (prefer passing; if never passed, keep last)
        if best_result is None or verdict.pass_ or not best_verdict.pass_:  # type: ignore[union-attr]
            best_result = result
            best_verdict = verdict

        # ── Persist attempt log ────────────────────────────────────────────────
        if logs_dir and resource_id:
            _write_attempt_log(logs_dir, resource_id, attempt_log)

        # ── Pass → stop ────────────────────────────────────────────────────────
        if verdict.pass_:
            logger.info("Evaluator passed on attempt %d", attempt)
            break

        # ── Fail → route retry ─────────────────────────────────────────────────
        if attempt < MAX_RETRIES:
            retry_from = verdict.retry_task or 4  # default: re-run Task 4 only
            logger.warning(
                "Evaluator failed (attempt %d/%d): %s — retrying from Task %d",
                attempt, MAX_RETRIES, verdict.failure_reason, retry_from,
            )
            start_from = retry_from
            prior = result
        else:
            # Exhausted retries
            logger.warning(
                "Evaluator: max retries (%d) exhausted. Best draft: verdict=%s. "
                "Unresolved issues: %s",
                MAX_RETRIES, best_verdict.verdict if best_verdict else "?",
                best_verdict.failure_reason if best_verdict else "unknown",
            )
            if logs_dir and resource_id:
                _write_unresolved_log(logs_dir, resource_id, attempt_log, best_verdict)

    # Fallback: should not happen, but guard against empty loop
    if best_result is None:
        raise RuntimeError("run_with_evaluator: no result produced — check logs")

    return best_result, best_verdict, attempt_log  # type: ignore[return-value]


# ─────────────────────────────────────────────────────────────────────────────
# Log helpers
# ─────────────────────────────────────────────────────────────────────────────

def _write_attempt_log(logs_dir: Path, resource_id: str, attempt_log: list[dict]) -> None:
    """Append the current attempt log state to <logs_dir>/<resource_id>-eval.jsonl."""
    try:
        p = logs_dir / f"{resource_id}-eval.jsonl"
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps({
                "resource_id": resource_id,
                "at": datetime.now().isoformat(timespec="seconds"),
                "attempts": attempt_log,
            }, ensure_ascii=False) + "\n")
    except OSError as e:
        logger.warning("Could not write eval log: %s", e)


def _write_unresolved_log(
    logs_dir: Path,
    resource_id: str,
    attempt_log: list[dict],
    verdict: EvaluatorVerdict | None,
) -> None:
    """Write a dedicated unresolved-issues log for the human editor."""
    try:
        p = logs_dir / f"{resource_id}-unresolved.json"
        p.write_text(
            json.dumps({
                "resource_id": resource_id,
                "logged_at": datetime.now().isoformat(timespec="seconds"),
                "message": (
                    f"Content generation exhausted {MAX_RETRIES} retry attempts. "
                    "The best draft is available but has unresolved evaluator issues. "
                    "Human editor review is recommended before approving."
                ),
                "final_verdict": verdict.to_dict() if verdict else {},
                "attempts": attempt_log,
            }, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except OSError as e:
        logger.warning("Could not write unresolved log: %s", e)
