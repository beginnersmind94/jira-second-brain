---
id: GUIDE-007
title: "Custom Reports Quick Reference Guide"
platform: "SC"
module: "Reports"
content_type: "Quick Guide"
source_url: "https://s3.us-east-1.amazonaws.com/docs.schoolcafe.com/Reports/Custom_Reports_Quick_Reference_Guide.pdf"
local_pdf: "raw/guides/pdf/SC/Reports/Quick-Guide/GUIDE-007-custom-reports-quick-reference-guide.pdf"
software_version: "6.4.8"
source_updated: "12/21/2023"
document_type: "Quick Guide"
author: "Content Team"
curated_against_raw_sha: "55286307dbf0d87f"
curated_against_raw_at: "2026-05-18T20:39:37+00:00"
last_reviewed_by: ""
status: "needs_initial_review"
---

# Custom Reports Quick Reference Guide

> Seeded from the raw extraction. Edit freely. When the raw drifts, review the diff and update this file, then mark it reviewed with `python scripts/mark_guide_reviewed.py GUIDE-007`.

## CREATE A CUSTOM REPORT
This guide will cover how to create a Custom Report and configure it for scheduled distribution.
To create a Custom Report, navigate to Reports > Custom Reports.
On the Custom Reports page
1. Click the + NEW button in the top right corner
   The Add Custom Report page displays.

2. Complete the fields in the Selection section
   a. Name – Enter a name that will enable other users to know what the report is about
   b. Description – Use the optional description to provide helpful information specific to the report
   c. Owner – Select the district user that is responsible for making decisions about the report and the one others can go to for questions
   d. Modules – Select the module that the dataset comes from
   e. Data Source – Select the dataset that you want to use, filtered by the module you selected
   f. Contains PII – Select Yes if the dataset contains personally identifiable information about students
   g. Dynamic Query – Visible to Customer Support only; select Yes if you want to write custom SQL code instead of using the graphical editor
   Click CANCEL if you changed your mind about creating a report.
   The NEXT button remains disabled until all the required fields are completed.
3. Click the NEXT button to go to the Configuration section

4. Complete the SOURCE TABLE tab in the Configuration section
   a. Click the Enabled toggle switch on all fields you want
   b. Drag rows up and down to determine the order you want them to appear in your report
   c. For any row, optionally give an alternate name that will appear in your report by typing it in the Alt Name field
   d. Filter the results with the Operator and Value columns
   i. Operators use smart values:
1. Text fields use text operators like “Equals”
2. Numeric fields use numeric operators like “=”
3. Date fields are disabled and use smart values ii. Value fields:
1. Text and numeric fields allow data entry in the text box
2. Date fields use smart dates, which are configured in the REPORT PARAMETERS tab
   e. Optionally apply the Locations special Report Parameter
   i. For datasets that have a SchoolCode field, the Location Report Parameter appears on the bottom ii. Optionally use pre-configured Location Report Parameters to apply smart filters to your dataset iii. This enables you to define location groupings such as “All Elementary Schools” and use this setting instead of having to select all the schools for each report
   The NEXT button remains disabled until you click the Generate SQL button on the SQL tab.
   The other tabs remain disabled until you select at least one column in the dataset.

5. Complete the DEFAULT SORT tab in the Configuration section
   Optionally, use this grid to define the order in which the results are returned.
   a. Select a column in the Source Field column
   b. Select if you want it ascending or descending in the Description column
   c. Optionally click the Trash Can icon to delete the Source Field
   d. Optionally click the ADD NEW + button to add another column to sort by
   If there are multiple columns, the sort will be applied in order of the grid.
   Rows with no values will be ignored.

6. Complete the ARGUMENTS tab in the Configuration section
   Use these fields to modify your dataset results.
   a. Optionally check DISTINCT to apply the Distinct argument to the data results
   b. Optionally check TOP and enter a number to filter the number of records returned in the data results
   If you check TOP, you must enter a number in the text box next to it.

7. Complete the SQL tab in the Configuration section
   a. Click the GENERATE SQL button
   i. This auto-generates the necessary SQL needed to produce the report based on the selections on the other tabs
   The NEXT button remains disabled until you click this button.
   b. Optionally click the RUN button to preview the data
   c. Optionally click the CLEAR button to remove the SQL code and start over
   Warning – If you make changes in the other Configuration tabs, it will delete the SQL, and you will have to regenerate it.
8. Click the NEXT button to go to the Sharing section

9. Complete the Sharing section
   The objective of this section is to identify people who will be typical users of the report and notify them that you have created it and shared it with them. Additionally, your choices can be used in the Distribution section to save you time.
   a. Select if you want to share the report with others
   i. The default is No ii. If you select Yes, you must pick at least one person or one role before you can click the NEXT button
   b. If Yes, select the user(s) or role(s) or both The NEXT button remains disabled until you make one selection.
   The system is smart enough to share only once if you select a user in a selected role.
10. Click the NEXT button to go to the Distribution section

11. Complete the Distribution section
   a. First, decide if you want to distribute the report
   i. Select No if you do not want to send it to anyone on a schedule; you can still view reports manually
   b. Choose the Format that you would like the report to be distributed
   c. Choose which distribution method you would like:
   i. Select one or more between Email, Inbox, and FTP Choices are independent.
   d. If you select Email:
   i. Optionally add an individual SchoolCafé User
   Optionally copy users from the Sharing section to save time.
   ii. Optionally add all members of a SchoolCafé Role
   Optionally copy roles from the Sharing section to save time.
   iii. Optionally add external email accounts
   Be careful when sending documents with PII data to external accounts.
   iv. Documents with PII data will not be distributed to SchoolCafé users who are not in the PII role
   v. Users will receive an email of the report in the format selected per the schedule defined in the next section
   e. If you select Inbox:
   i. Optionally add an individual SchoolCafé User
   Optionally copy users from the Sharing section to save time.
   ii. Optionally add all members of a SchoolCafé role
   Optionally copy roles from the Sharing section to save time.
   iii. Documents with PII data will not be distributed to SchoolCafé users who are not in the PII role iv. Users will receive a Workspace Inbox message of the report in the format selected per the schedule defined in the next section
   f. If you select FTP:
   i. Obtain the FTP settings from your administrator or SchoolCafé Customer Support representative if you do not have it already ii. Enter the required information in their respective fields
12. Click the NEXT button to go to the Scheduling section

13. Complete the Scheduling section
   a. First, decide if you want to schedule sending the report
   i. Select No if you do not want to send it to anyone on a schedule
   b. Then decide if you want to send just once or send recurring
   c. If Once, then select the date and time you want to send it
   d. If Recurring, then select the first and last dates along with what days of the week and time of the day you want the report distributed
14. Click the NEXT button to go to the Review section

15. Review the Review section one last time before saving
16. Click the SAVE button to commit your report to the database
   A confirmation response appears at the top of the page, and the Custom Report is added.
   You are returned to the dashboard.

The Custom Report is added to the list.
