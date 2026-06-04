---
name: project-item-management-patterns
description: Epic-to-feature mapping, ticket patterns, and structural notes for Item Management module transcripts
metadata:
  type: project
---

## Key Epics for Item Management — Creating Items

| Epic | Key Focus Area |
|---|---|
| NXT-36067 | IM - Item Units & Sub-types (2023 redesign: combined pack/serving grid, base unit, inventory readiness) |
| NXT-45562 | IM - Units Card Overhaul (dual units, merge logic, editability rules, banners) |
| NXT-30027 | IM - Item Details Overhaul (item card, nutrient info, contributions, allergens, POS) |
| NXT-26823 | IM - Item Type Consolidation - Recipe Rework (HACCP, recipe steps, control points) |
| NXT-29833 | IM - Menu & POS Consolidation (menu info tab, POS pricing, DMI flow) |
| NXT-40487 | IM - Production Usability Enhancements 2023 (images & docs, allergen card redesign, nutrient details) |
| NXT-40775 | IM/INV - Business Rule & Validation Enhancements (inventory eligibility locking) |
| NXT-51260 | IM - Usability & UX Enhancements 8.X (taxable on adults only, contributions redesign) |
| NXT-13780 | IM - UI Improvements (custom allergen configuration) |
| NXT-37500 | IM - Consolidation Enhancement & Cleanup (inventory info tab contract preview) |

## Ticket Patterns Observed

- Item card fields (description, category, storage, valuation group) → no single dedicated story; covered in NXT-30036/NXT-30037 (Item Details Overhaul). AC is minimal — mostly covered by Description.
- Pack sizes and Higher/Lower prompt → NXT-37110 (AC: confirmed)
- Serving sizes (food only) → NXT-35898 (AC: confirmed)
- Link servings to packs (inventory eligibility) → NXT-37441 (AC: confirmed)
- Costing / Missing Costing alert → NXT-37568 (AC: confirmed)
- Unit identifiers (P, BU, MI badges) → NXT-37109 (AC: confirmed)
- Base unit auto-assign → NXT-37111 (AC: confirmed)
- Dual unit / Base Unit promotion → NXT-40778 (AC: confirmed)
- Whole Numbers / Decimals → NXT-33518 (AC: confirmed)
- GTIN/UPC → NXT-37815 (AC: confirmed)
- Images & Documents → NXT-41273 (AC: confirmed; RN: External/Internal — good content source)
- Nutrient Details (fields, Missing Value checkbox) → NXT-43239 (AC: confirmed; RN: External/Internal)
- Ingredient Info (edible yield, sub-ingredients, buy American, locally grown) → NXT-30100 (AC: minimal); Yield Factor moved to Units per NXT-47249
- Contribution Info (meal pattern) → NXT-30102 + NXT-37216 (AC: minimal; no RN text)
- Allergen Info (standard allergens, disclaimer) → NXT-30103 + NXT-41275 (AC: confirmed)
- Custom Allergens (configuration page) → NXT-24128 (AC: detailed)
- Menu Info / Direct Menu Item creation → NXT-39594 (AC: minimal; show-on-POS confirmed)
- Menu Item fields (name, button name, category, max days, etc.) → NXT-30155 / NXT-30037
- Menu Item Serving + add more servings → NXT-40447 (AC: confirmed)
- Menu Item Serving Exceptions → NXT-54229 (AC: mentions Exceptions availability rule); no dedicated exceptions story found
- POS Pricing (student/adult grid, Set All Prices) → NXT-30155 (AC: confirmed Set All Prices); Taxable checkbox (Adults tab only) → NXT-58442 (AC: confirmed; epic NXT-51260)
- HACCP / Steps card / Control Points → NXT-36583 + NXT-36742 (AC: confirmed)
- Inventory Info tab (vendor contracts) → NXT-40479 (AC: confirmed)

## Unmatched Pattern Types

- Contribution Info (Meat/Meat Alt, Grains, etc. — USDA meal pattern fields): multiple match attempts returned 0 results. The feature is visible in NXT-30102 description only (not AC). Use lowest trust; flag as AC-empty in metadata.
- "Three tier maximum" hard cap: mentioned by presenter but not found as a dedicated story. Covered implicitly in NXT-37110 description language. Mark as unmatched (business rule not in a discrete ticket).
- Ingredient Info card Yield Factor discrepancy: NXT-47249 AC explicitly removes Yield Factor from Ingredient Info and moves it to Units card. If a presenter describes Yield Factor on Ingredient Info, flag as outdated presenter information. Verified on 2026-05-29.
- Costing auto-scaling (divide-down cost calculation): no dedicated story. Part of NXT-37568 description logic. AC does not describe the calculation formula.
- Menu Item Serving Exceptions (not-served by school level): no dedicated story found. Cross-referenced in bugs (NXT-60473) but no story AC available.
- "Sub-quantity must be standard pack size, not short-ship" → business guidance, not a ticket.

## Cross-Module Patterns

- Inventory receiving / vendor contracts → Inventory module (Justin, Inventory PM)
- Recipes (item used as recipe ingredient) → Recipes module
- Menu Planning (nutrients feed menu analysis) → Menu Planning module
- Family Hub (parent-facing menu display) → Family Hub / parent portal module
- PrimeroEdge legacy references → legacy system, not SchoolCafe 2.0

**Why:** Saves repeated Jira queries on subsequent Item Management transcripts.
**How to apply:** When mapping a new Item Management transcript, check this pattern list before running Jira match calls — use direct `ticket` lookups on confirmed IDs instead of re-running match.
