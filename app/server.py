"""Jira Brain POC — apply Jira tickets to a guide PDF, review edits inline, get a PDF back.

Internal POC. Single-file Flask app. Templates inline. Subprocess to `claude -p` for the LLM call.

Flow:
  1. POST /                  drop a PDF
  2. GET  /jobs/<id>/module  pick the module (dropdown, pre-filled guess from filename)
  3. POST /jobs/<id>/module  confirm; kicks off PDF→MD + propose edits
  4. GET  /jobs/<id>/processing  polls status until ready
  5. GET  /jobs/<id>/review  the interactive diff (TOC sidebar, approve/reject per edit)
  6. POST /jobs/<id>/decide  body {edit_id, decision: approve|reject}
  7. POST /jobs/<id>/render  apply approved edits, render to PDF
  8. GET  /jobs/<id>/out.pdf download

Per-job scratch lives under app/jobs/<id>/.
"""
from __future__ import annotations

import csv
import difflib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import uuid
from datetime import datetime
from pathlib import Path

from flask import Flask, abort, jsonify, redirect, render_template_string, request, send_file, url_for
from pypdf import PdfReader

APP_DIR = Path(__file__).resolve().parent
REPO = APP_DIR.parent
JOBS_DIR = APP_DIR / "jobs"
JOBS_DIR.mkdir(exist_ok=True)

# Default CSV — POC assumption: the repo already has a Jira CSV at this path.
DEFAULT_CSV = REPO / "raw" / "_imports" / "processed" / "Perseus_Jira_1.csv"

# Modules available in the dropdown — derived from existing guide directory tree.
MODULES = sorted(p.name for p in (REPO / "raw" / "guides" / "markdown" / "SC").iterdir() if p.is_dir())

# CSV column conventions (matches what we discovered in this session).
ALLOWED_RESOLUTIONS = {"Done", "Fixed", "Resolved"}
RN_REQUIRED_TRUE = {"External Only", "External/Internal", "Internal Only", "Yes", "Y", "True"}
MIN_RESOLVED = datetime(2023, 1, 1)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB upload cap

# ───────────────────────── helpers ─────────────────────────


def job_dir(job_id: str) -> Path:
    d = JOBS_DIR / job_id
    if not d.exists():
        abort(404, "unknown job")
    return d


def write_status(job_id: str, phase: str, **extra) -> None:
    """Write current job status — phase + optional fields. Polled by /processing."""
    d = JOBS_DIR / job_id
    d.mkdir(exist_ok=True)
    (d / "status.json").write_text(
        json.dumps({"phase": phase, "updated_at": datetime.now().isoformat(timespec="seconds"), **extra}),
        encoding="utf-8",
    )


def read_status(job_id: str) -> dict:
    p = JOBS_DIR / job_id / "status.json"
    if not p.exists():
        return {"phase": "unknown"}
    return json.loads(p.read_text(encoding="utf-8"))


def guess_module_from_filename(filename: str) -> str | None:
    """Cheap heuristic: match module name as substring (case-insensitive) in the filename."""
    fn = filename.lower().replace("_", " ").replace("-", " ")
    for m in MODULES:
        if m.lower().replace("-", " ") in fn:
            return m
    return None


def parse_date(s: str):
    if not s:
        return None
    for fmt in ("%m/%d/%Y %I:%M %p", "%d/%b/%y %I:%M %p", "%d/%b/%Y %I:%M %p", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(s.strip(), fmt)
        except ValueError:
            continue
    return None


def filter_csv_for_module(csv_path: Path, module: str) -> list[dict]:
    """Apply the same filter we used in the Eligibility run: module + resolution + date + RN-required."""
    csv.field_size_limit(min(sys.maxsize, 2_000_000_000))
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        headers = next(reader)

        def col(name):
            return headers.index(name)

        ix = {
            "summary": col("Summary"),
            "key": col("Issue key"),
            "resolution": col("Resolution"),
            "resolved": col("Resolved"),
            "module": col("Custom field (Module)"),
            "rn": col("Custom field (Release Notes)"),
            "rn_required": col("Custom field (Release Notes Required)"),
            "rn_title": col("Custom field (Release Notes Title)"),
            "desc": col("Description"),
        }
        # AC may be split across multiple columns of the same name
        ac_cols = [i for i, h in enumerate(headers) if h == "Custom field (Acceptance Criteria)"]

        out: list[dict] = []
        for row in reader:
            if len(row) <= max(ix.values()):
                continue
            if row[ix["module"]].strip().lower() != module.lower():
                continue
            if row[ix["resolution"]].strip() not in ALLOWED_RESOLUTIONS:
                continue
            d = parse_date(row[ix["resolved"]])
            if not d or d < MIN_RESOLVED:
                continue
            rn_req = row[ix["rn_required"]].strip()
            ac = " ".join(row[i].strip() for i in ac_cols if i < len(row) and row[i].strip())
            if rn_req not in RN_REQUIRED_TRUE and not ac:
                continue
            out.append({
                "key": row[ix["key"]],
                "summary": row[ix["summary"]],
                "resolved": d.strftime("%Y-%m-%d"),
                "rn_required": rn_req,
                "rn_title": row[ix["rn_title"]],
                "rn": row[ix["rn"]],
                "ac": ac,
            })
        return out


def extract_pdf_to_md(pdf_path: Path) -> str:
    """Cheap text extraction. POC quality — pypdf page text joined with newlines.

    For better fidelity we could route through scripts/guide_text_cleanup.py later.
    """
    reader = PdfReader(str(pdf_path))
    chunks = []
    for page in reader.pages:
        try:
            chunks.append(page.extract_text() or "")
        except Exception:
            chunks.append("")
    return "\n\n".join(chunks).strip() + "\n"


# Generic words that aren't useful as keywords for ticket matching.
_FILTER_STOPWORDS = {
    "the", "and", "for", "with", "from", "into", "this", "that", "your", "you",
    "guide", "quick", "page", "view", "click", "select", "button", "user", "users",
    "module", "function", "tab", "tabs", "section", "field", "fields",
    "add", "new", "use", "see", "set", "all", "any", "etc", "pdf", "html",
    "step", "steps", "type", "name", "icon", "form", "data", "input",
}


def keywords_from_guide(guide_md: str, filename: str) -> set[str]:
    """Pull distinctive tokens from the guide title + H1/H2 + filename to use as
    a coarse ticket-relevance filter. Returns lowercase tokens >2 chars, stopwords removed."""
    headers = re.findall(r"^#{1,2}\s+(.+)$", guide_md, re.MULTILINE)
    title_line = guide_md.lstrip().split("\n", 1)[0] if guide_md else ""
    haystack = " ".join([filename, title_line, *headers]).lower()
    # tokenize on non-word, drop stopwords + short tokens + pure digits + "GUIDE-NNN"-style
    tokens: set[str] = set()
    for w in re.findall(r"[a-z]+", haystack):
        if len(w) > 2 and w not in _FILTER_STOPWORDS:
            tokens.add(w)
    return tokens


def prefilter_tickets(tickets: list[dict], keywords: set[str], min_keep: int = 3) -> list[dict]:
    """Keep tickets whose summary/RN/AC/title mentions any of the guide's keywords.

    If the filter would keep fewer than `min_keep`, fall back to all tickets — better
    to give the LLM too much than to miss a real match because of a thin keyword set.
    """
    if not keywords:
        return tickets
    out: list[dict] = []
    for t in tickets:
        haystack = " ".join([
            t.get("summary", ""), t.get("rn", ""), t.get("ac", ""), t.get("rn_title", "")
        ]).lower()
        if any(kw in haystack for kw in keywords):
            out.append(t)
    if len(out) < min_keep:
        return tickets
    return out


# ───────────────────────── LLM call ─────────────────────────


PROPOSAL_PROMPT = """You are editing a public customer-facing guide (markdown) using shipped Jira tickets as the source of truth for what changed in the product.

Read every rule in CLAUDE.md before drafting. Specifically the anti-hallucination rules and the "Verbatim-citation rule for guide edits". Quote, don't paraphrase. Don't invent specifics. Translate internal codes (BABECL, FRENOSSN, AUTODCNOTIFY, INCCEPVER, etc.) to the on-screen label the user sees; if you can't find the label in source, flag it as an open question and skip the edit.

You will be given:
  - The current guide markdown content
  - A list of filtered Jira tickets (Release Notes + Acceptance Criteria) for the same module

For each ticket that produces a user-visible change to THIS guide, emit a proposed edit. Use the guide's existing voice: short imperatives, bullet brevity, no release-note voice ("we have added", "we've updated"), no AC paste, no internal codes.

Output STRICT JSON only, wrapped in a single fenced ```json``` block. Schema:

{
  "proposed_edits": [
    {
      "id": "e1",
      "ticket": "NXT-12345",
      "resolved": "2024-01-09",
      "reason": "RN: \\"verbatim quote from RN or AC justifying this edit\\"",
      "anchor": "## Section header or unique line the edit follows/replaces",
      "operation": "insert_after" | "replace",
      "before": "exact verbatim substring from the current MD that anchors the edit",
      "after": "the new text that should be there (for replace, this is the full replacement; for insert_after, this is the new text to insert after `before`)"
    }
  ],
  "skipped_tickets": [
    {"ticket": "NXT-XXXXX", "reason": "one-line reason"}
  ],
  "open_notes": [
    "ambiguous things, on-screen labels missing from source, etc."
  ]
}

Rules:
- `before` MUST exist verbatim in the current MD (the backend uses it for string replacement).
- For `insert_after`, the backend will insert `after` immediately after the `before` text.
- For `replace`, the backend will replace `before` with `after`.
- Make `before` unique enough to anchor cleanly. Include surrounding lines if needed.
- Keep `after` concise — match the surrounding voice.
- The output is rendered as styled HTML/PDF, so **use proper markdown hierarchy** in `after`: `##` for section headings, `###` for subsections, numbered lists (`1.`, `2.`) for sequential steps, `-` bullets for non-sequential items, **bold** for UI labels (button names, field labels), `> blockquote` for tips/warnings, and code spans (`code`) for system codes, settings names, or values shown literally. Don't write a wall of prose where a list or heading would read better.
- If no tickets produce a user-visible change to this guide, return an empty `proposed_edits` array and explain in `open_notes`.

CURRENT GUIDE (markdown):
```markdown
{GUIDE_MD}
```

FILTERED TICKETS (JSON):
```json
{TICKETS_JSON}
```

Emit the JSON now. Nothing else."""


def _read_env_file() -> dict:
    """Read app/.env into a dict (POC-grade, no full dotenv parsing).

    Format: one KEY=value per line, # for comments. Values may be quoted.
    Re-read on every subprocess call so edits to .env take effect without restart.
    """
    env_path = APP_DIR / ".env"
    out: dict[str, str] = {}
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s and not s.startswith("#") and "=" in s:
                k, _, v = s.partition("=")
                out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def find_claude_binary() -> str:
    """Resolve the `claude` binary on Windows/macOS/Linux.

    Looks in this order:
      1. CLAUDE_BIN env var (explicit override)
      2. `shutil.which("claude" / "claude.cmd" / "claude.exe")` (on PATH)
      3. Default Claude Desktop install location:
         %APPDATA%/Claude/claude-code/<version>/claude.exe (Windows)
         ~/Library/Application Support/Claude/claude-code/<version>/claude (macOS)

    Raises RuntimeError with setup hints if nothing works.
    """
    explicit = os.environ.get("CLAUDE_BIN")
    if explicit and Path(explicit).exists():
        return explicit
    for name in ("claude", "claude.cmd", "claude.exe"):
        found = shutil.which(name)
        if found:
            return found
    # Windows desktop install
    appdata = os.environ.get("APPDATA")
    if appdata:
        base = Path(appdata) / "Claude" / "claude-code"
        if base.exists():
            candidates = sorted(base.glob("*/claude.exe"), reverse=True)
            if candidates:
                return str(candidates[0])
    # macOS desktop install
    mac_base = Path.home() / "Library" / "Application Support" / "Claude" / "claude-code"
    if mac_base.exists():
        candidates = sorted(mac_base.glob("*/claude"), reverse=True)
        if candidates:
            return str(candidates[0])
    raise RuntimeError(
        "Could not locate the `claude` binary. Either:\n"
        "  - Set CLAUDE_BIN=<path-to-claude-or-claude.exe>\n"
        "  - Add `claude` to your PATH\n"
        "  - Install the Claude Code desktop app at the standard location"
    )


def call_claude_for_proposals(guide_md: str, tickets: list[dict], job_dir: Path) -> dict:
    """Shell out to `claude -p` with the proposal prompt; parse the fenced JSON from stdout.

    Prompt is piped via subprocess `input=` (no temp file — avoids Windows file-lock issues).
    Both prompt and raw response are persisted in the job dir for debugging.
    """
    claude_bin = find_claude_binary()
    prompt = PROPOSAL_PROMPT.replace("{GUIDE_MD}", guide_md).replace(
        "{TICKETS_JSON}", json.dumps(tickets, indent=2)
    )
    (job_dir / "prompt.txt").write_text(prompt, encoding="utf-8")

    env = os.environ.copy()
    env.update(_read_env_file())  # overlay app/.env (e.g., CLAUDE_CODE_OAUTH_TOKEN)
    try:
        result = subprocess.run(
            [claude_bin, "-p", "--model", "haiku", "--output-format=text"],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=600,
            encoding="utf-8",
            env=env,
        )
    except FileNotFoundError as e:
        raise RuntimeError(
            f"Could not execute `{claude_bin}` (FileNotFoundError: {e}). "
            "Run `claude doctor` to verify the install."
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("`claude -p` did not return within 10 minutes. Retry or check API/quota.")

    (job_dir / "llm_response.txt").write_text(result.stdout or "", encoding="utf-8")
    if result.stderr:
        (job_dir / "llm_stderr.txt").write_text(result.stderr, encoding="utf-8")

    # Detect common auth failure signature and surface setup hint.
    auth_hint = (
        "Authentication failed when invoking `claude -p` as a subprocess. The desktop app's "
        "session token isn't shared with subprocess invocations. Run this once in a terminal:\n"
        "    claude setup-token\n"
        "Then retry. (Requires a Claude Code subscription.)"
    )
    blob = (result.stdout or "") + "\n" + (result.stderr or "")
    if result.returncode != 0:
        if "401" in blob or "Invalid authentication" in blob or "Failed to authenticate" in blob:
            raise RuntimeError(auth_hint)
        raise RuntimeError(f"`claude -p` failed (exit {result.returncode}): {result.stderr[:500]}")
    if ("Invalid authentication" in blob) or ("Failed to authenticate" in blob):
        raise RuntimeError(auth_hint)

    out = result.stdout
    m = re.search(r"```json\s*\n(.*?)\n```", out, re.DOTALL)
    if not m:
        raise RuntimeError(
            f"No JSON block in claude output. See app/jobs/{job_dir.name}/llm_response.txt. "
            f"First 500 chars:\n{out[:500]}"
        )
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Bad JSON from claude: {e}. Block:\n{m.group(1)[:500]}")


# ───────────────────────── async processing ─────────────────────────


def process_in_background(job_id: str, module: str) -> None:
    import time
    d = JOBS_DIR / job_id
    timings: dict[str, float] = {}
    try:
        t0 = time.monotonic()
        write_status(job_id, "extracting", message="Converting PDF to markdown…")
        pdf_path = d / "in.pdf"
        md = extract_pdf_to_md(pdf_path)
        (d / "in.md").write_text(md, encoding="utf-8")
        timings["extract_s"] = round(time.monotonic() - t0, 2)

        t0 = time.monotonic()
        write_status(job_id, "matching", message=f"Filtering tickets for {module}…")
        if not DEFAULT_CSV.exists():
            raise RuntimeError(f"CSV not found at {DEFAULT_CSV}")
        all_tickets = filter_csv_for_module(DEFAULT_CSV, module)
        # Narrow further by keyword overlap with the guide so the LLM doesn't have to
        # consider every ticket in the module. Falls back to all tickets if the filter
        # is too aggressive.
        filename = (d / "filename.txt").read_text(encoding="utf-8") if (d / "filename.txt").exists() else ""
        kws = keywords_from_guide(md, filename)
        tickets = prefilter_tickets(all_tickets, kws)
        (d / "tickets.json").write_text(json.dumps(tickets, indent=2), encoding="utf-8")
        (d / "tickets_all.json").write_text(json.dumps(all_tickets, indent=2), encoding="utf-8")
        timings["match_s"] = round(time.monotonic() - t0, 2)

        t0 = time.monotonic()
        msg = f"Asking Haiku to draft edits ({len(tickets)} of {len(all_tickets)} tickets after keyword pre-filter)…"
        write_status(job_id, "proposing", message=msg)
        result = call_claude_for_proposals(md, tickets, d)
        (d / "proposals.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        timings["llm_s"] = round(time.monotonic() - t0, 2)

        write_status(
            job_id,
            "ready",
            message="Review proposed edits.",
            n_edits=len(result.get("proposed_edits", [])),
            n_skipped=len(result.get("skipped_tickets", [])),
            n_tickets_considered=len(tickets),
            n_tickets_total=len(all_tickets),
            timings=timings,
        )
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        (JOBS_DIR / job_id / "error.txt").write_text(tb, encoding="utf-8")
        write_status(job_id, "error", error=str(e), timings=timings)


# ───────────────────────── routes ─────────────────────────


INDEX_HTML = """<!doctype html>
<html><head><meta charset="utf-8"><title>Jira Brain — Apply tickets to a guide</title>
<style>
  body{font-family:ui-sans-serif,system-ui,sans-serif;background:#f7f8fa;color:#1f2933;margin:0;display:grid;place-items:center;min-height:100vh}
  .card{background:#fff;border:1px solid #d9dde4;border-radius:8px;padding:40px;max-width:520px;width:90%;box-shadow:0 1px 3px rgba(0,0,0,.04)}
  h1{margin:0 0 8px;font-size:20px}
  p.sub{margin:0 0 24px;color:#5b6470;font-size:14px}
  .drop{border:2px dashed #b9c0c9;border-radius:8px;padding:48px 16px;text-align:center;color:#5b6470;font-size:14px;cursor:pointer;transition:.15s}
  .drop:hover,.drop.over{border-color:#1b7a3a;color:#1b7a3a;background:#f0fbf3}
  input[type=file]{display:none}
  .meta{font-size:12px;color:#8a8f96;margin-top:18px;text-align:center}
</style></head><body>
<div class="card">
  <h1>Apply Jira tickets to a guide</h1>
  <p class="sub">Drop a SchoolCafé guide PDF. We'll match it against the latest Jira export, propose edits, and let you approve them one by one.</p>
  <form id="f" method="post" enctype="multipart/form-data" action="/upload">
    <label class="drop" id="drop">
      <span id="dropText">Drop a PDF here, or click to browse.</span>
      <input id="file" type="file" name="pdf" accept="application/pdf" required>
    </label>
  </form>
  <div class="meta">Internal POC · runs locally</div>
</div>
<script>
const drop=document.getElementById('drop'),file=document.getElementById('file'),txt=document.getElementById('dropText'),f=document.getElementById('f');
drop.addEventListener('click',()=>file.click());
file.addEventListener('change',()=>{if(file.files.length){txt.textContent='Uploading '+file.files[0].name+'…';f.submit();}});
['dragover','dragenter'].forEach(e=>drop.addEventListener(e,ev=>{ev.preventDefault();drop.classList.add('over');}));
['dragleave','drop'].forEach(e=>drop.addEventListener(e,ev=>{ev.preventDefault();drop.classList.remove('over');}));
drop.addEventListener('drop',ev=>{if(ev.dataTransfer.files.length){file.files=ev.dataTransfer.files;file.dispatchEvent(new Event('change'));}});
</script>
</body></html>"""


MODULE_HTML = """<!doctype html>
<html><head><meta charset="utf-8"><title>Confirm module</title>
<style>
  body{font-family:ui-sans-serif,system-ui,sans-serif;background:#f7f8fa;color:#1f2933;margin:0;display:grid;place-items:center;min-height:100vh}
  .card{background:#fff;border:1px solid #d9dde4;border-radius:8px;padding:32px;max-width:480px;width:90%}
  h1{margin:0 0 6px;font-size:18px}
  p.sub{margin:0 0 20px;color:#5b6470;font-size:13px}
  .fn{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px;color:#5b6470;background:#eef1f5;padding:4px 8px;border-radius:4px;display:inline-block;margin-bottom:18px}
  label{display:block;font-size:12px;color:#5b6470;text-transform:uppercase;letter-spacing:.06em;margin-bottom:6px}
  select{width:100%;padding:10px;font-size:14px;border:1px solid #d9dde4;border-radius:6px;background:#fff;margin-bottom:18px}
  button{background:#1b7a3a;color:#fff;border:0;border-radius:6px;padding:10px 18px;font-size:14px;cursor:pointer}
  button:hover{background:#15602e}
  .row{display:flex;justify-content:space-between;align-items:center;gap:12px}
  .back{color:#5b6470;text-decoration:none;font-size:13px}
</style></head><body>
<div class="card">
  <h1>Which module?</h1>
  <p class="sub">Pick the module this guide belongs to. We'll filter the Jira export to its tickets.</p>
  <div class="fn">{{ filename }}</div>
  <form method="post">
    <label>Module</label>
    <select name="module">
      {% for m in modules %}
        <option value="{{ m }}" {% if m == guess %}selected{% endif %}>{{ m }}</option>
      {% endfor %}
    </select>
    <div class="row">
      <a class="back" href="/">← upload a different file</a>
      <button type="submit">Continue</button>
    </div>
  </form>
</div>
</body></html>"""


PROCESSING_HTML = """<!doctype html>
<html><head><meta charset="utf-8"><title>Processing</title>
<style>
  body{font-family:ui-sans-serif,system-ui,sans-serif;background:#f7f8fa;color:#1f2933;margin:0;display:grid;place-items:center;min-height:100vh}
  .card{background:#fff;border:1px solid #d9dde4;border-radius:8px;padding:40px;max-width:480px;width:90%;text-align:center}
  h1{margin:0 0 14px;font-size:18px}
  .msg{color:#5b6470;font-size:13px;margin:0 0 20px}
  .spinner{display:inline-block;width:28px;height:28px;border:3px solid #eef1f5;border-top-color:#1b7a3a;border-radius:50%;animation:s 1s linear infinite}
  @keyframes s{to{transform:rotate(360deg)}}
  .err{color:#b21f2d;background:#fbd5d8;padding:12px;border-radius:6px;text-align:left;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px;white-space:pre-wrap}
</style></head><body>
<div class="card">
  <div class="spinner" id="sp"></div>
  <h1 id="phase">Starting…</h1>
  <p class="msg" id="msg">Hang tight.</p>
  <div id="err" class="err" style="display:none"></div>
</div>
<script>
const id="{{ job_id }}";
async function tick(){
  const r=await fetch(`/jobs/${id}/status`);
  const j=await r.json();
  document.getElementById('phase').textContent=({extracting:'Extracting PDF',matching:'Filtering tickets',proposing:'Drafting edits',ready:'Ready',error:'Error'})[j.phase]||j.phase;
  document.getElementById('msg').textContent=j.message||'';
  if(j.phase==='ready'){window.location='/jobs/'+id+'/review';return;}
  if(j.phase==='error'){document.getElementById('sp').style.display='none';document.getElementById('err').style.display='block';document.getElementById('err').textContent=j.error||'unknown error';return;}
  setTimeout(tick,1500);
}
tick();
</script>
</body></html>"""


@app.route("/")
def index():
    return INDEX_HTML


@app.route("/upload", methods=["POST"])
def upload():
    f = request.files.get("pdf")
    if not f or not f.filename:
        abort(400, "no file")
    job_id = uuid.uuid4().hex[:12]
    d = JOBS_DIR / job_id
    d.mkdir()
    pdf_path = d / "in.pdf"
    f.save(pdf_path)
    (d / "filename.txt").write_text(f.filename, encoding="utf-8")
    return redirect(url_for("module", job_id=job_id))


@app.route("/jobs/<job_id>/module", methods=["GET", "POST"])
def module(job_id: str):
    d = job_dir(job_id)
    filename = (d / "filename.txt").read_text(encoding="utf-8") if (d / "filename.txt").exists() else ""
    if request.method == "POST":
        mod = request.form.get("module", "")
        if mod not in MODULES:
            abort(400, "unknown module")
        (d / "module.txt").write_text(mod, encoding="utf-8")
        write_status(job_id, "queued", message="Starting…")
        threading.Thread(target=process_in_background, args=(job_id, mod), daemon=True).start()
        return redirect(url_for("processing", job_id=job_id))
    return render_template_string(
        MODULE_HTML, filename=filename, modules=MODULES, guess=guess_module_from_filename(filename)
    )


@app.route("/jobs/<job_id>/processing")
def processing(job_id: str):
    job_dir(job_id)
    return render_template_string(PROCESSING_HTML, job_id=job_id)


@app.route("/jobs/<job_id>/status")
def status(job_id: str):
    job_dir(job_id)
    return jsonify(read_status(job_id))


# Review + decide + render endpoints are implemented in review.py for readability.
from review import register_review_routes  # noqa: E402

register_review_routes(app, JOBS_DIR, REPO)


if __name__ == "__main__":
    app.run(debug=True, port=5050)
