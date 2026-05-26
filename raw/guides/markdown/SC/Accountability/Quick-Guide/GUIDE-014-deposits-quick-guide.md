---
id: GUIDE-014
title: "Deposits Quick Guide"
platform: "SC"
module: "Accountability"
content_type: "Quick Guide"
source_url: "https://s3.us-east-1.amazonaws.com/docs.schoolcafe.com/Accountability/Deposits_Quick_Guide.pdf"
local_pdf: "raw/guides/pdf/SC/Accountability/Quick-Guide/GUIDE-014-deposits-quick-guide.pdf"
curated_against_raw_sha: "5afcd4da67d46d2b"
curated_against_raw_at: "2026-05-18T20:39:39+00:00"
last_reviewed_by: ""
status: "needs_initial_review"
---

# Deposits Quick Guide

> Seeded from the raw extraction. Edit freely. When the raw drifts, review the diff and update this file, then mark it reviewed with `python scripts/mark_guide_reviewed.py GUIDE-014`.

The Deposits function allows users to
- Search for Deposit Slips
- Create Deposit Slips
- Edit Deposit Slips

## Search for Deposit Slips
1. Select a Site Code/Site Name
2. Enter the optional Bank Deposit Slip #
3. Select the Date
4. Click the APPLY button
   Deposits display in the table below.

## Create Deposit Slips
Creating a Deposit Slip should be done daily for all cash and checks received.
1. Click the NEW button in the top right corner of the page
   The Create Deposit Slip slide deck displays.
   All Sessions must be reconciled to create a Deposit Slip for the specific date.
2. Select the required Site Code/Site Name, Deposit Date, and optional Bank Deposit

## Slip #
3. Click the CREATE button
   The Create Deposit Slip slide deck expands to display:
- Denominations
- Check(s)
<!-- Source: NXT-71628 (resolved 2026-05-04). RN is empty; AC is the only source.
     AC verbatim: "Add a new Credit Card Section in Summary for Deposits"; "New section is automatically visible if calculated cards is > 0"; "hide by default if calculated card = 0"; "add button to add credit cards 'Add Credit Card Deposit' where when clicked: shows new Credit Card Section as a summary section line and requires comment. Once clicked replaces itself with 'Remove Credit Cards' button. TOOLTIP: 'Adds ability to track 3rd party credit card revenue to this deposit'"; "When Remove button is clicked hide section and delete Card input."; "Calculate out expected credit card amount inline with new section as 'Credit Cards (Expected: $[sum])'"; "Adjust deposit Variance by subtracting the difference between the calculated Cards and Deposited Card Amount. Variance sum = Variance sum - (Calculated Card - Deposited Card)"; "For legacy Deposit add note. New functionality is not available." -->
- Credit Card Section in Summary — automatically visible if calculated cards is > 0; hidden by default if calculated cards = 0. To surface it manually, click the "Add Credit Card Deposit" button (tooltip: "Adds ability to track 3rd party credit card revenue to this deposit"); a comment is required. The button then changes to "Remove Credit Cards"; clicking Remove hides the section and deletes the Card input. The section shows an inline "Credit Cards (Expected: $[sum])" label. Deposit Variance adjusts by subtracting the difference between the calculated Cards and the Deposited Card Amount. (On legacy Deposits, this functionality is not available.)
- Summary
<!-- Source: NXT-54193 (resolved 2024-12-26).
     AC verbatim: "Sub-Total line added for Coins and Bills"; "Shows the total of the Amount column. In the example above: $0.74, $17.00".
     RN verbatim: "We have updated Deposit Slips to show a sub-total for coins and bills." -->
4. In the Denominations section, enter the coin and bill amounts deposited
   Either enter the count or specific amounts for each. A Sub-Total line for Coins and Bills shows the total of the Amount column.
5. In the Check(s) section, click the ADD NEW CHECK button
   The Add New Check window displays.

## Add New Check
1. Enter the Check Number
2. Enter the Amount
3. Click the SAVE button
   The added check appears in the Check(s) section.
   Repeat this process to add additional checks as needed.
   Added checks can be edited (Pencil icon) and deleted (Trash Can icon).
   All checks received from the Session automatically populate in the Check(s) section.

6. Review the Summary section
   The Summary section displays the cash and check totals based on the amounts entered and the total combined deposit amount.
   The Summary section automatically updates each time a change has been made in the Cash or Check section.
7. Enter a comment
   A comment is required.
8. Click the SAVE button to add the Deposit Slip
   A confirmation response appears on the page.
   The Deposit Slip is created.
9. Click OKAY to remove the pop-up
   You are returned to the Deposits page.
   Use the Edit option to adjust the Deposit Slip if needed.
   Repeat this process to create additional Deposit Slips as needed.

## Edit Deposit Slip
The Edit option is used to edit the Deposit Slip if a change has occurred.
Editing previously created deposits is based on user Role Permissions.
1. On the Deposits page, select a Site Code/Site Name
<!-- Source: NXT-71628 (resolved 2026-05-04).
     AC verbatim: "Make the Bank Deposit Slip # field alphanumeric instead of numeric." -->
2. Enter the optional Bank Deposit Slip # (alphanumeric)
3. Select the Date
4. Click the APPLY button
   Deposits display in the table below.
5. In the Action(s) column, click the Deposit Details (Paper) icon next to the deposit you want to edit
   The Deposit Details page displays.
6. Edit the information as needed
- Denominations
- Checks – Edit or Add a new check
<!-- Source: NXT-58466 (resolved 2025-03-24).
     AC verbatim: "User can update the Deposit Slip Bank Number while editing." -->
- Bank Deposit Slip Number — the user can update it while editing
7. Enter a comment
   A comment is required.
8. Click the SAVE button to save your changes
   You are returned to the Deposits page.

<!-- Source: NXT-58466 (resolved 2025-03-24). RN field for this ticket points to NXT-56813 for the customer-facing notes (not in this CSV row).
     AC verbatim: "Delete option added"; "Confirmation prompt"; "Locked to Delete CRUD permission"; "Rolled out to Central Office, Director, SC Admin roles"; "Status available for viewing in both Grid and Details"; "Can filter out deleted slips"; "History updated → we can use a comment: Deposit Slip deleted by {{UserFirst}} + ' ' + {{UserLast}} at {{Full Timestamp}}."; "Deleted Deposit Slips are not included in rollups / reports"; "Linked Sessions moved out of Deposited (move to Reconciled)"; "User can still see deposit slip details of a Deleted slip"; "User can update the Deposit Slip Bank Number while editing".
     Interpretation: AC's "Delete CRUD permission" uses dev-team shorthand (CRUD = Create/Read/Update/Delete); rendered in guide text as "Delete permission" since the customer-facing permission name is not in AC or RN.
     Open: exact UI location of the Delete option (Description: "from inside Deposit Slip Details"); customer-facing label of the Delete permission as shown in the role-permission admin UI. -->
## Delete Deposit Slip
A Delete option has been added, gated by the Delete permission. The permission has been rolled out to the Central Office, Director, and SC Admin roles.

1. Select the Delete option
   A confirmation prompt displays.
2. Confirm the deletion
   The status is updated to Deleted. The History entry records "Deposit Slip deleted by <UserFirst> <UserLast> at <Full Timestamp>." Deleted Deposit Slips are not included in rollups or reports. Linked Sessions move out of Deposited (move to Reconciled). The user can still see the details of a Deleted slip.

The deleted-slip status is available for viewing in both Grid and Details, and the user can filter out deleted slips.
