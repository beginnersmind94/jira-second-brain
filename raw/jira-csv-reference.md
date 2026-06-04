# Jira CSV Export — Working Reference

**What it is:** Jira's "all fields" CSV export. One row per issue. The current file
(`raw/_imports/Perseus Jira (5).csv`) is **3,661 rows × 745 columns** (NXT project,
filtered to a created-date window covering the SC 2.0 25/26 roadmap). The column *set*
and *order* depend on which fields were selected at export time — so **match columns by
header name, not by hardcoded index.**

> Built from this export: offline demo fixtures for 7 modules live at
> `learning-agent/data/demo/<module-slug>-fixture.json` (Accountability, Account
> Management, Eligibility, Item Management, Menu Planning, Insights, Inventory).
> Builder: `learning-agent/build_fixtures_from_csv.py`.

## Structural gotchas (these will bite a naive reader)
1. **Multi-value fields repeat under the *same* header.** `Comment` appears ~38×,
   `Log Work` 29×, `Sprint` 14×, `Watchers` 8×, `Components` 5×, `Labels` 4×,
   `Fix versions` 2×. A plain `header.index('Comment')` finds only the first —
   **collect *all* indices where `header == name`** and join them.
2. **There are two `Custom field (Acceptance Criteria)` columns — the first is EMPTY,
   the second holds the content** (cols 494 vs 495 in this file). If AC reads as blank,
   you grabbed the wrong one. This is the single most important quirk for wiki/guide
   work, since AC is the highest-trust field. *(Builder picks the AC column with content.)*
3. **Encoding:** read with `encoding='utf-8-sig'` (BOM present). Expect mojibake in
   customer/district names (`â€™`→`'`, `â€"`→`–`) — clean it (re-encode cp1252 → decode utf-8).
4. **Big text + long rows:** Description runs ~19K chars, AC ~14K — set
   `csv.field_size_limit(10**7)`. Nothing is truncated; full text is present.
5. **Dates are `M/D/YYYY h:mm AM/PM` strings** — parse them; don't sort lexically.

## Columns that matter most (ranked), with field IDs
| Column (header) | Field ID | Why it matters |
|---|---|---|
| `Issue key` | — | Stable identifier; `raw/tickets/` filename anchor |
| **`Custom field (Acceptance Criteria)`** (2nd one) | `customfield_10131` | **Highest-trust: agreed behavior.** Ranked #1 in CLAUDE.md |
| `Custom field (Release Notes)` / `(... (Internal))` / `(... Title)` / `(... Required)` | `10148 / 10219 / 10285 / 10218` | Customer-facing voice; drives guide edits. `Required` ∈ {External Only, Internal Only, External/Internal, Not Required} |
| `Custom field (Module)` | `customfield_10147` | **Pre-categorized module tag — more reliable than parsing Summary.** 22 values present |
| `Description` | — | Narrative, but **lowest-trust** (problem statement, pre-scope) |
| `Summary`, `Issue Type`, `Status`, `Status Category`, `Resolution`, `Priority` | — | Core triage; `Status Category` ∈ {To Do, In Progress, Done}; `Resolution` distinguishes Done/Won't Do/Duplicate |
| `Created`, `Updated`, `Resolved` | — | Recency/staleness; `Resolved` blank on ~11% of Done items |
| `Comment` (all of them) | — | Append-only discussion; **often carries origin signal** (Freshdesk #, decisions) not in Description/AC |
| `Parent` / `Parent summary` / `Custom field (Release Version)` | `— / — / 10146` | Hierarchy + release bucketing (e.g. "Release (PE 25-26)") |
| `Custom field (Story Points)` / `(Story point estimate)` | `10102 / 10xxx` | Effort proxy |

## Fields that exist but are EMPTY/unreliable in NXT — don't build on them
- `Custom field (Request Type)` — 100% blank.
- A `State` custom field — 100% blank.
- **No structured Customer or Contract field** → any customer attribution is
  **text-derived** (Summary/Description/AC/Comments); flag it as such, never as audited.

## Verified structure of the current export (`Perseus Jira (5).csv`)
- 3,661 rows × 745 cols. `Issue key` col 1, `Summary` 0, `Status` 4, `Issue Type` 3,
  `Priority` 12, `Components` 27–31, **`Custom field (Module)` 592**,
  **`Custom field (Acceptance Criteria)` 494 (empty) + 495 (content, 1136 non-empty)**,
  `Release Notes` 627, `RN (Internal)` 628, `RN Title` 631, `RN Required` 630,
  `Description` 38, `Parent` 740, `Parent summary` 742, `Comment` 702+.
- Issue types: Bug 1586, Story 1058, Task 718, Epic 125, Tech-Debt 88, Enhancement 78.
- Per-module rows: Item Management 535, Menu Planning 371, Inventory 282,
  Accountability 271, Eligibility 127, Account Management 33, Insights 27.

## One-liner (for the top of CLAUDE.md)
> *Jira CSV = "all fields" export, one row/issue, ~745 cols. Match by header name;
> multi-value fields (Comment, Components, Labels, Sprint…) repeat under the same header
> — collect all. **Acceptance Criteria is the 2nd of two AC columns (first is empty).**
> Read utf-8-sig, raise csv field-size limit, parse M/D/YYYY dates. Trust order:
> AC > Release Notes > Internal RN > Description. `Custom field (Module)` beats
> summary-parsing. No structured Customer/Request-Type/State field — those are blank;
> customer signal is text-derived.*
