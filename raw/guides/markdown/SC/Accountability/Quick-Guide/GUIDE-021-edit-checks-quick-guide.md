---
id: GUIDE-021
title: "Edit Checks Quick Guide"
platform: "SC"
module: "Accountability"
content_type: "Quick Guide"
source_url: "https://s3.us-east-1.amazonaws.com/docs.schoolcafe.com/Accountability/Edit_Checks_Quick_Guide.pdf"
local_pdf: "raw/guides/pdf/SC/Accountability/Quick-Guide/GUIDE-021-edit-checks-quick-guide.pdf"
curated_against_raw_sha: "40615453ee27432b"
curated_against_raw_at: "2026-05-18T20:39:39+00:00"
last_reviewed_by: ""
status: "needs_initial_review"
---

# Edit Checks Quick Guide

> Seeded from the raw extraction. Edit freely. When the raw drifts, review the diff and update this file, then mark it reviewed with `python scripts/mark_guide_reviewed.py GUIDE-021`.

The Edit Checks function allows district users to review the attendance factor compared to the meals served on a particular day. This review aims to verify and resolve discrepancies so the district does not overclaim any meals on their reimbursement claim.
The Attendance Factor must be configured correctly for the Edit Checks function to display the correct data.

## View Edit Checks
<!-- Source: NXT-58225 (resolved 2025-02-19).
     AC verbatim: "Date Picker updated to match the one on the FOH Dashboard"; "Site Picker swapped out for multi-select"; "Comments window changed to a side drawer"; "Sessions link added to Edit Checks result grid"; "Option to do Edit Checks vs Reverse Edit Checks added"; "Edit Checks is the default selection"; "User can go to the Sessions for the Site + Date in the grid".
     RN verbatim: "We have added an option to the Edit Checks page to allow for the configuration and searching of low meal counts. We're calling these Reverse Edit Checks." -->
An option to do Edit Checks vs. Reverse Edit Checks has been added, with Edit Checks as the default. The Date Picker has been updated to match the one on the FOH Dashboard, and the Site Picker has been swapped out for multi-select.
1. Select the Site Code/Site Name (multi-select)
2. Select the Date
3. Click the APPLY button
   Edit Checks display in the table below. The result grid now includes a Sessions link that lets the user go to the Sessions for the Site + Date.

## Resolve Edit Checks
1. Select a radio button to view one of the following:
- Unresolved – Edit Checks that require review
This is the default view.
- Resolved – Edit Checks that have been validated
- All – Displays both Unresolved and Resolved Edit Checks
2. Click the Resolve/Comment icon for the desired Edit Check
   <!-- Source: NXT-58225 (resolved 2025-02-19). AC verbatim: "Comments window changed to a side drawer". -->
   The Comments window — now a side drawer — displays.
3. Enter a comment into the field
4. Click the ADD COMMENT button to resolve the Edit Check
   A purple checkmark appears for a resolved Edit Check under the Resolved column.
   Click the Resolved or All radio buttons to view resolved Edit Checks.
   Repeat this process to resolve additional Edit Checks as needed.

<!-- Withdrawn: NXT-65306 (resolved 2025-10-29). AC field is "-" (empty) and Release Notes are blank for this ticket. Under the strict verbatim-quote standard, no proposal is permitted from Description alone. Flag for SME: the Description describes a new system setting ("Edit checks for daily attendance counts?") and new exception types on this page; if accurate, AC should be backfilled and the section re-proposed. -->

## View Comment History
1. Select a radio button to view one of the following:
- Resolved – Edit Checks that have been validated
- All – Displays both Unresolved and Resolved Edit Checks
2. Click the Resolve/Comment icon for the desired Resolved Edit Check
   The Edit Check Comments pop-up window displays.
3. View the Comment History
   Users can add additional comments as desired.
   Comments cannot be deleted.
   Click the CLOSE button to return to the Edit Checks page.
