---
title: Forms — Quick Guide
module: Eligibility
content_type: quick-guide
source_tickets: [NXT-69982, NXT-70092, NXT-70440, NXT-70450, NXT-70451, NXT-70452, NXT-70453, NXT-71226, NXT-71227]
status: draft_for_sme_review
created_at: 2026-05-13
authored_from: tickets
---

# Forms — Quick Guide

## Overview

Forms in Eligibility lets a district configure and accept non-traditional benefit applications — for example, Summer EBT — without relying on an external system. Cybersoft Implementation team members and district admins define each form type and its application image, then submitted form applications appear in a grid alongside existing Eligibility data. Family Hub families submit form applications once the Forms license is enabled for the district.

## Form Configuration — Forms tab

Form Configuration is the page where district admins manage form types, application images, and the auto-processing rules that route online applications to Pending. The page has three tabs — Forms (default), Form Image Templates, and Auto-Processing Rules — and any user with page-level access to Form Configuration has the same level of access on all three tabs.

The Forms tab lets you add or remove non-school-meal forms. The School Meal Application and Income Survey can also be modified here in a limited capacity.

Add a new form:
1. On the Forms tab, click Add New Form Application to open the drawer
2. Fill out the form configuration fields (listed below)
3. Click Save to add the form to the list

Form configuration fields:
- Name — up to 50 characters
- Description — up to 50 characters
- Other Benefit — dropdown of active benefits paired with the current academic year (for example, "Bus Fees (2025-2026)")
- Form Image Template — choose from active templates; Default is the default value
- Start Date — auto-populated to today; required
- End Date — optional; leave blank or set a future end date
- Site(s) Associated — multi-select against active sites for the district
- Form requires verification — Yes/No. If Yes, choose Standard or Rolling
- Income Collection Method — Individual, Household, or None. If Individual, also answer Accept child income (Yes/No)
- Form requires last 4 digits of SSN — Yes/No/Partial
- Form requires electronic signature — Yes/No
- This form must have its own notification letters — Yes/No
- Display privacy act / disclaimer — Yes/No
- Accept PFD — Yes/No (shown only if the district is in Alaska)
- Form is enabled — controls whether the form appears as Enabled or Disabled in the grid

A form can be associated with only one image template, but a single image template can be reused across multiple forms.

[SME QUESTION: NXT-70450's title says "Add New Form to grid" while its body refers to the drawer as "Add New Form Application." What is the actual label of the button on the Forms tab? This is the form-type-definition drawer, distinct from the Add New Form Application button on the Other Forms page described later in this guide.]

[SME QUESTION: What permission gates access to the Form Configuration page? NXT-70092 says any user with page-level access to Form Configuration has access to all three tabs, but does not name the specific role or operation that grants that page-level access.]

## Form Configuration — Form Image Templates tab

The Form Image Templates tab manages the HTML image templates that accompany each non-school-meal form. The Default School Meal Application and Income Survey image templates are not edited here — to update those, contact Customer Care.

The grid lists all image templates with these columns:
- Template Name (the Default record is named "Standard Image Template")
- Form(s) Associated
- Status — Active by default; column filters available
- Type — Standard or Custom
- Action(s)

Row actions:
- Edit (pencil) — opens a drawer to change the template name, the forms associated, and active/inactive status
- View — opens the form image HTML editor for editing template content
- History — shows which user updated the template and when (field-level history of image edits is not tracked)

Add or save a new image template:
1. Click View on an existing template (or on Default) to open the HTML editor
2. The editor title shows the form name — for example, "Summer EBT Form Image"
3. Edit the HTML text. Be careful not to modify field data
4. Click Save As. You cannot overwrite the Default template
5. When prompted, name the new template and confirm. It appears in the grid and is referenceable when configuring a form

[SME QUESTION: NXT-70451 says Save As is "enabled to anyone." Does "anyone" mean any user who can view this tab, or any user in the district regardless of role? Confirm the actual permission scope.]

## Form Configuration — Auto-Processing Rules tab

The Auto-Processing Rules tab controls scenarios where an online application with automatic processing may be parked as Pending instead of being processed. For example, applications with students at CEP sites are typically routed to Pending and not processed automatically; turning that option off causes those applications to process normally and not appear in Pending Applications.

[SME QUESTION: NXT-70092 describes the Auto-Processing Rules tab in general terms and gives the CEP example. Which specific toggles/settings now live on this tab? The tab is described as containing "the formerly existing content on the page" — please confirm the full list shipped.]

## FRE Application Image configuration

The Application Image page in Eligibility > Settings lets Cybersoft admins update the default HTML image template that all current FRE applications use. The page is restricted to Cybersoft admin permissions by default.

A warning is shown beneath the page title:

> Warning: Please make sure that any changes to this image are in compliance with the rules and regulations for the state to which this district belongs, and be advised that updates made to this image will immediately impact ALL applications, past and present.

Update the FRE application image:
1. Navigate to Eligibility > Settings > Application Image
2. Review the warning
3. Edit the default FRE image displayed beneath the warning
4. Click Save to permanently save your changes for the district, or Cancel to discard them

The default image is named "Standard Application Image."

## Other Forms — Add New Form Application

The Other Forms page lives in Eligibility > Forms > Other Forms, between Surveys and Processing in the Eligibility navigation. From here, district users submit form applications against any active form type configured in Form Configuration.

The Add New Form Application button opens a stepper that mimics the existing Add New Survey workflow for Income Surveys, with the steps adjusted to match the selected form's configuration.

Submit a new form application:
1. On the Other Forms page, click Add New Form Application
2. Choose the active form type (for example, Summer EBT, Income Survey, or any other configured form). Only one form type can be selected
3. The Add New Form Application stepper opens, displaying the chosen form's name
4. Complete each step according to the form's configuration:
   - Income collection — Individual (each household member has their own income; PFD is collected only in this scenario), Household (a single total household-income field), or None (income fields hidden; only Total Household Members / Household Size remain)
   - Contact Info — First Name and Last Name are required; other fields are optional
   - SSN — visible only when the form requires last 4 digits of SSN. Partial is treated the same as Yes
   - Signature — visible only when the form requires an electronic signature
5. Review the Pending Reasons shown on the Submit step. If household size does not match, the application cannot be submitted until the issue is resolved
6. Click Submit to submit the application as complete, or Mark as Pending to save it for later review
7. The associated form application image is shown on the final step, with print and export options
8. Choose I'm Done For Now to return to the Other Forms page, or Submit Another Form Application to start a new entry

[SME QUESTION: NXT-71226 notes that the form-type selection mechanism is negotiable (drawer, dropdown, or other picker). Which final UI shipped? Update this section to match.]

## Other Forms — Submitted form applications grid

When the Other Forms page loads, it displays all submitted form applications in the grid. Two tabs are available: ALL (every submitted form application) and Pending (only applications in Pending status).

Default columns on the ALL tab:
- Form Application #
- Form Name
- Entry Method
- Status
- Received Date
- Result
- Household Size
- Household Income Range
- Household Income
- Frequency

Default columns on the Pending tab:
- Form Application #
- Form Name
- Entry Method
- Received Date
- Student Name(s)
- Reason

The Result column displays Qualified or Unqualified once the application has been processed; it is blank until then.

Grid results work in tandem with the filters above the grid. The form-selection filter is labeled Form Name (formerly Form Select).

[SME QUESTION: NXT-70440 lists Application Details, History, Delete, and the Excel button as items that "can be handled in a separate story." Which of these are available on the Other Forms page today, and which are deferred?]

## Family Hub side — Forms license and Forms Template

Forms is gated by a SchoolCafé district license also called Forms. Cybersoft admins enable it per district from Super Admin > Configuration > Configure Districts. Enabling the Forms license ties the Forms Template and Fill Out a Form operations to that district.

When the Forms license is enabled for a district:
- The district's short URL page shows a "Submit Forms" line, displayed after the existing "Submit Meal Applications" line
- In the Benefits category, the Forms Template page becomes available to district admins. It mirrors the existing Program Template page in structure and steps, listing all active forms and letting the admin edit them
- The Forms Template page uses the same language list as the Manage Languages page

The Fill Out a Form operation, which surfaces forms to Family Hub applicants, is also gated by the Forms license.

[SME QUESTION: NXT-71227 says the Forms Template page mirrors Program Template "except one additional step described below," and points to a follow-up story for form questionnaire answers / settings. Which additional step is shipped in the current Forms Template page, if any?]

[SME QUESTION: When a district enables the Forms license, does the "Submit Forms" link appear on the short URL page immediately, or is a separate Family Hub cache invalidation / release required before applicants can see it?]

## Source tickets

| Ticket | Resolved | Summary |
|---|---|---|
| NXT-69982 | 2026-02-23 | Forms Framework — Other Forms page added in nav between Surveys and Processing; Form Settings renamed to Form Configuration; Other Forms permission added |
| NXT-70092 | 2026-02-23 | Form Configuration page layout — three tabs (Forms, Form Image Templates, Auto-Processing Rules); shared page-level access |
| NXT-70450 | 2026-04-14 | Form Configuration > Forms tab — Add New Form drawer (form-type definition fields) |
| NXT-70451 | 2026-04-14 | Form Image Templates tab — add/edit form image templates with Save As |
| NXT-70452 | 2026-03-31 | Form Image Templates tab — combined template grid with Edit, View, History row actions |
| NXT-70453 | 2026-04-14 | FRE Application Image — new page in Eligibility > Settings for Cybersoft admins |
| NXT-70440 | 2026-05-12 | Other Forms — submitted form applications grid (ALL and Pending tabs, default columns) |
| NXT-71226 | 2026-05-04 | Other Forms — Add New Form Application button stepper for submitting an application |
| NXT-71227 | 2026-04-28 | SchoolCafé Forms license + Forms Template page + "Submit Forms" line on district short URL |
