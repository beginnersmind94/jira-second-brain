---
id: GUIDE-030
title: "View and Modify Menu Grids Quick Guide"
platform: "SC"
module: "Accountability"
content_type: "Quick Guide"
source_url: "https://s3.us-east-1.amazonaws.com/docs.schoolcafe.com/Accountability/Menu_Grids_View_Modify_Quick_Guide.pdf"
local_pdf: "raw/guides/pdf/SC/Accountability/Quick-Guide/GUIDE-030-view-and-modify-menu-grids-quick-guide.pdf"
curated_against_raw_sha: "8d09b6fde72d6b04"
curated_against_raw_at: "2026-05-18T20:39:40+00:00"
last_reviewed_by: ""
status: "needs_initial_review"
---

# View and Modify Menu Grids Quick Guide

> Seeded from the raw extraction. Edit freely. When the raw drifts, review the diff and update this file, then mark it reviewed with `python scripts/mark_guide_reviewed.py GUIDE-030`.

The Menu Grids function allows users to view, edit, or delete Menu Grid Names, Site Types, Meal Types, or Days Allowed.

## View Menu Grids
1. Select a Site Type to search or leave it blank to select all
2. Select a Meal Type to search or leave it blank to select all
3. Click the SEARCH button
   Menu Grids display in the table below.

## Edit Menu Grids
You can edit the Menu Grid details, including the Menu Name, Meal Type, Site Type, Days Allowed, and the Menu Grid Layout.
1. Identify the Menu Grid you wish to change
2. Click the Edit icon for the desired Menu Grid
   The Add Menu Grid page displays.
3. Modify the desired information
4. Click the SAVE button at the bottom of the page to save your changes
   A confirmation response appears atop the page, and the Menu Grid is changed.
   Repeat this process to edit additional Menu Grids as needed.

## Edit Menu Items/Categories
You can edit the Menu Item/Category details, including the Size, Position, Color, and Text.
1. On the Menu Grid Layout, identify the Menu Item/Category you wish to change
2. Click the Ellipsis (Three-Dot) icon for the desired Menu Item/Category, and options appear
3. Select EDIT
   The Edit Button pop-up window displays.
4. Modify the desired information
5. Click the SAVE button to return to the Add Menu Grid page
6. Click the SAVE button at the bottom of the page to save your changes
   A confirmation response appears atop the page, and the Menu Item/Category is changed.
   Repeat this process to edit additional Menu Items/Categories as needed.

## Delete Menu Items/Categories
1. On the Menu Grid Layout, click the Ellipsis (Three-Dot) icon for a desired Menu
   Item/Category, and options appear
2. Select DELETE, and the Menu Item/Category is deleted
3. Click the SAVE button at the bottom of the page to save the deletion
   A confirmation response appears atop the page, and the Menu Item/Category is changed.
   Repeat this process to delete additional Menu Items/Categories as needed.

## Set a Default Menu Item
A single Menu Item button on the Menu Grid can be designated as the Default Menu Item. When a patron is loaded in the POS application, the Default Menu Item is automatically added to the sales transaction if the patron is eligible to receive it.
1. On the Menu Grid Layout, click the Ellipsis (Three-Dot) icon for the desired Menu
   Item, and options appear
2. Select EDIT
   The Edit Button pop-up window displays.
3. Click the Set as Default Item toggle switch on to set the Menu Item as the Default
   Item
4. Click the SAVE button
   If a Default Menu Item is already set for the Menu Grid, a pop-up window will appear asking if you want to set the selected Menu Item as the Default Menu Item instead. Select the YES button to return to the Add Menu Grid page.
   A Star will appear on the selected Menu Items button. This is used to designate the Menu Item as a Default Menu Item.
5. Click the SAVE button at the bottom of the page to save your changes
   A confirmation response appears atop the page, and the Default Menu Item is set.

## Delete Menu Grids
Only disabled Menu Grids can be deleted.
1. Identify the Menu Grid you wish to delete
2. Click the Delete icon for the desired Menu Grid
   The Notification pop-up window displays.
3. Click YES to confirm your selection
   A confirmation response appears atop the page, and the Menu Grid is deleted.
   Repeat this process to delete additional Menu Grids as needed.

<!-- Source: NXT-54019 (resolved 2025-02-07).
     AC verbatim: "Copy Menu Grid action added to Menu Grids grid"; "User is prompted to name the menu grid"; "Name must be unique for the district"; "If name is fine, copy everything over to the new menu grid"; "User is given a success message".
     RN verbatim: "We have added a 'Copy' action to the Menu Grids page. This will create an exact copy of the existing Menu Grid with a new name."
     Open: AC does not specify the icon, hover text, or the verbatim error and success message strings (Description provides these as "Copy icon", hover "Copy Menu Grid", error "The menu name is already in use. Please enter a new menu name.", success "Menu Grid copied successfully."). The list of properties that are copied (Meal Type, Enabled, Site Type, Days Allowed, rows, columns, button positions) is described in Description as "everything"; AC says only "copy everything over". -->
## Copy a Menu Grid
A Copy Menu Grid action has been added to the Menu Grids grid. It creates an exact copy of the existing Menu Grid under a new name.

1. Select the Copy action on the desired Menu Grid
   The user is prompted to name the menu grid.
2. Enter a new name and confirm
   The name must be unique for the district. If the name is acceptable, the system copies everything over to the new menu grid and gives the user a success message.
