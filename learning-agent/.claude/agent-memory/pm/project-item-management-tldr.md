---
name: project-item-management-tldr
description: TLDR one-pager content plan for Item Management module — 39 features merged to 25 rows, 5 gotchas, 685-word density estimate, [TO VERIFY] catalog
metadata:
  type: project
---

TLDR plan for Item Management completed 2026-05-29. Plan written to `logs/20260529-pipeline/plan-tldr.md`.

**Why:** TLDR hard constraint is one page with all features present. 39 mapper features compressed to 25 Key Features table rows via documented merge rules; all features preserved by name within merged sentences.

**How to apply:** For future TLDR plans on feature-rich modules (20+ features), run a merge pass before writing the plan. Target: features that are sub-fields of the same card or sequential steps in one workflow can share a row if the sentence names all constituent features. Stop merging when further consolidation would hide a feature name. Budget ~685 words for 25-row table + 5 other sections — this is at the upper edge of safe range for one dense HTML page.

Key merge decisions (39 → 25):
- Item card creation + all Item card optional fields → 1 row
- Item Category + Storage Category + Valuation Group → 1 row (three-dropdown step)
- Food/Non-Food + Fluid/Non-Fluid → 1 row (both Units-card header questions)
- Pack sizes + 3-tier max → 1 row (cap is a property of entry)
- Unit Identifiers (P/BU/MI badges) + Base Unit auto-assign → 1 row (read-only outputs of same save)
- Missing Costing alert + Manage Costing button + auto-calculation → 1 row (two states of same prompt)
- Inventory Ready flag + Publish toggle auto-enable → 1 row (fire together)
- GTIN/UPC + barcode icons → 1 row (icon is direct result of GTIN entry)
- Yield Factor (Units card, per-serving) + Ingredient Info card sub-fields → 1 row (adjacent cards; Yield Factor confirmed moved to Units per NXT-47249 D1)
- Menu Info tab Direct Menu Item creation + Show on POS toggle → 1 row (sequential steps on same tab)
- Menu Item Serving + Menu Item Serving Exceptions → 1 row (both Actions on Units card once Menu Item)
- Steps/HACCP + Control Points (CCPs) → 1 row (two phases of one Steps-card workflow)
- POS Pricing Students grid + Adults tab + Set All Prices + Taxable → 1 row (same tab, two sub-tabs)
- Nutrient Info oz-to-grams conversion folded into Nutrient Details row

Standalone rows kept for: Whole Numbers/Decimals (lifetime lock behavior), Serving sizes (highest priority NXT-37441), Serving-to-pack link (Highest priority, prerequisite for Inventory), Base Unit Merge/promotion (distinct AC), Images & Docs (RN-visible), Nutrient Details (RN-visible), Contribution Info, Allergen Info, Custom Allergen config, Menu Item fields (separate from tab creation), Inventory Info tab, Editability locking.

Gotcha selection (5 cross-cutting):
1. Add all pack sizes BEFORE entering costing — transcript [05:18]
2. Serving must be linked to pack via Sub-Qty for Inventory eligibility — NXT-37441 AC
3. Base Unit + Decimals lock after first Inventory transaction — NXT-54229 AC + transcript [37:35]
4. Custom allergens must be created in Configuration before they appear on items — NXT-24128 AC
5. Discrepancy D1: Yield Factor moved from Ingredient Info to Units card per NXT-47249 Done-Done

Density: 685 words (~25 rows × 12 avg + 5 sections). Upper edge of safe range. Compression levers documented in plan if Writer reports overflow: shorten table sentences first; never drop rows.

16 [TO VERIFY] items catalogued in plan. Ambiguous A1 (custom allergen Family Hub toggle) excluded.

[[feedback-tldr-compression]]
