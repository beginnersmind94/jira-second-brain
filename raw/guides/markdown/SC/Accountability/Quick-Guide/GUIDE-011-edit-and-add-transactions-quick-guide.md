---
id: GUIDE-011
title: "Edit and Add Transactions Quick Guide"
platform: "SC"
module: "Accountability"
content_type: "Quick Guide"
source_url: "https://s3.us-east-1.amazonaws.com/docs.schoolcafe.com/Accountability/Sessions_Edit_Add_Transactions_Quick_Guide.pdf"
local_pdf: "raw/guides/pdf/SC/Accountability/Quick-Guide/GUIDE-011-edit-and-add-transactions-quick-guide.pdf"
curated_against_raw_sha: "996dae3ae33744ee"
curated_against_raw_at: "2026-05-18T20:39:38+00:00"
last_reviewed_by: ""
status: "needs_initial_review"
---

# Edit and Add Transactions Quick Guide

> Seeded from the raw extraction. Edit freely. When the raw drifts, review the diff and update this file, then mark it reviewed with `python scripts/mark_guide_reviewed.py GUIDE-011`.

When reconciling Sessions, the user may

## Find a Session
1. Select the Site Code/Site Name, Status, and Date
2. Click the SEARCH button
   Session information displays in the table below.
3. Identify the Session that you want to edit or add a transaction
4. Click the Reconcile icon for the desired Session
   The Reconciliation page displays.

## Edit Transaction
1. Scroll down to the Transactions section of the Reconciliation page
2. Select the Edit (Paper) icon for the desired transaction in the Action(s) column
   The Edit Transaction slide deck displays.

## Add Item
With the transaction selected and the Edit Transaction slide deck open
1. Scroll to the Sales Details section and click the ADD button
   The POS Menu Items window displays.
2. Select the Menu Item Category
3. Select the Menu Item
4. Enter the Quantity
5. Click the SAVE button
   The window closes, and you are returned to the Edit Transaction slide deck.
6. Enter the Amount Tendered, Deposit Amount, Change Returned, and Payment Method, if needed
7. Enter the required Comments
8. Click the SAVE button to add the transaction
   You are returned to the Reconciliation page.

## Edit Sales Quantity
With the transaction selected and the Edit Transaction slide deck open
1. Scroll to the Sales Details section and select the Item to update
   Not all Items are eligible to be edited.
2. In the QTY column, enter the new quantity for the desired Item
   Adjusting the quantity may affect the balance details.
   Review the amount and update accordingly.
3. Enter the required Comments
4. Click the SAVE button
   You are returned to the Reconciliation page.

## Remove Item
With the transaction selected and the Edit Transaction slide deck open
1. Scroll to the Sales Details section and identify the Item to remove
2. Click the Trash Can icon for the desired Item
   A pop-up window appears.
3. Click the REMOVE button to confirm deletion
   Removing all Items and payments from a transaction will completely remove it from the Session.
4. Enter the required Comments
5. Click the SAVE button
   You are returned to the Reconciliation page.

## Change Payment Amount or Method
With the transaction selected and the Edit Transaction slide deck open
1. On the right-hand panel, enter the Amount Tendered, Deposit Amount, or Change Returned in the New column, if needed
<!-- Source: NXT-54012 (resolved 2024-11-04).
     AC verbatim: "Editing Transactions → Partial Payment is possible, if BABECL and Purchase Restrictions are not triggered"; "User is given an error message if BABECL or Purchase Restrictions are blocking it when they try to Save"; "Special Permission for Override is added"; "If user has the permission, they get an Override/Cancel option on the error message"; "If they Override, allow the edit to go through".
     RN verbatim: "We have made an update to the Add/Edit Transaction screen to allow for a partial payment on a transaction - where the funds may be both from cash, and a debit at the same time. This functionality has always been available at the POS, but is now available while adding or editing a transaction via the website."
     Interpretation: AC's "BABECL" is an internal system-setting code (dev-team shorthand) — rendered in guide text as "the district's charge-limit setting" since the customer-facing setting name is not in AC or RN.
     Open: customer-facing name of the BABECL system setting; specific Payment Method values eligible for partial payment; exact role-permission label as displayed in the admin UI (Description: "Override Restrictions/Charge Limits When Editing Transactions"). -->
   The Add/Edit Transaction screen allows partial payment on this screen (funds may be both from cash and a debit at the same time). If the district's charge-limit setting or the patron's Purchase Restrictions are triggered, the user sees an error message; a new override permission, when held, surfaces an Override / Cancel option on that error message, and choosing Override allows the edit through.
2. Select the correct Payment Method
3. Enter the required Comments
4. Click the SAVE button
   You are returned to the Reconciliation page.

## Add Transaction
On the Sessions page
1. Select the Site Code/Site Name, Status, and Date
2. Click the SEARCH button
   Session information displays in the table below.
3. Identify the Session to add a transaction
4. Click the Reconcile icon for the desired Session
   The Reconciliation page displays.
5. In the Transactions section, click the ADD TRANSACTION button
   The Add Transaction slide deck displays.
6. Select the transactions Meal Type
7. Click the SEARCH PATRON button
8. Enter the Patron Name/ID Number
9. Click the SEARCH button
   Patron’s information displays below.
10. Click on the desired patron
   The patron’s name displays on the right-hand panel.
   You are returned to the Add Transaction slide deck.

## Add Item
With a Session and patron selected and the Add Transaction slide deck open
1. Scroll to the Sales Details section and click the ADD button
   A pop-up window displays.
2. Select the Menu Item Category
3. Select the Menu Item
4. Enter the Quantity
5. Click the SAVE button
6. Enter the Payment Method, Payment Amount, Deposit Amount, and Change Returned, if needed
7. Enter the required Comments
8. Click the SAVE button to add the transaction
   You are returned to the Reconciliation page.

## Add Payment
With a Session and patron selected and the Add Transaction slide deck open
1. Select the Payment Method
2. Enter the Payment Amount, Deposit Amount, and Change Returned, if needed
3. Enter the required Comments
4. Click the SAVE button to add the payment to the Session
   You are returned to the Reconciliation page.
