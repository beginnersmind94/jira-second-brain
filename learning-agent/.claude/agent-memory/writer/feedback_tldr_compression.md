---
name: feedback-tldr-compression
description: TLDR compression rules — merge decisions and word economy techniques validated on Item Management (25 rows from 39 features)
metadata:
  type: feedback
---

Merge sub-fields onto a single row when they: (1) appear on the same card/tab, (2) form a single logical step for staff, or (3) one is a direct system output of the other. Keep all feature names present in the row sentence — merger means name appears in text, not that feature is dropped.

When row descriptions approach 15 words, cut trailing clauses rather than wrapper sentences. "Enter X; system does Y automatically." is better than "Enter X; the system will automatically calculate and apply Y across all tiers."

Gotcha bullets: lead with the consequence ("X locks after..."), not the context. Saves ~5 words per bullet.

Never drop rows, gotchas, or Where-to-go-next entries to recover space — compression must come from word count within rows. This is a hard template constraint.

**Why:** TLDR template requires completeness (omission implies feature does not exist) AND one-page constraint. These two constraints collide on feature-rich modules — compression within rows is the only valid escape valve. See [[feedback-tldr-patterns]] for CSS density settings.

**How to apply:** After drafting the table, do a pass trimming any row exceeding 15 words to ≤12 words. Check gotcha bullets: if any run over 30 words (excluding citation comment), cut the explanatory parenthetical.

**[TO VERIFY] placement rule (from Evaluator failure, retry 1 of 3, 2026-05-29):** NEVER place `[TO VERIFY]` markers in visible cell text on a TLDR one-pager. Move all `[TO VERIFY]` caveats into the row's HTML comment: e.g. `<!-- Source: NXT-#### Description (TIER 3) — label [TO VERIFY] before publish -->`. The visible cell shows only the user-facing description. A scan-speed one-pager with "[TO VERIFY]" scattered in rendered text fails the template. This is an Evaluator hard-block criterion.
