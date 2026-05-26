---
id: GUIDE-071
title: "Create Variety Menu Items Quick Guide"
platform: "SC"
module: "Item Management"
content_type: "Quick Guide"
source_url: "https://s3.us-east-1.amazonaws.com/docs.schoolcafe.com/ItemManagement/Create_Variety_Menu_Items_Quick_Guide.pdf"
local_pdf: "raw/guides/pdf/SC/Item-Management/Quick-Guide/GUIDE-071-create-variety-menu-items-quick-guide.pdf"
software_version: "7.3"
source_updated: "4/4/2024"
document_type: "Quick Guide"
author: "Content Team"
curated_against_raw_sha: "d529af7538a54834"
curated_against_raw_at: "2026-05-18T20:39:47+00:00"
last_reviewed_by: ""
status: "needs_initial_review"
---

# Create Variety Menu Items Quick Guide

> Seeded from the raw extraction. Edit freely. When the raw drifts, review the diff and update this file, then mark it reviewed with `python scripts/mark_guide_reviewed.py GUIDE-071`.

This guide will cover how to create Variety Menu Items. This includes entering the recommended information for the Menu Item and Servings cards as well as the Images & Docs card. It will also cover the various tabs available when creating a Variety Menu Item.
Variety Menu Items provide a different kind of flexibility for Menu Planning. This type of Menu Item is a placeholder with other Menu Items linked to it. Variety Menu Items are created with specific meal contribution values, and then Menu Items that meet the contribution requirement are assigned. Users can select which items to serve for the day within a Production Record. When publishing menus, the only name that displays is the name of the Variety Menu Item.
An example could be assorted fruit or cereal variety. Cereal variety is the name that would be shown in Family Hub. On the Production Record, users indicate which specific Menu Items they will serve and document leftovers (e.g., Cheerios, Chex, Cinnamon Toast Crunch).
To create Variety Menu Items, navigate to Item Management > Menu Items.

## MENU ITEM CARD
The Menu Item card contains high-level information for the Menu Item such as the Menu Item Name, Button Name, and Menu Item Category.

## Process / Descriptions Images
On the Menu Items page
1. Click the + NEW button

2. Select Variety Menu Item

## The Create Variety Menu Item page
displays.

On the Summary card
3. Enter the following information:
- Click the Show on POS toggle if the
Menu Item will be sold directly on the
POS
- Menu Item Name, Menu Item

## Category, and Button Name (English)
These fields are required.
- Marketing Name & Description, Button Name (Spanish), Meal Type,

## and Tags
These fields are optional.
- Click the POS Entree checkbox as needed
 The POS Entree option is used to identify this Menu Item as a reimbursable meal.

## SERVINGS CARD
The Servings card allows users to configure the Menu Item serving size and set the contribution.
On the Servings card
1. Enter the Amount, Description, and Weight These fields are required.
2. Click the SAVE button to continue
   The page refreshes, and the serving size is added to the Servings card.

3. Click the CONTRIBUTION INFO chip to assign contribution information for the added serving size
   The Contribution Information slide deck displays with editable fields.

4. Enter the contribution information as needed for the Menu Item
   At least one Food Component value must be entered to create the Variety Menu Item.
   The contribution selected must be the minimum contribution for all items added to the Variety Menu Item.
5. Click the SAVE button to retain the contribution information
   The card refreshes, and the contribution information is added.
   The MENU INFO tab will be selected.

An icon for the selected Food Components appears in the Servings card beside the Description.
Note the different Identifiers visible for the serving size (Default Serving Measure and Menu Item Serving ).
The NUTRIENT INFO and MENU INFO tabs have an Incomplete Sub-Type Status.

MENU INFO TAB
The MENU INFO tab allows users to assign individual Menu Items to the Variety Menu Item.
The MENU INFO tab has an Incomplete Sub-Type Status. This means this sub-type has been enabled but is not ready for use.
On the MENU INFO tab
1. Click the View More Options icon on the Menu Items card

2. Select Edit
   The Menu Item Search card displays.

3. Use the Menu Item Search card to search for Menu Items to add
   Users can search by description to find specific Menu Items or enter “MI-” to search all Menu Items with the minimum food component.
4. Click the Arrow icon to generate results

5. Select the desired Menu Item
   The row of the selected Menu Item is highlighted.
6. Click the + ADD button
   The Menu Item is added to the Menu Items card with additional fields.

Any added Menu Items will be assigned the Serving Quantity that matches the Variety Menu Items contribution values.
A Directions field is available to add instructions as needed.
This Menu Item can be deleted as needed.
Repeat steps 3-6 to add as many Menu Items as needed.

7. Click the SAVE button once all the Menu Items are added
   The card refreshes, and the Menu Items are added to the Menu Items card.

The MENU INFO tab and NUTRIENT INFO tabs change to an Active Sub-Type Status.
As the Menu Items are added, the Cost / Value are dynamically calculated in the Servings card, and the NUTRIENT INFO tab will have calculated average values based on the added Menu Items' nutritional values.
This Variety Menu Item is officially created and found within Menu Planning.
The Menu Item Metrics card is in development and does not have data for now.

NUTRIENT INFO TAB
Once Menu Items are assigned, the nutrients are calculated and automatically updated on the NUTRIENT INFO tab. This applies to the Nutrient Details and Allergen Info cards which display a ‘System Calculated’ chip to indicate this auto calculation. However, the Contribution information cannot be edited. All Menu Items must be removed from the Variety Menu Item to change contributions.
The NUTRIENT INFO tab has an Active Sub-Type Status. This means this sub-type has been enabled and is ready for use.
On the NUTRIENT INFO tab
Note that the Serving Size is available based on what was entered in the Servings card.
1. Click the View More Options icon on the Nutrient Details card

2. Select Edit
   The card refreshes, and editable fields display.

3. Edit all the required nutrient information for the Menu Item
   Click the Missing Value checkbox for a nutrient if specific nutrient details are not included on the label.
4. Click SAVE to retain the nutrient details
   The card refreshes, and the nutrient details are added.
   If the nutrient details are edited, the SYSTEM CALCULATED chip will change to MANUALLY ENTERED.

Users can click the MANUALLY ENTERED chip to revert to the system calculated values based on the recipe ingredients. A confirmation is required.

 Contributions cannot be edited. All Menu
Items must be removed to change the contributions.

On the Allergen Info card
5. Click the View More Options icon

6. Select Edit
   The allergen slide deck displays.

View the Allergen Feature Disclaimer before assigning allergens to the Menu Item.
7. Click the No allergens indicated checkbox if there are no allergens indicated with the Menu Item
   The Standard Allergens and Custom Allergens sections will no longer appear if this checkbox is clicked.
8. Select the checkbox(es) from the list of Standard Allergens if there are allergens associated with the Menu Item
9. Click + ADD CUSTOM ALLERGEN if an allergen is associated with the Menu Item but is not a standard allergen
   See steps 11-16 below to add custom allergens.
10. Click the SAVE button to retain the standard allergen information
   The card refreshes, and the standard allergen information is added.
   An icon displays for whichever standard allergens were selected.
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
Users can click the MANUALLY ENTERED chip to revert to the system calculated values based on the Menu Item ingredients. A confirmation is required.
All the nutrient information is entered.

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

The image has now been added to the Menu Item.
