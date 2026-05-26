"""Dump filtered tickets as a single markdown digest so the reconciliation step
can grep / scan for claims, instead of reading 61 separate files.
"""
import json

src = r'C:\Users\rahul.mehta\Downloads\Financials-Documentation-KT\jira-brain\reports\guide-updates\Eligibility\_filtered_tickets.json'
out = r'C:\Users\rahul.mehta\Downloads\Financials-Documentation-KT\jira-brain\reports\guide-updates\Eligibility\_digest.md'

with open(src, 'r', encoding='utf-8') as f:
    tickets = json.load(f)

with open(out, 'w', encoding='utf-8') as f:
    f.write(f'# Filtered ticket digest — {len(tickets)} tickets\n\n')
    for t in tickets:
        f.write(f"## {t['key']} — {t['summary']}\n\n")
        f.write(f"- Resolved: {t['resolved_iso']}\n")
        f.write(f"- Status: {t['status']}\n")
        f.write(f"- Resolution: {t['resolution']}\n")
        f.write(f"- Components: {', '.join(t['components'])}\n\n")
        if t['description']:
            f.write('### Description\n\n')
            f.write(t['description'] + '\n\n')
        if t['acceptance_criteria']:
            f.write('### Acceptance Criteria\n\n')
            f.write(t['acceptance_criteria'] + '\n\n')
        f.write('---\n\n')

print(f'Wrote {out}')
