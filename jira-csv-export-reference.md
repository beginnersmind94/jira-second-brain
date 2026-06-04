# Jira CSV Export — Working Reference

Everything learned from processing the Jira "all-fields" CSV exports (`Perseus Jira (N).csv`) for this project. Companion to `jira-mcp-reference.md` (that doc = the live MCP/API; this doc = the offline CSV export). Written so a future Claude session skips the trial-and-error.

---

## What it is

A **Jira "all fields" CSV export**: one row per issue, every configured field included. The reference export processed here was the NXT project filtered to a created-date window:

- **3,661 data rows × 745 columns**
- One row per issue (multi-value fields are *not* exploded into extra rows — they spread across repeated columns; see below)
- The column **set and order depend on what was selected at export time** → **always match columns by header *name*, never by a hardcoded index.** Indices in this doc are from the reference file and are illustrative only.

---

## Quick-start loader (handles every gotcha below)

```python
import csv, re
from datetime import datetime
csv.field_size_limit(10**7)                      # AC/Description run to ~14–19K chars

with open(path, encoding='utf-8-sig', newline='') as f:   # BOM present
    rows = list(csv.reader(f))
header, data = rows[0], rows[1:]

def idxs(name):                                  # ALL columns with this header (multi-value fields repeat)
    return [i for i, h in enumerate(header) if h == name]
def first(name):                                 # first column with this header
    return idxs(name)[0]

# Acceptance Criteria: TWO columns; the FIRST is empty, the SECOND holds content.
ac_cols = idxs('Custom field (Acceptance Criteria)')
AC = ac_cols[-1]                                 # use the LAST one

COMMENTS = idxs('Comment')                       # ~38 columns; join them for full discussion
def g(r, i): return r[i] if i < len(r) else ''
def comments(r): return ' '.join(g(r, i) for i in COMMENTS if g(r, i).strip())

def fix(s):                                      # de-mojibake (customer/district names)
    return (s or '').replace('â€™', "'").replace('â€“', '–').replace('â€œ', '"').replace('â€\x9d', '"')

def parse_dt(s):                                 # dates are M/D/YYYY h:mm AM/PM strings — never sort lexically
    for fmt in ('%m/%d/%Y %I:%M %p', '%m/%d/%Y %H:%M'):
        try: return datetime.strptime(s, fmt)
        except ValueError: pass
    return None
```

---

## Structural gotchas (each will bite a naive reader)

1. **Multi-value fields repeat under the *same* header.** Counts in the reference file: `Comment` ×38, `Log Work` ×29, `Sprint` ×14, `Watchers` ×8/`Watchers Id` ×8, `Components` ×5, `Labels` ×4, `Fix versions` ×2. `header.index('Comment')` finds only the first — **collect all indices and join.**
2. **Two `Custom field (Acceptance Criteria)` columns — the FIRST is EMPTY, the SECOND holds the text** (cols 494 vs 495 here). If AC reads blank, you grabbed the wrong column. *This is the most important quirk for wiki work, since AC is the highest-trust field.*
3. **Encoding = UTF-8 with BOM** → `encoding='utf-8-sig'`. Expect mojibake in names (`â€™`→`'`). On Windows, reconfigure stdout to UTF-8 before printing or it throws on `Σ`/`→`/`’`.
4. **Big text + long rows** → `csv.field_size_limit(10**7)`. Description ≤ ~19K chars, AC ≤ ~14K. Nothing is truncated — full text is present (no need to re-fetch via MCP just for body text).
5. **Dates are `M/D/YYYY h:mm AM/PM` strings.** Parse them; lexical sort puts `1/1/2026` before `9/9/2025`.
6. **`Resolved` is blank on ~11% of Done-category issues** — don't use `resolutiondate` as the sole "completed" signal; combine with `Status Category = Done` / `Resolution = Done`.

---

## Columns that matter most (ranked for ticket→knowledge work)

| Header | Custom field ID | Why it matters / trust |
|---|---|---|
| `Issue key` | — | Stable identifier; the `raw/tickets/<KEY>.md` filename anchor |
| `Custom field (Acceptance Criteria)` **(2nd column)** | `customfield_10131` | **Highest-trust — the agreed behavior.** Per CLAUDE.md, AC is source #1 |
| `Custom field (Release Notes)` | `customfield_10148` | Customer-facing voice; drives guide edits |
| `Custom field (Release Notes (Internal))` | `customfield_10219` | Internal context when populated |
| `Custom field (Release Notes Title)` | `customfield_10285` | RN headline |
| `Custom field (Release Notes Required)` | `customfield_10218` | ∈ {External Only, Internal Only, External/Internal, Not Required} — filter first two for customer-facing guide work |
| `Custom field (Module)` | `customfield_10147` | **Pre-categorized module tag — more reliable than parsing Summary.** 27 values |
| `Description` | — | Narrative, but **lowest-trust** (problem statement / pre-scope) |
| `Summary` · `Issue Type` · `Status` · `Status Category` · `Resolution` · `Priority` | — | Core triage. `Status Category` ∈ {To Do, In Progress, Done}; `Resolution` separates Done / Won't Do / Duplicate |
| `Created` · `Updated` · `Resolved` | — | Recency & staleness (note `Resolved` blank caveat above) |
| `Comment` (all ×38) | — | Append-only discussion; **often carries origin signal (Freshdesk #, decisions) absent from Description/AC** |
| `Parent` / `Epic Link` | `customfield_10014` | Hierarchy (avoid double-counting epics + children) |
| `Custom field (Release Version)` | `customfield_10146` | Release bucketing, e.g. "Release (PE 25-26)" |
| `Custom field (Story Points)` / `(Story point estimate)` | `customfield_10102` / — | Effort proxy |
| `Components` (×5) · `Labels` (×4) | — | Secondary categorization; overlaps Module |
| `Assignee` · `Reporter` · `Creator` · `Custom field (Product Owner)` | — / `customfield_10145` | People; redact PII in `wiki/` per CLAUDE.md |

**Trust order for content (matches CLAUDE.md):** Acceptance Criteria → Release Notes → Release Notes (Internal) → Description (lowest). Prefer `Custom field (Module)` over summary keyword-parsing for categorization.

---

## Fields present but EMPTY / unreliable in NXT — do not build on them

- `Custom field (Request Type)` — **100% blank** in the reference export.
- A `State` custom field — **100% blank**.
- **No structured Customer or Contract field exists.** Any customer/contract attribution is **text-derived** (Summary/Description/AC/Comments) → always flag it as inferred, never present it as audited. (This is the single biggest data-quality gap; see the MCP reference's note on the missing custom-field discovery tool.)

---

## Verified facts from the reference export (provenance)

- Project NXT (= "2.0" / SchoolCafé 2.0). Window: `created` 2025-07-01 → 2026-06-02.
- Type mix (created-in-window): Bug 1,586 · Story 1,058 · Task 718 · Epic 125 · Tech-Debt 88 · Enhancement 78 · New Feature 7 · Feature 1.
- AC populated on ~99% of Story/Enh/New-Feature (in the **2nd** AC column); 100% of dev items have AC *or* Description.
- `Custom field (Module)` is 100% populated; 27 allowed values.

---

## Cross-reference

- **Live data / writes / ADF / comments / @mentions** → `jira-mcp-reference.md`. Key bridge fact: AC = `customfield_10131`; on a *live* read it returns **ADF JSON**, but in this **CSV export it is already rendered plain text** (the 2nd AC column).
- The CSV is a point-in-time snapshot; the MCP is live. For "what shipped / current state," prefer the MCP; for bulk analysis without rate limits or token blowup, prefer the CSV (offload large pulls to disk and parse with Python).

*Last verified against `Perseus Jira (5).csv` (3,661 rows × 745 cols), 2026-06-03.*
