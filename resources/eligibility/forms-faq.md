---
id: elig-forms-faq
title: "Forms — FAQ"
platform: schoolcafe
module: Eligibility
page: "Form Configuration"
content_type: faq
roles: ["director","manager"]
tags: ["forms","onboarding","troubleshooting"]
status: draft
template: faq
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

# Forms — FAQ

> Questions district admins and managers actually ask about **Forms in Eligibility** — Form Configuration, Other Forms, image templates, and Family Hub. Every answer cites the source ticket the behavior shipped from.

## Q1 — Where did "Form Settings" go? I can't find it in the menu.

It was renamed to **Form Configuration**. Same data, expanded scope — the page now houses non–school-meal form types (like Summer EBT) alongside the existing Income Survey and School Meal Application configuration. It lives under **Eligibility → Form Configuration**.

**Source:** [[raw/tickets/NXT-69982|NXT-69982]]

---

## Q2 — What's the new "Other Forms" page for, and where does it sit?

**Other Forms** is the page where district users submit form applications against any active form type your district has configured. It sits in the Eligibility nav between **Surveys** and **Processing**. The button there — **Add New Form Application** — runs a stepper similar to Add New Survey, with steps adjusted to the chosen form's configuration.

**Source:** [[raw/tickets/NXT-69982|NXT-69982]], [[raw/tickets/NXT-71226|NXT-71226]]

---

## Q3 — What are the three tabs on Form Configuration, and do I need different access for each?

Three tabs: **Forms** (default), **Form Image Templates**, and **Auto-Processing Rules**. Page-level access is shared — anyone with access to Form Configuration has the same access to all three tabs. There's no per-tab permission.

**Source:** [[raw/tickets/NXT-70092|NXT-70092]]

---

## Q4 — I have one image template that works for Summer EBT — can I reuse it for another form type?

Yes. One image template can be associated with **multiple** forms. The constraint is in the other direction: a single form points to exactly one image template.

**Source:** [[raw/tickets/NXT-70450|NXT-70450]]

---

## Q5 — Can I overwrite the Default form image template?

No. The Default template is protected — you cannot Save over it. Use **Save As** from the HTML editor (opened via the View action on the Default row) to clone it under a new name, then edit the clone. Your new template appears in the grid and becomes selectable when configuring a form.

**Source:** [[raw/tickets/NXT-70451|NXT-70451]]

---

## Q6 — What can I do from each row of the Form Image Templates grid?

Three row actions: **Edit** (pencil) opens a drawer to change the template name, the forms it's associated with, and its active/inactive status. **View** opens the form image HTML editor for editing the template's content. **History** shows which user updated the template and when — note that **field-level** history of image edits is not tracked, only the change event.

**Source:** [[raw/tickets/NXT-70452|NXT-70452]]

---

## Q7 — Where do I edit the master FRE application image, the one all current applications use?

That's a separate page: **Eligibility → Settings → Application Image**. The default image there is named "Standard Application Image." This page is restricted to **Cybersoft admin** permissions by default — district admins normally don't have it. The page also displays a compliance warning before the editor, because edits to this image apply immediately to **all applications, past and present**.

**Source:** [[raw/tickets/NXT-70453|NXT-70453]]

---

## Q8 — What does the warning on the FRE Application Image page actually say?

Quoted: *"Please make sure that any changes to this image are in compliance with the rules and regulations for the state to which this district belongs, and be advised that updates made to this image will immediately impact ALL applications, past and present."* If you're updating the image for a single new form (not the whole FRE workflow), use the Form Image Templates tab instead — those edits only affect forms that point to that template.

**Source:** [[raw/tickets/NXT-70453|NXT-70453]]

---

## Q9 — What does the "Result" column on the Other Forms grid show?

It shows **Qualified** or **Unqualified** once the application has been processed. Until the application is processed, the column is blank. The default columns on the ALL tab are: Form Application #, Form Name, Entry Method, Status, Received Date, Result, Household Size, Household Income Range, Household Income, Frequency.

**Source:** [[raw/tickets/NXT-70440|NXT-70440]]

---

## Q10 — What's the difference between the ALL tab and the Pending tab on Other Forms?

**ALL** lists every submitted form application regardless of status. **Pending** shows only those in Pending status — a narrower set of columns: Form Application #, Form Name, Entry Method, Received Date, Student Name(s), Reason. Both tabs respect the grid filters above (Form Name, formerly labeled "Form Select," is one of those filters).

**Source:** [[raw/tickets/NXT-70440|NXT-70440]]

---

## Q11 — A form's SSN field is set to "Partial." What does that mean for the applicant?

Partial behaves the same as **Yes** — the applicant is required to enter the last 4 digits of their SSN to complete the form. The Partial label exists for configuration clarity (some districts want the option of distinguishing it from full-SSN forms), but the runtime behavior on the SSN step in the Add New Form Application stepper is identical to Yes.

**Source:** [[raw/tickets/NXT-71226|NXT-71226]]

---

## Q12 — Families in our district can't see the new "Submit Forms" link on the short URL page. What's missing?

Your district's **Forms license** is probably not enabled yet. The Forms license is a SchoolCafé district license that gates the entire framework: when enabled, the district's short-URL page shows the **"Submit Forms"** line beneath the existing **"Submit Meal Applications"** line, and the Forms Template page becomes available to district admins under Family Hub's Benefits category. Cybersoft enables the license per district from **Super Admin → Configuration → Configure Districts** — request it from your Cybersoft Implementation contact.

**Source:** [[raw/tickets/NXT-71227|NXT-71227]]

---

## Q13 — What's the "Forms Template" page in Family Hub, and how is it different from Program Template?

Once the Forms license is on, **Forms Template** appears in the Benefits category in Family Hub. It mirrors the existing **Program Template** page in structure and steps — listing all active forms and letting an admin edit each one — and it uses the same language list as the Manage Languages page. The exact additional step (if any) beyond Program Template parity is still being confirmed against the shipped UI; ask your SME if you need precise step counts before going live.

**Source:** [[raw/tickets/NXT-71227|NXT-71227]]

---

## Q14 — Online Summer EBT applications are auto-processing when I'd rather review them. Where do I turn that off?

The **Auto-Processing Rules** tab on Form Configuration controls when an online application that would normally auto-process is parked in Pending instead. The canonical example: applications with students at CEP sites are typically routed to Pending; turning that rule off causes those to process normally and not appear in Pending Applications. For a Summer EBT pilot you'd typically leave the parking rule on so your team gets a chance to review the first batch.

**Source:** [[raw/tickets/NXT-70092|NXT-70092]]

---

> **Status:** Draft, pending SME review. Two items remain open and have been intentionally **not** answered above (per the anti-hallucination rule "cite or cut"): (1) the exact role/operation that grants page-level access to Form Configuration, and (2) the precise additional step the Forms Template page adds beyond Program Template. Add those answers after SME confirmation.
