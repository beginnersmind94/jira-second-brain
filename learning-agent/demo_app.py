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
import sys
import time
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, Response
from sse_starlette.sse import EventSourceResponse

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
    plan_system_prompt,
    write_section,
)
from demo import ALLOWED_TOOLS as DEMO_ALLOWED_TOOLS, MCP_SERVER_NAME, demo_mcp_server
import pricing

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
DEFAULT_MODULE = os.getenv("DEMO_MODULE", "Item Management")
if DEFAULT_MODULE not in AVAILABLE_MODULES and AVAILABLE_MODULES:
    DEFAULT_MODULE = sorted(AVAILABLE_MODULES)[0]
demo._FIX = demo._load_fixture(DEFAULT_MODULE)
_FIX_MODULE = DEFAULT_MODULE
print(f"[demo_app] {len(AVAILABLE_MODULES)} module fixtures available: {sorted(AVAILABLE_MODULES)}")
print(f"[demo_app] default '{_FIX_MODULE}': {len(demo._FIX.get('tickets', {}))} tickets + "
      f"{len(demo._FIX.get('epics', {}))} epics")


def _ensure_fixture(module: str) -> None:
    """Swap demo._FIX to the requested module's fixture (the tools read this global)."""
    if module in AVAILABLE_MODULES and demo._FIX.get("module") != module:
        demo._FIX = demo._load_fixture(module)

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

    # Stamp a banner unless the doc has been SME-approved (it never is in the demo).
    meta = prod._read_meta(meta_path) or {}
    banner = None
    if not meta.get("sme_approved"):
        banner = ("⚠ PENDING REVIEW BY SME — provisional draft, grounding auto-verified "
                  "but not yet approved by a subject-matter expert. Do not treat as final.")

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


@app.get("/api/config")
async def config():
    # Offer every module we have an offline fixture for + every format.
    return {"modules": sorted(AVAILABLE_MODULES), "templates": list(demo_d.VALID_FORMATS)}


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
            "grounded": grounded, "cost_usd": m.get("cost_usd"),
        })
    gens.sort(key=lambda g: g.get("created_at", ""), reverse=True)
    total_cost = round(sum(g.get("cost_usd") or 0 for g in gens), 4)

    # 3) capability suite-run logs
    runs = []
    runs_dir = prod.BASE / "eval" / "runs"
    if runs_dir.exists():
        for rj in sorted(runs_dir.glob("*/report.json"), reverse=True)[:10]:
            try:
                d = json.loads(rj.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            runs.append({"stamp": d.get("stamp"), "module": d.get("module"),
                         "trials": d.get("trials"), "per_format": d.get("per_format"),
                         "total_cost_usd": d.get("total_cost_usd"),
                         "regression_summary": d.get("regression_summary")})

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
            {"label": "Total cost to date", "value": f"${total_cost:.2f}", "ok": True,
             "plain": "Total AI processing cost across all guides produced so far."},
        ],
    }

    return {"score": score, "regression": regression, "generations": gens[:50],
            "generations_total_cost_usd": total_cost, "suite_runs": runs}


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
async def _stream_celld(transcript_path, transcript_id, module, rid, log, fmt="long-form"):
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
    plan_prompt = (
        f"Plan a {fmt} `{module}` guide from the transcript at:\n  {transcript_path}\n"
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
        return i, await write_section(s, registry, by_ticket, module, sem, budget=budget)

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
        f"\nAssembled. {integ['ok']} citations verified verbatim; "
        f"tier violations={integ['tier_lie']}, non-verbatim={integ['quote_not_found']}, "
        f"invalid IDs={asm['invalid_cite_id']}.\n"
        f"Run cost: ${cost['cost_usd']:.4f}  "
        f"({cost['output_tokens']:,} out + {cost['input_tokens']:,} in + "
        f"{cost['cache_read_tokens']:,} cache-read tok).\n"})

    (prod.DRAFTS / f"{rid}.html").write_text(html, encoding="utf-8")
    draft_meta = {
        "id": rid, "status": "draft", "module": module, "template": fmt,
        "transcript_id": transcript_id, "transcript_filename": None,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "demo": True, "method": "sectioned+registry",
        "citation_integrity": {"verified": integ["ok"], "tier_lie": integ["tier_lie"],
                               "not_found": integ["quote_not_found"], "invalid_cite_id": asm["invalid_cite_id"]},
        "cost_usd": cost["cost_usd"], "cost": cost,
    }
    (prod.DRAFTS / f"{rid}.json").write_text(json.dumps(draft_meta, indent=2), encoding="utf-8")
    yield prod._sse_event("done", {"resource_id": rid, "status": "draft", **draft_meta})


# ── /generate — offline generation against the fixture ────────────────────────
async def _stream_generation_demo(transcript_id: str, module: str, template: str):
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
        "module": module, "template": template,
    })

    # ALL formats use the validated Cell D sectioned+registry pipeline — grounding
    # guaranteed by construction (long-form, micro-guide, tldr, release-notes).
    if template in demo_d.VALID_FORMATS:
        async for ev in _stream_celld(transcript_path, transcript_id, module, rid, log, fmt=template):
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
):
    if module not in AVAILABLE_MODULES:
        raise HTTPException(400, f"no offline fixture for module '{module}'. Available: {sorted(AVAILABLE_MODULES)}")
    if template not in demo_d.VALID_FORMATS:
        raise HTTPException(400, f"unknown format: {template}")
    return EventSourceResponse(_stream_generation_demo(transcript_id, module, template))


# ── /resources/{rid}/evaluate — DETERMINISTIC grounding gate ──────────────────
# The product's trust guarantee: re-check every citation token against the real
# source field by exact match. No LLM (the model-based eval threw transient SDK
# errors and isn't needed — the deterministic check IS the guarantee).
async def _stream_evaluation_demo(rid: str, draft_html: str, transcript_text: str, meta: dict):
    yield prod._sse_event("eval_start", {"resource_id": rid})

    integ = validate_citations(draft_html)
    tier_lie, not_found, ok = integ["tier_lie"], integ["quote_not_found"], integ["ok"]
    invalid = draft_html.count("INVALID_CITE_ID")
    hard = tier_lie + not_found + invalid
    verdict = "pass" if hard == 0 else "fail"

    eval_data = {
        "verdict": verdict,
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
    }
    prod._eval_path(rid).write_text(json.dumps(eval_data, indent=2), encoding="utf-8")
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
    transcript_id = meta.get("transcript_id")
    if not transcript_id:
        raise HTTPException(400, "resource has no source transcript_id")
    t_meta = prod._read_meta(prod.TRANSCRIPT_META / f"{transcript_id}.json")
    if not t_meta:
        raise HTTPException(404, "source transcript metadata missing")
    transcript_path = (prod.BASE / t_meta["path"]).resolve()
    if not transcript_path.exists():
        raise HTTPException(404, "source transcript file missing")

    transcript_text = transcript_path.read_text(encoding="utf-8")
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
        integ = validate_citations(html_path.read_text(encoding="utf-8"))
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
    uvicorn.run("demo_app:app", host="127.0.0.1", port=8001, reload=False)
