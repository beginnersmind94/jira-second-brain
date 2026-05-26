---
id: GUIDE-026
title: "Charge Limits Quick Guide"
platform: "SC"
module: "Accountability"
content_type: "Quick Guide"
source_url: "https://s3.us-east-1.amazonaws.com/docs.schoolcafe.com/Accountability/Charge_Limits_Quick_Guide.pdf"
local_pdf: "raw/guides/pdf/SC/Accountability/Quick-Guide/GUIDE-026-charge-limits-quick-guide.pdf"
curated_against_raw_sha: "2fbd728e242d85ff"
curated_against_raw_at: "2026-05-18T20:39:40+00:00"
last_reviewed_by: ""
status: "needs_initial_review"
---

# Charge Limits Quick Guide

> Seeded from the raw extraction. Edit freely. When the raw drifts, review the diff and update this file, then mark it reviewed with `python scripts/mark_guide_reviewed.py GUIDE-026`.

Charge Limits allow users to set negative balance limits for all students and adults of specific Eligibility Types, Site Types, or Grade Groups for meals and a la carte purchases. Charge Limits will restrict the patron from making a purchase in the POS application beyond the set dollar amount.

## Edit Charge Limits
<!-- Source: NXT-54168 (resolved 2024-09-20).
     AC verbatim: "User is informed if no charge limit exists / blank"; "Text: No Charge Limit"; "POS updated to treat charge limits not existing as a blank value. (no charge limit)".
     RN verbatim: "We have updated the Charge Limits configuration page to clearly show when no charge limit has been set. Previously there was some ambiguity here; the text update is aimed to remove that."
     Open: AC does not state how a $0.00 entry differs from a blank value; an earlier draft included that contrast as interpretation and it has been removed. -->
If no charge limit has been set (the field is blank), the page now displays the text "No Charge Limit". The POS treats a charge limit that does not exist as a blank value (no charge limit).
1. Ensure that the CHARGE LIMITS tab is selected
2. Click the Edit icon for a desired patron/Meal Type and Site Type
3. Enter the dollar amount for each Eligibility Type/Adult Type as needed
   Entering a positive number equates to a negative value.
   Values for any Charge Limit (student or adult) must be between $0.00 and $9,999.99.
4. Click the Checkmark to save the entered value or click X to cancel
   A confirmation response appears atop the page, and the dollar amount is changed.
   Repeat this process to change additional patrons/Meal Types, and Site Types Charge Limits as needed.
