---
key: NXT-77
summary: "Claims - Grid List"
status: "Done Done"
resolution: "Done"
components: ["Accountability"]
sprints: ["Perseus Sprint 32"]
low_signal: false
---

# NXT-77 — Claims - Grid List

## Description
As a Central Office Admin I want to be able to create reimbursement claims per period so that the department can be paid.

*Mockup*

[https://www.figma.com/proto/yrkJeGfd3f9hWjqm0qvfir/Edge2.0_V1?node-id=159652%3A184416&viewport=978%2C-1276%2C0.25&scaling=min-zoom|https://www.figma.com/proto/yrkJeGfd3f9hWjqm0qvfir/Edge2.0_V1?node-id=159652%3A184416&viewport=978%2C-1276%2C0.25&scaling=min-zoom|smart-link] 

!POS-Claims - List By Period Range (View Only).png|width=1920,height=1318!

!POS-Claims - List By Period --Dropdown2.png|width=1926,height=1323!

!POS-Claims - List By  single period is selected.png|width=1926,height=1323!

!POS-Claims - List By Period (42e45dc4-6cc4-4fb1-8f1c-e16af69f8a02).png|width=1926,height=1323!

!POS-Claims - Claim Created.jpg|width=100%!

!POS-Claims - Create Claim.jpg|width=1922,height=1321!

[^SFSPSummaryDistrictClaim (1).pdf]
[^SFSPDetailedDistrictClaimBySite (1).pdf]
[^SummaryDistrictClaim.pdf]
[^DetailedDistrictClaimBySite.pdf]
[^AdvancedClaimInfo.pdf]

*Requirements*

* Users can select an academic year and period(s) to select claims to see.
* Users can select to view claim data by a date range.
* Users can create a new claim 
* Users can recreate an existing claim.
* Claims for SNP, CACFP, and SFSP can be viewed by selecting the claim type
* User can Preview or Export the selected claim
* When the claim is generated the claim summary is displayed.

* Selecting ‘Create Claim’ generates the type of claim selected for the period. SNP, SFSP, CACFP
* A claim can only be created if all the claiming sites have closed their period for the claiming period.
* The user verifies if a claim can be generated
* A summary of the claim is displayed when complete

Notes:

* Each state has its own format for claim exports off of this page. We may want to consider creating a UI that lets that be customizable - we can likely specify every data point required for this in a future story

## Acceptance Criteria
User can select to show claim data by Periods or Date range
The user can select ALL or a specific period.
If all is selected a list of claims is shown for all created claims
If a specific period is selected and the claim doesn't exist the claim can be created if all meal exceptions are resolved, all sessions are Reconciled and/or Deposited, all edit checks are resolved, and the period is closed for all sites
Based on the Reimbursable Meal Types recorded for the period the claim(s) are generated, When the generate claim is clicked

1 When there are still meal exceptions, display a message "There are meal exceptions that need to be resolved, Do you want to resolve them?" Yes = Open the Period, Show the Exceptions List for all, for the Period. No = return to the grid.
2 When there are sessions that are not Reconciled or Deposited (ie. Initialized, Opened, Closed) a message is displayed "One or more sessions is not reconciled or deposited for the period. Do you want to reconcile the session(s)?" Yes = Open the Period, Open the POS Reconciliation list page with all as parameters and date for the previous month, No = return to the grid
3. When the are unresolved edit checks the message is displayed " There are unresolved Edit Checks. Do you want to resolve them?" Yes = Open the Edit Checks list page with all and date month for the period, and unresolved as the selection. No = return to the grid.
4 When the period isn't closed for all sites a message is displayed "One or more periods are open. Do you want to close them?" Yes = Open the POS Period page in System, No = return to the grid

If a specific period is selected and a claim exits then the claim can be regenerated
For a period the claim can be viewed as a Summary (claim data total of all sites) or Detailed (claim data for each site)
For SNP there is also an advanced view.
All views can be exported
All views can be printed
