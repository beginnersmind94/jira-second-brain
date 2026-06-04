"""AI-assisted draft revision — the human-in-the-loop review step.

Two small agents, both tool-less:

  * **Edit agent** — given the current draft HTML and a reviewer's plain-English
    instruction, emits a list of targeted find/replace operations. It NEVER
    touches the `<!-- Source: [[NXT-####:TIER]] "quote" -->` citation comments
    (those are the grounding guarantee) and NEVER invents new cited facts. The
    deterministic gate (demo.validate_citations) re-runs after every edit, so a
    bad edit that breaks a citation is caught and blocks approval automatically.

  * **Triage agent** — classifies the edit as `stylistic` (wording / tone /
    formatting / ordering — no claim changed) or `substantive` (a fact, number,
    label, step, or behaviour changed or was added). The deterministic gate
    proves the *quotes* are intact but cannot see a new *unsourced* claim added
    to the prose — that gap is exactly what triage flags so substantive edits
    get a closer human look while stylistic tweaks approve fast.

This module is pure helpers + option/prompt builders (network-free import).
The SDK `query()` execution lives in demo_app.py, matching the agent_sdk/demo
split where those modules only build options and prompts.
"""
from __future__ import annotations

import json
import re

from claude_agent_sdk import ClaudeAgentOptions

MODEL = "claude-sonnet-4-6"

# Same "no built-in tools" posture as the generator/evaluator — the edit and
# triage agents reason over text only; they have no filesystem or web reach.
_DISALLOWED = [
    "Read", "Write", "Edit", "Bash", "PowerShell", "Glob", "Grep",
    "WebFetch", "WebSearch", "Task", "TaskCreate", "TaskGet",
    "TaskList", "TaskUpdate", "TaskOutput", "TaskStop",
    "NotebookEdit", "Skill", "AskUserQuestion",
    "EnterPlanMode", "ExitPlanMode", "EnterWorktree", "ExitWorktree",
    "CronCreate", "CronDelete", "CronList",
    "Monitor", "PushNotification", "RemoteTrigger", "ScheduleWakeup",
]

# A find/replace target that contains any part of a Source comment is rejected —
# the agent must never edit citations, and this is the server-side backstop.
_SOURCE_FRAGMENT_RE = re.compile(r"<!--\s*Source", re.IGNORECASE)


# ─────────────────────────────────────────────────────────────────────────────
# JSON parsing (agents are told to emit a single JSON object; be forgiving)
# ─────────────────────────────────────────────────────────────────────────────


def parse_json(text: str) -> dict | None:
    """Extract one JSON object from an assistant message, tolerating code fences
    and surrounding prose."""
    text = (text or "").strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Deterministic op application
# ─────────────────────────────────────────────────────────────────────────────


def apply_ops(raw_html: str, ops: list[dict]) -> tuple[str, list[dict], list[dict]]:
    """Apply find/replace ops to the raw draft HTML.

    Returns (new_html, applied, skipped). An op is skipped (never partially
    applied) when:
      * `find` is empty,
      * `find` or `replace` overlaps a `<!-- Source ... -->` citation comment,
      * `find` is not present verbatim in the current HTML.

    Replaces only the first occurrence of each `find` so anchors stay precise;
    the agent is told to make `find` unique. Skips are reported, not silent.
    """
    html = raw_html
    applied: list[dict] = []
    skipped: list[dict] = []
    for i, op in enumerate(ops or []):
        find = op.get("find", "")
        replace = op.get("replace", "")
        reason = op.get("reason", "")
        rec = {"index": i, "find": find, "replace": replace, "reason": reason}
        if not find:
            skipped.append({**rec, "why": "empty find"})
            continue
        if _SOURCE_FRAGMENT_RE.search(find) or _SOURCE_FRAGMENT_RE.search(replace):
            skipped.append({**rec, "why": "touches a Source citation comment (forbidden)"})
            continue
        if find not in html:
            skipped.append({**rec, "why": "find not found verbatim in draft"})
            continue
        html = html.replace(find, replace, 1)
        applied.append(rec)
    return html, applied, skipped


# ─────────────────────────────────────────────────────────────────────────────
# Edit agent
# ─────────────────────────────────────────────────────────────────────────────


def build_edit_options() -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        model=MODEL,
        effort="medium",
        system_prompt=_EDIT_SYSTEM,
        disallowed_tools=_DISALLOWED,
        tools=[],
        max_turns=2,
    )


_EDIT_SYSTEM = """You revise a customer-facing learning guide (HTML) according to a reviewer's instruction.

You output a small set of TARGETED find/replace operations — never the whole document.

HARD RULES (these protect the product's grounding guarantee — violating them is a failure):
1. NEVER modify, move, reorder, or delete any HTML comment that begins with `<!-- Source:`. These are verbatim Jira citations and are the audit trail. Your `find` and `replace` text must NOT contain any `<!-- Source` substring.
2. Do NOT introduce new factual claims about the product — features, numbers, field labels, menu paths, steps, limits, behaviours, error strings. Only reword/restructure claims that are ALREADY present and cited in the document.
3. If the instruction asks for new product facts that are not already in the document, do NOT invent them. Either:
   - set `"refused": true` with a clear `refusal_reason`, or
   - add the requested statement wrapped in a `[TO VERIFY: ...]` marker so a human resolves it against Jira. NEVER fabricate a `<!-- Source -->` citation.
4. You MAY freely improve: wording, tone, clarity, concision, headings, list/table formatting, ordering, typos, transitions — as long as the meaning of every cited claim is preserved.
5. SCOPE — you make TARGETED, LOCALIZED edits only. If the instruction is a WHOLE-DOCUMENT transformation — translating the guide to another language, rewriting or restructuring the entire document, or changing the language/voice of the whole thing — do NOT attempt it with partial ops (that produces an incoherent half-edited guide). Decline: set `"refused": true`, `"refusal_kind": "out_of_scope"`, and a `refusal_reason` that says targeted edits can't do whole-document changes and names the supported path (point edits here; translation is a separate capability, not an inline edit).

Each `find` MUST be an exact, verbatim substring of the current HTML, unique enough to anchor cleanly (include a little surrounding text if needed). Keep ops minimal and scoped to the instruction.

Output STRICT JSON only — one object, no prose around it:

{
  "ops": [
    {"find": "<exact substring of current HTML>", "replace": "<new text>", "reason": "<one line>"}
  ],
  "notes": "<optional: what you changed, or what you could not do>",
  "refused": false,
  "refusal_kind": "none",
  "refusal_reason": ""
}

When you decline, set `refused: true` and `refusal_kind`:
  - `"no_source"` — the instruction needs a product fact with no citable source (rule 3);
  - `"out_of_scope"` — a whole-document transform such as translation (rule 5).
If the instruction simply needs no change, return an empty `ops` array and explain in `notes` (leave `refused` false)."""


def build_edit_prompt(raw_html: str, instruction: str, fmt: str, module: str) -> str:
    return (
        f"MODULE: {module}\nFORMAT: {fmt}\n\n"
        f"REVIEWER INSTRUCTION:\n{instruction}\n\n"
        "CURRENT DRAFT HTML (edit this; preserve every <!-- Source: ... --> comment exactly):\n"
        "```html\n"
        f"{raw_html}\n"
        "```\n\n"
        "Emit the JSON now. Nothing else."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Triage agent — decide whether the edit needs a closer (substantive) look
# ─────────────────────────────────────────────────────────────────────────────


def build_triage_options() -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        model=MODEL,
        system_prompt=_TRIAGE_SYSTEM,
        disallowed_tools=_DISALLOWED,
        tools=[],
        max_turns=2,
    )


_TRIAGE_SYSTEM = """You classify a single edit to a customer-facing learning guide so the system knows whether it can be approved fast or needs a closer factual review.

You are given the exact find -> replace operations that were applied (the EFFECT), plus the reviewer's stated intent as low-trust context.

JUDGE THE EFFECT, NOT THE STATED INTENT. Compare each operation's before-text to its after-text and decide what actually changed. The stated intent can understate the change — "make the intro punchier" might flip a conditional claim ("auto-processes when enabled") into an absolute one ("always auto-processes"). Trust the diff, not the description.

Classify the edit as exactly one of:
- "stylistic": only wording, tone, clarity, concision, formatting, headings, list/table layout, ordering of non-sequential items, or typo fixes. The MEANING of every factual claim is unchanged. No claim, number, label, path, step, limit, permission, frequency, or scope was added, removed, or altered.
- "substantive": the before->after diff adds, removes, or changes any factual claim — a number, field label, menu path, procedure step or its order, limit, permission, frequency, condition/caveat, or behaviour — OR introduces a new product statement (including a `[TO VERIFY]` marker). Anything that could affect accuracy or grounding.

When uncertain, choose "substantive". A wrong "stylistic" call lets an unverified claim slip through (the dangerous error); a wrong "substantive" call only costs an extra review.

Output STRICT JSON only:
{"classification": "stylistic" | "substantive", "reason": "<one sentence about what the diff changed>", "confidence": 0.0-1.0}"""


def build_triage_prompt(instruction: str, applied: list[dict]) -> str:
    ops_lines = []
    for op in applied:
        ops_lines.append(
            f"- BEFORE: {json.dumps(op.get('find', ''), ensure_ascii=False)}\n"
            f"  AFTER:  {json.dumps(op.get('replace', ''), ensure_ascii=False)}"
        )
    ops_text = "\n".join(ops_lines) if ops_lines else "(no operations were applied)"
    return (
        f"OPERATIONS APPLIED ({len(applied)}) — judge these:\n{ops_text}\n\n"
        f"Reviewer's stated intent (CONTEXT ONLY — may understate the change):\n{instruction}\n\n"
        "Classify by the before->after effect. Emit the JSON now. Nothing else."
    )
