---
id: elig-dc-daily-review-sop
title: "SOP — Daily Potential Matches Review"
platform: schoolcafe
module: Eligibility
page: "Direct Certification — Potential Matches"
content_type: sop-how-to
roles: ["manager"]
tags: ["frequency:daily","compliance","sop"]
status: draft
template: sop-how-to
source_refs:
  - "raw/tickets/NXT-15058.md"
  - "raw/tickets/NXT-13343.md"
  - "raw/tickets/NXT-14223.md"
  - "raw/tickets/NXT-63982.md"
updated: 2026-05-13
---

# SOP — Daily Potential Matches Review

> **Trigger:** a new DC file was imported, **or** there are open rows on the Potential Matches tab from a prior day.
> **Owner:** child-nutrition manager (district). (`Your team`)
> **Frequency:** daily until the queue is empty.
> **Time:** 5–20 minutes depending on queue size.

## When to run this

Run every business day until Potential Matches is empty after a file import. Don't let the queue persist across reporting periods — an unworked queue means students who should be certified free are eating at the wrong price tier.

## Steps

1. **`Your team`** — open **Eligibility → Direct Certification → Potential Matches**.
2. **`Your team`** — click the first row to open the drawer. Read Match Points and the three category totals: Personal Information, Contact Information, ID Numbers. Source: [[raw/tickets/NXT-15058|NXT-15058]].
3. **`Your team`** — open **Comparison Scorecard** for any row where the categories disagree (e.g. high Personal but zero ID Numbers — that's a candidate for typo or stale ID).
4. **`Your team`** — decide:
   - **Match** — type a comment that names the specific evidence ("matched on full name + DOB + guardian phone"). Save. Source: [[raw/tickets/NXT-15058|NXT-15058]].
   - **Mark as Reviewed** — close without certifying. Source: [[raw/tickets/NXT-15058|NXT-15058]].
5. **`Your team`** — for rows that look almost-but-not-quite right, check Account Management for a correctable typo on the student record. After a save there, secondary matching reruns and the row may now auto-match. Source: [[raw/tickets/NXT-14223|NXT-14223]].
6. **`Your team`** — repeat until the queue is empty.

## Checks before you finish

- [ ] Potential Matches tab shows zero rows for today's date range.
- [ ] Every Matched action you performed has a non-empty comment (you can spot-check by opening any row you matched).
- [ ] DC Counts report (Eligibility → Reports → Direct Certification Counts) for today's site selection shows the certifications you confirmed. Source: [[raw/tickets/NXT-63982|NXT-63982]].

## Escalation

- **A row's scorecard is high in Personal Information but zero in ID Numbers, and Account Management shows the right ID →** escalate to your district registrar with the student's ID and the file # before matching. Could be a state-file ID error.
- **A row you matched yesterday now shows back as Potential Match →** open the student in Account Management; a roster change may have triggered secondary matching to re-score them. Verify before acting. Source: [[raw/tickets/NXT-14223|NXT-14223]].
- **More than 24 hours of queue not cleared →** escalate to the district director with the count.

## Sources

- [[raw/tickets/NXT-15058|NXT-15058 — Potential Matches drawer]]
- [[raw/tickets/NXT-13343|NXT-13343 — Scorecard]]
- [[raw/tickets/NXT-14223|NXT-14223 — Secondary matching]]
- [[raw/tickets/NXT-63982|NXT-63982 — DC Counts report]]
