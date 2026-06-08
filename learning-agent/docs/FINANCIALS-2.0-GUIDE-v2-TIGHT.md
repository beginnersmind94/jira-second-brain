# Financials 2.0 · Internal Training

# Onboarding, Without the Yawn

*A jobs-to-be-done guide for the district finance and child-nutrition staff bringing Financials 2.0 online — and for the Cybersoft implementers walking them through it.*

**11 Jobs to be Done · 90-Day Cheat Sheet**

SchoolCafé · Cybersoft Implementation Team · June 2026 Edition

---

> **About this edition.** This guide was brought up to date against the Financials backlog using the Learning Studio **coverage + grounding gates**: every product-behavior claim folded in from the backlog traces to a verbatim quote from a ticket's Acceptance Criteria, carried in an inline `<!-- Source: NXT-####:AC "…" -->` comment. Everything in the body is **shipped behavior, written in the present tense**. Anything **specified but not yet shipped** has been moved out of your way into one place — the appendix, *"What's Coming Next."* If you go looking for an appendix feature and it isn't on your screen, the guide isn't wrong — it hasn't shipped yet.

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
| Click **Approve** then **Post** on three separate pages every period | Do nothing. Posting fires the moment the upstream POS or Inventory period closes — *true for the first 2.0 build* (manual Post / Repost controls are returning as an option; see the appendix) | You can no longer "forget to post." But you also can't post early. Mapping must be complete or nothing posts. |
| Have your CoA import rejected because one account code was off | Get a non-blocking import. Bad codes flag a warning; the rest land cleanly | Fix issues iteratively instead of being stuck in a reject-fix-reupload loop. |
| Map ~248 system accounts on the revenue side, even programs you don't run | Map ~72 data points, deactivate what you don't use, bulk-map the rest by section | Phase 1 of mapping is deletion, not data entry. |
| Manually do a "Pay Refunds" entry to clear the refunds-liability bucket | Get one balanced entry, no liability parking | Fewer accounts to manage. No accidentally orphaned liabilities. |
| Get a "dirty" flag on the financial period whenever POS reopened, even if nothing changed | See exactly what changed when source data is re-closed; auto-adjust if you opt in | No more pointless reposting. |
| Run reports against live data that drifted from what was posted | Generate reports from posted ledger entries only — async, downloaded from Document Center | The numbers in your report match the numbers in your ledger. Always. |
| Have a flat list of revenue accounts to map | Map by eligibility × program with bulk actions and a Program filter | Map all NSLP revenue in one click. |
| Create a separate GL Entry Type for every audit adjustment shape | Use one Template Entry that allows the same account on both debit and credit sides | Auditors can do anything they need without a support ticket. |
| Log in and hunt for "how is the district doing?" | Land on a **Financial Dashboard** — Net Income, Revenue, Expenses, a trend arrow, and a site-by-site table (see Job 0) | One screen answers "where do we stand?" before you touch setup. |

> ⚠️ **One headline to qualify up front.** This guide states that posting is automatic and the old **Approve / Post** buttons are gone. That is true for the first 2.0 build. A wave of work is in flight that brings manual **Post / Repost / Remove** controls and a **Review / Post All** queue back as an *option* for districts that want them — it has not shipped yet. See the appendix (Manual posting queues). If you see Post buttons on your screen, the product isn't broken; you're on a newer build.

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

# Job 0 — "See where my district stands the moment I log in" (Financial Dashboard)

**TL;DR:** The Financial Dashboard is your single-glance scoreboard — Net Income, Total Revenue, and Total Expenses for a period you pick at the top right, a trend arrow that tells you if the district is improving month over month, and a table breaking the numbers down site by site.

**When this is your job:** Login, day one and every day after. For a CN Director or Business Administrator this is usually the first screen you read — before you drop into the setup Jobs below.

**The three KPI cards.** The dashboard leads with Net Income, Total Revenue, and Total Expenses for whatever period you've selected. <!-- Source: NXT-68659:AC "Changing the period recalculates Net Income, Total Revenue, and Total Expenses and updates the card label (e.g., \"Net Income (June 2025)\")." --> Net Income is the headline number, shown big with dollar formatting — it's simply Total Revenue minus Total Expenses, and if the district is in the red it shows with a minus sign (e.g. `-$125,000`). <!-- Source: NXT-68659:AC "Net Income = Total Revenue – Total Expenses; if negative, show with a minus sign (e.g., -$125,000)." --> Total Revenue and Total Expenses sit underneath, each rounded to the nearest dollar. <!-- Source: NXT-68659:AC "Total Revenue and Total Expenses are shown below as smaller values, rounded to the nearest dollar." --> The card title carries the period in parentheses so you always know what window you're reading — e.g. "Net Income (June 2025)." <!-- Source: NXT-68659:AC "Changing the period recalculates Net Income, Total Revenue, and Total Expenses and updates the card label (e.g., \"Net Income (June 2025)\")." -->

The numbers are built from **posted General Ledger transactions only** — the same posted-ledger truth the rest of 2.0 runs on. <!-- Source: NXT-68659:AC "Data source is posted financial transactions from the General Ledger." --> Every active site is rolled in, <!-- Source: NXT-68659:AC "Calculations include all active sites." --> and only accounts whose base type is Revenue or Expense count toward the totals. <!-- Source: NXT-68659:AC "Only GL accounts with base type Revenue or Expense are included." -->

**The period selector (top right).** Pick your reporting window from the **"Period:"** dropdown in the top-right corner. <!-- Source: NXT-68659:AC "Period selector is a standard dropdown labeled “Period:” in the top right of the dashboard." --> Options are Current Month, Current Quarter, Current Fiscal Year, and a Custom Range. <!-- Source: NXT-68659:AC "Period options: Current Month (MMM YYYY), Current Quarter (Q# YYYY), Current Fiscal Year (FY YYYY), Custom Range." --> On load it defaults to **Current Fiscal Year** as of today, so you open to a year-to-date picture without touching anything. <!-- Source: NXT-68659:AC "Default period on dashboard load: Current Fiscal Year (FY ) as of today." --> The Current Fiscal Year and Current Quarter ranges come straight from your Fiscal Year Settings (the dates you configure in Job 4) and use *fiscal* quarters, not calendar quarters. <!-- Source: NXT-68659:AC "Current Fiscal Year date range comes from Fiscal Year Settings (start and end dates)." --> <!-- Source: NXT-68659:AC "Current Quarter uses fiscal quarters (Q1–Q4) defined by Fiscal Year Settings." --> The "Current …" ranges are system-defined — you can't hand-edit them; pick Custom Range when you need your own dates. <!-- Source: NXT-68659:AC "Period date ranges for the quarter, year-to-date and current month are system-defined and not user-editable." -->

> ⚠️ **The dashboard can move during an open period.** The totals include every posted transaction whose posting date falls in your window — **even if that fiscal period is still open.** <!-- Source: NXT-68659:AC "Include all posted transactions whose transaction/posting date falls within the selected period, even if the fiscal period is still open." --> A blank side reads as **0**, not an error: if there are no posted Revenue or Expense transactions, that column shows 0 and Net Income treats it as zero. <!-- Source: NXT-68659:AC "If there are no posted Revenue or Expense transactions in the selected period, show \"0\" for the respective column and calculate net income assuming it’s value as zero." -->

**The trend arrow (am I improving?).** Next to Net Income, a small arrow compares the **latest completed fiscal month** against the month before it — up if higher, down if lower, **no arrow if equal.** <!-- Source: NXT-68659:AC "Trend arrow compares Net Income for the latest completed fiscal month vs the immediately previous fiscal month." --> <!-- Source: NXT-68659:AC "If latest > previous show ↑; if less show ↓; if equal show no arrow." --> "Completed" means a fiscal month that has fully passed in real time. <!-- Source: NXT-68659:AC "A completed month = a fiscal month that has fully passed in real time." --> Brand-new districts won't see an arrow until two fiscal months are on the books. <!-- Source: NXT-68659:AC "Hide arrow if fewer than two completed fiscal months exist in the current fiscal year." -->

> ⚠️ **The arrow ignores the period dropdown.** Changing the period selector does **not** change what the arrow compares — it always looks at the two most recently completed fiscal months. <!-- Source: NXT-68659:AC "Trend arrow is not affected by the selected reporting period." --> The tooltip says it out loud: *"Trend compares the two most recently completed fiscal months."* <!-- Source: NXT-68659:AC "Tooltip: *“Trend compares the two most recently completed fiscal months.”*" -->

**The site-by-site table.** Below the cards, a table breaks the same numbers out per site — columns Location, Revenue, Expenses, and Net Income (Revenue minus Expenses) for each active site, with a district total row at the bottom carrying your district name. <!-- Source: NXT-68659:AC "Site-by-site performance table shows Revenue, Expenses, and Net Income (Revenue – Expenses) for each active site, plus a district total row at the bottom." --> <!-- Source: NXT-68659:AC "Columns: Location, Revenue, Expenses, Net Income." --> <!-- Source: NXT-68659:AC "For the district-level entry, use the district name." --> It uses the **same period** you picked and **posted GL transactions only**, <!-- Source: NXT-68659:AC "Table uses only posted GL transactions and the same selected period as the dashboard." --> sorts by **Net Income, highest first** (Location name breaks ties), <!-- Source: NXT-68659:AC "Default sort is Net Income descending; secondary sort by Location name." --> and **lists active sites only.** <!-- Source: NXT-68659:AC "Only show *active* sites; do not display inactive sites." -->

> ⚠️ **A dash in Net Income means data is missing, not break-even.** Net Income only fills in when **both** Revenue and Expense totals exist for that row; otherwise the cell shows **–**. <!-- Source: NXT-68659:AC "Net Income only appears when both Revenue and Expense totals are present; otherwise show “–”." --> The tooltip explains: *"Net Income is unavailable because Revenue and/or Expenses are missing for this period."* <!-- Source: NXT-68659:AC "Tooltip: *“Net Income is unavailable because Revenue and/or Expenses are missing for this period.”*" --> Don't read a dash as a zero.

**What this is *not*.** It's not a report you download — the dashboard is a live on-screen read; the downloadable board/auditor files live in Job 9. And it includes nothing beyond what's posted to the GL. The dashboard's truth is the posted ledger.

> 🔧 **Implementer:** The dashboard's "Current" windows are only as right as the customer's Fiscal Year Settings — that's literally where the ranges come from. <!-- Source: NXT-68659:AC "Current Fiscal Year date range comes from Fiscal Year Settings (start and end dates)." --> Walk Job 4 *before* you point a director at this screen; a fiscal year off by a month makes every "Current Quarter" number look wrong. (A refinement that adds site-name sorting to the table is on the way — see the appendix.)

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

> 🔧 **Implementer:** The two prep questions ("which programs do you run?" and "how many GL accounts for meal sales?") drive everything. Ask them on a screen share before the customer touches this page so they can use Bulk Actions instead of mapping row by row. *(A separate Valuation Categories mapping — Asset + Expense per inventory category — gates inventory posting when it ships; see the appendix.)*

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

> 🔧 **Implementer:** Ask the customer: "How do you reconcile prepaid balances in your ERP — by school, or one bucket?" That answer determines the setting. The mode can be changed later, and only affects future entries. *(Heads-up: the single prepaid bucket is being split into POS vs. Online liabilities in a coming release — see the appendix.)*

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

> 🔧 **Implementer:** Recommend new districts leave Automatic Entry Adjustments off for their first fiscal year, so they can review what would have changed before opting into automatic adjustments. *(The Periods screen is growing into a per-site close/reopen console — see the appendix.)*

---

# Job 5 — "Get my opening balances in"

**TL;DR:** Pull balances from your ERP as of the day before go-live. Upload. Confirm debits = credits.

**Prerequisite:** Like the GL Accounts Import, the Opening Balance Import has to be registered in Imports & Exports › Imports › Add New first (see Before-You-Touch step 4). If your implementer hasn't done that, the import option won't be available when you click Import.

**Where:** Configuration › Opening Balance Import.

**Required columns:** Account Code, Site Code (if Distributed), Debit Balance, Credit Balance.

**What you need to know:**
- This is your first-FY anchor for the audit trail. (You're not locked out if you get it wrong — re-importing with a replacement warning is on the way; see the appendix.)
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

> **See also:** *"What posting actually puts in your ledger,"* below — it opens the hood on the exact debit/credit lines each kind of posting writes.

---

# What posting actually puts in your ledger

The rest of this guide keeps telling you "posting is automatic." True — but what does it *post*? When a period closes, the system writes balanced double-entry lines for you: a debit, a credit, an amount, a date, and a site. Two of these flows are live today — your meal-sales revenue and your sales-tax liability. (The whole inventory side and reimbursements are on the roadmap — see the appendix.)

### Meal-sales revenue → your ledger, when you close a POS period

🎯 **The job:** you close a POS period and your meal money lands in the general ledger automatically, split correctly between revenue and the prepaid balances customers drew down.

When a POS period is closed for a site, the system posts your meal-sales revenue to the ledger without a manual journal entry. <!-- Source: NXT-66384:AC "*When a POS period is closed:* * Backend accesses the <meal sales revenue source> from the accountability database * Ledger Entries are created in the tables associated with the given district" --> The entry is labeled **Meal Sales Revenue**. <!-- Source: NXT-66384:AC "*Transaction Code:* MEALSLS ** *Transaction Description:* Meal Sales Revenue" -->

What the entry contains:

- **Debit side** — your **Cash in Bank** account *and* the **prepaid balance** account, by site. <!-- Source: NXT-66384:AC "*Accounts Debited:* <Cash In Bank GL Site Sub Account> AND <Prepaid Account GL Site Sub Account>" --> (Why prepaid is debited: when a student spends down money they paid earlier, that prepaid liability goes down — so it sits on the debit side here.)
- **Credit side** — your **meal-sales** and **à la carte sales** revenue accounts, by site. <!-- Source: NXT-66384:AC "*Accounts Credited:* <Meal Sales AND A La Carte Sales GL Site Sub Accounts>" -->
- The meal-sales account follows the **revenue program** the money came from (e.g. the School Breakfast Program); the à la carte account follows the **meal type** (e.g. Breakfast). <!-- Source: NXT-66384:AC "The *meal sales account* must align to the *student revenue source* (e.g., School Breakfast Program), and the *a la carte account* must align to the *student meal type* (e.g., Breakfast)." -->

⚠️ **Watch-outs before this will post:**
- Every meal-sales revenue data point must be mapped to a GL account first (a Job 2 task). <!-- Source: NXT-66384:AC "All Meal Sales Revenue accounts mapped to GL Accounts" -->
- The financial period has to be **open** from the posting date through today. <!-- Source: NXT-66384:AC "Financial periods must be open from the date of posting to the current date." -->
- **Every** POS period inside the financial period's date range has to be **closed**. <!-- Source: NXT-66384:AC "All POS periods that fall in the selected Financial period's date range need to be closed." -->
- The entry posts dated to the **last day of the POS period**, not the day you close it. <!-- Source: NXT-66384:AC "The last day of the POS Period is used as the Posting date." -->

> 🔧 **Implementer note — this is why one GL account can show two different totals on your P&L.** Each debit/credit line is tagged with the exact data point it came from, so the P&L can total *by data point* even when several data points map to the same GL account. <!-- Source: NXT-66384:AC "each debit/credit line must be attributed to the originating data point / data source (e.g., the specific meal sales revenue data point or reimbursement data point) so the Profit & Loss report can calculate totals by data point even when one GL account is mapped to multiple data points." --> There may be several accounts on each side; the system validates that total debits equal total credits before it posts. <!-- Source: NXT-66384:AC "Note that there may be multiple accounts involved on either side of the transaction. Validate that debit and credit totals are equal." -->

### Sales tax → posted as a liability you owe, not as revenue

🎯 **The job:** the tax you collected at the register is tracked as money you owe the state, ready to remit — and it never inflates your revenue.

When a POS period closes for a site, the system creates **exactly one** sales-tax entry for that site and period, with **two lines only**: <!-- Source: NXT-70304:AC "*Then* the system creates *exactly one* TAXCLCTD journal entry for that *site + POS period*." -->

1. **Debit: Cash in Bank** — the net sales tax. <!-- Source: NXT-70304:AC "*Debit:* Cash in Bank = Net Sales Tax" -->
2. **Credit: Sales Tax Owed (a liability)** — the net sales tax. <!-- Source: NXT-70304:AC "*Credit:* Sales Tax Owed (Liability) = Net Sales Tax" -->

The amount is **net** tax — tax collected minus tax reversed (voids and returns) in that same POS period — <!-- Source: NXT-70304:AC "Posted Amount = *Tax Collected – Tax Reversed* (same POS period)." --> dated the **last day of the POS period.** <!-- Source: NXT-70304:AC "Posting Date = *last day of the POS period*." --> On the POS Period Close job it shows up as **"Sales Tax Collected."** <!-- Source: NXT-70304:AC "Appears as 'Sales Tax Collected' in POS Period Close job corresponding to the period." -->

> ⚠️ **Watch-out — an inactive account silently skips the tax posting.** If either the Cash in Bank or the Sales Tax Owed account is inactive when posting runs, the system **skips** the sales-tax entry. <!-- Source: NXT-70304:AC "*Given* Cash in Bank or Sales Tax Owed is inactive *When* posting runs *Then* skip TAXCLCTD" --> Keep both active or your tax liability won't post. And note: meal-sales revenue is the **tax-exclusive** amount — the gross figure that includes tax must never be used for revenue posting. <!-- Source: NXT-70304:desc "*Meal Sales Revenue* = the tax-exclusive revenue amount (does *not* include sales tax)." --> <!-- Source: NXT-70304:desc "*Total / Gross Amount* = Meal Sales Revenue *plus* Sales Tax (may exist in POS, but must not be used for revenue posting)." --> That separation keeps your reported revenue honest.

---

# Job 9 — "Pull a report for my board, my auditor, or to know where I stand"

**Where:** Reports landing page — three tiles.

| Report | Use when… | Output shape |
|---|---|---|
| **General Ledger** | Auditor wants account-level detail | One Excel sheet per selected account; multi-select with Select All for all active mapped accounts |
| **Journal** | You need a date-range view of all activity | One workbook, one sheet covering all selected locations |
| **Revenue & Expenditure (P&L)** | Board meeting, monthly review, fiscal close | One worksheet per site; a revenue table, an expense table, Net Income, and a Cost of Food Used breakdown |

Generation is async. You click Generate, the file builds in the background, you get notified, and you download from the Document Center. No spinning loaders.

> ⚠️ **One reporting truth in 2.0:** Reports pull only from posted ledger entries. There's no "live recalculate" mode. If a number isn't in the ledger, it isn't in the report. This is by design — your reports always match your ledger, which means your reports always match what got exported to your ERP. *(Two more report tiles — Trial Balance and Balance Sheet — are coming; see the appendix.)*

## Reading the P&L

The P&L is officially the **Revenue & Expenditure (P&L) Report**. <!-- Source: NXT-68643:AC "Page title: *“Revenue and Expenditure (P&L) Report”*" --> You generate it like the other two: pick parameters, click Generate, download from the Document Center.

**Parameters.** Choose a fiscal year, a reporting period, and one or more sites; each selected site gets its own worksheet in one Excel file, and one Generate produces one workbook. <!-- Source: NXT-68643:AC "Choose a fiscal year, reporting period, and sites. When multiple sites are selected, each site gets its own P&L worksheet in the Excel file." --> <!-- Source: NXT-68643:AC "*One workbook per Generate action.*" --> The reporting period can be a single month, a quarter, a fiscal year-to-date, or a custom date range. <!-- Source: NXT-68643:AC "Options:\n*** {{Single month}}\n*** {{Quarter}}\n*** {{Fiscal YTD}}\n*** {{Custom date range}}" --> Select **All** sites and the report consolidates every site into one. <!-- Source: NXT-68643:AC "If ‘All’ is selected, consolidate data from all sites within the district in one report." --> Any line with no data shows a dash, with zero used for the math. <!-- Source: NXT-68643:AC "If a line in the report doesn’t have any data, indicate so using a ‘-‘ and use zero in the backend for calculations" -->

**How the columns are computed.** For a revenue row, the current period is credits minus debits in the period; for an expense row, debits minus credits. <!-- Source: NXT-68643:AC "** current period = (sum of credits in period) – (sum of debits in period)" --> <!-- Source: NXT-68643:AC "** current period = (sum of debits in period) – (sum of credits in period)" --> Year-to-date is the running total from the fiscal-year start through the end of the selected period. <!-- Source: NXT-68643:AC "** year-to-date = cumulative (credits – debits) from fiscal year start up to the end date of the selected reporting period" --> % of Revenue and % of Expenses are each the row divided by its table total, shown as `XX.XX%`. <!-- Source: NXT-68643:AC "*if total revenue > 0 → (current period ÷ total revenue) × 100, display as \"XX.XX%\"*" --> Net Income at the bottom is total revenue minus total expenses. <!-- Source: NXT-68770:AC "display net income = total revenue – total expenses and subtotals" -->

> ⚠️ **Custom date range hides the comparison columns.** Pick a custom range and the report intentionally drops every prior-period comparison column — so "where did my % Change column go?" is expected, not a defect. <!-- Source: NXT-68643:AC "*Note: If the user selects a custom date range, do not show any columns involving comparison with prior periods.*" --> A period with no postings exports a "No records were found" line, <!-- Source: NXT-68643:AC "If no records are available, indicate in export that “No records were found”" --> and when total revenue or expenses is zero or negative, the percentage columns are suppressed with a warning banner explaining why. <!-- Source: NXT-68643:AC "if total revenue ≤ 0 AND total expenses ≤ 0 → \"Total revenue and expenses are zero or negative for this period. Percentage calculations have been suppressed.\"" -->

**Cost of Food Used.** The P&L includes a **Cost of Food Used** subsection, grouped by Valuation Category (Food and Non-Food) exactly as defined in the Inventory Usage Report. <!-- Source: NXT-70296:AC "Add a \"Cost of Food Used\" subsection in the P&L." --> <!-- Source: NXT-70296:AC "Group by Valuation Category (Food & Non-Food) as already defined in the Inventory Usage Report." --> It breaks the cost into Beginning Inventory, Purchases, Additions, Net Transfers (transfers in minus transfers out), and Ending Inventory, then derives Cost of Food Used (A + B + C ± D − E). <!-- Source: NXT-70296:AC "* Line A — Beginning Inventory\n* Line B — Purchases\n* Line C — Additions\n* Line D — Net Transfers (Transfers In − Transfers Out)\n* Line E — Ending Inventory\n* Line F — Cost of Food Used ({{A + B + C ± D − E = COFU}})" --> These numbers are pulled **live from the Inventory Usage Report** — the P&L does not recalculate them. <!-- Source: NXT-70296:AC "All Cost of Sales data is fetched live from the Usage Report. The P&L does not independently calculate these values in columns A - D." --> So if Inventory data is stale, P&L Cost of Food Used is stale: close your Inventory period first.

> 🔧 **Implementer note — what populates the two tables today.** In the current build the P&L is driven by **manual journal entries only**, not automated POS/inventory feeds. A revenue row appears for each revenue-type GL account that shows up in at least one manual-entry line dated inside the period; an expense row appears the same way. <!-- Source: NXT-68643:AC "revenue table must include one row for each gl account that meets both of these conditions:\n** account type = revenue\n** account appears in at least one manual entry line (debit or credit) where the posting date is inside the selected reporting period" --> Each row label is the GL account name exactly as stored. <!-- Source: NXT-68643:AC "row label must use the gl account name exactly as stored in the gl accounts table" --> So an empty P&L in early onboarding usually means the manual entries that feed it haven't posted yet — not a bug. (The exact same row and total values feed the Job 0 dashboard, so the two always agree. <!-- Source: NXT-68770:AC "these exact revenue values (each row + totals) must be used by the dashboard" -->) *A much deeper P&L — meal-type revenue detail, a reimbursements section, itemized expenses, meal counts, a standalone COGS report, and a board-ready PDF — is on the roadmap. See the appendix.*

---

# Job 10 — "Figure out why a posting failed (or didn't run)"

**TL;DR:** One page. Activity › Posting Activity Log.

**Where:** Financials › Activity › Posting Activity Log.

**What you'll see:**
- Summary cards (last 30 days): Total Jobs, Completed, Failed, Running. <!-- Source: NXT-69493:AC "*Summary cards*: Four cards at top — Total Jobs (30 Days), Completed (green), Failed (red), Running (orange)." -->
- A table of every posting job: Job Name, Type (POS / Inventory / Claim), Status, Last Run, Triggered By.
- Expand a successful job → entries created, total amount, duration, breakdown by entry type, and a "View in Journal →" link that pre-filters the journal to that job.
- Expand a failed job → red warning, error reason ("Missing GL account mapping for site: Washington Elementary," etc.).

In the first 2.0 build this page is a **read-only monitor** — postings are triggered when an upstream period closes, not from here, and you watch them land. <!-- Source: NXT-69493:AC "*Manual trigger*: Out of scope — jobs triggered from Fiscal Periods page, not here." -->

> ⚠️ **Manual posting is returning as an option.** A wave of work brings a **Ready to Post** queue (Review / Post All) and per-site **Post / Repost / Remove** grids back to this page for districts that post by hand. It hasn't shipped — see the appendix (Manual posting queues). The "do nothing, posting is automatic" promise is the *default*, not the only mode.

**The five reasons posting halts globally:**
1. An active data point isn't mapped.
2. An entry references an inactive data point.
3. The financial period covering the source date is closed.
4. The source POS/Inventory period isn't closed yet.
5. A category's base type doesn't match the data points referencing it.

Fix one of those, the job re-runs (or you re-trigger from the source system). The log keeps history.

> ⚠️ **Partial-failure caveat:** If a job posts some entries and then fails, it shows as Failed with no entries listed in the expanded row. Some entries did post — they're in the journal. Filter the journal by date range to find them before re-running, or you'll double-post.

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
- [ ] First report (P&L) generated and reviewed
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
| Approve / Post buttons | Removed from the first 2.0 build — a read-only monitor; posting runs in the background. Per-site **Post / Repost / Remove** and a **Review / Post All** queue are returning as an option for districts that post manually (see the appendix). "Gone" describes the first 2.0 build, not the end state. |
| Refunds Liability + Pay Refunds entries | (gone — single-step refund posting) |

---

# When you're stuck

- **Posting didn't run.** → Posting Activity Log. The error reason is on the row.
- **Posting ran but the numbers look wrong.** → Open the Ledger for the affected account, find the transaction, click through to its line items. Reverse if needed.
- **Report shows a number you don't recognize.** → It came from a posted ledger entry. Find that entry. The chain is always: source event → posted entry → report.
- **The product won't let you do something.** → Almost always a base-type, period-state, or mapping check. The error message will say which.
- **The "Import" button doesn't show the import type you expected.** → That import type hasn't been registered yet in Imports & Exports (see Before-You-Touch step 4). Ping your implementer.
- **You see Post buttons or a "Ready to Post" queue the guide says are gone.** → You're on a newer build. Manual posting is returning as an option (see the appendix). The "posting is automatic" story is the default, not the only mode.
- **You can't tell if a behavior is intentional.** → Check with your implementer. The product specs are the source of truth for fine-grained behavior.

---

# Appendix — What's Coming Next (not yet shipped)

> Everything in this appendix is **specified but not yet shipped** — agreed, in-development behavior captured from the Financials backlog, not a screen you can open today. It's grouped by theme and names the relevant ticket key(s) so you can track them. Treat it as a roadmap teaser; don't demo any of it as working or promise a customer a column, button, or screen here as shipped. The ticket keys are pointers, not instructions.

### Manual posting queues — Post/Repost controls return to the Posting Activity Log
The "do nothing, posting is automatic" promise is being qualified. A **Ready to Post** queue (Review / Post All) will let you review and post closed periods without leaving the Activity Log (**NXT-70065**). Two per-site grids — one POS, one Inventory — will add a **Status** column (Not Ready / Ready to Post / Posted / Error) and **Post / View / Repost / Remove** actions (**NXT-65487**, **NXT-66123**). The four summary cards (Total / Completed / Failed / Running) get replaced by three "what matters now" cards — posting progress, needs attention, dollars posted (**NXT-70066**) — with failed jobs pinned to the top of the table (**NXT-70067**) and richer completed-job detail plus CSV/PDF/ERP export (**NXT-70068**). A **"You're posting manually" nudge banner** appears when automatic posting is off (**NXT-70069**). Login summaries, a yellow "missing GL mappings" banner, and a new **Requires Review** status round it out (**NXT-69972**, **NXT-70866**); when you fix a missing mapping in Account Mapping, failed jobs **rerun themselves** — no manual retry (**NXT-70111**). *Not yet shipped.*

### Roles & permissions — three access tiers (Job 11)
Three tiers are specified for the Financial Oversight module: **full-access admins** (Director / Central Office / SchoolCafé Administrator, identical permissions — **NXT-66928**); a **Finance Coordinator** who configures everything but is fenced out of deletes, report export, and most period actions (**NXT-66927**); and a **read-only Cafeteria Manager** who can view the dashboard, configuration, manual entries, and reports but reaches nothing for posting, void/reverse, ERP export, or periods (**NXT-66929**). Selecting a role pre-sets its permission boxes. Open items the AC doesn't resolve: where the roles screen lives, the canonical role-picker labels, and the exact period actions a Finance Coordinator can perform. *Not yet shipped.*

### Prepaid-liability split — POS vs. Online
The single "Prepaid Account" data point is being retired in favor of **two source-split liabilities — POS Prepaid and Online Prepaid** — split by enrollment site, with period-end reclassification (**NXT-70909**, **NXT-70305**). A related change splits sales-tax handling (revenue vs. a Sales Tax Owed liability) and adds Deposit Variances posting (**NXT-69981**). This is a Job 2 / Job 3 mapping decision when it lands — getting it wrong mis-maps real money. Confirm the exact data-point labels with the SME before mapping; don't assume "POS Prepaid Liability" is the on-screen string. *Not yet shipped.*

### P&L detail layer — the deep version of Job 9
Today's P&L ships as a shell (revenue table, expense table, Cost of Food Used). The detail layer adds: **revenue broken out by program and meal type** with cost-per-meal and prior-period comparison, drill-down to site (**NXT-65475**, refined by **NXT-69386**); a **Government Reimbursements** section that recognizes revenue *when meals are served* (accrual), not when the check clears (**NXT-65480**); an **itemized Expenses** section with cost-per-meal and categories (**NXT-65483**); a **Meal Counts** section matching the Meal Count Report (**NXT-65486**); a **standalone Cost of Goods Sold** report that also feeds the P&L's Cost of Sales line (**NXT-65481**); the backend rebuild underneath all of it (**NXT-68770**, **NXT-68719**); and a separate **board-ready promotional PDF** with executive summary, budget-vs-actual, compliance checks, and KPI tables, carrying a "not a substitute for audited financials" disclosure (**NXT-70682**). One open conflict to watch: the shipped Cost of Food Used fetches live from the Inventory Usage Report, while a Phase-2 rebuild derives it from manual usage entries until Item Management integration lands (**NXT-68719**) — confirm which a given release uses. *Not yet shipped.*

### Trial Balance & Balance Sheet reports — the 4th and 5th tiles
The Reports page lists three tiles today. Two more are specified: a **Trial Balance** report with Oracle-aligned columns (**NXT-71184**) and a **Balance Sheet** (Assets / Liabilities / Equity + Net Income, per-site worksheets) (**NXT-71182**). *Not yet shipped.*

### Navigation & licensing — finding and turning on Financials
The module is specified to live as **"Financial Oversight"** in the left sidebar (Front Office group, breadcrumbs, license-gated) (**NXT-66966**), enabled via a **License Management** toggle tied to the district's license type (**NXT-66965**), with a defined module architecture naming Settings / Balance Sheet / Export to ERP / Void-Reverse (**NXT-66930**). This pairs with the Week-0 implementer setup. *Not yet shipped.*

### Posting-engine entries — the inventory side and reimbursements
Beyond the two live flows (meal sales, sales tax), the rest of what posting will write is specified but not built. Inventory close will post **one balanced entry per entry type, per Valuation Category, per site, per period** — purchases, withdrawals/usage, add-to-inventory, and transfers — all dated the period's last day, with one missing category mapping blocking the whole site-period (**NXT-70295**); a finer purchase grain by **Valuation Category × Vendor** follows (**NXT-70620**). This is gated by a **Valuation Categories** mapping page where each category needs **both** an Asset and an Expense account before it can post, locked once it has posted activity (**NXT-65482** — a Job 2 prerequisite). **Reimbursement Claim and Reimbursement Received** entries (receivable when claimed, cash when paid) are specified by site (**NXT-66385**), along with commodity/USDA usage, waste, site↔warehouse transfers, and warehouse fees (**NXT-66386**, **NXT-66389**, **NXT-66387**, **NXT-66388**). A central posting-engine stored procedure resolves system-account codes to each district's GL accounts and keeps every entry balanced (**NXT-65485**). Note: some of these inventory stories describe Approve / Post / Reapprove controls, which is part of the same manual-posting wave above. *Not yet shipped.*
