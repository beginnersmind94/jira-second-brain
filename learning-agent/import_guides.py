#!/usr/bin/env python3
"""Import the existing human-authored SchoolCafe / Family Hub guides into the
Learning Studio library so the customer view is populated for the demo.

Reads jira-brain/raw/guides/manifest.csv + each guide's CURATED .md, converts the
markdown body to HTML, and writes a library resource (drafts/<id>.html +
drafts/<id>.json) with status=approved so it shows in the Library / Customer view.

HONEST PROVENANCE: these are human-authored guides imported as-is. They did NOT pass
the grounding gate, so they are NOT marked "grounded by construction" (no
citation_integrity block, grounded=false). provenance=human_authored_imported.
Grounding / citations come later ("just add them for now, update later").

Run:  python import_guides.py            (writes into <this dir>/drafts)
Idempotent: re-running overwrites the same <id>.{html,json}.
"""
import csv
import html as _html
import json
import re
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent          # .../learning-agent
JB = HERE.parent                                  # .../jira-brain
MANIFEST = JB / "raw" / "guides" / "manifest.csv"
OUT = HERE / "drafts"
OUT.mkdir(parents=True, exist_ok=True)


def parse_frontmatter(text: str):
    """Return (meta dict, body) for a YAML-ish frontmatter markdown file."""
    meta, body = {}, text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            for line in text[3:end].strip("\n").splitlines():
                if ":" in line:
                    k, _, v = line.partition(":")
                    meta[k.strip()] = v.strip().strip('"').strip("'")
            body = text[end + 4:].lstrip("\n")
    return meta, body


def _strip_internal(body: str) -> str:
    """Drop internal authoring notes (the 'Seeded from the raw extraction…' blockquote)."""
    keep = []
    for ln in body.splitlines():
        s = ln.strip()
        if s.startswith(">") and ("Seeded from the raw extraction" in s or "mark_guide_reviewed" in s):
            continue
        keep.append(ln)
    return "\n".join(keep)


def md_to_html(body: str) -> str:
    """Markdown -> HTML. Prefer python-markdown; fall back to a small converter."""
    body = _strip_internal(body)
    body = re.sub(r"^\s*#\s+.*\n", "", body, count=1)  # drop the leading # title (card shows it)
    try:
        import markdown  # type: ignore
        return markdown.markdown(body, extensions=["extra", "sane_lists", "nl2br"])
    except Exception:
        pass

    def inline(s: str) -> str:
        s = _html.escape(s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        return s

    out, para = [], []
    cur_list = None  # None | 'ol' | 'ul'

    def flush_para():
        if para:
            out.append("<p>" + inline(" ".join(para).strip()) + "</p>")
            para.clear()

    def close_list():
        nonlocal cur_list
        if cur_list:
            out.append(f"</{cur_list}>")
            cur_list = None

    for raw in body.splitlines():
        s = raw.strip()
        if not s:
            flush_para(); close_list(); continue
        h = re.match(r"^(#{1,6})\s+(.*)$", s)
        if h:
            flush_para(); close_list()
            lvl = min(len(h.group(1)), 4)
            out.append(f"<h{lvl}>{inline(h.group(2))}</h{lvl}>")
            continue
        want = None
        if re.match(r"^[0-9]+[.)]\s+", s):
            want = "ol"
        elif re.match(r"^([a-zA-Z][.)]|[-*•])\s+", s):
            want = "ul"
        if want:
            flush_para()
            if cur_list != want:
                close_list(); out.append(f"<{want}>"); cur_list = want
            item = re.sub(r"^([0-9]+[.)]|[a-zA-Z][.)]|[-*•])\s+", "", s)
            out.append("<li>" + inline(item) + "</li>")
            continue
        close_list()
        para.append(s)
    flush_para(); close_list()
    return "\n".join(out)


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-") or "guide"


def main():
    rows = list(csv.DictReader(MANIFEST.open(encoding="utf-8")))
    imported, skipped, by_module = 0, [], {}
    for r in rows:
        rid = (r.get("id") or "").strip()
        cur_rel = (r.get("curated_markdown_path") or "").strip()
        cur = JB / cur_rel if cur_rel else None
        if not rid or not cur or not cur.exists():
            skipped.append((rid or "?", "missing curated .md")); continue
        fm, body = parse_frontmatter(cur.read_text(encoding="utf-8"))
        html_body = md_to_html(body)
        if not html_body.strip():
            skipped.append((rid, "empty body")); continue
        title = fm.get("title") or r.get("title") or rid
        module = fm.get("module") or r.get("module") or ""
        ctype = fm.get("content_type") or r.get("content_type") or "Guide"
        meta = {
            "id": rid,
            "status": "approved",
            "approved": True,
            "sme_approved": True,
            "title": title,
            "module": module,
            "template": slug(ctype),
            "content_type": ctype,
            "origin": "internal",
            "origin_label": "Cybersoft (internal)",
            "platform": fm.get("platform") or r.get("platform") or "",
            "source_url": r.get("source_url") or fm.get("source_url") or "",
            "software_version": r.get("software_version") or fm.get("software_version") or "",
            "source_updated": r.get("source_updated") or fm.get("source_updated") or "",
            "created_at": r.get("updated_at") or datetime.now().isoformat(timespec="seconds"),
            "demo": True,
            "method": "imported_guide",
            "provenance": "human_authored_imported",
            "grounded": False,
            "source_note": ("Imported SchoolCafe/Family Hub guide (human-authored). "
                            "Not gate-verified — grounding/citations to be added later."),
        }
        article = f'<article class="guide imported-guide">\n{html_body}\n</article>\n'
        (OUT / f"{rid}.html").write_text(article, encoding="utf-8")
        (OUT / f"{rid}.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        imported += 1
        by_module[module] = by_module.get(module, 0) + 1

    print(f"Imported {imported} guides -> {OUT}")
    for m in sorted(by_module):
        print(f"  {m}: {by_module[m]}")
    if skipped:
        print(f"Skipped {len(skipped)}:")
        for rid, why in skipped:
            print(f"  {rid}: {why}")


if __name__ == "__main__":
    main()
