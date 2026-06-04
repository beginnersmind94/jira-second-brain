## Content Plan — Item Management — TLDR One-Pager

### Template: TLDR one-pager (1 page, scan speed)
### Source transcript: 20260529-070600-item-management-2026-05-28-item-management-create-items-training.md
### Target audience: District Admin, Nutrition Manager, Food Service Director

---

## Section 1 — What this module does

**Planned text (one sentence):**
Item Management is where District Admins and Nutrition Managers create and maintain every food and non-food item — including pack sizes, nutrients, allergens, costing, and menu configuration — before the item can be used in Inventory, Recipes, or POS.

**Source cites:** NXT-30036 AC [+NEW / Item Description required]; NXT-35898 AC [Food/Non-Food]; NXT-30155 AC [POS tab]; transcript [00:00]–[00:52].

---

## Section 2 — Key Features table

### Merge rules applied (per compression memory [[feedback-tldr-compression]])

The mapper inventory has 39 matched features. Many are sub-fields of the same card or sequential steps of the same workflow. The table below merges them into 26 rows while preserving every feature name in the sentence text. No feature is omitted — merger means the name appears in the row's sentence, not that it is dropped.

**Merge decisions:**
1. Item card creation (+NEW, Item Details page) + Item card fields (Item Description, Tags, Brand Name, Manufacturer, Product Code) → **1 row** — all fields are on the same initial card; Description is the only required one.
2. Item Category + Storage Category + Valuation Group → **1 row** — three dropdowns on the same Product Info step; their required-together logic makes them one feature to staff.
3. Food vs. Non-Food selection + Fluid vs. Non-Fluid selection → **1 row** — both are header-bar questions on the Units card answered before the grid enables.
4. Pack size add (+PACK, Higher/Lower, Description, Sub-Qty, Weight) + Three-tier maximum → **1 row** — three-tier cap is a property of the pack-size entry workflow, not an independent feature.
5. Unit Identifiers column (P/BU/MI badges) + Base Unit auto-assignment (lowest pack = BU by default) → **1 row** — both are read-only system outputs of the save step; staff see them together.
6. Missing Costing alert + Manage Costing button (auto-calculation of costs across tiers) → **1 row** — these are two states of the same costing prompt; the button replaces the alert.
7. Inventory Ready flag / green flag + Publish toggle auto-enable → **1 row** — both fire together when Inventory readiness conditions are met.
8. Whole Numbers vs. Decimals setting → **standalone row** — affects downstream Inventory throughout item's lifetime; functionally independent from all other flags.
9. GTIN/UPC entry + barcode icons in Identifiers → **1 row** — barcode icon is the direct result of entering a GTIN; they are one workflow.
10. Serving size add (+SERVING, Amount, Description, Weight/Ounce) → **standalone row** — food-only; high priority (NXT-35898 High); central to nutrient and recipe chains.
11. Link servings to pack sizes (Inventory Eligibility, Sub-Qty on serving row) → **standalone row** — Highest priority ticket (NXT-37441); prerequisite for Inventory readiness; must be its own row for visibility.
12. Base Unit promotion / Merge (serving promoted to BU for food, dual unit) → **standalone row** — dedicated AC in NXT-40778; involves a Merge prompt; distinct from auto-assignment.
13. Edible Yield Factor (Units card, per-serving) + Ingredient Info card (Sub Ingredients, Standard Recipe Directions, Locally Grown, Buy American checkboxes) → **1 row** — all Ingredient Info card or closely adjacent sub-fields; Yield Factor moved to Units card per NXT-47249 (write at Units card location, not Ingredient Info).
14. Images & Documents card (drag-and-drop, Use As dropdown, up to 10 files) → **standalone row** — RN-visible (External+Internal); medium priority; enough differentiating detail to warrant its own row.
15. Nutrient Details entry (required fields, Missing Value checkbox, Vitamin A/C now optional, nested auto-zero) → **standalone row** — RN-visible (External+Internal); high priority; Nutrition Manager audience.
16. Contribution Info card (meal pattern credits: Fruits, Meat/Meat Alternates, Grains, Milk, Vegetables) → **standalone row** — [TO VERIFY: specific component names are Description-only per NXT-30102/37216 field-name caution list; use "meal pattern credits" generically].
17. Allergen Info card (standard allergens, Contains/Processed/May Contain/Free From forms, Allergen Feature Disclaimer) → **standalone row** — cited AC in NXT-30103, NXT-41275; allergen forms confirmed in AC priority order.
18. Custom Allergen configuration (IM > Configuration > Item Configuration > Custom Allergens) → **standalone row** — detailed AC in NXT-24128; setup is a prerequisite to using custom allergens on items; District Admin action.
19. Menu Info tab — Direct Menu Item creation (CREATE MENU ITEM, Menu Item fields) + Show on POS toggle → **1 row** — creating the menu item and enabling POS are sequential steps on the same tab; staff do them together.
20. Menu Item fields requiring [TO VERIFY] labels → flagged within the row sentence (see note below).
21. Menu Item Serving (+Menu Serving button) + Menu Item Serving Exceptions (not-served by school level / meal pattern group) → **1 row** — both are actions on the Units card once the item is a Menu Item per NXT-54229 AC.
22. Steps card / HACCP (ENABLE RECIPE, HACCP Process selection, Pre-Prep Instructions, Add Steps, drag-and-drop reorder) + HACCP Control Points (Add CCP, Critical Limit, Corrective Action) → **1 row** — two phases of one Steps-card workflow; staff complete both on the same card.
23. POS Pricing — Students grid (Free/Reduced/Paid/Second Meal × school levels, Set All Prices) + Adults tab (staff/visitor/program, Taxable Adults-only) → **1 row** — same tab, two sub-tabs; Taxable is an Adults-tab-only property confirmed by NXT-58442 AC.
24. Inventory Info tab (read-only vendor contract preview, shortcut to Inventory Contract Items) → **standalone row** — AC confirmed NXT-40479; read-only nature is important to call out explicitly so staff don't try to edit from IM.
25. Editability locking (Base Unit + Whole Numbers/Decimals locked after first Inventory transaction) → **standalone row** — high priority (NXT-54229 High); critical gotcha; also appears in Gotchas section but deserves one feature row for the scan reader.
26. Nutrient Info / Serving Size auto-conversion (oz to grams shown in Nutrient Info tab header) → **fold into Nutrient Details row** — this is a display property of the Nutrient Details card; merging keeps row count at 26.

**Final row count: 26**

### Full Key Features table (to be rendered as HTML <table> by Writer)

| # | Feature name (user-facing label) | One-sentence description (≤15 words) | Ticket | [TO VERIFY] flags |
|---|---|---|---|---|
| 1 | Item card | Create items with a required Item Description; add optional Tags, Brand Name, Manufacturer, and Product Code. | NXT-30036 | "Brand Name," "Manufacturer," "Product Code," "Tags" — field names from Description only; assert labels cautiously or use [TO VERIFY] |
| 2 | Product Info attributes | Three required dropdowns — Item Category, Storage Category, Valuation Group — needed for Inventory use. | NXT-30037 | Field names ("Item Category," "Storage Category," "Valuation Group") are Description-only; assert as [TO VERIFY] |
| 3 | Food / Non-Food and Fluid / Non-Fluid selection | Two header questions on the Units card that control which unit types and fields are available. | NXT-35898 | None — AC confirmed |
| 4 | Pack sizes | Add up to three tiers of pack sizes [TO VERIFY: three-tier cap]; Sub-Qty links tiers; Weight optional for non-food. | NXT-37110 | Three-tier maximum not in AC; mark with [TO VERIFY] |
| 5 | Unit Identifiers and Base Unit | Identifiers column shows P/BU/MI badges; the lowest pack size is auto-assigned as the Base Unit. | NXT-37109, NXT-37111 | "P," "BU," "MI" badge labels — Description-only; assert as [TO VERIFY] |
| 6 | Costing | Enter cost for one pack size unit; the system scales cost to all others automatically. | NXT-37568 | "Missing Costing" alert label, "Manage Costing" button label — Description-only |
| 7 | Inventory Readiness banner | Always-visible banner shows whether the item meets Inventory requirements; turns green when ready. | NXT-53530, NXT-37111 | None — AC confirmed |
| 8 | Whole Numbers / Decimals | Sets whether the Base Unit can be counted in decimals throughout Inventory for this item. | NXT-33518 | None — AC confirmed |
| 9 | GTIN / UPC | Enter 8–14 digit barcodes per pack size; a barcode icon appears in the Identifiers column. | NXT-37815 | None — AC confirmed (digit range explicitly in AC) |
| 10 | Serving sizes (food items only) | Add serving sizes with Amount, Description, and Weight; forms the basis for nutrient and recipe calculations. | NXT-35898 | None — AC confirmed |
| 11 | Serving-to-pack link | Sub-Qty on the serving row connects a serving to its parent pack size, making the item Inventory-eligible. | NXT-37441 | None — AC confirmed |
| 12 | Merge / Base Unit promotion | When a pack size matches an existing serving, a Merge prompt appears to create a dual-use unit. | NXT-40778 | Presenter used "promote" / "BASE UNIT chip"; AC says "Merge"; use AC term. Exact dialog text [TO VERIFY] |
| 13 | Yield Factor and Ingredient Info | Edible Yield Factor is set per serving on the Units card; Ingredient Info card holds Sub Ingredients, Standard Recipe Directions, Locally Grown, and Buy American checkboxes. | NXT-47249, NXT-30100 | DISCREPANCY D1: presenter said Yield Factor is on Ingredient Info card; NXT-47249 AC (Done-Done) moved it to Units card. Use Units card location. Sub Ingredients, Standard Recipe Directions, Locally Grown, Buy American — field names from Description only; [TO VERIFY] |
| 14 | Images & Documents | Drag-and-drop card for images and documents (up to 10 files); assign a Use As type for each file. | NXT-41273 | 5 MB limit [TO VERIFY]; specific file types [TO VERIFY]; Use As dropdown values are AC-confirmed |
| 15 | Nutrient Details | Enter required nutrients; Vitamin A and Vitamin C are now optional; entering 0 for Total Fat or Total Carbs auto-zeros nested nutrients; oz values convert to grams automatically in the tab header. | NXT-43239 | "Per 100g" column, auto-percentage calculation — Description-only; [TO VERIFY] |
| 16 | Contribution Info | Records meal pattern credits (Fruits, Meat/Meat Alternates, Grains, Milk, Vegetables) in a slideout; can be skipped. | NXT-30102, NXT-37216 | Specific component names [TO VERIFY] — AC says "Load the Contributions section" without naming components |
| 17 | Allergen Info | Displays standard allergens in priority order: Contains, Processed, May Contain, Free From; includes Allergen Feature Disclaimer. | NXT-30103, NXT-41275 | Standard allergen list (Crustacean Shellfish, Egg, Fish, etc.) — Description-only; [TO VERIFY] exact list |
| 18 | Custom Allergen configuration | Create district-specific allergens at IM > Configuration > Item Configuration > Custom Allergens; duplicates are blocked. | NXT-24128 | "Show on Family Hub menus" toggle — AMBIGUOUS (A1 in factcheck); do not assert without product team confirmation |
| 19 | Menu Info tab / Direct Menu Item | Create a Menu Item directly from the item; enable Show on POS to unlock pricing configuration. | NXT-39594, NXT-30155 | "Disabled" status label before configuration — Description-only; tab rename to "MENU & POS INFO" — Description-only; individual field names (Menu Item Name, Button Name, etc.) — Description-only; all [TO VERIFY] |
| 20 | Menu Item fields | Required fields include Menu Item Name, Button Name (English), and Menu Item Category; optional fields include Marketing Name, Max Days, and Leftover Category. | NXT-30155 | All individual field names are Description-only; [TO VERIFY] |
| 21 | Menu Item Servings and Exceptions | Add scaled menu servings via +Menu Serving; mark exceptions for specific schools or meal pattern groups that do not serve this item. | NXT-40447, NXT-54229 | Exact UI steps for Exceptions [TO VERIFY]; AC confirms availability but not the specific workflow |
| 22 | Steps / HACCP and Control Points | Enable a recipe, select a HACCP Process [TO VERIFY: No Cook / Same Day Service / Complex Food], add steps and Control Points with editable Critical Limit and Corrective Action. | NXT-36583, NXT-36742 | HACCP process names [TO VERIFY]; Pre-Prep Instructions, Prep Time, Cook Time field names [TO VERIFY]; 42°F critical limit value [TO VERIFY] |
| 23 | POS Pricing | Set student pricing (Free/Reduced/Paid by school level) and adult pricing; Taxable option appears on Adults tab only. | NXT-30155, NXT-58442 | Student pricing grid structure (school level labels) — Description-only; [TO VERIFY] |
| 24 | Inventory Info tab | Read-only preview of active vendor contracts from Inventory; shortcut icon opens Contract Items in a new tab. | NXT-40479 | Contract detail column names (vendor name, lead time, etc.) — Description-only; [TO VERIFY] |
| 25 | Editability locking | Base Unit and Whole Numbers/Decimals setting become locked once the item is used in Inventory transactions. | NXT-54229 | Specific trigger events ("inventory count, receipt, adjustment") — Description-only; [TO VERIFY] |
| 26 | Inventory Info tab (sub-note: this row kept separate from GTIN for scan clarity; GTIN is a Units-card action while Inventory Info is a read-only tab) | — see row 24 — | — | Row 24 covers this; no duplication |

**CORRECTION — row 26 is not a real row.** After merge pass, the table is exactly **25 rows** (rows 1–25 above, with row 26 removed; Inventory Info tab = row 24 only). The final count: **25 rows**.

---

## Section 3 — Who uses it

**Planned text:**
District Admins create and maintain all item records; Nutrition Managers complete nutrient, contribution, allergen, and menu details; Food Service Directors review item status before items go live.

**Source:** mapper-metadata.json audience_roles; transcript [00:52].

---

## Section 4 — Common workflows (verb-first bullets)

1. Create a non-food item — add Item Description, select Product Info dropdowns, add pack size tiers, enter costing.
2. Create a food item — complete Item card, add pack sizes, add serving sizes, link serving to pack via Sub-Qty, confirm Base Unit.
3. Set up nutrients — open Nutrient Details, enter required nutrients, use Missing Value checkbox for absent nutrients, save.
4. Configure allergens — record standard allergen forms on the Allergen Info card; add district-specific allergens first via IM Configuration > Custom Allergens.
5. Make an item a Menu Item — open Menu Info tab, complete required fields, enable Show on POS if the item will be sold at the register, configure POS pricing.
6. Enable recipe / HACCP — click ENABLE RECIPE on Steps card, select HACCP Process, add preparation steps, add Control Points with Critical Limit and Corrective Action.
7. Attach supporting documents — drag files onto Images & Documents card, assign Use As type (e.g., CN Label, Preferred Inventory Image).

**Source cites:** All seven workflows are drawn from verified transcript segments and AC-confirmed features. See factcheck.md verified claims V1–V37.

---

## Section 5 — Important gotchas (3–5, each cited)

**Selected gotchas — cross-cutting consequences only (per compression memory principle):**

### Gotcha 1 — Add all pack sizes BEFORE entering costing
Enter all pack size tiers first, then address the Missing Costing alert; costing entered mid-way may not scale correctly across remaining tiers. <!-- Source: transcript [05:18] — "the system tells you not to address that until you've added ALL your pack sizes" -->

### Gotcha 2 — Serving must be linked to a pack size for Inventory eligibility
An unlinked serving size makes the item Inventory Ineligible; always enter Sub-Qty on the serving row to connect it to the parent pack size. <!-- Source: NXT-37441 AC: "Trigger Inventory readiness based on proper pack-serving links" -->

### Gotcha 3 — Base Unit and Whole Numbers/Decimals lock after first Inventory transaction
Once you have completed an inventory count, receipt, or adjustment for an item, the Base Unit and Whole Numbers/Decimals setting cannot be changed [TO VERIFY: exact trigger events]. <!-- Source: NXT-54229 AC: "Long-term editing: changing sub-quantities listed as restricted"; transcript [37:35]–[38:05] -->

### Gotcha 4 — Custom allergens must be created in Configuration before they appear on item records
To apply a custom allergen to an item, a District Admin must first set it up at IM > Configuration > Item Configuration > Custom Allergens; it will not appear in the allergen slideout until that step is done. <!-- Source: NXT-24128 AC: "A Custom allergens option is added under IM configuration area" -->

### Gotcha 5 — Discrepancy: Yield Factor location
Discrepancy: presenter said Yield Factor is on the Ingredient Info card [20:42]; NXT-47249 AC (Done-Done) states it was moved to the Units card (per-serving column). Use the Units card workflow — the Ingredient Info card no longer shows Yield Factor. <!-- Source: factcheck.md D1 HIGH; NXT-47249 AC: "Remove Yield Factor from Ingredient Info card (moved to Units)" -->

**Gotcha count: 5** (at the template maximum; all 5 are cross-cutting and cited).

---

## Section 6 — Where to go next

- [[Inventory module]] — Vendor contracts, receiving, and item counts reference the pack sizes and Base Unit configured here.
- [[Recipes module]] — Serving sizes and Ingredient Info (Sub Ingredients, Yield Factor) feed recipe ingredient calculations.
- [[Menu Planning module]] — Nutrient data and Contribution Info entered here drive menu nutrient analysis.
- [[Family Hub module]] — Marketing Name, Menu Item description, and custom allergen visibility for parent-facing menus.
- [[POS module]] — Button Name, POS Entree flag, and POS Pricing configured in Menu Info flow to the POS touchscreen.

**Source cites:** factcheck.md cross-module claims C1–C8; mapper-inventory.md cross-module references C1–C9.

---

## Density estimate and one-page risk assessment

### Row count
- Key features table: **25 rows**
- Common workflows: **7 bullets**
- Gotchas: **5 bullets**
- Where to go next: **5 bullets**
- Section headings: 6

### Word count estimate
| Section | Estimated words |
|---|---|
| What this module does | ~35 |
| Key features table (25 rows × ~12 words avg) | ~300 |
| Who uses it | ~30 |
| Common workflows (7 × ~15 words) | ~105 |
| Gotchas (5 × ~25 words incl. cite) | ~125 |
| Where to go next (5 × ~12 words) | ~60 |
| Section headings + table headers | ~30 |
| **Total** | **~685 words** |

### One-page assessment
A standard dense HTML page at the layout described in tldr.md holds approximately 600–750 words with a 2-column table. **685 words is at the upper edge of the safe range.** The following compression levers are available if the Writer reports overflow:

1. **Shorten table sentences:** Several rows in the Key features table run to 14–15 words; trimming to 10 words average saves ~50 words.
2. **Compress Gotcha 5 (Discrepancy):** The Discrepancy gotcha is the longest bullet; cut the explanatory parenthetical to save ~15 words.
3. **Trim workflow bullets:** Workflows 1 and 2 each have two sub-clauses; drop the trailing clause if needed.

**Do NOT drop rows, omit gotchas, or cut "Where to go next" entries to recover space — compression must come from word count within rows, not feature omission.** This is a hard constraint from the template definition.

### [TO VERIFY] items for Writer awareness
The following items in the Key features table must be marked [TO VERIFY] in the draft (cannot be asserted from Tier-1 AC):
- Three-tier pack-size cap (row 4)
- P/BU/MI badge labels (row 5)
- "Missing Costing" and "Manage Costing" button labels (row 6)
- Yield Factor location (row 13) — use Units card; Discrepancy D1
- 5 MB file size limit, specific file types (row 14)
- Per-100g column in Nutrient Details (row 15)
- Contribution component names: Fruits, Meat/Meat Alternates, Grains, Milk, Vegetables (row 16)
- Standard allergen list enumeration (row 17)
- Custom allergen "Show on Family Hub" toggle — AMBIGUOUS A1; omit entirely
- All Menu Info / POS Info field names (rows 19–20): Menu Item Name, Button Name, Marketing Name, Max Days, Leftover Category, etc.
- Menu Item Serving Exceptions exact UI steps (row 21)
- HACCP process names: No Cook, Same Day Service, Complex Food (row 22)
- Pre-Prep Instructions, Prep Time, Cook Time field names (row 22)
- Critical Limit auto-fill value of 42°F (row 22)
- Student pricing grid structure / school-level labels (row 23)
- Inventory Info tab contract detail column names (row 24)
- Editability locking trigger events (row 25)

---

## Handoff checklist

- [x] Mapper inventory reviewed (39 matched features, 8 unmatched, 9 cross-module)
- [x] Factcheck report reviewed (37 verified, 3 discrepancies, 14 unsupported, 3 ambiguous)
- [x] Template constraints checked (1-page, 6 sections flat, 2-column table, all features present)
- [x] Merge pass complete — 39 features compressed to 25 rows; merge rules documented above
- [x] [TO VERIFY] items catalogued — Writer must mark these in draft, not assert them
- [x] Discrepancy D1 (Yield Factor location) surfaced in Gotcha 5 and row 13 — Writer must not follow presenter's Ingredient Info workflow for Yield Factor
- [x] Ambiguous item A1 (custom allergen Family Hub toggle) excluded — no AC support
- [x] Density estimate complete — 685 words, upper edge of safe range; compression levers documented
- [x] SME fact-check can proceed — gotchas 1–5 are all cited; [TO VERIFY] items do not block TLDR draft but should be resolved before publish
- [x] Writer has enough to generate — full feature table, workflow bullets, gotcha text, and cross-module links provided
