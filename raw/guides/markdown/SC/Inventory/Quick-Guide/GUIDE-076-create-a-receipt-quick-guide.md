---
id: GUIDE-076
title: "Create a Receipt Quick Guide"
platform: "SC"
module: "Inventory"
content_type: "Quick Guide"
source_url: "https://s3.us-east-1.amazonaws.com/docs.schoolcafe.com/Inventory/Create_Receipt_Quick_Guide.pdf"
local_pdf: "raw/guides/pdf/SC/Inventory/Quick-Guide/GUIDE-076-create-a-receipt-quick-guide.pdf"
software_version: "6.3"
source_updated: "3/31/2023"
document_type: "Quick Guide"
author: "Content Team"
curated_against_raw_sha: "0f8a83eac2ced87c"
curated_against_raw_at: "2026-05-18T20:39:47+00:00"
last_reviewed_by: ""
status: "needs_initial_review"
---

# Create a Receipt Quick Guide

> Seeded from the raw extraction. Edit freely. When the raw drifts, review the diff and update this file, then mark it reviewed with `python scripts/mark_guide_reviewed.py GUIDE-076`.

This guide will cover how to create a Receipt, add a Menu Item that wasn’t initially ordered, and save the Receipt. Once Orders are received, the Perpetual Inventory will automatically update.
 An Order must be in an Open Status before it can be received.
To create a Receipt, navigate to Inventory > Orders > View Orders.
On the ORDERS tab
1. Select from the Filters as needed
2. Click the APPLY button
   The View Order List will change based on the filters selected.

3. Click the Create Receipt icon for the desired Order
   The New Receipt page displays.

In the Receipt Details section
4. Verify the Site, Vendor, Order #, Order Amount, Receipt Amount, and Delivery Date
5. Enter the Transaction Date, Transaction Time, Order Delivered By, Invoice #, Invoice Amount, and Comments Fields indicated with an asterisk are required.
   If the Order Amount and Invoice Amount are not equal, then a pop-up message will appear to verify.

In the Charges / Discounts Details section
6. Enter all Charge and Discount amounts as needed

In the Receipt Items Details table
7. Verify the Received Qty
8. In the Confirm column, click the Checkbox for each Item that was received
   Click the header Checkbox to select all Items.
   The Checkbox(es) will illuminate purple for the confirmed Item(s).
9. Verify the Item Price, Delivery Fee, Processing Fee, and Net Off Invoice fields for each Item
10. Click the ADD ITEM button to add a new Item to the Order
   See the ADD ITEM section for more information.
11. Use the icons in the Action column to add the Date on Product or add Comments for an Item as needed

## ADD ITEM(S)
When creating a Receipt, the user can add an Item if an Item was received and is not on the original Order.
In the Receipt Item Details table
1. Click the ADD ITEM button

## The Add Items to Receipt for Order page
displays.
2. Select from the Filters as needed
3. Click the APPLY button
   The Item Select table will change based on the filters selected.

4. Click the Checkbox for each Item to add to the Order
   The Checkbox(es) will illuminate purple for the confirmed Item(s).

5. Click the ADD ITEMS button
   The user is returned to the New Receipt page.
   The added Item appears in the Receipt Item Details table.
6. Enter the Received Qty
7. In the Confirm column, click the Checkbox
8. Verify the Item Price, Delivery Fee, Processing Fee, and Net Off Invoice fields
9. Use the icons in the Action column to add the Date on Product or add Comments for the Item as needed

## CONFIRM RECEIPT
Once all the required information is confirmed, a Receipt will be created. All received Items will be added to the Perpetual Inventory.
1. Click the CONFIRM button
   The user is navigated to the RECEIPTS tab.

A success message displays.

Click the BACK TO VIEW RECEIPTS button to navigate to the View Order Receipts page.
