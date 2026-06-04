---
name: feedback_nxt53316_ac_field_defect
description: Hard-fail rule — any quote labeled AC: that actually comes from the Description field is an automatic fail, route to Task 3 (SME)
metadata:
  type: feedback
---

A quote labeled `AC:` in a source comment that originates from the Description field (TIER 3) is a hard fail. This specific defect was first identified in a prior draft (NXT-53316 incident) and remains a standing auto-fail criterion.

**Why:** Description fields are TIER 3 — never citable as AC. Promotions of Description text to AC status in fact-check or drafts directly violate the anti-hallucination rules and can ship incorrect product behavior to staff.

**How to apply:** In every spot-check, pull the live AC field for each cited ticket. If the quoted string is absent from AC/RN and present only in Description, that is a hard fail → route to Task 3 (SME to re-verify and correct the fact-check entry). Do not waive even if the claim appears substantively accurate — the tier rule is absolute.

**First confirmed occurrence in this pipeline:** NXT-39594 — "a 'Show on POS' toggle will control the presence of the POS attributes and Pricing table" cited as `NXT-39594 AC (via factcheck V27)` but the AC for NXT-39594 contains only "Create a Menu Item tab." The Show on POS toggle language is in the Description field only.
