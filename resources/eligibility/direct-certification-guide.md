---
id: elig-dc-guide
title: "Direct Certification — Full Guide"
platform: schoolcafe
module: Eligibility
page: "Direct Certification"
content_type: long-form-guide
roles: ["director","manager"]
tags: ["onboarding","compliance","frequency:weekly"]
status: draft
template: long-form-guide
source_refs:
  - "wiki/concepts/Eligibility.md"
  - "wiki/workflows/direct-certification.md"
  - "raw/tickets/NXT-15058.md"
  - "raw/tickets/NXT-14223.md"
  - "raw/tickets/NXT-13343.md"
  - "raw/tickets/NXT-60922.md"
  - "raw/tickets/NXT-63982.md"
  - "raw/tickets/NXT-58224.md"
  - "raw/tickets/NXT-21564.md"
updated: 2026-05-13
---

# Eligibility — Direct Certification (Full Guide)

> **One-line promise:** by the end you can run Direct Certification end-to-end — import a state file, review matches, certify students, and pull the reports the USDA review will ask for.
> **Audience:** District directors and child-nutrition managers.
> **Time:** 30–45 min.
> **Status:** Draft. Pending SME review.

## At a glance

Direct Certification (DC) is how districts qualify students for free meals **without** a household application. The state sends a file of students known to be in SNAP, TANF, foster care, or (where authorized) Medicaid. SchoolCafe matches that file against your enrolled students and certifies the matches as free.

In SchoolCafe, DC has two entry paths — **File Import** and **Manual Entry** — and three review tabs: **Matched**, **Potential Matches**, and **Reviewed**. The page name "Potential Matches" is what was previously called "Unmatched"; the rename happened together with the matching-drawer redesign. Source: [[raw/tickets/NXT-15058|NXT-15058]].

What this guide does **not** cover: household paper/online Free & Reduced applications (that lives in a separate guide), income surveys, and the state-by-state policy differences in who appears on a DC file.

## Why this exists

Federal rule requires districts to directly certify SNAP-eligible students without making the household apply. Doing this by hand against a state spreadsheet is the original failure mode — slow, error-prone, and impossible to audit. DC in SchoolCafe is the mechanism that turns the state's file into certified-free students with a scorecard the auditor can see. Source: [[wiki/concepts/Eligibility.md|Eligibility]], [[wiki/workflows/direct-certification.md|Direct Certification Matching]].

## Concepts

- **Direct Certification (DC)** — automatic free-meal qualification from a state-supplied list. Source: [[wiki/workflows/direct-certification.md]].
- **File Import** — the standard path: upload the state DC file; the system matches it against your roster. Manual Entry is a separate path for one-off corrections. Source: [[raw/tickets/NXT-60922|NXT-60922]].
- **Matched** — student record on the DC file was confidently linked to a student in your roster; eligibility set to free with a DC reason. Source: [[raw/tickets/NXT-15058|NXT-15058]].
- **Potential Match** — the file record looked close to one of your students but did not clear the auto-match threshold; needs human review. (Previously labeled "Unmatched.") Source: [[raw/tickets/NXT-15058|NXT-15058]].
- **Reviewed** — a Potential Match that a user has already handled (either matched or marked as not a match). (Previously labeled "Dismissed.") Source: [[raw/tickets/NXT-15058|NXT-15058]].
- **Scorecard** — the per-student breakdown of which fields produced match points and how many. Source: [[raw/tickets/NXT-13343|NXT-13343]], [[raw/tickets/NXT-15058|NXT-15058]].
- **Match Factors** — categories of evidence used in the scorecard: Personal Information, Contact Information, ID Numbers. Source: [[raw/tickets/NXT-15058|NXT-15058]].

## How it works

1. **File arrives.** Your team gets a DC file from the state agency. The cadence is set by the state — often monthly, sometimes more frequently.
2. **Your team uploads the file.** Eligibility → Direct Certification → File Import. (Owner: `Your team`.)
3. **The system runs auto-matching.** Each DC record is scored against enrolled students using Personal Information, Contact Information, and ID Numbers. (Owner: `Cybersoft`.) Source: [[raw/tickets/NXT-15058|NXT-15058]].
4. **Records sort into Matched / Potential Matches / Reviewed.** Confident matches become certifications automatically; the rest queue for human review. Source: [[raw/tickets/NXT-15058|NXT-15058]].
5. **Your team works the Potential Matches queue.** For each potential match, your reviewer opens the drawer, reads the scorecard, and either confirms the match (with a required comment) or marks it Reviewed. (Owner: `Your team`.) Source: [[raw/tickets/NXT-15058|NXT-15058]].
6. **Secondary matching runs when students change.** When an enrolled student's record is updated via Account Management, the system rechecks them against existing DC files — so a typo fix can produce a late match without re-uploading. (Owner: `Cybersoft`.) Source: [[raw/tickets/NXT-14223|NXT-14223]].
7. **Reports.** DC counts and the per-student "By Direct Certification" report are available under Eligibility → Reports. Source: [[raw/tickets/NXT-63982|NXT-63982]], [[raw/tickets/NXT-21564|NXT-21564]].

## Step-by-step (the common path)

### Import a state DC file

1. Navigate to **Eligibility → Direct Certification → File Import**.
2. Upload the state file. The system records the **Import Date** and queues processing.
3. When processing finishes, **Processed Date** is set. Source: [[raw/tickets/NXT-58224|NXT-58224]].
4. Review the file summary — matched count, potential-match count, error count.

### Review the Potential Matches queue

1. Open **Eligibility → Direct Certification → Potential Matches**.
2. Click a row to open the drawer. The drawer shows: photo, full name, preferred name, Student ID, current eligibility + reason, current enrollment site, match factors by category, total match points, and comments. Source: [[raw/tickets/NXT-15058|NXT-15058]].
3. Click **Comparison Scorecard** for the full breakdown of which fields earned points.
4. Decide:
   - **Match** — confirms the certification. A comment is required. Source: [[raw/tickets/NXT-15058|NXT-15058]].
   - **Mark as Reviewed** — record kept but no certification applied.

### Reverse a decision on the Reviewed tab

1. Open **Reviewed**.
2. If a record's status is **Matched**, the available action is **Unmatch & Mark as Reviewed**.
3. If a record's status is **Reviewed**, the available action is **Match**. Source: [[raw/tickets/NXT-15058|NXT-15058]].

### Run the DC Counts report

1. Eligibility → Reports → Direct Certification Counts.
2. Multi-select **Site Code / Site Name** for the sites you want. Source: [[raw/tickets/NXT-63982|NXT-63982]].
3. Pick the date range with the date picker.
4. Run. Source criteria appear on the report header so the file is auditable.

## Examples

### Example 1 — A typical monthly cycle (`<District A>`)

Your team receives the state file on the first Tuesday of the month. Upload at 7am, processing completes by 7:10am, 1,824 students match automatically, 47 land in Potential Matches, 6 produce errors (typically malformed dates). Your reviewer works through 47 potential matches over two days — confirms 31, marks 16 as not-a-match — and re-runs the DC Counts report for the auditor.

### Example 2 — A late match via secondary matching (`<District B>`)

A student's last name was misspelled at enrollment. Three weeks after the DC file import they were not on it. Your registrar corrects the spelling in Account Management; the system silently re-runs the match against the existing file and the student now appears as Matched. Source: [[raw/tickets/NXT-14223|NXT-14223]].

### Example 3 — Manual Entry vs. File Import (`<District C>`)

A new student arrives mid-year already SNAP-certified per a household letter. Your team needs to enter the certification manually. On the Manual Entry screen, "Direct Certification" is **not** an option in the entry-method dropdown — that option exists only for File Import. Use the appropriate other certification reason your state allows. Source: [[raw/tickets/NXT-60922|NXT-60922]].

## Edge cases & known issues

- **"Direct Certification" missing from a dropdown?** That's by design on Manual Entry. It only appears for File Import. Source: [[raw/tickets/NXT-60922|NXT-60922]].
- **A student moved sites mid-import.** The drawer shows current enrollment site, which may not be the site that was active when the file ran. Source: [[raw/tickets/NXT-15058|NXT-15058]].
- **The "By Direct Certification" report is now HTML.** Old PDF/Dundas links from saved bookmarks may not resolve. Source: [[raw/tickets/NXT-21564|NXT-21564]].
- **Status labels changed.** "Unmatched" → "Potential Matches" and "Dismissed" → "Reviewed". Older training material may use the old labels. Source: [[raw/tickets/NXT-15058|NXT-15058]].

## Sources

- [[wiki/concepts/Eligibility.md|Eligibility (concept page)]]
- [[wiki/workflows/direct-certification.md|Direct Certification (workflow page)]]
- [[raw/tickets/NXT-15058.md|NXT-15058 — Potential Matches drawer & rename]]
- [[raw/tickets/NXT-13343.md|NXT-13343 — Scorecard on Matched]]
- [[raw/tickets/NXT-14223.md|NXT-14223 — Secondary matching on student update]]
- [[raw/tickets/NXT-60922.md|NXT-60922 — Remove DC option from Manual Entry]]
- [[raw/tickets/NXT-63982.md|NXT-63982 — DC Counts report multi-select]]
- [[raw/tickets/NXT-21564.md|NXT-21564 — By DC report HTML conversion]]
- [[raw/tickets/NXT-58224.md|NXT-58224 — Elig - Direct Cert custom-report dataset]]
