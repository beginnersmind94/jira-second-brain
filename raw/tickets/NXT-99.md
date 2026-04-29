---
key: NXT-99
summary: "Configuration - Charge Limits - Move to POS from System"
status: "Done Done"
resolution: "Done"
components: ["Accountability"]
sprints: ["Perseus Sprint 32"]
low_signal: false
---

# NXT-99 — Configuration - Charge Limits - Move to POS from System

## Description
As a Central Office Admin I want a way to configure category restrictions and charge limits.

*Mockup:*

!Screen Shot 2020-11-24 at 8.55.05 AM.png|width=765,height=654!

[https://www.figma.com/proto/yrkJeGfd3f9hWjqm0qvfir/Edge2.0_V1?node-id=120790%3A166403&viewport=294%2C5%2C0.25&scaling=scale-down-width|https://www.figma.com/proto/yrkJeGfd3f9hWjqm0qvfir/Edge2.0_V1?node-id=120790%3A166403&viewport=294%2C5%2C0.25&scaling=scale-down-width|smart-link] 

*Requirements:*

* Charge Limits will be entered for both Meals and Ala-Carte for both Students and Adults.
* Student Limits are set by Site Type or Grade Group
* Adult Limits are set by Site Type
* Limits default to $0.00 and have a maximum of $999999.99

Move functionality and table from System to POS.

## Acceptance Criteria
Charge Limits is launched from the Configuration from the left panel
Charge Limits is reached through the tabs of the Configuration page.
The System Page is Launched.
Charge limits default to $0 
Charge limit maximum is $999999.99
If the edited value is not saved it will revert to the previous value
Charge limits are entered by Adult Person type(Staff, Visitor, Program Adult) for each Site Type. 
Charge limits are entered for Students by Eligibility type(Free, Reduced, Paid) for either Site Type or Grade Group.
Charge limits are entered for both Meals and Ala-Carte 
Grade Group Setting = PRICEMODE values Site Type or RDA Group
When PRICEMODE = RDA Group then Student charge limits are by Grade Groups.
