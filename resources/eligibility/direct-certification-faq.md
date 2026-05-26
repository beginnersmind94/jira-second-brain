---
id: elig-dc-faq
title: "Direct Certification — FAQ"
platform: schoolcafe
module: Eligibility
page: "Direct Certification"
content_type: faq
roles: ["director","manager","cashier"]
tags: ["troubleshooting","compliance"]
status: draft
template: faq
source_refs:
  - "raw/tickets/NXT-15058.md"
  - "raw/tickets/NXT-14223.md"
  - "raw/tickets/NXT-13343.md"
  - "raw/tickets/NXT-60922.md"
  - "raw/tickets/NXT-63982.md"
  - "raw/tickets/NXT-21564.md"
  - "raw/tickets/NXT-58224.md"
updated: 2026-05-13
---

# Direct Certification — FAQ

## Q1 — Where did the "Unmatched" tab go?

It was renamed to **Potential Matches**. Same data, same scoring, new name. The rename happened alongside the new drawer view.

**Source:** [[raw/tickets/NXT-15058|NXT-15058]]

---

## Q2 — Why is "Dismissed" now "Reviewed"?

To make the meaning clearer — a row marked Reviewed has been handled by a human, but it can still be matched later if you change your mind. The status was renamed in the same release as the Potential Matches rename.

**Source:** [[raw/tickets/NXT-15058|NXT-15058]]

---

## Q3 — Why can't I select "Direct Certification" on the Manual Entry screen?

By design. Direct Certification is only available as a result of File Import. It was explicitly removed from the Manual Entry dropdown so users wouldn't claim a DC certification without a real state-file source.

**Source:** [[raw/tickets/NXT-60922|NXT-60922]]

---

## Q4 — What does the scorecard actually score on?

Three categories: **Personal Information** (name fields, DOB, DOB variations), **Contact Information** (guardian name and address, phone numbers), and **ID Numbers** (SSN, State ID, Student ID). Each category accumulates points; the drawer shows the totals.

**Source:** [[raw/tickets/NXT-15058|NXT-15058]]

---

## Q5 — A comment field appeared when I tried to Match. Do I have to fill it in?

Yes. A comment is required when you click Match on a Potential Match. This is the audit trail an auditor will look for if the certification is challenged later.

**Source:** [[raw/tickets/NXT-15058|NXT-15058]]

---

## Q6 — I fixed a student's name in Account Management — do I need to re-upload the DC file?

No. The system re-runs DC matching automatically when a student record is updated through Account Management. If the corrected record now scores high enough against an existing DC file, it appears in the queue without any re-import.

**Source:** [[raw/tickets/NXT-14223|NXT-14223]]

---

## Q7 — Can I see exactly why an auto-matched student was matched?

Yes. Open the student from either the Matched tab or the File Details → Students section; both surface the same scorecard.

**Source:** [[raw/tickets/NXT-13343|NXT-13343]]

---

## Q8 — My DC Counts report needs more than one site. Is that possible?

Yes. Site Code and Site Name are multi-select on the DC Counts report. Pick all the sites you need on a single run.

**Source:** [[raw/tickets/NXT-63982|NXT-63982]]

---

## Q9 — A trainer's bookmark to the "By Direct Certification" report 404s. What changed?

The report was migrated from Dundas to native HTML. All options and parameters are unchanged, but the URL is different. Update the bookmark from the Eligibility → Reports page.

**Source:** [[raw/tickets/NXT-21564|NXT-21564]]

---

## Q10 — I want to pull DC data into a custom report. What's available?

The "Elig - Direct Cert" dataset is available in Custom Reports. It includes Student ID, names, File #, Academic Year, Import/Processed/Notification/Approval/Eligibility Start & End Dates, DC Type, Match Method, Entry Method, current and prior eligibility, household info, and Case Number — among others.

**Source:** [[raw/tickets/NXT-58224|NXT-58224]]
