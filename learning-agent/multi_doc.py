"""Cross-module combined guide — stitch N single-module drafts into ONE grounded document.

Grounding is per-claim, not per-document: each claim traces to a verbatim span in its OWN
module's tickets. So a combined doc validates against the UNION of the source modules'
fixtures — ticket keys (NXT-####) are globally unique, so the union is collision-free and
every citation resolves to its real ticket. Cross-module grounding is exact, not approximate.

Generation stays single-module (cap-friendly, done whenever). Combining is deterministic,
keyless, and instant — zero extra model calls.

CLI:  python multi_doc.py <rid> <rid> ... [--title "..."] [--pdf]
      each <rid> is a drafts/<rid>.html (+ drafts/<rid>.json carrying its module) the pipeline wrote.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
import uuid
from datetime import datetime

import demo
from demo import _load_fixture, _slug, validate_citations

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

DRAFTS = demo.DRAFTS
_H1_RE = re.compile(r"<h1\b[^>]*>.*?</h1>", re.I | re.S)
_SOURCES_RE = re.compile(r"\n*<h2[^>]*>\s*Sources\s*</h2>[\s\S]*$", re.I)
_KEY_RE = re.compile(r"\[\[\s*([A-Z]+-\d+)\s*:")


def union_fixture(modules: list[str]) -> dict:
    """Union of each module's fixture. Ticket keys are globally unique -> no collision."""
    tickets: dict[str, dict] = {}
    epics: dict[str, dict] = {}
    for m in dict.fromkeys(modules):
        fx = _load_fixture(m)
        tickets.update(fx.get("tickets", {}))
        epics.update(fx.get("epics", {}))
    return {"module": " + ".join(dict.fromkeys(modules)), "tickets": tickets, "epics": epics}


def _body_of(html: str) -> str:
    """Strip the leading <h1> and the trailing Sources section; keep the graded body
    (its <h2> sections and every <!-- Source: --> comment, verbatim)."""
    h = _H1_RE.sub("", html, count=1)
    h = _SOURCES_RE.sub("", h)
    return h.strip()


def combine(parts: list[tuple[str, str]], title: str, fixture: dict) -> str:
    """parts = [(module_label, draft_html)] -> one combined grounded HTML doc:
    <h1>title>, then per part <h2>module</h2> + its body, then one merged Sources list."""
    issues: set[str] = set()
    chunks: list[str] = []
    for module, html in parts:
        issues.update(_KEY_RE.findall(html))
        chunks.append(f"<h2>{module}</h2>\n{_body_of(html)}")
    body = "\n\n".join(chunks)
    sources = ""
    if issues:
        items = [f"  <li><code>{k}</code> — {(fixture['tickets'].get(k) or fixture['epics'].get(k) or {}).get('summary', '')}</li>"
                 for k in sorted(issues)]
        sources = "\n\n<h2>Sources</h2>\n<ul>\n" + "\n".join(items) + "\n</ul>"
    return f"<h1>{title}</h1>\n\n{body}{sources}"


def _load_part(rid: str) -> tuple[str, str]:
    html_path = DRAFTS / f"{rid}.html"
    meta_path = DRAFTS / f"{rid}.json"
    if not html_path.exists():
        raise SystemExit(f"ERROR: draft HTML not found: {html_path}")
    module = ((json.loads(meta_path.read_text(encoding="utf-8")) or {}).get("module", "")
              if meta_path.exists() else "")
    if not module:
        raise SystemExit(f"ERROR: no 'module' in drafts/{rid}.json — cannot ground this part")
    return module, html_path.read_text(encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rids", nargs="+", help="draft ids to combine (drafts/<rid>.html)")
    ap.add_argument("--title", default=None)
    ap.add_argument("--pdf", action="store_true")
    args = ap.parse_args()

    parts = [_load_part(r) for r in args.rids]
    modules = [m for m, _ in parts]
    uniq = list(dict.fromkeys(modules))
    title = args.title or ("Combined guide — " + ", ".join(uniq))

    fx = union_fixture(modules)
    demo._FIX = fx  # validate_citations reads the process-global fixture
    combined = combine(parts, title, fx)
    integ = validate_citations(combined)
    clean = integ["tier_lie"] == 0 and integ["quote_not_found"] == 0 and "INVALID_CITE_ID" not in combined

    rid = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-combined-{_slug('-'.join(uniq))[:40]}-{uuid.uuid4().hex[:6]}"
    (DRAFTS / f"{rid}.html").write_text(combined, encoding="utf-8")
    (DRAFTS / f"{rid}.json").write_text(json.dumps({
        "id": rid, "status": "draft", "module": " + ".join(uniq), "modules": uniq,
        "template": "combined-release-notes", "method": "combined-multi-module",
        "source_drafts": args.rids, "created_at": datetime.now().isoformat(timespec="seconds"),
        "demo": True,
        "citation_integrity": {"verified": integ["ok"], "tier_lie": integ["tier_lie"],
                               "not_found": integ["quote_not_found"], "invalid_cite_id": 0},
    }, indent=2), encoding="utf-8")

    print(f"combined {len(parts)} drafts -> {rid}")
    print(f"modules: {', '.join(uniq)}  ({len(fx['tickets'])} tickets in union fixture)")
    print(f"grounding: tier_lie={integ['tier_lie']} not_found={integ['quote_not_found']} "
          f"ok={integ['ok']} tokened={integ['tokened']}  -> {'CLEAN' if clean else 'VIOLATIONS'}")

    if args.pdf:
        import pdf_export
        clean_html = re.sub(r"<!--\s*Source:[\s\S]*?-->", "", combined)
        pdf = pdf_export.render_html_to_pdf(clean_html, banner=None)
        (DRAFTS / f"{rid}.pdf").write_bytes(pdf)
        print(f"PDF: drafts/{rid}.pdf ({round(len(pdf)/1024, 1)} kb, {'valid' if pdf[:5] == b'%PDF-' else 'INVALID'})")

    return 0 if clean else 1


if __name__ == "__main__":
    sys.exit(main())
