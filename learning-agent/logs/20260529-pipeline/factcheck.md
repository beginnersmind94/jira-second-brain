## Fact-Check Report — Item Management: Creating Food and Non-Food Items

**Transcript:** `20260529-070600-item-management-2026-05-28-item-management-create-items-training.md`
**Presenter:** Sarah Chen (Implementation Specialist)
**Fact-checked against:** Live NXT Jira (cloudId: f946bf46-f1dc-4086-9c0b-d1f4809786e9) — AC read directly via MCP on 2026-05-29
**Tier rule applied throughout:** AC (TIER 1) and RN/RN Internal (TIER 1) are citable. Description (TIER 3) is never cited as AC. Field names sourced only from Description are flagged [TO VERIFY].

---

### Verified Claims

| # | Transcript claim | Timestamp | Supporting source (verbatim TIER-1 AC or RN) | Ticket |
|---|---|---|---|---|
| V1 | Item card loads on click of +NEW; Item Description is required | [01:42]–[02:01] | AC: "Load the new initial item creation screen on click of +New; Provide the identifying information fields (Description + global info) — Require Description" | NXT-30036 |
| V2 | Tags, Brand Name, Manufacturer, Product Code are present on the Item card | [02:50]–[03:10] | AC: "Provide the identifying information fields (Description + global info); Provide Tags field" | NXT-30036 |
| V3 | Item Category, Storage Category, and Valuation Group are required (three dropdowns) when not skipping | [02:22]–[02:50] | AC: "If not skipping, require a value for all 3 dropdowns" | NXT-30037 |
| V4 | Units card has FOOD and NON-FOOD selection before the grid is enabled | [04:15]–[04:30] | AC: "Provide Food item and Fluid item questions in the header bar of the card before enabling the grid" | NXT-35898 |
| V5 | Food items only: Fluid vs. Non-Fluid question appears; fluid items use volume (milliliters), non-fluid use grams | [13:00]–[13:25] | AC: "Provide Food item and Fluid item questions in the header bar of the card before enabling the grid; After questions, load the grid with Add Serving Size and Add Pack Size actions (based on question input)" (fluid → volume confirmed in Description; non-food disables servings per NXT-35898 AC) | NXT-35898 |
| V6 | +PACK button adds a pack size row; Sub-Qty field appears when adding a second or lower pack size; Weight is optional for rare scenarios | [03:50]–[06:52] | AC: "Provide the ability to add pack size units in the combined Units grid; Bring attention to the appropriate Sub-Qty fields as required to link Pack Sizes; Emphasize Weight field for rare scenarios where required" | NXT-37110 |
| V7 | Serving size and pack sizes must be linked (Sub-Qty on the serving row) for Inventory eligibility; alert fires when they are disconnected | [15:02]–[16:08] | AC: "Provide Sub-Qty on the Serving Size row in valid scenarios; Trigger Inventory readiness based on proper pack-serving links" | NXT-37441 |
| V8 | Identifiers column displays icons for each unit's important flags | [07:30]–[07:52] | AC: "Populate the Identifiers column with various icons associated with different important flags which are assigned at a unit level" | NXT-37109 |
| V9 | Only one pack-size unit cost can be manually entered; system scales to others | [08:08]–[08:52] | AC: "Provide an optional Costing step; Require FMV for Inventory readiness" (single-unit entry and scaling confirmed in Description; AC confirms costing step and FMV requirement) | NXT-37568 |
| V10 | Inventory Readiness banner is always displayed | [09:05]–[09:27] | AC: "Always display the inventory readiness banner (including for placeholder units; for all scenarios including 'Non-Inventory' for Ineligible or Disabled)" | NXT-53530 |
| V11 | Base Unit confirmation step is part of inventory setup | [09:05], [17:05]–[17:42] | AC: "Provide a step to confirm Inventory info, including the Base Unit" | NXT-37111 |
| V12 | Whole Numbers vs. Decimals option on the Units card controls whether the Base Unit can be counted in decimals | [09:48]–[10:20] | AC: "Provide an option in the context of the new Units card to determine whether the Base Unit can be counted in decimals; Update Inventory to consume the decimal flag to enable or disable the presence of decimals throughout the module for that item" | NXT-33518 |
| V13 | GTIN/UPC can be entered per pack size; 8–14 digits; barcode icon appears in Identifiers column when GTIN is present | [09:18]–[09:48] | AC: "Add an edit GTIN/UPC function to the Units card; Allow 8-14 digits in the GTIN field (UPC: 12 digits; GTIN: 14 digits; anything else = invalid); Display barcode identifier for units which have GTIN" | NXT-37815 |
| V14 | Serving size add (+SERVING button); ability to add and save independent serving sizes; Amount, Description, Weight fields | [13:52]–[14:12] | AC: "Provide a button for adding a Serving Size unit; Provide the ability to add and save independent serving sizes" | NXT-35898 |
| V15 | Images & Documents: replaces old Images card; drawer panel via expand icon; Use As dropdown for images (Preferred Ingredient Image, Preferred Inventory Image, Menu Image) and documents (CN Label, Buy American Exemption Letter, Product Formulation Statements, Meal Credits) | [10:28]–[11:55] | AC: "Replace the edit mode of the Images card with a new Image & Document slideout using the common component; For images, provide a 'Use As' dropdown: Preferred Ingredient Image, Preferred Inventory Image, Menu Image (for publishing); For documents, provide a 'Use As' dropdown: CN Label, Buy American Exemption Letter, Product Formulation Statements, Meal Credits" | NXT-41273 |
| V16 | Up to 10 files can be uploaded to Images & Documents | [10:28]–[11:55] | RN: "Up to 10 files can be uploaded with any combination of supported file types" | NXT-41273 |
| V17 | Nutrient Details card redesigned; Vitamin A and Vitamin C are now optional; Moisture and Ash do not require Missing checkbox | [19:12]–[20:42] | AC: "Update business rules: Vitamin A, Vitamin C, Moisture, Ash changed to optional; Moisture and Ash do not require a 'Missing' checkbox as they are never present on nutrition labels" | NXT-43239 |
| V18 | Missing Value (M) checkbox marks a nutrient as absent rather than zero | [19:40], [35:35]–[36:05] | AC: "Update business rules: Vitamin A, Vitamin C, Moisture, Ash changed to optional; leaving them blank will automatically enable the Is Missing option" (RN confirms "(M)" designation behavior) | NXT-43239 |
| V19 | Nutrient Details: nested nutrients auto-zero when parent is set to 0 (Total Fat → Sat Fat, Trans Fat; Total Carbs → Fiber, Sugar) | [19:12]–[20:25] | AC: "Automatically set nested nutrients to zero if the parent nutrient is set to 0 (e.g. if Total Fat is 0, Sat Fat and Trans Fat auto-zero; same for Carbohydrates → Fiber/Sugar)" | NXT-43239 |
| V20 | Ingredient Info card completion does not block the next section | [20:42]–[21:00] | AC: "Card completion or not does not affect the next section from being available" | NXT-30100 |
| V21 | Contribution Info: load section; edit in slideout; skip allowed | [21:52]–[22:20] | AC: "Load the Contributions section once the Serving Measures is successfully saved; Add/Edit Contributions in the slideout; Allow user to 'skip for now' if they do not want to enter the information at the time" | NXT-30102 |
| V22 | Allergen Info: load section; allergens can be entered without nutrient/contribution info; skip allowed | [22:20]–[23:10] | AC: "Load the Allergens section; Can create or enter allergen without having nutrient/contribution information entered; Allow user to 'skip for now' if they do not want to enter the information at the time" | NXT-30103 |
| V23 | Allergen forms in priority order: Contains, Processed (Facility), May Contain, Free From | [22:42]–[23:10] | AC: "Prioritize allergen forms in the following order: 'Contains' form, 'Processed....' form, 'May Contain' form, 'Free From'" | NXT-41275 |
| V24 | Custom Allergens accessed at: Item Management > Configuration > Item Configuration > Custom Allergen option; pop-up asks for data source and configuration option; only Local data source | [23:10]–[23:55] | AC: "A Custom allergens option is added under IM configuration area; Option: Custom Allergen; Once user selects configuration a pop-up window is presented to the user asking for data source and configuration option desired. When user clicks apply, system redirects to the appropriate configuration area; Only use Local data source" | NXT-24128 |
| V25 | Custom Allergen slide-out fields: Custom Allergen Description (mandatory, free text); Data Source (mandatory, Local only) | [23:28]–[23:55] | AC: "Custom Allergen Description [Free text box] — Is a Mandatory field; Data Source [Dropdown, Local] — Is a Mandatory field; Only one Data Source can be selected [Local]" | NXT-24128 |
| V26 | Custom Allergen: duplicate validation with message; newly added allergen listed on result grid | [23:55]–[24:02] | AC: "Custom Allergen is Mandatory and no duplicates are allowed; If Custom Allergen already exist warn the user with a message 'Custom Allergen already in use, please use a different Custom Allergen name'; The newly added Custom Allergen is listed on the result grid; System returns to Custom Allergen screen" | NXT-24128 |
| V27 | Menu Item tab created; Show on POS toggle controls POS attributes and pricing table | [24:30]–[27:12] | **[CORRECTED 2026-05-29 — orchestrator, verified live via MCP]** NXT-39594 AC contains ONLY: "Redesign the Recipe details page…", "Create a tab structure for Recipes", "Create a Menu Item tab". The "Show on POS toggle…controls the POS attributes and Pricing table" text is NXT-39594 **Description (TIER 3) — do NOT cite as AC**. Cite the Menu Item tab to **NXT-39594 AC: "Create a Menu Item tab"**; cite the toggle→pricing behavior to **NXT-30155 AC (see V28): "Enable the POS Info tab if the user specifies the item as a POS Item; Load the POS attributes and Pricing section under the POS tab"** + transcript [27:12]. | NXT-39594 (Menu Item tab) / NXT-30155 (toggle→POS pricing) |
| V28 | POS Info tab enabled when item is specified as a POS Item; Students and Adults tabs; Set All Prices option per tab in edit mode | [29:55]–[30:55] | AC: "Enable the POS Info tab if the user specifies the item as a POS Item; Load the POS attributes and Pricing section under the POS tab; Separate pricing for Students and Adults with tabs; Provide the 'Set All Prices' option which can be used on one tab at a time (in Edit only)" | NXT-30155 |
| V29 | Taxable option appears only on the Adult tab of POS Pricing, not on the Students tab | [31:20]–[31:48] | AC: "Only display the Taxable option when the Adult tab is selected on POS Pricing (for both view and edit mode; note: POS does not consider tax for students)" | NXT-58442 |
| V30 | Ability to add additional Menu Item serving sizes via +Menu Serving button within MI Units edit mode | [27:32]–[27:55] | AC: "Provide the ability to add additional serving sizes for the Menu Item; Within the MI Units edit mode, provide a '+Menu Serving' button" | NXT-40447 |
| V31 | Menu Serving and Exceptions are available once the item is a Menu Item | [27:55]–[28:18] | AC: "Menu Serving and Exceptions should be available once the item is a Menu Item" | NXT-54229 |
| V32 | Steps card — HACCP Process selection added to the Steps process and tab | [28:18]–[29:10] | AC: "Add a small selection for Recipe HACCP Process (this will belong to the Steps process and tab)" | NXT-36583 |
| V33 | Control Points (CCPs) can be added to the recipe; Critical Limit and Corrective Action are editable on each CCP | [29:10]–[29:42] | AC: "Allow CCPs to be added to the recipe like steps; Allow added CCPs to be edited for Critical Limit and Corrective Action" | NXT-36742 |
| V34 | Inventory Info tab: read-only view of active vendor contracts; shortcut icon opens Inventory Contract Items page in a new tab, pre-loaded for the relevant item | [32:05]–[32:40] | AC: "Display a read-only 'Inventory Item Active Contracts' card which has a preview of the Contract Items page details for that item (show only active status contracts); Provide an icon to open Inventory in a new tab: navigate to the Contract Items page; pre-load the contract for the relevant item" | NXT-40479 |
| V35 | Long-term editing: changing sub-quantities is listed as a restricted operation | [37:35]–[38:05] | AC: "Long-term editing: changing weight for recipe ingredient; changing weight for DMI; changing description for ingredient or DMI; changing pack size descriptions; changing sub-quantities (including inventory-able servings and dual units)" | NXT-54229 |
| V36 | "Merge" mechanism (AC language): when creating a pack size that matches a serving size, a dedicated Merge prompt appears; once merged, serving sub-qty is promoted to new base unit | [17:05]–[17:42] | AC: "Prompt users with a dedicated 'Merge' button when they are attempting to create a unit which is likely intended to be a dual unit; Once the Merge button is clicked, show a special editable mode; if the serving has sub-qty, promote that sub-qty to the new base unit" | NXT-40778 |
| V37 | Non-food items do not have serving sizes (Base Unit promotion to dual unit is only available for food items) | [04:30], [38:30] | AC: "Provide Food item and Fluid item questions in the header bar of the card before enabling the grid; After questions, load the grid with Add Serving Size and Add Pack Size actions (based on question input)" — serving sizes only enabled after Food = Yes | NXT-35898 |

---

### Flagged Discrepancies

> [!warning] **DISCREPANCY D1 — Severity: HIGH**
> **Edible Yield Factor location**
>
> **Transcript says** [20:42]: "below that — Ingredient Info card. Click the three dots, Edit. This is where you set the Edible Yield Factor — that's the percentage of the item that's actually edible."
>
> **Jira (NXT-47249 AC, TIER 1) says**: "Make Yield Factor configurable on each serving in the Units card; Provide a dedicated step for editing yield factor (show only serving sizes; add a dedicated Yield Factor column; allow Yield Factor to be edited for each serving size; add a custom record at the bottom for 'Default (all other measures)'); **Remove Yield Factor from Ingredient Info card (moved to Units)**"
>
> Status: NXT-47249 is "Done Done."
>
> The presenter described the old pre-NXT-47249 location (Ingredient Info card). Per current AC, Yield Factor has been removed from Ingredient Info and is now serving-specific on the Units card, with a dedicated Yield Factor column per serving size.
>
> **Writer action required:** Do not follow the presenter's workflow for Yield Factor. The correct current workflow uses the Units card. Confirm exact UI steps with product team before writing. This is a primary content error — if left uncorrected it will directly misdirect staff.

---

> [!warning] **DISCREPANCY D2 — Severity: MEDIUM**
> **Base Unit promotion language (presenter: "promote"; Jira AC: "Merge")**
>
> **Transcript says** [17:05]–[17:22]: "Click the BASE UNIT chip. And the system asks: 'Confirm Carton as Base Unit, or promote Each to lowest Inventory Unit?' … Click the Each row … Click CONFIRM."
>
> **Jira (NXT-40778 AC, TIER 1) says**: "Prompt users with a dedicated 'Merge' button when they are attempting to create a unit which is likely intended to be a dual unit … Provide a 'Merge w/ Serving' prompt button in the Identifier column when entering a duplicate description on a pack size … Once the Merge button is clicked, show a special editable mode in which the user can confirm the merging of the serving and pack"
>
> The AC uses "Merge" / "Merge w/ Serving" throughout. The presenter uses "promote" and describes a "BASE UNIT chip." The underlying behavior (serving becomes base unit / dual unit) is consistent, but the exact UI element names — "Merge button," "BASE UNIT chip," specific dialog text — differ.
>
> **Writer action required:** Use "Merge" as the official AC-grounded term. The specific dialog prompts ("Confirm Carton as Base Unit, or promote Each...") are not in any AC text — mark those exact strings as [TO VERIFY].

---

> [!warning] **DISCREPANCY D3 — Severity: LOW**
> **Images & Documents — "JPEG, PNG, PDF, Word, spreadsheets" file type list and "5 MB per file" limit**
>
> **Transcript says** [11:02]: "You can do images — JPEG, PNG — and also documents like PDFs, Word docs, even spreadsheets. Max file size is 5 MB per file."
>
> **Jira (NXT-41273 RN, TIER 1) says**: "Up to 10 files can be uploaded with any combination of supported file types." No file type list and no per-file size limit are stated anywhere in AC or RN.
>
> **Writer action required:** The 10-file limit is citable from RN. The 5 MB limit and the specific file type enumeration (JPEG, PNG, PDF, Word, spreadsheets) have no AC or RN source. Mark both as [TO VERIFY] — they may be correct but cannot be asserted from Tier-1 sources.

---

### Unsupported Statements

| # | Claim | Timestamp | Notes |
|---|---|---|---|
| U1 | "I think it's a 250 character limit on [Item Description]" | [02:01] | 250-char limit appears in NXT-30036 Description only ("allow up to 250 characters to be typed"), not in AC ("Require Description" only). Include as [TO VERIFY] — likely correct but Description-tier only. |
| U2 | "the system only allows a maximum of three tiers" for pack sizes | [07:05]–[07:30] | No AC text in NXT-37110 states a three-tier cap. Description references multi-tier sub-qty scenarios via Figma prototypes; the cap is implicit in mockups, not stated. Include as [TO VERIFY] rather than asserting as a hard fact. |
| U3 | Costing auto-scale formula: "$80 divided by 20 sleeves = $4 per Sleeve; $4 divided by 25 = $0.16 per Cup" | [08:32]–[08:52] | NXT-37568 AC confirms single-unit cost entry and auto-scaling concept ("Require FMV for Inventory readiness") but the division formula itself is Description-tier. The example arithmetic is consistent with the Description, but the formula cannot be cited from AC. Include the concept (single-unit entry, system calculates others) with [TO VERIFY] on the formula wording. |
| U4 | "Sub-quantity needs to be what the STANDARD pack size is ... The item record should reflect the standard — what's on the spec sheet, basically" (Q&A guidance on short-shipping) | [10:43]–[11:00] | No ticket found that states this operational rule as an AC. This is presenter guidance on process intent — include as attributed presenter guidance (not system behavior) or omit. Do not assert as product AC. |
| U5 | "weight is optional for non-food" pack sizes [04:40]; "weight is not required" for non-food | [04:40]–[05:00] | NXT-37110 AC: "Emphasize Weight field for rare scenarios where required." The AC does not specify food vs. non-food distinction for weight optionality. Consistent in intent but not explicitly food/non-food segmented in AC. Include with [TO VERIFY] on the non-food specificity. |
| U6 | "HACCP processes: No Cook, Same Day Service, Complex Food" — three named options | [28:35]–[28:58] | NXT-36583 AC says only "Add a small selection for Recipe HACCP Process." The three process names are in Description only ("No Cook, Same Day Service, Complex Food (reflects configured processes)"). Include as [TO VERIFY]. |
| U7 | Cold Hold Critical Limit auto-fills as "hold at less than or equal to 42°F" with a Corrective Action | [29:10]–[29:42] | NXT-36742 AC confirms CCPs have editable Critical Limit and Corrective Action; "load with configured defaults" is Description-level. The 42°F value is presenter-stated and not in any Tier-1 source. Include the auto-fill concept (confirmed in AC) but mark the 42°F value as [TO VERIFY]. |
| U8 | "once you've actually done an inventory count or a receipt or an adjustment with that item, the Base Unit and the Whole Numbers/Decimals setting get locked" | [37:35]–[38:05] | NXT-54229 AC lists "changing sub-quantities" as a long-term editing restriction; the specific trigger events ("inventory count or receipt or adjustment") and the specific locked fields (Base Unit, Whole Numbers/Decimals) are in Description of NXT-37111 and NXT-54229 only, not AC text. Include the general concept with [TO VERIFY] on trigger specifics. |
| U9 | Inventory Info tab shows: "vendor name, vendor item number, unit, lead time, min/max order quantities, current price" | [32:05]–[32:40] | NXT-40479 AC confirms a "read-only 'Inventory Item Active Contracts' card with a preview of the Contract Items page details." The specific columns listed by the presenter are Description-only. Include as [TO VERIFY]. |
| U10 | "Allergen bulk import" for 500 items | [24:05]–[24:30] | Presenter explicitly said: "I'm honestly not sure of the details on that. I'll follow up." Not a demonstrated feature. No ticket found. Exclude entirely — do not include in learning content. |
| U11 | Item copy/clone feature — "I don't think the copy feature is in 2.0 yet" | [33:11]–[33:35] | Presenter explicitly uncertain; no confirmed ticket. Not a demonstrated feature. Exclude. |
| U12 | "Data sharing feature where you can get items from a corporate database" | [33:35]–[34:00] | Presenter explicitly said: "I don't think that's the same as what you're asking. Let me put that on the follow-up list." Not demonstrated, not confirmed. Exclude. |
| U13 | "sales tax calculation" behavior in 2.0 | [31:20]–[31:35] | Presenter said: "I'm not sure how the sales tax calculation works in 2.0." Admitted unknown. Exclude. |
| U14 | Quick reference guides on the SchoolCafé support site for non-food and food item creation; food guide is "40-something pages" | [37:15]–[37:35] | Presenter statement about external support materials. No Jira source. May be included as a reference pointer but cannot be verified from AC. Mark as [TO VERIFY] with note to confirm link and page count before publish. |

---

### Ambiguous Claims

| # | Claim | Timestamp | Ambiguity |
|---|---|---|---|
| A1 | "you can toggle on whether it shows on Family Hub menus" when creating a custom allergen | [23:28] | [AMBIGUOUS — presenter said "you can toggle on whether it shows on Family Hub menus" at [23:28] when describing the custom allergen slide-out card. NXT-24128 AC (confirmed live) lists only two slide-out fields: Custom Allergen Description and Data Source. Could mean: (A) there is an additional field not yet captured in NXT-24128 AC (possible later enhancement), or (B) presenter is describing a Family Hub configuration that happens elsewhere, not on this slide-out. No supporting ticket found. Do not assert this toggle in learning content without product team confirmation.] |
| A2 | "nothing is locked once you save it. Well — actually, hmm, let me think. The item description you can always change. Some things once the item is used in Inventory, there are some restrictions." | [03:58]–[04:15] | [AMBIGUOUS — presenter made a verbal correction in real time. Final stated position: Item Description can always be changed; some fields lock after Inventory use. The "some restrictions" is unspecified. Use the corrected statement (Item Description is always editable); for the locking caveat, cite NXT-54229 AC's "Long-term editing" list which enumerates restricted fields. Do not assert that Item Description specifically locks — presenter's final answer is that it does not.] |
| A3 | Sarah's Q&A answer on dual-unit workflow for serving = pack scenario: "I think you still add a pack and then the system offers to make it a dual unit" | [17:52]–[18:35] | [AMBIGUOUS — presenter said "it's in the guide, steps 18 through 28 I think. But the key thing is: add the serving first, always." Could mean (A) there is a specific dual-unit creation order (serving first is required), or (B) serving first is recommended but not enforced. NXT-40778 AC says the Merge prompt fires when creating a pack that matches a serving — implying servings can exist first. NXT-35898 AC does not state an order requirement. Use the AC-supported statement: the system prompts a Merge when a pack matches an existing serving. Do not assert that order is enforced.] |

---

### Cross-Module Claims (flag, do not incorporate as Item Management AC)

| # | Claim | Timestamp | Module | Handling |
|---|---|---|---|---|
| C1 | "everything downstream just works" — Inventory, menus, POS affected by item setup | [00:00]–[00:28] | Inventory / Menu Planning / POS | One-line intro acknowledgment only. Do not expand. |
| C2 | Inventory Info tab shows vendor contracts added via the Inventory module: "you've added it to a contract — you know, in the Inventory module, not here" | [32:05]–[32:40] | Inventory | One line: "Contract details populated from the Inventory module" + link placeholder [→ Inventory: Contract Items]. Do not describe the Inventory contract setup workflow. |
| C3 | "Serving sizes are the basis for all Ingredient usage, like in recipes and menu planning" | [13:25]–[13:52] | Recipes / Menu Planning | One line: "Serving sizes configured here feed ingredient calculations in the Recipes module" + link placeholder [→ Recipes module]. |
| C4 | Sub Ingredients and Standard Recipe Directions on Ingredient Info card: "they'll show up on any multi-item recipe that uses this yogurt as an ingredient" | [21:00]–[21:22] | Recipes | One line: "Sub Ingredients and Standard Recipe Directions display on recipes where this item is used as an ingredient" + link placeholder [→ Recipes module]. |
| C5 | "It only matters when you're using the item in menu planning, because that's where the nutrient analysis happens" | [35:25]–[35:35] | Menu Planning | One line: "Nutrient data entered here drives nutrient analysis in Menu Planning" + link placeholder [→ Menu Planning module]. |
| C6 | Marketing Name & Description "is what shows up in Family Hub, the parent-facing side" | [26:15]–[26:48] | Family Hub | One line: "Marketing Name & Description display in Family Hub for parents" + link placeholder [→ Family Hub module]. |
| C7 | Button Name (English/Spanish) and POS Entree flag — "what the cashier sees on the POS touchscreen" | [25:28]–[27:12] | POS | One line: "Button Name and POS Entree flag control POS display and reimbursable meal tracking" + link placeholder [→ POS module]. |
| C8 | Max Days and Leftover Category — "how many days the item can be carried over on a production record" | [25:28]–[26:15] | Production Records | One line: "Max Days and Leftover Category govern production record carryover behavior" + link placeholder [→ Production Records module]. |
| C9 | "I think in Inventory they have some workaround for receiving in higher units but I honestly don't know the details. Justin would know — he's the Inventory PM." | [36:38]–[36:48] | Inventory | Exclude entirely — presenter admitted uncertainty. Do not reference. |
| C10 | PrimeroEdge comparisons ("In PrimeroEdge it was...") | [24:05]–[24:30], [31:35] | Legacy / PrimeroEdge | Exclude entirely. These are legacy system comparisons, not SchoolCafé 2.0 product descriptions. |

---

### Field-Name Caution List

Fields whose exact labels appear only in Description (TIER 3). The writer must mark these [TO VERIFY] rather than assert the label as definitive product text.

| Field / Label | Ticket | What AC says | What is Description-only |
|---|---|---|---|
| "Item Category," "Storage Category," "Valuation Group" | NXT-30037 | "require a value for all 3 dropdowns" | The three field names themselves |
| "Brand Name," "Product Code," "Manufacturer" | NXT-30036 | "identifying information fields (Description + global info)" | These specific field names |
| 250-character limit on Item Description | NXT-30036 | "Require Description" only | "allow up to 250 characters" |
| "Missing Costing" alert label | NXT-37568 | "Provide an optional Costing step" | Alert label "Missing Costing" |
| "Manage Costing" button label | NXT-37568 | Costing step concept only | Button label "Manage Costing" |
| "P" badge (Pack Size identifier), "BU" badge (Base Unit identifier), "MI" badge | NXT-37109 | "Populate the Identifiers column with various icons" | Specific badge letter codes |
| "Sub Ingredients," "Standard Recipe Directions" field names | NXT-30100 | "1/3 width card for miscellaneous food item info" | Both field names |
| "Locally Grown," "Buy American" checkbox labels | NXT-30100 | "1/3 width card for miscellaneous food item info" | Both checkbox labels |
| "Buy American checked → cannot upload exemption letter" (business rule) | NXT-30100 / NXT-41273 | NXT-41273 AC lists "Buy American Exemption Letter" as a document type; NXT-30100 AC does not state the checkbox-disables-upload rule | The business rule linking Buy American checkbox to exemption letter upload availability |
| Specific meal pattern component names: "Meat/Meat Alternates," "Grains," "Vegetables" | NXT-30102 | "Load the Contributions section; Add/Edit Contributions in the slideout" | Specific component names |
| HACCP Process names: "No Cook," "Same Day Service," "Complex Food" | NXT-36583 | "Add a small selection for Recipe HACCP Process" | All three process names |
| "Pre-Preparation Instructions," "Prep Time," "Cook Time" field names | NXT-36583 | "Add a small selection for Recipe HACCP Process" (Steps process only) | All three field names |
| Cold Hold Critical Limit value of "less than or equal to 42°F" | NXT-36742 | "Allow added CCPs to be edited for Critical Limit and Corrective Action" | The 42°F specific value |
| 5 MB per-file size limit for Images & Docs | NXT-41273 | "Up to 10 files can be uploaded" (RN TIER 1) | 5 MB limit |
| Specific file types for Images & Docs (JPEG, PNG, PDF, Word, spreadsheet) | NXT-41273 | "any combination of supported file types" (RN TIER 1) | The type enumeration |
| "Disabled" status label on Menu Info tab before configuration | NXT-39594 | NXT-39594 AC = only "Create a Menu Item tab" (+ two Recipe-redesign bullets). The "Show on POS toggle controls POS attributes" line is **Description (TIER 3), not AC** — see corrected V27. | "Disabled" status label (Description-tier; mark [TO VERIFY]) |
| Tab rename to "MENU & POS INFO" after Show on POS enabled | NXT-39594 | NXT-39594 AC does NOT state the rename; "Show on POS toggle will control the presence of the POS attributes" is **Description (TIER 3)**. Toggle→pricing behavior is AC-grounded only via **NXT-30155** (V28). | The renamed tab label (Description-tier; mark [TO VERIFY]) |
| Menu Item fields: "Menu Item Name," "Button Name (English)," "Menu Item Category," "Max Days," "Marketing Name & Description," "Button Name (Spanish)," "Meal Type," "Leftover Category," "Preparation Site Item," "Show in Summary," "POS Entree" | NXT-30155 | "Enable POS Info tab; Load POS attributes and Pricing section; Set All Prices option" | All individual field names |
| "Allow Sale" toggle on POS Pricing | NXT-30155 | "Load the POS attributes and Pricing section" | Toggle label |
| Inventory contract details: "vendor name, vendor item number, unit, lead time, min/max order quantities, current price" | NXT-40479 | "read-only 'Inventory Item Active Contracts' card with a preview of the Contract Items page details" | The specific column names |

---

### Summary

- **Total claims checked:** 56 (37 verified claims + 3 discrepancies + 14 unsupported + 3 ambiguous + 10 cross-module; field-name caution list is an overlay, not an additional count)
- **Verified (Tier-1 sourced):** 37
- **Discrepancies (transcript vs. Jira AC conflict):** 3 (D1 HIGH, D2 MEDIUM, D3 LOW)
- **Unsupported (no Tier-1 source; must be [TO VERIFY] or excluded):** 14
- **Ambiguous:** 3
- **Cross-module (exclude or one-line reference):** 10

**Critical action before writing:** Discrepancy D1 (Edible Yield Factor on Ingredient Info vs. Units card per NXT-47249) must be resolved with the product team before any draft section on Ingredient Info is written. The presenter's workflow is demonstrably outdated relative to a Done-Done ticket. Writing it as presented would actively misdirect staff.
