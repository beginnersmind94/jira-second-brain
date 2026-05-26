---
id: GUIDE-057
title: "Eligibility Reports Quick Guide"
platform: "SC"
module: "Eligibility"
content_type: "Quick Guide"
source_url: "https://s3.us-east-1.amazonaws.com/docs.schoolcafe.com/Eligibility/Reports_Quick_Guide.pdf"
local_pdf: "raw/guides/pdf/SC/Eligibility/Quick-Guide/GUIDE-057-eligibility-reports-quick-guide.pdf"
curated_against_raw_sha: "14eb954c701abead"
curated_against_raw_at: "2026-05-18T20:39:44+00:00"
last_reviewed_by: ""
status: "needs_initial_review"
---

# Eligibility Reports Quick Guide

> Seeded from the raw extraction. Edit freely. When the raw drifts, review the diff and update this file, then mark it reviewed with `python scripts/mark_guide_reviewed.py GUIDE-057`.

Eligibility Reports contain data regarding students’ current Eligibility Statuses and Eligibility changes.
Users can access the reports at any point during the school year.

Eligibility reports run on PowerBI. The earlier HTML reports are being phased out.
Across these reports, applicable dropdowns now accept multiple selections and the date selector has been updated. The reports interpret the selected parameters when generating output, and the Report Criteria section reflects them.

## Application Counts Report
The Application Counts Report lists the total number of all applications, broken down by eligibility status and eligibility reason.
1. Select Application Counts
   The Application Counts Report page displays.
2. Select the Site(s) as needed
3. Pick the Date as needed
4. Click the GENERATE button to generate the report
5. View the report results
   Click the DOWNLOAD button to export the report as a PDF or EXCEL file.
   Click the X to close the report.
   Click the BACK button to return to the Eligibility Reports page.

## CEP Identified Students Report
The CEP Identified Students Report shows students who have been CEP identified as of a given date.
- Summary: number of directly certified students and total student count for each site.
- Detailed: lists which students are directly certified.
1. Select CEP Identified Students
   The CEP Identified Students page displays.
2. Select the Site(s) as needed
3. Select the As of Date as needed (defaults to 04/01 of the current year; any date can be picked)
4. Select the Options (Summary or Detailed)
5. Click the POWERBI (BETA) button to generate the report
6. View the report results
   The Summary report shows Identified Percentage and the Claiming Percentage at the standard 1.6× multiplier.
   Click EXPORT to export the report into various file formats.
   Click the X to close the report.
   Click the BACK button to return to the Eligibility Reports page.

## Direct Certification Counts Report
The Direct Certification Counts Report lists eligibility totals based on the Direct Certification.
1. Select Direct Certification Counts, The Direct Certification Counts Report page displays.
2. Select the Site(s) as needed
3. Pick the Date as needed
4. Click the GENERATE button to generate the report
5. View the report results
   Click the DOWNLOAD button to export the report as a PDF or EXCEL file.
   Click the X to close the report.
   Click the BACK button to return to the Eligibility Reports page.

## Eligibility Summary Report
The Eligibility Summary Report displays the total number of all students, broken down by site, eligibility status, and eligibility reason.
1. Select Eligibility Summary
   The Eligibility Summary Report page displays.
2. Select the Site(s) as needed
3. Pick the Date as needed
4. Enable the percentages option if you want the report to show percentages alongside counts (export reflects the option)
5. Choose the report format: Compact (the existing summary) or Detailed (breaks grouped categories into individual price-type start reasons, for example splitting the DC column into separate DC types)
6. Click the GENERATE button to generate the report
7. View the report results
   Click the DOWNLOAD button to export the report as a PDF or EXCEL file.
   Click the X to close the report.
   Click the BACK button to return to the Eligibility Reports page.

## Eligibility Status Change Report
The Eligibility Status Change Report shows eligibility changes over a selected time frame. You can filter to only the latest change per student.
1. Select Status Change on the Eligibility Reports landing page
2. Select Site and date range
3. Click the button to generate the report
4. View the grid; download the grid as needed
   Filters are available on specific columns, and Manage Views is supported.

## Income Surveys Report
The Income Surveys Report provides the percentage of economically disadvantaged students, as well as the number of surveys broken down by household size and income data.
1. Select Income Surveys
   The Income Survey Report page displays.

## Economically Disadvantaged Report
The Economically Disadvantaged Report will only show income survey data based on patron survey submissions. The count on this report is based only on income surveys.
1. Select the Economically Disadvantaged Report Type
2. Select the Site(s) as needed
3. Click the GENERATE button to generate the report
4. View the report results
   Click the DOWNLOAD button to export the report as a PDF or EXCEL file.
   Click the X to close the report.
   Click the BACK button to return to the Eligibility Reports page.

## Income Range Count Report
The Income Range Count Report will show counts based on the household size and eligibility (Free, Reduced, and Paid).
1. Select the Income Range Count Report Type
2. Select the Site(s) as needed
3. Click the GENERATE button to generate the report
4. View the report results
   Click the DOWNLOAD button to export the report as a PDF or EXCEL file.
   Click the X to close the report.
   Click the BACK button to return to the Eligibility Reports page.

## Roster Report
The Roster Report allows users to generate a customized view of students using various filters.
1. Select Roster
   The Roster Report page displays.
2. Enter the As of Date as needed
3. Select the Site Code/Site Name as needed
4. Select the Grade as needed
5. Select the Eligibility as needed
6. Select the Basis as needed
7. Enter the Birth Date as needed
8. Click the APPLY button to generate the report
9. View the report results
   The report includes First Name, Middle Name, and Last Name columns. They are off by default; enable them under Manage Views. The combined Student Name column remains available.
   Click the EXCEL button to export the report.
   Click the BACK button to return to the Eligibility Reports page.
