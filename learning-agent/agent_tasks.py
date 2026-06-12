"""Generator agent — Tasks 1–4 as four separate Claude Agent SDK query() calls.

V1.5 split from agent_sdk.py's single query() call so the Evaluator (Task 5)
can route a retry to the specific failing task rather than re-running the whole
pipeline from scratch.

Task handoff shape:
    Task 1 → feature_inventory (JSON str)
    Task 2 → content_plan      (JSON str)
    Task 3 → fact_check        (JSON str)
    Task 4 → draft_html        (HTML str)

Windows gotcha: NEVER inline large text (transcripts, ticket dumps) into
ClaudeAgentOptions.system_prompt — the SDK passes system_prompt as a CLI arg
and the Windows command-line arg limit (~32 KB) causes a spawn failure that
looks like "Claude Code not found". Transcripts and prior-task outputs ALWAYS
go in the user prompt (first positional arg to query()).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
    create_sdk_mcp_server,
    query,
)

from tools_sdk import SDK_TOOLS

APP_DIR = Path(__file__).parent
TEMPLATES_DIR = APP_DIR / "templates"

VALID_TEMPLATES = ("long-form", "micro-guide", "tldr")
VALID_MODULES = (
    "Eligibility", "Accountability", "Inventory", "Item Management",
    "Menu Planning", "Production", "Insights", "Account Management",
    "Reports", "System",
)

MCP_SERVER_NAME = "producer_tools"

mcp_server = create_sdk_mcp_server(
    name=MCP_SERVER_NAME,
    version="1.0.0",
    tools=SDK_TOOLS,
)

ALLOWED_TOOLS = [
    f"mcp__{MCP_SERVER_NAME}__{t.name}"
    for t in SDK_TOOLS
]

_DISALLOWED = [
    "Read", "Write", "Edit", "Bash", "PowerShell", "Glob", "Grep",
    "WebFetch", "WebSearch", "Task", "TaskCreate", "TaskGet",
    "TaskList", "TaskUpdate", "TaskOutput", "TaskStop",
    "NotebookEdit", "Skill", "AskUserQuestion",
    "EnterPlanMode", "ExitPlanMode", "EnterWorktree", "ExitWorktree",
    "CronCreate", "CronDelete", "CronList",
    "Monitor", "PushNotification", "RemoteTrigger", "ScheduleWakeup",
]

# ─────────────────────────────────────────────────────────────────────────────
# Shared tool-calling options factory
# ─────────────────────────────────────────────────────────────────────────────

def _make_options(system_prompt: str, max_turns: int = 16) -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        model="claude-sonnet-4-6",
        system_prompt=system_prompt,
        mcp_servers={MCP_SERVER_NAME: mcp_server},
        allowed_tools=ALLOWED_TOOLS,
        disallowed_tools=_DISALLOWED,
        tools=[],
        max_turns=max_turns,
    )


def _make_text_options(system_prompt: str, max_turns: int = 8) -> ClaudeAgentOptions:
    """Options for reasoning-only tasks (no tools needed)."""
    return ClaudeAgentOptions(
        model="claude-sonnet-4-6",
        system_prompt=system_prompt,
        allowed_tools=[],
        disallowed_tools=_DISALLOWED,
        tools=[],
        max_turns=max_turns,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Helper: run a query() to completion, collect text output and usage
# ─────────────────────────────────────────────────────────────────────────────

async def _run_query(prompt: str, options: ClaudeAgentOptions) -> tuple[str, Any]:
    """Run query() to completion; return (final_text, usage).

    Collects only AssistantMessage TextBlock output (no streaming side-effects).
    Tool call/result messages are consumed but not returned — they appear in the
    agent's reasoning and feed forward automatically within the same run.
    """
    parts: list[str] = []
    usage = None
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in (message.content or []):
                if isinstance(block, TextBlock):
                    parts.append(block.text)
        elif isinstance(message, ResultMessage):
            usage = getattr(message, "usage", None)
    return "\n".join(parts).strip(), usage


# ─────────────────────────────────────────────────────────────────────────────
# Task 1 — Map transcript to Jira
# ─────────────────────────────────────────────────────────────────────────────

_TASK1_SYSTEM = """You are the Mapping Agent (Task 1 of 4) in a learning content pipeline.

Your ONLY job: parse the transcript and map each feature/workflow mentioned to Jira tickets.

TOOL DISCIPLINE — you have EXACTLY these tools: parse_transcript, match_tickets, read_epic.
Do NOT use any other tool. Cap: 6 match_tickets calls, 4 read_epic calls.

STEPS:
1. Call parse_transcript on the path in the user message.
2. List every distinct feature, workflow, or behavior the presenter mentioned.
3. For each feature, call match_tickets (multi-word phrase, NOT a single keyword) with the module.
4. Collect unique epic keys from all hits, call read_epic ONCE per unique epic.
5. Emit a feature inventory JSON object as your FINAL assistant message.

OUTPUT FORMAT — your FINAL message must be ONLY a JSON object:
{
  "features": [
    {
      "name": "...",
      "tickets": ["NXT-XXXX", ...],
      "epic": "NXT-XXXX",
      "priority": "High|Medium|Low",
      "rn_visibility": "External Only|External-Internal|Internal Only|",
      "ac_summary": "one-line summary of AC (or 'AC empty')",
      "cross_module": false,
      "roles": ["..."]
    }
  ],
  "unmatched": ["feature names that had no ticket matches"],
  "module": "...",
  "transcript_path": "..."
}

Parallelise: emit all match_tickets calls in one assistant turn when possible.
"""


async def run_task1(transcript_path: str, module: str) -> tuple[dict, Any]:
    """Task 1: Map transcript features to Jira tickets.

    Returns (feature_inventory_dict, usage).
    """
    prompt = (
        f"Run Task 1 — map transcript to Jira for module `{module}`.\n\n"
        f"Transcript path: {transcript_path}\n\n"
        f"Call parse_transcript on the path above, then match_tickets for each feature "
        f"(use module=\"{module}\"). Pull unique epics with read_epic. "
        f"Emit ONLY the JSON feature inventory as your final message."
    )
    text, usage = await _run_query(prompt, _make_options(_TASK1_SYSTEM, max_turns=16))
    # Extract JSON from the response (the model might prepend/append prose despite instructions)
    inventory = _extract_json(text) or {"features": [], "unmatched": [], "module": module,
                                         "transcript_path": transcript_path, "raw": text}
    return inventory, usage


# ─────────────────────────────────────────────────────────────────────────────
# Task 2 — Plan the content
# ─────────────────────────────────────────────────────────────────────────────

_TASK2_SYSTEM = """You are the Planning Agent (Task 2 of 4) in a learning content pipeline.

Your ONLY job: given a feature inventory and a template type, decide what to include and how deep.

You have NO tools. This is pure reasoning.

INPUTS (in the user message):
- Feature inventory JSON from Task 1
- Template type: long-form | micro-guide | tldr

PRIORITY SIGNALS:
- Jira priority (High > Medium > Low)
- RN visibility (External-facing = more relevant for staff training)
- Role relevance (does this feature apply to the training audience?)
- Cross-module flags (mention one line only, do not deep-dive)

TEMPLATE RULES:
- long-form: all features at full depth unless explicitly out of scope
- micro-guide: top 3-5 workflows only; if plan includes >5 full-depth workflows, flag that long-form is more appropriate
- tldr: all features at one sentence each — NO step-by-step

OUTPUT FORMAT — your FINAL message must be ONLY a JSON object:
{
  "template": "...",
  "sections": [
    {
      "title": "...",
      "features": ["feature names to cover here"],
      "depth": "full|brief|mention",
      "reason": "why this depth"
    }
  ],
  "omitted": [
    {"feature": "...", "reason": "..."}
  ],
  "warning": "optional: 'too many workflows for micro-guide, consider long-form'" or null
}
"""


async def run_task2(
    feature_inventory: dict,
    template: str,
    module: str,
) -> tuple[dict, Any]:
    """Task 2: Plan the content structure from the feature inventory.

    Returns (content_plan_dict, usage).
    """
    prompt = (
        f"Run Task 2 — plan the content for a `{template}` guide on module `{module}`.\n\n"
        f"FEATURE INVENTORY FROM TASK 1:\n{json.dumps(feature_inventory, indent=2)[:6000]}\n\n"
        f"Decide which features to include at full depth, briefly, or omit. "
        f"Emit ONLY the JSON content plan as your final message."
    )
    text, usage = await _run_query(prompt, _make_text_options(_TASK2_SYSTEM, max_turns=6))
    plan = _extract_json(text) or {"template": template, "sections": [], "omitted": [],
                                   "warning": None, "raw": text}
    return plan, usage


# ─────────────────────────────────────────────────────────────────────────────
# Task 3 — Fact-check against KB
# ─────────────────────────────────────────────────────────────────────────────

_TASK3_SYSTEM = """You are the Fact-Check Agent (Task 3 of 4) in a learning content pipeline.

Your ONLY job: verify that what the transcript presenter said matches Jira AC and the KB.

TOOL DISCIPLINE — you have EXACTLY these tools: search_kb, read_ticket.
Cap: 6 read_ticket calls, skip search_kb unless a specific UI label or menu path needs verification.

CHECKS (for each planned section):
- Does the transcript workflow match the current Jira AC? (call read_ticket)
- Did the presenter mention a feature absent from both Jira and KB?
- Did the presenter give specific numbers, limits, or field names that differ from AC?
- Did the presenter describe behavior from a DIFFERENT module? (flag as cross-module)

NEVER silently correct the presenter. Surface discrepancies verbatim.

OUTPUT FORMAT — your FINAL message must be ONLY a JSON object:
{
  "verified": [
    {"claim": "...", "source": "NXT-XXXX AC: 'verbatim quote'", "section": "..."}
  ],
  "discrepancies": [
    {"claim": "...", "transcript_says": "...", "jira_says": "...", "ticket": "NXT-XXXX", "section": "..."}
  ],
  "unsupported": [
    {"claim": "...", "reason": "no Jira match found", "section": "..."}
  ],
  "cross_module_flags": [
    {"claim": "...", "likely_module": "...", "section": "..."}
  ]
}
"""


async def run_task3(
    feature_inventory: dict,
    content_plan: dict,
    module: str,
) -> tuple[dict, Any]:
    """Task 3: Fact-check transcript claims against Jira KB.

    Returns (fact_check_results_dict, usage).
    """
    # Keep the user prompt bounded — ticket text comes back from tools, not from us
    inventory_snippet = json.dumps(feature_inventory, indent=2)[:4000]
    plan_snippet = json.dumps(content_plan, indent=2)[:3000]
    prompt = (
        f"Run Task 3 — fact-check for module `{module}`.\n\n"
        f"FEATURE INVENTORY:\n{inventory_snippet}\n\n"
        f"CONTENT PLAN:\n{plan_snippet}\n\n"
        f"For each planned section, call read_ticket on the most relevant tickets and verify "
        f"claims. Emit ONLY the JSON fact-check results as your final message."
    )
    text, usage = await _run_query(prompt, _make_options(_TASK3_SYSTEM, max_turns=14))
    results = _extract_json(text) or {"verified": [], "discrepancies": [], "unsupported": [],
                                       "cross_module_flags": [], "raw": text}
    return results, usage


# ─────────────────────────────────────────────────────────────────────────────
# Task 4 — Generate the learning content
# ─────────────────────────────────────────────────────────────────────────────

def _load_template_prompt(template: str) -> str:
    if template not in VALID_TEMPLATES:
        raise ValueError(f"unknown template {template!r}")
    return (TEMPLATES_DIR / f"{template}.md").read_text(encoding="utf-8")


_TASK4_SYSTEM_BASE = """You are the Content Writer (Task 4 of 4) in a learning content pipeline.

Your ONLY job: generate the final HTML learning resource.

You have NO tools. Write HTML directly from the fact-checked inputs in the user message.

CITATION RULES (non-negotiable):
- Every factual claim has an inline HTML comment immediately after:
    <!-- Source: NXT-1234 AC: "verbatim quote" -->
    <!-- Source: NXT-5678 RN: "verbatim quote" -->
    <!-- Source: transcript [MM:SS] -->
- Quote verbatim. Do NOT paraphrase inside the comment.
- If a claim has no citable source, CUT it.
- Discrepancies between transcript and Jira go in <blockquote class="discrepancy">.
- Unsourced specifics get [TO VERIFY] markers.
- Internal Jira jargon is translated to user-facing language; original kept in the comment.

OUTPUT FORMAT:
- Plain HTML only. No <html>/<head>/<body> wrappers. Start with <h1>.
- Semantic tags: <h1>/<h2>/<h3>, <ol>/<ul>/<li>, <table>, <blockquote>, <code>, <strong>, <em>, <p>.
- Inline <!-- Source: ... --> comments throughout.
- Transcript is the VOICE; Jira AC is the TRUTH. Surface conflicts — never silently pick one.
- Follow the TEMPLATE INSTRUCTIONS below for section structure and length.

GLOBAL RULES:
- Cite or cut. No invented specifics. No cross-feature pattern matching.
- Stay strictly within the template's structure and length budget.
"""


async def run_task4(
    feature_inventory: dict,
    content_plan: dict,
    fact_check: dict,
    template: str,
    module: str,
) -> tuple[str, Any]:
    """Task 4: Generate the final HTML learning resource.

    Returns (draft_html_str, usage).
    """
    template_instructions = _load_template_prompt(template)
    # System prompt: base instructions + template definition (static, small enough for system_prompt)
    system_prompt = _TASK4_SYSTEM_BASE + (
        "\n\n═══════════════════════════════════════════════════════════\n"
        "TEMPLATE INSTRUCTIONS\n"
        "═══════════════════════════════════════════════════════════\n\n"
        + template_instructions
    )

    # Prior task outputs go in the USER PROMPT (not system_prompt) to stay under Windows CLI limit
    plan_snippet = json.dumps(content_plan, indent=2)[:4000]
    fc_snippet = json.dumps(fact_check, indent=2)[:4000]
    inventory_snippet = json.dumps(feature_inventory, indent=2)[:2000]

    prompt = (
        f"Run Task 4 — generate the `{template}` HTML guide for module `{module}`.\n\n"
        f"FEATURE INVENTORY (Task 1 output):\n{inventory_snippet}\n\n"
        f"CONTENT PLAN (Task 2 output):\n{plan_snippet}\n\n"
        f"FACT-CHECK RESULTS (Task 3 output):\n{fc_snippet}\n\n"
        f"Write the complete HTML resource following the template structure above. "
        f"Emit ONLY the HTML as your final message — no wrapper prose, no markdown fences."
    )

    max_turns = {"tldr": 8, "micro-guide": 10, "long-form": 14}.get(template, 12)
    text, usage = await _run_query(prompt, _make_text_options(system_prompt, max_turns=max_turns))

    # Strip any accidental markdown fence wrappers
    import re
    fence = re.search(r"```(?:html)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    h_match = re.search(r"<h[1-2]\b", text, flags=re.I)
    if h_match:
        text = text[h_match.start():].strip()

    return text, usage


# ─────────────────────────────────────────────────────────────────────────────
# Orchestrator: run Tasks 1–4 in sequence, passing outputs forward
# ─────────────────────────────────────────────────────────────────────────────

class TaskResult:
    """Container returned by run_tasks_1_4() and used by the retry loop."""

    def __init__(
        self,
        task1: dict,
        task2: dict,
        task3: dict,
        draft_html: str,
        usages: list,
        start_from: int = 1,
    ):
        self.task1 = task1       # feature_inventory
        self.task2 = task2       # content_plan
        self.task3 = task3       # fact_check_results
        self.draft_html = draft_html
        self.usages = usages     # one usage object per task run
        self.start_from = start_from  # which task the run started from (1, 2, 3, or 4)


async def run_tasks_1_4(
    transcript_path: str,
    module: str,
    template: str,
    *,
    start_from: int = 1,
    prior: TaskResult | None = None,
) -> TaskResult:
    """Run Tasks 1–4 sequentially, passing each task's output to the next.

    Args:
        transcript_path: path to the uploaded transcript file.
        module: Jira/product module name.
        template: one of "long-form", "micro-guide", "tldr".
        start_from: which task to start from (1=full run, 2/3/4=partial retry).
        prior: a previous TaskResult — must be supplied when start_from > 1 so we
               can carry forward the outputs of tasks that don't need re-running.

    Returns a TaskResult with all four task outputs populated.
    """
    if start_from > 1 and prior is None:
        raise ValueError("prior must be supplied when start_from > 1")

    usages: list = []

    # ── Task 1 ────────────────────────────────────────────────────────────────
    if start_from <= 1:
        task1, u1 = await run_task1(transcript_path, module)
        usages.append(u1)
    else:
        task1 = prior.task1  # type: ignore[union-attr]
        usages.append(None)

    # ── Task 2 ────────────────────────────────────────────────────────────────
    if start_from <= 2:
        task2, u2 = await run_task2(task1, template, module)
        usages.append(u2)
    else:
        task2 = prior.task2  # type: ignore[union-attr]
        usages.append(None)

    # ── Task 3 ────────────────────────────────────────────────────────────────
    if start_from <= 3:
        task3, u3 = await run_task3(task1, task2, module)
        usages.append(u3)
    else:
        task3 = prior.task3  # type: ignore[union-attr]
        usages.append(None)

    # ── Task 4 ────────────────────────────────────────────────────────────────
    if start_from <= 4:
        draft_html, u4 = await run_task4(task1, task2, task3, template, module)
        usages.append(u4)
    else:
        draft_html = prior.draft_html  # type: ignore[union-attr]
        usages.append(None)

    return TaskResult(
        task1=task1,
        task2=task2,
        task3=task3,
        draft_html=draft_html,
        usages=usages,
        start_from=start_from,
    )


# ─────────────────────────────────────────────────────────────────────────────
# JSON extraction helper (tolerant of prose wrapping despite instructions)
# ─────────────────────────────────────────────────────────────────────────────

def _extract_json(text: str) -> dict | None:
    """Return the first JSON object found in text, or None."""
    import re
    # Try raw parse first
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        pass
    # Strip markdown fences
    fence = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text)
    if fence:
        try:
            return json.loads(fence.group(1))
        except json.JSONDecodeError:
            pass
    # Find the outermost {...} block
    start = text.find("{")
    if start == -1:
        return None
    depth, i = 0, start
    while i < len(text):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start:i + 1])
                except json.JSONDecodeError:
                    return None
        i += 1
    return None
