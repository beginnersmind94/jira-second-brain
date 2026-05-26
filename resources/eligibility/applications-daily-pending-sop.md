---
id: elig-apps-daily-pending-sop
title: "SOP — Daily Pending Applications & Pending Students Review"
platform: schoolcafe
module: Eligibility
page: "Applications"
content_type: sop-how-to
roles: ["manager"]
tags: ["frequency:daily","applications","sop"]
status: draft
template: sop-how-to
source_refs:
  - "raw/tickets/NXT-66798.md"
  - "raw/tickets/NXT-5204.md"
  - "raw/tickets/NXT-7337.md"
  - "raw/tickets/NXT-56318.md"
updated: 2026-05-13
---

# SOP — Daily Pending Applications & Pending Students Review

> **Trigger:** an online application has landed in Pending overnight, **or** there are open rows on the Pending Applications or Pending Students tab from a prior day.
> **Owner:** child-nutrition manager (district). (`Your team`)
> **Frequency:** daily until both Pending tabs are empty.
> **Time:** 10–30 minutes depending on queue size.

## When to run this

Run every business day until both Pending tabs show zero rows. An unworked Pending Applications queue means households who should be Free or Reduced are getting charged Paid prices at the cashier — and households whose application is sitting in Pending Students aren't getting any eligibility update at all because the student-to-application link hasn't been resolved. Source: [[raw/tickets/NXT-66798|NXT-66798]].

## Steps

### Part 1 — Pending Applications tab

Applications fail automatic processing (or are manually marked Pending) when they hit a configured Pending Reason — for example, household-size discrepancy, CEP site mismatch, missing SSN when required, or refused benefits questions that need a human read.

1. **`Your team`** — open **Eligibility → Applications** and select the **PENDING APPLICATIONS** tab.
2. **`Your team`** — click the **View (paper) icon** on the first row to open **Application Details**. Source: [[raw/tickets/NXT-5204|NXT-5204]].
3. **`Your team`** — navigate to the **Summary** section to read the **Pending Reasons** — this tells you exactly what's blocking automatic processing.
4. **`Your team`** — read each section the application has: **Students**, **Household Members**, **Contact Information**, **Details** (other benefits, demographic), **Notifications**, **Comments**, **Documents**, **Application Status History**, **Adult Signature / SSN**. Some sections may hide based on the application's configuration. Source: [[raw/tickets/NXT-7337|NXT-7337]].
5. **`Your team`** — decide (the **MORE ACTIONS** button is where most decisions live, in addition to the primary Process / Notify in the left panel):
   - **PROCESS APPLICATION** — process or reprocess. **A comment is required** if the application is in Pending or Processed status when you click Process. Source: [[raw/tickets/NXT-5204|NXT-5204]].
   - **REFUSE BENEFITS** — declines benefits; select a Result, a Start Date, and enter a comment.
   - **MARK AS PENDING** — keep it open if you've made edits but aren't ready to process.
   - **DELETE** — pick a Reason, add a required comment. If any students are on the application, **deletion returns them to their previous eligibility** — verify what that is first.
   - **ADD TO VERIFICATION** — push into the verification process instead of a normal certification.
6. **`Your team`** — if you need to send a household notification (acceptance, denial, request for missing info), use **NOTIFY** from the left panel. The notification will use the application's selected language if a corresponding language template is configured. Source: [[raw/tickets/NXT-5204|NXT-5204]].
7. **`Your team`** — repeat for every row until the tab is clear.

### Part 2 — Pending Students tab

A Pending Student row exists when the application was submitted but the system can't link it to a student in your roster — usually because the student wasn't enrolled at submission time, or the name/DOB on the application doesn't match the roster cleanly. Source: [[raw/tickets/NXT-66798|NXT-66798]].

1. **`Your team`** — switch to the **PENDING STUDENTS** tab.
2. **`Your team`** — click **FIND MATCHES** to let the system attempt automatic matching. A green checkmark appears in the Matched Status column for rows where the system finds candidates. Source: [[raw/tickets/NXT-66798|NXT-66798]].
3. **`Your team`** — for each row with potential matches, click the **View (paper) icon** to open Match Details. The screen shows each candidate student's **Status** (Active / Inactive) and current **Eligibility** with Basis (e.g. "Free (DC MEDICAID)"). If multiple candidates appear, you **must** select one with the **Match** button before continuing — the workflow does not let you proceed without selecting. Source: [[raw/tickets/NXT-66798|NXT-66798]].
4. **`Your team`** — for rows that didn't auto-find candidates, click the **Search (magnifying glass) icon** for the row, enter the student's name in **Search Students**, click **SELECT STUDENT** on the right row, compare Application Details to the Matched Student, then click **MATCH** in the bottom-right.
5. **`Your team`** — if the student record itself has the wrong details (typo in the application), click the **Edit (pencil) icon** and update — then **Save** in the bottom right. The Edit slide deck returns you to the Pending Students tab.
6. **`Your team`** — **once all rows on the page have a match selected**, check the checkbox at the top of the grid to select all (or pick individual rows), then click **PROCESS MATCHES**. A confirmation pop-up displays; click **YES**. Application Details update at this point — student gets the benefit, the link is recorded. Source: [[raw/tickets/NXT-66798|NXT-66798]].

## Checks before you finish

- [ ] Pending Applications tab shows zero rows for today (or only rows you've explicitly chosen to leave open with a Comment).
- [ ] Pending Students tab shows zero rows.
- [ ] Every **Process Application** action you ran has a non-empty comment (you can spot-check by opening any application you processed and reading the Comments section).
- [ ] **Eligibility Status Changes Report** (Eligibility → Reports → Eligibility Status Changes) with today's Process Date range shows the certifications you completed. Source: [[raw/tickets/NXT-56318|NXT-56318]].

## Escalation

- **A Pending Application's Pending Reason names a household-size mismatch you can't verify →** escalate to the household for clarification via the Notify action; don't process until they reply.
- **A Pending Application has students at a CEP site and you don't know whether to process →** check Form Configuration → Auto-Processing Rules with your director — the CEP-park rule is a deliberate district setting, not a bug.
- **A Pending Student row has multiple Active candidates with the same name and DOB →** stop. Escalate to your district registrar; the wrong match here puts the wrong eligibility on the wrong student.
- **Both Pending tabs are clear, but the Eligibility Status Changes report shows fewer Process Date entries than you remember running →** open an application from today via the ALL tab and read the **Application Status History** section to verify it processed. If the status never moved past Pending, re-run.
- **More than 48 hours of queue not cleared →** escalate to the district director with the count.

## Sources

- [[raw/tickets/NXT-66798|NXT-66798 — Pending Students with multiple matches]]
- [[raw/tickets/NXT-5204|NXT-5204 — Application Details: Summary & Navigation panel]]
- [[raw/tickets/NXT-7337|NXT-7337 — Application Entry: Review conditionals]]
- [[raw/tickets/NXT-56318|NXT-56318 — Eligibility Status Changes Report]]
