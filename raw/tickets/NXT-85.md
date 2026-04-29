---
key: NXT-85
summary: "Deposits - Deposit Details - Summary"
status: "Done Done"
resolution: "Done"
components: ["Accountability"]
sprints: ["Perseus Sprint 29", "Perseus Sprint 30", "Perseus Sprint 31"]
low_signal: false
---

# NXT-85 — Deposits - Deposit Details - Summary

## Description
When creating a deposit slip I need to see a summary of cash, checks, the amount of deposit and expected amount of deposit. 

*Mockup:*

[https://www.figma.com/proto/yrkJeGfd3f9hWjqm0qvfir/Edge2.0_V1?node-id=5834%3A730&scaling=min-zoom|https://www.figma.com/proto/yrkJeGfd3f9hWjqm0qvfir/Edge2.0_V1?node-id=5834%3A730&scaling=min-zoom]

*Requirements:*

* Cash is calculated from denominations entered
* Checks is calculated from list of checks entered
* Deposit total is calculated from Cash + Checks
* Expected Deposit is calculated by summing the Cash Deposited and the Checks Deposited in the sessions included in the deposit. 
** For each session the Cash Deposited is Closing Cash - Opening Cash
** For each session the Checks Deposited is the Total Check Amount in the Closing balance
* A comment is required if Expected Deposit is different than Deposit Total [https://primeroedgenext.atlassian.net/browse/NXT-5374|https://primeroedgenext.atlassian.net/browse/NXT-5374|smart-link] [https://primeroedgenext.atlassian.net/browse/NXT-5375|https://primeroedgenext.atlassian.net/browse/NXT-5375|smart-link]

## Acceptance Criteria
Cash is calculated from denominations entered
Checks is calculated from list of checks entered
Deposit total is calculated from Cash + Checks
Expected Deposit is calculated by summing the Cash Deposited and the Checks Deposited in the sessions included in the deposit. 
For each session the Cash Deposited is Closing Cash - Opening Cash
For each session the Checks Deposited is the Total Check Amount in the Closing balance
A comment is required if Expected Deposit is different than Deposit Total
