"""FastAPI server: upload transcript -> generate HTML resource -> publish -> library.

Routes:
    GET  /                              — single-page UI (Author + Library tabs)
    POST /transcripts                   — upload .md/.txt, returns transcript_id
    GET  /transcripts                   — list uploaded transcripts
    GET  /transcripts/{id}              — fetch transcript text
    GET  /generate                      — SSE stream of agent messages (query params: transcript_id, module, template). On completion, persists a draft resource and emits final {resource_id} event.
    GET  /resources                     — list resources (drafts + published), filterable by module/template/status
    GET  /resources/{id}                — fetch resource HTML
    POST /resources/{id}/publish        - move draft -> published
    GET  /resources/{id}/pdf            — TODO V1.5: PDF export

Run:
    uvicorn app:app --host 127.0.0.1 --port 8000
"""
import asyncio
import json
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from sse_starlette.sse import EventSourceResponse

from claude_agent_sdk import (
    AssistantMessage,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ThinkingBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
    query,
)

from agent_sdk import (
    VALID_MODULES,
    VALID_TEMPLATES,
    build_options,
    build_user_prompt,
)
from evaluator_sdk import build_evaluator_options, build_evaluator_prompt

load_dotenv()

BASE = Path(__file__).parent
TRANSCRIPTS = BASE / "raw" / "transcripts"
TRANSCRIPT_META = BASE / "raw" / "transcripts" / "metadata"
DRAFTS = BASE / "drafts"
PUBLISHED = BASE / "published"
PUB_META = BASE / "published" / "metadata"
LOGS = BASE / "logs"
STATIC = BASE / "static"

for d in (TRANSCRIPTS, TRANSCRIPT_META, DRAFTS, PUBLISHED, PUB_META, LOGS, STATIC):
    d.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _slug(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9\-]+", "-", text).strip("-").lower()
    return s[:48] or "item"


def _now_id() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def _resource_id(module: str, template: str) -> str:
    return f"{_now_id()}-{_slug(module)}-{template}-{uuid.uuid4().hex[:6]}"


def _read_meta(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _list_resources_in(dir_: Path, status: str) -> list[dict]:
    out: list[dict] = []
    meta_dir = PUB_META if status == "published" else dir_
    for html in dir_.glob("*.html"):
        rid = html.stem
        meta = _read_meta(meta_dir / f"{rid}.json") or {}
        if status == "draft":
            eval_data = _read_meta(_eval_path(rid)) or {}
            verdict = str(eval_data.get("verdict") or "").strip().lower()
            if verdict:
                meta["evaluator_verdict"] = verdict
                meta["evaluator_summary"] = eval_data.get("summary")
                meta["evaluated_at"] = eval_data.get("evaluated_at")
            else:
                meta.setdefault("evaluator_verdict", None)
        meta.setdefault("id", rid)
        meta.setdefault("status", status)
        meta.setdefault("path", str(html.relative_to(BASE)))
        out.append(meta)
    return out


def _resolve_resource(rid: str) -> tuple[Path, Path, str] | None:
    """Return (html_path, meta_path, status) or None."""
    for d, meta_dir, status in (
        (PUBLISHED, PUB_META, "published"),
        (DRAFTS, DRAFTS, "draft"),
    ):
        html = d / f"{rid}.html"
        if html.exists():
            return html, meta_dir / f"{rid}.json", status
    return None


# Strip inline <!-- Source: ... --> comments for the "view" pass.
SOURCE_COMMENT_RE = re.compile(r"<!--\s*Source:[\s\S]*?-->")


def _strip_source_comments(html: str) -> str:
    return SOURCE_COMMENT_RE.sub("", html)


def _parse_eval_json(text: str) -> dict | None:
    """Extract a JSON object from the evaluator's final assistant message.
    Strips markdown fences and surrounding prose."""
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


def _eval_path(rid: str) -> Path:
    """Where the evaluation JSON for a resource lives. Stays next to the draft."""
    return DRAFTS / f"{rid}.eval.json"


# ─────────────────────────────────────────────────────────────────────────────
# App
# ─────────────────────────────────────────────────────────────────────────────


app = FastAPI(title="Learning Studio")


@app.get("/", response_class=HTMLResponse)
async def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/config")
async def config():
    return {
        "modules": list(VALID_MODULES),
        "templates": list(VALID_TEMPLATES),
    }


# ── Transcripts ─────────────────────────────────────────────────────────────


@app.post("/transcripts")
async def upload_transcript(file: UploadFile, module: str | None = None):
    if not file.filename:
        raise HTTPException(400, "filename missing")
    suffix = Path(file.filename).suffix.lower()
    if suffix not in (".md", ".txt"):
        raise HTTPException(400, "only .md and .txt accepted in V1")
    if module and module not in VALID_MODULES:
        raise HTTPException(400, f"unknown module: {module}")

    body = await file.read()
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError:
        text = body.decode("utf-8", errors="replace")

    transcript_id = f"{_now_id()}-{_slug(module or 'unscoped')}-{_slug(file.filename)}"
    transcript_path = TRANSCRIPTS / f"{transcript_id}.md"
    transcript_path.write_text(text, encoding="utf-8")

    meta = {
        "id": transcript_id,
        "filename": file.filename,
        "module": module,
        "uploaded_at": datetime.now().isoformat(timespec="seconds"),
        "char_count": len(text),
        "path": str(transcript_path.relative_to(BASE)),
    }
    (TRANSCRIPT_META / f"{transcript_id}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8"
    )
    return meta


@app.get("/transcripts")
async def list_transcripts():
    out = []
    for meta_file in sorted(TRANSCRIPT_META.glob("*.json"), reverse=True):
        m = _read_meta(meta_file)
        if m:
            out.append(m)
    return out


@app.get("/transcripts/{tid}")
async def get_transcript(tid: str):
    meta = _read_meta(TRANSCRIPT_META / f"{tid}.json")
    if not meta:
        raise HTTPException(404, "transcript not found")
    path = TRANSCRIPTS / f"{tid}.md"
    return {**meta, "text": path.read_text(encoding="utf-8")}


# ── Generation (SSE) ────────────────────────────────────────────────────────


def _sse_event(kind: str, payload) -> dict:
    return {"event": kind, "data": json.dumps(payload, ensure_ascii=False)}


async def _stream_generation(transcript_id: str, module: str, template: str):
    meta = _read_meta(TRANSCRIPT_META / f"{transcript_id}.json")
    if not meta:
        yield _sse_event("error", {"message": f"transcript {transcript_id} not found"})
        return
    transcript_path = (BASE / meta["path"]).resolve()

    rid = _resource_id(module, template)
    log_path = LOGS / f"{rid}.jsonl"

    def log(event_kind, payload):
        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"k": event_kind, "p": payload}, ensure_ascii=False) + "\n")

    yield _sse_event("start", {
        "resource_id": rid,
        "transcript_id": transcript_id,
        "module": module,
        "template": template,
    })

    try:
        options = build_options(template)
    except ValueError as e:
        yield _sse_event("error", {"message": str(e)})
        return

    prompt = build_user_prompt(str(transcript_path), module, template)
    final_text_parts: list[str] = []
    result_meta: dict = {}

    try:
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, SystemMessage):
                payload = {"subtype": getattr(message, "subtype", "?")}
                yield _sse_event("system", payload)
                log("system", payload)
            elif isinstance(message, AssistantMessage):
                for block in (message.content or []):
                    if isinstance(block, TextBlock):
                        final_text_parts.append(block.text)
                        yield _sse_event("text", {"text": block.text})
                        log("text", {"text": block.text[:500]})
                    elif isinstance(block, ThinkingBlock):
                        yield _sse_event("thinking", {"text": block.thinking})
                    elif isinstance(block, ToolUseBlock):
                        payload = {"name": block.name, "input": block.input, "id": block.id}
                        yield _sse_event("tool_call", payload)
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
                        yield _sse_event("tool_result", {
                            "tool_use_id": block.tool_use_id,
                            "text": text,
                        })
                        log("tool_result", {"len": len(text), "preview": text[:200]})
            elif isinstance(message, ResultMessage):
                result_meta = {
                    "cost_usd": getattr(message, "total_cost_usd", None),
                    "num_turns": getattr(message, "num_turns", None),
                    "duration_ms": getattr(message, "duration_ms", None),
                }
                yield _sse_event("result", result_meta)
                log("result", result_meta)
    except Exception as e:
        yield _sse_event("error", {"message": f"agent run failed: {e}"})
        log("error", {"message": str(e)})
        return

    html_text = "\n".join(final_text_parts).strip()
    # Crude extraction: if the model wrapped output in ```html ... ```, unwrap it
    fence = re.search(r"```(?:html)?\s*([\s\S]*?)```", html_text)
    if fence:
        html_text = fence.group(1).strip()
    # Strip planning/reasoning preamble — keep from the first <h1> or <h2>
    h_match = re.search(r"<h[1-2]\b", html_text, flags=re.I)
    if h_match:
        html_text = html_text[h_match.start():].strip()

    draft_html = DRAFTS / f"{rid}.html"
    draft_html.write_text(html_text, encoding="utf-8")

    draft_meta = {
        "id": rid,
        "status": "draft",
        "module": module,
        "template": template,
        "transcript_id": transcript_id,
        "transcript_filename": meta.get("filename"),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        **result_meta,
    }
    (DRAFTS / f"{rid}.json").write_text(json.dumps(draft_meta, indent=2), encoding="utf-8")

    yield _sse_event("done", {"resource_id": rid, "status": "draft", **draft_meta})


@app.get("/generate")
async def generate(
    transcript_id: str = Query(...),
    module: str = Query(...),
    template: str = Query(...),
):
    if module not in VALID_MODULES:
        raise HTTPException(400, f"unknown module: {module}")
    if template not in VALID_TEMPLATES:
        raise HTTPException(400, f"unknown template: {template}")
    return EventSourceResponse(_stream_generation(transcript_id, module, template))


# ── Resources (library) ─────────────────────────────────────────────────────


@app.get("/resources")
async def list_resources(
    module: str | None = None,
    template: str | None = None,
    status: str | None = None,
):
    out = _list_resources_in(DRAFTS, "draft") + _list_resources_in(PUBLISHED, "published")
    if module:
        out = [r for r in out if r.get("module") == module]
    if template:
        out = [r for r in out if r.get("template") == template]
    if status:
        out = [r for r in out if r.get("status") == status]
    out.sort(key=lambda r: r.get("created_at", ""), reverse=True)
    return out


@app.get("/resources/{rid}")
async def get_resource(rid: str, view: str = "draft"):
    """view='draft' shows raw HTML with <!-- Source: --> comments preserved.
    view='clean' strips them (publish preview)."""
    resolved = _resolve_resource(rid)
    if not resolved:
        raise HTTPException(404, "resource not found")
    html_path, meta_path, status = resolved
    html = html_path.read_text(encoding="utf-8")
    if view == "clean":
        html = _strip_source_comments(html)
    meta = _read_meta(meta_path) or {"id": rid, "status": status}
    return JSONResponse({"meta": meta, "html": html})


# ── Evaluator (Task 5) ──────────────────────────────────────────────────────


async def _stream_evaluation(rid: str, draft_html: str, transcript_text: str, meta: dict):
    yield _sse_event("eval_start", {"resource_id": rid})

    options = build_evaluator_options()
    prompt = build_evaluator_prompt(
        draft_html=_strip_source_comments(draft_html),  # eval sees clean HTML; comments are checked separately by us
        transcript_text=transcript_text,
        template=meta.get("template", "?"),
        module=meta.get("module", "?"),
    )
    # We want the evaluator to see <!-- Source: --> comments though — give it both
    prompt = (
        prompt
        + "\n\n=== RAW DRAFT WITH SOURCE COMMENTS (use for citation spot-check) ===\n"
        + draft_html[:20000]
    )

    final_text_parts: list[str] = []
    try:
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, SystemMessage):
                yield _sse_event("eval_system", {"subtype": getattr(message, "subtype", "?")})
            elif isinstance(message, AssistantMessage):
                for block in (message.content or []):
                    if isinstance(block, TextBlock):
                        final_text_parts.append(block.text)
                    elif isinstance(block, ToolUseBlock):
                        yield _sse_event("eval_tool_call",
                                         {"name": block.name, "input": block.input, "id": block.id})
            elif isinstance(message, UserMessage):
                for block in (message.content or []):
                    if isinstance(block, ToolResultBlock):
                        content = block.content
                        if isinstance(content, list):
                            text = " ".join(c.get("text", "") if isinstance(c, dict) else str(c)
                                            for c in content)
                        else:
                            text = str(content)
                        yield _sse_event("eval_tool_result",
                                         {"tool_use_id": block.tool_use_id, "text": text})
            elif isinstance(message, ResultMessage):
                yield _sse_event("eval_result", {
                    "cost_usd": getattr(message, "total_cost_usd", None),
                    "num_turns": getattr(message, "num_turns", None),
                    "duration_ms": getattr(message, "duration_ms", None),
                })
    except Exception as e:
        yield _sse_event("eval_error", {"message": f"evaluator failed: {e}"})
        return

    raw = "\n".join(final_text_parts).strip()
    eval_data = _parse_eval_json(raw)
    if eval_data is None:
        eval_data = {
            "verdict": "error",
            "summary": "Could not parse evaluator output as JSON.",
            "checks": [],
            "raw_excerpt": raw[:600],
        }

    eval_data["resource_id"] = rid
    eval_data["evaluated_at"] = datetime.now().isoformat(timespec="seconds")
    _eval_path(rid).write_text(json.dumps(eval_data, indent=2), encoding="utf-8")

    yield _sse_event("eval_done", eval_data)


@app.get("/resources/{rid}/evaluate")
async def evaluate_resource(rid: str):
    """Run the Evaluator on a draft. SSE stream + writes drafts/<rid>.eval.json."""
    resolved = _resolve_resource(rid)
    if not resolved:
        raise HTTPException(404, "resource not found")
    html_path, meta_path, _status = resolved

    meta = _read_meta(meta_path) or {}
    transcript_id = meta.get("transcript_id")
    if not transcript_id:
        raise HTTPException(400, "resource has no source transcript_id")

    t_meta = _read_meta(TRANSCRIPT_META / f"{transcript_id}.json")
    if not t_meta:
        raise HTTPException(404, "source transcript metadata missing")

    transcript_path = (BASE / t_meta["path"]).resolve()
    if not transcript_path.exists():
        raise HTTPException(404, "source transcript file missing")

    transcript_text = transcript_path.read_text(encoding="utf-8")
    draft_html = html_path.read_text(encoding="utf-8")

    return EventSourceResponse(_stream_evaluation(rid, draft_html, transcript_text, meta))


@app.get("/resources/{rid}/evaluation")
async def get_evaluation(rid: str):
    """Return the stored evaluator JSON, or 404 if it hasn't run yet."""
    p = _eval_path(rid)
    if not p.exists():
        raise HTTPException(404, "no evaluation yet — call /resources/{rid}/evaluate first")
    return JSONResponse(_read_meta(p))


@app.get("/logs/{rid}")
async def get_log(rid: str, format: str = "json"):
    """Return the per-job server-side log (JSONL trace written during generation).

    format=json (default): parsed list[{k, p}] for UI consumption
    format=raw: plain JSONL text for download
    """
    log_path = LOGS / f"{rid}.jsonl"
    if not log_path.exists():
        raise HTTPException(404, f"no log for resource_id={rid}")
    if format == "raw":
        return FileResponse(log_path, media_type="text/plain", filename=f"{rid}.jsonl")
    events = []
    with log_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                events.append({"k": "parse_error", "p": {"raw": line[:200]}})
    return JSONResponse({"resource_id": rid, "event_count": len(events), "events": events})


@app.post("/resources/{rid}/publish")
async def publish_resource(rid: str, override: bool = False):
    """Publish a draft. **Hard-gated by Evaluator verdict.**
    - verdict=pass  → publish proceeds
    - verdict=warn  → publish proceeds (caller is expected to have reviewed)
    - verdict=fail  → 409 unless override=true is explicitly passed
    - no verdict    → 409 (must run evaluator first)
    - verdict=error → 409 (evaluator ran but couldn't parse; re-run)
    """
    src_html = DRAFTS / f"{rid}.html"
    src_meta = DRAFTS / f"{rid}.json"
    if not src_html.exists():
        raise HTTPException(404, "draft not found")

    # ─ Hard-gate on Evaluator verdict ─
    eval_data = _read_meta(_eval_path(rid))
    if not eval_data:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "no_evaluation",
                "message": "No evaluator verdict on file. Run /resources/{rid}/evaluate first.",
            },
        )
    verdict = str(eval_data.get("verdict") or "").strip().lower()
    if verdict == "fail" and not override:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "evaluator_fail",
                "message": "Evaluator returned FAIL — publish blocked.",
                "verdict": verdict,
                "summary": eval_data.get("summary"),
                "checks": eval_data.get("checks"),
                "hint": "Pass ?override=true to publish anyway (explicit human decision).",
            },
        )
    if verdict not in ("pass", "warn") and not (verdict == "fail" and override):
        raise HTTPException(
            status_code=409,
            detail={
                "error": "evaluator_did_not_complete",
                "message": "Evaluator did not produce a publishable verdict.",
                "verdict": verdict or None,
                "summary": eval_data.get("summary"),
                "hint": "Re-run /resources/{rid}/evaluate.",
            },
        )

    # ─ Proceed with publish ─
    raw_html = src_html.read_text(encoding="utf-8")
    cleaned = _strip_source_comments(raw_html)
    dst_html = PUBLISHED / f"{rid}.html"
    dst_html.write_text(cleaned, encoding="utf-8")

    meta = _read_meta(src_meta) or {}
    meta.update({
        "id": rid,
        "status": "published",
        "published_at": datetime.now().isoformat(timespec="seconds"),
        "draft_html_archived": str(src_html.relative_to(BASE)),
        "evaluator_verdict": verdict,
        "evaluator_summary": eval_data.get("summary"),
        "evaluator_override": bool(override and verdict == "fail"),
    })
    (PUB_META / f"{rid}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8"
    )
    # Leave draft files in place as an audit trail.
    return meta


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)
