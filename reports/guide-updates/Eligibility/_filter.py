"""Filter Perseus Jira CSV per the task spec and emit:
  - filtered_ticket_index.md  (human-readable index)
  - _filtered_tickets.json    (full filtered records for downstream analysis)
"""
import csv
import json
import sys
from datetime import date

SRC = r'C:\Users\rahul.mehta\Downloads\Perseus Jira (2).csv'
OUT_DIR = r'C:\Users\rahul.mehta\Downloads\Financials-Documentation-KT\jira-brain\reports\guide-updates\Eligibility'

csv.field_size_limit(min(2**31 - 1, sys.maxsize))

with open(SRC, 'r', encoding='utf-8-sig', newline='') as f:
    reader = csv.reader(f)
    rows = list(reader)

header = rows[0]
data = rows[1:]

print(f'Total rows: {len(data)}')
print(f'Total cols in header: {len(header)}')


def find_indices(name):
    return [i for i, h in enumerate(header) if h == name]


idx_summary = header.index('Summary')
idx_key = header.index('Issue key')
idx_status = header.index('Status')
idx_resolution = header.index('Resolution')
idx_resolved = header.index('Resolved')
idx_components = find_indices('Components')
idx_description = header.index('Description')
idx_ac = find_indices('Custom field (Acceptance Criteria)')
idx_status_cat = header.index('Status Category')
idx_parent_summary = header.index('Parent summary') if 'Parent summary' in header else None

print(f'Summary col idx: {idx_summary}')
print(f'Issue key col idx: {idx_key}')
print(f'Status col idx: {idx_status}')
print(f'Resolution col idx: {idx_resolution}')
print(f'Resolved col idx: {idx_resolved}')
print(f'Components col idxs: {idx_components}')
print(f'Description col idx: {idx_description}')
print(f'AC col idxs: {idx_ac}')
print(f'Status Category col idx: {idx_status_cat}')

CUTOFF = date(2024, 5, 13)
BLOCKED_RESOLUTIONS = {"Won't Do", "Duplicate", "Cannot Reproduce", "Not a Bug"}


def parse_date(s):
    if not s:
        return None
    s = s.strip()
    if not s:
        return None
    try:
        mdy = s.split(' ')[0]
        parts = mdy.split('/')
        if len(parts) != 3:
            return None
        m, d, y = parts
        return date(int(y), int(m), int(d))
    except Exception:
        return None


def safe(row, idx):
    return row[idx] if idx < len(row) else ''


filtered = []
counters = {
    'total': 0,
    'rejected_status_cat': 0,
    'rejected_resolved_date': 0,
    'rejected_no_eligibility_component': 0,
    'rejected_blocked_resolution': 0,
    'rejected_empty_body': 0,
    'kept': 0,
}

for row in data:
    counters['total'] += 1

    status_cat = safe(row, idx_status_cat)
    if status_cat != 'Done':
        counters['rejected_status_cat'] += 1
        continue

    resolved_raw = safe(row, idx_resolved)
    resolved = parse_date(resolved_raw)
    if not resolved or resolved < CUTOFF:
        counters['rejected_resolved_date'] += 1
        continue

    components = [safe(row, i) for i in idx_components]
    if not any('eligibility' in c.lower() for c in components if c):
        counters['rejected_no_eligibility_component'] += 1
        continue

    resolution = safe(row, idx_resolution)
    if resolution in BLOCKED_RESOLUTIONS:
        counters['rejected_blocked_resolution'] += 1
        continue

    description = safe(row, idx_description).strip()
    ac_parts = [safe(row, i).strip() for i in idx_ac]
    ac = '\n\n'.join(p for p in ac_parts if p)
    if not description and not ac:
        counters['rejected_empty_body'] += 1
        continue

    filtered.append({
        'key': safe(row, idx_key),
        'summary': safe(row, idx_summary),
        'status': safe(row, idx_status),
        'resolution': resolution,
        'resolved_raw': resolved_raw,
        'resolved_iso': resolved.isoformat(),
        'components': [c for c in components if c],
        'description': description,
        'acceptance_criteria': ac,
    })
    counters['kept'] += 1

print('\n--- Counters ---')
for k, v in counters.items():
    print(f'  {k}: {v}')

# Sort by resolved date descending (newest first)
filtered.sort(key=lambda x: x['resolved_iso'], reverse=True)

# Write filtered_ticket_index.md
md_path = OUT_DIR + r'\filtered_ticket_index.md'
with open(md_path, 'w', encoding='utf-8') as f:
    f.write('# Filtered Eligibility tickets — index\n\n')
    f.write('- **Source:** `C:\\Users\\rahul.mehta\\Downloads\\Perseus Jira (2).csv` '
            f'(Perseus Jira export, {len(data)} data rows)\n')
    f.write('- **Cutoff date:** 2024-05-13 (last 2 years from 2026-05-13)\n\n')
    f.write('## Filters applied\n\n')
    f.write('1. Status Category = `Done`\n')
    f.write('2. Resolved date >= 2024-05-13\n')
    f.write('3. At least one `Components` column contains "eligibility" (case-insensitive substring)\n')
    f.write("4. Resolution NOT IN: `Won't Do`, `Duplicate`, `Cannot Reproduce`, `Not a Bug`\n")
    f.write('5. Description and Acceptance Criteria not both empty\n\n')
    f.write('## Filter funnel\n\n')
    f.write(f'- Total data rows scanned: **{counters["total"]}**\n')
    f.write(f'- Rejected (Status Category != Done): {counters["rejected_status_cat"]}\n')
    f.write(f'- Rejected (Resolved date missing or < 2024-05-13): {counters["rejected_resolved_date"]}\n')
    f.write(f'- Rejected (no Eligibility component): {counters["rejected_no_eligibility_component"]}\n')
    f.write(f'- Rejected (blocked resolution): {counters["rejected_blocked_resolution"]}\n')
    f.write(f'- Rejected (Description and AC both empty): {counters["rejected_empty_body"]}\n')
    f.write(f'- **Retained: {counters["kept"]}**\n\n')
    f.write('## Retained tickets (newest first)\n\n')
    f.write('| Key | Resolved | Summary |\n')
    f.write('|---|---|---|\n')
    for t in filtered:
        s = t['summary'].replace('|', '\\|').replace('\n', ' ').replace('\r', ' ')
        f.write(f"| {t['key']} | {t['resolved_iso']} | {s} |\n")

print(f'\nWrote: {md_path}')

# Dump full filtered records to JSON
json_path = OUT_DIR + r'\_filtered_tickets.json'
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(filtered, f, indent=2, ensure_ascii=False)
print(f'Wrote: {json_path}')
