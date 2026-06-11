# Financials 2.0 Onboarding Guide — Coverage Report

> **What this is.** A grounding + coverage audit of the *Financials 2.0 — Onboarding, Without the Yawn* guide (`financials-guide.txt`, April 2026 Edition) against all 136 Financials (`NXT-`) stories. It answers three questions: how much of the shipped + planned product does the guide actually describe, where are the gaps, and where has the guide gone stale relative to ticket Acceptance Criteria.
>
> **Scoring.** `covered` = 1.0, `partial` = 0.5, `missing` = 0.0, over 136 tickets. "Partial" means the guide touches the feature area but omits material AC behavior; it is not "good enough."
>
> **Status honesty.** Per owner direction, *every* Financials story is treated as a feature regardless of Jira status — but development status is tagged truthfully. Only **Done Done** is shipped behavior the guide may describe in the present tense. Everything else (New / In Progress / Story Refinement / PO Review / Committed / Testing / Ready for Development / Refinement) is **UPCOMING** and must be marked as such ("(Coming)") so a backlog story is never presented as if it already works.
>
> **Grounding rule for the drafting phase that follows.** Every product-behavior claim drafted from this report must trace to a verbatim AC quote (`<!-- Source: NXT-####:AC "..." -->`). RN is empty in this fixture; AC is the highest-trust source and `desc` is supporting context only. Backend codes (RTNCHCKPOS, PPACC, MEALSLS, etc.) get translated to user-facing language in prose; the raw code stays inside the citation comment.

---

## 1. Headline coverage

| Metric | Value |
|---|---|
| **Weighted coverage** | **38.2%** (52.0 of 136) |
| Covered (1.0) | 19 tickets (14.0%) |
| Partial (0.5) | 66 tickets (48.5%) |
| Missing (0.0) | 51 tickets (37.5%) |
| Stale (guide contradicts current AC) | 22 tickets |
| Shipped (Done Done) | 45 tickets (33%) |
| Upcoming (all other statuses) | 91 tickets (67%) |

**Read this honestly.** 38% is the *generous* number — it counts every "partial" as half-credit, and 66 of 136 tickets are partial. The guide has a solid spine for the seven Day-1-through-go-live jobs (Jobs 1, 2, 6, 7, 8, 9 are all real and mostly accurate for what shipped), but:

- **Two-thirds of the backlog (91 tickets) is upcoming** and the guide is written almost entirely in the present tense. The biggest risk is not omission — it's the guide asserting "posting is automatic, do nothing" while a whole wave of manual-posting-queue stories (NXT-70065/66/67, NXT-65487, NXT-66123) is in flight that *reintroduces* manual Post/Repost controls. That's an active contradiction, not a gap.
- **19 tickets have no Job home at all** — entire feature areas (roles & permissions, module navigation/licensing, the Financial Dashboard, the inventory posting engine, the Configuration Wizard intro) the guide simply does not have a section for. One of those (the Financial Dashboard, NXT-68659) is already **shipped**.

### Counts by Jira status

| Status | Count | Shipped? |
|---|---|---|
| New | 79 | Upcoming |
| Done Done | 45 | **Shipped** |
| Story Refinement/Efforting | 5 | Upcoming |
| In Progress | 2 | Upcoming |
| PO Review | 2 | Upcoming |
| Committed | 1 | Upcoming |
| Testing | 1 | Upcoming |
| Ready for Development | 1 | Upcoming |

---

## 2. Coverage matrix by guide Job

Each Financials story was mapped to the guide Job it most naturally belongs to (or `none` if the guide has no home for it). Percentages are weighted coverage within the Job.

| Job (guide section) | Tickets | Weighted | Covered / Partial / Missing | Stale | Health |
|---|---|---|---|---|---|
| **Job 1** — Get my chart of accounts in | 26 | 40% | 2 / 17 / 7 | 2 | Broad but shallow — many partials |
| **Job 2** — Account Mapping | 25 | 46% | 2 / 19 / 4 | 5 | Broad but shallow + stale spots |
| **Job 3** — Prepaids/refunds by site or district | 2 | 75% | 1 / 1 / 0 | 0 | Healthy, small |
| **Job 4** — Open my fiscal year (Periods) | 12 | **17%** | 0 / 4 / 8 | 1 | **Thinnest covered Job** |
| **Job 5** — Get my opening balances in | 2 | 50% | 0 / 2 / 0 | 2 | **Both stale** |
| **Job 6** — Make a manual journal entry | 9 | 72% | 4 / 5 / 0 | 0 | Healthy |
| **Job 7** — Fix a posting that went out wrong | 2 | 100% | 2 / 0 / 0 | 1 | Healthy (1 stale nuance) |
| **Job 8** — See what happened (Journal/Ledger) | 2 | 100% | 2 / 0 / 0 | 0 | Healthy |
| **Job 9** — Pull a report | 21 | 48% | 5 / 10 / 6 | 5 | Large, half-covered |
| **Job 10** — Posting Activity Log / why a posting failed | 16 | 31% | 1 / 8 / 7 | 4 | **Weak + actively contradicted** |
| **(none)** — no guide section exists | 19 | **0%** | 0 / 0 / 19 | 2 | **Entire feature areas missing** |

### Where each ticket lands

- **Job 1 (26):** NXT-70093, 69433, 69422, 69421, 68570, 68312, 67677, 67675, 67674, 67541, 67540, 67539, 67534, 67533, 67532, 67503, 66898, 66897, 66797, 66796, 66795, 66380, 66379, 65010, 65009, 64976
- **Job 2 (25):** NXT-70909, 70422, 70305, 70304, 70194, 70193, 69981, 69959, 69520, 69504, 69488, 69392, 69272, 69127, 69114, 69100, 69099, 69098, 69097, 69084, 69070, 69059, 65011, 65006, 65000*†
- **Job 3 (2):** NXT-70372, 70340
- **Job 4 (12):** NXT-70312, 70311, 70309, 70075, 70074, 70073, 69733, 69732, 69062, 68658, 67003, 66550
- **Job 5 (2):** NXT-71249, 71240
- **Job 6 (9):** NXT-70777, 69519, 68708, 68291, 69071, 66136, 65133, 65132, 65000†
- **Job 7 (2):** NXT-68295, 68294
- **Job 8 (2):** NXT-65124, 65123
- **Job 9 (21):** NXT-71184, 71182, 70620, 70426, 70423, 70296, 69386, 68770, 68719, 68643, 68641, 68637, 68635, 68549, 68548, 67676, 65486, 65483, 65481, 65480, 65475
- **Job 10 (16):** NXT-70866, 70295, 70111, 70069, 70068, 70067, 70066, 70065, 69972, 69933, 69388, 66389, 66386, 66385, 66384, 69493
- **(none) (19):** NXT-70682, 68660, 68659, 67481, 67479, 66966, 66965, 66930, 66929, 66928, 66927, 66896, 66563, 66388, 66387, 66123, 65487, 65485, 65482

> *† NXT-65000 (read-only debit/credit posting-rules viewer per entry type) straddles Job 2 (mapping/templates) and Job 6 (Template Entries); counted once under Job 6 in the matrix totals. Note for drafting.

### Thin / at-risk Jobs

- **Job 4 (Periods) — 17%, the weakest covered Job.** Eight of twelve tickets are missing. The guide treats period setup as "enter dates + frequency, save, move on," but AC describes a Manage Periods table with per-site POS/Inventory status, close/reopen-all, posting-aggregation frequency, period-action confirmation modals, and bell notifications. The guide is a paragraph; the product is a console.
- **Job 10 (Posting Activity Log) — 31%, and partly contradicted.** See Cluster C1 — this is the single most dangerous Job because shipped/upcoming AC reverses the guide's central "do nothing" promise.
- **The `none` bucket — 0%.** Five distinct feature areas with no guide section at all (Clusters C2, C3, C4, C8 below). One is shipped.
- **Job 9 (Reports) — 48% across 21 tickets.** The guide's three-tile Reports page is being expanded with two new report types (Trial Balance, Balance Sheet) and a deep P&L build-out; half the tickets are missing or partial.

---

## 3. Gap list — themed clusters

Gaps grouped into themes. Each cluster notes: ticket keys, whether it **extends an existing Job** or needs a **NEW section**, priority (P0 job-critical / P1 important / P2 nice-to-have), and the shipped-vs-upcoming mix. Clusters are ordered by priority, then size.

> Priority lens: **P0** = the guide is *wrong or dangerously incomplete* about something a user does in the first 90 days (active contradiction, or a shipped feature with no coverage of the thing users will reach for). **P1** = important feature area materially under-described. **P2** = refinement/polish a user can succeed without.

---

### C1 — Posting Activity Log is being rebuilt and the guide's "posting is automatic, do nothing" promise is now contradicted **(P0)**

- **Tickets:** NXT-70065, NXT-70066, NXT-70067, NXT-70068, NXT-70069, NXT-69972, NXT-65487, NXT-66123 (manual-queue / grid / card-set changes); plus NXT-70866, NXT-70111 (notifications + auto-rerun on mapping fix).
- **Maps to:** Extends **Job 10** (and the "What changed in 2.0" table + Glossary, which both assert Approve/Post buttons are *gone*).
- **Gap type:** stale + missing. Direct contradiction.
- **Shipped vs upcoming:** All upcoming (New). NXT-69493 (the Done Done baseline the current Job 10 was written from) stays accurate; the contradiction is the *new* wave layered on top.
- **Why P0:** The guide's headline 2.0 selling point — "Do nothing. Posting fires the moment the upstream period closes… you can no longer forget to post" — is being walked back. NXT-70065 adds a manual **Ready-to-Post queue (Review / Post All)**; NXT-65487 and NXT-66123 add **POS and Inventory postings grids with Post / Repost / Remove** actions and a Status column; NXT-70066 **replaces the four summary cards** the guide enumerates (Total / Completed / Failed / Running) with three new ones; NXT-70069 adds a **"You're posting manually" nudge banner**. NXT-70067 adds failed-job pinning + a red Failed-count badge; NXT-69972 adds a login notification banner and a Requires-Review status. A customer reading today's guide and then seeing Post buttons will conclude the guide (or the product) is broken. This must be reframed with clear "(Coming)" tagging and a watch-out, and the Glossary line "Approve / Post buttons (gone…)" must be qualified.

---

### C2 — Roles & permissions: no section exists **(P0)**

- **Tickets:** NXT-66927 (Finance Coordinator granular), NXT-66928 (Director / Central Office / Admin full access), NXT-66929 (Cafeteria Manager read-only/limited).
- **Maps to:** **NEW section.** The guide has zero roles & permissions content.
- **Gap type:** missing.
- **Shipped vs upcoming:** All upcoming (New).
- **Why P0:** "Who can touch the ledger" is a first-week question for any finance module, and the guide's audience explicitly includes multiple roles (CN Director, Finance Manager, accountants, Cafeteria Managers). Three distinct permission tiers are specified in AC. Without this, an implementer cannot answer "what will my cafeteria managers see?" — a question that gates go-live. Tag as (Coming) but build the section now; it is job-critical knowledge even pre-release.

---

### C3 — The Financial Dashboard is shipped and undocumented **(P0)**

- **Tickets:** NXT-68659 (**Done Done** — Net Income / Revenue / Expense KPI cards, period selector, trend arrow, site table), NXT-68660 (district site-by-site Revenue/Expense/Net Income table; posted txns only).
- **Maps to:** **NEW section** (logically a landing/"where do I stand at a glance" job, distinct from Job 9 reports).
- **Gap type:** missing.
- **Shipped vs upcoming:** **Mixed — NXT-68659 is shipped (Done Done)**; NXT-68660 is upcoming (Story Refinement).
- **Why P0:** This is a *shipped* surface the guide describes nowhere. It is likely the first screen a director lands on. A new hire will see a dashboard the training never mentions. Document the shipped KPI dashboard in present tense; tag the district site-table expansion as (Coming).

---

### C4 — Module placement, navigation & licensing: no section exists **(P1)**

- **Tickets:** NXT-66966 ("Financial Oversight" left-sidebar nav, Front Office group, breadcrumbs, license-gated), NXT-66965 (enable via License Management toggle, district license type), NXT-66930 (module architecture naming Settings / Balance Sheet / Export to ERP / Void-Reverse).
- **Maps to:** **NEW section** — likely a "Before you touch the product" or "Finding Financials" preface.
- **Gap type:** missing.
- **Shipped vs upcoming:** All upcoming (New).
- **Why P1:** "How do I even get to Financials, and how do we turn it on?" is an implementer setup question. The guide jumps straight to Job 1 assuming you're already in the module. NXT-66930 also names features (Balance Sheet, Export to ERP, Void/Reverse) that confirm other clusters. Tag (Coming); pairs naturally with the existing Week-0 implementer setup content.

---

### C5 — Prepaid liability is being split into POS vs Online, retiring the single "Prepaid Account" **(P1)**

- **Tickets:** NXT-70909 (split POS / Online Prepaid Liability + period-end reclassification), NXT-70305 (replace single Prepaid Account data point with POS + Online, source-split by enrollment site), NXT-69981 (sales-tax split: revenue vs Sales Tax Owed liability, plus Deposit Variances posting). Related shipped: NXT-70304 (auto-posts net sales tax, Done Done — see C6).
- **Maps to:** Extends **Job 2** (data points / mapping) and the "What changed in 2.0" framing.
- **Gap type:** stale (NXT-70909, NXT-70305 flagged stale) + missing (NXT-69981).
- **Shipped vs upcoming:** All upcoming (New).
- **Why P1:** The guide implies a single prepaid bucket. AC retires it for two source-split liabilities with period-end reclassification — a mapping decision the customer makes during Phase 2/3 setup. Getting this wrong mis-maps real money. Tag (Coming) and add an Open question for the exact data-point labels (do not invent "POS Prepaid Liability" as a UI string unless AC states it).

---

### C6 — Posting-engine entry rules (sales tax, MEALSLS, inventory close, reimbursement) are undocumented **(P1)**

- **Tickets:** NXT-70304 (**Done Done** — net sales-tax auto-post: Debit Cash / Credit Sales Tax Owed, one per site/period), NXT-66384 (**Done Done** — MEALSLS entry shape + data-point attribution), NXT-70295 (inventory close PURCH/WD/ADDINV/transfers per valuation category, PO Review), NXT-70620 (inventory PURCH at Valuation Category × Vendor, Refinement), NXT-66385 (auto reimbursement Claim + Received shapes, New), NXT-66389 / NXT-66386 / NXT-66388 / NXT-66387 (withdrawal-waste, usage/commodity, warehouse fees, inventory transfers — all New), NXT-65485 (backend posting stored proc resolving system accounts to tenant GL, New), NXT-65482 (Valuation Categories page mapping inventory categories to Asset/Expense, Refinement).
- **Maps to:** Extends **Job 10** (why postings happen/fail) and **Job 2** (valuation-category mapping); several have no home.
- **Gap type:** mostly missing; NXT-70304 and NXT-66384 are partial.
- **Shipped vs upcoming:** **Mixed — NXT-70304 and NXT-66384 are shipped (Done Done)**; the rest upcoming.
- **Why P1:** The guide says "posting is automatic" but never shows *what entries get created*. Two of these (sales tax, MEALSLS meal-sales entry shape) are shipped and explain real ledger lines a user will see in Job 8/Job 10. The Valuation Categories page (NXT-65482) is a required mapping prerequisite that gates inventory posting. Translate backend codes (PURCH, WD, ADDINV, MEALSLS) to plain language in prose; keep codes only in citations.

---

### C7 — P&L report build-out (Reimbursements, Expenses detail, Revenue detail, Meal Counts, COGS) **(P1)**

- **Tickets:** NXT-65480 (Reimbursements section: meal counts × USDA rates, accrual), NXT-65483 (Expenses section: CPM, categories, GL sourcing), NXT-65475 (Revenue detail by program/meal type, drill-down, export), NXT-65486 (Meal Counts section), NXT-65481 (standalone COGS report by inventory category), NXT-69386 (per-data-point revenue rows, Net Revenue excl. tax vs Total Collected, Fed/State reimbursement rows), NXT-68770 (Phase-1 P&L backend formulas), NXT-68719 (Phase-2 P&L sources COGS from manual Inventory entries — stale), NXT-70682 (promotional P&L PDF — executive summary/KPI/variance; **none** bucket). Shipped baseline: NXT-68643, NXT-70296.
- **Maps to:** Extends **Job 9** (P&L); NXT-70682 is a distinct PDF artifact (possibly NEW subsection).
- **Gap type:** mostly partial; NXT-65480/65486/70682 missing.
- **Shipped vs upcoming:** Baseline P&L (NXT-68643 P&L parameters, NXT-70296 Cost of Foods Used) is **shipped**; the section expansion is all upcoming.
- **Why P1:** P&L is the board/auditor deliverable (Job 9's stated purpose). The shipped guide covers the P&L shell + COFU accurately, but the entire revenue/expense/reimbursement/meal-count detail layer is upcoming and unmentioned. NXT-68719 is also *stale*: guide says COFU comes live from the Inventory Usage Report, AC (Phase 2) sources COGS from manual Inventory entries — flag the conflict, don't silently pick.

---

### C8 — Two new report tiles (Trial Balance, Balance Sheet) are not on the three-tile Reports page **(P1)**

- **Tickets:** NXT-71184 (Trial Balance, Oracle-aligned columns — Committed), NXT-71182 (Balance Sheet: Assets/Liab/Equity + Net Income, per-site worksheets — In Progress).
- **Maps to:** Extends **Job 9** (Reports landing page).
- **Gap type:** missing + stale (the guide enumerates exactly three tiles; these are the 4th and 5th).
- **Shipped vs upcoming:** Both upcoming (Committed / In Progress).
- **Why P1:** The 90-Day Cheat Sheet literally tells users to generate "Trial Balance / P&L" in weeks 4–8 — but Trial Balance has no tile in the guide's Reports section. The guide promises a report it doesn't document. Tag (Coming) on the tiles; reconcile the cheat-sheet reference.

---

### Additional clusters (documented for completeness; below the top-8 for drafting)

These are real but lower-priority or more diffuse than the eight above.

- **C9 — Periods console depth (Job 4) [P1, but folded into Job 4 rather than a cluster of its own]:** NXT-70073, 70074, 70075, 70309, 70311, 70312, 69732, 69733, 67003, 66550, 69062, 68658. Per-site POS/Inventory status popovers, posting-aggregation frequency (Daily/Weekly/Monthly, locked after first post), period-action modals, close-anyway warnings, Starting Fund Balance field, bell notifications. NXT-68658 is the shipped Manage Periods baseline (Done Done); rest upcoming. *Job 4 is the thinnest covered Job (17%) — addressing C9 is the single biggest single-Job lift.*
- **C10 — Configuration Wizard / guided import flow (Job 1) [P2]:** NXT-66896 (wizard intro), 66897 (structure page Skip/Reset), 66898 (import Type→Upload→Field-Mapping→Review), 67005 (Smart Mapping with confidence badges), plus upload-UX tickets 66795/66796/66797/66379/66380. All New. The guide teaches a job-organized manual path; a guided wizard is a parallel UX the guide doesn't mention. P2 because the manual path still works.
- **C11 — GL config audit trail + History tab (Job 1) [P2]:** NXT-67539 (4th "History" tab on GL Accounts), 67540 (backend before/after audit of all GL config changes), 69433 (view-only Rules button on GL grid), 69392 (Rules drawer for system data points). NXT-69433/69392 are **Done Done** (shipped, but missing from guide); 67539/67540 upcoming. The guide says GL Accounts has *three* tabs; a 4th is coming.
- **C12 — Account lifecycle rules (Job 1) [P2]:** NXT-67674 (block deleting accounts with posted txns), 67676 (transaction snapshots account code/desc at posting), 68312 (per-site GL sub-account codes), 67541 (saving Account Code Structure versions + recodes transactions). Mix of shipped backend (67676 New; 68312 Done Done) and upcoming. Deletion/versioning mechanics the guide omits.
- **C13 — Payroll & manual-entry expansion (Job 6) [P2]:** NXT-70777 (payroll import: template, FY+Period, closed-period block, $0.01 tolerance), 69071 (Payroll & Manual Entries page + Ledger "Payroll Entry" type), 68708 (mandatory Entry Type dropdown on Manual Entry form), 65000 (read-only posting-rules viewer). All New except none. Job 6 is already healthy (72%); these are enhancements.

---

## 4. Stale-content list (guide says X, current AC says Y)

22 tickets are flagged stale. These are the cases where the guide is **not merely incomplete but contradicts** current AC — the highest-risk category for customer-facing content, because a confidently-wrong statement is worse than a silent gap.

| Ticket | Status | Guide says (X) | AC says (Y) |
|---|---|---|---|
| NXT-70065 | New | "Do nothing, posting is automatic" | Manual **Ready-to-Post queue** (Review / Post All) |
| NXT-70066 | New | Four summary cards: Total / Completed / Failed / Running | **Three new cards** replace them |
| NXT-70069 | New | Posting is automatic, do nothing | Adds **"You're posting manually" nudge banner** |
| NXT-65487 | New | "Approve / Post buttons are gone" (Glossary) | **POS postings grid** with Post / Repost / Remove + Status column |
| NXT-66123 | New | "Approve / Post buttons are gone" | **Inventory postings grid** with Post / Approve / Repost / Remove |
| NXT-66386 | New | Approve / Post are gone (automatic on upstream close) | Usage/Commodity **Approve / Post / Reapprove checkbox matrix** |
| NXT-71249 | New | Opening Balance is a "one-time import" | Adds Fiscal Year selection, two amount schemes, dup blocking, atomic load, **replacement warning** (re-import allowed) |
| NXT-71240 | Refinement | "One-time import" | Dedicated read-only Opening Balance entry, effective date = day before FY start, **hard reversal on re-import** |
| NXT-71184 | Committed | Reports page has exactly three tiles | Adds **Trial Balance** report/tile |
| NXT-71182 | In Progress | Reports page has exactly three tiles | Adds **Balance Sheet** report/tile |
| NXT-70909 | New | One prepaid bucket ("Prepaid Account") | Splits into **POS + Online Prepaid Liability** with period-end reclassification |
| NXT-70305 | New | One prepaid bucket | Replaces single Prepaid Account with **POS + Online**, source-split by enrollment site |
| NXT-69959 | Done Done | "~72 total" data points | **77 revenue data points** grouped by category (+ program list, Rules drawer) |
| NXT-69084 | Done Done | Bulk Actions / Map All flow; nav at Configuration › Account Mapping | Per-row **Edit-drawer** management view + mapping-progress banner |
| NXT-69070 | New | Bulk Actions / Program-filter / 4-phase model | **Mapping wizard** with auto-save, summary cards, valuation dual-mapping, named rules |
| NXT-68719 | New | COFU sourced **live** from Inventory Usage Report | Phase-2 P&L sources **COGS from manual Inventory entries** |
| NXT-68637 | Done Done | GL report = one workbook, per-account **sheets** | Final state exports **each account as a separate file** |
| NXT-68635 | Done Done | Tile labeled **"Profit & Loss"** | AC mandates tile name **"Revenue & Expenditure (P&L)"** |
| NXT-68294 | Done Done | Reversing-a-reversal = undocumented, "ask implementer" | AC **blocks** reversing a reversal + prefills a locked reason |
| NXT-67534 | Done Done | State template auto-populates segments | State is **pre-set and locked; user must click Apply Template**; adds replace-confirmation + Delete All Segments |
| NXT-67003 | New | Periods at **Configuration › Periods**, no per-site close | Periods under **System › Management › Periods** with per-site Close All / Reopen All |
| NXT-65009 | Done Done | Account Categories "have no codes" | Categories **can carry an optional code** (warns on format mismatch) |

**Highest-severity stale items (fix first):**
1. **The "posting is automatic / Approve-Post gone" reversal** (NXT-70065, 70066, 70069, 65487, 66123, 66386) — six tickets converge on undoing the guide's central promise. This is Cluster C1 and is the #1 correction. Even though all are upcoming, the guide states the *opposite* as a present-tense fact in three places (the "What changed" table, Job 10, the Glossary).
2. **"One-time" Opening Balance import** (NXT-71249, 71240) — guide says one-time; AC explicitly supports re-import with hard reversal + replacement warning. A customer told "one-time" will be afraid to correct a bad opening-balance file.
3. **Data-point count "~72"** (NXT-69959, and NXT-69097/69084 context) — appears in the "What changed" table, Job 2 vocabulary, *and* the Glossary. AC says 77 on the revenue side alone. Either soften to "about six dozen, organized by section" with a citation, or update — but the specific "~72" / "~248" figures need an AC anchor before they ship again.

> Note on shipped-vs-stale: several stale items are **Done Done** (NXT-69959, 69084, 68637, 68635, 68294, 67534, 65009). These are not "coming" — the *shipped* product already diverges from the guide. They are present-tense corrections, not (Coming) tags. The upcoming stale items (C1 wave, opening-balance, periods relocation) get (Coming) framing instead.

---

## Appendix — method notes

- **Job mapping** uses the `maps_to` field from the coverage rows, normalized to Job number. NXT-65000 appears under Job 6 in totals (straddles Job 2/6).
- **`none` bucket** = 19 tickets with no guide section. These drive the NEW-section clusters (C2 roles, C3 dashboard, C4 nav/licensing, parts of C6 posting engine, C7 promotional P&L PDF, C10 wizard intro).
- **Shipped = Done Done only.** This is deliberately strict. "Committed," "Testing," "Ready for Development," and "In Progress" are *not* shipped for the purpose of present-tense guide prose — a Committed report a customer can't yet open should read "(Coming)."
- **Coverage % is weighted and generous.** A stricter "fully covered only" reading would be 19/136 = 14%. The 38.2% figure credits the 66 partials at half each.
- All ticket-key citations above trace to the coverage-row notes; the drafting phase that consumes this report must re-ground every *behavior* claim to a verbatim AC quote per the project's grounding rules before any of it reaches customer-facing prose.
