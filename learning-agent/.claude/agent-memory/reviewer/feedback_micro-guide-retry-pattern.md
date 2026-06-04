---
name: feedback_micro-guide-retry-pattern
description: Micro-guide retry 1 succeeded after Writer fixed word count and a single bad AC citation (NXT-39594 V27 misclassification). Pattern: micro-guide failures tend to be one-fix retries if the root cause is a single mis-attributed citation or a single extra section.
metadata:
  type: feedback
---

The item-management micro-guide failed retry 0 on two issues: word count (1,890 words > 1,500 ceiling) and one Description-tier quote labeled AC (NXT-39594 "Show on POS toggle" behavior attributed to AC when it was Description only — the V27 misclassification).

Retry 1 passed at 1,198 words with the citation corrected to NXT-30155 AC + transcript [27:12].

**Why:** The retry was clean because the failure was narrow and precisely diagnosed. The Writer received a specific fix instruction: remove extra h2 section, compress to ≤1,500 words, correct NXT-39594 to cite only "Create a Menu Item tab".

**How to apply:** When routing a micro-guide FAIL to Task 4 (Writer), always specify:
1. Exact word count measured and target
2. Exact section(s) to remove or collapse (not "shorten the guide")
3. Exact citation correction with the correct ticket + field + verbatim quote

**Minor residual defect** (non-blocking): GTIN/UPC (M6) one-liner silently dropped from Related content. At 1,198 words there was budget for it. Flag in future micro-guide reviews — silently dropped demoted mentions should appear as non-blocking notes, not hard fails, when word count is already under ceiling.

**HTML authoring note:** Retry 1 introduced a malformed closing tag: `<code>CREATE MENU ITEM<\code>` (backslash). Not a content/citation issue but should be flagged to Writer as a cosmetic defect.
