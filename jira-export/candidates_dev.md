# DEV customer-specific CANDIDATES (read & classify each)

Total: 68

====================================================================================================
NXT-63908 | Story | Module=Inventory | Status=Done Done (Done) | Res='Done' | flags=['FD_descAC']
Created=7/10/2025 1:16 PM Resolved=9/29/2025 9:54 PM Labels=''
SUMMARY: INV - Vendors - Items - Ignore unorderable items for VI# uniqueness

DESCRIPTION:
As a food service director I want the VI# uniqueness to only consider *orderable* items so I can assign VI# without having to check unorderable items.

Source of Issue: [https://primeroedge.freshdesk.com/a/tickets/287828|https://primeroedge.freshdesk.com/a/tickets/287828|smart-link] 

{quote}I keep getting a message that my vendor id number is a duplicate, but I can’t find the duplicate number when I search it.{quote}

!image-20250904-041627.png|width=83.33333333333334%,alt="image-20250904-041627.png"!

ACCEPTANCE CRITERIA:
* Update the VI# uniqueness validation to only consider orderable items 
* Apply uniqueness check when items are made orderable again
** if necessary, flag item as requiring new VI# before being made orderable
** Ensure these changes do *not* affect the overall ordering logic
* Prompt user on Update Orderability screen to correct duplicate VI# before making unorderable items Orderable again
** “Duplicate Vendor Item #. Please change VI# before making item orderable again.”

====================================================================================================
NXT-65504 | Story | Module=Family Hub | Status=Done Done (Done) | Res='Done' | flags=['FD_descAC', 'known_customer']
Created=8/12/2025 9:19 AM Resolved=8/22/2025 10:21 AM Labels=''
SUMMARY: FH - WebView Update for Adams 12 App

DESCRIPTION:
[https://primeroedge.freshdesk.com/a/tickets/289943|https://primeroedge.freshdesk.com/a/tickets/289943]

As an Adams 12 parent I want to use our custom app to view the online menus, however they will not load due to WebView not being supported.

----

*requirements*

* Adams 12 parents can use the adams 12 app to view the online menus website.

----

Notes from Venkat:

The issue might be the web app being marked as unsupported due to missing browser details in User-Agent data.
The app is from Apptegy, and the message indicates it's using a User-Agent of 'Mozilla/5.0 (Linux; Android 15; 23053RN02A Build/AP3A.240905.015.A2; wv)'.

Our regular browsers (e.g., Chrome) have a User-Agent like:
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'

The '; wv' part in the Apptegy User-Agent is the clue that it's an Android WebView.

To allow FH to load inside the Apptegy Android app WebView, we can treat any User-Agent containing '; wv' as allowed by default (assuming we trust Apptegy with no browser and version details) instead of blocking it for missing version information.

We can rely on this, make the change, and push the code.

ACCEPTANCE CRITERIA:
WebView supported on the Android version of the FH app

====================================================================================================
NXT-65541 | Story | Module=Accountability | Status=New (In Progress) | Res='' | flags=['FD_descAC']
Created=8/13/2025 10:30 AM Resolved= Labels=''
SUMMARY: FO - Year Begin - Updates

DESCRIPTION:
Few feedback tickets:

* [https://primeroedge.freshdesk.com/a/tickets/289187|https://primeroedge.freshdesk.com/a/tickets/289187] → Inventory Period pointing at the wrong page, POS Periods does not exist.
* [https://primeroedge.freshdesk.com/a/tickets/289213|https://primeroedge.freshdesk.com/a/tickets/289213] → show current year on page load
* [https://primeroedge.freshdesk.com/a/tickets/289232|https://primeroedge.freshdesk.com/a/tickets/289232] → goes back to page 1 after updating a task instead of staying on current page, video attached
* [https://primeroedge.freshdesk.com/a/tickets/289234|https://primeroedge.freshdesk.com/a/tickets/289234] → edit status from the main grid, without having to use the edit pencil
* Add Performance Based Incentives to the list

ACCEPTANCE CRITERIA:
--

====================================================================================================
NXT-65573 | Story | Module=Accountability | Status=Done Done (Done) | Res='Done' | flags=['struct_desc']
Created=8/14/2025 3:05 PM Resolved=11/5/2025 6:27 PM Labels=''
SUMMARY: ACC - Attendance Feature - Edit Check Worksheet Report

DESCRIPTION:
For our districts in NC the state requires that their Daily Attendance be compared to served counts in the Edit Check and Edit Check Worksheet. With the new Weekly Attendance Feature, these districts will be entering Count every day and need it compared within the Edit check report. Whether we modify the existing report or create a new one we will need to support this tie-in for consuming the entered attendance counts on the Edit Check report.

Add new checkbox as a report option.
add new checkbox “include attendance count columns”

*Edit Check*

* AF column needs to be calculated based on daily attendance counts. (Days Attendance/ Days Approved x100 to convert to percentage)
* Rest of the calculations continue as-is.
* Add the Special Provision Claiming %s back into the report (CEP/P2)
* If date range the header attendance factor label must be the average.



*Edit Check Worksheet*

* Pull in the Edit Check Comments for the resolution in addition to any flagged edit check messages
Example from New Brunswick County Schools old software's report:
!https://dev.azure.com/Cybersoft-Technologies-Inc/0d08063f-212a-4277-87f0-199e49d410e9/_apis/wit/attachments/c37c1643-9a62-48a4-a466-cbcdad611a74?fileName=image.png|width=1115,height=566,alt="Image"!

Example Editcheck worksheet from NC website

!https://dev.azure.com/Cybersoft-Technologies-Inc/0d08063f-212a-4277-87f0-199e49d410e9/_apis/wit/attachments/297d1f88-11c0-4006-9c36-af8fed63a177?fileName=image.png|width=1679,height=1148,alt="Image"!


h1. New Mock ups for Edit Check Worksheet

h3. Add 3 new columns for Attendance, Eligible, and Attendance Factor _and Recalculate Monthly Attendance Factor_

---------------------------------------\

!https://dev.azure.com/Cybersoft-Technologies-Inc/0d08063f-212a-4277-87f0-199e49d410e9/_apis/wit/attachments/d8a22c94-58c5-4cda-82d6-f6ede80c78de?fileName=image.png|width=1425,height=593,alt="Image"!

h2.  New rows for sums and average per Meal Type

!https://dev.azure.com/Cybersoft-Technologies-Inc/0d08063f-212a-4277-87f0-199e49d410e9/_apis/wit/attachments/ca6373b0-70af-4921-8849-2394317f0a81?fileName=image.png|width=1405,height=308,alt="Image"!

h2. Eligible x AF recalculation

!https://dev.azure.com/Cybersoft-Technologies-Inc/0d08063f-212a-4277-87f0-199e49d410e9/_apis/wit/attachments/304ad2a3-8599-4d2f-a10a-edcdd7640126?fileName=image.png|width=1392,height=638,alt="Image"!

h2. Footnote for Report when setting is on:

!https://dev.azure.com/Cybersoft-Technologies-Inc/0d08063f

ACCEPTANCE CRITERIA:
-

====================================================================================================
NXT-66209 | Story | Module=Inventory | Status=Done Done (Done) | Res='Done' | flags=['contract']
Created=9/3/2025 11:29 PM Resolved=11/12/2025 3:52 PM Labels=''
SUMMARY: INV - Distribution - Consider setting for Source of Substitutions

DESCRIPTION:
As a Distribution Manager I want the Add/Sub item to consider the contract settings so we can control which items are added and when they can be added.



h3. Add Item tool - View Perpetual

!Picking - Add Item Pending-20250904-051637.png|width=75%,alt="Picking - Add Item Pending-20250904-051637.png"!



h3. Add Item tool - Substitutions only

* ‘Is a Substitution?’ checkbox is removed

!Assign - Sub Only-20250904-051532.png|width=75%,alt="Assign - Sub Only-20250904-051532.png"!

ACCEPTANCE CRITERIA:
* Settings from [https://primeroedgenext.atlassian.net/browse/NXT-65553|https://primeroedgenext.atlassian.net/browse/NXT-65553|smart-link] 
* Consider new setting for ‘Source of Substitutions’
** if the setting value is ‘Site Perpetual’ consider all the items at the distribution site as eligible to be added
*** display the shortcut button as “View Perpetual” and open the site’s Perpetual Inventory page
** if the setting value is ‘Contract Items’ consider only the contract items as eligible (current behavior)
* (UX) Display Quantity Available in the Add/Sub Item slide-out (in all instances, regardless of setting)
** Use correct QOH value (projected vs. actual) depending on Assignment or Picking
* Consider the new setting ‘Allow Non-Substitution Added Items’ 
** if this is set to ‘Yes’ then the current behavior is fine
** if this is set to ‘No’ then the Add Item framework should be updated to only allow substitutions
*** remove the ‘Is a Substitution?’ checkbox and require a substitution selection for all added items
*** remove the Add Item button for Picking status

====================================================================================================
NXT-66210 | Story | Module=Inventory | Status=Done Done (Done) | Res='Done' | flags=['contract']
Created=9/3/2025 11:30 PM Resolved=11/13/2025 5:24 PM Labels=''
SUMMARY: INV - Distribution - Consider setting for Orders After Assignment

DESCRIPTION:
As a Distribution Manager I want settings on the internal contract so I can customize certain distribution details for my district’s operations.



h3. Create Order - consider setting for Delivery Date

!image-20250910-134534.png|width=91.66666666666667%,alt="image-20250910-134534.png"!



h3. Edit Order - Needs to consider this setting

!image-20250910-134431.png|width=91.66666666666667%,alt="image-20250910-134431.png"!

ACCEPTANCE CRITERIA:
* Consider the new setting for ‘Allow Orders After Assignment’ [https://primeroedgenext.atlassian.net/browse/NXT-65553|https://primeroedgenext.atlassian.net/browse/NXT-65553|smart-link] 
* When the setting value is ‘Prompt each time’ it will follow the existing behavior and display a warning icon on the Review tab with the green & red approve/reject buttons
* When the setting is ‘Auto-create new Distribution’ it will automatically create another distribution in Unassigned status, containing the new order and any other future orders
* When the setting is ‘Disallow orders after Assignment’ the order process will prevent sites from ordering once that day has been assigned
** the Delivery Date will become invalid for that vendor; sites will have to pick the next available date

====================================================================================================
NXT-66293 | Story | Module=PE Insights | Status=Done Done (Done) | Res='Done' | flags=['struct_desc']
Created=9/5/2025 9:03 AM Resolved=12/11/2025 9:04 AM Labels=''
SUMMARY: PE-SC Insights -Reimbursable Meals- Revenue KPI

DESCRIPTION:
Per Dallas:

h1. Revenue KPI

The Meals section of the revenue KPI should be updated to include reimbursable revenue source. We want to separate the current 3 data points we have for free, reduced, and paid students into 6 data point. For each price type, we will display the amount captured for meal sales and reimbursable. Adding reimbursable revenue give the full picture to the school district of how much revenue they are collecting as whole. This also will impact other future KPIs when we compare them against total revenue earned (ex – Labor as % of revenue, food cost as % of revenue, etc).

The 6 data points include…

·         *Student Meal Sales (Free)*: This is the amount charged/paid for sales to free students for Is Meal items. Amount can be found on the Activity report, meal sales column, for free students in all meal programs. Typically, this number is going to be $0.00, as free students are not charged for reimbursable (is meal) meals.

·         *Student Reimbursable (Free)*: This is the amount the district is reimbursed for serving free meals to students. Reimbursement rate is applied against the number of meals sold to free students. Amount can be found on the Activity report, reimbursement column, for free students in all meal programs.

·         *Student Meal Sales (Reduced)*: This is the amount charged/paid for sales to free students for Is Meal items. Amount can be found on the Activity report, meal sales column, for free students in all meal programs. Typically, this number is going to be lower, as reduced students are charged only $0.30 for breakfast and $0.40 for lunch reimbursable (is meal) meals.

·         *Student Reimbursable (Reduced)*: This is the amount the district is reimbursed for serving reduced-price meals to students. Reimbursement rate is applied against the number of meals sold to reduced students. Amount can be found on the Activity report, reimbursement column, for reduced students in all meal programs.

·         *Student Meal Sales (Paid)*: This is the amount charged/paid for sales to free students for Is Meal items. Amount can be found on the Activity report, meal sales column, for free students in all meal programs.

·         *Student Reimbursable (Paid)*: This is the amount the district is reimbursed for serving reduced-price meals to students. Reimbursement rate is applied against the number of meals sold to paid students. Amount can be found on the Activity report, reimbursement column, for paid students in a

ACCEPTANCE CRITERIA:
coming

====================================================================================================
NXT-66443 | Story | Module=Family Hub | Status=Release Testing (To Do) | Res='Done' | flags=['known_customer']
Created=9/11/2025 9:42 AM Resolved=5/11/2026 9:40 AM Labels=''
SUMMARY: Family Hub - WoodForest migration

DESCRIPTION:
Family Hub - WoodForest migration

ACCEPTANCE CRITERIA:
--

====================================================================================================
NXT-66821 | Story | Module=Eligibility | Status=Done Done (Done) | Res='Done' | flags=['FD_descAC']
Created=9/23/2025 3:10 PM Resolved=4/15/2026 8:13 AM Labels='FO-Refinement'
SUMMARY: Elig - DC - Extensions - Extending a different DC Type to the same student, blocking inactive Source students

DESCRIPTION:
[https://primeroedge.freshdesk.com/a/tickets/295727|https://primeroedge.freshdesk.com/a/tickets/295727] - trying to extend SNAP after having previously extended Medicaid

[https://primeroedge.freshdesk.com/a/tickets/296439|https://primeroedge.freshdesk.com/a/tickets/296439] - same scenario 

[https://primeroedge.freshdesk.com/a/tickets/314274|https://primeroedge.freshdesk.com/a/tickets/314274] - scenario B below

*requirements*

Scenario A:

* User can perform a DC Extension between two students repeatedly:
** Only if the DC Type has changed.
*** Example: Student A (DC Medicaid), Student B (Paid)
*** Extension from A → B (DC Medicaid)
*** Student A updates to DC SNAP
*** Extension from A → B (DC SNAP)
* User can perform a Manual Match repeatedly along the same lines
* -User is shown warning text if the two students have been previously matched but is not blocked like they are currently.-
** -Warning text: This extension has happened previously and can be seen under Reviewed. You can match them again if required.-



!image-20250923-204326.png|width=465,alt="image-20250923-204326.png"!

----

[https://primeroedge.freshdesk.com/a/tickets/314274|https://primeroedge.freshdesk.com/a/tickets/314274]

Scenario B

* DC Extension is created for a student who is active (Student A → Student B)
* Potential Extension is not reviewed 
* Student A goes Inactive
* Potential Extensions continue to be created because the student was active with DC benefits at one point

*requirements*

* Check DC Extensions for Inactive Source Students (the one with benefits) and delete/block any potential extensions from being created on them.
** User can then use Manual to do an extension on them if required.



*Discussion Notes* {{2026-04-10}} with Hussain and Harsha.

* Scope on this is to be limited to Manual Match only for Scenario A.
* Scope on Scenario B is for only inactive students.

ACCEPTANCE CRITERIA:
* User can perform a DC Extension repeatedly between the same students. (scenario A)
** Manual Match should be possible in this scenario, but the user is advised accordingly.
* Inactive students are not used as a source of DC Extension + data clean-up. (scenario B)

====================================================================================================
NXT-67479 | Story | Module=Financials | Status=Done Done (Done) | Res='' | flags=['known_customer']
Created=10/15/2025 11:29 AM Resolved= Labels=''
SUMMARY: Tullahoma Financials enhancements

DESCRIPTION: (blank)

ACCEPTANCE CRITERIA:
Tullahoma Financials enhancements

PBIs : 

[https://dev.azure.com/Cybersoft-Technologies-Inc/PrimeroEdge%20Classic/_workitems/edit/108845|https://dev.azure.com/Cybersoft-Technologies-Inc/PrimeroEdge%20Classic/_workitems/edit/108845|smart-link] 



[https://dev.azure.com/Cybersoft-Technologies-Inc/PrimeroEdge%20Classic/_workitems/edit/108846|https://dev.azure.com/Cybersoft-Technologies-Inc/PrimeroEdge%20Classic/_workitems/edit/108846|smart-link] 

[https://dev.azure.com/Cybersoft-Technologies-Inc/PrimeroEdge%20Classic/_workitems/edit/108847/?view=edit|https://dev.azure.com/Cybersoft-Technologies-Inc/PrimeroEdge%20Classic/_workitems/edit/108847/?view=edit|smart-link] 

[https://dev.azure.com/Cybersoft-Technologies-Inc/PrimeroEdge%20Classic/_workitems/edit/107335|https://dev.azure.com/Cybersoft-Technologies-Inc/PrimeroEdge%20Classic/_workitems/edit/107335|smart-link]

====================================================================================================
NXT-67538 | Enhancement | Module=Family Hub | Status=Done Done (Done) | Res='Done' | flags=['struct_desc']
Created=10/20/2025 2:56 PM Resolved=11/12/2025 11:38 AM Labels=''
SUMMARY: FamPortal - Low Balance Alerts/Make Payments - Update communication to specify alternate payment methods (Part 1)

DESCRIPTION:
From Bhanu:

For legal and compliance purposes, a specific line should be added to the low balance alert email that SchoolCafé sends to parents. We need to create user stories for both PE SchoolCafe and Family Hub parent portal to implement this change. As this is compliance-related, we should prioritize this update. Additionally, any payment-related communication to parents on the website and mobile applications should include this alternative payment method text.

{quote} *Alternative Payment Methods: Parents can avoid fees by delivering a check or cash directly to the School District.*{quote}



Requirements:

# Update the default Setting value for ‘Make Payments - Payment Guidelines contact info’ from:
## OLD: For alternative payment methods to your child's food service account, please contact your school district's food service office. You can find their contact info in the Support page.
## NEW: Alternative Payment Methods: Parents can avoid fees by delivering a check or cash directly to the School District. For more information, please contact your school district's food service office. You can find their contact info in the Support page.
!image-20251020-202148.png|width=1071,alt="image-20251020-202148.png"!

# Update the Low Balance Reminder body text (‘AlertMaster’ table) to include this line



Placement of the line within the new template (for example):

----

Email From: [+customercare@schoolcafe.com+|mailto:customercare@schoolcafe.com]

Email Subject: Low balance alert for your student account(s)

 

…

  You can set one up for one or more students on your account by selecting ‘Automatic Payments’ on your dashboard.  

  Alternative Payment Methods: Parents can avoid fees by delivering a check or cash directly to the School District.

 

  For questions regarding your student's cafeteria account, to transfer funds between cafeteria accounts, or to obtain a refund of cafeteria account balances,

  please contact   

…

ACCEPTANCE CRITERIA:
* Verify that the new default value for the Payment Guidelines contact info setting has been updated with the new text.
** Update the translations also
* Verify that new default low balance alerts include this new line of text as well. 
** We will need to find a way to update custom templates for those districts using them as well. If it is possible (database only), this may be done post release.

====================================================================================================
NXT-67621 | Story | Module=Platform - Data Exchange | Status=New (In Progress) | Res='' | flags=['known_customer', 'struct_summary']
Created=10/23/2025 11:59 AM Resolved= Labels=''
SUMMARY: District Migration-Anchorage School District-BO Migration

DESCRIPTION: (blank)

ACCEPTANCE CRITERIA:
Test if all the menu items, recipes, ingredients, and single ingredient recipes are migrated correctly to SchoolCafe.

====================================================================================================
NXT-67942 | Enhancement | Module=Family Hub | Status=Done Done (Done) | Res='Done' | flags=['struct_desc']
Created=10/29/2025 2:15 PM Resolved=12/9/2025 11:37 AM Labels=''
SUMMARY: FamPortal - Alternate Payment Methods (Part 2) - Update other templates/areas to specify alternate payment methods

DESCRIPTION:
Continued from part 1, we need to add the following lines to a few more places for legal/compliance purposes:

{quote} *Alternative Payment Methods: Parents can avoid fees by delivering a check or cash directly to the School District.*{quote}



Requirements:

# On the Parent Dashboard, when adding or updating a student's automatic payment setting, update the text displaying at the top of the pop-up:
#* *OLD*: {color:#4c9aff}*A $___ convenience fee will be charged on all online Food Service payments by card.* {color}

#* *NEW*: {color:#4c9aff}*A $___ convenience fee will be charged on all online Food Service payments by card (your district may update this rate from time to time).* {color}

{color:#4c9aff}*Alternative Payment Methods: Parents can avoid fees by delivering a check or cash directly to the School District. For more information, please contact your school district's food service office. You can find their contact info in the Support page.*{color}

Location:
!https://dev.azure.com/Cybersoft-Technologies-Inc/0d08063f-212a-4277-87f0-199e49d410e9/_apis/wit/attachments/b609cb93-0396-4b2f-a224-a214845769a2?fileName=image.png|width=1037,alt="Image"!
# Similar to the previous story where we updated the Low Balance Reminder body text, let's include this line on the following templates in the same location:

## *You set up a new automatic payment*
## *Your automatic payment is expiring*
## *Your automatic payment was processed*




Placement of the line within the new template (for example):

----

…

   Alternative Payment Methods: Parents can avoid fees by delivering a check or cash directly to the School District.

 

  For questions regarding your student's cafeteria account, to transfer funds between cafeteria accounts, or to obtain a refund of cafeteria account balances,

  please contact   

…

ACCEPTANCE CRITERIA:
* Verify that the new text that displays when adding or updating an automatic payment setting
** Update the translations also (if possible)
* Verify that the various automatic payment templates include this new line of text as well.
** We will need to find a way to update custom templates for those districts using them as well. If it is possible (database only), this may be done post release.

====================================================================================================
NXT-67944 | Enhancement | Module=Family Hub | Status=Done Done (Done) | Res='Done' | flags=['FD_descAC']
Created=10/29/2025 2:18 PM Resolved=12/5/2025 8:32 AM Labels=''
SUMMARY: FamPortal - Super Admin - Configure Districts - Add 'Accept'/'Reject' buttons to Documents window

DESCRIPTION:
As a Cybersoft admin, I would like to be able to notify district admins who submit documents through the Family portal website whether their document has been accepted or rejected (similar to agreements), so that I do not have to potentially discuss financial documents through less private forums such as Freshdesk.

*Summary*

# Within the 'Documents' section of the Configure District page, when a user selects a document, display both 'Accept' and 'Reject' buttons just like we do when it is an agreement
# When a user clicks either of those buttons, send an email to whoever uploaded the document



*Details*

# In the Super Admin portal, in _Configuration → Configure Districts_, in the Documents section pop-up's PDF viewer, we currently only display 'Accept' and 'Reject' buttons when the document is an Agreement. Instead, let's add those buttons for any file type.
# When either button is clicked, send an email to whoever uploaded the document. Let's create 2 different templates that are tied to each button: Document Accepted vs. Document Rejected.
# The purpose of this story is to reduce the extra communication between Shelly and the Customer Care team in which she has to tell them to tell the customer whether their documents have been received or not. This will allow us to communicate with the customer directly, as we will only create a ticket for CC if a document has been rejected (which doesn't happen often). 
# Within the Documents pop-up, add a new column: 'Document Status', which shows whether the district has been 'Accepted', 'Rejected', or blank (no action taken yet). For existing documents, we can display the status as 'Accepted' upon release (via seed script?) if necessary.
# 

_Accepted_ Template:

*Subject*: : {{DistrictName}} - SchoolCafé Documentation Submission Accepted

*Body:* 

Hello!

This is just a notification that the documentation you or your staff have recently submitted has been accepted by our administrative team, and your district's profile has been updated accordingly. If this is a bank change request, please allow up to 5 business days for the changes to take effect. Unless you are receiving this notification in error (in which case, you can contact our customer care team for more information), no further action is needed on your part at this time.

Thank you!

- Team SchoolCafé



_Rejected_ Template:

*Subject*: {{DistrictName}} - SchoolCafé Documentation Submission Not Accepted (More Information Required)

*Body:* 

Hello,

T

ACCEPTANCE CRITERIA:
* Verify new Accept/Reject buttons have been added to the view of each document
* Verify that new email templates have been added which correspond to these buttons

====================================================================================================
NXT-67945 | Enhancement | Module=Family Hub | Status=New (In Progress) | Res='' | flags=['FD_descAC', 'struct_desc']
Created=10/29/2025 2:22 PM Resolved= Labels=''
SUMMARY: SchoolCafé - Admin - Settings - Add setting to hide Eligibility Info - Notifications content

DESCRIPTION:
As a district admin, I would like the ability to prevent potentially unauthorized users from being able to view sensitive data related to students, so that damaging actions such as leaks of eligibility letters and other personal information become much less common.

*Summary*

Add a new setting which can potentially limit the amount of information that is available to any user who creates a parent account.

*Details*

* In PrimeroEdge -> System Settings add a new setting (or enhance our existing setting. *Praveen* will add details):

* {color:#403294}*PREFERRED SETTING*{color}
** *Description* - Only Display Eligibility Notifications tied to a User's Application
** *Type* - Toggle
** *Default Setting* - ON
** *Tooltip* - When toggled on, parents will only be able to view eligibility notifications within the Eligibility Info tab that are directly related to the application(s) they submitted. Direct Certification letters, since they are not tied to an application, can not be viewed within a parent account when this setting is toggled on.

** Behavior - When this setting is toggled on, do the following:
*** When a parent user goes to Eligibility Info and selects the Notifications tab, only display letters that are linked to the applications and verification responses submitted by that user. So for example: DC letters, Household Letters, Mailing Labels, etc. that are not tied to an applications, should now be hidden, as well as Approval/Denial notices or other letters that pertain to applications which this parent did not submit.
* {color:#ffc400}*ALTERNATIVE SETTING*{color} (If the above setting isn't feasible right now, add this one instead)
** *Description* - Hide All Eligibility Notifications
** *Type* - Toggle
** *Default Setting* - OFF
** *Tooltip* - When toggled on, parents will not be able to view eligibility notifications within the Eligibility Info tab. However, they will still be able to submit and view their own submitted applications.

** Behavior - When users toggle this setting on, do the following:
** When a parent user goes to Eligibility Info and selects the Notifications table, display a message (either upon clicking the tab as a pop-up, or displaying within the page itself while still hiding the notifications content):
_For security purposes, your school district does not currently allow viewing of electronic eligibility notifications in SchoolCafé. To receive your notifications, please reach out to your district at:_
_{{insert District Con

ACCEPTANCE CRITERIA:
Verify that new student PII safeguards have been added as configurable by a district

====================================================================================================
NXT-67947 | Enhancement | Module=Family Hub | Status=Done Done (Done) | Res='Done' | flags=['FD_descAC']
Created=10/29/2025 3:02 PM Resolved=11/11/2025 1:10 PM Labels=''
SUMMARY: FamPortal - School Menus - Modify Category/Item Display order logic

DESCRIPTION:
*Summary*

Currently in the School Menus page, we are sorting/displaying a menu’s categories based on the display order of the items within the categories. Instead, let’s do the following:

* Upon navigating to the School Menus page, sort/display menus based on the Display Order of the menu in the Menu Lines section of the Menu Configuration page. Regarding menu items:
** Top-level: Sort Menu Item Categories by Display Order in Item Management → Item Configuration → Menu Item Category
** 2nd-level: Sort Menu Items within those categories by the menu’s Item display order (alphabetical)
* If a menu item exists in multiple categories across different menus/lines, and the Family Portal user selects all lines, display the item in each category.



Related tickets: 

# [https://primeroedge.freshdesk.com/a/tickets/302464|https://primeroedge.freshdesk.com/a/tickets/302464] 
# [https://primeroedge.freshdesk.com/a/tickets/303154|https://primeroedge.freshdesk.com/a/tickets/303154]

ACCEPTANCE CRITERIA:
Verify that menus now display based on the sorting rules in the Description above

====================================================================================================
NXT-68100 | Story | Module=Platform - Data Exchange | Status=Story Refinement/Efforting (In Progress) | Res='' | flags=['struct_desc']
Created=11/4/2025 1:22 PM Resolved= Labels=''
SUMMARY: SC - Multi Tenant - Data Exchange Update

DESCRIPTION:
*I am a* central realm district user
*I want to* perform student and DC file imports and DC exports from the Imports & Exports screen
*so that I* can manage district-level data centrally and prepare data for downstream front office processing.

----

h2. *Notes*

* This functionality applies to *central realm districts only*, not school districts.
* This is for *file-based imports only*, not API-based imports.
* The *API tab must be hidden* for central realm users.
* A user is considered a *Central Realm user* when their *Region ID* maps to a record whose *Realm Type = Central*. All other district users have *Realm Type = District*.
* *District Code (UI) = Region ID (database field)* and should be treated as the same identifier throughout processing.
* The *District Code data type must match the Region ID data type*.
* Validation occurs at *two stages*:
** Configuration Save (mapping screen)
** File Processing (backend row-level validation)
* Validation rules must be consistent across both stages (Central vs non-Central logic).
* Validation is performed at the *row level* during file processing:
** Valid rows are processed
** Invalid rows are logged as exceptions
* Existing saved import configurations must continue to work:
** District Code defaults to *unmapped* for existing configurations
** Required validation only applies for Central Realm users going forward
* For front office processing, this story is responsible for dumping data into the *transaction tables*. The front office team will complete downstream consumption/import after this work is delivered.
* This enhancement must *not introduce performance degradation* in import processing.
* *QA Note:* Perform regression testing on existing district import functionality to ensure no existing workflows are broken.

----

h2. *Out of Scope*

* API-based imports and exports
* All import types other than Student and DCM
* All export types other than DCM
* Any changes to front office processing logic

----

h2. *User Flow*

# A user logs into SchoolCafé.
# The user logs into a *central realm district* in SchoolCafé.
# The user navigates to *System Settings → Imports & Exports*.
# The user clicks *Add New Import*.
# The user selects either:
#* Student Import
#* DCM Import
# The user uploads a file and proceeds through:
#* Mapping
#* Configuration
#* Save process
# When the user clicks *Save*, the system validates required fields based on district type.
# If validation passes, the configuration is saved.
# T

ACCEPTANCE CRITERIA:
h3. *1. Central Realm Access & Visibility*

* Imports & Exports menu is accessible in Central Realm.
* System correctly identifies Central Realm using Region ID and Realm Type.
* District-level UI is hidden.
* Only supported options are visible.

----

h3. *2. Import Types (Student & DCM Only)*

* Only Student and DCM import options are available.
* Other import types are not displayed.

----

h3. *3. Export Types (DCM Only)*

* Only DCM export is available.
* Other export types are hidden.
* DCM export template includes District Code .
* Exported files correctly populate District Code .

----

h3. *4. District Code Field Definition*

* District Code exists in import templates.
* District Code maps to Region ID.
* Data type matches Region ID.
* District Code appears on mapping screen.
* District Code appears on review screen.
* District Code is saved in audit/history logs.
* District Code is stored in transaction tables.

----

h3. *5. Mapping & Review Validation*

* District Code can be mapped from uploaded files.
* Validation occurs on Save.
* Validation follows Student ID logic.
* District Code is required for Central Realm users.
* District Code is optional for non-Central users.
* Save is blocked if missing for Central Realm.
* Review screen displays District Code .
* Mapping persists after save.

----

h3. *6. Data Staging for Front Office*

* Valid rows are written to transaction tables.
* Transaction records include District Code when applicable.
* Data is available for front office processing.

----

h3. *7. UI Restrictions for Central Realm*

* UI adjusts based on Central Realm context.
* District-level functionality is hidden.
* API tab is hidden.
* Unsupported imports/exports are hidden.

----

h3. *8. Backward Compatibility / Non-Regression*

* Existing district imports function as before.
* No regressions occur in current workflows.
* Non-Central users are not blocked by missing District Code .
* Existing configurations continue to work.

----

h3. *9.

====================================================================================================
NXT-68212 | Story | Module=System | Status=Done Done (Done) | Res='' | flags=['reqby']
Created=11/11/2025 11:07 AM Resolved= Labels=''
SUMMARY: SC - MT - Users Update

DESCRIPTION:
As an SC Admin, I want to be able to manage district and site access on Users screen for a Central realm so that I can manage user access.

*Notes*

* This story covers managing user access to a child realm via the Users Add and Edit screens

*User Flow*

* District is created and user is added via users screen
* System checks if the district is a central realm
* If yes, System allows Admin to:
** Select children districts
** Optionally select children sites 
* 
* Later:
* The user logs in and browses to Central
* The user clicks the View button on the district they are given rights to
* System redirects the user to that district

*Requirements*

* On the System > Users, do the following:
* Ensure all the districts show up in the districts column
* Put a character limit on the length of the field followed by “…”
* Put a hover over on the column field
** On hover over, show all the districts the user has access to
** If can’t do hover over, add an action button in the actions column
* 
* On the System > Users when user clicks Add New or Edit, do the following:
* 
* On the Districts field:
** Check if the user’s current district is central realm and has children districts
** If no, do nothing
** If Yes, then enable the districts field to be a multi-select list
** Data: All children districts
** Note: Don’t let user remove their central district, else will blow everything up
** First option should be “All” and default selected
* 
* On the Sites field:
** Update the list of sites for all selected districts, not just the one
* 
* Ensure that when adding or removing a District to the user, that:
** Districts list in Central is updated correctly

ACCEPTANCE CRITERIA:
h1. *1. System > Users – Grid Enhancements*

h3. Districts Column

* *Display all districts* that a user has access to in the *Districts* column.
* Apply a *character limit* to the visible text (truncate with “…”) if it exceeds the limit.
** Example: _“North Central District, South…”_
* Add a *hover tooltip* showing the full list of districts the user has access to.
** Tooltip displays all district names in full, comma-separated or line-separated format.
* If hover functionality cannot be implemented:
** Add an *action button* in the *Actions* column that, when clicked, opens a small pop-up or modal listing all accessible districts.

----

h2. *2. Add New / Edit User – Districts Field*

h3. Conditional Logic

* When opening the *Add New* or *Edit* user drawer:
** The system checks if the current district is a *Central realm* and has *child districts*.
** *If not Central or has no children:*
*** Districts field remains unchanged (standard behavior).
** *If Central realm with child districts:*
*** Enable the *Districts* field as a *multi-select dropdown*.

h3. Data Population

* Populate the dropdown list with *all child districts* of the current Central realm.
* *Exclusions:*
** Exclude the Central realm itself from the list.
** Prevent the user from removing their Central district assignment (must always remain selected).
* *Default Option:*
** Add a first option labeled *“All”*, selected by default.
** Selecting “All” automatically selects all child districts.

h3. Behavior

* Admin can select one or multiple districts for the user.
* Deselecting “All” clears all selections but retains the Central district.

----

h2. *3. Sites Field Behavior*

* When districts are selected in the multi-select list:
** The *Sites* field dynamically updates to include sites from *all selected districts*.
** Combine site lists from all selected districts and remove duplicates.
* If a district is deselected:
** Automatically remove sites belonging exclusively to that district.
* The u

====================================================================================================
NXT-68249 | Enhancement | Module=Menu Planning | Status=Done Done (Done) | Res='Done' | flags=['FD_descAC', 'known_customer']
Created=11/12/2025 1:35 PM Resolved=1/7/2026 3:19 PM Labels=''
SUMMARY: Texas City - Pre-K Meal pattern(2 of 5 Components) 

DESCRIPTION:
[^primeroedge.freshdesk.com_helpdesk_tickets_303802_print.pdf]

ACCEPTANCE CRITERIA:
2 of 5 Components issue Fix

COMMENT(FD context): ...11/12/2025 3:01 PM;5d27f7699c0d030c2977fa5f;Ticket ID: 303802 - Freshdesk ticket status changed to : Development 12/2/2025 1:45 PM;6111541f8ad5b600703ea2e6;Will only handle Standard in this enhancement. Will have a...

====================================================================================================
NXT-68250 | Enhancement | Module=Menu Planning | Status=New (In Progress) | Res='' | flags=['known_customer']
Created=11/12/2025 1:46 PM Resolved= Labels=''
SUMMARY: Texas City - Snack Pre-K Meal pattern and CACFP

DESCRIPTION: (blank)

ACCEPTANCE CRITERIA:
Need to Add

====================================================================================================
NXT-68256 | Story | Module=Eligibility | Status=Done Done (Done) | Res='Done' | flags=['FD_descAC']
Created=11/12/2025 3:01 PM Resolved=5/5/2026 10:44 AM Labels='FO-Refinement'
SUMMARY: Elig - Verification - 2026 QoL Updates, Include CEP Setting Update

DESCRIPTION:
Tickets:

* [https://primeroedge.freshdesk.com/a/tickets/298990|https://primeroedge.freshdesk.com/a/tickets/298990] → CEP Apps not getting included

*requirements*

* Sampling Page
** Add columns to show the Student Count Date and the Application Count Date
** Application Count Date = Final Sample Date
** Student Count Date = Collection Date
* Verification Collection Report
** User can save the collection report for retrieval later
*** Save the report to PDF and store it
*** User can view the PDF, and see who generated it + when
** PDF button adjusted into a Save button
** Show a grid of saved copies
*** Columns: Generation Date, User, Actions
*** Actions: View, Download
** Instructional text added to the page: 
*** {noformat}This report shows live data. Backdating eligibility can adjust these numbers over time. To download a copy of the report, please click on Save. This will store a copy in the grid below. {noformat}
* Include CEP Sites / Apps in sample creation + random-select
** If the setting is on, we need to include the CEP Sites rather than exclude them for sample creation and application random-select.
** Update setting description: If enabled, this setting will include students from CEP Sites for Section 3 and 4 of the Collection Worksheet. Normally these counts are excluded from this section of the report. It will also include applications for students at CEP sites for sample creation and selection.

ACCEPTANCE CRITERIA:
* New columns in Sampling page
* Collection Report
** PDF button replaced with a Save button.
** Save Report feature added, stores a backup in blob
** Grid added to show saved reports.
*** Columns: Generation Date, User, Actions 
*** Actions: View, Download
*** View should preview the PDF, Download will download it
* Include CEP Sites setting updated
** Sample generation + app selection includes special provision sites

====================================================================================================
NXT-68632 | Story | Module=Platform - Data Exchange | Status=Done Done (Done) | Res='' | flags=['known_customer', 'struct_summary']
Created=11/24/2025 10:58 AM Resolved= Labels=''
SUMMARY: District Migration-Mankato Area Public Schools ISD 77

DESCRIPTION:
[https://primeroedgenext.atlassian.net/wiki/spaces/SBO/pages/3967975426/BO+Migration+Mankato+Notes+Feedback|https://primeroedgenext.atlassian.net/wiki/spaces/SBO/pages/3967975426/BO+Migration+Mankato+Notes+Feedback|smart-link]

ACCEPTANCE CRITERIA:
Test if all the menu items, recipes, ingredients, and single ingredient recipes are migrated correctly to SchoolCafe.

+*Notes:*+
1. There’s no preferred measures for this district.

====================================================================================================
NXT-68735 | Story | Module=Inventory | Status=New (In Progress) | Res='' | flags=['struct_desc']
Created=12/2/2025 12:02 PM Resolved= Labels=''
SUMMARY: Insights - Dashboard Page - Physical Inventory Discrepancy KPI (Backend)

DESCRIPTION:
As a school district director, I want to view the total discrepancy amount across all schools so that I can investigate potential causes such as spoilage, theft, or misreporting.

!image-20251202-180345.png|width=345,alt="image-20251202-180345.png"!

!image-20251202-180358.png|width=309,alt="image-20251202-180358.png"!

!image-20251202-180407.png|width=297,alt="image-20251202-180407.png"!

!image-20251202-182339.png|width=1032,alt="image-20251202-182339.png"!

ACCEPTANCE CRITERIA:
* Step#1: For the selected time period dropdown option  , find all physical inventories with Reconciled status and counting completed date time with in the start and end dates of the selected time period dropdown option.
* Step#2 : sum the discrepancy amounts of all physical inventories resulted in above step#1 and from all selected sites. 
* Show the percentage of total inventory by calculating the total inventory value from all selected sites ( Refer to  [+NXT-68734+|https://primeroedgenext.atlassian.net/browse/NXT-68734]  for details on how to Calculate the total inventory value )
* SPs/APIs provided should support for displaying the site breakdown for all periods and  for a selected storage category, item category and item type  or for a specific item etc..

====================================================================================================
NXT-68910 | Enhancement | Module=Family Hub | Status=Done Done (Done) | Res='Done' | flags=['FD_descAC']
Created=12/10/2025 1:38 PM Resolved=1/29/2026 11:38 AM Labels=''
SUMMARY: FamPortal- Miscellaneous Small Changes 2026 Q1 (Part 1)

DESCRIPTION:
This will be a catch-all story for all of the minor fixes and small requests made during the quarter.

# In School Menus - Monthly View's printable menu, the grade does not appear in the Print Preview dialog. Can we add it?
!image-20251210-193907.png|width=889,alt="image-20251210-193907.png"!

# Per David, with the new address requirements when adding a card, the ‘Use profile information’ checkbox is causing some issues when not checked because the address can differ. Instead, let’s uncheck the checkbox by default.
!image-20260106-222817.png|width=670,alt="image-20260106-222817.png"!

Related ticket: [https://primeroedge.freshdesk.com/a/tickets/307409|https://primeroedge.freshdesk.com/a/tickets/307409] 

# Add a setting to hide payment details for 3rd party districts:
## Some districts use SchoolCafe for everything payment-related except actually making payments (i.e. low balance alerts, purchase history, etc.). However, they still need to be assigned the 'Payments' license for these features. But, this license shows this line in the District Short URL page:Let's add a new setting to fix this:
### Name: '3rd Party Payment District'
### Type: Boolean ON/OFF toggle
### Default Setting: OFF
### Can be changed by district admins: Yes
### Tooltip: When toggled on, this setting hides the payment-related lines from the district's short URL page.
### Behavior: Same as above. When a user toggles this on, hide the 'Make Payments' and 'Set up Auto Pay' lines from the district's Short URL page.
!image-20251210-194009.png|width=688,alt="image-20251210-194009.png"!

ACCEPTANCE CRITERIA:
Complete the list of small updates in the Description

====================================================================================================
NXT-69292 | Enhancement | Module=Menu Planning | Status=Done Done (Done) | Res='Done' | flags=['FD_commentonly', 'known_customer', 'struct_summary']
Created=1/2/2026 11:24 AM Resolved=1/8/2026 5:17 PM Labels=''
SUMMARY: SC Implementation - Hill City ISD #2 - Nutrient Report Issue

DESCRIPTION:
The Menu Cycle Nutrient Summary calculation methodology should be updated to use actual values instead of day-wise percentage values. This modification will ensure consistency with the Slideout and Nutrient report calculations.

ACCEPTANCE CRITERIA:
The Menu Cycle Nutrient Summary calculation methodology should be updated to use actual values instead of day-wise percentage values. This modification will ensure consistency with the Slideout and Nutrient report calculations.

COMMENT(FD context): ...1/2/2026 11:40 AM;5d27f7699c0d030c2977fa5f;Ticket ID: 308059 - Freshdesk ticket status changed to : Development 1/6/2026 10:55 AM;712020:3d682e5b-145f-45ec-9c91-6ee3bdf8eb9b;[~accountid:6111541f8ad5b600703ea2e6] V...

====================================================================================================
NXT-69341 | Enhancement | Module=Family Hub | Status=Done Done (Done) | Res='Done' | flags=['FD_descAC', 'struct_desc']
Created=1/5/2026 3:11 PM Resolved=2/11/2026 1:39 PM Labels=''
SUMMARY: FamPortal - School Menus - Add settings to control field behavior display 'Contains' allergen texts

DESCRIPTION:
+*Summary*+

In this story, let's add 5 settings to the _Family Portal > District Admin login > Configuration > Manage Settings_ page.

+*Background*+

# *Show All Serving Lines by Default.* Since we have added the new printable menus page and consolidated some other fields especially, a few districts have asked that we begin allowing users to view all serving lines by default when they come to the School Menus page, so that they can see everything being served right away. I don't think this is a good idea for the average user, so let's make it a setting instead.

# *Show All Menu Item Categories by Default.* Same rationale as above. The new printable menu pop-up make it less risky to show all categories by default within the base Monthly Menus page as well as the pop-up. Let's add a setting for this as well.

3a & 3b. *Display Breakfast or Lunch.* One district has the very rare scenario of not offering Breakfast, only Lunch. However, we are currently hard-coding these values to the Meal Types field in the School Menus page, while the other meal types are not hard-coded. Since these 2 meal types are both tied to the same program, let's add two settings instead: 'Display 'Breakfast' and 'Display Lunch'. As a bonus, we can eventually use this within SCTV/SCTV+.

# *Show Custom Allergen Details.* Years ago, we made a change related to item translations that caused us to hide the custom allergens texts in the menu item details pop-up. Austin ISD complained that this information is no longer showing and they want to bring it back, but no other districts have complained about this (to our knowledge). However, these are important details that we should probably be showing.

!https://dev.azure.com/Cybersoft-Technologies-Inc/0d08063f-212a-4277-87f0-199e49d410e9/_apis/wit/attachments/77cdffbc-c4d9-466e-8833-2611a1ca3bf7?fileName=image.png|width=1085,alt="Image"!

----

In this story, let's add the following 5 new settings to the SchoolCafé/FP admin 'Manage Settings' page: 

* Add a new Yes/No (or toggle) setting: *Show custom allergen details for menu items*

# Default Setting: Yes (ON)
# Can be changed by district admins: Yes
# Tooltip: _Displays notes about custom allergens, including whether an item contains or was processed in a facility that also processes said allergens._  
# If the setting is set to 'No', continue hiding the details above as we have been doing.
# If 'Yes', display those details.
# We do not need to translate the proper nouns (allergen names).

ACCEPTANCE CRITERIA:
Verify new settings have been added and function as expected.

====================================================================================================
NXT-69463 | Enhancement | Module=Menu Planning | Status=Done Done (Done) | Res='Done' | flags=['FD_descAC']
Created=1/14/2026 10:10 AM Resolved=3/3/2026 2:07 PM Labels=''
SUMMARY: MP- Pre-K Meal pattern(2 of 5 Components) - Adjust Nutrition Report and Slideout for Fail (API Only)

DESCRIPTION:
[^primeroedge.freshdesk.com_helpdesk_tickets_303802_print.pdf]

ACCEPTANCE CRITERIA:
* Adjust fail cases in the food component report and match the fail on Nutrition Report and Slide out for Menu cycle

====================================================================================================
NXT-69492 | Story | Module=Accountability | Status=Done Done (Done) | Res='Done' | flags=['FD_descAC', 'known_customer']
Created=1/15/2026 2:22 PM Resolved=4/28/2026 2:52 PM Labels=''
SUMMARY: Acc DQ - Adams 12 - SchoolCafe - Oracle financial exports

DESCRIPTION:
FD# [[#309264] SC - Adams 12 - SchoolCafe - Oracle financial exports : Cybersoft PrimeroEdge|https://primeroedge.freshdesk.com/a/tickets/309264]

[Explanation Doc|https://cybersofttechnologies-my.sharepoint.com/:x:/g/personal/marcus_suarez_cybersoft_net/IQA7WTTW9FxzQZ09dbP-bNtlAZ4GnfLEAivzk4XtEIn_cSA?e=GaQ0Ys]

[Additional Info Doc|https://cybersofttechnologies-my.sharepoint.com/:w:/g/personal/dallas_taras_cybersoft_net/IQBVgTBukMV7RJhizn3V3Yg6Afdcly-K8KUwWToTkBcSIig?e=waK2V4]

----

*Online Payment Transactions*

Total of Online Payments for each date + site combination, split between positive (AdjustmentIndicator N) and potential returns/refunds (AdjustmentIndicator Y)

!https://attachment.freshdesk.com/inline/attachment?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MjIxODM2ODE3ODEsImRvbWFpbiI6InByaW1lcm9lZGdlLmZyZXNoZGVzay5jb20iLCJhY2NvdW50X2lkIjo1MDc2MTF9.92FSeCTbQOvDvEBVPNKyth6_Vb8YMLxBXkTQqPexeZE|width=716,alt="image.png"!

Data should be Per Date, Per Site, Per AdjustmentIndicator

Columns

* TransactionDate - date field
* SchoolCode - sitecode
* SchoolName - schoolname
* Amount - money field, sum per date + site + adjustmentindicator
* TransactionID - unique id for this combination of date + site
** let’s try using the first Session Number for that site
** backup: use TransactionDate+Site. ex: 20260102106
* AdjustmentIndicator - N/Y field, N for positive totals, Y for negative

----

*UsageTransaction*

Total of Debit Sales for each date + site combination, with the same AdjustmentIndicator clause.

!https://attachment.freshdesk.com/inline/attachment?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MjIxODM2ODE3NzksImRvbWFpbiI6InByaW1lcm9lZGdlLmZyZXNoZGVzay5jb20iLCJhY2NvdW50X2lkIjo1MDc2MTF9.KL3hG7xx8Skebj7gQ3UeVpExbyJRlblTaamMuq19TpU|width=703,alt="image.png"!

Data should be Per Date, Per Site, Per AdjustmentIndicator

Columns

* TransactionDate - date field
* SchoolCode - sitecode
* SchoolName - schoolname
* Amount - money field, sum per date + site + adjustmentindicator
* TransactionID - unique id for this combination of date + site
** let’s try using the first Session Number for that site
** backup: use TransactionDate+Site. ex: 20260102106
* AdjustmentIndicator - N/Y field, N for positive totals, Y for negative

----

*CashSaleTransaction*

Total of Cash taken in per site, per date, per AdjustmentIndicator. Pulls the Deposit Bag Number if present. Also breaks the cash down by the amount spent (Revenue Amount) vs deposited to account bala

ACCEPTANCE CRITERIA:
* 4 scripts created
* 4 sample files created for customer approval
* 4 datasets created

====================================================================================================
NXT-69710 | Story | Module=Accountability | Status=Done Done (Done) | Res='Done' | flags=['FD_descAC']
Created=1/21/2026 2:54 PM Resolved=3/16/2026 2:25 PM Labels=''
SUMMARY: FO - Attendance  > Monthly Entry Type> Bulk Entry tool > Allow partial entry for Either AF or ADA

DESCRIPTION:
[https://primeroedge.freshdesk.com/a/tickets/309797|https://primeroedge.freshdesk.com/a/tickets/309797|smart-link] 


!image-20260121-205658.png|width=922,alt="image-20260121-205658.png"!


We should allow user to enter in ADA or AF by itself to apply using the bulk entry tool.
Currently it is forcing the user to put in a value for both text boxes in order to save.

ACCEPTANCE CRITERIA:
Bulk entry tool on the Monthly Entry type allows for saving when at least one entry is input (AF or Only ADA entered.)

====================================================================================================
NXT-69781 | Story | Module=Accountability | Status=New (In Progress) | Res='' | flags=['struct_desc']
Created=1/27/2026 3:44 PM Resolved= Labels=''
SUMMARY: Acc (Multi-Tenant) - Reports - Meal Participation

DESCRIPTION:
As Sam the State Coordinator I want to create my own reports on Meal Participation for the districts I manage. To do that, I will need a data set available that I can filter and change the views for, save, and export. This will save me time and let me create my own custom reporting.

----

*Requirements*

* New Report page
* New “dataset” / rollup tables for data at a district/site/date level.
* New grid report
* Role Permissions

!image-20260203-225551.png|width=685,alt="image-20260203-225551.png"!

!image-20260203-230335.png|width=685,alt="image-20260203-230335.png"!



*Report Options*

* Districts (multi-select, All option)
* Site Types (multi-select)
* Sites (multi-select, fueled by District selections, All option)
** Show the district as part of this. May want to tab it in.
** Example:
*** ABC School District
**** 101 Elem
**** 201 Middle
**** 301 High
*** DEF School District
**** 101 Elem
**** 201 Middle
**** 301 High
* Date Selector (standard)
* Program Selector (single select, SNP default)
* Meal Type (multi-select, fueled by Program Selector)
* Report options: 
** Summary (default) / Detailed (radio buttons)
** Meal Count (default) / Percentage (radio buttons)
** Include Adults (checkbox, off by default))
*** Controls visibility on the Adult data showing 
** Include Enrollment Counts (checkbox, off by default)
*** Controls visibility on the Enrollment data showing



*Grid Reports*

* Summary: Single line for each district
* Detailed: Single line for each district, site
* Meal Count: Show the meal counts
* Percentage: Show the percentage that had the meal



Grid Columns

* Date
* District
* Site
* Program
* Meal Type
* Patron Type
* Eligibility Type
* Meal Count
* Participation %



Report Info

* Break down counts by:
** District
** Site
** Meal Type
** Patron Type (Students / Adults) 
** Eligibility
* Show Sub-Totals per District
* Show Totals
* Show Average Participation %s on all versions
* Adult columns toggled by the Include Adults checkbox
* Total Enrollment shown for all selected districts
* Enrollment counts by district (use our standard method to calculate this.)
** Total Enrollment:  Highest total enrollment for all serving days.  Free/Reduced: Average enrollment for all serving days. Paid: Total Enrollment - (Free average + Reduced average)
* Report Legend explains the enrollment calculations and the Average Participation columns 



[^Meal Participation Meal Counts.xlsx]
[^Meal Participation Percentages.xlsx]

ACCEPTANCE CRITERIA:
* User has access to a Reports landing page
* User access to a Meal Participation report page
* Role Permissions related to the state-level page added (TBD)
* User has filters on the page
* User has a new District dropdown that shows them their list of available districts
** Multi select dropdown
** All selection also available
* District selection(s) update the Site dropdown accordingly
** User should only see sites that are part of the selected districts
* User can run the Meal Participation report with multiple versions:
** Summary 
** Percentages
** Include Adult columns
** Include Enrollment count columns
* Reports available

====================================================================================================
NXT-69805 | Story | Module=Platform - Data Exchange | Status=New (In Progress) | Res='' | flags=['struct_summary']
Created=1/29/2026 7:09 AM Resolved= Labels=''
SUMMARY: District Migration-Inventory Module Migration

DESCRIPTION:
Confluence Link: [https://primeroedgenext.atlassian.net/wiki/spaces/NEXT/pages/4077060097/2.0+Migration-Inventory+DB|https://primeroedgenext.atlassian.net/wiki/spaces/NEXT/pages/4077060097/2.0+Migration-Inventory+DB|smart-link]

ACCEPTANCE CRITERIA:
Need to Migrate all the required tables marked in the confluence

====================================================================================================
NXT-69850 | Story | Module=Platform - Data Exchange | Status=Done Done (Done) | Res='' | flags=['known_customer', 'struct_summary']
Created=2/1/2026 7:01 PM Resolved= Labels=''
SUMMARY: District Migration-Mankato Area Public Schools ISD 77

DESCRIPTION: (blank)

ACCEPTANCE CRITERIA:
Migrate required tables for FamilyHub

====================================================================================================
NXT-70030 | Story | Module=Accountability | Status=Story Refinement/Efforting (In Progress) | Res='' | flags=['struct_desc']
Created=2/5/2026 8:35 AM Resolved= Labels=''
SUMMARY: Acc (Multi-Tenant) - Reports - Meal Participation (Additional reports)

DESCRIPTION:
As Sam the State Coordinator I want to run a Meal Participation report across multiple districts to compare against reimbursement claim submissions quickly, and also to get a sense on the overall program participation across my various districts.

----

*Requirements*

* New Report page
* New PowerBI report
* Role Permissions

!image-20260203-225551.png|width=685,alt="image-20260203-225551.png"!

!image-20260203-230335.png|width=685,alt="image-20260203-230335.png"!



*Report Options*

* Districts (multi-select, All option)
* Site Types (multi-select)
* Sites (multi-select, fueled by District selections, All option)
** Show the district as part of this. May want to tab it in.
** Example:
*** ABC School District
**** 101 Elem
**** 201 Middle
**** 301 High
*** DEF School District
**** 101 Elem
**** 201 Middle
**** 301 High
* Date Selector (standard)
* Program Selector (single select, SNP default)
* Meal Type (multi-select, fueled by Program Selector)
* Report options: 
** Summary (default) / Detailed (radio buttons)
** Meal Count (default) / Percentage (radio buttons)
** Include Adults (checkbox, off by default))
*** Controlls visibility on the Adult data showing 
** Include Enrollment Counts (checkbox, off by default)
*** Controls visibility on the Enrollment data showing



Reports

* Summary: Single line for each district
* Detailed: Single line for each district, site
* Meal Count: Show the meal counts
* Percentage: Show the percentage that had the meal



Report Info

* Break down counts by:
** District
** Site
** Meal Type
** Patron Type (Students / Adults) 
** Eligibility
* Show Sub-Totals per District
* Show Totals
* Show Average Participation %s on all versions
* Adult columns toggled by the Include Adults checkbox
* Total Enrollment shown for all selected districts
* Enrollment counts by district (use our standard method to calculate this.)
** Total Enrollment:  Highest total enrollment for all serving days.  Free/Reduced: Average enrollment for all serving days. Paid: Total Enrollment - (Free average + Reduced average)
* Report Legend explains the enrollment calculations and the Average Participation columns 



[^Meal Participation Meal Counts.xlsx]
[^Meal Participation Percentages.xlsx]

ACCEPTANCE CRITERIA:
* User can run the Meal Participation report with multiple versions:
** Summary (Meal Counts)
** Detailed (Meal Counts)
** Detailed (Percentages)

====================================================================================================
NXT-70214 | Story | Module=Accountability | Status=Done Done (Done) | Res='Done' | flags=['FD_descAC']
Created=2/11/2026 2:46 PM Resolved=3/16/2026 2:33 PM Labels=''
SUMMARY: FO - Accountability > Transactions > Exceptions > Do not allow exceptions adjustments during a closed period.

DESCRIPTION:
[https://primeroedge.freshdesk.com/a/tickets/308434|https://primeroedge.freshdesk.com/a/tickets/308434|smart-link] 
When a period is closed it should mean closed. We should not be allowing adjustments after a period is closed because that will cause discrepancies which causes issue for districts.

ACCEPTANCE CRITERIA:
{color:#36b37e}Transaction Adjustments:{color}
Do Not allow serving exception adjustments for a closed period{color:#ff5630} *both*{color}{color:#ff5630} {color}duplicate meals and eligibility variance.
{color:#ff991f}If{color} closed period is detected >: disable action buttons and display tooltip note:
”This Period is closed, If adjustments are needed it will need to be reopened”
Display toast message with the text:
”This Period is closed, If adjustments are needed it will need to be reopened here{color:#4c9aff}[link]{color}” (link to periods page, check for permissions)

{color:#36b37e}Reconciliation:{color}
{color:#ff991f}If{color} closed period is detected >: disable action buttons and display tooltip note:
Inside of Reconciliation Move session and Delete session actions must be disabled
Display tooltip over action buttons:
”This Period is closed, If adjustments are needed it will need to be reopened”

====================================================================================================
NXT-70215 | Story | Module=Accountability | Status=Story Refinement/Efforting (In Progress) | Res='' | flags=['FD_descAC']
Created=2/11/2026 2:50 PM Resolved= Labels=''
SUMMARY: FO - Accountability  > Claims > SNP Reports > Standard Export > Show Actual Claim data (Archive) and add generation date note.

DESCRIPTION:
[https://primeroedge.freshdesk.com/a/tickets/308434|https://primeroedge.freshdesk.com/a/tickets/308434|smart-link] 
In order to prevent data mismatches and confusion we need to lock down the standard export tab to match what the claim actually was. Currently it displays live data which confuses the district if there are any changes. We should also add a note clarifying the functionality of the tab.



!image-20260211-210019.png|width=1000,alt="image-20260211-210019.png"!

Old/Existing:

!image-20260211-205951.png|width=1000,alt="image-20260211-205951.png"!


 New


!image-20260211-210338.png|width=1000,alt="image-20260211-210338.png"!

ACCEPTANCE CRITERIA:
Save standard export info on claim generation.
Show saved data in Standard Export tab
Display note. “You are viewing archived data. Data originally generated on [DATE].”

====================================================================================================
NXT-70309 | Story | Module=Financials | Status=New (In Progress) | Res='' | flags=['known_customer']
Created=2/16/2026 4:19 PM Resolved= Labels=''
SUMMARY: FIN - Configure GL Posting Aggregation Frequency

DESCRIPTION:
As a District Nutrition Accountant I want to configure whether my General Ledger batches are generated Daily, Weekly, or Monthly So that the frequency of my automated ledger entries matches the reconciliation rhythm of my District’s specific ERP (e.g., Oracle vs. Tyler Munis).

ACCEPTANCE CRITERIA:
*Configuration Options*

* The system must provide a "Posting Frequency" setting at the District Configuration level.
* *Option A: Daily (Bank Deposit Level)*
** Logic: Aggregates all transactions by "Transaction Date" and "Bank Deposit Slip Number".
** Use Case: Supports the Adams 12 "Daily transactions ONLY" requirement.
* *Option B: Monthly (Period Level)*
** Logic: Aggregates all transactions within the open Period into a single journal entry.
** Use Case: Standard districts reconciling against a monthly bank statement.
* *Option C: Weekly (Custom/Fiscal Week)*
** Logic: Aggregates transactions by a user-defined 7-day cycle (e.g., Mon-Sun).

*Fiscal Period Protection (The "Accountant's Safety Net")*

* _Crucial Validation:_ If "Weekly" is selected, the system must force a "Hard Break" at month-end.
* Example: If a week runs Mar 29 - Apr 4, the system must split this into *two* separate postings (Mar 29-31 and Apr 1-4) to ensure revenue is recognized in the correct Fiscal Period.

*Immutable History*

* Once a frequency is selected and the first transaction is posted, the setting must be locked for the remainder of the Fiscal Year to prevent reporting gaps or overlaps.

* *Retroactive Aggregation:* Changing the setting will not re-aggregate or re-post past entries; it only applies to future data.
* *Manual Override:* Users cannot "force" a daily posting if the system is set to Monthly; they must change the configuration first.

*DEPENDENCIES:*

* *Financial Periods:* Fiscal Periods must be defined to support the month-end split logic.

* *Bank Integration:* For Daily aggregation, the system depends on receiving the "Bank Deposit Slip Number" from the POS/Payment Processor.

====================================================================================================
NXT-70380 | Enhancement | Module=Eligibility | Status=Done Done (Done) | Res='Done' | flags=['FD_descAC']
Created=2/18/2026 2:54 PM Resolved=4/23/2026 1:11 PM Labels=''
SUMMARY: Elig./FH - Income Surveys - Add New Setting to stop auto-processing Surveys with Unidentified Students

DESCRIPTION:
{panel:bgColor=#deebff}
Carrying forward work completed as part of [https://dev.azure.com/Cybersoft-Technologies-Inc/PrimeroEdge%20Classic/_workitems/edit/99540/|https://dev.azure.com/Cybersoft-Technologies-Inc/PrimeroEdge%20Classic/_workitems/edit/99540/] 
{panel}



Ticket: [https://primeroedge.freshdesk.com/a/tickets/267487|https://primeroedge.freshdesk.com/a/tickets/267487] 

*Summary:*

* Currently, surveys without identified students (students with missing required info like IDs) are still being auto-processed under certain conditions. Though the student does get marked as being pending.

*Details:*

* Add a new setting to correct this.
** Setting Name: *_Auto-Process all Online Income Surveys_* 
** Description: This setting determines when a manually-entered income survey can be automatically processed by the system.
** Options: Yes/No/Only if all students identified
*** Default Setting value: *Only if all students identified*
*** When setting value is ‘_Yes’_, there is no change in functionality (continue the current functionality of processing all income surveys)
*** When set to ‘_No’_, do not auto-process any surveys (surveys will always have the status of ‘Pending’)
*** When set to ‘_Only if all students identified’_, only process income surveys where all students on income survey are matched/identified.
** Manual entry of income surveys is unchanged.

*Mockup:*

N/A

ACCEPTANCE CRITERIA:
Verify new setting has been added and each value functions as described above

Verify manual entry behavior is unchanged

====================================================================================================
NXT-70381 | Enhancement | Module=Family Hub | Status=Done Done (Done) | Res='Done' | flags=['FD_descAC']
Created=2/18/2026 4:00 PM Resolved=3/24/2026 11:59 AM Labels='FO-Refinement'
SUMMARY: FH - Menus - Display Ingredients for all menu item types, inclusive of sub-recipes (FD: 310993)

DESCRIPTION:
FD: [https://primeroedge.freshdesk.com/a/tickets/310993|https://primeroedge.freshdesk.com/a/tickets/310993]

*requirements*

* Ensure that all items that CAN be added to menus, and then pushed to menu publishing, have their ingredients listed.
* Recursively include any sub-items/recipes that may have their own ingredient list.
** Display with the sub-recipe marketing description and then the ingredients.
** Example: Chicken Tacos (Chicken, Flour Tortilla, Lettuce, Tomato, Cheddar Cheese)

ACCEPTANCE CRITERIA:
Verify that all menu item types which can be added to a menu now have their ingredients shown when the menu is published to the Family Portal. Check all listed ingredients to see if they also contain ingredients that need to be displayed, like with sub-recipes.

====================================================================================================
NXT-70424 | Enhancement | Module=Accountability | Status=Done Done (Done) | Res='Done' | flags=['FD_descAC']
Created=2/20/2026 1:04 PM Resolved=3/17/2026 9:59 AM Labels='FO-Refinement'
SUMMARY: Acc - Add Transaction - Use session location instead of patron enrollment site for recording data

DESCRIPTION:
[https://primeroedge.freshdesk.com/a/tickets/305261|https://primeroedge.freshdesk.com/a/tickets/305261]

!image-20260220-190648.png|width=371,alt="image-20260220-190648.png"!

*requirements*

* Use the Serving Site instead of the Enrollment Site when recording transactions via Reconciliation
** Pricing should be based off of Serving Site as well, unless the district has Grade Group pricing enabled.

ACCEPTANCE CRITERIA:
* Use the Serving Site instead of the Enrollment Site when recording transactions via Reconciliation
** Pricing based on Serving Site, unless Grade Group / RDA is active.

====================================================================================================
NXT-70586 | Story | Module=Accountability | Status=Done Done (Done) | Res='Done' | flags=['FD_descAC']
Created=2/26/2026 3:36 PM Resolved=4/1/2026 10:35 AM Labels=''
SUMMARY: Acc > End of Day - Remove Status from Suspicious Transactions task

DESCRIPTION:
Freshdesk: [https://primeroedge.freshdesk.com/a/tickets/312058|https://primeroedge.freshdesk.com/a/tickets/312058]

*requirements*

* Remove the Status field from the Suspicious Transactions task

!image-20260318-132620.png|width=576,alt="image-20260318-132620.png"!

ACCEPTANCE CRITERIA:
* Remove the Status field from the Suspicious Transactions task

====================================================================================================
NXT-70587 | Story | Module=Accountability | Status=Done Done (Done) | Res='Done' | flags=['FD_descAC']
Created=2/26/2026 3:52 PM Resolved=5/1/2026 1:14 PM Labels='FO-Refinement'
SUMMARY: Acc > Reports > Edit Check Worksheet - Add Total Enrollment count

DESCRIPTION:
Freshdesk: [https://primeroedge.freshdesk.com/a/tickets/311719|https://primeroedge.freshdesk.com/a/tickets/311719]

As Dana the Director I need the Edit Check Worksheet to show total (highest) enrollment counts, and adjust those based on attendance factor, to comply with the State.

The Elig column shows the Total Enrollment daily, however we need to add a single calculation for the highest enrollment over the selected date range multiplied by the attendance factor.

*requirements*

* User can see Total Enrollment counts for each site
** This would be the highest count under the Elig column for that site over the date range
* User can see the Total Enrollment count modified by the Attendance Factor for each site

!image-20260317-205543.png|width=732,alt="image-20260317-205543.png"!

* Update text: Attendance Factor (A/F) → Attendance Factor (AF)
* Add the new info into the header for each site, examples:
** Total Enrollment (TE): 1,204
** TE x AF: 1,105 
* Add notes to the legend to explain:
** Total Enrollment: The highest enrollment count for the site over the date range.
** TE x AF: Total Enrollment multipled by the Attendance Factor percentage

ACCEPTANCE CRITERIA:
* User can see Total Enrollment counts for each site
* User can see the Total Enrollment count modified by the Attendance Factor for each site
* Legend updated
* Attendance Factor text updated

====================================================================================================
NXT-70754 | Story | Module=Platform - Data Exchange | Status=Done Done (Done) | Res='' | flags=['known_customer', 'struct_summary']
Created=3/3/2026 7:39 AM Resolved= Labels=''
SUMMARY: District Migration  - Post Migration Mankato Findings

DESCRIPTION: (blank)

ACCEPTANCE CRITERIA:
Fix all the issues faced during Mankato Migration

====================================================================================================
NXT-71223 | Story | Module=Platform - Data Exchange | Status=Done Done (Done) | Res='' | flags=['known_customer', 'struct_summary']
Created=3/17/2026 4:09 PM Resolved= Labels=''
SUMMARY: District Migration - Washburn

DESCRIPTION: (blank)

ACCEPTANCE CRITERIA:
Migrate Data for Washburn

====================================================================================================
NXT-71249 | Story | Module=Financials | Status=New (In Progress) | Res='' | flags=['contract']
Created=3/19/2026 2:52 PM Resolved= Labels=''
SUMMARY: FIN — Opening Balance Import: Data Exchange

DESCRIPTION:
As a district finance user, I want to import opening account balances into Financials at the start of a fiscal year or when going live on the system, so that my balance sheet and trial balance reflect accurate starting positions before any period transactions are recorded.

----

h2. TL;DR

Build a new *Opening Balance Import* type in Import Monitor — standard 4-tab flow. _BL owns validation and writes; DE owns UI and orchestration._

*Flow:*

* *Pre-upload:* _Fiscal Year_ dropdown + *Description* input (10–50 chars) on the left; *Download Template* link + help text on the right (matches production Import Setup layout). Eligibility query fires on FY selection; restatement gate triggers here if BL flags the FY.
* *File Upload:* {{xlsx / xls / csv / txt}}, *single sheet only* (reject multi-sheet at upload). *FILE DATA PREVIEW* button shows raw first rows.
* *Field Mapping:* Map 4 required targets ({{GLAccount}}, {{SiteCode}}, {{Debit}}, {{Credit}}) + 1 optional ({{AccountName}} — if mapped, must match the AccountName recorded for the GLAccount in CoA). Column mapping only — no validation here.
* *Review:* FY, Description, totals, effective date (from BL). User confirms → Save calls BL Commit.

*Restatement gate* fires on Pre-upload when the eligibility query flags the FY as having a *closed period* or a *prior OB import*. Gate requires the user to type the confirmation phrase {{Yes, I would like to overwrite the previous import.}} — Continue disabled until the typed value matches the phrase. The *Description entered on Pre-upload doubles as the restatement reason* — no separate reason field. Description + confirmation timestamp pass to BL on Commit.

*At Commit*, BL runs every business rule (per NXT-71240) in one atomic pass. If anything fails, the entire file is rejected; no ledger write. Failures surface in *Import Monitor → Exceptions tab*. If eligibility state changed between FY selection and Commit, BL blocks Commit via a modal on Review; the user re-satisfies the gate.

*Atomic.* All rows write or none. _No partial imports, ever._

*Saved mapping* auto-persists on success — auto-loads next time. Every import still goes through Commit under the same rules. *FY and Description are not persisted* — entered fresh per import.

*Roles with edit access:* Director, Central Office, SchoolCafe Admin. Customer/Technical Support always full.

----

h2. Requirements

h3. 1) Import Type

1.1 New Import Monitor Import Type *Opening Balance Import*. Help text appears 

ACCEPTANCE CRITERIA:
*AC1 — Import Type Available.* When a Finance user views Import Types in Import Monitor, Opening Balance Import appears regardless of prerequisite state.

*AC2 — Pre-upload Tab: Fiscal Year Selector + Eligibility Query.* When the user selects Opening Balance Import, the Pre-upload tab shows a Fiscal Year dropdown listing all FYs. On FY selection, DE calls BL's eligibility query and routes the user to Eligible / Not Eligible / Restatement Required behavior per §3.3–§3.5.

*AC3 — Eligibility Query — Not Eligible.* When the eligibility query returns Not Eligible, Next is blocked at FY selection. The wizard cannot progress past Pre-upload. Two triggers:

* *Chart of Accounts has no Asset, Liability, or Equity account:* the message includes a deep link to Chart of Accounts.
* *Prior FY has open periods:* the message includes a deep link to Period Management (_Financials > Configuration > Periods_).

*AC4 — Restatement Gate Triggered on Pre-upload.* When the eligibility query returns Restatement Required (closed periods in target FY, prior OB import, or both), a confirmation gate appears on Pre-upload. The user must type the phrase {{Yes, I would like to overwrite the previous import.}} into the confirmation field. Continue is disabled until the typed value matches the phrase.

*Trigger messages shown on the gate:*

* *Closed periods:* {{The selected fiscal year has one or more closed periods. To post opening balances, reopen the affected periods first.}}
* *Prior OB import:* {{An Opening Balance Import already exists for this fiscal year. Continuing will reverse the existing entries and replace them with this import.}}
* *Both triggers:* Both messages above are shown, and the closed-period links below also appear.

*Links shown when closed periods is a trigger:*

* {{Reopen periods in Period Management}} → _Financials > Configuration > Periods_
* {{Post a manual adjustment instead (no period reopening required)}} → _Financials > General Ledger > Add New Entry > Manual En

====================================================================================================
NXT-71412 | Story | Module=System | Status=Story Refinement/Efforting (In Progress) | Res='' | flags=['struct_desc']
Created=3/24/2026 10:39 AM Resolved= Labels=''
SUMMARY: SC - MT - District - Linked Realms Tab Updates

DESCRIPTION:
As a *Customer Support user*, I want to manage realm relationships on the *System > Districts > Linked Realms* tab without being restricted by a hard-coded parent-child hierarchy, so that a district or other realm can be linked to multiple related realms (e.g., state, third-party management company, county, etc.) while maintaining data integrity.

----

h1. Background / Notes

The existing Linked Realms tab was originally built around a *strict one-to-one parent-child hierarchy*, where each realm could only have a single parent.

This approach no longer meets business needs.

We are transitioning to a *many-to-one relationship model*, where:

* A district (or any realm) can be linked to *multiple other realms*
* Example:
** Katy ISD → Texas State
** Katy ISD → Third-Party Management Company
** Katy ISD → County

Additionally:

* Realm relationships are no longer strictly hierarchical
* Relationships should be treated as *flexible associations*
* However, we must still *prevent circular relationships* (e.g., A → B → C → A)

----

h1. Current Navigation

*System > Districts > Liked Realms tab*

----

h1. Current Problems

* Hard-coded *one-to-one parent-child relationship*
* Limited realm type selection
* “Select Type” and “Select State” labels are misleading
* Realm selection depends on type selection
* No search/type-ahead for large datasets
* Realms excluded incorrectly if already assigned elsewhere
* No protection against circular references

----

h1. Desired Outcome

* Support *many-to-one realm relationships*
* Allow linking of *any realm to any other realm*
* Remove dependency on strict hierarchy
* Improve usability of selection controls
* Ensure *data integrity via circular reference prevention*

----

h1. Technical / Implementation Notes

* Remove one-to-one parent-child constraints in backend
* Update relationship model to support many-to-one
* Implement *graph traversal check* for circular references
** Depth-first search or similar
* Update Available Realms query:
** exclude only assigned realms
* Implement type-ahead search control (combo box/autocomplete)
* Add UI state for disabled realms
* Add backend validation for circular relationships

----

h1. Out of Scope

* Boundary management
* Role/permission mapping
* Delegated user assignment
* Authentication/token updates

----

h1. Functional Requirements

h2. 1. Rename field labels

* “Select Type” → *Realm Type*
* “Select State” → *Select Realm*

----

h2. 2. Include all realm types

The *Rea

ACCEPTANCE CRITERIA:
h2. AC1: Label updates

Given the user is on the Linked Realms tab,
then labels display:

* Realm Type
* Select Realm

----

h2. AC2: All realm types available

Given the user opens Realm Type,
then all supported types are listed

----

h2. AC3: Realm Type optional

Given no type is selected,
then user can still search/select any realm

----

h2. AC4: Type filters realm list

Given a Realm Type is selected,
then Select Realm shows only matching types

----

h2. AC5: Search functionality

Given user types in Select Realm,
then results filter dynamically

----

h2. AC6: Any realm can be selected

Given a realm is not already assigned,
then it can be selected regardless of type

----

h2. AC7: Realms with existing relationships still available

Given a realm is linked elsewhere,
then it still appears in Available Realms if not assigned to current realm

----

h2. AC8: Prevent duplicates

Given a realm is already assigned,
then it cannot be assigned again to the same current realm

----

h2. AC9: Available realms filtering

Given Available Realms is displayed,
then it excludes only:

* already assigned realms
* optionally self

----

h2. AC10: Many-to-one relationships supported

Given a realm already has one relationship,
then additional relationships can be added successfully

----

h2. AC11: Circular references disabled in UI

Given selecting a realm would create a circular relationship,
then:

* it appears in list
* it is disabled
* it cannot be selected

----

h2. AC12: Circular reference messaging

Given disabled realm is shown,
then user sees indicator and explanation

----

h2. AC13: Circular reference blocked on save

Given a circular relationship is attempted via UI or API,
then:

* save is rejected
* error message is returned

====================================================================================================
NXT-71417 | Story | Module=Production | Status=Done Done (Done) | Res='Done' | flags=['FD_commentonly']
Created=3/24/2026 12:53 PM Resolved=4/15/2026 8:08 AM Labels=''
SUMMARY: PR - Status - Production Withdrawal 

DESCRIPTION:
As a production manager, once I withdraw my inventory, I would like the menu lines that the withdrawal has affected to change status to withdrawal complete

ACCEPTANCE CRITERIA:
* Trigger a status change for any production record that has been withdrawn from inventory
** Status changes to Withdrawal complete
* Any changes that happen on the record will not change the status or alter the withdrawn items after the status has been changed

COMMENT(FD context): .../24/2026 1:59 PM;5fa1ae72c9b15a0078e4c4a8;[~accountid:5ecd59d1eb77320c1f72591d] , We are committed to working on this FD request [https://primeroedge.freshdesk.com/a/tickets/315146|https://primeroedge.freshdesk.com/a/tickets/315146|smart-link]   Please do the Assignment. 4/3/2026 2:54 PM;712020:3d68...

====================================================================================================
NXT-71628 | Story | Module=Accountability | Status=Done Done (Done) | Res='Done' | flags=['known_customer']
Created=3/31/2026 3:47 PM Resolved=5/4/2026 2:12 PM Labels=''
SUMMARY: Deposit Feature - Add New Section for Cards

DESCRIPTION:
When it comes to the deposit, small districts typically do not care when it comes specifically to credit cards as their processes largely exist outside SchoolCafe, with bigger districts or districts that want to account for it all in SchoolCafe, we will need to modify the deposit page to include a new Credit card section.
Update the deposit feature to include a new section specifically for card transactions, ensuring that card deposits are clearly separated and accurately recordable for the new Square integration.

When there is no calculated card but a deposited card sum: it is expected that the variance would receive a surplus. 

EX: Variance after Cash/Check amounts = 11 --> 

Calculated credit card = 0 and Deposited Credit Card = $50 --> 

Deposit Variance = ($39)



!image-20260331-210551.png|width=1000,alt="image-20260331-210551.png"!

!image-20260331-210413.png|width=1000,alt="image-20260331-210413.png"!

The Checks section has a different style than the Denominations and looks unprofessional lets fix that:


!image-20260331-204749.png|width=1000,alt="image-20260331-204749.png"!

Button  Tool Tip


!image-20260331-210137.png|width=1000,alt="image-20260331-210137.png"!

*Discussion 4/15/26 - Matt, Josh*

* Bank Deposit Slip # field needs to be updated to alphanumeric while we’re in there.
** This is for Adams 12 and their Oracle integration.

ACCEPTANCE CRITERIA:
Make the Bank Deposit Slip # field alphanumeric instead of numeric.



Add a new Credit Card Section in Summary for Deposits
- New section is automatically visible if calculated cards is > 0
- hide by default if calculated card = 0
- add button to add credit cards “Add Credit Card Deposit” where when clicked: shows new Credit Card Section as a summary section line and requires comment. Once clicked replaces itself with “Remove Credit Cards” button. TOOLTIP: “Adds ability to track 3rd party credit card revenue to this deposit”
-When Remove button is clicked hide section and delete Card input.


-Ui tweaks (as shown in mockups above)
- New Section that Provides space to enter in a credit card sum.
Calculate out expected credit card amount inline with new section as “Credit Cards (Expected: $[sum])” if Calculated Card < 0 or “Add Card Transaction” Button is clicked (which would be “(Expected: $0)”

Adjust deposit Variance by subtracting the difference between the calculated Cards and Deposited Card Amount. Variance sum = Variance sum - (Calculated Card - Deposited Card)

For legacy Deposit add note. New functionality is not available.

====================================================================================================
NXT-71667 | Story | Module=Global Catalog | Status=New (In Progress) | Res='' | flags=['contract']
Created=4/3/2026 10:38 AM Resolved= Labels='GC_NR'
SUMMARY: [Reuse ]GC - PE - Menu planning  -Global Catalog - Pending Updates - Get mapped items from Cybersoft catalog for items in the selected data source (backend)

DESCRIPTION:
Scope: 

# Add a new dropdown option in data provider dropdown  “Cybersoft Catalog”
# Remove the 1 world sync option from data provider 
# keep the 3rd party sources option in the dropdown and All GDSN related buttons on the page. 
## Check for updates button will be moved next to Data provider dropdown 
## Cybersoft Catalog will be the default option in Data provider drop down
## When 3rd Party Source(s) is selected we will show all other buttons , choose file, upload button etc.. download exceptions, etc.. 
## No need to fix the bug thats showing on this page when 3rd party sources is selected, and at the same time Dont discard the code related to GDSN connect , contract is not ended yet, it will be active till this summer or so. Just FYI
### !image-20260409-205049.png|width=578,alt="image-20260409-205049.png"!
# 
# when selected Cybersoft catalog in data provider dropdown and  clicked on check for updates button:
## Get the list of Cybersoft catalog items mapped to items from selected data source items  Story [https://primeroedgenext.atlassian.net/browse/NXT-71830|https://primeroedgenext.atlassian.net/browse/NXT-71830|smart-link] covers the details on mapping the district item to a Cybersoft catalog item. 
# on menu planning > ingredient details page:  we have a link for {color:#0747a6}+Linked to Global Catalog Item+ {color}{color:#0747a6} {color}but , currently, its not working , when i asked Backoffice team guys to check, Michael told me its not calling an API but not returning any data and told me that GC team has to take look into it. – please make sure its showing the link for mapped items and working however it was working before. - we can meet and discuss if any questions on this. 

!image-20260408-160434.png|width=1034,alt="image-20260408-160434.png"!

!image-20260407-204229.png|width=651,alt="image-20260407-204229.png"!

ACCEPTANCE CRITERIA:
# Add a new dropdown option in data provider dropdown “Cybersoft Catalog”
# Remove the 1 world sync option from data provider
# keep the 3rd party sources option in the dropdown and All GDSN related buttons on the page.
## Check for updates button will be moved next to Data provider dropdown
## Cybersoft Catalog will be the default option in Data provider drop down
## When 3rd Party Source(s) is selected we will show all other buttons , choose file, upload button etc.. download exceptions, etc..
## No need to fix the bug thats showing on this page when 3rd party sources is selected, and at the same time Dont discard the code related to GDSN connect , contract is not ended yet, it will be active till this summer or so. Just FYI
### !image-20260409-205049 (6e7142d9-fc83-40f8-9a31-1e3d8644f43b).png|width=578,alt="image-20260409-205049.png"!
#  
# when selected Cybersoft catalog in data provider dropdown and  clicked on check for updates button:
## Get the list of Cybersoft catalog items mapped to items from selected data source items  Story [https://primeroedgenext.atlassian.net/browse/NXT-71830|https://primeroedgenext.atlassian.net/browse/NXT-71830|smart-link] covers the details on mapping the district item to a Cybersoft catalog item.
# on menu planning > ingredient details page:  we have a link for {color:#0747a6}+Linked to Global Catalog Item+ {color}{color:#0747a6} {color}but , currently, its not working , when i asked Backoffice team guys to check, Michael told me its not calling an API but not returning any data and told me that GC team has to take look into it. – please make sure its showing the link for mapped items and working however it was working before. .

====================================================================================================
NXT-71744 | Story | Module=Platform - Data Exchange | Status=Done Done (Done) | Res='Done' | flags=['FD_descAC']
Created=4/7/2026 8:47 AM Resolved=5/6/2026 10:00 AM Labels=''
SUMMARY: Adult Import Header-less File

DESCRIPTION:
Production request to add headerless file support for Adult imports the way we do for Students, particulary as it relates to PowerSchool.

Freshdesk ticket: [https://primeroedge.freshdesk.com/a/tickets/316155|https://primeroedge.freshdesk.com/a/tickets/316155]

ACCEPTANCE CRITERIA:
Users are able to import headerless files for Adult and Student Import from the UI and also from SFTP.
Users are able to import files with headers for Adult and Student Import from the UI and also from SFTP.
Users are able to import files for all other imports from the UI as well as from SFTP.

====================================================================================================
NXT-71762 | Story | Module=Global Catalog | Status=Story Refinement/Efforting (In Progress) | Res='' | flags=['contract']
Created=4/7/2026 12:15 PM Resolved= Labels='GC_PE'
SUMMARY: GC - PE - Global Catalog - Pending Updates - Compare district items and Cybersoft catalog items data to identify the differences and populate items in the results grid.

DESCRIPTION:
Scope of this story : backend logic to compare the source and Cybersoft catalog items to identify the changes, UI  is already available and  seems to be working 

* UI changes
* Results grid to show the items with at least one available update 
* Grid filters for showing All, Linked Ingredients & Stock Items, Stock Items without linked Ingredients, Ingredients without linked Stock Items
* Status column dropdown filters for all, reviewed, partially reviewed and completed, 
* grid pagination, sorting, column filters  and hyperlinks  to navigate to ingredient page and stock item page for columns should work  as shown in the below screenshot,

# Add a new dropdown option in data provider dropdown  “Cybersoft Catalog”
# Remove the 1 world sync option from data provider 
# keep the 3rd party sources option in the dropdown and All GDSN related buttons on the page. 
## Check for updates button will be moved next to Data provider dropdown 
## Cybersoft Catalog will be the default option in Data provider drop down
## When 3rd Party Source(s) is selected we will show all other buttons , choose file, upload button etc.. download exceptions, etc.. 
## No need to fix the bug thats showing on this page when 3rd party sources is selected, and at the same time Dont discard the code related to GDSN connect , contract is not ended yet, it will be active till this summer or so. Just FYI

 4. when selected Cybersoft catalog in data provider dropdown and  clicked on check for updates button: Get the list of Cybersoft catalog items mapped to items from selected data source items  Story [https://primeroedgenext.atlassian.net/browse/NXT-71830|https://primeroedgenext.atlassian.net/browse/NXT-71830|smart-link] covers the details on mapping the district item to a Cybersoft catalog item.

!image-20260413-204755.png|width=788,alt="image-20260413-204755.png"!

Use the existing results grid with same columns shown below for listing Items.  

# List the items in the grid with at least  one available update for ingredient details or stock item details between selected data source items and Cybersoft catalog items.
# Items with differences only displayed in the results grid.
## for example : if 200 items matched between Cybersoft catalog and district data, and 150 items having updates, then we will list only 150 items in the grid. remaining 50 items matching for all fields will not be listed in the grid. 
## use the existing UI for showing the updates , below is the screenshot of results gr

ACCEPTANCE CRITERIA:
Scope of this story : backend logic to compare the source and Cybersoft catalog items to identify the changes, UI  is already available seems to be working 

* UI changes
* Results grid to show the items with at least one available update 
* Grid filters for showing All, Linked Ingredients & Stock Items, Stock Items without linked Ingredients, Ingredients without linked Stock Items
* Status column dropdown filters for all, reviewed, partially reviewed and completed, 
* grid pagination, sorting, column filters  and hyperlinks  to navigate to ingredient page and stock item page for columns should work  as shown in the below screenshot, 

# Add a new dropdown option in data provider dropdown  “Cybersoft Catalog”
# Remove the 1 world sync option from data provider 
# keep the 3rd party sources option in the dropdown and All GDSN related buttons on the page. 
## Check for updates button will be moved next to Data provider dropdown 
## Cybersoft Catalog will be the default option in Data provider drop down
## When 3rd Party Source(s) is selected we will show all other buttons , choose file, upload button etc.. download exceptions, etc.. 
## No need to fix the bug thats showing on this page when 3rd party sources is selected, and at the same time Dont discard the code related to GDSN connect , contract is not ended yet, it will be active till this summer or so. Just FYI

# when selected Cybersoft catalog in data provider dropdown and  clicked on check for updates button: Get the list of Cybersoft catalog items mapped to items from selected data source items .

----

Use the existing results grid with same columns shown below for listing Items.  

# List the items in the grid with at least  one available update for ingredient details or stock item details between selected data source items and Cybersoft catalog items.
# Items with differences only displayed in the results grid.
## for example : if 200 items matched between Cybersoft catalog and district data, and 150 items 

====================================================================================================
NXT-71821 | Enhancement | Module=Family Hub | Status=Ready For Testing (To Do) | Res='' | flags=['FD_descAC']
Created=4/9/2026 12:47 PM Resolved= Labels=''
SUMMARY: Fam.Portal - Menus - Handle visibility of Menus for Staff at Intermediate sites

DESCRIPTION:
{panel:bgColor=#deebff}
This story was copied over from Classic. Implementation is already complete there via this story: [https://dev.azure.com/Cybersoft-Technologies-Inc/PrimeroEdge%20Classic/_workitems/edit/112738|https://dev.azure.com/Cybersoft-Technologies-Inc/PrimeroEdge%20Classic/_workitems/edit/112738|smart-link]  
{panel}

* In the SchoolCafé family portal, the staff user was unable to view menus when the district configured menus by grade. This occurred because the user was linked to an Adult account associated with an Intermediate school type, which caused issues with the default grade assigned for each site type. 

* In SchoolCafé, school types are dynamic, and their naming and grade mappings are inconsistent or unclear.

* To address this issue, let’s implement the following change.
** Even if a district has opted to use menu data *by grade*, we can modify code to use the API for staff to fetch menu data *without grade* (like when the setting is OFF).
** The difference between *by grade* and *without grade* applies only to the nutrition information. With the current implementation, we default staff to a specific grade, which means they are not receiving accurate nutrition information based on the serving size configured for staff.

 

Examples of tickets in Classic:

[https://primeroedge.freshdesk.com/a/tickets/264863|https://primeroedge.freshdesk.com/a/tickets/264863] 

[https://primeroedge.freshdesk.com/a/tickets/279685|https://primeroedge.freshdesk.com/a/tickets/279685]

ACCEPTANCE CRITERIA:
Verify that Staff users in the Family Portal, who belong to sites with the Intermediate Site Type (or any non-traditional site other than Elem, Middle, High School) is able to log in to their account and view their menus in the Family Portal

====================================================================================================
NXT-71875 | Story | Module=Platform - Data Exchange | Status=Done Done (Done) | Res='' | flags=['known_customer', 'struct_summary']
Created=4/13/2026 8:06 AM Resolved= Labels=''
SUMMARY: FamilyHub - District Migration - Washburn

DESCRIPTION: (blank)

ACCEPTANCE CRITERIA:
Migrate Data for Washburn

====================================================================================================
NXT-71891 | Story | Module=Global Catalog | Status=Testing (In Progress) | Res='' | flags=['struct_desc']
Created=4/13/2026 4:00 PM Resolved= Labels='GC_MDM'
SUMMARY: GC- MDM - AI search page and Review Items Queue - AI Search +Search by batch name for reviewing and approving items. 

DESCRIPTION:
GC- MDM - AI search page and Review Items Queue - AI Search +Search by batch name for reviewing and approving items. 

# AI search page : 
##  AI search based on uploaded file using GTIN and Preferred ingredient name,.
### insert the new AI search results in to [GC_Items_ExtractedUsingAI] - if the GTIN already exists in [GC_Items_ExtractedUsingAI]  table rows, then don't insert them. but assign the batch to that existing item. 
## Capture the batch name from user input and give the name to the search results so, user can easily fetch all these items ,review the data and approve them into Cybersoft catalog.
### make sure the batch name is unique in a district  
### maybe a new table with these columns? BatchID, RegionID, BatchName, AIItemid, IsReviewed, IsApproved, GC_Itemid
### IsReviewed-  isreviewed yes when an item is approved or rejected  or no when user has not clicke don any button for that item. 
### IsApproved  - Yes when user approved it and added to the catalog. 
### GC_Itemid - column will have an itemid if an item is approved and added to our catalog,. 
### Batch name  “ABC” can be assigned in Talladega district and Boone county schools. - its unique per district not across all districts. 
# Review Queue page : When search online option is selected, batch dropdown will show up
##   Lists all batches with at least one item in not approved status.
## if all items were approved in a batch, then don't list that batch in the batch dropdown. 
## when search online option and batch is selcted, then in the results grid .. list only items that are not reviewed yet. dont include the items that are already approved. 
## We should be able to get all items  of a batch of a district from DB no matter whether they are approved or not.,
## when a batch name and other search boxes like GTIN or item name are provided then perform the AND condition for all search fields with user input.   

!image-20260518-194558.png|width=1454,alt="image-20260518-194558.png"!

ACCEPTANCE CRITERIA:
GC- MDM - AI search page and Review Items Queue - AI Search +Search by batch name for reviewing and approving items. 

# AI search page : 
##  AI search based on uploaded file using GTIN and Preferred ingredient name,.
### insert the new AI search results in to [GC_Items_ExtractedUsingAI] - if the GTIN already exists in [GC_Items_ExtractedUsingAI]  table rows, then don't insert them. but assign the batch to that existing item. 
## Capture the batch name from user input and give the name to the search results so, user can easily fetch all these items ,review the data and approve them into Cybersoft catalog.
### make sure the batch name is unique in a district  
### maybe a new table with these columns? BatchID, RegionID, BatchName, AIItemid, IsReviewed, IsApproved, GC_Itemid
### IsReviewed-  isreviewed yes when an item is approved or rejected  or no when user has not clicke don any button for that item. 
### IsApproved  - Yes when user approved it and added to the catalog. 
### GC_Itemid - column will have an itemid if an item is approved and added to our catalog,. 
### Batch name  “ABC” can be assigned in Talladega district and Boone county schools. - its unique per district not across all districts. 
# Review Queue page : When search online option is selected, batch dropdown will show up
##   Lists all batches with at least one item in not approved status.
## if all items were approved in a batch, then don't list that batch in the batch dropdown. 
## when search online option and batch is selcted, then in the results grid .. list only items that are not reviewed yet. dont include the items that are already approved. 
## We should be able to get all items  of a batch of a district from DB no matter whether they are approved or not.,
## when a batch name and other search boxes like GTIN or item name are provided then perform the AND condition for all search fields with user input.

====================================================================================================
NXT-71897 | Story | Module=Platform - Data Exchange | Status=In Progress (In Progress) | Res='' | flags=['known_customer', 'struct_summary']
Created=4/13/2026 4:20 PM Resolved= Labels=''
SUMMARY: Dilworth - District Migration

DESCRIPTION: (blank)

ACCEPTANCE CRITERIA:
Migrate the data from PE to SC

====================================================================================================
NXT-72038 | Story | Module=SCTV | Status=New (In Progress) | Res='' | flags=['FD_descAC']
Created=4/15/2026 12:06 PM Resolved= Labels=''
SUMMARY: SCTV - Support Spanish Language Display on SchoolCafe TV Boards

DESCRIPTION:
*As a* District Nutrition Director at a school with a Spanish immersion program, *I want* SchoolCafe TV display boards to support Spanish language rendering of menu item names and categories, *so that* our Spanish-speaking students and families can read the daily menu in their primary language on the cafeteria display screens.

*Context:*
Freshdesk Ticket #317174 — Stillwater Area Schools #834 reported that while menus can already be viewed in Spanish on the SchoolCafe parent portal, there is currently no way to configure SchoolCafe TV displays to show menus in Spanish. The customer is opening a new school with a Spanish immersion line and needs this capability.

ACCEPTANCE CRITERIA:
# A district or site administrator can configure a SchoolCafe TV device or line to display menu content in Spanish.
# When Spanish is selected, item short names, category headers, and any other customer-facing text on the TV display render in Spanish (leveraging existing Spanish translations from the menu publishing system).
# The language setting should be configurable per device or per line (to be confirmed during refinement).
# English remains the default language if no override is configured.
# The setting does not affect the underlying menu data — only the display rendering on the TV board.

COMMENT(FD context): ...4/15/2026 12:11 PM;712020:a40dec2d-ec27-4f19-9eff-5109c3fe1dea;[~accountid:5d8d15b516bcf20dd1c68046]  New story from Freshdesk #317174 (Stillwater Area Schools). Customer is opening a Spanish immersion school and needs SCTV boards to display menus in Spanish. SchoolC...

====================================================================================================
NXT-72040 | Story | Module=Platform - Data Exchange | Status=In Progress (In Progress) | Res='' | flags=['known_customer', 'struct_summary']
Created=4/15/2026 5:02 PM Resolved= Labels=''
SUMMARY: Dilworth - FamilyHub District Migration

DESCRIPTION: (blank)

ACCEPTANCE CRITERIA:
DataMigration

====================================================================================================
NXT-72140 | Story | Module=Eligibility | Status=New (In Progress) | Res='' | flags=['FD_descAC']
Created=4/20/2026 2:51 PM Resolved= Labels=''
SUMMARY: Eligibility - Settings - Income Guidelines - Eligibility Guidelines - Update new Eligibility Guidelines for 2026-27 (OBSOLETE?)

DESCRIPTION:
*Summary*

* Run a script to insert new Eligibility guidelines for all districts that allows them to get the guidelines. 
* Ref Ticket: [+https://primeroedge.freshdesk.com/helpdesk/tickets/316868+|https://primeroedge.freshdesk.com/helpdesk/tickets/316868]



*Details*

# Run a script to insert the new guidelines for 2026-27 according to the federal reference here: [+https://www.govinfo.gov/content/pkg/FR-2026-04-09/pdf/2026-06842.pdf+|https://www.govinfo.gov/content/pkg/FR-2026-04-09/pdf/2026-06842.pdf]
# Location:

!image-20260420-195408.png|width=1059,alt="image-20260420-195408.png"!



*Mockup*

!https://dev.azure.com/Cybersoft-Technologies-Inc/0d08063f-212a-4277-87f0-199e49d410e9/_apis/wit/attachments/f9d4f5b6-99b5-459e-a5e9-31243faff319?fileName=image.png|width=804,alt="Image"!

ACCEPTANCE CRITERIA:
Verify new guidelines can be downloaded/viewed/reflected within the Eligibility module

====================================================================================================
NXT-72160 | Story | Module=Financials | Status=New (In Progress) | Res='' | flags=['contract']
Created=4/22/2026 8:09 AM Resolved= Labels=''
SUMMARY: FIN — Payroll Import: Data Exchange

DESCRIPTION:
As a district finance user, I want to import journal entry lines into Financials, so that recurring payroll and other month-end journal entries can be loaded efficiently without manual data entry.

_Updated 2026-05-11. Rewritten to reflect the 2026-05-08 meeting with Hussain: validator gate removed; the import wizard is pure setup; all business-rule validation runs on the BL side (_*_NXT-70777_*_). Scope trimmed to behavior specific to Payroll Import — universal Import Monitor mechanics (column mapping interaction, file data preview, saved mapping persistence, supported file formats, multi-sheet handling, atomic file rejection, Import Monitor result chrome and tabs) are platform-provided and not re-described here._

----

h2. Scope

Behavior specific to *Payroll Import* in the Import Monitor pipeline: registering the import type, the Pre-upload fields, the file columns, the DE-side staging check, and the handoff to BL (*NXT-70777*).

----

h2. Requirements

h3. 1) Import Type Registration

The Import Monitor selector includes *Payroll Import* as a selectable type. Selection tooltip: _"Loads payroll and other month-end journal entries. File must have separate Debit and Credit columns."_

h3. 2) Pre-upload Fields

||Field||Required||Notes||
|Import Type|Yes|"Payroll Import"|
|Entry Description|Yes|Free text, max 50 characters. Applied verbatim as the header description on every journal entry produced by this import. Entered fresh on every import; never part of saved mapping.|

No fiscal year or period selector — both are derived per row from PostedDate at processing time (BL — see *NXT-70777*).

h3. 3) File Columns

The file must carry these 5 columns. This is the canonical Payroll Import contract.

||Column||Required||Type||Notes||
|GLAccount|Yes|String|Account identifier per Financials rules.|
|SiteCode|Yes|String|Must reference a valid SchoolCafe site. Use the Central Office site code for district-wide entries.|
|PostedDate|Yes|Date|Drives entry boundary (one entry per unique PostedDate), fiscal year, and period for the row.|
|Debit|Conditional|Decimal|Required if Credit is blank. Mutually exclusive with Credit per row.|
|Credit|Conditional|Decimal|Required if Debit is blank. Mutually exclusive with Debit per row.|

No line-level Description column — Financials 2.0 carries description at the entry header only.

h3. 4) DE Staging Check

After the user clicks Save and before BL Commit is invoked, DE performs one file-derived check:

*File-level Dr = Cr with

ACCEPTANCE CRITERIA:
*AC1 — Import Type Available.* Payroll Import appears in the Import Monitor selector with the tooltip text from §1.

*AC2 — Entry Description Required.* The Pre-upload tab presents Entry Description as a required free-text field with a 240-character maximum. The user cannot proceed past Pre-upload without a non-empty value.

*AC3 — Entry Description Not Saved in Mapping.* Saved mapping does not include Entry Description. It is re-entered on every import.

*AC4 — Field Mapping Targets.* The Field Mapping step presents GLAccount, SiteCode, PostedDate, Debit, and Credit as the SchoolCafé fields (§3).

*AC5 — DE Staging Dr=Cr Check.* On Save, DE sums all Debit values and all Credit values across the file. If |Debits − Credits| > $0.01, the file is rejected before BL Commit runs.

*AC6 — File Balance Exception Surfaced.* A staging-side rejection appears in Import Monitor → Exceptions as a row of type FileBalance with a description naming total Debits, total Credits, and the difference. No entries are written.

*AC7 — DE Sends to BL.* After the staging check passes, DE sends to BL Commit: the rows from the file, the Entry Description from Pre-upload, and the file details (original filename, file hash, uploaded by, uploaded at).

*AC8 — Supported File Formats.* Payroll Import accepts xlsx, xls, csv, and txt files. Any other format is rejected at upload per Import Monitor platform behavior.

*AC9 — Single Sheet.* DE reads only the first sheet of the uploaded file. Multi-sheet files are not rejected at upload; if the first sheet’s columns do not match the target fields, the Field Mapping step surfaces the mismatch.

*AC10 — Configuration Permissions.* Only users with Director, Central Office, or SchoolCafe Admin roles can create and edit Payroll Import configurations. Customer/Technical Support roles have full access (platform pattern).

*AC11 — Download Template Available.* The Pre-upload right-side panel includes a Download Template link that provides an .xlsx file with he

====================================================================================================
NXT-72261 | Story | Module=PE Insights | Status=Story Refinement/Efforting (In Progress) | Res='' | flags=['contract']
Created=4/28/2026 4:18 PM Resolved= Labels=''
SUMMARY: Insights - Security - Resources API - SC

DESCRIPTION:
*As a SchoolCafé Admin*
I want Insights permissions to be available through a SchoolCafe API
So that Insights can determine which KPI resources a user is allowed to access

----

h3. *Notes*

* This story applies to the *SchoolCafe platform only*.
* This story is for creating the SchoolCafe API only.
* A separate PrimeroEdge story will be created to provide the same type of permission data.
* A separate Insights story will be created for consuming the API and enforcing permissions in the Insights application.
* Permissions should not be included in the authentication token or full user profile object.
* This API should return only permission data relevant to the *Insights module*.

----

h3. *System Flow*

* User logs into SchoolCafe.
* User clicks on the *Insights* button.
* User is redirected (via SSO) to the Insights application in a new browser tab.
* After authentication is completed, the Insights application will call this API to retrieve the user’s Insights permissions.
* The API returns a list of resources the user has access to.
* The Insights application uses this data to:
** Control visibility of KPI cards, grids, and drawers
** Enforce access to features such as configuration and drill-through

----

h3. *Requirements*

* Create an API endpoint that returns Insights resource permissions for a user.
* The API should support retrieving permissions based on:
** User ID
** District ID
* The API should return a list of Insights resources the user has access to.
* Returned permission data should include enough information for Insights to determine:
** Which Insights resources the user can view
** Which Insights resources the user can edit, if applicable
* The returned permissions should be based on the user’s assigned role permissions in SchoolCafe.
* The API should only return resources related to the *Insights module*.
* The API should include KPI-level resources created under the Insights Dashboard, including:
** Front office KPI resources
** Back office KPI resources
** Menu Analysis
** Insights Dashboard permissions, if applicable
* Do not include unrelated modules or non-Insights permissions in the response.

----

h3. *Best Practices / Implementation Guidance*

* *Use a stable resource identifier*
** Return a consistent resource key/code (not only display name) to avoid dependency on UI labels.
* *Return allowed resources consistently*
** Prefer returning only the resources the user has access to.
** Insights will treat missing resources as no

ACCEPTANCE CRITERIA:
* API returns Insights resource permissions by User ID and District ID.
* API response includes only Insights-related resources.
* API returns the resources and permissions the user has access to based on SchoolCafe role permissions.
* API supports both View and Edit permissions where applicable.
* Users with no Insights permissions receive a valid no-access response.
* Response contract is documented and shared for PrimeroEdge alignment.
* API does not require Insights permissions to be added to the authentication token or full user profile object.

====================================================================================================
NXT-72262 | Story | Module=PE Insights | Status=Story Refinement/Efforting (In Progress) | Res='' | flags=['contract']
Created=4/28/2026 4:21 PM Resolved= Labels=''
SUMMARY: Insights - Security - API - PE

DESCRIPTION:
*As a SchoolCafé Admin*
I want Insights permissions to be available through a PrimeroEdge API
So that Insights can determine which KPI resources a user is allowed to access

----

h3. *Notes*

* This story applies to the *PrimeroEdge platform only*.
* This story is for creating the PrimeroEdge API only.
* A separate SchoolCafe story establishes the API contract that this API must follow.
* This API should *match the response contract defined by SchoolCafe* to ensure consistency across platforms.
* A separate Insights story will be created for consuming the API and enforcing permissions in the Insights application.
* Permissions should not be included in the authentication token or full user profile object.
* This API should return only permission data relevant to the *Insights module*.

----

h3. *System Flow*

* User logs into PrimeroEdge.
* User clicks on the *Insights* button.
* User is redirected (via SSO) to the Insights application in a new browser tab.
* After authentication is completed, the Insights application will call this API to retrieve the user’s Insights permissions.
* The API returns a list of resources the user has access to.
* The Insights application uses this data to:
** Control visibility of KPI cards, grids, and drawers
** Enforce access to features such as configuration and drill-through

----

h3. *Requirements*

* Create an API endpoint that returns Insights resource permissions for a user.
* The API should support retrieving permissions based on:
** User ID
** District ID
* The API should return a list of Insights resources the user has access to.
* Returned permission data should:
** Match the *SchoolCafe API response contract*
** Include enough information for Insights to determine:
*** Which resources the user can view
*** Which resources the user can edit, if applicable
* The returned permissions should be based on the user’s assigned role permissions in PrimeroEdge.
* The API should only return resources related to the *Insights module*.
* The API should include:
** Front office KPI resources
** Back office KPI resources
** Menu Analysis
** Insights Dashboard permissions, if applicable
* Do not include unrelated modules or non-Insights permissions in the response.

----

h3. *Best Practices / Implementation Guidance*

* *Follow the SchoolCafe contract*
** Response structure must match SchoolCafe to ensure compatibility with Insights.
* *Use a stable resource identifier*
** Return a consistent resource key/code (not only disp

ACCEPTANCE CRITERIA:
* API returns Insights resource permissions by User ID and District ID.
* API response matches the SchoolCafe API contract.
* API response includes only Insights-related resources.
* API returns the resources and permissions the user has access to based on PrimeroEdge role permissions.
* API supports both View and Edit permissions where applicable.
* Users with no Insights permissions receive a valid no-access response.
* API does not require Insights permissions to be added to the authentication token or full user profile object.

====================================================================================================
NXT-72372 | Story | Module=PE Insights | Status=Story Refinement/Efforting (In Progress) | Res='' | flags=['contract']
Created=5/1/2026 2:10 PM Resolved= Labels=''
SUMMARY: Insights - Schoolie  - Service Layer

DESCRIPTION:
*As a SchoolCafé Admin*
I want Schoolie AI requests handled through a shared service layer
So that AI behavior is consistent, trackable, reusable, and easier to maintain across the application

----

h3. *Notes*

* This story applies to the *Insights application*.
* Schoolie is used in multiple locations, including:
** Workspace Daily Recap
** Insights Dashboard analysis
** KPI Drawer analysis
** Compare Selected Sites
** Trend Analysis
* This story creates a shared AI service layer so Schoolie logic is not duplicated across each feature.
* The service layer should support both source platforms:
** SchoolCafe
** PrimeroEdge
* The service layer should integrate with the Usage Tracking Framework.
* If the Usage Tracking Framework is not fully available at implementation time, the AI service should be structured so logging can be plugged in later without refactoring the Schoolie entry points.

----

h3. *Requirements*

h4. *Centralized AI Request Handling*

* Create a shared service layer for Schoolie AI requests.
* All Schoolie entry points should route requests through this service layer.
* The service layer should handle:
** Prompt retrieval
** Prompt version selection
** Request/context construction
** OpenAI request execution
** Response handling
** Error handling
** Caching integration, when available
** Usage tracking events

----

h4. *Supported Schoolie Contexts*

The service layer should support the following Schoolie contexts:

* Workspace Daily Recap
* Dashboard Analysis
* KPI Drawer Analysis
* Compare Selected Sites
* Trend Analysis
* Future Schoolie prompt contexts

----

h4. *Prompt Handling*

* Retrieve the appropriate configured prompt based on prompt type/context.
* Use the latest active prompt version unless another version is explicitly provided.
* Include prompt version in the request context for:
** caching
** logging
** troubleshooting
** auditability

----

h4. *Request Context*

* Service should support passing relevant context, including:
** User ID
** District ID
** Source platform
** Prompt type/context
** Prompt version
** KPI identifier, when applicable
** District name, when available
** Site name, when applicable
** Selected site IDs
** Site count
** Date range
** Drawer type, when applicable
** Source screen / entry point
** Data payload or data hash

----

h4. *OpenAI Execution*

* Execute OpenAI request using the configured prompt and provided data/context.
* Support structured response output when available.
* Support fallb

ACCEPTANCE CRITERIA:
* All Schoolie entry points can route requests through the shared AI service layer.
* Service retrieves configured prompt based on prompt type/context.
* Prompt version is included in AI request context.
* OpenAI request logic is centralized and not duplicated across UI components.
* Service supports Workspace, Dashboard, KPI Drawer, Compare Selected Sites, and Trend Analysis contexts.
* Service integrates with Schoolie cache when available.
* Service emits AI usage events to the Usage Tracking Framework.
* Usage events include user, district, platform, prompt context, source screen, and response status.
* Cache hits do not call OpenAI.
* Errors are handled consistently and do not break the calling UI.
* Service returns a consistent response object to UI components.

====================================================================================================
NXT-72383 | Story | Module=PE Insights | Status=Story Refinement/Efforting (In Progress) | Res='' | flags=['contract']
Created=5/3/2026 1:42 PM Resolved= Labels=''
SUMMARY: Insights - Usage - Framework

DESCRIPTION:
*As a SchoolCafé Admin / Product Team Member*
I want a reusable usage tracking framework for Insights Workspace
So that we can measure product adoption, feature usage, and user engagement across the application

----

h3. *Notes*

* This story creates the *foundation only* for usage tracking.
* This story should not attempt to instrument every feature in the app.
* Follow-up stories will add tracking to:
** App and page usage
** Insights Dashboard
** Menu Analysis
** Schoolie AI
** Feedback usage
* Usage tracking should support both source platforms:
** SchoolCafe
** PrimeroEdge
* Usage data should be stored in the *Insights SaaS database/location*, not in the source platform databases.
* The framework should be reusable so future features can emit usage events without creating custom logging logic each time.

----

h3. *Requirements*

h4. *Create Shared Usage Event Contract*

* Define a standard usage event structure that can support different event types.
* Each event should include core fields where available:
** Event Type
** Timestamp
** User ID
** District ID
** Source Platform
*** SchoolCafe
*** PrimeroEdge
** Application
*** Insights Workspace
** Page / Area
** Context / Metadata
* Event-specific details should be supported through a flexible context object.

Example event structure:

{noformat}{
  "eventType": "KPI_DRAWER_OPENED",
  "timestamp": "2026-05-03T10:15:00Z",
  "userId": "12345",
  "districtId": "67890",
  "platform": "SchoolCafe",
  "application": "InsightsWorkspace",
  "page": "InsightsDashboard",
  "context": {
    "kpi": "Meals Per Labor Hour",
    "drawerType": "District",
    "dateRange": "This Month",
    "siteSelectionType": "All Sites",
    "siteCount": 25
  }
}
{noformat}

----

h4. *Create Usage Logging Service*

* Create a shared usage logging service that application features can call.
* Features should emit usage events through this shared service, not by directly calling APIs.
* Service should support logging events with:
** Required core fields
** Optional event-specific context
* Service should be reusable across Insights Workspace features.

----

h4. *Create Backend Endpoint*

* Create an API endpoint to receive usage events.
* Endpoint should validate required fields.
* Endpoint should store valid usage events.
* Endpoint should return a successful response when the event is captured.

----

h4. *Create Database Storage*

* Create a database table or equivalent persistence layer for usage events.

Recommended structur

ACCEPTANCE CRITERIA:
* Shared usage event contract is defined.
* Shared usage logging service is created.
* Backend endpoint accepts and stores usage events.
* Usage data is stored in the Insights SaaS database/location.
* Event table supports core fields plus flexible context JSON.
* Framework supports both SchoolCafe and PrimeroEdge users.
* Logging failures do not interrupt normal user workflows.
* Framework is reusable for future feature instrumentation stories.
* Initial controlled event type list is documented.

====================================================================================================
NXT-72677 | Story | Module=Platform - Data Exchange | Status=Story Refinement/Efforting (In Progress) | Res='' | flags=['FD_descAC', 'reqby']
Created=5/8/2026 9:29 AM Resolved= Labels=''
SUMMARY: Photo Import - Only One at a Time

DESCRIPTION:
*As a* Customer Support user,

*I want to* prevent multiple photo imports from running simultaneously for a single district,

*So that* system conflicts are avoided and photo imports complete successfully without crashing.

----

h3. *Notes*

* *Reference Ticket:* [Freshdesk #317627|https://primeroedge.freshdesk.com/a/tickets/317627]
* *Context:* Recent district complaints indicate that parallel photo import processes are causing database deadlocks or resource conflicts, leading to failed imports.
* *Scope:* This gatekeeping logic should be specific to the *Photo Import* type within the "Add New Import" workflow.

----

h3. *Business Requirements*

# *Concurrent Import Check:* When a user selects "Photo Import" from the "Add New Import" dropdown/selection, the system must perform a real-time check for any existing photo import tasks with a status of "Running" or "In Progress" for that specific District ID.
# *Workflow Gating:* If an active photo import is detected:
#* The "Next" button must be disabled/greyed out.
#* The user must be blocked from reaching the file upload/selection stage.
# *User Notification:* An informational message must be displayed to the user stating: _"There is currently a photo import running for this district. Please come back later once the current process is complete. You can monitor import progress on the Import Monitor tab"_
# *Standard Path:* If no active photo import is found, the system should allow the user to proceed to the upload and processing stages as usual.

ACCEPTANCE CRITERIA:
* *AC 1:* System verifies active photo imports immediately upon selection of the "Photo Import" type.
* *AC 2:* Users are physically prevented from clicking "Next" if a conflict is detected.
* *AC 3:* Specific guidance text is displayed only when a conflict exists.
* *AC 4:* System allows only one photo import to be processed per district at any given time.
* *AC 5:* Normal import functionality is restored automatically once the running import moves to a "Completed" or "Failed" status.

====================================================================================================
NXT-72755 | Story | Module=PE Insights | Status=Story Refinement/Efforting (In Progress) | Res='' | flags=['contract']
Created=5/11/2026 1:48 PM Resolved= Labels=''
SUMMARY: Insights - Telemetry - Standards

DESCRIPTION:
As a Product Team member, I want a standardized Product Observability Framework architecture and telemetry contract, so that usage, error, and performance tracking can be implemented consistently across Insights and future Workspace applications.

----

h1. Goals

Define the shared telemetry architecture and standards that will support:

* usage analytics
* error tracking
* performance tracking
* unified session pathways
* workflow correlation
* future observability domains

This story is architecture-focused and does not implement full instrumentation yet.

----

h1. Scope

This story defines:

* shared telemetry philosophy
* event taxonomy
* shared metadata standards
* correlation/session strategy
* telemetry domains
* batching/retry strategy
* configuration model
* storage approach
* migration strategy for existing usage tracking

This story does NOT include:

* full frontend instrumentation
* dashboard implementation
* complete migration of existing usage tracking
* production rollout

----

h1. Telemetry Domains

The framework must support distinct telemetry domains:

||Domain||Purpose||
|Usage|User interactions and workflows|
|Error|Failures, exceptions, API issues|
|Performance|Duration, latency, slow workflows|
|Future Domains|AI telemetry, reliability scoring, diagnostics|

Each domain must:

* share a common telemetry foundation
* support domain-specific metadata
* remain independently extensible

----

h1. Architecture Requirements

h2. Shared Telemetry Logger

Define a unified developer-facing API:

{noformat}telemetry.trackUsage(...)
telemetry.trackError(...)
telemetry.trackPerformance(...)
{noformat}

Internally:

* domain services remain separated
* shared queue/batching infrastructure reused
* shared metadata resolution reused

----

h2. Shared Metadata Contract

Define standardized shared telemetry fields.

Required shared fields:

* eventId
* eventDomain
* eventName
* timestamp
* sessionId
* module
* source

Optional shared fields:

* correlationId
* workflowId
* parentEventId
* districtId
* siteId
* userId
* route
* page
* component
* action

Field naming conventions must be standardized across all telemetry domains.

----

h2. Correlation Strategy

The framework must support:

* session-level correlation
* workflow correlation
* parent-child event relationships

Requirements:

* session timelines must support usage, error, and performance events together
* errors/performance events may reference triggering usage events
* correlation IDs

ACCEPTANCE CRITERIA:
* Shared telemetry domains are defined
* Shared metadata contract is defined
* Session/correlation strategy is defined
* Error taxonomy is defined
* Performance taxonomy is defined
* Configuration strategy is defined
* Migration strategy is documented
* Naming conventions are standardized
* Architecture supports future telemetry domains
* Existing usage tracking compatibility considerations are documented

====================================================================================================
NXT-72766 | Story | Module=PE Insights | Status=Story Refinement/Efforting (In Progress) | Res='' | flags=['contract']
Created=5/11/2026 2:17 PM Resolved= Labels=''
SUMMARY: Insights - Telemetry - Migrate Usage

DESCRIPTION:
As a Product Team member, I want the existing usage tracking framework to use the shared telemetry foundation, so that usage, error, and performance events can be correlated consistently without breaking existing dashboards or reporting.

h2. Goal

Refactor the existing usage tracker to plug into the new Product Observability Framework while preserving current behavior.

h2. Scope

This story includes:

* migrating usage events to shared telemetry types
* routing usage events through {{TelemetryLogger.trackUsage(...)}}
* adding missing shared metadata
* preserving district include/exclude behavior
* preserving existing dashboard compatibility
* adding correlation/session support
* avoiding large rewrites

This story does not include:

* changing existing dashboard visuals
* adding new usage events
* adding error dashboard widgets
* adding performance dashboard widgets
* rebuilding funnels
* changing business definitions of existing usage KPIs

h2. Migration Requirements

Existing usage tracking must continue to work.

Preserve:

* current usage events
* current event names where possible
* current dashboard calculations
* current district exclusions for demo/test districts
* current session behavior unless intentionally replaced by {{SessionManager}}
* current API/storage contract unless a backward-compatible migration is included

h2. Shared Telemetry Fields to Add

Add or map these fields onto usage events:

{noformat}eventDomain: "usage";
eventId;
eventName;
timestamp;
sessionId;
correlationId?;
workflowId?;
parentEventId?;
districtId?;
siteId?;
userId?;
module;
source;
route?;
page?;
component?;
action?;
properties?;
{noformat}

h2. Usage Event Mapping

Map existing usage events into standardized categories:

{noformat}usageCategory:
  | "page_view"
  | "navigation"
  | "interaction"
  | "filter"
  | "drawer"
  | "report"
  | "ai"
  | "settings";
{noformat}

Example mappings:

||Existing Event||Usage Category||
|Dashboard viewed|{{page_view}}|
|KPI card clicked|{{interaction}}|
|KPI drawer opened|{{drawer}}|
|Filter changed|{{filter}}|
|Report exported|{{report}}|
|AI recap requested|{{ai}}|
|Settings updated|{{settings}}|

h2. Correlation Requirements

Usage events should support correlation context.

Example:

{noformat}const context = telemetry.createWorkflowContext("inventory_value_drawer");

telemetry.trackUsage("kpi_drawer_opened", {
  ...context,
  usageCategory: "drawer",
  component: "KpiDrawer",
  action: "open_inventory_value"
});
{noformat}

ACCEPTANCE CRITERIA:
* Existing usage tracker routes through shared telemetry foundation.
* Usage events include {{eventDomain: "usage"}}.
* Usage events include shared session metadata.
* Usage events support optional correlation/workflow metadata.
* Existing district usage exclusions continue working.
* Error tracking remains independent of usage exclusions.
* Performance tracking remains independently configurable.
* Existing dashboards continue working.
* Existing event names are preserved unless explicitly mapped.
* Migration avoids large instrumentation rewrites.
* Existing usage tracker can remain as a compatibility wrapper.

====================================================================================================
NXT-72790 | Story | Module=Item Management | Status=Story Refinement/Efforting (In Progress) | Res='' | flags=['FD_descAC', 'known_customer']
Created=5/12/2026 9:56 AM Resolved= Labels=''
SUMMARY: IM - Item Config - Menu Item Categories - allow Cybersoft categories to be disabled for POS Item

DESCRIPTION:
As a Front Office only customer I want the ability to disable the 5 major menu item categories (Entree, Milk, Grain, Veg, Fruit) from being enabled as POS Item categories, so I can use only the POS categories I create.

* [FD Ticket 318420 (internal)|https://primeroedge.freshdesk.com/a/tickets/318430]
* [FD Ticket 321324 (Mankato)|https://primeroedge.freshdesk.com/a/tickets/321324] 

Currently, the POS Item checkbox is forcibly enabled just like Menu Item. However, only Menu Item needs to be forcibly enabled.

!image-20260512-145600.png|width=673,alt="image-20260512-145600.png"!

ACCEPTANCE CRITERIA:
* Update the Menu Item Categories edit slide-out to allow the POS Item checkbox to be disabled for the categories in the Cybersoft data source 
* Keep the Menu Item checkbox forcibly enabled

====================================================================================================
NXT-73278 | Enhancement | Module=Accountability | Status=In Progress (In Progress) | Res='' | flags=['FD_descAC', 'known_customer', 'struct_summary']
Created=5/28/2026 7:50 AM Resolved= Labels=''
SUMMARY: Acc-Wadena- Deer Creek Public Schools - Edit Check notation question

DESCRIPTION:
District called reporting Edit check flag on sessions for reduced.

!https://attachment.freshdesk.com/inline/attachment?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MjIxOTA5MDk1MzMsImRvbWFpbiI6InByaW1lcm9lZGdlLmZyZXNoZGVzay5jb20iLCJhY2NvdW50X2lkIjo1MDc2MTF9.UgeOx7zNEfg4HPadbDfV5O6tpd-fMlU5ccHfpgmpRZ8|width=250!

!https://attachment.freshdesk.com/inline/attachment?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MjIxOTA5MDk1MzcsImRvbWFpbiI6InByaW1lcm9lZGdlLmZyZXNoZGVzay5jb20iLCJhY2NvdW50X2lkIjo1MDc2MTF9.ZL1lCWMuxHy16BMgj0v-wR-zxCR71UD0W-t4QQDRcco|width=250!

!https://attachment.freshdesk.com/inline/attachment?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MjIxOTA5MDk2MTksImRvbWFpbiI6InByaW1lcm9lZGdlLmZyZXNoZGVzay5jb20iLCJhY2NvdW50X2lkIjo1MDc2MTF9.vY6VdfcsIZu-hatilMEa7vhp9-LLFh9ewocTpYZXu48|width=250!

in the report we are checking  Mealcount> ([Approved] + Visit - Away) where as edit check page we are checking  Mealcount> Approved

Due to this edit check page showing data and where as edit check report is not showing highlighting



----

Discussion on {{2026-05-29}} (Hussain, Haritha, Naveen, Prasoona, Harsha, Matt)

* Edit Check report needs a small update as well to flag edit checks on attendance factor for small counts.
* Text update: AA Elig = Attendance Adjusted Eligible. The number of meals allowed before the Attendance Factor is exceeded. Calculation = (Elig (V/A) X AF)

!image-20260529-165100.png|width=516,alt="image-20260529-165100.png"!

ACCEPTANCE CRITERIA:
check changes in edit check page and edit check report

====================================================================================================
NXT-73281 | Story | Module=Platform - Data Exchange | Status=New (In Progress) | Res='' | flags=['known_customer']
Created=5/29/2026 7:08 PM Resolved= Labels=''
SUMMARY: Washburn - Post Migration Observations & Fixes

DESCRIPTION: (blank)

ACCEPTANCE CRITERIA:
Issues found during & after Washburn Migration

