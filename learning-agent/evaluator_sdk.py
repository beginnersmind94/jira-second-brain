"""Evaluator — Task 5.

A separate Claude Agent SDK query() call that grades a draft produced by the
Generator. Structural enforcement of what `CLAUDE-producer.md` calls for:
template fit, source grounding, citation spot-check. It does NOT rewrite the
draft. It only reports.

V1.5 minimum: one pass, no retry routing. The Generator runs Tasks 1-4 in
one query; the Evaluator runs once after, in a second query, with refusal
authority over the Publish action.
"""
from claude_agent_sdk import ClaudeAgentOptions, create_sdk_mcp_server

from tools_sdk import read_ticket

EVALUATOR_PROMPT = """You are an editor grading a draft learning guide produced by a separate AI agent. Your job: grade it. You DO NOT rewrite. You ONLY report.

You receive:
- The draft HTML (with inline <!-- Source: ... --> comments preserved)
- The original transcript text
- The expected module
- The template type: `long-form` (2500–6000 words), `micro-guide` (600–1500 words HARD CEILING), or `tldr` (≤500 words, one page)

You have ONE tool: `read_ticket(issue_key)`. Use it to spot-check 2 or 3 of the most consequential ticket citations in the draft — confirm the quoted AC text actually appears in the ticket's real Acceptance Criteria.

CHECKS (in order, do not skip):

1. **Template fit** — Does the draft use the expected section structure? For micro-guide: Purpose, Who this is for, Before you start, Top workflows, Common mistakes, Related content, Sources.

2. **Length budget** — Estimate word count from the rendered text (ignore HTML tags and <!-- --> comments). Is it within the template's budget? micro-guide HARD CEILING is 1500 words.

3. **Source grounding** — Every non-trivial factual claim should have an inline `<!-- Source: ... -->` comment. Sample 5-10 claims; flag if a significant fraction lack citations.

4. **Citation spot-check** — Pick 2-3 ticket citations in the draft. For each, call `read_ticket` and confirm the quoted AC text actually appears verbatim in the ticket's Acceptance Criteria. A fabricated quote is a HARD FAIL.

5. **Discrepancy handling** — Are transcript-vs-Jira discrepancies surfaced (via blockquote.discrepancy or explicit flagging) rather than silently picked?

6. **[TO VERIFY] markers** — Are unsourced specifics (exact labels, error strings, menu paths not in any source) flagged with [TO VERIFY] rather than fabricated?

OUTPUT FORMAT — your FINAL assistant message must be ONLY a JSON object, no surrounding prose, no markdown fence:

{
  "verdict": "pass" | "warn" | "fail",
  "summary": "one-line readable summary",
  "word_count": <integer estimate>,
  "checks": [
    {"name": "Template fit", "status": "ok"|"warn"|"fail", "detail": "..."},
    {"name": "Length budget", "status": "ok"|"warn"|"fail", "detail": "..."},
    {"name": "Source grounding", "status": "ok"|"warn"|"fail", "detail": "..."},
    {"name": "Citation spot-check", "status": "ok"|"warn"|"fail", "detail": "...", "checked": ["NXT-XXXX", ...]},
    {"name": "Discrepancy handling", "status": "ok"|"warn"|"fail", "detail": "..."},
    {"name": "Unverifiable specifics", "status": "ok"|"warn"|"fail", "detail": "..."}
  ]
}

Verdict rules:
- "fail" if ANY check is fail (especially fabricated citations)
- "warn" if any check is warn but none fail
- "pass" only if all six checks are ok

Be specific in the `detail` field. "Looks good" is not helpful; "Length 4200 words exceeds micro-guide ceiling of 1500" is.
"""

EVALUATOR_MCP_SERVER_NAME = "evaluator_tools"

evaluator_mcp_server = create_sdk_mcp_server(
    name=EVALUATOR_MCP_SERVER_NAME,
    version="1.0.0",
    tools=[read_ticket],
)

EVALUATOR_ALLOWED = [f"mcp__{EVALUATOR_MCP_SERVER_NAME}__read_ticket"]


def build_evaluator_options() -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        model="claude-sonnet-4-6",
        system_prompt=EVALUATOR_PROMPT,
        mcp_servers={EVALUATOR_MCP_SERVER_NAME: evaluator_mcp_server},
        allowed_tools=EVALUATOR_ALLOWED,
        disallowed_tools=[
            "Read", "Write", "Edit", "Bash", "PowerShell", "Glob", "Grep",
            "WebFetch", "WebSearch", "Task", "TaskCreate", "TaskGet",
            "TaskList", "TaskUpdate", "TaskOutput", "TaskStop",
            "NotebookEdit", "Skill", "AskUserQuestion",
        ],
        tools=[],
        max_turns=8,
    )


def build_evaluator_prompt(
    draft_html: str, transcript_text: str, template: str, module: str
) -> str:
    return (
        f"Grade this draft `{template}` learning guide for the `{module}` module.\n\n"
        f"=== TRANSCRIPT (source) ===\n{transcript_text[:8000]}\n\n"
        f"=== DRAFT HTML (to grade) ===\n{draft_html[:20000]}\n\n"
        f"Run all six checks. Spot-check 2-3 ticket citations via read_ticket. "
        f"Emit ONLY the JSON object as your final message. No surrounding prose."
    )
