---
name: project_item-management-micro-guide-2026-05-29
description: Content plan decisions for Item Management micro guide, 2026-05-29 — 4 workflows selected, SME discrepancies resolved, Writer-ready
metadata:
  type: project
---

Micro guide content plan completed 2026-05-29 for the Item Management module, Brunswick County Schools onboarding cohort. Full plan at `logs/20260529-pipeline/plan-micro-guide.md`.

**4 workflows selected (within ≤5 limit):**
1. Create a non-food item (item card through Inventory Readiness) — NXT-30036/30037/35898/37110/37568/37111/53530
2. Create a food item through Inventory Eligibility (includes serving↔pack link) — NXT-35898/37110/37441(Highest)/37111/40778/53530/37568
3. Set up Menu Info and POS Pricing — NXT-39594/30155/58442/40447
4. Configure allergens (standard + custom) — NXT-30103/41275/24128

**Why costing is embedded (not standalone):** Costing (NXT-37568) is an optional step within both Workflow 1 and 2 — entering cost for one unit causes the system to scale to others. No standalone workflow slot. [[feedback_costing-as-embedded-step]]

**Why NXT-37441 (Highest priority) is embedded:** Serving↔pack Sub-Qty link cannot be performed without the surrounding food item pack/serving setup. Embedded as the pivotal step in Workflow 2. [[feedback_highest-priority-as-embedded-step]]

**Key omissions:**
- HACCP/Steps (NXT-36583/36742): food-only, Nutrition Manager, complex — recommend dedicated guide or long-form
- Menu Serving Exceptions (NXT-54229): no AC for UI steps — [TO VERIFY], omit until SME confirms
- Edible Yield Factor (NXT-47249): DISCREPANCY D1 HIGH — presenter described Ingredient Info card location but NXT-47249 Done Done moved it to Units card. Omit from micro; requires product team confirmation before long-form.
- Contribution Info (NXT-30102/37216): field names Description-only; Nutrition Manager only; one-line mention

**SME discrepancies carried to Writer:**
- D1 (HIGH): Yield Factor location — omit from micro entirely
- D2 (MEDIUM): "Merge" not "promote" — Writer uses AC term
- D3 (LOW): 10-file limit only from RN; 5 MB and file type list are [TO VERIFY]

**Word budget:** ~1,300 estimated; target 600–1,200, ceiling 1,500. No long-form flag needed.

**How to apply:** These 4 workflows are the stable core of this module for any onboarding guide. Long-form adds HACCP/Steps, Contribution Info (after SME verification), Edible Yield Factor (after D1 resolved), and Menu Serving Exceptions (after AC confirmed).
