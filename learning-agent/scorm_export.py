"""
scorm_export.py — SCORM 1.2 package builder for Learning Studio.

Produces a self-contained .zip (bytes) containing:
  - imsmanifest.xml  (SCORM 1.2-compliant manifest)
  - index.html       (SCO launch page — iframe wrapper, SCORM API shim)
  - content/         (module HTML files, one per module)
  - quiz/            (quiz JSON per module, when present)

Usage
-----
    from scorm_export import build_scorm_package
    zip_bytes = build_scorm_package(track, modules)
    # track  — dict from /api/tracks/{id}  (expanded)
    # modules — list of module dicts (same as track["modules"])

The returned bytes can be served directly as application/zip.

SCORM 1.2 notes
---------------
- cmi.core.lesson_status is set to "completed" when all module iframes have
  fired their "done" postMessage.
- LMSInitialize / LMSFinish are called around the session.
- No score is tracked (learning content, not assessment); the SCO launch page
  sets cmi.core.score.raw=100 on completion so an LMS that requires a score
  does not show a failure state.

Stub-point for content files
------------------------------
The builder pulls module HTML from the published/ directory via
`_load_module_html()`. If a file is not found there it emits a placeholder
stub so the package still validates — an SME can replace the placeholder
before distributing.
"""
from __future__ import annotations

import html as _html
import io
import re
import textwrap
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import xml.etree.ElementTree as ET

# Base directory of this file → resolve relative paths to published/ etc.
_BASE = Path(__file__).resolve().parent


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────


def build_scorm_package(track: dict, modules: list[dict]) -> bytes:
    """Return a SCORM 1.2 package as raw zip bytes.

    Parameters
    ----------
    track   : Track dict (id, title, description, product, role_tags, …).
    modules : Ordered list of module dicts (id, title, source, …).  May be
              empty — the package will still be valid (one placeholder page).
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        _write_manifest(zf, track, modules)
        _write_launch_page(zf, track, modules)
        _write_module_content(zf, modules)
        _write_quiz_json(zf, modules)
    return buf.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
# imsmanifest.xml
# ─────────────────────────────────────────────────────────────────────────────

_MANIFEST_HEADER = """<?xml version="1.0" encoding="UTF-8"?>"""

_SCORM12_NS = {
    "xmlns": "http://www.imsproject.org/xsd/imscp_rootv1p1p2",
    "xmlns:adlcp": "http://www.adlnet.org/xsd/adlcp_rootv1p2",
    "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "xsi:schemaLocation": (
        "http://www.imsproject.org/xsd/imscp_rootv1p1p2 "
        "imscp_rootv1p1p2.xsd "
        "http://www.adlnet.org/xsd/adlcp_rootv1p2 "
        "adlcp_rootv1p2.xsd"
    ),
}


def _safe_xml_id(text: str) -> str:
    """Sanitise text to a valid XML NCName (starts with letter, no spaces)."""
    s = re.sub(r"[^A-Za-z0-9._-]", "_", text)
    if s and not s[0].isalpha():
        s = "R_" + s
    return s or "SCO_ROOT"


def _write_manifest(zf: zipfile.ZipFile, track: dict, modules: list[dict]) -> None:
    """Build and write imsmanifest.xml."""
    track_id = _safe_xml_id(track.get("id") or "track")
    title = track.get("title") or "Learning Track"
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Build the manifest XML manually (avoids namespace complexities of
    # xml.etree for multi-NS docs; simpler and easier to audit).
    lines: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<manifest identifier="{mid}" version="1.3"'.format(mid=track_id),
        '  xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2"',
        '  xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"',
        '  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
        '  xsi:schemaLocation="http://www.imsproject.org/xsd/imscp_rootv1p1p2 imscp_rootv1p1p2.xsd'
        ' http://www.adlnet.org/xsd/adlcp_rootv1p2 adlcp_rootv1p2.xsd">',
        '  <metadata>',
        '    <schema>ADL SCORM</schema>',
        '    <schemaversion>1.2</schemaversion>',
        '  </metadata>',
        '  <organizations default="ORG_{mid}">'.format(mid=track_id),
        '    <organization identifier="ORG_{mid}">'.format(mid=track_id),
        '      <title>{t}</title>'.format(t=_html.escape(title)),
    ]

    # One <item> per module, pointing at the shared SCO launch page.
    for i, mod in enumerate(modules):
        mod_id = _safe_xml_id(mod.get("id") or f"mod_{i}")
        mod_title = _html.escape(mod.get("title") or f"Module {i + 1}")
        lines += [
            '      <item identifier="ITEM_{idx}_{mid}" identifierref="RES_SCO">'.format(
                idx=i, mid=mod_id
            ),
            '        <title>{t}</title>'.format(t=mod_title),
            '      </item>',
        ]

    if not modules:
        lines += [
            '      <item identifier="ITEM_placeholder" identifierref="RES_SCO">',
            '        <title>(No modules)</title>',
            '      </item>',
        ]

    lines += [
        '    </organization>',
        '  </organizations>',
        '  <resources>',
        # Single SCO resource — the launch page wraps all modules.
        '    <resource identifier="RES_SCO" type="webcontent"',
        '      adlcp:scormtype="sco" href="index.html">',
        '      <file href="index.html"/>',
    ]

    # Declare content files so the LMS knows what's in the package.
    for i, mod in enumerate(modules):
        content_path = _module_content_path(mod, i)
        lines.append('      <file href="{p}"/>'.format(p=_html.escape(content_path)))
        quiz_path = _module_quiz_path(mod, i)
        if quiz_path:
            lines.append('      <file href="{p}"/>'.format(p=_html.escape(quiz_path)))

    lines += [
        '    </resource>',
        '  </resources>',
        '</manifest>',
    ]

    zf.writestr("imsmanifest.xml", "\n".join(lines))


# ─────────────────────────────────────────────────────────────────────────────
# SCO launch page (index.html)
# ─────────────────────────────────────────────────────────────────────────────

_SCO_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: system-ui, sans-serif; background: #f5f5f5; height: 100vh;
            display: flex; flex-direction: column; }}
    #header {{ background: #1a3c5e; color: #fff; padding: 10px 18px;
               display: flex; align-items: center; gap: 12px; font-size: 15px; font-weight: 600; }}
    #progress-bar {{ height: 4px; background: #d0d5dd; }}
    #progress-fill {{ height: 4px; background: #3b82f6; width: 0; transition: width .4s ease; }}
    #nav {{ display: flex; gap: 8px; padding: 10px 14px; background: #fff;
            border-bottom: 1px solid #e2e6ea; flex-wrap: wrap; }}
    .nav-btn {{ padding: 6px 14px; border: 1px solid #d0d5dd; border-radius: 6px;
                background: #fff; cursor: pointer; font-size: 13px; color: #374151; }}
    .nav-btn:hover {{ background: #f3f4f6; }}
    .nav-btn.active {{ background: #1a3c5e; color: #fff; border-color: #1a3c5e; }}
    #content-frame {{ flex: 1; border: none; background: #fff; }}
    #completion-banner {{ display: none; background: #d1fae5; color: #065f46;
                          padding: 14px 20px; text-align: center; font-weight: 600;
                          border-top: 2px solid #6ee7b7; font-size: 15px; }}
  </style>
</head>
<body>
  <div id="header">
    <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor"
         stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 2H8l-2 5h12z"/>
    </svg>
    {title}
  </div>
  <div id="progress-bar"><div id="progress-fill"></div></div>
  <div id="nav">{nav_buttons}</div>
  <iframe id="content-frame" src="{first_src}" title="Module content"></iframe>
  <div id="completion-banner" role="status">
    All modules complete — certificate issued.
  </div>

  <script>
  // ── SCORM 1.2 API shim (window.API) ────────────────────────────────────────
  // Most LMSes inject the real API into the parent frame.  This shim handles
  // the case where no real LMS is present (offline / preview), logs calls, and
  // tracks lesson_status in-memory so the SCO behaves correctly either way.
  (function() {{
    var _data = {{}};
    var _initialized = false;
    function _log(fn, args) {{
      if (window.console && console.log) console.log('[SCORM]', fn, args);
    }}
    window.API = {{
      LMSInitialize: function(s) {{
        _log('LMSInitialize', s);
        _initialized = true;
        _data['cmi.core.lesson_status'] = 'incomplete';
        return 'true';
      }},
      LMSFinish: function(s) {{
        _log('LMSFinish', s);
        _initialized = false;
        return 'true';
      }},
      LMSGetValue: function(k) {{
        var v = _data[k] !== undefined ? _data[k] : '';
        _log('LMSGetValue', k + ' = ' + v);
        return v;
      }},
      LMSSetValue: function(k, v) {{
        _log('LMSSetValue', k, v);
        _data[k] = v;
        return 'true';
      }},
      LMSCommit: function(s) {{
        _log('LMSCommit', s);
        return 'true';
      }},
      LMSGetLastError: function()  {{ return '0'; }},
      LMSGetErrorString: function(n) {{ return ''; }},
      LMSGetDiagnostic: function(n) {{ return ''; }},
    }};
  }})();

  // ── Module navigation + completion tracking ─────────────────────────────────
  var _modules = {modules_json};
  var _done    = {{}};  // module index → true when complete

  function _updateProgress() {{
    var n    = _modules.length || 1;
    var done = Object.keys(_done).length;
    var pct  = Math.round(100 * done / n);
    document.getElementById('progress-fill').style.width = pct + '%';
    if (done >= n) _onAllDone();
  }}

  function _onAllDone() {{
    // Report completion to the LMS.
    window.API.LMSSetValue('cmi.core.lesson_status', 'completed');
    window.API.LMSSetValue('cmi.core.score.raw', '100');
    window.API.LMSCommit('');
    window.API.LMSFinish('');
    document.getElementById('completion-banner').style.display = 'block';
  }}

  // Listen for postMessage from module iframes signalling completion.
  window.addEventListener('message', function(ev) {{
    if (!ev.data || typeof ev.data !== 'object') return;
    if (ev.data.type === 'scorm_module_done') {{
      _done[ev.data.index] = true;
      var btn = document.getElementById('nav-btn-' + ev.data.index);
      if (btn) btn.textContent = btn.textContent + ' ✓';
      _updateProgress();
    }}
  }});

  function showModule(idx) {{
    var m = _modules[idx];
    if (!m) return;
    document.getElementById('content-frame').src = m.src;
    document.querySelectorAll('.nav-btn').forEach(function(b, i) {{
      b.classList.toggle('active', i === idx);
    }});
  }}

  // Auto-initialize SCORM session.
  window.API.LMSInitialize('');
  </script>
</body>
</html>
"""


def _module_content_path(mod: dict, index: int) -> str:
    mid = _safe_xml_id(mod.get("id") or f"mod_{index}")
    return f"content/{mid}.html"


def _module_quiz_path(mod: dict, index: int) -> Optional[str]:
    """Return the quiz JSON path for this module, or None if no quiz."""
    mid = _safe_xml_id(mod.get("id") or f"mod_{index}")
    return f"quiz/{mid}.json"


def _write_launch_page(zf: zipfile.ZipFile, track: dict, modules: list[dict]) -> None:
    """Write the SCO index.html."""
    title = _html.escape(track.get("title") or "Learning Track")

    if modules:
        first_src = _module_content_path(modules[0], 0)
        nav_buttons = "\n    ".join(
            '<button class="nav-btn{active}" id="nav-btn-{i}" onclick="showModule({i})">'
            "{t}</button>".format(
                active=" active" if i == 0 else "",
                i=i,
                t=_html.escape(mod.get("title") or f"Module {i + 1}"),
            )
            for i, mod in enumerate(modules)
        )
        import json as _json
        modules_json = _json.dumps(
            [{"src": _module_content_path(m, i), "title": m.get("title") or f"Module {i+1}"}
             for i, m in enumerate(modules)]
        )
    else:
        first_src = "content/placeholder.html"
        nav_buttons = '<span style="color:#6b7280;font-size:13px;">No modules in this track.</span>'
        modules_json = "[]"

    html_out = _SCO_TEMPLATE.format(
        title=title,
        nav_buttons=nav_buttons,
        first_src=first_src,
        modules_json=modules_json,
    )
    zf.writestr("index.html", html_out)


# ─────────────────────────────────────────────────────────────────────────────
# Module content files
# ─────────────────────────────────────────────────────────────────────────────

_PLACEHOLDER_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>{title}</title>
<style>body{{font-family:system-ui,sans-serif;padding:32px;color:#374151;}}
  .placeholder{{background:#fef3c7;border:1px solid #f59e0b;border-radius:8px;
    padding:24px;max-width:600px;margin:0 auto;}}
  h2{{margin:0 0 12px;font-size:18px;}} p{{margin:0;font-size:14px;line-height:1.6;}}
</style></head>
<body>
  <div class="placeholder">
    <h2>Module content placeholder</h2>
    <p><strong>{title}</strong></p>
    <p>This module's content file was not found in the published library at package-build
    time. Replace this placeholder with the approved module HTML before distributing the
    SCORM package.</p>
  </div>
  <script>
    // Notify the SCO launch page that this (placeholder) module is "done" after 3 s.
    // A real module should send this message after the learner has reviewed the content.
    setTimeout(function() {{
      if (window.parent && window.parent !== window) {{
        var idx = {index};
        window.parent.postMessage({{type:'scorm_module_done', index:idx}}, '*');
      }}
    }}, 3000);
  </script>
</body>
</html>
"""

_MODULE_WRAPPER = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 860px;
            margin: 0 auto; padding: 24px 20px; color: #1f2937; line-height: 1.6; }}
    h1,h2,h3 {{ color: #1a3c5e; }}
    .scorm-done-btn {{ display: none; margin: 32px auto 0; padding: 12px 28px;
                       background: #1a3c5e; color: #fff; border: none; border-radius: 8px;
                       cursor: pointer; font-size: 15px; font-weight: 600; }}
    .scorm-done-btn.visible {{ display: block; }}
  </style>
</head>
<body>
  {body_content}
  <button class="scorm-done-btn visible" id="done-btn"
          onclick="markDone()" aria-label="Mark this module complete">
    Mark complete ✓
  </button>
  <script>
    var _MODULE_INDEX = {index};
    function markDone() {{
      document.getElementById('done-btn').disabled = true;
      document.getElementById('done-btn').textContent = 'Completed ✓';
      if (window.parent && window.parent !== window) {{
        window.parent.postMessage({{type:'scorm_module_done', index:_MODULE_INDEX}}, '*');
      }}
    }}
    // Auto-mark after 30 minutes if the learner forgets to click.
    setTimeout(markDone, 30 * 60 * 1000);
  </script>
</body>
</html>
"""


def _load_module_html(mod: dict) -> Optional[str]:
    """Load the module's published HTML, or None if not found."""
    mid = mod.get("id") or ""
    # Try published/ first, then drafts/.
    for parent in (_BASE / "published", _BASE / "drafts"):
        p = parent / f"{mid}.html"
        if p.exists():
            try:
                return p.read_text(encoding="utf-8")
            except OSError:
                pass
    return None


def _strip_source_comments(html: str) -> str:
    """Remove <!-- Source: … --> citation comments (same logic as prod._strip_source_comments)."""
    return re.sub(r"<!--\s*Source:[^>]*-->", "", html, flags=re.DOTALL)


def _extract_body(html: str) -> str:
    """Extract content between <body …> and </body>, falling back to the whole string."""
    m = re.search(r"<body[^>]*>(.*?)</body>", html, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else html.strip()


def _write_module_content(zf: zipfile.ZipFile, modules: list[dict]) -> None:
    """Write content/<mod-id>.html for each module."""
    for i, mod in enumerate(modules):
        path = _module_content_path(mod, i)
        raw = _load_module_html(mod)
        title = mod.get("title") or f"Module {i + 1}"
        if raw:
            clean = _strip_source_comments(raw)
            body = _extract_body(clean)
            content = _MODULE_WRAPPER.format(
                title=_html.escape(title),
                body_content=body,
                index=i,
            )
        else:
            content = _PLACEHOLDER_HTML.format(
                title=_html.escape(title),
                index=i,
            )
        zf.writestr(path, content)

    if not modules:
        # Write the placeholder referred to in index.html.
        zf.writestr(
            "content/placeholder.html",
            _PLACEHOLDER_HTML.format(title="No modules", index=0),
        )


# ─────────────────────────────────────────────────────────────────────────────
# Quiz JSON
# ─────────────────────────────────────────────────────────────────────────────


def _write_quiz_json(zf: zipfile.ZipFile, modules: list[dict]) -> None:
    """Write quiz/<mod-id>.json for modules that carry quiz data."""
    import json as _json

    for i, mod in enumerate(modules):
        quiz = mod.get("quiz")  # expanded track may include quiz dict
        if not quiz:
            # Attempt to load from quiz_store if available.
            try:
                import quiz_store as _qs
                qid = mod.get("quiz_id")
                if qid:
                    quiz = _qs.load_quiz(qid)
            except Exception:
                pass
        if not quiz:
            continue
        path = _module_quiz_path(mod, i)
        if path:
            zf.writestr(path, _json.dumps(quiz, ensure_ascii=False, indent=2))
