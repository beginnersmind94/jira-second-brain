## Content Plan — Item Management — TLDR One-Pager

### Template: TLDR one-pager (1 page)
### Source transcript: `raw/transcripts/20260529-070600-item-management-2026-05-28-item-management-create-items-training.md`
### Target audience: District food-service staff responsible for item setup (Brunswick County Schools onboarding cohort); roles include data-entry staff and implementation leads.

---

## Compression strategy (writer's primary risk: overflow)

The inventory contains 35 matched features. At one sentence each, a 35-row table plus five other sections will overflow one page. The solution is **row consolidation**: merge sub-behaviors of the same card or workflow into a single row, preserving every feature name in the sentence so completeness is not lost. The merge rules below reduce 35 features to **24 Key Features rows**. Do not merge further — each remaining row covers a distinct user decision point.

No feature may be silently dropped. If a merged row cannot name all constituent features in ≤15 words, split the row rather than omit a feature name.

---

## Include at full depth

All 35 matched features must appear in the Key Features table. "Full depth" for a TLDR means one sentence per row — there are no tiered depths. The table IS the content. See merge rules below.

---

## Mention briefly (1-2 sentences)

Not applicable for TLDR template. Every feature is one sentence in the Key Features table. There is no "mention briefly" tier separate from the table.

---

## Omit

| # | Feature / Workflow | Reason for omission |
|---|---|---|
| — | Bulk allergen import (Unmatched #9) | Presenter-uncertain; explicitly flagged as unverified. Excluded per CLAUDE.md rule. |
| — | Copy item feature (Unmatched #10) | Presenter-uncertain; NXT-56820 bug exists but unverified. Excluded per CLAUDE.md rule. |
| — | Catalog/corporate DB item import (Unmatched #11) | Presenter-uncertain. Excluded per CLAUDE.md rule. |
| — | 4th-tier receiving workaround (Unmatched #12) | Cross-module (Inventory) + presenter-uncertain. Excluded. |
| — | Sales tax rate configuration (Unmatched #13) | Presenter-uncertain; scoped to business office, not item-setup staff. Excluded. |
| — | Sub-qty = standard spec / short-ship handling (Unmatched #3) | Process opinion, not a ticketed feature. |
| — | Tabs grayed out until Units card saved (Unmatched #4) | UI state note; in ticket description not AC. Suitable only as a gotcha if space allows — see gotchas section. |
| — | "Don't fix costing until all packs added" (Unmatched #5) | Sequencing UX note; covered within the Costing row and gotchas. Not a standalone feature. |
| — | Nutrient save-block / item usable while Incomplete (Unmatched #6) | Partially NXT-43239; specific claim not in AC. Mark [TO VERIFY] if referenced at all. |
| — | Missing Value "(M)" report marker (Unmatched #7) | NXT-43239 covers checkbox; report semantics not in AC. Can note briefly inside Nutrient Details row. |
| — | Costing auto-scale formula details (Unmatched #8) | Algorithm not in AC. The auto-scale behavior is covered in the Costing row; the formula itself is omitted. |

Cross-module references (Inventory lock behavior, vendor contracts, recipe/menu planning links, Family Hub) are noted in "Where to go next" — not expanded in the Key Features table.

---

## Key Features table — merge rules (35 features → 24 rows)

Writer must produce exactly these 24 rows in the order shown. The "Features consolidated" column names every matched feature (#) that the row must represent.

| Row # | Row label (user-facing) | Features consolidated | Merge rationale | Writer sentence guidance |
|---|---|---|---|---|
| 1 | Item card — required fields | #1 (partial: required fields) | Standalone — foundational entry point | Name the four required-for-Inventory fields (Item Description, Item Category, Storage Category, Valuation Group) in ≤15 words |
| 2 | Item card — optional fields | #1 (partial: optional fields) | Split from Row 1 to keep row 1 under 15 words | Name optional fields (Tags, Brand, Manufacturer, Product Code) briefly |
| 3 | Food / Non-Food and Fluid / Non-Fluid selection | #2, #3 | Both are Units-card type-selection questions asked in sequence; Fluid/Non-Fluid only appears after Food is chosen | One sentence naming both choices and their purpose (grams vs. milliliters) |
| 4 | Pack sizes with Higher / Lower hierarchy | #4, #5 | 3-tier max is a property of pack-size entry, not a separate feature | Name the Higher/Lower prompt and the 3-tier maximum in ≤15 words |
| 5 | Unit identifier badges (P / BU / MI) and Base Unit auto-assignment | #6, #7 | Badges and auto-assignment are both read-only results of the same Units-card save; user sees them together | One sentence: badges identify role; Base Unit auto-assigns to lowest level |
| 6 | Costing — one-unit entry, auto-scale, and Manage Costing | #8 | Standalone — distinct workflow step | Name one-unit entry and auto-scale behavior; mention Manage Costing for updates |
| 7 | Inventory Ready flag and Publish toggle | #9 | Standalone — gating milestone | Name the flag and toggle; note green flag = ready to publish |
| 8 | GTIN / UPC barcode entry | #10 | Standalone — optional but distinct | One sentence: 8–14 digit codes per pack size; enables barcode scanning |
| 9 | Whole Numbers vs. Decimals | #11 | Standalone — low priority but locks permanently; critical gotcha candidate | One sentence: controls inventory count unit; locks once item is used in Inventory |
| 10 | Images & Documents | #12 | Standalone — applies to food and non-food | One sentence: upload images/PDFs up to 5 MB; assign via Use As dropdown |
| 11 | Serving sizes (food only) and oz→g auto-conversion | #13 | Standalone — food-only, distinct from pack sizes | One sentence: add serving sizes separately from packs; weight auto-converts oz to grams |
| 12 | Serving ↔ Pack linking for Inventory Eligibility | #14 | Standalone — Highest priority; must not be merged | One sentence: servings and packs must be explicitly linked before item is Inventory-eligible |
| 13 | Base Unit promotion and Dual Unit (food only) | #15 | Standalone — food-only promotion step | One sentence: serving size can be promoted to Base Unit, creating a Dual Unit for food items |
| 14 | Inventory-eligibility lock (Base Unit + Decimals) | #16 | Standalone — critical lock behavior; also a gotcha | One sentence: Base Unit and Decimals setting lock permanently once item is used in Inventory |
| 15 | Nutrient Details — USDA nutrients, Missing Value, per-100g and %DV auto-calc | #17 | Standalone — food-only; major tab | Name USDA nutrient entry, Missing Value checkbox, and auto-calculated columns in ≤15 words |
| 16 | Ingredient Info — Edible Yield Factor, Sub Ingredients, Recipe Directions, Locally Grown, Buy American | #18, #19, #20 | All sub-fields of the same Ingredient Info card; user interacts with them in one editing session | One sentence naming all five fields by their user-facing labels |
| 17 | Contribution Info — Meal Pattern contribution | #21 | Standalone — [TO VERIFY] flag required | One sentence; append [TO VERIFY] per mapper note |
| 18 | Allergen Info — standard allergens and Allergen Feature Disclaimer | #22, #23 | Disclaimer is displayed at the top of the allergen card; not a separate navigation target | One sentence: standard allergen status per item; disclaimer states district retains verification responsibility |
| 19 | Custom Allergens — add to item and configure in Item Configuration | #24, #25 | Config page is the prerequisite for adding custom allergens; user needs both steps together | One sentence: custom allergens must be created in IM > Configuration first, then added per item |
| 20 | Direct Menu Item creation and Menu Item card fields | #26, #27 | Menu Item card fields are entered as part of the creation workflow; not a separate visit | One sentence: food items can be designated Direct Menu Items with name, category, POS Entree flag, and marketing fields |
| 21 | Show on POS toggle | #28 | Standalone — triggers additional fields and POS Pricing tab | One sentence: enabling Show on POS reveals POS attributes and activates the POS Pricing tab |
| 22 | Menu Item Serving sizes and Serving Exceptions | #29, #30 | Both are actions on the Units card's MENU SERVING UI; Exceptions follow directly from serving setup | One sentence: additional menu servings can be added; exceptions control which groups are not served |
| 23 | HACCP — Enable Recipe, HACCP Process (Step 0), Recipe Steps, and Control Points | #31, #32 | Steps card with HACCP config and recipe steps are one workflow in two phases; user completes both in sequence | One sentence: configure HACCP process type and add recipe steps with Critical Control Points on the Steps card |
| 24 | POS Pricing — Student and Adult grids, Set All Prices, Allow Sale, Taxable checkbox | #33, #34 | Same POS Pricing tab, two sub-tabs; Set All Prices and Allow Sale are controls within the grids | One sentence: set student and adult prices per eligibility type; Set All Prices fills all columns at once |

Row 35 from the mapper (Inventory Info tab / vendor contracts) is noted separately:

| Row 25 | Inventory Info tab — vendor contract display | #35 | Standalone — read-only, distinct tab | One sentence: read-only tab shows active vendor contracts once item is published to Inventory |

**Final row count: 25 rows.** This is within one-page capacity when rows average 10–12 words each and the remaining five sections are kept to 1–3 lines each.

---

## Section order

The six required TLDR sections, in template-mandated order. No subsections. No `<h3>`. Flat only.

1. **What this module does** — One sentence. Active voice. "Item Management is where [role] creates and configures food and non-food items that flow to Inventory, menus, POS, and reporting." Name the outcome (downstream modules unblocked) and the primary user (food-service data-entry staff or implementation leads).

2. **Key features** — 2-column `<table>` with `<thead>`. Left: user-facing feature label (do not use ticket IDs or dev codenames). Right: one sentence ≤15 words. Use the 25 rows from the merge table above, in that order. Row order follows the Item card → Units card → tab sequence as presented in training — this mirrors how a user would encounter features in the UI.

3. **Who uses it** — One sentence. Roles visible in transcript: district food-service staff, implementation specialists, and district admins (Configuration page). Do not expand.

4. **Common workflows** — Bulleted list, 4–6 bullets, verb-first, one line each. Use these:
   - Create a non-food item (Item card → Units card → Pack sizes → Costing → Publish)
   - Create a food item (Item card → Units card → Serving + Pack sizes → Link → Costing → Publish)
   - Configure nutrient, allergen, and contribution info for a food item
   - Set up a Direct Menu Item and configure POS pricing
   - Add HACCP process and recipe steps to a menu item
   - Update costing after initial setup using Manage Costing

   Writer may trim to 4–5 bullets if page is tight — remove the last one first (Manage Costing is covered in the Key features table).

5. **Important gotchas** — Bulleted list, exactly 4 bullets (fits one page; 5 risks overflow). Each must cite a source inline via `<!-- Source: -->` comment. Use these four, in priority order:

   | # | Gotcha | Source citation |
   |---|---|---|
   | 1 | Add ALL pack sizes before entering costing — the Missing Costing alert appears immediately but fixing it early means redoing the auto-scale calculation | Transcript [05:18]–[05:45] (Sarah's explicit warning) |
   | 2 | Base Unit and Whole Numbers/Decimals lock permanently once the item is used in Inventory — get these right before any inventory count, receipt, or adjustment | Transcript [37:35]–[38:05], NXT-54229, NXT-33518 |
   | 3 | Serving sizes and pack sizes must be explicitly linked (Inventory Ready alert) before the item becomes Inventory-eligible — an unlinked food item will not flow to Inventory | Transcript [15:02]–[16:08], NXT-37441 |
   | 4 | Custom allergens must be created in IM > Configuration > Item Configuration before they can be added to an item — adding them directly on the allergen card is not possible | Transcript [23:28]–[23:55], NXT-24128 |

   The fifth gotcha candidate (3-tier maximum / no 4th tier) is already captured in the Key Features table Row 4. Do not repeat it as a gotcha unless the page has room — it adds redundancy, and the hard constraint is 3–5 so 4 is valid.

6. **Where to go next** — Bulleted list, 3–4 items with `[[link placeholders]]`. Use:
   - `[[Inventory Module Guide]]` — vendor contracts, inventory counts, receiving; Base Unit and Decimals behavior once locked
   - `[[Recipes Module Guide]]` — serving sizes and sub-ingredient data feed recipe ingredient usage
   - `[[Menu Planning Module Guide]]` — nutrient analysis runs here; Direct Menu Items appear on menus
   - `[[Item Management — Long-form Guide]]` — full step-by-step workflows for every tab covered here

---

## Writer page-budget guidance

The one-page constraint is hard. Approximate budget at standard HTML rendering (~700 words per page, dense layout):

| Section | Budget |
|---|---|
| What this module does | ~20 words |
| Key features table (25 rows × ~12 words average) | ~300 words |
| Who uses it | ~15 words |
| Common workflows (5 bullets × ~10 words) | ~50 words |
| Important gotchas (4 bullets × ~15 words) | ~60 words |
| Where to go next (4 bullets × ~8 words) | ~30 words |
| **Total** | **~475 words** |

475 words leaves ~225 words of headroom for HTML structure overhead (tags, whitespace in source). This is tight but achievable. **Do not add explanatory prose between sections.** Each section is its label plus its content only. If any section runs long, compress the Key Features rows first — shorten sentences, not remove rows.

---

## [TO VERIFY] flags the Writer must carry forward

The following claims have weak Jira grounding and must be marked [TO VERIFY] in the draft per mapper notes:

1. **Contribution Info / Meal Pattern fields (#21)** — field names sourced from Description only, not AC. Row 17 sentence must end with [TO VERIFY].
2. **Menu Item Serving Exceptions (#30)** — no dedicated story AC; transcript is primary voice. Row 22 sentence must end with [TO VERIFY].
3. **Item Description 250-char limit** — presenter said "I think" at [02:01]. Do not assert as fact; omit the specific limit or mark [TO VERIFY] if mentioned.
4. **Edible Yield Factor UI placement (#18)** — NXT-47249 AC places it on the Units card; transcript shows it in Ingredient Info at [20:58]. Row 16 should note Ingredient Info card per transcript voice; append [AMBIGUOUS — verify current UI placement].

---

## Handoff checklist

- [x] Mapper inventory reviewed (35 matched features, 13 unmatched items cataloged)
- [x] Template constraints checked (TLDR: one page, all features, one sentence each, 6 required sections, no subsections)
- [x] 35 matched features compressed to 25 Key Features rows via documented merge rules — no feature dropped
- [x] 11 unmatched/presenter-uncertain items confirmed omitted with reasons
- [x] 4 Important gotchas selected with transcript timestamp / ticket citations
- [x] 4 [TO VERIFY] flags carried forward from mapper
- [x] Page-budget estimate completed (~475 words, within one-page capacity)
- [x] SME fact-check can proceed (Contribution Info, Serving Exceptions, Edible Yield Factor placement, 3-tier max cap are the priority verification targets)
- [x] Writer has enough to generate — merge table, row order, section budgets, and gotcha citations all specified
