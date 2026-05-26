---
id: GUIDE-048
title: "Direct Certification - Files Quick Guide"
platform: "SC"
module: "Eligibility"
content_type: "Quick Guide"
source_url: "https://s3.us-east-1.amazonaws.com/docs.schoolcafe.com/Eligibility/Direct_Certification_Files_Quick_Guide.pdf"
local_pdf: "raw/guides/pdf/SC/Eligibility/Quick-Guide/GUIDE-048-direct-certification-files-quick-guide.pdf"
curated_against_raw_sha: "427a360a2e314de0"
curated_against_raw_at: "2026-05-18T20:39:43+00:00"
last_reviewed_by: ""
status: "needs_initial_review"
---

# Direct Certification - Files Quick Guide

> Seeded from the raw extraction. Edit freely. When the raw drifts, review the diff and update this file, then mark it reviewed with `python scripts/mark_guide_reviewed.py GUIDE-048`.

The Files function allows district users to manage their Direct Certification list.
The Files function allows the district to
- Search for Direct Certification files by
  - Approval
  - Student
- Direct Certification Summary
  - Delete file
  - Add or Remove documents
- Create a new file by
  - Importing files in bulk
  - Manually entering the files and then process
- Process Pending or newly added Direct Certification files

## Search Files
Districts can search for Direct Certification Files received by
- Approval
- Student

## Search by Approval
1. Select an Academic Year from the dropdown
2. Select the Approval radio button
3. Select an Approval Type from the dropdown
   Additionally, you can enter a File Number to locate a specific Direct Approval File.
4. Click the APPLY button
   Files display below.

## Search by Student
1. Select an Academic Year from the dropdown
2. Select the Student radio button
3. Enter the student’s First Name, Last Name, Date of Birth, or Student ID#
   It is required to use at least one of the fields to look up a Direct Approval File by student.
4. Click the APPLY button
   Files display below.

## Direct Certification Summary
1. Identify the file you wish to view the Summary of
2. Click the Summary (Paper) icon for the desired file
   The Direct Certification Summary page displays.
3. View the Direct Certification Summary page
   In the Students section, the per-student action previously labeled Revert is now Unmatch. The confirmation prompt matches the one on the Matched page and includes the option to block the student from being directly certified for the rest of the academic year.

## Delete File
Using the DELETE button changes the eligibility for all students involved in the selected file back to their previous statuses.
1. On the Direct Certification Summary page, click the DELETE button to the right
   The Confirmation pop-up window displays.
2. Enter required Comments
3. Click the DELETE button
   A File deleted Successfully! message displays, and the file is deleted.
   The status changes to DELETED.
   Repeat this process to delete additional files as needed.
   Click the BACK button to return to Files page.
   Documents
1. On the Direct Certification Summary page, scroll down to the Documents section
   Or click Documents on right hand side of the page.
2. Click the ADD/REMOVE button
   The Add Document slide deck displays.
   Previously added documents and comments display in the Documents &
   Comments table.

## Add Document
1. Use the Drag & Drop File Here option or click the SELECT FILE button to upload documents
   Uploaded files populate below with options to download and remove the files.
   The Checkmark icon indicates that the document was correctly uploaded.
2. Enter a required Comment
3. Click the SAVE button
   The file will appear in the Documents section on the Direct Certification Summary page.

## Remove a Document
1. Identify the file you wish to remove in the Documents & Comments table
2. Select the Remove icon for the desired file
3. Enter a required Comment
4. Click the SAVE button

## Add Files
Direct Certification entries can be imported or manually entered and then processed.

## Add Student by File Import
Files must be mapped before using this function. Refer to Import Configuration in the System module for more information.
For states using a single file that contains multiple direct certification programs, the Direct Certification DC Type mapping supports DC Foster, Migrant, Runaway, Head Start, Even Start, RCCI, Principal Approved, Pre-K (Free), and Pre-K (Reduced). Contact Support if you need help configuring the mapping.
1. On the Files page, click the NEW button in the top right corner
   The New File page displays.
2. Select the File Import radio button
3. Select a Program from the dropdown
4. Select an approval Type from the dropdown
5. Enter the Approval Date
6. Select the Current Configuration Name from the dropdown
7. Import files using the Drag & Drop File Here option or click the SELECT FILE button
8. Click the SUBMIT button once the file has been successfully uploaded
   Repeat this process to add additional direct certification files as needed.
After processing completes, the uploaded file is automatically attached to the Documents section of the file's Direct Certification Summary, where it can be viewed without leaving the page.

## Add Student by Manual Entry
1. On the Files page, click the NEW button in the top right corner
   The New File page displays.
2. Select the Manual Entry radio button
3. Select a Program from the dropdown
4. Select an approval Type from the dropdown
5. Enter the Approval Date
6. Enter the student’s Name or ID to generate the results
7. Click the ADD button for the student you want to add
   The selected student displays in the Selected Students table.
   The student is now on the list to be submitted.
   The selected student(s) can be deleted.
   Repeat steps 6 and 7 to add additional students as needed.
   Use the Delete student (Trash Can) icon to remove a selected student(s).
8. Enter an optional Comment
9. Click the SUBMIT button to save the entry for processing
   A confirmation response displays, and the direct certification file is added.
   You are returned to the Files page.
   Repeat this process to manually add additional direct certification files as needed.
Manual Entry files no longer have a Preprocessing Review step. After submission, the file moves directly to Processed and student eligibility is updated immediately.

## Pending Direct Certification Files
Direct Certification entries which have been newly added or previously entered showing a Status of PENDING can be processed.
1. On the Files page, select an Academic Year from the dropdown
2. Select the Approval/Student radio button
3. Select an Approval Type from the dropdown
   Additionally, you can enter a File Number to locate a specific Direct Approval File.
4. Click the APPLY button
   Files display below.
5. Click the Summary (Paper) icon for the desired file with a PENDING Status
   The Preprocessing Review page displays.
6. If there are supporting documents to show student approval, follow the steps below
- Navigate to the Documents section
- Click the ADD/REMOVE button
The Add Document slide deck displays.
- Use the Drag & Drop File Here option or click the SELECT FILE button to upload a document
- Enter a required Comment
- Click the SAVE button
The selected document(s) appear in the Documents section.
The added document(s) can be deleted.
If there are no documents to add, then go to Step 7.
7. Click the PROCESS button
   The CONFIRMATION pop-window displays.
8. Select PROCESS
   A File processed successfully! message displays.
   You are returned to the Preprocessing Review page.
   The status changes to PROCESSED.
   The DELETE button is now displayed.
   Repeat this process to process additional direct certification files as needed.
9. Click the DELETE button if you need to delete this processed file
   A Comment is required to delete the selected file.
   Once a Direct Certification file has been deleted, it cannot be restored.
