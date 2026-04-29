---
key: NXT-89
summary: "State Claim Exports - Configuration Page"
status: "New"
resolution: ""
components: []
sprints: []
low_signal: false
---

# NXT-89 — State Claim Exports - Configuration Page

## Description
As a Central Office Admin I want an easy way to configure my claim export so I can upload it to another system.

*Requirements*

* A UI where users can design their data export for meal and attendance data.
* User can set export format - tab, comma, fixed length.
* For fixed length - user can set length of column, padding, alignment.
* User can designate order of data - row 1 is Site Number, row 2 is Month Number, row 3 is number of students, etc.
* User can preview the results of the configuration without having to export the file to check it.
* Data Elements for columns:
** Almost all data elements are a combination of meal type and eligibility.
** Example for Breakfast:
*** Number of Free Meals
*** Number of Reduced Meals
*** Number of Paid Meals
*** Number of Second Meals
*** Number of Adult Meals
*** Approved Count for Free / Reduced / Paid.
*** Number of Operating Days (days this meal was served / available)
** Other examples are site specific like:
*** Total number of students enrolled at site.
*** Site information - name, site number, state site number.
*** Average Daily Attendance (Total # of Students for all operating days * Attendance Factor / # of Operating Days)
** Typically each row will be a site, but some states have more than 1 row with the same site.

## Acceptance Criteria
User can configure a robust, multi-column export with combinations of meal types and eligibility data for the claiming period selected.
