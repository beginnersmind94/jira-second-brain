"""PDF export for demo resources.

Renders a resource's CLEAN guide HTML (Source comments already stripped by the
caller) to PDF bytes using pymupdf's Story API. The Story engine paginates the
flowable HTML into a fitz.Document written to an in-memory buffer.

Used only by demo_app.py (GET /resources/{rid}/pdf). Does not touch any prod
path. If Story is unavailable for some reason, falls back to a plain fitz text
render that preserves heading sizes.
"""
import io
import re

import pymupdf

# A4-ish letter page in points (612 x 792 = US Letter), with 1" margins.
_PAGE_RECT = pymupdf.paper_rect("letter")
_MARGIN = 54  # 0.75"
_CONTENT_RECT = pymupdf.Rect(
    _PAGE_RECT.x0 + _MARGIN,
    _PAGE_RECT.y0 + _MARGIN,
    _PAGE_RECT.x1 - _MARGIN,
    _PAGE_RECT.y1 - _MARGIN,
)

# Simple print stylesheet: readable serif body, sized headings, bordered tables,
# list spacing. Kept minimal — the Story CSS engine supports a subset of CSS.
_PRINT_CSS = """
body {
    font-family: "Georgia", "Times New Roman", serif;
    font-size: 11pt;
    line-height: 1.5;
    color: #1a1a1a;
}
h1 {
    font-family: "Helvetica", "Arial", sans-serif;
    font-size: 22pt;
    color: #11324d;
    margin-top: 0;
    margin-bottom: 12pt;
    border-bottom: 2px solid #11324d;
    padding-bottom: 4pt;
}
h2 {
    font-family: "Helvetica", "Arial", sans-serif;
    font-size: 16pt;
    color: #11324d;
    margin-top: 16pt;
    margin-bottom: 6pt;
}
h3 {
    font-family: "Helvetica", "Arial", sans-serif;
    font-size: 13pt;
    color: #244;
    margin-top: 12pt;
    margin-bottom: 4pt;
}
p { margin-top: 0; margin-bottom: 8pt; }
ul, ol { margin-top: 4pt; margin-bottom: 8pt; }
li { margin-bottom: 4pt; }
table {
    border-collapse: collapse;
    width: 100%;
    margin-top: 8pt;
    margin-bottom: 12pt;
}
th, td {
    border: 1px solid #888;
    padding: 5pt 7pt;
    text-align: left;
    vertical-align: top;
}
th { background-color: #eef2f6; font-family: "Helvetica", "Arial", sans-serif; }
blockquote {
    margin: 8pt 0;
    padding: 4pt 12pt;
    border-left: 3px solid #b0c4d8;
    color: #444;
    font-style: italic;
}
code {
    font-family: "Courier New", monospace;
    font-size: 10pt;
    background-color: #f2f2f2;
}
.pending-banner {
    font-family: "Helvetica", "Arial", sans-serif;
    font-size: 10pt;
    font-weight: bold;
    color: #8a5a00;
    background-color: #fff4d6;
    border: 1px solid #e0b94a;
    padding: 6pt 10pt;
    margin-bottom: 14pt;
}
"""

_DOC_TEMPLATE = (
    "<!DOCTYPE html><html><head><meta charset=\"utf-8\"></head>"
    "<body>{body}</body></html>"
)


def _wrap_document(clean_html: str, banner: str | None = None) -> str:
    """Wrap a guide HTML fragment in a minimal full document (optional top banner)."""
    body = clean_html or ""
    banner_html = (f'<div class="pending-banner">{banner}</div>' if banner else "")
    if re.search(r"<html[\s>]", body, flags=re.I):
        # Already a full doc: inject the banner right after <body> if we can.
        if banner_html:
            return re.sub(r"(<body[^>]*>)", r"\1" + banner_html, body, count=1, flags=re.I)
        return body
    return _DOC_TEMPLATE.format(body=banner_html + body)


def render_html_to_pdf(clean_html: str, banner: str | None = None) -> bytes:
    """Render clean guide HTML to PDF bytes via pymupdf's Story API.

    `clean_html` must already have <!-- Source --> comments stripped by the
    caller. `banner`, if given, renders as a highlighted strip at the top (used
    for the "Pending Review by SME" stamp). Returns PDF bytes (starts with b"%PDF").
    """
    document_html = _wrap_document(clean_html, banner)

    if hasattr(pymupdf, "Story"):
        return _render_with_story(document_html)
    return _render_fallback((f"[{banner}]\n\n" if banner else "") + clean_html)


def _render_with_story(document_html: str) -> bytes:
    """Preferred path: Story paginates the HTML into a Document buffer."""
    buf = io.BytesIO()
    writer = pymupdf.DocumentWriter(buf)
    story = pymupdf.Story(html=document_html, user_css=_PRINT_CSS)

    more = 1
    # Guard against a pathological non-converging layout.
    for _ in range(10_000):
        if not more:
            break
        device = writer.begin_page(_PAGE_RECT)
        more, _filled = story.place(_CONTENT_RECT)
        story.draw(device)
        writer.end_page()
    writer.close()

    data = buf.getvalue()
    if not data.startswith(b"%PDF"):
        raise RuntimeError("Story render did not produce a PDF")
    return data


def _render_fallback(clean_html: str) -> bytes:
    """Fallback: strip tags to text, preserve headings as larger lines.

    Only used if pymupdf.Story is unavailable. Builds a PDF with fitz directly.
    """
    # Convert headings to marked lines, then strip remaining tags.
    text = clean_html or ""
    text = re.sub(r"<h1[^>]*>(.*?)</h1>", r"\n\n# \1\n", text, flags=re.I | re.S)
    text = re.sub(r"<h2[^>]*>(.*?)</h2>", r"\n\n## \1\n", text, flags=re.I | re.S)
    text = re.sub(r"<h3[^>]*>(.*?)</h3>", r"\n\n### \1\n", text, flags=re.I | re.S)
    text = re.sub(r"<li[^>]*>(.*?)</li>", r"\n  - \1", text, flags=re.I | re.S)
    text = re.sub(r"</p>|<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    doc = pymupdf.open()
    lines = text.split("\n")
    page = None
    y = 0.0
    line_h = 14.0

    def _new_page():
        nonlocal page, y
        page = doc.new_page(width=_PAGE_RECT.width, height=_PAGE_RECT.height)
        y = _CONTENT_RECT.y0

    _new_page()
    for line in lines:
        size = 11.0
        if line.startswith("### "):
            line, size = line[4:], 13.0
        elif line.startswith("## "):
            line, size = line[3:], 16.0
        elif line.startswith("# "):
            line, size = line[2:], 22.0
        if y + line_h > _CONTENT_RECT.y1:
            _new_page()
        page.insert_text(
            (_CONTENT_RECT.x0, y), line, fontsize=size, fontname="helv"
        )
        y += line_h if size <= 11 else size + 6

    data = doc.tobytes()
    doc.close()
    if not data.startswith(b"%PDF"):
        raise RuntimeError("fallback render did not produce a PDF")
    return data
