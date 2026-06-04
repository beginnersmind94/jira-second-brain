---
name: project_item_management_pipeline
description: Active pipeline job for Item Management micro-guide (2026-05-29); current status, retry count, and blocking issues
metadata:
  type: project
---

Job: Item Management micro-guide, 2026-05-29 pipeline.

**Why:** Brunswick County Schools onboarding cohort; target audience District Admin + Nutrition Manager.

**Current status (after first review):** FAIL — 2 blocking issues:
1. TEMPLATE VIOLATION (route Task 4): word count ~1,890 vs 1,500 ceiling. Extra `<h2>` "Also in this module" is an 8th section not in the required 7. Must compress.
2. SOURCE GROUNDING FAIL (route Task 3): NXT-39594 "Show on POS toggle" quote labeled as `AC:` but it is in Description only (TIER 3). Factcheck V27 misclassified this. SME must re-verify NXT-39594 and correct the factcheck before Writer retries.

**Retry count:** 1 of 3 max.

**D1 (Edible Yield Factor):** Correctly omitted from draft. No action needed for this retry.
**D2 (Merge language):** Correctly handled — "Merge" used per AC.
**D3 (5 MB / file types):** Correctly [TO VERIFY]'d.

**How to apply:** On next review pass, verify (a) word count ≤1,500 and exactly 7 `<h2>` sections, (b) NXT-39594 Show on POS toggle cite corrected to `Description:` or replaced with a genuine AC quote, (c) the 4 workflows and 4 blockquote pitfalls are still intact after compression.
