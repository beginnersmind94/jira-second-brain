---
name: project-item-management-module
description: Planning notes for Item Management module — presenter signals, confidence flags, and sourcing risks carried across all three template types
metadata:
  type: project
---

Item Management content planning is active as of 2026-05-29. Source transcript: REC-2026-0515-IM-001, presenter Sarah Chen (Implementation Specialist), audience Brunswick County Schools onboarding cohort.

**Why:** End-to-end 3-template test (long-form, micro, TLDR) using the same mapper inventory.

**Key planning signals to apply across all three templates:**

- Highest-priority feature: Serving↔Pack linking (NXT-37441, priority = Highest) — never omit from any template.
- Three presenter-uncertain items must be excluded from all templates: bulk allergen import, copy item, catalog/corporate DB import.
- Roles & permissions: NOT demonstrated in transcript. Source = NXT-53316 AC only. NXT-53316 Description is TIER 3 — never cite as AC.
- Edible Yield Factor placement: [AMBIGUOUS] — NXT-47249 AC says Units card; presenter showed Ingredient Info tab. Flag in all templates.
- Contribution Info field names: Description-tier only (NXT-30102 + NXT-37216). All field names = [TO VERIFY] in all templates.
- Serving Exceptions (feature #30): no dedicated story AC. NXT-54229 covers lock behavior, not exceptions UI. Field names = [TO VERIFY].
- Sales tax rate config (feature #34 / NXT-58442): presenter uncertain. Include Taxable checkbox but mark rate config [TO VERIFY].
- Custom Allergens prerequisite: must be set up in Configuration BEFORE adding to items. This is a hard prerequisite, not a workflow step.

**How to apply:** Reference these signals for micro and TLDR planning to ensure consistent sourcing decisions across all three template outputs for this module.

**Long-form plan status (2026-05-29):** Complete. 10 sections planned, 11 workflow subsections in Section 4, 39 features mapped, 10 SME must-handle items (D1–D10) inventoried. D1 (Yield Factor) and D2 (Vitamin A/C) are must-resolve before Writer proceeds. D3–D10 can be marked `[TO VERIFY]` in draft. Plan written to `logs/20260529-pipeline/plan-long-form.md`.
