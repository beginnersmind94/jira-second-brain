"""Inline the 4 Eligibility guide markdowns into resource-center.html as
<script type="text/markdown"> blocks, so the detail panel can render content
without needing fetch() (which fails under file:// or cross-origin preview).
"""
from pathlib import Path
import re

HTML = Path(r'C:\Users\rahul.mehta\Downloads\Financials-Documentation-KT\jira-brain\wiki\training\resource-center.html')
GUIDES = Path(r'C:\Users\rahul.mehta\Downloads\Financials-Documentation-KT\jira-brain\wiki\guides\eligibility')

# resource_id (matches catalog JSON id) -> guide filename
MAP = {
    'elig-forms-quick-guide':       'forms-quick-guide.md',
    'elig-collection-worksheet':    'collection-worksheet-quick-guide.md',
    'elig-reports-quick-guide':     'eligibility-reports-quick-guide.md',
    'elig-view-modify-apps':        'view-and-modify-applications-quick-guide.md',
}

# Build script blocks (escape any literal </script> to keep the parser sane).
blocks = []
for rid, fn in MAP.items():
    body = (GUIDES / fn).read_text(encoding='utf-8')
    body = body.replace('</script>', r'<\/script>')
    blocks.append(f'<script type="text/markdown" id="md-{rid}">\n{body}\n</script>')

embed = '<!-- embedded guide markdown — keeps content inline so fetch() is not required -->\n' + '\n'.join(blocks)

html = HTML.read_text(encoding='utf-8')

# Remove any prior embed (idempotent re-run)
html = re.sub(
    r'<!-- embedded guide markdown.*?(?=<script type="application/json")',
    '', html, count=1, flags=re.DOTALL
)

anchor = '<script type="application/json" id="catalog-data">'
if anchor not in html:
    raise SystemExit('anchor script tag not found')

html = html.replace(anchor, embed + '\n\n' + anchor, 1)

HTML.write_text(html, encoding='utf-8')
print(f'Embedded {len(MAP)} markdown blocks. New HTML size: {len(html)} bytes.')
