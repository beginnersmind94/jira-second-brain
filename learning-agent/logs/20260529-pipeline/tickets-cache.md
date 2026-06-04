==== NXT-30036 ====
## Acceptance Criteria [TIER 1]
- Load the new initial item creation screen on click of +New
- Provide the identifying information fields (Description + global info)
  - Require Description
- Provide Tags field
- Provide a Save button for continuing

## Release Notes [TIER 1]
EMPTY

## Release Notes Internal
EMPTY

## Description [TIER 3 — never cite as AC]
Story covers: Item Description (formerly Name) — Mandatory, allow up to 250 characters; Brand Name (dropdown); Product Code; Manufacturer (dropdown); Data Source dropdown (Local only); Tags field; duplicate item check; Save & Continue button. Upon first Save, item is officially created and assigned an Item #.

==== NXT-30037 ====
## Acceptance Criteria [TIER 1]
- Load the item header after user saves initial info
- Display the Product Info attributes
- Allow user to skip Product Info attributes
- If not skipping, require a value for all 3 dropdowns

## Release Notes [TIER 1]
EMPTY

## Release Notes Internal
EMPTY

## Description [TIER 3 — never cite as AC]
Attributes: Item Category, Storage Category, Valuation Group. Enabling Unit Info grid requires all 3 dropdown values selected. Skip button allows creating POS-only item without Product Info.

==== NXT-37110 ====
## Acceptance Criteria [TIER 1]
- Provide the ability to add pack size units in the combined Units grid
- Bring attention to the appropriate Sub-Qty fields as required to link Pack Sizes
- Emphasize Weight field for rare scenarios where required
- Build concept of Inventory Readiness for item status and create item flow logic

## Release Notes [TIER 1]
EMPTY

## Release Notes Internal
EMPTY

## Description [TIER 3 — never cite as AC]
+ Pack button inserts a new row. Description is a hybrid smart text field. Sub-Qty only shown when adding second+ pack size (Higher/Lower logic). Weight optional except when linking to servings. Three-tier implicit in mockups; no explicit cap stated in AC.

==== NXT-35898 ====
## Acceptance Criteria [TIER 1]
- Provide the new Units card in the item creation header which is the combination of the pack size and serving size sections
- Provide Food item and Fluid item questions in the header bar of the card before enabling the grid
- After questions, load the grid with Add Serving Size and Add Pack Size actions (based on question input)
- Display a header bar area for various prompts or questions provided to the user
- Provide a button for adding a Serving Size unit
- Provide the ability to add and save independent serving sizes
- Provide a button for adding Pack Size units

## Release Notes [TIER 1]
EMPTY

## Release Notes Internal
EMPTY

## Description [TIER 3 — never cite as AC]
Food Item Y/N → if Yes, ask Fluid Item Y/N → if Fluid, switch to Volume for serving sizes / disable serving sizes for non-food. Grid columns: Amount, Description, Sub-Qty, Weight/Volume, Cost/Value, Identifiers, Action. Amount = 1 on serving size makes it "potentially inventory-able."

==== NXT-37441 ====
## Acceptance Criteria [TIER 1]
- Provide Sub-Qty on the Serving Size row in valid scenarios
- Emphasize Weight field for Pack Size base units when Sub-Qty is not used for linking
- Trigger Inventory readiness based on proper pack-serving links

## Release Notes [TIER 1]
EMPTY

## Release Notes Internal
EMPTY

## Description [TIER 3 — never cite as AC]
Sub-Qty on serving size row enabled when serving Amount = 1 (potentially inventory-able). Question: "How many [serving description] are in [pack description]?" Weight alternative for linking when sub-qty not used. Items with unlinked pack/serving are Inventory Ineligible.

==== NXT-37568 ====
## Acceptance Criteria [TIER 1]
- Provide questions/prompts to complete the overall required fields for saving the initial Units card and proceeding to item creation
- Provide an optional Costing step
- Require FMV for Inventory readiness

## Release Notes [TIER 1]
EMPTY

## Release Notes Internal
EMPTY

## Description [TIER 3 — never cite as AC]
Cost/Value field enabled for all pack size units or linked serving size (linked via Sub-Qty). User selects the specific unit to enter pricing; system scales to others. Can skip costing → item flagged as "Missing Costing." FMV required for Inventory readiness. Manage Costing button replaces Missing Costing flag after cost is entered.

==== NXT-37109 ====
## Acceptance Criteria [TIER 1]
- Populate the Identifiers column with various icons associated with different important flags which are assigned at a unit level
- Indicate typical Serving Size identifiers such as Nutrient association, Contribution association, etc.
- Add new identifiers to better help explain the expanded concepts of the Units card

## Release Notes [TIER 1]
EMPTY

## Release Notes Internal
EMPTY

## Description [TIER 3 — never cite as AC]
Identifiers include: Base Unit (only if serving is also a pack size), Serving Size indicators (Nutrition assigned, Contributions assigned, Used on a recipe), Preferred Measure (star icon), Menu Item (MI — used for Menu Item / Single Item Recipe), $ icon for the unit where cost was manually entered.

==== NXT-37111 ====
## Acceptance Criteria [TIER 1]
- Provide questions/prompts to complete the overall required fields for saving the initial Units card and proceeding to item creation
- Provide a step to confirm Inventory info, including the Base Unit

## Release Notes [TIER 1]
EMPTY

## Release Notes Internal
EMPTY

## Description [TIER 3 — never cite as AC]
If fewer than 3 pack sizes and no inventory-able serving: "Is [lowest unit] the smallest inventory-able unit?" If inventory-able serving exists: "Is [lowest unit] or [linked serving] the smallest inventory-able unit?" Serving can be promoted to base unit (dual unit). Exception: this option is invalid once item is in Inventory tables and Pack Size is locked.

==== NXT-33518 ====
## Acceptance Criteria [TIER 1]
[NOTE: Module field in Jira = "Inventory" — not "Item Management." However ticket is child of NXT-36067 (IM epic) and describes Units card behavior.]
- Provide an option in the context of the new Units card to determine whether the Base Unit can be counted in decimals
- Update Inventory to consume the decimal flag to enable or disable the presence of decimals throughout the module for that item

## Release Notes [TIER 1]
EMPTY

## Release Notes Internal
EMPTY

## Description [TIER 3 — never cite as AC]
Option presented in Units card context. If base unit does not allow decimals, item always restricted to whole numbers in Inventory. Example: milk carton = whole numbers; bag of flour = decimals. TBD when option is locked.

==== NXT-37815 ====
## Acceptance Criteria [TIER 1]
- Provide an Edit mode which is specific to the Inventory Info tab (filter by only pack size units and any servings linked via sub-qty or with '1' as amount and non-standard measure)
- Add an edit GTIN/UPC function to the Units card in edit mode: replace Identifiers column with a GTIN/UPC column and a text field for each unit
- Allow 8-14 digits in the GTIN field (UPC: 12 digits; GTIN: 14 digits; anything else = invalid; show alert icon for invalid data)
- Display the Pricing button in edit mode
- Display barcode identifier for units which have GTIN
- Provide informational guided messages in the banner bar

## Release Notes [TIER 1]
EMPTY

## Release Notes Internal
EMPTY

## Description [TIER 3 — never cite as AC]
Inventory Info tab provides view and manage capabilities for GTIN/UPC numbers, item substitutions, and expanded pack size details. Figma prototype link in description.

==== NXT-40778 ====
## Acceptance Criteria [TIER 1]
- Prompt users with a dedicated 'Merge' button when they are attempting to create a unit which is likely intended to be a dual unit (primary method to capture dual units; also allows single unit dual units)
- Implement a hard stop warning for matching Description or Weight/Volume (exact same description or weight between pack and serving; also in placeholder mode)
- Implement a soft stop warning if Weight/Volume is within 15% of each other (warning with Merge prompt; after placeholder mode)
- Provide a 'Merge w/ Serving' prompt button in the Identifier column when entering a duplicate description on a pack size
- Once Merge button clicked: show special editable mode to confirm merging; if serving has no sub-qty, keep in edit mode and require input of sub-qty; if serving has sub-qty, promote that sub-qty to new base unit

## Release Notes [TIER 1]
EMPTY

## Release Notes Internal
EMPTY

## Description [TIER 3 — never cite as AC]
Handles "dual unit" scenario (item that is both a serving size and a pack size) whether packs or servings are created first.

==== NXT-53530 ====
## Acceptance Criteria [TIER 1]
- Update the logic and UX behavior for Inventory Readiness
- Remove the sequential logic of the inventory requirements (operate more like a status)
- Always display the inventory readiness banner (including for placeholder units; for all scenarios including 'Non-Inventory' for Ineligible or Disabled)
- Provide very clear messaging for each banner version
- Display very user friendly icons/labels for highlighted fields

## Release Notes [TIER 1]
EMPTY

## Release Notes Internal
EMPTY

## Description [TIER 3 — never cite as AC]
Inventory Readiness revised to be status-based rather than sequential. Always-visible banner covers all states. Mockup shows banner with clear state labels.

==== NXT-41273 ====
## Acceptance Criteria [TIER 1]
- Replace the edit mode of the Images card with a new Image & Document slideout using the common component
- In the slideout, use the image and file preview component
- Provide a 'Image & Document Options' card below with Item Management specific use cases
- For images, provide a 'Use As' dropdown: Preferred Ingredient Image, Preferred Inventory Image, Menu Image (for publishing)
- For documents, provide a 'Use As' dropdown: CN Label, Buy American Exemption Letter, Product Formulation Statements, Meal Credits

## Release Notes [TIER 1]
Title: "Item Management Images & Documents"
Text: "All item types within the Item Management module have been updated with a new Images & Documents feature, which replaces the previous Images-only card. Images & Documents is the top right card on each details page, and clicking the expand icon will display a drawer panel with a file upload tool. Up to 10 files can be uploaded with any combination of supported file types. Once images and documents are uploaded, they can be assigned with 'Use As' options in the table section below the upload tool. For image files, these Use As options include Preferred Image options for each Ingredient, Inventory, and Menu uses. These Preferred Image flags will determine which image is selected as the primary image when using that item in various sub-type contexts, such as displaying the Preferred Inventory Image when using the Ordering function. For both image and document files, there are document labels that can be assigned for tracking purposes, such as CN Label, Product Formulation Statement, or Buy American Exemption Letter."

## Release Notes Internal
"The 'Preferred Ingredient' image will be prioritized on the Items page split view and when searching ingredients on recipes. The 'Preferred Inventory' image will be prioritized on the Items page for non-food items and is shown on the Inventory Ordering cart. The 'Preferred Menu' image will be displayed when searching and managing menu items on a Variety Menu Item, as well as when adding menu items to a Menu."

## Description [TIER 3 — never cite as AC]
Attach documents to items, recipes and other IM types for product formulation statements, CN labels, crediting documents, and other important pieces of information.

==== NXT-43239 ====
## Acceptance Criteria [TIER 1]
- Redesign Nutrient Details to more effectively use the card space (shorter rows, smaller inputs, 50% page width, improved error handling)
- Automatically set nested nutrients to zero if the parent nutrient is set to 0 (e.g. if Total Fat is 0, Sat Fat and Trans Fat auto-zero; same for Carbohydrates → Fiber/Sugar)
- Update business rules: Vitamin A, Vitamin C, Moisture, Ash changed to optional; Moisture and Ash do not require a "Missing" checkbox as they are never present on nutrition labels
- Consider 0% as valid input (currently vitamin % not saving zeroes)

## Release Notes [TIER 1]
Title: "Nutrient Details Improvements"
Text: "The Nutrient Details card has been updated on all types within Item Management. The card has been redesigned to better utilize available space, and some functional enhancements have been made. Vitamin A and Vitamin C are now considered optional for nutrient entry, and leaving them blank will automatically enable the Is Missing option. Similarly, Moisture and Ash have been made optional and the Is Missing option has been removed, as these nutrients are generally not provided on labels. Data entry and error handling have also received some usability improvements."

## Release Notes Internal
"Nutrient Details update also includes a resolution to an issue with entering 0 on Daily Value % not being accepted. Some data entry enhancements have been made for Total Fat and Total Carbohydrates; entering 0 for these values will now automatically populate the nested nutrients with 0 as well."

## Description [TIER 3 — never cite as AC]
Nutrient Details redesigned to read more like a nutrition label. Optimized sizing for condensed views.

==== NXT-30100 ====
## Acceptance Criteria [TIER 1]
- Provide a 1/3 width card for the miscellaneous food item info
- Card completion or not does not affect the next section from being available

## Release Notes [TIER 1]
EMPTY

## Release Notes Internal
EMPTY

## Description [TIER 3 — never cite as AC]
Fields: Edible Yield Factor (numeric); Sub Ingredients (comments popup, up to 500 chars); Standard Recipe Directions (comments popup, up to 500 chars); Buy American (checkbox); Exemption Letter (upload control); Locally Grown (checkbox). NOTE: Per NXT-47249, Edible Yield Factor has been moved from Ingredient Info to the Units card. Ingredient Info card may no longer display Yield Factor.

==== NXT-47249 ====
## Acceptance Criteria [TIER 1]
- Make Yield Factor configurable on each serving in the Units card
- Provide a dedicated step for editing yield factor (show only serving sizes; add dedicated Yield Factor column; allow Yield Factor to be edited for each serving size; add a custom record at the bottom for 'Default (all other measures)')
- Remove Yield Factor from Ingredient Info card (moved to Units)
- Don't show the percentage in view mode if it's set to 100%
- Update all Recipe calculations to use the serving specific yield factor (if applicable)

## Release Notes [TIER 1]
EMPTY

## Release Notes Internal
EMPTY

## Description [TIER 3 — never cite as AC]
Serving-specific yield factors allow a single item (like apples) to have different yield factors for different serving contexts (sliced, cored, etc.).

==== NXT-30102 ====
## Acceptance Criteria [TIER 1]
- Load the Contributions section once the Serving Measures is successfully saved
- Add/Edit Contributions in the slideout
- Allow user to "skip for now" if they do not want to enter the information at the time

## Release Notes [TIER 1]
EMPTY

## Release Notes Internal
EMPTY

## Description [TIER 3 — never cite as AC]
Contributions section at 1/3 width to the right of Nutrients. Edit/Add in slideout (see Recipes for example). Can create contributions without nutrient information. Displayed in 'card' format.

==== NXT-37216 ====
## Acceptance Criteria [TIER 1]
- Redesign the Contributions card to more closely resemble the Allergens card
- List each applicable component on a dedicated row within the card (sequence: Fruits, MMA, Grains, Milk, Veg)
- Display the component icon circle for each applicable contribution
- Display the specific contributions in chips within the row
- Color the contribution chips accordingly (color per food component)
- Use different icons for Cups vs. Ounce Equivalent
- Also update the Menu Items list Contributions column to use the same styling for the chips (short version chips)

## Release Notes [TIER 1]
EMPTY

## Release Notes Internal
EMPTY

## Description [TIER 3 — never cite as AC]
Contributions card redesigned with component chips (icons and colors). Veg subcategories use specific color codes. Short version chips used in list views.

==== NXT-30103 ====
## Acceptance Criteria [TIER 1]
- Load the Allergens section
- Can create or enter allergen without having nutrient/contribution information entered
- Allow user to "skip for now" if they do not want to enter the information at the time

## Release Notes [TIER 1]
EMPTY

## Release Notes Internal
EMPTY

## Description [TIER 3 — never cite as AC]
Allergens section displayed in 1/3 width below Contributions. Edit/Add in slideout. Update Allergen Feature Disclaimer: replace 'PrimeroEdge' with 'SchoolCafe'. Condensed appearance for card fit.

==== NXT-41275 ====
## Acceptance Criteria [TIER 1]
- Remove the grid based approach in favor of a simple label statement for each applicable Allergen Form (in every applicable screen: Item Details, Recipe Details, Menu Item Details, POS-Only Details; make it a reusable component)
- Prioritize allergen forms in the following order: 'Contains' form, 'Processed....' form, 'May Contain' form, 'Free From'
- List each allergen after the appropriate allergen form label (bold; custom allergens after standard; sorted alphabetically ascending within each row; 'Free From' label bold, allergens regular)
- Use icon for each appropriate status: octagon alert with red for Contains; circle alert with orange for May Contains or Processed; green "not applicable" icon for Free From
- Move the Disclaimer to the more actions menu option (still opens the slideout)

## Release Notes [TIER 1]
EMPTY

## Release Notes Internal
EMPTY

## Description [TIER 3 — never cite as AC]
Allergens card view mode redesigned to show only applicable allergens with applicable forms. No longer displays all allergens with empty states.

==== NXT-24128 ====
## Acceptance Criteria [TIER 1]
Entry Point:
- A Custom allergens option is added under IM configuration area
- Option: Custom Allergen

Result Grid:
- Display fields as per mockup
- User can search and sort fields on result grid
- User can edit Custom Allergen Description (Description only, and only for user-created custom allergens)
- User can deactivate Custom Allergen only if no items/recipes/menus are using it (confirmation message required)

Slide Out Card fields:
- Custom Allergen Description [free text box] — Mandatory
- Data Source [dropdown, Local only] — Mandatory

On SAVE:
- Validation: Custom Allergen is mandatory, no duplicates allowed
- If duplicate: warn "Custom Allergen already in use, please use a different Custom Allergen name"
- Newly added allergen listed on result grid
- System returns to Custom Allergen screen

Other:
- X icon closes slideout, cancels transaction
- Pagination present
- Export [PDF Format]: title "Custom Allergen Configuration"; covers Description and Data Source Name fields; header: Updated by [User Name], Generated on [System date/time UTC]; footer: Powered by SchoolCafe for [School District Name]; pagination present

General:
- Once user selects configuration a pop-up window is presented asking for data source and configuration option. When user clicks Apply, system redirects to configuration area.
- Only use Local data source.

## Release Notes [TIER 1]
EMPTY

## Release Notes Internal
EMPTY

## Description [TIER 3 — never cite as AC]
User story for creating custom allergens in the IM Configuration area to help identify items with allergens.

==== NXT-39594 ====
## Acceptance Criteria [TIER 1]
- Redesign the Recipe details page to appear similarly to the Item overhaul design
- Create a tab structure for Recipes
- Create a Menu Item tab

## Release Notes [TIER 1]
EMPTY

## Release Notes Internal
EMPTY

## Description [TIER 3 — never cite as AC]
Populate the Menu Item & POS Info tab per new design. Insert Max Carryover Days into Leftover Category field space. Move Favorite to header. Show on POS toggle controls POS attributes and Pricing table presence. Once saved, adjust card for view mode.

==== NXT-30155 ====
## Acceptance Criteria [TIER 1]
- Enable the POS Info tab if the user specifies the item as a POS Item
- Load the POS attributes and Pricing section under the POS tab
- Maintain existing logic, rules, etc.
- Separate pricing for Students and Adults with tabs

## Release Notes [TIER 1]
EMPTY

## Release Notes Internal
EMPTY

## Description [TIER 3 — never cite as AC]
Main attributes: Button Name (English) — Mandatory; Button Name (Spanish); Meal Type (optional, required if using Generic Item Pricing); POS Item Category; Flags (Meal, Vendable, Generic Item). Pricing section flags: Taxable, DM Reimbursable Meal, Use Generic Item Pricing. Pricing grid: Students and Adults tabs. 'Set All Prices' option per tab in edit mode.

==== NXT-40447 ====
## Acceptance Criteria [TIER 1]
- Provide the ability to add additional serving sizes for the Menu Item which are scaled from the primary measure (or using weight/volume)
- Separate this "Add Serving" function from the primary Add Serving function (this function is only adding Menu Item servings)
- Within the Menu Item tab specific version of the Units card, provide an Edit mode
- Within the MI Units edit mode, provide a "+Menu Serving" button
- When +Menu Serving is clicked, insert a new serving size row: only Amount and Description editable; pre-load Description with original Menu Item serving measure; Description is a dropdown (not free text) with only the menu item measure and corresponding weight or volume measures; Calculate Weight/Volume by scaling from original measure; Use row level Save icon
- Provide guided informational messages in the banner bar

## Release Notes [TIER 1]
EMPTY

## Release Notes Internal
EMPTY

## Description [TIER 3 — never cite as AC]
Allows creation of additional scaled serving sizes for menu items (e.g. different size servings for different school levels).

==== NXT-54229 ====
## Acceptance Criteria [TIER 1]
- Certain functions should be enabled based on sub-type logic, rather than selected tab:
  - Menu Serving and Exceptions should be available once the item is a Menu Item
  - Cost/Value should be available as soon as there is at least one unit
  - GTIN/UPC should be available once there is a pack size unit or an inventory-able serving (1 Each)
  - Disable or gray out the Add button and Update button options when they're not available (do not remove them from the button options)
- When to exit placeholder mode
- Long-term editing: changing weight for recipe ingredient; changing weight for DMI; changing description for ingredient or DMI; changing pack size descriptions; changing sub-quantities (including inventory-able servings and dual units)
- Match banners/font/styling for Summary Info card

## Release Notes [TIER 1]
EMPTY

## Release Notes Internal
EMPTY

## Description [TIER 3 — never cite as AC]
Units card behavior consistent across all tabs. Sub-type logic governs button availability rather than tab selection.

==== NXT-36583 ====
## Acceptance Criteria [TIER 1]
- Add a small selection for Recipe HACCP Process (this will belong to the Steps process and tab)

## Release Notes [TIER 1]
EMPTY

## Release Notes Internal
EMPTY

## Description [TIER 3 — never cite as AC]
HACCP section above Steps card. HACCP Process selection: No Cook, Same Day Service, Complex Food (reflects configured processes). Pre-Preparation Instructions (may be included). Independent Save/Cancel. Validate saves against added control points. If changing process clears associated CCPs, warn user.

==== NXT-36742 ====
## Acceptance Criteria [TIER 1]
- Allow CCPs to be added to the recipe like steps
- Allow added CCPs to be edited for Critical Limit and Corrective Action

## Release Notes [TIER 1]
EMPTY

## Release Notes Internal
EMPTY

## Description [TIER 3 — never cite as AC]
'Add Control Point' sub-option on the Add Steps button (split button). CCP selection from list configured for selected HACCP process. Show Description, Critical Limit, Corrective Action (accordion). Upon CCP selection: Critical Limit and Corrective Action fields editable (load with configured defaults). Required fields must be populated before CCP can be saved. CCPs inserted into recipe as steps.

==== NXT-40479 ====
## Acceptance Criteria [TIER 1]
- Display a read-only 'Inventory Item Active Contracts' card which has a preview of the Contract Items page details for that item (show only active status contracts)
- [Struck through: Provide an edit icon for contract pricing — moved to future story NXT-40480]
- Provide an icon to open Inventory in a new tab: navigate to the Contract Items page; pre-load the contract for the relevant item

## Release Notes [TIER 1]
EMPTY

## Release Notes Internal
EMPTY

## Description [TIER 3 — never cite as AC]
Inventory Info tab on the Item page for viewing GTIN/UPC numbers, item substitutions, and expanded pack size details. Mockup shows state when no contracts exist.

==== NXT-58442 ====
## Acceptance Criteria [TIER 1]
- Only display the Taxable option when the Adult tab is selected on POS Pricing (for both view and edit mode; note: POS does not consider tax for students)
- Remove the 'DM Reimbursable Meal' option from POS Only Items (hide in view/edit mode; do not delete code; set flag to False)

## Release Notes [TIER 1]
EMPTY

## Release Notes Internal
EMPTY

## Description [TIER 3 — never cite as AC]
Story driven by implementation issue from FreshDesk ticket 271876. Taxable option previously appeared on Students tab causing confusion.
