"""Generate PDFs for all four wiki/guides/eligibility/*.md files using markdown-pdf.

Each PDF:
- single column
- serif body (Georgia / Times)
- sans-serif headings (Helvetica / Arial)
- page numbers
- file title in header
- final page lists source_tickets pulled from the frontmatter (for SME provenance)
"""
import re
import sys
from pathlib import Path

import yaml
from markdown_pdf import MarkdownPdf, Section

GUIDE_DIR = Path(r'C:\Users\rahul.mehta\Downloads\Financials-Documentation-KT\jira-brain\wiki\guides\eligibility')
PDF_DIR = GUIDE_DIR / 'pdf'
PDF_DIR.mkdir(exist_ok=True)

CSS_MAIN = """
body {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 11pt;
  line-height: 1.5;
  color: #1a1a1a;
}
h1, h2, h3, h4, h5 {
  font-family: Helvetica, Arial, sans-serif;
  color: #111;
  page-break-after: avoid;
}
h1 { font-size: 20pt; margin-top: 0; }
h2 { font-size: 15pt; margin-top: 1.4em; border-bottom: 1px solid #ddd; padding-bottom: 4px; }
h3 { font-size: 12pt; margin-top: 1.2em; }
code, pre {
  font-family: Consolas, "Courier New", monospace;
  font-size: 10pt;
  background: #f4f4f4;
}
pre { padding: 8px; border-radius: 3px; }
table {
  border-collapse: collapse;
  width: 100%;
  margin: 0.8em 0;
  font-size: 10pt;
}
th, td {
  border: 1px solid #999;
  padding: 6px 8px;
  text-align: left;
  vertical-align: top;
}
th { background: #efefef; font-family: Helvetica, Arial, sans-serif; }
blockquote {
  border-left: 3px solid #888;
  padding-left: 10px;
  color: #555;
  margin-left: 0;
}
ul, ol { padding-left: 22px; }
li { margin-bottom: 2px; }
"""

CSS_FOOTER = CSS_MAIN + """
body { font-style: italic; color: #444; }
"""


def split_frontmatter(text):
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', text, flags=re.DOTALL)
    if not m:
        return {}, text
    return yaml.safe_load(m.group(1)) or {}, m.group(2).lstrip('\n')


def render_source_tickets_page(fm):
    keys = fm.get('source_tickets') or []
    if not keys:
        return None
    lines = [
        '## Source tickets (for SME provenance)',
        '',
        'This guide was authored or edited based on the following Jira tickets. '
        'Please verify any factual claim by tracing it back to its source ticket.',
        '',
    ]
    for k in keys:
        lines.append(f'- **{k}**')
    return '\n'.join(lines)


def make_pdf(md_path: Path):
    raw = md_path.read_text(encoding='utf-8')
    fm, body = split_frontmatter(raw)
    title = fm.get('title') or md_path.stem

    pdf = MarkdownPdf(toc_level=2, mode='commonmark', optimize=True)
    pdf.meta['title'] = str(title)
    pdf.meta['author'] = 'Cybersoft — Eligibility module'
    pdf.meta['subject'] = f'Quick Guide ({fm.get("status", "draft")})'

    # Main content section (with page header showing file title)
    header_html = f'<header style="font-family:Helvetica,Arial,sans-serif;font-size:9pt;color:#666;">{title}</header>'
    pdf.add_section(Section(body, paper_size='Letter'), user_css=CSS_MAIN)

    # Source tickets footer page (new section forces page break)
    footer = render_source_tickets_page(fm)
    if footer:
        pdf.add_section(Section(footer, paper_size='Letter'), user_css=CSS_FOOTER)

    out_path = PDF_DIR / f'{md_path.stem}.pdf'
    pdf.save(str(out_path))
    return out_path


def main():
    md_files = sorted(p for p in GUIDE_DIR.glob('*.md') if not p.name.startswith('_') and p.name != 'sme_review_log.md')
    if not md_files:
        print('no guide markdown files found', file=sys.stderr)
        sys.exit(1)
    print(f'Generating {len(md_files)} PDFs...')
    for md in md_files:
        try:
            out = make_pdf(md)
            size = out.stat().st_size
            print(f'  OK  {out.name}  ({size} bytes)')
        except Exception as e:
            print(f'  ERR {md.name}: {e}', file=sys.stderr)
            raise


if __name__ == '__main__':
    main()
