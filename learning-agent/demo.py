"""STEP 2 (the live demo). Real generation, Jira pre-cached, NO Jira network.

This is a STANDALONE copy for the demo only. It does NOT touch the production
path (tools_sdk.py / agent_sdk.py / smoke_test.py / app.py are untouched). It
reuses agent_sdk's system prompt + template loader so the model behaves exactly
like prod, but swaps the six tools for offline versions that serve from the
fixture written by demo_capture.py.

What's "live" vs "pre-cached":
  - The LLM genuinely generates all three drafts each run (real output, no canned
    HTML). That's the part the audience sees being "live".
  - The Jira reads are served from data/demo/<module-slug>-fixture.json, captured
    ahead of time by demo_capture.py. Zero Jira network at showtime — so the demo
    is fast and can't fail on Jira/auth mid-show.
  - The transcript is read for real from disk (it's local anyway).

Run order:
  1) ONCE, ahead of time, with live Jira reachable:
         python demo_capture.py --module "Item Management"
  2) At showtime (no Jira needed):
         python demo.py
  3) View in the UI we built (start it if it isn't running):
         uvicorn app:app --host 127.0.0.1 --port 8000
     Open http://127.0.0.1:8000 → Library tab. The three demo drafts appear there.

Output: writes drafts/<rid>.html + drafts/<rid>.json for each template, in the
exact schema app.py's Library reads — so they render inside the existing UI with
no change to any prod file. (Also keeps a flat demo-<slug>-<template>.html copy.)
"""
import argparse
import asyncio
import json
import re
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    create_sdk_mcp_server,
    query,
    tool,
)

# Reuse the prod system prompt + template loader + user prompt builder so the
# model reasons identically to production. We only swap the tools (offline) and
# the data source (fixture instead of live Jira).
from agent_sdk import (
    BASE_SYSTEM_PROMPT,
    MCP_SERVER_NAME,
    build_user_prompt,
    load_template_prompt,
)
from evaluator_sdk import EVALUATOR_PROMPT, build_evaluator_prompt

APP_DIR = Path(__file__).parent
DEMO_DIR = APP_DIR / "data" / "demo"
# Same locations app.py's Library reads from. We only WRITE data files here —
# app.py itself is untouched.
DRAFTS = APP_DIR / "drafts"
TRANSCRIPTS = APP_DIR / "raw" / "transcripts"
TRANSCRIPT_META = APP_DIR / "raw" / "transcripts" / "metadata"

TEMPLATES = ("long-form", "micro-guide", "tldr")
DEFAULT_MODULE = "Item Management"
DEFAULT_TRANSCRIPT = (
    "raw/transcripts/"
    "20260529-070600-item-management-2026-05-28-item-management-create-items-training.md"
)

# Loaded once at startup from the fixture. Shape:
#   {"module": str, "captured_at": str, "tickets": {key: rec}, "epics": {key: rec}}
_FIX: dict = {}


def _load_fixture(module: str) -> dict:
    slug = module.lower().replace(" ", "-")
    path = DEMO_DIR / f"{slug}-fixture.json"
    if not path.exists():
        raise SystemExit(
            f"ERROR: no fixture at {path}\n"
            f"Run the one-time capture first (needs live Jira):\n"
            f'    python demo_capture.py --module "{module}"'
        )
    return json.loads(path.read_text(encoding="utf-8"))


def _ok(text: str) -> dict:
    return {"content": [{"type": "text", "text": text}]}


def _slug(text: str) -> str:
    """Mirror app.py._slug so resource ids match the Library's expectations."""
    s = re.sub(r"[^a-zA-Z0-9\-]+", "-", text).strip("-").lower()
    return s[:48] or "item"


def _register_transcript(transcript_path: str, module: str) -> str:
    """Register the demo transcript in the same metadata store app.py uses, so
    the Library card has a filename and the Evaluate/Publish flows work if the
    presenter clicks them. Data-file only — does not touch app.py."""
    p = Path(transcript_path)
    if not p.is_absolute():
        p = (APP_DIR / p).resolve()
    tid = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{_slug(module)}-demo"
    TRANSCRIPT_META.mkdir(parents=True, exist_ok=True)
    meta = {
        "id": tid,
        "filename": p.name,
        "module": module,
        "uploaded_at": datetime.now().isoformat(timespec="seconds"),
        "char_count": p.stat().st_size if p.exists() else 0,
        "path": str(p.relative_to(APP_DIR)) if p.is_relative_to(APP_DIR) else str(p),
    }
    (TRANSCRIPT_META / f"{tid}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8"
    )
    return tid


# ============================================================================
# Offline tool set — same names/signatures as tools_sdk, served from _FIX.
# Output strings mirror the live tools byte-for-byte so the model can't tell.
# ============================================================================

@tool(
    "parse_transcript",
    "Read the full text of an uploaded training transcript (Task 1). The "
    "transcript is the immutable source of voice; Jira is behavioral truth.",
    {"transcript_path": str},
)
async def parse_transcript(args):
    p = Path(args["transcript_path"])
    if not p.is_absolute():
        candidate = (APP_DIR / p).resolve()
        if candidate.exists():
            p = candidate
    if not p.exists():
        return _ok(f"ERROR: transcript not found at {p}")
    try:
        text = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = p.read_text(encoding="utf-8", errors="replace")
    return _ok(text)


def _score(rec: dict, terms: list[str]) -> int:
    hay = " ".join([
        rec.get("summary", ""), rec.get("ac", ""), rec.get("rn", ""),
        rec.get("desc", ""), " ".join(rec.get("components", [])),
    ]).lower()
    return sum(hay.count(t) for t in terms)


@tool(
    "match_tickets",
    "Search Cybersoft NXT Jira for tickets matching a SHORT phrase (2–4 words). "
    "Optionally narrow by `module`. Returns up to 5 candidates with key, summary, "
    "status, components, priority, Module, and a description snippet. Each result "
    "includes its parent epic — call `read_epic` next.",
    {"query": str, "module": str},
)
async def match_tickets(args):
    query_str = (args.get("query") or "").strip()
    module = (args.get("module") or "").strip()
    if len(query_str) < 3:
        return _ok("ERROR: query too short — pass a multi-word phrase.")
    terms = [t.lower() for t in query_str.split() if len(t) > 2]
    if not terms:
        return _ok("ERROR: no usable terms in query.")

    scored = []
    for rec in _FIX["tickets"].values():
        # Honor the module filter: never surface another module's tickets.
        if module and (rec.get("module") or "") != module:
            continue
        s = _score(rec, terms)
        if s > 0:
            scored.append((s, rec))
    scored.sort(key=lambda x: (-x[0], x[1].get("key", "")))
    top = scored[:5]

    jql = f'project = NXT AND text ~ "{query_str}" AND "Module" = "{_FIX["module"]}" ORDER BY priority DESC, updated DESC'
    if not top:
        return _ok(f'No tickets matched for: "{query_str}"\nJQL: {jql}')

    lines = [f"[JQL: {jql}]"]
    for _, rec in top:
        comps = ", ".join(rec.get("components", [])) or "-"
        desc_text = rec.get("desc", "")
        snippet = desc_text[:160].replace("\n", " ") + ("…" if len(desc_text) > 160 else "")
        epic_key = rec.get("epic_key", "-")
        epic_sum = rec.get("epic_summary", "")
        lines.append(
            f"{rec.get('key', '?')} | [{rec.get('status', '?')}] [{rec.get('issuetype', '?')}] "
            f"[P:{rec.get('priority', '-')}] [Module:{rec.get('module', '-')}] [RN:{rec.get('rn_required', '-')}]\n"
            f"  {rec.get('summary', '')}\n"
            f"  components: {comps}\n"
            f"  epic: {epic_key}" + (f" — {epic_sum}" if epic_sum else "") + "\n"
            f"  desc [TIER 3 — if cited, token [[{rec.get('key', '?')}:DESC]]; call read_ticket for AC]: {snippet or '(empty)'}"
        )
    return _ok("\n\n".join(lines))


@tool(
    "search_kb",
    "Search the local jira-brain knowledge base for supporting/contradicting "
    "context (Task 3). Returns up to 5 matches with path and snippet.",
    {"query": str},
)
async def search_kb(args):
    # KB is disabled in the demo — tickets+transcript carry the show.
    query_str = (args.get("query") or "").strip()
    return _ok(f'No KB matches for: "{query_str}"  (KB disabled in demo)')


@tool(
    "read_ticket",
    "Fetch one Jira ticket's full content by key. Returns Acceptance Criteria "
    "(TIER 1), Release Notes (TIER 1), Release Notes Internal (TIER 2), and "
    "Description (TIER 3). Quote AC or RN verbatim in citations.",
    {"issue_key": str},
)
async def read_ticket(args):
    key = args["issue_key"].strip().upper()
    rec = _FIX["tickets"].get(key) or _FIX["epics"].get(key)
    if rec is None:
        return _ok(f"ERROR: issue {key} not found.")

    comps = ", ".join(rec.get("components", [])) or "-"
    ac_text = rec.get("ac", "")
    rn_text = rec.get("rn", "")
    rn_internal = rec.get("rn_internal", "")
    desc = rec.get("desc", "")
    rn_title = rec.get("rn_title", "")
    epic_key = rec.get("epic_key", "-")
    epic_sum = rec.get("epic_summary", "")

    parts = [
        f"{key} | [{rec.get('status', '?')}] [{rec.get('issuetype', '?')}] [P:{rec.get('priority', '-')}] {rec.get('summary', '')}",
        f"Module: {rec.get('module', '-')}  |  components: {comps}  |  RN Required: {rec.get('rn_required', '-')}",
        f"Epic: {epic_key}" + (f" — {epic_sum}" if epic_sum else "") + "  (call read_epic for full epic context + sibling tickets)",
        "",
        "CITATION TOKENS — quote ONLY from the blocks below, and copy the EXACT "
        f"[[{key}:TIER]] token shown for the block you quoted into your "
        "<!-- Source --> comment. The tier is FIXED by the block the text lives in; "
        "you do not get to choose it. Text under Description is Tier 3 and must NEVER "
        "be cited as AC.",
    ]
    if rn_title:
        parts.append(f"Release Notes Title: {rn_title}")
    parts.append(f"\n## Acceptance Criteria  [TIER 1 — agreed workflow]  ← cite this text as [[{key}:AC]]\n{ac_text[:4000] if ac_text else '(empty — this ticket has NO AC; do not cite anything as [[' + key + ':AC]])'}")
    parts.append(f"\n## Release Notes  [TIER 1 — customer-facing voice]  ← cite this text as [[{key}:RN]]\n{rn_text[:3000] if rn_text else '(empty)'}")
    if rn_internal:
        parts.append(f"\n## Release Notes (Internal)  [TIER 2]  ← cite this text as [[{key}:RNINT]]\n{rn_internal[:2000]}")
    parts.append(f"\n## Description  [TIER 3 — lowest trust — NEVER cite as AC]  ← cite this text as [[{key}:DESC]] (stays Tier 3)\n{desc[:3000] if desc else '(empty)'}")
    return _ok("\n".join(parts))


@tool(
    "read_epic",
    "Given an epic key, return the epic's summary + Acceptance Criteria + ALL "
    "child stories under it (key, status, summary). Call AFTER match_tickets.",
    {"epic_key": str},
)
async def read_epic(args):
    key = args["epic_key"].strip().upper()
    epic = _FIX["epics"].get(key)
    if epic is None:
        # Mirror prod: a non-epic key still returns, with a warning.
        rec = _FIX["tickets"].get(key)
        if rec is None:
            return _ok(f"ERROR: epic {key} not found.")
        return _ok(
            f"WARNING: {key} is not an Epic (it's {rec.get('issuetype', '?')}). "
            f"Returning what we got, but the children list may be empty — only Epics group stories."
        )

    e_ac = epic.get("ac", "")
    e_rn = epic.get("rn", "")
    e_desc = epic.get("desc", "")

    children_lines = []
    for ck in epic.get("children", []):
        c = _FIX["tickets"].get(ck)
        if c is None:
            continue
        children_lines.append(
            f"  {ck} | [{c.get('status', '?')}] [{c.get('issuetype', '?')}] "
            f"[P:{c.get('priority', '-')}] [RN:{c.get('rn_required', '-')}] {c.get('summary', '')}"
        )

    parts = [
        f"EPIC {key} | [{epic.get('status', '?')}] {epic.get('summary', '')}",
        f"Module: {epic.get('module', '-')}",
    ]
    if e_ac:
        parts.append(f"\n## Epic Acceptance Criteria  [TIER 1]  ← cite this text as [[{key}:AC]]\n{e_ac[:2500]}")
    if e_rn:
        parts.append(f"\n## Epic Release Notes  [TIER 1]  ← cite this text as [[{key}:RN]]\n{e_rn[:1500]}")
    if e_desc:
        parts.append(f"\n## Epic Description  [TIER 3 — NEVER cite as AC]  ← cite this text as [[{key}:DESC]]\n{e_desc[:2000]}")
    parts.append(f"\n## Child stories ({len(children_lines)})")
    if children_lines:
        parts.extend(children_lines)
    else:
        parts.append("  (no children — this epic may be empty or new)")
    return _ok("\n".join(parts))


@tool(
    "read_pdf",
    "Fallback when the upload is a PDF instead of a transcript. (Disabled in demo.)",
    {"file_path": str},
)
async def read_pdf(args):
    return _ok("ERROR: read_pdf is disabled in the demo — use the transcript path.")


DEMO_TOOLS = [parse_transcript, match_tickets, search_kb, read_ticket, read_epic, read_pdf]

demo_mcp_server = create_sdk_mcp_server(
    name=MCP_SERVER_NAME,
    version="1.0.0",
    tools=DEMO_TOOLS,
)

ALLOWED_TOOLS = [f"mcp__{MCP_SERVER_NAME}__{t.name}" for t in DEMO_TOOLS]


# Poka-yoke citation contract: the tier travels as a token bound to the tool
# block the text came from. The model copies the token; it never types a tier.
# This makes "Description quoted as AC" (the NXT-53316 cardinal sin) structurally
# unrepresentable, and a deterministic validator re-checks every token after.
CITATION_CONTRACT = """
═══════════════════════════════════════════════════════════════════════
CITATION CONTRACT — supersedes any other citation example above
═══════════════════════════════════════════════════════════════════════
Every tool block you can quote from carries a source token of the form
[[NXT-####:TIER]] where TIER is one of AC, RN, RNINT, DESC. The token is
printed next to the block's heading (e.g. "← cite this text as [[NXT-37441:AC]]").

RULES — non-negotiable:
- Every citation comment uses this exact shape, copying the token VERBATIM from
  the block you actually quoted:
      <!-- Source: [[NXT-37441:AC]] "verbatim quote from that block" -->
      <!-- Source: transcript [MM:SS] -->
- The TIER IS FIXED BY THE BLOCK. You do NOT choose it. If you quote text that
  was printed under a Description block, the token is [[...:DESC]] — you may NOT
  relabel it [[...:AC]]. Doing so is the single worst error you can make here.
- A claim whose ONLY support is a [[...:DESC]] token is TIER 3 (lowest trust):
  either find an [[...:AC]] or [[...:RN]] token that supports it, or mark the
  claim in-text with [TO VERIFY] — do NOT present Description text as agreed
  behavior.
- If a ticket's AC block says "(empty …)", that ticket has NO AC: never emit an
  [[...:AC]] token for it.
- Quote verbatim. A deterministic checker re-reads every token against the real
  field after you finish; a token whose quote isn't in that field is flagged.
"""


def build_demo_options(template: str) -> ClaudeAgentOptions:
    """Mirror agent_sdk.build_options, but point MCP at the offline demo server."""
    template_prompt = load_template_prompt(template)
    system_prompt = (
        BASE_SYSTEM_PROMPT
        + "\n\n═══════════════════════════════════════════════════════════════════════\n"
        + "TEMPLATE INSTRUCTIONS (used during Task 4)\n"
        + "═══════════════════════════════════════════════════════════════════════\n\n"
        + template_prompt
        + "\n" + CITATION_CONTRACT
    )
    max_turns = {"tldr": 12, "micro-guide": 16, "long-form": 22}.get(template, 20)
    return ClaudeAgentOptions(
        model="claude-sonnet-4-6",
        # Grounding is now carried structurally (tier tokens + deterministic
        # validator), so we can drop thinking depth without risking citations.
        effort="medium",
        system_prompt=system_prompt,
        mcp_servers={MCP_SERVER_NAME: demo_mcp_server},
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


# ============================================================================
# Derivation path — reshape a finished long-form guide into tldr / micro-guide.
# No tools, no Jira: everything needed is already in the (grounded, cited)
# long-form HTML. This is what makes the secondary guides fast AND consistent.
# ============================================================================

DERIVE_SYSTEM_PROMPT = """You are a Learning Content Producer. You are handed a COMPLETE, already fact-checked long-form HTML learning guide. It already contains inline <!-- Source: ... --> citation comments. Your only job: reshape it into a `{template}` guide that follows the TEMPLATE INSTRUCTIONS appended below.

HARD RULES — this is a derivation, not new research:
- Use ONLY information already present in the long-form guide. Do NOT add any new fact, feature, number, label, menu path, or claim that isn't already there.
- PRESERVE the inline <!-- Source: ... --> comments EXACTLY, including their [[NXT-####:TIER]] source tokens. When you compress or merge sentences, keep the citation(s) that backed them. NEVER drop a citation, NEVER invent a new one, and NEVER change a token's tier (e.g. you may not turn [[...:DESC]] into [[...:AC]]).
- You have NO tools. Do not attempt to call any. Everything you need is in the HTML below.
- The target template's LENGTH CEILING IS ABSOLUTE and beats completeness. You are compressing a large source into a much smaller guide — aggressively DROP lower-priority material. Do NOT attempt to preserve every section or feature from the long-form. **tldr ≤500 words / one page; micro-guide ≤1,500 words.**
- Match the target template's section structure and length budget EXACTLY.
- Keep any <blockquote class="discrepancy"> and [TO VERIFY] markers that appear in the source — do not silently resolve them.

OUTPUT FORMAT:
- Plain HTML, no <html>/<head>/<body> wrappers, start with <h1>. No preamble text — the HTML is the deliverable.
"""


def build_derive_options(template: str) -> ClaudeAgentOptions:
    """Options for the derivation pass: NO tools (so it can't hit Jira), small
    turn budget (it's a single reshape turn)."""
    template_prompt = load_template_prompt(template)
    system_prompt = (
        DERIVE_SYSTEM_PROMPT.format(template=template)
        + "\n\n═══════════════════════════════════════════════════════════════════════\n"
        + "TEMPLATE INSTRUCTIONS\n"
        + "═══════════════════════════════════════════════════════════════════════\n\n"
        + template_prompt
        + "\n" + CITATION_CONTRACT
    )
    return ClaudeAgentOptions(
        model="claude-sonnet-4-6",
        effort="medium",  # reshape-only; tokens carry the grounding
        system_prompt=system_prompt,
        allowed_tools=[],
        disallowed_tools=[
            "Read", "Write", "Edit", "Bash", "PowerShell", "Glob", "Grep",
            "WebFetch", "WebSearch", "Task", "TaskCreate", "TaskGet",
            "TaskList", "TaskUpdate", "TaskOutput", "TaskStop",
            "NotebookEdit", "Skill", "AskUserQuestion",
        ],
        tools=[],
        max_turns=4,
    )


def build_derive_prompt(long_form_html: str, template: str, module: str) -> str:
    return (
        f"Reshape this finished long-form guide for module `{module}` into a "
        f"`{template}` guide, following the template instructions in your system "
        f"prompt. Preserve every <!-- Source: ... --> citation. Output ONLY the "
        f"HTML (start with <h1>), no surrounding text.\n\n"
        f"=== LONG-FORM GUIDE (the source to reshape) ===\n{long_form_html}"
    )


async def derive(template: str, long_form_html: str, module: str) -> tuple[str, str, dict]:
    """Derive a tldr/micro-guide from a finished long-form guide. No tools."""
    options = build_derive_options(template)
    prompt = build_derive_prompt(long_form_html, template, module)
    html, metrics = await _run_query(prompt, options, f"deriving {template}")
    return template, html, metrics


# ============================================================================
# Offline evaluator — same prompt as prod, but read_ticket serves the fixture.
# Used to grade each draft on the four grounding bars after generation.
# ============================================================================

_EVAL_SERVER_NAME = "evaluator_tools"
_demo_eval_server = create_sdk_mcp_server(
    name=_EVAL_SERVER_NAME, version="1.0.0", tools=[read_ticket]
)


def build_demo_evaluator_options() -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        model="claude-sonnet-4-6",
        system_prompt=EVALUATOR_PROMPT,
        mcp_servers={_EVAL_SERVER_NAME: _demo_eval_server},
        allowed_tools=[f"mcp__{_EVAL_SERVER_NAME}__read_ticket"],
        disallowed_tools=[
            "Read", "Write", "Edit", "Bash", "PowerShell", "Glob", "Grep",
            "WebFetch", "WebSearch", "Task", "TaskCreate", "TaskGet",
            "TaskList", "TaskUpdate", "TaskOutput", "TaskStop",
            "NotebookEdit", "Skill", "AskUserQuestion",
        ],
        tools=[],
        max_turns=8,
    )


def _parse_eval_json(text: str) -> dict | None:
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


async def evaluate_draft(html: str, transcript_text: str, template: str, module: str,
                         draft_cap: int = 120000) -> dict:
    """Grade one draft on the grounding bars. Returns the evaluator JSON.
    NOTE: includes the FULL draft (long-form guides run ~50K chars; the old
    20K cap made the evaluator judge half a document and falsely flag the back
    half as 'missing sections')."""
    options = build_demo_evaluator_options()
    prompt = (
        f"Grade this draft `{template}` learning guide for the `{module}` module.\n\n"
        f"=== TRANSCRIPT (source) ===\n{transcript_text[:8000]}\n\n"
        f"=== FULL DRAFT HTML (to grade — source comments preserved for citation spot-check) ===\n"
        f"{html[:draft_cap]}\n\n"
        f"Run all checks against the ENTIRE document above. Spot-check 2-3 ticket "
        f"citations via read_ticket. Emit ONLY the JSON object as your final message."
    )
    chunks: list[str] = []
    try:
        async for msg in query(prompt=prompt, options=options):
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        chunks.append(block.text)
    except Exception as e:
        return {"verdict": "error", "summary": f"evaluator failed: {e}", "checks": []}
    return _parse_eval_json("\n".join(chunks)) or {
        "verdict": "error", "summary": "could not parse evaluator JSON", "checks": [],
    }


SOURCE_COMMENT_RE = re.compile(r"<!--\s*Source:[\s\S]*?-->")

# ── Deterministic citation validator — the exact-match "CitationAgent" ──
# Re-checks every [[NXT-####:TIER]] token against the real fixture field. No LLM:
# string-matching against ground truth is strictly better for exact-quote tiering.
_TOKEN_RE = re.compile(r"\[\[(NXT-\d+):(AC|RN|RNINT|DESC)\]\]")
_QUOTE_RE = re.compile(r"[\"“]([^\"”]{6,})[\"”]")
_FIELD_BY_TIER = {"AC": "ac", "RN": "rn", "RNINT": "rn_internal", "DESC": "desc"}


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip().lower()


def validate_citations(html: str) -> dict:
    """Verify every tier token against ground-truth fields. Returns an integrity report."""
    rpt = {"total": 0, "tokened": 0, "ok": 0, "tier_lie": 0, "quote_not_found": 0,
           "untokened_ticket": 0, "transcript": 0, "violations": []}
    for cm in re.findall(r"<!--\s*Source:([\s\S]*?)-->", html):
        rpt["total"] += 1
        tok = _TOKEN_RE.search(cm)
        if not tok:
            if re.search(r"transcript", cm, re.I):
                rpt["transcript"] += 1
            elif re.search(r"NXT-\d+", cm):
                rpt["untokened_ticket"] += 1
            continue
        rpt["tokened"] += 1
        key, tier = tok.group(1), tok.group(2)
        qm = _QUOTE_RE.search(cm)
        rec = _FIX["tickets"].get(key) or _FIX["epics"].get(key) or {}
        fields = {t: _norm(rec.get(f, "")) for t, f in _FIELD_BY_TIER.items()}
        if not qm:
            rpt["violations"].append((key, tier, "no-quote", ""))
            continue
        quote = _norm(qm.group(1))
        if quote and quote in fields.get(tier, ""):
            rpt["ok"] += 1
        else:
            found_in = [t for t, txt in fields.items() if quote and quote in txt]
            if found_in:
                rpt["tier_lie"] += 1
                rpt["violations"].append((key, tier, "tier_lie->" + "/".join(found_in), qm.group(1)[:60]))
            else:
                rpt["quote_not_found"] += 1
                rpt["violations"].append((key, tier, "quote_not_found", qm.group(1)[:60]))
    return rpt


def enforce_citations(html: str) -> tuple[str, dict]:
    """Deterministically fix the cardinal sin: any token whose quote lives in a
    DIFFERENT field than claimed is relabeled to its true tier, with a visible
    note. This guarantees zero Description-as-AC, independent of the model."""
    counts = {"relabeled": 0}

    def _fix(m: re.Match) -> str:
        cm = m.group(0)
        tok = _TOKEN_RE.search(cm)
        qm = _QUOTE_RE.search(cm)
        if not tok or not qm:
            return cm
        key, tier = tok.group(1), tok.group(2)
        quote = _norm(qm.group(1))
        rec = _FIX["tickets"].get(key) or _FIX["epics"].get(key) or {}
        fields = {t: _norm(rec.get(f, "")) for t, f in _FIELD_BY_TIER.items()}
        if quote and quote in fields.get(tier, ""):
            return cm  # correct already
        found = [t for t, txt in fields.items() if quote and quote in txt]
        if found:  # tier-lie → relabel to the field it actually came from
            actual = found[0]
            counts["relabeled"] += 1
            fixed = cm.replace(f"[[{key}:{tier}]]", f"[[{key}:{actual}]]")
            return fixed.replace("-->", f"[auto-corrected {tier}->{actual}, Tier-3 unless verified] -->")
        return cm  # quote_not_found: can't safely auto-fix; left for the report

    fixed_html = re.sub(r"<!--\s*Source:[\s\S]*?-->", _fix, html)
    return fixed_html, counts


def _extract_html(text: str) -> str:
    """Strip a ```html fence if present, then trim to the first heading."""
    t = text.strip()
    fence = re.search(r"```html\s*(.*?)```", t, re.DOTALL | re.IGNORECASE)
    if fence:
        t = fence.group(1).strip()
    else:
        t = re.sub(r"^```html\s*", "", t, flags=re.IGNORECASE).strip()
        t = re.sub(r"```$", "", t).strip()
    m = re.search(r"<h[1-2][ >]", t, re.IGNORECASE)
    if m:
        t = t[m.start():]
    return t


def _usage_brief(usage: dict | None) -> dict:
    """Pull the telemetry that settles 'output vs thinking time' from a usage dict."""
    u = usage or {}
    return {
        "input_tokens": u.get("input_tokens"),
        "output_tokens": u.get("output_tokens"),
        "cache_read_input_tokens": u.get("cache_read_input_tokens"),
        "cache_creation_input_tokens": u.get("cache_creation_input_tokens"),
        # surfaced if the SDK breaks thinking out separately:
        "thinking_tokens": u.get("thinking_tokens") or u.get("reasoning_tokens"),
    }


async def _run_query(prompt: str, options: ClaudeAgentOptions, label: str) -> tuple[str, dict]:
    """Run one query(), returning (html, metrics). metrics carries timing + token usage."""
    t0 = time.monotonic()
    chunks: list[str] = []
    metrics: dict = {"usage": None, "duration_api_ms": None, "num_turns": None}
    try:
        async for msg in query(prompt=prompt, options=options):
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        chunks.append(block.text)
            elif isinstance(msg, ResultMessage):
                metrics["usage"] = _usage_brief(getattr(msg, "usage", None))
                metrics["duration_api_ms"] = getattr(msg, "duration_api_ms", None)
                metrics["num_turns"] = getattr(msg, "num_turns", None)
                metrics["cost_usd"] = getattr(msg, "total_cost_usd", None)
    except Exception as e:  # demo robustness — one stage failing shouldn't kill the show
        metrics["secs"] = time.monotonic() - t0
        metrics["error"] = str(e)
        return f"<!-- ERROR {label}: {e} -->", metrics
    metrics["secs"] = time.monotonic() - t0
    html = _extract_html("\n".join(chunks)) if chunks else "<!-- no output -->"
    return html, metrics


async def generate(template: str, transcript_path: str, module: str) -> tuple[str, str, dict]:
    """Run one template end-to-end (full Tasks 1-4). Returns (template, html, metrics)."""
    options = build_demo_options(template)
    user_prompt = build_user_prompt(transcript_path, module, template)
    html, metrics = await _run_query(user_prompt, options, f"generating {template}")
    return template, html, metrics


def _words(html: str) -> int:
    """Rough visible word count: strip tags + source comments."""
    txt = SOURCE_COMMENT_RE.sub("", html)
    txt = re.sub(r"<[^>]+>", " ", txt)
    return len(txt.split())


async def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--module", default=DEFAULT_MODULE)
    ap.add_argument("--transcript", default=DEFAULT_TRANSCRIPT)
    ap.add_argument("--no-eval", action="store_true", help="skip the grounding eval pass")
    ap.add_argument("--label", default="A:bound-only", help="run label for the telemetry header")
    args = ap.parse_args()

    global _FIX
    _FIX = _load_fixture(args.module)
    print(
        f"[{args.label}] fixture: {len(_FIX.get('tickets', {}))} tickets + "
        f"{len(_FIX.get('epics', {}))} epics (module '{_FIX.get('module')}')"
    )

    DRAFTS.mkdir(parents=True, exist_ok=True)
    transcript_id = _register_transcript(args.transcript, args.module)
    transcript_filename = Path(args.transcript).name
    slug = _slug(args.module)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    def _write_draft(template: str, html: str, metrics: dict, derived_from: str | None) -> None:
        rid = f"{stamp}-{slug}-{template}-{uuid.uuid4().hex[:6]}"
        (DRAFTS / f"{rid}.html").write_text(html, encoding="utf-8")
        draft_meta = {
            "id": rid, "status": "draft", "module": args.module, "template": template,
            "transcript_id": transcript_id, "transcript_filename": transcript_filename,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "demo": True, "run_label": args.label,
            "gen_seconds": round(metrics.get("secs", 0), 1),
            "usage": metrics.get("usage"),
        }
        if derived_from:
            draft_meta["derived_from"] = derived_from
        (DRAFTS / f"{rid}.json").write_text(json.dumps(draft_meta, indent=2), encoding="utf-8")
        (APP_DIR / f"demo-{slug}-{template}.html").write_text(html, encoding="utf-8")

    results: list[tuple[str, str, dict, str | None]] = []

    enforce_log: dict[str, int] = {}

    t0 = time.monotonic()
    # Step 1 — long-form (full research + citations).
    print("Step 1: generating long-form (full research, the long pole)…")
    _, lf_html, lf_metrics = await generate("long-form", args.transcript, args.module)
    lf_html, enf = enforce_citations(lf_html)  # deterministic cardinal-sin fix
    enforce_log["long-form"] = enf["relabeled"]
    _write_draft("long-form", lf_html, lf_metrics, None)
    results.append(("long-form", lf_html, lf_metrics, None))

    # Step 2 — derive the two short guides FROM the corrected long-form, in parallel.
    print("Step 2: deriving micro-guide + tldr from the long-form (no Jira)…")
    derived = await asyncio.gather(
        derive("micro-guide", lf_html, args.module),
        derive("tldr", lf_html, args.module),
    )
    for template, html, metrics in derived:
        html, enf = enforce_citations(html)
        enforce_log[template] = enf["relabeled"]
        _write_draft(template, html, metrics, "long-form")
        results.append((template, html, metrics, "long-form"))
    total = time.monotonic() - t0

    # ── Telemetry table — the output-vs-thinking signal the A/B needs ──
    print(f"\n=== TELEMETRY [{args.label}] ===")
    print(f"{'stage':<12} {'secs':>7} {'words':>7} {'chars':>8} {'out_tok':>8} {'in_tok':>8} {'cache_rd':>9} {'think_tok':>9}")
    for template, html, m, _ in results:
        u = m.get("usage") or {}
        print(f"{template:<12} {m.get('secs', 0):7.1f} {_words(html):7d} {len(html):8d} "
              f"{str(u.get('output_tokens')):>8} {str(u.get('input_tokens')):>8} "
              f"{str(u.get('cache_read_input_tokens')):>9} {str(u.get('thinking_tokens')):>9}")
    print(f"\nTotal wall time: {total:.1f}s  (long-form {lf_metrics.get('secs', 0):.0f}s + derivations)")

    # ── Deterministic citation integrity — the cardinal-sin check, exact-match ──
    print(f"\n=== CITATION INTEGRITY [{args.label}]  (tier_lie should be 0 after enforce) ===")
    print(f"{'stage':<12} {'cites':>6} {'tokened':>8} {'ok':>5} {'tier_lie':>9} {'not_found':>10} {'autofix':>8}")
    for template, html, _, _ in results:
        r = validate_citations(html)  # run on the ENFORCED html now in results
        print(f"{template:<12} {r['total']:6d} {r['tokened']:8d} {r['ok']:5d} "
              f"{r['tier_lie']:9d} {r['quote_not_found']:10d} {enforce_log.get(template, 0):8d}")
        for key, tier, kind, q in r["violations"][:4]:
            print(f"    ⚠ {key}:{tier} {kind}  “{q}”")

    # ── Eval pass — the four grounding bars per stage ──
    if not args.no_eval:
        transcript_text = ""
        tp = Path(args.transcript)
        if not tp.is_absolute():
            tp = (APP_DIR / tp).resolve()
        if tp.exists():
            transcript_text = tp.read_text(encoding="utf-8")
        print(f"\n=== EVAL (grounding bars) [{args.label}] ===")
        verdicts = await asyncio.gather(*(
            evaluate_draft(html, transcript_text, template, args.module)
            for template, html, _, _ in results
        ))
        for (template, *_), ev in zip(results, verdicts):
            checks = "; ".join(f"{c.get('name')}={c.get('status')}" for c in (ev.get("checks") or []))
            print(f"\n{template}: VERDICT={str(ev.get('verdict')).upper()}  (wc={ev.get('word_count')})")
            print(f"  {ev.get('summary')}")
            if checks:
                print(f"  checks: {checks}")
    print("\nView in the UI:  uvicorn app:app --host 127.0.0.1 --port 8000  → Library tab.")


if __name__ == "__main__":
    asyncio.run(main())
