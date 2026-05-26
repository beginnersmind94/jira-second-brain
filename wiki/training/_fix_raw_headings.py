"""One-time pass over raw PDF-extracted guides to fix headings + paragraph breaks.

The raw extractions in raw/guides/markdown/SC/Eligibility/Quick-Guide/ lost
PDF formatting, so section names like "ALL tab" / "PROCESS MATCHES button"
land mid-paragraph and don't render as headings. This script:

  - Promotes lines matching "<ALL CAPS> tab"   → "## $0"
  - Promotes lines matching "<ALL CAPS> button" → "### $0"
  - Promotes lines matching "<ALL CAPS> page"   → "## $0"
  - Inserts a blank line before/after any heading it touches so markdown
    parsers actually treat it as a heading
  - Also adds a blank line between any "Title-cased line" and a following
    "ALL tab" line (the common pattern at the top of these guides)

Idempotent. Re-running on already-promoted lines is a no-op.

After running: re-run _embed_v2.py to refresh the inlined blocks in v2 HTML.
"""
from pathlib import Path
import re

DIR = Path(r'C:\Users\rahul.mehta\Downloads\Financials-Documentation-KT\jira-brain\raw\guides\markdown\SC\Eligibility\Quick-Guide')

# Patterns we'll promote. Order matters — most specific first.
PROMOTIONS = [
    # "FOO bar" where FOO is all caps and bar is one of {tab, page}
    (re.compile(r'^([A-Z][A-Z ]{1,40}(?:tab|page))\s*$', re.M), r'\n\n## \1\n\n'),
    # "FOO button" → ### (a level deeper since buttons are inside sections)
    (re.compile(r'^([A-Z][A-Z &]{1,40}button)\s*$', re.M), r'\n\n### \1\n\n'),
    # Action verbs in caps that act as sub-headings, e.g. "PROCESS APPLICATION & QUIT", "PROCESS APPLICATION", "NOTIFY"
    # Only match when the next non-empty line is body text (heuristic: starts with "Use this" / a dash / verb).
    # Keeping this off by default — too aggressive.
]

# Total counter so we can report something useful.
def dedupe_duplicate_h2(text: str) -> tuple[str, int]:
    """The PDF extractions often have the same section name twice — once as a
    bullet-only summary at the top, once as the full procedural section below.
    The promotion script makes both ## headings; keep only the LAST occurrence
    (the procedural one), drop the earlier sections + their content.
    """
    lines = text.split("\n")
    # Find all "## X" heading positions
    h2_pattern = re.compile(r'^## (.+?)\s*$')
    occurrences = {}  # heading text → list of line indices
    for i, line in enumerate(lines):
        m = h2_pattern.match(line)
        if m:
            occurrences.setdefault(m.group(1).strip(), []).append(i)

    # For each duplicated heading, mark the first occurrence's section for removal
    # (lines from that heading up to but not including the next ## or ### at same/lower level)
    lines_to_remove = set()
    dupes = 0
    for heading, idxs in occurrences.items():
        if len(idxs) < 2:
            continue
        # Drop every occurrence except the last
        for occ in idxs[:-1]:
            # Find end: next ## (or end of file)
            end = len(lines)
            for j in range(occ + 1, len(lines)):
                if h2_pattern.match(lines[j]):
                    end = j
                    break
            for k in range(occ, end):
                lines_to_remove.add(k)
            dupes += 1

    if not dupes:
        return text, 0
    new_lines = [l for i, l in enumerate(lines) if i not in lines_to_remove]
    # Collapse blank-line runs at the join points
    out = "\n".join(new_lines)
    out = re.sub(r'\n{3,}', '\n\n', out)
    return out, dupes


def fix_one(text: str) -> tuple[str, int, int]:
    promoted = 0
    for pat, repl in PROMOTIONS:
        n = len(pat.findall(text))
        if n:
            text = pat.sub(repl, text)
            promoted += n
    text = re.sub(r'\n{3,}', '\n\n', text)
    text, deduped = dedupe_duplicate_h2(text)
    return text, promoted, deduped


changed_files = 0
total_promotions = 0
total_dedupes = 0
for fn in sorted(DIR.glob('GUIDE-*.md')):
    src = fn.read_text(encoding='utf-8')
    new, promoted, deduped = fix_one(src)
    if (promoted or deduped) and new != src:
        fn.write_text(new, encoding='utf-8')
        changed_files += 1
        total_promotions += promoted
        total_dedupes += deduped
        parts = []
        if promoted: parts.append(f'+{promoted} heading(s)')
        if deduped:  parts.append(f'-{deduped} dup section(s)')
        print(f'  {fn.name}: {", ".join(parts)}')

print(f'\nPromoted {total_promotions} heading(s), deduped {total_dedupes} section(s) across {changed_files} file(s).')
print('Now run: python _embed_v2.py')
