<!--
Guide-update draft for Financials 2.0 — "Onboarding, Without the Yawn" (April 2026 Edition).
Cluster C3 from FINANCIALS-2.0-COVERAGE-REPORT.md: the Financial Dashboard is shipped (NXT-68659, Done Done)
but documented nowhere. This drafts a NEW Job section in the guide's voice.

Grounding: every product-behavior sentence carries an inline <!-- Source: NXT-####:AC "verbatim quote" --> tracing
to that ticket's Acceptance Criteria. RN is empty in this fixture; AC is the highest-trust source and `desc` is
supporting context only. Backend/system codes would be translated in prose and kept only in citations — this
cluster's AC happens to use plain UI language, so no code translation was needed.

Status honesty:
  - NXT-68659 = Done Done => SHIPPED. The KPI cards, period selector, trend arrow, and the per-site table
    are described in PRESENT TENSE (live behavior).
  - NXT-68660 = Story Refinement/Efforting => UPCOMING. It is a separate refinement of the site table; only the
    refinements unique to it are tagged "(Coming)". Note: in NXT-68660 the Revenue-Analysis and Expense-Analysis
    cards are struck through in the AC (cut from scope), so they are NOT documented here.
-->

# Job 0 — "See where my district stands the moment I log in" (Financial Dashboard)

> **Where this slots in.** This is a new section for the guide. Logically it sits *before* Job 1 as a landing /
> "at-a-glance" job — it's the screen a director reads, not a setup task they perform. It is distinct from Job 9
> (Reports), which produces downloadable board/auditor files. **Open question for SME:** the guide should state the
> exact menu path / screen name for this dashboard. NXT-68659 AC calls it "the dashboard" and "the Financial
> Dashboard" but never states its navigation path, so none is asserted here.

**TL;DR:** The Financial Dashboard is your single-glance scoreboard — Net Income, Total Revenue, and Total Expenses for a period you pick at the top right, a trend arrow that tells you if the district is improving month over month, and a table breaking the numbers down site by site.

**When this is your job:** Login, day one and every day after. For a CN Director or Business Administrator this is usually the first screen you land on — read it before you drop into the setup Jobs below.

**Status:** ✅ **Shipped today.** Everything in this section is live unless explicitly tagged **(Coming)**.

---

## The three KPI cards (the top of the page)

The dashboard leads with Net Income, Total Revenue, and Total Expenses for whatever period you've selected. <!-- Source: NXT-68659:AC "Changing the period recalculates Net Income, Total Revenue, and Total Expenses and updates the card label (e.g., \"Net Income (June 2025)\")." -->

- **Net Income** is the headline number, shown big with dollar formatting and comma separators. <!-- Source: NXT-68659:AC "Main Net Income number is shown in large text with currency formatting and thousands separators." --> It's simply Total Revenue minus Total Expenses, and if the district is in the red it shows with a minus sign (e.g. `-$125,000`). <!-- Source: NXT-68659:AC "Net Income = Total Revenue – Total Expenses; if negative, show with a minus sign (e.g., -$125,000)." -->
- **Total Revenue** and **Total Expenses** sit underneath as smaller numbers, each rounded to the nearest whole dollar. <!-- Source: NXT-68659:AC "Total Revenue and Total Expenses are shown below as smaller values, rounded to the nearest dollar." -->
- The card's title carries the period in parentheses so you always know what window you're reading — e.g. "Net Income (June 2025)." <!-- Source: NXT-68659:AC "Changing the period recalculates Net Income, Total Revenue, and Total Expenses and updates the card label (e.g., \"Net Income (June 2025)\")." -->

**What the numbers are built from:** posted General Ledger transactions only — the same posted-ledger truth the rest of 2.0 runs on. <!-- Source: NXT-68659:AC "Data source is posted financial transactions from the General Ledger." --> Every active site is rolled in, <!-- Source: NXT-68659:AC "Calculations include all active sites." --> and only accounts whose base type is Revenue or Expense count toward the totals. <!-- Source: NXT-68659:AC "Only GL accounts with base type Revenue or Expense are included." -->

> ⚠️ **Empty period reads as zero, not blank.** If there are no posted Revenue or Expense transactions in the period you picked, that side shows **0** and Net Income is calculated treating it as zero — the card won't go blank or error out. <!-- Source: NXT-68659:AC "If there are no posted Revenue or Expense transactions in the selected period, show \"0\" for the respective column and calculate net income assuming it’s value as zero." -->

---

## The period selector (top right)

Pick your reporting window from the **"Period:"** dropdown in the top-right corner of the dashboard. <!-- Source: NXT-68659:AC "Period selector is a standard dropdown labeled “Period:” in the top right of the dashboard." --> Your options are Current Month, Current Quarter, Current Fiscal Year, and a Custom Range. <!-- Source: NXT-68659:AC "Period options: Current Month (MMM YYYY), Current Quarter (Q# YYYY), Current Fiscal Year (FY YYYY), Custom Range." --> When the dashboard loads it defaults to **Current Fiscal Year** as of today, so you open to a year-to-date picture without touching anything. <!-- Source: NXT-68659:AC "Default period on dashboard load: Current Fiscal Year (FY ) as of today." -->

A few things worth knowing about how the windows are defined:

- The **Current Fiscal Year** range comes straight from your Fiscal Year Settings (the start and end dates you configure in Job 4). <!-- Source: NXT-68659:AC "Current Fiscal Year date range comes from Fiscal Year Settings (start and end dates)." --> **Current Month** is the 1st through the last day of this calendar month, within the fiscal year that contains today. <!-- Source: NXT-68659:AC "Current Month = 1st to last day of the current calendar month, within the fiscal year that includes today." -->
- **Current Quarter** uses your *fiscal* quarters (Q1–Q4), not calendar quarters — again defined by Fiscal Year Settings. <!-- Source: NXT-68659:AC "Current Quarter uses fiscal quarters (Q1–Q4) defined by Fiscal Year Settings." --> Every "Current …" option stays inside the active fiscal year. <!-- Source: NXT-68659:AC "All “Current …” options must fall inside the active fiscal year" -->
- The Current Month, Quarter, and year-to-date ranges are **system-defined — you can't hand-edit them**; pick Custom Range when you need your own dates. <!-- Source: NXT-68659:AC "Period date ranges for the quarter, year-to-date and current month are system-defined and not user-editable." -->

> ⚠️ **Open vs. closed periods don't gate the dashboard.** The totals include every posted transaction whose posting date falls in your selected window — **even if that fiscal period is still open.** <!-- Source: NXT-68659:AC "Include all posted transactions whose transaction/posting date falls within the selected period, even if the fiscal period is still open." --> So the dashboard can move during an open period as new postings land; that's expected, not a bug.

🔧 **Implementer:** The dashboard's "Current" windows are only as right as the customer's Fiscal Year Settings, because that's literally where the ranges come from. <!-- Source: NXT-68659:AC "Current Fiscal Year date range comes from Fiscal Year Settings (start and end dates)." --> Walk Job 4 (Open my fiscal year) *before* you point a director at this screen — a fiscal year that's off by a month makes every "Current Quarter" number look wrong.

---

## The trend arrow (am I improving?)

Next to Net Income you'll see a small trend arrow. It compares Net Income for the **latest completed fiscal month** against the month right before it. <!-- Source: NXT-68659:AC "Trend arrow compares Net Income for the latest completed fiscal month vs the immediately previous fiscal month." --> "Completed" means a fiscal month that has fully passed in real time — the current, still-running month doesn't count yet. <!-- Source: NXT-68659:AC "A completed month = a fiscal month that has fully passed in real time." -->

- Up if the latest month beat the previous one, down if it came in lower, and **no arrow at all if they're equal.** <!-- Source: NXT-68659:AC "If latest > previous show ↑; if less show ↓; if equal show no arrow." -->
- Brand-new districts won't see an arrow until there are two completed fiscal months on the books — with fewer than two, it's hidden. <!-- Source: NXT-68659:AC "Hide arrow if fewer than two completed fiscal months exist in the current fiscal year." -->

> ⚠️ **The arrow ignores the period dropdown.** Changing the period selector at the top **does not** change what the arrow compares — it always looks at the two most recently completed fiscal months, no matter what window the KPI cards are showing. <!-- Source: NXT-68659:AC "Trend arrow is not affected by the selected reporting period." --> If that's confusing on screen, the tooltip says it out loud: *"Trend compares the two most recently completed fiscal months."* <!-- Source: NXT-68659:AC "Tooltip: *“Trend compares the two most recently completed fiscal months.”*" -->

---

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

---

## What this is *not*

- It is **not** a report you download. The dashboard is a live on-screen read; the downloadable board/auditor files live in Job 9 (Reports), which generate from posted ledger entries and arrive through the Document Center.
- It does **not** include unposted activity beyond what's already posted to the GL. Like everything in 2.0, the dashboard's truth is the posted ledger. <!-- Source: NXT-68659:AC "Data source is posted financial transactions from the General Ledger." -->

---

<!--
OPEN QUESTIONS FOR SME (do not ship as fact — AC does not state these):
1. Menu path / screen name for the Financial Dashboard. NXT-68659 AC names it "the dashboard" / "Financial
   Dashboard" but gives no navigation path. NXT-68660's epic is "Dashboard". Cross-cluster note: C4 (module
   nav, NXT-66966) may define the left-sidebar location once that lands. Confirm before publishing a path.
2. Whether the dashboard is one of the role-gated surfaces (C2 roles, NXT-66927/66928/66929). AC for NXT-68659
   says nothing about who can see it; do not assert visibility-by-role here.
3. Exact on-screen wording of the trend "up/down" indicator (arrow glyph vs. label). AC specifies ↑ / ↓ behavior
   and "no arrow" but not a text label; left as "up / down arrow" rather than inventing a label string.

STATUS LEDGER:
  - NXT-68659 — Done Done — SHIPPED — KPI cards, period selector, trend arrow, site-by-site table (present tense).
  - NXT-68660 — Story Refinement/Efforting — UPCOMING ("(Coming)") — site-table refinement (sort-by-name,
    aggregated district total). Its Revenue-Analysis and Expense-Analysis cards are STRUCK THROUGH in AC => out of
    scope => intentionally NOT documented as features.
-->
