---
id: GUIDE-069
title: "Create Food Items Quick Guide"
platform: "SC"
module: "Item Management"
content_type: "Quick Guide"
source_url: "https://s3.us-east-1.amazonaws.com/docs.schoolcafe.com/ItemManagement/Create_Food_Items_Quick_Guide.pdf"
local_pdf: "raw/guides/pdf/SC/Item-Management/Quick-Guide/GUIDE-069-create-food-items-quick-guide.pdf"
software_version: "7.3"
source_updated: "4/4/2024"
document_type: "Quick Guide"
author: "Content Team"
curated_against_raw_sha: "45f5f017a3ab81bf"
curated_against_raw_at: "2026-05-18T20:39:46+00:00"
last_reviewed_by: ""
status: "needs_initial_review"
---

# Create Food Items Quick Guide

> Seeded from the raw extraction. Edit freely. When the raw drifts, review the diff and update this file, then mark it reviewed with `python scripts/mark_guide_reviewed.py GUIDE-069`.

This guide will cover how to create Food Items. This includes entering the recommended information for the Item and Units cards as well as the Images & Docs card. It will also cover the recommended information in the NUTRIENT INFO, MENU INFO, POS PRICING, and INVENTORY INFO tabs.
To create Food Items, navigate to Item Management > Items.

## ITEM CARD
The Item card applies to all Item types and contains information such as the Item Description, Tags, Category information, etc.

## Process / Descriptions Images
On the Items page
1. Click the + NEW button
   The Item Details page displays.
   On the Summary card
2. Enter the following information:
- Item Description
Required for all Items.
- Item Category, Storage Category,

## and Valuation Group
Required for Inventory.
- Tags, Brand Name, Manufacturer,

## and Product Code
Optional for all Items.
3. Click the SAVE button to continue
   The page refreshes, and the Units card comes into focus.

## UNITS CARD
The Units card configures and manages all serving size and pack size units.
Serving sizes are the basis for all Ingredient usage, while pack sizes are the basis for all Inventory usage.
On the Units card
1. Select the FOOD button

2. Select the NON-FLUID (G) button or the FLUID (ML) button

3. Click the + SERVING button
   A row with fields displays below.

4. Enter the Amount and Description
5. Enter the Weight
   These fields are required.
6. Click the Checkmark icon to save the unit
   The page refreshes, and the serving size is added to the Units card.
   The NUTRIENT INFO, MENU INFO, and INVENTORY INFO tabs display. These cannot be edited until the Units card is saved.

Repeat steps 3-6 to add as many serving sizes as needed.
After adding a serving size, a Missing Costing  alert appears in the card header. This will prompt the user to enter the fair market value for Inventory and Production costing. This alert should not be reviewed until all serving and pack sizes have been added.

7. Click the + PACK button

8. Enter the Description
   This field is required.
9. Enter the Weight as needed
   This field is not required for pack size units since Inventory does not track weight.
10. Click the Checkmark icon to save the unit
   The page refreshes, and the pack size is added to the Units card.

After adding a serving and pack size, the Inventory Ready  and Missing Costing  alerts appear in the card header. This will prompt the user to link the serving and pack size units for Inventory eligibility. This alert should not be reviewed until all serving and pack sizes have been added.
The INVENTORY INFO tab has an Incomplete Sub-Type Status.
11. Click the + PACK button again to add a second pack size
   If the pack size and the serving size are the same, it is recommended to add the serving size first. Follow steps 18-28 to create a dual unit.

12. Click the ↑ HIGHER or ↓ LOWER button based on the unit being added
   A row with fields displays below or above.

13. Enter the Description
14. Enter the Sub-Qty
   These fields are required.
15. Enter the Weight as needed
16. Click the Checkmark icon to save the unit
   The page refreshes, and the pack size is added to the Units card.

The following Food Item currently has a 2-tier pack size structure.
The system allows a maximum of 3-tier pack sizes.
Note the different Identifiers added for each unit (Serving , Pack Size , and Base Unit ).
Each unit can be edited or deleted as needed.
17. Click the Inventory Ready alert to expand the banner alert message
   Banner alerts will not prevent anything from being saved or otherwise interfere with managing the Item; they will only appear until the Item is made ready for Inventory.

18. Click the Edit icon beside the banner alert message
   The Sub-Qty field for the serving size and the Weight field for the pack size base unit becomes available.

19. Enter the Sub-Qty of the serving size OR the Weight of the pack size base unit
   In this example, the Sub-Qty will be entered for the serving size.
20. Click the SAVE button to retain the information
   The page refreshes, and the sub-quantity for the serving size is added to the Units card.

The Inventory Ready  alert disappears as the serving and pack units are now linked.
21. Click the Missing Costing alert to expand the banner alert message
   Banner alerts will not prevent anything from being saved or otherwise interfere with managing the Item; they will only appear until the Item is made ready for Inventory.

22. Click the Edit icon beside the banner alert message
   The Cost / Value fields become available for each unit.

23. Enter the Cost / Value for a unit
   While entering the cost for one unit, the Cost / Value fields for the other units are disabled.
   The cost can only be entered for a single unit, which will scale to the other units based on their conversion.
24. Click the SAVE button to save the cost
   The page refreshes, and the cost is added to the Units card.

The costing information scales to the other units once the card is saved.
After adding the costing, the Missing Costing  alert is resolved and the Inventory Ready  flag appears. This means that the Item is ready to be published to Inventory.
The Manage Costing  button is now available to edit costing as needed.
The INVENTORY INFO tab changes to a Complete Sub-Type Status.
25. Click the Inventory Ready flag to expand the banner message

View the banner message for this example: This 2 tier item is published to Inventory with Carton as the BASE UNIT, counted in WHOLE NUMBERS These options can be changed until the Item is used in Inventory.
26. Click the BASE UNIT chip to select another unit as the Base Unit
   The Base Unit is automatically assigned to the lowest pack size unit. However, Items with a serving size that could also be a pack size in Inventory will have the option of promoting the serving size to be part of the pack size, therefore replacing the existing Base Unit.

View the banner message for this example: Confirm Carton as Base Unit, or promote Each to lowest Inventory Unit?
27. Select the serving size row to promote it as the Base Unit
   The banner message changes.
   The row of the selected unit is highlighted.

View the banner message for this example: Confirm Each as Base Unit, or revert Carton to lowest Inventory Unit?
28. Click the CONFIRM button to confirm the selection
   The card refreshes, and the Base Unit is changed.

View the banner message for this example: This 3 tier item is published to Inventory with Each as the BASE UNIT, counted in WHOLE NUMBERS Note the different Identifiers that are added for the serving size (Pack Size  and Base Unit ).
29. The system defaults to count the base unit in Whole Numbers; to change the base unit to decimals, click the
   WHOLE NUMBERS chip
   If the base unit should be counted in whole numbers, proceed to step 32.

View the banner message for this example: Should the item base unit (Each) be inventoried in WHOLE NUMBERS or DECIMALS?
30. Select the DECIMALS chip to change the count to decimals
31. Click the CONFIRM button to confirm the selection
   The card refreshes, and the count is retained.

The Publish toggle will automatically enable when Items are inventory ready.
32. Click the CONTINUE button to close the banner alert
33. Click the SAVE & CLOSE button to retain changes
   The page refreshes, and the Units card information is saved.

The NUTRIENT INFO tab has an Incomplete Sub-Type Status, the MENU INFO tab has a Disabled Sub-Type Status, and the INVENTORY INFO tab has an Active Sub-Type Status. Once the units are saved, these tabs are no longer grayed out.

NUTRIENT INFO TAB
The NUTRIENT INFO tab contains nutritional and ingredient information and serves as the primary tab for Food Items.
The NUTRIENT INFO tab has an Incomplete Sub-Type Status. This means this sub-type has been enabled but is not ready for use.
On the NUTRIENT INFO tab
Note that the Serving Size is available based on what was entered in the Units card.
1. Click the View More Options icon on the Nutrient Details card

2. Select Edit
   The card refreshes, and editable fields display.

3. Enter all the required nutrient information for the Item
   Fields indicated with an Asterisk are required.
   Click the Missing Value checkbox for a nutrient if specific nutrient details are not included on the label.
4. Click SAVE to retain the nutrient details
   The card refreshes, and the nutrient details are added.

The NUTRIENT INFO tab changes to an Active Sub-Type Status.

On the Ingredient Info card
5. Click the View More Options icon

6. Select Edit
   Editable fields display.

7. Enter the following information:
- Edible Yield Factor (%), Sub

## Ingredients, and Standard Recipe
Directions
- Standard Recipe Directions: Any directions entered here will be added to any multi-item recipe, including this item.
Directions do not populate for Direct

## Menu Items. See the Menu Info Tab
section for more information.
- View the Assigned to Recipes number

## Click the Eye icon to navigate to the
Recipes page and view the recipe that uses the Item as an Ingredient.
- Click the Locally Grown and Buy American checkboxes as needed
If the Buy American checkbox is clicked, the option to upload an Exemption Letter will not be available.
- Click the Upload icon to upload the exemption letter
8. Click SAVE to retain the ingredient information
   The card refreshes, and the ingredient information is added.
   A success message displays.

On the Contribution Info card
9. Click the View More Options icon

10. Select Edit
   The Contribution Information slide deck displays with editable fields.

11. Enter the contribution information as

## needed for the Item
12. Click the SAVE button to retain the contribution information
   The card refreshes, and the contribution information is added.
   A card icon displays for whichever food components were selected.

On the Allergen Info card
13. Click the View More Options icon

14. Select Edit
   The allergen slide deck displays.

 View the Allergen Feature Disclaimer before assigning allergens to the Item.
15. Click the No allergens indicated checkbox if there are no allergens indicated with the Item
   The Standard Allergens and Custom Allergens sections will no longer appear if this checkbox is clicked.
16. Select the checkbox(es) from the list of Standard Allergens if there are allergens associated with the Item
17. Click + ADD CUSTOM ALLERGEN if an allergen is associated with the Item but is not a standard allergen
   See steps 19-24 below to add custom allergens.
18. Click the SAVE button to retain the standard allergen information
   The card refreshes, and the standard allergen information is added.
   An icon displays for whichever allergens were selected.

To add a custom allergen that is not available,

## navigate to Item Management > Configuration
> Item Configuration.
On the Item Configuration page
19. Select Custom Allergerns from the dropdown
20. Click the APPLY button

## The Custom Allergen Configuration page
displays.
21. Click the + NEW button
   The ADD CUSTOM ALLERGEN slide deck displays.

22. Enter the Custom Allergen Description

## The Data Source defaults to Local and
cannot be changed.
23. Click the Allergen available on Family Hub menus toggle on as needed
24. Click the SAVE button to save the custom allergen
   The custom allergen is added and a success message displays.

On the Allergen Info card
25. Click the View More Options icon

26. Select Edit
   The allergen slide deck displays.

27. Click + ADD CUSTOM ALLERGEN
   A row with fields displays below.

28. Select the custom allergen from the dropdown
   The custom allergen can be deleted as needed.
29. Select the checkbox that applies to the custom allergen
30. Click the ADD button
   The custom allergen is added to the Custom Allergen section.

31. Click the SAVE button
   The custom allergen is added to the Menu Item.

An icon displays for whichever allergens were selected.

All the nutrient information is entered.

MENU INFO TAB
The MENU INFO tab allows users to turn an Item into a Direct Menu Item. A Direct Menu Item is a single item that will be served on a menu.
The MENU INFO tab has a Disabled Sub-Type Status. This means that this sub-type has not been enabled.
Once the MENU INFO tab is selected, the system will prompt the user to configure the Menu Item Serving Size.
The first step for configuring the Menu Item is to select the serving size in the Units card. If only a single serving size is configured, the system will skip this step and automatically select that serving.
On the MENU INFO tab
1. Navigate to the Units card at the top of the page and click the CREATE MENU ITEM button
   The card refreshes, and fields display in the Menu Item card below.

On the Menu Item card
2. Enter the following information:
- Click the Favorite icon to flag this Menu Item as a favorite on the Menu Planner
- Click the Show on POS toggle if the Menu Item will be sold directly on the POS Once the card is saved, additional fields and the POS PRICING tab will display.
The following fields are required:
- Menu Item Name: This name will display on Menus, Production Records, and internal reports.
- Button Name (English): This will display as the button name in English on the POS.
- Menu Item Category: This is the default category when creating menus.
- Max Days: This designates on a Production Record how many days an item can be carried over. This only applies for the Unspecified and Carryover Leftover Categories.
The following fields are optional:
- Marketing Name & Description: This is the name and description that will appear in Family Hub.
- Button Name (Spanish): This will display as the button name in Spanish on the POS.
- Meal Type: This is used when building Menu Grids on the POS.
- Leftover Category: This is used in Production Records to determine what to do with any leftover Items that were produced.
- Tags: This is used as a custom filter.
- Preparation Site Item checkbox: This is used to identify Menu Items that will be prepared at a prep site.
- Show in Summary checkbox: This is used as a filter in the Menu Calendar Report.
- POS Entree checkbox: This is used to identify this Menu Item as a reimbursable meal.
3. Click the SAVE button to continue
   The page refreshes, and the Menu Item information is saved.
   Once saved, the MENU INFO tab changes to the MENU & POS INFO tab.
   The POS PRICING tab also displays.

Note that a Menu Item Serving  icon is added to the Identifiers for the selected serving size.
On the Units card
4. Click the Edit icon to manage the Menu Item Serving Sizes and Exceptions The card refreshes into its editable state.

5. Click the + MENU SERVING button to configure additional Menu Serving Sizes
6. Click the EXCEPTIONS button to configure Serving Exceptions for Menu Item Servings

7. Select the Meal Pattern & Serving Group for the serving size
8. Click the NOT SERVED button as needed
   Use this button if a Serving Group is not allowed to be served a specific Item.
   A row displays below the serving size.

The NOT SERVED  button is disabled.
9. Select the Meal Pattern & Serving Group that cannot be served this Item
10. Click the SAVE button to retain changes
   The card refreshes, and the exceptions are added to the Units card.

Note that an Exception   icon is added to the Identifiers for the selected Menu Item serving.
Each exception can be edited as needed.
11. Click the SAVE & CLOSE button to retain changes
   The card refreshes, and the Units card information is saved.

The Steps card provides the ability to configure the HACCP Process, Pre-Preparation Instructions, Prep Time, Cook Time, and directions.
On the Steps card
12. Click the ENABLE RECIPE button
   The card refreshes, and editable fields display.

13. Click the View More Options icon on the Steps card

14. Select Edit
   The card refreshes, and editable fields display.

The first time the Steps card is edited, it will enter the edit mode for Step 0. This is where all recipe configuration comes before the recipe is produced. This includes the HACCP Process, Pre-Preparation Instructions, Prep Time, and Cook Time.
15. Select the HACCP Process
   By default, None is selected, preventing any control points from being added to the steps.
16. Enter the Pre-Preparation Instructions as needed
17. Enter the Prep Time and Cook Time as needed
18. Click the SAVE button to save the HACCP Process
   The page refreshes, and the HACCP Process is added to the Steps card.
   Also, the + ADD button is enabled.

The + ADD button allows users to add steps and control points.
19. Click the + ADD button to add a step to the Recipe
   The Recipe Direction field displays.

20. Enter the Recipe Direction for that step
21. Click the SAVE button to add to the step
   The card refreshes, and the step is added to the Steps card.

The added step can be edited or deleted as needed.
Repeat steps 19 - 21 to add more steps as needed.
a. Click the Edit icon to edit the step
b. Click the Delete icon to delete the step
22. Click the dropdown arrow on the + ADD button to add a control point

23. Select Control Point
   The card refreshes and options display.

The options available are dependent on the HACCP Process selected in Step 0.
24. Select the Critical Control Point
   The Critical Limit temperature and Corrective Action populate based on the critical control point selected.

25. Edit the Critical Limit as needed
26. Edit the Corrective Action as needed
27. Click the SAVE button to add the critical control point to the steps
   The card refreshes, and the control point step is added to the Steps card. These steps appear differently than the regular steps.

The added control point can be edited or deleted as needed.
The dropdown arrow can be used to view the Corrective Action for that control point step.
Repeat steps 22 - 27 to add more control points as needed.
The Steps card supports drag & drop functionality to reorder recipe steps as needed. If a step is missed and needs to be added later, it will be added as the last step but can be easily dragged to the correct position. Any reordering of steps requires the Steps card to be saved.
a. Click the Edit icon to edit the step
b. Click the Delete icon to delete the step
c. Click the Dropdown Arrow to view the details of the step
28. Click the SAVE & CLOSE button once all steps and control points are added

Once the steps are added and saved, the Steps card is officially complete.

## POS PRICING TAB
The POS PRICING tab allows users to configure pricing information for students and adults. Once this information is entered, the Menu Item will be available to add to a Menu Grid.
On the POS PRICING tab
1. Click the View More Options icon

2. Select Edit
   Editable fields display.

3. Click the Taxable checkbox as needed
4. Configure prices for various combinations of student eligibility types and site types
5. If all prices are the same, enter a price into the field and click the SET ALL PRICES button to apply costs to all enabled price fields
6. Click the Allow Sale toggle to restrict sales to certain student eligibility types
   For each student eligibility type, the allow sale toggle is enabled as a price is entered.
7. Select the ADULTS pricing tab to set pricing for staff, visitors, and program adults
   The adult POS pricing fields display.

8. Enter the adult pricing information following the previous steps
9. Click the SAVE button to retain the POS pricing information
   The page refreshes, and the POS pricing information is saved.

This Menu Item is now available within POS for the configured groups at the configured sale price.

INVENTORY INFO TAB
The INVENTORY INFO tab provides a glance into the Inventory module by showing any active vendor contracts to which the Item is assigned. For a new Item, this list would be empty.
This tab displays the main contract Item attributes for Items that have already been published to Inventory and added to a contract. It also provides a shortcut icon to open that contract on the Contract Items page in Inventory.
The INVENTORY INFO tab has an Active Sub-Type Status. This means this sub-type has been enabled and is ready for use.
On the INVENTORY INFO tab
1. Click the Edit icon to update the pack size units or manage GTIN/UPC numbers on the Units card
   The card refreshes into its editable state.

2. Click the GTIN/UPC button to enter the GTIN/UPC codes
   The GTIN / UPC  fields become available for each pack size unit.

3. Enter the GTIN/UPC codes for each pack size unit as needed
4. Click the SAVE button to save the codes
   The page refreshes, and the entered GTIN/UPC codes are added to the Units card.

Note that a GTIN / UPC  icon is added to the Identifiers for any units with a GTIN provided.
Each units GTIN/UPC codes can be edited as needed.

## IMAGES & DOCS CARD
The Images & Docs card is universal for all Item types and functions the same across all pages. This card can be used to upload various images and documents for different uses in Item Management.
On the Images & Docs card
1. Click the Expand icon

## The Management Images & Documents
slide deck displays.

2. Use the Drag & Drop Files Here option or click the SELECT FILES button to upload

## images of the Item
Multiple images can be uploaded.

A preview of the image is available for download.
3. Select an option from the Use as… dropdown
   A comment can be added for the uploaded image.
   The uploaded image can be deleted as needed.
4. Click the SAVE button once all images have been uploaded
   The slide deck closes, and the image is saved.

The image has now been added to the Item.
