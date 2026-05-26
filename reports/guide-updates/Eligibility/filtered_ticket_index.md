# Filtered Eligibility tickets — index

- **Source:** `C:\Users\rahul.mehta\Downloads\Perseus Jira (2).csv` (Perseus Jira export, 449 data rows)
- **Cutoff date:** 2024-05-13 (last 2 years from 2026-05-13)

## Filters applied

1. Status Category = `Done`
2. Resolved date >= 2024-05-13
3. At least one `Components` column contains "eligibility" (case-insensitive substring)
4. Resolution NOT IN: `Won't Do`, `Duplicate`, `Cannot Reproduce`, `Not a Bug`
5. Description and Acceptance Criteria not both empty

## Filter funnel

- Total data rows scanned: **449**
- Rejected (Status Category != Done): 88
- Rejected (Resolved date missing or < 2024-05-13): 300
- Rejected (no Eligibility component): 0
- Rejected (blocked resolution): 0
- Rejected (Description and AC both empty): 0
- **Retained: 61**

## Retained tickets (newest first)

| Key | Resolved | Summary |
|---|---|---|
| NXT-70440 | 2026-05-12 | Eligibility - Other Forms - Display submitted Form Applications in Grid |
| NXT-68256 | 2026-05-05 | Elig - Verification - 2026 QoL Updates, Include CEP Setting Update |
| NXT-71226 | 2026-05-04 | Eligibility - Other Forms - (Part 1) Complete 'Add New Form Application' button functionality |
| NXT-71227 | 2026-04-28 | SchoolCafé - Forms - (Part 1) Family Hub-related changes for Forms Licensing, Forms Template |
| NXT-66821 | 2026-04-15 | Elig - DC - Extensions - Extending a different DC Type to the same student, blocking inactive Source students |
| NXT-70453 | 2026-04-14 | Eligibility - Configuration - FRE Application Image - New page to modify FRE image |
| NXT-70451 | 2026-04-14 | Eligibility - Forms - Form Configuration - Form Image Templates Tab - Add new image templates |
| NXT-70450 | 2026-04-14 | Eligibility - Forms - Form Configuration - Forms Tab - Add New Form to grid |
| NXT-70452 | 2026-03-31 | Eligibility - Forms - Form Configuration - Form Image Templates Tab - Template Grid |
| NXT-70092 | 2026-02-23 | Eligibility - Forms Framework - Form Configuration - Add ability to add/update Forms (UI) |
| NXT-69982 | 2026-02-23 | Eligibility - Forms Framework - Add/update necessary operations, and permissions  |
| NXT-66798 | 2025-10-28 | Elig - Apps - Pending Students with multiple matches |
| NXT-63985 | 2025-08-25 | Elig - Reports - Income Survey - Page / Report Updates |
| NXT-63980 | 2025-08-22 | Elig - Reports - Application Counts - Page / Report Updates |
| NXT-63984 | 2025-08-18 | Elig - Reports - Eligibility Summary - Page / Report Updates |
| NXT-63983 | 2025-08-18 | Elig - Reports - Eco Dis % - Page / Report Updates |
| NXT-63982 | 2025-08-18 | Elig - Reports - Direct Certification Counts - Page / Report Updates |
| NXT-63981 | 2025-08-18 | Elig - Reports - CEP Identified Students - Page / Report Updates |
| NXT-63628 | 2025-07-28 | Elig - Optional Benefits - Allow next Academic Year to be editable, Copy feature |
| NXT-63753 | 2025-07-08 | FH - FRE Apps - SSN question for Students at CEP Sites |
| NXT-60922 | 2025-06-10 | Elig - Direct Certs - Remove 'Direct Certification' as an option for Manual Entry |
| NXT-60492 | 2025-06-10 | Elig - Verification - QoL Updates, Include CEP Setting, Minnesota Reporting |
| NXT-60920 | 2025-05-27 | FO - Print/Email - Messaging Update (FD #272290) |
| NXT-60490 | 2025-05-12 | Elig - Applications - Privacy Act Statement - App Images, Field, Settings |
| NXT-59832 | 2025-04-23 | DMF - Migrate Verification tables in Eligibility DB for Front office migration  |
| NXT-58224 | 2025-04-23 | FO - Datasets - Eligibility - Direct Certification |
| NXT-60134 | 2025-04-11 | Elig - Reports - Surveys - Remove the Eco Dis % report from the Surveys report |
| NXT-58190 | 2025-04-09 | FO - Datasets - Eligibility - Applications |
| NXT-58222 | 2025-03-31 | FO - Datasets - Eligibility - Surveys |
| NXT-58537 | 2025-03-24 | Upgrade all Frontoffice Modules to .Net 8.0 |
| NXT-27577 | 2025-02-24 | Family Hub - School Menus - Get display order for each menu published from SchoolCafé |
| NXT-55697 | 2025-02-12 | Elig - Application processing on same day as Carryover Expiration and Adverse Action |
| NXT-54190 | 2025-02-12 | Elig - Forms - Applicant Information column, filters (FD: 254416) |
| NXT-56345 | 2025-02-11 | Elig - Summary Report - Detailed option to include all price type reasons (FD 265473) |
| NXT-56318 | 2025-02-03 | Elig - Eligibility Change Report (FD 265260) |
| NXT-56281 | 2025-01-28 | Elig - Scheduler framework update for Verification Auto-Notify |
| NXT-55588 | 2025-01-28 | Elig - Scheduler framework update for Automatic DC Notifications |
| NXT-58191 | 2025-01-20 | FO - Datasets - AcctMgt_StudentData - New columns (FD: 268513) |
| NXT-55012 | 2025-01-14 | Elig - Notifications - Carryover to show Active students only (FD: 259884) |
| NXT-54189 | 2025-01-06 | Elig - Notifications (Apps/Surveys) - Search filters on columns, Student ID # field (FD 256633) |
| NXT-54692 | 2024-12-02 | FO - Grids - Manage Views - Enable the Save View options (FD #260053, 260382) |
| NXT-54816 | 2024-11-19 | Elig - Applications - Use all Pending Reasons for Online Apps (FD: 254409) |
| NXT-56185 | 2024-11-15 | Elig/System - Remove the DCMCHSTUID system setting |
| NXT-53570 | 2024-10-31 | AcctMgt/System - Random PINs for Imports (FD: #251615) |
| NXT-55590 | 2024-10-23 | Elig/System - DC Matching - Default system setting for Student ID against SSN |
| NXT-55413 | 2024-10-23 | Sys - Templates - Language usage for Fields - Carryover Expiration + Correction Letter |
| NXT-54075 | 2024-10-02 | Elig - Potential Matches - Option to hide lesser matches (FD 255896) |
| NXT-53985 | 2024-09-16 | Sys - Templates - Language usage for Fields - Direct Certification |
| NXT-53984 | 2024-09-16 | Sys - Templates - Language usage for Fields - Direct Approval |
| NXT-49465 | 2024-09-16 | FO - Document Center - Update Verification letters to use background process |
| NXT-53414 | 2024-08-30 | Elig - DC Precedence - Merge tables, label updates |
| NXT-53982 | 2024-08-21 | Sys - Templates - Language usage for Fields - Approval/Denial Letter |
| NXT-53571 | 2024-08-12 | FH - Applications - Controls for required fields on applicant data (FD: 253686) |
| NXT-52656 | 2024-08-09 | AcctMgt - Reminders - Preview Letter option, select checkboxes |
| NXT-52864 | 2024-08-07 | FH - Online Apps - Mandatory SSN Controls |
| NXT-49684 | 2024-08-07 | FO - Document Center - Workflow update for Notifications > Direct Cert |
| NXT-52653 | 2024-08-05 | Elig - Dashboard - Potential Matches CTA Update |
| NXT-51194 | 2024-07-24 | FO - Document Center - Update Income Surveys to use background process, Page Updates |
| NXT-49691 | 2024-07-23 | FO - Document Center - Workflow update for Notifications > Applications |
| NXT-51520 | 2024-07-02 | FO - Documents Center - Workflow update for Notifications > Carryover |
| NXT-48689 | 2024-05-21 | Family Hub - Homepage - Sign in with Apple |
