---
name: cross-module-bleed-item-management
description: Modules most likely to generate cross-module bleed during Item Management training, based on REC-2026-0515-IM-001. Inventory and Recipes/Menu Planning are the primary bleed sources.
metadata:
  type: project
---

Item Management training frequently bleeds into:

1. **Inventory** — Inventory Info tab, vendor contracts, receiving workflows, GTIN/UPC for receiving, Base Unit locking after first Inventory transaction, pallet/case receiving workarounds. Key signal: "Justin would know — he's the Inventory PM." Do not verify Inventory-side behavior under IM stories.

2. **Recipes / Menu Planning** — Serving sizes as ingredient basis, Sub Ingredients, Standard Recipe Directions on Ingredient Info card, nutrient data used in menu planning. NXT-47249 Yield Factor is now serving-specific explicitly to support recipe calculations — this is IM-owned but feeds Recipes.

3. **Family Hub** — Marketing Name & Description field on Menu Item, "Show on Family Hub menus" toggle on Custom Allergens (unsupported). [[unsupported-custom-allergen-family-hub-toggle]]

4. **POS (Point of Sale)** — Button Name (English/Spanish), POS Entree flag, Allow Sale toggle, reimbursable meal designation. These fields are configured in IM but consumed by POS.

5. **Production Records** — Max Days / Leftover Category on Menu Item card feed production records. Production is a separate module.

6. **PrimeroEdge (legacy)** — Presenter (Sarah) compared 2.0 to PrimeroEdge when uncertain about 2.0 features. Any PrimeroEdge comparison is legacy and must be excluded from 2.0 content.

**Why:** Item Management is the master data source for many downstream modules. Trainers naturally describe downstream effects. Cross-module references should get one line + link placeholder in published content, not deep-dives.

**How to apply:** When a presenter says "in Inventory..." or "on the menu..." or "for recipes...", flag as cross-module. Do not verify in IM tickets.
