---
name: feedback-tldr-word-count-inflation
description: TLDR Writer consistently over-produces word count vs plan estimate; plan estimates are optimistic and actual drafts run ~2x planned words
metadata:
  type: feedback
---

The Writer's first TLDR draft (20260529-item-management-tldr-draft.html) came in at ~1,278 words against the plan's estimated ~685 words — nearly double the estimate. The plan even provided explicit compression levers and a hard "DO NOT drop rows" constraint, but the Writer inflated rows instead of compressing them.

**Why:** The Writer appears to treat the plan's per-row sentence guidance as a floor rather than a ceiling. Multi-clause sentences (using semicolons) are the primary inflation mechanism, pushing individual rows to 20–31 words against a 15-word cap.

**How to apply:** When reviewing TLDR drafts, independently count visible words (comments+tags stripped) before doing any other check. If count exceeds ~750 words, it is guaranteed to overflow one page — route immediately to Task 4 without waiting to complete the full rubric. Do not accept a "reads well" argument; one-page is a hard constraint.
