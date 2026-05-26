---
id: GUIDE-003
title: "Data Management Quick Guide"
platform: "SC"
module: "System"
content_type: "Quick Guide"
source_url: "https://s3.us-east-1.amazonaws.com/docs.schoolcafe.com/System/Data_Management_Quick_Guide.pdf"
local_pdf: "raw/guides/pdf/SC/System/Quick-Guide/GUIDE-003-data-management-quick-guide.pdf"
extraction_warnings: []
extracted_at: "2026-05-18T20:39:36+00:00"
raw_text_sha256: "7d7c096bb72650c5"
generated: true
status: "draft_extracted"
---

# Data Management Quick Guide

Users will follow these steps to import and export data for their districts within SchoolCafé. This guide will include the Import Dashboard, Export Dashboard, Import Monitor, Export Monitor, and SIS Auto Sync functions.
Import Dashboard
The Import Dashboard function allows users to configure new Imports, edit existing Import configurations, enable/disable Imports, and delete Import configurations. Users can also use this page to Import files manually.
For Import Dashboard, go to System > Integration > Import Dashboard.

## Configure New Imports
1. Click the NEW button in the top right corner
   The Import Setup page displays.
   A process wizard on the lefthand side is available to help guide you while configuring a new Import.
   Different sections will be available based on the Import Type selected.
   Once a process wizard icon turns purple, you can click on it to return to that section.
   Pre-Upload
1. Select an Import Type from the dropdown
   A series of questions or fields may become available based on the Import Type selected.
   Answer the following question regarding the Import Type.
2. Would you like to download a template?
   a. If Yes, you can download the template with available columns and fill in the columns
   b. Click the NEXT button to proceed
   c. If No, you are navigated to the File Upload section

## File Upload
1. Use the DRAG AND DROP FILES option or the SELECT button to upload a file of

## the Import Type
The Delimiter and Qualifier will be detected automatically once the file is uploaded. Check both before moving to the next step.
2. Click the NEXT button to proceed

## Field Mapping
1. Drag and drop to map the file fields from the SOURCE column to the MAPPED column
   A key is available at the bottom of the page and describes different icons associated with field mapping.
   A File Data Preview is available at the bottom of the page. Click the right-facing arrow to view a preview of the imported file.
2. Click the NEXT button to proceed
   Review
1. Review the SchoolCafé Fields and Mapped Fields
2. Edit the Current File Name as desired
3. Click the Enabled toggle switch on or off Activating this configuration will deactivate the existing active configuration.
4. Click the SAVE button to create the new Import
   Click the EDIT MAPPING button to return to the Field Mapping section and make the edits as necessary.
   A confirmation message appears, and the Import is configured.
   Repeat this process to configure additional Imports as needed.

## Perform Manual Imports

## File Upload
1. Click the IMPORT button for the desired Import configuration
   The Import File page displays.
2. Use the DRAG AND DROP FILES option or the SELECT button to upload a file of

## the Import Type
3. Click the NEXT button to proceed
   Review
1. Review the uploaded file
2. Click the IMPORT FILE button
   A confirmation message appears, and the Import is configured.
   Repeat this process to manually configure additional Imports as needed.
   To view the progress of an Import, navigate to the Imports Monitor page.

## Export Dashboard
The Export Dashboard function allows users to configure new Exports, edit existing Export configurations, enable/disable Exports, and delete Export configurations.
For Export Dashboard, go to System > Integration > Export Dashboard.

## Configure New Exports
1. Click the NEW button in the top right corner
   The Export Setup page displays.
   A process wizard on the lefthand side is available to help guide you while configuring a new Export.
   Once a process wizard icon turns purple, you can click on it to return to that section.
   Pre-Export
1. Select the Export Type from the dropdown
2. Click the NEXT button to proceed

## Field Mapping
The SOURCE – SchoolCafé Fields are available for the Target - File Fields.
1. Rename the TARGET – File Fields as desired
   The File Fields will be the fields’ names used in the Export header.
2. Click the NEXT button to proceed
   Review
1. Review the SchoolCafé Fields and Export Fields
2. Edit the Current File Name as desired
3. Click the Enabled toggle switch on or off Activating this configuration will deactivate the existing active configuration.
4. Click the SAVE button to create the new Export
   Click the EDIT EXPORT button to return to the Field Mapping section and make the edits as necessary.
   A confirmation message appears, and the Export is configured.
   Repeat this process to configure additional Exports as needed.

## Import Monitor
The Import Monitor will display an overview of Imports that are processing or have been processed.
For Import Monitor, go to System > Integration > Import Monitor.

## View Imports
1. Select the Import Type(s) from the dropdown
2. Select the Date Range from the dropdown
3. Select the Status(es) from the dropdown
   Results will display in the table below.
4. Click the VIEW LOG button for the desired Import
   The Import Monitor page displays with additional information.
   Depending on the Import Type being viewed, the following sections may or may not be visible.
   Summary
1. View Import information such as the Total Records, Updated amount, Added amount, Activated amount, Withdrawn amount, Processed amount, Active
   Account Before Import, Import Start Date, Import End Date, and Status

## ACTIVITY MONITOR
1. Ensure that the ACTIVITY MONITOR tab is selected
2. View Import information such as the Activity Name, Start Time, End Time,

## Duration, and Status

## HISTORY LOG
1. Select the HISTORY LOG tab
2. View Import information such as the Account ID, Process Message, Exception

## Message, and Processed Date
EXCEPTIONS
1. Select the EXCEPTIONS tab
2. View Import information such as the Student ID, Processed Message, Allergens,

## Processed Date, and Processed by

## Export Monitor
The Export Monitor function is used to check the status of Exports.
For Export Monitor, go to System > Integration > Export Monitor.

## View Exports
1. Select the Export Type from the dropdown
2. Select the Date Range from the dropdown
5. Select the Status from the dropdown
   Results will display in the table below.
3. Click the VIEW LOG button for the desired Configuration
   The Export Monitor page displays with additional information.

## ACTIVITY MONITOR
1. View the Export information such as the Activity Name, Start Time, End Time,

## Duration, and Status
SIS Auto Sync
The SIS Auto Sync function allows users to configure API settings to import students via an API for the following providers: Aeries, PowerSchool, and Skyward.
It also provides the ability to schedule a recurring Student Import via API.
For SIS Auto Sync, go to System > Integration > SIS Auto Sync.

## Configure New API Configurations
The API configuration configures automatic Imports from a third-party Information System.
1. Click the NEW button in the top right corner of the page
   The SIS Auto-Sync page displays.
2. Select the Import Type from the dropdown
3. Select the Provider from the dropdown
4. Enter the required information from the third-party company
   a. URL
   b. Key
   c. Secret
5. Click the TEST CONNECTION button to test the connection

## Schedule Imports using the Scheduler
1. Click the Scheduler toggle switch on
2. Click the Checkbox(es) to select the day(s)
   Click the Select All checkbox to select all days.
3. Enter the Start time

4. Enter the End time
5. Select the Frequency from the dropdown
   The frequency should not be greater than the selected time interval.
6. Click the Save button to create the new configuration
   A confirmation message appears, and the configuration is created.
   Repeat this process to create API Configurations as needed.
