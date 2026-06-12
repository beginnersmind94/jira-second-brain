"""DEMO server — the SAME UI as app.py, but generation + evaluation run OFFLINE
against the pre-captured Jira fixture (data/demo/<module-slug>-fixture.json).

The point: in the browser you upload a transcript, pick module + template, and
watch it "process" live (tool calls stream, draft appears in the Library) — but
there is ZERO Jira network at showtime, so it's fast and can't fail mid-show.
The LLM genuinely generates each draft; only the Jira reads are pre-cached.

This is a STANDALONE copy. It does NOT touch the production path
(app.py / agent_sdk.py / tools_sdk.py / evaluator_sdk.py / smoke_test.py are
untouched). It REUSES app.py's unchanged route handlers by re-registering them
(importing app.py is network-free) and overrides only the three routes that must
run offline: /generate, /resources/{rid}/evaluate, and /api/config.

Run order:
    1) ONCE, ahead of time, with live Jira reachable:
           python demo_capture.py --module "Item Management"
    2) Demo server (no Jira needed):
           uvicorn demo_app:app --host 127.0.0.1 --port 8001
       Open http://127.0.0.1:8001  →  Author tab  →  upload the transcript,
       pick "Item Management" + a template  →  Run.

Note the port is 8001 so it can run alongside the real app.py (port 8000).
Override the captured module with env DEMO_MODULE if your fixture is a different one.
"""
import asyncio
import json
import os
import re
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
from fastapi import Body, Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from sse_starlette.sse import EventSourceResponse

from auth import CurrentUser, get_current_user
from tenancy import assert_district_access, filter_to_accessible_districts, get_user_districts

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ThinkingBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
    create_sdk_mcp_server,
    query,
)

# Reuse prod helpers + unchanged route handlers (import is network-free).
import app as prod
# Offline tools + offline generator options.
import demo
from demo import build_demo_options, build_derive_options, build_derive_prompt, validate_citations
from agent_sdk import VALID_TEMPLATES, build_user_prompt
from evaluator_sdk import EVALUATOR_PROMPT, build_evaluator_prompt
# Cell D — sectioned + quote-registry long-form (the validated architecture).
import demo_d
from demo_d import (
    _DISALLOWED,
    _FORMAT_BUDGET,
    _parse_json,
    assemble,
    build_registry,
    build_transcript_registry,
    plan_system_prompt,
    transcript_plan_system_prompt,
    transcript_span_menu,
    write_section,
    SECTION_SYSTEM_PROMPT_TRANSCRIPT,
)
from demo import ALLOWED_TOOLS as DEMO_ALLOWED_TOOLS, MCP_SERVER_NAME, demo_mcp_server
import pricing
# AI-assisted review step — edit agent + edit-triage agent (network-free import).
import revise
# Intent-and-scope front end — "describe what you need" (network-free import).
import intent_agent
# Quiz Builder — persistence + QA/grounding gate (+ the support judge for the QA pass).
import quiz_store
import qbank_gate
# Quality rubric scorers — Coverage, Clarity, Structure (advisory heuristics, no LLM call).
from scorers import compute_scores

load_dotenv()

# ── Discover ALL available module fixtures; load one to start ─────────────────
# The offline tools read demo._FIX (a single module's fixture). For multi-module
# we discover every data/demo/*-fixture.json and swap demo._FIX per request to the
# module being generated — so each run grounds against the RIGHT module's Jira.
_DEMO_DIR = Path(demo.__file__).parent / "data" / "demo"


def _discover_modules() -> dict[str, str]:
    """Map module-name -> fixture path for every fixture on disk."""
    out: dict[str, str] = {}
    for fp in sorted(_DEMO_DIR.glob("*-fixture.json")):
        try:
            mod = json.loads(fp.read_text(encoding="utf-8")).get("module")
            if mod:
                out[mod] = str(fp)
        except (json.JSONDecodeError, OSError):
            continue
    return out


AVAILABLE_MODULES = _discover_modules()
# Modules offered for transcript-only mode that have NO Jira fixture (label-only;
# grounding comes from the transcript itself). Override/extend via env (comma-sep).
TRANSCRIPT_EXTRA_MODULES = [m.strip() for m in os.getenv(
    "DEMO_TRANSCRIPT_MODULES", "Financials").split(",") if m.strip()]
# Master on/off for the whole external-learning layer (ICN content, roster, study sets).
# One switch so it can be disabled until the ICN fair-use agreement is in place.
EXTERNAL_LEARNING = os.getenv("EXTERNAL_LEARNING", "1").lower() not in ("0", "false", "off", "no")
DEFAULT_MODULE = os.getenv("DEMO_MODULE", "Item Management")
if DEFAULT_MODULE not in AVAILABLE_MODULES and AVAILABLE_MODULES:
    DEFAULT_MODULE = sorted(AVAILABLE_MODULES)[0]
demo._FIX = demo._load_fixture(DEFAULT_MODULE)
_FIX_MODULE = DEFAULT_MODULE
print(f"[demo_app] {len(AVAILABLE_MODULES)} module fixtures available: {sorted(AVAILABLE_MODULES)}")
print(f"[demo_app] default '{_FIX_MODULE}': {len(demo._FIX.get('tickets', {}))} tickets + "
      f"{len(demo._FIX.get('epics', {}))} epics")


# The reused prod /transcripts handler validates the upload's module against
# prod.VALID_MODULES. Extend it so transcript-only modules (e.g. Financials, which
# has no Jira fixture) are accepted on upload — the module is just a label there.
prod.VALID_MODULES = tuple(dict.fromkeys(
    list(prod.VALID_MODULES) + sorted(AVAILABLE_MODULES) + TRANSCRIPT_EXTRA_MODULES))


def _ensure_fixture(module: str) -> None:
    """Swap demo._FIX to the requested module's fixture (the tools read this global)."""
    if module in AVAILABLE_MODULES and demo._FIX.get("module") != module:
        demo._FIX = demo._load_fixture(module)


async def _run_text(prompt: str, options) -> tuple[str, object]:
    """Run a tool-less query() to completion; return (final_text, usage).

    Used by the review/revise step for the edit + triage agents, which only
    reason over text and emit a single JSON object.
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


def _transcript_text_for(meta: dict) -> str:
    """Load the uploaded transcript text for a draft, by its transcript_id. Needed
    to verify transcript-only citations verbatim. Empty string if there is none."""
    tid = meta.get("transcript_id")
    if not tid:
        return ""
    t_meta = prod._read_meta(prod.TRANSCRIPT_META / f"{tid}.json")
    if not t_meta:
        return ""
    tp = (prod.BASE / t_meta["path"]).resolve()
    return tp.read_text(encoding="utf-8") if tp.exists() else ""


def _deterministic_eval(rid: str, draft_html: str, transcript_text: str = "") -> dict:
    """The grounding gate, as data: re-check every citation token against the
    fixture (Jira tokens) or the transcript (transcript-only tokens) by exact match.
    No LLM — the deterministic check IS the guarantee. Caller is responsible for
    _ensure_fixture() on the right module first, and for passing transcript_text
    when the draft was generated in transcript-only mode (else those tokens fail
    closed). Persists drafts/<rid>.eval.json and returns the verdict dict."""
    integ = validate_citations(draft_html, transcript_text=transcript_text)
    tier_lie, not_found, ok = integ["tier_lie"], integ["quote_not_found"], integ["ok"]
    invalid = draft_html.count("INVALID_CITE_ID")
    hard = tier_lie + not_found + invalid
    eval_data = {
        "verdict": "pass" if hard == 0 else "fail",
        "summary": (f"Deterministic grounding check: {ok} citations verified verbatim against "
                    f"source; {tier_lie} tier violations, {not_found} non-verbatim, {invalid} invalid IDs."),
        "checks": [
            {"name": "Citation tiers (no Description-as-AC)", "status": "ok" if tier_lie == 0 else "fail",
             "detail": f"tier_lie={tier_lie}"},
            {"name": "Verbatim citations", "status": "ok" if not_found == 0 else "fail",
             "detail": f"non-verbatim={not_found}"},
            {"name": "Valid citation IDs", "status": "ok" if invalid == 0 else "fail",
             "detail": f"invalid_cite_id={invalid}"},
            {"name": "Citations verified against source", "status": "ok",
             "detail": f"{ok} exact-quote, correct-tier citations"},
        ],
        "method": "deterministic-registry-validation",
        "resource_id": rid,
        "evaluated_at": datetime.now().isoformat(timespec="seconds"),
        "integrity": {"verified": ok, "tier_lie": tier_lie,
                      "not_found": not_found, "invalid_cite_id": invalid},
        # The specific offending citations (for the Evals drill-down). Each:
        # (ticket, tier, reason, quote-snippet). Empty when grounding is clean.
        "violations": [{"ticket": v[0], "tier": v[1], "issue": v[2], "quote": v[3]}
                       for v in integ.get("violations", [])][:25],
    }
    prod._eval_path(rid).write_text(json.dumps(eval_data, indent=2), encoding="utf-8")
    return eval_data


def _log_review_decision(record: dict) -> None:
    """Append one review-loop decision to a durable, append-only audit trail
    (logs/review-decisions.jsonl). EVERY outcome is logged — edit applied,
    refused, no-change, approved, approve-blocked — so a human (or an eval) can
    later judge whether a refusal was appropriate or the editor over-reached
    (took on a whole-doc/translation task it should have declined). This is also
    the real-traffic corpus for the triage + scope evals (eval/EVAL-SPEC.md §7)."""
    rec = {"at": datetime.now().isoformat(timespec="seconds"), **record}
    try:
        with (prod.LOGS / "review-decisions.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError:
        pass


def _trunc_ops(ops, n=8, L=160):
    return [{"find": o.get("find", "")[:L], "replace": o.get("replace", "")[:L]} for o in ops[:n]]

# ── Offline evaluator: same prompt as prod, but read_ticket serves the fixture ─
EVAL_SERVER_NAME = "evaluator_tools"
demo_eval_server = create_sdk_mcp_server(
    name=EVAL_SERVER_NAME, version="1.0.0", tools=[demo.read_ticket]
)


def build_demo_evaluator_options() -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        model="claude-sonnet-4-6",
        system_prompt=EVALUATOR_PROMPT,
        mcp_servers={EVAL_SERVER_NAME: demo_eval_server},
        allowed_tools=[f"mcp__{EVAL_SERVER_NAME}__read_ticket"],
        disallowed_tools=[
            "Read", "Write", "Edit", "Bash", "PowerShell", "Glob", "Grep",
            "WebFetch", "WebSearch", "Task", "TaskCreate", "TaskGet",
            "TaskList", "TaskUpdate", "TaskOutput", "TaskStop",
            "NotebookEdit", "Skill", "AskUserQuestion",
        ],
        tools=[],
        max_turns=8,
    )


# ── App: reuse the prod UI + unchanged routes, override the three offline ones ─
app = FastAPI(title="Learning Studio (DEMO)")

# Projects flow (Trainer creates a project, imports sites + users via CSV).
# Self-contained module — in-memory store, mock cookie auth, /api/projects/* routes.
from projects import router as projects_router
app.include_router(projects_router)

# ── Module library + Track builder (/api/modules, /api/tracks/*) ─────────────
import modules_store as _ms
import quiz_store as _qs


@app.get("/api/modules")
async def api_list_modules(
    source: str = "",
    product: str = "",
    role: str = "",
    q: str = "",
    current_user: CurrentUser = Depends(get_current_user),
):
    """List approved modules. Learners see only modules for their district or untagged global modules.
    Trainers see all modules. icn_dir wired in so ICN_DOC modules are addable to a track."""
    result = _ms.list_modules(source=source, product=product, role=role, q=q, icn_dir=_ICN_DIR)
    if not current_user.is_trainer:
        uid = current_user.district_id or ""
        result["modules"] = [
            m for m in result.get("modules", [])
            if not m.get("district_id") or m.get("district_id") == uid
        ]
        result["total"] = len(result["modules"])
    return result


@app.get("/api/tracks")
async def api_list_tracks(
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
):
    """List tracks, scoped by the caller's identity. Trainers see all tracks; learners
    see only tracks matching their role or untagged (global) tracks."""
    all_tracks = _ms.list_tracks()
    force_all = request.query_params.get("all") in ("1", "true")
    if force_all or current_user.is_trainer:
        return {"tracks": all_tracks}
    role = current_user.role
    filtered = [t for t in all_tracks
                if not t.get("role_tags") or role in (t.get("role_tags") or [])]
    return {"tracks": filtered}


@app.post("/api/tracks")
async def api_create_track(body: dict):
    track = _ms.create_track(
        title=body.get("title", "Untitled Track"),
        description=body.get("description", ""),
        product=body.get("product", "SchoolCafé"),
        role_tags=body.get("role_tags"),
    )
    return track


@app.get("/api/tracks/{tid}")
async def api_get_track(tid: str):
    track = _ms.load_track(tid)
    if not track:
        raise HTTPException(404, "track not found")
    # icn_dir so ICN_DOC modules expand inside a track (learner sees the mixed track).
    return _ms.expand_track(track, icn_dir=_ICN_DIR)


@app.put("/api/tracks/{tid}/modules")
async def api_set_track_modules(tid: str, body: dict):
    track = _ms.load_track(tid)
    if not track:
        raise HTTPException(404, "track not found")
    track["module_ids"] = body.get("module_ids") or []
    _ms.save_track(track)
    return {"module_ids": track["module_ids"]}


@app.put("/api/tracks/{tid}")
async def api_update_track(tid: str, body: dict):
    track = _ms.load_track(tid)
    if not track:
        raise HTTPException(404, "track not found")
    for field in ("title", "description", "product", "role_tags"):
        if field in body:
            track[field] = body[field]
    _ms.save_track(track)
    return track


@app.post("/api/tracks/{tid}/publish")
async def api_publish_track(tid: str):
    track = _ms.load_track(tid)
    if not track:
        raise HTTPException(404, "track not found")
    if not track.get("module_ids"):
        raise HTTPException(409, {"error": "no_modules", "detail": "Add at least one module before publishing."})
    track["status"] = "published"
    _ms.save_track(track)
    return track


@app.post("/api/tracks/{tid}/quiz")
async def api_attach_quiz(tid: str, body: dict):
    track = _ms.load_track(tid)
    if not track:
        raise HTTPException(404, "track not found")
    qid = body.get("quiz_id", "")
    if not _qs.load_quiz(qid):
        raise HTTPException(404, "quiz not found")
    track["quiz_id"] = qid
    _ms.save_track(track)
    return {"quiz_id": qid}


@app.delete("/api/tracks/{tid}")
async def api_delete_track(tid: str):
    if not _ms.delete_track(tid):
        raise HTTPException(404, "track not found")
    return {"ok": True}


# Unchanged routes — reuse prod's handlers verbatim (they read/write the same
# drafts/, published/, logs/, transcripts/ dirs).
app.get("/", response_class=HTMLResponse)(prod.index)
app.post("/transcripts")(prod.upload_transcript)
app.get("/transcripts")(prod.list_transcripts)
app.get("/transcripts/{tid}")(prod.get_transcript)
app.get("/resources")(prod.list_resources)
app.get("/resources/{rid}")(prod.get_resource)
app.get("/resources/{rid}/evaluation")(prod.get_evaluation)
app.get("/logs/{rid}")(prod.get_log)
app.post("/resources/{rid}/publish")(prod.publish_resource)


# ── /resources/{rid}/pdf — download the clean guide HTML as a PDF ─────────────
# Renders the resource's CLEAN HTML (Source comments stripped) to PDF bytes via
# pymupdf's Story API. 404 if the resource doesn't exist; render failures return
# a 500 with a clear message rather than crashing the server.
@app.get("/resources/{rid}/pdf")
async def resource_pdf(rid: str):
    resolved = prod._resolve_resource(rid)
    if not resolved:
        raise HTTPException(404, "resource not found")
    html_path, meta_path, _status = resolved

    try:
        raw_html = html_path.read_text(encoding="utf-8")
    except OSError as e:
        raise HTTPException(500, f"could not read resource HTML: {e}")

    clean_html = prod._strip_source_comments(raw_html)

    # Stamp a "pending review" banner until a human has approved the guide.
    # Approval (the Library gate) is the human sign-off — approved downloads are clean.
    meta = prod._read_meta(meta_path) or {}
    banner = None
    if not (meta.get("approved") or meta.get("sme_approved")):
        banner = ("⚠ PENDING REVIEW — provisional draft, grounding auto-verified "
                  "but not yet approved by a human reviewer. Do not treat as final.")

    try:
        import pdf_export
        pdf_bytes = pdf_export.render_html_to_pdf(clean_html, banner=banner)
    except Exception as e:  # never crash the server on a render error
        raise HTTPException(500, f"PDF render failed: {e}")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{rid}.pdf"'},
    )


# ── DEMO roster simulation (mock multi-tenant) ───────────────────────────────
# A simulated district/learner roster so the demo can show a per-ISD admin view and
# switch between districts. This is SYNTHETIC, clearly-labeled demo data — no real
# students. Deterministic per district (seeded) so it doesn't churn on refresh.
_DISTRICTS = [
    {"id": "houston-isd", "name": "Houston ISD", "domain": "houstonisd"},
    {"id": "dallas-isd", "name": "Dallas ISD", "domain": "dallasisd"},
    {"id": "austin-isd", "name": "Austin ISD", "domain": "austinisd"},
    {"id": "cy-fair-isd", "name": "Cypress-Fairbanks ISD", "domain": "cfisd"},
]
_ROSTER_FIRST = ["Maria", "James", "Aisha", "Carlos", "Linda", "Wei", "Diego", "Sarah", "Robert",
                 "Priya", "Kenji", "Grace", "Marcus", "Elena", "Tyler", "Fatima", "Rosa", "Andre",
                 "Nia", "Hector", "Joy", "Sam", "Lucia", "Omar", "Beth", "Trang", "Carl", "Imani"]
_ROSTER_LAST = ["Garcia", "Johnson", "Patel", "Nguyen", "Smith", "Williams", "Brown", "Lee",
                "Martinez", "Davis", "Khan", "Lopez", "Wilson", "Thomas", "Reyes", "Okafor",
                "Cohen", "Tran", "Flores", "Bell", "Ramirez", "Young", "Diaz", "Foster"]
_ROSTER_ROLES = ["POS Cashier", "Cafeteria Manager", "Frontline Cafeteria Staff", "District Nutrition Director"]
_ROSTER_PATHS = ["POS Cashier Basics", "Cafeteria Manager: Food Safety Refresher",
                 "Frontline Staff: Food Safety Skills", "Menu Planning Foundations"]
_ROSTER_STATUS = ["Not started", "In progress", "Completed"]


def _roster_for(d: dict) -> list:
    import hashlib
    import random
    seed = int(hashlib.md5(d["id"].encode()).hexdigest(), 16) % (2 ** 32)
    rnd = random.Random(seed)
    out = []
    for _ in range(rnd.randint(18, 32)):
        fn, ln = rnd.choice(_ROSTER_FIRST), rnd.choice(_ROSTER_LAST)
        status = rnd.choices(_ROSTER_STATUS, weights=[3, 4, 3])[0]
        prog = 100 if status == "Completed" else (0 if status == "Not started" else rnd.randint(10, 90))
        out.append({
            "name": f"{fn} {ln}", "role": rnd.choice(_ROSTER_ROLES),
            "email": f"{fn[0].lower()}{ln.lower()}@{d['domain']}.org",
            "assigned": rnd.choice(_ROSTER_PATHS), "progress": prog, "status": status,
            "last_active": rnd.choice(["Today", "Yesterday", "3 days ago", "Last week", "2 weeks ago", "—"]),
        })
    out.sort(key=lambda x: x["name"])
    return out


def _district_stats(d: dict) -> dict:
    """Seeded per-district roll-up for the management dashboard (synthetic demo)."""
    import hashlib
    roster = _roster_for(d)
    n = len(roster)
    completed = sum(1 for x in roster if x["status"] == "Completed")
    in_progress = sum(1 for x in roster if x["status"] == "In progress")
    h = int(hashlib.md5((d["id"] + "stats").encode()).hexdigest(), 16)
    flagged = d["id"] == "dallas-isd"
    return {
        "learners": n, "completed": completed, "in_progress": in_progress,
        "not_started": n - completed - in_progress,
        "completion_rate": round(100 * completed / n) if n else 0,
        "avg_progress": round(sum(x["progress"] for x in roster) / n) if n else 0,
        "active_7d": round(n * (0.55 + (h % 35) / 100.0)),
        "help_request": flagged,
        "help_note": "3 cashiers stuck on Inventory Distribution" if flagged else "",
        "due": "Jun 30",
    }


@app.get("/api/roster")
async def api_roster(
    request: Request,
    isd: str = "",
    current_user: CurrentUser = Depends(get_current_user),
):
    """District roster + per-district roll-up. Tenant-scoped.

    Tenant isolation enforced at the API layer (BRD NFR): assert_district_access()
    raises 403 before any data is returned for a district the caller cannot access.
    Trainers see their book-of-business; learners/directors see only their district.
    """
    if isd:
        assert_district_access(current_user, isd)
    accessible_ids = set(get_user_districts(current_user))
    visible = [d for d in _DISTRICTS if d["id"] in accessible_ids] if accessible_ids else [_DISTRICTS[0]]
    if isd and any(d["id"] == isd for d in visible):
        selected_id = isd
    else:
        selected_id = visible[0]["id"]
    districts = [{**d, **_district_stats(d)} for d in visible]
    selected = next(d for d in visible if d["id"] == selected_id)
    return {
        "districts": districts,
        "selected": selected["id"],
        "selected_name": selected["name"],
        "roster": _roster_for(selected),
        "demo": True,
        "viewer": {"id": current_user.id, "name": current_user.name,
                    "role": current_user.role, "is_trainer": current_user.is_trainer},
    }

@app.get("/api/icn")
async def api_icn():
    """Catalog feed for the Content tab: license-aware cards + suggested paths +
    the role/topic facets to filter on. No asset bytes here — only metadata,
    attribution, and the right outbound link per license posture."""
    lms, by_id = _icn_load()
    cards_in = lms.get("content_cards", [])
    _cidx = _icn_chunk_index()
    quiz_ids = set(_cidx.keys())  # assets with ingestible text → quizzable
    qtopics = set()  # chunk-backed topics → can author quizzes/flashcards by topic
    for _cs in _cidx.values():
        for _c in _cs:
            for _t in (_c.get("topics") or []):
                qtopics.add(str(_t).replace("_", " ").title())
    cards = []
    roles, topics = set(), set()
    counts = {"download_allowed": 0, "link_only": 0, "embed_only": 0}
    for c in cards_in:
        a = by_id.get(c.get("asset_id"), {})
        lp = c.get("license_posture") or a.get("license_posture") or "link_only"
        counts[lp] = counts.get(lp, 0) + 1
        rts = c.get("role_tags") or []
        tts = c.get("topic_tags") or []
        roles.update(rts); topics.update(tts)
        has_thumb = bool((a.get("preview_images") or c.get("preview_images")))
        cards.append({
            "asset_id": c.get("asset_id"),
            "title": _clean_title(c.get("title"), a.get("source_page_title")),
            "subtitle": (c.get("subtitle") or "")[:160],
            "asset_type": c.get("asset_type"),
            "roles": rts, "topics": tts,
            "license_posture": lp,
            "action_label": c.get("primary_action_label") or "Open",
            "source_url": c.get("source_url") or a.get("source_url"),
            "embed_url": a.get("embed_url"),
            "attribution": a.get("attribution_text") or f"Source: {c.get('source_label') or 'Institute of Child Nutrition'}",
            "source_label": c.get("source_label") or a.get("source_org"),
            "has_thumb": has_thumb,
            "has_quiz": c.get("asset_id") in quiz_ids,
            "card_id": c.get("card_id"),
        })
    # Resolve learning paths to their full module assets (so the path detail view can
    # render each step with its type, source link, and quiz). Derive a role from the modules.
    by_cardid = {c["card_id"]: c for c in cards if c.get("card_id")}
    paths = []
    for p in lms.get("suggested_learning_paths", []):
        mods = [by_cardid[cid] for cid in p.get("module_card_ids", []) if cid in by_cardid]
        role_counts = {}
        for m in mods:
            for r in (m.get("roles") or []):
                role_counts[r] = role_counts.get(r, 0) + 1
        role = max(role_counts, key=role_counts.get) if role_counts else None
        paths.append({"id": p.get("path_id"), "title": p.get("title"),
                      "description": p.get("description"), "role": role, "modules": mods})
    return {
        "cards": cards,
        "paths": paths,
        "roles": sorted(roles),
        "topics": sorted(topics),
        "quiz_topics": sorted(qtopics),
        "counts": counts,
        "total": len(cards),
    }


def _icn_chunk_index() -> dict:
    """asset_id -> [chunk dicts] from the imported citation-preserving chunks.jsonl.
    Only the publisher-permitted, ingestion-allowed assets are present here."""
    idx: dict[str, list] = {}
    p = _ICN_DIR / "chunks" / "chunks.jsonl"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                c = json.loads(line)
            except json.JSONDecodeError:
                continue
            idx.setdefault(c.get("asset_id"), []).append(c)
    return idx


def _icn_chunks_by_topic(topic: str) -> list:
    """All ingestible chunks tagged with `topic`, across assets (case/format tolerant —
    'Food Safety' matches the 'food_safety' chunk tag). For author-by-topic study sets."""
    tnorm = topic.strip().lower().replace(" ", "_")
    out = []
    for cs in _icn_chunk_index().values():
        for c in cs:
            tops = c.get("topics") or []
            if isinstance(tops, str):
                tops = [tops]
            if any(tnorm in str(t).lower().replace(" ", "_") for t in tops):
                out.append(c)
    return out


_QUIZ_SYS = """You write a short multiple-choice quiz that checks understanding of a training document for school-nutrition staff. You have NO tools.

RULES:
- Base EVERY question ONLY on the provided source excerpts. Never use outside knowledge or invent facts.
- Each question has a clear stem, EXACTLY 4 options, and exactly one correct option.
- For each question you MUST include "source_quote": a SHORT verbatim span (about 5-25 words) copied EXACTLY, character-for-character, from ONE excerpt — the span that proves the correct answer — and "chunk_id": the id of the excerpt it came from.
- Plain, professional, non-tricky language. Spread questions across different excerpts.

OUTPUT — your FINAL message is ONLY this JSON object, no prose, no code fence:
{"questions":[{"q":"...","options":["...","...","...","..."],"answer":0,"explanation":"why, in one sentence","source_quote":"exact words from an excerpt","chunk_id":"..."}]}"""


@app.post("/api/icn/quiz")
async def icn_quiz(payload: dict = Body(...)):
    """Generate a grounded multiple-choice quiz from one ICN asset's chunks. Every
    question carries a verbatim source_quote that is re-verified against the source
    text; questions whose quote can't be found are dropped (grounding by construction,
    quiz edition). Attribution + source_url + page travel with each kept question."""
    asset_id = (payload.get("asset_id") or "").strip()
    topic = (payload.get("topic") or "").strip()
    n = max(3, min(int(payload.get("n", 6) or 6), 10))
    if asset_id:
        chunks = _icn_chunk_index().get(asset_id) or []
        _lms, by_id = _icn_load()
        a = by_id.get(asset_id, {})
        title = _clean_title(a.get("title") or (chunks[0].get("title") if chunks else asset_id))
        attribution = a.get("attribution_text") or "Source: Institute of Child Nutrition / USDA."
        src_url = a.get("source_url")
    elif topic:
        chunks = _icn_chunks_by_topic(topic)
        title = topic.replace("_", " ").title()
        attribution = "Source: Institute of Child Nutrition / USDA."
        src_url = None
    else:
        raise HTTPException(400, "asset_id or topic is required")
    if not chunks:
        raise HTTPException(404, detail={"error": "not_ingestible",
            "message": "No ingestible text for that selection (link-only / no extracted transcript), so a quiz can't be generated."})

    # Build the excerpt menu (in the USER prompt → stdin, never the system prompt).
    by_cid = {}
    excerpts, total = [], 0
    for c in chunks:
        txt = (c.get("text") or "").strip()
        if len(txt) < 40:
            continue
        by_cid[c["chunk_id"]] = c
        excerpts.append(f"[{c['chunk_id']}]\n{txt}")
        total += len(txt)
        if total > 16000:  # keep the prompt bounded
            break
    if not excerpts:
        raise HTTPException(404, detail={"error": "no_text", "message": "No usable text excerpts for this asset."})

    prompt = (f"Document: {title}\nWrite {n} multiple-choice questions grounded ONLY in these excerpts.\n\n"
              f"EXCERPTS:\n" + "\n\n".join(excerpts) + "\n\nEmit ONLY the JSON object.")
    opts = ClaudeAgentOptions(
        model="claude-sonnet-4-6", effort="medium", system_prompt=_QUIZ_SYS,
        allowed_tools=[], disallowed_tools=_DISALLOWED, tools=[], max_turns=4,
    )
    try:
        text, _usage = await _run_text(prompt, opts)
    except Exception as e:
        raise HTTPException(502, f"quiz generation failed: {e}")
    parsed = _parse_json(text) or {}
    raw_qs = parsed.get("questions") or []

    # Grounding gate: keep only questions whose verbatim source_quote is found in a chunk.
    kept, dropped = [], 0
    for q in raw_qs:
        quote = (q.get("source_quote") or "").strip()
        opts_list = q.get("options") or []
        if not quote or len(opts_list) != 4 or not isinstance(q.get("answer"), int):
            dropped += 1
            continue
        nq = demo._norm(quote)
        src = by_cid.get(q.get("chunk_id"))
        hit = src if (src and nq in demo._norm(src.get("text", ""))) else \
              next((c for c in by_cid.values() if nq in demo._norm(c.get("text", ""))), None)
        if not hit or not (0 <= q["answer"] < 4):
            dropped += 1
            continue
        kept.append({
            "q": q.get("q", ""), "options": opts_list, "answer": q["answer"],
            "explanation": q.get("explanation", ""),
            "source_quote": quote, "page": hit.get("page"), "slide": hit.get("slide"),
            "source_url": hit.get("source_url") or src_url,
        })
    return JSONResponse({
        "asset_id": asset_id, "topic": topic, "title": title, "attribution": attribution,
        "source_url": src_url, "questions": kept,
        "generated": len(raw_qs), "kept": len(kept), "dropped": dropped,
    })


def _strip_tags(html: str) -> str:
    """HTML -> readable text for quiz grounding (drop tags, keep paragraph breaks)."""
    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", html or "")
    t = re.sub(r"(?i)</(p|div|li|h[1-6]|tr)\s*>", "\n", t)
    t = re.sub(r"(?i)<br\s*/?>", "\n", t)
    t = re.sub(r"<[^>]+>", " ", t)
    for a, b in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'), ("&#39;", "'"), ("&nbsp;", " ")):
        t = t.replace(a, b)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n\n", t)
    return t.strip()


async def _grounded_quiz(excerpts_by_id: dict, title: str, n: int, attribution: str, src_url):
    """Shared grounded-MCQ core: run _QUIZ_SYS over {excerpt_id: text}; keep ONLY questions
    whose verbatim source_quote is found in an excerpt (grounding by construction).
    Shared by /api/icn/quiz (ICN chunks) and /api/resources/{rid}/quiz (a generated guide)."""
    by_id, excerpts, total = {}, [], 0
    for eid, txt in excerpts_by_id.items():
        txt = (txt or "").strip()
        if len(txt) < 40:
            continue
        by_id[eid] = txt
        excerpts.append(f"[{eid}]\n{txt}")
        total += len(txt)
        if total > 16000:
            break
    if not excerpts:
        return {"questions": [], "generated": 0, "kept": 0, "dropped": 0,
                "title": title, "attribution": attribution, "source_url": src_url,
                "note": "no usable excerpts (guide too short/empty after stripping)"}
    prompt = (f"Document: {title}\nWrite {n} multiple-choice questions grounded ONLY in these excerpts.\n\n"
              "EXCERPTS:\n" + "\n\n".join(excerpts) + "\n\nEmit ONLY the JSON object.")
    opts = ClaudeAgentOptions(
        model="claude-sonnet-4-6", effort="medium", system_prompt=_QUIZ_SYS,
        allowed_tools=[], disallowed_tools=_DISALLOWED, tools=[], max_turns=4,
    )
    text, _usage = await _run_text(prompt, opts)
    parsed = _parse_json(text) or {}
    raw_qs = parsed.get("questions") or []
    kept, dropped = [], 0
    for q in raw_qs:
        quote = (q.get("source_quote") or "").strip()
        opts_list = q.get("options") or []
        if not quote or len(opts_list) != 4 or not isinstance(q.get("answer"), int) or not (0 <= q["answer"] < 4):
            dropped += 1
            continue
        nq = demo._norm(quote)
        cid = q.get("chunk_id")
        hit = cid if (cid in by_id and nq in demo._norm(by_id[cid])) else \
            next((eid for eid, t in by_id.items() if nq in demo._norm(t)), None)
        if not hit:
            dropped += 1
            continue
        kept.append({"q": q.get("q", ""), "options": opts_list, "answer": q["answer"],
                     "explanation": q.get("explanation", ""), "source_quote": quote, "excerpt_id": hit})
    return {"questions": kept, "generated": len(raw_qs), "kept": len(kept), "dropped": dropped,
            "title": title, "attribution": attribution, "source_url": src_url}


@app.post("/api/resources/{rid}/quiz")
async def resource_quiz(rid: str, payload: dict = Body(default={})):
    """Generate a grounded quiz FROM a published/generated guide. The guide's own sections
    are the excerpts; every kept question carries a verbatim quote found in the guide text.
    'Learning validation on a generated guide' — quiz-from-content wired to the real resource
    store. <!-- Source --> citations are stripped first so questions ground against the
    visible guide text, not the citation comments."""
    resolved = prod._resolve_resource(rid)
    if not resolved:
        raise HTTPException(404, "resource not found")
    html_path, meta_path, _status = resolved
    try:
        raw_html = html_path.read_text(encoding="utf-8")
    except OSError as e:
        raise HTTPException(500, f"could not read resource: {e}")
    clean = prod._strip_source_comments(raw_html)
    parts = re.split(r"(?is)<h[23][^>]*>(.*?)</h[23]>", clean)
    excerpts_by_id = {}
    if len(parts) >= 3:
        intro = _strip_tags(parts[0])
        if len(intro) >= 40:
            excerpts_by_id["Intro"] = intro
        for i in range(1, len(parts) - 1, 2):
            head = (_strip_tags(parts[i]).strip()[:64]) or f"Section {i // 2 + 1}"
            body = _strip_tags(parts[i + 1])
            excerpts_by_id[f"{i // 2 + 1}. {head}"] = f"{head}\n{body}"
    else:
        excerpts_by_id["Guide"] = _strip_tags(clean)
    meta = prod._read_meta(meta_path) or {}
    title = meta.get("title") or meta.get("module") or rid
    n = max(3, min(int(payload.get("n", 6) or 6), 10))
    try:
        res = await _grounded_quiz(excerpts_by_id, title, n,
                                   attribution=f"From guide {rid}: {title}", src_url=None)
    except Exception as e:
        raise HTTPException(502, f"quiz generation failed: {e}")
    return JSONResponse({"resource_id": rid, "sections": list(excerpts_by_id.keys()), **res})


@app.get("/api/resources/{rid}/exercise")
async def resource_exercise(rid: str):
    """Return ONE grounded exercise item for a guide-type lesson.

    Reuses the quiz grounding gate (_grounded_quiz / _QUIZ_SYS) but requests
    n=1 question and reshapes the result into the exercise wire format:

        { "question": "...",
          "choices": [{"text": "...", "source_quote": "..."}],
          "correct_index": 0,
          "source_span": "..." }

    Every choice is grounded: the correct choice carries a verbatim source_quote
    found in the guide text; distractor choices carry an empty source_quote.
    Returns 404 when the resource doesn't exist and 204 (no content) when the
    grounding gate produces no kept questions — both signal the client to fall
    back to hardcoded constants."""
    resolved = prod._resolve_resource(rid)
    if not resolved:
        raise HTTPException(404, "resource not found")
    html_path, meta_path, _status = resolved
    try:
        raw_html = html_path.read_text(encoding="utf-8")
    except OSError as e:
        raise HTTPException(500, f"could not read resource: {e}")
    clean = prod._strip_source_comments(raw_html)
    parts = re.split(r"(?is)<h[23][^>]*>(.*?)</h[23]>", clean)
    excerpts_by_id: dict = {}
    if len(parts) >= 3:
        intro = _strip_tags(parts[0])
        if len(intro) >= 40:
            excerpts_by_id["Intro"] = intro
        for i in range(1, len(parts) - 1, 2):
            head = (_strip_tags(parts[i]).strip()[:64]) or f"Section {i // 2 + 1}"
            body = _strip_tags(parts[i + 1])
            excerpts_by_id[f"{i // 2 + 1}. {head}"] = f"{head}\n{body}"
    else:
        excerpts_by_id["Guide"] = _strip_tags(clean)
    meta = prod._read_meta(meta_path) or {}
    title = meta.get("title") or meta.get("module") or rid
    try:
        res = await _grounded_quiz(excerpts_by_id, title, n=1,
                                   attribution=f"From guide {rid}: {title}", src_url=None)
    except Exception as e:
        raise HTTPException(502, f"exercise generation failed: {e}")
    questions = res.get("questions") or []
    if not questions:
        return Response(status_code=204)
    q = questions[0]
    choices = [
        {"text": opt, "source_quote": q.get("source_quote", "") if i == q["answer"] else ""}
        for i, opt in enumerate(q["options"])
    ]
    return JSONResponse({
        "question": q.get("q", ""),
        "choices": choices,
        "correct_index": q["answer"],
        "source_span": q.get("source_quote", ""),
    })


# ─────────────────────────────────────────────────────────────────────────────
# Library assistant — grounded Q&A over ALL library guides (the rail's "reply").
# Same grounding-by-construction as the generator and the quiz: the model may
# answer ONLY from guide excerpts, every claim carries a VERBATIM quote, and we
# DROP any citation whose quote isn't a verbatim substring of the cited guide.
# No grounded citation -> "not in the library" (never a free-form answer).
# ─────────────────────────────────────────────────────────────────────────────
_LIB_ANSWER_SYS = (
    "You are the Library Assistant for SchoolCafe Learning Studio. Answer the user's question "
    "USING ONLY the supplied guide excerpts — never outside knowledge, never a plausible guess. "
    "For EVERY claim in your answer you must cite a VERBATIM quote copied exactly from one of the "
    "excerpts. If the excerpts do not contain the answer, you MUST return answer=null — do not "
    "improvise. Reply with ONLY a JSON object, no prose around it: "
    '{"answer": "<concise 1-3 sentence answer, or null if unsupported>", '
    '"citations": [{"rid": "<the GUIDE id from the excerpt header>", '
    '"quote": "<span copied verbatim from that guide\'s excerpt>"}]}. '
    "When in doubt, answer=null. A wrong or unsupported answer is far worse than 'not in the library'."
)

_LIB_STOP = {"the", "and", "for", "does", "support", "how", "can", "what", "guide", "guides", "show",
             "find", "give", "need", "about", "with", "from", "that", "this", "have", "has", "are",
             "module", "when", "where", "who", "why", "into", "you", "your", "not", "but", "all", "any"}
_LIB_INDEX = {"sig": None, "docs": None}


def _library_docs() -> list:
    """Cached content index over library guides: [{rid,title,module,template,text,excerpts}].
    Scans both dirs (V1 keeps approved guides in DRAFTS with a status flag, not a separate tree)."""
    try:
        listing = (prod._list_resources_in(prod.DRAFTS, "draft")
                   + prod._list_resources_in(prod.PUBLISHED, "published"))
    except Exception:
        listing = []
    sig = tuple(sorted((r.get("id"), r.get("created_at", "")) for r in listing if r.get("id")))
    if _LIB_INDEX["sig"] == sig and _LIB_INDEX["docs"] is not None:
        return _LIB_INDEX["docs"]
    docs = []
    for r in listing:
        rid = r.get("id")
        if not rid:
            continue
        try:
            got = _resource_excerpts(rid)
        except Exception:
            got = None
        if not got:
            continue
        excerpts, full, title, _label = got
        if len((full or "").strip()) < 40:
            continue
        docs.append({"rid": rid, "title": title, "module": r.get("module", ""),
                     "template": r.get("template", ""), "text": full, "excerpts": excerpts})
    _LIB_INDEX["sig"], _LIB_INDEX["docs"] = sig, docs
    return docs


def _rank_library(question: str, docs: list, k: int = 4) -> list:
    """Keyword content rank (term frequency over title+module+full text). Real content search
    over ~all guides; swap in the Chroma index here for semantic recall later."""
    terms = [w for w in re.findall(r"[a-z0-9]{3,}", (question or "").lower()) if w not in _LIB_STOP]
    if not terms:
        return docs[:k]
    scored = []
    for d in docs:
        hay = (d["title"] + " " + d["module"] + " " + d["text"]).lower()
        s = sum(hay.count(t) for t in terms)
        if s:
            scored.append((s, d))
    scored.sort(key=lambda x: -x[0])
    return [d for _s, d in scored[:k]]


@app.post("/api/library/ask")
async def library_ask(payload: dict = Body(default={})):
    """Grounded Q&A over ALL library guides. Returns an answer ONLY if it can be backed by a
    verbatim quote from a real guide; otherwise 'not in the library'. Grounded by construction —
    the same gate as the generator and the quiz. This is the rail's content-query 'reply'."""
    question = (payload.get("question") or payload.get("q") or "").strip()
    if not question:
        raise HTTPException(400, "question required")
    docs = _library_docs()
    top = _rank_library(question, docs, k=4) if docs else []
    guide_cards = [{"rid": d["rid"], "title": d["title"], "module": d["module"],
                    "template": d["template"]} for d in top[:3]]
    if not top:
        return JSONResponse({"question": question, "answer": None, "grounded": False,
                             "citations": [], "guides": [], "note": "not in the library"})
    # Bounded labeled excerpts for the top guides.
    blocks, by_excerpt, total = [], {}, 0
    for d in top:
        for eid, txt in (d["excerpts"] or {}).items():
            txt = (txt or "").strip()
            if len(txt) < 40:
                continue
            by_excerpt[f"{d['rid']} :: {eid}"] = (d, txt)
            blocks.append(f"[GUIDE {d['rid']} | {d['title']} | section: {eid}]\n{txt}")
            total += len(txt)
            if total > 14000:
                break
        if total > 14000:
            break
    prompt = (f"QUESTION: {question}\n\nGUIDE EXCERPTS (the ONLY allowed source):\n\n"
              + "\n\n".join(blocks) + "\n\nEmit ONLY the JSON object.")
    opts = ClaudeAgentOptions(model="claude-sonnet-4-6", effort="medium", system_prompt=_LIB_ANSWER_SYS,
                              allowed_tools=[], disallowed_tools=_DISALLOWED, tools=[], max_turns=4)
    try:
        text, _usage = await _run_text(prompt, opts)
    except Exception as e:
        raise HTTPException(502, f"library assistant failed: {e}")
    parsed = _parse_json(text) or {}
    answer = parsed.get("answer")
    verified, guide_ids = [], []
    for c in (parsed.get("citations") or []):
        quote = (c.get("quote") or "").strip()
        if not quote:
            continue
        nq = demo._norm(quote)
        hit = next(((d, key.split(" :: ", 1)[-1]) for key, (d, txt) in by_excerpt.items()
                    if nq and nq in demo._norm(txt)), None)
        if hit:
            d, eid = hit
            verified.append({"rid": d["rid"], "title": d["title"], "module": d["module"],
                             "template": d["template"], "section": eid, "quote": quote})
            if d["rid"] not in guide_ids:
                guide_ids.append(d["rid"])
    grounded = bool(answer) and bool(verified)
    return JSONResponse({
        "question": question,
        "answer": answer if grounded else None,
        "grounded": grounded,
        "citations": verified,
        "guides": guide_cards,
        "note": None if grounded else "not in the library",
    })


# ─────────────────────────────────────────────────────────────────────────────
# Quiz Builder — create / edit / approve / take quizzes grounded in published content.
# Generation reuses the grounded MCQ core (_grounded_quiz); quiz_store owns persistence
# + the deterministic QA gate. Every edit/approve re-derives the CURRENT source text and
# re-verifies grounding, so a guide changing under a quiz is caught (drift) not ignored.
# ─────────────────────────────────────────────────────────────────────────────

def _resource_excerpts(rid: str):
    """(excerpts_by_id, full_source_text, title, label) for a generated guide, or None."""
    resolved = prod._resolve_resource(rid)
    if not resolved:
        return None
    html_path, meta_path, _status = resolved
    clean = prod._strip_source_comments(html_path.read_text(encoding="utf-8"))
    parts = re.split(r"(?is)<h[23][^>]*>(.*?)</h[23]>", clean)
    excerpts_by_id = {}
    if len(parts) >= 3:
        intro = _strip_tags(parts[0])
        if len(intro) >= 40:
            excerpts_by_id["Intro"] = intro
        for i in range(1, len(parts) - 1, 2):
            head = (_strip_tags(parts[i]).strip()[:64]) or f"Section {i // 2 + 1}"
            excerpts_by_id[f"{i // 2 + 1}. {head}"] = f"{head}\n{_strip_tags(parts[i + 1])}"
    else:
        excerpts_by_id["Guide"] = _strip_tags(clean)
    meta = prod._read_meta(meta_path) or {}
    title = meta.get("title") or meta.get("module") or rid
    label = (f"{meta.get('module', '')} {meta.get('template', '')}".strip()) or title
    return excerpts_by_id, _strip_tags(clean), title, label


def _asset_excerpts(asset_id: str):
    """(excerpts_by_id, full_source_text, title, label) for an ICN/internal Content asset."""
    chunks = _icn_chunk_index().get(asset_id) or []
    _lms, by_id = _icn_load()
    a = by_id.get(asset_id, {})
    title = _clean_title(a.get("title") or asset_id)
    excerpts_by_id, full = {}, []
    for c in chunks:
        txt = (c.get("text") or "").strip()
        if len(txt) < 40:
            continue
        excerpts_by_id[c["chunk_id"]] = txt
        full.append(txt)
    return excerpts_by_id, "\n".join(full), title, title


async def _generate_for_source(source_type: str, source_id: str, n: int):
    if source_type == "resource":
        got = _resource_excerpts(source_id)
        if not got:
            raise HTTPException(404, "source guide not found")
        excerpts, source_text, title, label = got
    elif source_type == "asset":
        excerpts, source_text, title, label = _asset_excerpts(source_id)
        if not excerpts:
            raise HTTPException(404, "no ingestible text for that asset")
    else:
        raise HTTPException(400, "source_type must be 'resource' or 'asset'")
    res = await _grounded_quiz(excerpts, title, n, attribution=f"Quiz source: {label}", src_url=None)
    return res.get("questions", []), source_text, label, title


def _quiz_source_text(quiz: dict) -> str:
    """Re-derive the CURRENT source text for a quiz (so drift is always measured live)."""
    st, sid = quiz.get("source_type"), quiz.get("source_id")
    try:
        if st == "resource":
            got = _resource_excerpts(sid)
            return got[1] if got else ""
        if st == "asset":
            return _asset_excerpts(sid)[1]
    except Exception:
        return ""
    return ""


@app.post("/api/quizzes/generate")
async def quizzes_generate(payload: dict = Body(...)):
    source_type = (payload.get("source_type") or "").strip()
    source_id = (payload.get("source_id") or "").strip()
    n = max(quiz_store.MIN_Q, min(int(payload.get("n", 6) or 6), quiz_store.MAX_Q))
    if not source_id:
        raise HTTPException(400, "source_id is required")
    try:
        gen, source_text, label, title = await _generate_for_source(source_type, source_id, n)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(502, f"quiz generation failed: {e}")
    quiz = quiz_store.build_quiz(
        source_type=source_type, source_id=source_id, source_label=label,
        title=payload.get("title") or f"Quiz — {title}",
        generated_questions=gen, source_text=source_text)
    return JSONResponse(quiz)


@app.post("/api/quizzes/create")
async def quizzes_create(payload: dict = Body(default={})):
    """Create a BLANK manual quiz (no source). Manual questions can't be auto-grounded,
    so they stay manual_unverified and need SME sign-off before approval."""
    title = (payload.get("title") or "Untitled quiz").strip()
    n = max(1, min(int(payload.get("n", 4) or 4), quiz_store.MAX_Q))
    quiz = {
        "id": quiz_store.new_quiz_id("manual"),
        "title": title, "status": "draft",
        "source_type": "manual", "source_id": "", "source_label": "Manual (no source)",
        "source_content_hash": "", "questions": [quiz_store.blank_question() for _ in range(n)],
        "stale": False,
    }
    quiz_store.save_quiz(quiz)
    return JSONResponse(quiz)


@app.get("/api/quizzes")
async def quizzes_list():
    return JSONResponse({"quizzes": quiz_store.list_quizzes()})


@app.get("/api/quizzes/{qid}")
async def quizzes_get(qid: str):
    q = quiz_store.load_quiz(qid)
    if not q:
        raise HTTPException(404, "quiz not found")
    return JSONResponse(q)


@app.put("/api/quizzes/{qid}")
async def quizzes_update(qid: str, payload: dict = Body(...)):
    quiz = quiz_store.load_quiz(qid)
    if not quiz:
        raise HTTPException(404, "quiz not found")
    if "title" in payload:
        quiz["title"] = payload["title"]
    if isinstance(payload.get("questions"), list):
        quiz["questions"] = payload["questions"]
    # An edit re-opens review and re-grounds every question against the CURRENT source.
    # It also voids any prior support-flag override — a changed quiz must be re-acknowledged.
    quiz["status"] = "draft"
    quiz["approved"] = False
    quiz["support_override"] = False
    quiz.pop("overridden_flags", None)
    src = _quiz_source_text(quiz)
    for q in quiz.get("questions", []):
        quiz_store.verify_question(q, src)
    quiz["source_content_hash"] = quiz_store.source_hash(src)
    quiz["stale"] = False
    quiz_store.save_quiz(quiz)
    return JSONResponse({"quiz": quiz, "qa": quiz_store.qa_gate(quiz, src)})


@app.get("/api/quizzes/{qid}/qa")
async def quizzes_qa(qid: str):
    """Deterministic QA + drift check. ENFORCES drift prevention: an approved quiz that
    drifted or lost grounding is dropped back to draft (stale) so it can't stay live."""
    quiz = quiz_store.load_quiz(qid)
    if not quiz:
        raise HTTPException(404, "quiz not found")
    src = _quiz_source_text(quiz)
    report = quiz_store.qa_gate(quiz, src)  # mutates questions' grounded/provenance
    reopened = False
    if quiz.get("status") == "approved" and (report["drifted"] or not report["ok"]):
        quiz["status"] = "draft"
        quiz["approved"] = False
        quiz["stale"] = True
        reopened = True
    quiz_store.save_quiz(quiz)
    return JSONResponse({"qa": report, "status": quiz.get("status"),
                         "stale": quiz.get("stale", False), "reopened": reopened})


@app.post("/api/quizzes/{qid}/approve")
async def quizzes_approve(qid: str, payload: dict = Body(default={})):
    quiz = quiz_store.load_quiz(qid)
    if not quiz:
        raise HTTPException(404, "quiz not found")
    src = _quiz_source_text(quiz)
    report = quiz_store.qa_gate(quiz, src)
    if not report["ok"]:
        quiz_store.save_quiz(quiz)
        raise HTTPException(409, detail={"error": "qa_not_clean",
            "message": "Cannot approve — the QA gate has blocking issues. "
                       "Fix grounding or get SME sign-off on manual questions.",
            "qa": report})
    # Advisory support-check flags (from /check) are OVERRIDABLE, but only with an explicit,
    # RECORDED acknowledgement. The client passes the flagged set + override; a flagged quiz
    # without override is blocked (the server holds the line, not just the UI).
    flagged = payload.get("flagged") or {}
    override = bool(payload.get("override"))
    if flagged and not override:
        quiz_store.save_quiz(quiz)
        raise HTTPException(409, detail={"error": "support_flags_unacknowledged",
            "message": f"{len(flagged)} question(s) flagged by Check answers. "
                       "Acknowledge the override to approve, or fix the flagged question(s).",
            "flagged": list(flagged.keys())})
    now = datetime.now().isoformat(timespec="seconds")
    quiz["status"] = "approved"
    quiz["approved"] = True
    quiz["stale"] = False
    quiz["approved_at"] = now
    quiz["support_override"] = bool(flagged)
    if flagged:
        quiz["overridden_flags"] = flagged
        quiz["override_at"] = now
    else:
        quiz.pop("overridden_flags", None)
    quiz_store.save_quiz(quiz)
    _log_review_decision({
        "rid": qid, "action": "approve_quiz", "quiz_title": quiz.get("title"),
        "outcome": "approved_with_override" if flagged else "approved",
        "overridden_flags": list(flagged.keys()) if flagged else [],
    })
    return JSONResponse({"quiz": quiz, "qa": report})


@app.post("/api/quizzes/{qid}/check")
async def quizzes_check(qid: str):
    """Advisory LLM 'check answers' pass: does each grounded question's cited quote actually
    SUPPORT its keyed answer? Reuses the question-bank support judge — catches wrong-key the
    verbatim gate can't. Does NOT mutate status (advisory)."""
    quiz = quiz_store.load_quiz(qid)
    if not quiz:
        raise HTTPException(404, "quiz not found")
    qs = quiz.get("questions") or []
    grounded = [(i, q) for i, q in enumerate(qs) if q.get("grounded")]

    async def _judge(i, q):
        correct = (q.get("options") or [None])[q.get("answer_index", 0)]
        try:
            verdict = await qbank_gate.llm_support_judge(q.get("source_quote", ""), q.get("stem", ""), correct)
            if not verdict.get("ok"):
                return {"index": i, "stem": q.get("stem", ""), "reason": verdict.get("reason", "")}
        except Exception as e:
            return {"index": i, "stem": q.get("stem", ""), "reason": f"judge error: {e}"}
        return None

    # Judge questions in PARALLEL (was sequential — N back-to-back LLM calls summed their latency).
    results = await asyncio.gather(*[_judge(i, q) for i, q in grounded])
    return JSONResponse({"checked": len(grounded), "flagged": [r for r in results if r]})


@app.post("/api/quizzes/{qid}/score")
async def quizzes_score(qid: str, payload: dict = Body(...)):
    quiz = quiz_store.load_quiz(qid)
    if not quiz:
        raise HTTPException(404, "quiz not found")
    return JSONResponse(quiz_store.score_quiz(quiz, payload.get("answers") or []))


@app.delete("/api/quizzes/{qid}")
async def quizzes_delete(qid: str):
    return JSONResponse({"deleted": quiz_store.delete_quiz(qid)})


@app.get("/api/resources/{rid}/approved-quiz")
async def resource_approved_quiz(rid: str):
    """Return the most-recent APPROVED quiz built from this resource, re-verified
    against the CURRENT source so a drifted/ungrounded quiz is never served. This is
    the learner 'Take quiz' deterministic path — a known-good, source-cited quiz that
    needs no live LLM call. 404 when no approved, still-grounded quiz exists for the
    resource (the caller then falls back to live generation). Grounding is NOT
    weakened: qa_gate is the same authority the approve gate uses."""
    best = None
    for row in quiz_store.list_quizzes():
        if row.get("source_id") != rid or row.get("status") != "approved":
            continue
        quiz = quiz_store.load_quiz(row["id"])
        if not quiz:
            continue
        report = quiz_store.qa_gate(quiz, _quiz_source_text(quiz))  # re-grounds in memory
        if not report["ok"]:
            continue
        if best is None or (quiz.get("approved_at") or "") > (best.get("approved_at") or ""):
            best = quiz
    if not best:
        raise HTTPException(404, "no approved quiz for this resource")
    return JSONResponse(best)


# ─────────────────────────────────────────────────────────────────────────────
# Certificates (FR-CP-08) — a learner who completes a track can be issued a
# completion certificate. Minimal + persisted: the record proves who completed
# what and when; the client renders it as a downloadable/printable certificate.
# ─────────────────────────────────────────────────────────────────────────────
CERTS = Path(__file__).resolve().parent / "certificates"


@app.post("/api/certificates")
async def issue_certificate(payload: dict = Body(default={})):
    """Issue + persist a completion certificate for a track. Validates the track
    exists; records the learner, track, and issue time. Returns the certificate."""
    track_id = (payload.get("track_id") or "").strip()
    if not track_id:
        raise HTTPException(400, "track_id is required")
    track = _ms.load_track(track_id)
    if not track:
        raise HTTPException(404, "track not found")
    learner = (payload.get("learner_name") or "").strip() or "Demo Learner"
    CERTS.mkdir(parents=True, exist_ok=True)
    now = datetime.now()
    cid = f"cert-{now.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
    cert = {
        "id": cid,
        "track_id": track_id,
        "track_title": track.get("title") or track_id,
        "learner_name": learner,
        "product": track.get("product") or "SchoolCafé",
        "role": (track.get("role_tags") or [None])[0],
        "modules": len(track.get("module_ids") or []),
        "issued_at": now.isoformat(timespec="seconds"),
    }
    (CERTS / f"{cid}.json").write_text(json.dumps(cert, indent=2, ensure_ascii=False), encoding="utf-8")
    return JSONResponse(cert)


@app.get("/api/certificates/{cid}")
async def get_certificate(cid: str):
    p = CERTS / f"{cid}.json"
    if not p.exists():
        raise HTTPException(404, "certificate not found")
    return JSONResponse(json.loads(p.read_text(encoding="utf-8")))


# ─────────────────────────────────────────────────────────────────────────────
# SCORM 1.2 export (V2) — GET /api/tracks/{id}/scorm
# Returns a self-contained .zip importable into any SCORM 1.2 LMS.
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/api/tracks/{tid}/scorm")
async def api_scorm_export(tid: str):
    """Build and return a SCORM 1.2 package for the given track.

    Returns: application/zip — Content-Disposition: attachment; filename=<title>.zip

    The package contains:
      - imsmanifest.xml  (SCORM 1.2 manifest listing all modules)
      - index.html       (SCO launch page with SCORM API shim + iframe nav)
      - content/         (module HTML from published/ or a placeholder if not found)
      - quiz/            (quiz JSON per module, when a quiz is attached)
    """
    track = _ms.load_track(tid)
    if not track:
        raise HTTPException(404, "track not found")
    expanded = _ms.expand_track(track, icn_dir=_ICN_DIR)
    modules = expanded.get("modules") or []
    try:
        zip_bytes = scorm_export.build_scorm_package(track=expanded, modules=modules)
    except Exception as exc:
        raise HTTPException(500, f"SCORM package build failed: {exc}")
    # Sanitise the track title for use as a filename.
    safe_title = re.sub(r"[^\w\s-]", "", track.get("title") or tid).strip().replace(" ", "_") or tid
    filename = f"{safe_title}.zip"
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ─────────────────────────────────────────────────────────────────────────────
# xAPI status — GET /api/xapi/status
# Reports whether the real LRS is configured.
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/api/xapi/status")
async def api_xapi_status():
    """Report xAPI client configuration.

    Returns:
      stub           — True when operating in stub mode (logs to xapi-stub.jsonl).
      lrs_configured — True when LRS_ENDPOINT + LRS_KEY are set in the environment.

    To activate real LRS writeback, set LRS_ENDPOINT and LRS_KEY in .env and restart.
    """
    return JSONResponse({
        "stub": _xapi.client.stub,
        "lrs_configured": _xapi.client.lrs_configured,
    })


_FLASH_SYS = """You write study flashcards that help school-nutrition staff learn a topic. You have NO tools.

RULES:
- Base EVERY card ONLY on the provided source excerpts. Never use outside knowledge or invent facts.
- Each card has a short "front" (a term, prompt, or question) and a "back" (the answer/definition).
- For each card you MUST include "source_quote": a SHORT verbatim span (about 5-25 words) copied EXACTLY, character-for-character, from ONE excerpt that supports the back, and "chunk_id": the id of that excerpt.
- Keep fronts crisp and backs concise. Spread cards across different excerpts.

OUTPUT — your FINAL message is ONLY this JSON object, no prose, no code fence:
{"cards":[{"front":"...","back":"...","source_quote":"exact words from an excerpt","chunk_id":"..."}]}"""


@app.post("/api/icn/flashcards")
async def icn_flashcards(payload: dict = Body(...)):
    """Generate grounded flashcards from an ICN asset OR a topic (cross-asset). Each card's
    back carries a verbatim source_quote re-verified against the source; cards that fail
    verification are dropped. Same grounding-by-construction guarantee as the quiz."""
    asset_id = (payload.get("asset_id") or "").strip()
    topic = (payload.get("topic") or "").strip()
    n = max(4, min(int(payload.get("n", 8) or 8), 14))
    if asset_id:
        chunks = _icn_chunk_index().get(asset_id) or []
        _lms, by_id = _icn_load()
        a = by_id.get(asset_id, {})
        title = _clean_title(a.get("title") or (chunks[0].get("title") if chunks else asset_id))
        attribution = a.get("attribution_text") or "Source: Institute of Child Nutrition / USDA."
        src_url = a.get("source_url")
    elif topic:
        chunks = _icn_chunks_by_topic(topic)
        title = topic.replace("_", " ").title()
        attribution = "Source: Institute of Child Nutrition / USDA."
        src_url = None
    else:
        raise HTTPException(400, "asset_id or topic is required")
    if not chunks:
        raise HTTPException(404, detail={"error": "not_ingestible",
            "message": "No ingestible text for that selection, so flashcards can't be generated."})

    by_cid, excerpts, total = {}, [], 0
    for c in chunks:
        txt = (c.get("text") or "").strip()
        if len(txt) < 40:
            continue
        by_cid[c["chunk_id"]] = c
        excerpts.append(f"[{c['chunk_id']}]\n{txt}")
        total += len(txt)
        if total > 16000:
            break
    if not excerpts:
        raise HTTPException(404, detail={"error": "no_text", "message": "No usable text excerpts."})

    prompt = (f"Topic: {title}\nWrite {n} study flashcards grounded ONLY in these excerpts.\n\n"
              f"EXCERPTS:\n" + "\n\n".join(excerpts) + "\n\nEmit ONLY the JSON object.")
    opts = ClaudeAgentOptions(
        model="claude-sonnet-4-6", effort="medium", system_prompt=_FLASH_SYS,
        allowed_tools=[], disallowed_tools=_DISALLOWED, tools=[], max_turns=4,
    )
    try:
        text, _usage = await _run_text(prompt, opts)
    except Exception as e:
        raise HTTPException(502, f"flashcard generation failed: {e}")
    raw = (_parse_json(text) or {}).get("cards") or []

    kept, dropped = [], 0
    for card in raw:
        front, back = (card.get("front") or "").strip(), (card.get("back") or "").strip()
        quote = (card.get("source_quote") or "").strip()
        if not (front and back and quote):
            dropped += 1
            continue
        nq = demo._norm(quote)
        src = by_cid.get(card.get("chunk_id"))
        hit = src if (src and nq in demo._norm(src.get("text", ""))) else \
              next((c for c in by_cid.values() if nq in demo._norm(c.get("text", ""))), None)
        if not hit:
            dropped += 1
            continue
        kept.append({"front": front, "back": back, "source_quote": quote,
                     "page": hit.get("page"), "slide": hit.get("slide"),
                     "source_url": hit.get("source_url") or src_url})
    return JSONResponse({
        "asset_id": asset_id, "topic": topic, "title": title, "attribution": attribution,
        "cards": kept, "generated": len(raw), "kept": len(kept), "dropped": dropped,
    })


@app.get("/icn/thumb/{asset_id}")
async def icn_thumb(asset_id: str):
    """Serve a page-1 preview image for an asset (PDFs only). 404 → UI shows a glyph."""
    _lms, by_id = _icn_load()
    a = by_id.get(asset_id) or {}
    rel = (a.get("preview_images") or [None])[0]
    if not rel:
        raise HTTPException(404, "no preview")
    # preview_images are stored relative to the pack root; we imported extracted/ as-is
    candidate = (_ICN_DIR / rel).resolve()
    # guard against path traversal — must stay inside data/icn
    if not str(candidate).startswith(str(_ICN_DIR.resolve())) or not candidate.exists():
        raise HTTPException(404, "preview not found")
    return Response(content=candidate.read_bytes(), media_type="image/png")


@app.get("/api/config")
async def config():
    # Offer every module we have an offline fixture for + every format.
    # `modules` are fixture-backed (required for Jira-grounded mode). Transcript-only
    # mode needs NO fixture, so it also offers `extra_modules` (free, label-only) —
    # e.g. Financials — letting you generate + verify against your own domain.
    extra = [m for m in TRANSCRIPT_EXTRA_MODULES if m not in AVAILABLE_MODULES]
    return {"modules": sorted(AVAILABLE_MODULES), "extra_modules": extra,
            "templates": list(demo_d.VALID_FORMATS),
            "external_learning": EXTERNAL_LEARNING}


@app.get("/api/evals")
async def evals_feed():
    """Live eval dashboard feed: (1) the deterministic regression suite run on the
    spot, (2) grounding for every guide generated so far (from each draft's
    citation_integrity), (3) the persisted capability suite-run logs (eval/runs/)."""
    # 1) regression — run the 15 deterministic checks live (fast, no SDK)
    try:
        import eval.regression as _reg
        passed = failed = skipped = 0
        checks = []
        for name, fn in _reg.CHECKS:
            try:
                ok, detail = fn()
            except Exception as e:  # a broken check is a fail, not a crash
                ok, detail = False, f"EXCEPTION: {e}"
            status = "skip" if ok is None else ("pass" if ok else "fail")
            checks.append({"name": name, "status": status, "detail": detail})
            skipped += ok is None
            passed += ok is True
            failed += ok is False
        regression = {"passed": passed, "failed": failed, "skipped": skipped,
                      "total": len(_reg.CHECKS), "checks": checks}
    except Exception as e:
        regression = {"error": str(e)}

    # 2) per-generation grounding — every draft that carries citation_integrity
    gens = []
    for mf in prod.DRAFTS.glob("*.json"):
        if mf.name.endswith(".eval.json"):
            continue
        m = prod._read_meta(mf) or {}
        ci = m.get("citation_integrity")
        if not ci:
            continue
        grounded = (ci.get("tier_lie", 0) == 0 and ci.get("not_found", 0) == 0
                    and ci.get("invalid_cite_id", 0) == 0)
        gens.append({
            "id": m.get("id"), "template": m.get("template"),
            "created_at": m.get("created_at", ""), "method": m.get("method", ""),
            "verified": ci.get("verified"), "tier_lie": ci.get("tier_lie"),
            "not_found": ci.get("not_found"), "invalid_cite_id": ci.get("invalid_cite_id"),
            "grounded": grounded,
            # cost_usd intentionally omitted from customer-facing payload (see /api/evals note below)
        })
    gens.sort(key=lambda g: g.get("created_at", ""), reverse=True)
    total_cost = round(sum(g.get("cost_usd") or 0 for g in gens), 4)

    # 3) capability suite-run logs
    runs = []
    runs_dir = prod.BASE / "eval" / "runs"

    def _scrub_cost(obj):
        """Recursively drop any key containing 'cost' so AI-spend never reaches the
        customer-facing payload (not even via the network tab)."""
        if isinstance(obj, dict):
            return {k: _scrub_cost(v) for k, v in obj.items() if "cost" not in k.lower()}
        if isinstance(obj, list):
            return [_scrub_cost(x) for x in obj]
        return obj

    if runs_dir.exists():
        for rj in sorted(runs_dir.glob("*/report.json"), reverse=True)[:10]:
            try:
                d = json.loads(rj.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            runs.append(_scrub_cost({"stamp": d.get("stamp"), "module": d.get("module"),
                         "trials": d.get("trials"), "per_format": d.get("per_format"),
                         "regression_summary": d.get("regression_summary")}))

    # ── Headline "Trust Score" — one number a layman gets, + plain-English parts ──
    reg_pass, reg_total = regression.get("passed", 0), (regression.get("total", 0) or 0)
    reg_rate = (reg_pass / reg_total) if reg_total else 1.0
    clean = sum(1 for g in gens if g["grounded"])
    gtotal = len(gens)
    ground_rate = (clean / gtotal) if gtotal else 1.0
    overall = round(100 * (0.5 * reg_rate + 0.5 * ground_rate))
    grade = "A" if overall >= 95 else "B" if overall >= 85 else "C" if overall >= 70 else "D"
    score = {
        "overall": overall, "grade": grade, "headline": "Grounding Trust Score",
        "one_liner": ("Every claim in every guide is automatically traced to a real source at the "
                      "correct trust level — and we check it can't be faked."),
        "components": [
            {"label": "Automated quality safeguards",
             "value": (f"All {reg_total} checks passing" if regression.get("failed", 0) == 0
                       else f"{reg_pass} of {reg_total} passing"),
             "ok": regression.get("failed", 0) == 0,
             "plain": "Built-in checks that make it impossible to misquote a source or present a low-trust "
                      "note as an approved requirement. All passing means the safety net is fully in place."},
            {"label": "Every claim backed by a real source",
             "value": (f"{clean} of {gtotal} guides verified" if gtotal else "no guides yet"),
             "ok": clean == gtotal,
             "plain": "How many generated guides have every statement traced to a genuine source at the correct "
                      "level of trust — no invented facts, no mislabelled sources."},
            # NOTE: cost is intentionally NOT exposed in the customer-facing /api/evals
            # payload. Internal cost logging stays in run logs / generation metadata, but
            # the customer never sees a price tag here. (total_cost is still computed above
            # for any internal use, just not shipped in this response.)
        ],
    }

    return {"score": score, "regression": regression, "generations": gens[:50],
            "suite_runs": runs}


def _find_long_form_html(transcript_id: str) -> str | None:
    """Most recent long-form draft for this transcript, if one exists."""
    best_html, best_at = None, ""
    for meta_file in prod.DRAFTS.glob("*.json"):
        if meta_file.name.endswith(".eval.json"):
            continue
        m = prod._read_meta(meta_file) or {}
        if m.get("transcript_id") == transcript_id and m.get("template") == "long-form":
            html_path = prod.DRAFTS / f"{m.get('id')}.html"
            if html_path.exists() and m.get("created_at", "") >= best_at:
                best_at = m.get("created_at", "")
                best_html = html_path.read_text(encoding="utf-8")
    return best_html


# ── Cell D — sectioned + quote-registry pipeline, streamed to the UI ──────────
# All three formats (long-form / micro-guide / tldr) flow through this same
# registry + CITE-ID + deterministic-render path. Grounding guaranteed by
# construction; only the section plan + budget differ by format.
async def _stream_celld(transcript_path, transcript_id, module, rid, log, fmt="long-form", directive=""):
    yield prod._sse_event("system", {"subtype": f"planning {fmt} (research)"})
    log("system", {"subtype": f"planning {fmt}"})

    budget = _FORMAT_BUDGET.get(fmt, _FORMAT_BUDGET["long-form"])
    plan_opts = ClaudeAgentOptions(
        model="claude-sonnet-4-6", effort="medium",
        system_prompt=plan_system_prompt(module, fmt),
        mcp_servers={MCP_SERVER_NAME: demo_mcp_server},
        allowed_tools=DEMO_ALLOWED_TOOLS, disallowed_tools=_DISALLOWED,
        tools=[], max_turns=20,
    )
    directive_block = (
        f"\nUSER DIRECTIVE (apply to SCOPE / EMPHASIS / AUDIENCE / TONE — e.g. focus on a "
        f"sub-topic, or frame for a specific district. FRAMING ONLY: never invent facts or "
        f"audience-specific claims not backed by tickets; fold tone/audience into each "
        f'section\'s "scope" so the writers honor it):\n  {directive.strip()}\n'
        if directive and directive.strip() else ""
    )
    plan_prompt = (
        f"Plan a {fmt} `{module}` guide from the transcript at:\n  {transcript_path}\n"
        f"{directive_block}"
        f'Call parse_transcript first (module="{module}"). Emit ONLY the JSON section plan.'
    )
    plan_parts: list[str] = []
    plan_usage = None
    try:
        async for message in query(prompt=plan_prompt, options=plan_opts):
            if isinstance(message, AssistantMessage):
                for block in (message.content or []):
                    if isinstance(block, TextBlock):
                        plan_parts.append(block.text)
                    elif isinstance(block, ToolUseBlock):
                        yield prod._sse_event("tool_call", {"name": block.name, "input": block.input, "id": block.id})
                        log("tool_call", {"name": block.name, "input": block.input})
            elif isinstance(message, UserMessage):
                for block in (message.content or []):
                    if isinstance(block, ToolResultBlock):
                        content = block.content
                        text = (" ".join(c.get("text", "") if isinstance(c, dict) else str(c) for c in content)
                                if isinstance(content, list) else str(content))
                        yield prod._sse_event("tool_result", {"tool_use_id": block.tool_use_id, "text": text})
            elif isinstance(message, ResultMessage):
                plan_usage = getattr(message, "usage", None)
    except Exception as e:
        yield prod._sse_event("error", {"message": f"planning failed: {e}"})
        return

    plan = _parse_json("\n".join(plan_parts))
    if not plan or not plan.get("sections"):
        yield prod._sse_event("error", {"message": "planner did not return a valid section plan"})
        return
    sections_plan = plan["sections"]
    all_keys = [k for s in sections_plan for k in s.get("ticket_keys", [])]
    registry, by_ticket = build_registry(all_keys)
    yield prod._sse_event("text", {"text":
        f"Planned {len(sections_plan)} sections from {len(set(all_keys))} tickets "
        f"({len(registry)} citable verbatim quotes). Writing sections in parallel…\n"})
    log("plan_done", {"sections": len(sections_plan), "spans": len(registry)})

    # Parallel section writers (CITE-IDs only), streamed as each completes.
    sem = asyncio.Semaphore(4)

    async def _idx(i, s):
        return i, await write_section(s, registry, by_ticket, module, sem, budget=budget, directive=directive)

    tasks = [asyncio.create_task(_idx(i, s)) for i, s in enumerate(sections_plan)]
    ordered: list = [None] * len(tasks)
    for fut in asyncio.as_completed(tasks):
        i, sec = await fut
        ordered[i] = sec
        yield prod._sse_event("text", {"text": f"  ✓ {sec['title']}  ({sec['secs']:.0f}s)\n"})
        log("section_done", {"title": sec["title"], "stop_reason": sec.get("stop_reason")})

    # Deterministic assemble + render (tier_lie / not_found impossible here).
    html, asm = assemble(module, ordered, registry)
    integ = validate_citations(html)

    # Cost of this run = plan call + every section call, priced from pricing.py.
    usages = [plan_usage] + [s.get("usage") for s in ordered]
    cost = pricing.cost_of(usages)

    yield prod._sse_event("text", {"text":
        f"\nAssembled. {integ['ok']} claims verified against their sources; "
        f"{integ['tier_lie']} trust-tier issues, {integ['quote_not_found']} unverifiable, "
        f"{asm['invalid_cite_id']} broken references.\n"})

    (prod.DRAFTS / f"{rid}.html").write_text(html, encoding="utf-8")
    # Grounding score: 5 if fully clean, 3 if ≤2 issues, 1 if more.
    _ci_bad = integ["tier_lie"] + integ["quote_not_found"] + asm["invalid_cite_id"]
    _grounding_score = 5 if _ci_bad == 0 else (3 if _ci_bad <= 2 else 1)
    _rubric_scores = compute_scores(html, fmt, grounding_score=_grounding_score)
    draft_meta = {
        "id": rid, "status": "draft", "module": module, "template": fmt,
        "transcript_id": transcript_id, "transcript_filename": None,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "demo": True, "method": "sectioned+registry",
        "citation_integrity": {"verified": integ["ok"], "tier_lie": integ["tier_lie"],
                               "not_found": integ["quote_not_found"], "invalid_cite_id": asm["invalid_cite_id"]},
        "scores": _rubric_scores,
        "cost_usd": cost["cost_usd"], "cost": cost,
    }
    (prod.DRAFTS / f"{rid}.json").write_text(json.dumps(draft_meta, indent=2), encoding="utf-8")
    yield prod._sse_event("done", {"resource_id": rid, "status": "draft", **draft_meta})


# ── Transcript-only Cell D — registry built from VERBATIM transcript spans ────
# Same pipeline shape as _stream_celld, but the source of truth is the uploaded
# transcript, not Jira: spans are pre-numbered into a registry, the planner assigns
# span ids to sections (no tools, no Jira), section writers emit [CITE:T####] only,
# and the gate re-verifies every span verbatim against the transcript. For
# navigation/procedure an SME demos live (Jira is behavior-only) and no-fixture modules.
async def _stream_celld_transcript(transcript_path, transcript_id, module, rid, log, fmt="long-form", directive=""):
    yield prod._sse_event("system", {"subtype": f"planning {fmt} (transcript-only)"})
    log("system", {"subtype": f"planning {fmt} transcript-only"})

    try:
        transcript_text = Path(transcript_path).read_text(encoding="utf-8")
    except OSError as e:
        yield prod._sse_event("error", {"message": f"could not read transcript: {e}"})
        return

    registry, by_span, ids = build_transcript_registry(transcript_text)
    if not ids:
        yield prod._sse_event("error", {"message": "transcript produced no citable spans (too short or empty)"})
        return
    span_menu = transcript_span_menu(registry, ids)

    budget = _FORMAT_BUDGET.get(fmt, _FORMAT_BUDGET["long-form"])
    directive_block = (
        f"\nUSER DIRECTIVE (apply to SCOPE / EMPHASIS / AUDIENCE / TONE only — FRAMING ONLY: "
        f"never invent facts or claims not in the transcript spans):\n  {directive.strip()}\n"
        if directive and directive.strip() else ""
    )
    plan_opts = ClaudeAgentOptions(
        model="claude-sonnet-4-6", effort="medium",
        system_prompt=transcript_plan_system_prompt(module, fmt),
        allowed_tools=[], disallowed_tools=_DISALLOWED, tools=[], max_turns=8,
    )
    # The span list goes in the USER prompt (stdin), NOT the system prompt — the SDK
    # passes system_prompt as a CLI arg, which would blow the Windows command-line
    # length limit for a real transcript and make the CLI fail to spawn.
    plan_prompt = (
        f"Plan a {fmt} `{module}` guide grounded ONLY in the numbered transcript spans below.\n"
        f"{directive_block}"
        f"Assign span ids to each section. Emit ONLY the JSON section plan.\n\n"
        f"NUMBERED TRANSCRIPT SPANS:\n{span_menu}"
    )
    plan_parts: list[str] = []
    plan_usage = None
    try:
        async for message in query(prompt=plan_prompt, options=plan_opts):
            if isinstance(message, AssistantMessage):
                for block in (message.content or []):
                    if isinstance(block, TextBlock):
                        plan_parts.append(block.text)
            elif isinstance(message, ResultMessage):
                plan_usage = getattr(message, "usage", None)
    except Exception as e:
        yield prod._sse_event("error", {"message": f"planning failed: {e}"})
        return

    plan = _parse_json("\n".join(plan_parts))
    if not plan or not plan.get("sections"):
        yield prod._sse_event("error", {"message": "planner did not return a valid section plan"})
        return
    sections_plan = plan["sections"]
    used = {c for s in sections_plan for c in s.get("span_ids", [])}
    yield prod._sse_event("text", {"text":
        f"Planned {len(sections_plan)} sections from {len(used)} verbatim transcript spans "
        f"({len(ids)} spans available). Writing sections in parallel…\n"})
    log("plan_done", {"sections": len(sections_plan), "spans_used": len(used)})

    sem = asyncio.Semaphore(4)

    async def _idx(i, s):
        return i, await write_section(s, registry, by_span, module, sem, budget=budget,
                                      directive=directive, section_tmpl=SECTION_SYSTEM_PROMPT_TRANSCRIPT)

    tasks = [asyncio.create_task(_idx(i, s)) for i, s in enumerate(sections_plan)]
    ordered: list = [None] * len(tasks)
    for fut in asyncio.as_completed(tasks):
        i, sec = await fut
        ordered[i] = sec
        yield prod._sse_event("text", {"text": f"  ✓ {sec['title']}  ({sec['secs']:.0f}s)\n"})
        log("section_done", {"title": sec["title"], "stop_reason": sec.get("stop_reason")})

    html, asm = assemble(module, ordered, registry)
    integ = validate_citations(html, transcript_text=transcript_text)
    usages = [plan_usage] + [s.get("usage") for s in ordered]
    cost = pricing.cost_of(usages)

    yield prod._sse_event("text", {"text":
        f"\nAssembled. {integ['ok']} claims verified verbatim against the transcript; "
        f"{integ['quote_not_found']} unverifiable, {asm['invalid_cite_id']} broken references.\n"})

    (prod.DRAFTS / f"{rid}.html").write_text(html, encoding="utf-8")
    # Grounding score: no tier_lie possible (transcript-only has no Jira tier), so only count not_found + broken refs.
    _ci_bad_t = integ["quote_not_found"] + asm["invalid_cite_id"]
    _grounding_score_t = 5 if _ci_bad_t == 0 else (3 if _ci_bad_t <= 2 else 1)
    _rubric_scores_t = compute_scores(html, fmt, grounding_score=_grounding_score_t)
    draft_meta = {
        "id": rid, "status": "draft", "module": module, "template": fmt,
        "transcript_id": transcript_id, "transcript_filename": None,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "demo": True, "method": "transcript+registry", "source": "transcript-only",
        "citation_integrity": {"verified": integ["ok"], "tier_lie": integ["tier_lie"],
                               "not_found": integ["quote_not_found"], "invalid_cite_id": asm["invalid_cite_id"]},
        "scores": _rubric_scores_t,
        "cost_usd": cost["cost_usd"], "cost": cost,
    }
    (prod.DRAFTS / f"{rid}.json").write_text(json.dumps(draft_meta, indent=2), encoding="utf-8")
    _deterministic_eval(rid, html, transcript_text=transcript_text)  # write eval.json with transcript verify
    yield prod._sse_event("done", {"resource_id": rid, "status": "draft", **draft_meta})


# ── /generate — offline generation against the fixture ────────────────────────
async def _stream_generation_demo(transcript_id: str, module: str, template: str,
                                  directive: str = "", source: str = "jira"):
    _ensure_fixture(module)  # ground against THIS module's Jira, not whatever loaded last
    meta = prod._read_meta(prod.TRANSCRIPT_META / f"{transcript_id}.json")
    if not meta:
        yield prod._sse_event("error", {"message": f"transcript {transcript_id} not found"})
        return
    transcript_path = (prod.BASE / meta["path"]).resolve()

    rid = prod._resource_id(module, template)
    log_path = prod.LOGS / f"{rid}.jsonl"

    def log(event_kind, payload):
        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"k": event_kind, "p": payload}, ensure_ascii=False) + "\n")

    yield prod._sse_event("start", {
        "resource_id": rid, "transcript_id": transcript_id,
        "module": module, "template": template, "source": source,
    })

    # Transcript-only mode: ground solely in the uploaded transcript (no Jira).
    if source == "transcript" and template in demo_d.VALID_FORMATS:
        async for ev in _stream_celld_transcript(transcript_path, transcript_id, module, rid, log, fmt=template, directive=directive):
            yield ev
        return

    # ALL formats use the validated Cell D sectioned+registry pipeline — grounding
    # guaranteed by construction (long-form, micro-guide, tldr, release-notes).
    if template in demo_d.VALID_FORMATS:
        async for ev in _stream_celld(transcript_path, transcript_id, module, rid, log, fmt=template, directive=directive):
            yield ev
        return

    # (legacy derive path — unused now that all formats go through Cell D)
    # Cascade: if this is a short guide and a long-form already exists for this
    # transcript, DERIVE from it (fast, no Jira) instead of re-researching.
    lf_html = _find_long_form_html(transcript_id) if template != "long-form" else None
    deriving = lf_html is not None
    try:
        if deriving:
            options = build_derive_options(template)
            prompt = build_derive_prompt(lf_html, template, module)
            yield prod._sse_event("system", {"subtype": "deriving_from_long_form"})
            log("system", {"subtype": "deriving_from_long_form"})
        else:
            options = build_demo_options(template)  # ← offline tools, no Jira
            prompt = build_user_prompt(str(transcript_path), module, template)
    except ValueError as e:
        yield prod._sse_event("error", {"message": str(e)})
        return

    final_text_parts: list[str] = []
    result_meta: dict = {}

    try:
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, SystemMessage):
                payload = {"subtype": getattr(message, "subtype", "?")}
                yield prod._sse_event("system", payload)
                log("system", payload)
            elif isinstance(message, AssistantMessage):
                for block in (message.content or []):
                    if isinstance(block, TextBlock):
                        final_text_parts.append(block.text)
                        yield prod._sse_event("text", {"text": block.text})
                        log("text", {"text": block.text[:500]})
                    elif isinstance(block, ThinkingBlock):
                        yield prod._sse_event("thinking", {"text": block.thinking})
                    elif isinstance(block, ToolUseBlock):
                        payload = {"name": block.name, "input": block.input, "id": block.id}
                        yield prod._sse_event("tool_call", payload)
                        log("tool_call", {"name": block.name, "input": block.input})
            elif isinstance(message, UserMessage):
                for block in (message.content or []):
                    if isinstance(block, ToolResultBlock):
                        content = block.content
                        if isinstance(content, list):
                            text = " ".join(
                                c.get("text", "") if isinstance(c, dict) else str(c)
                                for c in content
                            )
                        else:
                            text = str(content)
                        yield prod._sse_event("tool_result", {
                            "tool_use_id": block.tool_use_id, "text": text,
                        })
                        log("tool_result", {"len": len(text), "preview": text[:200]})
            elif isinstance(message, ResultMessage):
                result_meta = {
                    "cost_usd": getattr(message, "total_cost_usd", None),
                    "num_turns": getattr(message, "num_turns", None),
                    "duration_ms": getattr(message, "duration_ms", None),
                }
                yield prod._sse_event("result", result_meta)
                log("result", result_meta)
    except Exception as e:
        yield prod._sse_event("error", {"message": f"agent run failed: {e}"})
        log("error", {"message": str(e)})
        return

    html_text = "\n".join(final_text_parts).strip()
    import re
    fence = re.search(r"```(?:html)?\s*([\s\S]*?)```", html_text)
    if fence:
        html_text = fence.group(1).strip()
    h_match = re.search(r"<h[1-2]\b", html_text, flags=re.I)
    if h_match:
        html_text = html_text[h_match.start():].strip()

    (prod.DRAFTS / f"{rid}.html").write_text(html_text, encoding="utf-8")
    draft_meta = {
        "id": rid, "status": "draft", "module": module, "template": template,
        "transcript_id": transcript_id, "transcript_filename": meta.get("filename"),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "demo": True, **result_meta,
    }
    if deriving:
        draft_meta["derived_from"] = "long-form"
    (prod.DRAFTS / f"{rid}.json").write_text(json.dumps(draft_meta, indent=2), encoding="utf-8")
    yield prod._sse_event("done", {"resource_id": rid, "status": "draft", **draft_meta})


@app.get("/generate")
async def generate(
    transcript_id: str = Query(...),
    module: str = Query(...),
    template: str = Query(...),
    directive: str = Query("", description="optional authoring directive: audience/focus/tone (framing only)"),
    source: str = Query("jira", description="grounding source: 'jira' (default) or 'transcript' (transcript-only mode)"),
):
    # Jira mode needs an offline fixture; transcript-only mode does NOT (it grounds
    # in the uploaded transcript itself, so it works for any module).
    if source != "transcript" and module not in AVAILABLE_MODULES:
        raise HTTPException(400, f"no offline fixture for module '{module}'. Available: {sorted(AVAILABLE_MODULES)}")
    if template not in demo_d.VALID_FORMATS:
        raise HTTPException(400, f"unknown format: {template}")
    if source not in ("jira", "transcript"):
        raise HTTPException(400, f"unknown source: {source} (expected 'jira' or 'transcript')")
    return EventSourceResponse(_stream_generation_demo(transcript_id, module, template, directive, source))


# ── /resources/{rid}/evaluate — DETERMINISTIC grounding gate ──────────────────
# The product's trust guarantee: re-check every citation token against the real
# source field by exact match. No LLM (the model-based eval threw transient SDK
# errors and isn't needed — the deterministic check IS the guarantee).
async def _stream_evaluation_demo(rid: str, draft_html: str, transcript_text: str, meta: dict):
    yield prod._sse_event("eval_start", {"resource_id": rid})
    eval_data = _deterministic_eval(rid, draft_html, transcript_text=transcript_text)
    yield prod._sse_event("eval_done", eval_data)


@app.get("/resources/{rid}/evaluate")
async def evaluate_resource(rid: str):
    resolved = prod._resolve_resource(rid)
    if not resolved:
        raise HTTPException(404, "resource not found")
    html_path, meta_path, _status = resolved

    meta = prod._read_meta(meta_path) or {}
    if meta.get("module"):
        _ensure_fixture(meta["module"])  # grounding check must use this draft's module fixture
    # The demo evaluator is DETERMINISTIC (validate_citations) and ignores the
    # transcript, so a transcript is optional — scope-built drafts have none.
    transcript_text = ""
    transcript_id = meta.get("transcript_id")
    if transcript_id:
        t_meta = prod._read_meta(prod.TRANSCRIPT_META / f"{transcript_id}.json")
        if t_meta:
            tp = (prod.BASE / t_meta["path"]).resolve()
            if tp.exists():
                transcript_text = tp.read_text(encoding="utf-8")
    draft_html = html_path.read_text(encoding="utf-8")
    return EventSourceResponse(_stream_evaluation_demo(rid, draft_html, transcript_text, meta))


# ── /resources/{rid}/publish_pending — release for use, marked "Pending SME Review" ──
# Our converged policy: the deterministic grounding gate is the machine floor;
# SME sign-off is the human floor. This action releases a provably-grounded doc
# for use + download, stamped "Pending Review by SME" until a human approves.
@app.post("/resources/{rid}/publish_pending")
async def publish_pending(rid: str):
    resolved = prod._resolve_resource(rid)
    if not resolved:
        raise HTTPException(404, "resource not found")
    html_path, meta_path, _status = resolved
    meta = prod._read_meta(meta_path) or {}

    # Machine floor: only release provably-grounded docs.
    ci = meta.get("citation_integrity")
    if not ci:  # older/non-Cell-D draft — compute grounding now
        if meta.get("module"):
            _ensure_fixture(meta["module"])
        integ = validate_citations(html_path.read_text(encoding="utf-8"),
                                   transcript_text=_transcript_text_for(meta))
        ci = {"tier_lie": integ["tier_lie"], "not_found": integ["quote_not_found"],
              "invalid_cite_id": 0}
    violations = (ci.get("tier_lie", 0) or 0) + (ci.get("not_found", 0) or 0) + (ci.get("invalid_cite_id", 0) or 0)
    if violations > 0:
        raise HTTPException(409, detail={
            "error": "grounding_not_clean",
            "message": "Cannot release: the grounding gate has violations. "
                       "Fix grounding before releasing for SME review.",
            "citation_integrity": ci,
        })

    meta["status"] = "pending_sme_review"
    meta["status_label"] = "Pending Review by SME"
    meta["available"] = True
    meta["sme_approved"] = False
    meta["released_at"] = datetime.now().isoformat(timespec="seconds")
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta


# ── Intent-and-scope front end: "describe what you need" (no transcript) ──────
# The agent resolves WHAT to build (module, topic, format, outline) and grounds it
# in real tickets; it never supplies content. A confirmed outline flows through the
# SAME back half of the Cell-D pipeline (registry → section writers → assemble →
# deterministic gate), so grounding-by-construction is identical to the transcript path.
_SCOPE_TOOLS = [f"mcp__{MCP_SERVER_NAME}__{n}" for n in ("match_tickets", "read_ticket", "read_epic")]


def _scope_search_options(module: str, fmt: str) -> ClaudeAgentOptions:
    spec = demo_d._FORMAT_SPEC.get(fmt, demo_d._FORMAT_SPEC["long-form"])
    return ClaudeAgentOptions(
        model="claude-sonnet-4-6", effort="medium",
        system_prompt=intent_agent.build_scope_system_prompt(module, fmt, spec),
        mcp_servers={MCP_SERVER_NAME: demo_mcp_server},
        allowed_tools=_SCOPE_TOOLS, disallowed_tools=_DISALLOWED,
        tools=[], max_turns=20,
    )


async def _stream_from_scope(module: str, fmt: str, sections_plan: list[dict], topic: str):
    """Generate from a CONFIRMED scope outline — the back half of _stream_celld,
    minus the transcript planner. The outline IS the plan."""
    _ensure_fixture(module)
    rid = prod._resource_id(module, fmt)
    log_path = prod.LOGS / f"{rid}.jsonl"

    def log(k, p):
        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"k": k, "p": p}, ensure_ascii=False) + "\n")

    yield prod._sse_event("start", {"resource_id": rid, "module": module, "template": fmt, "source": "intent-scope"})
    budget = _FORMAT_BUDGET.get(fmt, _FORMAT_BUDGET["long-form"])
    all_keys = [k for s in sections_plan for k in s.get("ticket_keys", [])]
    registry, by_ticket = build_registry(all_keys)
    yield prod._sse_event("text", {"text":
        f"Confirmed scope: {len(sections_plan)} sections from {len(set(all_keys))} tickets "
        f"({len(registry)} citable verbatim quotes). Writing sections in parallel…\n"})
    log("scope_confirmed", {"sections": len(sections_plan), "spans": len(registry)})

    sem = asyncio.Semaphore(4)

    async def _idx(i, s):
        return i, await write_section(s, registry, by_ticket, module, sem, budget=budget)

    tasks = [asyncio.create_task(_idx(i, s)) for i, s in enumerate(sections_plan)]
    ordered: list = [None] * len(tasks)
    for fut in asyncio.as_completed(tasks):
        i, sec = await fut
        ordered[i] = sec
        yield prod._sse_event("text", {"text": f"  ✓ {sec['title']}  ({sec['secs']:.0f}s)\n"})

    html, asm = assemble(module, ordered, registry)
    integ = validate_citations(html)
    cost = pricing.cost_of([s.get("usage") for s in ordered])

    (prod.DRAFTS / f"{rid}.html").write_text(html, encoding="utf-8")
    # Grounding score: 5 if fully clean, 3 if ≤2 issues, 1 if more.
    _ci_bad_s = integ["tier_lie"] + integ["quote_not_found"] + asm["invalid_cite_id"]
    _grounding_score_s = 5 if _ci_bad_s == 0 else (3 if _ci_bad_s <= 2 else 1)
    _rubric_scores_s = compute_scores(html, fmt, grounding_score=_grounding_score_s)
    draft_meta = {
        "id": rid, "status": "draft", "module": module, "template": fmt,
        "transcript_id": None, "transcript_filename": None,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "demo": True, "method": "scope+registry", "source": "intent-scope", "topic": topic,
        "citation_integrity": {"verified": integ["ok"], "tier_lie": integ["tier_lie"],
                               "not_found": integ["quote_not_found"], "invalid_cite_id": asm["invalid_cite_id"]},
        "scores": _rubric_scores_s,
        "cost_usd": cost["cost_usd"], "cost": cost,
    }
    (prod.DRAFTS / f"{rid}.json").write_text(json.dumps(draft_meta, indent=2), encoding="utf-8")
    _deterministic_eval(rid, html)  # write eval.json so the verdict is on file (no transcript needed)
    yield prod._sse_event("text", {"text":
        f"\nAssembled. {integ['ok']} claims verified against their sources; tier issues={integ['tier_lie']}, "
        f"unverifiable={integ['quote_not_found']}, broken references={asm['invalid_cite_id']}.\n"})
    yield prod._sse_event("done", {"resource_id": rid, "status": "draft", **draft_meta})


@app.post("/intent/resolve")
async def intent_resolve(payload: dict = Body(...)):
    """Stage 1 (module + intent) → Stage 2 (fixture-scoped scope search). Returns a
    ScopeProposal, a clarifying question, or a refusal. Asks rather than guessing on
    ambiguity — the primary defense against silent wrong-module grounding."""
    request = (payload.get("request") or "").strip()
    if not request:
        raise HTTPException(400, "request is required")
    history = payload.get("history") or ""
    mods = sorted(AVAILABLE_MODULES)

    try:
        rtext, rusage = await _run_text(
            intent_agent.build_resolver_prompt(request, mods, history),
            intent_agent.build_resolver_options())
    except Exception as e:
        raise HTTPException(502, f"resolver failed: {e}")
    r = intent_agent.parse_json(rtext) or {}

    if r.get("refused"):
        _log_review_decision({"action": "intent_resolve", "outcome": "refused",
                              "request": request, "reason": r.get("refused_reason")})
        return JSONResponse({"stage": "refused", "reason": r.get("refused_reason")
                             or "No grounded data for that area yet.", "available_modules": mods})
    module = r.get("module")
    if r.get("ambiguous") or not module or module not in AVAILABLE_MODULES:
        q = r.get("clarifying_question") or "Which product module should this cover?"
        _log_review_decision({"action": "intent_resolve", "outcome": "clarify",
                              "request": request, "question": q})
        return JSONResponse({"stage": "clarify", "question": q, "available_modules": mods})

    fmt = r.get("format") if r.get("format") in demo_d.VALID_FORMATS else "long-form"
    topic = r.get("topic") or request
    depth = r.get("depth") or ""
    _ensure_fixture(module)
    prompt = (f"The user wants a {fmt} guide about: {topic}\n"
              f"Research the {module} Jira (module-scoped) and produce the section outline. Emit ONLY the JSON.")
    try:
        stext, susage = await _run_text(prompt, _scope_search_options(module, fmt))
    except Exception as e:
        raise HTTPException(502, f"scope search failed: {e}")
    s = intent_agent.parse_json(stext) or {}
    cost = pricing.cost_of([rusage, susage])

    if not s.get("supported", True) or not s.get("sections"):
        _log_review_decision({"action": "intent_resolve", "outcome": "unsupported",
                              "request": request, "module": module, "note": s.get("note")})
        return JSONResponse({"stage": "unsupported", "module": module,
                             "note": s.get("note") or "No supporting tickets for that topic in this module.",
                             "cost_usd": cost["cost_usd"]})

    keys = sorted({k for sec in s["sections"] for k in sec.get("ticket_keys", [])})
    _log_review_decision({"action": "intent_resolve", "outcome": "scope_proposed", "module": module,
                          "request": request, "topic": topic, "format": fmt,
                          "sections": len(s["sections"]), "ticket_keys": keys,
                          "assumed_format": bool(r.get("assumed_format")), "cost_usd": cost["cost_usd"]})
    return JSONResponse({"stage": "scope", "cost_usd": cost["cost_usd"], "scope": {
        "module": module, "format": fmt, "depth": depth, "topic": topic,
        "assumed_format": bool(r.get("assumed_format")), "sections": s["sections"]}})


@app.post("/intent/confirm")
async def intent_confirm(payload: dict = Body(...)):
    """Hand a confirmed scope to the pipeline. Output is a draft, subject to the same
    review → edit → triage → re-gate → approve flow as any other guide."""
    scope = payload.get("scope") or {}
    module = scope.get("module")
    fmt = scope.get("format") if scope.get("format") in demo_d.VALID_FORMATS else "long-form"
    sections = scope.get("sections") or []
    if module not in AVAILABLE_MODULES:
        raise HTTPException(400, f"unknown/missing module: {module}")
    if not sections:
        raise HTTPException(400, "scope has no sections")
    return EventSourceResponse(_stream_from_scope(module, fmt, sections, scope.get("topic", "")))


# ── POST /resources/{rid}/revise — AI-assisted edit (the human review loop) ───
# Reviewer describes a change in plain English. An edit agent emits targeted
# find/replace ops that NEVER touch <!-- Source --> citations; we apply them,
# re-run the deterministic grounding gate (free), and a triage agent classifies
# the edit stylistic vs substantive so stylistic tweaks approve fast and
# substantive ones get flagged. An edit un-approves the doc (must re-approve).
@app.post("/resources/{rid}/revise")
async def revise_resource(rid: str, payload: dict = Body(...)):
    instruction = (payload.get("instruction") or "").strip()
    if not instruction:
        raise HTTPException(400, "instruction is required")

    resolved = prod._resolve_resource(rid)
    if not resolved:
        raise HTTPException(404, "resource not found")
    html_path, meta_path, _status = resolved
    meta = prod._read_meta(meta_path) or {}
    module = meta.get("module")
    fmt = meta.get("template", "?")
    if module:
        _ensure_fixture(module)  # grounding re-check must use this draft's module fixture
    t_text = _transcript_text_for(meta)  # for transcript-only drafts: verify spans verbatim
    raw_html = html_path.read_text(encoding="utf-8")

    # 1) Edit agent → find/replace ops (no whole-doc rewrite, no citation edits)
    try:
        edit_text, edit_usage = await _run_text(
            revise.build_edit_prompt(raw_html, instruction, fmt, module or "?"),
            revise.build_edit_options(),
        )
    except Exception as e:
        raise HTTPException(502, f"edit agent failed: {e}")
    edit_json = revise.parse_json(edit_text) or {}

    if edit_json.get("refused"):
        refusal_kind = edit_json.get("refusal_kind") or "none"
        refusal_reason = edit_json.get("refusal_reason") or edit_json.get("notes") or "The edit was refused."
        _log_review_decision({
            "rid": rid, "module": module, "template": fmt, "action": "revise",
            "instruction": instruction, "outcome": "refused",
            "refusal_kind": refusal_kind, "refusal_reason": refusal_reason,
        })
        return JSONResponse({
            "rid": rid, "changed": False, "refused": True,
            "refusal_kind": refusal_kind, "refusal_reason": refusal_reason,
            "applied": [], "skipped": [],
        })

    ops = edit_json.get("ops") or []
    new_html, applied, skipped = revise.apply_ops(raw_html, ops)
    changed = bool(applied) and new_html != raw_html

    # 2) Deterministic grounding re-check — ALWAYS, free, non-negotiable backstop.
    integ = validate_citations(new_html, transcript_text=t_text)
    invalid = new_html.count("INVALID_CITE_ID")
    violations = integ["tier_lie"] + integ["quote_not_found"] + invalid
    verdict = "pass" if violations == 0 else "fail"
    integrity = {"verified": integ["ok"], "tier_lie": integ["tier_lie"],
                 "not_found": integ["quote_not_found"], "invalid_cite_id": invalid}

    # 3) Triage agent → does this edit need a closer (substantive) human look?
    triage = {"classification": "stylistic", "reason": "No operations were applied.", "confidence": 1.0}
    triage_usage = None
    if applied:
        try:
            triage_text, triage_usage = await _run_text(
                revise.build_triage_prompt(instruction, applied),
                revise.build_triage_options(),
            )
            parsed = revise.parse_json(triage_text)
        except Exception:
            parsed = None
        if parsed and parsed.get("classification") in ("stylistic", "substantive"):
            triage = parsed
        else:
            triage = {"classification": "substantive",
                      "reason": "Triage output could not be parsed — defaulting to substantive (safe).",
                      "confidence": 0.0}

    cost = pricing.cost_of([edit_usage, triage_usage])

    if changed:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        # Audit backup in a subdir so it is NOT picked up by the *.html resource glob.
        backup_dir = prod.DRAFTS / "_pre_edit"
        backup_dir.mkdir(exist_ok=True)
        (backup_dir / f"{rid}-{ts}.html").write_text(raw_html, encoding="utf-8")
        html_path.write_text(new_html, encoding="utf-8")

        _deterministic_eval(rid, new_html, transcript_text=t_text)  # refresh drafts/<rid>.eval.json
        meta["citation_integrity"] = integrity
        # An edit re-opens review: an approved guide drops back to draft until re-approved.
        if meta.get("approved"):
            meta["approved"] = False
            meta["status"] = "draft"
            meta.pop("approved_at", None)
            meta.pop("status_label", None)
        meta.setdefault("edit_history", []).append({
            "at": datetime.now().isoformat(timespec="seconds"),
            "instruction": instruction,
            "applied": len(applied), "skipped": len(skipped),
            "classification": triage.get("classification"),
            "reason": triage.get("reason"),
            "verdict": verdict,
            "cost_usd": cost["cost_usd"],
        })
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    _log_review_decision({
        "rid": rid, "module": module, "template": fmt, "action": "revise",
        "instruction": instruction,
        "outcome": "applied" if changed else "no_change",
        "ops_applied": len(applied), "ops_skipped": len(skipped),
        "ops": _trunc_ops(applied), "skipped": [{"why": s.get("why"), "find": s.get("find", "")[:80]} for s in skipped[:8]],
        "triage": triage, "verdict": verdict, "integrity": integrity,
        "cost_usd": cost["cost_usd"],
    })

    return JSONResponse({
        "rid": rid, "changed": changed, "refused": False,
        "applied": applied, "skipped": skipped,
        "notes": edit_json.get("notes", ""),
        "integrity": integrity, "verdict": verdict,
        "triage": triage,
        "needs_closer_review": triage.get("classification") == "substantive",
        "html": prod._strip_source_comments(new_html), "raw_html": new_html,
        "cost_usd": cost["cost_usd"],
    })


# ── POST /resources/{rid}/approve — the human gate INTO the Library ───────────
# Approval is the human floor on top of the machine grounding floor. Only an
# approved resource appears in the Library. Grounding must be clean to approve.
@app.post("/resources/{rid}/approve")
async def approve_resource(rid: str):
    resolved = prod._resolve_resource(rid)
    if not resolved:
        raise HTTPException(404, "resource not found")
    html_path, meta_path, _status = resolved
    meta = prod._read_meta(meta_path) or {}

    # Machine floor: re-validate LIVE against the current fixture (don't trust a
    # possibly-stale stored integrity — the gate must reflect ground truth now).
    if meta.get("module"):
        _ensure_fixture(meta["module"])
    raw_html = html_path.read_text(encoding="utf-8")
    integ = validate_citations(raw_html, transcript_text=_transcript_text_for(meta))
    invalid = raw_html.count("INVALID_CITE_ID")
    ci = {"verified": integ["ok"], "tier_lie": integ["tier_lie"],
          "not_found": integ["quote_not_found"], "invalid_cite_id": invalid}
    violations = ci["tier_lie"] + ci["not_found"] + ci["invalid_cite_id"]
    if violations > 0:
        _log_review_decision({
            "rid": rid, "module": meta.get("module"), "template": meta.get("template"),
            "action": "approve", "outcome": "approve_blocked", "integrity": ci,
        })
        raise HTTPException(409, detail={
            "error": "grounding_not_clean",
            "message": "Cannot approve: the grounding gate has violations. "
                       "Fix grounding (or revise) before approving.",
            "citation_integrity": ci,
        })
    meta["citation_integrity"] = ci  # refresh with the live result

    meta["status"] = "approved"
    meta["status_label"] = "Approved · in Library"
    meta["approved"] = True
    meta["available"] = True
    meta["approved_at"] = datetime.now().isoformat(timespec="seconds")
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    _log_review_decision({
        "rid": rid, "module": meta.get("module"), "template": meta.get("template"),
        "action": "approve", "outcome": "approved", "integrity": ci,
    })
    return meta


# ── GET /review-log — the review-loop decision audit trail ────────────────────
# Every edit/approve decision (applied, refused, no_change, approved, blocked).
# Filter by ?rid= for one resource. The substrate for auditing appropriateness
# and for mining real-traffic cases into the triage/scope evals.
@app.get("/review-log")
async def review_log(rid: str | None = None, limit: int = 200):
    p = prod.LOGS / "review-decisions.jsonl"
    if not p.exists():
        return JSONResponse({"entries": [], "total": 0})
    entries = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if rid and e.get("rid") != rid:
            continue
        entries.append(e)
    # quick tallies so an auditor sees the shape at a glance
    counts: dict[str, int] = {}
    for e in entries:
        counts[e.get("outcome", "?")] = counts.get(e.get("outcome", "?"), 0) + 1
    return JSONResponse({"total": len(entries), "counts": counts, "entries": entries[-limit:]})


# ── DELETE /resources/{rid} — remove a guide + its metadata + eval ────────────
@app.delete("/resources/{rid}")
async def delete_resource(rid: str):
    removed = []
    for d in (prod.DRAFTS, prod.PUBLISHED, prod.PUB_META):
        for suffix in (".html", ".json", ".eval.json"):
            p = d / f"{rid}{suffix}"
            if p.exists():
                try:
                    p.unlink()
                    removed.append(p.name)
                except OSError:
                    pass
    for bak in (prod.DRAFTS / "_pre_edit").glob(f"{rid}-*.html"):  # AI-edit audit backups
        try:
            bak.unlink()
            removed.append(bak.name)
        except OSError:
            pass
    log_path = prod.LOGS / f"{rid}.jsonl"
    if log_path.exists():
        try:
            log_path.unlink()
            removed.append(log_path.name)
        except OSError:
            pass
    if not removed:
        raise HTTPException(404, "resource not found")
    return {"deleted": rid, "files": removed}


if __name__ == "__main__":
    import uvicorn
    # Windows: the Claude Agent SDK spawns the `claude` CLI as a child process,
    # which REQUIRES the ProactorEventLoop. If uvicorn ends up on a
    # SelectorEventLoop (its win32 choice in some configs), every generation dies
    # with "Claude Code not found" because Selector can't spawn subprocesses on
    # Windows. Force a Proactor loop and run uvicorn's server inside it so the
    # loop type is deterministic regardless of uvicorn's own factory choice.
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        config = uvicorn.Config("demo_app:app", host="127.0.0.1", port=8001, reload=False, loop="asyncio")
        asyncio.run(uvicorn.Server(config).serve())
    else:
        uvicorn.run("demo_app:app", host="127.0.0.1", port=8001, reload=False)

# ── Compliance report (BRD FR-RP-03 — CN Director export) ───────────────────
# V2 scaffold: reads from the SAME seeded roster as /api/roster.
# Real data requires SSO + roster sync (Platform V1.5, Tasks 11–13).
# Every response is stamped "DEMO DATA" until real roster data lands.

_COMPLIANCE_NOTE = (
    "DEMO DATA — roster is seeded. Real data requires SSO + roster sync (Platform V1.5)."
)
_COMPLIANCE_DUE = "2026-06-30"

# Role → canonical track name shown on the compliance report
_ROLE_TRACK: dict[str, str] = {
    "POS Cashier":                  "New Cashier Onboarding",
    "Frontline Cafeteria Staff":    "New Cashier Onboarding",
    "Cafeteria Manager":            "Site Manager Essentials",
    "District Nutrition Director":  "Eligibility Certification Prep",
}


def _compliance_status(raw_status: str) -> str:
    """Normalise seeded status strings to report-ready labels."""
    return {
        "Completed":    "Complete",
        "In progress":  "In Progress",
        "Not started":  "Not Started",
    }.get(raw_status, raw_status)


def _build_compliance_report(isd: str) -> dict:
    """Build the JSON compliance report for a district from seeded roster data.

    Returns an empty dict when the district ID is unknown so callers can 404.
    """
    d = next((x for x in _DISTRICTS if x["id"] == isd), None)
    if d is None:
        return {}
    roster = _roster_for(d)
    total     = len(roster)
    complete  = sum(1 for r in roster if r["status"] == "Completed")
    in_prog   = sum(1 for r in roster if r["status"] == "In progress")
    not_start = sum(1 for r in roster if r["status"] == "Not started")
    # "Overdue": In Progress with <20 % completion — proxy for seeded data that
    # carries no explicit deadline field.
    overdue   = sum(1 for r in roster if r["status"] == "In progress" and r["progress"] < 20)
    staff_rows = [
        {
            "name":           r["name"],
            # Derive a human-readable site from the email domain; fall back to em dash.
            "site":           (r.get("email", "").split("@")[1].split(".")[0]
                               .replace("-", " ").title() + " Site"
                               if "@" in r.get("email", "") else "\u2014"),
            "role":           r["role"],
            "track":          _ROLE_TRACK.get(r["role"], r.get("assigned", "\u2014")),
            "completion_pct": r["progress"],
            "status":         _compliance_status(r["status"]),
            "last_active":    r["last_active"],
        }
        for r in roster
    ]
    return {
        "district":    d["name"],
        "report_date": datetime.now().strftime("%Y-%m-%d"),
        "due_date":    _COMPLIANCE_DUE,
        "summary": {
            "total":        total,
            "complete":     complete,
            "in_progress":  in_prog,
            "not_started":  not_start,
            "overdue":      overdue,
        },
        "staff": staff_rows,
        "note":  _COMPLIANCE_NOTE,
    }


@app.get("/api/districts/{isd}/compliance-report")
async def compliance_report_json(isd: str):
    """JSON compliance report for a district (BRD FR-RP-03).

    Seeded from the same deterministic roster as /api/roster.
    Returns 404 for unknown district IDs so callers can detect invalid scopes.
    The note field in every response advertises the seeded-data caveat.
    """
    report = _build_compliance_report(isd)
    if not report:
        raise HTTPException(status_code=404, detail=f"District '{isd}' not found.")
    return JSONResponse(content=report)


@app.get("/api/districts/{isd}/compliance-report/pdf")
async def compliance_report_pdf(isd: str):
    """PDF compliance report for a district (BRD FR-RP-03).

    Renders via pdf_export.render_html_to_pdf() — same engine as the guide exporter.
    Stamps a DEMO DATA banner at the top of every page until real roster data lands.
    Returns 404 for unknown district IDs.
    """
    from pdf_export import render_html_to_pdf

    report = _build_compliance_report(isd)
    if not report:
        raise HTTPException(status_code=404, detail=f"District '{isd}' not found.")

    summary = report["summary"]
    rows_html = "".join(
        f"<tr><td>{r['name']}</td><td>{r['site']}</td><td>{r['role']}</td>"
        f"<td>{r['track']}</td><td>{r['completion_pct']}%</td>"
        f"<td>{r['status']}</td><td>{r['last_active']}</td></tr>"
        for r in report["staff"]
    )
    report_html = (
        f"<h1>Compliance Report \u2014 {report['district']}</h1>"
        f"<p><strong>Report date:</strong> {report['report_date']} &nbsp;|&nbsp;"
        f" <strong>Training due:</strong> {report['due_date']}</p>"
        "<h2>Summary</h2>"
        "<table><thead><tr><th>Total staff</th><th>Complete</th><th>In Progress</th>"
        "<th>Not Started</th><th>Overdue</th></tr></thead><tbody><tr>"
        f"<td>{summary['total']}</td><td>{summary['complete']}</td>"
        f"<td>{summary['in_progress']}</td><td>{summary['not_started']}</td>"
        f"<td>{summary['overdue']}</td></tr></tbody></table>"
        "<h2>Staff Detail</h2>"
        "<table><thead><tr><th>Name</th><th>Site</th><th>Role</th><th>Track</th>"
        "<th>Completion</th><th>Status</th><th>Last Active</th></tr></thead>"
        f"<tbody>{rows_html}</tbody></table>"
    )
    banner = "DEMO DATA \u2014 seeded roster. Requires SSO + roster sync (V1.5) for real data."
    try:
        pdf_bytes = render_html_to_pdf(report_html, banner=banner)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"PDF render failed: {exc}") from exc

    filename = f"compliance-report-{isd}-{report['report_date']}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


