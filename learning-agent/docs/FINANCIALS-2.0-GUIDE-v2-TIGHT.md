# Financials 2.0 · Onboarding Guide

### Onboarding, Without the Yawn

*A jobs-to-be-done guide for the district finance and child-nutrition staff bringing Financials 2.0 online — and for the Cybersoft implementation staff walking them through it.*

**12 Jobs to be Done · 90-Day Cheat Sheet**

SchoolCafé · Cybersoft Implementation Team · June 2026 Edition

---

### Who this is for

District finance and child-nutrition staff getting started in Financials 2.0 (CN Director, Finance Manager / Director, Business Administrator, accountants who'll touch the ledger). Also for: Cybersoft implementation staff onboarding a district. Look for the 🔧 callouts — those are yours.

One thing to remember before you start: **Financials is a downstream module.** It reads what POS and Inventory hand it. It never invents source data, it never modifies it, and it can't post until upstream periods are closed.

### How to read this guide

It's organized by jobs you're trying to get done — not by menus. Each section is short on purpose. Skim the TL;DRs, drop into the section that matches what you're doing today, and come back when the next one becomes your problem.

---

### What actually changed from PrimeroEdge (read this first — 90 seconds)

| You used to… | Now you… | Why it matters |
|---|---|---|
| Click **Approve** then **Post** on three separate pages every period | Choose your model — posting fires automatically when an upstream period closes, or use the **Review / Post All** queue and per-site **Post / Repost / Remove** grids to post by hand | You decide whether "set and forget" or "eyes on every post" fits your workflow |
| Have your CoA import rejected because one account code was off | Get a non-blocking import. Bad codes flag a warning; the rest land cleanly | Fix issues iteratively instead of being stuck in a reject-fix-reupload loop. |
| Map ~248 system accounts on the revenue side, even programs you don't run | Map ~72 data points, deactivate what you don't use, use Smart Mapping suggestions, then bulk-map the rest by section | Phase 1 of mapping is deletion, not data entry. |
| Manually do a "Pay Refunds" entry to clear the refunds-liability bucket | Get one balanced entry, no liability parking | Fewer accounts to manage. No accidentally orphaned liabilities. |
| Get a "dirty" flag on the financial period whenever POS reopened, even if nothing changed | See exactly what changed when source data is re-closed; auto-adjust if you opt in | No more pointless reposting. |
| Run reports against live data that drifted from what was posted | Generate reports from posted ledger entries only — async, downloaded from Document Center | The numbers in your report match the numbers in your ledger. Always. |
| Have a flat list of revenue accounts to map | Map by eligibility × program with bulk actions and a Program filter | Map all NSLP revenue in one click. |
| Create a separate GL Entry Type for every audit adjustment shape | Use one Template Entry that allows the same account on both debit and credit sides | Auditors can do anything they need without a support ticket. |
| Log in and hunt for "how is the district doing?" | Land on a **Financial Dashboard** — Net Income, Revenue, Expenses, a trend arrow, and a site-by-site table | One screen answers "where do we stand?" before you touch setup. |

---

### Before you touch the product

You can't shortcut these. Lock them down before login.

1. **Find the module.** Open **Financial Oversight** from the left sidebar (Front Office group). If it isn't there, your Cybersoft implementation team enables it via License Management — it's tied to the district's license type and doesn't appear until licensed.
2. **Account code structure** — How long are your segments? What does each represent? If your state publishes a standard (Texas FASRG, etc.), have it open. If you have a custom structure, get the segment definitions in writing from your ERP team.
3. **Your chart of accounts, exported from your ERP** (Oracle, Tyler Munis, etc.) — You'll fill the GL Accounts Import template with this. The template lives at Configuration › General Ledger Accounts › Import.
4. **Two short answers** — Have these on hand. They'll save hours later:
   - Which meal programs do you actually run? (NSLP, SBP, Special Milk, CACFP, SFSP, etc.) — You'll deactivate everything else.
   - How many distinct GL accounts do you post meal sales revenue to? — For most districts, the answer is "one or two." That answer drives whether mapping takes 5 minutes or 5 hours.
5. **The imports have to be turned on first.** Before you can run the GL Accounts Import (Job 1), the Opening Balance Import (Job 5), or the payroll journal-entry import, each one has to be registered as an import type in the platform's Imports & Exports area. Until that registration happens, the import type you expect won't appear on the picklist when you click the Import button.

Where the registration happens: **Imports & Exports › Imports tab › Add New.** For each import type, the implementation team:
- Adds the import to the picklist of import types
- Sets the accepted file format (`.xlsx` / `.xls` / `.csv`)
- Defines required columns and column mappings
- Confirms the help-tooltip text the district will see at upload time

After registration, you see "GL Accounts Import," "Opening Balance Import," and the payroll journal-entry import as available options when you hit the Import button in Configuration.

> 🔧 **Implementer:** Send the GL Accounts template to the district at kickoff. Their ERP team typically needs lead time to pull a clean chart of accounts. Also confirm the site-code segment length matches the actual site codes on the Sites page — the system pads with leading zeros if a site code is shorter than the segment length.

> 🔧 **Implementer:** Register all three import types during environment setup, even the ones the district won't use until later. Opening Balance is needed in week 3; payroll often comes after go-live. Treat import-type registration as part of "stand up the environment," not "start onboarding the district."

---

## Job 0 — "See where my district stands the moment I log in" (Financial Dashboard)

**TL;DR:** The Financial Dashboard is your single-glance scoreboard — Net Income, Total Revenue, and Total Expenses for a period you pick at the top right, a trend arrow that tells you if the district is improving month over month, and a table breaking the numbers down site by site.

**When this is your job:** Login, day one and every day after. For a CN Director or Business Administrator this is usually the first screen you read — before you drop into the setup Jobs below.

**The three KPI cards.** The dashboard leads with Net Income, Total Revenue, and Total Expenses for whatever period you've selected. <!-- Source: NXT-68659:AC "Changing the period recalculates Net Income, Total Revenue, and Total Expenses and updates the card label (e.g., \"Net Income (June 2025)\")." --> Net Income is the headline number, shown big with dollar formatting — it's simply Total Revenue minus Total Expenses, and if the district is in the red it shows with a minus sign (e.g. `-$125,000`). <!-- Source: NXT-68659:AC "Net Income = Total Revenue – Total Expenses; if negative, show with a minus sign (e.g., -$125,000)." --> Total Revenue and Total Expenses sit underneath, each rounded to the nearest dollar. <!-- Source: NXT-68659:AC "Total Revenue and Total Expenses are shown below as smaller values, rounded to the nearest dollar." --> The card title carries the period in parentheses so you always know what window you're reading — e.g. "Net Income (June 2025)." <!-- Source: NXT-68659:AC "Changing the period recalculates Net Income, Total Revenue, and Total Expenses and updates the card label (e.g., \"Net Income (June 2025)\")." -->

The numbers are built from **posted General Ledger transactions only** — the same posted-ledger truth the rest of 2.0 runs on. <!-- Source: NXT-68659:AC "Data source is posted financial transactions from the General Ledger." --> Every active site is rolled in, <!-- Source: NXT-68659:AC "Calculations include all active sites." --> and only accounts whose base type is Revenue or Expense count toward the totals. <!-- Source: NXT-68659:AC "Only GL accounts with base type Revenue or Expense are included." -->

**The period selector (top right).** Pick your reporting window from the **"Period:"** dropdown in the top-right corner. <!-- Source: NXT-68659:AC "Period selector is a standard dropdown labeled "Period:" in the top right of the dashboard." --> Options are Current Month, Current Quarter, Current Fiscal Year, and a Custom Range. <!-- Source: NXT-68659:AC "Period options: Current Month (MMM YYYY), Current Quarter (Q# YYYY), Current Fiscal Year (FY YYYY), Custom Range." --> On load it defaults to **Current Fiscal Year** as of today, so you open to a year-to-date picture without touching anything. <!-- Source: NXT-68659:AC "Default period on dashboard load: Current Fiscal Year (FY ) as of today." --> The Current Fiscal Year and Current Quarter ranges come straight from your Fiscal Year Settings (the dates you configure in Job 4) and use *fiscal* quarters, not calendar quarters. <!-- Source: NXT-68659:AC "Current Fiscal Year date range comes from Fiscal Year Settings (start and end dates)." --> <!-- Source: NXT-68659:AC "Current Quarter uses fiscal quarters (Q1–Q4) defined by Fiscal Year Settings." --> The "Current …" ranges are system-defined — you can't hand-edit them; pick Custom Range when you need your own dates. <!-- Source: NXT-68659:AC "Period date ranges for the quarter, year-to-date and current month are system-defined and not user-editable." -->

> ⚠️ **The dashboard can move during an open period.** The totals include every posted transaction whose posting date falls in your window — **even if that fiscal period is still open.** <!-- Source: NXT-68659:AC "Include all posted transactions whose transaction/posting date falls within the selected period, even if the fiscal period is still open." --> A blank side reads as **0**, not an error: if there are no posted Revenue or Expense transactions, that column shows 0 and Net Income treats it as zero. <!-- Source: NXT-68659:AC "If there are no posted Revenue or Expense transactions in the selected period, show \"0\" for the respective column and calculate net income assuming it's value as zero." -->

**The trend arrow (am I improving?).** Next to Net Income, a small arrow compares the **latest completed fiscal month** against the month before it — up if higher, down if lower, **no arrow if equal.** <!-- Source: NXT-68659:AC "Trend arrow compares Net Income for the latest completed fiscal month vs the immediately previous fiscal month." --> <!-- Source: NXT-68659:AC "If latest > previous show ↑; if less show ↓; if equal show no arrow." --> "Completed" means a fiscal month that has fully passed in real time. <!-- Source: NXT-68659:AC "A completed month = a fiscal month that has fully passed in real time." --> Brand-new districts won't see an arrow until two fiscal months are on the books. <!-- Source: NXT-68659:AC "Hide arrow if fewer than two completed fiscal months exist in the current fiscal year." -->

> ⚠️ **The arrow ignores the period dropdown.** Changing the period selector does **not** change what the arrow compares — it always looks at the two most recently completed fiscal months. <!-- Source: NXT-68659:AC "Trend arrow is not affected by the selected reporting period." --> The tooltip says it out loud: *"Trend compares the two most recently completed fiscal months."* <!-- Source: NXT-68659:AC "Tooltip: *"Trend compares the two most recently completed fiscal months."*" -->

**The site-by-site table.** Below the cards, a table breaks the same numbers out per site — columns Location, Revenue, Expenses, and Net Income (Revenue minus Expenses) for each active site, with a district total row at the bottom carrying your district name. <!-- Source: NXT-68659:AC "Site-by-site performance table shows Revenue, Expenses, and Net Income (Revenue – Expenses) for each active site, plus a district total row at the bottom." --> <!-- Source: NXT-68659:AC "Columns: Location, Revenue, Expenses, Net Income." --> <!-- Source: NXT-68659:AC "For the district-level entry, use the district name." --> It uses the **same period** you picked and **posted GL transactions only**, <!-- Source: NXT-68659:AC "Table uses only posted GL transactions and the same selected period as the dashboard." --> sorts by **Net Income, highest first** (Location name breaks ties), <!-- Source: NXT-68659:AC "Default sort is Net Income descending; secondary sort by Location name." --> and **lists active sites only.** <!-- Source: NXT-68659:AC "Only show *active* sites; do not display inactive sites." -->

> ⚠️ **A dash in Net Income means data is missing, not break-even.** Net Income only fills in when **both** Revenue and Expense totals exist for that row; otherwise the cell shows **–**. <!-- Source: NXT-68659:AC "Net Income only appears when both Revenue and Expense totals are present; otherwise show "–"." --> The tooltip explains: *"Net Income is unavailable because Revenue and/or Expenses are missing for this period."* <!-- Source: NXT-68659:AC "Tooltip: *"Net Income is unavailable because Revenue and/or Expenses are missing for this period."*" --> Don't read a dash as a zero.

**What this is *not*.** It's not a report you download — the dashboard is a live on-screen read; the downloadable board/auditor files live in Job 9. And it includes nothing beyond what's posted to the GL. The dashboard's truth is the posted ledger.

> 🔧 **Implementer:** The dashboard's "Current" windows are only as right as the district's Fiscal Year Settings — that's literally where the ranges come from. <!-- Source: NXT-68659:AC "Current Fiscal Year date range comes from Fiscal Year Settings (start and end dates)." --> Walk Job 4 *before* you point a director at this screen; a fiscal year off by a month makes every "Current Quarter" number look wrong.

---

## Job 1 — "Get my chart of accounts into the system"

**TL;DR:** Define the account code structure → import your CoA from the ERP → fix any flagged accounts in place.

**When this is your job:** Day 1. Nothing else works without it.

**Prerequisite:** The GL Accounts Import has to be registered in Imports & Exports first (see Before-You-Touch step 5). If "GL Accounts Import" doesn't show up when you click the Import button, registration hasn't happened yet — flag it to your implementer.

**What it looks like:**

Configuration › General Ledger Accounts has three tabs. Visit them in order:

1. **Account Code Structure.** Pick your state from the dropdown — if your state has a public standard, segments auto-populate. Otherwise build segments manually: name, position, length. Save.
2. **Account Categories.** These are groupings (Salaries & Benefits, Food Costs, etc.) — not GL accounts. They have no codes. They exist to organize your CoA for reports. Optional — if you skip them, the system assigns each imported account to its base-type default (Asset → "Asset" category, etc.).
3. **Individual GL Accounts.** Click Import › GL Accounts Import. Required columns: Account Code, Account Description, Account Category, Account Base Type. Upload.

**What you'll see when it works:** A grid of accounts. Anything that didn't match the structure shows a yellow warning icon — an "X accounts need structure corrections" banner appears at the top with a count. The import still succeeded.

**Watch out:**
- Warnings don't block the import, but they will cause export problems with your ERP later. Resolve before you start mapping.
- Account Code is treated as a string during import to preserve leading zeros and your district's segment formatting exactly. Don't let Excel quietly convert a column to numbers and chop your zeros.
- Once a transaction posts to an account in a category, the category's Base Type is locked forever. You can't accidentally re-classify Cash as Revenue six months in.

**What's renamed from PrimeroEdge:**
- "GL Code Segments" → Account Code Structure
- "Parent Accounts" → Account Categories

#### Reversing a GL Accounts import

<!-- Source: NXT-73326 -->
If you imported the wrong file, use **Reverse Import** from the Import & Export Log (see the Import & Export Log section). Two outcomes depending on activity:

- **Full reversal** (no accounts have any posted transactions): all imported accounts, categories, data-point mappings, and template rules are deleted. If any accounts were mapped to data points, the confirmation dialog lists each one before you confirm.
- **Partial reversal** (some accounts have posted transactions): only accounts with zero transaction activity are deleted. Accounts with posted activity are left in place. A category is deleted only if every account in it was removed; if any account in the category has activity and is kept, the category stays.

After a full or partial reversal, re-import the corrected file. Kept accounts update in place — no duplicate conflict.

> 🔧 **Implementer:** Walk the district through resolving warnings live. Unresolved structure mismatches don't block the import, but they do cause ERP export problems downstream.

---

## Job 2 — "Tell the system where to post each kind of transaction"

**TL;DR:** Subtract programs you don't run → review Smart Mapping suggestions → bulk-map by section → override exceptions → map Valuation Categories.

**The vocabulary you need:**
- **Data points** are the buckets of financial activity Financials collects from across SchoolCafé — meal sales by eligibility, reimbursements by program, inventory transactions, prepaids, etc. They replace "system accounts" in PrimeroEdge. There are ~72 of them, organized by section (Assets, Liabilities, Revenue, Expenses) and grouped within each section.
- **Mapping** = picking which of your imported GL accounts each data point posts to.

**Where:** Configuration › Account Mapping.

#### Phase 1 — Subtract (5 minutes)

1. Filter by Program at the top of the page.
2. For each program your district doesn't run: click Bulk Actions, use the section-level checkbox to grab everything, then Deactivate All in the floating action bar.
3. Confirm. Repeat per program.

The data points for programs you don't run drop out of the active list.

#### Phase 2 — Smart Mapping (check first before mapping by hand)

<!-- Source: NXT-67005 -->
Before you start mapping manually, look for the **Smart Mapping** step in Account Mapping. Smart Mapping presents each required data point as a card with:
- The data point's name and a plain-English description of its purpose
- A **confidence badge** (High / Medium / Low) when the system has a suggestion
- For high-confidence suggestions: "Suggested: [Account Code] — [Account Description]" with **Confirm** and **Choose Different** buttons
- For data points with no confident suggestion: a dropdown filtered to only accounts of the matching base type (Revenue accounts only for Revenue data points, etc.)

When you click **Confirm**, the mapping is saved, the card shows a green checkmark, and the progress counter ticks up. When you click **Choose Different**, a dropdown expands showing all matching-base-type accounts — select one and it saves automatically.

A progress bar ("X of Y required data points mapped") updates in real time so you always know where you stand.

Smart Mapping never writes a mapping without your confirmation. If you prefer to start from scratch, skip to Phase 3.

#### Phase 3 — Bulk-map by section (5 minutes)

1. In Bulk Actions mode, select all groups in Revenue.
2. Click Map All in the floating action bar.
3. Pick the GL account from the typeahead (only Revenue-type accounts appear — base-type filtering is enforced).
4. Apply. Repeat for Assets, Liabilities, Expenses.

> ⚠️ Map All only works inside one section. Cross-section selection grays the button out. This is intentional — base types must match.

#### Phase 4 — Override the few that aren't routine (10 minutes)

Exit Bulk Actions. Expand the relevant group. Use inline edit on the rows that need a different account than your bulk pass set. Common: NSLP reimbursements posting to a different account than other reimbursements; food vs. non-food inventory expenses.

#### Phase 5 — Valuation Categories (required for inventory posting)

<!-- Source: NXT-65482 -->
For inventory posting to work, each **Valuation Category** (e.g. Food, Non-Food) needs both an **Asset account** and an **Expense account** assigned. Configure these in the Valuation Categories tab within Account Mapping. Once a Valuation Category has any posted transaction activity, those account assignments lock — you can't re-map a category that already has a transaction history. Map all Valuation Categories before you close your first Inventory period.

#### Phase 6 — Custom data points (only if you need them)

Pre-installed payroll already splits Salaries / Wages / Benefits / Overtime. If you need more granularity, click Add Data Point and define a journal entry template (debit account + credit account). Validation: debit and credit must balance and at least one side must reference the data point itself.

Click Save Changes. All changes commit at once and show in the configuration history.

> ⚠️ **Critical — every active data point must always be mapped.** The posting engine checks every active mapping before any job runs. One unmapped active data point halts all posting (POS, Inventory, Reimbursements). If you don't need a data point anymore, deactivate it. Don't just remove the mapping.

> 🔧 **Implementer:** The two prep questions ("which programs do you run?" and "how many GL accounts for meal sales?") drive everything. Ask them on a screen share before the district touches this page so they can use Bulk Actions instead of mapping row by row. Make sure Valuation Categories (Phase 5) are mapped before the district closes their first Inventory period — a missing category blocks inventory posting for the whole site-period, not just that category.

---

## Job 3 — "Decide whether to track prepaids/refunds by site or by district"

**TL;DR:** One radio button. Pick the model your ERP already uses. Then confirm how you split POS vs. Online prepaid funds.

**Where:** Configuration › Settings › Posting Settings.

**The Distributed vs. Centralized choice:**
- **Distributed (Enrollment Site)** — default. One entry per site per period for prepaids, bonuses, refunds, and account transfers. Choose this if your ERP reconciles prepaid balances by school.
- **Centralized (District Office)** — one combined entry at the central office level. Choose this if your ERP has a single district prepaid liability account.

**What it affects:** Pre Payment (POS + Online), Bonus, Refunds, Returned Checks, Returned Check Fees, Account Adjustments, Account Transfer In/Out. It does not change how meal sales or reimbursements post — those are always per-site.

**Prepaid sources — POS and Online are tracked separately.** <!-- Source: NXT-70909 --> <!-- Source: NXT-70305 --> The prepaid liability is split into two source types:
- **POS Prepaid** — money loaded at the register
- **Online Prepaid** — money loaded through the parent portal

Each has its own data point in Account Mapping. In Job 2, map the POS Prepaid and Online Prepaid data points to **separate GL accounts** if your ERP tracks them differently; map them to the **same account** if you consolidate. At period end, any prepaid liability balance posts per site (Distributed) or district-wide (Centralized), split by source.

**Watch out:**
- Switching Distributed/Centralized modes shows a confirmation dialog. The change is forward-only — already-posted entries don't restate.
- Centralized uses your Central Office site code from Site Configuration. If none is defined, the system uses all zeros (matching your site-code segment length).

> 🔧 **Implementer:** Two questions to ask on setup: (1) "Do you reconcile prepaid balances in your ERP by school or in one district bucket?" — sets Distributed vs. Centralized. (2) "Do you track funds loaded at the register separately from funds loaded online?" — determines whether to split POS Prepaid and Online Prepaid into different GL accounts or map both to the same one.

---

## Job 4 — "Open my fiscal year so I can actually start"

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

## Job 5 — "Get my opening balances in"

**TL;DR:** Pull balances from your ERP as of the day before go-live. Upload. Confirm debits = credits.

**Prerequisite:** Like the GL Accounts Import, the Opening Balance Import has to be registered in Imports & Exports › Imports › Add New first (see Before-You-Touch step 5). If your implementer hasn't done that, the import option won't be available when you click Import.

**Where:** Configuration › Opening Balance Import.

**Required columns:** Account Code, Site Code (if Distributed), Debit Balance, Credit Balance.

**What you need to know:**
- This is your first-FY anchor for the audit trail. One Opening Balance Import is active per fiscal year — the most recent one.
- Total debits must equal total credits across the file. If they don't, the import rejects and tells you the variance. Validate this before you upload.
- Distributed posting → balances at site level. Centralized → district-level totals are fine.
- Audit trail records who imported, when, and the file contents.

#### Reversing or replacing an opening balance import

<!-- Source: NXT-73303 -->
If you need to correct your opening balances, use **Reverse Import** from the Import & Export Log. Reversal removes all opening balance journal entries and returns the fiscal year to a no-opening-balance state. Three situations block reversal:

- The fiscal year has already been through Year-End Close
- The import was already overwritten by a later restatement
- The relevant period is currently closed — reopen the period first, then reverse

After reversing, upload the corrected file as a fresh import. A comment is required to confirm.

> 🔧 **Implementer:** Build this into the timeline at week one — the district's ERP team needs lead time, and reconciling the file against the imported CoA usually takes at least one round of corrections. Confirm the Opening Balance Import is already registered as an import type in Imports & Exports before the file is ready to upload.

---

## Job 6 — "Make a manual journal entry"

**TL;DR:** Two modes — Template (pre-populated) or Manual (blank). Both must balance. Both must fall in an open period.

**Where:** Journal & Ledger › New Entry.

**Quick anatomy:**
- **Site selection** — district-wide or specific site. Site code embeds into the account code (e.g. `1000-2000-3000-001-50000` for site 001). District-wide → all zeros.
- **Entry Type** — required. <!-- Source: NXT-68708 --> You must select an entry type before saving. Choose **Template** (pre-populated lines from a saved Template Entry) or **Manual** (blank slate).
- **Posted Date** — defaults to today. Cannot exceed today. Cannot fall in a closed period or closed FY (you'll get an inline error).
- **Line items** — Account / Debit / Credit. Real-time balance check at the bottom. Make Entry button only enables when debits = credits and both > 0.

**The Template Entry change worth knowing:** A single template can include the same GL account on both debit and credit sides. PrimeroEdge blocked this, which forced multiple entry types for audit work. In 2.0, one "EOY Audit Adjustments" template covering your entire CoA is enough — the system shows an informational warning if you put the same account on both sides, but it's not a block.

**Renamed from PrimeroEdge:**
- "Ad-Hoc Entries" → Manual Entries
- "GL Entry Types" → Template Entries

#### Bulk payroll entries via import

<!-- Source: NXT-72160 --> <!-- Source: NXT-70777 -->
Districts that process payroll outside of SchoolCafé bring their payroll journal entries in via the **Payroll Import** — registered once in Imports & Exports, then available from the Import button in Journal & Ledger.

**Before you upload,** enter an **Entry Description** (max 50 characters). This text becomes the header description on every journal entry the import creates — it's how you'll identify the batch in the ledger.

**Required columns in the file:**

| Column | Notes |
|---|---|
| GLAccount | Account code per your imported CoA |
| SiteCode | Must match a valid site. Use the Central Office code for district-wide lines. |
| PostedDate | Drives which fiscal period the line lands in. One journal entry is created per unique PostedDate. |
| Debit | Required if Credit is blank. Cannot have both Debit and Credit on the same row. |
| Credit | Required if Debit is blank. |

The file is rejected before any entries are written if total Debits and Credits don't balance to within $0.01 — so validate your file before upload.

Confirm with your implementation team that the Payroll Import type is registered in Imports & Exports before your first payroll close week.

#### Payroll duplicate detection

<!-- Source: NXT-72753 -->
When you upload a payroll file, the system checks whether any rows share a PostedDate with a previous payroll import. Detection is by PostedDate (not just fiscal period) because districts sometimes import multiple payroll files within the same period.

If a matching PostedDate is found, you're shown a prompt:
- **Keep existing** — the new file is discarded; the prior import stays.
- **Overwrite** — the prior import's journal entries are reversed, and the new file is posted in their place.

The audit trail is preserved either way — both the original and the overwrite are recorded.

#### Reversing a payroll import

<!-- Source: NXT-73304 -->
Payroll imports can be reversed from the Import & Export Log. Batches for non-overlapping PostedDate ranges are independently reversible — you can reverse January payroll without touching February's. Reversal is blocked if:

- The fiscal year has been through Year-End Close
- The batch was already overwritten by a later import (via duplicate detection)

After reversing, the relevant period opens back up. Upload the corrected file as a new import.

---

## Job 7 — "Fix a posting that went out wrong"

**TL;DR:** Click the reverse icon. Type a reason. Done.

**Where:** Journal or Ledger view, on the row of the bad transaction.

**What happens:**
1. Side drawer opens showing the original transaction.
2. You type a reason (required).
3. The system creates a new, balanced reversal entry with debit/credit flipped. The original is tagged REVERSED; the new one is tagged REVERSAL OF #[id]. Both stay visible in the ledger.

**One hard boundary:** <!-- Source: NXT-68294 --> Reversing a reversal is blocked. The system prevents you from reversing a transaction that is already itself a reversal. If you reversed an entry in error, make a new manual entry to correct the balance — don't try to reverse the reversal.

**What auditors will love:** The reason text is preserved. Both transactions remain in place. The pair is linked. There's no quiet "delete" path.

---

## Job 8 — "See what happened — by account or by date"

Two views, one job.

| View | Best for | What it shows |
|---|---|---|
| **Ledger** | "What's the balance of this account as of this date?" | One account, running balance, beginning + ending balance bar fixed at the bottom. |
| **Journal** | "What happened on these days, across these sites?" | All accounts, by date, expandable rows showing line items. |

Both support: location filter, date-range filter, sortable columns, transaction-ID hyperlink to a details drawer, in-place reversal, and async Excel export through the Document Center.

**Note on PrimeroEdge:** Districts moving from PrimeroEdge will remember separate Journal and Ledger pages. In 2.0, both views still exist, but the data model behind them is unified — the same transaction shows up in both, and the line-level details, reversal status, and audit metadata are consistent across views.

**Balance behavior — read this once, never forget it:** Asset and Expense accounts are debit-normal: debits add. Liability, Equity, and Revenue accounts are credit-normal: credits add. The Ledger does this math correctly per account type. A liability with a $500 debit posting will see its balance go down, which is what you want.

> **See also:** *"What posting actually puts in your ledger,"* below — it opens the hood on the exact debit/credit lines each kind of posting writes.

---

## What posting actually puts in your ledger

The rest of this guide keeps telling you "posting is automatic." True — but what does it *post*? When a period closes, the system writes balanced double-entry lines for you: a debit, a credit, an amount, a date, and a site. Four flows post automatically: meal-sales revenue, sales-tax liability, inventory transactions, and reimbursements.

#### Meal-sales revenue → your ledger, when you close a POS period

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

#### Sales tax → posted as a liability you owe, not as revenue

🎯 **The job:** the tax you collected at the register is tracked as money you owe the state, ready to remit — and it never inflates your revenue.

When a POS period closes for a site, the system creates **exactly one** sales-tax entry for that site and period, with **two lines only**: <!-- Source: NXT-70304:AC "*Then* the system creates *exactly one* TAXCLCTD journal entry for that *site + POS period*." -->

1. **Debit: Cash in Bank** — the net sales tax. <!-- Source: NXT-70304:AC "*Debit:* Cash in Bank = Net Sales Tax" -->
2. **Credit: Sales Tax Owed (a liability)** — the net sales tax. <!-- Source: NXT-70304:AC "*Credit:* Sales Tax Owed (Liability) = Net Sales Tax" -->

The amount is **net** tax — tax collected minus tax reversed (voids and returns) in that same POS period — <!-- Source: NXT-70304:AC "Posted Amount = *Tax Collected – Tax Reversed* (same POS period)." --> dated the **last day of the POS period.** <!-- Source: NXT-70304:AC "Posting Date = *last day of the POS period*." --> On the POS Period Close job it shows up as **"Sales Tax Collected."** <!-- Source: NXT-70304:AC "Appears as 'Sales Tax Collected' in POS Period Close job corresponding to the period." -->

> ⚠️ **Watch-out — an inactive account silently skips the tax posting.** If either the Cash in Bank or the Sales Tax Owed account is inactive when posting runs, the system **skips** the sales-tax entry. <!-- Source: NXT-70304:AC "*Given* Cash in Bank or Sales Tax Owed is inactive *When* posting runs *Then* skip TAXCLCTD" --> Keep both active or your tax liability won't post. And note: meal-sales revenue is the **tax-exclusive** amount — the gross figure that includes tax must never be used for revenue posting. <!-- Source: NXT-70304:desc "*Meal Sales Revenue* = the tax-exclusive revenue amount (does *not* include sales tax)." --> <!-- Source: NXT-70304:desc "*Total / Gross Amount* = Meal Sales Revenue *plus* Sales Tax (may exist in POS, but must not be used for revenue posting)." --> That separation keeps your reported revenue honest.

#### Inventory → one entry per category and transaction type, when you close an Inventory period

🎯 **The job:** close an Inventory period and every purchase, withdrawal, and transfer lands in your GL, organized by Valuation Category and site.

<!-- Source: NXT-70295 --> <!-- Source: NXT-70620 --> <!-- Source: NXT-65482 -->
When you close an Inventory period, the system posts **one balanced entry per transaction type, per Valuation Category, per site, per period** — all dated the period's last day. The transaction types covered:

- **Purchases** — broken out by Valuation Category and Vendor.
- **Withdrawals / Usage** — what was consumed in the period.
- **Add-to-Inventory** — manual additions.
- **Transfers** — site-to-site movements, posted at both the sending and receiving site.

Each entry uses the Asset account and Expense account you mapped to that Valuation Category in Job 2 (Phase 5). **A missing mapping on any one Valuation Category blocks posting for the entire site-period** — not just that category. Map all Valuation Categories before you close your first Inventory period.

#### Reimbursements → two entries, timed to when you earn them

🎯 **The job:** government reimbursements appear in your ledger as a receivable when you submit the claim — not when the check arrives — so your revenue matches the period you earned it in.

<!-- Source: NXT-66385 --> <!-- Source: NXT-66386 --> <!-- Source: NXT-66389 -->

**Reimbursement Claim (when you submit):**
- Debit: Reimbursements Receivable (Asset)
- Credit: Government Reimbursements Revenue
- Posted per site, dated the claim submission date.

**Reimbursement Received (when the check clears):**
- Debit: Cash in Bank
- Credit: Reimbursements Receivable
- Closes the receivable and records the actual cash.

**Commodity / USDA entries** (where applicable): USDA commodity value posts as an inventory addition using the commodity's published dollar value — even though no cash changes hands. Warehouse fees post as an expense at the receiving site. Site-to-warehouse and warehouse-to-site transfers post at both ends.

---

## Job 9 — "Pull a report for my board, my auditor, or to know where I stand"

**Where:** Reports landing page — five tiles.

| Report | Use when… | Output shape |
|---|---|---|
| **General Ledger** | Auditor wants account-level detail | One Excel sheet per selected account; multi-select with Select All for all active mapped accounts |
| **Journal** | You need a date-range view of all activity | One workbook, one sheet covering all selected locations |
| **Revenue & Expenditure (P&L)** | Board meeting, monthly review, fiscal close | One worksheet per site; revenue table, expense table, Net Income, Cost of Food Used |
| **Trial Balance** | Period reconciliation, Oracle export alignment | Debit and credit totals per account, Oracle-aligned column layout <!-- Source: NXT-71184 --> |
| **Balance Sheet** | Full financial position at a point in time | Assets / Liabilities / Equity + Net Income, one worksheet per site <!-- Source: NXT-71182 --> |

Generation is async. You click Generate, the file builds in the background, you get notified, and you download from the Document Center. No spinning loaders.

> ⚠️ **One reporting truth in 2.0:** Reports pull only from posted ledger entries. There's no "live recalculate" mode. If a number isn't in the ledger, it isn't in the report. This is by design — your reports always match your ledger, which means your reports always match what got exported to your ERP.

### Reading the P&L

The P&L is officially the **Revenue & Expenditure (P&L) Report**. <!-- Source: NXT-68643:AC "Page title: *"Revenue and Expenditure (P&L) Report"*" --> You generate it like the other reports: pick parameters, click Generate, download from the Document Center.

**Parameters.** Choose a fiscal year, a reporting period, and one or more sites; each selected site gets its own worksheet in one Excel file, and one Generate produces one workbook. <!-- Source: NXT-68643:AC "Choose a fiscal year, reporting period, and sites. When multiple sites are selected, each site gets its own P&L worksheet in the Excel file." --> <!-- Source: NXT-68643:AC "*One workbook per Generate action.*" --> The reporting period can be a single month, a quarter, a fiscal year-to-date, or a custom date range. <!-- Source: NXT-68643:AC "Options:\n*** {{Single month}}\n*** {{Quarter}}\n*** {{Fiscal YTD}}\n*** {{Custom date range}}" --> Select **All** sites and the report consolidates every site into one. <!-- Source: NXT-68643:AC "If 'All' is selected, consolidate data from all sites within the district in one report." --> Any line with no data shows a dash, with zero used for the math. <!-- Source: NXT-68643:AC "If a line in the report doesn't have any data, indicate so using a '-' and use zero in the backend for calculations" -->

**How the columns are computed.** For a revenue row, the current period is credits minus debits in the period; for an expense row, debits minus credits. <!-- Source: NXT-68643:AC "** current period = (sum of credits in period) – (sum of debits in period)" --> <!-- Source: NXT-68643:AC "** current period = (sum of debits in period) – (sum of credits in period)" --> Year-to-date is the running total from the fiscal-year start through the end of the selected period. <!-- Source: NXT-68643:AC "** year-to-date = cumulative (credits – debits) from fiscal year start up to the end date of the selected reporting period" --> % of Revenue and % of Expenses are each the row divided by its table total, shown as `XX.XX%`. <!-- Source: NXT-68643:AC "*if total revenue > 0 → (current period ÷ total revenue) × 100, display as \"XX.XX%\"*" --> Net Income at the bottom is total revenue minus total expenses. <!-- Source: NXT-68770:AC "display net income = total revenue – total expenses and subtotals" -->

> ⚠️ **Custom date range hides the comparison columns.** Pick a custom range and the report intentionally drops every prior-period comparison column — so "where did my % Change column go?" is expected, not a defect. <!-- Source: NXT-68643:AC "*Note: If the user selects a custom date range, do not show any columns involving comparison with prior periods.*" --> A period with no postings exports a "No records were found" line, <!-- Source: NXT-68643:AC "If no records are available, indicate in export that "No records were found"" --> and when total revenue or expenses is zero or negative, the percentage columns are suppressed with a warning banner explaining why. <!-- Source: NXT-68643:AC "if total revenue ≤ 0 AND total expenses ≤ 0 → \"Total revenue and expenses are zero or negative for this period. Percentage calculations have been suppressed.\"" -->

**Revenue detail — broken out by program and meal type.** <!-- Source: NXT-65475 --> <!-- Source: NXT-69386 --> The revenue table shows each revenue data point as its own row — NSLP breakfast, SBP lunch, à la carte, etc. — with cost-per-meal alongside the dollar totals. You can drill into any site from the district-level view to see that site's program-level breakdown.

**Government Reimbursements section.** <!-- Source: NXT-65480 --> Reimbursements appear in their own section, recognized when meals are served — not when the check clears. This means the revenue aligns with the period it was earned in, which is how most districts present reimbursements in board reports.

**Itemized Expenses section.** <!-- Source: NXT-65483 --> The expense table shows each expense data point as its own row, with cost-per-meal alongside the dollar total and grouped by the Account Category you set up in Job 1.

**Meal Counts section.** <!-- Source: NXT-65486 --> The P&L includes a Meal Counts section that matches the Meal Count Report — counts by program and meal type for the selected period and sites.

**Cost of Food Used.** The P&L includes a **Cost of Food Used** subsection, grouped by Valuation Category (Food and Non-Food) exactly as defined in the Inventory Usage Report. <!-- Source: NXT-70296:AC "Add a \"Cost of Food Used\" subsection in the P&L." --> <!-- Source: NXT-70296:AC "Group by Valuation Category (Food & Non-Food) as already defined in the Inventory Usage Report." --> <!-- Source: NXT-65481 --> It breaks the cost into Beginning Inventory, Purchases, Additions, Net Transfers (transfers in minus transfers out), and Ending Inventory, then derives Cost of Food Used (A + B + C ± D − E). <!-- Source: NXT-70296:AC "* Line A — Beginning Inventory\n* Line B — Purchases\n* Line C — Additions\n* Line D — Net Transfers (Transfers In − Transfers Out)\n* Line E — Ending Inventory\n* Line F — Cost of Food Used ({{A + B + C ± D − E = COFU}})" --> These numbers are pulled **live from the Inventory Usage Report** — the P&L does not recalculate them. <!-- Source: NXT-70296:AC "All Cost of Sales data is fetched live from the Usage Report. The P&L does not independently calculate these values in columns A - D." --> Close your Inventory period before generating the P&L if you want current Cost of Food Used numbers.

**Board-ready PDF.** <!-- Source: NXT-70682 --> The P&L is also available as a formatted board PDF with an executive summary, budget-vs-actual table, compliance checklist, and key performance tables. The PDF carries the disclosure: *"This report is not a substitute for audited financial statements."* Generate it from the Reports landing page — it's a separate output format from the Excel workbook.

> 🔧 **Implementer note — what populates the P&L.** The P&L is driven by posted ledger entries. A revenue row appears for each revenue-type GL account that shows up in at least one entry line dated inside the period; an expense row appears the same way. <!-- Source: NXT-68643:AC "revenue table must include one row for each gl account that meets both of these conditions:\n** account type = revenue\n** account appears in at least one manual entry line (debit or credit) where the posting date is inside the selected reporting period" --> An empty P&L in early onboarding usually means the entries that feed it haven't posted yet — not a bug. The exact same row and total values feed the Job 0 dashboard, so the two always agree. <!-- Source: NXT-68770:AC "these exact revenue values (each row + totals) must be used by the dashboard" -->

---

## Job 10 — "Monitor and manage postings"

**TL;DR:** One page. Activity › Posting Activity Log. Watch automatic postings land — or hold and post by hand when you want control.

**Where:** Financials › Activity › Posting Activity Log.

### The "do nothing" path (automatic posting)

By default, posting fires when an upstream period closes. You don't trigger it — you watch it land. The Posting Activity Log shows:

- **Summary cards** — three cards at the top: <!-- Source: NXT-70066 --> **Posting progress** (what's posted vs. what's queued), **Needs attention** (failed jobs or decisions waiting on you), and **Dollars posted** (total GL value posted in the current period).
- A table of every posting job: Job Name, Type (POS / Inventory / Claim), Status, Last Run, Triggered By. **Failed jobs are pinned to the top** of the table so they're never buried. <!-- Source: NXT-70067 -->
- Expand a successful job → entries created, total amount, duration, breakdown by entry type, CSV/PDF/ERP export options, and a "View in Journal →" link that pre-filters the journal to that job. <!-- Source: NXT-70068 -->
- Expand a failed job → red warning, error reason ("Missing GL account mapping for site: Washington Elementary," etc.).

**Login summary.** <!-- Source: NXT-69972 --> Each time you open Financials, a brief summary shows what's happened since your last login — postings that landed, jobs that failed, and anything that needs attention.

### The "post by hand" path (manual posting)

<!-- Source: NXT-70065 --> <!-- Source: NXT-65487 --> <!-- Source: NXT-66123 -->
When you want to review before posting, switch to manual posting mode. Two grids appear — one for POS periods, one for Inventory periods — showing each period's posting status per site:

| Status | Meaning |
|---|---|
| Not Ready | Upstream period isn't closed yet |
| Ready to Post | Closed and waiting for your action |
| Posted | Done |
| Error | Failed — see the error reason |

On each row, use the **Post / View / Repost / Remove** action buttons. Or, use **Review / Post All** at the top to post everything in the Ready to Post queue at once.

**"You're posting manually" nudge banner.** <!-- Source: NXT-70069 --> When automatic posting is off, a banner appears at the top of the Posting Activity Log as a reminder — so there's no confusion about why the system isn't posting on its own.

### When a mapping is missing

<!-- Source: NXT-70866 --> <!-- Source: NXT-70111 --> If a posting job failed because a GL account mapping is missing, a yellow banner appears with a link straight to the unmapped data point in Account Mapping. Fix the mapping there, and **the affected jobs retry automatically** — no manual re-trigger needed.

### Why posting halts globally

**The five reasons posting stops:**
1. An active data point isn't mapped.
2. An entry references an inactive data point.
3. The financial period covering the source date is closed.
4. The source POS/Inventory period isn't closed yet.
5. A category's base type doesn't match the data points referencing it.

Fix one of those, the job re-runs. The log keeps history.

> ⚠️ **Partial-failure caveat:** If a job posts some entries and then fails, it shows as Failed with no entries listed in the expanded row. Some entries did post — they're in the journal. Filter the journal by date range to find them before re-running, or you'll double-post.

---

## Job 11 — "Manage who can do what" (Roles & Permissions)

**TL;DR:** Three tiers. Assign the right tier. The tier pre-sets permission checkboxes — you can adjust from there.

**Where:** Financial Oversight › Settings › User Roles

<!-- Source: NXT-66927 --> <!-- Source: NXT-66928 --> <!-- Source: NXT-66929 -->

Financials 2.0 has three access tiers for the Financial Oversight module:

| Role | Who it fits | What they can do |
|---|---|---|
| **Full Access Admin** (Director / Central Office / SchoolCafé Administrator) | CN Director, Finance Director, Business Administrator | Everything — all configuration, all entries, all reports, all period and posting actions. These three job titles map to identical permissions. |
| **Finance Coordinator** | Finance staff doing day-to-day bookkeeping | All configuration, all manual entries, all reports — but no deletes, no report export, and no period or posting actions. |
| **Cafeteria Manager** (read-only) | Site managers who need to see numbers but not touch them | View the dashboard, configuration, manual entries, and reports. Cannot post, void/reverse, export to ERP, or take any period action. |

**How to assign:** Select a role from the role picker on the person's account. Selecting a role pre-sets the permission checkboxes for that tier. You can adjust individual permissions within a tier — the role just sets the starting point.

> 🔧 **Implementer:** During onboarding, assign Full Access Admin to the CN Director and Finance Manager first. Finance Coordinator is right for accounting staff who do data entry but shouldn't be able to accidentally close a period or trigger a posting.

---

## Import & Export Log

**Where:** Financials › Configuration › Import & Export Log

<!-- Source: NXT-73286 -->
The Import & Export Log is your single-pane view of everything that has moved in or out of Financials — every import you've run, every report you've downloaded, every export you've generated — without leaving the module.

**What each row shows:**
- Import or export type (GL Accounts Import, Payroll Import, P&L Report, etc.)
- Run status (In Progress / Completed / Failed)
- Row counts, exception counts, and error messages where applicable
- Date, time, and who triggered the action

**Category filter (All / Imports / Exports / Reports):** Use the pill at the top to narrow the grid. Imports and Reports are active today; the Exports category is present and will fill as configured export jobs are added.

**Re-downloading output:** Click the download icon on any completed report row to pull the file again — you don't need to go back to the originating page or regenerate.

**Reverse Import:** For imports that support reversal (GL Accounts, Opening Balance, Payroll), a **Reverse** button appears on the completed row. Each type has its own rules:

| Import type | What reversal does | Blocked by |
|---|---|---|
| **GL Accounts** | Zero-activity accounts deleted. Accounts with posted transactions kept in place. <!-- Source: NXT-73326 --> | Nothing — reverse is always available; outcome depends on activity |
| **Opening Balance** | All OB journal entries removed; FY returns to no-opening-balance state. <!-- Source: NXT-73303 --> | Year-End Close, a later restatement, or a currently-closed period (reopen first) |
| **Payroll** | Entries for that PostedDate batch reversed. Each date-range batch is independently reversible. <!-- Source: NXT-73304 --> | Year-End Close, or if the batch was overwritten by a later import |

A mandatory comment is required to confirm any reversal. On confirm, status moves to Reversal In Progress, then Reversed (or Partially Reversed for GL Accounts with mixed activity). If the reversal fails, a Retry button appears.

**Deep links:** The page header links directly to Import Monitor and Export Monitor in the system administration area for full run logs.

> 🔧 **Implementer:** Finance Coordinators have read-only access to the Import & Export Log. Only Full Access Admins can trigger Reverse Import actions.

---

## The First-90-Days Cheat Sheet

Print this. Tape it to a monitor.

**Week 0 (implementation team setup, before the district logs in)**
- [ ] Financial Oversight license enabled in License Management
- [ ] GL Accounts Import registered in Imports & Exports
- [ ] Opening Balance Import registered in Imports & Exports
- [ ] Payroll journal-entry import registered (if in scope)
- [ ] Site codes confirmed against site-code segment length
- [ ] User roles assigned (Full Access Admin to CN Director + Finance Manager)

**Week 1**
- [ ] Account code structure saved
- [ ] CoA imported (warnings noted, not necessarily fixed yet)
- [ ] Fiscal year + period frequency configured

**Week 2**
- [ ] Structure warnings on CoA resolved
- [ ] Account Mapping: Phases 1–4 done (subtract, Smart Map, bulk-map, overrides)
- [ ] Valuation Categories mapped (Job 2, Phase 5) — required before first Inventory period close
- [ ] POS Prepaid and Online Prepaid data points mapped (same or separate GL accounts per district preference)
- [ ] Posting Settings (Distributed vs. Centralized) chosen

**Week 3**
- [ ] Opening balances imported and validated (debits = credits)
- [ ] One POS or Inventory period closed → test posting reviewed in Posting Activity Log
- [ ] Posting mode confirmed: automatic (default) or manual (Review / Post All queue)

**Weeks 4–8**
- [ ] First real period close walked through with implementation team
- [ ] First report (P&L) generated and reviewed
- [ ] First manual entry made (even if just a $0 dummy to learn the flow)
- [ ] Reversal walkthrough completed
- [ ] Import & Export Log reviewed to confirm all imports are logged correctly

**Weeks 9–12**
- [ ] Automatic Entry Adjustments toggle decision made (most: leave off)
- [ ] First fiscal-year-equivalent rollover dry run scoped, even if not run

> 🔧 **Implementer:** Run a test posting on a single closed period before go-live and review the entries with the district's finance team line by line. Catching mapping or base-type issues here is much cheaper than catching them after live data has been posted.

---

## Glossary — what it used to be called

| PrimeroEdge | Financials 2.0 |
|---|---|
| GL Code Segments | Account Code Structure |
| Parent Accounts | Account Categories |
| System Accounts | Data Points |
| GL Entry Types | Template Entries |
| Ad-Hoc Entries | Manual Entries |
| Approve / Post buttons | The default is automatic posting in the background. For districts that want manual control: use the **Review / Post All** queue and per-site **Post / Repost / Remove** actions in the Posting Activity Log (Job 10). |
| Refunds Liability + Pay Refunds entries | (gone — single-step refund posting) |

---

## When you're stuck

- **Posting didn't run.** → Posting Activity Log. The error reason is on the row. If it's a missing mapping, fix the mapping in Account Mapping and the job retries itself automatically.
- **Posting ran but the numbers look wrong.** → Open the Ledger for the affected account, find the transaction, click through to its line items. Reverse if needed (Job 7).
- **Report shows a number you don't recognize.** → It came from a posted ledger entry. Find that entry. The chain is always: source event → posted entry → report.
- **The product won't let you do something.** → Almost always a base-type, period-state, or mapping check. The error message will say which.
- **The "Import" button doesn't show the import type you expected.** → That import type hasn't been registered yet in Imports & Exports (see Before-You-Touch step 5). Ping your implementation team.
- **You need to undo an import.** → Import & Export Log › find the import row › Reverse. Each import type has its own conditions (see the Import & Export Log section).
- **You can't tell if a behavior is intentional.** → Check with your implementation team.
