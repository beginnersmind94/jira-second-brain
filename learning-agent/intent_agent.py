"""Intent-and-scope agent — the "describe what you need" front end.

It resolves *what to build* (module, topic, format, depth) and an outline grounded
in real tickets, then hands a confirmed scope to the existing generation pipeline.
It is NEVER a source of factual content: the registry, [CITE:id] markers, and the
deterministic grounding gate remain the sole authority, so grounding-by-construction
is preserved. The agent's judgment is reserved for the open-ended parts — intent,
search, and what-to-build — exactly where Anthropic's guidance endorses it.

Two stages:
  1. resolve_module  — tool-less. Map the request to ONE available module, or ask a
     clarifying question when ambiguous, or refuse when no fixture exists for it.
     This is the primary defense against the silent wrong-module failure (DP9):
     when unsure, ASK — don't guess.
  2. scope_search    — fixture-backed. Search the resolved module's Jira, select the
     tickets/epics that genuinely match the topic, and emit a SECTION OUTLINE in the
     exact shape the pipeline consumes ({id,title,scope,ticket_keys}). Refuse to
     ground a topic with no supporting tickets (same no-invention rule as the editor).

This module is pure prompt/schema/option builders (network-free import). The SDK
query() execution + fixture-backed tool wiring live in demo_app.py.
"""
from __future__ import annotations

import json
import re

from claude_agent_sdk import ClaudeAgentOptions

MODEL = "claude-sonnet-4-6"

_DISALLOWED = [
    "Read", "Write", "Edit", "Bash", "PowerShell", "Glob", "Grep",
    "WebFetch", "WebSearch", "Task", "TaskCreate", "TaskGet",
    "TaskList", "TaskUpdate", "TaskOutput", "TaskStop",
    "NotebookEdit", "Skill", "AskUserQuestion",
    "EnterPlanMode", "ExitPlanMode", "EnterWorktree", "ExitWorktree",
    "CronCreate", "CronDelete", "CronList",
    "Monitor", "PushNotification", "RemoteTrigger", "ScheduleWakeup",
]


def parse_json(text: str) -> dict | None:
    text = (text or "").strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Stage 1 — module + intent resolution (tool-less; ask when ambiguous)
# ─────────────────────────────────────────────────────────────────────────────


def build_resolver_options() -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        model=MODEL,
        system_prompt=_RESOLVER_SYSTEM,
        disallowed_tools=_DISALLOWED,
        tools=[],
        max_turns=2,
    )


_RESOLVER_SYSTEM = """You resolve a user's plain-English request for a learning guide into a concrete build scope. You decide WHICH product module, format, and depth — or you ASK.

You will be given the user's request and the EXACT list of modules that have grounded data available. You may ONLY pick a module from that list.

Rules:
- Map the request to exactly ONE module from the available list when you are confident.
- If the request is ambiguous between modules, or you cannot tell which module it belongs to, DO NOT GUESS. Ask ONE focused clarifying question. Guessing the wrong module is the most dangerous error — it would produce a confident guide grounded in the wrong feature's tickets.
- If the request clearly names a product area that is NOT in the available list, refuse: say which area it is and that there's no grounded data for it yet. Do not substitute a different module.
- Resolve `format` to one of: long-form, micro-guide, tldr, release-notes. If the user didn't say, infer a sensible default from the request (a quick overview -> tldr or micro-guide; a full reference -> long-form) but mark `assumed_format: true`.
- `depth` is a short free-text note (e.g., "top workflows only", "comprehensive").

Output STRICT JSON only — one object, no prose:
{
  "module": "<exact module name from the list, or null>",
  "ambiguous": false,
  "clarifying_question": "",
  "refused": false,
  "refused_reason": "",
  "format": "long-form|micro-guide|tldr|release-notes",
  "assumed_format": false,
  "depth": "",
  "topic": "<one-line restatement of what the user wants the guide to cover>"
}
Set `ambiguous: true` (with a `clarifying_question`) OR `refused: true` (with a `refused_reason`) OR a concrete `module`. Never more than one of those."""


def build_resolver_prompt(request: str, available_modules: list[str], history: str = "") -> str:
    mods = "\n".join(f"  - {m}" for m in available_modules)
    hist = f"\nEarlier in this conversation:\n{history}\n" if history else ""
    return (
        f"AVAILABLE MODULES (you may only choose from these):\n{mods}\n{hist}\n"
        f"USER REQUEST:\n{request}\n\n"
        "Resolve the scope. Emit the JSON now. Nothing else."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Stage 2 — scope search + outline (fixture-backed tools, wired in demo_app)
# ─────────────────────────────────────────────────────────────────────────────


def build_scope_system_prompt(module: str, fmt: str, spec_text: str) -> str:
    return _SCOPE_TEMPLATE.replace("__MODULE__", module).replace("__FMT__", fmt).replace("__SPEC__", spec_text)


_SCOPE_TEMPLATE = """You are the SCOPE PLANNER for a __FMT__ guide on the `__MODULE__` module. The user described what they want in words (there is NO transcript). You research the module's Jira and produce a SECTION OUTLINE as JSON. You do NOT write the guide, and you do NOT supply facts — every claim is added later, cited from the tickets you name here.

Tools (module-scoped to `__MODULE__`): match_tickets, read_ticket, read_epic. Caps: ≤6 match_tickets, ≤8 read_ticket, ≤4 read_epic.

Steps:
1. Search for the features/workflows the user asked about (match_tickets, 2–4 word phrases).
2. read_ticket the most behaviorally relevant results to confirm they genuinely match the user's topic AND this module. If results are off-topic, reformulate and search again.
3. MINE ALL TICKET TYPES — Bugs -> gotchas/known issues; Tasks -> setup/prerequisites; Tech-Debt -> limitations; Epics -> grouping/theme. Assign the right ticket TYPE to the right section.
4. Produce the SECTION OUTLINE:
__SPEC__
   Each section names the EXACT Jira ticket keys whose AC/RN back its claims (only keys you actually read and confirmed on-topic). ticket_keys may be [] for a lightly-touched section. Do NOT include a "Sources" section — it's auto-generated.

GROUNDING RULES:
- Only name ticket keys you actually read and that genuinely match the user's topic in THIS module. Never invent keys.
- If a ticket's parent epic is shown as "parent reference only" / "carries no AC/RN", that's fine — cite the ticket, not the epic; do not block on it.
- If the user's topic has NO real supporting tickets in this module, do NOT fabricate an outline. Set `"supported": false` and explain in `note` (the topic may belong to another module, or simply isn't built).

OUTPUT — your FINAL message must be ONLY this JSON object, no prose, no fence:
{
  "supported": true,
  "note": "",
  "sections": [
    {"id": "s1", "title": "...", "scope": "1-2 sentence description", "ticket_keys": ["NXT-1234"]}
  ]
}
Use the EXACT section titles the spec specifies."""
