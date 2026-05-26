# Curated categories — IM Bugs + Stories (locked for Step 1.3)

_Locked from `proposed_categories.md` after Rahul checkpoint. 12 problem-space categories, plus implicit `Other`. Migration is **not** a category — provenance lives in the new `customer_reported_via_cs` + `cs_source` fields instead. Categories describe what the ticket is about, not where it came from._

---

## Why no Migration category

The proposal's #10 "Configuration, Master Data & Migration" was three different things glued together. After breaking it down:

- ~71 tickets in scope match a Migration / SC-Implementation pattern, almost all `PCS-*` field bugs reported by district-implementation engagements (e.g. *"SC Implementation - District_X - Item export request"*).
- ~136 tickets match Configuration (admin-page improvements: Data Sources, Multi-Tenant, HACCP, Brand, Valuation Group).
- "Master Data" as a sub-pattern was thin once the regex bleed from #5 (Units) and #11 (USDA) was removed; folded into Configuration.

Forcing the 71 PCS-* tickets into a "Migration" category would lose the cross-cutting view. A PCS-* ticket about a vendor sync bug is a problem in **Inventory Sync & Publishing** (#10) — its PCS-* prefix is a *provenance* signal, not a *problem-space* signal. Splitting these signals into different fields lets us answer questions like *"what % of Recipe Authoring bugs come from live customers?"* — which a single category axis would foreclose.

**Decision:** Migration drops as a category. Two new fields carry the provenance signal independently: `customer_reported_via_cs` and `cs_source` (see Output schema below).

---

## #4 vs. #11 disambiguation (read this before tagging)

Both #4 (Nutrients, Contributions & Allergens) and #11 (Configuration) can sound like "configuration." They are not interchangeable.

- **#4 is feature-level setup.** Configuring how *a single menu item, recipe, or food item* is described nutritionally — entering its nutrient values, indicating its contributions, marking its allergens. The ticket is about how a user fills in these fields on a particular item or recipe, or how the calculation/display behaves once they have.
- **#11 is system-level setup.** Configuring the *platform* — the master HACCP processes available to all districts, the brand/manufacturer reference list, the data sources / multi-tenancy settings, the categories users can pick from. The ticket is about an Item Configuration sub-page or admin surface, not about an individual item.

If you can rephrase the ticket as *"a user editing one item is having a problem with X,"* it's likely #4 (or another feature category). If you can rephrase it as *"an admin is setting up the platform-wide list/page for X,"* it's #11.

**Examples:**
- *"IM-Items-Nutrient Info-Total Fat logic is not working as expected"* → **#4** (a user editing nutrients on one item)
- *"IM - Item Config - HACCP Configuration page - CCP - delete icon not enabled"* → **#11** (admin configuring the system-wide HACCP list)
- *"IM- Items, Recipes, Menu Items - Add Sesame as a Standard Allergen on UI"* → **#12** (regulatory mandate, not just config) — see USDA disambiguation below
- *"IM - Configuration - Data Sources"* → **#11**
- *"IM - Items - Allow nutrient entry by percentage"* → **#4** (changing how nutrient *entry* works on items)

## #11 vs. #12 disambiguation

#12 (USDA & Regulatory) trumps #11 when the *driver* is an external regulatory mandate. *"Add Sesame as a Standard Allergen"* would otherwise be #4 or #11 if someone just wanted to extend the allergen list — but because Sesame became a standard allergen by federal law, the driver makes it #12. Same for *"Beans/Peas (Legumes) → Beans, Peas & Lentils"*, *"USDA Corrections for 2025"*, *"CN25 Update"*, *"+Sugar → Ad Sugars"*.

If a USDA mandate isn't named or implied in the ticket, default to the feature category.

---

## The 12 categories

For each: **definition · what's in · what's adjacent but excluded · Bug shape · Story shape · 4–6 example tickets**.

### 1. Item Onboarding — Wizard

**Definition.** The per-item onboarding flow where a user steps through Initial Info → Pack Size → Menu Item Info → Contributions → Nutrients → Allergens → Review → Publish, one item at a time. Includes the slide-out review pages, status icons (complete / incomplete / publish-ready), autosave, the per-section "skip" / "decide later" logic, the Excel-to-Wizard handoff, and the local-publishing terminal step. Adjacent but excluded: bulk-update workflows that operate over many items at once (#2); the underlying nutrient/contribution model itself (#4); the units math the wizard exposes (#6).

**Bug shape.** *"Auto-save fires before user changes anything"*, *"Status icon shows wrong state on Review page"*, *"500 error on Save Weights"*, *"Section shows complete when user unselected it"*.

**Story shape.** *"Item Onboarding - Add Special Permission"*, *"Review Menu Item Info page"*, *"Excel column header changes for clarity"*, *"Add Menu Item Info Blank Template"*.

**Examples.** `NXT-62688` Bug · `NXT-68646` Bug · `NXT-66427` Bug · `NXT-66007` Story · `NXT-60116` Story.

**Top Epics (signal):** `IM - Bulk Item Onboarding - Ingredient Info`, `IM - Item Onboarding- Excel Import/Export & Local Publishing`, `IM - Bulk Inventory & Direct Menu Item Onboarding`.

### 2. Item Onboarding — Bulk Tools

**Definition.** Tools that operate over many items at once: Bulk Update workflows for nutrients / vitamins / serving info / cost-value, the Bulk Apply column-multi-select function, header-filters in Bulk Item, Bulk Check Updates, the in-session view-mode for items, single-item slideouts launched *from* Bulk tools. Adjacent but excluded: the per-item wizard (#1); list-page bulk actions that aren't part of the dedicated Bulk Item tool (#7).

**Bug shape.** *"Bulk Update - Vitamins Bulk Update - Enter by % of Daily Value Missing checkboxes not working"*, *"Bulk Item - View Mode - Multiple UI Issues"*, *"Bulk Update - 500 error on duplicate description save"*.

**Story shape.** *"Bulk Item - Bulk Apply - Multi-Select R&D"*, *"Bulk Item - Check Updates"*, *"Bulk Item - Update Nutrients Individual Slideout"*.

**Examples.** `NXT-70100` Bug · `NXT-68833` Bug · `NXT-68882` Bug · `NXT-56249` Story · `NXT-67565` Story · `NXT-68590` Story.

**Top Epics (signal):** `IM - Bulk Item - Local Updates`, `IM - Bulk Item - Section Filters and Enhancements`, `IM - Bulk Item - Usability Enhancements`.

### 3. Recipe Authoring

**Definition.** Building and editing recipes: Steps & Ingredients tab, sub-recipes (recipes-within-recipes), recipe scaling logic, ingredient direction options, the Find & Replace tool for ingredients, recipe history/audit, recipe-specific fields (HACCP CCPs on a recipe, recipe nutrient sync). Adjacent but excluded: nutrient values inside a recipe (#4 if the issue is the data, #3 if the issue is recipe-flow); recipe reports (#9); menu items built on top of recipes (#4).

**Bug shape.** *"Reordering steps doesn't persist on save"*, *"Sub-recipe nutrients not syncing past depth 2"*, *"Find & Replace footer truncated"*, *"Recipe SummaryInfo API deadlock"*, *"Tags not displaying after save"*.

**Story shape.** *"Recipe Rework - Steps & Ingredients - View Steps"*, *"Add Ingredient Direction Options"*, *"Find & Replace - Copy - Confirm icons"*, *"Strict Batching flag"*, *"Sub-recipe contributions in recommendations"*.

**Examples.** `NXT-37238` Bug · `NXT-36791` Bug · `NXT-67906` Bug · `NXT-36071` Story · `NXT-49785` Story · `NXT-50899` Story.

### 4. Menu Items, VMI & POS Configuration

**Definition.** Configuring individual Menu Items, Variety Menu Items (VMI), and POS-only items: the Menu & POS Info tab, exceptions and not-served logic, scaled menu servings, POS button names and pricing, contribution editing on VMIs, custom (unlinked) menu items, menu-item flags (Added Sugar Product, etc.). Note: this is **feature-level** config — about how a single menu item is set up. System-level config (multi-tenant, HACCP processes, valuation groups) is #11. Adjacent but excluded: the base food item underneath the menu item (#6 if it's a units issue); list-page filtering of menu items (#7); contributions math itself (#5).

**Bug shape.** *"VMI shows Menu & POS Info instead of Menu Info"*, *"Not Served row delete also deletes exceptions"*, *"Menu Item status active without serving info"*, *"POS button uniqueness check missing"*.

**Story shape.** *"MI Consolidation - POS Only Item Pricing"*, *"Menu Items - Scaled menu servings"*, *"VMI - Remove Menu Item Metrics card"*, *"Allow POS to be independently deactivated"*.

**Examples.** `NXT-42691` Bug · `NXT-40879` Bug · `NXT-59223` Bug · `NXT-39988` Story · `NXT-40447` Story · `NXT-46679` Story.

### 5. Nutrients, Contributions & Allergens

**Definition.** The data model and per-item entry/display for nutritional information: nutrient values & calculations (calories, fats, carbs, sodium, vitamins), the contributions slideout (vegetable/fruit/grain/protein/milk/legume math), allergen card display & data, percentage-based nutrient entry, sync logic when item nutrients change, nutrient-info display variants (label view, etc.). Adjacent but excluded: USDA-driven changes specifically (#12); the configuration of allergen lists at platform level (#11); reports of nutrient data (#9).

**Bug shape.** *"Total Fat validation incorrect"*, *"Nutrient % not calculating automatically"*, *"Allergens dropdown showing duplicates"*, *"Custom allergens not unselectable"*, *"Nutrient label view doesn't show second serving"*.

**Story shape.** *"Item History (Contributions)"*, *"Recipe Rework - Nutrition Info - Contributions"*, *"VMI Nutritional Information Auto-populate"*, *"Nutrient Details updates"*, *"Allow nutrient entry by percentage"*.

**Examples.** `NXT-58576` Bug · `NXT-66083` Bug · `NXT-71508` Bug · `NXT-25727` Story · `NXT-36109` Story · `NXT-43239` Story.

### 6. Units, Pack Sizes & Serving Measures

**Definition.** The Units card across all item types and the underlying data model for measure/quantity: pack sizes, base/highest unit logic, fluid vs. food units, serving sizes, weight/volume math, unit identifiers (preferred / base / serving), pack-serving link, GTIN/UPC handling, decimal vs. whole-number behavior, placeholder units, food/fluid questionnaire. Adjacent but excluded: how units appear in *reports* (#9); how units are entered through *bulk tools* (#2); how units flow into Inventory (#10).

**Bug shape.** *"Units Card 400 error after creating Not Served"*, *"Cost cleared when deleting inventory-able serving"*, *"Fluid measurement saving incorrectly"*, *"Pack size weight banner shows wrong message"*, *"Confirm button on empty weight has no response"*.

**Story shape.** *"Units card - Rules for Editability"*, *"Items - Units - Unit Identifiers"*, *"Placeholder Unit - Entering Values"*, *"Pack Size Color Change"*, *"Improve Food/Fluid Questions"*.

**Examples.** `NXT-66978` Bug · `NXT-60338` Bug · `NXT-69027` Bug · `NXT-37109` Story · `NXT-53796` Story · `NXT-54229` Story.

### 7. List Pages, Search, Filters & Navigation

**Definition.** The Items / Recipes / Menu Items list pages and how users move through them: grids, advanced filters, search by description / code / tag, manage-views (column persistence), sort, pagination ("load more"), header filters, split-view docking, split-view selected-item color, status filters with sub-types, page transitions. Adjacent but excluded: bulk operations launched *from* a list page (#2); reports launched from list-page dropdowns (#9); list-page UI polish that doesn't break a workflow (#8).

**Bug shape.** *"Searching by special characters throws 500"*, *"Pagination selection ignored"*, *"Pending deactivation status not selecting by default"*, *"Search load-more behavior inconsistent"*.

**Story shape.** *"All List Pages - Cohesion Updates"*, *"List Page & Nav Updates - status filter sequence"*, *"CNDB Items - Preserve Manage Views"*, *"Add Menu Item filter on Menu Items - Items Page"*.

**Examples.** `NXT-44449` Bug · `NXT-66741` Bug · `NXT-58136` Bug · `NXT-44871` Bug · `NXT-47036` Story · `NXT-52874` Story.

### 8. UI/UX Polish, Copy & Visual Defects

**Definition.** Tickets that are *only* about visual presentation, microcopy, button styling, color, alignment, tooltips, banner wording, icons not appearing, character counters, text truncation, label capitalization. The defining trait: no underlying data is wrong, no flow is broken — the UI just looks or reads off. Adjacent but excluded: visual issues that *block* a workflow (those go to the relevant feature category — a button that "looks wrong" *and* is non-functional belongs in the feature it blocks).

**Bug shape.** *"Cancel button purple instead of grey"*, *"Sticky footer truncated"*, *"Tooltip wording incorrect"*, *"Banner messages alignment off"*, *"Marketing Name Description Label overstretches"*.

**Story shape.** *"UI Improvements - Tool Tip"*, *"Items - Units - UI adjustments - Text Guidance"*, *"Pack Size Color Change"*, *"UX Improvements - Item Split View Selected Color"*.

**Examples.** `NXT-54925` Bug · `NXT-48826` Bug · `NXT-42093` Bug · `NXT-22056` Story · `NXT-38016` Story · `NXT-60862` Story.

**Note.** Expect this category to skew long-duration / high-passive-linger. Polish bugs get deferred. The `linger_rate` finding for #8 is itself useful demo material.

### 9. Reports & Data Exports

**Definition.** Generated outputs: Recipe Nutrition Report, Recipe Materials Report, All Food Item Report, Item List Export, Recipe Cost report, Production print recipes, PowerBI conversions. Both the engine that produces them and the cosmetic correctness of the rendered output. Adjacent but excluded: the data being reported on (that's the underlying-feature category); reports launched from inside the Bulk Item tool (#2).

**Bug shape.** *"Recipe Cost report shows null"*, *"Item List Export 500 error"*, *"Print recipes shows 0-serving entries"*, *"Recipe Nutrition Report missing trans fat column"*, *"PowerBI ReportId vs Report Name mismatch"*.

**Story shape.** *"Reports - Page Cleanup"*, *"Update All Food Item Report (PowerBI)"*, *"Recipe Nutrition Report - Percent of calories from Macronutrients"*, *"INV Reports - Consider Item BU Decimal Setting"*.

**Examples.** `NXT-42110` Bug · `NXT-50781` Bug · `NXT-37618` Bug · `NXT-31941` Story · `NXT-35689` Story · `NXT-43043` Story.

### 10. Inventory Sync & Publishing

**Definition.** Where IM ends and another module begins: publishing items to the Inventory module, sync logic when an item is locked / pending-deactivation / synced / published, the Inventory tab of an item, vendor contracts on items, find-and-replace operations that span IM↔MP, contribution flow IM→Production. Adjacent but excluded: pure inventory-module bugs that don't originate in IM; reports that span modules (#9). When a ticket fires this category, also set `touches_other_modules` to True.

**Bug shape.** *"Items synced to Inventory and clearing categories breaks status"*, *"Item visible on Inventory even if not published"*, *"Menu & POS Info shows incomplete sign after SIR migration"*, *"Active vendor contract not shown for unorderable items"*, *"GSDN upload failing in migration"*.

**Story shape.** *"Items/Recipes/Menu Items - History for sync-related API changes"*, *"IM/MP - Find & Replace - Menu Items - Replace"*, *"Item Import - Make Inventory Ready fields optional"*.

**Examples.** `NXT-44402` Bug · `NXT-40833` Bug · `NXT-45852` Bug · `NXT-46347` Bug · `NXT-47156` Story · `NXT-47364` Story.

### 11. Configuration

**Definition.** *System-level* configuration of the platform: Item Configuration sub-pages (HACCP processes, common measures, brands, manufacturers, item categories, storage categories, valuation groups, leftover categories, MI/POS categories), tag management, data sources / multi-tenancy config. The unifying trait: an admin is setting up the platform-wide list/page that other users will pick from. Adjacent but excluded: feature-level setup of an individual item (#4 for nutrient/contribution/allergen entry; #6 for unit setup); USDA-driven changes that touch master lists (#12).

**Bug shape.** *"HACCP CCP delete icon not enabled"*, *"Common Measures - Local Measures created even if Cybersoft"*, *"Valuation Category dropdown options not showing"*, *"Brand Configuration save not working"*.

**Story shape.** *"IM - Configuration - Data Sources"*, *"Multi-Tenant Settings"*, *"HACCP Configuration page"*, *"Brand Configuration"*, *"Items - Consume Sub-Type logic for Inventory info"*, *"Change Valuation Group to 'Valuation Category'"*.

**Examples.** `NXT-37175` Bug · `NXT-53348` Bug · `NXT-71222` Story · `NXT-23235` Story · `NXT-36069` Story · `NXT-71655` Story.

### 12. USDA & Regulatory Updates

**Definition.** Tickets driven by external regulatory or compliance requirements — primarily USDA: CN25/CNDB structural updates, allergen list changes mandated by law (Sesame), USDA submission corrections, label/wording changes mandated for compliance ("Beans/Peas → Beans, Peas & Lentils"; "Extra Vegetables → Additional Vegetables"; "+Sugar → Ad Sugars"), Recipe Nutrition Report fields required for USDA approval, parenthetical serving measure handling. **Driver is the discriminator:** if a USDA / FDA / regulatory mandate is named or strongly implied, this category wins over #4 or #11.

**Bug shape.** Rare. When present, usually a QA finding against a recently-released compliance change.

**Story shape.** *"Update to CN25 - Verify CN changes"*, *"Add Sesame as a Standard Allergen"*, *"Beans/Peas (Legumes) → Beans, Peas & Lentils"*, *"USDA Corrections for 2025 Submission"*, *"CNDB 2025.X Monthly Update Implementation"*, *"Recipe Nutrition Report - Percent of calories from Macronutrients (USDA)"*.

**Examples.** `NXT-34198` Story · `NXT-51345` Story · `NXT-33173` Story · `NXT-67404` Story · `NXT-32108` Story · `NXT-18603` Story.

### Other (implicit)

Reserved for tickets that genuinely fit none of the 12. **Hard gates:** if `Other` exceeds 10% overall or 15% within Bugs alone after Step 1.3, the categorization halts and `other_reason` distribution is surfaced before re-running.

---

## Output schema for `ticket_categories.csv`

| Field | Type | Source |
| --- | --- | --- |
| `issue_key` | string | passthrough |
| `issue_type` | enum: Bug / Story | passthrough |
| `primary_category` | string (one of 12 + `Other`) | LLM |
| `secondary_category` | string, nullable | LLM |
| `category_confidence` | enum: high / medium / low | LLM |
| `other_reason` | string, nullable | LLM (only when primary == `Other`) |
| `customer_reported_via_cs` | bool | mechanical: `issue_key.startswith("PCS-")` |
| `cs_source` | enum: implementation / live_customer / unclear / null | LLM (only when `customer_reported_via_cs == True`) |
| `touches_other_modules` | bool | mechanical: `len(components_all) > 1` OR `primary_category == 10` |
| `other_modules_list` | string, pipe-joined | mechanical: `components_all` minus `Item Management` |

### `cs_source` detection rules

Only applies when `issue_key` starts with `PCS-`:

- Title contains `"SC Implementation"` or `"District [name] - <onboarding-shaped>"` → `implementation`
- Title or description references production usage, post-go-live timeframes, live-system context → `live_customer`
- Created date within ~60 days of the district's first appearance in the corpus → `implementation` (LLM hint, not enforced)
- None of the above clearly discriminate → `unclear`

When `customer_reported_via_cs == False`, `cs_source` is `null`.

---

## What this curated list intentionally leaves out

- A "Migration" category. Provenance is now `customer_reported_via_cs` + `cs_source`.
- A "Tech-Debt-shaped Stories" category. Folded into the host feature.
- A "Master Data" category separate from Configuration. Folded into #11.
- A "list-page search vs. navigation" split. Single bucket per Rahul.
- A visual-vs-flow split inside #8. Single bucket per the data (10% of bugs are visual-only; flow defects belong in their host feature).

---

## Hard gates for Step 1.3

- `Other` rate < 10% overall — else surface `other_reason` distribution and halt
- `Other` rate < 15% within Bugs alone — else surface and halt
- `cs_source == 'unclear'` rate < 30% within the PCS-* subset — else surface ambiguous PCS-* tickets and halt

If gates pass, proceed to Workstream 2.
