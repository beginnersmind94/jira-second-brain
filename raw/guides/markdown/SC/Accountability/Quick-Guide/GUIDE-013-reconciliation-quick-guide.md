---
id: GUIDE-013
title: "Reconciliation Quick Guide"
platform: "SC"
module: "Accountability"
content_type: "Quick Guide"
source_url: "https://s3.us-east-1.amazonaws.com/docs.schoolcafe.com/Accountability/Sessions_Reconciliation_Quick_Guide.pdf"
local_pdf: "raw/guides/pdf/SC/Accountability/Quick-Guide/GUIDE-013-reconciliation-quick-guide.pdf"
curated_against_raw_sha: "cb11d69e3910d2b2"
curated_against_raw_at: "2026-05-18T20:49:51+00:00"
last_reviewed_by: "rahul.mehta@example.com"
status: "reviewed"
---

# Reconciliation Quick Guide

> Seeded from the raw extraction. Edit freely. When the raw drifts, review the diff and update this file, then mark it reviewed with `python scripts/mark_guide_reviewed.py GUIDE-013`.

The Sessions function allows users to
- Find CLOSED Sessions
- Reconcile Sessions
- Close an OPENED Session to reconcile
Reconciliation is used to determine whether the actual amount received at the POS Terminal matches the calculated amount online based on transactions for that day.
Reconciliation is a required End of Day task and must be completed for every Session generated in SchoolCafé.

## Find a CLOSED Session
Only CLOSED and BALANCED Sessions are eligible for reconciliation.
<!-- Source: NXT-60921 (resolved 2025-06-04).
     AC verbatim: "Site selector updated"; "Date selector updated"; "Separate tab added with Session # added as Search Filter"; "Existing tab: Search"; "New tab: Session #"; "3 new columns added"; "Available in Saved Views"; "Filtering added to 4 columns"; "Status tags colorized".
     RN verbatim: "The Site dropdown is now a multi-select!"; "The Date selector has been updated to have more modern ranges. ('This Week', 'Last Week')"; "A Session # search tab has been added to help you find a specific session."; "New grid columns - Cashier, Total Sales, and Meal Count."; "Filters added to: Terminal, Cashier, Opening Balance, Closing Balance, Over/Under"; "Session Status tags are now color-coded." -->
1. Select the Site Code/Site Name (the Site dropdown is a multi-select), Status, and Date (the Date selector supports ranges such as 'This Week' and 'Last Week')
   A Session # search tab has been added beside the existing Search tab to help find a specific session.
2. Click the SEARCH button
   Session information displays in the table below. New grid columns — Cashier, Total Sales, and Meal Count — are available, with filters on Terminal, Cashier, Opening Balance, Closing Balance, and Over/Under. Session Status tags are color-coded.
3. Identify the Session with the CLOSED status and $0.00 Over/Under to reconcile

## Reconcile a Closed Session
1. Click the Reconcile icon for a CLOSED Session
   The Reconciliation page displays.
2. Review the Summary details
3. Verify this message is displayed in orange - THE SESSION IS BALANCED AND READY TO RECONCILE
4. Click the RECONCILE button
   A green THE SESSION IS RECONCILED statement displays.
   RECONCILED displays in green.
   Click the BACK button to return to the Sessions page.

<!-- Source: NXT-36439 (resolved 2023-04-18).
     AC verbatim: "Delete Session option added."; "Requires a confirmation from the user."; "Requires a comment."; "Undo button available for 30 seconds before deletion begins."; "Deletion to be done via adjustments."; "Adjustments of all types must be available under the Transactions > Adjustments page."; "Adjustments should use the comment from the user in this format: Session Deleted: comment"; "Rollups run afterwards."; "Role Permission added."
     RN verbatim: "An option to delete a session has been added. Role permissions for this have also been added."; "A 30 second 'Undo' option is available after confirming the delete, but after that all transactions in the session will be adjusted off and the session will be updated to a new status of Deleted."; "Support will not be able to reverse the deletion; we advise being very certain before starting the deletion process." -->
<!-- Source: NXT-53996 (resolved 2024-08-23).
     AC verbatim: "Online Payment sessions cannot be deleted."; "User is informed why."; "Delete Session Confirmation prompt updated to tell the user how many transactions and $$ payments are in the session."
     RN verbatim: "We have temporarily removed permissions to delete sessions. If you need a session removed, please contact our Support team for assistance. The permission will be returned in the future along with an option to restore a deleted session."; "However, we have added in a permanent blocker to prevent sessions at Central Office from being deleted. These sessions typically contain online payments from Family Hub, along with refunds and other account-related actions taken by staff at the Nutrition Office. You will need to contact Support if one of these sessions does need to be removed."
     Open: Exact UI location of the Delete Session control (Description says "More Actions dropdown on the Reconciliation page", not in AC or RN). Restore Session capability (NXT-54040) is anticipated in NXT-53996's RN but not in this pass. -->
### Delete a Session
An option to delete a session has been added, gated by a role permission. Online Payment sessions cannot be deleted, and a permanent blocker prevents sessions at Central Office (which typically contain Family Hub online payments, refunds, and other account-related actions) from being deleted; contact Support if one of these needs to be removed.

1. Select the Delete Session option
   A confirmation prompt requires a comment. The prompt tells the user how many transactions and dollar payments are in the session.
2. Confirm the delete
   A 30-second Undo is available after confirming. After the 30 seconds, all transactions in the session are adjusted off, the session is updated to a new status of Deleted, and rollups run afterwards. Support will not be able to reverse the deletion — be very certain before starting the deletion process.
3. After deletion, the transactions appear as adjustments on the Transactions / Adjustments page
   The adjustment uses the user's comment in this format: "Session Deleted: <comment>".

## Close an OPENED Session
The user may force close an OPENED Session to be able to reconcile.
Force closing an OPENED Session is not a best practice and is not recommended as it may cause data loss and unbalanced Sessions.
1. Select the Site Code/Site Name, Status, and Date
2. Click the SEARCH button
   Session information displays in the table below.
3. Identify the Session with the OPENED status and $0.00 Over/Under to close
   Ensure all service is complete before closing an OPENED Session.
4. Click the Reconcile icon for the desired Session
   The Reconciliation page displays.

5. THIS SESSION IS NOT CLOSED message displays in orange
   Only CLOSED and BALANCED Sessions are eligible for reconciliation.
   Follow the steps below the orange message to close the Session.
   THIS SESSION IS NOT CLOSED:
- Wait for the cashier to close the Session at the POS terminal
Once CLOSED, reconcile the Session.
If the cashier is still serving, force closing an active Session may cause a loss of transactions.
- Correct all incorrect transactions before closing the Session
See the Edit and Add Transactions Guide for more information.
See the Unbalanced Sessions Guide for more information.
- Close the Session by clicking the Edit Pencil icon next to the Closing Date/Time/Balance The Closing Balance pop-up window displays.
Closing Balance Window:
  - Click the SAVE button
THE SESSION IS BALANCED AND READY TO RECONCILE message displays in orange.
The CLOSED status displays in green on the right-hand panel.
If THE SESSION IS NOT BALANCED message displays with the ADJUST
SESSION button; see the Unbalanced Session Guide.
6. Click the RECONCILE button
   A green THE SESSION IS RECONCILED statement appears, and the status changes to RECONCILED.
   Click the BACK button to return to the Sessions page.
