## Content Plan — Item Management: Creating Food and Non-Food Items — Long-form Guide

### Template: Long-form (~20 pages, 2,500–6,000 words)
### Source transcript: `raw/transcripts/20260529-070600-item-management-2026-05-28-item-management-create-items-training.md`
### Target audience: District Admin, Nutrition Manager, Food Service Director (Brunswick County Schools onboarding cohort)

---

## Planning notes

This is a long-form guide. The selection rule is: **all features included**. No feature is omitted without an explicit reason. Cross-module items get one line + link placeholder. Features whose specifics are unsupported in AC get `[TO VERIFY]` markers. SME discrepancies from the Mapper are carried forward as must-handle items in the draft.

39 matched features + 9 cross-module references → all 39 features appear in the guide. 8 unmatched items are reviewed below; 5 are excluded (presenter-uncertain or unconfirmed), 3 are included as `[TO VERIFY]` or discrepancy callouts.

---

## Section 1: Overview

### Included features
- Module purpose: creation and configuration of food and non-food items in SchoolCafé 2.0 [transcript: 00:00–00:52]
- Scope statement: Item Management as the source-of-truth record; downstream effects on Inventory, Menus, POS, Family Hub, and Production [transcript: 00:00, 34:08–34:45]
- The two item types (food vs. non-food) and why they differ in complexity [transcript: 00:52–01:24]
- The creation sequence (Item card → Units card → tabs) as the structural thread [transcript: 03:38–03:50]

### Depth
4–6 sentences per template spec. Name the two item types, name the downstream modules affected (one line each — not deep-dived), and state the outcome a user is trying to reach (a fully configured item that is Inventory Ready and optionally a Direct Menu Item).

### Ticket citations
None required in Overview — this is framing, not a factual claim. Any downstream module reference is cross-module (one line only; see Related Content section).

### Transcript anchors
[00:00]–[00:52], [34:08]–[35:00]

### Cross-module refs introduced here
Inventory, Menus, POS, Family Hub, Production — named only; not elaborated. All resolve to Related Content (Section 9).

---

## Section 2: Roles and Permissions

### Included features
- District Admin: creates and edits items, configures pack sizes, enters costing, manages GTIN, configures allergens, sets up Menu Info, sets POS Pricing [transcript: 01:24–38:42, passim; roles listed in Mapper inventory col "Roles Mentioned"]
- Nutrition Manager: enters Nutrient Details, Contribution Info, Allergen Info, configures Menu Item Serving Exceptions [transcript: 18:55–23:10, 27:55–28:18; Mapper rows 18, 20, 23, 24, 30]
- Food Service Director: audience role per transcript metadata; overlap with District Admin for creation tasks [mapper-metadata.json: audience_roles]
- Custom Allergen configuration: District Admin only (NXT-24128 AC: "A Custom allergens option is added under IM configuration area") [Mapper row 25]

### Depth
Moderate table: Role → Actions → Relevant tickets. Not a permissions-matrix deep-dive (no granular CRUD rules found in AC for most tickets). Where AC is silent on role gating, note "role not explicitly restricted in AC — confirm in system" as `[TO VERIFY]`.

### Ticket citations
NXT-24128 (Custom Allergen config entry point — role-gated to IM Configuration access)
NXT-37815 (Inventory Info tab edit mode — District Admin context in transcript)
NXT-43239 (Nutrient Details — Nutrition Manager role in Mapper row 20)
NXT-30102 (Contribution Info — Nutrition Manager + District Admin in Mapper row 23)
NXT-54229 (Menu Serving and Exceptions — Nutrition Manager + District Admin in Mapper row 30)

### Transcript anchors
[00:52] (scope framing), [18:55] (Nutrient Info — Nutrition Manager context), [21:52]–[22:20] (Contributions), [23:10]–[24:02] (Custom Allergen — District Admin navigation)

### [TO VERIFY] notes
Role-gating rules (who can create vs. view-only) are not explicitly in any AC text. The Writer should include a `[TO VERIFY: confirm whether Nutrition Manager can create items or is view/edit-only on food-specific tabs]` marker.

---

## Section 3: Prerequisites

### Included features
The following must be in place before item creation is meaningful:

1. **Item Category, Storage Category, Valuation Group lookups populated** — Required dropdowns; if empty, the three fields can't be filled. AC: NXT-30037 "If not skipping, require a value for all 3 dropdowns." [transcript: 02:22–02:50]
2. **Custom Allergens configured** (if district uses non-standard allergens) — Must exist before they can be assigned to an item. NXT-24128 AC confirms the configuration entry point. [transcript: 23:10–23:55]
3. **HACCP Processes configured** — HACCP Process selection on the Steps card pulls from configured processes; "No Cook / Same Day Service / Complex Food" listed by presenter are defaults but configurable. NXT-36583 Description: "reflects configured processes." [transcript: 28:35–28:58] → `[TO VERIFY: confirm whether HACCP processes are district-configurable or system-fixed]`
4. **POS module configured** (if setting POS Pricing) — Tax rate configuration and price logic referenced by presenter at [31:20]–[31:48] as outside Item Management. Cross-module prerequisite.
5. **Inventory module setup** (if using Inventory Readiness) — Contracts, vendor info, and receiving live in Inventory module, not IM. NXT-40479 AC confirms the read-only contract card pulls from Inventory. [transcript: 32:05–32:50]
6. **User login credentials** — Noted in transcript as a recent setup issue for attendees [transcript: 00:28]. Mention as a practical prerequisite; no ticket citation.

### Depth
Bulleted list with one-sentence explanation per item. Mark cross-module prerequisites with one line + link placeholder.

### Ticket citations
NXT-30037, NXT-24128, NXT-36583, NXT-40479

### Transcript anchors
[00:28], [02:22], [23:10], [28:35], [31:35], [32:05]

---

## Section 4: Full Workflows

This is the core of the long-form guide. 10 subsections, structured to follow the actual creation sequence Sarah demonstrated. Non-food workflow first (simpler), then food workflow (builds on non-food). Within food, tabs are covered in the order Sarah covered them.

### 4.1 Creating a Non-Food Item (end-to-end workflow)

**Purpose:** Create a supply/non-consumable item (cups, trays, napkins, gloves) ready for Inventory.

**Features in this subsection:**
- +NEW button → Item Details page / Item card [Mapper row 1; NXT-30036, NXT-30037; transcript 01:24–03:38]
- Item Description (required, 250-char) [Mapper row 2; NXT-30036 AC: "Require Description"; transcript 02:01]
  - `[TO VERIFY: 250-char limit stated by presenter at [02:01]; in NXT-30036 Description only, not AC]`
- Item Category, Storage Category, Valuation Group (required for Inventory use) [Mapper row 2; NXT-30037 AC: "If not skipping, require a value for all 3 dropdowns"; transcript 02:22]
- Tags, Brand Name, Manufacturer, Product Code (optional) [Mapper row 3; NXT-30036 AC: "Provide Tags field; Provide the identifying information fields"; transcript 02:50]
- SAVE → Units card appears [transcript 03:38]
- Food/Non-Food selection → NON-FOOD disables serving sizes [Mapper row 4; NXT-35898 AC: "Provide Food item and Fluid item questions"; transcript 04:15–04:30]
- +PACK button, Higher/Lower prompt, Description, Sub-Qty, Weight (optional for non-food) [Mapper row 6; NXT-37110 AC: "Provide the ability to add pack size units"; transcript 03:50–07:05]
- Three-tier maximum — +PACK grays out after third tier [Mapper row 7; NXT-37110; transcript 07:05–07:30]
  - `[TO VERIFY: three-tier cap stated at [07:05]; NXT-37110 AC does not explicitly state the cap — in Description only]`
- Unit Identifiers: P badges (pack), BU badge (base unit) [Mapper row 8; NXT-37109 AC: "Populate the Identifiers column with various icons"; transcript 07:30–07:52]
  - `[TO VERIFY: "P" and "BU" badge labels not in NXT-37109 AC; in Description mockups only]`
- Missing Costing alert → enter cost for one unit → system scales to others [Mapper row 9; NXT-37568 AC: "Provide an optional Costing step"; transcript 07:52–08:52]
  - `[TO VERIFY: divide-down formula ($80 → $4 → $0.16) is from Description of NXT-37568, not AC]`
- Manage Costing button replaces Missing Costing alert after save [Mapper row 10; NXT-37568; transcript 09:05]
  - `[TO VERIFY: "Manage Costing" button label from Description only, not in NXT-37568 AC]`
- Inventory Ready flag / green flag + Publish toggle auto-enable [Mapper row 11; NXT-37111 AC: "Provide a step to confirm Inventory info"; NXT-53530 AC: "Always display the inventory readiness banner"; transcript 09:05–09:18]
- GTIN/UPC entry per pack size, 8–14 digits, barcode icons [Mapper row 12; NXT-37815 AC: "Allow 8-14 digits in the GTIN field (UPC: 12 digits; GTIN: 14 digits)"; transcript 09:18–09:48]
- Whole Numbers vs. Decimals setting [Mapper row 13; NXT-33518 AC: "Provide an option in the context of the new Units card to determine whether the Base Unit can be counted in decimals"; transcript 09:48–10:20]
  - Note: NXT-33518 Jira module field = "Inventory" but is child of NXT-36067 (IM epic); usable per Mapper tier_caution.
- Base Unit auto-assignment (lowest pack size = BU by default) [Mapper row 14; NXT-37111; transcript 07:30, 38:05–38:30]
- Images & Documents card — drag-and-drop, "Use as" dropdown [Mapper row 16; NXT-41273 AC: full Use As list; transcript 10:28–11:55]
  - `[TO VERIFY: "5 MB per file" and specific file types (JPEG, PNG, PDF, Word, spreadsheets) stated by presenter at [11:02]; NOT in NXT-41273 AC or RN. RN says "up to 10 files" but no size limit stated]`
- Editability locking: Base Unit and Whole Numbers/Decimals locked once item used in Inventory [Mapper row 39; NXT-54229 AC mentions "changing sub-quantities" under long-term editing; transcript 37:35–38:05]
  - `[TO VERIFY: explicit locking language is in Description of NXT-37111 and NXT-54229, not in AC text]`

**Depth:** Full step-by-step, numbered steps, screen names, what user sees at each step. Use Sarah's Dixie Cup example (12 oz, Box > Sleeve > Cup, $80 costing) — this is the primary teaching example for non-food.

**Ticket citations (primary):** NXT-30036, NXT-30037, NXT-35898, NXT-37110, NXT-37109, NXT-37568, NXT-37111, NXT-53530, NXT-37815, NXT-33518, NXT-41273, NXT-54229

**Transcript anchors:** [01:24]–[11:55], [37:35]–[38:30]

---

### 4.2 Creating a Food Item — Item Card and Units Card

**Purpose:** Set up the item record and unit structure for a consumable food item. Covers the extra food-specific steps on the Units card before reaching the nutrition/allergen/menu tabs.

**Features in this subsection:**
- Same Item card process as non-food (Description, Category, etc.) — refer back to 4.1; note Sarah's Yogurt example [transcript 12:12–12:50]
- Food/Non-Food selection → FOOD; then Fluid/Non-Fluid question (food-only) [Mapper row 5; NXT-35898 AC: "if Yes, ask Fluid Item; if Yes, switch to 'Volume' for Serving Sizes"; transcript 12:50–13:25]
  - Examples: yogurt = Non-Fluid (grams); juice/milk = Fluid (milliliters) [transcript 13:00–13:25]
- +SERVING button (food-only): Amount, Description, Weight/Unit [Mapper row 17; NXT-35898 AC: "Provide a button for adding a Serving Size unit"; transcript 13:52–14:12]
  - Recommended order: serving sizes first, then pack sizes [transcript 18:35–18:48]
- Tabs (Nutrient Info, Menu Info, Inventory Info) appear but are grayed out until Units card saved [transcript 14:12–14:30]
- +PACK for food item pack sizes (same mechanics as non-food) [transcript 14:30–14:50]
- Link servings to pack sizes: Inventory Eligibility alert, Sub-Qty on serving row [Mapper row 19; NXT-37441 AC: "Provide Sub-Qty on the Serving Size row in valid scenarios; Trigger Inventory readiness based on proper pack-serving links"; transcript 15:02–16:08]
  - This is the **highest-priority ticket in the inventory** (NXT-37441 = Highest)
  - Example: 16 yogurts in a carton → Sub-Qty: 16 [transcript 15:42–16:08]
- Costing for food item (same process, applied after serving-pack link) [NXT-37568; transcript 16:08–16:48]
- Base Unit auto-default (lowest pack = BU) [NXT-37111; transcript 16:48–17:05]
- Base Unit promotion: serving size promoted to BU for food items (dual unit workflow) [Mapper row 15; NXT-40778 AC: "Prompt users with a dedicated 'Merge' button when they are attempting to create a unit which is likely intended to be a dual unit"; transcript 17:05–17:42]
  - AC uses "Merge" language; presenter called it "promote." Both terms should appear in the draft.
  - Non-food items cannot promote (no serving sizes) — confirmed at [38:30]
- GTIN, Whole Numbers/Decimals, Images & Docs — same as non-food; cross-reference section 4.1
- Editability locking after Inventory use — same constraint as non-food [transcript 37:35–38:05]

**Depth:** Full step-by-step. Use Sarah's Yoplait Strawberry Yogurt, 4 oz example throughout. Numbered steps where order matters (serving-first recommendation is a soft recommendation, not a hard constraint — note this).

**Ticket citations (primary):** NXT-35898, NXT-37441, NXT-37568, NXT-37110, NXT-37111, NXT-40778, NXT-53530

**Transcript anchors:** [12:12]–[17:52], [18:35]–[18:48]

---

### 4.3 Nutrient Details (Nutrient Info tab)

**Purpose:** Enter FDA-standard nutritional data for a food item; required for menu planning compliance.

**Features in this subsection:**
- Serving size display in tab header with oz-to-grams auto-conversion [Mapper row 18; NXT-43239; transcript 18:55–19:12]
- Nutrient Details entry: required fields (asterisk), optional fields, Missing Value checkbox [Mapper row 20; NXT-43239 AC: "Update business rules: Vitamin A, Vitamin C, Moisture, Ash changed to optional; Moisture and Ash do not require a 'Missing' checkbox"; transcript 19:12–20:25]
  - Key discrepancy to surface: NXT-43239 AC states Vitamin A and Vitamin C are NOW OPTIONAL; presenter described them in the asterisk-required flow without calling them out as optional. Draft must surface this.
  - Auto-zero of nested nutrients: "if Total Fat is 0, Sat Fat and Trans Fat auto-zero" — NXT-43239 AC confirmed [transcript 20:25 area — not explicitly called out by presenter but AC-confirmed behavior; include with AC citation]
  - Per 100g column and % auto-calculation: presenter noted at [20:25] but not in AC; from Description only → `[TO VERIFY: per-100g auto-calc behavior — not in NXT-43239 AC; in Description only]`
- (M) marker display for Missing Value entries [transcript 20:25–20:42]
- Nutrient Info tab stays Incomplete if required fields not entered; item still usable for Inventory [transcript 35:25–35:35]
- Nutrient data used in menu planning (cross-module) [transcript 35:25–35:35; C4] → one line + link to Menu Planning module

**Depth:** Full — walk through the nutrient entry screen, identify required vs. optional fields, explain the Missing Value checkbox behavior, include the Vitamin A/C discrepancy callout.

**Ticket citations:** NXT-43239 (primary)

**Transcript anchors:** [18:55]–[20:42], [35:25]–[35:35]

**SME must-handle item:** Discrepancy — presenter did not call out Vitamin A and Vitamin C as optional (only described the asterisk pattern). NXT-43239 AC explicitly makes them optional. Writer must include a `> [!warning] Discrepancy` callout quoting both.

---

### 4.4 Ingredient Info Card

**Purpose:** Record edible yield, sub-ingredients, recipe directions, and domestic compliance flags for food items.

**Features in this subsection:**
- Edible Yield Factor [Mapper row 21; transcript 20:42–21:00]
  - **Critical SME discrepancy:** Presenter described Edible Yield Factor as being on the Ingredient Info card [20:42]. NXT-47249 AC explicitly states it was MOVED to the Units card (per-serving) and removed from Ingredient Info. Writer must include a `> [!warning] Discrepancy` callout: presenter described old location; current AC places it on Units card.
  - NXT-47249 AC: "Make Yield Factor configurable on each serving in the Units card; Remove Yield Factor from Ingredient Info card"
  - The correct current behavior (Yield Factor on Units card, per serving) must be the primary instruction; the presenter's description gets a discrepancy callout.
- Sub Ingredients [Mapper row 21; NXT-30100 Description: "Sub Ingredients (comments popup, up to 500 chars)"; transcript 21:00–21:22]
  - `[TO VERIFY: 500-char limit from NXT-30100 Description only, not AC]`
- Standard Recipe Directions [Mapper row 21; NXT-30100 Description; transcript 21:00–21:22]
  - Cross-module reference: directions show on multi-item recipes (Recipes module) [C2; transcript 21:00]
  - `[TO VERIFY: Standard Recipe Directions behavior — from NXT-30100 Description only, not AC]`
- Locally Grown checkbox [Mapper row 22; NXT-30100; transcript 21:22–21:42]
  - `[TO VERIFY: checkbox is in NXT-30100 Description only, not AC]`
- Buy American checkbox and exemption letter upload interaction [Mapper row 22; transcript 21:22–21:42]
  - Business rule stated by presenter: "If Buy American is checked, you can't upload an exemption letter." This business rule is NOT in any AC text. NXT-41273 AC confirms "Buy American Exemption Letter" as a document type in Images & Docs. The interaction/disabling rule is Description-level only.
  - `[TO VERIFY: the rule that checking Buy American disables the exemption letter upload — not found in any AC text]`

**Depth:** Full — walk through each field, include both discrepancy callouts (Yield Factor location, Buy American rule).

**Ticket citations:** NXT-30100, NXT-47249, NXT-41273

**Transcript anchors:** [20:42]–[21:42]

**SME must-handle items:**
1. Edible Yield Factor placement: presenter said Ingredient Info card; NXT-47249 AC says Units card. Must be resolved before publish.
2. Buy American / exemption letter interaction: business rule not in AC; must be confirmed or marked `[TO VERIFY]`.

---

### 4.5 Contribution Info Card

**Purpose:** Record meal pattern credits (Meat/Meat Alternates, Grains, Vegetables, etc.) for a food item.

**Features in this subsection:**
- Contribution Info card entry via slideout panel [Mapper row 23; NXT-30102 AC: "Add/Edit Contributions in the slideout; Allow user to skip for now"; transcript 21:52–22:20]
- Meal pattern components — display and entry [Mapper row 23; NXT-37216 AC: "List each applicable component on a dedicated row within the card (sequence: Fruits, MMA, Grains, Milk, Veg)"; transcript 21:52–22:20]
  - Specific field names (Meat/Meat Alt, Grains, Veg, etc.) from NXT-37216 AC confirmed at sequence level; detailed sub-field names for each component are in NXT-30102 Description only → `[TO VERIFY: confirm exact field names and sub-categories for each meal pattern component]`
  - NXT-37216 AC also covers contribution chip display (color-coded, icon, cups vs. oz equivalent) — include in the Key Fields section rather than step-by-step
- Skip option: Contribution Info does not block proceeding to next section [NXT-30102 AC: "Allow user to skip for now"; transcript implied]
- Yogurt example: 1 oz equivalent of Meat/Meat Alternates [transcript 21:52–22:20]

**Depth:** Full — walk through slideout entry, yogurt example, explain the skip option. Note the chip display is covered in Key Fields (Section 5).

**Ticket citations:** NXT-30102, NXT-37216

**Transcript anchors:** [21:52]–[22:20]

---

### 4.6 Allergen Info and Custom Allergen Configuration

**Purpose:** Record allergen information for a food item; configure custom allergens at the district level.

**Features in this subsection:**
- Allergen Info card entry via slideout [Mapper row 24; NXT-30103 AC: "Load the Allergens section; Can create or enter allergen without having nutrient/contribution information"; transcript 22:20–23:10]
- Allergen Feature Disclaimer [NXT-30103 Description mentions "Update Allergen Feature Disclaimer"; transcript 22:20–22:42]
  - `[TO VERIFY: Disclaimer content/language — mentioned in NXT-30103 Description as "replace PrimeroEdge with SchoolCafe" but AC only says "Load the Allergens section"]`
- Standard allergen list display [NXT-41275 AC: prioritized order: Contains, Processed, May Contain, Free From; transcript 22:42–23:10]
  - Standard allergen names (Crustacean Shellfish, Egg, Fish, Gluten, Milk, Peanuts, Sesame, Soy, Tree Nuts, Wheat) — presenter-stated at [22:42]; in NXT-30103 Description only, not AC → `[TO VERIFY: confirm standard allergen list matches system]`
  - Icons: octagon alert/red for Contains; circle alert/orange for May Contain/Processed; green for Free From [NXT-41275 AC confirms icon logic at concept level]
- Custom Allergen creation workflow [Mapper row 25; NXT-24128 AC: full entry point, result grid, slideout card fields, validation; transcript 23:10–23:55]
  - Navigation: Item Management → Configuration → Item Configuration → Custom Allergens dropdown → APPLY → +NEW
  - Required fields: Custom Allergen Description (free text), Data Source (Local only)
  - Validation: no duplicates, "Custom Allergen already in use, please use a different Custom Allergen name"
  - "Show on Family Hub menus" toggle: presenter mentioned at [23:28]; NOT in NXT-24128 AC → `[AMBIGUOUS: presenter said "you can toggle on whether it shows on Family Hub menus" at [23:28]; no corresponding AC text found. Include as [TO VERIFY]]`
  - Export: PDF format per NXT-24128 AC [include in Reports section 6]
- Adding custom allergen to an item: +ADD CUSTOM ALLERGEN, select from dropdown, set allergen form, ADD, SAVE [transcript 23:55–24:02]
- Skip option: allergens can be created/entered without nutrient or contribution info first [NXT-30103 AC]

**Depth:** Full — two sub-workflows: (a) applying standard allergens to an item, (b) creating and then applying a custom allergen. Include discrepancy callout for Family Hub toggle.

**Ticket citations:** NXT-30103, NXT-41275, NXT-24128

**Transcript anchors:** [22:20]–[24:02]

**Unmatched item disposition:** U5 (Family Hub toggle) → included as `[TO VERIFY / AMBIGUOUS]`, not as confirmed feature. U6 (bulk allergen import) → excluded entirely; presenter said "I'm honestly not sure of the details on that" at [24:05]. No confirmed feature.

---

### 4.7 Menu Info Tab — Creating a Direct Menu Item

**Purpose:** Turn a food item into a Direct Menu Item (DMI) that can be placed on menus and served as a reimbursable meal.

**Features in this subsection:**
- Menu Info tab initial state: Disabled status before configuration [Mapper row 26; NXT-39594; transcript 24:30–24:55]
  - `[TO VERIFY: "Disabled status" is from NXT-39594 Description/mockups; not in AC]`
- CREATE MENU ITEM trigger on Units card banner [transcript 25:18–25:28]
- Menu Item fields (required): Menu Item Name, Button Name English, Menu Item Category [Mapper row 27; NXT-30155 AC: structural confirmation; transcript 25:28–27:12]
  - Field-level enumeration is from NXT-30155 Description and presenter; AC confirms tab/section structure only. Required field status from presenter-demonstrated behavior → `[TO VERIFY: confirm which Menu Item fields are system-required vs. recommended]`
- Menu Item fields (optional): Max Days, Marketing Name, Button Name Spanish, Meal Type, Leftover Category, Tags, Prep Site Item, Show in Summary, POS Entree [Mapper row 27; transcript 25:28–27:12]
  - Marketing Name and Description: appear on Family Hub (cross-module) [C5; transcript 26:15]
  - Max Days and Leftover Category: feed Production Records (cross-module) [C7; transcript 25:28]
  - POS Entree flag: feeds POS module; reimbursable meal eligibility [C6; transcript 26:48–27:12]
- Show on POS toggle → enables POS Pricing tab; tab renamed "MENU & POS INFO" [Mapper row 28; NXT-39594 AC: "a 'Show on POS' toggle will control the presence of the POS attributes and Pricing table"; transcript 27:12–27:32]
  - Tab rename "MENU & POS INFO" is from NXT-39594 Description/presenter only → `[TO VERIFY]`

**Depth:** Full — step-by-step through the CREATE MENU ITEM workflow, each field explained, cross-module callouts (Family Hub, Production, POS) as one-line references.

**Ticket citations:** NXT-39594, NXT-30155

**Transcript anchors:** [24:30]–[27:32]

---

### 4.8 Menu Item Serving, Additional Menu Servings, and Exceptions

**Purpose:** Add alternate serving sizes for the menu item and configure which school groups may not receive it.

**Features in this subsection:**
- MI badge on Units card (Menu Item Serving indicator) [Mapper row 29; NXT-37109 AC; transcript 27:32–27:55]
- +MENU SERVING button (add scaled menu servings) [Mapper row 29; NXT-40447 AC: "Provide the ability to add additional serving sizes for the Menu Item; Within the MI Units edit mode, provide a '+Menu Serving' button"; transcript 27:32–27:55]
  - New serving row: Amount and Description editable; pre-loaded from original; scales weight/volume automatically
  - NXT-54229 AC confirms: "Menu Serving and Exceptions should be available once the item is a Menu Item"
- Menu Item Serving Exceptions (not-served by school level / meal pattern group) [Mapper row 30; NXT-54229 AC; transcript 27:55–28:18]
  - Workflow: Edit Units card → EXCEPTIONS → assign Meal Pattern & Serving Group → NOT SERVED → set group
  - Detailed UI steps are presenter-stated at [27:55]; not in any AC text → `[TO VERIFY: exact UI steps for Exceptions — workflow described by presenter at [27:55] but not found in NXT-54229 AC]`

**Depth:** Full — step-by-step for both sub-workflows (add menu serving, configure exceptions). Include the NXT-54229 availability rule (must be a Menu Item first).

**Ticket citations:** NXT-40447, NXT-54229, NXT-37109

**Transcript anchors:** [27:32]–[28:18]

---

### 4.9 Steps Card — HACCP and Recipe Steps

**Purpose:** Configure food safety (HACCP) process, control points, and recipe directions for a food item.

**Features in this subsection:**
- ENABLE RECIPE button on Steps card [Mapper row 31; NXT-36583; transcript 28:18–28:35]
- HACCP Process selection (Step 0): No Cook / Same Day Service / Complex Food [Mapper row 31; NXT-36583 AC: "Add a small selection for Recipe HACCP Process"; transcript 28:35–28:58]
  - Process names (No Cook, Same Day Service, Complex Food): in NXT-36583 Description; not enumerated in AC → `[TO VERIFY: confirm current HACCP process names]`
- Pre-Preparation Instructions, Prep Time, Cook Time [Mapper row 32; transcript 28:58–29:10]
  - These sub-fields are from NXT-36583 Description only, not AC → `[TO VERIFY: confirm Pre-Prep Instructions, Prep Time, Cook Time are on the Steps card]`
- Recipe step add (+ADD, step directions) [Mapper row 33; transcript 29:10–29:42]
  - Step add and drag-and-drop reorder are presenter-demonstrated; not in NXT-36583 AC → `[TO VERIFY: confirm +ADD and drag-and-drop reorder behavior for recipe steps]`
- HACCP Control Points: +ADD → Control Point → select type → Critical Limit auto-fill → Corrective Action [Mapper row 34; NXT-36742 AC: "Allow CCPs to be added to the recipe like steps; Allow added CCPs to be edited for Critical Limit and Corrective Action"; transcript 29:10–29:42]
  - Cold Hold example: auto-fills "≤42°F" Critical Limit and a Corrective Action. Auto-fill from configured defaults: in NXT-36742 Description. AC confirms editability.
  - `[TO VERIFY: "≤42°F" value for Cold Hold CCP Critical Limit — from NXT-36742 Description / presenter only; not in AC]`
- HACCP process change warning: changing process clears associated CCPs → warn user [NXT-36583 Description; not in AC] → `[TO VERIFY]`

**Depth:** Full — step-by-step for HACCP setup and adding control points. Use yogurt No Cook example from transcript. Include all `[TO VERIFY]` markers for Description-only details.

**Ticket citations:** NXT-36583, NXT-36742

**Transcript anchors:** [28:18]–[29:55]

---

### 4.10 POS Pricing Tab

**Purpose:** Set student and adult pricing for Point of Sale transactions.

**Features in this subsection:**
- Students pricing grid: Free/Reduced/Paid/Second Meal × Elementary/Middle/High/Alternative [Mapper row 35; NXT-30155 AC: "Separate pricing for Students and Adults with tabs"; transcript 29:55–30:55]
  - Grid structure (student types × site types): in NXT-30155 Description; AC confirms tab separation only → `[TO VERIFY: confirm exact student type and site type column labels]`
- Set All Prices shortcut [NXT-30155 AC: "Provide the 'Set All Prices' option which can be used on one tab at a time (in Edit only)"; transcript 30:15–30:55]
- Allow Sale toggle: auto-enables when price entered; can be manually disabled [Mapper row 35; transcript 30:55–31:08]
  - Allow Sale toggle behavior: from presenter only; not in NXT-30155 AC → `[TO VERIFY]`
- Adults tab: staff, visitor, program adult pricing [Mapper row 36; NXT-30155 AC: "Separate pricing for Students and Adults with tabs"; transcript 31:08–31:20]
- Taxable checkbox — Adults tab only [Mapper row 37; NXT-58442 AC: "Only display the Taxable option when the Adult tab is selected on POS Pricing (for both view and edit mode; note: POS does not consider tax for students)"; transcript 31:20–31:48]
  - Presenter explicitly stated uncertainty about how sales tax calculation works in 2.0 at [31:35]: "I'm not sure how the sales tax calculation works in 2.0." This is an admitted unknown — exclude the calculation detail; include a `[TO VERIFY: how tax rate is configured and applied — presenter expressed uncertainty at [31:35]]`
- DM Reimbursable Meal: removed from POS Only Items per NXT-58442 AC — include as a note/exception (it was previously visible, now hidden)

**Depth:** Full — walk through both tabs, Set All Prices shortcut, Taxable checkbox, and the DM Reimbursable Meal removal. No invented calculation specifics.

**Ticket citations:** NXT-30155, NXT-58442

**Transcript anchors:** [29:55]–[31:48]

---

### 4.11 Inventory Info Tab

**Purpose:** View active vendor contracts for the item and access the Inventory module's Contract Items page directly.

**Features in this subsection:**
- Read-only Inventory Item Active Contracts card [Mapper row 38; NXT-40479 AC: "Display a read-only 'Inventory Item Active Contracts' card"; transcript 32:05–32:50]
  - Read-only from IM; editing happens in Inventory module [presenter: 32:05]
  - Contract fields listed by presenter (vendor name, vendor item number, unit, lead time, min/max, current price): in NXT-40479 Description only, not AC → `[TO VERIFY: confirm which contract fields are displayed on the read-only card]`
- Shortcut icon to Inventory Contract Items page (opens in new tab, pre-loaded for item) [NXT-40479 AC: "Provide an icon to open Inventory in a new tab; navigate to the Contract Items page; pre-load the contract for the relevant item"; transcript 32:40]
- Empty state for new items (no contracts yet) [NXT-40479 Description; transcript 32:05–32:15]
- Units card editable from this tab (same as main Units card view) [transcript 32:40–32:50]
  - `[TO VERIFY: whether Units card edit from Inventory Info tab is a distinct feature or just the same Units card — presenter mentioned it at [32:40] but no dedicated ticket found]`

**Depth:** Moderate — describe the read-only card, the shortcut, and the cross-module relationship. Keep cross-module details (contract management, ordering, receiving) to one line each.

**Ticket citations:** NXT-40479

**Transcript anchors:** [32:05]–[32:50]

---

## Section 5: Key Fields and Statuses

### Included features (all important data inputs from all 39 matched features)

**Item card fields**
| Field | Ticket | Required? | Valid values / controls |
|---|---|---|---|
| Item Description | NXT-30036 | Yes | Free text; 250-char limit `[TO VERIFY — Description only]`; no upper-case constraint in AC |
| Item Category | NXT-30037 | Yes (if using Inventory) | Dropdown; populated from district configuration |
| Storage Category | NXT-30037 | Yes (if using Inventory) | Dropdown |
| Valuation Group | NXT-30037 | Yes (if using Inventory) | Dropdown |
| Tags | NXT-30036 | No | Free text multi-value |
| Brand Name | NXT-30036 | No | Dropdown per AC description |
| Manufacturer | NXT-30036 | No | Dropdown per AC description |
| Product Code | NXT-30036 | No | Free text |

**Units card fields and statuses**
| Field / Status | Ticket | Notes |
|---|---|---|
| Food / Non-Food | NXT-35898 | Controls whether serving sizes and fluid question appear |
| Fluid / Non-Fluid (food only) | NXT-35898 | Switches serving size unit: grams (non-fluid) vs. milliliters (fluid) |
| Sub-Qty (pack-to-pack link) | NXT-37110 | Required to link tiers; enables costing scale-down |
| Sub-Qty (serving-to-pack link) | NXT-37441 | Enables Inventory Eligibility; triggers Inventory Readiness |
| Weight (pack size) | NXT-37110 | Optional for non-food; required in specific scenarios |
| GTIN/UPC | NXT-37815 | 8–14 digits; 12 = UPC, 14 = GTIN; shows barcode icon in Identifiers |
| Whole Numbers / Decimals | NXT-33518 | Default: whole numbers; locked after first Inventory transaction |
| Base Unit (BU) | NXT-37111 | Auto-assigned to lowest pack; promotable for food items |
| Missing Costing (status/alert) | NXT-37568 | Appears until cost entered for one unit |
| Inventory Ready (flag/banner) | NXT-37111, NXT-53530 | Always visible; shows state (Ready / Ineligible / Incomplete) |
| Inventory Eligible / Ineligible | NXT-37441 | Determined by pack-serving link; Ineligible = no Sub-Qty link |
| Publish toggle | NXT-53530 | Auto-enables when Inventory Ready; controls item's availability downstream |
| Edible Yield Factor (Units card, per serving) | NXT-47249 | Configurable per serving size; default covers all other measures |

**Identifiers column icons**
| Icon | Ticket | Meaning |
|---|---|---|
| P badge | NXT-37109 | Pack size unit `[TO VERIFY: label "P" from Description/mockup only]` |
| BU badge | NXT-37109 | Base unit `[TO VERIFY: label "BU" from Description/mockup only]` |
| Barcode icon | NXT-37815 | GTIN/UPC assigned |
| MI badge | NXT-37109, NXT-40447 | Menu Item Serving |
| $ icon | NXT-37109 | Unit where cost was manually entered |

**Nutrient Details fields (key business rules)**
| Rule | Ticket | Detail |
|---|---|---|
| Required nutrients | NXT-43239 | Fields with asterisk; enforced on save |
| Vitamin A, Vitamin C | NXT-43239 | NOW OPTIONAL per AC; leaving blank auto-enables "Is Missing" |
| Moisture, Ash | NXT-43239 | Optional; no "Is Missing" checkbox (not on labels) |
| Missing Value (M) marker | NXT-43239 | Flags incomplete data; "(M)" shown in card view |
| 0% Daily Value | NXT-43239 | Valid input; AC explicitly addresses this bug fix |
| Auto-zero nested nutrients | NXT-43239 | Total Fat = 0 auto-sets Sat Fat + Trans Fat; Total Carbs = 0 auto-sets Fiber + Sugar |

**Contribution Info statuses (card display)**
| Display element | Ticket | Detail |
|---|---|---|
| Component row sequence | NXT-37216 | Fruits, MMA, Grains, Milk, Veg — AC-confirmed order |
| Contribution chips | NXT-37216 | Color-coded per component; Cups vs. oz equivalent icon |

**Allergen card statuses**
| Form | Ticket | Icon |
|---|---|---|
| Contains | NXT-41275 | Octagon alert, red |
| Processed (in facility) | NXT-41275 | Circle alert, orange |
| May Contain | NXT-41275 | Circle alert, orange |
| Free From | NXT-41275 | Green "not applicable" icon |

**Item-level statuses**
| Status | Trigger | Ticket |
|---|---|---|
| Inventory Info tab: Incomplete | Units card not yet saved / not linked | NXT-37111 |
| Inventory Ready | Pack sizes + costing + base unit confirmed | NXT-37111, NXT-53530 |
| Inventory Ineligible | Pack and serving not linked (food items) or item explicitly disabled | NXT-37441, NXT-53530 |
| Menu Info: Disabled | Menu Item not yet created | NXT-39594 |
| Missing Costing (alert) | No cost entered for any unit | NXT-37568 |
| Manage Costing (button) | Replaces Missing Costing after cost saved | NXT-37568 `[TO VERIFY: button label]` |
| Locked (Base Unit / Whole Nos.) | First Inventory transaction recorded | NXT-54229, NXT-37111 `[TO VERIFY: locking trigger — in Description only]` |
| Nutrient Info: Incomplete | Required nutrient fields not filled | NXT-43239 |

### Depth
Field-by-field reference table format per template spec. Cite the ticket for each field. `[TO VERIFY]` markers inline for any field whose specifics are Description-only.

### Ticket citations
All tickets listed above.

### Transcript anchors
Cross-reference from Section 4 subsections.

---

## Section 6: Reports and Outputs

### Included features
- **Custom Allergen Configuration export** — PDF format; title "Custom Allergen Configuration"; covers Description and Data Source Name; header: Updated by [User Name], Generated on [System date/time UTC]; footer: Powered by SchoolCafe for [School District Name]; pagination present [NXT-24128 AC; transcript 23:10–23:55]
- **Publish toggle** — item publish to Inventory as the primary output event. Not a report, but the downstream trigger. [NXT-53530; transcript 09:05–09:18]
- **Nutrient analysis (cross-module)** — nutrient data fed to menu planning module for nutrient analysis reports [C4; transcript 35:25–35:35] → one line + link placeholder
- **Preferred Image flags downstream use** — Preferred Inventory Image used in Inventory Ordering cart; Preferred Menu Image used in menu item search and Variety Menu; Preferred Ingredient Image used on Items page and recipe ingredient search [NXT-41273 RN Internal; transcript 11:28–11:55] → note these are outputs consumed by other modules

### Depth
Per template spec: what's in each output, who consumes it, when it's run. The Custom Allergen export is the only standalone report with full AC detail. Others are cross-module outputs (one line each).

### Ticket citations
NXT-24128, NXT-53530, NXT-41273

### Transcript anchors
[09:05], [11:28]–[11:55], [23:10], [35:25]

### Note
No dedicated reporting story found for Item Management itself (items list, item detail report, etc.) other than the allergen configuration export. `[TO VERIFY: are there additional IM reports — e.g., items list export, incomplete items report — not covered in the transcript or matched tickets?]`

---

## Section 7: Exceptions

### Included features (each must cite a ticket)
1. **Base Unit locked after Inventory transaction** — Base Unit and Whole Numbers/Decimals setting locked once item is used in any Inventory transaction (count, receipt, adjustment). Presenter warning at [37:35]. [NXT-54229 Description, NXT-37111 Description; `[TO VERIFY: explicit lock trigger not in AC]`]
2. **Three-tier maximum** — +PACK button grays out after third tier. [NXT-37110 Description; `[TO VERIFY: cap not in AC]`; transcript 07:05–07:30]
3. **Inventory Ineligibility for unlinked food items** — Food items with pack sizes but no linked serving size (no Sub-Qty) are flagged Inventory Ineligible. [NXT-37441 AC: "Trigger Inventory readiness based on proper pack-serving links"; transcript 15:02]
4. **Non-food items: no serving sizes, no base-unit promotion** — Confirmed by AC (NXT-35898: non-food disables serving sizes) and presenter at [38:30].
5. **Vitamin A and Vitamin C now optional** — Previously required; NXT-43239 AC changed this. Presenter did not flag this change in the training session. `[Discrepancy — see Section 4.3]`
6. **Edible Yield Factor location changed** — Moved from Ingredient Info card to Units card per NXT-47249. Presenter described the old location. `[Discrepancy — see Section 4.4]`
7. **DM Reimbursable Meal hidden from POS Only Items** — NXT-58442 AC: "Remove the 'DM Reimbursable Meal' option from POS Only Items (hide in view/edit mode; do not delete code; set flag to False)." Not demonstrated in transcript; AC-sourced.
8. **GTIN invalid entry alert** — 8–14 digits only; "anything else = invalid; show alert icon for invalid data" [NXT-37815 AC; transcript 09:18–09:48]
9. **Skip option for Nutrient, Contribution, Allergen sections** — Each section allows "skip for now" without blocking progression. [NXT-30102 AC, NXT-30103 AC; confirmed in transcript]
10. **Nutrient required fields enforced on save** — Asterisk fields are enforced when saving the Nutrient Details card; but Nutrient Info tab Incomplete status does not block Inventory use. [NXT-43239; transcript 35:02–35:35]
11. **Custom Allergen deactivation blocked if in use** — "User can deactivate Custom Allergen only if no items/recipes/menus are using it (confirmation message required)" [NXT-24128 AC]
12. **Duplicate description or weight hard stop on pack/serving** — "Implement a hard stop warning for matching Description or Weight/Volume (exact same description or weight between pack and serving)" [NXT-40778 AC]
13. **Soft stop for pack/serving weight within 15%** — "Implement a soft stop warning if Weight/Volume is within 15% of each other (warning with Merge prompt)" [NXT-40778 AC]

### Depth
One paragraph per exception: symptom/scenario, what the system does, ticket citation. Discrepancy callouts (5 and 6) reference the `> [!warning]` blocks in their respective workflow sections.

### Ticket citations
NXT-54229, NXT-37111, NXT-37110, NXT-37441, NXT-35898, NXT-43239, NXT-47249, NXT-58442, NXT-37815, NXT-30102, NXT-30103, NXT-24128, NXT-40778

### Transcript anchors
[07:05], [09:18], [15:02], [20:42], [35:02], [37:35]

---

## Section 8: Troubleshooting

### Included features (sourced from transcript Q&A and known-issue tickets only)

1. **"Tabs are grayed out after adding serving sizes"**
   - Cause: Units card has not been saved yet. Tabs (Nutrient Info, Menu Info, Inventory Info) become active only after saving the Units card.
   - Source: Transcript behavior at [14:12]–[14:30]; NXT-35898 AC.

2. **"Inventory Ready alert says servings and packs must be linked"**
   - Cause: No Sub-Qty entered on the serving size row linking it to a pack size.
   - Fix: Click Inventory Ready alert → Edit → enter Sub-Qty on serving row → SAVE.
   - Source: NXT-37441 AC; transcript [15:22]–[16:08].

3. **"Nutrient Details won't save — required field error"**
   - Cause: One or more asterisk-required nutrient fields are blank (without a Missing Value checkbox).
   - Fix: Either enter the value or check the Missing Value checkbox.
   - Source: NXT-43239 AC; transcript [35:02]–[35:25].

4. **"Can I change the sub-quantity if I entered the wrong amount?"**
   - Caution: Long-term editing of sub-quantities is restricted once the item is used in Inventory. NXT-54229 AC explicitly lists "changing sub-quantities (including inventory-able servings and dual units)" under long-term editing restrictions.
   - Source: NXT-54229 AC; transcript [37:35] (locking warning).
   - `[TO VERIFY: what is the exact error or restriction message shown when sub-qty change is attempted after Inventory use?]`

5. **"What if we receive a box with fewer sleeves than the sub-quantity says?"** (Tom's question at [10:43])
   - Answer: Sub-quantity should reflect the standard pack specification (what's on the spec sheet). Short-ship discrepancies are handled during receiving in Inventory module, not in item setup.
   - Source: Transcript Q&A [10:43]–[11:00]; no specific ticket (operational guidance, not a system feature).

6. **"Vitamin C showing as required but it isn't on the label"**
   - Clarification: As of NXT-43239, Vitamin A and Vitamin C are no longer required. Leaving them blank will auto-enable "Is Missing." Vitamin C does not need a manual Missing Value check.
   - Source: NXT-43239 AC; `[Discrepancy — presenter's training did not call out this change explicitly]`.

7. **"Missing Costing alert won't go away after entering a price"**
   - Cause: Cost was entered but not saved (checkmark/SAVE not clicked for the costing step).
   - Source: Presenter walkthrough at [08:08]–[08:52]; NXT-37568 AC.
   - `[TO VERIFY: confirm whether there is a specific save step vs. an auto-save on the costing screen]`

8. **"Custom allergen duplicate error"**
   - Cause: Attempting to create a custom allergen with the same description as an existing one.
   - System response: "Custom Allergen already in use, please use a different Custom Allergen name"
   - Source: NXT-24128 AC (verbatim).

### Depth
Symptom → cause → fix format per template. Only items with a ticket or Q&A transcript source. 8 items above; Writer should not add troubleshooting items without a source.

### Ticket citations
NXT-35898, NXT-37441, NXT-43239, NXT-54229, NXT-37568, NXT-24128

### Transcript anchors
[10:43], [14:12], [15:22], [35:02], [37:35]

---

## Section 9: Related Content

### Cross-module references (one line + link placeholder each)

Based on C1–C9 from the Mapper's cross-module inventory:

1. **Inventory module** — Manages contracts, receiving, stock counts, and ordering; the Item Management record is the source of truth that Inventory consumes. `[[link: Inventory module guide]]` [C1, C8]
2. **Recipes / Menu Planning** — Serving sizes defined in Item Management are the basis for ingredient quantities in recipes; Sub Ingredients and Standard Recipe Directions on the Ingredient Info card appear in recipe views. `[[link: Recipes module guide]]` [C2, C3]
3. **Menu Planning** — Nutrient data entered on the Nutrient Info tab is consumed by menu planning for nutrient analysis. `[[link: Menu Planning module guide]]` [C4]
4. **Family Hub** — Marketing Name and Description (Menu Info tab), and the custom allergen "Show on Family Hub menus" toggle (if confirmed), feed the parent-facing portal. `[[link: Family Hub module guide]]` [C5]
5. **POS (Point of Sale)** — Button Name (English/Spanish), POS Entree flag, and POS Pricing configured in Item Management feed the POS touchscreen display and transaction logic. `[[link: POS module guide]]` [C6]
6. **Production Records** — Max Days and Leftover Category on the Menu Info tab affect how items are carried over or discarded on production records. `[[link: Production Records module guide]]` [C7]
7. **PrimeroEdge (legacy)** — Sarah referenced PrimeroEdge for comparison at several points; these are legacy contrasts, not SchoolCafé 2.0 features. No link needed; mention only to avoid confusion.

### Unmatched items excluded from content (logged here per long-form "no omission without reason" rule)
- **U6 — Allergen bulk import:** Presenter explicitly stated uncertainty ("I'm honestly not sure of the details on that, I'll follow up") at [24:05]. Not a demonstrated feature; not confirmed in any ticket. **Excluded.**
- **U7 — Item copy/clone:** Presenter said "I don't think the copy feature is in 2.0 yet" at [33:11]. Not a confirmed feature; no ticket found. **Excluded.**
- **U8 — Data sharing / corporate item catalog import:** Presenter said "I know there's a data sharing feature but I don't think that's the same as what you're asking. Let me put it on the follow-up list" at [33:35]. Not a demonstrated feature; presenter explicitly unsure. **Excluded.**

### Depth
One line per cross-module reference with link placeholder. The three excluded unmatched items are logged here per the template's hard constraint (no omission without explicit reason).

---

## Section 10: Sources

### Ticket inventory (all tickets cited in the guide)
NXT-30036, NXT-30037, NXT-35898, NXT-37110, NXT-37111, NXT-37441, NXT-37568, NXT-37109, NXT-33518, NXT-37815, NXT-40778, NXT-53530, NXT-41273, NXT-43239, NXT-30100, NXT-47249, NXT-30102, NXT-37216, NXT-30103, NXT-41275, NXT-24128, NXT-39594, NXT-30155, NXT-40447, NXT-54229, NXT-36583, NXT-36742, NXT-40479, NXT-58442

### Transcript
`raw/transcripts/20260529-070600-item-management-2026-05-28-item-management-create-items-training.md`
Recording ID: REC-2026-0515-IM-001
Presenter: Sarah Chen (Implementation Specialist)
Date: May 15, 2026

### Key timestamp index (for Writer inline citation reference)
| Timestamp | Content |
|---|---|
| [00:00]–[00:52] | Scope and item type overview |
| [01:24]–[03:38] | Item card creation (non-food: Dixie Cup example) |
| [03:50]–[07:05] | Pack size add workflow |
| [07:05]–[07:30] | Three-tier maximum |
| [07:30]–[07:52] | Identifiers column (P, BU badges) |
| [07:52]–[09:18] | Costing → Inventory Ready |
| [09:18]–[10:20] | GTIN, Whole Numbers/Decimals |
| [10:28]–[11:55] | Images & Documents |
| [12:12]–[12:50] | Item card (food: Yogurt example) |
| [12:50]–[13:25] | Food/Non-Food, Fluid/Non-Fluid |
| [13:52]–[14:12] | Serving size add |
| [14:30]–[15:02] | Pack sizes for food item |
| [15:02]–[16:08] | Link servings to packs (Sub-Qty) |
| [16:08]–[16:48] | Costing for food item |
| [16:48]–[17:52] | Base unit default and promotion (dual unit) |
| [18:55]–[20:42] | Nutrient Details tab |
| [20:42]–[21:42] | Ingredient Info card |
| [21:52]–[22:20] | Contribution Info card |
| [22:20]–[24:02] | Allergen Info + Custom Allergen |
| [24:30]–[27:32] | Menu Info tab, Direct Menu Item fields |
| [27:32]–[28:18] | Menu Item Serving + Exceptions |
| [28:18]–[29:55] | Steps card, HACCP, Control Points |
| [29:55]–[31:48] | POS Pricing (Students + Adults + Taxable) |
| [32:05]–[32:50] | Inventory Info tab |
| [34:08]–[35:00] | Food vs. non-food recap |
| [35:25]–[35:35] | Nutrient status / menu planning cross-module |
| [37:35]–[38:30] | Locking rules + Base Unit recap |

### Inline citation format (for Writer)
```
<!-- Source: NXT-XXXX AC: "verbatim quote" -->
<!-- Source: transcript [MM:SS] -->
<!-- Source: NXT-XXXX Description [TIER 3 — context only, not AC] -->
```
Note: Description-tier citations must be accompanied by a `[TO VERIFY]` or explicit caveat; they cannot stand alone as factual claims.

---

## SME Must-Handle Items Before Writer Proceeds

The following discrepancies must be resolved or explicitly surfaced in the draft. They are not Writer decisions:

| # | Item | Type | Ticket(s) | Transcript ref | Status |
|---|---|---|---|---|---|
| D1 | Edible Yield Factor location: presenter said Ingredient Info card; NXT-47249 AC says Units card (removed from Ingredient Info) | Critical factual discrepancy | NXT-47249, NXT-30100 | [20:42] | Must surface as `> [!warning] Discrepancy` callout; current AC behavior is the authoritative instruction |
| D2 | Vitamin A and Vitamin C now optional: presenter's training implied they follow the asterisk/required pattern without calling out the change | Partial discrepancy | NXT-43239 | [19:12]–[20:25] | Must surface as `> [!warning] Discrepancy` callout |
| D3 | Three-tier maximum: stated by presenter; no AC source | AC-thin | NXT-37110 | [07:05] | `[TO VERIFY]` marker; SME to confirm or locate AC |
| D4 | Costing divide-down formula: presenter demonstrated; not in AC | AC-thin | NXT-37568 | [08:32] | `[TO VERIFY]` marker |
| D5 | "Show on Family Hub menus" custom allergen toggle | Unmatched / ambiguous | NXT-24128 | [23:28] | `[AMBIGUOUS / TO VERIFY]` marker |
| D6 | Buy American + exemption letter upload interaction rule | AC-thin | NXT-30100, NXT-41273 | [21:22] | `[TO VERIFY]` marker |
| D7 | Base Unit / Whole Numbers locking after Inventory transaction | AC-thin | NXT-54229, NXT-37111 | [37:35] | `[TO VERIFY]` marker; in Description only |
| D8 | Pre-Prep Instructions, Prep Time, Cook Time on Steps card | AC-thin | NXT-36583 | [28:58] | `[TO VERIFY]` marker |
| D9 | File size limit (5 MB) and specific file types for Images & Docs | AC-thin | NXT-41273 | [11:02] | `[TO VERIFY]` marker; presenter-stated, not in AC or RN |
| D10 | HACCP process names (No Cook / Same Day Service / Complex Food) | AC-thin | NXT-36583 | [28:35] | `[TO VERIFY]` marker |

---

## Handoff checklist

- [x] Mapper inventory reviewed (39 matched features, 8 unmatched, 9 cross-module)
- [x] Template constraints checked (long-form: all features included, 10 required sections, 2,500–6,000 words target)
- [x] All 39 matched features mapped to at least one section
- [x] Unmatched items U1–U8 reviewed: U1–U4 promoted/absorbed into matched features or `[TO VERIFY]` markers; U5 = `[AMBIGUOUS/TO VERIFY]`; U6, U7, U8 = excluded with logged reason
- [x] All 9 cross-module references assigned to Related Content (Section 9) as one-line + link placeholders
- [x] SME must-handle discrepancies D1–D10 explicitly inventoried above
- [x] `[TO VERIFY]` markers planned for all AC-thin specifics (char limits, file sizes, tier cap, formula, HACCP process names, button labels, locking behavior)
- [x] Two `> [!warning] Discrepancy` callouts planned (D1: Yield Factor; D2: Vitamin A/C)
- [x] No features dropped without explicit reason logged
- [ ] SME fact-check can proceed (D1 and D2 are must-resolve before draft; D3–D10 can be marked in draft)
- [ ] Writer has enough to generate (yes — section-by-section depth plan complete; ticket citations and transcript anchors provided for all 10 sections)
