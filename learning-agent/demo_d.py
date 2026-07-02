"""Cell D — sectioned generation + quote registry (the CitationAgent-as-architecture).

The fix the research converged on, after Cells A–C showed:
  - truncation is STRUCTURAL (single-turn 10-section write hits an output ceiling)
  - the writer paraphrases under medium effort → Description-as-AC leaks past an
    exact-match validator as `not_found`.

Cell D removes BOTH by changing the contract: the writer is never allowed to type
quote text or a tier label. It emits only [CITE:<id>] markers. A deterministic
assembler renders the exact span + tier from a quote registry built straight from
the fixture (ground truth). So:
  - wrong tier is impossible by construction (tier comes from the registry)
  - not_found is impossible (the quote IS the registry span)
  - truncation is gone (each section is its own bounded turn)

Pipeline:
  Plan (research, tools on) -> build registry from fixture -> N bounded section
  writers (tools off, CITE-IDs only, parallel) -> deterministic assemble+render
  -> strict validation -> LLM eval (semantic support backstop only).

Focused on the long-form (where the failures live). Derivations are deferred to a
follow-up once long-form clears Cell D's pass criteria — keeps the variable isolated.

Run:  python demo_d.py            (needs data/demo/<module>-fixture.json)
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
    query,
)

# Reuse the offline tools, fixture loader, eval, and helpers from the demo.
import demo
from demo import (
    APP_DIR,
    DRAFTS,
    MCP_SERVER_NAME,
    _load_fixture,
    _norm,
    _register_transcript,
    _slug,
    _words,
    build_demo_evaluator_options,
    demo_mcp_server,
    evaluate_draft,
    validate_citations,
)
from demo import ALLOWED_TOOLS as DEMO_ALLOWED_TOOLS
from citation_gate import run_gate
from config import citations_enabled

DEFAULT_MODULE = "Item Management"
DEFAULT_TRANSCRIPT = demo.DEFAULT_TRANSCRIPT
SECTION_CONCURRENCY = 4  # cap parallel section writers (CLI subprocesses are heavy)

_DISALLOWED = [
    "Read", "Write", "Edit", "Bash", "PowerShell", "Glob", "Grep",
    "WebFetch", "WebSearch", "Task", "TaskCreate", "TaskGet",
    "TaskList", "TaskUpdate", "TaskOutput", "TaskStop",
    "NotebookEdit", "Skill", "AskUserQuestion",
    "EnterPlanMode", "ExitPlanMode", "EnterWorktree", "ExitWorktree",
    "CronCreate", "CronDelete", "CronList",
    "Monitor", "PushNotification", "RemoteTrigger", "ScheduleWakeup",
]


# ============================================================================
# Quote registry — built deterministically from the fixture (GROUND TRUTH).
# ============================================================================
_TIER_FIELDS = [("AC", "ac"), ("RN", "rn"), ("RNINT", "rn_internal"), ("DESC", "desc")]


def build_registry(ticket_keys: list[str]) -> tuple[dict, dict]:
    """Return (registry, by_ticket). registry[id] = {issue, tier, span}."""
    registry: dict[str, dict] = {}
    by_ticket: dict[str, list[str]] = {}
    for key in dict.fromkeys(ticket_keys):  # dedupe, preserve order
        rec = demo._FIX["tickets"].get(key) or demo._FIX["epics"].get(key)
        if not rec:
            continue
        ids: list[str] = []
        for tier, field in _TIER_FIELDS:
            text = (rec.get(field) or "").strip()
            if not text:
                continue
            spans = [s.strip() for s in re.split(r"\n+", text) if len(s.strip()) >= 8]
            for i, span in enumerate(spans, 1):
                cid = f"{key}:{tier}:{i:02d}"
                registry[cid] = {"issue": key, "tier": tier, "span": span}
                ids.append(cid)
        by_ticket[key] = ids
    return registry, by_ticket


# ============================================================================
# Transcript-only registry — built from VERBATIM transcript spans (NO Jira).
# Same grounding-by-construction contract as the Jira path: the section writer
# emits [CITE:T####] ids only; assemble() renders the exact transcript span; the
# gate (validate_citations(html, transcript_text=…)) re-verifies each span appears
# verbatim in the transcript. Use case: the navigation/procedure an SME demos live
# that Jira (behavior-only) never records, and modules with no captured fixture.
# ============================================================================
_T_MIN_SPAN = 25  # ignore trivially short lines (speaker tags, "OK", bare timestamps)


def split_transcript_spans(text: str) -> list[str]:
    """Split a transcript into verbatim, citable spans at the blank-line (utterance)
    boundary. Each span is sanitized identically to how the gate will verify it."""
    spans: list[str] = []
    for block in re.split(r"\n\s*\n", text or ""):
        s = demo.sanitize_span(block)
        if len(s) >= _T_MIN_SPAN:
            spans.append(s)
    return spans


def build_transcript_registry(text: str) -> tuple[dict, dict, list[str]]:
    """Return (registry, by_span, ids). registry[id] = {issue:'TRANSCRIPT',
    tier:'T####', span}. by_span mirrors by_ticket so write_section/_citation_menu
    work unchanged (each span id maps to itself)."""
    registry: dict[str, dict] = {}
    by_span: dict[str, list[str]] = {}
    ids: list[str] = []
    for i, span in enumerate(split_transcript_spans(text), 1):
        cid = f"T:{i:04d}"
        registry[cid] = {"issue": "TRANSCRIPT", "tier": f"T{i:04d}", "span": span}
        by_span[cid] = [cid]
        ids.append(cid)
    return registry, by_span, ids


def transcript_span_menu(registry: dict, ids: list[str]) -> str:
    """The numbered span list the planner reads to assign spans to sections."""
    return "\n".join(f"[{cid}] {registry[cid]['span']}" for cid in ids)


_T_PLAN_TEMPLATE = """You are the PLANNER for a __LABEL__ on the `__MODULE__` module, grounded ONLY in a training transcript. There is NO Jira here — every claim the writers make MUST quote the transcript verbatim, so plan only what the transcript actually supports.

The user message contains the transcript split into numbered verbatim spans [T:0001]…[T:NNNN]. You do NOT write the guide; you produce a SECTION PLAN as JSON and assign to each section the span ids whose content supports it.

__SPEC__
   Do NOT include a "Sources" section — it is generated automatically from the citations.
   Assign to each section's "span_ids" ONLY ids that appear in the provided list and that genuinely back that section. A purely structural section (e.g. "Related Content") may have [].
   Do NOT invent span ids. Do NOT plan a section the transcript spans cannot support.

OUTPUT — your FINAL message must be ONLY this JSON object, no prose, no fence:
{
  "sections": [
    {"id": "s1", "title": "...", "scope": "1-2 sentence description", "span_ids": ["T:0001"]}
  ]
}"""


def transcript_plan_system_prompt(module: str, fmt: str) -> str:
    # NOTE: keep this SMALL. The SDK passes system_prompt as a CLI argument
    # (--system-prompt), which is subject to the OS command-line length limit
    # (~32KB on Windows). The (potentially large) numbered span list is passed in
    # the USER prompt instead (delivered over stdin, no length limit).
    return (_T_PLAN_TEMPLATE
            .replace("__LABEL__", _FORMAT_LABEL.get(fmt, fmt))
            .replace("__MODULE__", module)
            .replace("__SPEC__", _FORMAT_SPEC.get(fmt, _FORMAT_SPEC["long-form"])))


# ============================================================================
# Stage 1 — Plan (research with tools, emit JSON section plan, NO writing).
# Format-parameterized: all three formats use the SAME registry + CITE-ID +
# deterministic pipeline; only the required section list and budgets differ.
# ============================================================================
VALID_FORMATS = ("long-form", "micro-guide", "tldr", "release-notes")

_FORMAT_LABEL = {
    "long-form": "long-form learning guide",
    "micro-guide": "micro-guide",
    "tldr": "TLDR one-pager",
    "release-notes": "customer release notes",
}

_FORMAT_SPEC = {
    "long-form": (
        '   The guide MUST use these top-level sections, IN THIS ORDER, EXACT titles:\n'
        '   - "Overview"\n'
        '   - "Roles & Permissions"\n'
        '   - "Prerequisites"\n'
        '   - one "Workflow: <name>" section per major taught workflow (3–6 of them)\n'
        '   - "Key Fields & Statuses"\n'
        '   - "Reports & Outputs"\n'
        '   - "Exceptions & Troubleshooting"\n'
        '   - "Related Content"\n'
        '   Aim for 9–14 sections total (a comprehensive reference).'
    ),
    "micro-guide": (
        '   The guide MUST use these top-level sections, IN THIS ORDER, EXACT titles:\n'
        '   - "Purpose"\n'
        '   - "Who This Is For"\n'
        '   - "Before You Start"\n'
        '   - one "Workflow: <name>" section per TOP workflow (3–5 of them, highest-priority ONLY)\n'
        '   - "Common Mistakes"\n'
        '   - "Related Content"\n'
        '   6–9 sections total. Concise task guide, NOT a full reference — pick the top workflows only.'
    ),
    "tldr": (
        '   The guide MUST use EXACTLY these 5 sections, IN THIS ORDER, EXACT titles:\n'
        '   - "What This Module Does"\n'
        '   - "Key Features"\n'
        '   - "Common Workflows"\n'
        '   - "Gotchas"\n'
        '   - "Where To Go Next"\n'
        '   A one-glance scan card — HARD CEILING 500 words for the WHOLE guide. Every section is 1-2 lines; '
        '"Key Features" is a compact table of AT MOST 8 rows, one terse line each. Cut aggressively to stay under 500.'
    ),
    "release-notes": (
        '   This is CUSTOMER RELEASE NOTES for the release the recording reviews — NOT a how-to guide.\n'
        '   SELECTION: include the changes the review actually covered. Keep ONLY externally-facing tickets\n'
        '   (Release Notes Required = "External Only" or "External/Internal"); EXCLUDE "Internal Only" / "Not Required".\n'
        '   VOICE: each entry is grounded in the ticket\'s Release Notes (RN) field — the customer-facing voice (Tier 1);\n'
        '   use AC only to confirm behavior, never internal jargon.\n'
        '   STRUCTURE — use these top-level sections, IN THIS ORDER, only those that have content:\n'
        '   - "What\'s New" (New Feature / Feature / Story tickets that add capability)\n'
        '   - "Enhancements" (Enhancement / Improvement tickets)\n'
        '   - "Fixes" (Bug tickets — describe the customer-visible fix, not the internal cause)\n'
        '   - "Known Limitations" (Tech-Debt / explicitly-noted caveats; omit if none)\n'
        '   Each entry: a short bolded title (use the Release Notes Title when present) + 1-2 customer-facing sentences,\n'
        '   each [CITE:…:RN] (or :AC to confirm behavior). One entry per ticket. Group by change type above, newest-feature-first.'
    ),
}

_FORMAT_BUDGET = {
    "long-form": "120–350 words",
    "micro-guide": "60–140 words",
    "tldr": "AT MOST 1–2 short sentences for this section (Key Features may be a compact table, MAX 8 rows, one terse line each). The ENTIRE guide MUST stay under 500 words — be ruthlessly terse; if unsure, cut.",
    "release-notes": "1–2 customer-facing sentences per change entry; group entries under this section's change-type heading. Concise and scannable.",
}

_PLAN_TEMPLATE = """You are the PLANNER for a __LABEL__ on the `__MODULE__` module. You do research, then output a SECTION PLAN as JSON. You do NOT write the guide.

Tools (call in parallel where you can): parse_transcript, match_tickets, read_epic, read_ticket, search_kb. Caps: ≤6 match_tickets, ≤4 read_epic, ≤8 read_ticket, ≤4 search_kb.

Steps:
1. parse_transcript on the given path.
2. Identify the workflows/features the PRESENTER actually taught.
3. match_tickets per feature, read_epic for unique epics, read_ticket for the most behaviorally relevant tickets to confirm which tickets back each feature.
   MINE ALL TICKET TYPES — not just Stories. Each carries different, citable signal (the match_tickets results show the type in [brackets]):
     - Bug tickets        -> known issues / "Gotchas" / "Common mistakes" / "Fixes"
     - Task tickets       -> setup steps / "Prerequisites"
     - Tech-Debt tickets  -> "Known limitations" / caveats
     - Epics              -> the theme and section grouping
   Deliberately pull the right ticket TYPE for the right section, and assign those keys to that section's ticket_keys.
3b. For navigation, menu paths, UI labels, or customer-facing step order, you MAY call search_kb to cross-check against the SME-curated guides (guides are navigation-authoritative; tickets are behavior-authoritative). This informs section scope only — it does NOT add citations; every written claim still cites Jira/transcript.
4. Produce a SECTION PLAN:
__SPEC__
   Do NOT include a "Sources" section — it is generated automatically from the citations.
   Each section names the EXACT Jira ticket keys whose Acceptance Criteria / Release Notes back its claims (only keys you actually read). ticket_keys may be [] for "Related Content" or a lightly-touched section.

OUTPUT — your FINAL message must be ONLY this JSON object, no prose, no fence:
{
  "sections": [
    {"id": "s1", "title": "...", "scope": "1-2 sentence description", "ticket_keys": ["NXT-1234"]}
  ]
}
Rules: use the EXACT section titles specified above; do not invent ticket keys."""


def plan_system_prompt(module: str, fmt: str = "long-form") -> str:
    return (_PLAN_TEMPLATE
            .replace("__LABEL__", _FORMAT_LABEL.get(fmt, fmt))
            .replace("__MODULE__", module)
            .replace("__SPEC__", _FORMAT_SPEC.get(fmt, _FORMAT_SPEC["long-form"])))


def _parse_json(text: str) -> dict | None:
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


# ============================================================================
# Stage 2 — Section writer (tools OFF, emits [CITE:id] markers ONLY).
# ============================================================================
SECTION_SYSTEM_PROMPT = """You are writing ONE section of a learning guide for the `{module}` module. You have NO tools.

THE CITATION CONTRACT — this is the whole point:
- You may NOT type quote text, tier labels, ticket field names, or <!-- Source --> comments.
- To support a claim, append a marker [CITE:<id>] immediately after the sentence, using ONLY ids from the AVAILABLE CITATIONS list below. A deterministic assembler will replace each marker with the exact verbatim quote and tier — that is not your job.
- If a factual claim has no supporting id in the list, CUT the claim. Do not assert un-citable specifics.
- You may cite the transcript with [CITE:transcript MM:SS] for voice/teaching-style claims only (never for product behavior).

LENGTH: keep this section tight — {budget}. Prefer short paragraphs, lists, and one compact table over prose.

OUTPUT: an HTML fragment for THIS section only, starting with <h2>{title}</h2>. Semantic tags only. No <h1>, no wrapper text, no preamble."""

# Transcript-only mode: the transcript IS the source of truth (not a voice-only
# aside), so the contract is identical but the citations are verbatim transcript
# spans. The writer still emits [CITE:id] markers ONLY and never types quote text.
SECTION_SYSTEM_PROMPT_TRANSCRIPT = """You are writing ONE section of a learning guide for the `{module}` module. You have NO tools. This guide is grounded ONLY in the training transcript — there is no Jira, so the transcript is your single source of truth.

THE CITATION CONTRACT — this is the whole point:
- You may NOT type quote text, source labels, or <!-- Source --> comments.
- To support a claim, append a marker [CITE:<id>] immediately after the sentence, using ONLY ids from the AVAILABLE CITATIONS list below. A deterministic assembler replaces each marker with the exact verbatim transcript span — that is not your job.
- If a claim has no supporting id in the list, CUT it. Do not assert anything the transcript spans do not say — no Jira knowledge, no product behavior the presenter did not demonstrate, no invented specifics.
- Write what the presenter actually taught: navigation, menu paths, the order of steps, what they clicked and said.

LENGTH: keep this section tight — {budget}. Prefer short paragraphs, lists, and one compact table over prose.

OUTPUT: an HTML fragment for THIS section only, starting with <h2>{title}</h2>. Semantic tags only. No <h1>, no wrapper text, no preamble."""


def build_section_options(module: str, title: str, budget: str,
                          system_tmpl: str = SECTION_SYSTEM_PROMPT) -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        model="claude-sonnet-4-6",
        effort="medium",
        system_prompt=system_tmpl.format(module=module, title=title, budget=budget),
        allowed_tools=[],
        disallowed_tools=_DISALLOWED,
        tools=[],
        max_turns=4,
    )


def friendly_agent_error(result_text: str | None = None,
                         api_error_status: int | None = None,
                         exc: Exception | None = None) -> str:
    """Turn an agent/CLI failure into a human-actionable message.

    The Agent SDK collapses a CLI ``is_error`` result whose ``errors`` list is
    empty into the cryptic ``"Claude Code returned an error result: <subtype>"``.
    For an API auth failure the CLI's legacy ``subtype`` is still ``"success"``,
    so the surfaced text becomes the actively-misleading ``"...error result:
    success"``. Prefer the ResultMessage's own ``result`` text when we captured
    it (e.g. ``"Failed to authenticate. API Error: 401 ..."``) and append a fix
    hint when the failure smells like expired CLI auth.
    """
    msg = (result_text or "").strip()
    if not msg and exc is not None:
        msg = str(exc).strip()
    if not msg:
        msg = "the content agent returned an error"
    low = msg.lower()
    is_auth = (
        api_error_status == 401
        or "authenticat" in low          # "authenticate" / "authentication"
        or "401" in low
        or "error result: success" in low  # the SDK's masked-401 signature
    )
    if is_auth:
        msg += (
            " — the Claude CLI's OAuth token has expired or is invalid; "
            "run `claude login` to re-authenticate, then retry."
        )
    return msg


async def _run(prompt: str, options: ClaudeAgentOptions) -> dict:
    """Run one query(); capture text, stop_reason, usage, timing."""
    t0 = time.monotonic()
    chunks: list[str] = []
    out = {"text": "", "stop_reason": None, "usage": None, "secs": 0.0}
    try:
        async for msg in query(prompt=prompt, options=options):
            if isinstance(msg, AssistantMessage):
                for b in msg.content:
                    if isinstance(b, TextBlock):
                        chunks.append(b.text)
            elif isinstance(msg, ResultMessage):
                out["stop_reason"] = getattr(msg, "stop_reason", None)
                out["usage"] = getattr(msg, "usage", None)
                if getattr(msg, "is_error", False):
                    # Capture the CLI's real error text NOW — the SDK will
                    # otherwise collapse the trailing ProcessError into the
                    # misleading "error result: success" (see friendly_agent_error).
                    out["error"] = friendly_agent_error(
                        getattr(msg, "result", None),
                        getattr(msg, "api_error_status", None),
                    )
    except Exception as e:
        # Keep the specific result-level error if we already captured one.
        if not out.get("error"):
            out["error"] = friendly_agent_error(exc=e)
        out["text"] = f"<!-- ERROR: {out['error']} -->"
        out["secs"] = time.monotonic() - t0
        return out
    out["text"] = "\n".join(chunks)
    # is_error with no exception (clean stream end): make _section_ok fail loudly.
    if out.get("error") and not out["text"].strip():
        out["text"] = f"<!-- ERROR: {out['error']} -->"
    out["secs"] = time.monotonic() - t0
    return out


def _citation_menu(by_ticket: dict, registry: dict, ticket_keys: list[str]) -> str:
    """Render the AVAILABLE CITATIONS list for a section's allowed tickets."""
    lines = []
    for key in dict.fromkeys(ticket_keys):
        for cid in by_ticket.get(key, []):
            e = registry[cid]
            lines.append(f"[CITE:{cid}] ({e['tier']}) — {e['span'][:200]}")
    return "\n".join(lines) if lines else "(no citations available — write only what the transcript supports, with [CITE:transcript MM:SS])"


def _section_ok(frag: str) -> bool:
    """A section is usable if it produced real HTML (not an SDK error placeholder)."""
    if not frag or "Claude Code returned an error" in frag or frag.lstrip().startswith("<!-- ERROR"):
        return False
    return bool(re.search(r"<h[1-6]", frag, re.I)) or len(frag) > 60


async def _write_section_via_citations(sec: dict, registry: dict, module: str,
                                       sem: asyncio.Semaphore, directive: str = "") -> dict:
    """Version B writer: the Citations API produces the grounded spans. Returns the SAME
    section shape as write_section ({title, html-with-[CITE:id], ...}) and merges synthetic,
    section-namespaced registry entries so the existing assemble() renders them verbatim."""
    import time as _time
    import citations_client  # lazy: Version A never imports anthropic

    t0 = _time.monotonic()
    title = sec.get("title", "Section")
    sid = sec.get("id") or _slug(title)  # section id namespaces cite-ids (no cross-section collision)
    docs = citations_client.build_ticket_documents(sec.get("ticket_keys") or [])
    async with sem:
        res = await asyncio.to_thread(
            citations_client.write_section_citations, sec, docs, module, directive)
    # segments_to_html is pure + unit-tested; entries are globally unique via `sid`.
    html, entries = citations_client.segments_to_html(res["segments"], sid)
    registry.update(entries)  # safe under asyncio: runs on the event-loop thread after the await
    if not html.lower().startswith("<h2"):
        html = f"<h2>{title}</h2>\n{html}"
    return {"title": title, "html": html, "stop_reason": "citations",
            "secs": round(_time.monotonic() - t0, 1), "errored": False,
            "attempts": 1, "usage": res.get("usage")}


async def write_section(sec: dict, registry: dict, by_ticket: dict, module: str,
                        sem: asyncio.Semaphore, budget: str = "120–350 words",
                        max_attempts: int = 3, directive: str = "",
                        section_tmpl: str = SECTION_SYSTEM_PROMPT) -> dict:
    # Version B: only Jira-grounded sections (with ticket_keys) go through the Citations API.
    # Transcript-only sections (span_ids) and structural sections (no keys) fall through to the
    # existing SDK writer — identical to Version A for those sections.
    if citations_enabled() and sec.get("ticket_keys"):
        return await _write_section_via_citations(sec, registry, module, sem, directive=directive)
    title = sec.get("title", "Section")
    # In transcript-only mode the plan carries span_ids instead of ticket_keys;
    # both resolve through the same by_ticket/registry menu lookup.
    cite_keys = sec.get("ticket_keys") or sec.get("span_ids", [])
    menu = _citation_menu(by_ticket, registry, cite_keys)
    # Optional authoring directive (audience/tone/emphasis) — FRAMING ONLY, never facts.
    directive_line = (
        f"\nAUTHORING DIRECTIVE (shape tone/audience/emphasis ONLY — never invent facts "
        f"or audience-specific claims; every statement still comes from the citations above): "
        f"{directive.strip()}\n" if directive and directive.strip() else ""
    )
    prompt = (
        f"Section: {title}\nScope: {sec.get('scope', '')}\n{directive_line}\n"
        f"AVAILABLE CITATIONS (use ONLY these ids; emit [CITE:id], never the quote text):\n{menu}\n\n"
        f"Write the <h2>{title}</h2> section now."
    )
    total_secs = 0.0
    last_frag = ""
    last_error = ""
    async with sem:
        for attempt in range(1, max_attempts + 1):
            r = await _run(prompt, build_section_options(module, title, budget, system_tmpl=section_tmpl))
            total_secs += r["secs"]
            if r.get("error"):
                last_error = r["error"]
            frag = r["text"].strip()
            frag = re.sub(r"^```html\s*", "", frag, flags=re.I)
            frag = re.sub(r"```$", "", frag).strip()
            last_frag = frag
            if _section_ok(frag):
                return {"title": title, "html": frag, "stop_reason": r["stop_reason"],
                        "secs": total_secs, "errored": False, "attempts": attempt,
                        "usage": r.get("usage")}
    # Exhausted retries — flag it so pass-criteria fails loudly instead of silently shipping a gap.
    reason = f" — {last_error}" if last_error else ""
    return {"title": title, "html": f"<h2>{title}</h2>\n<p>[ERROR: section failed after {max_attempts} attempts{reason}]</p>",
            "stop_reason": "error", "secs": total_secs, "errored": True, "attempts": max_attempts,
            "usage": None, "error_reason": last_error}


# ============================================================================
# Stage 3 — Deterministic assembly: render [CITE:id] -> exact span + tier.
# ============================================================================
_CITE_RE = re.compile(r"\[CITE:\s*([^\]]+?)\s*\]")


def assemble(title: str, sections: list[dict], registry: dict) -> tuple[str, dict]:
    """Replace every [CITE:id] with a rendered citation from the registry.
    Returns (html, report). Wrong tier / not_found are impossible here by design;
    invalid_cite_id is the only failure the model can cause."""
    report = {"rendered": 0, "invalid_cite_id": 0, "transcript": 0, "invalid_examples": [], "issues": set()}

    def _render(m: re.Match) -> str:
        cid = m.group(1).strip()
        if cid.lower().startswith("transcript"):
            report["transcript"] += 1
            return f"<!-- Source: {cid} -->"
        e = registry.get(cid)
        if not e:
            report["invalid_cite_id"] += 1
            if len(report["invalid_examples"]) < 6:
                report["invalid_examples"].append(cid)
            return f"<!-- Source: INVALID_CITE_ID:{cid} -->"
        report["rendered"] += 1
        report["issues"].add(e["issue"])
        span = e["span"].replace("\n", " ").strip()
        return f'<!-- Source: [[{e["issue"]}:{e["tier"]}]] "{span}" -->'

    body = "\n\n".join(s["html"] for s in sections)
    body = _CITE_RE.sub(_render, body)

    # Deterministic Sources section — guarantees the required heading and an
    # accurate ticket list (every issue actually cited, no LLM call to fail).
    sources_html = ""
    if report["issues"]:
        items = []
        for k in sorted(report["issues"]):
            if k == "TRANSCRIPT":  # transcript-only mode — one verbatim source
                items.append("  <li><code>TRANSCRIPT</code> — uploaded training session "
                             "(every claim quoted verbatim from the recording)</li>")
                continue
            rec = demo._FIX["tickets"].get(k) or demo._FIX["epics"].get(k) or {}
            items.append(f"  <li><code>{k}</code> — {rec.get('summary', '')}</li>")
        sources_html = "\n\n<h2>Sources</h2>\n<ul>\n" + "\n".join(items) + "\n</ul>"

    html = f"<h1>{title}: Learning Guide</h1>\n\n{body}{sources_html}"
    return html, report


# ============================================================================
# Orchestration
# ============================================================================
async def run_cell_d(module: str, transcript: str, label: str, do_eval: bool,
                     fmt: str = "long-form") -> None:
    demo._FIX = _load_fixture(module)
    print(f"[{label}] fixture: {len(demo._FIX['tickets'])} tickets + {len(demo._FIX['epics'])} epics "
          f"(module '{demo._FIX['module']}') | format: {fmt}")

    DRAFTS.mkdir(parents=True, exist_ok=True)
    transcript_id = _register_transcript(transcript, module)
    transcript_filename = Path(transcript).name
    budget = _FORMAT_BUDGET.get(fmt, _FORMAT_BUDGET["long-form"])

    t0 = time.monotonic()

    # ── Stage 1: Plan (format-specific section list) ──
    print(f"Stage 1: planning {fmt} (research with tools, emit section plan)…")
    plan_opts = ClaudeAgentOptions(
        model="claude-sonnet-4-6", effort="medium",
        system_prompt=plan_system_prompt(module, fmt),
        mcp_servers={MCP_SERVER_NAME: demo_mcp_server},
        allowed_tools=DEMO_ALLOWED_TOOLS, disallowed_tools=_DISALLOWED,
        tools=[], max_turns=20,
    )
    plan_prompt = (
        f"Plan a {fmt} `{module}` guide from the transcript at:\n  {transcript}\n"
        f"Call parse_transcript first (module=\"{module}\"). Emit ONLY the JSON section plan."
    )
    pr = await _run(plan_prompt, plan_opts)
    plan = _parse_json(pr["text"])
    if not plan or not plan.get("sections"):
        print(f"  PLAN FAILED to parse. Raw head:\n{pr['text'][:800]}")
        return
    sections_plan = plan["sections"]
    plan_secs = pr["secs"]
    all_keys = [k for s in sections_plan for k in s.get("ticket_keys", [])]
    registry, by_ticket = build_registry(all_keys)
    print(f"  plan: {len(sections_plan)} sections, {len(set(all_keys))} tickets, "
          f"{len(registry)} citable spans  ({plan_secs:.0f}s)")

    # ── Stage 2: Section writers (parallel, CITE-IDs only) ──
    print("Stage 2: writing sections in parallel (CITE-IDs only, no quote text)…")
    sem = asyncio.Semaphore(SECTION_CONCURRENCY)
    sections = await asyncio.gather(*(
        write_section(s, registry, by_ticket, module, sem, budget=budget) for s in sections_plan
    ))
    sec_total = time.monotonic() - t0 - plan_secs

    # ── Stage 3: Assemble + render ──
    html, asm = assemble(module, sections, registry)
    total = time.monotonic() - t0

    # Persist as a draft so it shows in the Library too.
    slug = _slug(module)
    rid = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{slug}-{fmt}-{uuid.uuid4().hex[:6]}"
    (DRAFTS / f"{rid}.html").write_text(html, encoding="utf-8")
    (DRAFTS / f"{rid}.json").write_text(json.dumps({
        "id": rid, "status": "draft", "module": module, "template": fmt,
        "transcript_id": transcript_id, "transcript_filename": transcript_filename,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "demo": True, "run_label": label, "method": "sectioned+registry",
        "gen_seconds": round(total, 1),
    }, indent=2), encoding="utf-8")
    (APP_DIR / f"demo-{slug}-{fmt}-D.html").write_text(html, encoding="utf-8")

    # ── Telemetry + pass criteria ──
    print(f"\n=== CELL D TELEMETRY [{label}] ===")
    print(f"plan {plan_secs:.0f}s | sections {sec_total:.0f}s | total {total:.0f}s | "
          f"{len(sections)} sections | {_words(html)} words | {len(html)} chars")
    print(f"{'#':>2} {'secs':>6} {'att':>3} {'stop_reason':<14} title")
    truncated = errored = 0
    for i, s in enumerate(sections, 1):
        sr = s.get("stop_reason") or "?"
        if sr == "max_tokens":
            truncated += 1
        if s.get("errored"):
            errored += 1
        print(f"{i:>2} {s['secs']:6.1f} {s.get('attempts', 1):>3} {sr:<14} {s['title'][:50]}")

    integ = run_gate(html)["substring"]
    print(f"\nassembly: rendered={asm['rendered']} invalid_cite_id={asm['invalid_cite_id']} transcript={asm['transcript']}")
    if asm["invalid_examples"]:
        print(f"  invalid ids: {asm['invalid_examples']}")
    print(f"validator on assembled: tier_lie={integ['tier_lie']} not_found={integ['quote_not_found']} ok={integ['ok']} tokened={integ['tokened']}")

    print(f"\n=== PASS CRITERIA [{label}] ===")
    min_sections = {"tldr": 5, "micro-guide": 6, "release-notes": 2, "long-form": 8}.get(fmt, 8)
    checks = {
        f"all sections present (>={min_sections})": len(sections) >= min_sections,
        "no section errored (after retries)": errored == 0,
        "no section truncated (max_tokens)": truncated == 0,
        "tier_lie == 0": integ["tier_lie"] == 0,
        "not_found == 0": integ["quote_not_found"] == 0,
        "invalid_cite_id == 0": asm["invalid_cite_id"] == 0,
    }
    for name, ok in checks.items():
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")

    # ── Stage 4: LLM eval as semantic backstop ──
    if do_eval:
        tp = Path(transcript)
        if not tp.is_absolute():
            tp = (APP_DIR / tp).resolve()
        ttext = tp.read_text(encoding="utf-8") if tp.exists() else ""
        print(f"\n=== EVAL (semantic backstop) [{label}] ===")
        ev = await evaluate_draft(html, ttext, fmt, module)
        cks = "; ".join(f"{c.get('name')}={c.get('status')}" for c in (ev.get("checks") or []))
        print(f"long-form: VERDICT={str(ev.get('verdict')).upper()} (wc={ev.get('word_count')})")
        print(f"  {ev.get('summary')}")
        if cks:
            print(f"  checks: {cks}")

    print(f"\nView in the UI:  uvicorn app:app --host 127.0.0.1 --port 8000  → Library tab.")


async def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--module", default=DEFAULT_MODULE)
    ap.add_argument("--transcript", default=DEFAULT_TRANSCRIPT)
    ap.add_argument("--label", default="D:sectioned+registry")
    ap.add_argument("--format", default="long-form", choices=VALID_FORMATS)
    ap.add_argument("--no-eval", action="store_true")
    args = ap.parse_args()
    await run_cell_d(args.module, args.transcript, args.label, not args.no_eval, fmt=args.format)


if __name__ == "__main__":
    asyncio.run(main())
