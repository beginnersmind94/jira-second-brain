<!--
Grounded guide-update draft for gap cluster C8 (Job 9 — Pull a report).
Source of record: NXT-71184 (Trial Balance, status=Committed → UPCOMING),
                  NXT-71182 (Balance Sheet, status=In Progress → UPCOMING).
RN is empty in this fixture; AC is the highest-trust source, desc is supporting context only.
Every product-behavior sentence carries an inline <!-- Source: NXT-####:AC "verbatim quote" -->.
Both reports are UPCOMING — tagged "(Coming)" per status-honesty rule. Do not present in present tense as shipped.
Backend/accounting jargon is translated in prose; the verbatim AC token stays inside the citation comment.
-->

# Job 9 — Pull a report (refresh): two more tiles are on the way

> **Reconciliation note for the maintainer.** The 90-Day Cheat Sheet tells a new finance lead to generate a **"Trial Balance / P&L"** in weeks 4–8, but today's Reports page documents only three tiles (General Ledger, Journal, Revenue & Expenditure / P&L) and Trial Balance is not one of them. Two backlog stories close that gap by adding a **4th and 5th tile**. Until they ship, the cheat-sheet line is a promise the Reports section doesn't yet keep — so both tiles below are tagged **(Coming)** and written in the future tense. When NXT-71184 and NXT-71182 reach Done Done, drop the "(Coming)" tags, move the prose to present tense, and remove this note.

---

## Where this fits

Legacy → 2.0, same as the rest of Job 9: in the old world you exported a flat dump and rebuilt the statement in a spreadsheet. In 2.0 the Reports landing page is a set of tiles — click a tile, set a few parameters, and the system queues the report and drops the finished file in your **Document Center** when it's ready. <!-- Source: NXT-71184:AC "the tooltip about Document Center notification is present" --> Today there are three tiles. These two stories add Trial Balance and Balance Sheet alongside them, with the tiles **sorted A–Z** so the order on the page will shift once they land. <!-- Source: NXT-71184:AC "tiles are sorted A–Z" -->

---

## (Coming) Trial Balance — "does it all still balance?"

> **Status: UPCOMING (NXT-71184, *Committed*).** Not live yet. Don't tell a customer it's there today.

**TL;DR.** A new Reports tile that lists *every* GL account with its debit and credit balances so you can prove total debits equal total credits for a period — and read the district's financial position by base type. Column layout mirrors Oracle's General Ledger Trial Balance, so it'll feel familiar if you export to Oracle. Pick a fiscal year, a period (or a range), and a site; export to Excel or PDF.

### The tile

When this ships, a **Trial Balance** tile will appear on the Reports landing page with the description *"Verify that total debits equal total credits across all accounts for a selected period."* <!-- Source: NXT-71184:AC "a \"Trial Balance\" tile is displayed with the description \"Verify that total debits equal total credits across all accounts for a selected period.\"" --> Clicking it opens a configuration page titled **"Trial Balance Report."** <!-- Source: NXT-71184:AC "the page title reads \"Trial Balance Report,\"" -->

### Steps (as specified)

1. **Open the Trial Balance tile.** The configuration page loads with its defaults already set: Fiscal Year is the current fiscal year, Period is the current open period, the Period Range toggle is off, and Site is **All**. <!-- Source: NXT-71184:AC "Fiscal Year defaults to the current fiscal year, Period defaults to the current open period, Period Range toggle is off, and Site defaults to All." -->
2. **Choose your scope.** Leave Site on **All** to roll the numbers up across every site — each GL account row will show values summed across all sites, grouped under base-type and account-category headers. <!-- Source: NXT-71184:AC "each GL account row shows values summed across all sites, grouped under base type and account category headers." --> Or pick a single site to scope every row to that site only, with the same structure and hierarchy. <!-- Source: NXT-71184:AC "each GL account row shows values for that site only, with the same report structure and hierarchy." -->
3. **(Optional) Span multiple periods.** The page opens in single-period mode; there's also a period-range option for covering more than one period at once. *(See the watch-out below for exactly which activity lands in which column.)* <!-- Source: NXT-71184:AC "the user enables the Period Range toggle with From Period = October (Period 2) and To Period = December (Period 4)" -->
4. **(Optional) Filter.** You can narrow the report by base type, account category, or a range of account codes; only matching GL accounts show, and the subtotals re-sum to the filtered set. <!-- Source: NXT-71184:AC "only GL accounts matching the filter criteria are displayed, with subtotals reflecting the filtered data." -->
5. **Read it top-to-bottom.** Accounts are grouped by **base type in this order: Assets, Liabilities, Equity, Revenue, Expenditures**, each with a subtotal row, <!-- Source: NXT-71184:AC "GL accounts are grouped under base types in order: Assets, Liabilities, Equity, Revenue, Expenditures, each with a subtotal row." --> and within each base type they're grouped under your **user-defined account categories**, each with its own subtotal. <!-- Source: NXT-71184:AC "they are grouped under the user-defined account categories, each with a subtotal row." -->
6. **Check the proof line.** At the bottom, the **grand total** shows total debits equal total credits — that equality is the whole point of the report. <!-- Source: NXT-71184:AC "When the user views the grand total row, Then total debits equal total credits." -->
7. **Export.** Send it to **Excel** (a flat table of every visible row and column, subtotals included, with no empty or merged cells) <!-- Source: NXT-71184:AC "the export contains all visible rows and columns as a flat table with subtotals and no empty or merged cells." --> or to **PDF**, which captures the report exactly as it's currently displayed. <!-- Source: NXT-71184:AC "the PDF reflects the currently visible state of the report." -->

### Columns you'll see

Each GL account row will carry **Year Beginning Balance (Debit/Credit), Net Beginning Balance, Prior Periods (Debit/Credit), Period Activity (Debit/Credit), Ending Balance (Debit/Credit), and Net Ending Balance.** <!-- Source: NXT-71184:AC "they can see Year Beginning Balance (Debit/Credit), Net Beginning Balance, Prior Periods (Debit/Credit), Period Activity (Debit/Credit), Ending Balance (Debit/Credit), and Net Ending Balance columns." --> The **Net** columns are always Debit minus Credit no matter the base type — so an Asset with a $100,000 beginning debit reads **+100,000**, and a Liability with a $50,000 beginning credit reads **−50,000**; the sign tells you which side the balance sits on. <!-- Source: NXT-71184:AC "the Net Beginning Balance is −50,000. The formula is always Debit minus Credit regardless of base type." -->

> 🔧 **Implementer callout — set up the Opening Balance Import first.**
> Year Beginning Balance comes from the district's opening balance import, not from a guess. If no opening balance import exists for the selected fiscal year, the Year Beginning Balance columns will read **"Not set"** (with a visual indicator) instead of 0.00 for the permanent accounts. <!-- Source: NXT-71184:AC "Year Beginning Balance columns show _\"Not set\"_ rather than 0.00 for permanent accounts." --> That's the system telling you a setup step is missing — not that the balance is zero. Revenue and Expenditure accounts are different: they always show **0.00** at year beginning, with a label noting these accounts reset at fiscal year start. <!-- Source: NXT-71184:AC "Year Beginning Balance columns show 0.00 with a clear label indicating these accounts reset at fiscal year start." -->

> ⚠️ **Watch-out — "Prior Periods" depends on how you scoped the report.**
> In single-period mode, **Prior Periods** holds everything from Period 1 up to the period *before* the one you picked, and **Period Activity** is just the period you picked. Example: with a September-start fiscal year and Period = November, Prior Periods covers September–October and Period Activity is November only. <!-- Source: NXT-71184:AC "Prior Periods columns show total activity from Period 1 (September) through Period 2 (October), and Period Activity shows November only." --> In range mode it's everything *before* your From Period that lands in Prior Periods, and the From–To span that lands in Period Activity — e.g. From = October, To = December puts September in Prior Periods and October–December in Period Activity. <!-- Source: NXT-71184:AC "Prior Periods columns show total activity from Period 1 (September) only, and Period Activity shows October through December." --> And if you start at Period 1, **Prior Periods is 0.00 for every account** — there's nothing before it. <!-- Source: NXT-71184:AC "When the report renders, Then Prior Periods columns show 0.00 for all accounts." -->

> ⚠️ **Watch-out — zero-balance accounts are hidden by default.**
> Accounts with zero beginning balance, zero period activity, and zero ending balance are hidden out of the gate, with an option to show them. <!-- Source: NXT-71184:AC "those GL accounts are hidden by default with an option to show them." --> If an account you expected is missing, that's why — toggle them back on.

> **🪪 Oracle alignment (per the story's Notes).** The column structure and parameters are modeled after Oracle's General Ledger Trial Balance Report to keep things familiar for districts that export to Oracle. <!-- Source: NXT-71184:AC "*Oracle alignment:* The column structure and parameters are modeled after Oracle's General Ledger Trial Balance Report to ensure familiarity for districts exporting to Oracle." -->

---

## (Coming) Balance Sheet — "what's our financial position, on one page?"

> **Status: UPCOMING (NXT-71182, *In Progress*).** Not live yet. Don't tell a customer it's there today.

**TL;DR.** A new Reports tile that produces a formal Assets / Liabilities / Equity statement for a period, with a single **Net Income** line inside Equity standing in for all the revenue and expense activity. No individual GL accounts split into debit/credit columns — it's a clean, net-amount snapshot you can hand to an administrator or auditor. Pick a fiscal year, a reporting period, and one or more sites; multi-site selections give you one worksheet per site.

### The tile

> **Open question — the landing-page tile copy isn't in AC.** NXT-71184's tile list (the only place AC enumerates the Reports tiles verbatim) names General Ledger, Journal, Revenue & Expenditure (P&L), and Trial Balance — it does **not** include a Balance Sheet tile name or description. <!-- Source: NXT-71184:AC "a \"Trial Balance\" tile is displayed with the description \"Verify that total debits equal total credits across all accounts for a selected period.\" and tiles are sorted A–Z." --> NXT-71182's AC only describes navigating *to* the Balance Sheet, not the exact tile label/description on the landing page. <!-- Source: NXT-71182:AC "When they navigate to Balance Sheet, Then the report parameters page is displayed with the title \"Balance Sheet Report\"" --> **Do not invent the tile's display text.** Confirm the exact label and one-line description with the PO before this goes in the customer guide.

### Steps (as specified)

1. **Open the Balance Sheet report.** The parameters page is titled **"Balance Sheet Report,"** with helper text: *"Choose a fiscal year, reporting period, and sites. When multiple sites are selected, each site gets its own Balance Sheet worksheet in the Excel file."* <!-- Source: NXT-71182:AC "the report parameters page is displayed with the title \"Balance Sheet Report\" and helper text \"Choose a fiscal year, reporting period, and sites. When multiple sites are selected, each site gets its own Balance Sheet worksheet in the Excel file.\"" -->
2. **Pick a reporting period.** The Reporting Period dropdown offers four ways to define the date range: **Single month, Quarter, Fiscal YTD, and Custom date range.** <!-- Source: NXT-71182:AC "it displays four options: Single month, Quarter, Fiscal YTD, and Custom date range." -->
3. **Choose your sites (cascading filters).** Both **Site Type** and **Site** default to **All** and accept multiple selections. <!-- Source: NXT-71182:AC "\"All\" is selected by default and the user can select multiple types." --> <!-- Source: NXT-71182:AC "\"All\" is selected by default and the user can select multiple sites." --> Site Type narrows the Site list: pick, say, Elementary + Middle School and the Site dropdown refreshes to just sites in those types, plus the "All" option. <!-- Source: NXT-71182:AC "When the Site dropdown refreshes, Then it shows only sites belonging to the selected types plus the \"All\" option." --> Whatever you pick scopes every number on the report — beginning balance, period activity, ending balance, and Net Income — to ledger entries from the matching sites. <!-- Source: NXT-71182:AC "all values (Beginning Balance, Period Activity, Ending Balance, Net Income) reflect only ledger entries from the matching sites." -->
4. **Generate, then grab it from the Document Center.** This report runs **asynchronously** — when you submit, it's queued for processing and you're notified when the file is ready in the Document Center. <!-- Source: NXT-71182:AC "the report is queued for processing and the user is notified when it is ready in the Document Center." --> The generate/export button carries the tooltip *"You'll be notified once your file is ready and can download it from the Document Center."* <!-- Source: NXT-71182:AC "it reads \"You'll be notified once your file is ready and can download it from the Document Center.\"" -->

### What's on it

The report shows **Assets, Liabilities, and Equity sections in order**, each with expandable account-category groups, category subtotals, and section totals — plus a **Net Income** line inside the Equity section. <!-- Source: NXT-71182:AC "it displays Assets, Liabilities, and Equity sections in order with category groups, category subtotals, section totals, and a Net Income line within Equity." --> Category groups expand to reveal the individual account rows under them. <!-- Source: NXT-71182:AC "When the user expands a category group, Then individual account rows within that category are revealed with the category subtotal row visible." --> Any account without a category lands in an **"Other"** group at the bottom of its section, behaving like any other group. <!-- Source: NXT-71182:AC "the account appears under an \"Other\" group at the bottom of its section with the same expandable and subtotal behavior." --> The balance check it's proving is the **expanded accounting equation: Total Assets = Total Liabilities + Total Equity + Net Income.** <!-- Source: NXT-71182:AC "Then Total Assets = Total Liabilities + Total Equity + Net Income." -->

> 🔧 **Implementer callout — Net Income, not revenue/expense lines.**
> A balance sheet is a snapshot of permanent accounts, so **no individual Revenue or Expenditure account appears as a row** — their combined effect shows up only as the single Net Income line inside Equity. <!-- Source: NXT-71182:AC "no individual Revenue or Expenditure accounts appear as rows; their net effect appears only as the Net Income line within the Equity section." --> If a customer asks "where's my meal-sales revenue on the balance sheet?", that's the answer: it's folded into Net Income, and the P&L is where the line-item detail lives. This is also the cleanest contrast with the Trial Balance tile above — the Trial Balance lists *every* account in debit/credit columns; the Balance Sheet is the net-amount summary.

> ⚠️ **Watch-out — out-of-balance is surfaced, not silent.**
> If Total Assets doesn't equal Total Liabilities and Equity, the report shows a **prominent warning with the out-of-balance amount** rather than quietly rendering. <!-- Source: NXT-71182:AC "a prominent warning is displayed showing the out-of-balance amount." --> Treat that banner as a data problem to chase, not a report bug.

> ⚠️ **Watch-out — multi-site exports split into per-site worksheets/pages.**
> With **"All" or a single site**, the Excel file is one worksheet holding the full balance sheet. <!-- Source: NXT-71182:AC "the Excel file contains one worksheet with the full balance sheet." --> Select **multiple specific sites** and you get **one worksheet per site**, each named for its site and scoped to that site's data. <!-- Source: NXT-71182:AC "the Excel file contains one worksheet per site, each named with the site name, each containing a complete balance sheet scoped to that site's data." --> PDF works the same way — multiple sites produce **one balance sheet per site with a page break between sites.** <!-- Source: NXT-71182:AC "the PDF contains one balance sheet per site with page breaks between sites." --> So "I want every elementary school on its own tab" is a supported export shape, not a manual split.

> **Formatting note.** Balances opposite their normal side (and a negative Net Income) display **in parentheses** — standard financial-statement presentation. <!-- Source: NXT-71182:AC "the value is displayed in parentheses." -->

---

## Reconciling the 90-Day Cheat Sheet

The cheat sheet's "generate Trial Balance / P&L in weeks 4–8" line is **forward-looking** for the Trial Balance half until NXT-71184 ships — the P&L tile already exists, but the Trial Balance tile does not yet. <!-- Source: NXT-71184:AC "a \"Trial Balance\" tile is displayed" --> Two clean options for the maintainer:

- **Keep the cheat-sheet line, add a "(Coming)" qualifier to the Trial Balance half** so a week-4 reader isn't sent hunting for a tile that isn't there yet; or
- **Soften it to "P&L (Trial Balance coming soon)"** until the tile lands, then restore the original wording.

Either way, the fix is a wording change in the cheat sheet plus the two (Coming) tiles above — no new behavior claims beyond what NXT-71184 / NXT-71182 AC supports.

---

### Open questions for the PO / SME (don't ship to customers unresolved)

1. **Balance Sheet landing-page tile copy** — exact tile label and one-line description are not in either ticket's AC (see the tile callout above). Confirm before publishing.
2. **Visibility on the page once both land** — tiles sort A–Z, so the published order will be *Balance Sheet, General Ledger, Journal, Revenue & Expenditure (P&L), Trial Balance*. <!-- Source: NXT-71184:AC "tiles are sorted A–Z" --> Verify that's the intended final order and that the existing three tiles' copy is unchanged.
3. **Go-live wording** — when each story reaches Done Done, flip its "(Coming)" tag and move its prose to present tense; until then, neither may be described as available.
