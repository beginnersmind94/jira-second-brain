# AUDIT & CITATIONS — NXT Customer-Specific Cost Report (AY 2025/26)

*Companion to `NXT_customer_cost_GAMMA_brief.md`. Auto-generated from source on the data as loaded. Purpose: let any reviewer trace every figure to a Jira issue + field and reproduce the methodology.*

---
## A. Source data & reproducibility
- **Source of record:** `Perseus Jira (5).csv` — 3,661 NXT issues, full-field Jira export (745 columns).
- **Canonical scope query (run by the requester, reproduced here):**
  ```
  project = NXT AND issuetype in standardIssueTypes() AND created >= "2025-07-01" AND created < "2026-07-01" ORDER BY created ASC
  ```
- **Window verified:** all rows `Created` 2025-07-01 → 2026-06-02 (AY-to-date). Half-open interval; no sub-tasks (standardIssueTypes()).
- **MCP capabilities used:** `searchJiraIssuesUsingJql` (discovery/paging), `getJiraProjectIssueTypesMetadata`, `getJiraIssueTypeMetaWithFields`, `getVisibleJiraProjects`, `atlassianUserInfo`. **Not available in this MCP (flagged, not worked around):** native CSV export, saved-filter, bulk ops, custom-field discovery, JQL total counts. The CSV used here was supplied by the requester.
- **Field IDs:** Module = `customfield_10147` / CSV col "Custom field (Module)" (col 592). Acceptance Criteria = `customfield_10131` / CSV col 495 (col 494 is an empty duplicate). Comments = 38 "Comment" columns (scanned).
- **Reproduce:** `python jira-export/classify_final.py` (figures + deliverable CSVs) and `python jira-export/build_audit.py` (this doc). Candidate dumps: `classify_pass1.py`.

## B. Methodology & decision rules
1. **In-scope development denominator** = issue types Story + Enhancement + New Feature, created in window; **minus** migration dev-type stories (moved to migration program), **minus** dead "Ignore, old" tickets (NXT-67060, NXT-67061), **plus** genuine customer enhancements recovered from Task/Tech-Debt.
2. **Excluded from dev scope:** Bug (fixes), Tech-Debt (internal), Epic/Feature (containers), Sub-tasks (none present).
3. **Qualifies as customer-specific** only if (a) tied to a single named customer OR Freshdesk-originated, AND (b) an enhancement/new development. Classification was made by **reading Summary + Description + Acceptance Criteria + Comments per ticket** — never keyword-only.
4. **Request type:** FD (cites a Freshdesk ticket) / direct (named customer, no FD) / contractual (explicit contract language).
5. **Migrations** = held in a separate program bucket (services/implementation), excluded from both numerator and denominator so numerator ⊆ denominator.
6. **Cost rule:** $5,000 per qualifying ticket (as specified).
7. **"Completed"** = `Resolution = Done` ∪ `Status Category = Done` (union; `resolutiondate` not used — blank on ~11% of Done items).

## C. Figure-by-figure traceability (every number in the brief)
| Figure in brief | Value | How it is derived / where to check |
|---|---|---|
| Total NXT issues in window | 3,661 | row count of source CSV |
| In-scope dev denominator | 1,130 | 1143 Story/Enh/NewFeat − 12 migration-dev − 2 ignore + 1 recovered |
| Customer-specific enhancements | 27 | §D table (per-ticket verified) |
| Cost @ $5K | $135,000 | 27 × $5,000 |
| % of in-scope dev | 2.39% | 27 ÷ 1130 |
| Request-type split | 25 FD / 2 direct / 0 contractual | §D column "type" |
| Completed subset | 20 → $100,000 | Done union over the 27 |
| Full customer footprint | 249 | §G: union of FD/district/migration signal over all 3,661 |
| Footprint by type | Bug 124 / Story 34 / Task 74 / Enh 14 | §G |
| Migration program | 156 | §F: summary contains the word migration |
| Dilworth / Washburn | 57 / 46 items | §F by-customer |
| Tier: +fixes | 151 → $755,000 | 27 enh + 124 customer bugs |
| Tier: full footprint | 249 → $1,245,000 | union × $5K (ceiling) |

## D. The customer-specific enhancements — full evidence (the 27)
*Each row: the literal source text that drove the call. "type" F=Freshdesk, D=direct. Verify by opening the ticket or searching the CSV field named.*

| # | Ticket | Type | Customer | Module | Status | Cite | Literal evidence (field → text) |
|---|---|---|---|---|---|---|---|
| 1 | NXT-63908 | F | Carl Junction Schools | Inventory | Done Done | FD #287828 | *Description:* VI# without having to check unorderable items. Source of Issue: [https://primeroedge.freshdesk.com/a/tickets/287828\|https://primeroedge.freshdesk.com/a/tickets/287828\|smart-link] {quote}I keep getting a message that my vendor id number is |
| 2 | NXT-65504 | F | Adams 12 | Family Hub | Done Done | FD #289943 | *Description:* [https://primeroedge.freshdesk.com/a/tickets/289943\|https://primeroedge.freshdesk.com/a/tickets/289943] As an Adams 12 parent I want to use our custom app to view the online menus, how |
| 3 | NXT-65541 | F | — | Accountability | New | FD #289187/289213/289232/289234 | *Description:* Few feedback tickets: * [https://primeroedge.freshdesk.com/a/tickets/289187\|https://primeroedge.freshdesk.com/a/tickets/289187] → Inventory Period pointing at the wrong page, POS Periods does not exist. * [htt |
| 4 | NXT-66821 | F | — | Eligibility | Done Done | FD #295727/296439/314274 | *Description:* [https://primeroedge.freshdesk.com/a/tickets/295727\|https://primeroedge.freshdesk.com/a/tickets/295727] - trying to extend SNAP after having previously extended Medicaid [https://prime |
| 5 | NXT-67479 | D | Tullahoma | Financials | Done Done | named in Summary+AC | *Acceptance Criteria:* Tullahoma Financials enhancements PBIs : [https://dev.azure.com/Cybersoft-Technologies-Inc/PrimeroEdge%20Classic/_workitems/edit/108845\|h |
| 6 | NXT-67947 | F | — | Family Hub | Done Done | FD #302464/303154 | *Description:* ines, display the item in each category. Related tickets: # [https://primeroedge.freshdesk.com/a/tickets/302464\|https://primeroedge.freshdesk.com/a/tickets/302464] # [https://primeroedge.freshdesk.com/a/tickets/303154\|https://primeroedge. |
| 7 | NXT-68249 | F | Texas City | Menu Planning | Done Done | FD #303802 | *Description:* [^primeroedge.freshdesk.com_helpdesk_tickets_303802_print.pdf] |
| 8 | NXT-68250 | D | Texas City | Menu Planning | New | named in Summary | *Acceptance Criteria:* Need to Add |
| 9 | NXT-68256 | F | — | Eligibility | Done Done | FD #298990 | *Description:* Tickets: * [https://primeroedge.freshdesk.com/a/tickets/298990\|https://primeroedge.freshdesk.com/a/tickets/298990] → CEP Apps not getting included *requirements* * Sampling Page ** Add columns t |
| 10 | NXT-69292 | F | Hill City ISD | Menu Planning | Done Done | FD #308059 (comment) | *Comment:* 1/2/2026 11:40 AM;5d27f7699c0d030c2977fa5f;Ticket ID: 308059 - Freshdesk ticket status changed to : Development |
| 11 | NXT-69463 | F | Texas City | Menu Planning | Done Done | FD #303802 | *Description:* [^primeroedge.freshdesk.com_helpdesk_tickets_303802_print.pdf] |
| 12 | NXT-69492 | F | Adams 12 | Accountability | Done Done | FD #309264 | *Description:* FD# [[#309264] SC - Adams 12 - SchoolCafe - Oracle financial exports : Cybersoft PrimeroEdge\|https://primeroedge.freshdesk.com/a/tickets/309264] [ |
| 13 | NXT-69710 | F | — | Accountability | Done Done | FD #309797 | *Description:* [https://primeroedge.freshdesk.com/a/tickets/309797\|https://primeroedge.freshdesk.com/a/tickets/309797\|smart-link] !image-20260121-205658.png\|width=922,alt="image-20260121-205658.png |
| 14 | NXT-70214 | F | — | Accountability | Done Done | FD #308434 | *Description:* [https://primeroedge.freshdesk.com/a/tickets/308434\|https://primeroedge.freshdesk.com/a/tickets/308434\|smart-link] When a period is closed it should mean closed. We should not be allow |
| 15 | NXT-70215 | F | — | Accountability | Story Refinement/Efforting | FD #308434 | *Description:* [https://primeroedge.freshdesk.com/a/tickets/308434\|https://primeroedge.freshdesk.com/a/tickets/308434\|smart-link] In order to prevent data mismatches and confusion we need to lock dow |
| 16 | NXT-70265 | F | — | Account Management | Done Done | FD #311711 [recovered from Task] | *Description:* [https://primeroedge.freshdesk.com/a/tickets/311711\|https://primeroedge.freshdesk.com/a/tickets/311711\|smart-link] |
| 17 | NXT-70380 | F | — | Eligibility | Done Done | FD #267487 | *Description:* rimeroEdge%20Classic/_workitems/edit/99540/] {panel} Ticket: [https://primeroedge.freshdesk.com/a/tickets/267487\|https://primeroedge.freshdesk.com/a/tickets/267487] *Summary:* * Currently, surveys without identified students (students with |
| 18 | NXT-70381 | F | — | Family Hub | Done Done | FD #310993 | *Description:* FD: [https://primeroedge.freshdesk.com/a/tickets/310993\|https://primeroedge.freshdesk.com/a/tickets/310993] *requirements* * Ensure that all items that CAN be added to menus, and then pus |
| 19 | NXT-70424 | F | — | Accountability | Done Done | FD #305261 | *Description:* [https://primeroedge.freshdesk.com/a/tickets/305261\|https://primeroedge.freshdesk.com/a/tickets/305261] !image-20260220-190648.png\|width=371,alt="image-20260220-190648.png"! *requirem |
| 20 | NXT-70586 | F | — | Accountability | Done Done | FD #312058 | *Description:* Freshdesk: [https://primeroedge.freshdesk.com/a/tickets/312058\|https://primeroedge.freshdesk.com/a/tickets/312058] *requirements* * Remove the Status field from the Suspicious Transactions task |
| 21 | NXT-70587 | F | — | Accountability | Done Done | FD #311719 | *Description:* Freshdesk: [https://primeroedge.freshdesk.com/a/tickets/311719\|https://primeroedge.freshdesk.com/a/tickets/311719] As Dana the Director I need the Edit Check Worksheet to show total (highest) enr |
| 22 | NXT-71417 | F | — | Production | Done Done | FD #315146 (comment) | *Comment:* 77320c1f72591d] , We are committed to working on this FD request [https://primeroedge.freshdesk.com/a/tickets/315146\|https://primeroedge.freshdesk.com/a/tickets/315146\|smart-link] Please do the Assignment. |
| 23 | NXT-71744 | F | — | Platform - Data Exchange | Done Done | FD #316155 | *Description:* ts, particulary as it relates to PowerSchool. Freshdesk ticket: [https://primeroedge.freshdesk.com/a/tickets/316155\|https://primeroedge.freshdesk.com/a/tickets/316155] |
| 24 | NXT-71821 | F | — | Family Hub | Ready For Testing | FD #264863/279685 | *Description:* size configured for staff. Examples of tickets in Classic: [https://primeroedge.freshdesk.com/a/tickets/264863\|https://primeroedge.freshdesk.com/a/tickets/264863] [https://primeroedge.freshdesk.com/a/tickets/279685\|https://primeroedge.fre |
| 25 | NXT-72038 | F | Stillwater Area Schools | SCTV | New | FD #317174 | *Description:* read the daily menu in their primary language on the cafeteria display screens. *Context:* Freshdesk Ticket #317174 — Stillwater Area Schools #834 reported that while menus can already be viewed in Spanish on the SchoolCafe parent portal, t |
| 26 | NXT-72790 | F | Mankato | Item Management | Story Refinement/Efforting | FD #318430/321324 | *Description:* only the POS categories I create. * [FD Ticket 318420 (internal)\|https://primeroedge.freshdesk.com/a/tickets/318430] * [FD Ticket 321324 (Mankato)\|https://primeroedge.freshdesk.com/a/tickets/321324] Currently, the POS Item checkbox is for |
| 27 | NXT-73278 | F | Wadena-Deer Creek Public Schools | Accountability | In Progress | Freshdesk attachments + "District called" | *Description:* District called reporting Edit check flag on sessions for reduced. !https://attachment.freshdesk.com/inline/attachment?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MjIxOTA5MDk1MzMsImRvbWFpbiI6InByaW1lcm9lZGdlLmZyZXNoZGVza |

## E. Uncertain / judgment calls (the 9 — excluded from the 27)
| Ticket | Module | Status | Why excluded | Literal evidence |
|---|---|---|---|---|
| NXT-65573 | Accountability | Done Done | State-level (North Carolina) compliance; New Brunswick County Schools named only as example | *Description:* ull in the Edit Check Comments for the resolution in addition to any flagged edit check messages Example from New Brunswick County Schools old software's report: !https://dev.azure.com/Cybersoft-Techn |
| NXT-65729 | Family Hub | Done Done | FD #292500 (Benton SD) but a default-setting flip [Task], minimal dev | *Description:* ould be turned on !image-20250820-191204.png\|width=1132,height=177,alt="image-20250820-191204.png"! FD # [[#292500] SC Issue- Benton School District- Family Hub app issues : Cybersoft PrimeroEdge\|ht |
| NXT-67945 | Family Hub | New | FD-flagged but general configurable privacy setting; no single customer | *Description:* Contact/Phone/Email Information from the Support page}}_ *Mockup* N/A Related ticket: [https://primeroedge.freshdesk.com/a/tickets/301178\|https://primeroedge.freshdesk.com/a/tickets/301178] |
| NXT-68910 | Family Hub | Done Done | Q1 catch-all; only one sub-item (FD #307409) customer-driven | *Description:* .png\|width=670,alt="image-20260106-222817.png"! Related ticket: [https://primeroedge.freshdesk.com/a/tickets/307409\|https://primeroedge.freshdesk.com/a/tickets/307409] # Add a setting to hide paymen |
| NXT-69341 | Family Hub | Done Done | Austin ISD one complainant; shipped as 5 general settings for all districts | *Description:* lated to item translations that caused us to hide the custom allergens texts in the menu item details pop-up. Austin ISD complained that this information is no longer showing and they want to bring it |
| NXT-70309 | Financials | New | General GL posting-frequency feature; Adams 12 cited only as a use-case driver | *Acceptance Criteria:* : Aggregates all transactions by "Transaction Date" and "Bank Deposit Slip Number". ** Use Case: Supports the Adams 12 "Daily transactions ONLY" requirement. * *Option B: Monthly (Period Level)* ** Lo |
| NXT-70622 | Inspections | Done Done | Yotta/Clear Creek ISD app-crash FIX [Task] - customer-named but a fix, not enhancement | *Description:* 39] Yotta app crashes : Cybersoft PrimeroEdge\|https://primeroedge.freshdesk.com/a/tickets/310039] [[#312742] Clear Creek ISD - Yotta Real Contact : Cybersoft PrimeroEdge\|https://primeroedge.freshdes |
| NXT-71628 | Accountability | Done Done | General deposit/card feature; only alphanumeric Bank Deposit Slip # is Adams-12-specific | *Description:* , Josh* * Bank Deposit Slip # field needs to be updated to alphanumeric while we’re in there. ** This is for Adams 12 and their Oracle integration. |
| NXT-72140 | Eligibility | New | Federal 2026-27 eligibility guidelines (all districts/regulatory); FD #316868 referenced | *Description:* s that allows them to get the guidelines. * Ref Ticket: [+https://primeroedge.freshdesk.com/helpdesk/tickets/316868+\|https://primeroedge.freshdesk.com/helpdesk/tickets/316868] *Details* # Run a scrip |

*If the four strongest (NXT-70309, 71628, 69341, 65729) were counted, the headline would move to 31 items / $155,000 / 2.7%.*

## F. Migration program (separate bucket)
- **156 items** whose summary references a migration. By type: Bug 100 · Task 43 · Story 12 · Feature 1.
- **By named customer:** Dilworth 57 · Washburn 46 · Mankato 5 · Anchorage 3.
- Observed migration tickets per district (summary-keyword count): **Dilworth 57 (~$285K) · Washburn 46 (~$230K) · Mankato 5 · Anchorage 3** — range ~3–57 (~$15K–$285K). The ~$250K figure is the *two largest*, not a per-district average; status is mixed (not all certified complete).
- Full list: `nxt_migration_program_categorized.csv`.

## G. The 249 footprint (how the "real cost" number is built)
- **Definition:** any of the 3,661 issues whose full text contains a Freshdesk reference, a known district name, or "migration" in the summary. Union, de-duplicated by issue.
- **Result:** 249 issues — Bug 124 · Task 74 · Story 34 · Enhancement 14 · Tech-Debt 2 · Feature 1.
- **Confidence:** this is a **signal-based ceiling**, NOT per-ticket verified. It includes example-district mentions and "freshdesk-as-a-forum" false positives (e.g. NXT-67944). The verified figure is the 27; the footprint brackets the upper bound.

## H. Forward pipeline & scenario (assumptions exposed)
- **Source:** 93 Freshdesk customer conversations (`conversations_batch.json`). Districts parsed from subjects.
- **Distinct districts in the FD onboarding/issue stream:** 31. Only **Mankato** appears in NXT migrations to date.
- **Top by engagement (tickets / turns = friction proxy):**
  - Southwest ISD: 13 tickets, 135 turns
  - Healdsburg Unified School District: 5 tickets, 61 turns
  - Old Colony Regional: 4 tickets, 35 turns
  - Suffolk City Public Schools: 3 tickets, 29 turns
  - Mankato Area School District ISD: 3 tickets, 26 turns
  - Waller ISD: 3 tickets, 51 turns
  - Carl Junction Schools: 3 tickets, 74 turns
  - Mashpee Public Schools: 2 tickets, 18 turns
  - Mexico School District: 2 tickets, 19 turns
  - Cybersoft USD: 2 tickets, 11 turns
- **Scenario math:** ~$250K per *large* district (the two largest observed) × {8, 15} = $2.0M / $3.75M. **Assumptions (explicit):** (a) magnitude depends on district size mix — small districts ran ~3–5 tickets (~$15–25K), so $2–3.8M is a high-volume-weighted ceiling, not a midpoint; (b) not all FD-active districts become full 2.0 back-office migrations; conversion rate unknown. Planning range, not a forecast.
- **Onboarding-blocker concentration (FD tickets touching each area):** Item Management 35 · Menu Planning 28 · Production 13 · Contract Items/Vendors 9 · Eligibility/POS/Permissions ~0.

## I. Freshdesk cross-check
- 93 FD conversations cross-referenced against NXT. Only ~10 NXT issues cite a batch FD id (most FD volume resolves in support/training, not dev) — consistent with a small enhancement count.
- Hidden customer names resolved: **FD#287828 → NXT-63908 = Carl Junction Schools**; FD#315146 → NXT-71417 (SC Training origin).
- Business-signal scan of all 93: **0** go-live/deadline/escalation/churn/contract-with-customer hits, **0** "Dallas" mentions. The 3 "contract" hits were the vendor-contract-items *feature*. (Stated so the brief claims no urgency the data lacks.)

## J. Known limitations (restated for audit)
- **Created-based & AY-to-date** (through 2026-06-02) — not full-year, not completion-based. A `resolutiondate` view would shift edges.
- **No structured Customer/Contract/State field** in NXT (all blank) — customer-specificity is text-derived; hence the explicit Uncertain list.
- **Some specs live in Azure DevOps** (e.g. NXT-67479 Tullahoma) — unreadable from the CSV; classified from available text.
- **$5K/ticket is uniform** — ignores effort and phase-splits (Planning/Development/Delivery trios).
- **Name variants** (e.g. Mankato in 4 spellings) can fragment customer rollups; counts here use distinctive tokens.
- **249 footprint & forward-wave $ are estimates**, labeled as such; the 27/$135K/2.4% are per-ticket verified.

## K. Deliverables index
- `NXT_customer_cost_GAMMA_brief.md` — the 2-page brief (Gamma input)
- `nxt_customer_specific_AY2025-26.csv` — the 27 qualifying, with evidence
- `nxt_uncertain_AY2025-26.csv` — the 9 judgment calls
- `nxt_migration_program_categorized.csv` — the migration items, categorized
- `nxt_classification_all_inscope.csv` — all 1,143 dev tickets labelled (full audit trail)
- `classify_final.py / classify_pass1.py / build_audit.py` — reproducible scripts
- `Perseus Jira (5).csv` — source of record