---
id: elig-dc-file-import
title: "Direct Certification — Import a State DC File"
platform: schoolcafe
module: Eligibility
page: "Direct Certification — File Import"
content_type: micro-guide
roles: ["manager"]
tags: ["frequency:monthly","compliance","onboarding"]
status: draft
template: micro-guide
source_refs:
  - "wiki/workflows/direct-certification.md"
  - "raw/tickets/NXT-15058.md"
  - "raw/tickets/NXT-58224.md"
  - "raw/tickets/NXT-60922.md"
  - "raw/tickets/NXT-14223.md"
updated: 2026-05-13
---

# Import a State DC File — Micro Guide

> **You'll be able to:** upload your state's Direct Certification file and confirm the system finished processing it before you walk away.
> **Audience:** Child-nutrition manager (district).
> **Time:** 5 minutes.

## Before you start

- You have the DC file from your state agency, saved locally with the original filename.
- Your account has permission to import into Eligibility → Direct Certification.
- You know the academic year the file is for. The Import Date is recorded automatically. Source: [[raw/tickets/NXT-58224|NXT-58224]].

## Steps

1. **Navigate to Eligibility → Direct Certification → File Import.**
2. **Upload the file.** Select the state's file from your computer and submit.
3. **Wait for Processing.** The page shows the file in a Processing state. When it finishes, **Processed Date** is set on the file record. Source: [[raw/tickets/NXT-58224|NXT-58224]].
4. **Read the summary.** Note the counts for Matched and Potential Matches.
5. **Hand off the queue.** Tell your reviewer that Potential Matches is ready to work. The daily-review SOP covers that part.

## If it goes wrong

- **File upload rejected →** wrong file format or wrong academic year on the header. Get the original file from your state portal again; do not re-save it through Excel (Excel rewrites dates and IDs).
- **Match count looks way too low →** the file may be a delta (changes only) instead of a full file, or student IDs in SchoolCafe don't match the state's. Open the Potential Matches drawer on a few rows and check the scorecard for which categories scored zero — Personal / Contact / ID Numbers. Source: [[raw/tickets/NXT-15058|NXT-15058]].
- **A student you expected to match isn't there at all →** their roster record may have been wrong at the moment of import. Fix the student in Account Management; secondary matching will recheck them against the existing file with no re-upload. Source: [[raw/tickets/NXT-14223|NXT-14223]].
- **You meant to manually certify one student, not import a file →** Manual Entry's entry-method dropdown does **not** include Direct Certification by design. File Import is the only DC-entry path. Source: [[raw/tickets/NXT-60922|NXT-60922]].

## Sources

- [[wiki/workflows/direct-certification.md]]
- [[raw/tickets/NXT-15058.md|NXT-15058]]
- [[raw/tickets/NXT-58224.md|NXT-58224]]
- [[raw/tickets/NXT-60922.md|NXT-60922]]
- [[raw/tickets/NXT-14223.md|NXT-14223]]
