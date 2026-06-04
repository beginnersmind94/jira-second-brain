"""Review UI + decide/render endpoints. Split out of server.py for readability."""
from __future__ import annotations

import difflib
import html
import json
import re
from pathlib import Path

from flask import abort, jsonify, redirect, render_template_string, request, send_file, url_for


REVIEW_HTML = """<!doctype html>
<html><head><meta charset="utf-8"><title>Review proposed edits</title>
<style>
body{font-family:ui-sans-serif,system-ui,sans-serif;background:#f7f8fa;color:#1f2933;margin:0}
.layout{display:grid;grid-template-columns:300px 1fr;min-height:100vh}
nav.toc{position:sticky;top:0;align-self:start;height:100vh;overflow-y:auto;background:#fff;border-right:1px solid #d9dde4;padding:18px 14px}
nav.toc .title{font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:#5b6470;margin:0 0 12px}
nav.toc .sub{font-size:12px;color:#5b6470;margin:0 0 14px;line-height:1.5}
nav.toc ul{list-style:none;padding:0;margin:0}
nav.toc li{margin:4px 0}
nav.toc a{display:flex;justify-content:space-between;align-items:center;gap:8px;padding:8px;border-radius:5px;font-size:12px;color:#1f2933;text-decoration:none}
nav.toc a:hover{background:#eef1f5}
nav.toc a .ticket{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:11px;color:#6b7280}
.badge{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:10px;padding:2px 6px;border-radius:10px;background:#eef1f5;color:#5b6470}
.badge.approved{background:#d4f5dd;color:#1b7a3a}
.badge.rejected{background:#fbd5d8;color:#b21f2d}
main{padding:28px 32px 120px;max-width:1100px}
.page-head{padding:0 0 18px;border-bottom:1px solid #e3e7ec;margin-bottom:24px}
.page-head h1{margin:0 0 6px;font-size:20px}
.page-head .meta{font-size:13px;color:#5b6470}
section.edit{background:#fff;border:1px solid #d9dde4;border-radius:8px;margin:0 0 22px;overflow:hidden;scroll-margin-top:16px}
section.edit header{padding:14px 20px;background:#fafbfc;border-bottom:1px solid #e3e7ec}
section.edit header .row{display:flex;align-items:center;justify-content:space-between;gap:12px}
section.edit header .id{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px;color:#5b6470}
section.edit header h2{margin:6px 0 0;font-size:14px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
section.edit .reason{padding:10px 20px;font-size:12px;color:#5b6470;background:#fffdf6;border-bottom:1px solid #f5ecd6}
section.edit .diff-table{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12.5px;border-collapse:collapse;width:100%}
section.edit .diff-table td{padding:4px 10px;vertical-align:top}
section.edit .diff-table .ln{background:#eef1f5;color:#6b7280;text-align:right;width:42px;font-size:11px}
.diff_add{background:#d4f5dd}
.diff_sub{background:#fbd5d8}
.diff_chg{background:#fff3c4}
.actions{padding:14px 20px;display:flex;gap:10px;border-top:1px solid #e3e7ec;background:#fafbfc}
.btn{border:0;border-radius:6px;padding:8px 14px;font-size:13px;cursor:pointer;font-weight:500}
.btn-approve{background:#1b7a3a;color:#fff}.btn-approve:hover{background:#15602e}
.btn-reject{background:#fff;color:#b21f2d;border:1px solid #fbd5d8}.btn-reject:hover{background:#fbd5d8}
.btn-secondary{background:#fff;color:#5b6470;border:1px solid #d9dde4}
.actions .status{margin-left:auto;font-size:12px;color:#5b6470;align-self:center}
.actions .status.approved{color:#1b7a3a;font-weight:600}
.actions .status.rejected{color:#b21f2d;font-weight:600}
.aside{margin:30px 0 0;padding:0;background:#fff;border:1px solid #d9dde4;border-radius:8px;overflow:hidden}
.aside summary{padding:14px 20px;cursor:pointer;font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:#5b6470;font-weight:600;list-style:none;display:flex;justify-content:space-between;align-items:center}
.aside summary::-webkit-details-marker{display:none}
.aside summary::after{content:'+';font-size:18px;color:#8a8f96;font-weight:400}
.aside details[open] summary::after{content:'−'}
.aside summary:hover{background:#fafbfc}
.aside .body{padding:0 20px 16px;border-top:1px solid #eef1f5}
.aside ul{margin:12px 0 0;padding-left:18px;font-size:13px;color:#1f2933;max-height:340px;overflow-y:auto}
.aside li{margin:4px 0;line-height:1.45}
.empty-state{text-align:center;padding:48px 24px;background:#fff;border:1px solid #d9dde4;border-radius:8px;margin:0 0 24px}
.empty-state .icon{font-size:32px;line-height:1;color:#8a8f96;margin:0 0 12px}
.empty-state h2{margin:0 0 8px;font-size:18px;color:#1f2933}
.empty-state p{margin:0 auto;font-size:14px;color:#5b6470;max-width:520px;line-height:1.6}
.footer-bar{position:fixed;bottom:0;left:300px;right:0;background:#fff;border-top:1px solid #d9dde4;padding:14px 32px;display:flex;align-items:center;justify-content:space-between;gap:12px}
.footer-bar .count{font-size:13px;color:#5b6470}
.footer-bar .count strong{color:#1f2933}
.btn-render{background:#1b7a3a;color:#fff;border:0;border-radius:6px;padding:10px 20px;font-size:14px;cursor:pointer;font-weight:600}
.btn-render:disabled{background:#b9c0c9;cursor:not-allowed}
.btn-render:hover:not(:disabled){background:#15602e}
.modal-bg{position:fixed;inset:0;background:rgba(20,25,35,.45);display:none;align-items:center;justify-content:center;z-index:50}
.modal-bg.show{display:flex}
.modal{background:#fff;border-radius:8px;padding:24px 26px;max-width:520px;width:90%;box-shadow:0 10px 40px rgba(0,0,0,.18)}
.modal h2{margin:0 0 8px;font-size:18px}
.modal .summary{font-size:14px;color:#5b6470;margin:0 0 14px}
.modal .skipped{background:#fbf5d6;border:1px solid #f5e7a1;border-radius:6px;padding:12px 14px;margin:0 0 16px}
.modal .skipped h3{margin:0 0 6px;font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:#8b6914}
.modal .skipped ul{margin:0;padding-left:18px;font-size:13px;color:#5b3e0a}
.modal .skipped li{margin:3px 0}
.modal .skipped li strong{font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.modal .row{display:flex;gap:8px;justify-content:flex-end;flex-wrap:wrap}
.modal .btn-primary{background:#1b7a3a;color:#fff;border:0;border-radius:6px;padding:10px 16px;font-size:13.5px;cursor:pointer;text-decoration:none;font-weight:600;display:inline-block}
.modal .btn-primary:hover{background:#15602e}
.modal .btn-secondary{background:#fff;color:#1f2933;border:1px solid #d9dde4;border-radius:6px;padding:10px 14px;font-size:13px;cursor:pointer;text-decoration:none;font-weight:500;display:inline-block}
.modal .btn-secondary:hover{background:#f3f5f8;border-color:#c4cad2}
.modal .btn-close{background:#fff;color:#5b6470;border:1px solid #d9dde4;border-radius:6px;padding:10px 14px;font-size:13px;cursor:pointer}
.modal .pdf-hint{margin:10px 0 14px;padding:8px 12px;background:#f5f7fa;border-radius:6px;font-size:12px;color:#5b6470;line-height:1.5}
.modal .pdf-hint strong{color:#1f2933;font-weight:600}
@media (max-width:900px){.layout{grid-template-columns:1fr}.footer-bar{left:0}}
</style></head><body>
<div class="layout">
<nav class="toc">
  <p class="title">Proposed edits</p>
  <p class="sub">{{ n_edits }} edit{{ '' if n_edits == 1 else 's' }} drafted from {{ n_tickets }} candidate ticket{{ '' if n_tickets == 1 else 's' }} in <strong>{{ module }}</strong>.</p>
  <ul>
    {% for e in edits %}
      <li><a href="#{{ e.id }}">
        <span><span class="ticket">{{ e.ticket }}</span> · {{ (e.reason or '')[:50] }}{{ '…' if (e.reason or '')|length > 50 else '' }}</span>
        <span class="badge" id="badge-{{ e.id }}">pending</span>
      </a></li>
    {% endfor %}
  </ul>
</nav>
<main>
  <div class="page-head">
    <h1>{{ filename }}</h1>
    <div class="meta">Module: {{ module }} · Review each edit below, then render.</div>
  </div>

  {% for e in edits %}
  <section class="edit" id="{{ e.id }}" data-id="{{ e.id }}">
    <header>
      <div class="row">
        <div>
          <div class="id">{{ e.ticket }} · resolved {{ e.resolved }} · operation: {{ e.operation }}</div>
          <h2>{{ e.anchor or '(no anchor)' }}</h2>
        </div>
      </div>
    </header>
    <div class="reason"><strong>Source:</strong> {{ e.reason }}</div>
    {{ e.diff_html|safe }}
    <div class="actions">
      <button class="btn btn-approve" onclick="decide('{{ e.id }}','approve')">Approve</button>
      <button class="btn btn-reject" onclick="decide('{{ e.id }}','reject')">Reject</button>
      <span class="status" id="status-{{ e.id }}">pending</span>
    </div>
  </section>
  {% endfor %}

  {% if not edits %}
  <div class="empty-state">
    <div class="icon">✓</div>
    <h2>No edits proposed for this guide</h2>
    <p>The LLM reviewed {{ n_tickets }} candidate {{ 'ticket' if n_tickets == 1 else 'tickets' }} in <strong>{{ module }}</strong> and didn't find any that produce a user-visible change to this specific guide. This usually means the relevant tickets touch other modules' guides, or are backend-only changes.</p>
  </div>
  {% endif %}

  {% if notes %}
  <details class="aside" {% if not edits %}open{% endif %}>
    <summary>Open notes ({{ notes|length }})</summary>
    <div class="body">
      <ul>{% for n in notes %}<li>{{ n }}</li>{% endfor %}</ul>
    </div>
  </details>
  {% endif %}

  {% if skipped %}
  <details class="aside">
    <summary>Skipped tickets ({{ skipped|length }})</summary>
    <div class="body">
      <ul>{% for s in skipped %}<li><strong>{{ s.ticket }}</strong> — {{ s.reason }}</li>{% endfor %}</ul>
    </div>
  </details>
  {% endif %}
</main>
</div>

<div class="footer-bar">
  <div class="count"><strong id="approvedCount">0</strong> approved · <strong id="rejectedCount">0</strong> rejected · <strong id="pendingCount">{{ n_edits }}</strong> pending</div>
  <button id="renderBtn" class="btn-render" onclick="render()" {% if n_edits == 0 %}disabled{% endif %}>Render &amp; preview</button>
</div>

<div class="modal-bg" id="resultModal">
  <div class="modal">
    <h2 id="resultTitle">Render complete</h2>
    <p class="summary" id="resultSummary"></p>
    <div class="skipped" id="resultSkipped" style="display:none">
      <h3>Skipped edits</h3>
      <ul id="resultSkippedList"></ul>
    </div>
    <div class="pdf-hint">
      <strong>Need a PDF?</strong> Open the HTML preview, then use your browser's <strong>Print → Save as PDF</strong>. Print styles are baked in.
    </div>
    <div class="row">
      <button class="btn-close" onclick="document.getElementById('resultModal').classList.remove('show')">Back to review</button>
      <a class="btn-secondary" id="resultDownloadMd" download>Download .md</a>
      <a class="btn-secondary" id="resultDownloadHtml" download>Download .html</a>
      <a class="btn-primary" id="resultView" target="_blank" rel="noopener">Open HTML preview ↗</a>
    </div>
  </div>
</div>

<script>
const jobId="{{ job_id }}";
const total={{ n_edits }};
const decisions={};
async function decide(id,what){
  decisions[id]=what;
  const badge=document.getElementById('badge-'+id);
  const status=document.getElementById('status-'+id);
  badge.textContent=what==='approve'?'approved':'rejected';
  badge.className='badge '+(what==='approve'?'approved':'rejected');
  status.textContent=what==='approve'?'✓ approved':'✗ rejected';
  status.className='status '+(what==='approve'?'approved':'rejected');
  await fetch(`/jobs/${jobId}/decide`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({edit_id:id,decision:what})});
  updateCounts();
}
function updateCounts(){
  let a=0,r=0;Object.values(decisions).forEach(v=>v==='approve'?a++:r++);
  document.getElementById('approvedCount').textContent=a;
  document.getElementById('rejectedCount').textContent=r;
  document.getElementById('pendingCount').textContent=total-a-r;
}
async function render(){
  const btn=document.getElementById('renderBtn');
  btn.disabled=true;btn.textContent='Rendering…';
  const res=await fetch(`/jobs/${jobId}/render`,{method:'POST'});
  if(!res.ok){alert('render failed: '+await res.text());btn.disabled=false;btn.textContent='Render & preview';return;}
  const j=await res.json();
  const summary=`Applied ${j.applied} of ${j.approved} approved edit${j.approved===1?'':'s'}.`;
  document.getElementById('resultSummary').textContent=summary;
  const skipBox=document.getElementById('resultSkipped');
  const skipList=document.getElementById('resultSkippedList');
  skipList.innerHTML='';
  if(j.skipped && j.skipped.length){
    skipBox.style.display='block';
    j.skipped.forEach(s=>{
      const li=document.createElement('li');
      li.innerHTML='<strong>'+s.ticket+'</strong> — '+s.reason;
      skipList.appendChild(li);
    });
    document.getElementById('resultTitle').textContent='Render complete — some edits skipped';
  } else {
    skipBox.style.display='none';
    document.getElementById('resultTitle').textContent='Render complete';
  }
  document.getElementById('resultView').href=j.html_url;
  document.getElementById('resultDownloadMd').href=j.md_url;
  document.getElementById('resultDownloadHtml').href=j.html_download_url;
  document.getElementById('resultModal').classList.add('show');
  btn.disabled=false;btn.textContent='Render & preview';
}
</script>
</body></html>"""


def inline_diff_html(before: str, after: str, operation: str) -> str:
    """Render a small per-edit side-by-side diff. Inline, no external CSS deps."""
    if operation == "insert_after":
        before_lines = before.splitlines() or [""]
        after_lines = (before + ("\n" if not before.endswith("\n") else "") + after).splitlines()
    else:  # replace
        before_lines = before.splitlines() or [""]
        after_lines = after.splitlines() or [""]
    differ = difflib.HtmlDiff(tabsize=4, wrapcolumn=80)
    table = differ.make_table(
        before_lines, after_lines, fromdesc="Current", todesc="Proposed", context=False
    )
    # difflib renders a `<table class="diff">`; we override its class in our CSS
    # by adding our own wrapper class.
    return f'<div class="diff-table">{table}</div>'


def apply_edits(md: str, proposals: list[dict], approved_ids: set[str]) -> tuple[str, list[dict], list[dict]]:
    """Apply approved edits in order.

    Returns (final_md, applied, skipped) where applied/skipped are lists of
    {id, ticket, reason}. Skipped means the edit was approved but its `before`
    anchor was no longer findable (usually because an earlier approved edit
    mutated the text it referenced).
    """
    out = md
    applied: list[dict] = []
    skipped: list[dict] = []
    for p in proposals:
        if p["id"] not in approved_ids:
            continue
        before = p["before"]
        after = p["after"]
        op = p.get("operation", "insert_after")
        if before not in out:
            skipped.append({
                "id": p["id"],
                "ticket": p["ticket"],
                "reason": "anchor text not found after prior edits (likely overlap with another approved edit)",
            })
            continue
        if op == "replace":
            out = out.replace(before, after, 1)
        else:  # insert_after
            joiner = "" if before.endswith("\n") else "\n"
            out = out.replace(before, before + joiner + after, 1)
        applied.append({"id": p["id"], "ticket": p["ticket"]})
    return out, applied, skipped


HTML_DOC_CSS = """
:root { --ink:#1f2933; --muted:#5b6470; --rule:#d9dde4; --accent:#d27c3a; --bg-soft:#fafbfc; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto,
               "Helvetica Neue", Arial, sans-serif;
  max-width: 760px;
  margin: 0 auto;
  padding: 56px 28px 96px;
  color: var(--ink);
  font-size: 16px;
  line-height: 1.65;
  background: #fff;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}
.doc-header {
  border-bottom: 1px solid var(--rule);
  padding-bottom: 14px;
  margin-bottom: 28px;
}
.doc-header .eyebrow {
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--accent);
  font-weight: 600;
  margin: 0 0 6px;
}
.doc-header .meta {
  margin: 8px 0 0;
  font-size: 12.5px;
  color: var(--muted);
}
h1 { font-size: 30px; margin: 0; line-height: 1.2; letter-spacing: -0.01em; font-weight: 700; }
h2 {
  font-size: 21px; margin: 38px 0 12px; line-height: 1.3;
  border-bottom: 1px solid var(--rule); padding-bottom: 6px; font-weight: 700;
}
h3 { font-size: 17px; margin: 26px 0 8px; line-height: 1.35; font-weight: 700; }
h4 { font-size: 14.5px; margin: 20px 0 6px; line-height: 1.4; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; }
p  { margin: 0 0 14px; }
ol, ul { margin: 0 0 16px; padding-left: 28px; }
li { margin: 5px 0; }
li > p { margin: 4px 0; }
li > ol, li > ul { margin-top: 4px; margin-bottom: 8px; }
strong { font-weight: 600; color: var(--ink); }
em { font-style: italic; }
code {
  font-family: ui-monospace, SFMono-Regular, Menlo, "Cascadia Mono", Consolas, monospace;
  font-size: 0.92em;
  background: #eef1f5;
  padding: 1px 5px;
  border-radius: 4px;
}
pre {
  background: var(--bg-soft);
  border: 1px solid var(--rule);
  padding: 14px 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 0 0 18px;
  font-size: 13.5px;
  line-height: 1.55;
}
pre code { background: none; padding: 0; border-radius: 0; font-size: inherit; }
blockquote {
  margin: 0 0 18px;
  padding: 8px 18px;
  border-left: 3px solid var(--accent);
  color: var(--muted);
  background: #fffaf0;
  font-style: italic;
}
blockquote > :last-child { margin-bottom: 0; }
hr { border: 0; border-top: 1px solid var(--rule); margin: 36px 0; }
table { border-collapse: collapse; width: 100%; margin: 0 0 18px; font-size: 14.5px; }
th, td { border: 1px solid var(--rule); padding: 8px 12px; text-align: left; vertical-align: top; }
th { background: var(--bg-soft); font-weight: 600; }
a { color: var(--accent); text-decoration: none; border-bottom: 1px solid rgba(210,124,58,0.35); }
a:hover { border-bottom-color: var(--accent); }
img { max-width: 100%; height: auto; }

@media print {
  body { padding: 12mm 14mm 18mm; max-width: 100%; font-size: 11pt; }
  h1 { font-size: 22pt; }
  h2 { font-size: 14pt; page-break-after: avoid; }
  h3 { font-size: 12pt; page-break-after: avoid; }
  pre, blockquote, table { page-break-inside: avoid; }
  .doc-header .meta { display: none; }
}
"""


def md_to_html(md_path: Path, html_path: Path, title: str = "", subtitle: str = "") -> None:
    """Render a markdown file to a self-contained styled HTML document.

    YAML frontmatter is stripped before rendering. The output is a single .html
    file with embedded CSS — opens cleanly in any browser, includes print styles
    so browser Print → Save as PDF produces a decent PDF.
    """
    import markdown as md_lib

    text = md_path.read_text(encoding="utf-8")
    # Strip YAML frontmatter so it doesn't render as plain text at the top
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            text = text[end + 4 :].lstrip("\n")

    body_html = md_lib.markdown(
        text,
        extensions=["fenced_code", "tables", "sane_lists", "smarty"],
        output_format="html5",
    )

    title_text = title or md_path.stem
    eyebrow = "Updated guide" if subtitle else ""
    meta_html = f'<p class="meta">{html.escape(subtitle)}</p>' if subtitle else ""
    eyebrow_html = f'<p class="eyebrow">{html.escape(eyebrow)}</p>' if eyebrow else ""

    doc = (
        "<!doctype html>\n"
        '<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        f"<title>{html.escape(title_text)}</title>\n"
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<style>{HTML_DOC_CSS}</style>\n"
        "</head>\n<body>\n"
        '<div class="doc-header">'
        f"{eyebrow_html}"
        f"<h1>{html.escape(title_text)}</h1>"
        f"{meta_html}"
        "</div>\n"
        f"{body_html}\n"
        "</body>\n</html>\n"
    )
    html_path.write_text(doc, encoding="utf-8")


def register_review_routes(app, jobs_dir: Path, repo: Path) -> None:
    def jdir(job_id: str) -> Path:
        d = jobs_dir / job_id
        if not d.exists():
            abort(404)
        return d

    @app.route("/jobs/<job_id>/review")
    def review(job_id: str):
        d = jdir(job_id)
        proposals_path = d / "proposals.json"
        if not proposals_path.exists():
            return redirect(url_for("processing", job_id=job_id))
        proposals = json.loads(proposals_path.read_text(encoding="utf-8"))
        tickets = json.loads((d / "tickets.json").read_text(encoding="utf-8")) if (d / "tickets.json").exists() else []
        filename = (d / "filename.txt").read_text(encoding="utf-8") if (d / "filename.txt").exists() else "(unknown)"
        module = (d / "module.txt").read_text(encoding="utf-8") if (d / "module.txt").exists() else ""

        edits = proposals.get("proposed_edits", [])
        for e in edits:
            e["diff_html"] = inline_diff_html(e.get("before", ""), e.get("after", ""), e.get("operation", "insert_after"))

        return render_template_string(
            REVIEW_HTML,
            job_id=job_id,
            filename=filename,
            module=module,
            n_edits=len(edits),
            n_tickets=len(tickets),
            edits=edits,
            skipped=proposals.get("skipped_tickets", []),
            notes=proposals.get("open_notes", []),
        )

    @app.route("/jobs/<job_id>/decide", methods=["POST"])
    def decide(job_id: str):
        d = jdir(job_id)
        body = request.get_json(silent=True) or {}
        edit_id = body.get("edit_id")
        decision = body.get("decision")
        if not edit_id or decision not in ("approve", "reject"):
            abort(400, "bad body")
        dec_path = d / "decisions.json"
        decisions = json.loads(dec_path.read_text(encoding="utf-8")) if dec_path.exists() else {}
        decisions[edit_id] = decision
        dec_path.write_text(json.dumps(decisions, indent=2), encoding="utf-8")
        return jsonify({"ok": True})

    @app.route("/jobs/<job_id>/render", methods=["POST"])
    def render(job_id: str):
        d = jdir(job_id)
        md_path = d / "in.md"
        proposals = json.loads((d / "proposals.json").read_text(encoding="utf-8"))
        dec_path = d / "decisions.json"
        decisions = json.loads(dec_path.read_text(encoding="utf-8")) if dec_path.exists() else {}
        approved_ids = {eid for eid, dec in decisions.items() if dec == "approve"}

        md = md_path.read_text(encoding="utf-8")
        final_md, applied, skipped = apply_edits(md, proposals.get("proposed_edits", []), approved_ids)
        (d / "out.md").write_text(final_md, encoding="utf-8")
        (d / "render_result.json").write_text(
            json.dumps({"approved": len(approved_ids), "applied": applied, "skipped": skipped}, indent=2),
            encoding="utf-8",
        )

        # Pull a friendly title from the original filename
        src_name = (d / "filename.txt").read_text(encoding="utf-8") if (d / "filename.txt").exists() else "Updated guide"
        title = src_name.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").strip() or "Updated guide"
        subtitle = f"{len(applied)} of {len(approved_ids)} approved edits applied"
        md_to_html(d / "out.md", d / "out.html", title=title, subtitle=subtitle)

        return jsonify({
            "html_url": url_for("view_html", job_id=job_id),
            "md_url": url_for("download_md", job_id=job_id),
            "html_download_url": url_for("download_html", job_id=job_id),
            "approved": len(approved_ids),
            "applied": len(applied),
            "skipped": skipped,
        })

    @app.route("/jobs/<job_id>/out.html")
    def view_html(job_id: str):
        d = jdir(job_id)
        html_path = d / "out.html"
        if not html_path.exists():
            abort(404)
        return send_file(html_path, mimetype="text/html; charset=utf-8", as_attachment=False)

    @app.route("/jobs/<job_id>/out.html/download")
    def download_html(job_id: str):
        d = jdir(job_id)
        html_path = d / "out.html"
        if not html_path.exists():
            abort(404)
        return send_file(html_path, mimetype="text/html; charset=utf-8",
                         as_attachment=True, download_name=f"{job_id}.html")

    @app.route("/jobs/<job_id>/out.md")
    def download_md(job_id: str):
        d = jdir(job_id)
        md_path = d / "out.md"
        if not md_path.exists():
            abort(404)
        return send_file(md_path, mimetype="text/markdown; charset=utf-8",
                         as_attachment=True, download_name=f"{job_id}.md")
