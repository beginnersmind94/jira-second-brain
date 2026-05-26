---
id: GUIDE-073
title: "Create a Physical Inventory Quick Guide"
platform: "SC"
module: "Inventory"
content_type: "Quick Guide"
source_url: "https://s3.us-east-1.amazonaws.com/docs.schoolcafe.com/Inventory/Create_Physical_Inventory_Quick_Guide.pdf"
local_pdf: "raw/guides/pdf/SC/Inventory/Quick-Guide/GUIDE-073-create-a-physical-inventory-quick-guide.pdf"
software_version: "6.3 Updated"
document_type: "Quick Guide"
author: "Content Team"
curated_against_raw_sha: "cad8b193ef9348d6"
curated_against_raw_at: "2026-05-18T20:39:47+00:00"
last_reviewed_by: ""
status: "needs_initial_review"
---

# Create a Physical Inventory Quick Guide

> Seeded from the raw extraction. Edit freely. When the raw drifts, review the diff and update this file, then mark it reviewed with `python scripts/mark_guide_reviewed.py GUIDE-073`.

The Physical Inventory function is used to record quantities of Items that a site has received. Once the Physical Inventory is reconciled, counts entered in the Physical Inventory will replace the counts in Perpetual Inventory.
Creating a Physical Inventory includes printing the Physical Inventory Count Sheet, entering physical counts, and reconciling.
 Before reconciling a Physical Inventory, all transactions must be completed.
To create a Physical Inventory, navigate to Inventory > Inventory > Physical Inventory.

## CREATE A PHYSICAL INVENTORY

## Process / Descriptions Images
On the Physical Inventory page
1. Click the NEW button
   The New Physical Inventory slide deck displays.
2. Select the Site
3. Select the Period
   The Interim option is the type of Inventory used between regular Inventory periods. Once the Physical Inventory has been reconciled, the counts will be updated based on when the Physical Inventory was started.
4. Click the START button
   The Physical Inventory Options section displays below.

04/06/2023

The Physical Inventory Options section allows users to select which Items they want to include in their Inventory.
5. Select a QOH option
6. Select a Select by option
7. Select the Storage Category as needed
8. Select the Item Category as needed
9. Click the START button
   The SUMMARY tab for the selected site and period displays.

## PRINT PHYSICAL INVENTORY COUNT SHEET
The Physical Inventory Count Sheet is used to record quantities for each Item.
On the SUMMARY tab
1. Click the PRINT PHYSICAL COUNT button
   A printing preview of the Physical
   Inventory Count Sheet displays.
   While taking Physical Inventory, the user may be logged out. To access the Physical Inventory, navigate to Inventory > Inventory > Physical Inventory. On the Physical Inventory page, click the View icon to access the current Inventory.

ENTER PHYSICAL COUNTS
After the Item quantities have been recorded on the Physical Inventory Count Sheet, they must be entered into the Physical Inventory. If other Items were counted that were not listed on the Physical Inventory Count Sheet, they can also be added.
On the SUMMARY tab
1. Select the desired Storage Category
   Selecting any storage category will navigate the user to the ITEMS tab.
   Alternatively, users can select the ITEMS tab to select all storage categories. Once this tab is selected, all storage categories will display.

On the ITEMS tab
Users can click the ADD ITEM button to add Items to the Physical Inventory if needed. See the ADD ITEM(S) section for more information.
2. Enter the Unit Quantity and Lowest Unit Quantity for each Item as needed
   Decimals can be used in the Lowest Unit Quantity column.
   Click the Comments icon to add a comment for each Item as needed.
   Unchecking any Item checkbox will exclude the Item from the physical count and maintain the perpetual inventory value regardless of its accuracy. To represent a zero value, leave the checkbox checked and the unit fields blank, and the system will populate a zero when saved.
3. Select the SUMMARY tab once quantities have been entered

On the SUMMARY tab
4. Click the SAVE AS COMPLETE button
   Alternatively, users can click the SAVE AS INCOMPLETE button if they are not done entering quantities.
   The Physical Inventory Complete Details pop-up window displays.

5. Enter whom the Physical Inventory was

## Counted By
6. Enter any Comments
7. Click the SAVE button

## ADD ITEM(S)
The ADD ITEM button can be used to add Items that were not listed on the Physical Inventory.
If no Items need to be added, proceed to the Reconcile section.
On the ITEMS tab
1. Click the ADD ITEM button
   The Add Item slide deck displays.
2. Select the Storage Category
3. Select the Item Category
4. Select the Item
5. Enter the Useable Quantity per Case
6. Enter the Useable Quantity per Carton
7. Enter any Comments
8. Click the ADD button

RECONCILE
Once the Physical Inventory is saved as complete and the counts are verified, it must be reconciled. The physical counts will override the perpetual counts.
On the SUMMARY tab
1. Verify the information in the Physical Inventory Details section as needed
   Users can click the MODIFY button to edit their Physical Inventory if needed. A comment is required.
2. Click the RECONCILE button to finalize the Physical Inventory
   The Reconcile Inventory Details pop-up window displays.

3. Click the OK button
