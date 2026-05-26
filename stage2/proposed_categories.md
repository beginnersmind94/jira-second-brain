# Proposed categories — IM Bugs + Stories (Stage 2 / Workstream 1.1)

_Generated from a 200-ticket stratified sample (120 Bugs + 80 Stories, 103 distinct sprint values). Bottom-up reading; categories describe the **problem space**, not the work type — each is meant to catch both Bugs and Stories that share a customer-impact theme._

**11 proposed categories.** All are intended to be type-agnostic. `Other` is implicit and reserved for tickets that don't fit any of these.

This file is the gate for Step 1.2 (Rahul checkpoint). Don't proceed to top-down tagging until the list is curated.

---

## How to read this file

For each category:

- **Name** — short, problem-space label.
- **Definition** — one paragraph. What's in. What's adjacent but excluded.
- **Bug shape** — what a typical Bug in this category looks like.
- **Story shape** — what a typical Story in this category looks like.
- **Example tickets** — 4–6 from the sample, mixed Bug + Story, mixed Epics where possible.
- **Notes** — anything Rahul should weigh when curating.

Sample size in each category is rough — these are observations from the 200-ticket read, not a tagging pass. Volumes will firm up after Step 1.3.

---

## 1. Item Onboarding & Bulk Tools

**Definition.** Anything that happens inside the Bulk Item / Item Onboarding tool: the multi-step wizards (Initial Info → Pack Size → Menu Item → Nutrients → Contributions → Allergens → Review → Publish), the Excel import/export flows, file upload validation, autosave, the bulk-update workflows for nutrients/vitamins/serving info, the per-section "complete/incomplete" status logic, the publish-to-local mechanic. Excludes: the underlying nutrient/contribution data model itself (that's #4), and Excel reports that aren't part of onboarding (that's #8).

**Bug shape.** "Status icon shows wrong state on Review page", "500 error on Save Weights", "Auto-save fires before user changes anything", "Section shows complete when user unselected it", "Filter dropdown doesn't deselect".

**Story shape.** "Add Special Permission gating", "Bulk Apply for column-level multi-select", "Provide Check Updates step", "Excel column header changes for clarity", "Review Menu Item Info page", "Bulk Item - Update Nutrients single-item slideout".

**Example tickets.**
- `NXT-62688` (Bug) — Multiple issues, Import File Validations
- `NXT-68646` (Bug) — Item Onboarding - Auto save - PO observations
- `NXT-66427` (Bug) — Publishing to Local Items - Incomplete icon not showing
- `NXT-66007` (Story) — Item Onboarding - Add Special Permission
- `NXT-56249` (Story) — Bulk Item - Bulk Apply - Multi-Select R&D
- `NXT-68590` (Story) — Bulk Item - Check Updates

**Notes.** Highest-volume single category in the sample. Probably 20–25% of all in-scope tickets. Concentrated under three Epics: "IM - Bulk Item Onboarding - Ingredient Info", "IM - Bulk Item - Local Updates", "IM - Item Onboarding - Excel Import/Export & Local Publishing". If category-vs-Epic overlap is too tight here, this becomes a thin category and Epic does the work — worth checking at 1.5.

---

## 2. Recipe Authoring

**Definition.** Anything about constructing or editing a Recipe: Steps & Ingredients tab, sub-recipes (recipes-within-recipes), recipe scaling logic, ingredient direction options, the Find & Replace tool for ingredients, recipe history/audit. Excludes: nutrient calculation that happens *inside* a recipe (that's #4); recipe reports (that's #8); menu items built on top of recipes (that's #3).

**Bug shape.** "Reordering steps doesn't persist on save", "Sub-recipe nutrients not syncing past depth 2", "Find & Replace footer truncated", "Tags not displaying after save", "API deadlock on Recipe SummaryInfo".

**Story shape.** "Add Steps & Ingredients tab", "Recipe Rework - Nutrition card redesign", "Add Ingredient Direction Options", "Find & Replace - Copy - Confirm icons", "Strict Batching flag", "Sub-recipe contributions in recommendations".

**Example tickets.**
- `NXT-37238` (Bug) — Recipe Summary blank/default fields
- `NXT-36791` (Bug) — Recipe Rework - Steps & Ingredients UI consolidated issues
- `NXT-67906` (Bug) — Recipe SummaryInfo API deadlock
- `NXT-36071` (Story) — Recipe Rework - Steps & Ingredients - View Steps
- `NXT-49785` (Story) — Recipes - Ingredients - Direction Options
- `NXT-50899` (Story) — Considering Sub Recipes as part of recommendations

**Notes.** Recipe Rework was clearly a multi-quarter Epic effort. Lots of "Recipe Rework" Stories paired with regression Bugs that landed afterwards. Pain page here is a natural narrative arc.

---

## 3. Menu Items, VMI & POS Configuration

**Definition.** Anything about Menu Items, Variety Menu Items (VMI), and POS-only items: creating/editing them, the Menu & POS info tab, exceptions and not-served logic, scaled menu servings, POS button names and pricing, contribution editing on VMIs, custom (unlinked) menu items. Excludes: the base food item that the menu item is derived from (that's #5 if it's about units, #4 if nutrient data); list-page filtering of menu items (that's #6).

**Bug shape.** "VMI shows Menu & POS Info instead of Menu Info", "Not Served row delete also deletes exceptions", "Variety Menu Item shows inactive during loading", "Menu Item status active without serving info", "POS button uniqueness check missing".

**Story shape.** "MI Consolidation - POS Only Item Pricing", "Menu Items - Scaled menu servings", "VMI - Remove Menu Item Metrics card", "Custom Menu Item Nutrient Info tab", "Allow POS to be independently deactivated".

**Example tickets.**
- `NXT-42691` (Bug) — VMI shows Menu & POS Info tab instead of Menu Info
- `NXT-40879` (Bug) — Menu Items Exceptions - Not Served row delete
- `NXT-59223` (Bug) — DMI contribution display incorrect
- `NXT-39988` (Story) — POS Only Item - Pricing
- `NXT-40447` (Story) — Menu Items - Servings - Menu Servings (scaled)
- `NXT-46679` (Story) — Allow POS to be independently deactivated

**Notes.** Tight overlap with Epic "IM - Menu & POS Consolidation" and "IM - Recipe/Menu Item Management Expansion". Justin will recognize this as the "MI Consolidation" arc.

---

## 4. Nutrients, Contributions & Allergens

**Definition.** The data model for nutritional information: nutrient values & calculations (calories, fats, carbs, sodium, vitamins), the contributions slideout (vegetable/fruit/grain/protein/milk/legume math), allergen card display & data, percentage-based nutrient entry, sync logic when item nutrients change. Excludes: USDA-mandated changes specifically (that's #11), even though they often touch nutrient/contribution data.

**Bug shape.** "Total Fat validation incorrect", "Nutrient % not calculating automatically", "Allergens dropdown showing duplicates", "Sat Fat updating without changes", "Custom allergens not unselectable", "Nutrient label view doesn't show second serving".

**Story shape.** "Item History (Contributions)", "Recipe Rework - Nutrition Info - Contributions", "VMI Nutritional Information Auto-populate", "Nutrient Details updates", "All Types Nutrient Info Allergens Card Redesign", "Allow nutrient entry by percentage".

**Example tickets.**
- `NXT-58576` (Bug) — Total Fat/Carbohydrate logic incorrect
- `NXT-66083` (Bug) — Percentage not calculating in Nutrients
- `NXT-71508` (Bug) — Duplicate Allergens in dropdown
- `NXT-25727` (Story) — VMI Nutritional Information Auto-populate
- `NXT-36109` (Story) — Recipe Rework - Nutrition Info - Contributions
- `NXT-43239` (Story) — Nutrient Details updates

**Notes.** The "contributions flow" thread (item → recipe → menu item) is a recurring story shape; might warrant a sub-category if the volume's high.

---

## 5. Units, Pack Sizes & Serving Measures

**Definition.** The Units card across all item types and the underlying data model for measure/quantity: pack sizes, base/highest unit logic, fluid vs. food units, serving sizes, weight/volume math, unit identifiers (preferred, base, serving), pack-serving link, GTIN/UPC handling, decimal vs. whole-number behavior, placeholder units. Excludes: how units appear in *reports* (that's #8); how units are entered through *bulk tools* (that's #1).

**Bug shape.** "Units card 400 error after creating Not Served", "Cost cleared when deleting inventoryable serving", "Fluid measurement saving incorrectly", "Pack size weight banner shows wrong message", "Duplicate UPC/GTIN accepted", "Confirm button on empty weight has no response".

**Story shape.** "Units card - Rules for Editability", "Items - Units - Unit Identifiers", "Placeholder Unit - Entering Values", "Pack Size Color Change", "Convert scaled weights to higher units (R&D)", "Improve Food/Fluid Questions".

**Example tickets.**
- `NXT-66978` (Bug) — Units Card incorrect banner messages
- `NXT-60338` (Bug) — Units Card 400 error after Not Served
- `NXT-69027` (Bug) — Deleting inventory-able serving clears cost
- `NXT-37109` (Story) — Items - Units - Unit Identifiers
- `NXT-53796` (Story) — Placeholder Unit - Entering Values
- `NXT-54229` (Story) — Units Card - Rules for Editability

**Notes.** The "IM - Units Card Overhaul" Epic concentrates a lot of these. Stories pre-overhaul; Bugs post-overhaul. Time-axis split likely useful.

---

## 6. List Pages, Search, Filters & Navigation

**Definition.** The Items / Recipes / Menu Items list pages and how users move through them: grids, advanced filters, search by description/code/tag, manage-views (column persistence), sort, pagination ("load more"), header filters, split view docking, split-view selected-item color, status filters with sub-types, page transitions. Excludes: bulk operations launched *from* a list page (that's #1); reports launched from list-page dropdowns (that's #8).

**Bug shape.** "Searching by special characters throws 500", "Pagination selection ignored", "Pending deactivation status not selecting by default", "Search load-more behavior inconsistent", "Local Items list UI consolidated issues".

**Story shape.** "All List Pages - Cohesion Updates", "List Page & Nav Updates - status filter sequence", "CNDB Items - Preserve Manage Views", "Add Menu Item filter on Menu Items - Items Page", "Local Items - Manage Views".

**Example tickets.**
- `NXT-44449` (Bug) — Items page search by special chars throws 500
- `NXT-66741` (Bug) — Items list not respecting selection
- `NXT-58136` (Bug) — Search load-more inconsistent
- `NXT-44871` (Bug) — Local Items Split View consolidated UI issues
- `NXT-47036` (Story) — All List Pages Cohesion Updates
- `NXT-52874` (Story) — CNDB Items Preserve Manage Views

**Notes.** The "IM - List Page & Nav Updates" Epic shows up a lot here. Could split into "search" vs. "navigation" but the categories tend to co-occur on the same list-page tickets.

---

## 7. UI/UX Polish, Copy & Visual Defects

**Definition.** Tickets that are *only* about visual presentation, microcopy, button styling, color, alignment, tooltips, banner wording, icons not appearing, character counters, text truncation, label capitalization. The defining trait: no underlying data is wrong, no flow is broken — the UI just looks or reads off. Excludes: visual bugs that *block* a workflow (those go to the relevant feature category — e.g. a button that "looks wrong" but is also non-functional belongs in the feature it blocks).

**Bug shape.** "Cancel button purple instead of grey", "Sticky footer truncated", "Tooltip wording incorrect", "Banner messages alignment off", "Marketing Name Description Label overstretches", "Sesame appearing duplicate on Allergens Card".

**Story shape.** "UI Improvements - Tool Tip", "Items - Units - UI adjustments - Text Guidance", "Items - Recipe Rework - Steps & Ingredients - Edit Step UI consolidated", "Pack Size Color Change", "UX Improvements - Item Split View Selected Color".

**Example tickets.**
- `NXT-54925` (Bug) — Cancel button purple in HACCP Process
- `NXT-48826` (Bug) — Find & Replace - Sticky footer truncated
- `NXT-42093` (Bug) — POS Summary mandatory field overlapping
- `NXT-22056` (Story) — UX Improvements - Item Split View Selected Color
- `NXT-38016` (Story) — Items - Units - UI adjustments - Text Guidance
- `NXT-60862` (Story) — Pack Size Color Change

**Notes.** This category is a magnet for low-impact bugs. Useful for the "linger" analysis — we'd expect P90 here to be longer than other categories because polish tickets get deferred. If volume is too high (>20% of Bugs), consider splitting into "visual-only" vs. "copy/microcopy".

---

## 8. Reports & Data Exports

**Definition.** Generated outputs: Recipe Nutrition Report, Recipe Materials Report, All Food Item Report, Item List Export, Recipe Cost report, Production print recipes, PowerBI conversions. Both the engine that produces them and the cosmetic correctness of the rendered output. Excludes: the data being reported on (that's the underlying-feature category); reports launched from inside the Bulk Item tool (that's #1).

**Bug shape.** "Recipe Cost report shows null", "Item List Export 500 error", "Print recipes shows 0-serving entries", "Recipe Nutrition Report missing trans fat column", "Update Recipe Nutrition Report UI issues", "PowerBI ReportId vs Report Name mismatch".

**Story shape.** "Reports - Page Cleanup", "Update All Items Report (PowerBI)", "Recipe Nutrition Report - Percent of calories from Macronutrients", "INV Reports - Consider Item BU Decimal Setting".

**Example tickets.**
- `NXT-42110` (Bug) — Recipe Cost and Recipe Material Report consolidated issues
- `NXT-50781` (Bug) — Item List Export API Error 500
- `NXT-37618` (Bug) — Update Recipe Nutrition Report UI
- `NXT-31941` (Story) — Reports - Page Cleanup
- `NXT-35689` (Story) — Update All Food Item Report (PowerBI)
- `NXT-43043` (Story) — INV Reports - Consider Item BU Decimal Setting

**Notes.** Probably 5–10% of in-scope tickets. Close kinship with the "IM/INV - Report Updates & PowerBI Conversion" Epic. Justin may want to merge with another category or keep distinct depending on whether reports are seen as a coherent surface in his mental model.

---

## 9. Inventory Sync, Publishing & Cross-Module Boundaries

**Definition.** Where IM ends and another module begins: publishing items to the Inventory module, sync logic when an item is locked / pending-deactivation / synced / published, the inventory tab of an item, vendor contracts on items, find-and-replace operations that span IM↔MP, contribution flow IM→Production. Excludes: pure inventory-module bugs that don't originate in IM; reports that span modules (that's #8).

**Bug shape.** "Items synced to Inventory and clearing categories breaks status", "Item visible on Inventory even if not published", "Menu & POS Info shows incomplete sign after SIR migration", "Active vendor contract not shown for unorderable items", "GSDN upload failing in migration".

**Story shape.** "Items/Recipes/Menu Items - History for sync-related API changes", "Find & Replace - Menu Items - Replace (cross-module)", "Item Import - Make Inventory Ready fields optional".

**Example tickets.**
- `NXT-44402` (Bug) — Summary Card user can clear groups till Item is not Synced
- `NXT-40833` (Bug) — Item visible on inventory even if not published
- `NXT-45852` (Bug) — Menu & POS Info incomplete sign after SIR migration
- `NXT-46347` (Bug) — Active vendor contract on unorderable items
- `NXT-47156` (Story) — History for sync-related API changes
- `NXT-47364` (Story) — IM/MP - Find & Replace - Menu Items - Replace
- `NXT-44510` (Story) — Item Import - Make Inventory Ready fields optional

**Notes.** Cross-module signal lives here. If `touches_other_modules` is the operationalized version, this category should correlate strongly with that flag.

---

## 10. Configuration, Master Data & Migration

**Definition.** Item Configuration sub-pages (HACCP processes, common measures, brands, manufacturers, item categories, storage categories, valuation groups), tag management, data sources / multi-tenancy config, master-data-driven things like "Sesame as a Standard Allergen on UI", migration-time observations (data didn't carry, environment URLs, status-not-defaulting). Excludes: USDA-driven content changes (that's #11) even though they often arrive as configuration changes.

**Bug shape.** "HACCP Process - delete icon not enabled after CCP removal", "Sesame appearing duplicate on Allergens Card", "Recipe HACCP Process - default 0 not going off", "Common Measures - Local Measures created even if Cybersoft", "Pending deactivation status not selecting by default after migration", "GSDN upload failing in migration".

**Story shape.** "HACCP Configuration page", "Brand Configuration", "Configuration - Data Sources (multi-tenancy)", "Items, Recipes, Menu Items - Add Sesame as a Standard Allergen on UI", "MI/POS Categories color change".

**Example tickets.**
- `NXT-37175` (Bug) — HACCP CCP delete icon not enabled
- `NXT-53348` (Bug) — Common Measures - Local Measures created
- `NXT-54737` (Bug) — Migration: status filter default
- `NXT-71222` (Story) — Configuration - Data Sources
- `NXT-23235` (Story) — Brand Configuration
- `NXT-36069` (Story) — HACCP Configuration page - Processes

**Notes.** Migration-specific tickets (PCS-* and "Migration Observation" subjects) cluster here. If migration volume is large, consider splitting "Configuration" from "Migration" — but at sample read, the volume looks blended and small.

---

## 11. USDA & Regulatory Updates

**Definition.** Tickets driven by external regulatory or compliance requirements — primarily USDA: CN25/CNDB structural updates, allergen list changes mandated by law (Sesame), USDA submission corrections, label/wording changes mandated for compliance ("Beans/Peas → Beans, Peas & Lentils"; "Extra Vegetables → Additional Vegetables"; "+Sugar → Ad Sugars"), Recipe Nutrition Report fields required for USDA approval, parenthetical serving measure handling. Excludes: nutrient calculation issues that aren't tied to a USDA mandate (that's #4); CN25 import bugs that are about the data tool (that could be #1 or #4 depending on locus).

**Bug shape.** Rare in this category — most tickets are Stories driven by external mandates. When Bugs exist, they're QA findings against the new compliance changes.

**Story shape.** "Update to CN25 - Verify CN changes", "Add Sesame as a Standard Allergen", "Beans/Peas (Legumes) → Beans, Peas & Lentils", "USDA Corrections for 2025 Submission", "CNDB Monthly Update Implementation", "Recipe Nutrition Report - Percent of calories from Macronutrients (USDA)".

**Example tickets.**
- `NXT-34198` (Story) — Add Sesame as a Standard Allergen on UI
- `NXT-51345` (Story) — Beans/Peas (Legumes) → Beans, Peas & Lentils
- `NXT-33173` (Story) — Extra Vegetables → Additional Vegetables
- `NXT-67404` (Story) — USDA Corrections for 2025 Submission
- `NXT-32108` (Story) — Update to CN25 - Verify CN changes
- `NXT-62716` (Story) — CNDB 2025.X Monthly Update Implementation
- `NXT-18603` (Story) — Recipe Nutrition Report - need Percent of calories from Macronutrients (USDA)

**Notes.** Almost entirely Story-driven. Median duration likely longer than typical Stories because changes often have to round-trip USDA validation. This category exists because "regulatory mandate" is a meaningfully different driver than "customer pain" or "internal improvement" — useful at demo for showing the corpus reflects external pressure too. If volume is small (<5% of in-scope) Rahul may choose to merge into #4 / #10.

---

## Cross-cutting observation: Tech-Debt-shaped Stories

A small number of Stories in scope describe pure backend/architecture work — single-source-of-truth tag tables, multi-select component rewrites, Read Replica DB usage for HACCP, Recipe SummaryInfo deadlock, API deadlock fixes, sub-recipe nutrient sync at depth >2. These don't fit any of the customer-impact categories cleanly. Rahul should decide: do these get a separate **"Internal Engineering / Tech-Debt-Shaped"** category (12th), or do they fold into the feature they touch (e.g. NXT-37981 "Remove MP_Tag" → Configuration; NXT-43301 "Multi Select feature" → UI/UX Polish)?

Recommendation: fold into the host feature. The corpus already excludes Tech-Debt as an issue type, so the tech-debt-shaped Stories that *did* slip in are usually about a specific feature.

---

## What's intentionally NOT a category

- **"API Errors / 500-class bugs"** — work-type, not problem-space. Per spec rule. A 500 on Bulk Item belongs in #1, a 500 on a Report belongs in #8.
- **"Regression Bugs"** — same reasoning. The "Regression - " prefix is a workflow tag, not a problem space.
- **"District-reported issues" (PCS-*)** — these are reporter-driven, not problem-space. Each PCS-* ticket fits one of the 11 categories above based on what the issue is about.
- **"Bulk vs. single-item" as a top-level split** — within #1 (Item Onboarding & Bulk Tools) the bulk-vs-single distinction matters, but elevating it to a top-level category would split flow-coherent tickets across categories.

---

## Spot-check sample (5 random tickets, my best guess at category)

For Rahul to sanity-check the scheme works:

| issue_key | type | best-fit category | confidence |
| --- | --- | --- | --- |
| `NXT-44871` | Bug | List Pages, Search, Filters & Navigation | high |
| `NXT-39988` | Story | Menu Items, VMI & POS Configuration | high |
| `NXT-43965` | Bug | Nutrients, Contributions & Allergens | high (cost flag in Recipe ingredients card → arguable for #2) |
| `NXT-71222` | Story | Configuration, Master Data & Migration | high |
| `NXT-67906` | Bug | Recipe Authoring | medium (it's a backend deadlock; could argue Tech-Debt-shaped → Recipe Authoring is the surface) |

Borderline cases above are the early signal that Rahul's curation pass needs to (a) decide where ambiguous backend issues land and (b) confirm the Recipe vs. Menu Item split holds under stress.

---

## Open questions for Rahul

1. **Do USDA & Regulatory get their own #11, or fold into #4 / #10?** I argued for distinct because the *driver* (external mandate) is different. Volume might be 4–6% — fine for its own category in my view, but it's the most defensible to merge.
2. **Does "Tech-Debt-shaped Stories" get a 12th category, or fold into the host feature?** I recommend folding.
3. **Reports & Exports (#8) — separate or merged into the host feature?** Currently separate because the report surface itself has its own bugs. Could go either way.
4. **Does "List Pages & Navigation" (#6) split into "search/filter" vs. "navigation/views"?** Don't recommend it — they co-occur on the same tickets — but flagging.
5. **Is the Onboarding & Bulk Tools category (#1) too dominant?** If it ends up at 25–30% of the corpus, the pain page for it will be the headline. May warrant splitting into "Item Onboarding wizard" vs. "Bulk Update tool" if you want two pain pages.

Once curated, write the final list as `curated_categories.md` (or replace this file in place) and resume at Step 1.3.
