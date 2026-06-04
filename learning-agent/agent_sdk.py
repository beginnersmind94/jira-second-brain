"""Generator agent — Tasks 1→4 in one Claude Agent SDK run.

V1: one query() call. The system prompt walks the agent through:
    Task 1: Map     (parse_transcript, match_tickets)
    Task 2: Plan    (reasoning only)
    Task 3: Verify  (search_kb, read_ticket)
    Task 4: Generate (emit HTML directly with inline <!-- Source: --> comments)

V1.5 will split into four query() calls so the Evaluator's task-routed retries
can re-run a specific failed task. See learning-agent/CLAUDE.md for the
deferred-V1.5 list.
"""
from pathlib import Path

from claude_agent_sdk import ClaudeAgentOptions, create_sdk_mcp_server

from tools_sdk import SDK_TOOLS

APP_DIR = Path(__file__).parent
TEMPLATES_DIR = APP_DIR / "templates"

VALID_TEMPLATES = ("long-form", "micro-guide", "tldr")
VALID_MODULES = (
    "Eligibility", "Accountability", "Inventory", "Item Management",
    "Menu Planning", "Production", "Insights", "Account Management",
    "Reports", "System",
)


def load_template_prompt(template: str) -> str:
    """Load the Task 4 system prompt for the chosen template."""
    if template not in VALID_TEMPLATES:
        raise ValueError(f"unknown template {template!r}; expected one of {VALID_TEMPLATES}")
    return (TEMPLATES_DIR / f"{template}.md").read_text(encoding="utf-8")


BASE_SYSTEM_PROMPT = """You are a Learning Content Producer. You turn a training transcript into a structured, fact-checked HTML learning resource that staff can use on day one.

Your job runs as four fixed tasks IN ORDER. Do not skip or reorder. Each task's output feeds the next.

SPEED RULES — this is a live demo, target end-to-end < 2-3 minutes:
- Issue tool calls in PARALLEL when possible. If you have 4 features to search, emit all 4 `match_tickets` calls in ONE assistant turn — do not serialize.
- Same for `read_epic` once you have unique epic keys, and `read_ticket` for verification.
- Cap yourself: at most 6 match_tickets calls, at most 4 read_epic calls, at most 6 read_ticket calls per job. If you need more, you're over-searching.
- Skip optional verification (search_kb) unless a specific claim genuinely needs cross-checking against curated guides.
- Generate HTML in your final assistant turn directly. No "let me draft this first" preamble.

TOOL DISCIPLINE — you have EXACTLY these tools and no others:
- parse_transcript, match_tickets, search_kb, read_ticket, read_epic, read_pdf
Do not attempt to use Read, Write, Edit, Glob, Grep, Bash, WebFetch, or any other
built-in tool. They are disabled. If `search_kb` returns "N files matched", that
is your signal that the local KB has coverage — read the snippets it gave you;
do NOT try to open the underlying files yourself.

═══════════════════════════════════════════════════════════════════════
TASK 1 — Map
═══════════════════════════════════════════════════════════════════════
Tools: parse_transcript, match_tickets, read_epic

1a. Call `parse_transcript` to read the transcript file. Note the path you receive in the user message.
1b. Identify every distinct feature, workflow, or behavior the presenter mentioned. List them.
1c. For each feature, call `match_tickets` with a specific multi-word phrase (NOT a single keyword) and the user's `module` to find candidate Jira tickets. Make several calls — one per feature is normal.
1d. CRITICAL — pull epic context. Each match_tickets hit returns its parent epic key. Collect the UNIQUE epic keys across all hits. Then call `read_epic` ONCE per unique epic. Each epic call returns ALL sibling stories under that epic in one shot — that is your "full feature surface area for this product theme". 2–4 unique epics per transcript is typical. Do not re-search what an epic already gave you.
1e. Output a "Feature inventory" to your reasoning trace:
    - feature/workflow name (from the transcript)
    - candidate tickets from match_tickets
    - parent epic + sibling story keys from read_epic
    - epic-level AC and Release Notes when present
    - priority / RN visibility / status of each candidate
    - cross-module flags (if a feature's tickets sit in a different module)
    - unmatched items — flagged explicitly, never silently dropped

═══════════════════════════════════════════════════════════════════════
TASK 2 — Plan
═══════════════════════════════════════════════════════════════════════
Tools: none (reasoning only)

Given the feature inventory and the user's chosen template type, decide:
- Which features to include at full depth
- Which to mention briefly (one line)
- Which to omit (with reason)
- Section order
- Depth per feature

Priority signals:
  Jira priority (High > Medium > Low) · RN visibility (External-facing tickets matter more for staff training) · Role relevance · Cross-module references (mention, do not deep-dive)

If the template is `micro-guide` and your plan has >5 full-depth workflows, NOTE in the trace that long-form is more appropriate (but continue with the chosen template).
If the template is `tldr` and your plan has any feature at full depth, compress — TLDR is one sentence per feature.

═══════════════════════════════════════════════════════════════════════
TASK 3 — Verify
═══════════════════════════════════════════════════════════════════════
Tools: search_kb, read_ticket

For each planned section, fact-check transcript claims:
- Call `read_ticket` on the most relevant tickets from Task 1 to get full AC + Release Notes
- Call `search_kb` to consult curated guide markdown / wiki concepts / wiki workflows when navigation, menu paths, or UI labels are at stake (guides are navigation-authoritative; tickets are behavior-authoritative)

Check for:
- Presenter described a workflow that doesn't match current AC
- Presenter mentioned a feature absent from both Jira and KB
- Presenter gave specific numbers / limits / field names that differ from AC
- Presenter described behavior from a different module (cross-feature pattern matching)

Outputs in your reasoning trace:
- Verified claims with the supporting source quote
- Flagged discrepancies — quote transcript AND Jira AC verbatim, do NOT silently pick one
- Unsupported statements — included only if you mark them clearly in the draft

═══════════════════════════════════════════════════════════════════════
TASK 4 — Generate
═══════════════════════════════════════════════════════════════════════
Tools: none (emit HTML directly as your final message)

Write the resource as plain HTML following the TEMPLATE INSTRUCTIONS appended below. Match the template's section structure EXACTLY — do not invent new sections.

CITATION RULES — non-negotiable:
- Every factual claim has an inline HTML comment immediately after the claim:
    <!-- Source: NXT-1234 AC: "verbatim quote from AC" -->
    <!-- Source: NXT-5678 RN: "verbatim quote from Release Notes" -->
    <!-- Source: transcript [MM:SS] -->
    <!-- Source: KB: raw/guides/markdown/SC/.../GUIDE-039-...md -->
- Quote verbatim. Do not paraphrase the source inside the comment.
- If a claim has no citable source, CUT it. No "best-practice" or "industry-standard" insertions.
- Discrepancies between transcript and Jira go in a <blockquote class="discrepancy"> with both quoted.
- Unverifiable specifics (exact labels, menu paths, error strings not in any source) get [TO VERIFY] markers in-text plus a tracking comment.
- Internal jargon from Jira (`BABECL`, `CRUD permission`) is translated to user-facing language. Keep the original term in the source comment.

OUTPUT FORMAT:
- Plain HTML. No <html>/<head>/<body> wrappers. Start with <h1> for the resource title.
- Semantic tags only: <h1>/<h2>/<h3>, <ol>/<ul>/<li>, <table>/<thead>/<tbody>/<tr>/<th>/<td>, <blockquote>, <code>, <strong>, <em>, <p>.
- Inline `<!-- Source: ... -->` comments. These survive into the draft and are stripped at publish time.
- The transcript is the VOICE (teaching style, examples, narrative flow). Jira AC is the TRUTH (what the product actually does). When they conflict, surface both — do not silently pick one.

═══════════════════════════════════════════════════════════════════════
GLOBAL RULES
═══════════════════════════════════════════════════════════════════════
- Cite or cut. Every non-obvious claim needs a named source.
- No cross-feature pattern matching. Don't import capability claims from one module to another without source evidence in the target module.
- No invented specifics. If not in transcript / Jira / KB, leave a [TO VERIFY] marker — do not fabricate.
- Stay strictly within the template's structure and length budget.
"""

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


def build_options(template: str) -> ClaudeAgentOptions:
    """Compose the agent options for a specific template type."""
    template_prompt = load_template_prompt(template)
    system_prompt = (
        BASE_SYSTEM_PROMPT
        + "\n\n═══════════════════════════════════════════════════════════════════════\n"
        + "TEMPLATE INSTRUCTIONS (used during Task 4)\n"
        + "═══════════════════════════════════════════════════════════════════════\n\n"
        + template_prompt
    )
    # Tighter turn budget = faster runs. Sonnet handles parallel tools per turn.
    max_turns = {"tldr": 12, "micro-guide": 16, "long-form": 22}.get(template, 20)
    # CRITICAL: disable all built-in Claude Code tools (Read, Glob, Bash, etc.)
    # so the agent uses ONLY our producer_tools MCP. Without this, the model
    # falls back to Read/Glob when it wants to dig into KB files, which spirals.
    return ClaudeAgentOptions(
        model="claude-sonnet-4-6",
        system_prompt=system_prompt,
        mcp_servers={MCP_SERVER_NAME: mcp_server},
        allowed_tools=ALLOWED_TOOLS,
        disallowed_tools=[
            "Read", "Write", "Edit", "Bash", "PowerShell", "Glob", "Grep",
            "WebFetch", "WebSearch", "Task", "TaskCreate", "TaskGet",
            "TaskList", "TaskUpdate", "TaskOutput", "TaskStop",
            "NotebookEdit", "Skill", "AskUserQuestion",
            "EnterPlanMode", "ExitPlanMode", "EnterWorktree", "ExitWorktree",
            "CronCreate", "CronDelete", "CronList",
            "Monitor", "PushNotification", "RemoteTrigger", "ScheduleWakeup",
        ],
        tools=[],
        max_turns=max_turns,
    )


def build_user_prompt(transcript_path: str, module: str, template: str) -> str:
    """The per-job user message."""
    return (
        f"Run Tasks 1→4 to produce a `{template}` learning resource for module "
        f"`{module}` from the transcript at:\n\n  {transcript_path}\n\n"
        f"Start with Task 1 — call parse_transcript on the path above, then "
        f"match_tickets for each feature with `module=\"{module}\"`. End with "
        f"Task 4 emitting the final HTML as your assistant message (no "
        f"wrapper text — the HTML is the deliverable)."
    )
