"""Append the remaining raw Eligibility quick-guides to catalog/resources.json.

Idempotent: skips entries whose id already exists. Pulls title / content_type /
source_url from each markdown's frontmatter; infers page from the title.

After running, re-run _embed_v2.py so v2 HTML picks up the new inlined content.
"""
from pathlib import Path
import json
import re

ROOT = Path(r'C:\Users\rahul.mehta\Downloads\Financials-Documentation-KT\jira-brain')
RAW_DIR = ROOT / 'raw' / 'guides' / 'markdown' / 'SC' / 'Eligibility' / 'Quick-Guide'
CATALOG = ROOT / 'catalog' / 'resources.json'

# Map GUIDE-XXX → (catalog id, page label) for the ones we're adding.
# Pages chosen to match the in-product nav so source-card breadcrumbs read naturally.
GUIDES = {
    'GUIDE-036': ('elig-add-applications',          'Applications · Add'),
    'GUIDE-038': ('elig-application-processing',    'Applications · Process'),
    'GUIDE-039': ('elig-add-income-surveys',        'Income Surveys · Add'),
    'GUIDE-040': ('elig-view-income-surveys',       'Income Surveys · View'),
    'GUIDE-041': ('elig-processing',                'Processing'),
    'GUIDE-042': ('elig-sampling',                  'Verification · Sampling'),
    'GUIDE-043': ('elig-tracking',                  'Verification · Tracking'),
    'GUIDE-044': ('elig-tracking-forms',            'Verification · Tracking Forms'),
    'GUIDE-045': ('elig-inactive-applications',     'Applications · Inactive'),
    'GUIDE-046': ('elig-backdated-applications',    'Applications · Backdated'),
    'GUIDE-048': ('elig-dc-files',                  'Direct Certification · Files'),
    'GUIDE-049': ('elig-dc-matched',                'Direct Certification · Matched'),
    'GUIDE-050': ('elig-dc-potential-matches-qg',   'Direct Certification · Potential Matches'),
    'GUIDE-051': ('elig-dc-extensions',             'Direct Certification · Extensions'),
    'GUIDE-052': ('elig-dc-file-search',            'Direct Certification · File Search'),
    'GUIDE-053': ('elig-apps-notifications',        'Notifications · Applications'),
    'GUIDE-054': ('elig-income-surveys-notifications', 'Notifications · Income Surveys'),
    'GUIDE-055': ('elig-dc-notifications',          'Notifications · Direct Certification'),
    'GUIDE-056': ('elig-carryover-notifications',   'Notifications · Carryover'),
}

# Tagging hint per page area — used to seed the tag chips.
TAGS_FOR = {
    'Applications': ['applications', 'frequency:daily'],
    'Income Surveys': ['income-surveys'],
    'Processing': ['applications', 'processing'],
    'Verification': ['verification', 'compliance', 'frequency:annual'],
    'Direct Certification': ['compliance', 'direct-certification'],
    'Notifications': ['notifications', 'household-comms'],
}

# Roles default — most quick-guides are manager-facing daily ops.
DEFAULT_ROLES = ['director', 'manager']

def parse_frontmatter(text: str) -> dict:
    m = re.match(r'\s*---\s*\n(.*?)\n---\s*\n', text, re.DOTALL)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if ':' not in line:
            continue
        k, _, v = line.partition(':')
        v = v.strip().strip('"\'')
        out[k.strip()] = v
    return out

def tags_from_page(page: str) -> list:
    for prefix, tags in TAGS_FOR.items():
        if page.startswith(prefix) or prefix in page:
            return tags
    return ['onboarding']

# Load existing catalog
catalog = json.loads(CATALOG.read_text(encoding='utf-8'))
existing_ids = {r['id'] for r in catalog['resources']}

added = 0
skipped = 0
missing = []

for fn in sorted(RAW_DIR.glob('*.md')):
    # Pull GUIDE-XXX prefix from filename
    m = re.match(r'(GUIDE-\d{3})-(.+)\.md$', fn.name)
    if not m:
        continue
    guide_num = m.group(1)
    if guide_num not in GUIDES:
        # Already mapped via the 4 hand-cataloged elig docs (037, 047, 057) — skip.
        skipped += 1
        continue

    rid, page = GUIDES[guide_num]
    if rid in existing_ids:
        skipped += 1
        continue

    text = fn.read_text(encoding='utf-8')
    fm = parse_frontmatter(text)
    title = fm.get('title', fn.stem.replace('-', ' ').title())
    # Clean the title's "Quick Guide" suffix → "— Quick Guide" for consistency with catalog style
    if title.endswith(' Quick Guide'):
        title = title[:-len(' Quick Guide')] + ' — Quick Guide'

    rel_path = str(fn.relative_to(ROOT)).replace('\\', '/')
    source_url = fm.get('source_url', '')

    entry = {
        'id': rid,
        'title': title,
        'platform': 'schoolcafe',
        'module': 'Eligibility',
        'page': page,
        'content_type': 'micro-guide',
        'roles': DEFAULT_ROLES,
        'tags': tags_from_page(page),
        'status': 'review',
        'path': rel_path,
        'source_refs': [source_url] if source_url else [],
        'updated': '2026-05-13',
    }
    catalog['resources'].append(entry)
    existing_ids.add(rid)
    added += 1

# Write back with 2-space indent (matches existing style)
CATALOG.write_text(json.dumps(catalog, indent=2) + '\n', encoding='utf-8')
print(f'Added {added} entries. Skipped {skipped} (already present or unmapped).')
if missing:
    print('Missing files:', missing)
print(f'Catalog now has {len(catalog["resources"])} resources.')
