<!--
Cluster C1 guide refresh — Job 10 (Posting Activity Log) + "What changed in 2.0" table row + Glossary.
Grounding: every product-behavior sentence carries an inline <!-- Source: NXT-####:AC "verbatim quote" --> tracing to that ticket's Acceptance Criteria.
Status: ALL ten tickets in this cluster are Jira status "New" → tagged (Coming) / in-development. The Done Done baseline (NXT-69493) the current Job 10 was written from stays accurate; this refresh layers the upcoming wave on top and qualifies the present-tense "posting is automatic, do nothing / Approve-Post buttons gone" claims.
RN is empty for every ticket here, so AC is the sole highest-trust source; desc carries persona/intent only.
-->

# Job 10 — Posting Activity Log (refresh)

> ⚠️ **What's changing here (read this before the section below).** Today's guide tells you posting is fully hands-off — "Do nothing. Posting fires the moment the upstream period closes… you can no longer forget to post" — and the Glossary says the old **Approve / Post** buttons are *gone*. **That is true for the version shipping now, but a wave of work is in flight that brings manual Post / Repost controls back as an option.** None of it has shipped yet (all of it is in development at the time of writing). If you are reading this and you see **Post** buttons or a **Ready to Post** queue on your screen, the product is not broken and neither is this guide — you are on a newer build. Everything tagged **(Coming)** below is the new behavior.

---

## TL;DR

- **Today (shipped):** the Posting Activity Log is a read-only monitor. Postings run in the background when an upstream period closes; you open this page to confirm jobs ran and to see why any failed. The shipped page has **four** summary cards (Total Jobs / Completed / Failed / Running) and a reverse-chronological job table. <!-- Source: NXT-69493:AC "*Summary cards*: Four cards at top — Total Jobs (30 Days), Completed (green), Failed (red), Running (orange)." --> <!-- Source: NXT-69493:AC "*Manual trigger*: Out of scope — jobs triggered from Fiscal Periods page, not here." -->
- **(Coming) Manual posting comes back as an option.** A **Ready to Post** queue lets you review closed periods and post them yourself, without leaving this page. <!-- Source: NXT-70065:AC "A \"Ready to Post\" section appears between the summary cards and the job history table" --> <!-- Source: NXT-70065:AC "two actions: Review and Post All" -->
- **(Coming) Two posting grids** — one for POS, one for Inventory — give you a per-site, per-month list with a **Status** column and **Post / View / Repost / Remove** actions. <!-- Source: NXT-65487:AC "*Status* (Not Ready, Ready to Post, Posted, Error)" --> <!-- Source: NXT-65487:AC "*Actions* (Post, View, Repost, Remove)" -->
- **(Coming) The top of the page is redesigned** from four system-job counts to three "what matters now" cards: posting progress, what needs attention, and dollars posted this period. <!-- Source: NXT-70066:AC "Replace the four Phase 1 cards (Total Jobs, Completed, Failed, Running) with three cards in a horizontal grid" -->
- **(Coming) A gentle nudge** points manual posters toward turning automatic posting back on. <!-- Source: NXT-70069:AC "Banner text: \"You're posting manually. Districts with automatic posting enabled only visit this page when something needs attention.\"" -->

---

## What this page is for

You come to the Posting Activity Log to answer one question: *did my financial data post correctly, and if not, what do I fix?* <!-- Source: NXT-69493:desc "As a Child Nutrition Director, I want to view a log of all background posting jobs, so that I can confirm my financial data is being posted correctly." --> The shipped version is a monitor only — postings are triggered elsewhere, and you watch them land here. <!-- Source: NXT-69493:AC "*Manual trigger*: Out of scope — jobs triggered from Fiscal Periods page, not here." -->

The upcoming work keeps that monitoring job but adds a second job on the same page: **reviewing and posting closed periods yourself.** <!-- Source: NXT-70065:desc "As a CN Director, I want to see which periods are closed and waiting for ledger entries so I can review and post them without navigating away from the Activity Log." -->

---

## (Coming) The Ready-to-Post queue — review and post without leaving the page

> 🔧 **Implementer note:** This section is the single biggest change to the "do nothing" story. If your district leaves automatic posting on, you will rarely see this queue do anything (closed periods post themselves and the queue stays empty). If automatic posting is off, this is where you'll work each period close. All of it is **(Coming)** — status *New* / in development.

A new **Ready to Post** card sits between the summary cards and the job history table; it's expanded by default and shows a badge with how many periods are waiting. <!-- Source: NXT-70065:AC "A \"Ready to Post\" section appears between the summary cards and the job history table" --> <!-- Source: NXT-70065:AC "Section is a collapsible card with a left-border accent and a badge showing pending item count" --> <!-- Source: NXT-70065:AC "Section is expanded by default; collapses on header click" -->

Each waiting period shows as one row with the period name, how many sites it covers, a type badge (POS or Inventory), and two buttons — **Review** and **Post All**. <!-- Source: NXT-70065:AC "Each pending item shows as a row: period name, site count, type badge (POS Posting / Inventory Posting), and two actions: Review and Post All" --> Rows are grouped one per period per type, so a large district doesn't get a wall of rows. <!-- Source: NXT-70065:AC "Items aggregate one row per period per type, regardless of district size" -->

**To review before posting:** click **Review** to open an inline checklist of the sites in that period — each row a checkbox, the site name, the entry types you'd expect, and an estimated amount. <!-- Source: NXT-70065:AC "Clicking Review expands an inline panel below that row with a checklist table: checkbox, site name, expected entry types, estimated amount" --> Every site is checked by default; you get a **Select All / Deselect All** toggle and a search-by-site-name filter, and the **Post Selected (X sites)** button updates its count as you check and uncheck. <!-- Source: NXT-70065:AC "All sites checked by default; \"Select All / Deselect All\" toggle and search-by-site-name filter are present" --> <!-- Source: NXT-70065:AC "\"Post Selected (X sites)\" button updates count dynamically as user checks/unchecks" -->

**To post:** clicking **Post All** or **Post Selected** opens a confirmation modal with a preview table — site, entry types, estimated amount, and a total — so you confirm the dollars before you commit. <!-- Source: NXT-70065:AC "Clicking Post All or Post Selected opens a confirmation modal showing a preview table of entries (site, entry types, estimated amount, total)" --> On confirm, the queue row animates away, the badge count drops, and a new **Running** job appears at the top of the job history table with **Triggered By** showing *your* name (not "System"). <!-- Source: NXT-70065:AC "On confirm: pending item animates out, a new Running job appears at the top of the job history table with Triggered By showing the current user name, badge count decrements" -->

When several periods are waiting, a **Post All Pending** button appears in the section header and its confirmation modal rolls everything up to a period-level summary with totals. <!-- Source: NXT-70065:AC "When 2+ items are pending, a \"Post All Pending\" batch button appears in the section header; confirmation modal shows a period-level summary with totals" -->

When nothing is waiting, the section shows an all-clear empty state. <!-- Source: NXT-70065:AC "When no items are pending, section shows an empty state: \"All caught up. Every closed period has been posted.\" with muted quip underneath" -->

---

## (Coming) The POS and Inventory posting grids — per-site Post / Repost / Remove

> ⚠️ **Watch-out — this is the line the Glossary will need to qualify.** Today's Glossary says the legacy **Approve / Post** buttons are *gone*. These two grids bring **Post**, **Repost**, and **Remove** actions back at the per-site level. Treat the Glossary's "gone" as "gone in the version that shipped, returning as an explicit per-site control." Both grids are **(Coming)** — status *New*.

**POS postings grid.** A table lists each site and month with **Total Revenue**, **Total Transactions**, and a **Status** of *Not Ready, Ready to Post, Posted,* or *Error*, plus **Post / View / Repost / Remove** actions. <!-- Source: NXT-65487:AC "Create a table with these columns:" --> <!-- Source: NXT-65487:AC "*Status* (Not Ready, Ready to Post, Posted, Error)" --> <!-- Source: NXT-65487:AC "*Actions* (Post, View, Repost, Remove)" --> Selecting a site shows a summary of its POS transactions. <!-- Source: NXT-65487:AC "Selecting a site displays a summary of various POS transactions." -->

**Inventory postings grid.** Same idea for inventory — site, month, the same four-value **Status**, and **Post / View / Repost / Remove**; selecting a site shows a summary of its inventory transactions. <!-- Source: NXT-66123:AC "Create a table with these columns:" --> <!-- Source: NXT-66123:AC "*Status* (Not Ready, Ready to Post, Posted, Error)" --> <!-- Source: NXT-66123:AC "*Actions* (Post, View, Repost, Remove)" --> <!-- Source: NXT-66123:AC "Selecting a site displays a summary of various Inventory transactions." -->

> 🔧 **Implementer note — period setup gates inventory posting.** If your financial and inventory periods aren't lined up, the grid blocks the post and shows this exact message in an info tooltip: *"To Approve or Post, close all open Inventory Periods up to the selected Financial Period's end date. To Approve or Post, open all Financial Periods from the start date of the selected Financial Period to today's date."* <!-- Source: NXT-66123:AC "*Then* I should receive the message “To Approve or Post, close all open Inventory Periods up to the selected Financial Period's end date.\nTo Approve or Post, open all Financial Periods from the start date of the selected Financial Period to today's date.” via a tooltip with an info icon." -->

> **Open question (do not invent):** NXT-66123's title and its tooltip both use the word **Approve** ("To *Approve* or Post…"), but its **Actions** column lists only *Post / View / Repost / Remove* — no Approve button. The coverage audit also referred to an "Approve" action on the Inventory grid. The AC does not define a separate Approve control, so this guide does not describe one. **Confirm with the PO whether Inventory has a distinct Approve step or whether "Approve" is legacy wording for Post.**

---

## (Coming) Redesigned summary cards — progress, problems, dollars

The four shipped cards (Total Jobs / Completed / Failed / Running) are being replaced by **three** cards. <!-- Source: NXT-70066:AC "Replace the four Phase 1 cards (Total Jobs, Completed, Failed, Running) with three cards in a horizontal grid" --> <!-- Source: NXT-70066:desc "As a CN Director, I want the top-of-page cards to tell me what matters right now — progress, problems, and dollars — not system job counts." -->

1. **Posting Progress** — the current fiscal period, showing "X of Y sites posted" with a thin progress bar; a site counts as posted only once *all* its posting types are done. <!-- Source: NXT-70066:AC "Card 1 — Posting Progress: label is the current fiscal period name (uppercase), value shows \"X of Y sites posted\", thin green progress bar underneath proportional to completion. A site counts as \"posted\" only when all its posting types are complete." -->
2. **Needs Attention** — a red count of failed/unresolved jobs; click it to jump to the table filtered to failures. When there are none it reads "No issues ✓" in green. <!-- Source: NXT-70066:AC "Card 2 — Needs Attention: value shows failed/unresolved count in red. Clickable — scrolls to and filters the job history table to failed jobs. When zero: \"No issues ✓\" in green" -->
3. **Posted This Period** — total dollars posted to the ledger this period, with a delta versus the prior period. <!-- Source: NXT-70066:AC "Card 3 — Posted This Period: value shows total dollar amount of ledger entries for the current period in green. Subtitle shows delta vs prior period (e.g., \"↑ $4,200 vs Dec 2025\")" -->

The old job counts don't disappear — they move into the job-table header as muted inline text (for example, "25 total · 21 completed · 2 failed · 1 running"). <!-- Source: NXT-70066:AC "The old job counts (total, completed, failed, running) move to the job history table section header as inline muted text: \"Posting Jobs (Last 30 Days) · 25 total · 21 completed · 2 failed · 1 running\"" -->

---

## (Coming) Failures surface first

Failed jobs get pinned to the top of the table no matter how you've sorted it, with a **Needs Attention** divider above them and a **Recent Jobs** divider below. <!-- Source: NXT-70067:AC "Failed jobs are pinned to the top of the job history table regardless of sort order" --> <!-- Source: NXT-70067:AC "A \"Needs Attention\" divider row appears above the first failed job; a \"Recent Jobs\" divider appears below the last failed job, before completed/running jobs" --> The **Failed** filter chip carries a red count badge (for example, "Failed 2"). <!-- Source: NXT-70067:AC "The \"Failed\" filter chip shows a red badge with the count of failed jobs (e.g., \"Failed 2\")" --> Expanding a failed job shows the error, a plain-language help line, and a **Resolve Issue** link. <!-- Source: NXT-70067:AC "Expanded failed job detail panels show: error message, a direct help line (\"This one needs a fix before it's audit-ready. Here's what to do →\"), and a Resolve Issue link" -->

---

## (Coming) Richer completed-job detail + export

Open a completed POS job and you'll see an **Entries by GL Entry Type** table — entry type, the debit/credit accounts, a count, and a total. <!-- Source: NXT-70068:AC "Expanded completed POS job panels show an \"Entries by GL Entry Type\" table with columns: entry type, debit/credit accounts, entry count, total amount" --> **Reimbursement Receivable** is the first, bold row; **Sales Tax Collected** appears as a muted, conditional last row only if your district has sales tax configured, with a footnote that entry types depend on your configuration. <!-- Source: NXT-70068:AC "Reimbursement Receivable is the first row in the table, visually prominent (bold text)" --> <!-- Source: NXT-70068:AC "Sales Tax Collected appears as the last row only if the district has sales tax configured; styled as conditional (muted italic)" --> <!-- Source: NXT-70068:AC "A footnote below the table reads: \"Entry types shown depend on your district's configuration.\"" --> An **Export Entries** button offers **CSV, PDF,** or **ERP Format**. <!-- Source: NXT-70068:AC "Clicking Export shows a dropdown with format options: CSV, PDF, ERP Format" --> When you posted a job yourself, the **Triggered By** column shows a user icon before your name. <!-- Source: NXT-70068:AC "The Triggered By column shows a user icon before the name when the job was triggered manually (not \"System\")" -->

---

## (Coming) "You're posting manually" nudge

If automatic posting is off, a low-key banner appears between the summary cards and the Ready-to-Post section: *"You're posting manually. Districts with automatic posting enabled only visit this page when something needs attention."* <!-- Source: NXT-70069:AC "A standalone banner appears between the summary cards and the Ready to Post section when automatic posting is not enabled" --> <!-- Source: NXT-70069:AC "Banner text: \"You're posting manually. Districts with automatic posting enabled only visit this page when something needs attention.\"" --> It offers an **Enable automatic posting →** link and an X to dismiss for the session, and it never shows if automatic posting is already on. <!-- Source: NXT-70069:AC "Right side shows \"Enable automatic posting →\" link and an X dismiss button" --> <!-- Source: NXT-70069:AC "Dismissing hides the banner for the session (persists via local storage)" --> <!-- Source: NXT-70069:AC "Banner never renders if automatic posting is already enabled" --> The page subtitle becomes "Your posting jobs, tracked and audit-ready." <!-- Source: NXT-70069:AC "Page subtitle updated to: \"Your posting jobs, tracked and audit-ready.\"" -->

> 🔧 **Implementer note:** This banner is the product's own acknowledgement that manual posting is a *mode*, not the default. The 2.0 promise ("posting is automatic") is the recommended path; the manual queue and grids above exist for districts that choose to keep it hands-on. Frame it that way for staff so the two messages don't read as contradictory.

---

## (Coming) Notifications: blocked postings and login summaries

**Blocked by missing GL mappings.** When the readiness gate blocks a posting job, a bell notification fires and a **yellow** banner pins to the top of this page: *"Financial postings could not run. [X] required GL mappings are incomplete."* — where [X] is the live count of gaps. <!-- Source: NXT-70866:AC "When the readiness gate is active, display a yellow informational banner pinned to the top of the Posting Activity Log page" --> <!-- Source: NXT-70866:AC "Notification text: _\"Financial postings could not run. [X] required GL mappings are incomplete.\"_ where [X] = current count of incomplete mappings" --> The banner links straight to the Account Mapping page filtered to the incomplete mappings, has no dismiss button, and clears itself once every required mapping is complete. <!-- Source: NXT-70866:AC "Banner includes a link to Account Mapping page, pre-filtered to incomplete mappings only" --> <!-- Source: NXT-70866:AC "Banner has no dismiss button — it remains visible as long as gaps exist" --> <!-- Source: NXT-70866:AC "Banner disappears automatically when all required mappings are complete" -->

**Login summary.** When you arrive in Financial Oversight and there's been posting activity since your last login, a banner summarizes it — e.g. "X posting jobs completed since your last login. View Activity Log →" — and prioritizes warnings if any jobs failed or need review. <!-- Source: NXT-69972:AC "If new activity exists, a notification banner displays" --> <!-- Source: NXT-69972:AC "*Given* there are new completed jobs since last login, *Then:* notification displays: \"X posting jobs completed since your last login. View Activity Log →\"" --> <!-- Source: NXT-69972:AC "*Then:* notification prioritizes warnings: \"X jobs need attention, Y completed. View Activity Log →\"" --> Clicking through opens this page filtered to jobs since your last login. <!-- Source: NXT-69972:AC "*Given* the user clicks \"View Activity Log →\", *Then:* user navigates to Posting Activity Log, filtered to jobs since last login." -->

> 🔧 **New status to know — "Requires Review."** Beyond Completed / Failed, a job can land as **Requires Review** when a posting already exists for that period or claim. The expanded row tells you to review and manually reverse the existing entry before reposting. <!-- Source: NXT-69972:AC "*Given* a posting job has status \"Requires Review\" due to existing system-generated entry, *Then:* expanded row shows: \"A system-generated posting already exists for [Period]. Review and manually reverse if needed before reposting.\"" --> <!-- Source: NXT-69972:AC "*Given* a posting job has status \"Requires Review\" due to existing claim posting, *Then:* expanded row shows: \"A posting already exists for this claim. Review and manually reverse if needed before reposting.\"" -->

---

## (Coming) Fix the mapping once — failed jobs rerun themselves

You don't re-post failed jobs by hand after fixing a mapping. When you save the missing GL mappings under **Financials > Account Mapping**, the system automatically reruns every posting job that had failed for a missing-mapping reason, and logs each new result here. <!-- Source: NXT-70111:AC "When a user saves missing GL mappings in {{Financials > Account Mapping}}, the system automatically reruns all previously failed posting jobs whose failure reason was missing mapping." --> <!-- Source: NXT-70111:AC "The rerun is system-triggered (no manual retry), and each job logs the new result (success or new failure reason) in Posting Activity Log." -->

> 🔧 **Implementer note — the resolution loop, end to end:** a job fails for a missing mapping → the yellow banner and bell point you to Account Mapping → you fill the gap → the failed jobs rerun on their own and reappear here with their new result. No "resolved" notification fires; postings just resume. <!-- Source: NXT-70866:AC "If the user resolves all gaps, do not send a \"resolved\" notification — postings resume silently on the next cycle" -->

---

## Glossary — proposed qualification

> The current Glossary line reads (paraphrased from the audit): **"Approve / Post buttons — gone in 2.0; posting is automatic."** Recommended replacement, qualified and dated:

**Approve / Post buttons (legacy → 2.0).** Removed from the version of the Posting Activity Log that shipped first; that build is a read-only monitor and posting runs in the background. <!-- Source: NXT-69493:AC "*Manual trigger*: Out of scope — jobs triggered from Fiscal Periods page, not here." --> **(Coming)** Per-site **Post / Repost / Remove** actions return on the POS and Inventory posting grids, and a **Review / Post All** queue returns on the Activity Log, for districts that post manually. <!-- Source: NXT-65487:AC "*Actions* (Post, View, Repost, Remove)" --> <!-- Source: NXT-66123:AC "*Actions* (Post, View, Repost, Remove)" --> <!-- Source: NXT-70065:AC "two actions: Review and Post All" --> So: "gone" describes the first 2.0 build, not the product's end state.

> **Open question (do not invent a release label):** the AC for these tickets does not state *when* the manual controls ship or under what release/version name. This guide tags them **(Coming)** only. Do not add a version number, sprint, or date to the Glossary or the "What changed in 2.0" table until the PO confirms one.

---

## "What changed in 2.0" table — proposed row edits

> The audit flagged these existing rows as stating the *opposite* of what's coming as present-tense fact. Proposed replacements (the legacy→2.0 column keeps the shipped-first behavior; a new note column qualifies it):

| Area | Shipped first in 2.0 | (Coming) — qualify the "gone/automatic" claim |
|---|---|---|
| Posting trigger | Posting runs in the background; manual trigger is out of scope on this page. <!-- Source: NXT-69493:AC "*Manual trigger*: Out of scope — jobs triggered from Fiscal Periods page, not here." --> | A manual **Ready to Post** queue (**Review / Post All**) returns on the Activity Log. <!-- Source: NXT-70065:AC "two actions: Review and Post All" --> |
| Summary cards | Four cards: Total Jobs / Completed / Failed / Running. <!-- Source: NXT-69493:AC "*Summary cards*: Four cards at top — Total Jobs (30 Days), Completed (green), Failed (red), Running (orange)." --> | **Three** cards (Posting Progress / Needs Attention / Posted This Period) replace them; the counts move to the table header. <!-- Source: NXT-70066:AC "Replace the four Phase 1 cards (Total Jobs, Completed, Failed, Running) with three cards in a horizontal grid" --> |
| Approve / Post buttons | Removed; the page is a read-only monitor. <!-- Source: NXT-69493:AC "*Manual trigger*: Out of scope — jobs triggered from Fiscal Periods page, not here." --> | **Post / Repost / Remove** return per site on the POS and Inventory grids. <!-- Source: NXT-65487:AC "*Actions* (Post, View, Repost, Remove)" --> <!-- Source: NXT-66123:AC "*Actions* (Post, View, Repost, Remove)" --> |
| "You can't forget to post" | Automatic posting means you don't have to remember. *(Keep, but qualify.)* | If automatic posting is off, a **"You're posting manually"** nudge banner appears. <!-- Source: NXT-70069:AC "Banner text: \"You're posting manually. Districts with automatic posting enabled only visit this page when something needs attention.\"" --> |

---

## Sources

All ten tickets in this cluster are Jira status **New** → tagged **(Coming)** throughout. The one shipped anchor used to describe today's behavior is **NXT-69493** (Done Done).

- **NXT-69493** (Done Done) — current shipped Posting Activity Log: four cards, read-only monitor, manual trigger out of scope.
- **NXT-70065** (New) — Ready-to-Post queue (Review / Post All).
- **NXT-70066** (New) — summary cards redesign (four → three).
- **NXT-70067** (New) — failed-job pinning, dividers, red Failed badge, Resolve Issue.
- **NXT-70068** (New) — enhanced completed-job detail + Export (CSV/PDF/ERP).
- **NXT-70069** (New) — "You're posting manually" nudge banner + subtitle change.
- **NXT-69972** (New) — login notifications + "Requires Review" status + failure messages.
- **NXT-65487** (New) — View POS Postings grid (Post / View / Repost / Remove).
- **NXT-66123** (New) — View Inventory Postings grid + period-config tooltip.
- **NXT-70866** (New) — blocked-posting bell + yellow Account-Mapping banner.
- **NXT-70111** (New) — auto-rerun failed jobs when GL mapping is saved.
