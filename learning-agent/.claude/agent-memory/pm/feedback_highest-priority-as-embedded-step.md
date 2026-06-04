---
name: feedback_highest-priority-as-embedded-step
description: A Highest-priority ticket does not automatically deserve its own workflow slot — if it is a required mid-workflow step, embed it prominently within the parent workflow
metadata:
  type: feedback
---

In the Item Management micro guide plan (2026-05-29), NXT-37441 (Serving↔Pack linking, Highest Jira priority) was considered for its own workflow slot but correctly embedded as a critical step within the "Create a food item" workflow instead.

**Why:** The Serving↔Pack link cannot be performed without first adding serving sizes and pack sizes in the same workflow. Creating a standalone workflow would be artificial and confusing. The prominence of the Highest priority is preserved by: (a) treating it as the central pitfall for workflow 2, (b) including the "Inventory Ready alert persists" consequence explicitly in the steps.

**How to apply:** When a high-priority ticket maps to a step that is sequentially dependent on the surrounding workflow (cannot be initiated independently by the user), embed it with a clear pitfall callout rather than forcing it into its own workflow slot. Reserve workflow slots for tasks users can independently initiate.
