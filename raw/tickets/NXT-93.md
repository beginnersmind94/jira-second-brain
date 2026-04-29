---
key: NXT-93
summary: "Account Management - Rosters - Special Roster creation from session data"
status: "New"
resolution: ""
components: ["Account Management"]
sprints: []
low_signal: false
---

# NXT-93 — Account Management - Rosters - Special Roster creation from session data

## Description
As a Central Office Admin I want a way to create custom lists of students across grades / sites for use in field trips.

Requirements:

Display a session list of patrons, allow the user to select patrons and save the patron list as a roster.

* Allow the user to build the list from a session, by selecting students from the session.

## Acceptance Criteria
Using a session, the user can select multiple students and create a roster.
Initially the order is in transaction order but can be sorted. 
Multiple rosters can be created from one session.
A new button is added "Create roster from session"
Filters allow the user to select a session by Site, and date.
Patrons can be selected from the session
