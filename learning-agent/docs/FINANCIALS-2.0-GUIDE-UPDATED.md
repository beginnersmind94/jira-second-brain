# Financials 2.0 · Internal Training

# Onboarding, Without the Yawn

*A jobs-to-be-done guide for the district finance and child-nutrition staff bringing Financials 2.0 online — and for the Cybersoft implementers walking them through it.*

**11 Jobs to be Done · 90-Day Cheat Sheet**

SchoolCafé · Cybersoft Implementation Team · April 2026 Edition

---

> ## What this update covers
>
> This edition has been brought up to date against the **136-ticket Financials backlog** (Perseus Jira capture), using the Learning Studio **coverage + grounding gates**: every new or changed product-behavior claim traces to a verbatim quote from a ticket's Acceptance Criteria, carried in an inline `<!-- Source: NXT-####:AC "…" -->` comment.
>
> **"(Coming)" tags mark features that are specified but not yet shipped.** A line tagged **(Coming)** describes agreed, in-development behavior — a backlog story, not a screen you can open today. Live, shipped behavior is written in the present tense with no tag. Read the tags, not just the headings: if you go looking for a (Coming) feature and it isn't on your screen, the guide isn't wrong — the feature hasn't shipped yet.
>
> New since the last edition: a **Financial Dashboard** landing view (Job 0), a **roles & permissions** plan (Job 11, Coming), a deep-dive into **what posting actually writes to your ledger** (expanding Jobs 2/8/10), and a full **P&L build-out** (expanding Job 9). The Job 10 "posting is automatic / Approve-Post buttons gone" story has been **qualified** — those statements are true for the first 2.0 build, but manual Post / Repost controls and a Review/Post-All queue are returning as an option (Coming).

---

## Who this is for

District finance and child-nutrition staff getting started in Financials 2.0 (CN Director, Finance Manager / Director, Business Administrator, accountants who'll touch the ledger). Also for: Cybersoft implementation staff onboarding a district. Look for the 🔧 callouts — those are yours.

One thing to remember before you start: **Financials is a downstream module.** It reads what POS and Inventory hand it. It never invents source data, it never modifies it, and it can't post until upstream periods are closed.

## How to read this guide

It's organized by jobs you're trying to get done — not by menus. Each section is short on purpose. Skim the TL;DRs, drop into the section that matches what you're doing today, and come back when the next one becomes your problem.

---

## What actually changed in 2.0 (read this first — 90 seconds)

| You used to… | Now you… | Why it matters |
|---|---|---|
| Click **Approve** then **Post** on three separate pages every period | Do nothing. Posting fires the moment the upstream POS or Inventory period closes — *for the first 2.0 build* (manual Post / Repost controls are **(Coming)** back as an option; see Job 10). | You can no longer "forget to post." But you also can't post early. Mapping must be complete or nothing posts. |
| Have your CoA import rejected because one account code was off | Get a non-blocking import. Bad codes flag a warning; the rest land cleanly | Fix issues iteratively instead of being stuck in a reject-fix-reupload loop. |
| Map ~248 system accounts on the revenue side, even programs you don't run | Map ~72 data points, deactivate what you don't use, bulk-map the rest by section | Phase 1 of mapping is deletion, not data entry. |
| Manually do a "Pay Refunds" entry to clear the refunds-liability bucket | Get one balanced entry, no liability parking | Fewer accounts to manage. No accidentally orphaned liabilities. |
| Get a "dirty" flag on the financial period whenever POS reopened, even if nothing changed | See exactly what changed when source data is re-closed; auto-adjust if you opt in | No more pointless reposting. |
| Run reports against live data that drifted from what was posted | Generate reports from posted ledger entries only — async, downloaded from Document Center | The numbers in your report match the numbers in your ledger. Always. |
| Have a flat list of revenue accounts to map | Map by eligibility × program with bulk actions and a Program filter | Map all NSLP revenue in one click. |
| Create a separate GL Entry Type for every audit adjustment shape | Use one Template Entry that allows the same account on both debit and credit sides | Auditors can do anything they need without a support ticket. |

<!-- C1 refresh: the following rows qualify the present-tense "gone/automatic" claims the live guide states as fact. Source tickets are status New → tagged (Coming). The shipped-first anchor is NXT-69493 (Done Done). -->

> **Update — the Posting Activity Log story is being qualified (see Job 10).** The audit flagged the rows below as stating the *opposite* of what's coming as present-tense fact. The "Shipped first in 2.0" column keeps what shipped; the "(Coming)" column qualifies it.

| Area | Shipped first in 2.0 | (Coming) — qualify the "gone / automatic" claim |
|---|---|---|
| Posting trigger | Posting runs in the background; manual trigger is out of scope on the Activity Log page. <!-- Source: NXT-69493:AC "*Manual trigger*: Out of scope — jobs triggered from Fiscal Periods page, not here." --> | A manual **Ready to Post** queue (**Review / Post All**) returns on the Activity Log. <!-- Source: NXT-70065:AC "two actions: Review and Post All" --> |
| Summary cards | Four cards: Total Jobs / Completed / Failed / Running. <!-- Source: NXT-69493:AC "*Summary cards*: Four cards at top — Total Jobs (30 Days), Completed (green), Failed (red), Running (orange)." --> | **Three** cards (Posting Progress / Needs Attention / Posted This Period) replace them; the counts move to the table header. <!-- Source: NXT-70066:AC "Replace the four Phase 1 cards (Total Jobs, Completed, Failed, Running) with three cards in a horizontal grid" --> |
| Approve / Post buttons | Removed; the page is a read-only monitor. <!-- Source: NXT-69493:AC "*Manual trigger*: Out of scope — jobs triggered from Fiscal Periods page, not here." --> | **Post / Repost / Remove** return per site on the POS and Inventory grids. <!-- Source: NXT-65487:AC "*Actions* (Post, View, Repost, Remove)" --> <!-- Source: NXT-66123:AC "*Actions* (Post, View, Repost, Remove)" --> |
| "You can't forget to post" | Automatic posting means you don't have to remember. *(Keep, but qualify.)* | If automatic posting is off, a **"You're posting manually"** nudge banner appears. <!-- Source: NXT-70069:AC "Banner text: \"You're posting manually. Districts with automatic posting enabled only visit this page when something needs attention.\"" --> |

---

## Before you touch the product

You can't shortcut these. Lock them down before login.

1. **Account code structure** — How long are your segments? What does each represent? If your state publishes a standard (Texas FASRG, etc.), have it open. If you have a custom structure, get the segment definitions in writing from your ERP team.
2. **Your chart of accounts, exported from your ERP** (Oracle, Tyler Munis, etc.) — You'll fill the GL Accounts Import template with this. The template lives at Configuration › General Ledger Accounts › Import.
3. **Two short answers** — Have these on hand. They'll save hours later:
   - Which meal programs do you actually run? (NSLP, SBP, Special Milk, CACFP, SFSP, etc.) — You'll deactivate everything else.
   - How many distinct GL accounts do you post meal sales revenue to? — For most districts, the answer is "one or two." That answer drives whether mapping takes 5 minutes or 5 hours.
4. **The imports themselves have to be turned on first.** Before any customer can run the GL Accounts Import (Job 1), the Opening Balance Import (Job 5), or the Payroll journal-entry import, each one has to be registered as an import type in the platform's Imports & Exports area first. Until that registration happens, the import type the customer expects won't appear on the picklist when they click the Import button.

Where the registration happens: **Imports & Exports › Imports tab › Add New.** For each import (GL Accounts, Opening Balance, Payroll), the implementer:
- Adds the import to the picklist of import types
- Sets the accepted file format (`.xlsx` / `.xls` / `.csv`)
- Defines required columns and column mappings (e.g. for GL Accounts: Account Code, Account Description, Account Category, Account Base Type)
- Confirms the help-tooltip text the customer will see at upload time

After registration, customers see "GL Accounts Import," "Opening Balance Import," and (when in scope) the payroll journal-entry import as available options when they hit the Import button in Configuration. Without registration, they don't.

> 🔧 **Implementer:** Send the GL Accounts template to the customer at kickoff. The customer's ERP team typically needs lead time to pull a clean chart of accounts. Also confirm the site-code segment length matches the actual site codes on the Sites page — the system pads with leading zeros if a site code is shorter than the segment length.

> 🔧 **Implementer:** Register all three import types during environment setup, even the ones the customer won't use until later. Opening Balance is needed in week 3; Payroll often comes after go-live. Treat import-type registration as part of "stand up the environment," not "start onboarding the district."

---

<!-- ============================================================ -->
<!-- C3 — NEW SECTION (Job 0, Financial Dashboard). Slots before Job 1. -->
<!-- NXT-68659 = Done Done => SHIPPED (present tense). NXT-68660 = Story Refinement => (Coming). -->
<!-- ============================================================ -->

# Job 0 — "See where my district stands the moment I log in" (Financial Dashboard)

> **Where this slots in.** This is a new section for the guide. Logically it sits *before* Job 1 as a landing / "at-a-glance" job — it's the screen a director reads, not a setup task they perform. It is distinct from Job 9 (Reports), which produces downloadable board/auditor files. **Open question for SME:** the guide should state the exact menu path / screen name for this dashboard. NXT-68659 AC calls it "the dashboard" and "the Financial Dashboard" but never states its navigation path, so none is asserted here.

**TL;DR:** The Financial Dashboard is your single-glance scoreboard — Net Income, Total Revenue, and Total Expenses for a period you pick at the top right, a trend arrow that tells you if the district is improving month over month, and a table breaking the numbers down site by site.

**When this is your job:** Login, day one and every day after. For a CN Director or Business Administrator this is usually the first screen you land on — read it before you drop into the setup Jobs below.

**Status:** ✅ **Shipped today.** Everything in this section is live unless explicitly tagged **(Coming)**.

## The three KPI cards (the top of the page)

The dashboard leads with Net Income, Total Revenue, and Total Expenses for whatever period you've selected. <!-- Source: NXT-68659:AC "Changing the period recalculates Net Income, Total Revenue, and Total Expenses and updates the card label (e.g., \"Net Income (June 2025)\")." -->

- **Net Income** is the headline number, shown big with dollar formatting and comma separators. <!-- Source: NXT-68659:AC "Main Net Income number is shown in large text with currency formatting and thousands separators." --> It's simply Total Revenue minus Total Expenses, and if the district is in the red it shows with a minus sign (e.g. `-$125,000`). <!-- Source: NXT-68659:AC "Net Income = Total Revenue – Total Expenses; if negative, show with a minus sign (e.g., -$125,000)." -->
- **Total Revenue** and **Total Expenses** sit underneath as smaller numbers, each rounded to the nearest whole dollar. <!-- Source: NXT-68659:AC "Total Revenue and Total Expenses are shown below as smaller values, rounded to the nearest dollar." -->
- The card's title carries the period in parentheses so you always know what window you're reading — e.g. "Net Income (June 2025)." <!-- Source: NXT-68659:AC "Changing the period recalculates Net Income, Total Revenue, and Total Expenses and updates the card label (e.g., \"Net Income (June 2025)\")." -->

**What the numbers are built from:** posted General Ledger transactions only — the same posted-ledger truth the rest of 2.0 runs on. <!-- Source: NXT-68659:AC "Data source is posted financial transactions from the General Ledger." --> Every active site is rolled in, <!-- Source: NXT-68659:AC "Calculations include all active sites." --> and only accounts whose base type is Revenue or Expense count toward the totals. <!-- Source: NXT-68659:AC "Only GL accounts with base type Revenue or Expense are included." -->

> ⚠️ **Empty period reads as zero, not blank.** If there are no posted Revenue or Expense transactions in the period you picked, that side shows **0** and Net Income is calculated treating it as zero — the card won't go blank or error out. <!-- Source: NXT-68659:AC "If there are no posted Revenue or Expense transactions in the selected period, show \"0\" for the respective column and calculate net income assuming it’s value as zero." -->

## The period selector (top right)

Pick your reporting window from the **"Period:"** dropdown in the top-right corner of the dashboard. <!-- Source: NXT-68659:AC "Period selector is a standard dropdown labeled “Period:” in the top right of the dashboard." --> Your options are Current Month, Current Quarter, Current Fiscal Year, and a Custom Range. <!-- Source: NXT-68659:AC "Period options: Current Month (MMM YYYY), Current Quarter (Q# YYYY), Current Fiscal Year (FY YYYY), Custom Range." --> When the dashboard loads it defaults to **Current Fiscal Year** as of today, so you open to a year-to-date picture without touching anything. <!-- Source: NXT-68659:AC "Default period on dashboard load: Current Fiscal Year (FY ) as of today." -->

A few things worth knowing about how the windows are defined:

- The **Current Fiscal Year** range comes straight from your Fiscal Year Settings (the start and end dates you configure in Job 4). <!-- Source: NXT-68659:AC "Current Fiscal Year date range comes from Fiscal Year Settings (start and end dates)." --> **Current Month** is the 1st through the last day of this calendar month, within the fiscal year that contains today. <!-- Source: NXT-68659:AC "Current Month = 1st to last day of the current calendar month, within the fiscal year that includes today." -->
- **Current Quarter** uses your *fiscal* quarters (Q1–Q4), not calendar quarters — again defined by Fiscal Year Settings. <!-- Source: NXT-68659:AC "Current Quarter uses fiscal quarters (Q1–Q4) defined by Fiscal Year Settings." --> Every "Current …" option stays inside the active fiscal year. <!-- Source: NXT-68659:AC "All “Current …” options must fall inside the active fiscal year" -->
- The Current Month, Quarter, and year-to-date ranges are **system-defined — you can't hand-edit them**; pick Custom Range when you need your own dates. <!-- Source: NXT-68659:AC "Period date ranges for the quarter, year-to-date and current month are system-defined and not user-editable." -->

> ⚠️ **Open vs. closed periods don't gate the dashboard.** The totals include every posted transaction whose posting date falls in your selected window — **even if that fiscal period is still open.** <!-- Source: NXT-68659:AC "Include all posted transactions whose transaction/posting date falls within the selected period, even if the fiscal period is still open." --> So the dashboard can move during an open period as new postings land; that's expected, not a bug.

> 🔧 **Implementer:** The dashboard's "Current" windows are only as right as the customer's Fiscal Year Settings, because that's literally where the ranges come from. <!-- Source: NXT-68659:AC "Current Fiscal Year date range comes from Fiscal Year Settings (start and end dates)." --> Walk Job 4 (Open my fiscal year) *before* you point a director at this screen — a fiscal year that's off by a month makes every "Current Quarter" number look wrong.

## The trend arrow (am I improving?)

Next to Net Income you'll see a small trend arrow. It compares Net Income for the **latest completed fiscal month** against the month right before it. <!-- Source: NXT-68659:AC "Trend arrow compares Net Income for the latest completed fiscal month vs the immediately previous fiscal month." --> "Completed" means a fiscal month that has fully passed in real time — the current, still-running month doesn't count yet. <!-- Source: NXT-68659:AC "A completed month = a fiscal month that has fully passed in real time." -->

- Up if the latest month beat the previous one, down if it came in lower, and **no arrow at all if they're equal.** <!-- Source: NXT-68659:AC "If latest > previous show ↑; if less show ↓; if equal show no arrow." -->
- Brand-new districts won't see an arrow until there are two completed fiscal months on the books — with fewer than two, it's hidden. <!-- Source: NXT-68659:AC "Hide arrow if fewer than two completed fiscal months exist in the current fiscal year." -->

> ⚠️ **The arrow ignores the period dropdown.** Changing the period selector at the top **does not** change what the arrow compares — it always looks at the two most recently completed fiscal months, no matter what window the KPI cards are showing. <!-- Source: NXT-68659:AC "Trend arrow is not affected by the selected reporting period." --> If that's confusing on screen, the tooltip says it out loud: *"Trend compares the two most recently completed fiscal months."* <!-- Source: NXT-68659:AC "Tooltip: *“Trend compares the two most recently completed fiscal months.”*" -->

## The site-by-site table

Below the cards is a table that breaks the same numbers out per site: Revenue, Expenses, and Net Income (Revenue minus Expenses) for each active site, with a district total row at the bottom. <!-- Source: NXT-68659:AC "Site-by-site performance table shows Revenue, Expenses, and Net Income (Revenue – Expenses) for each active site, plus a district total row at the bottom." --> The columns are Location, Revenue, Expenses, and Net Income, <!-- Source: NXT-68659:AC "Columns: Location, Revenue, Expenses, Net Income." --> and the bottom roll-up row carries your district name in the Location column. <!-- Source: NXT-68659:AC "For the district-level entry, use the district name." -->

How it behaves:

- It reads the **same period** you picked at the top and, like the cards, uses **posted GL transactions only.** <!-- Source: NXT-68659:AC "Table uses only posted GL transactions and the same selected period as the dashboard." -->
- It's sorted by **Net Income, highest first**, with Location name as the tie-breaker. <!-- Source: NXT-68659:AC "Default sort is Net Income descending; secondary sort by Location name." -->
- **Inactive sites never appear** — only active sites are listed. <!-- Source: NXT-68659:AC "Only show *active* sites; do not display inactive sites." -->
- A site with no numbers for the period shows a dash (**–**) in its numeric columns. <!-- Source: NXT-68659:AC "Sites with no data show “–” in numeric fields." -->

> ⚠️ **A dash in Net Income means data is missing, not that the site broke even.** Net Income only fills in when **both** Revenue and Expense totals exist for that row; if either is missing, the cell shows **–**. <!-- Source: NXT-68659:AC "Net Income only appears when both Revenue and Expense totals are present; otherwise show “–”." --> The tooltip explains why: *"Net Income is unavailable because Revenue and/or Expenses are missing for this period."* <!-- Source: NXT-68659:AC "Tooltip: *“Net Income is unavailable because Revenue and/or Expenses are missing for this period.”*" --> Don't read a dash as a zero.

### (Coming) Refinements to the site table

A follow-up refinement (NXT-68660, in refinement — **not yet live**) sharpens this same table. When it ships you'll be able to:

- **(Coming)** Sort the table by site name as well as by Net Income — Net Income descending stays the default. <!-- Source: NXT-68660:AC "Sortable by Net Income (default: descending)" --> <!-- Source: NXT-68660:AC "Also by site name" -->
- **(Coming)** Read an aggregated district total row at the bottom of the table. <!-- Source: NXT-68660:AC "Aggregated district total row at the bottom." --> *(Interpretation: this restates the district total row that NXT-68659 already ships; NXT-68660 is the refinement that owns it going forward.)*

The refinement keeps the same ground rules you already know: posted GL transactions only, <!-- Source: NXT-68660:AC "Only posted GL transactions included." --> active sites only, <!-- Source: NXT-68660:AC "Only show data for active sites" --> a dash in every column for any site with no data in the selected period, <!-- Source: NXT-68660:AC "Show {{- }}in all columns." --> and it filters on the same period dropdown at the top of the dashboard. <!-- Source: NXT-68660:AC "Uses the *selected period* from the period dropdown at the top of the dashboard" -->

> 🔧 **Implementer:** Two "Top revenue sources" and "Top expense categories" analysis cards were *considered* for this dashboard and then **cut** — they're struck through in NXT-68660's Acceptance Criteria. Don't promise a customer revenue/expense ranking cards on the dashboard today; that scope was removed. (Reporting-level revenue/expense detail lives in the P&L work — see Job 9.)

## What this is *not*

- It is **not** a report you download. The dashboard is a live on-screen read; the downloadable board/auditor files live in Job 9 (Reports), which generate from posted ledger entries and arrive through the Document Center.
- It does **not** include unposted activity beyond what's already posted to the GL. Like everything in 2.0, the dashboard's truth is the posted ledger. <!-- Source: NXT-68659:AC "Data source is posted financial transactions from the General Ledger." -->

> **Open questions for SME (do not ship as fact — AC does not state these):**
> 1. Menu path / screen name for the Financial Dashboard. NXT-68659 AC names it "the dashboard" / "Financial Dashboard" but gives no navigation path. Confirm before publishing a path.
> 2. Whether the dashboard is one of the role-gated surfaces (see Job 11 roles, NXT-66927/66928/66929). AC for NXT-68659 says nothing about who can see it; do not assert visibility-by-role here.
> 3. Exact on-screen wording of the trend up/down indicator (arrow glyph vs. label). AC specifies ↑ / ↓ / "no arrow" behavior but not a text label; left as "up / down arrow" rather than inventing one.

---

# Job 1 — "Get my chart of accounts into the system"

**TL;DR:** Define the account code structure → import your CoA from the ERP → fix any flagged accounts in place.

**When this is your job:** Day 1. Nothing else works without it.

**Prerequisite:** The GL Accounts Import has to be registered in Imports & Exports first (see Before-You-Touch step 4). If "GL Accounts Import" doesn't show up when you click the Import button, registration hasn't happened yet — flag it to your implementer.

**What it looks like:**

Configuration › General Ledger Accounts has three tabs. Visit them in order:

1. **Account Code Structure.** Pick your state from the dropdown — if your state has a public standard, segments auto-populate. Otherwise build segments manually: name, position, length. Save.
2. **Account Categories.** These are groupings (Salaries & Benefits, Food Costs, etc.) — not GL accounts. They have no codes. They exist to organize your CoA for reports. Optional — you can skip them and let the system auto-assign by base type when you import.
3. **Individual GL Accounts.** Click Import › GL Accounts Import. Required columns: Account Code, Account Description, Account Category, Account Base Type. Upload.

**What you'll see when it works:** A grid of accounts. Anything that didn't match the structure shows a yellow warning icon — an "X accounts need structure corrections" banner appears at the top with a count. The import still succeeded.

**Watch out:**
- Warnings don't block the import, but they will cause export problems with your ERP later. Resolve before you start mapping.
- Account Code is treated as a string during import to preserve leading zeros and your district's segment formatting exactly. Don't let Excel quietly convert a column to numbers and chop your zeros.
- Once a transaction posts to an account in a category, the category's Base Type is locked forever. You can't accidentally re-classify Cash as Revenue six months in.
- If you skip Account Categories in the import, every account gets assigned to its base-type default (Asset → "Asset" category, etc.). Reclassify later — no rush.

**What's renamed from legacy:**
- "GL Code Segments" → Account Code Structure
- "Parent Accounts" → Account Categories

> 🔧 **Implementer:** Walk the customer through resolving warnings live. Unresolved structure mismatches don't block the import, but they do cause ERP export problems downstream.

---

# Job 2 — "Tell the system where to post each kind of transaction"

**TL;DR:** Subtract first, then map. Deactivate programs you don't run, then bulk-map what's left, then override the few exceptions.

**The vocabulary you need:**
- **Data points** are the buckets of financial activity Financials collects from across SchoolCafé — meal sales by eligibility, reimbursements by program, inventory transactions, prepaids, etc. They replace "system accounts" in legacy. There are ~72 of them, organized by section (Assets, Liabilities, Revenue, Expenses) and grouped within each section.
- **Mapping** = picking which of your imported GL accounts each data point posts to.

**Where:** Configuration › Account Mapping.

### Phase 1 — Subtract (5 minutes)

1. Filter by Program at the top of the page.
2. For each program your district doesn't run: click Bulk Actions, use the section-level checkbox to grab everything, then Deactivate All in the floating action bar.
3. Confirm. Repeat per program.

The data points for programs you don't run drop out of the active list.

### Phase 2 — Bulk-map by section (5 minutes)

1. Still in Bulk Actions mode. Select all groups in Revenue.
2. Click Map All in the floating action bar.
3. Pick the GL account from the typeahead (only Revenue-type accounts appear — base-type filtering is enforced).
4. Apply. Repeat for Assets, Liabilities, Expenses.

> ⚠️ Map All only works inside one section. Cross-section selection grays the button out. This is intentional — base types must match.

### Phase 3 — Override the few that aren't routine (10 minutes)

Exit Bulk Actions. Expand the relevant group. Use inline edit on the rows that need a different account than your bulk pass set. Common: NSLP reimbursements posting to a different account than other reimbursements; food vs. non-food inventory expenses.

### Phase 4 — Custom data points (only if you need them)

Pre-installed payroll already splits Salaries / Wages / Benefits / Overtime. If you need more granularity, click Add Data Point and define a journal entry template (debit account + credit account). Validation: debit and credit must balance and at least one side must reference the data point itself.

Click Save Changes. All changes commit at once and show in the configuration history.

> ⚠️ **Critical — every active data point must always be mapped.** The posting engine checks every active mapping before any job runs. One unmapped active data point halts all posting (POS, Inventory, Reimbursements). If you don't need a data point anymore, deactivate it. Don't just remove the mapping.

> 🔧 **Implementer:** The two prep questions ("which programs do you run?" and "how many GL accounts for meal sales?") drive everything. Ask them on a screen share before the customer touches this page so they can use Bulk Actions instead of mapping row by row.

<!-- ============================================================ -->
<!-- C6 — Job 2 prerequisite: Valuation Categories. NXT-65482 (Story Refinement) => (Coming). -->
<!-- ============================================================ -->

### Phase 5 — (Coming) Set up Valuation Categories before any inventory can post

> ⚠️ **All of this is (Coming).** Inventory posting (Job 8/10 deep-dive, Part B) does not run yet. But the mapping that gates it belongs here in Job 2, so set it up when this ships — it's a prerequisite, not an afterthought.

🎯 **The job:** tell Financials how each kind of inventory is valued and which GL accounts it should hit — *before* any inventory can post.

A Valuation Category cannot be used in postings until it has **both** an Asset account (for inventory value) and an Expense account (for usage) mapped. <!-- Source: NXT-65482:AC "Every valuation category must have *both* an Asset Account and an Expense Account mapped before it can be used in postings." --> Both account fields start blank and you fill them from a searchable dropdown of your GL accounts. <!-- Source: NXT-65482:AC "Asset Account (GL account for inventory value) (this is blank and to be filled in by the user, make it a searchable dropdown of all GL accounts so they can pick the relevant one)" -->

The page shows, per category: the category name, its **valuation method** (such as FIFO, Last Received Price, Moving Average, Replacement Value, or Standard Price), the Asset account, the Expense account, and the data source. <!-- Source: NXT-65482:AC "* Valuation Category ** Valuation Method (e.g., FIFO, Last Received Price, Moving Average, Replacement Value, Standard Price) ** Asset Account ... ** Expense Account ... ** Data Source (e.g., Local, State Level, Food Distribution)" -->

⚠️ **Watch-outs that bite later:**

- **One account, one category.** Each asset or expense account can be linked to **only one** Valuation Category. <!-- Source: NXT-65482:AC "Each asset and expense account can only be linked to one valuation category." -->
- **Mapping changes are not retroactive.** Changing a category's accounts or valuation method affects **future postings only** — it never restates what's already posted. <!-- Source: NXT-65482:AC "Changes to account mappings or valuation method only affect *future postings* and do not retroactively change historical posted values." -->
- **Once it's posted, it's locked.** After a Valuation Category has any posted activity, its Asset and Expense accounts are **permanently locked**; to use different accounts you create a *new* category and move items to it. <!-- Source: NXT-65482:AC "Once a valuation category has any posted activity, its Asset and Expense GL accounts become permanently locked and cannot be edited." --> <!-- Source: NXT-65482:AC "If a district needs to change the GL accounts, they must create a new valuation category and begin using that going forward; historical categories remain frozen for audit integrity." --> The system warns you when you hit this. <!-- Source: NXT-65482:AC "Provide warning 'This valuation category already has posted activity, so its GL accounts can't be changed. To use different accounts, create a new valuation category and move the items to it. Historical mappings are locked for audit integrity.'" -->
- **You can't orphan a mapped account.** If you try to delete an asset or expense account that's linked to a category, the system blocks it and tells you to assign a different account first. <!-- Source: NXT-65482:AC "If the user tries to delete an asset or expense account linked to a valuation category on the GL Accounts page, block it and inform the user that they must first assign a different account to that valuation group" -->

> 📌 **Open question (label):** AC sources this data from "Item Management > Item Configuration > Valuation Categories" but does not state the exact in-Financials menu path or page title a user clicks to reach the mapping view. <!-- Source: NXT-65482:AC "Data is sourced from Item Managemnt > Item Configuration > Valuation Categories" --> Confirm the customer-facing navigation label with the SME before publishing.

---

# Job 3 — "Decide whether to track prepaids/refunds by site or by district"

**TL;DR:** One radio button. Pick the model your ERP already uses.

**Where:** Configuration › Settings › Posting Settings.

**The choice:**
- **Distributed (Enrollment Site)** — default. One entry per site per period for prepaids, bonuses, refunds, and account transfers. Choose this if your ERP reconciles prepaid balances by school.
- **Centralized (District Office)** — one combined entry at the central office level. Choose this if your ERP has a single district prepaid liability account.

**What it affects:** Pre Payment (POS + Online), Bonus, Refunds, Returned Checks, Returned Check Fees, Account Adjustments, Account Transfer In/Out. It does not change how meal sales or reimbursements post — those are always per-site.

**Watch out:**
- Switching modes shows a confirmation dialog. The change is forward-only — already-posted entries don't restate.
- Centralized uses your Central Office site code from Site Configuration. If none is defined, the system uses all zeros (matching your site-code segment length).

> 🔧 **Implementer:** Ask the customer: "How do you reconcile prepaid balances in your ERP — by school, or one bucket?" That answer determines the setting. The mode can be changed later, and only affects future entries.

---

# Job 4 — "Open my fiscal year so I can actually start"

**TL;DR:** Enter FY start/end + frequency. The system generates the periods. Move on.

**Where:** Configuration › Periods.

**What you do:**
1. Enter fiscal year start and end (e.g. July 1 – June 30 for Texas).
2. Pick a frequency: Weekly, Biweekly, Semi-monthly, or Monthly. Monthly is most common.
3. Save. Periods populate, all in Open state.

**What "Open" vs. "Closed" means:**
- **Open:** manual entries allowed, automated posting flows in.
- **Closed:** manual entries blocked. Source data (POS / Inventory) keeps flowing in regardless — the period just gets a "dirty" indicator if upstream changes after you closed it.

**The one toggle you should know about: Automatic Entry Adjustments.** Default: off. When off, if a closed POS or Inventory period gets reopened and reclosed with different numbers, the system tells you what changed and waits for your review before adjusting. When on, the system auto-reverses and reposts. The history drawer shows every status change with timestamps.

**Locked after first save:** Fiscal year dates and period frequency. Splitting individual periods after generation is allowed.

> 🔧 **Implementer:** Recommend new districts leave Automatic Entry Adjustments off for their first fiscal year, so they can review what would have changed before opting into automatic adjustments.

---

# Job 5 — "Get my opening balances in"

**TL;DR:** Pull balances from your ERP as of the day before go-live. Upload. Confirm debits = credits.

**Prerequisite:** Like the GL Accounts Import, the Opening Balance Import has to be registered in Imports & Exports › Imports › Add New first (see Before-You-Touch step 4). If your implementer hasn't done that, the import option won't be available when you click Import.

**Where:** Configuration › Opening Balance Import.

**Required columns:** Account Code, Site Code (if Distributed), Debit Balance, Credit Balance.

**What you need to know:**
- This is a one-time import. It anchors the audit trail for your first FY.
- Total debits must equal total credits across the file. If they don't, the import rejects and tells you the variance. Validate this before you upload.
- Distributed posting → balances at site level. Centralized → district-level totals are fine.
- Audit trail records who imported, when, and the file contents.

> 🔧 **Implementer:** Build this into the timeline at week one — the customer's ERP team needs lead time, and reconciling the file against the imported CoA usually takes at least one round of corrections. Confirm the Opening Balance Import is already registered as an import type in Imports & Exports before the file is ready to upload.

---

# Job 6 — "Make a manual journal entry"

**TL;DR:** Two modes — Template (pre-populated) or Manual (blank). Both must balance. Both must fall in an open period.

**Where:** Journal & Ledger › New Entry.

**Quick anatomy:**
- **Site selection** — district-wide or specific site. Site code embeds into the account code (e.g. `1000-2000-3000-001-50000` for site 001). District-wide → all zeros.
- **Posted Date** — defaults to today. Cannot exceed today. Cannot fall in a closed period or closed FY (you'll get an inline error).
- **Mode toggle** — Template or Manual.
  - **Template:** select a Template Entry (e.g. "Monthly Salaries", "EOY Audit Adjustments") — line items pre-populate, all editable.
  - **Manual:** blank slate.
- **Line items** — Account / Debit / Credit. Real-time balance check at the bottom. Make Entry button only enables when debits = credits and both > 0.

**Bulk payroll entries via import (when in scope):** Districts that close payroll outside of SchoolCafé can bring their payroll journal entries in via a dedicated journal-entry-lines import — same setup pattern as the GL Accounts and Opening Balance imports (registered once in Imports & Exports, then available from the Import button in Journal & Ledger). If your district plans to use this path, confirm with your implementer that the payroll import type is registered before payroll close week.

**The Template Entry change worth knowing:** A single template can include the same GL account on both debit and credit sides. Legacy blocked this, which forced multiple entry types for audit work. In 2.0, one "EOY Audit Adjustments" template covering your entire CoA is enough — the system shows an informational warning if you put the same account on both sides, but it's not a block.

**Renamed from legacy:**
- "Ad-Hoc Entries" → Manual Entries
- "GL Entry Types" → Template Entries

---

# Job 7 — "Fix a posting that went out wrong"

**TL;DR:** Click the reverse icon. Type a reason. Done.

**Where:** Journal or Ledger view, on the row of the bad transaction.

**What happens:**
1. Side drawer opens showing the original transaction.
2. You type a reason (required).
3. The system creates a new, balanced reversal entry with debit/credit flipped. The original is tagged REVERSED; the new one is tagged REVERSAL OF #[id]. Both stay visible in the ledger.

**Reversing a reversal:** This isn't a documented path — the design covers reversing an original transaction, not reversing a reversal of an original. If you find yourself wanting to do it, treat it as "stop and ask your implementer" rather than assumed-supported.

**What auditors will love:** The reason text is preserved. Both transactions remain in place. The pair is linked. There's no quiet "delete" path.

---

# Job 8 — "See what happened — by account or by date"

Two views, one job.

| View | Best for | What it shows |
|---|---|---|
| **Ledger** | "What's the balance of this account as of this date?" | One account, running balance, beginning + ending balance bar fixed at the bottom. |
| **Journal** | "What happened on these days, across these sites?" | All accounts, by date, expandable rows showing line items. |

Both support: location filter, date-range filter, sortable columns, transaction-ID hyperlink to a details drawer, in-place reversal, and async Excel export through the Document Center.

**Note on legacy:** Older PrimeroEdge customers will remember separate Journal and Ledger pages. In 2.0, both views still exist, but the data model behind them is unified — the same transaction shows up in both, and the line-level details, reversal status, and audit metadata are consistent across views.

**Balance behavior — read this once, never forget it:** Asset and Expense accounts are debit-normal: debits add. Liability, Equity, and Revenue accounts are credit-normal: credits add. The Ledger does this math correctly per account type. A liability with a $500 debit posting will see its balance go down, which is what you want.

> **See also:** the Job 8 / Job 10 deep-dive below — *"What posting actually puts in your ledger"* — opens the hood on the exact debit/credit lines each kind of posting writes.

---

# Job 9 — "Pull a report for my board, my auditor, or to know where I stand"

**Where:** Reports landing page — three tiles.

| Report | Use when… | Output shape |
|---|---|---|
| **General Ledger** | Auditor wants account-level detail | One Excel sheet per selected account; multi-select with Select All for all active mapped accounts |
| **Journal** | You need a date-range view of all activity | One workbook, one sheet covering all selected locations |
| **Profit & Loss** | Board meeting, monthly review, fiscal close | One sheet per site; revenue, expenses, net income, Cost of Foods Used breakdown |

**P&L additions you should know about:**
- Reporting period options: Single month, Quarter, Fiscal YTD, or Custom range.
- Cost of Foods Used subsection — Beginning Inventory + Purchases + Additions ± Net Transfers − Ending Inventory. Sourced live from the Inventory Usage Report. If Inventory data is stale, P&L COFU is stale. Close your Inventory period first.
- % calculations suppress (show "-") if total revenue or total expenses ≤ 0.
- Custom date ranges drop the prior-period and % change columns. They only make sense for standard periods.

Generation is async. You click Generate, the file builds in the background, you get notified, and you download from the Document Center. No spinning loaders.

> ⚠️ **One reporting truth in 2.0:** Reports pull only from posted ledger entries. There's no "live recalculate" mode. If a number isn't in the ledger, it isn't in the report. This is by design — your reports always match your ledger, which means your reports always match what got exported to your ERP.

<!-- ============================================================ -->
<!-- C7 — Job 9 (continued): P&L build-out. NXT-68643 (shell) + NXT-70296 (COFU) shipped; the rest (Coming). -->
<!-- ============================================================ -->

## Job 9 (continued) — Reading the P&L, line by line

> **TL;DR.** The P&L (officially the **Revenue & Expenditure (P&L) Report**) is your board-and-auditor deliverable. Today it ships as a parameter screen that builds a per-site Excel workbook with a revenue table, an expense table, and a Cost of Food Used breakdown. A much deeper version is coming: meal-type-level revenue, a reimbursements section, an itemized expenses section, a Meal Counts section, a standalone Cost of Goods Sold report, and a board-ready promotional PDF. **The shell is live; the detail layer is (Coming).** This section tells you what works today and what's on the way, so you don't promise a customer a column that isn't there yet.

### What's live today (shipped)

You generate a P&L the same way you generate the General Ledger and Journal reports: pick parameters, click Generate, download from the Document Center.

**Parameters.** Choose a fiscal year, a reporting period, and one or more sites; multiple sites each get their own worksheet in one Excel file. <!-- Source: NXT-68643:AC "Choose a fiscal year, reporting period, and sites. When multiple sites are selected, each site gets its own P&L worksheet in the Excel file." --> The reporting period can be a single month, a quarter, a fiscal year-to-date, or a custom date range. <!-- Source: NXT-68643:AC "Options:\n*** {{Single month}}\n*** {{Quarter}}\n*** {{Fiscal YTD}}\n*** {{Custom date range}}" --> One Generate action produces one workbook. <!-- Source: NXT-68643:AC "*One workbook per Generate action.*" --> If you select **All** sites, the report consolidates every site in the district into a single report. <!-- Source: NXT-68643:AC "If ‘All’ is selected, consolidate data from all sites within the district in one report." --> Any line with no data shows a dash, and the backend uses zero for the math. <!-- Source: NXT-68643:AC "If a line in the report doesn’t have any data, indicate so using a ‘-‘ and use zero in the backend for calculations" -->

> 🔧 **Implementer note — what populates the two tables today.** In the current (Phase 1) build the P&L is driven by **manual journal entries only**, not by automated POS/inventory feeds. A revenue row appears for each revenue-type GL account that shows up in at least one manual entry line dated inside the period; an expense row appears the same way for expense-type accounts. <!-- Source: NXT-68643:AC "revenue table must include one row for each gl account that meets both of these conditions:\n** account type = revenue\n** account appears in at least one manual entry line (debit or credit) where the posting date is inside the selected reporting period" --> Each row label is the GL account name exactly as stored. <!-- Source: NXT-68643:AC "row label must use the gl account name exactly as stored in the gl accounts table" --> So if a customer's P&L looks empty in early onboarding, it's usually because the manual entries that feed it haven't been posted yet — not a bug.

**How the columns are computed (live).** For a revenue row, the current period is credits minus debits in the period; for an expense row, it's debits minus credits. <!-- Source: NXT-68643:AC "** current period = (sum of credits in period) – (sum of debits in period)" --> <!-- Source: NXT-68643:AC "** current period = (sum of debits in period) – (sum of credits in period)" --> Year-to-date is the running total from the fiscal-year start through the end of the selected period. <!-- Source: NXT-68643:AC "** year-to-date = cumulative (credits – debits) from fiscal year start up to the end date of the selected reporting period" --> % of Revenue and % of Expenses are each computed as the row divided by its table total, shown as `XX.XX%`. <!-- Source: NXT-68643:AC "*if total revenue > 0 → (current period ÷ total revenue) × 100, display as \"XX.XX%\"*" --> Net Income at the bottom is total revenue minus total expenses. <!-- Source: NXT-68770:AC "display net income = total revenue – total expenses and subtotals" -->

> ⚠️ **Watch-out — custom date range hides the comparison columns.** If a customer picks a custom date range, the report intentionally drops every prior-period comparison column. <!-- Source: NXT-68643:AC "*Note: If the user selects a custom date range, do not show any columns involving comparison with prior periods.*" --> So "where did my % Change column go?" is expected behavior, not a defect — they're on a custom range. A period with no postings exports a "No records were found" line. <!-- Source: NXT-68643:AC "If no records are available, indicate in export that “No records were found”" --> And when a period's total revenue or total expenses is zero or negative, the percentage columns are suppressed and a warning banner explains why. <!-- Source: NXT-68643:AC "if total revenue ≤ 0 AND total expenses ≤ 0 → \"Total revenue and expenses are zero or negative for this period. Percentage calculations have been suppressed.\"" -->

**Cost of Food Used (live).** The P&L includes a **Cost of Food Used** subsection, grouped by Valuation Category (Food and Non-Food) exactly as those categories are defined in the Inventory Usage Report. <!-- Source: NXT-70296:AC "Add a \"Cost of Food Used\" subsection in the P&L." --> <!-- Source: NXT-70296:AC "Group by Valuation Category (Food & Non-Food) as already defined in the Inventory Usage Report." --> It breaks the cost into Beginning Inventory, Purchases, Additions, Net Transfers (transfers in minus transfers out), and Ending Inventory, then derives Cost of Food Used from them. <!-- Source: NXT-70296:AC "* Line A — Beginning Inventory\n* Line B — Purchases\n* Line C — Additions\n* Line D — Net Transfers (Transfers In − Transfers Out)\n* Line E — Ending Inventory\n* Line F — Cost of Food Used ({{A + B + C ± D − E = COFU}})" --> These numbers are pulled **live from the Inventory Usage Report** — the P&L does not recalculate them itself. <!-- Source: NXT-70296:AC "All Cost of Sales data is fetched live from the Usage Report. The P&L does not independently calculate these values in columns A - D." -->

> ⚠️ **Watch-out (read this before you teach Cost of Food Used) — the source of this number is changing.** Today's shipped behavior is "Cost of Food Used is fetched live from the Inventory Usage Report." <!-- Source: NXT-70296:AC "All Cost of Sales data is fetched live from the Usage Report." --> A Phase-2 rebuild of the P&L instead derives Ending Inventory from **manually entered inventory transactions** until the Item Management integration lands: *"After integration, this value will be sourced from Item Management. However, since we are not there yet, we will determine this with the formula below using transactions of the type Inventory – Usage (COGS)."* <!-- Source: NXT-68719:AC "Ending Inventory: After integration, this value will be sourced from Item Management. However, since we are not there yet, we will determine this with the formula below using transactions of the type Inventory – Usage (COGS):" --> **These two are in tension** — one says "live from the Usage Report," the other says "computed from manual usage entries until integration." Do not silently pick one when training. State that the live-feed version is what's shipped, the manual-entry version is the Phase-2 plan, and flag it as an **Open question** (below) for the product owner to confirm which a given customer's release behaves like.

### What's coming to the P&L (upcoming — not yet live)

Everything in this part is **(Coming)**. The tickets are real and define the agreed behavior, but they are New / in development — do not demo them as working or promise the columns to a customer as shipped.

#### (Coming) Revenue, broken out by program and meal type

The revenue table is being expanded from "one row per GL account" to a meal-type-level breakdown. The planned version shows a row for **every program and meal type defined in the district's configuration** (the AC's examples include NSLP Lunch, SBP Breakfast, CACFP Supper, and others). <!-- Source: NXT-65475:AC "For *every program and meal type defined in the district’s configuration* (e.g., NSLP Lunch, SBP Breakfast, CACFP Supper, SFSP Snack, Adult Meals, Second Meals, Milk, or any other configured type)" --> Each row will carry a full comparison set: current period, prior period, current and prior cost-per-meal, percent of total revenue, change from prior period, and year-to-date totals. <!-- Source: NXT-65475:AC "** Revenue for *Current Period*\n** Revenue for *Prior Period*\n** *Current Cost-per-Meal*\n** *Prior Cost-per-Meal*\n** *Percentage of Total Revenue* (current period)\n** *Change from Prior Period* (percentage and/or dollar change)\n** *Year-to-Date Total Revenue*" --> Rows will be grouped first by program, then by meal type. <!-- Source: NXT-65475:AC "Display metrics in a *tabular format*, grouped first by *Program*, then by *Meal Type*, with clear labels for Current Period, Prior Period, and YTD." --> The report will count only **closed POS periods** inside the selected period, <!-- Source: NXT-65475:AC "Report includes only *closed POS periods* within the selected financial period." --> and you'll be able to drill from district totals down to program, meal type, and site level. <!-- Source: NXT-65475:AC "Drill-down supported from *District totals → Program totals → Meal type → Site level* when multiple sites are included." --> The same dataset that drives the Accountability Revenue Report feeds this section, so the two reconcile. <!-- Source: NXT-65475:AC "Report uses the same dataset that drives the *Accountability → Revenue Report* for consistency." -->

A companion ticket refines the same section's totals. The revenue table is planned to show a row for **every meal-sales revenue mapping marked Active**, and a mapped-but-zero program still shows at `$0.00` rather than disappearing. <!-- Source: NXT-69386:AC "Create a row corresponding to every single meal sales revenue data point with the status “Active” in the mapping page.\n** If a program is active but has no revenue, it should still display with $0.00 with the income in the current period section." --> An **Additional Income** line is added under Revenue, and the totals are redefined so that Net Revenue excludes sales tax while Total Collected includes it. <!-- Source: NXT-69386:AC "* Add *Additional Income* under the *Revenue* section.\n* *Net Revenue (excludes sales tax)* = Cash Sales + Debit Sales + Additional Income\n* *Sales Tax Collected* = Cash Tax + Debit Tax\n* *Total Collected (includes sales tax)* = Net Revenue + Sales Tax Collected" -->

> 🔧 **Implementer note — where these revenue rows come from in Phase 2.** In the Phase-2 design, each revenue row is sourced from a specific manual-entry type — separate entry types for catering, for breakfast/lunch à-la-carte, adult/visitor, paid, and reduced. <!-- Source: NXT-68719:AC "Revenue – Catering\n### Revenue – Breakfast A La Carte\n### Revenue – Breakfast Adult/Visitor\n### Revenue – Breakfast Paid\n### Revenue – Breakfast Reduced\n### Revenue – Lunch A La Carte\n### Revenue – Lunch Adult/Visitor\n### Revenue – Lunch Paid\n### Revenue – Lunch Reduced" --> (In the AC these are internal entry-type names; when this ships, confirm the customer-facing row labels with the product owner before teaching them — see Open questions.)

#### (Coming) Reimbursements section

A dedicated **Government Reimbursements** section is planned. It pulls reimbursable meal counts from the Meal Count Report across the district's active federal and state programs, applies the reimbursement rate in effect for the period, and earns reimbursement as meal count times rate, summed across programs. <!-- Source: NXT-65480:AC "Pull reimbursable meal counts from the *Meal Count Report*, ensuring it includes all active federal and state meal programs" --> <!-- Source: NXT-65480:AC "For each program:\n{{Earned Reimbursement = Σ (Meal Count × Applicable Rate)}}" --> Individual programs are itemized behind the scenes, but the summary shows a single **Total Government Reimbursements** figure. <!-- Source: NXT-65480:AC "Include separate line items by program in the backend for transparency, but aggregate to a *Total Government Reimbursements* figure in the main summary." --> Its columns are designed to match the Meal Sales Revenue section so the two read consistently. <!-- Source: NXT-65480:AC "Match “Meal Sales Revenue” section’s columns for consistency" -->

> 🔧 **Implementer note — reimbursement is recognized when earned, not when paid.** This is the whole point of the section, and it surprises districts used to cash accounting. Revenue is recognized in the **current service period** on an accrual basis — the system records an amount owed by federal funds when the meals are served, and clears it to cash only when the claim payment actually arrives. <!-- Source: NXT-65480:AC "Recognize revenue in the *current service period* (accrual method):\n** Debit: _Due from Federal Funds (Asset)_\n** Credit: _Reimbursement Program System Accounts (Revenue)_\n* When payment is received:\n** Debit: _Cash in Bank_\n** Credit: _Due from Federal Funds_" --> Two business rules gate it: the financial periods must be open from the posting date through today, and **all POS periods in the selected range must be closed**. <!-- Source: NXT-65480:AC "Financial periods must be open from posting date to current date.\n* All POS periods in the selected financial period’s range must be closed." --> Mid-year rate changes are handled by applying the rate valid on each meal's service date. <!-- Source: NXT-65480:AC "Handle mid-year reimbursement rate changes by applying rates valid for the service date of each meal." -->

The refinement ticket splits reimbursements into two rows — one aggregating all Active **Federal Sources** mappings, one aggregating all Active **State Sources** mappings — each valued as credits minus debits for entries whose claim-period posting date falls in the report range. <!-- Source: NXT-69386:AC "Create a row for Reimbursement Claim - Federal Sources.\n** This row is the aggregation of all reimbursement data points with the status “Active” created for Federal Sources." --> <!-- Source: NXT-69386:AC "Create a row for Reimbursement Claim - State Sources.\n** This row is the aggregation of all reimbursement data points with the status “Active” created for State Sources." -->

#### (Coming) Expenses detail (cost-per-meal, % of revenue, categorized)

The expense table is being expanded to the same comparison grid as revenue — current period, prior period, current and prior cost-per-meal, % of revenue, % change from prior, year-to-date, YTD cost-per-meal, and item % of category. <!-- Source: NXT-65483:AC "** Current Period\n** Prior Period\n** Current CPM (Cost per Meal)\n** Prior CPM\n** Current % of Revenue\n** % Change from Prior Period\n** Year-to-Date Total\n** YTD CPM\n** Item % of Category" --> Expenses are grouped by category, with the AC naming four sources: inventory-related expenses from the Inventory Posting module, payroll from payroll imports or manual GL postings, purchased goods and services from Accounts Payable when invoices post to GL expense accounts, and miscellaneous expenses from manual journal entries. <!-- Source: NXT-65483:AC "** *Inventory-related expenses* (e.g., Cleaning Supplies, Supplies) from *Inventory Posting* module.\n** *Payroll expenses* (e.g., Professional Salaries, Wages) from *payroll imports* or manual GL postings.\n** *Purchased goods and services* (e.g., Professional Services, Operational Supplies) from *Accounts Payable* when invoices are posted to GL expense accounts.\n** *Miscellaneous expenses* from *manual journal entries* or adjustments posted to expense codes." --> Only postings in **open financial periods** within the selected fiscal period are included, and expenses display grouped by GL account code and description. <!-- Source: NXT-65483:AC "** Only include postings within the selected fiscal period that are in *open financial periods*.\n** Group and display expenses by GL account code and description." --> In the Phase-2 design the cost-of-operation half of expenses is itself split into two sub-sections — general/administrative expenses and a separate salaries-and-wages block sourced from payroll entries. <!-- Source: NXT-68719:AC "The SG&A expenses table has two sections (Sales, Goods & Administrative (SG&A) and Salaries & Wages)" -->

#### (Coming) Meal Counts section

A **Meal Counts** section is planned, sourced from the same POS meal-transaction data as the standalone Meal Count Report so the totals match. <!-- Source: NXT-65486:AC "Use the same source data as the Meal Count report for the specified filters and dates." --> <!-- Source: NXT-65486:AC "Ensure totals in the financial report match those in the source report." --> It keeps the Meal Count Report's existing breakdowns — program types, adult, à-la-carte, and so on — <!-- Source: NXT-65486:AC "Maintain the breakdowns shown in that report (program types, adult, a la carte, etc.)." --> and shows current period, prior period %, % change from prior, year-to-date, and % of total meals. <!-- Source: NXT-65486:AC "** Current period\n** Prior period %\n** % change from prior period\n** Year-to-date\n** % of total meals" -->

#### (Coming) Cost of Goods Sold — both inside the P&L and as a standalone report

A standalone monthly **Cost of Goods Sold** report is planned, broken out by inventory category with a total line for the chosen scope (district, area, or site). <!-- Source: NXT-65481:AC "Show results by inventory category (e.g., Main Dish, Dairy, Bread, Supplies).\n* Provide a total line for the selected scope (district, area, or site)." --> It shows Beginning Inventory, Purchases, net Transfers, Ending Inventory, and COGS, where **COGS = Beginning Inventory + Purchases + Transfers − Ending Inventory**. <!-- Source: NXT-65481:AC "* Beginning Inventory\n* Purchases\n* Transfers (net in/out)\n* Ending Inventory\n* Cost of Goods Sold (COGS)" --> <!-- Source: NXT-65481:AC "COGS = Beginning Inventory + Purchases + Transfers − Ending Inventory" --> That same COGS value flows into the P&L's expense section as **Cost of Sales**, and the report reconciles to the General Ledger because it uses the same ledger postings. <!-- Source: NXT-65481:AC "COGS values also flow through to the Profit & Loss report under the *Expenses section* as *Cost of Sales*." --> <!-- Source: NXT-65481:AC "This report reconciles to the General Ledger, since it uses the same ledger postings that drive financial statements." --> An empty period still generates a report with the column headers in place. <!-- Source: NXT-65481:AC "If the selected parameters return no data, generate an empty report with the columns" -->

> 🔧 **Implementer note — Phase-2 COGS uses Item Management's valuation categories.** In the Phase-2 P&L rebuild, the Cost of Goods Sold rows are the **Valuation Categories defined in Item Management** (Item Configuration), and the formula adds an explicit Transfers-Out term: *COGS = Beginning Inventory + Purchases + Transfers In − Transfers Out − Ending Inventory.* <!-- Source: NXT-68719:AC "Valuation Categories are sourced from Item Management > Item Configuration > Valuation Categories" --> <!-- Source: NXT-68719:AC "The formula for COGS is COGS = Beginning Inventory + Purchases + Transfers In - Transfers Out - Ending Inventory" --> The "Description" column is the valuation-category name from Item Management — **it is not a financials data point**, so don't try to map it on the financials side. <!-- Source: NXT-68719:AC "This refers to the name of the valuation category and is sourced from item management. It *does not* refer to any data source from financials." --> Negative values across the report are shown in parentheses and all figures round to two decimals. <!-- Source: NXT-68719:AC "Use parantheses to indicate negative values\n### All dollar values and percentages should be rounded to two decimal places" -->

#### (Coming) Backend rebuild that all of the above sits on

A backend story restates the engine for the expanded report: the user picks a reporting period, the system builds a revenue table and an expense table, and **Net Income = Total Revenue − Total Expenses**. <!-- Source: NXT-68770:AC "display net income = total revenue – total expenses and subtotals" --> The exact row and total values the report computes are the same values the **Financial Dashboard** consumes — so the dashboard and the P&L will always agree. <!-- Source: NXT-68770:AC "these exact revenue values (each row + totals) must be used by the dashboard" --> <!-- Source: NXT-68770:AC "these exact expense values (each row + totals) must be used by the dashboard" --> A row appears for a revenue or expense GL account only if that account shows up in at least one manual entry line dated inside the period — same rule as the shipped shell. <!-- Source: NXT-68770:AC "account appears in at least one manual entry line (debit or credit) where the posting date is inside the selected reporting period" -->

### (Coming) The promotional P&L — a board-ready PDF (likely a new subsection)

This one is **not just more columns on the existing report — it's a separate printable artifact** aimed at sharing with internal teams and external stakeholders, so it likely earns its own subsection rather than living inside the working P&L. Treat it as **(Coming)**.

The planned PDF leads with header info (district name, report title, reporting period, fiscal year, and a "generated by" name and date-time) <!-- Source: NXT-70682:AC "The report shows header information: district name, report title, reporting period, fiscal year, and “generated by” name/date-time." --> and an **Executive Summary** table covering Net Gain/(Loss), Total Revenue, Total Expenditures, and Beginning and Ending Fund Balance. <!-- Source: NXT-70682:AC "The report includes an *Executive Summary* table with columns {{Line Item}} and {{Amount}}, containing:\n#* Net Gain/(Loss)\n#* Total Revenue\n#* Total Expenditures\n#* Beginning Fund Balance\n#* Ending Fund Balance" --> Below that sit detailed **Revenue** and **Expenditures** tables, each carrying a Budget column, a Variance column, and a Total row — note these are **budget-vs-actual** tables, which the working P&L does not have. <!-- Source: NXT-70682:AC "The report includes a *Revenue* table with columns:\n#* Description\n#* Current Period\n#* YTD\n#* Budget\n#* % of Revenue\n#* % Change\n#* Variance" --> <!-- Source: NXT-70682:AC "The report includes an *Expenditures* table with columns:\n#* Description\n#* Current Period\n#* YTD\n#* Budget\n#* % of Expenses\n#* % Change\n#* Variance" -->

It also includes a **Summary** table with a Prior Year column, <!-- Source: NXT-70682:AC "The report includes a *Summary* table with columns:\n#* Line Item\n#* Current Period\n#* YTD\n#* Budget\n#* Variance\n#* Prior Year" --> a **Compliance Checks** table (metric, value, status, benchmark), <!-- Source: NXT-70682:AC "The report includes a *Compliance Checks* table with columns:\n#* Metric\n#* Value\n#* Status\n#* Benchmark" --> and a **KPI Analysis** table with a plain-language "Signal" column explaining each metric. <!-- Source: NXT-70682:AC "The report includes a *KPI Analysis* table with columns:\n#* Metric\n#* Current\n#* vs Prior Year\n#* Signal" -->

> ⚠️ **Watch-out — set the right expectation when you show this to a customer.** Two design choices matter for how you frame it. First, every line is tagged by data source: a legend marks each figure as **system-generated** or **manually entered**, so a reader can see which numbers are computed versus keyed by hand. <!-- Source: NXT-70682:AC "The report includes a legend defining data source markers: {{System-generated}} and {{Manually entered}}." --> Second, the report carries an explicit disclosure that **it is not a substitute for a fully audited financial statement** — keep that disclosure in any copy you share so no one mistakes the promotional PDF for audited financials. <!-- Source: NXT-70682:AC "The report includes a disclosure statement that this is not a substitute for a fully audited financial statement." --> The output is built for stakeholder distribution as a printable report/PDF. <!-- Source: NXT-70682:AC "Generate output suitable for stakeholder distribution as a printable report/PDF." -->

### P&L — legacy → 2.0, for this section

| You may hear / expect | In Financials 2.0 |
|---|---|
| "The P&L" / "the income statement" | The report is named **Revenue & Expenditure (P&L) Report**. <!-- Source: NXT-68643:AC "Page title: *“Revenue and Expenditure (P&L) Report”*" --> |
| "Cost of Goods Sold" | Inside the P&L the food-cost block is labeled **Cost of Food Used** (Beginning Inventory → Purchases → Additions → Net Transfers → Ending Inventory → COFU). <!-- Source: NXT-70296:AC "Add a \"Cost of Food Used\" subsection in the P&L." --> A standalone Cost of Goods Sold report and the Phase-2 "Cost of Sales" expense line are **(Coming)**. <!-- Source: NXT-65481:AC "COGS values also flow through to the Profit & Loss report under the *Expenses section* as *Cost of Sales*." --> |
| "Reimbursement shows up when the check clears" | (Coming) Reimbursement is recognized **when meals are served** (accrual), and cleared to cash when the claim is paid. <!-- Source: NXT-65480:AC "Recognize revenue in the *current service period* (accrual method):" --> |
| "Revenue is one lump sum" | (Coming) Revenue breaks out by program and meal type, with cost-per-meal and prior-period comparison per row. <!-- Source: NXT-65475:AC "grouped first by *Program*, then by *Meal Type*" --> |

> **Open questions for the SME / product owner (P&L build-out):**
> 1. **Cost of Food Used source — live feed vs. manual entries.** The shipped report fetches it **live from the Inventory Usage Report**; the Phase-2 rebuild derives Ending Inventory from manual `Inventory – Usage (COGS)` entries until the Item Management integration lands. Which behavior does the customer's current release actually use, and when does the cutover happen? (Do not resolve in the guide until confirmed.)
> 2. **Customer-facing revenue/expense row labels.** The Phase-2 AC lists internal entry-type names (e.g., `Revenue – Lunch Paid`, `Expense – SG&A`, `Expense – Payroll`). <!-- Source: NXT-68719:AC "Revenue – Lunch Paid" --> <!-- Source: NXT-68719:AC "Expense – SG&A\n#### Expense – Payroll\n#### Expense – Other" --> What are the exact customer-facing labels for these rows? Don't print the internal entry-type strings in the guide as if they were UI labels.
> 3. **Reimbursement program-account naming.** AC references a "Reimbursement Program System Accounts (Revenue)" account and "Due from Federal Funds (Asset)." Confirm the exact account names a customer will see before naming them in customer-facing copy.
> 4. **Promotional PDF — where does Budget come from?** The promotional report adds Budget and Variance columns the working P&L lacks. AC does not state where the budget figures are entered or imported. Flag as unspecified — do not invent a budget-entry path.
> 5. **Two overlapping backend stories.** NXT-68770 and NXT-68719 both restate the P&L backend at different depths. Confirm which is the authoritative spec for the release being documented so the guide doesn't describe two different layouts.

---

# Job 10 — "Figure out why a posting failed (or didn't run)"

**TL;DR:** One page. Activity › Posting Activity Log.

**Where:** Financials › Activity › Posting Activity Log.

**What you'll see:**
- Summary cards (last 30 days): Total Jobs, Completed, Failed, Running.
- A table of every posting job: Job Name, Type (POS / Inventory / Claim), Status, Last Run, Triggered By.
- Expand a successful job → entries created, total amount, duration, breakdown by entry type, and a "View in Journal →" link that pre-filters the journal to that job.
- Expand a failed job → red warning, error reason ("Missing GL account mapping for site: Washington Elementary," etc.).

**The five reasons posting halts globally:**
1. An active data point isn't mapped.
2. An entry references an inactive data point.
3. The financial period covering the source date is closed.
4. The source POS/Inventory period isn't closed yet.
5. A category's base type doesn't match the data points referencing it.

Fix one of those, the job re-runs (or you re-trigger from the source system). The log keeps history.

> ⚠️ **Partial-failure caveat:** If a job posts some entries and then fails, it shows as Failed with no entries listed in the expanded row. Some entries did post — they're in the journal. Filter the journal by date range to find them before re-running, or you'll double-post.

<!-- ============================================================ -->
<!-- C1 — Job 10 refresh. ALL ten cluster tickets are status New => everything below tagged (Coming). -->
<!-- Shipped anchor for TODAY's behavior is NXT-69493 (Done Done). -->
<!-- ============================================================ -->

## Job 10 (refresh) — what's coming to the Posting Activity Log

> ⚠️ **Read this before the section below.** This guide tells you posting is fully hands-off — "Do nothing. Posting fires the moment the upstream period closes… you can no longer forget to post" — and the Glossary says the old **Approve / Post** buttons are *gone*. **That is true for the version shipping now, but a wave of work is in flight that brings manual Post / Repost controls back as an option.** None of it has shipped yet (all of it is in development at the time of writing). If you see **Post** buttons or a **Ready to Post** queue on your screen, the product is not broken and neither is this guide — you are on a newer build. Everything tagged **(Coming)** below is the new behavior.

### TL;DR

- **Today (shipped):** the Posting Activity Log is a read-only monitor. Postings run in the background when an upstream period closes; you open this page to confirm jobs ran and to see why any failed. The shipped page has **four** summary cards (Total Jobs / Completed / Failed / Running) and a reverse-chronological job table. <!-- Source: NXT-69493:AC "*Summary cards*: Four cards at top — Total Jobs (30 Days), Completed (green), Failed (red), Running (orange)." --> <!-- Source: NXT-69493:AC "*Manual trigger*: Out of scope — jobs triggered from Fiscal Periods page, not here." -->
- **(Coming) Manual posting comes back as an option.** A **Ready to Post** queue lets you review closed periods and post them yourself, without leaving this page. <!-- Source: NXT-70065:AC "A \"Ready to Post\" section appears between the summary cards and the job history table" --> <!-- Source: NXT-70065:AC "two actions: Review and Post All" -->
- **(Coming) Two posting grids** — one for POS, one for Inventory — give you a per-site, per-month list with a **Status** column and **Post / View / Repost / Remove** actions. <!-- Source: NXT-65487:AC "*Status* (Not Ready, Ready to Post, Posted, Error)" --> <!-- Source: NXT-65487:AC "*Actions* (Post, View, Repost, Remove)" -->
- **(Coming) The top of the page is redesigned** from four system-job counts to three "what matters now" cards: posting progress, what needs attention, and dollars posted this period. <!-- Source: NXT-70066:AC "Replace the four Phase 1 cards (Total Jobs, Completed, Failed, Running) with three cards in a horizontal grid" -->
- **(Coming) A gentle nudge** points manual posters toward turning automatic posting back on. <!-- Source: NXT-70069:AC "Banner text: \"You're posting manually. Districts with automatic posting enabled only visit this page when something needs attention.\"" -->

### What this page is for

You come to the Posting Activity Log to answer one question: *did my financial data post correctly, and if not, what do I fix?* <!-- Source: NXT-69493:desc "As a Child Nutrition Director, I want to view a log of all background posting jobs, so that I can confirm my financial data is being posted correctly." --> The shipped version is a monitor only — postings are triggered elsewhere, and you watch them land here. <!-- Source: NXT-69493:AC "*Manual trigger*: Out of scope — jobs triggered from Fiscal Periods page, not here." -->

The upcoming work keeps that monitoring job but adds a second job on the same page: **reviewing and posting closed periods yourself.** <!-- Source: NXT-70065:desc "As a CN Director, I want to see which periods are closed and waiting for ledger entries so I can review and post them without navigating away from the Activity Log." -->

### (Coming) The Ready-to-Post queue — review and post without leaving the page

> 🔧 **Implementer note:** This section is the single biggest change to the "do nothing" story. If your district leaves automatic posting on, you will rarely see this queue do anything (closed periods post themselves and the queue stays empty). If automatic posting is off, this is where you'll work each period close. All of it is **(Coming)** — status *New* / in development.

A new **Ready to Post** card sits between the summary cards and the job history table; it's expanded by default and shows a badge with how many periods are waiting. <!-- Source: NXT-70065:AC "A \"Ready to Post\" section appears between the summary cards and the job history table" --> <!-- Source: NXT-70065:AC "Section is a collapsible card with a left-border accent and a badge showing pending item count" --> <!-- Source: NXT-70065:AC "Section is expanded by default; collapses on header click" -->

Each waiting period shows as one row with the period name, how many sites it covers, a type badge (POS or Inventory), and two buttons — **Review** and **Post All**. <!-- Source: NXT-70065:AC "Each pending item shows as a row: period name, site count, type badge (POS Posting / Inventory Posting), and two actions: Review and Post All" --> Rows are grouped one per period per type, so a large district doesn't get a wall of rows. <!-- Source: NXT-70065:AC "Items aggregate one row per period per type, regardless of district size" -->

**To review before posting:** click **Review** to open an inline checklist of the sites in that period — each row a checkbox, the site name, the entry types you'd expect, and an estimated amount. <!-- Source: NXT-70065:AC "Clicking Review expands an inline panel below that row with a checklist table: checkbox, site name, expected entry types, estimated amount" --> Every site is checked by default; you get a **Select All / Deselect All** toggle and a search-by-site-name filter, and the **Post Selected (X sites)** button updates its count as you check and uncheck. <!-- Source: NXT-70065:AC "All sites checked by default; \"Select All / Deselect All\" toggle and search-by-site-name filter are present" --> <!-- Source: NXT-70065:AC "\"Post Selected (X sites)\" button updates count dynamically as user checks/unchecks" -->

**To post:** clicking **Post All** or **Post Selected** opens a confirmation modal with a preview table — site, entry types, estimated amount, and a total — so you confirm the dollars before you commit. <!-- Source: NXT-70065:AC "Clicking Post All or Post Selected opens a confirmation modal showing a preview table of entries (site, entry types, estimated amount, total)" --> On confirm, the queue row animates away, the badge count drops, and a new **Running** job appears at the top of the job history table with **Triggered By** showing *your* name (not "System"). <!-- Source: NXT-70065:AC "On confirm: pending item animates out, a new Running job appears at the top of the job history table with Triggered By showing the current user name, badge count decrements" -->

When several periods are waiting, a **Post All Pending** button appears in the section header and its confirmation modal rolls everything up to a period-level summary with totals. <!-- Source: NXT-70065:AC "When 2+ items are pending, a \"Post All Pending\" batch button appears in the section header; confirmation modal shows a period-level summary with totals" -->

When nothing is waiting, the section shows an all-clear empty state. <!-- Source: NXT-70065:AC "When no items are pending, section shows an empty state: \"All caught up. Every closed period has been posted.\" with muted quip underneath" -->

### (Coming) The POS and Inventory posting grids — per-site Post / Repost / Remove

> ⚠️ **Watch-out — this is the line the Glossary needs to qualify.** Today's Glossary says the legacy **Approve / Post** buttons are *gone*. These two grids bring **Post**, **Repost**, and **Remove** actions back at the per-site level. Treat the Glossary's "gone" as "gone in the version that shipped, returning as an explicit per-site control." Both grids are **(Coming)** — status *New*.

**POS postings grid.** A table lists each site and month with **Total Revenue**, **Total Transactions**, and a **Status** of *Not Ready, Ready to Post, Posted,* or *Error*, plus **Post / View / Repost / Remove** actions. <!-- Source: NXT-65487:AC "Create a table with these columns:" --> <!-- Source: NXT-65487:AC "*Status* (Not Ready, Ready to Post, Posted, Error)" --> <!-- Source: NXT-65487:AC "*Actions* (Post, View, Repost, Remove)" --> Selecting a site shows a summary of its POS transactions. <!-- Source: NXT-65487:AC "Selecting a site displays a summary of various POS transactions." -->

**Inventory postings grid.** Same idea for inventory — site, month, the same four-value **Status**, and **Post / View / Repost / Remove**; selecting a site shows a summary of its inventory transactions. <!-- Source: NXT-66123:AC "Create a table with these columns:" --> <!-- Source: NXT-66123:AC "*Status* (Not Ready, Ready to Post, Posted, Error)" --> <!-- Source: NXT-66123:AC "*Actions* (Post, View, Repost, Remove)" --> <!-- Source: NXT-66123:AC "Selecting a site displays a summary of various Inventory transactions." -->

> 🔧 **Implementer note — period setup gates inventory posting.** If your financial and inventory periods aren't lined up, the grid blocks the post and shows this exact message in an info tooltip: *"To Approve or Post, close all open Inventory Periods up to the selected Financial Period's end date. To Approve or Post, open all Financial Periods from the start date of the selected Financial Period to today's date."* <!-- Source: NXT-66123:AC "*Then* I should receive the message “To Approve or Post, close all open Inventory Periods up to the selected Financial Period's end date.\nTo Approve or Post, open all Financial Periods from the start date of the selected Financial Period to today's date.” via a tooltip with an info icon." -->

> **Open question (do not invent):** NXT-66123's title and its tooltip both use the word **Approve** ("To *Approve* or Post…"), but its **Actions** column lists only *Post / View / Repost / Remove* — no Approve button. The AC does not define a separate Approve control, so this guide does not describe one. **Confirm with the PO whether Inventory has a distinct Approve step or whether "Approve" is legacy wording for Post.**

### (Coming) Redesigned summary cards — progress, problems, dollars

The four shipped cards (Total Jobs / Completed / Failed / Running) are being replaced by **three** cards. <!-- Source: NXT-70066:AC "Replace the four Phase 1 cards (Total Jobs, Completed, Failed, Running) with three cards in a horizontal grid" -->

1. **Posting Progress** — the current fiscal period, showing "X of Y sites posted" with a thin progress bar; a site counts as posted only once *all* its posting types are done. <!-- Source: NXT-70066:AC "Card 1 — Posting Progress: label is the current fiscal period name (uppercase), value shows \"X of Y sites posted\", thin green progress bar underneath proportional to completion. A site counts as \"posted\" only when all its posting types are complete." -->
2. **Needs Attention** — a red count of failed/unresolved jobs; click it to jump to the table filtered to failures. When there are none it reads "No issues ✓" in green. <!-- Source: NXT-70066:AC "Card 2 — Needs Attention: value shows failed/unresolved count in red. Clickable — scrolls to and filters the job history table to failed jobs. When zero: \"No issues ✓\" in green" -->
3. **Posted This Period** — total dollars posted to the ledger this period, with a delta versus the prior period. <!-- Source: NXT-70066:AC "Card 3 — Posted This Period: value shows total dollar amount of ledger entries for the current period in green. Subtitle shows delta vs prior period (e.g., \"↑ $4,200 vs Dec 2025\")" -->

The old job counts don't disappear — they move into the job-table header as muted inline text (for example, "25 total · 21 completed · 2 failed · 1 running"). <!-- Source: NXT-70066:AC "The old job counts (total, completed, failed, running) move to the job history table section header as inline muted text: \"Posting Jobs (Last 30 Days) · 25 total · 21 completed · 2 failed · 1 running\"" -->

### (Coming) Failures surface first

Failed jobs get pinned to the top of the table no matter how you've sorted it, with a **Needs Attention** divider above them and a **Recent Jobs** divider below. <!-- Source: NXT-70067:AC "Failed jobs are pinned to the top of the job history table regardless of sort order" --> <!-- Source: NXT-70067:AC "A \"Needs Attention\" divider row appears above the first failed job; a \"Recent Jobs\" divider appears below the last failed job, before completed/running jobs" --> The **Failed** filter chip carries a red count badge (for example, "Failed 2"). <!-- Source: NXT-70067:AC "The \"Failed\" filter chip shows a red badge with the count of failed jobs (e.g., \"Failed 2\")" --> Expanding a failed job shows the error, a plain-language help line, and a **Resolve Issue** link. <!-- Source: NXT-70067:AC "Expanded failed job detail panels show: error message, a direct help line (\"This one needs a fix before it's audit-ready. Here's what to do →\"), and a Resolve Issue link" -->

### (Coming) Richer completed-job detail + export

Open a completed POS job and you'll see an **Entries by GL Entry Type** table — entry type, the debit/credit accounts, a count, and a total. <!-- Source: NXT-70068:AC "Expanded completed POS job panels show an \"Entries by GL Entry Type\" table with columns: entry type, debit/credit accounts, entry count, total amount" --> **Reimbursement Receivable** is the first, bold row; **Sales Tax Collected** appears as a muted, conditional last row only if your district has sales tax configured, with a footnote that entry types depend on your configuration. <!-- Source: NXT-70068:AC "Reimbursement Receivable is the first row in the table, visually prominent (bold text)" --> <!-- Source: NXT-70068:AC "Sales Tax Collected appears as the last row only if the district has sales tax configured; styled as conditional (muted italic)" --> <!-- Source: NXT-70068:AC "A footnote below the table reads: \"Entry types shown depend on your district's configuration.\"" --> An **Export Entries** button offers **CSV, PDF,** or **ERP Format**. <!-- Source: NXT-70068:AC "Clicking Export shows a dropdown with format options: CSV, PDF, ERP Format" --> When you posted a job yourself, the **Triggered By** column shows a user icon before your name. <!-- Source: NXT-70068:AC "The Triggered By column shows a user icon before the name when the job was triggered manually (not \"System\")" -->

### (Coming) "You're posting manually" nudge

If automatic posting is off, a low-key banner appears between the summary cards and the Ready-to-Post section: *"You're posting manually. Districts with automatic posting enabled only visit this page when something needs attention."* <!-- Source: NXT-70069:AC "A standalone banner appears between the summary cards and the Ready to Post section when automatic posting is not enabled" --> <!-- Source: NXT-70069:AC "Banner text: \"You're posting manually. Districts with automatic posting enabled only visit this page when something needs attention.\"" --> It offers an **Enable automatic posting →** link and an X to dismiss for the session, and it never shows if automatic posting is already on. <!-- Source: NXT-70069:AC "Right side shows \"Enable automatic posting →\" link and an X dismiss button" --> <!-- Source: NXT-70069:AC "Dismissing hides the banner for the session (persists via local storage)" --> <!-- Source: NXT-70069:AC "Banner never renders if automatic posting is already enabled" --> The page subtitle becomes "Your posting jobs, tracked and audit-ready." <!-- Source: NXT-70069:AC "Page subtitle updated to: \"Your posting jobs, tracked and audit-ready.\"" -->

> 🔧 **Implementer note:** This banner is the product's own acknowledgement that manual posting is a *mode*, not the default. The 2.0 promise ("posting is automatic") is the recommended path; the manual queue and grids above exist for districts that choose to keep it hands-on. Frame it that way for staff so the two messages don't read as contradictory.

### (Coming) Notifications: blocked postings and login summaries

**Blocked by missing GL mappings.** When the readiness gate blocks a posting job, a bell notification fires and a **yellow** banner pins to the top of this page: *"Financial postings could not run. [X] required GL mappings are incomplete."* — where [X] is the live count of gaps. <!-- Source: NXT-70866:AC "When the readiness gate is active, display a yellow informational banner pinned to the top of the Posting Activity Log page" --> <!-- Source: NXT-70866:AC "Notification text: _\"Financial postings could not run. [X] required GL mappings are incomplete.\"_ where [X] = current count of incomplete mappings" --> The banner links straight to the Account Mapping page filtered to the incomplete mappings, has no dismiss button, and clears itself once every required mapping is complete. <!-- Source: NXT-70866:AC "Banner includes a link to Account Mapping page, pre-filtered to incomplete mappings only" --> <!-- Source: NXT-70866:AC "Banner has no dismiss button — it remains visible as long as gaps exist" --> <!-- Source: NXT-70866:AC "Banner disappears automatically when all required mappings are complete" -->

**Login summary.** When you arrive in Financial Oversight and there's been posting activity since your last login, a banner summarizes it — e.g. "X posting jobs completed since your last login. View Activity Log →" — and prioritizes warnings if any jobs failed or need review. <!-- Source: NXT-69972:AC "*Given* there are new completed jobs since last login, *Then:* notification displays: \"X posting jobs completed since your last login. View Activity Log →\"" --> <!-- Source: NXT-69972:AC "*Then:* notification prioritizes warnings: \"X jobs need attention, Y completed. View Activity Log →\"" --> Clicking through opens this page filtered to jobs since your last login. <!-- Source: NXT-69972:AC "*Given* the user clicks \"View Activity Log →\", *Then:* user navigates to Posting Activity Log, filtered to jobs since last login." -->

> 🔧 **New status to know — "Requires Review."** Beyond Completed / Failed, a job can land as **Requires Review** when a posting already exists for that period or claim. The expanded row tells you to review and manually reverse the existing entry before reposting. <!-- Source: NXT-69972:AC "*Given* a posting job has status \"Requires Review\" due to existing system-generated entry, *Then:* expanded row shows: \"A system-generated posting already exists for [Period]. Review and manually reverse if needed before reposting.\"" --> <!-- Source: NXT-69972:AC "*Given* a posting job has status \"Requires Review\" due to existing claim posting, *Then:* expanded row shows: \"A posting already exists for this claim. Review and manually reverse if needed before reposting.\"" -->

### (Coming) Fix the mapping once — failed jobs rerun themselves

You don't re-post failed jobs by hand after fixing a mapping. When you save the missing GL mappings under **Financials > Account Mapping**, the system automatically reruns every posting job that had failed for a missing-mapping reason, and logs each new result here. <!-- Source: NXT-70111:AC "When a user saves missing GL mappings in {{Financials > Account Mapping}}, the system automatically reruns all previously failed posting jobs whose failure reason was missing mapping." --> <!-- Source: NXT-70111:AC "The rerun is system-triggered (no manual retry), and each job logs the new result (success or new failure reason) in Posting Activity Log." -->

> 🔧 **Implementer note — the resolution loop, end to end:** a job fails for a missing mapping → the yellow banner and bell point you to Account Mapping → you fill the gap → the failed jobs rerun on their own and reappear here with their new result. No "resolved" notification fires; postings just resume. <!-- Source: NXT-70866:AC "If the user resolves all gaps, do not send a \"resolved\" notification — postings resume silently on the next cycle" -->

> **Open question (do not invent a release label):** the AC for these tickets does not state *when* the manual controls ship or under what release/version name. This guide tags them **(Coming)** only. Do not add a version number, sprint, or date to the Glossary or the "What changed in 2.0" table until the PO confirms one.

---

<!-- ============================================================ -->
<!-- C6 — Job 8 / Job 10 deep-dive: what posting writes to the ledger. -->
<!-- Live: NXT-70304, NXT-66384 (Done Done). Everything else (Coming). -->
<!-- ============================================================ -->

# Job 8 / Job 10 deep-dive — What posting actually puts in your ledger

> **Where this lives.** This expands **Job 8 ("See what happened — Journal & Ledger")** and **Job 10 ("Why a posting fired or failed — Posting Activity Log")**. It also leans on the Job 2 prerequisite above (Phase 5 — Valuation Categories), which gates all inventory posting.

> **TL;DR.** The rest of this guide keeps telling you "posting is automatic." True — but it never shows you *what* it posts. This section opens the hood. When a period closes, the system writes balanced double-entry lines for you: a debit, a credit, an amount, a date, and a site. Two of these flows are **live today** (your meal-sales revenue and your sales-tax liability). The rest — the whole inventory side and reimbursements — are **(Coming)**. Read the live ones as fact; read the (Coming) ones as "this is what's being built, don't expect the buttons yet."

> ⚠️ **Read the status tags, not just the headings.** A line tagged **(Coming)** describes a backlog story, not a screen you can open today. If you go looking for it and it isn't there, the guide isn't wrong — the feature hasn't shipped. Live behavior is written in the present tense with no tag.

## Legacy → 2.0, for this section

| You used to think… | In 2.0 it's actually… |
|---|---|
| "Posting is a black box; money just appears in the GL." | Every posted line names its **debit account, credit account, amount, posting date, and source** — and you can open the entry to see them. <!-- Source: NXT-65485:AC "The output will show all the information needed for the ledger entry — which accounts are debited and credited, the amount, the date, and where the transaction came from." --> (engine: **(Coming)**) |
| "Sales tax is part of my meal revenue." | Sales tax is a **liability you owe**, posted separately from revenue — never counted as income. <!-- Source: NXT-70304:desc "*Sales Tax* = the tax amount collected on taxable sales (a *liability*, not revenue)." --> **(Live)** |
| "Inventory just needs GL accounts somewhere." | Inventory posts by **Valuation Category**, and each category needs **both** an Asset and an Expense account before it can post at all. <!-- Source: NXT-65482:AC "Every valuation category must have *both* an Asset Account and an Expense Account mapped before it can be used in postings." --> **(Coming)** |

## Part A — The two flows that are LIVE today

These two are **Done Done**. The entries described here are real lines you will see in the Journal and Ledger (Job 8) right now.

### A1. Meal-sales revenue → your ledger, when you close a POS period **(Live)**

🎯 **The job:** you close a POS period and your meal money lands in the general ledger automatically, split correctly between revenue and the prepaid balances customers drew down.

When a POS period is closed for a site, the system posts your meal-sales revenue to the ledger without a manual journal entry. <!-- Source: NXT-66384:AC "*When a POS period is closed:* * Backend accesses the <meal sales revenue source> from the accountability database * Ledger Entries are created in the tables associated with the given district" --> The entry is labeled **Meal Sales Revenue**. <!-- Source: NXT-66384:AC "*Transaction Code:* MEALSLS ** *Transaction Description:* Meal Sales Revenue" --> (Backend transaction code: `MEALSLS` — you don't type this; it's the system's internal tag for the entry.)

What the entry contains:

- **Debit side** — your **Cash in Bank** account *and* the **prepaid balance** account, by site. <!-- Source: NXT-66384:AC "*Accounts Debited:* <Cash In Bank GL Site Sub Account> AND <Prepaid Account GL Site Sub Account>" --> (Why prepaid is debited: when a student spends down money they paid earlier, that prepaid liability goes down — so it sits on the debit side here.)
- **Credit side** — your **meal-sales** and **à la carte sales** revenue accounts, by site. <!-- Source: NXT-66384:AC "*Accounts Credited:* <Meal Sales AND A La Carte Sales GL Site Sub Accounts>" -->
- The meal-sales account follows the **revenue program** the money came from (for example, the School Breakfast Program), and the à la carte account follows the **meal type** (for example, Breakfast). <!-- Source: NXT-66384:AC "The *meal sales account* must align to the *student revenue source* (e.g., School Breakfast Program), and the *a la carte account* must align to the *student meal type* (e.g., Breakfast)." -->

> 🔧 **Implementer note — this is why one GL account can show two different totals on your P&L.** Each debit/credit line is tagged with the exact data point it came from, so the Profit & Loss report can total *by data point* even when several data points map to the same GL account. <!-- Source: NXT-66384:AC "each debit/credit line must be attributed to the originating data point / data source (e.g., the specific meal sales revenue data point or reimbursement data point) so the Profit & Loss report can calculate totals by data point even when one GL account is mapped to multiple data points." --> If you've ever wondered how the P&L splits a shared account, this is the mechanism.

⚠️ **Watch-outs before this will post:**

- Every meal-sales revenue data point must be mapped to a GL account first. <!-- Source: NXT-66384:AC "All Meal Sales Revenue accounts mapped to GL Accounts" --> (That's a Job 2 task.)
- The financial period has to be **open** from the posting date through today. <!-- Source: NXT-66384:AC "Financial periods must be open from the date of posting to the current date." -->
- **Every** POS period that falls inside the financial period's date range has to be **closed**. <!-- Source: NXT-66384:AC "All POS periods that fall in the selected Financial period's date range need to be closed." -->
- The entry posts dated to the **last day of the POS period**, not the day you close it. <!-- Source: NXT-66384:AC "The last day of the POS Period is used as the Posting date." -->

> 📌 **The lines always balance.** There may be several accounts on each side; the system validates that total debits equal total credits before it posts. <!-- Source: NXT-66384:AC "Note that there may be multiple accounts involved on either side of the transaction. Validate that debit and credit totals are equal." -->

### A2. Sales tax → posted as a liability you owe, not as revenue **(Live)**

🎯 **The job:** the tax you collected at the register is tracked as money you owe the state, ready to remit — and it never inflates your revenue.

When a POS period closes for a site, the system creates **exactly one** sales-tax entry for that site and period. <!-- Source: NXT-70304:AC "*Then* the system creates *exactly one* TAXCLCTD journal entry for that *site + POS period*." --> (Backend code: `TAXCLCTD`, "tax collected.") The entry has **two lines only**:

1. **Debit: Cash in Bank** — the net sales tax. <!-- Source: NXT-70304:AC "*Debit:* Cash in Bank = Net Sales Tax" -->
2. **Credit: Sales Tax Owed (a liability)** — the net sales tax. <!-- Source: NXT-70304:AC "*Credit:* Sales Tax Owed (Liability) = Net Sales Tax" -->

The amount is **net** tax: tax collected minus tax reversed (voids and returns) in that same POS period. <!-- Source: NXT-70304:AC "Posted Amount = *Tax Collected – Tax Reversed* (same POS period)." --> It posts dated to the **last day of the POS period**. <!-- Source: NXT-70304:AC "Posting Date = *last day of the POS period*." --> Like every posting, debits equal credits. <!-- Source: NXT-70304:AC "Total Debits = Total Credits for TAXCLCTD." -->

> 🔧 **Implementer note — where you'll see it on the close screen.** On the POS Period Close job for that period, this shows up as **"Sales Tax Collected."** <!-- Source: NXT-70304:AC "Appears as 'Sales Tax Collected' in POS Period Close job corresponding to the period." -->

⚠️ **Watch-out — an inactive account silently skips the tax posting.** If either the Cash in Bank account or the Sales Tax Owed account is inactive when posting runs, the system **skips** the sales-tax entry. <!-- Source: NXT-70304:AC "*Given* Cash in Bank or Sales Tax Owed is inactive *When* posting runs *Then* skip TAXCLCTD" --> Keep both accounts active or your tax liability won't post.

> 💡 **Why this matters for accuracy.** Meal-sales revenue is the **tax-exclusive** amount — the gross/total figure that includes tax must never be used for revenue posting. <!-- Source: NXT-70304:desc "*Meal Sales Revenue* = the tax-exclusive revenue amount (does *not* include sales tax)." --> <!-- Source: NXT-70304:desc "*Total / Gross Amount* = Meal Sales Revenue *plus* Sales Tax (may exist in POS, but must not be used for revenue posting)." --> That separation is what keeps your reported revenue honest.

## Part B — The inventory side **(Coming)**

> ⚠️ **All of Part B is upcoming.** None of these inventory entries post yet. Read this as "here's how inventory will hit your ledger," and complete the prerequisite — Job 2, Phase 5 (Valuation Categories) — now so you're ready when it ships.

### B1. What inventory close will post **(Coming)**

🎯 **The job:** when an inventory period closes, your food and supply costs land in the ledger automatically — no manual journal entries — grouped the way your reports expect.

When an inventory period transitions to **Closed** for a site, the system will start a posting job named **"Inventory Posting"** for that site and period, with no manual trigger. <!-- Source: NXT-70295:AC "*Then* the system automatically initiates a posting job named \"Inventory Posting\" for that site-period with no manual trigger required" --> Every entry is dated the **last day of the inventory period**. <!-- Source: NXT-70295:AC "*Then* every entry in the batch has a posting date of 2026-01-31" -->

**Grouping (the grain).** The system creates **one entry per entry type, per Valuation Category, per site, per period**, and each entry balances on its own. <!-- Source: NXT-70295:AC "*Then* the system creates exactly two WD entries for Site A — one for $2,000 (Purchased Food) and one for $800 (USDA Foods)" --> <!-- Source: NXT-70295:AC "*Then* total debits = total credits on that entry" --> So if one site used food from two categories, you get two separate withdrawal entries, not one blended line.

**The entry types and the lines each one writes** (all amounts come from the Inventory **Usage Report**):

| In plain language | Debit | Credit | Amount comes from |
|---|---|---|---|
| **Purchases** — stock bought in | the category's **Asset** account | **Cash in Bank** (one configured account, *not* from the category mapping) | the Purchases column <!-- Source: NXT-70295:AC "Debit → Valuation Category's Asset GL Account ** Credit → Cash in Bank GL Account (single configured account, not derived from Valuation Category mapping) ** Amount = Purchases column value from Usage Report" --> |
| **Withdrawals / usage** — stock consumed in production | the category's **Expense** account | the category's **Asset** account | the Usage value <!-- Source: NXT-70295:AC "Debit → Valuation Category's Expense GL Account ** Credit → Valuation Category's Asset GL Account ** Amount = Usage value from Usage Report" --> |
| **Add to inventory** — stock added back | the category's **Asset** account | the category's **Expense** account | the Add to Inventory value <!-- Source: NXT-70295:AC "Debit → Valuation Category's Asset GL Account ** Credit → Valuation Category's Expense GL Account ** Amount = Add to Inventory value from Usage Report" --> |
| **Transfer out** — stock sent to another site | the category's **Expense** account | the category's **Asset** account | the Transfers value <!-- Source: NXT-70295:AC "*Scenario: Transfer-out posting* ... Debit → Valuation Category's Expense GL Account ** Credit → Valuation Category's Asset GL Account ** Amount = Transfers In value from Usage Report" --> |
| **Transfer in** — stock received from another site | the category's **Asset** account | the category's **Expense** account | the Transfers value <!-- Source: NXT-70295:AC "*Scenario: Transfer-in posting* ... Debit → Valuation Category's Asset GL Account ** Credit → Valuation Category's Expense GL Account ** Amount = Transfers In value from Usage Report" --> |

(Backend codes for the curious — you never type these: purchases `PURCH`, withdrawals `WD`, add-to-inventory `ADDINV`, transfer-out `INVTRFRFR`, transfer-in `INVTRFRTO`.) <!-- Source: NXT-70295:desc "Period-close batch postings for 5 entry types: PURCH, WD, ADDINV, INVTRFRFR, INVTRFRTO." -->

> 🔧 **Implementer note — Purchases is the odd one out.** For every other entry type, both the debit and the credit come from the same Valuation Category mapping. Purchases is the only type where the credit side is a **single configured Cash in Bank account** instead. <!-- Source: NXT-70295:AC "Credit → Cash in Bank GL Account (single configured account, not derived from Valuation Category mapping)" --> Configure that one Cash in Bank account when you set up inventory posting.

⚠️ **Watch-out — one missing mapping blocks the entire site-period.** If *any* Valuation Category in scope is missing its Asset **or** Expense account, **nothing posts for that site-period** — not even the entry types that don't touch the unmapped category. <!-- Source: NXT-70295:AC "*Then* no posting job runs for any entry type in that site-period — including entry types that do not use the Valuation Category with the missing mapping" --> Finish all your category mappings (Job 2, Phase 5) before you expect a clean close.

⚠️ **Watch-out — it's all-or-nothing on validation.** If one entry type in the batch fails validation (for example a rounding imbalance), the **whole** site-period batch is rejected, zero entries are created, and the reason is logged. <!-- Source: NXT-70295:AC "*Then* zero entries are created for the entire site-period batch" --> <!-- Source: NXT-70295:AC "*Then* the entire posting batch for that site-period is rejected and the error is logged in the Posting Activity Log" -->

### B2. What you'll see in Job 8 (Journal/Ledger) and Job 10 (Activity Log) for inventory **(Coming)**

Posted inventory entries will appear in the **Journal and Ledger right alongside** your POS and manual entries. <!-- Source: NXT-70295:AC "*Then* the posted inventory entries appear alongside POS and manual entries" --> You'll be able to tell them apart: each one shows its **source module ("Inventory")**, its entry-type code and name (for example "Withdrawals"), the site, and the Valuation Category. <!-- Source: NXT-70295:AC "*Then* it displays source module (\"Inventory\"), entry type code and name (e.g., \"WD — Withdrawals\"), site, and Valuation Category" --> Open any entry and the detail will show the entry type, the Valuation Category, the **list of source transaction IDs** from inventory that were rolled into it, the posting date, and the site. <!-- Source: NXT-70295:AC "** Entry type (e.g., \"WD — Inventory Withdrawals\") ** Valuation Category ** List of source transaction IDs from the inventory module that were aggregated into the entry ** Posting date ** Site" --> You can filter the ledger by site, fiscal year, financial period, GL account, and entry type. <!-- Source: NXT-70295:AC "*Then* entries are filterable by site, fiscal year, financial period, GL account, and entry type" -->

In **Job 10 (Posting Activity Log)**, a successful inventory close logs a confirmation for the site-period; a failure logs the **specific reason**. <!-- Source: NXT-70295:AC "*Then* a log entry confirms successful completion for that site-period" --> <!-- Source: NXT-70295:AC "*Then* a log entry shows the specific failure reason for that site-period" -->

> 🔧 **Implementer note — reopening and re-closing a period (how corrections work).** If you reopen a posted inventory period, the posting batch in the Periods view shows that state. <!-- Source: NXT-70295:AC "*Then* the corresponding posting batch in the Periods view reflects this state" --> When you re-close it, the system reposts **only if you have the repost setting enabled** in Periods — otherwise nothing happens. <!-- Source: NXT-70295:AC "*Then* the system automatically initiates a repost for that site-period" --> <!-- Source: NXT-70295:AC "*Given* a previously-posted inventory period has been reopened and the user has the repost setting disabled in Periods *When* the period is re-closed *Then* no repost is initiated" --> A repost never edits or deletes the original entries — they stay in the ledger with their original values. <!-- Source: NXT-70295:AC "*Then* the original entries remain unmodified and undeleted with their original values" --> Instead it writes **reversal entries** dated to the **original posting date** (not today), with every amount inverted (debits become credits), each referencing the entry it reverses; then it posts a fresh batch under the same rules. <!-- Source: NXT-70295:AC "*Then* each reversal entry's posting date equals the original entry's posting date (last day of the inventory period), not today's date" --> <!-- Source: NXT-70295:AC "*Then* all amounts are the exact inverse of the originals (debits become credits, credits become debits) and each reversal references the original entry it reverses" -->

> ⚠️ **Known limitation — two kinds of waste won't tie out.** Waste recorded through a withdrawal reason code **is** included in the withdrawal postings above. Production-record waste (from Insights) uses fair-market-value estimates and **will not reconcile** to those withdrawal-based postings. This is a documented product limitation, not a bug. <!-- Source: NXT-70295:AC "Waste/spoilage via withdrawal reason codes is included in WD postings." --> <!-- Source: NXT-70295:AC "Production-record waste (Insights) uses fair market value estimates and will not reconcile to withdrawal-based postings." --> <!-- Source: NXT-70295:desc "This is a *documented product limitation*, not a bug." -->

> 📌 **Source-of-truth note:** every dollar amount in inventory postings comes from the inventory module's own valuation (the Valuation/Usage reports). Financials does **not** recompute inventory values — it consumes what inventory provides. <!-- Source: NXT-70295:desc "Financials does not independently calculate inventory values; it consumes what inventory provides." -->

### B3. A finer purchase grain is being added: by Vendor **(Coming)**

🎯 **The job:** keep purchase postings manageable in the GL while still being able to reconcile them back to what each vendor was paid.

A later refinement will post purchases at **Valuation Category × Vendor** detail — one total per site, period, vendor, and category. <!-- Source: NXT-70620:AC "*Then* exactly 3 debit/credit pairs are created (V1/Food, V1/NonFood, V2/Food), and no receipt/item-level pairs exist." --> Each pair debits the category's **Inventory Asset** account and credits the configured **Cash in Bank** account. <!-- Source: NXT-70620:AC "*Then* Debit = VC's Inventory Asset GL *And* Credit = configured Cash in Bank GL." --> The posted amount uses the **Total Receipt Amount**, not market value. <!-- Source: NXT-70620:AC "the posted total equals *Total Receipt Amount / Amount*, not Market Value." -->

⚠️ **Watch-outs (when this ships):**

- A receipt with no vendor is grouped under **"Unknown Vendor"** and still posts; totals still tie to the period's Total Receipt Amount. <!-- Source: NXT-70620:AC "*Then* amounts from those receipts are included under Vendor = \"Unknown Vendor\" *And* totals still tie to the period's Total Receipt Amount." -->
- A missing category mapping blocks posting and the error **lists every** missing mapping, not just the first. <!-- Source: NXT-70620:AC "*Then* nothing posts *And* the error lists VC2 as missing (and any other missing mappings)." -->
- A closed period with **zero receipts** posts nothing and the job is still marked **successful** with "0 entries created." <!-- Source: NXT-70620:AC "*Then* zero PURCH entries are created *And* job is marked successful with \"0 entries created.\"" -->

> 📌 **Open relationship note:** NXT-70620 (Vendor-level detail) and NXT-70295's purchase entry (category-level) both describe the purchase posting and are at different refinement stages. Confirm with the SME which grain ships first so the guide states one, not both, as current. *(Interpretation, not from AC.)*

## Part C — Reimbursements and other inventory entries on the roadmap **(Coming)**

> ⚠️ Everything in Part C is upcoming (status **New**). These are specified but not built; treat as roadmap.

### C1. Reimbursement Claim and Reimbursement Received **(Coming)**

🎯 **The job:** your state and federal meal-program money flows into the ledger as receivables when you claim it, then as cash when it arrives.

Two separate entries, created **by site**: <!-- Source: NXT-66385:AC "Ledger entries are created by site for each claim and reimbursement." -->

- **Reimbursement Claim** — **Debit: Due from Federal Funds** (a receivable), **Credit: the reimbursement revenue account**; dated the **last day of the claim period**. <!-- Source: NXT-66385:AC "*Reimbursement Claim* *** *Debit:* Due from Federal Funds (Asset) *** *Credit:* Reimbursement Program System Accounts (Revenue)" --> <!-- Source: NXT-66385:AC "_Reimbursement Claim_ (GLEntryTypeCd = RMBRSCLM) entries use the last day of the claim period as posting date." --> (Backend codes: `RMBRSCLM`; receivable `DUEFEDF`; revenue `RMBRSMNT`.)
- **Reimbursement Received** — **Debit: Cash in Bank**, **Credit: Due from Federal Funds** (clearing the receivable); dated the **current date**. <!-- Source: NXT-66385:AC "*Reimbursement Received* *** *Debit:* Cash in Bank (Asset) *** *Credit:* Due from Federal Funds (Asset)" --> <!-- Source: NXT-66385:AC "_Reimbursement Received_ (GLEntryTypeCd = RMBRSRCVD) entries use the current date as posting date." --> (Backend codes: `RMBRSRCVD`; cash `CASHBNK`.)

These entries will be visible in the General Ledger journal and View Ledger, with site-level drill-down, and flow into financial statements as revenue and assets. <!-- Source: NXT-66385:AC "Entries are visible in the General Ledger journal and View Ledger pages. ** Users can drill down to see site-level breakdowns. ** Reimbursement claim and received amounts flow into financial statements as revenue and assets." -->

⚠️ **Watch-out (when this ships) — resubmitting a claim reverses the old one first.** If a claim is recreated and resubmitted, the system auto-generates rollback entries that reverse the originals (the debit/credit sides swap) **before** posting the new claim and received entries from the updated data. <!-- Source: NXT-66385:AC "If a claim is recreated and resubmitted, rollback ledgers are automatically generated before new postings." --> <!-- Source: NXT-66385:AC "After rollback entries are posted, the new Claim and Reimbursement entries are created using the updated data." -->

> 📌 **Conflict to flag (don't pick silently):** NXT-66385 says Reimbursement *Received* posts to the **current date**, while the inventory-side stories post everything to the period's last day. These are different flows, so both can be right — but confirm the **Received = current date** rule with the SME, since it's the one posting in this whole section that does *not* use a period-end date. <!-- Source: NXT-66385:AC "_Reimbursement Received_ (GLEntryTypeCd = RMBRSRCVD) entries use the current date as posting date." -->

### C2. Other inventory entries specified but not yet built **(Coming)**

These overlap with the inventory engine in B1 and are tracked separately; the consistent rule across all of them is **posting date = last day of the inventory period** and **rollbacks reverse the entries** on a repost. <!-- Source: NXT-66386:AC "Posting date = last day of inventory period." --> <!-- Source: NXT-66386:AC "Rollbacks: Reverse entries if reposted." -->

- **Inventory usage, including commodity (USDA) usage** — usage debits Expense, credits Asset; commodity usage is the same shape valued at **Standard Price**, and both flow to the P&L as food expense and reduce inventory on the Balance Sheet. <!-- Source: NXT-66386:AC "_Usage (GLEntryTypeCd: WD)_ → Debit Expense, Credit Asset. ** _Commodity Usage (GLEntryTypeCd: COMMUSG, Value = Standard Price)_ → Debit Expense, Credit Asset." --> <!-- Source: NXT-66386:AC "Entries visible in GL journal/View Ledger, flow to P&L as food expense and Balance Sheet as reduced inventory." -->
- **Withdrawals / waste** — debits Expense, credits Asset, so unusable stock leaves assets and is recorded as waste expense. <!-- Source: NXT-66389:AC "_Withdrawal/Waste (GLEntryTypeCd: WD or WASTE depending on setup)_ → Debit Expense, Credit Asset." --> <!-- Source: NXT-66389:AC "Entries flow into GL and financial statements as waste expense." -->
- **Inventory transfers (site ↔ warehouse)** — debits the receiving site's Asset, credits the warehouse's Asset, so stock movement shifts balances between locations with **zero net effect** across the district. <!-- Source: NXT-66387:AC "_Warehouse Receives (GLEntryTypeCd: WHIRCV, Multisite)_ → Debit Site Asset, Credit Warehouse Asset." --> <!-- Source: NXT-66387:AC "net effect is zero across district but shifts balances between locations." -->
- **Warehouse fees (delivery, processing)** — debits the site's Expense, credits the warehouse's Expense, capturing those costs as operational expense. <!-- Source: NXT-66388:AC "_Warehouse Receives Commodity Fees (GLEntryTypeCd: None, Multisite)_ → Debit Site Expense, Credit Warehouse Expense." --> <!-- Source: NXT-66388:AC "Entries flow into food cost/operational expense reporting." -->

⚠️ **Watch-out — these stories contradict the "Approve/Post buttons are gone" promise.** Usage/commodity posting AC describes an **Approve / Post / Reapprove** control governed by a checkbox-state matrix. <!-- Source: NXT-66386:AC "The availability of Approve, Post, and Reapprove follows the checkbox state matrix (see attached rules)." --> That conflicts with the guide's headline claim that posting is fully automatic with no Post button. This is part of the broader Job 10 contradiction (the manual-posting wave above) — flag it; do not present "fully automatic, no buttons" as settled while these stories are in flight.

> 📌 **Open question (warehouse codes):** NXT-66388 (warehouse fees) and one transfer line in NXT-66387 state the entry type code as "None," and NXT-66389 says the waste code is "`WD` or `WASTE` depending on setup." <!-- Source: NXT-66388:AC "_Warehouse Receives Commodity Fees (GLEntryTypeCd: None, Multisite)_" --> <!-- Source: NXT-66389:AC "_Withdrawal/Waste (GLEntryTypeCd: WD or WASTE depending on setup)_" --> The user-facing entry-type label is not finalized in AC — leave it as a placeholder and confirm with the SME before publishing.

## Under the hood — why this all balances (for the curious) **(Coming)**

> 🔧 You don't operate this directly, but it's worth knowing what produces these lines. A single posting engine takes each source transaction (meal sales, inventory, payroll), looks up the matching debit/credit rule in one central rules table, and swaps the system-account codes in that rule for **your** district's actual GL accounts using your account mapping. <!-- Source: NXT-65485:AC "For each transaction, it finds the matching debit and credit rule from our central rules table." --> <!-- Source: NXT-65485:AC "It replaces the system account codes from the rule with the correct GL accounts for that customer, using their account mapping." --> It writes one debit line and one credit line per transaction with matching amounts so the ledger stays balanced. <!-- Source: NXT-65485:AC "It creates one debit line and one credit line for each transaction, making sure the amounts match so the ledger stays balanced." -->

This is why two things in this guide are reliably true: a transaction that **can't** find a rule or a mapped account still shows up — flagged as needing a fix rather than silently dropped <!-- Source: NXT-65485:AC "If a transaction can't find a matching rule or account mapping, it still shows in the results, but is marked as needing a fix." --> — and re-running posting for the same period and data always produces the **same** result. <!-- Source: NXT-65485:AC "Running the procedure again for the same period and data will always give the same results." -->

## Quick reference — what posts, what's live

| Flow | Debit | Credit | When it posts | Status |
|---|---|---|---|---|
| Meal-sales revenue | Cash in Bank + Prepaid balance | Meal sales + À la carte | POS period close, dated period's last day | **Live** |
| Sales tax | Cash in Bank | Sales Tax Owed (liability) | POS period close, dated period's last day | **Live** |
| Purchases | Category Asset | Cash in Bank (one configured acct) | Inventory period close, dated period's last day | (Coming) |
| Withdrawals / usage / waste | Category Expense | Category Asset | Inventory period close | (Coming) |
| Add to inventory | Category Asset | Category Expense | Inventory period close | (Coming) |
| Transfer in / out | Asset ↔ Expense (per direction) | (per direction) | Inventory period close | (Coming) |
| Reimbursement Claim | Due from Federal Funds | Reimbursement revenue | Claim period's last day | (Coming) |
| Reimbursement Received | Cash in Bank | Due from Federal Funds | Current date | (Coming) |

---

<!-- ============================================================ -->
<!-- C2 — NEW SECTION (Job 11, Roles & Permissions). ALL THREE tickets status New => entire section (Coming). -->
<!-- ============================================================ -->

# Job 11 (Coming) — "Decide who can touch the ledger, and what they'll see"

> **(Coming)** — Roles & permissions for Financials 2.0 are **in development** (Jira: NXT-66927, NXT-66928, NXT-66929, all *New*). Build your access plan now, but treat every behavior below as the **specified** design, not something you can click today. Nothing in this section is live yet.

**TL;DR:** Three access tiers ship with Financials 2.0 — **full-access admins**, a **Finance Coordinator** who configures everything but is fenced out of a few transaction and period actions, and a **read-only Cafeteria Manager**. Pick the tier per person before go-live; the lower two tiers are *not* "admin with a few boxes unchecked."

**When this is your job:** Week 0–1, during environment setup — right alongside registering imports and confirming site codes. "What will my cafeteria managers actually see?" is a go-live-gating question, and the answer is fixed by role.

**Who this is for:** Everyone the guide already addresses — the CN Director, Finance Manager/Director, Business Administrator, accountants who touch the ledger, *and* the Cafeteria Managers who only need to look. Each maps to exactly one of the three tiers below.

> 🔧 **Implementer:** This is a real onboarding decision, not a checkbox sweep. The three tiers behave differently *by design* — selecting a role pre-sets its permission boxes, and two of the three tiers have a default master toggle state that tells you at a glance what kind of role you picked. Walk the customer through "who is each person, and which tier do they need" before anyone logs in.

## The three tiers at a glance

Each tier below is the permission set Financials 2.0 will apply when that role accesses the module. <!-- Source: NXT-66928:AC "*When* I access the Financial Oversight module / *Then* I should have the following permissions:" --> Read down the column that matches the person you're setting up.

| Area | **Director / Central Office / SchoolCafe Admin** | **Finance Coordinator** | **Cafeteria Manager** |
|---|---|---|---|
| Dashboard | Full — view, edit, add, delete, configure layout | View only | View only |
| Configuration (GL structure, Account Mapping, Import/Export templates, Version History) | Full — view, edit, add, delete | **Full** — view, edit, add, delete | **View only** — cannot change anything |
| Manual journal entries | Full — view, edit, add, delete | View, edit, add (**no delete**) | View only |
| Posting from POS / Inventory | Full | View only | **No access** |
| Void / Reverse a transaction | Full | Can void/reverse (edit) | **No access** |
| Reports (P&L, Balance Sheet, Site-Level Analysis) | Full | View only | View only |
| Export reports to ERP | Full | View only | **No access** |
| Period management (open/close periods, fiscal year) | Full | **Edit only** | **No access** |
| Default master toggle when role is selected | "Disable All" (everything already on) | (not specified — see Open Questions) | "Enable All" (most things off) |

> The three tiers are deliberately different shapes — a full admin, a configuration-heavy coordinator who is fenced out of deletes and most of period/report management, and a look-but-don't-touch manager. Match the person to the shape, not to a count of checkboxes.

## Tier 1 — Director, Central Office, SchoolCafe Administrator: full access

These three roles get the keys to everything, and they all get the **same** keys. <!-- Source: NXT-66928:AC "All three roles (Director, Central Office, SchoolCafe Administrator) have identical permissions" --> There are no restrictions on any feature. <!-- Source: NXT-66928:AC "I have FULL access to ALL modules and features" --> <!-- Source: NXT-66928:AC "No restrictions apply to any feature or capability" -->

What "full access" covers for these roles:

- **Everything is view, edit, add, and delete** across all Financials functions. <!-- Source: NXT-66928:AC "I can VIEW, EDIT, ADD, and DELETE across all Financial Oversight functions" -->
- **The dashboard** — view, edit, add, delete, and configure layouts and settings. <!-- Source: NXT-66928:AC "FULL access to Financial Oversight dashboard" --> <!-- Source: NXT-66928:AC "I can configure dashboard layouts and settings" -->
- **Configuration** — full access to GL structure (the Account Code Structure in this guide's terms), Account Mapping, Import/Export templates, and Version History. <!-- Source: NXT-66928:AC "GL Code Structure: FULL access (VIEW, EDIT, ADD, DELETE)" --> <!-- Source: NXT-66928:AC "Account Mapping: FULL access (VIEW, EDIT, ADD, DELETE)" --> <!-- Source: NXT-66928:AC "Import/Export Templates: FULL access (VIEW, EDIT, ADD, DELETE)" --> <!-- Source: NXT-66928:AC "Version History: FULL access (VIEW, EDIT, ADD, DELETE)" -->
- **Transactions** — full access to manual entries, posting from POS/Inventory, transaction search, and void/reverse. <!-- Source: NXT-66928:AC "Manual Entries: FULL access (VIEW, EDIT, ADD, DELETE)" --> <!-- Source: NXT-66928:AC "Post from POS/Inventory: FULL access (VIEW, EDIT, ADD, DELETE)" --> <!-- Source: NXT-66928:AC "Void/Reverse: FULL access (VIEW, EDIT, ADD, DELETE)" -->
- **Period management** — full control, including opening and closing financial periods and managing fiscal-year configurations (the same Periods work covered in Job 4). <!-- Source: NXT-66928:AC "I can open/close financial periods" --> <!-- Source: NXT-66928:AC "I can manage fiscal year configurations" -->
- **Reports** — full access to every report, including Export to ERP. <!-- Source: NXT-66928:AC "Export to ERP: FULL access (VIEW, EDIT, ADD, DELETE)" -->

What it looks like when this role is selected: every permission box is turned on automatically, and the master toggle reads **"Disable All"** by default — because there's nothing left to enable. <!-- Source: NXT-66928:AC "All permission checkboxes are automatically enabled when any of these three roles is selected" --> <!-- Source: NXT-66928:AC "Master toggle shows \"Disable All\" by default (since all permissions are enabled)" --> A full-access user also sees every saved configuration, no matter who created it. <!-- Source: NXT-66928:AC "All saved configurations are accessible regardless of who created them" -->

> 🔧 **Implementer:** Use the master-toggle state as your sanity check. If you select a Director-tier role and the toggle does **not** read "Disable All" with everything on, the role mapping is wrong — stop before you hand the environment over.

> ⚠️ **Watch out:** "Full access" really is full — including delete. These three roles can delete configuration, delete transactions, and delete dashboard elements. Reserve the Director tier for the people who genuinely need that reach; use the Finance Coordinator tier (below) for day-to-day configuration work that shouldn't include deleting posted-ledger data.

## Tier 2 — Finance Coordinator: configure everything, but fenced out of deletes, reports, and most of periods

This is the tier for the Finance Manager / accountant who *runs* the configuration but shouldn't have a delete-everything key. It's the most granular of the three. <!-- Source: NXT-66927:AC "*Given* I am logged in as a Finance Coordinator / *When* I access the Financial Oversight module / *Then* I should have the following permissions:" -->

**Where the Finance Coordinator has full power — Configuration.** They get full access to the Configuration module: GL structure, Account Mapping, Import/Export templates, and Version History, all view/edit/add/delete. <!-- Source: NXT-66927:AC "I have FULL access to the Configuration module" --> <!-- Source: NXT-66927:AC "GL Code Structure: FULL access (VIEW, EDIT, ADD, DELETE)" --> <!-- Source: NXT-66927:AC "Account Mapping: FULL access (VIEW, EDIT, ADD, DELETE)" --> <!-- Source: NXT-66927:AC "Import/Export Templates: FULL access (VIEW, EDIT, ADD, DELETE)" --> <!-- Source: NXT-66927:AC "Version History: FULL access (VIEW, EDIT, ADD, DELETE)" --> In practice that means a Finance Coordinator can own Jobs 1 and 2 (chart of accounts, account mapping) end to end.

**Where they're fenced in — transactions.** They can view, edit, and add transaction-management functions, but they **cannot delete** transactions and do not get full access. <!-- Source: NXT-66927:AC "I can VIEW, EDIT, and ADD transaction management functions" --> <!-- Source: NXT-66927:AC "I cannot DELETE transactions or have FULL access" --> Specifically:

- **Manual entries** — view, edit, and add (the Job 6 flow), but no delete. <!-- Source: NXT-66927:AC "Manual Entries: I can VIEW, EDIT, and ADD manual entries" -->
- **Posting from POS/Inventory** — view only. <!-- Source: NXT-66927:AC "Post from POS/Inventory: I can VIEW only" -->
- **Void / Reverse** — they *can* do this. The reverse-a-bad-posting flow from Job 7 is available to the Finance Coordinator. <!-- Source: NXT-66927:AC "Void/Reverse: I can EDIT transactions (void/reverse capability)" -->

**Reports — view only.** A Finance Coordinator can read every report but cannot edit, add, delete, or export them. P&L, Balance Sheet, and Site-Level Analysis are all view-only, including Export to ERP. <!-- Source: NXT-66927:AC "I can VIEW all reports but cannot modify them" --> <!-- Source: NXT-66927:AC "I cannot EDIT, ADD, DELETE, or have FULL access to reports" --> <!-- Source: NXT-66927:AC "Export to ERP: VIEW only" -->

**Period management — edit only.** This is the narrowest slice: the Finance Coordinator can **edit** period settings, but cannot view (as a separate permission), add, delete, or hold full access to period management. <!-- Source: NXT-66927:AC "I can EDIT period settings" --> <!-- Source: NXT-66927:AC "I cannot VIEW, ADD, DELETE, or have FULL access to period management" -->

**Dashboard — view only**, with no edit/add/delete and no dashboard-configuration rights. <!-- Source: NXT-66927:AC "I can VIEW the Financial Oversight dashboard" --> <!-- Source: NXT-66927:AC "I cannot EDIT, ADD, or DELETE dashboard elements" -->

How the permission screen behaves for this tier: the parent-module **"FULL access" toggle is a shortcut** — turning it on for a module flips on all of that module's child permissions at once; if you then change an individual box, the "FULL access" indicator updates to match. <!-- Source: NXT-66927:AC "When I click FULL access on a parent module, all child permissions are automatically enabled" --> <!-- Source: NXT-66927:AC "When I modify individual permissions, the FULL access indicator updates accordingly" --> The Finance Coordinator can also save a permission configuration for reuse in future sessions. <!-- Source: NXT-66927:AC "I can save my permission configurations for future sessions" -->

> ⚠️ **Watch out — "edit periods" is not "open/close periods" in the AC.** The Finance Coordinator AC grants *edit* on period settings and explicitly withholds full access; the open/close-periods and fiscal-year wording lives only in the Director tier. Don't assume a Finance Coordinator can close a period the way an admin can until the exact period actions are confirmed (see Open Questions). This matters because period close is what releases posting in Job 4 / Job 10.

> 🔧 **Implementer:** The Finance Coordinator is the right default for "the person who sets up and maintains Financials but isn't the district's top admin." They can do all of Job 1 and Job 2, make and reverse journal entries (Jobs 6–7), and read every report — but they can't delete transactions or export to the ERP, and their period control is limited to editing settings. If your customer needs that person to also close periods or push exports, they need the Director tier, or you flag the gap to the product owner.

## Tier 3 — Cafeteria Manager: read-only / limited

This is the "look, don't touch" tier. A Cafeteria Manager can see relevant financial information but cannot change financial data. <!-- Source: NXT-66929:AC "*Given* I am logged in as a Cafeteria Manager / *When* I access the Financial Oversight module / *Then* I should have the following permissions:" -->

What a Cafeteria Manager **can** see:

- **The dashboard** — view only; no edit, add, delete, or full access. <!-- Source: NXT-66929:AC "I can VIEW the Financial Oversight dashboard" --> <!-- Source: NXT-66929:AC "I cannot EDIT, ADD, DELETE, or have FULL access to dashboard elements" -->
- **Configuration — view only.** They can look at configuration settings (GL structure, Account Mapping, Import/Export templates, Version History) but cannot modify any of them. <!-- Source: NXT-66929:AC "I can VIEW configuration settings but cannot modify them" --> <!-- Source: NXT-66929:AC "GL Code Structure: VIEW only" --> <!-- Source: NXT-66929:AC "Account Mapping: VIEW only" --> <!-- Source: NXT-66929:AC "I cannot EDIT, ADD, or DELETE any configuration items" -->
- **Manual entries and transaction search — view only.** <!-- Source: NXT-66929:AC "Manual Entries: VIEW only" --> <!-- Source: NXT-66929:AC "Transaction Search: VIEW only" -->
- **Reports — view only**, including P&L, Balance Sheet, and Site-Level Analysis. <!-- Source: NXT-66929:AC "I can VIEW all reports but cannot modify them" --> <!-- Source: NXT-66929:AC "Profit & Loss: VIEW only" --> <!-- Source: NXT-66929:AC "Balance Sheet: VIEW only" --> <!-- Source: NXT-66929:AC "Site-Level Analysis: VIEW only" -->

What a Cafeteria Manager **cannot reach at all** (not even view):

- **Posting from POS/Inventory** — no access. <!-- Source: NXT-66929:AC "Post from POS/Inventory: No access (cannot VIEW, EDIT, ADD, or DELETE)" -->
- **Void / Reverse** — no access; the Job 7 fix-a-bad-posting flow is not available to this tier. <!-- Source: NXT-66929:AC "Void/Reverse: No access (cannot VIEW, EDIT, ADD, or DELETE)" -->
- **Export to ERP** — no access. <!-- Source: NXT-66929:AC "Export to ERP: No access (cannot VIEW, EDIT, ADD, or DELETE)" -->
- **Period management** — no access of any kind. <!-- Source: NXT-66929:AC "I have no access to period management" --> <!-- Source: NXT-66929:AC "I cannot VIEW, EDIT, ADD, DELETE, or have FULL access to period settings" -->

How the permission screen behaves for this tier: most boxes start **unchecked** when Cafeteria Manager is selected, only the view permissions for reachable modules are enabled, and the master toggle reads **"Enable All"** by default — the mirror image of the Director tier. <!-- Source: NXT-66929:AC "Most permission checkboxes remain unchecked when Cafeteria Manager role is selected" --> <!-- Source: NXT-66929:AC "Only VIEW permissions are enabled for accessible modules" --> <!-- Source: NXT-66929:AC "Master toggle shows \"Enable All\" by default (since most permissions are disabled)" -->

> ⚠️ **Watch out:** When a Cafeteria Manager tries something they're not allowed to do, they get an **"Access Denied"** message rather than a silent no-op — so "I clicked it and nothing happened" is usually a sign the action was blocked, not broken. <!-- Source: NXT-66929:AC "I receive appropriate \"Access Denied\" messages when attempting restricted actions" -->

> 🔧 **Implementer:** This is the answer to "what will my cafeteria managers see?" — the dashboard, configuration, manual entries, transaction search, and reports, all read-only; and nothing at all for posting, void/reverse, ERP export, or periods. Set this expectation with the customer's site staff up front so a Cafeteria Manager isn't surprised by an "Access Denied" on day one.

## How role switching behaves

Where AC specifies it, a tier's permission set is sticky: switching away from a role and back restores that role's permissions rather than leaking the previous role's access. This is stated for two of the three tiers:

- A **Cafeteria Manager's** limited set is maintained when switching between roles and returning. <!-- Source: NXT-66929:AC "My limited permission set is maintained when switching between roles and returning to Cafeteria Manager" -->
- The **Director tier** maintains full permissions across switches between Director, Central Office, and SchoolCafe Administrator. <!-- Source: NXT-66928:AC "Role switching between Director, Central Office, and SchoolCafe Administrator maintains full permissions" -->

> ⚠️ **Watch out:** The "permission set is maintained on role switch" guarantee is stated per-tier in the Cafeteria Manager and Director ACs. The Finance Coordinator AC does not restate it in those words — do not assume identical switch behavior for the Coordinator tier beyond what its own AC covers (see Open Questions).

## What gets logged

Permission and configuration changes are auditable — consistent with the rest of Financials 2.0, where the ledger and configuration history keep a trail (Jobs 1, 2, 7, 8).

- For the Finance Coordinator tier, **all permission changes are logged and auditable**. <!-- Source: NXT-66927:AC "All permission changes are logged and auditable" -->
- For the Director tier, **permission changes are logged with an audit trail for each role**. <!-- Source: NXT-66928:AC "Permission changes are logged with appropriate audit trail for each role" -->

(No audit-logging line appears in the Cafeteria Manager AC — unsurprising, since that tier can't change permissions. Don't infer the absence of an audit trail for that role; it simply isn't specified there.)

## What this is renamed from / where it sits relative to the rest of the guide

This is a **new** capability area, not a renamed legacy one — there's no legacy→2.0 glossary row for it yet. Two framing notes so it lines up with the rest of the guide:

- The AC for all three tiers calls the product the **"Financial Oversight module."** This guide calls it **Financials 2.0**. Treat those as the same module until a customer-facing module name is confirmed. <!-- Source: NXT-66928:AC "*When* I access the Financial Oversight module" -->
- The permission areas in the AC line up with the Jobs you already know: *Configuration* = Jobs 1–3 (chart of accounts, mapping, posting settings); *Transaction Management* = Jobs 6–7 (manual entries, reversals) plus posting; *Reports* = Job 9; *Period Management* = Job 4; *Dashboard* = Job 0 (Financial Dashboard). The AC module **labels** ("Transaction Management," "GL Code Structure") are quoted from the tickets and may not be the exact on-screen labels in this guide's wording — see Open Questions.

## Open Questions (for the SME / product owner — do not invent answers)

These are gaps the AC does **not** resolve. Per the no-invented-specifics rule, they're surfaced rather than filled.

1. **Where does the roles/permissions screen live?** No AC states a menu path (no `Configuration › …` location) or the page name for managing roles/permissions. *Needs a confirmed navigation path before this section can tell a user where to click.*
2. **What is the exact role-picker label and the canonical role names in the UI?** AC names the roles ("Finance Coordinator," "Director," "Central Office," "SchoolCafe Administrator," "Cafeteria Manager") but not the on-screen selector label or whether these are exactly how they appear in the role dropdown. The Finance Coordinator desc field says "Finance Manager"; AC says "Finance Coordinator" — *confirm which is the product term.*
3. **Do the AC module labels match this guide's labels?** AC uses "Transaction Management," "GL Code Structure," "Import/Export Templates." The guide uses "Journal & Ledger," "Account Code Structure," and the Imports & Exports area. *Confirm the permission-screen labels so prose can use the real ones instead of straddling both.*
4. **What is the Finance Coordinator's default master-toggle state?** AC gives the default toggle state for the Director tier ("Disable All") and the Cafeteria Manager tier ("Enable All") but is silent for the Finance Coordinator. *Left blank in the table on purpose — needs confirmation.*
5. **"Edit periods" vs. "open/close periods" for the Finance Coordinator.** AC grants the Coordinator "EDIT period settings" and withholds full access; the open/close-periods and fiscal-year wording appears only in the Director AC. *Confirm exactly which period actions the Coordinator can perform — this gates who can release posting.*
6. **Does the Coordinator's permission set persist on role switch?** Stated explicitly for the Cafeteria Manager and Director tiers; not stated for the Finance Coordinator. *Confirm before claiming identical behavior.*
7. **Exact restricted-action message strings.** AC quotes "Access Denied" for the Cafeteria Manager. *Confirm whether the same string is used for blocked actions in the other tiers, and whether it varies by action.*

---

# The First-90-Days Cheat Sheet

Print this. Tape it to a monitor.

**Week 0 (implementer setup, before the customer logs in)**
- [ ] GL Accounts Import registered in Imports & Exports
- [ ] Opening Balance Import registered in Imports & Exports
- [ ] Payroll journal-entry import registered (if in scope)
- [ ] Site codes confirmed against site-code segment length

**Week 1**
- [ ] Account code structure saved
- [ ] CoA imported (warnings noted, not necessarily fixed yet)
- [ ] Fiscal year + period frequency configured

**Week 2**
- [ ] Structure warnings on CoA resolved
- [ ] Account Mapping: Phase 1 (subtract) and Phase 2 (bulk-map) done
- [ ] Posting Settings (Distributed vs. Centralized) chosen

**Week 3**
- [ ] Account Mapping Phase 3 overrides finished
- [ ] Opening balances imported and validated (debits = credits)
- [ ] One POS or Inventory period closed → test posting reviewed in Posting Activity Log

**Weeks 4–8**
- [ ] First real period close walked through with implementer
- [ ] First report (Trial Balance / P&L) generated and reviewed
- [ ] First manual entry made (even if just a $0 dummy to learn the flow)
- [ ] Reversal walkthrough completed

**Weeks 9–12**
- [ ] Automatic Entry Adjustments toggle decision made (most: leave off)
- [ ] First fiscal-year-equivalent rollover dry run scoped, even if not run

> 🔧 **Implementer:** Run a test posting on a single closed period before go-live and review the entries with the customer's finance team line by line. Catching mapping or base-type issues here is much cheaper than catching them after live data has been posted.

---

# Glossary — what it used to be called

| Legacy PrimeroEdge | Financials 2.0 |
|---|---|
| GL Code Segments | Account Code Structure |
| Parent Accounts | Account Categories |
| System Accounts | Data Points |
| GL Entry Types | Template Entries |
| Ad-Hoc Entries | Manual Entries |
| Approve / Post buttons | Removed from the first 2.0 build — a read-only monitor; posting runs in the background. <!-- Source: NXT-69493:AC "*Manual trigger*: Out of scope — jobs triggered from Fiscal Periods page, not here." --> **(Coming)** Per-site **Post / Repost / Remove** return on the POS and Inventory grids, and a **Review / Post All** queue returns on the Activity Log, for districts that post manually. <!-- Source: NXT-65487:AC "*Actions* (Post, View, Repost, Remove)" --> <!-- Source: NXT-66123:AC "*Actions* (Post, View, Repost, Remove)" --> <!-- Source: NXT-70065:AC "two actions: Review and Post All" --> "Gone" describes the first 2.0 build, not the end state. |
| Refunds Liability + Pay Refunds entries | (gone — single-step refund posting) |

> **Open question (do not invent a release label):** AC states no ship date or version name for the manual posting controls. This guide tags them **(Coming)** only — do not add a version/sprint/date to this Glossary row until the PO confirms one.

---

# When you're stuck

- **Posting didn't run.** → Posting Activity Log. The error reason is on the row.
- **Posting ran but the numbers look wrong.** → Open the Ledger for the affected account, find the transaction, click through to its line items. Reverse if needed.
- **Report shows a number you don't recognize.** → It came from a posted ledger entry. Find that entry. The chain is always: source event → posted entry → report.
- **The product won't let you do something.** → Almost always a base-type, period-state, or mapping check. The error message will say which.
- **The "Import" button doesn't show the import type you expected.** → That import type hasn't been registered yet in Imports & Exports (see Before-You-Touch step 4). Ping your implementer.
- **You see Post buttons or a "Ready to Post" queue the guide says are gone.** → You're on a newer build. The manual-posting wave (Job 10, Coming) brings per-site Post/Repost and a Review/Post-All queue back as an option. The "posting is automatic" story is the default, not the only mode.
- **You can't tell if a behavior is intentional.** → Check with your implementer. The product specs are the source of truth for fine-grained behavior.
