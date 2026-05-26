---
id: GUIDE-070
title: "Create Recipes Quick Guide"
platform: "SC"
module: "Item Management"
content_type: "Quick Guide"
source_url: "https://s3.us-east-1.amazonaws.com/docs.schoolcafe.com/ItemManagement/Create_Recipes_Quick_Guide.pdf"
local_pdf: "raw/guides/pdf/SC/Item-Management/Quick-Guide/GUIDE-070-create-recipes-quick-guide.pdf"
software_version: "7.3"
source_updated: "4/4/2024"
document_type: "Quick Guide"
author: "Content Team"
curated_against_raw_sha: "cc919b25c35dcef5"
curated_against_raw_at: "2026-05-18T20:39:46+00:00"
last_reviewed_by: ""
status: "needs_initial_review"
---

# Create Recipes Quick Guide

> Seeded from the raw extraction. Edit freely. When the raw drifts, review the diff and update this file, then mark it reviewed with `python scripts/mark_guide_reviewed.py GUIDE-070`.

This guide will cover how to create Multi-Item Recipes. This includes entering the recommended information for the Recipe and Servings cards as well as the Images & Docs card. It will also cover the various tabs available when creating a Recipe.
 If only one Item is needed, see the Create Food Item Quick Guide to add directions and HACCP steps for that Item.
Creating a Recipe is intended only for those which require multiple Items.
To create Recipes, navigate to Item Management > Recipes.

## RECIPE CARD
The Recipe card contains high-level information for the recipe such as the Recipe Description and Tags.

## Process / Descriptions Images
On the Recipes page
1. Click the + NEW button
   The Recipe Details page displays.
   On the Summary card
2. Enter the Recipe Description
   This field is required.
3. Enter any Tags as needed

## SERVINGS CARD
The Servings card allows users to configure the Serving information.
On the Servings card
1. Enter the Amount, Description, and # of Servings
   These fields are required.
2. Click the Strict Batching toggle on
   Enabling this requires the planned counts on the production record to be in increments based on the number of servings. If the number of servings is 6, the planned counts may only be entered in quantities of 6 (6,12,18).
3. Click the SAVE button to continue
   The page refreshes, and the STEPS & INGREDIENTS tab will be selected.

Tabs display below with different Sub-Type Statuses. The NUTRIENT INFO and STEPS & INGREDIENTS tabs have an Incomplete Sub-Type Status, while the MENU INFO tab has a Disabled Sub-Type Status.

STEPS & INGREDIENTS TAB
The STEPS & INGREDIENTS tab provides the ability to configure pre-preparation information, add steps with directions, and add HACCP processes and control points.
The STEPS & INGREDIENTS tab has an Incomplete Sub-Type Status. This means this sub-type has been enabled but is not ready for use.
On the STEPS & INGREDIENTS tab
1. Click the View More Options icon on the Steps card

2. Select Edit
   The card refreshes, and editable fields display.

The first time the Steps card is edited, it will enter the edit mode for Step 0. This is where all recipe configuration comes before the recipe is produced. This includes the HACCP Process, Pre-Preparation Instructions, Prep Time, and Cook Time.
3. Select the HACCP Process
   By default, None is selected, preventing any control points from being added to the steps.
4. Enter the Pre-Preparation Instructions as needed
5. Enter the Prep Time and Cook Time as needed
6. Click the SAVE button to save the HACCP Process
   The card refreshes, and the HACCP Process is added to the Steps card.
   Also, the + ADD button is enabled.

The + ADD button allows users to add steps and control points.
7. Click the + ADD button to add a step to the Recipe
   The Recipe Direction field displays.
   Directions are required, but ingredients can be added as desired.

8. Enter the Recipe Direction for that step

9. Use the Ingredients card to search for an
   Ingredient to add to the step
   The ingredient search will include both Item

## and Recipe results from the Local and CN
databases.
10. Click the Arrow icon to generate results

11. Select the desired Ingredient
   The row of the selected Ingredient is highlighted.
12. Click the + ADD button
   The Ingredient is added to the Steps card with additional fields.

13. Enter the Quantity Needed for the Item
   Click the + to add an additional Quantity Needed.
   This Ingredient can be deleted as needed.
14. Click the SAVE button once all Ingredients are added
   Repeat steps 9-14 to add as many Ingredients as needed for this step.
   The card refreshes, and the recipe step is added to the Steps card.

The STEPS & INGREDIENTS and NUTRIENT INFO tabs change to an Active Sub-Type Status.
The added step can be edited or deleted as needed.
The dropdown arrow can be used to view the Ingredient information for that specific step.
The Ingredients added to the Recipe will display in the Ingredients card.
Repeat steps 7-14 to add more steps as needed.
a. Click the Edit icon to edit the step
b. Click the Delete icon to delete the step
c. Click the Dropdown Arrow to view the details of the step

15. Click the dropdown arrow on the + ADD button to add a control point

16. Select Control Point
   The card refreshes and options display.

The options available are dependent on the HACCP Process selected in Step 0.
17. Select the Critical Control Point
   The Critical Limit temperature and Corrective Action populate based on the critical control point selected.

18. Edit the Critical Limit as needed
19. Edit the Corrective Action as needed
20. Click the SAVE button to add the critical control point to the steps
   The card refreshes, and the control point step is added to the Steps card. These steps appear differently than the regular steps.

The added control point can be edited or deleted as needed.
The dropdown arrow can be used to view the Corrective Action for that control point step.
Repeat steps 15-20 to add more control points as needed.
The Ingredients card contains a cumulative list of all the Ingredients added to the steps. Clicking on a step will highlight the applicable Ingredients. Users can click the dropdown arrow to view the details of the step.
The Steps card supports drag & drop functionality to reorder recipe steps as needed. If a step is missed and needs to be added later, it will be added as the last step but can be easily dragged to the correct position. Any reordering of steps requires the Steps card to be saved.
a. Drag & drop the steps as needed
b. Click the Edit icon to edit the step
c. Click the Delete icon to delete the step
d. Click the Dropdown Arrow to view the details of the step
e. Click the icon under the Action column to view or edit that Ingredient
This will navigate the user to the Item Details page.
21. Click the SAVE & CLOSE button once all steps and control points are added

The Steps have been completed and saved, and this Recipe is officially created. With Ingredients added, the Servings card now has calculated values for Weight and Cost.

NUTRIENT INFO TAB
Once Ingredients are saved to the Recipe, the nutrients are calculated and automatically updated on the NUTRIENT INFO tab, just as the Servings card Weight and Cost attributes are auto calculated. This applies to the Nutrient Details and Allergen Info cards, which display a ‘System Calculated’ chip to indicate this auto calculation.
The user can manually override this nutrient information if desired.
The NUTRIENT INFO tab has an Active Sub-Type Status. This means this sub-type has been enabled and is ready for use.
On the NUTRIENT INFO tab
Note that the Serving Size is available based on what was entered in the Servings card.
1. Click the View More Options icon on the Nutrient Details card

2. Select Edit
   The card refreshes, and editable fields display.

3. Edit all the required nutrient information for the Recipe
   Click the Missing Value checkbox for a nutrient if specific nutrient details are not included on the label.
4. Click SAVE to retain the nutrient details
   The card refreshes, and the nutrient details are added.
   If the nutrient details are edited, the SYSTEM CALCULATED chip will change to MANUALLY ENTERED.

Users can click the MANUALLY ENTERED chip to revert to the system calculated values based on the recipe ingredients. A confirmation is required.

On the Allergen Info card
5. Click the View More Options icon

6. Select Edit
   The allergen slide deck displays.

View the Allergen Feature Disclaimer before assigning allergens to the Recipe.
7. Click the No allergens indicated checkbox if there are no allergens indicated with the Recipe
   The Standard Allergens and Custom Allergens sections will no longer appear if this checkbox is clicked.
8. Select the checkbox(es) from the list of Standard Allergens if there are allergens associated with the Recipe
9. Click + ADD CUSTOM ALLERGEN if an allergen is associated with the Recipe but is not a standard allergen
   See steps 11-16 below to add custom allergens.
10. Click the SAVE button to retain the standard allergen information
   The card refreshes, and the standard allergen information is added.
   An icon displays for whichever allergens were selected.
   If the allergen information is edited, the SYSTEM CALCULATED chip will change to MANUALLY ENTERED.

To add a custom allergen that is not available,

## navigate to Item Management > Configuration
> Item Configuration.
On the Item Configuration page
11. Select Custom Allergerns from the dropdown
12. Click the APPLY button

## The Custom Allergen Configuration page
displays.
13. Click the + NEW button
   The ADD CUSTOM ALLERGEN slide deck displays.

14. Enter the Custom Allergen Description

## The Data Source defaults to Local and
cannot be changed.
15. Click the Allergen available on Family Hub menus toggle on as needed
16. Click the SAVE button to save the custom allergen
   The custom allergen is added and a success message displays.

On the Allergen Info card
17. Click the View More Options icon

18. Select Edit
   The allergen slide deck displays.

19. Click + ADD CUSTOM ALLERGEN
   A row with fields displays below.

20. Select the custom allergen from the dropdown
   The custom allergen can be deleted as needed.
21. Select the checkbox that applies to the custom allergen
22. Click the ADD button
   The custom allergen is added to the Custom Allergen section.

23. Click the SAVE button
   The custom allergen is added to the Menu Item.

An icon displays for whichever allergens were selected.
Users can click the MANUALLY ENTERED chip to revert to the system calculated values based on the recipe ingredients. A confirmation is required.
 To accommodate USDA rules, the system cannot automatically apply Contributions.
These require user approval to ensure accuracy. For this reason, the Contributions provide a recommendation for the component values. This is also based on the recipe ingredients, calculating the values from all ingredient contribution configurations.
On the Contribution Info card
24. Click the View More Options icon

25. Select Edit
   The Contribution Information slide deck displays with editable fields.

## View the Recommendation Disclaimer
before applying the recommendation feature for the component values.
26. Click the APPLY RECOMMENDATION button to apply recommendations for the component values
   If a recommendation does exist, the recommended values will populate in the Recommendation column.
27. Enter or edit the contribution information for the Recipe if the recommended values are not capturing for all Recipe components
28. Click the SAVE button to retain the contribution information
   The card refreshes, and the contribution information is added.
   A card icon displays for whichever food components were selected.

All the nutrient information is entered.

MENU INFO TAB
The MENU INFO tab allows users to turn Multi-Item Recipes into Menu Items.
 The Menu Item will not be created until the MENU INFO tab is saved with the required fields.
The MENU INFO tab has a Disabled Sub-Type Status. This means that this sub-type has not been enabled.
Once the MENU INFO tab is selected, the system will prompt the user to configure the Menu Item Serving Size.
The first step for configuring the Menu Item is to select the serving size in the Servings card. If only a single serving size is configured, the system will skip this step and automatically select that serving.
On the MENU INFO tab
1. Navigate to the Servings card at the top of the page and click the CREATE MENU ITEM button
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
- Leftover Category: This is used in Production Records to determine what to do with any leftover Items that were produced.
- Tags: This is used as a custom filter.
- Meal Type: This is used when building Menu Grids on the POS.
- POS Entree checkbox: This is used to identify this Menu Item as a reimbursable meal.
- Preparation Site Item checkbox: This is used to identify Menu Items that will be prepared at a prep site.
- Show in Summary checkbox: This is used as a filter in the Menu Calendar Report.
3. Click the SAVE button to continue
   The page refreshes, and the Menu Item information is saved.
   Once saved, the MENU INFO tab changes to the MENU & POS INFO tab.
   The POS PRICING tab also displays.

The MENU & POS INFO tab changes to an Active Sub-Type Status.

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

The image has now been added to the Recipe.
