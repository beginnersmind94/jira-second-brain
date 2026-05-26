---
id: elig-onboarding-guide
title: "Eligibility in SchoolCafé — Onboarding Guide"
platform: schoolcafe
module: Eligibility
page: "Eligibility (module overview)"
content_type: long-form-guide
roles: ["director","manager"]
tags: ["onboarding","compliance","new-hire"]
status: draft
template: long-form-guide
source_refs:
  - "wiki/concepts/Eligibility.md"
  - "wiki/workflows/direct-certification.md"
  - "raw/tickets/NXT-15058.md"
  - "raw/tickets/NXT-13343.md"
  - "raw/tickets/NXT-14223.md"
  - "raw/tickets/NXT-60922.md"
  - "raw/tickets/NXT-63982.md"
  - "raw/tickets/NXT-21564.md"
  - "raw/tickets/NXT-58224.md"
  - "raw/tickets/NXT-5204.md"
  - "raw/tickets/NXT-7337.md"
  - "raw/tickets/NXT-66798.md"
  - "raw/tickets/NXT-69982.md"
  - "raw/tickets/NXT-70092.md"
  - "raw/tickets/NXT-70440.md"
  - "raw/tickets/NXT-70450.md"
  - "raw/tickets/NXT-70453.md"
  - "raw/tickets/NXT-71227.md"
  - "raw/tickets/NXT-68256.md"
  - "raw/tickets/NXT-56345.md"
  - "raw/tickets/NXT-56318.md"
updated: 2026-05-13
---

# Eligibility in SchoolCafé — Onboarding Guide

> **One-line promise:** by the end you'll understand every path a student takes to a meal-price determination in SchoolCafé — and where to go in the product to handle each path.
> **Audience:** new district directors, child-nutrition managers, and Cybersoft Implementation team members joining the SchoolCafé side of an account. Assumes no prior knowledge of the platform.
> **Time:** 40–55 min for a careful first read; ~3 hours if you click through each section in your sandbox alongside.
> **Status:** Draft. Pending SME review.

## At a glance

In SchoolCafé, **Eligibility** decides what meal price applies to each student — Free, Reduced, or Paid — and why. That determination drives every cashier transaction, every reimbursement claim your district files, and every state and federal compliance report. Source: [[wiki/concepts/Eligibility.md|Eligibility (concept page)]].

A student's price determination comes from one of four paths:

1. **Direct Certification (DC)** — a state-supplied file says the student is in SNAP / TANF / foster / (sometimes) Medicaid. They become Free automatically.
2. **A household application** — a paper or online Free & Reduced application is processed and the system grants Free, Reduced, or Paid based on the income/category answers.
3. **A district form application** — a non-traditional benefit (Summer EBT and similar), processed through Forms in Eligibility.
4. **CEP (Community Eligibility Provision)** — every student at a CEP site is served at no charge, with reimbursement based on a multiplier of identified-student counts.

This guide walks you through each path, the daily / weekly / monthly workflows around them, and how Verification closes the loop annually. What this guide does **not** cover: the cashier-side (POS) flow, menu planning, financial reporting beyond Eligibility's pieces, or state-specific policy variations.

## Why this exists

You'll inherit a system where many of the most consequential workflows — the ones that determine whether a hungry kid pays for lunch — are spread across half a dozen pages and a half-dozen integrations. Customers regularly ask "why is this student paying when they were free last month" or "why isn't my Summer EBT pilot showing applications" and the answer requires knowing which path the student is on. This guide is the map that lets you answer those questions without paging an SME. Source: [[wiki/concepts/Eligibility.md|Eligibility]].

## Concepts

The concepts below recur across every later section. Skim them now; come back when something downstream confuses you.

### Eligibility statuses

- **Free** — the student qualifies for free meals. Source can be DC, an approved household application, a Forms (non-meal benefit) application that qualified, or CEP-site enrollment.
- **Reduced** — the student qualifies for reduced-price meals. Only reached via household application income/size.
- **Paid** — the default state when no qualifying mechanism applies. Cashier charges full price.

### Reasons / Basis

Every status carries a **reason** explaining *how* it was set. Examples: "Free (DC MEDICAID)", "Free (Carryover)", "Paid (Default)". The reason is what auditors care about; the status alone isn't sufficient evidence. Source: [[raw/tickets/NXT-56318|NXT-56318]] — reasons are shown alongside status in the Eligibility Status Changes report and Pending Students match view.

### The four entry paths

| Path | Trigger | Output |
|---|---|---|
| **Direct Certification** | State sends a file; system matches against roster | Auto-certifies matches as Free; queues unsure rows in Potential Matches for human review. Source: [[raw/tickets/NXT-15058\|NXT-15058]] |
| **Household application** | Paper/online application submitted; staff process | Free, Reduced, or Paid based on income/category answers. Source: [[raw/tickets/NXT-7337\|NXT-7337]] |
| **Forms** (in Eligibility) | Non-meal benefit application (Summer EBT, etc.) submitted | Qualified or Unqualified result, recorded in Other Forms grid. Source: [[raw/tickets/NXT-69982\|NXT-69982]], [[raw/tickets/NXT-70440\|NXT-70440]] |
| **CEP enrollment** | Student is enrolled at a CEP-designated site | Free, with CEP reason; reimbursement rate is multiplier-based per identified students. Source: [[raw/tickets/NXT-68256\|NXT-68256]] |

### Pending

Not every application processes automatically. "Pending" is the catch-all for "human needs to look at this." Two flavors:

- **Pending Applications** — the application itself didn't clear auto-processing (e.g. household-size mismatch, CEP-site routing rule, missing required field). Source: [[raw/tickets/NXT-5204|NXT-5204]].
- **Pending Students** — the application processed, but the student listed on it can't be linked to your roster (typo, not yet enrolled, multiple candidates). Source: [[raw/tickets/NXT-66798|NXT-66798]].

Both have their own tab on the Applications page. They're worked daily; the next section covers the SOP.

### Ownership

Every action below is tagged with who runs it. The four owners you'll see:

- `Cybersoft` — Cybersoft (the SchoolCafé vendor) runs this; you don't have access by default.
- `Your team` — district staff (you and your reports).
- `Cybersoft + Your input` — Cybersoft executes, but only after you provide configuration or sign-off.
- `Parent/applicant` — household-side action (Family Hub, paper application).

This tag is load-bearing because customers default to assuming "the product does it" when verbs aren't qualified. Source: this guide adopts the same ownership convention as the rest of the customer-facing material in `resources/eligibility/`.

## How it works

### Path 1 — Direct Certification

1. **State sends a DC file** to your district on a state-set cadence (often monthly, sometimes more). (`Owner: Cybersoft + Your input` — Cybersoft set up the state integration, your team retrieves/uploads the file.)
2. **Your team uploads the file** at **Eligibility → Direct Certification → File Import**. The system records the **Import Date** and queues processing. (`Owner: Your team`.) Source: [[raw/tickets/NXT-58224|NXT-58224]].
3. **The system scores each DC record** against enrolled students using three categories — **Personal Information** (name, DOB, DOB variations), **Contact Information** (guardian name and address, phone), **ID Numbers** (SSN, State ID, Student ID). Confident matches certify automatically; unsure ones go to **Potential Matches**. (`Owner: Cybersoft`.) Source: [[raw/tickets/NXT-15058|NXT-15058]].
4. **Your team reviews Potential Matches** daily until the queue is empty. Click each row, read the scorecard, decide **Match** (with required comment) or **Mark as Reviewed**. (`Owner: Your team`.) Source: [[raw/tickets/NXT-15058|NXT-15058]].
5. **Secondary matching reruns silently** when an enrolled student's record changes via Account Management. A typo fix in a name can produce a late match against an already-imported file without any re-upload. (`Owner: Cybersoft`, triggered by `Your team`'s edit.) Source: [[raw/tickets/NXT-14223|NXT-14223]].
6. **Reports** — counts at Eligibility → Reports → Direct Certification Counts (Site Code / Site Name multi-select). Per-student detail at the "By Direct Certification" report. Source: [[raw/tickets/NXT-63982|NXT-63982]], [[raw/tickets/NXT-21564|NXT-21564]].

> **Gotcha:** "Direct Certification" is **not** an option on the Manual Entry screen. The only path to a DC certification is File Import. This was a deliberate removal so users wouldn't claim a DC certification without a real state-file source. Source: [[raw/tickets/NXT-60922|NXT-60922]].

### Path 2 — Household applications (Free & Reduced)

1. **A household submits an application** — paper (entered by your team) or online (Family Hub). (`Owner: Parent/applicant`, supported by `Your team` for paper entries.)
2. **The system attempts to auto-process**, applying the configured rules (household size, income thresholds, refusal flags, etc.). Source: [[raw/tickets/NXT-7337|NXT-7337]].
3. **If auto-processing succeeds**, the application gets a Status (Processed, Notified) and the student(s) get an Eligibility update.
4. **If auto-processing doesn't succeed**, the application lands on **Pending Applications**. Your team works the tab daily — see the SOP for the full step-by-step. Source: [[raw/tickets/NXT-5204|NXT-5204]].
5. **Even after processing**, the student may need a roster link — if the application named a student your district doesn't have (or has under a different spelling), the link sits on the **Pending Students** tab until your team resolves it via **FIND MATCHES** + manual matching. Source: [[raw/tickets/NXT-66798|NXT-66798]].
6. **Notifications** go to households automatically based on Status. The application carries a language selection; notifications use the corresponding language template when configured. Source: [[raw/tickets/NXT-5204|NXT-5204]].

### Path 3 — Forms (non-meal benefits)

Forms is the Eligibility sub-area for benefits that aren't standard F&R but still need application-style intake. The canonical example is **Summer EBT**.

1. **Cybersoft enables the Forms license** for your district from Super Admin → Configuration → Configure Districts. (`Owner: Cybersoft + Your input` — you ask, Cybersoft flips.) Source: [[raw/tickets/NXT-71227|NXT-71227]].
2. **Your team defines a form type** on Eligibility → Form Configuration → Forms tab using **Add New Form Application** — this is the *form-type-definition* drawer. The fields define what the application collects and how it processes. (`Owner: Your team`.) Source: [[raw/tickets/NXT-70450|NXT-70450]].
3. **Your team attaches an image template** to the form. Save As to clone the Default; one template can serve multiple forms but one form points to exactly one template. (`Owner: Your team`.) Source: [[raw/tickets/NXT-70450|NXT-70450]].
4. **Your team tunes Auto-Processing Rules** if needed (e.g. whether CEP-site applications park in Pending). (`Owner: Your team`.) Source: [[raw/tickets/NXT-70092|NXT-70092]].
5. **A family submits** via the "Submit Forms" link on the short URL (Family Hub), gated by the Forms license. (`Owner: Parent/applicant`.) Or your team enters one from **Eligibility → Forms → Other Forms → Add New Form Application** (the *application-submission* stepper — distinct from the form-type-definition drawer). Source: [[raw/tickets/NXT-71227|NXT-71227]], [[raw/tickets/NXT-69982|NXT-69982]].
6. **The application appears on Other Forms** with a Status; once processed, a Result of Qualified or Unqualified populates. Source: [[raw/tickets/NXT-70440|NXT-70440]].

For the full Forms walk-through, see [[resources/eligibility/forms-long-form-guide.md|Forms in Eligibility — Full Guide]] in this folder.

### Path 4 — CEP (Community Eligibility Provision)

CEP-designated sites serve every student free, regardless of individual application status. From the determination side, that means:

- Students at a CEP site default to a Free reason like "CEP" or a site-CEP variant.
- Applications for students at CEP sites are typically routed to **Pending** by the auto-processing rule (so your team can decide whether to certify them via the application path or rely on CEP). Source: [[raw/tickets/NXT-70092|NXT-70092]].
- Verification has a setting — **Include CEP Sites / Apps** — that controls whether CEP applications participate in sample creation and Section 3 & 4 of the Collection Worksheet. With the setting on, CEP sites are included; with it off (default historically), they're excluded. Source: [[raw/tickets/NXT-68256|NXT-68256]].

If your district has CEP sites, your daily Pending review will routinely include applications you'll choose **not** to process — because the student is already covered by CEP and processing the household application doesn't change their meal pricing.

## Step-by-step (the common path)

### Day 1 — get oriented

1. Log into SchoolCafé and navigate to **Eligibility**. The submenus map to the four paths above plus the cross-cutting pages: Applications, Direct Certification, Forms, Reports, Settings, Verification.
2. Open **Eligibility → Reports**. Run **Eligibility Summary** with the **Detailed** format and today's date — this shows you the current distribution of students across Free / Reduced / Paid and every individual price-type reason. **Compact** groups some reasons under "DC" or "Other"; **Detailed** lists everything separately, which is what you want on day one to see what's actually in your district. Source: [[raw/tickets/NXT-56345|NXT-56345]].
3. Note any reason you don't recognize. Come back to this guide's Concepts → Reasons section. If the reason still isn't documented, that's an SME conversation worth scheduling.

### Daily workflow

1. **Pending Applications + Pending Students review.** See [[resources/eligibility/applications-daily-pending-sop.md|SOP — Daily Pending Applications & Pending Students Review]] for the full step-by-step. Don't let either tab persist across a school day — anything left is a student paying the wrong price tomorrow.
2. **Potential Matches review** (when a recent DC file was imported). See [[resources/eligibility/direct-certification-daily-review.md|SOP — Daily Potential Matches Review]].
3. **Quick spot-check.** Run **Eligibility Status Changes Report** with a one-day date range. This is your audit-trail proof that the day's processing actually moved students. The date filter applies to the **Process Date**. Source: [[raw/tickets/NXT-56318|NXT-56318]].

### Monthly workflow

1. **DC file import.** Most states send monthly. Your team uploads, reviews Potential Matches, runs **DC Counts** for the auditor.
2. **DC Counts report** (Eligibility → Reports → Direct Certification Counts) with multi-site selection if you serve multiple sites.
3. **Eligibility Summary — Detailed format** for the monthly state-required snapshot.

### Annually — Verification

1. **Sampling.** Eligibility → Verification → Sampling. Note the **Student Count Date** and **Application Count Date** columns — Application Count Date = Final Sample Date, Student Count Date = Collection Date. Source: [[raw/tickets/NXT-68256|NXT-68256]].
2. **Collection Worksheet (FNS-742).** Auto-populates with totals from live data. Click **SAVE** to store a PDF snapshot — saved copies appear in the grid below (Generation Date / User / View / Download). See [[resources/eligibility/collection-worksheet-quick-guide.md|Collection Worksheet — Quick Guide]] for the full walkthrough. Source: [[raw/tickets/NXT-68256|NXT-68256]].
3. **Submit to state.** The state's deadline and format vary; saved PDF + the **Eligibility Status Changes** report for the verification window is typically the package.

### Onboarding a new form type (Summer EBT example)

See [[resources/eligibility/forms-long-form-guide.md|Forms in Eligibility — Full Guide]] Step 1, plus [[resources/eligibility/forms-faq.md|Forms FAQ]] Q1, Q3, Q4 for the most common gotchas.

## Examples

### Example 1 — A typical first month for a new manager (`<District A>`)

A new manager joins in mid-August. They run **Eligibility Summary (Detailed)** on day 2 — distribution is 38% Free / 9% Reduced / 53% Paid with "DC MEDICAID", "DC SNAP", "Approved Application", and "Carryover" as the most common reasons. They scan **Pending Applications** (3 rows from the back-to-school online intake bump), work each one with the SOP, verify via **Eligibility Status Changes** that the three are now Processed. The first **DC file** arrives August 28; they import, find 47 Potential Matches, work the queue over three days, confirm 31 / mark 16 Reviewed. Source workflows: [[wiki/workflows/direct-certification.md]], plus the SOPs above.

### Example 2 — Why is this student suddenly Paid? (`<District B>`)

A parent calls asking why their child, who was Free in May, is showing Paid in August. The manager opens **Eligibility Reports → Eligibility Status Changes** with a date range covering May through today, filters by the student's name. The grid shows: Prior Eligibility "Free (Carryover)", New Eligibility "Paid (Default)", Effective Date 08/15. The change is correct — Carryover expired and no new application has been submitted for the new year. The manager calls the parent back and walks them through a Family Hub application. Source: [[raw/tickets/NXT-56318|NXT-56318]].

### Example 3 — Summer EBT pilot ramp-up (`<District C>`)

A director wants Summer EBT live in two weeks. They (1) request the Forms license from Cybersoft Implementation, (2) define the form type with three pilot sites multi-selected, verification = Standard, SSN = Partial, (3) confirm the CEP-site auto-processing rule routes those to Pending (so the pilot team can hand-review), (4) test district-side via Other Forms → Add New Form Application with a fake household, (5) once the license flips, the "Submit Forms" link appears on the short URL and the first three Family Hub applications arrive within 24 hours. Source: [[resources/eligibility/forms-long-form-guide.md|Forms Framework — Full Guide]].

## Edge cases & known issues

- **"Direct Certification" is missing from the Manual Entry dropdown.** By design. DC is File Import only. Source: [[raw/tickets/NXT-60922|NXT-60922]].
- **A DC row reappears as Potential Match after you matched it yesterday.** Secondary matching re-ran because someone edited the student's record. Check Account Management before re-acting. Source: [[raw/tickets/NXT-14223|NXT-14223]].
- **"Unmatched" tab is gone.** It was renamed to **Potential Matches**. Older training material may still use the old name. Source: [[raw/tickets/NXT-15058|NXT-15058]].
- **"Dismissed" is now "Reviewed".** Same rename release as Potential Matches. Source: [[raw/tickets/NXT-15058|NXT-15058]].
- **The "By Direct Certification" report URL changed.** Migrated from Dundas to native HTML; old bookmarks 404. Re-bookmark from the Reports page. Source: [[raw/tickets/NXT-21564|NXT-21564]].
- **A Pending Application can't be submitted if household size doesn't match.** This is the most common Pending Reason on online applications. Source: [[raw/tickets/NXT-71226|NXT-71226]] (Forms stepper).
- **Deleting a Pending Application returns affected students to their previous eligibility.** Confirm what that was before you delete. Source: [[raw/tickets/NXT-5204|NXT-5204]] (More Actions: Delete).
- **The Eco-Disadvantaged % option on the Surveys report was removed.** Two Eco-Dis reports was confusing when surveys were on. Only Income Range remains there. Source: [[raw/tickets/NXT-60134|NXT-60134]].
- **Eligibility Status Changes report's Grade / Site / Patron Status are live values, not historical.** A student who moved sites since the change will show their current site, not the site at the time of the change. Source: [[raw/tickets/NXT-56318|NXT-56318]].
- **The FRE Application Image is Cybersoft-only by default.** Editing it affects every FRE application past and present immediately. If you need a form-specific image change, use Form Image Templates instead. Source: [[raw/tickets/NXT-70453|NXT-70453]].
- **Verification CEP-inclusion setting** toggles whether CEP apps are sampled for Verification. Default historically excludes them; the 2026 update added a setting to include. Source: [[raw/tickets/NXT-68256|NXT-68256]].

## Glossary

- **NXT** — the ticket-key prefix for the Perseus project (the SchoolCafé 2.0 engineering board). Every wikilink like `NXT-15058` references a single Jira issue in `raw/tickets/`.
- **Family Hub** — the parent-facing SchoolCafé surface (online applications, "Submit Forms," account management).
- **Short URL** — the district's public Family Hub URL. Where parents go to submit a meal application or, with the Forms license on, to submit a form.
- **Account Management** — the district-side roster page. Edits here trigger DC secondary matching automatically. Source: [[raw/tickets/NXT-14223|NXT-14223]].
- **FNS-742** — the federal Collection Worksheet form districts submit annually after verification.
- **CEP** — Community Eligibility Provision. Federal program that lets high-poverty schools serve all students free without individual applications.

## Sources

### Wiki

- [[wiki/concepts/Eligibility.md|Eligibility (concept page)]]
- [[wiki/workflows/direct-certification.md|Direct Certification Matching (workflow)]]

### Tickets cited inline above

- [[raw/tickets/NXT-15058.md|NXT-15058 — Potential Matches drawer + rename]]
- [[raw/tickets/NXT-13343.md|NXT-13343 — Scorecard on Matched]]
- [[raw/tickets/NXT-14223.md|NXT-14223 — Secondary matching on student update]]
- [[raw/tickets/NXT-60922.md|NXT-60922 — Remove DC option from Manual Entry]]
- [[raw/tickets/NXT-63982.md|NXT-63982 — DC Counts report multi-select]]
- [[raw/tickets/NXT-21564.md|NXT-21564 — By DC report HTML conversion]]
- [[raw/tickets/NXT-58224.md|NXT-58224 — Elig - Direct Cert custom-report dataset]]
- [[raw/tickets/NXT-5204.md|NXT-5204 — Application Details: Summary & Navigation panel]]
- [[raw/tickets/NXT-7337.md|NXT-7337 — Application Entry: Review conditionals]]
- [[raw/tickets/NXT-66798.md|NXT-66798 — Pending Students with multiple matches]]
- [[raw/tickets/NXT-69982.md|NXT-69982 — Forms Framework: Other Forms page + Form Configuration rename]]
- [[raw/tickets/NXT-70092.md|NXT-70092 — Form Configuration: three tabs + shared page-level access]]
- [[raw/tickets/NXT-70440.md|NXT-70440 — Other Forms grid (ALL and Pending tabs)]]
- [[raw/tickets/NXT-70450.md|NXT-70450 — Add New Form drawer]]
- [[raw/tickets/NXT-70453.md|NXT-70453 — FRE Application Image (Cybersoft-only)]]
- [[raw/tickets/NXT-71227.md|NXT-71227 — Forms license + Forms Template page + Submit Forms short URL line]]
- [[raw/tickets/NXT-68256.md|NXT-68256 — Verification 2026 QoL: Save Collection Worksheet, Include CEP setting]]
- [[raw/tickets/NXT-56345.md|NXT-56345 — Eligibility Summary: Compact vs Detailed]]
- [[raw/tickets/NXT-56318.md|NXT-56318 — Eligibility Status Changes Report]]
- [[raw/tickets/NXT-60134.md|NXT-60134 — Remove Eco Dis % from Surveys report]]

### Sibling guides in this folder

- [[resources/eligibility/direct-certification-guide.md|Direct Certification — Full Guide]]
- [[resources/eligibility/direct-certification-faq.md|Direct Certification — FAQ]]
- [[resources/eligibility/direct-certification-daily-review.md|SOP — Daily Potential Matches Review]]
- [[resources/eligibility/direct-certification-file-import.md|Direct Certification — Import a State DC File]]
- [[resources/eligibility/direct-certification-one-pager.md|Direct Certification — Potential Matches Quick Reference]]
- [[resources/eligibility/forms-long-form-guide.md|Forms in Eligibility — Full Guide]]
- [[resources/eligibility/forms-faq.md|Forms — FAQ]]
- [[resources/eligibility/applications-daily-pending-sop.md|SOP — Daily Pending Applications & Pending Students Review]]
- [[resources/eligibility/eligibility-reports-quick-reference.md|Eligibility Reports — Quick Reference]]
- [[wiki/guides/eligibility/forms-quick-guide.md|Forms — Quick Guide]]
- [[wiki/guides/eligibility/collection-worksheet-quick-guide.md|Collection Worksheet — Quick Guide]]
- [[wiki/guides/eligibility/eligibility-reports-quick-guide.md|Eligibility Reports — Quick Guide]]
- [[wiki/guides/eligibility/view-and-modify-applications-quick-guide.md|View & Modify Applications — Quick Guide]]
