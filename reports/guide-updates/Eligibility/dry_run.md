# Eligibility guide reconciliation — dry run

- **Date:** 2026-05-13
- **Module:** SC Eligibility
- **Guide scope:** `raw/guides/markdown/SC/Eligibility/Quick-Guide/*.md` (22 files, GUIDE-036 through GUIDE-057).
- **Authority:** the 61 filtered tickets in `reports/guide-updates/Eligibility/filtered_ticket_index.md` (Status Category = Done, Resolved on/after 2024-05-13, Eligibility component, non-empty body, valid resolution).
- **Supplementary context (non-authoritative):** `wiki/concepts/Eligibility.md`, `wiki/workflows/direct-certification.md`.
- **No edits applied.** This is dry-run only.

## Headline

**6 proposed changes across 3 guide files.** All six rest on filtered-ticket evidence; 5 are high confidence and 1 is medium. The remaining 19 guide files were reviewed and no changes are proposed — either no filtered tickets touched the topic, or the tickets that did touch the topic added new functionality the guide is silent on (gaps, not contradictions) or made backend-only changes.

## Proposed changes

### Change 1 — `GUIDE-047` — Collection Worksheet: PDF button replaced with Save button + saved-copies grid

- **File:** `raw/guides/markdown/SC/Eligibility/Quick-Guide/GUIDE-047-collection-worksheet-quick-guide.md`
- **Confidence:** high
- **Original passage (lines 38-41):**

  > Various Document icons are available throughout the worksheet; you can click on them to view the Collection Report. This information can be downloaded.
  > Click the PDF button to export the form.

- **Proposed replacement:**

  > Various Document icons are available throughout the worksheet; you can click on them to view the Collection Report. This information can be downloaded.
  > Click the SAVE button to store a PDF copy of the worksheet. Saved copies appear in a grid below the worksheet with Generation Date, User, and Actions (View, Download), so you can retrieve previously saved versions later.

- **Evidence:**
  - **NXT-68256** (resolved 2026-05-05): "PDF button adjusted into a Save button / Show a grid of saved copies / Columns: Generation Date, User, Actions / Actions: View, Download"
  - AC on the same ticket: "PDF button replaced with a Save button. / Save Report feature added, stores a backup in blob / Grid added to show saved reports."
- **Rationale:** The export button on the Collection Worksheet was replaced with a Save button that persists PDFs for later retrieval through a new saved-copies grid; the guide still describes the old direct-PDF-export behavior.

---

### Change 2 — `GUIDE-057` — Income Surveys Report: remove Economically Disadvantaged Report sub-option

- **File:** `raw/guides/markdown/SC/Eligibility/Quick-Guide/GUIDE-057-eligibility-reports-quick-guide.md`
- **Confidence:** high
- **Original passage (lines 97-112):**

  > Income Surveys Report
  > The Income Surveys Report provides the percentage of economically disadvantaged students, as well as the number of surveys broken down by household size and income data.
  > 1. Select Income Surveys
  > The Income Survey Report page displays.
  > Economically Disadvantaged Report
  > The Economically Disadvantaged Report will only show income survey data based on patron survey submissions. The count on this report is based only on income surveys.
  > 1. Select the Economically Disadvantaged Report Type
  > 2. Select the Site(s) as needed
  > 3. Click the GENERATE button to generate the report
  > 4. View the report results
  > Click the DOWNLOAD button to export the report as a PDF or EXCEL file.
  > Click the X to close the report.
  > Click the BACK button to return to the Eligibility Reports page.

- **Proposed replacement:**

  > Income Surveys Report
  > Data on the number of surveys broken down by household size and income data.
  > 1. Select Income Surveys
  > The Income Survey Report page displays.

  (Then continue directly to the "Income Range Count Report" subsection that already follows in the guide.)

- **Evidence:**
  - **NXT-60134** (resolved 2025-04-11) — Description: "Remove the Eco DIsadvantaged % option from the Surveys report / Income Range report is always available / Update the text on the reports landing page... OLD: Provides the percentage of economically disadvantaged students, as well as the number of surveys broken down by household size and income data. NEW: Data on the number of surveys broken down by household size and income data."
  - AC: "Eco Dis % report removed as an option in the Surveys report page. / Income Range report is always available / Eligibility Reports landing page text updated."
- **Rationale:** The Economically Disadvantaged % option was removed from the Income Surveys report; only Income Range Count remains, and the landing-page description was rewritten. The guide still describes the removed sub-option as a current selection. (Note: the leading description paragraph rewrite borders on "customer-facing phrasing," but it is included here because the same ticket gives the exact new text and the surrounding section structure has to change anyway to remove the deleted sub-option.)

---

### Change 3 — `GUIDE-057` — Eligibility Summary Report: add Compact / Detailed selection step

- **File:** `raw/guides/markdown/SC/Eligibility/Quick-Guide/GUIDE-057-eligibility-reports-quick-guide.md`
- **Confidence:** high
- **Original passage (lines 80-89):**

  > Eligibility Summary Report
  > The Eligibility Summary Report displays the total number of all students, broken down by site, eligibility status, and eligibility reason.
  > 1. Select Eligibility Summary
  > The Eligibility Summary Report page displays.
  > 2. Select the Site(s) as needed
  > 3. Pick the Date as needed
  > 4. Click the GENERATE button to generate the report
  > 5. View the report results

- **Proposed replacement:**

  > Eligibility Summary Report
  > The Eligibility Summary Report displays the total number of all students, broken down by site, eligibility status, and eligibility reason.
  > 1. Select Eligibility Summary
  > The Eligibility Summary Report page displays.
  > 2. Select the Site(s) as needed
  > 3. Pick the Date as needed
  > 4. Choose the report format: Compact (the existing summary, with some price-type reasons grouped under "DC" or "Other") or Detailed (every individual price-type reason listed separately).
  > 5. Click the GENERATE button to generate the report
  > 6. View the report results

- **Evidence:**
  - **NXT-56345** (resolved 2025-02-11) — Description: "Add a 'Compact' and 'Detailed' option to the Summary report. Compact → Existing report. Detailed → Put in every single price type reason instead of merging some together under 'DC' or 'Other'."
  - AC: "'Detailed' version added that includes all price type start reasons / 'Compact' version available - the current report / User can choose between both formats"
- **Rationale:** A new Compact/Detailed selector was added before report generation. The guide's current step list omits this selection.

---

### Change 4 — `GUIDE-057` — Add new "Eligibility Status Changes" report section

- **File:** `raw/guides/markdown/SC/Eligibility/Quick-Guide/GUIDE-057-eligibility-reports-quick-guide.md`
- **Confidence:** high
- **Original passage:** _None — this report is missing from the guide entirely._ Guide currently lists, in order: Application Counts, CEP Identified Students, Direct Certification Counts, Eligibility Summary, Income Surveys, Roster. The new report should be inserted between Eligibility Summary and Income Surveys.
- **Proposed replacement (new subsection to add):**

  > Eligibility Status Changes Report
  > Shows changes in student eligibility with a variety of search filters. The date range filter applies to the Process Date. Inactive eligibility lines are not shown.
  > 1. Select Eligibility Status Changes
  > The Eligibility Status Changes page displays.
  > 2. Select the Site(s) as needed (multi-select)
  > 3. Set the Date Range using the date range selector
  > 4. Set the Patron Status filter (Active is the default; Inactive and All are also available)
  > 5. Optionally select "Only show Last Eligibility Change" to display only one change per account across the date range
  > 6. Click APPLY to generate the report
  > 7. View the report results in the grid (default columns: ID #, First Name, Last Name, Grade, Site, Prior Eligibility, New Eligibility, Effective Date, Process Date)
  > Click EXCEL to export the results.
  > Click the BACK button to return to the Eligibility Reports page.
  > Note: Grade, Site, and Patron Status reflect current state, not historical values.

- **Evidence:**
  - **NXT-56318** (resolved 2025-02-03) — Description: "New Report for Eligibility: Name: Eligibility Status Changes / Search filters: Site picker, multi-select / Date picker (new date range selector) / Patron Status: Active (Default)/Inactive/All / Report options: Only show Last Eligibility Change ... Default view columns: ID #, First Name, Last Name, Grade, Site, Prior Eligibility, New Eligibility, Effective Date, Process Date."
  - AC: "Status Change report page added to Eligibility Reports Landing page / Status Change report added / Search options for site, date / Grid results / Grid can be downloaded"
- **Rationale:** A new report was added to the Eligibility Reports landing page; the guide doesn't list it.

---

### Change 5 — `GUIDE-037` — Pending Students "View Match Details": describe multi-match selection

- **File:** `raw/guides/markdown/SC/Eligibility/Quick-Guide/GUIDE-037-view-and-modify-applications-quick-guide.md`
- **Confidence:** high
- **Original passage (lines 227-232):**

  > View Match Details
  > A View icon displays for a student once a match is identified for that pending student.
  > 1. Click the View (Paper) icon for the desired student
  > The Match Details slide deck displays.
  > 2. Compare the Application Details to the Matched Student
  > Click the X to close the slide deck and return to the PENDING STUDENTS tab.

- **Proposed replacement:**

  > View Match Details
  > A View icon displays for a pending student once at least one potential match has been identified.
  > 1. Click the View (Paper) icon for the desired student
  > The Match Details slide deck displays.
  > 2. Compare the Application Details to the Matched Student(s). The Match Details screen shows each potential student's Status (Active/Inactive) and current Eligibility with Basis (for example, "Free (DC MEDICAID)").
  > 3. If multiple potential students are shown, you must select one using the Match button before continuing.
  > Click the X to close the slide deck and return to the PENDING STUDENTS tab.

- **Evidence:**
  - **NXT-66798** (resolved 2025-10-28) — Description: "On the View Match window: You are viewing the submitted information from the Form and details from at least 1 potential student. If multiple students are shown, select one with the Match button to proceed. ... Add the following lines for Student Details: Status (Show Active or Inactive); Eligibility (Show Free/Reduced/Paid and Basis. Example: Free (DC MEDICAID))."
  - AC: "User can complete Pending Student matches with multiple results / User must select 1 of the potential matches to proceed / User can see Status and Eligibility in the Match Details screen"
- **Rationale:** The View Match window now supports multi-match scenarios with an explicit selection step and displays per-student Status and Eligibility (with Basis). The guide describes only the single-match, read-only path.

---

### Change 6 — `GUIDE-037` — Pending Students "Search for Students": clarify what MATCH does (deferred update)

- **File:** `raw/guides/markdown/SC/Eligibility/Quick-Guide/GUIDE-037-view-and-modify-applications-quick-guide.md`
- **Confidence:** medium (original wording is ambiguous; the most natural reading conflicts with the ticket, but a charitable reading is consistent with it)
- **Original passage (lines 213-219):**

  > 3. Click the SELECT STUDENT button on the row of the desired student
  > The Compare Details section displays.
  > 4. Compare the Application Details to the Matched Student
  > 5. Click the MATCH button at the bottom right corner to update the student's information
  > A successful match message displays.
  > A green checkmark displays in the Matched Status column on the Applications page.

- **Proposed replacement:**

  > 3. Click the SELECT STUDENT button on the row of the desired student
  > The Compare Details section displays.
  > 4. Compare the Application Details to the Matched Student
  > 5. Click the MATCH button at the bottom right corner to link the selected student to the pending row.
  > A successful match message displays.
  > A green checkmark displays in the Matched Status column on the Applications page. The match link is created, but the application's eligibility and details are not updated until Process Matches is run on the PENDING STUDENTS tab.

- **Evidence:**
  - **NXT-66798** (resolved 2025-10-28) — Description: "All scenarios link a Pending Student to an actual Account (personid). We need to track the link. Application Details should *not* be updated as part of the search / manual matching. User needs to click Process Matches: to have the Application Details update."
  - AC: "Application Details is only updated after Process Matches is executed / Once Matches are processed: student is linked to the app / student eligibility updated accordingly"
- **Rationale:** The MATCH button in Search & Match Student now only creates a link to the account; eligibility and Application Details update only after the user runs Process Matches. The current wording ("to update the student's information") most naturally reads as immediate-update, which is the behavior the ticket explicitly removed. Confidence is medium because the original phrase is loose enough that it could be defended as describing the link itself rather than the application's data.

## Files reviewed, no change proposed

| File | Filtered tickets that touched the topic | Why no change |
|---|---|---|
| GUIDE-036-add-applications-quick-guide.md | NXT-60490 (Privacy Act on app images), NXT-52864 / NXT-63753 (FRENOSSN setting controls SSN visibility), NXT-54816 (online-app pending reasons) | Privacy Act change affects the rendered application image, not the wizard steps the guide describes. FRENOSSN behavior is conditional on a backend setting and the guide describes the default-on flow; the ticket adds an alternate flow but doesn't contradict the existing description. NXT-54816 changes online-app pending-reason population, which is a Family Hub flow rather than this Manual Entry guide. |
| GUIDE-037-view-and-modify-applications-quick-guide.md | NXT-66798 (Pending Students multi-match), NXT-54190 (new applicant-info columns), NXT-54816 (full pending-reasons range) | Two contradictions proposed above (Changes 5 and 6). The new applicant-info columns (Phone/Email/Address) and Student ID column are hidden by default in custom views and the guide's filter-list description doesn't claim to be exhaustive, so the omissions are gaps not contradictions. NXT-54816 adds richer pending-reason content but the guide's "view the Pending Reason in the Details section" line stays accurate. |
| GUIDE-038-application-processing-quick-guide.md | NXT-49691 (Notifications > Apps moved through Document Center), NXT-60920 (Email/Print success messaging) | The Document Center / background-process flow is an additional path for >20-letter batches; the guide's existing flow still works for single-application processing and doesn't claim print is always immediate. NXT-60920's specific success-message text is customer-facing phrasing the guide doesn't quote. |
| GUIDE-039-add-income-surveys-quick-guide.md | NXT-58222 (Surveys dataset), NXT-53571 (Phone/Email required-field controls), NXT-52864/NXT-63753 (SSN controls — apps not surveys) | Dataset addition is backend custom-reports, not the survey-add wizard. NXT-53571 governs Family Hub online-survey field requirements; this guide is for Manual Entry inside the Eligibility module, which doesn't enforce those settings. |
| GUIDE-040-view-income-surveys-quick-guide.md | NXT-54190 (new applicant-info columns), NXT-51194 (Surveys notifications → Document Center) | Same analysis as GUIDE-037 — added columns hidden by default, guide's filter list is non-exhaustive. The Document Center workflow applies to bulk notifications, not the View/Edit survey flow this guide covers. |
| GUIDE-041-processing-quick-guide.md | _(none in the filtered set)_ | No filtered ticket touches the Processing batch session review screen. |
| GUIDE-042-sampling-quick-guide.md | NXT-68256 (Sampling page new columns), NXT-60492 (Include CEP Sites setting, Minnesota section, retain search options) | NXT-68256 adds Student Count Date / Application Count Date columns to the grid; the guide doesn't enumerate grid columns so it doesn't contradict. NXT-60492's Include CEP Sites setting affects Collection Worksheet counts and (per the discussion note on the ticket) sample-generation behavior was already including CEP sites — the guide's "Sites operating under special provision programs (CEP/Provision II) should remain selected" instruction is not contradicted. Minnesota 4.1 section is worksheet content, not a sampling step. |
| GUIDE-043-tracking-quick-guide.md | NXT-56281 (Verification Auto-Notify in Recurring Notices), NXT-60492 (retain search options), NXT-49465 (Verification letters background process), NXT-55697 (carryover/adverse-action interaction) | The Auto-Notify toggle still lives on the Tracking page exactly as the guide describes (the ticket moves the underlying job into a new Recurring Notices tab but preserves the toggle UX). Retain-search-options is a returning-from-Details behavior the guide doesn't claim either way. Background-process flow for >20 letters is an alternate path; the guide's generic "confirmation response appears" is not contradicted. NXT-55697 adds a backend setting that the guide doesn't reference. |
| GUIDE-044-tracking-forms-quick-guide.md | NXT-49465 (Verification letters background process) | Same as GUIDE-043 — background path is additive, guide's existing print description still applies for small batches. |
| GUIDE-045-inactive-applications-quick-guide.md | _(none in the filtered set)_ | No filtered ticket touches the Inactive Applications report. |
| GUIDE-046-backdated-applications-quick-guide.md | _(none in the filtered set)_ | No filtered ticket touches the Backdated Applications report. |
| GUIDE-047-collection-worksheet-quick-guide.md | NXT-68256 (PDF→Save, saved-copies grid), NXT-60492 (single-download export, date-stamped column headings, MN section 4.1) | One contradiction proposed above (Change 1). The single-download export is consistent with the existing "Click the PDF button to export the form" line (singular form). Date-stamped column headings and Minnesota 4.1 are worksheet content rendered server-side, not steps the guide describes. |
| GUIDE-048-direct-certification-files-quick-guide.md | NXT-60922 (DC removed from Manual Entry Type dropdown), NXT-53414 (DC Precedence merge), NXT-56185 / NXT-55590 (DCMCHSTUID setting), NXT-58224 (DC dataset) | The guide describes the Manual Entry Type dropdown as "Select an approval Type from the dropdown" without enumerating options, so NXT-60922's removal of one option isn't directly contradicted. DC Precedence and DCMCHSTUID are backend configuration the guide doesn't reference. Dataset is custom-reports. |
| GUIDE-049-direct-certification-matched-quick-guide.md | _(no filtered ticket directly touches the Matched-tab page behavior)_ | Match Review / Comparison Scorecard / Unmatch flow described in the guide is consistent with all DC-related filtered tickets I reviewed. |
| GUIDE-050-direct-certification-potential-matches-quick-guide.md | NXT-54075 (Show Same/Lesser Benefits toggle), NXT-52653 (Dashboard CTA count fix), NXT-54692 (Save View on Potential Matches Manage Views) | The new "Show Same/Lesser Benefits" toggle and Save View feature are additive UI controls; the guide's filter description ("Select from the Points Filters") doesn't claim to be exhaustive and doesn't contradict them. NXT-52653 is a Dashboard bug fix, outside this guide's scope. |
| GUIDE-051-direct-certification-extensions-quick-guide.md | NXT-66821 (re-extend on DC Type change, block inactive source) | Scenario B (block inactive source students) is consistent with the guide's line "Eligible active students display in the table below" on the SEARCH & REVIEW tab. Scenario A (re-extension on DC Type change) is a backend-relaxation that the guide doesn't speak to either way. |
| GUIDE-052-direct-certification-file-search.md | _(none in the filtered set)_ | No filtered ticket touches DC File Search. |
| GUIDE-053-applications-notifications-quick-guide.md | NXT-49691 (Document Center link/Back/background flow), NXT-54189 (Student ID column), NXT-60920 (Email/Print success messaging), NXT-53982 (Approval/Denial Letter language fields) | Document Center additions are alternate-path UI, not a contradiction of the existing inline-notify flow. The Student ID column is a grid column that the guide doesn't enumerate. NXT-60920 specifies success-message text the guide doesn't quote. NXT-53982 affects letter generation, not the workflow the guide describes. |
| GUIDE-054-income-surveys-notifications-quick-guide.md | NXT-51194 (Surveys notifications → Document Center), NXT-54189 (Student ID column) | Same analysis as GUIDE-053 — Document Center additions and grid columns are gaps not contradictions. |
| GUIDE-055-direct-certification-notifications-quick-guide.md | NXT-49684 (DC notifications Document Center, Individual/Household format), NXT-55588 (Automatic DC moved to Recurring Notices, AUTODCNTFY removed), NXT-53985 / NXT-53984 (DC Letter / Direct Approval Letter language fields) | The Individual/Household letter-format selector from NXT-49684 is already present in the guide. Document Center link/Back button are additive UI. NXT-55588 moves an automated job into a new Recurring Notices tab but doesn't change the manual-notification flow this guide describes; AUTODCNTFY was a backend setting. NXT-53985 / 53984 are letter-generation changes the guide doesn't speak to in detail (the guide's existing "displayed in the student's selected language if an applicable language template is available" line is consistent). |
| GUIDE-056-carryover-notifications-quick-guide.md | NXT-55012 (Carryover sends only to Active students), NXT-55413 (Carryover Expiration Letter language fields), NXT-51520 (Carryover notifications → Document Center) | NXT-55012 narrows the search/send population to Active students — the guide doesn't claim inactive students are included, so the existing description is silent rather than contradicted. NXT-55413 affects letter generation. Document Center additions are additive UI. |
| GUIDE-057-eligibility-reports-quick-guide.md | NXT-63980 / 63981 / 63982 / 63983 / 63984 / 63985 (multi-select Site, new date picker on six reports), NXT-60134 (Eco Dis % removal), NXT-56345 (Compact/Detailed), NXT-56318 (Eligibility Status Changes), NXT-54692 (Save View on Roster) | Three contradictions proposed above (Changes 2, 3, 4). The multi-select Site upgrades are consistent with the guide's existing "Select the Site(s) as needed" wording. The date-picker swap is a component change with no surface contradiction in the guide's "Pick the Date as needed" wording. Save View on Roster's Manage Views is an additive feature the guide doesn't enumerate. |

## Tickets in the filtered set that didn't drive any guide change

These filtered tickets weren't a basis for proposed changes — either backend-only, outside the 22 guide files' scope, or covered already:

- **NXT-70440, NXT-71226, NXT-71227, NXT-70450, NXT-70451, NXT-70452, NXT-70453, NXT-70092, NXT-69982** — the entire Forms / Other Forms / Form Configuration / FRE Application Image framework (Summer EBT, Form Image Templates, Auto-Processing Rules tab, "Submit Forms" on Family Hub short URL, etc.). No existing guide in the 22-file set covers this framework, so there's nothing to reconcile against; this would be net-new guide authoring, out of scope for a reconciliation pass.
- **NXT-58224, NXT-58190, NXT-58222, NXT-58191** — new datasets for Custom Reports (DC, Applications, Surveys, AcctMgt_StudentData). Custom-reports surface is not in the 22-file guide set.
- **NXT-58537, NXT-59832** — backend infrastructure (.NET 8.0 upgrade, Verification DB migration).
- **NXT-53570** — Random PINs configuration in Account Management, not Eligibility guide surface.
- **NXT-52656** — AcctMgt Reminders page changes (checkbox column, Preview Letter, default 10 results). Not in the Eligibility guides.
- **NXT-48689, NXT-27577** — Family Hub features (Sign in with Apple, school menu display order). Not in the Eligibility guides.
- **NXT-63628** — Optional Benefits future-year edit + copy. Configuration page change, not in the 22-file guide set.
- **NXT-55697** — Carryover/Adverse Action interaction backend setting. No directly affected user-facing step in the guides.

## Notes on this pass

- I treated "workflow step added/removed" as in scope (Changes 3 and 4 add a step / a whole report). I did **not** treat additive UI controls (Document Center link, Recurring Notices tab, Save View, applicant-info columns hidden by default, etc.) as workflow-step-added contradictions, because the guides describe complete-as-written flows that still work and don't claim to be exhaustive.
- I treated label-only changes as out of scope per the rule, but Change 1 (PDF→Save) is in scope because the underlying behavior is different (PDFs are stored and retrievable, not just downloaded).
- Change 6 is the only medium-confidence item; the rest are high. If you'd rather see only high-confidence proposals, drop Change 6.
- The "wiki silent" status from the previous pass is no longer the bottleneck — tickets, not the wiki, drove every proposed change here.
