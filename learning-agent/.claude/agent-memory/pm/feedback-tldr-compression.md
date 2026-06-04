---
name: feedback-tldr-compression
description: TLDR planning rule — merge sub-behaviors into shared rows to hit one-page constraint without dropping features
metadata:
  type: feedback
---

For TLDR one-pagers with 20+ features, the writer's primary risk is overflow — not omission. The content plan must do the compression work, not leave it to the writer.

**Why:** A TLDR requires all features present AND one page. These two constraints are in tension above ~20 features. If the plan does not specify merge rules, the writer either overflows the page or silently drops features — both are failures.

**How to apply:** In the content plan, run an explicit merge pass on the mapper inventory. Document which features consolidate into which rows and why. Give the writer the final row count and a page-budget estimate. Target ≤25 rows for a 6-section TLDR at standard HTML density (~700 words/page). Merge criteria: sub-fields of the same card, sequential steps of the same workflow, or one feature that is a direct property/constraint of another. Never merge features from different cards or different user decisions into one row — that hides the feature.

[[project-item-management-tldr]]
