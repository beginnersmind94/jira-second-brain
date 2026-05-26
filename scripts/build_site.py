"""Static HTML site generator for the vault.

Converts wiki/ + raw/tickets/ to browsable HTML in output/site/.
Handles [[path|label]] wikilinks and [[path]] bare wikilinks.
"""
import html
import os
import re
import shutil
from pathlib import Path

import markdown

VAULT = Path(__file__).resolve().parent.parent
WIKI = VAULT / "wiki"
TICKETS = VAULT / "raw" / "tickets"
OUT = VAULT / "output" / "site"


CSS = """
* { box-sizing: border-box; }
body { font-family: -apple-system, Segoe UI, Roboto, sans-serif; max-width: 920px;
       margin: 0 auto; padding: 24px; color: #222; line-height: 1.55; }
header { border-bottom: 1px solid #e2e2e2; margin-bottom: 24px; padding-bottom: 8px; }
header a { color: #0969da; text-decoration: none; margin-right: 16px; font-weight: 500; }
header a:hover { text-decoration: underline; }
h1, h2, h3 { line-height: 1.25; }
h1 { border-bottom: 1px solid #eaecef; padding-bottom: 6px; }
code { background: #f6f8fa; padding: 2px 6px; border-radius: 4px; font-size: 0.92em; }
pre code { display: block; padding: 12px; overflow-x: auto; }
a { color: #0969da; }
a.broken { color: #cf222e; text-decoration: line-through; }
blockquote { border-left: 4px solid #d0d7de; color: #57606a; margin: 12px 0; padding: 4px 14px; }
ul { padding-left: 22px; }
.frontmatter { background: #f6f8fa; padding: 12px 16px; border-radius: 8px;
               font-size: 0.9em; margin-bottom: 20px; }
.frontmatter table { border-collapse: collapse; width: 100%; }
.frontmatter td { padding: 2px 6px; vertical-align: top; }
.frontmatter td:first-child { color: #57606a; width: 150px; }
"""

HEADER_HTML = """<header>
<a href="{root}index.html">Index</a>
<a href="{root}concepts.html">Concepts</a>
<a href="{root}workflows.html">Workflows</a>
<a href="{root}entities.html">Entities</a>
<a href="{root}tickets.html">Tickets</a>
</header>
"""


def wikilink_to_html(text, current_rel, source_dir_rel):
    """Replace [[target|label]] and [[target]] with proper <a> tags.

    current_rel: output path of the page being rendered, relative to OUT root.
    source_dir_rel: directory of the source .md (relative to VAULT) — used to resolve
                    wikilinks that are written relative to the source file.
    """
    def resolve(target):
        t = target.strip()
        t = re.sub(r"\.md$", "", t)
        # Bare NXT-xxxx -> raw/tickets/NXT-xxxx
        if re.fullmatch(r"NXT-\d+", t, re.IGNORECASE):
            t = f"raw/tickets/{t.upper()}"

        # Try multiple bases: absolute-from-vault, relative-to-source-dir
        candidates = [t, str(Path(source_dir_rel) / t).replace(os.sep, "/")]
        # If the source lives under wiki/, also try resolving relative to wiki/
        parts = source_dir_rel.split("/") if source_dir_rel else []
        if parts and parts[0] == "wiki":
            candidates.append(f"wiki/{t}")
        # And try wiki/-prefixed if source is vault root (for root index.html)
        if source_dir_rel in ("", "."):
            candidates.append(f"wiki/{t}")

        for cand in candidates:
            md_src = VAULT / Path(cand).with_suffix(".md")
            if md_src.exists():
                abs_target = OUT / Path(cand).with_suffix(".html")
                rel = os.path.relpath(abs_target, (OUT / current_rel).parent)
                return rel.replace(os.sep, "/"), True

        # None existed — link to first candidate as broken
        abs_target = OUT / Path(candidates[0]).with_suffix(".html")
        rel = os.path.relpath(abs_target, (OUT / current_rel).parent)
        return rel.replace(os.sep, "/"), False

    def repl(m):
        inner = m.group(1)
        if "|" in inner:
            target, label = inner.split("|", 1)
        else:
            target, label = inner, inner
        href, exists = resolve(target)
        cls = "" if exists else ' class="broken"'
        return f'<a href="{html.escape(href)}"{cls}>{html.escape(label)}</a>'

    return re.sub(r"\[\[([^\]]+)\]\]", repl, text)


FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def parse_fm_html(text):
    m = FM_RE.match(text)
    if not m:
        return "", text
    fm = m.group(1)
    rows = []
    for line in fm.split("\n"):
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        rows.append(f"<tr><td>{html.escape(k.strip())}</td><td>{html.escape(v.strip())}</td></tr>")
    if not rows:
        return "", text[m.end():]
    return f'<div class="frontmatter"><table>{"".join(rows)}</table></div>', text[m.end():]


def render_page(src_path, rel_out, title=None, source_dir_rel=None):
    src_text = src_path.read_text(encoding="utf-8")
    if source_dir_rel is None:
        source_dir_rel = str(src_path.parent.relative_to(VAULT)).replace(os.sep, "/")
        if source_dir_rel == ".":
            source_dir_rel = ""
    src_text = wikilink_to_html(src_text, rel_out, source_dir_rel)
    fm_html, body = parse_fm_html(src_text)
    body_html = markdown.markdown(body, extensions=["fenced_code", "tables", "toc"])
    # figure out root prefix for the nav header
    depth = len(Path(rel_out).parts) - 1
    root = "../" * depth if depth > 0 else ""
    nav = HEADER_HTML.format(root=root)
    page_title = title or src_path.stem
    out = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{html.escape(page_title)}</title>
<style>{CSS}</style></head><body>
{nav}
{fm_html}
{body_html}
</body></html>"""
    out_path = OUT / rel_out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(out, encoding="utf-8")


def build_listing(title, entries, rel_out):
    """Build a flat HTML list page from (href, label) entries."""
    items = "\n".join(f'<li><a href="{html.escape(h)}">{html.escape(l)}</a></li>' for h, l in entries)
    depth = len(Path(rel_out).parts) - 1
    root = "../" * depth if depth > 0 else ""
    nav = HEADER_HTML.format(root=root)
    page = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{html.escape(title)}</title>
<style>{CSS}</style></head><body>
{nav}
<h1>{html.escape(title)}</h1>
<ul>{items}</ul>
</body></html>"""
    (OUT / rel_out).parent.mkdir(parents=True, exist_ok=True)
    (OUT / rel_out).write_text(page, encoding="utf-8")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    # Render wiki/
    for md in WIKI.rglob("*.md"):
        rel = md.relative_to(VAULT).with_suffix(".html")
        render_page(md, str(rel).replace(os.sep, "/"))

    # Pass-through wiki/**/*.html (self-contained training artifacts per REPO_STRUCTURE.md §wiki/)
    for src in WIKI.rglob("*.html"):
        rel = src.relative_to(VAULT)
        dst = OUT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst)

    # Render raw/tickets/
    ticket_files = sorted(TICKETS.glob("*.md"))
    print(f"Rendering {len(ticket_files)} tickets...")
    for i, md in enumerate(ticket_files, 1):
        rel = md.relative_to(VAULT).with_suffix(".html")
        render_page(md, str(rel).replace(os.sep, "/"), title=md.stem)
        if i % 1000 == 0:
            print(f"  {i}/{len(ticket_files)}")

    # Build listings
    concept_entries = [
        (f"wiki/concepts/{p.stem}.html", p.stem.replace("-", " "))
        for p in sorted((WIKI / "concepts").glob("*.md"))
    ]
    workflow_entries = [
        (f"wiki/workflows/{p.stem}.html", p.stem.replace("-", " ").title())
        for p in sorted((WIKI / "workflows").glob("*.md"))
    ]
    entity_entries = [
        (f"wiki/entities/{p.stem}.html", p.stem.replace("-", " ").title())
        for p in sorted((WIKI / "entities").glob("*.md"))
    ]
    ticket_entries = [
        (f"raw/tickets/{p.stem}.html", p.stem) for p in ticket_files
    ]
    build_listing("Concepts", concept_entries, "concepts.html")
    build_listing("Workflows", workflow_entries, "workflows.html")
    build_listing("Entities", entity_entries, "entities.html")
    build_listing(f"All Tickets ({len(ticket_entries)})", ticket_entries, "tickets.html")

    # Root index copied from wiki/index.html
    root_src = OUT / "wiki" / "index.html"
    if root_src.exists():
        shutil.copy(root_src, OUT / "index.html")
        # rewrite relative links inside the copied root index (it was rendered at depth 2 originally,
        # re-render at depth 0 for cleanliness)
        render_page(WIKI / "index.md", "index.html", title="Perseus/NXT Second Brain")

    print(f"Done. Open: {OUT / 'index.html'}")


if __name__ == "__main__":
    main()
