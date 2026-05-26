# Filtered ticket digest — 61 tickets

## NXT-70440 — Eligibility - Other Forms - Display submitted Form Applications in Grid

- Resolved: 2026-05-12
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

As a Cybersoft Implementation team member or district admin, I would like to be able to set up Summer EBT (as well as any other non-traditional form) at a district-level with minimal steps, so that I do not have to use an external system just for this purpose.

*Summary*

* Integrate grid-level changes to the Other Forms page, for both ALL and Pending tabs

*Details*

* In Eligibility > Forms > Other Forms when the user loads the page, display all submitted Form Applications in the grid by doing the following:
** Pending form applications alone should also show in a ‘Pending’ tab.
** Please have the page switch to using the ‘Income Surveys’ list of columns instead of the ‘Applications’ list of columns (sorry!). Except, keep ‘Form Application #’ as there is no need for ‘Survey #’.
** Also, add a few new columns:
*** *Form Name* – the form to which this application belongs. Corresponds to ‘Form Select’ filter option.
**** Side-note: Please rename ‘Form Select’ to ‘Select Form’ or ‘Form Name’
*** *Result* – Will show ‘Qualified’ or ‘Unqualified’ but can be blank for now.
*** *Household Income* – Same as in Applications page (place it below Household Income Range in the columns list)
*** *Frequency* – Corresponds to the select income frequency (if applicable) selected on the application
** Default columns on ALL tab:
*** Form Application #
*** Form Name
*** Entry Method
*** Status
*** Received Date
*** Result
*** Household Size
*** Household Income Range
*** Household Income
*** Frequency
** Default columns on Pending tab:
*** Form Application #
*** Form Name
*** Entry Method
*** Received Date
*** Student Name(s)
*** Reason
** Grid results should now work in tandem with the filters above them
* Can be handled in a separate story:
** Application Details page, with its edits. We can work on this when we integrate ‘Qualified’/’Unqualified’
** History – Can be worked on with Application Details.
** Delete – Can be worked on with Application Details.
**  ‘Excel’ button – Can be skipped for now if it is additional effort as we need to make some changes to it anyway.

*Mockup*

N/A

### Acceptance Criteria

Verify the back-end work in the Other Forms page has been completed to support form applications displaying properly in the ALL and Pending tab grids.

---

## NXT-68256 — Elig - Verification - 2026 QoL Updates, Include CEP Setting Update

- Resolved: 2026-05-05
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

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

### Acceptance Criteria

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

---

## NXT-71226 — Eligibility - Other Forms - (Part 1) Complete 'Add New Form Application' button functionality

- Resolved: 2026-05-04
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

As a Cybersoft Implementation team member or district admin, I would like to be able to add Summer EBT (as well as any other non-traditional form) applications at a district-level with minimal steps, so that I do not have to use an external system just for this purpose.

*Summary*

* Allow users to add a form application for any active form type 
** *Story 1 (Application button/page UI, API): Effort - 8*
** Story 2 (Submit/Pending and Application Image): Effort - 8

*Details*

* In Eligibility > Forms > Other Forms, enable the ‘Add New Form Application’ button to open a stepper which mimics the Add New Survey page for current Income Surveys.
** This new entry page can be titled: *Add New Form Application*.
**  It would be great if somewhere on the page, or even on each step, if we can show the name of the specific form name to which this application belongs.
* This button will need to allow users to select +one+ active form type (i.e. Summer EBT form, Income Survey, ‘Form ABC’, etc.).
** Design is negotiable; i.e. currently this button opens a drawer. If we include the active forms in that drawer and have the user pick one which then takes them to the ‘Add New Form Application’ page for that form type, that is one solution.
* Within the ‘Form Application Entry’ page, have the stepper contain all of the steps of the existing application, with the exception of those functions which are tied to that form’s configuration. These steps will change based on the options selected:
* Income collection method
** Choice: *Individual / Household / None*
** Behavior: In the Household step of the application, we should display the related income collection fields according to what was chosen above
*** Individual: display the Household step with the individual household members having their own income (similar to current FRE app)
**** Only in this scenario, we will collect PFD
*** Household: display the Household step with a single total household income field (similar to current Income Survey)
*** None: hide the income fields entirely. Only Total Household Members/Household Size should remain.
* Contact Info Step
** Require First and Last Name fields only
* Form requires last 4 digits of SSN
** Choice: *Yes/No/Partial*
** Behavior: In the Comments step of the application, show or hide all text and fields for asking about/collecting SSN. If ‘Yes’, display a ‘Last 4 digits of SSN’ checkbox and field beneath the signature line (copy design from the FRE application stepper). 


!image-20260318-034951.png|width=671,alt="image-20260318-034951.png"!

!image-20260318-035018.png|width=719,alt="image-20260318-035018.png"!



* …
** Display it on the Summary step as well.
** Treat ‘Partial’ SSN the same as ‘Yes’
* Form requires electronic signature
** Choice: *Yes/No*
** Behavior: In the Submit step of the application, show or hide signature field/selection. 
* Allow the user to submit the application as complete or mark it as ‘Pending’, as well as the same ‘I’m Done’ or ‘Submit Another Form Application’ options. We can display submitted forms in the next story, and ‘Qualified’/’Unqualified’ results in a separate story as well.
** Add ‘Pending Reasons’ (same as Applications) as well, plus the related logic. i.e. household size needs to match or otherwise users cannot submit.
* Additionally, at the end of the application, display the associated form application image with its associated print/export buttons.



Reference screens

!image-20260318-035134.png|width=719,alt="image-20260318-035134.png"!

!image-20260318-035200.png|width=719,alt="image-20260318-035200.png"!

### Acceptance Criteria

Verify that the ‘Add New Form Application’ button is now functional, allowing the user to select their form of choice and then fill out (but not submit) an application according to that form’s configuration.

---

## NXT-71227 — SchoolCafé - Forms - (Part 1) Family Hub-related changes for Forms Licensing, Forms Template

- Resolved: 2026-04-28
- Status: Done Done
- Resolution: Done
- Components: Eligibility, Family Hub

### Description

As a Family Hub parent/applicant, I would like to be able to apply for Summer EBT (as well as any other non-traditional form) applications with minimal steps, so that I do not have to use an external system just for this purpose.

*Summary*

* Story 1:
** Update School Café Family Hub operations and licensing to reflect the new Forms changes.
** Add a new SchoolCafé 'Forms Template' template and application/wizard to reflect the new Forms changes. Effort: 8
* Story 2:
** Add a new SchoolCafé 'Fill out a Form' step to reflect the new Forms changes. The actual logic/ submission of the form application can be added later on if required. Effort: 8

*Details*

* In Super Admin – Configuration – Configure Districts, do the following:  
** Add a new License: ‘Forms’ 
** Tie ‘Forms Template’ and ‘Fill Out a Form’ operations to this license
!image-20260318-035507.png|width=789,height=388,alt="image-20260318-035507.png"!
* In the district short URL page, if the district has the ‘Forms’ district license toggled on, display a line that says ‘Submit Forms’. In terms of display order, display it after the ‘Submit Meal Applications’ line:

!image-20260318-035526.png|width=513,height=249,alt="image-20260318-035526.png"!

# As a district admin, in the Benefits category, copy what we are doing for SEBT (reference Summer EBT in the Classic SC Family Portal), when the Forms license is enabled:
#* Add a new ‘Forms Template’ page which functions like the ‘Program Template’ page, displays all active Forms and allows them to be edited. It can have the same steps as that page, except one additional step described below.
#* Use the same language list from Manage Languages page.
!image-20260318-035604.png|width=815,height=420,alt="image-20260318-035604.png"!
We can look at Form questionnaire answers/settings in a follow-up story.
#* This story is complete when all steps on the Forms Template page are completed, with the page being accessible by district admins when the newly-added Forms license is toggled on. A user should also then be able to see that the district accepts forms via the district’s short url page.
#* 

*Mockups*

N/A

### Acceptance Criteria

Verify new 'Forms' license, as well as district short URL behavior, has been added. Verify Forms Template has been added (full functionality is not required yet, just basic availability and design).

---

## NXT-66821 — Elig - DC - Extensions - Extending a different DC Type to the same student, blocking inactive Source students

- Resolved: 2026-04-15
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

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

### Acceptance Criteria

* User can perform a DC Extension repeatedly between the same students. (scenario A)
** Manual Match should be possible in this scenario, but the user is advised accordingly.
* Inactive students are not used as a source of DC Extension + data clean-up. (scenario B)

---

## NXT-70453 — Eligibility - Configuration - FRE Application Image - New page to modify FRE image

- Resolved: 2026-04-14
- Status: Done Done
- Resolution: Done
- Components: Eligibility, Family Hub

### Description

As a Cybersoft admin, I would like to be able to modify the HTML image template for my FRE apps, so that I may make them more closely aligned to my SchoolCafé (and paper) application.

*Summary*

* Add a new page to allow Cybersoft users to update the _Default_ application image template for the current FRE Application.
* When opening this image template, enable the 'Save' button for Cybersoft admins so that they can save changes on the district's behalf, upon (documented) request.

*Details*

* In Eligibility > Settings, add a new page: *_Application Image_*
** Page can be displayed at the bottom of the category
** By default, permissions for this page can be assigned to Cybersoft admins only
** Page should have a subtitle with a warning prompt: 
*** *Warning:* Please make sure that +any+ changes to this image are in compliance with the rules and regulations for the state to which this district belongs, and be advised that updates made to this image will immediately impact ALL applications, +past and present+.
*** 
* Within the page, beneath that warning
** display the default FRE image which corresponds to all current FRE apps (not form apps):
** enable a '_Save'_ (and 'Cancel') button, so that any changes they make on the page will be permanently saved in the Default image for that district. (Default inheritance can be from -10 region)
** Default name can be ‘Standard Application Image’

*Mockup*

N/A

### Acceptance Criteria

Verify that certain users can now update the standard FRE application image

---

## NXT-70451 — Eligibility - Forms - Form Configuration - Form Image Templates Tab - Add new image templates

- Resolved: 2026-04-14
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

As a Cybersoft Implementation team member, I would like to be able to set up Summer EBT (as well as any other non-traditional form) at a district-level with minimal steps, so that I do not have to use an external system just for this purpose.

*Summary*

* Integrate additional back-end changes to the Forms Configuration page’s Form Image Templates tab, allowing a user to view and add a form application image.

*Details*

* In _Eligibility > Settings > Forms Configuration_, do the following:
** In the *Form Image Templates* tab, add a Default form image template and the means to edit it as well as ‘Save As’ for the purpose of making multiple form application images.
*** Display a form image selection, where only ‘Default’ will be available in the beginning.
*** Based on the form selected, display the form’s image within the page and allow the user to edit the HTML directly.
**** The title can be ‘{formName} Form Image’ i.e. *Summer EBT Form Image*
**** Any text should be editable. Users will need to be careful not to touch field data.
*** Add a ‘Save As’ button which will be enabled to anyone. Users cannot overwrite the Default template.
*** When the user clicks the ‘Save As’ button in this drawer, prompt them to rename it, save it and add it to the grid. It should now be referenceable in other pages as needed. Grid behavior is in a separate story.
**** Just FYI: In the future, it should accommodate changes made when we get to the processing part (for both ‘Latest’ and ‘Original’ versions of an app)
!image-20260224-184809.png|width=488,alt="image-20260224-184809.png"!


*Mockups*

!image-20260224-190317.png|width=699,alt="image-20260224-190317.png"!

Reference image from Classic:

!image-20260224-201200.png|width=856,alt="image-20260224-201200.png"!

### Acceptance Criteria

Verify this particular work in the Form Configuration page has been completed to support full functionality of this tab

---

## NXT-70450 — Eligibility - Forms - Form Configuration - Forms Tab - Add New Form to grid

- Resolved: 2026-04-14
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

As a Cybersoft Implementation team member, I would like to be able to set up Summer EBT (as well as any other non-traditional form) at a district-level with minimal steps, so that I do not have to use an external system just for this purpose.

*Summary*

* Integrate back-end changes to the Forms Configuration page’s Forms tab.

*Details*

* In _Eligibility > Settings > Forms Configuration_, do the following:
** In the _Forms_ tab, add the back-end for the ‘Add New Form Application’ drawer.
*** {color:#403294}*Name* {color}(accepts any character up to 50, if we need a limit) 
*** {color:#403294}*Description* {color}(accepts any character up to 50, if we need a limit)
*** {color:#403294}*Other Benefit*{color}
**** Display a drop-down that includes the list of active benefits. Next to the benefit, display the current academic year. i.e. *Bus Fees (2025-2026)*
**** Please verify that the Other Benefits page disables the delete icon if any benefit is in use by an active form or an inactive form with applications already submitted.
*** {color:#403294}*Form Image Template*{color}
**** Display active form image templates created as part of [https://primeroedgenext.atlassian.net/browse/NXT-70451|https://primeroedgenext.atlassian.net/browse/NXT-70451|smart-link]. 
**** Keep ‘Default’ as the default field value.
*** {color:#403294}*Start Date*{color}
**** Automatically populate today’s date. This field is required and not currently in use, but may become so in the future.
*** {color:#403294}*End Date*{color}
**** This field can default as blank. It is optional and not currently in use, but may become so in the future (to set/treat a form as inactive).
*** {color:#403294}*Site(s) associated*{color}
**** Display all active sites for the district. Multi-select field.
*** {color:#403294}*Form requires verification*{color}
**** If the user selects ‘Yes’, display a second-level of options (toggle, drop-down, radio button, etc. any is fine): *Standard* or *Rolling*
**** We will implement the verification dates and types later.
*** {color:#403294}*Income collection method*{color} (just save the selection for now)
**** *Additional questions added after March 10th/11th meetings, added to this story by DEV request:*
***** IF Income collection method selection = ‘Individual’, display a new, nested question:
***** {color:#403294}*Accept child income*{color} (Yes/No - corresponding to child income setting. Can display that setting’s current Yes or No value by default, but allow the user to ignore it for the selected form application type)
*** {color:#403294}*Form requires last 4 digits of SSN*{color} (just save the selection for now)
*** {color:#403294}*Form requires electronic signature*{color} (just save the selection for now) 
*** {color:#403294}*This form must have its own notification letters*{color} (just save the selection for now) 
*** *Additional questions added after March 10th/11th meetings, added to this story by DEV request:*
**** {color:#403294}*Display privacy act / disclaimer*{color} (Yes/No - corresponding to the Disclaimer setting. Can display that setting’s current Yes or No value by default, but allow the user to ignore it for the selected form application type)
**** IF district is in Alaska (AK), display a new question:
**** {color:#403294}*Accept PFD*{color} (Yes/No - corresponding to the PFD setting. Can display that setting’s current Yes or No value by default, but allow the user to ignore it for the selected form application type)
*** {color:#403294}*Form is enabled*{color}
**** Displays whether the forms in the grid or Enabled/Active or Disabled/Active
** When the user clicks the Save button in this drawer, save it and add it to the list. It should now be referenceable in other pages as needed.

{panel:bgColor=#deebff}
* Form-to-Template is a 1:1 relationship. A form can only be associated with one template. 
** However, a template can be associated with multiple forms (i.e. Default).
{panel}



*Mockup*

N/A

### Acceptance Criteria

Verify this particular work in the Form Configuration page has been completed to support full functionality of this tab

---

## NXT-70452 — Eligibility - Forms - Form Configuration - Form Image Templates Tab - Template Grid

- Resolved: 2026-03-31
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

As a Cybersoft Implementation team member, I would like to be able to set up Summer EBT (as well as any other non-traditional form) at a district-level with minimal steps, so that I do not have to use an external system just for this purpose.

*Summary*

* Integrate additional back-end changes to the Forms Configuration page’s Form Image Templates tab, including the Action(s) column.
* Combine the Template and Reference Image tab’s into one, including the table.

*Details*

* In _Eligibility > Settings > Forms Configuration_, do the following:
** In the *Form Image Templates* tab, combine the grid for the Template and Reference Image sub-tabs, since we can probably tie everything together in a single grid.
** Remove the ‘Subject’ column. We’ll handle any additional functionality in the ‘Action(s)' column
** Display a ‘Default’ record in the grid, which will correspond to the default form application image. These fields should be searchable and sortable.
*** Template Name: *S**tandard Image Template* 
*** Form(s) Associated: This can be empty for now. We will tie this image to new forms in other stories.
*** Status: Active
**** Add column filters. 
*** Type: Standard or Custom
*** Action(s): Display the following buttons:
**** Edit Pencil - Opens a drawer that allows the user to change the name-, forms associated,- and active/inactive status.
**** View - Opens the form image HTML editor in [https://primeroedgenext.atlassian.net/browse/NXT-70451|https://primeroedgenext.atlassian.net/browse/NXT-70451|smart-link].
**** History - Allows the user to view all related changes to this template. We don’t necessarily need to track history of what fields were changed in the image, but we should at least show whether someone updated the image.
**** 

*Mockups*

!image-20260224-191223.png|width=1282,height=233,alt="image-20260224-191223.png"!

Reference image from Classic:

!image-20260224-195806.png|width=1218,height=624,alt="image-20260224-195806.png"!

### Acceptance Criteria

Verify this particular work in the Form Configuration page has been completed to support full functionality of this tab

---

## NXT-70092 — Eligibility - Forms Framework - Form Configuration - Add ability to add/update Forms (UI)

- Resolved: 2026-02-23
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

As a Cybersoft Implementation team member, I would like to be able to set up Summer EBT (as well as any other non-traditional form) at a district-level with minimal steps, so that I do not have to use an external system just for this purpose.

*Summary*

* Update page layout of _Form Configuration_ page to accommodate the ability to manage new and existing forms, as well as image templates

*Details*

* In _Form Configuration,_ do the following:
** Add new tabs for inserting and updating Forms, as well as Form Image Templates, as defined by the user
*** Divide the page into 3 tabs:
**** *Forms* (default tab)
***** Sub-title/help text:  This section lets you add or remove non-school meal forms. The School Meal Application and Income Survey (where applicable) can also be modified here in a limited capacity.
***** {color:#6554c0}*(NICE-TO-HAVE in this story)*{color} Beneath, display a basic table with a layout similar to the one we show in the ‘Forms’ section^1^ of the PrimeroEdge Forms & Benefits page (UI only--backend/API to be in a separate story) 
**** *Form Image Templates*
***** Sub-title/help text:  This section lets you manage custom image templates that accompany non-school meal forms (the 'Application Image'). To update the Default School Meal Application and Income Survey, please contact Customer Care.
***** {color:#6554c0}*(NICE-TO-HAVE in this story)* {color}Beneath, display a table similar to the one we show in the PrimeroEdge Form Image Templates page with Templates^2^ and Reference Image^3^ (backend/API to be in a separate story) 
**** *Auto-Processing Rules* (formerly the existing content on the page, will be moved to its own tab)
***** Sub-title/help text:  This section lets you control scenarios where an online application, with automatic processing, may be parked as pending. For example, applications with students at CEP sites are typically moved to Pending as they are not usually processed. But if you turn that option off, they will be processed per usual and will not be in Pending Applications.
** Any user who has page-level access to Form Configuration (formerly ‘Form Settings’), gets the same level of access for all 3 tabs.


*Mockup*

{panel:bgColor=#deebff}
(*Note* that I have combined all of the content into one page, but the final mockup should have this content divided into 3 separate page tabs rather than being visible all at once)
{panel}

!image-20260209-213421.png|width=1399,alt="image-20260209-213421.png"!



*Concept Images (from PrimeroEdge):*

*  Reference^1^

!image-20260209-210810.png|width=1182,alt="image-20260209-210810.png"!

*  Reference^2^

!image-20260209-211907.png|width=1188,alt="image-20260209-211907.png"!

*  Reference^3^

!image-20260209-214006.png|width=1188,alt="image-20260209-214006.png"!

### Acceptance Criteria

Verify these foundational items have been added to SchoolCafe to allow development of the full framework

---

## NXT-69982 — Eligibility - Forms Framework - Add/update necessary operations, and permissions 

- Resolved: 2026-02-23
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

As a Cybersoft Implementation team member, I would like to be able to set up Summer EBT (as well as any other non-traditional form) at a district-level with minimal steps, so that I do not have to use an external system just for this purpose.

*Summary*

* Update Forms category and pages, etc. to create a foundation for a 'Forms' framework
* Grant Forms permissions to some district-level users and enable the operation by default for districts with a Student Eligibility license

*Details*

* Add new page operation for viewing and managing other (non-App/Survey) forms within a district. 
** Create a new ‘Other Forms’ permission and automatically assign them to ‘SchoolCafé Administrator’ and ‘Director-‘level users, or any role that already has either Applications or Surveys permissions.
*** Create new page permissions. They can match those of the other pages in the Forms category
** Create new *_Other Forms_* operation/page. Automatically set operation to a number other than -1 at the district level (or however we make pages visible in the SC resource catalog).
*** This will be similar to the ‘Manage Forms’ page in PrimeroEdge in a separate story.
*** {color:#6554c0}*(NICE-TO-HAVE in this story)*{color} Within this new page, display a basic table with a layout similar to the one we show in that page (UI only--backend/API to be in a separate story). 
**** Look and feel can mimic our current Applications and Surveys pages:
!image-20260209-215717.png|width=987,alt="image-20260209-215717.png"!
**** Circled columns can likely be removed, since we will adopt the same ‘Pending Application’ and ‘Pending Students’ layout (again, API work in another story).
!image-20260209-215446.png|width=987,alt="image-20260209-215446.png"!


** This new operation can be placed between Surveys and Processing:
!image-20260204-032016.png|width=310,alt="image-20260204-032016.png"!
* Make small changes to the Form Settings page.
** Change the operation and page title to *_Form Configuration_*
** This page will house some of the data in the Forms & Benefits page in PrimeroEdge (just the top Forms section data) in a separate story.

### Acceptance Criteria

Verify these foundational items have been added to SchoolCafe to allow development of the full framework

---

## NXT-66798 — Elig - Apps - Pending Students with multiple matches

- Resolved: 2025-10-28
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

!image-20250923-190330.png|width=466,alt="image-20250923-190330.png"!

*requirements*

* User should be able to select 1 of the matches and complete the student matching.
* User should be able to see if one of the potential accounts is Active/Inactive
** Add the following lines for Student Details:
*** Status
**** Show Active or Inactive
*** Eligibility
**** Show Free/Reduced/Paid and Basis
***** Example: Free (DC MEDICAID)

----

SCOPE CREEP 10/9/25

* Workflow changes for the following scenarios:
** System single matches.
** System multiple matches.
** Manual matches.
* All scenarios link a Pending Student to an actual Account (personid)
** We need to track the link.
** Application Details should *not* be updated as part of the search / manual matching.
* User needs to click Process Matches: 
** to have the Application Details update.
** Existing workflow continues from here - student receives benefits, etc.
* Unmatch / Match button available if more than 1 potential pending student is found / added.
* Add the following strings:
** On the page itself:
*** You can see pending students from applications on this page. The *Find Matches* button will attempt to locate students to match them against. You can find, edit, and review matches under the Actions column. Find matches first, and then use the select checkboxes and the *Process Matches* button to extend eligibility.
*** !image-20251009-204246.png|width=852,alt="image-20251009-204246.png"!
** On the View Match window:
*** You are viewing the submitted information from the Form and details from at least 1 potential student. If multiple students are shown, select one with the *Match* button to proceed.
*** !image-20251009-204852.png|width=678,alt="image-20251009-204852.png"!

** Success message after the user selects a match, either from the View window or via a Manual Search: 
*** Pending Student match has been added. Select the checkboxes and use *Process Matches* to continue.

### Acceptance Criteria

* User can complete Pending Student matches in all scenarios
* User can complete Pending Student matches with multiple results
** User must select 1 of the potential matches to proceed
* User can see instruction text on the Pending Students tab, the View window, and a Success message when matching
* Links are created when a potential match is found
* User can remove a linked student
* Application Details is only updated after Process Matches is executed
* User can see Status and Eligibility in the Match Details screen 
* Once Matches are processed:
** student is linked to the app
** student eligibility updated accordingly

---

## NXT-63985 — Elig - Reports - Income Survey - Page / Report Updates

- Resolved: 2025-08-25
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

As Dana the Director I want finer control over selections on the Income Survey report so that I’m not having to run the report multiple times. This will be an efficiency driver.

!image-20250714-194402.png|width=834,height=252,alt="image-20250714-194402.png"!



*requirements*

* Update dropdowns to be multi-select
** Site Code / Site Name
* -Swap the date selector out for the new picker component-
* Reports updated to take and display the parameters accordingly

### Acceptance Criteria

* Selected dropdowns are converted into multi-select
* -Date selector swapped out-
* Reports accept parameters and display accordingly
** Report Criteria also updated accordingly

---

## NXT-63980 — Elig - Reports - Application Counts - Page / Report Updates

- Resolved: 2025-08-22
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

As Dana the Director I want finer control over selections on the Application Counts report so that I’m not having to run the report multiple times. This will be an efficiency driver.

!image-20250714-193743.png|width=834,height=266,alt="image-20250714-193743.png"!



*requirements*

* Update dropdowns to be multi-select
** Site Code / Site Name
* Swap the date selector out for the new picker component
* Reports updated to take and display the parameters accordingly

### Acceptance Criteria

* Selected dropdowns are converted into multi-select
* Date selector swapped out
* Reports accept parameters and display accordingly
** Report Criteria also updated accordingly

---

## NXT-63984 — Elig - Reports - Eligibility Summary - Page / Report Updates

- Resolved: 2025-08-18
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

As Dana the Director I want finer control over selections on the Summary report so that I’m not having to run the report multiple times. This will be an efficiency driver.

!image-20250714-194326.png|width=830,height=273,alt="image-20250714-194326.png"!



*requirements*

* Update dropdowns to be multi-select
** Site Code / Site Name
* Swap the date selector out for the new picker component
* Reports updated to take and display the parameters accordingly

### Acceptance Criteria

* Selected dropdowns are converted into multi-select
* Date selector swapped out
* Reports accept parameters and display accordingly
** Report Criteria also updated accordingly

---

## NXT-63983 — Elig - Reports - Eco Dis % - Page / Report Updates

- Resolved: 2025-08-18
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

As Dana the Director I want finer control over selections on the Eco Dis % report so that I’m not having to run the report multiple times. This will be an efficiency driver.

!image-20250714-194222.png|width=826,height=231,alt="image-20250714-194222.png"!



*requirements*

* Update dropdowns to be multi-select
** Site Code / Site Name
* -Swap the date selector out for the new picker component-
* Reports updated to take and display the parameters accordingly

### Acceptance Criteria

* Selected dropdowns are converted into multi-select
* -Date selector swapped out-
* Reports accept parameters and display accordingly
** Report Criteria also updated accordingly

---

## NXT-63982 — Elig - Reports - Direct Certification Counts - Page / Report Updates

- Resolved: 2025-08-18
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

As Dana the Director I want finer control over selections on the Direct Certification Counts report so that I’m not having to run the report multiple times. This will be an efficiency driver.

!image-20250714-194139.png|width=827,height=269,alt="image-20250714-194139.png"!



*requirements*

* Update dropdowns to be multi-select
** Site Code / Site Name
* Swap the date selector out for the new picker component
* Reports updated to take and display the parameters accordingly

### Acceptance Criteria

* Selected dropdowns are converted into multi-select
* Date selector swapped out
* Reports accept parameters and display accordingly
** Report Criteria also updated accordingly

---

## NXT-63981 — Elig - Reports - CEP Identified Students - Page / Report Updates

- Resolved: 2025-08-18
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

As Dana the Director I want finer control over selections on the CEP Identified Students report so that I’m not having to run the report multiple times. This will be an efficiency driver.

!image-20250714-194036.png|width=848,height=290,alt="image-20250714-194036.png"!



*requirements*

* Update dropdowns to be multi-select
** Site Code / Site Name
* Swap the date selector out for the new picker component
* Reports updated to take and display the parameters accordingly

### Acceptance Criteria

* Selected dropdowns are converted into multi-select
* Date selector swapped out
* Reports accept parameters and display accordingly
** Report Criteria also updated accordingly

---

## NXT-63628 — Elig - Optional Benefits - Allow next Academic Year to be editable, Copy feature

- Resolved: 2025-07-28
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

*tickets*

[https://primeroedge.freshdesk.com/a/tickets/286531|https://primeroedge.freshdesk.com/a/tickets/286531]



*requirements*

* User can select a future academic year and edit departments + optional benefits.
* User can select a prior academic year and copy departments + optional benefits to a new year.
** This should update the linked academic year but otherwise copy the department and benefit setup.
** User selects a year to copy from
** User gets a confirmation prompt

!image-20250625-191131.png|width=1666,height=618,alt="image-20250625-191131.png"!

----

Strings:

* Confirmation Prompt
** {noformat}This will copy and replace the optional benefits data for the following academic year: {{Academic Year}}. Departments and Benefits will be copied. Anything current configured for that academic year will be removed.

Are you sure you want to proceed?{noformat}

### Acceptance Criteria

* User can edit future academic years
* User can copy an academic year’s departments + benefits to another academic year
* Benefits work properly in application/survey workflows

---

## NXT-63753 — FH - FRE Apps - SSN question for Students at CEP Sites

- Resolved: 2025-07-08
- Status: Done Done
- Resolution: Done
- Components: Eligibility, Family Hub

### Description

*requirements*

* Update System Setting (FRENOSSN)
** Dropdown: On, Off (Default), Partial
** Description: Controls whether the applicant must answer / submit last-4 SSN as part of an online FRE application. Set this to Yes if this is mandatory for your state, or No to remove the question from the household application workflow. Set to Partial to remove the question if all students are at CEP schools.
* Add in a check for FRE Applications via Family Hub:
** All students on the FRE app are at CEP Sites
** Do not show / require the applicant to answer the Last-4 SSN / No SSN.
* Eligibility module:
** Text tied to No SSN should reflect as the alternate ‘No SSN or Not Applicable’ string.

### Acceptance Criteria

* System Setting adjusted
* If setting set to Partial:
** Verify: FRE Apps with all students at CEP Sites do not see the Last-4 SSN / No SSN question.
** Verify: FRE Image App available to the applicant does not show the Last-4 SSN / No SSN question.
** Verify: Eligibility module shows ‘No SSN or Not Applicable’

---

## NXT-60922 — Elig - Direct Certs - Remove 'Direct Certification' as an option for Manual Entry

- Resolved: 2025-06-10
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

[https://primeroedge.freshdesk.com/a/tickets/271984|https://primeroedge.freshdesk.com/a/tickets/271984] from Support

[https://primeroedge.freshdesk.com/a/tickets/271562|https://primeroedge.freshdesk.com/a/tickets/271562] Customer impacted

*requiremnents*

* Remove ‘Direct Certification’ from the dropdown if the user is doing Manual Entry.

!image-20250411-202522.png|width=1615,height=449,alt="image-20250411-202522.png"!

### Acceptance Criteria

* Option removed for Manual Entry
* Option remains for File Import

---

## NXT-60492 — Elig - Verification - QoL Updates, Include CEP Setting, Minnesota Reporting

- Resolved: 2025-06-10
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

Based on feedback from Support and Customer Tickets, some changes are needed for Verification next school year.

*requirements*

*Customer Feedback*

* Collection Report to export/print out in 1 download instead of requiring user to print page 1, then page 2.
* Retain user search options (Year, Sample Number, Tab, Pagination) when they come out of Verification Details → Tracking page.
* Collection Worksheet
** Column Headings that are tied to specified dates should include those dates 
*** ‘Number of Students’ → ‘Number of Students as of October 31’
*** ‘Number of Applications’ → Number of Applications as of October 1
*** We should reference the chosen dates from the Sample in case the user picked something different. This will also help some confusion.

!image-20250328-193734.png|width=703,height=121,alt="image-20250328-193734.png"!

*Include CEP Sites*

* Add a new setting:
** Name: Include Students from CEP Sites for Verification Reporting
** Category: Verification
** Module: Eligibility
** Common
** Setting values: Yes, No (Default)
** Description: If enabled, this setting will include students from CEP Sites for Section 3 and 4 of the Collection Worksheet. Normally these counts are excluded from this section of the report.
* If the setting is on, we need to include the CEP Sites rather than exclude them for sample creation and application random-select.
** Discussion on 6/2/25 → This is already happening, it is just the number of students that needs to be updated. We’re only including CEP sites, not P2 as part of this setting update.
* Sections 3 + 4 will need to be filled out for number of students.

*Specific Section for StateCode = MN, Minnesota*

* Collection Worksheet needs a new section, 4.1:
* Text: Check the box if you did not have any approved applications or you do not have any verification results to report.
* Checkbox - check it if Number of Approved Applications is 0.
** if 4.2a + 4.3a + 4.4a = 0 then check the box
* The existing section 4 needs to be incremented by 1. 4.1 → 4.2, 4.2 → 4.3, etc.

!image-20250328-193417.png|width=811,height=208,alt="image-20250328-193417.png"!

### Acceptance Criteria

* Collection Worksheet exports out in 1 print, not 2
* User retains search criteria when going from Verification Details → Tracking page
* Collection Worksheet gets specified date added to column headers
* ‘Include CEP Sites’ option added
** Sampling updated to include CEP sites for application #s and pool generation
** Worksheet updated to show counts
* Specific 4.1 section for Minnesota added

---

## NXT-60920 — FO - Print/Email - Messaging Update (FD #272290)

- Resolved: 2025-05-27
- Status: Done Done
- Resolution: Done
- Components: Account Management, Eligibility

### Description

[https://primeroedge.freshdesk.com/a/tickets/272290|https://primeroedge.freshdesk.com/a/tickets/272290]

*requirements*

* Add success messaging when using Email/Print
** Success message for both: Prints in progress, Emails sent successfully.
* Add success messages for Print options (Print All / Print Only)
** Success message: Prints are in progress.



!image-20250411-195817.png|width=1143,height=871,alt="image-20250411-195817.png"!

!image-20250411-195824.png|width=2232,height=1358,alt="image-20250411-195824.png"!

### Acceptance Criteria

* Messaging for Email/Print added
* Messaging for Print options added

---

## NXT-60490 — Elig - Applications - Privacy Act Statement - App Images, Field, Settings

- Resolved: 2025-05-12
- Status: Done Done
- Resolution: Done
- Components: Eligibility, Family Hub

### Description

As Dana the Director I need to have a Privacy Act displayed on the application image and right now there’s no way to do so.

*requirements*

* Add a new field to the Templates > Fields section
** Field Name: Privacy Act
** English text is below, we can use that to start any other language like we did with the disclaimer
* Add a setting to control displaying the Privacy Act and Disclaimer on application images
** Setting: Display Privacy Act and Disclaimer on Application Images
** Module: Eligibility
** Category: Applications
** Configuration: Common
** Values: On (default) / Off
** Description: This setting controls whether the Privacy Act and Non-Discrimination Statements are shown on application images. This includes the Eligibility module, but also on the Family Hub website.
* If the setting is on, we should include the two statements (both from Fields) in the Application Images.
** Location is shown below.
** This should update the application image across the Eligibility module
*** Application Details
*** Printing the application
** Also on Family Hub
*** We show the application image at the end of the workflow
*** Household can review these later



----

Privacy Act Default Text

{noformat}The Richard B. Russell National School Lunch Act requires the information on this application. You do not have to give the information, but if you do not, we cannot approve your child for free or reduced price meals. You must include the last four digits of the social security number of the adult household member who signs the application. The last four digits of the social security number is not required when you apply on behalf of a foster child or you list a Supplemental Nutrition Assistance Program (SNAP), Temporary Assistance for Needy Families (TANF) Program or Food Distribution Program on Indian Reservations (FDPIR) case number or other FDPIR identifier for your child or when you indicate that the adult household member signing the application does not have a social security number. We will use your information to determine if your child is eligible for free or reduced price meals, and for administration and enforcement of the lunch and breakfast programs. We MAY share your eligibility information with education, health, and nutrition programs to help them evaluate, fund, or determine benefits for their programs, auditors for program reviews, and law enforcement officials to help them look into violations of program rules.  {noformat}

----

Current Application Image + Proposed Positioning

!image-20250328-181541.png|width=703,height=925,alt="image-20250328-181541.png"!

* Add the Privacy Act and then the Disclaimer in a new section afterwards.
* If this is a 2nd page, that’s fine, but the Export/Print will need to handle it.

*Discussion 4/9/25 - Harsha, Haritha*

* This is moving back to the Templates > Fields page instead of Eligibility Descriptions.

### Acceptance Criteria

* New field added to Templates > Fields: Privacy Act
** User can edit it as needed
* New setting added
* If setting is on, Privacy Act and Disclaimer fields are shown on Application Images
** Visible for Family Hub also
** Application Details for Exports + Prints
*** Application Image
*** Application Image → Export, Print
*** Export

---

## NXT-59832 — DMF - Migrate Verification tables in Eligibility DB for Front office migration 

- Resolved: 2025-04-23
- Status: Done Done
- Resolution: Done
- Components: Eligibility, Platform - Data Exchange

### Description

As a District migration User, I want to do the migration for the Front office in the destination Eligibility DB. 

Need to migrate the below Verfication tables data from source to destination. 

* VER_Verification
* VER_VerificationSample
* VER_VerificationReset

To achieve this, Front office team needs to provide an API end point that will look up data that needs to migrated and inserts/updates data  to the above tables

Data exchange team will integrate the end point provided in ADF in District migration for Front office destination.

### Acceptance Criteria

* End point to look up, insert/update to verificaction related tables in Elig DB
* Integrate API into ADF in Front office destination migration 
* Validate the data got migrated successfully for Verification

---

## NXT-58224 — FO - Datasets - Eligibility - Direct Certification

- Resolved: 2025-04-23
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

As Dana the Director I need to create some custom reporting based on DC data, and need data fields made available for this.

*requirements*

Add the following dataset for Eligibility > Direct Cert

* Dataset Name: Elig - Direct Cert.
* Data Columns:
** Student ID
** Student First Name
** Student Last Name
** File #
** Academic Year
** Import Date
** Processed Date
** Notification Date
** Approval Date
** Eligibility Start Date
** Eligibility End Date
** Processor Name
** Eligibility
** DC Type
** Entry Method
** Student School Name
** Student Site Code
** Student Grade
** Student Language
** Guardian Name
** Guardian Address
** Guardian Home Phone
** Guardian Cell Phone
** Household PIN
** Current Eligibility
** Prior Eligibility
** Case Number
** Match Method
** Extension Source
** Extension Criteria

### Acceptance Criteria

* Dataset added, available for Custom Reports

---

## NXT-60134 — Elig - Reports - Surveys - Remove the Eco Dis % report from the Surveys report

- Resolved: 2025-04-11
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

As Dana the Director I see two Economically Disadvantaged reports when I have income surveys turned on and that’s confusing.

*requirements*

* Remove the Eco DIsadvantaged % option from the Surveys report
* Income Range report is always available
* Update the text on the reports landing page - no need to change the text based on the Survey setting.
** OLD: {{Provides the percentage of economically disadvantaged students, as well as the number of surveys broken down by household size and income data.}}
** NEW: {{Data on the number of surveys broken down by household size and income data.}}

### Acceptance Criteria

* Eco Dis % report removed as an option in the Surveys report page.
* Income Range report is always available
* Eligibility Reports landing page text updated.

---

## NXT-58190 — FO - Datasets - Eligibility - Applications

- Resolved: 2025-04-09
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

As Dana the Director I need to create some custom reporting based on application data, and need data fields made available for this.

*requirements*

Add the following dataset for Eligibility > Applications

* Dataset Name: Elig - Applications
* Data Columns:
** Application #
** Academic Year
** Received Date
** Processed Date
*** Latest only
** Notification Date
*** Latest only
** Processor Name
** Application Status
** Application Eligibility
** Application Basis
** Entry Method
** Student Names
** Student IDs
** Student School Names
** Student Site Codes
** Student Grades
** Benefits
** Info Sharing
** Included for Verification
** Error Prone
** Household Size
** Household Income
*** Include Frequency
** Applicant Name
** Applicant Home Phone
** Applicant Cell Phone
** Applicant Email
** Applicant Address
** Ethnicity
** Racial Identity
** Language
** Pending Reasons

*Discussion Notes*

* 1 row per application
* keep student data merged into 1 cell

### Acceptance Criteria

* Dataset added, available for Custom Reports

---

## NXT-58222 — FO - Datasets - Eligibility - Surveys

- Resolved: 2025-03-31
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

As Dana the Director I need to create some custom reporting based on survey data, and need data fields made available for this.

*requirements*

Add the following dataset for Eligibility > Surveys

* Dataset Name: Elig - Surveys
* Data Columns:
** Survey #
** Academic Year
** Received Date
** Processed Date
** Notification Date
** Processor Name
** Survey Status
** Survey Eligibility
** Survey Reason
** Entry Method
** Student Names
** Student IDs
** Student School Names
** Student Site Codes
** Student Grades
** Benefits
** Info Sharing
** Household Size
** Household Income Range
** Applicant Name
** Applicant Home Phone
** Applicant Cell Phone
** Applicant Email
** Applicant Address
** Language

### Acceptance Criteria

* Dataset added, available for Custom Reports

---

## NXT-58537 — Upgrade all Frontoffice Modules to .Net 8.0

- Resolved: 2025-03-24
- Status: Done Done
- Resolution: Done
- Components: Accountability, Account Management, Eligibility, Family Hub

### Acceptance Criteria

Upgrade all the modules to .net core 8.0 (including supporting applications as well). Also upgrade all the platform packages to latest version

---

## NXT-27577 — Family Hub - School Menus - Get display order for each menu published from SchoolCafé

- Resolved: 2025-02-24
- Status: Done Done
- Resolution: Done
- Components: Eligibility, Family Hub

### Description

As a district menu planner, I would like every menu published to the Family Hub to display to users in a specific order, so that I can make sure that Family Hub users see the most relevant menu line info first (rather than the first alphabetical line in the list).

*Summary*

A leftover request that we never got around to implementing in Classic. Menu Line display order was not being respected when a user viewed the published menu: (Mockup shows Classic but is scenario is valid in 2.0 SC as well)

!Screen Shot 2022-02-25 at 2.46.31 PM.png|width=718,height=592!

*Details*  

In SchoolCafé → Menu Planning → Settings → Menu Lines, each menu line has a corresponding display order value. Verify that this value is being sent down to the Family Hub, so that: 

* when the user goes to the School Menus page, the default serving line and menu loaded is the line with display order #1 as indicated in SchoolCafé
* when the user selects that drop-down for line/serving line: the remaining options are listed in the same display order configured in SchoolCafé

### Acceptance Criteria

Verify that SchoolCafé display order for a menu’s serving lines is being respected in the Family Hub for both the default serving line and the list of serving lines when the menu is published

Verify that these are updated in Family Hub when the menus are republished

---

## NXT-55697 — Elig - Application processing on same day as Carryover Expiration and Adverse Action

- Resolved: 2025-02-12
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

!image-20241010-192240.png|width=1166,height=270,alt="image-20241010-192240.png"!

Scenario 1

* Not checking future eligibility while processing apps
** Student’s Carryover expired 9/25
** New Paid (Default) record was due to start on 9/26
*** Student is still Free (Carryover) on 9/25
** Application came in and was processed on 9/25
*** Student would move to Reduced (Income)
** Adverse action check happened
*** Student currently is Free, moving to Reduced
** Reduced (Income) was moved out 10 days, which extended Paid (Default) until then.
* Expected outcome
** Student goes from Free (Carryover) to Reduced on 10/05 due to adverse action
** Paid (Default) record is made inactive

Scenario 2

* Adverse action may push the end of carryover out
** Carryover ends on 9/25
** Application processed on 9/23
** 10 adverse action days → new eligibility doesn’t start until 10/03 which is beyond the end of carryover.
* Expected outcome
** Well, depends on the setting for starters
*** If Adverse Action during Carryover is on, then go with the 10 adverse action days and push carryover out
*** If it’s off, then there’s no adverse action - immediate change next day for reduction of benefits.
** Let’s add a secondary setting for this to let districts have more nuanced control:
*** Setting: Adverse Action Extends Carryover Dates
**** Options: Yes, No (default)
**** Description: This setting applies if setting ‘Carryover (Grace Period) - Include Adverse Action Days for Carryover Students (ADACDUGRCP)’ is on. If both are enabled, then Carryover dates may be extended if a reduction in benefits happens within 10 days of the Carryover expiration date. 
**** Internal setting



*Discussion Notes at Refinement (10/15/24)*

* Matt to put together a matrix of scenarios for how this all interacts.
* This will have no impact on manual editing of eligibility via Account Management.

### Acceptance Criteria

* Scenario 1
** Future eligibility is taken into account when determining eligibility, and if adverse action should apply
* Scenario 2
** Secondary setting added to control whether adverse action can extend Carryover if the original setting is turned on

---

## NXT-54190 — Elig - Forms - Applicant Information column, filters (FD: 254416)

- Resolved: 2025-02-12
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

[https://primeroedge.freshdesk.com/a/tickets/254416|https://primeroedge.freshdesk.com/a/tickets/254416]

*requirements*

Forms pages - Applications, Surveys

* Add Applicant Contact Info as 3 new columns
** Show the applicant’s contact info from the form data: 
*** Applicant Phone #, Applicant Email, Applicant Address
**** Leave blank if no data to show
** For custom views, hidden by default
* Add search filter to the new columns, no sorting required

### Acceptance Criteria

* New columns added → Applicant Phone #, Applicant Email, Applicant Address
* New columns have search
* Not shown by default re: custom views

---

## NXT-56345 — Elig - Summary Report - Detailed option to include all price type reasons (FD 265473)

- Resolved: 2025-02-11
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

[https://primeroedge.freshdesk.com/a/tickets/265473|https://primeroedge.freshdesk.com/a/tickets/265473]

As Dana the Director I need to see specifics on how many students are each basis/pricetype reason, for each site, and the current Eligibility Summary report doesn’t quite get me there.



!image-20241101-191641.png|width=869,height=285,alt="image-20241101-191641.png"!

*requirements*

* Add a ‘Compact’ and ‘Detailed’ option to the Summary report.
** Compact → Existing report
** Detailed → Put in every single price type reason instead of merging some together under ‘DC’ or ‘Other’
* This will also need to be done for the Include Percentages option. (Discussion 01/21/25)

### Acceptance Criteria

* ‘Detailed’ version added that includes all price type start reasons
* ‘Compact’ version available - the current report
* User can choose between both formats

---

## NXT-56318 — Elig - Eligibility Change Report (FD 265260)

- Resolved: 2025-02-03
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

As Dana the Director I want a way to see eligibility changes by date so we can perform outreach to encourage participation / application submission.



*requirements*

* New Report for Eligibility:
** Name: Eligibility Status Changes
** Search filters:
*** Site picker, multi-select
*** Date picker
**** use the new date range selector from the Workspace Dashboard page
*** Patron Status
**** Active (Default)/Inactive/All
** Report options:
*** Only show Last Eligibility Change (Checkbox, unchecked by default - Matt may still need to change the label on this still)
**** If enabled, results will only show 1 eligibility change per account, not all changes over the timeframe
** Standard Reset and Apply buttons
** No search on page load
** Server side filtering/sorting
* Description for the reports landing page:
** Shows changes in student eligibility with a variety of search filters.
* Search is looking for students who have experienced a change in eligibility on/during the selected date range.
** Inactive eligibility lines will NOT be shown in the results
* Grid report, columns:
** ID # (F)
** First Name (F)
** Last Name (F)
** Grade (F)
** Site
** Patron Status
*** Active/Inactive based on account status
** Prior Eligibility (F)
** New Eligibility (F)
** Effective Date (F) (Default sort, oldest first)
*** This is the new eligibility start date
** Process Date 
** Email (F)
** Address (F)
** Phone Number (F)
* Export to Excel option
* Filter on the columns marked with an F above
* Custom views framework should be applied
** Default view columns: ID #, First Name, Last Name, Grade, Site, Prior Eligibility, New Eligibility, Effective Date, Process Date
* Text on the page:
** Full text to be added
*** Instructions: date range is related to the Process Date 
*** notes: Inactive eligibility lines are not shown, Grade/Site/Status are live data and not historical



||*First Name*||*Last Name*||*Grade*||*Site*||*Prior Eligibility*||*New Eligibility*||*Effective Date*||*Email*||*Address*||*Phone Number*||
|Matthew|Smithers|10|101 - ABC High|Free (Carryover)|Paid (Default)|09/25/2024|m@s.com|123 Fake St, Faketown 77375|(111) 222-3333|

PE Screenshots for reference:

!image-20241031-200433.png|width=1732,height=922,alt="image-20241031-200433.png"!

!image-20241031-200445.png|width=1330,height=758,alt="image-20241031-200445.png"!

*Notes at mini-demo (1/27/25)*

* Add full timestamp for Process Date
* Add Student ID column (F)

### Acceptance Criteria

* Status Change report page added to Eligibility Reports Landing page
* Status Change report added
* Search options for site, date
* Grid results
* Grid can be downloaded
* Certain columns have filters
* Manage Views added also

---

## NXT-56281 — Elig - Scheduler framework update for Verification Auto-Notify

- Resolved: 2025-01-28
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

* Add the Scheduler framework done for Reminder Letters for the following areas:
** Verification Follow-Up Notice (Auto-Notify on the Tracking page)
* Same functionality for the most part.
** User can edit the frequency, status.
** User can see history of when it was sent, and who it was sent for.
* Add or use the new page for showing these in Eligibility:
** Notifications → Recurring Notices



Notes for the specific “jobs”

* Verification Auto-Notify
** Master jobs created, set to run every 3 days by default for timeframe of 07/01 to12/01 each year.
** User can only edit the frequency, and the status.
** Would be very nice if toggling the Auto-Notify setting on the Tracking page updated the job frequency.
*** If this proves difficult - remove from the Tracking page.
** Explanatory note:
*** This job will automatically send follow-up notices to households every X number of days to help remind them that they need to respond to selection. The number of days between reminders can be adjusted. It will send the follow-up notice X number of days after the last reminder.

### Acceptance Criteria

* Recurring Notices tab added to Eligibility > Notifications
* Verification Auto-Notify moved over
** Master job(s) created
** Toggle on the Tracking page updates the Job re: Status and frequency days
* Notifications send automatically if enabled
* User can see history of sends, who received, look at the letter, same as Reminders
* Scripts ready to update this new job to use the same values as the current configuration
** User should not need to go in and configure these jobs

---

## NXT-55588 — Elig - Scheduler framework update for Automatic DC Notifications

- Resolved: 2025-01-28
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

* Add the Scheduler framework done for Reminder Letters for the following areas:
** Automatic DC Notifications
* Same functionality for the most part.
** User can edit the status.
** User can see history of when it was sent, and who it was sent for.
* New page for showing these in Eligibility can be located here:
** Notifications → Recurring Notices



Auto DC Notifications AUTODCNTFY  (every day 6 PM & checking past 7 days)


Notes for the specific “jobs”

* Automatic DC Notifications
** Master job created, set to run at 6pm local time.
** System Setting can be removed as part of this.
*** AUTODCNTFY
** Districts that have the setting turned on need to have the job set to status = active.
** Need an explanatory note for the job:
*** This job will automatically send an approval notice to primary guardians after any successful Direct Certification matches are processed. Potential Matches are included upon approval. DC Extensions are not included in this automation feature. The automatic notification letters will be sent at 6 PM daily.
** User can only edit whether this job is active or inactive.
* Post-deployment scripts need to be ready to configure this job to match the district’s current settings.

### Acceptance Criteria

* Recurring Notices tab added to Eligibility > Notifications
* Automatic DC Notifications moved over
** Master job created
** Setting removed
** Scripts ready to move districts with the setting set to Yes to have the job set to Active
* Notifications send automatically if enabled
* User can see history of sends, who received, look at the letter, same as Reminders
* Scripts ready to update the new job to use the same values as the system settings we are removing
** User should not need to go in and configure these jobs

---

## NXT-58191 — FO - Datasets - AcctMgt_StudentData - New columns (FD: 268513)

- Resolved: 2025-01-20
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

[https://primeroedge.freshdesk.com/a/tickets/268513|https://primeroedge.freshdesk.com/a/tickets/268513]

As Dana the Director I need a daily export of student data and the current dataset is missing a couple pieces of data.

*requirements*

Add the following columns to the existing dataset: AcctMgt_StudentData

* New Data Columns:
** Eligibility Process Date
*** This should be the date the eligibility line was created, which should be the same as the date the application or dc data was processed.

### Acceptance Criteria

* Dataset updated to have the new column

---

## NXT-55012 — Elig - Notifications - Carryover to show Active students only (FD: 259884)

- Resolved: 2025-01-14
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

[https://primeroedge.freshdesk.com/a/tickets/259884|https://primeroedge.freshdesk.com/a/tickets/259884]

Carryover Notifications are being sent to inactive students.

*requirements*

* Only show Active students in the carryover search results.
* Only send to Active students.

### Acceptance Criteria

* Carryover letters are only sent to Active students.

---

## NXT-54189 — Elig - Notifications (Apps/Surveys) - Search filters on columns, Student ID # field (FD 256633)

- Resolved: 2025-01-06
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

[https://primeroedge.freshdesk.com/a/tickets/256633|https://primeroedge.freshdesk.com/a/tickets/256633]

*requirements*

* For both Applications and Surveys
** Add a new column
*** Student ID #
**** Show the student ID numbers of the students on the applications
***** Get the actual matched ID number if possible
**** Searchable / filterable
**** Make it a default column for Custom Views

!image-20240826-151829.png|width=183,height=475,alt="image-20240826-151829.png"!



!image-20241118-150823.png|width=151,height=179,alt="image-20241118-150823.png"!

### Acceptance Criteria

* New column added → Student ID
* Search filters added

---

## NXT-54692 — FO - Grids - Manage Views - Enable the Save View options (FD #260053, 260382)

- Resolved: 2024-12-02
- Status: Done Done
- Resolution: Done
- Components: Accountability, Account Management, Eligibility

### Description

FD: [https://primeroedge.freshdesk.com/a/tickets/260053|https://primeroedge.freshdesk.com/a/tickets/260053], [https://primeroedge.freshdesk.com/a/tickets/260382|https://primeroedge.freshdesk.com/a/tickets/260382]

* Enable the ‘Save View’ feature on the Manage Views button for the following pages:
** Eligibility
*** DC → Potential Matches
*** Reports → Roster
** Accountability
*** Deposits
** AcctMgt
*** Notifications → Household Letters
* Update existing Manage View grids to not save search parameters. (See the Sessions page)
* See if we can block ‘Actions’ or remove as a Manage View option - needs to always be on.
** We also have a scenario where the checkboxes (see Sessions grid) can be removed - this also needs to always be on.
* -Potentially: Update to the new Manage Views buttons with the show/hide filter options.-



!image-20240908-172311.png|width=1987,height=790,alt="image-20240908-172311.png"!



!image-20240908-172555.png|width=639,height=264,alt="image-20240908-172555.png"!



!image-20241002-142831.png|width=1566,height=872,alt="image-20241002-142831.png"!



!image-20241002-143106.png|width=1490,height=640,alt="image-20241002-143106.png"!

### Acceptance Criteria

* Update FO Manage Views to not save search criteria, only columns
* Actions column should always be on - user cannot turn it off
* Enable ‘Save View’ feature on these pages:
** Eligibility
*** DC → Potential Matches
*** Reports → Roster
** Accountability
*** Deposits
** AcctMgt
*** Notifications → Household Letters
* See if we can diagnose why the checkbox disappears on pages like Sessions, Household Letters
** Fix if possible, bug for System/Platform otherwise

---

## NXT-54816 — Elig - Applications - Use all Pending Reasons for Online Apps (FD: 254409)

- Resolved: 2024-11-19
- Status: Done Done
- Resolution: Done
- Components: Eligibility, Family Hub

### Description

As Dana the Director I want to see the actual pending reason for online applications so I can make a quick, informed decision on keeping/deleting the app. 

Currently all online apps are using the ‘duplicate info’ reason - we have ~13 pending reasons, we should use them.

Also the Reason column on the Pending Apps tab is not showing that reason, so we’ll check that as well.

!image-20240913-150713.png|width=614,height=526,alt="image-20240913-150713.png"!

*requirements*

* Online applications make use of the full range of Pending Application reasons. Criteria below.
* User sees more information as part of this:
** If it’s a duplicate app, mention the other app # and the approval date.
** If the students are DC, show the dc file # and process date.
* All pending reasons applied to an application should show in the Pending Applications grid.
** We’re only showing the Pending Reason in the grid - the additional information is only in Application Details.



!image-20240913-164247.png|width=554,height=329,alt="image-20240913-164247.png"!



*pending reasons*

* All students are at CEP Sites
** Criteria: All identified students are at a CEP Site
** Additional text: None
* All students are directly certified
** Criteria: All students on the app have DC Basis reasons
** Additional text: Student #12345 received benefits from File #123, processed on 9/13/24. Student #22344 received benefits from File #98, processed on 9/13/24.
*** File # should be a link to open up that DC file in a new tab.
* Applicant and student with the same name
** Criteria: 1 student + Applicant have the same firstname and lastname
** Additional text: N/A
* Duplicate application
** Another application with the same data has been submitted.
** Additional text: Application #12345, #55444, #15224.
*** App # should be a link to open up that DC file in a new tab.
* Foster Child Application with multiple students listed
** Criteria: 1 student is Foster, the others are not
** Additional text: Foster Student(s): #12345, #55222
* Incomplete
** Not possible with online apps
* Incorrect categorical information
** Not possible with online apps
* Incorrect income information
** Not possible with online apps
* Missing household members
** Not possible with online apps
* Missing PFD information
** Not possible with online apps
* No signature
** Not possible with online apps
* Online Application: Unmatched student
** Criteria: Need to check the system setting ONLAPPROCE
*** If the setting is set to Only If All Students Are Identified:
**** 1 pending student, use the Pending reason, park as pending
*** If the setting is set to Only If At Least 1 Student Is Identified:
**** If all students are pending, use the pending reason, park app as pending
** Additional text: N/A
* Possible duplicate information
** Criteria: Same student name or ID entered multiple times
** Additional text: N/A





!image-20240913-164633.png|width=1080,height=381,alt="image-20240913-164633.png"!

### Acceptance Criteria

* Pending Apps grid shows all pending reasons applied to an application.
* Online App submission applies pending reasons based on criteria.
* Additional information shown in Application Details for pending reasons where outlined in requirements.

---

## NXT-56185 — Elig/System - Remove the DCMCHSTUID system setting

- Resolved: 2024-11-15
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

Remove the following setting:

* DC Matching - Match Student ID against DC File SSN 
* Code: DCMCHSTUID
* Description: This will match the student ID (from Student Details) against the SSN on the DC file, potentially forcing a guaranteed match if the points are high enough in DC Match Configuration. This should only be set if the DC file you are importing is actually a list of Student ID Numbers, and not an actual DC file from your state department.

### Acceptance Criteria

* Setting DCMCHSTUID removed.

---

## NXT-53570 — AcctMgt/System - Random PINs for Imports (FD: #251615)

- Resolved: 2024-10-31
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

[https://primeroedgenext.atlassian.net/browse/PCS-3883|https://primeroedgenext.atlassian.net/browse/PCS-3883|smart-link] 

[https://primeroedge.freshdesk.com/a/tickets/251615|https://primeroedge.freshdesk.com/a/tickets/251615]

As Dana the Director I want the system to apply random PIN numbers to accounts as they are imported.

*requirements*

* User has a page to configure Random PIN number ranges
** User can set the range for Students and Adults separately
*** Minimum value, maximum value
** There can be no overlap between the two, user needs an error message:
*** Text: PIN # range overlaps between Students and Adults.
** User can see the PINLENGTH value on the page.
** User can see who last updated the range settings
* Check the PINLENGTH setting as part of saving the PIN Number ranges
** Example:
*** Staff PIN Type = Random Pin
*** PINLENGTH = 6
*** Minimum Value for Adults = 400000
*** Maximum Value for Adults = 600000
*** Randomly generated numbers for adults would be between 400000 - 600000, and must be unique for the district/region’s active accounts. No duplicates allowed.
*** New page should also error if the user tries to set a 
** Min/Max Values must not overlap between Adults and Students.
* Imports need to be updated to check the Staff PIN and Student PIN settings, and if they’re Random PIN, apply randomly generated pins on new account creation.
* Update the PINLENGTH system setting to be a dropdown with value range: 1 - 12

!image-20240306-212834.png|width=50%!



*Discussion 8/27/24*

* Need a full configuration page for this
* Page will be added to Account Management
* Matt to provide a basic mockup for it
* Story to be moved to next sprint



*Basic mockup added 9/4/24:*

* Add a Settings/Tools nav section to Account Management
* Move System Settings under it
* Add the PIN Number Settings page

!image-20240904-162310.png|width=1798,height=403,alt="image-20240904-162310.png"!

Text for the page: {{This page controls the PIN Number ranges used if Random PINs need to be generated. This is controlled on the System > Settings page. Random PINs can be enabled for Students and/or Adults. The PIN Length can also be configured there.}}

Discussion 9/17/24 re: Scope

Team has discovered that the import side is missing PIN as a field for adults/employee imports. Platform team to add for File Import only.

* Students - API + File Import
* Adults/Employees - File Import only

### Acceptance Criteria

* Settings/Tools side-nav section added to Account Management
** Move the link to System Settings into this
* New page added under the Settings/Tools side-nav 
** PIN Number Settings
* User can set MIN and MAX value ranges for PIN #s for Adults.
* User can set MIN and MAX value ranges for PIN #s for Students.
* User can see who last edited the values and when.
* Account Creation (Imports, Add New Accounts, Editing Account Details) updated to check the PIN Type settings for both Adults and Students.
** If Random PIN, use the min/max values to apply a unique random pin on account creation.
** No duplicate PIN numbers allowed in the same region.
** If a PIN number exists we are not updating it.
** If the user removes a PIN (leaves it blank) and tries to Save, then we’ll generate a new PIN following the setting guidelines.

---

## NXT-55590 — Elig/System - DC Matching - Default system setting for Student ID against SSN

- Resolved: 2024-10-23
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

Change default setting of DC Matching - Match Student ID against DC File SSN DCMCHSTUID to 0

* Change default setting value to 0:
* Change the description: This will match the student ID (from Student Details) against the SSN on the DC file, potentially forcing a guaranteed match if the points are high enough in DC Match Configuration. This should only be set if the DC file you are importing is actually a list of Student ID Numbers, and not an actual DC file from your state department.

### Acceptance Criteria

* Setting DCMCHSTUID default value updated to 0.
* Updated description

---

## NXT-55413 — Sys - Templates - Language usage for Fields - Carryover Expiration + Correction Letter

- Resolved: 2024-10-23
- Status: Done Done
- Resolution: Done
- Components: Account Management, Eligibility

### Description

As Dana the Director I want to see fields on letter templates pull the appropriate language translation. Right now, all fields are returning english values only.

*requirements*

* Update Carryover Expiration Letter to check and use language fields when generating letters
** 1 field (Current Status)
* Update Correction Letter to check and use language fields when generating letters
** 2 fields (Current Status and Previous Statius)

### Acceptance Criteria

* Carryover Expiration Letter updated to check and use specific language fields instead of just English
* Correction Letter updated to check and use specific language fields instead of just English

---

## NXT-54075 — Elig - Potential Matches - Option to hide lesser matches (FD 255896)

- Resolved: 2024-10-02
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

[https://primeroedge.freshdesk.com/a/tickets/255896|https://primeroedge.freshdesk.com/a/tickets/255896]



!image-20240820-200346.png|width=1049,height=708,alt="image-20240820-200346.png"!

*requirements*

* Potential Matches page
** Add an option to the Potential Matches page:
*** Show Same/Lesser Benefits → Off by default
*** Add an info icon to explain the toggle, text: This option will include potential matches that are the same DC Type (Example: SNAP to SNAP) and potentially for lower-level benefit programs (Example: SNAP to TANF).
** Toggle behavior:
*** Off → Hide any potential matches that have the same DC Type or lower on the DC Precedence List
*** On → Show the potential matches that have the same DC Type or lower on the DC Precedence List
* Update the Eligibility Dashboard Potential Matches CTA to show the same number as if the toggle was off.

*Discussion Notes*

* We don’t want to offer a reduction in benefits (Free → Reduced) UNLESS the student is currently on Carryover or CEP Transfer.

### Acceptance Criteria

* Potential Matches page
** Show Same/Lesser Benefits toggle added to the page
** Info icon + tooltip added
** Impacts search results in the grid:
*** Off (default) → Do not show same DC Type or lower on the DC Precedence List
*** On → Show same DC Type or lower from DC Precedence
* Eligibility Dashboard
** Potential Matches CTA updates so the count is the same as the page with the option set to Off

---

## NXT-53985 — Sys - Templates - Language usage for Fields - Direct Certification

- Resolved: 2024-09-16
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

As Dana the Director I want to see fields on letter templates pull the appropriate language translation. Right now, all fields are returning english values only.

*requirements*

* Update Direct Certification Letter to check and use language fields when generating letters

### Acceptance Criteria

* Direct Certification Letter updated to check and use specific language fields instead of just English

---

## NXT-53984 — Sys - Templates - Language usage for Fields - Direct Approval

- Resolved: 2024-09-16
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

As Dana the Director I want to see fields on letter templates pull the appropriate language translation. Right now, all fields are returning english values only.

*requirements*

* Update Direct Approval Letter to check and use language fields when generating letters

### Acceptance Criteria

* Direct Approval Letter updated to check and use specific language fields instead of just English

---

## NXT-49465 — FO - Document Center - Update Verification letters to use background process

- Resolved: 2024-09-16
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

As Dora the Director I want all letters in a single location for easier handling and downloading.

*mockup*

n/a

*requirements*

* Update letters out of Verification to use the background process (more than 20 letters)
** 5 different letters, including the Tracking Forms page
* If the background process is triggered, use the updated workflow set in an earlier story.
** User is informed that their documents are processing and to check the Document Center.
** User is informed (email/workspace notification) when the print job is ready.
** User can nav to the Document Center and see the print job + download 1 file for all letters involved.

### Acceptance Criteria

* Verification pages updated to use the same background processing workflow for letters.
** >20 letters, background process triggers.
* User can download their file from the Document Center (DC).
** Tie into existing workflow: User is informed that they can collect their letters from the DC page, email/inbox msg when print is ready.
** DC link button added to the Verification pages → Tracking, Reporting (Tracking Forms)

---

## NXT-53414 — Elig - DC Precedence - Merge tables, label updates

- Resolved: 2024-08-30
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

As Dana the Director I want to configure my DC Precedence to match my state and that may mean moving an Other Source Categorical up over a Direct Cert.

!image-20240730-214339.png|width=1291,height=1118,alt="image-20240730-214339.png"!



*requirements*

* Combine the Assistance Program and Other Source Categorical tables into 1 table.
** Leave Reduced by itself
** Name of new table: Assistance & Other Source Categorical Programs
* User can change precedence order across all of them.
** Give the user a confirmation prompt when saving the tables.
*** Text: 
{noformat}Changes here will impact future Direct Certification matching. Please ensure the precedence order is correct before saving.

CANCEL / CONFIRM{noformat}

* Add text to the top of the page to explain to the user what the page is for and what their impact will be:
** Text: 
{noformat}This page controls the precedence order for Direct Cert. or Other Source Categorical benefits. The order ensures that students receive the highest possible benefits during automatic matching. Any changes you make here will impact future Direct Cert. matching.{noformat}
* Add new columns to the table:
** Type
*** Show ‘Assistance Program’ for DC SNAP, DC TANF, DC FDPIR, DC Medicaid (Free) and DC Foster. Show ‘Other Source Categorical Program’ for the remainder.
** Eligibility
*** Free
** Extensions Allowed
*** Yes for DC SNAP, DC TANF, DC FDPIR, DC Medicaid (Free), No for everything else
* Add new columns to the Reduced table:
** Type
*** Assistance Program for DCMA Reduced. 
*** Other Source Categorical Program for Pre-K.
** Eligibility
*** Reduced
** Extensions Allowed
*** Yes for DC Medicaid (Reduced), No for everything else

### Acceptance Criteria

* Assistance Programs and Other Source Categorical tables merged
** Table label updated
* Columns added to both tables:
** Type, Eligibility, Extensions Allowed
*** Type: Assistance Program or Other Source Categorical Program
*** Eligibility: Free or Reduced
*** Extensions Allowed: Yes or No
* Confirmation prompt when saving the edits added
* Explanation text added above the grids

---

## NXT-53982 — Sys - Templates - Language usage for Fields - Approval/Denial Letter

- Resolved: 2024-08-21
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

As Dana the Director I want to see fields on letter templates pull the appropriate language translation. Right now, all fields are returning english values only.

*requirements*

* Update Approval/Denial Letter to check and use language fields when generating letters

### Acceptance Criteria

* Approval/Denial Letter updated to check and use specific language fields instead of just English

---

## NXT-53571 — FH - Applications - Controls for required fields on applicant data (FD: 253686)

- Resolved: 2024-08-12
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

Freshdesk ticket - [https://primeroedge.freshdesk.com/a/tickets/253686|https://primeroedge.freshdesk.com/a/tickets/253686|smart-link] 

As Dana the Director I need certain applicant fields to be optional to get state approval for online applications.

*requirements*

* Add District Settings for Online FRE Apps (and Surveys) to control the email and phone # fields being required.
** Setting Name: Applicant Phone Number Required
*** Default: On
*** Tooltip: This controls whether the applicant must enter a phone number when submitting an FRE Application or an Income Survey.
** Setting Name: Applicant Email Required
*** Default: On
*** Tooltip: This controls whether the applicant must enter an email address when submitting an FRE Application or an Income Survey.
* If the settings are off - the fields are not mandatory and an app can be submitted without them.
* For guest applicants who are not logged in - add a confirmation prompt if both settings are off and the Email and Phone fields are left blank:
** Text: {{If you do not enter an email or phone number, you will not receive status notifications for this application. Do you want to proceed?}}
* Do not update user profiles as part of Applicant Info updates. 
** Keep the user profile separate from the application info.
** We don’t need to check settings for this - do not perform the update.





!image-20240807-131159.png|width=1099,height=850,alt="image-20240807-131159.png"!

### Acceptance Criteria

* Two new district settings added
* Application/Survey workflow updated to check the settings and allow submission if settings are set to no and fields are blank
* Guest applicants get a confirmation prompt if they leave both fields blank
* Updating Applicant Info does not update User Profile

---

## NXT-52656 — AcctMgt - Reminders - Preview Letter option, select checkboxes

- Resolved: 2024-08-09
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

!image-20240714-164056.png|width=1046,height=315,alt="image-20240714-164056.png"!

!image-20240714-164141.png|width=1057,height=133,alt="image-20240714-164141.png"!

*requirements*

* Move the checkbox to first column
* Add View feature from other notification pages
** Loads a preview of the letter that will be sent
* Default number of results in the grid updated from 5 → 10

### Acceptance Criteria

* Checkbox column moved to 1st column
* View feature added, user can preview the letter
* Default number of results in Reminders grid changed from 5 to 10

---

## NXT-52864 — FH - Online Apps - Mandatory SSN Controls

- Resolved: 2024-08-07
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

MN rolled out a new FRE Alternative App that is 99% an FRE App but requires no SSN question.

Since they are required to perform Verification on these, updating the FRE App instead of Income Surveys is the better route.

Freshdesk ticket: [https://primeroedge.freshdesk.com/a/tickets/251217|https://primeroedge.freshdesk.com/a/tickets/251217]

*requirements*

* Add a system setting for controlling the SSN field for FRE Applications.
** Setting name: FRE Applications - Applicant SSN Question Required
** Options: Yes/No
** Default: Yes
** External Setting
** Setting Code: FRENOSSN
** Description: Controls whether the applicant must answer / submit last-4 SSN as part of an online FRE application. Set this to Yes if this is mandatory for your state, or No to remove the question from the household application workflow.
* If the setting is set to Yes, current functionality persists.
* If the setting is set to No:
** Family Portal FRE Application
*** The question should be removed from the FRE Application
**** Applicant does not see it or have to answer it.
**** Applicant can submit the app without answering it.
*** Application Image
**** Last-4 SSN / No SSN field not visible.
**** Text block re: applicant’s SSN not visible.
** Eligibility Module
*** No SSN text on FRE Apps should be updated to:
**** No SSN or Not Applicable
*** Cannot edit the ‘No SSN or Not Applicable’ option
*** Submitted application should have this checkbox enabled as the SSN was Not Applicable.
*** Application Image
**** Last-4 SSN / No SSN Field not visible.
**** Text block re: last-4 SSN of the applicant also not visible.
*** Manual Entry
**** Last-4 SSN / No SSN text updated
**** Nice to have: already checked as No SSN / Not Applicable and user cannot uncheck it.







!image-20240722-213239.png|width=927,height=302,alt="image-20240722-213239.png"!



!image-20240722-213342.png|width=491,height=622,alt="image-20240722-213342.png"!

!image-20240725-151541.png|width=320,height=34,alt="image-20240725-151541.png"!



!image-20240722-213541.png|width=472,height=119,alt="image-20240722-213541.png"!

!image-20240722-213634.png|width=254,height=158,alt="image-20240722-213634.png"!



!image-20240723-131547.png|width=774,height=311,alt="image-20240723-131547.png"!

### Acceptance Criteria

* System Setting added
* FRE Application submission workflow updated if the new Setting is set to No
** Family Hub:
*** SSN question is not visible or required while submitting app
*** Applicant can submit an app without answering it
*** App Image does not show the Last-4 SSN / No SSN sections and the text block next to it
** Eligibility module:
*** Eligibility module shows ‘No SSN or Not Applicable’ as the option and it is checked
**** This cannot be adjusted while editing the application.
*** App Image does not show the Last-4 SSN / No SSN field and the text block to the left of it.

---

## NXT-49684 — FO - Document Center - Workflow update for Notifications > Direct Cert

- Resolved: 2024-08-07
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

As Dora the Director I want all letters in a single location for easier handling and downloading.

*mockup*

n/a

*requirements*

* Update the page workflow for Notifications > Direct Certification.
** Add a link to the Documents Center on the pages listed above.
** User should have a Back button to take them back to the page they were just on.
** If the user prints and it has to go to background processing (and become available at the Documents Center), inform them:
*** Text: Printing is in progress. Visit the Documents Center to download once it is ready.
** Remove any ‘download last generated’ bits from the page.
* If the background process is triggered, use the updated workflow set in an earlier story.
** User is informed that their documents are processing and to check the Document Center.
** User is informed (email/workspace notification) when the print job is ready.
** User can nav to the Document Center and see the print job + download 1 file for all letters involved.

### Acceptance Criteria

* Link to the Documents Center added to the page.
* ‘Back’ button available to return the user to the page they were on.
* Success messaging updated if background printing is involved.
* Remove any ‘Download last generated print’ bits from the pages.
* Grid changes > Server side pagination, Preview, Notify and Notify All button
* Notify Drawer changes > Letter format options (Individual / Household)

---

## NXT-52653 — Elig - Dashboard - Potential Matches CTA Update

- Resolved: 2024-08-05
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

!image-20240714-160739.png|width=1057,height=258,alt="image-20240714-160739.png"!

*Requirements*

* Update the Potential Matches Call to Action (CTA) on the Eligibility Dashboard to match the actual count from the Potential Matches page
** Currently it is ignoring any potential matches with points >automatic threshold.

### Acceptance Criteria

* Count of available potential matches is the same on the Potential Matches page and the Eligibility Dashboard.

---

## NXT-51194 — FO - Document Center - Update Income Surveys to use background process, Page Updates

- Resolved: 2024-07-24
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

As Dora the Director I want all letters in a single location for easier handling and downloading.

*mockup*

n/a

*requirements*

* Update letters out of Notifications > Surveys  to use the background process (more than 20 letters)
* If the background process is triggered, use the updated workflow set in an earlier story.
** User is informed that their documents are processing and to check the Document Center.
** User is informed (email/workspace notification) when the print job is ready.
** User can nav to the Document Center and see the print job + download 1 file for all letters involved.

### Acceptance Criteria

* Notifications > Survey pages updated to use the same background processing workflow for letters.
* Tie into the same workflow as other Document Center stories
** User is informed they can collect their print from the Document Center.
** User receives an email/inbox msg when the print is ready.
* Page updated to have a button that takes the user to the Document Center.
* Grid changes > Server side pagination, Preview, Notify and Notify All button

---

## NXT-49691 — FO - Document Center - Workflow update for Notifications > Applications

- Resolved: 2024-07-23
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

As Dora the Director I want all letters in a single location for easier handling and downloading.

*mockup*

n/a

*requirements*

* Update the page workflow for Notifications > Applications.
** Add a link to the Documents Center on the pages listed above.
** User should have a Back button to take them back to the page they were just on.
** If the user prints and it has to go to background processing (and become available at the Documents Center), inform them:
*** Text: Printing is in progress. Visit the Documents Center to download once it is ready.
** Remove any ‘download last generated’ bits from the page.
* If the background process is triggered, use the updated workflow set in an earlier story.
** User is informed that their documents are processing and to check the Document Center.
** User is informed (email/workspace notification) when the print job is ready.
** User can nav to the Document Center and see the print job + download 1 file for all letters involved.

### Acceptance Criteria

* Link to the Documents Center added to the page.
* ‘Back’ button available to return the user to the page they were on.
* Success messaging updated if background printing is involved.
* Remove any ‘Download last generated print’ bits from the pages.
* Grid changes > Server side pagination, Preview, Notify and Notify All button

---

## NXT-51520 — FO - Documents Center - Workflow update for Notifications > Carryover

- Resolved: 2024-07-02
- Status: Done Done
- Resolution: Done
- Components: Eligibility

### Description

As Dora the Director I want all letters in a single location for easier handling and downloading.

*mockup*

n/a

*requirements*

* Update the page workflow for Notifications > Carryover.
** Add a link to the Documents Center on the pages listed above.
** User should have a Back button to take them back to the page they were just on.
** If the user prints and it has to go to background processing (and become available at the Documents Center), inform them:
*** Text: Printing is in progress. Visit the Documents Center to download once it is ready.
** Remove any ‘download last generated’ bits from the page.
* If the background process is triggered, use the updated workflow set in an earlier story.
** User is informed that their documents are processing and to check the Document Center.
** User is informed (email/workspace notification) when the print job is ready.
** User can nav to the Document Center and see the print job + download 1 file for all letters involved.

### Acceptance Criteria

* Link to the Documents Center added to the page.
* ‘Back’ button available to return the user to the page they were on.
* Success messaging updated if background printing is involved.
* Remove any ‘Download last generated print’ bits from the pages.

---

## NXT-48689 — Family Hub - Homepage - Sign in with Apple

- Resolved: 2024-05-21
- Status: Done Done
- Resolution: Done
- Components: Eligibility, Family Hub

### Description

*Sign in with Google/Apple -* Previously, this feature was available in Classic. It allowed users to use the Apple plugins to create a SchoolCafe Family Hub account using their Apple profile. However, it is missing in the new Family Hub:

!image-20220322-185010.png|width=1638,height=817!

Let’s restore the button so that users can again create and log in using their Apple profile data.

### Acceptance Criteria

* Display the 'Sign in with Apple' button on the Family Hub homepage
* Allow a user to be able to create and login to their Family Hub account with Apple

---

