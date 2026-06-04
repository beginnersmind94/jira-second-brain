## Content Plan — Item Management — Micro Guide

### Template: Micro (~3 pages, 600–1,500 words hard ceiling)
### Source transcript: `raw/transcripts/20260529-070600-item-management-2026-05-28-item-management-create-items-training.md`
### Target audience: Brunswick County Schools onboarding cohort — implementation staff, nutrition directors, and site managers who must create and publish items before going live in Inventory, menus, and POS

---

### Workflow count: 4 (within the ≤5 hard limit — writer MUST NOT add a 5th)

The writer is explicitly bounded to the 4 workflows below. No additional workflows may be added. If content pressure builds, compress steps — do not overflow the workflow count or the 1,500-word ceiling.

---

### Include at full depth

| # | Feature / Workflow | Reason | Planned sections |
|---|---|---|---|
| 1 | Create a non-food item (Item card → Units/pack sizes → Costing → Publish) | Presenter's opening end-to-end demo (~10 min); simplest path; establishes shared concepts (Item card, Units card, costing, Inventory Ready) that food item workflow builds on. Tickets: NXT-30036/37110/37568/53530/37068. All High priority. | Purpose sentence → Steps (Item card fields, save, add pack tiers with Higher/Lower, costing one-unit entry + auto-scale, Inventory Ready + Publish toggle) → Pitfall: add ALL pack sizes before touching costing [05:45] |
| 2 | Create a food item through Inventory Eligibility (Food/Fluid selection → serving sizes → pack sizes → Serving↔Pack link → Costing → Base Unit promotion) | Presenter's second anchor demo; highest-priority ticket in inventory is NXT-37441 (Highest) — the Serving↔Pack link is unique to food items and breaks Inventory Eligibility if missed. Tickets: NXT-35898/37110/37441/37568/37111/40778. High + Highest. | Purpose sentence → Steps (FOOD + NON-FLUID/FLUID, add serving first, add pack sizes, link serving↔pack via Inventory Ready alert, costing, optional Base Unit promotion to serving size) → Pitfall: link servings to packs before saving — if skipped, Inventory Eligibility alert persists [15:02]–[15:42] |
| 3 | Make a food item a Direct Menu Item with POS Pricing (Menu Info → Show on POS → POS Pricing grid) | High-priority tickets NXT-39594/30155/58442; substantial transcript time [24:30]–[31:48]; day-one requirement for POS go-live; enables student + adult pricing and reimbursable meal designation (POS Entree checkbox). | Purpose sentence → Steps (MENU INFO tab → CREATE MENU ITEM, required fields: Menu Item Name / Button Name / Menu Item Category, POS Entree checkbox, Show on POS toggle, SAVE, POS PRICING tab → Student grid Set All Prices, Adults tab) → Pitfall: forgetting POS Entree checkbox — item won't count toward reimbursable meal if unchecked [26:48]–[27:12] |
| 4 | Set up allergens including custom allergens | Compliance-critical for school nutrition (attendee Tom explicitly raised it [21:42]); standard allergens Medium priority (NXT-30103/41275); custom allergen setup Medium priority (NXT-24128). Custom allergen requires a configuration step before the item-level step — that sequencing must be explicit. | Purpose sentence → Steps (NUTRIENT INFO tab → Allergen Info card → three-dot Edit → standard allergen status forms, plus ADD CUSTOM ALLERGEN → IF custom does not yet exist: IM > Configuration > Item Configuration > Custom Allergens > NEW → return to item and add) → Pitfall: custom allergen must be created in Configuration before it appears in the item's dropdown [23:10]–[23:55] |

---

### Mention briefly (1–2 sentences)

| # | Feature / Workflow | Reason |
|---|---|---|
| 1 | Nutrient Info — Nutrient Details card (USDA fields, Missing Value checkbox, Per-100g + %DV auto-calc) | High priority (NXT-43239); External/Internal RN visibility; compliance-adjacent. But data entry is mechanical — one sentence pointing users to the tab is enough; deep-dive belongs in long-form. |
| 2 | GTIN/UPC barcode entry (8–14 digits, optional) | Medium priority (NXT-37815); relevant only if district uses barcode scanners; one sentence: "Enter GTIN/UPC codes on the Units card if you use barcode scanners for receiving." |
| 3 | Whole Numbers vs. Decimals setting (locks once item used in Inventory) | Low priority ticket (NXT-33518) but has a hard lock consequence (NXT-54229 + NXT-16 lock behavior). One sentence in the Common Mistakes section is more appropriate than a full workflow. |
| 4 | Images & Documents card (5 MB/file; Use As dropdown; food + non-food) | Medium priority (NXT-41273); applicable to both item types; self-explanatory for most staff. One sentence: "Upload product images and documents via the Images & Docs card (5 MB per file max); use the 'Use As' dropdown to designate the Preferred Inventory Image." |
| 5 | Inventory-eligibility lock behavior (Base Unit + Decimals lock post-use) | High priority (NXT-54229/NXT-16); lock is permanent and painful to undo. Mention in Common Mistakes with timestamp [37:35]–[38:05] — "finalize Base Unit and Whole/Decimal setting before the item is used in any Inventory transaction." |
| 6 | Menu Item Serving — scaled servings and MENU SERVING button | Medium priority (NXT-40447); one line after the Direct Menu Item workflow: "To add additional serving sizes for the menu item, return to the Units card and click plus MENU SERVING." |

---

### Omit

| # | Feature / Workflow | Reason for omission |
|---|---|---|
| 1 | HACCP / Steps — Enable Recipe + HACCP Process (Step 0) + Add Recipe Steps + Control Points | High priority tickets (NXT-36583/36742) but narrowly scoped to users who configure food safety workflows; not a day-one item-creation task for onboarding staff. Micro guide is task-success for item creation, not food safety process setup. Include in long-form. |
| 2 | Menu Item Serving Exceptions (NOT SERVED by group) | High priority ticket (NXT-54229) but no dedicated story AC — mapper flagged [TO VERIFY] on field names. Risk of publishing unverified content. Also a specialized use case (per-group service restrictions) not relevant to all onboarding staff. Long-form only. |
| 3 | Nutrient Info — full field-by-field entry (Calories, Fat, etc.) | High priority (NXT-43239) but step-by-step nutrient entry is too granular for a micro guide (~20 fields). Covered by mention of Nutrient Info card. Full entry instructions belong in long-form. |
| 4 | Ingredient Info — Edible Yield Factor | Medium priority (NXT-47249/30100); mapper flagged version conflict [AMBIGUOUS] on UI placement. Do not include in micro guide until SME resolves the placement discrepancy. |
| 5 | Ingredient Info — Sub Ingredients + Standard Recipe Directions | Low priority (NXT-30100); cross-module relevance (recipes). One-line cross-module reference in Related Content is sufficient. |
| 6 | Ingredient Info — Locally Grown + Buy American | Low priority (NXT-30100); compliance niche; exemption letter logic is complex. Long-form only. |
| 7 | Contribution Info — Meal Pattern contribution | Weakest grounding: Low mapper confidence, field names from Description only, marked [TO VERIFY]. Do not include in micro guide until SME verifies field names against current UI. |
| 8 | Inventory Info tab — vendor contract display (read-only) | Low priority (NXT-40479); read-only; contracts are managed in Inventory module, not here. Cross-module reference in Related Content. |
| 9 | Unit identifiers column (P / BU / MI badges) | Medium priority (NXT-37109); visual/reference detail embedded in the item creation workflows. Mentioned implicitly when Inventory Ready and Base Unit steps are described. No standalone treatment needed. |
| 10 | Three-tier maximum pack size limit (behavioral cap) | Embedded as a natural consequence in Workflow 1 steps ("the plus PACK button grays out after three tiers" [07:05]). Not a separate workflow. |
| 11 | Bulk allergen import | Presenter-uncertain [24:02]–[24:30]; mapper explicitly flags as exclude. Not included. |
| 12 | Copy item feature | Presenter-uncertain [33:11]–[33:35]; NXT-56820 bug unresolved; mapper flags as exclude. Not included. |
| 13 | Catalog/corporate DB item import | Presenter-uncertain [34:00]; mapper flags as exclude. Not included. |
| 14 | 4th-tier receiving workaround | Cross-module (Inventory) + presenter-uncertain [36:48]–[37:00]; mapper flags as exclude. Not included. |
| 15 | Sales tax rate configuration | Presenter-uncertain [31:20]–[31:48]; scoped to business office; mapper flags as exclude. Not included. |
| 16 | Allergen Feature Disclaimer (display text only) | Medium priority (NXT-30103); one sentence within the allergen workflow steps is enough — "Read and acknowledge the Allergen Feature Disclaimer before configuring allergen status" [22:20]–[22:42]. Not a standalone section. |

---

### Common mistakes section — 4 pitfalls from transcript (aggregated, not per-workflow)

These appear in the dedicated "Common mistakes" section of the micro guide. Each must cite a transcript timestamp.

1. **Fixing costing before all pack sizes are added** — the system shows a Missing Costing alert as soon as the first pack is saved; do not click it until all tiers are in place. [05:45]–[05:55] (NXT-37568 description note)
2. **Skipping the Serving↔Pack link on food items** — the Inventory Ready alert will not clear and the item cannot be published to Inventory until servings and packs are numerically connected. [15:02]–[15:42] (NXT-37441)
3. **Not setting Base Unit and Whole/Decimal before first Inventory transaction** — both settings lock permanently once the item is used in any Inventory count, receipt, or adjustment. [37:35]–[38:05] (NXT-54229)
4. **Leaving the POS Entree checkbox unchecked on reimbursable items** — item will appear on POS but will not count toward a reimbursable meal; cashiers will see it as an a la carte item. [26:48]–[27:12] (NXT-39594)

---

### Section order

1. **Purpose** — one paragraph framing the outcome: "After reading this guide, you can create a non-food item, create a food item with Inventory Eligibility, configure allergens, and set up a Direct Menu Item with POS pricing."
2. **Who this is for** — nutrition directors, site managers, and implementation staff responsible for item setup in Brunswick County Schools' SchoolCafé 2.0 environment.
3. **Before you start** — prerequisites: login credentials active (Jaime's team [00:28]); Item Category / Storage Category / Valuation Group values agreed with district (recommended even if not using Inventory [02:22]–[02:50]); for allergen setup: custom allergens configured in IM > Configuration before item-level work [23:28]–[23:55]; for food items: nutrition label on hand [19:12]; for POS Pricing: district price schedule confirmed [30:15].
4. **Top workflows** — 4 subsections in this order: (1) Create a non-food item, (2) Create a food item through Inventory Eligibility, (3) Make a food item a Direct Menu Item with POS Pricing, (4) Set up allergens including custom allergens.
5. **Common mistakes** — 4 bullets as listed above.
6. **Related content** — Inventory module (for vendor contracts, receiving, and pack size lock behavior); Recipes module (for Sub Ingredients and serving size usage in recipes); Menu Planning module (for nutrient analysis and menu grids); Family Hub (for Marketing Name and Description display) — all as one-line link placeholders.
7. **Sources** — all ticket IDs cited, transcript timestamps cited per the inline source comment rules.

---

### PM planning notes (not for writer)

- **Why costing is NOT a standalone workflow:** Costing is an embedded step within both the non-food and food item creation workflows. Users encounter it in sequence after adding pack sizes — it is not independently initiated. Separating it into a fifth workflow would require repeating context already established in workflows 1 and 2, wasting word budget. The costing pitfall (common mistake #1) surfaces the most important behavioral detail.
- **Why Serving↔Pack link (NXT-37441, Highest) is workflow 2, not its own workflow:** The link cannot be performed without first setting up serving sizes and pack sizes; it is a required mid-workflow step, not an independent task. Embedding it in workflow 2 with its own pitfall callout gives it appropriate prominence without creating an artificial workflow split.
- **Allergens placed 4th, not 3rd:** Direct Menu Item + POS Pricing (#3) is higher combined priority (High tickets, POS go-live dependency). Allergens (#4) are Medium priority and compliance-driven. Either order is defensible but POS pricing is the harder blocker for day-one operations.
- **Template constraint confirmed:** 4 workflows ≤ 5-workflow hard limit. Estimated word count for 4 workflows at micro-guide depth is 800–1,100 words — within the 1,500-word ceiling.

---

### Handoff checklist

- [x] Mapper inventory reviewed (35 matched features, 13 unmatched/excluded cataloged)
- [x] Template constraints checked (≤5 workflows: 4 selected; word budget: estimated 800–1,100 words)
- [x] Omitted features documented with explicit reasons
- [x] Presenter-uncertain items confirmed excluded (bulk allergen import, copy item, catalog import, sales tax rate)
- [x] Cross-module references routed to Related Content, not deep-dived
- [x] [TO VERIFY] and [AMBIGUOUS] items (Contribution Info, Edible Yield Factor, Menu Serving Exceptions) excluded from micro guide pending SME resolution
- [ ] SME fact-check can proceed — priority items for SME: NXT-37441 Serving↔Pack link steps; NXT-39594 POS Entree checkbox behavior; NXT-30103 custom allergen Configuration path; NXT-37568 costing one-unit-only constraint
- [ ] Writer has enough to generate — 4 workflows, 4 common mistakes, 6 brief-mention items, section order, prerequisite sources all specified
