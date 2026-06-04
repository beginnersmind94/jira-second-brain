"""Tools for the Generator agent (Tasks 1–3).

Task 1: Map      — parse_transcript, match_tickets
Task 2: Plan     — no tools, reasoning only
Task 3: Verify   — search_kb, read_ticket
Task 4: Generate — no tools (model emits HTML directly)
"""
import base64
import csv
import json
import os
from pathlib import Path

import httpx
import pymupdf
from claude_agent_sdk import tool
from dotenv import load_dotenv

load_dotenv()

# -- Paths --
APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"
TRANSCRIPTS_DIR = APP_DIR / "raw" / "transcripts"
JIRA_BRAIN = Path(os.getenv("JIRA_BRAIN_PATH",
    r"C:\Users\rahul.mehta\Downloads\Financials-Documentation-KT\jira-brain"))
KB_GUIDES = JIRA_BRAIN / "raw" / "guides" / "markdown"
KB_CONCEPTS = JIRA_BRAIN / "wiki" / "concepts"
KB_WORKFLOWS = JIRA_BRAIN / "wiki" / "workflows"

# -- Jira REST --
JIRA_BASE = os.getenv("JIRA_BASE_URL", "").rstrip("/")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_TOKEN = os.getenv("JIRA_API_TOKEN", "")

# -- NXT custom field IDs (confirmed via /rest/api/3/field) --
AC_FIELD_ID = "customfield_10131"           # Acceptance Criteria (ADF)
RN_FIELD_ID = "customfield_10148"           # Release Notes (ADF)
RN_TITLE_FIELD_ID = "customfield_10285"     # Release Notes Title (plain)
RN_INTERNAL_FIELD_ID = "customfield_10219"  # Release Notes (Internal) (ADF)
RN_REQUIRED_FIELD_ID = "customfield_10218"  # Release Notes Required (option)
MODULE_FIELD_ID = "customfield_10147"       # Module (option)

EXTRA_FIELDS = [
    "summary", "status", "issuetype", "components", "description", "priority",
    "parent",
    AC_FIELD_ID, RN_FIELD_ID, RN_TITLE_FIELD_ID, RN_INTERNAL_FIELD_ID,
    RN_REQUIRED_FIELD_ID, MODULE_FIELD_ID,
]


def _parent_summary(parent_field) -> tuple[str, str]:
    """Return (key, summary) for a parent (typically the epic) or ('-', '')."""
    if not parent_field or not isinstance(parent_field, dict):
        return "-", ""
    pkey = parent_field.get("key", "-")
    psum = (parent_field.get("fields") or {}).get("summary", "")
    return pkey, psum


def _ok(text: str) -> dict:
    return {"content": [{"type": "text", "text": text}]}


def _basic_auth() -> str | None:
    if not (JIRA_BASE and JIRA_EMAIL and JIRA_TOKEN):
        return None
    raw = f"{JIRA_EMAIL}:{JIRA_TOKEN}".encode()
    return "Basic " + base64.b64encode(raw).decode()


def _adf_to_text(node) -> str:
    """Flatten Atlassian Document Format JSON to plain text."""
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return "".join(_adf_to_text(n) for n in node)
    if isinstance(node, dict):
        t = node.get("type")
        if t == "text":
            return node.get("text", "")
        if t in ("hardBreak", "rule"):
            return "\n"
        parts = _adf_to_text(node.get("content"))
        if t in ("paragraph", "heading", "listItem", "bulletList", "orderedList"):
            parts += "\n"
        return parts
    return ""


# ============================================================================
# Task 1: parse_transcript
# ============================================================================

@tool(
    "parse_transcript",
    "Read the full text of an uploaded training transcript. Use this FIRST in "
    "Task 1 (Map) so you can see what the presenter actually said before "
    "matching features to Jira. The transcript is the immutable source of "
    "voice and narrative; Jira is the source of behavioral truth.",
    {"transcript_path": str},
)
async def parse_transcript(args):
    p = Path(args["transcript_path"])
    if not p.is_absolute():
        # Try transcripts dir first, then cwd
        for base in (TRANSCRIPTS_DIR, APP_DIR):
            candidate = (base / p).resolve()
            if candidate.exists():
                p = candidate
                break
    if not p.exists():
        return _ok(f"ERROR: transcript not found at {p}")
    if p.suffix.lower() not in (".md", ".txt"):
        return _ok(f"ERROR: only .md and .txt accepted in V1; got {p.suffix}")
    try:
        text = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = p.read_text(encoding="utf-8", errors="replace")
    return _ok(text)


# ============================================================================
# Task 1: match_tickets (live NXT Jira search via REST)
# ============================================================================

@tool(
    "match_tickets",
    "Search Cybersoft NXT Jira for tickets matching a SHORT phrase from the "
    "transcript. Pass a 2–4 word phrase (feature name, workflow step, UI "
    "label). **IMPORTANT: JQL `text ~` is phrase-literal — 5+ word queries "
    "almost always return zero matches because the exact phrase doesn't appear "
    "anywhere.** Keep queries tight: 'Income Survey wizard', 'household step', "
    "'Add New Student'. Optionally narrow by `module` (Eligibility, "
    "Accountability, Inventory, Item Management, Menu Planning, Production, "
    "Insights, Account Management, Reports, System). Returns up to 5 candidates "
    "with key, summary, status, components, priority, Module, and a description "
    "snippet. Each result includes its parent epic — call `read_epic` next for "
    "full feature surface area, then `read_ticket` on the most relevant child "
    "stories for AC + Release Notes (Task 3).",
    {"query": str, "module": str},
)
async def match_tickets(args):
    query = (args.get("query") or "").strip()
    module = (args.get("module") or "").strip()
    if len(query) < 3:
        return _ok("ERROR: query too short — pass a multi-word phrase.")

    auth = _basic_auth()
    if auth is None:
        return _ok("ERROR: Jira credentials not configured (.env).")

    safe = query.replace("\\", "\\\\").replace('"', '\\"')
    jql_parts = ['project = NXT', f'text ~ "{safe}"']
    if module:
        safe_mod = module.replace('"', '\\"')
        jql_parts.append(f'"Module" = "{safe_mod}"')
    jql = " AND ".join(jql_parts) + " ORDER BY priority DESC, updated DESC"

    url = f"{JIRA_BASE}/rest/api/3/search/jql"
    headers = {
        "Authorization": auth,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    payload = {
        "jql": jql,
        "fields": ["summary", "status", "components", "issuetype",
                   "priority", "description", "parent", MODULE_FIELD_ID,
                   RN_REQUIRED_FIELD_ID],
        "maxResults": 5,
    }

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(url, headers=headers, json=payload)
    except httpx.HTTPError as e:
        return _ok(f"ERROR: Jira call failed: {e}")

    if r.status_code != 200:
        return _ok(f"ERROR: Jira HTTP {r.status_code}: {r.text[:300]}")

    data = r.json()
    issues = data.get("issues", [])
    if not issues:
        return _ok(f'No tickets matched for: "{query}"\nJQL: {jql}')

    lines = [f"[JQL: {jql}]"]
    for issue in issues:
        key = issue.get("key", "?")
        f = issue.get("fields") or {}
        summary = f.get("summary", "")
        status = (f.get("status") or {}).get("name", "?")
        itype = (f.get("issuetype") or {}).get("name", "?")
        prio = (f.get("priority") or {}).get("name", "-")
        comps = ", ".join(c.get("name", "") for c in (f.get("components") or [])) or "-"
        mod_val = f.get(MODULE_FIELD_ID)
        mod = mod_val.get("value") if isinstance(mod_val, dict) else (mod_val or "-")
        rn_req_val = f.get(RN_REQUIRED_FIELD_ID)
        rn_req = rn_req_val.get("value") if isinstance(rn_req_val, dict) else (rn_req_val or "-")
        desc_text = _adf_to_text(f.get("description")).strip()
        snippet = desc_text[:160].replace("\n", " ") + ("…" if len(desc_text) > 160 else "")
        epic_key, epic_sum = _parent_summary(f.get("parent"))
        lines.append(
            f"{key} | [{status}] [{itype}] [P:{prio}] [Module:{mod}] [RN:{rn_req}]\n"
            f"  {summary}\n"
            f"  components: {comps}\n"
            f"  epic: {epic_key}" + (f" — {epic_sum}" if epic_sum else "") + "\n"
            f"  desc: {snippet or '(empty)'}"
        )

    return _ok("\n\n".join(lines))


# ============================================================================
# Task 3: search_kb (local jira-brain knowledge base)
# ============================================================================

def _kb_files() -> list[Path]:
    """All KB markdown files we search across."""
    files: list[Path] = []
    if KB_GUIDES.exists():
        # Only the SME-curated `.md`, not the bot-extracted `.raw.md`
        for p in KB_GUIDES.rglob("*.md"):
            if not p.name.endswith(".raw.md") and not p.name.endswith(".legacy"):
                files.append(p)
    for d in (KB_CONCEPTS, KB_WORKFLOWS):
        if d.exists():
            files.extend(d.glob("*.md"))
    return files


@tool(
    "search_kb",
    "Search the local jira-brain knowledge base for context that supports or "
    "contradicts what the transcript presenter said. Covers SME-curated guide "
    "markdown, wiki/concepts/, and wiki/workflows/. Returns up to 5 matches "
    "with file path and a snippet around the keyword hit. Use this in Task 3 "
    "alongside `read_ticket` to fact-check claims that Jira alone doesn't "
    "settle (e.g. menu paths, UI labels, customer-facing procedure steps — "
    "the guides are navigation-authoritative).",
    {"query": str},
)
async def search_kb(args):
    query = (args.get("query") or "").strip()
    if len(query) < 3:
        return _ok("ERROR: query too short — pass a multi-word phrase.")

    terms = [t.lower() for t in query.split() if len(t) > 2]
    if not terms:
        return _ok("ERROR: no usable terms in query.")

    scored: list[tuple[int, Path, str]] = []
    for path in _kb_files():
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        lower = text.lower()
        score = sum(lower.count(t) for t in terms)
        if score == 0:
            continue
        # Pull a snippet around the first hit
        idx = -1
        for t in terms:
            i = lower.find(t)
            if i >= 0:
                idx = i
                break
        start = max(0, idx - 100)
        end = min(len(text), idx + 300)
        snippet = text[start:end].replace("\n", " ")
        if start > 0:
            snippet = "…" + snippet
        if end < len(text):
            snippet = snippet + "…"
        scored.append((score, path, snippet))

    if not scored:
        return _ok(f'No KB matches for: "{query}"')

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:5]
    # Don't mention total match count — the model treats it as an exploration
    # signal and tries to read underlying files. Just show the top hits.
    lines = [f"[KB top {len(top)} hits for: {query}]"]
    for score, path, snippet in top:
        rel = path.relative_to(JIRA_BRAIN) if path.is_relative_to(JIRA_BRAIN) else path
        lines.append(f"\n--- {rel} (score {score}) ---\n{snippet[:400]}")
    return _ok("\n".join(lines))


# ============================================================================
# Task 3: read_ticket (live NXT ticket with all tier-1 fields)
# ============================================================================

@tool(
    "read_ticket",
    "Fetch one Jira ticket's full content by key (e.g. 'NXT-19086'). Returns "
    "Acceptance Criteria (TIER 1 — agreed workflow), Release Notes (TIER 1 — "
    "customer-facing voice), Release Notes Internal (TIER 2), and Description "
    "(TIER 3 — lowest trust, often pre-scope). Use this in Task 3 to verify "
    "whether a transcript claim is actually supported. Quote AC or RN "
    "verbatim in your `<!-- Source: -->` citation comments.",
    {"issue_key": str},
)
async def read_ticket(args):
    key = args["issue_key"].strip().upper()
    auth = _basic_auth()
    if auth is None:
        return _ok("ERROR: Jira credentials not configured.")

    url = f"{JIRA_BASE}/rest/api/3/issue/{key}"
    params = {"fields": ",".join(EXTRA_FIELDS)}
    headers = {"Authorization": auth, "Accept": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(url, headers=headers, params=params)
    except httpx.HTTPError as e:
        return _ok(f"ERROR: Jira call failed: {e}")

    if r.status_code == 404:
        return _ok(f"ERROR: issue {key} not found.")
    if r.status_code != 200:
        return _ok(f"ERROR: HTTP {r.status_code}: {r.text[:300]}")

    data = r.json()
    f = data.get("fields") or {}

    summary = f.get("summary", "")
    status = (f.get("status") or {}).get("name", "?")
    itype = (f.get("issuetype") or {}).get("name", "?")
    prio = (f.get("priority") or {}).get("name", "-")
    comps = ", ".join(c.get("name", "") for c in (f.get("components") or [])) or "-"
    mod_val = f.get(MODULE_FIELD_ID)
    module = mod_val.get("value") if isinstance(mod_val, dict) else (mod_val or "-")
    rn_req_val = f.get(RN_REQUIRED_FIELD_ID)
    rn_required = rn_req_val.get("value") if isinstance(rn_req_val, dict) else "-"
    rn_title = f.get(RN_TITLE_FIELD_ID) or ""

    desc = _adf_to_text(f.get("description")).strip()
    ac_text = _adf_to_text(f.get(AC_FIELD_ID)).strip()
    rn_text = _adf_to_text(f.get(RN_FIELD_ID)).strip()
    rn_internal = _adf_to_text(f.get(RN_INTERNAL_FIELD_ID)).strip()

    epic_key, epic_sum = _parent_summary(f.get("parent"))

    parts = [
        f"{key} | [{status}] [{itype}] [P:{prio}] {summary}",
        f"Module: {module}  |  components: {comps}  |  RN Required: {rn_required}",
        f"Epic: {epic_key}" + (f" — {epic_sum}" if epic_sum else "") + "  (call read_epic for full epic context + sibling tickets)",
    ]
    if rn_title:
        parts.append(f"Release Notes Title: {rn_title}")
    parts.append(f"\n## Acceptance Criteria  [TIER 1 — agreed workflow]\n{ac_text[:4000] if ac_text else '(empty — flag in metadata)'}")
    parts.append(f"\n## Release Notes  [TIER 1 — customer-facing voice]\n{rn_text[:3000] if rn_text else '(empty)'}")
    if rn_internal:
        parts.append(f"\n## Release Notes (Internal)  [TIER 2]\n{rn_internal[:2000]}")
    parts.append(f"\n## Description  [TIER 3 — lowest trust]\n{desc[:3000] if desc else '(empty)'}")

    return _ok("\n".join(parts))


# ============================================================================
# Optional: read_pdf (V1.5 fallback — PDF transcript substitute per Dallas)
# ============================================================================

@tool(
    "read_pdf",
    "Fallback when the upload is a PDF instead of a transcript. Extracts all "
    "text via pymupdf. Treat the result as if it were a transcript: the PDF "
    "is the primary voice, Jira AC is the source of truth.",
    {"file_path": str},
)
async def read_pdf(args):
    p = Path(args["file_path"])
    if not p.is_absolute():
        p = (DATA_DIR / p).resolve()
    if not p.exists():
        return _ok(f"ERROR: file not found at {p}")
    try:
        doc = pymupdf.open(p)
    except Exception as e:
        return _ok(f"ERROR: could not open PDF: {e}")
    pages = []
    for i, page in enumerate(doc, start=1):
        pages.append(f"--- page {i} ---\n{page.get_text()}")
    doc.close()
    return _ok("\n\n".join(pages))


# ============================================================================
# Task 1: read_epic (epic context — siblings of a matched ticket)
# ============================================================================

@tool(
    "read_epic",
    "Given an epic key (e.g. 'NXT-12345'), return the epic's summary + "
    "Acceptance Criteria + ALL child stories under it (key, status, summary). "
    "Use this in Task 1 AFTER `match_tickets` returns hits — every hit "
    "includes its parent epic. Call read_epic on each unique epic to get the "
    "full feature surface area in ONE call, instead of guessing many search "
    "phrases. Epics are the right grain for 'related context' because Cybersoft "
    "groups all stories for a feature (e.g. all 7 wizard steps of Income "
    "Surveys) under one epic.",
    {"epic_key": str},
)
async def read_epic(args):
    key = args["epic_key"].strip().upper()
    auth = _basic_auth()
    if auth is None:
        return _ok("ERROR: Jira credentials not configured.")

    headers = {"Authorization": auth, "Accept": "application/json", "Content-Type": "application/json"}

    # 1. Fetch the epic itself
    epic_url = f"{JIRA_BASE}/rest/api/3/issue/{key}"
    epic_params = {"fields": f"summary,status,issuetype,components,description,priority,{AC_FIELD_ID},{RN_FIELD_ID},{MODULE_FIELD_ID}"}
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            er = await client.get(epic_url, headers=headers, params=epic_params)
    except httpx.HTTPError as e:
        return _ok(f"ERROR: Jira call failed (epic fetch): {e}")
    if er.status_code == 404:
        return _ok(f"ERROR: epic {key} not found.")
    if er.status_code != 200:
        return _ok(f"ERROR: HTTP {er.status_code}: {er.text[:300]}")

    epic_data = er.json()
    ef = epic_data.get("fields") or {}
    if (ef.get("issuetype") or {}).get("name", "") != "Epic":
        return _ok(
            f"WARNING: {key} is not an Epic (it's "
            f"{(ef.get('issuetype') or {}).get('name', '?')}). Returning what we got, but "
            f"the children list may be empty — only Epics group stories."
        )

    e_summary = ef.get("summary", "")
    e_status = (ef.get("status") or {}).get("name", "?")
    mod_val = ef.get(MODULE_FIELD_ID)
    e_module = mod_val.get("value") if isinstance(mod_val, dict) else (mod_val or "-")
    e_desc = _adf_to_text(ef.get("description")).strip()
    e_ac = _adf_to_text(ef.get(AC_FIELD_ID)).strip()
    e_rn = _adf_to_text(ef.get(RN_FIELD_ID)).strip()

    # 2. Fetch children (modern Jira: parent = <epic>; covers Epic Link too)
    search_url = f"{JIRA_BASE}/rest/api/3/search/jql"
    search_payload = {
        "jql": f'parent = "{key}" ORDER BY priority DESC, key ASC',
        "fields": ["summary", "status", "issuetype", "priority", RN_REQUIRED_FIELD_ID],
        "maxResults": 50,
    }
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            sr = await client.post(search_url, headers=headers, json=search_payload)
    except httpx.HTTPError as e:
        return _ok(f"ERROR: Jira call failed (children fetch): {e}")

    children_lines: list[str] = []
    if sr.status_code == 200:
        children = (sr.json() or {}).get("issues", []) or []
        for c in children:
            ck = c.get("key", "?")
            cf = c.get("fields") or {}
            csum = cf.get("summary", "")
            cstatus = (cf.get("status") or {}).get("name", "?")
            ctype = (cf.get("issuetype") or {}).get("name", "?")
            cprio = (cf.get("priority") or {}).get("name", "-")
            rn_req_val = cf.get(RN_REQUIRED_FIELD_ID)
            crn = rn_req_val.get("value") if isinstance(rn_req_val, dict) else "-"
            children_lines.append(
                f"  {ck} | [{cstatus}] [{ctype}] [P:{cprio}] [RN:{crn}] {csum}"
            )
    else:
        children_lines.append(f"  (children fetch failed: HTTP {sr.status_code})")

    parts = [
        f"EPIC {key} | [{e_status}] {e_summary}",
        f"Module: {e_module}",
    ]
    if e_ac:
        parts.append(f"\n## Epic Acceptance Criteria\n{e_ac[:2500]}")
    if e_rn:
        parts.append(f"\n## Epic Release Notes\n{e_rn[:1500]}")
    if e_desc:
        parts.append(f"\n## Epic Description\n{e_desc[:2000]}")
    parts.append(f"\n## Child stories ({len(children_lines)})")
    if children_lines:
        parts.extend(children_lines)
    else:
        parts.append("  (no children — this epic may be empty or new)")

    return _ok("\n".join(parts))


# Tools registered with the generator agent.
SDK_TOOLS = [parse_transcript, match_tickets, search_kb, read_ticket, read_epic, read_pdf]
