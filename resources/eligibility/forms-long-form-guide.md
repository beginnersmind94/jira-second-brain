---
id: elig-forms-long-form-guide
title: "Forms in Eligibility — Full Guide"
platform: schoolcafe
module: Eligibility
page: "Forms"
content_type: long-form-guide
roles: ["director","manager"]
tags: ["onboarding","forms","frequency:on-demand"]
status: draft
template: long-form-guide
source_refs:
  - "raw/tickets/NXT-69982.md"
  - "raw/tickets/NXT-70092.md"
  - "raw/tickets/NXT-70440.md"
  - "raw/tickets/NXT-70450.md"
  - "raw/tickets/NXT-70451.md"
  - "raw/tickets/NXT-70452.md"
  - "raw/tickets/NXT-70453.md"
  - "raw/tickets/NXT-71226.md"
  - "raw/tickets/NXT-71227.md"
updated: 2026-05-13
---

# Forms in Eligibility (Full Guide)

> **One-line promise:** by the end you can configure a non–school-meal form type (like Summer EBT) end-to-end — define the form, attach its application image, set its processing rules, accept submissions at the district, and enable Family Hub submission for households.
> **Audience:** District directors and child-nutrition managers. The Family Hub configuration parts assume someone on your team has Family Hub admin access.
> **Time:** 30–45 min to read; ~15 min to configure your first form once your Cybersoft license is enabled.
> **Status:** Draft. Pending SME review.

## At a glance

**Forms** is how SchoolCafé handles non-traditional benefit applications in Eligibility — anything that isn't a standard Free & Reduced school-meal application. The canonical example is **Summer EBT**, but Forms is generic: districts and Cybersoft Implementation define each form type once, then district staff or Family Hub families submit applications against that type, and the results land in a grid alongside existing Eligibility data. Source: [[raw/tickets/NXT-69982|NXT-69982]].

The framework has four pieces:

- **Form Configuration** (Eligibility → Form Configuration) — three tabs that define form types, attach image templates, and tune auto-processing. Source: [[raw/tickets/NXT-70092|NXT-70092]].
- **Other Forms** (Eligibility → Forms → Other Forms) — a new district-side page where staff submit and review form applications. Source: [[raw/tickets/NXT-69982|NXT-69982]].
- **FRE Application Image** (Eligibility → Settings → Application Image) — separate Cybersoft-admin page for the default FRE image used by every current FRE application. Source: [[raw/tickets/NXT-70453|NXT-70453]].
- **Family Hub side** — the **Forms license** unlocks "Submit Forms" on the district short URL and the **Forms Template** page in Family Hub. Source: [[raw/tickets/NXT-71227|NXT-71227]].

What this guide does **not** cover: the standard School Meal Application workflow (those are core eligibility, not "forms" in this framework), Direct Certification (separate concept, separate guide), or the household-application processing workflow (see [[wiki/concepts/Eligibility.md|Eligibility (concept)]] and the View & Modify Applications guide).

## Why this exists

Before the framework, every new non-meal benefit (Summer EBT, district-specific surveys, bus-fee assistance, etc.) needed a one-off implementation: a custom page, custom image template, custom routing. That made every state's Summer EBT rollout a project. The Forms framework collapses all of that into a single shape — a form type with a configurable image and a configurable processing rule set — so a new benefit goes from idea to live in days, not sprints. The reframing happened alongside renaming the existing "Form Settings" page to **Form Configuration**, because the old name no longer reflected scope. Source: [[raw/tickets/NXT-69982|NXT-69982]], [[wiki/concepts/Eligibility.md|Eligibility]].

## Concepts

- **Form type** — a configurable definition: a name, an image template, a date range, a set of sites, and a flag set (verification, income collection, SSN, signature, etc.). Each form type lives on the Forms tab of Form Configuration. Source: [[raw/tickets/NXT-70450|NXT-70450]].
- **Form Image Template** — the HTML image (printable view) that accompanies a form. Multiple forms can reuse one template; each form points to exactly one template. The "Default" template is named **Standard Image Template** and cannot be overwritten — you clone with **Save As**. Source: [[raw/tickets/NXT-70450|NXT-70450]], [[raw/tickets/NXT-70451|NXT-70451]].
- **Auto-Processing Rule** — a configurable exception in the auto-processing path. Example: applications at CEP sites are by default routed to Pending; turning that rule off makes them process normally. Source: [[raw/tickets/NXT-70092|NXT-70092]].
- **Form Application** — a single submission against a form type. Lives on the **Other Forms** page in a grid. Has a Status and (after processing) a Result of Qualified or Unqualified. Source: [[raw/tickets/NXT-70440|NXT-70440]].
- **Forms license** — a SchoolCafé district license that gates the whole framework on the Family Hub side. Enabled per district by Cybersoft from Super Admin → Configuration → Configure Districts. Source: [[raw/tickets/NXT-71227|NXT-71227]].
- **Forms Template page (Family Hub)** — mirror of the existing Program Template page, listing all active forms and letting district admins edit each one for the families view. Same language list as Manage Languages. Source: [[raw/tickets/NXT-71227|NXT-71227]].
- **FRE Application Image** — the master image template the standard FRE application uses. Distinct from Forms Image Templates: edits here affect **all** FRE applications immediately, past and present. Source: [[raw/tickets/NXT-70453|NXT-70453]].

## How it works

1. **Cybersoft enables the Forms license** for the district from Super Admin → Configuration → Configure Districts. This unlocks the Family Hub side and the "Submit Forms" link on the district's short URL. (`Owner: Cybersoft`.) Source: [[raw/tickets/NXT-71227|NXT-71227]].
2. **A district admin defines a form type** on Form Configuration → Forms tab using **Add New Form Application**. The fields define everything the application will collect and how it'll process. (`Owner: Your team`.) Source: [[raw/tickets/NXT-70450|NXT-70450]].
3. **The image template attached** to the form determines the printable view. Districts can clone the Default template via Save As and edit the HTML for their needs. (`Owner: Your team`, except the Default/Income Survey templates which are Cybersoft-managed.) Source: [[raw/tickets/NXT-70451|NXT-70451]], [[raw/tickets/NXT-70452|NXT-70452]].
4. **Auto-Processing Rules** decide whether incoming online applications are auto-processed or parked in Pending. (`Owner: Your team`.) Source: [[raw/tickets/NXT-70092|NXT-70092]].
5. **A Family Hub family submits an application** against the form type — visible from "Submit Forms" on the short URL, gated by the Forms license. (`Owner: Parent/applicant`.) Source: [[raw/tickets/NXT-71227|NXT-71227]].
6. **A district staff member submits or reviews** a form application from **Other Forms → Add New Form Application** (district-side entry) or the grid (review submissions). (`Owner: Your team`.) Source: [[raw/tickets/NXT-71226|NXT-71226]], [[raw/tickets/NXT-70440|NXT-70440]].
7. **The application gets a Result** (Qualified / Unqualified) once processed — the Result column is blank until then. Source: [[raw/tickets/NXT-70440|NXT-70440]].

## Step-by-step (the common path)

### Step 1 — Define a new form type

1. Navigate to **Eligibility → Form Configuration**. The page has three tabs — **Forms** (default), **Form Image Templates**, **Auto-Processing Rules**. Page-level access is shared across all three. Source: [[raw/tickets/NXT-70092|NXT-70092]].
2. On the **Forms** tab, click **Add New Form Application** to open the configuration drawer. Source: [[raw/tickets/NXT-70450|NXT-70450]].
3. Fill out the configuration fields:
   - **Name** (≤50 chars) and **Description** (≤50 chars)
   - **Other Benefit** — dropdown of active benefits paired with the current academic year (e.g. "Summer EBT (2025-2026)")
   - **Form Image Template** — choose from active templates; **Default** is the default value
   - **Start Date** — auto-populates to today; required
   - **End Date** — optional; leave blank or pick a future date
   - **Site(s) Associated** — multi-select against active sites
   - **Form requires verification** — Yes / No. If Yes: **Standard** or **Rolling**
   - **Income Collection Method** — Individual / Household / None. If Individual: also answer **Accept child income** (Yes/No)
   - **Form requires last 4 digits of SSN** — Yes / No / **Partial** (Partial behaves the same as Yes at runtime)
   - **Form requires electronic signature** — Yes / No
   - **This form must have its own notification letters** — Yes / No
   - **Display privacy act / disclaimer** — Yes / No
   - **Accept PFD** — Yes / No (shown only if the district is in Alaska)
   - **Form is enabled** — controls whether the form appears Enabled or Disabled in the grid
4. Click **Save**. The form appears in the grid and becomes selectable when staff submit a form application via **Other Forms** and when families submit via Family Hub (license permitting). Source: [[raw/tickets/NXT-70450|NXT-70450]].

### Step 2 — Manage form image templates

1. Open **Form Configuration → Form Image Templates**. The grid lists every image template with these columns: **Template Name** (the Default record is named "Standard Image Template"), **Form(s) Associated**, **Status** (Active by default; column filters available), **Type** (Standard or Custom), **Action(s)**. Source: [[raw/tickets/NXT-70452|NXT-70452]].
2. Use the **Edit (pencil)** action to change a template's name, the forms associated with it, or its active status. Source: [[raw/tickets/NXT-70452|NXT-70452]].
3. Use the **View** action to open the form image HTML editor — the editor's title shows the form name (e.g. "Summer EBT Form Image"). Edit the HTML content. **Be careful not to modify field data.** Source: [[raw/tickets/NXT-70451|NXT-70451]].
4. Click **Save As**. You **cannot overwrite the Default template**. Source: [[raw/tickets/NXT-70451|NXT-70451]].
5. When prompted, name the new template and confirm. It appears in the grid and is now selectable when configuring a form.
6. Use **History** to see who updated the template and when. (Field-level history of image edits is not tracked — just the change event.) Source: [[raw/tickets/NXT-70452|NXT-70452]].

> The Default School Meal Application and Income Survey image templates are **not** edited from this tab. To update those, contact Customer Care. Source: [[raw/tickets/NXT-70451|NXT-70451]].

### Step 3 — Tune Auto-Processing Rules

1. Open **Form Configuration → Auto-Processing Rules**.
2. Review the rules — the canonical example is: **applications at CEP sites are routed to Pending**. Turning that option off causes those applications to process normally. Source: [[raw/tickets/NXT-70092|NXT-70092]].

> The exact full toggle list shipped to this tab is still being confirmed with your SME — the original spec described the tab as housing "the formerly existing content on the page." Confirm the live UI before running a large rule change.

### Step 4 — Edit the master FRE Application Image (Cybersoft-only)

1. Navigate to **Eligibility → Settings → Application Image**. By default this page is restricted to **Cybersoft admin** permissions. Source: [[raw/tickets/NXT-70453|NXT-70453]].
2. Read the warning beneath the page title. Quoted in full: *"Please make sure that any changes to this image are in compliance with the rules and regulations for the state to which this district belongs, and be advised that updates made to this image will immediately impact ALL applications, past and present."* Source: [[raw/tickets/NXT-70453|NXT-70453]].
3. Edit the default FRE image (named "Standard Application Image") displayed beneath the warning.
4. Click **Save** to commit the change for the district, or **Cancel** to discard.

### Step 5 — Submit a form application district-side

1. Navigate to **Eligibility → Forms → Other Forms** (the page sits between Surveys and Processing in the nav). Source: [[raw/tickets/NXT-69982|NXT-69982]].
2. Click **Add New Form Application**.
3. Pick the active form type (e.g. "Summer EBT"). Only one form type can be selected per submission. Source: [[raw/tickets/NXT-71226|NXT-71226]].
4. The **Add New Form Application** stepper opens with the chosen form's name, mirroring the existing Add New Survey workflow for Income Surveys with the steps adjusted to that form's configuration. Source: [[raw/tickets/NXT-71226|NXT-71226]].
5. Complete each step according to the form's configuration:
   - **Income collection** — Individual (each household member has their own income; PFD is collected only in this scenario), Household (a single total household-income field), or None (income fields hidden; only Total Household Members / Household Size remain)
   - **Contact Info** — First Name and Last Name are required; other fields are optional
   - **SSN** — visible only when the form requires it. **Partial = Yes** at runtime (applicant enters last 4)
   - **Signature** — visible only when the form requires an electronic signature
6. Review the **Pending Reasons** shown on the Submit step. If household size doesn't match, the application **cannot** be submitted until resolved. Source: [[raw/tickets/NXT-71226|NXT-71226]].
7. Click **Submit** (submits as complete) or **Mark as Pending** (saves for later review).
8. The associated form application image is shown on the final step with print and export options.
9. Choose **I'm Done For Now** to return to the Other Forms page or **Submit Another Form Application** to start a new entry. Source: [[raw/tickets/NXT-71226|NXT-71226]].

### Step 6 — Review submitted applications

The Other Forms page loads with all submitted form applications in the grid. Two tabs:

- **ALL** — every submitted form application. Default columns: Form Application #, Form Name, Entry Method, Status, Received Date, Result, Household Size, Household Income Range, Household Income, Frequency. Source: [[raw/tickets/NXT-70440|NXT-70440]].
- **Pending** — only Pending applications. Default columns: Form Application #, Form Name, Entry Method, Received Date, Student Name(s), Reason. Source: [[raw/tickets/NXT-70440|NXT-70440]].

The Result column shows **Qualified** or **Unqualified** once processed; blank until then. Grid filters above the grid (including **Form Name**, formerly labeled "Form Select") work in tandem with the tab selection.

### Step 7 — Enable Family Hub submission

1. Coordinate with your Cybersoft Implementation contact to enable the **Forms license** for your district. Cybersoft enables it from Super Admin → Configuration → Configure Districts. Source: [[raw/tickets/NXT-71227|NXT-71227]].
2. Once enabled:
   - The district's short URL page shows a new **"Submit Forms"** line, displayed after the existing "Submit Meal Applications" line.
   - In the Benefits category in Family Hub, the **Forms Template** page becomes available to district admins. It mirrors Program Template in structure and steps, listing all active forms.
   - The Forms Template page uses the same language list as Manage Languages.
3. The **Fill Out a Form** operation, which surfaces forms to Family Hub applicants, is also gated by the Forms license.

## Examples

### Example 1 — Pilot Summer EBT for a single district (`<District A>`)

A district director wants to pilot Summer EBT for the upcoming summer, accepting applications only from families at three pilot sites. The director (a) confirms with Cybersoft Implementation that the Forms license is enabled, (b) creates the form type on Form Configuration → Forms with Summer EBT as the Other Benefit, the three pilot sites multi-selected, verification = Yes / Standard, SSN = Partial, signature = Yes, (c) leaves the Default image template attached for the pilot. The director then confirms on the Auto-Processing Rules tab that CEP-site applications still route to Pending so the pilot team can hand-review the first batch. Two days later, three applications appear on Other Forms → Pending — the director processes each one and the Result column shows Qualified. Source: [[raw/tickets/NXT-70450|NXT-70450]], [[raw/tickets/NXT-70092|NXT-70092]], [[raw/tickets/NXT-70440|NXT-70440]].

### Example 2 — Reusing an image template across two forms (`<District B>`)

A district has both Summer EBT and a district-specific Bus Fees benefit; both share the same disclaimer language and basic image layout. A staff member clones the Default template via Save As, names it "District B Standard," and edits the disclaimer language at the top. On Form Configuration → Forms, both Summer EBT and Bus Fees point to "District B Standard" as their image template. A later edit to the disclaimer wording updates both forms in one place. Source: [[raw/tickets/NXT-70451|NXT-70451]], [[raw/tickets/NXT-70450|NXT-70450]].

### Example 3 — A Pending row with a household-size mismatch (`<District C>`)

A family submits a Summer EBT application through Family Hub. On Submit, the Pending Reasons step shows "Household size does not match Total Household Members" — submission is blocked until the family corrects the size. They reload, fix it, resubmit. The application then appears on Other Forms → ALL with status Processed and Result Qualified. Source: [[raw/tickets/NXT-71226|NXT-71226]].

## Edge cases & known issues

- **You can't overwrite the Default image template.** Use Save As to clone, then edit the clone. Source: [[raw/tickets/NXT-70451|NXT-70451]].
- **Default School Meal Application and Income Survey image templates are managed by Cybersoft**, not editable from the Form Image Templates tab. Source: [[raw/tickets/NXT-70451|NXT-70451]].
- **Form Image Templates History records the event but not field-level diffs.** You can see who edited and when, not what they changed. Source: [[raw/tickets/NXT-70452|NXT-70452]].
- **SSN = Partial behaves the same as Yes** at runtime — the applicant still enters last-4. The Partial label is for configuration intent, not for changing the applicant flow. Source: [[raw/tickets/NXT-71226|NXT-71226]].
- **The FRE Application Image is restricted to Cybersoft admins** by default. Even a district admin generally can't reach it. Source: [[raw/tickets/NXT-70453|NXT-70453]].
- **Edits to the FRE Application Image affect ALL applications past and present, immediately.** The warning on the page exists for that reason. Source: [[raw/tickets/NXT-70453|NXT-70453]].
- **Family Hub families don't see "Submit Forms"** on the short URL until the Forms license is enabled. If a household reports the link is missing, the license is the first thing to check. Source: [[raw/tickets/NXT-71227|NXT-71227]].
- **A form can use only one image template; one image template can serve many forms.** This is asymmetric on purpose — keeps disclaimer/layout changes consolidated. Source: [[raw/tickets/NXT-70450|NXT-70450]].
- **Add New Form Application appears in two places with the same name.** On Form Configuration → Forms, it defines a new form *type* (drawer). On Other Forms, it submits a new form *application* (stepper). Same string, different action. Source: [[raw/tickets/NXT-70450|NXT-70450]], [[raw/tickets/NXT-71226|NXT-71226]].

## Glossary

(Optional — only terms not already defined in Concepts.)

- **Short URL** — the public district URL Family Hub uses for application/form intake. Once the Forms license is on, "Submit Forms" appears here alongside the existing "Submit Meal Applications" line. Source: [[raw/tickets/NXT-71227|NXT-71227]].
- **Program Template (Family Hub)** — the pre-existing page Forms Template mirrors. If you've configured Program Template before, the Forms Template steps will feel identical. Source: [[raw/tickets/NXT-71227|NXT-71227]].

## Sources

- [[wiki/concepts/Eligibility.md|Eligibility (concept page)]]
- [[raw/tickets/NXT-69982.md|NXT-69982 — Forms Framework: Other Forms page added; Form Settings → Form Configuration rename]]
- [[raw/tickets/NXT-70092.md|NXT-70092 — Form Configuration page layout; three tabs; shared page-level access]]
- [[raw/tickets/NXT-70440.md|NXT-70440 — Other Forms grid (ALL and Pending tabs, default columns)]]
- [[raw/tickets/NXT-70450.md|NXT-70450 — Add New Form drawer (form-type definition fields)]]
- [[raw/tickets/NXT-70451.md|NXT-70451 — Form Image Templates: add/edit with Save As]]
- [[raw/tickets/NXT-70452.md|NXT-70452 — Combined template grid with Edit/View/History row actions]]
- [[raw/tickets/NXT-70453.md|NXT-70453 — FRE Application Image: new page in Eligibility → Settings for Cybersoft admins]]
- [[raw/tickets/NXT-71226.md|NXT-71226 — Other Forms: Add New Form Application stepper]]
- [[raw/tickets/NXT-71227.md|NXT-71227 — SchoolCafé Forms license + Forms Template page + Submit Forms short URL]]
