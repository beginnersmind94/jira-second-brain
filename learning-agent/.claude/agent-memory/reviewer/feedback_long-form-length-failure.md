---
name: feedback_long-form-length-failure
description: Long-form Writer consistently over-generates — first attempt at 20260529 item-management draft produced 9,426 words against a 6,000-word ceiling (57% over). Compression on retry 1 succeeded: 5,983 words. Route to Task 4 with explicit compress budget.
metadata:
  type: feedback
---

The Writer over-generated on the first long-form draft by a wide margin: 9,426 visible words vs. the 6,000-word hard ceiling stated in the template spec.

**Why:** The Writer followed the plan's section-by-section depth instructions faithfully but did not apply any length budget per section. With 11 workflow subsections, 5+ reference tables, 13 exception items, and 8 troubleshooting items, prose accumulates past ceiling even when each section looks reasonable in isolation.

**How to apply:** When routing a long-form FAIL back to Task 4, always include an explicit compress budget: estimate ~545 words per section across 11 subsections (Full Workflows is the biggest target — trim step-by-step prose, collapse cross-references, reduce table rows to only AC-confirmed fields). Do not ask the Writer to cut features — cut prose density instead. Structural tables (Key Fields, Sources) are not the primary offenders; workflow steps are.

**Pattern to watch:** The Exceptions section (14 items) and Key Fields tables (~6 tables) together account for ~2,500 words. These are candidates for consolidation without feature loss.

**Retry 1 outcome (2026-05-29):** Compression to 5,983 words succeeded. Plan alignment and source grounding held — no features dropped, all 3 discrepancy callouts preserved, all 29 tickets cited, NXT-39594 citation fix correctly applied. Compress-only routing works; the Writer does not need a full re-plan to hit the ceiling.
