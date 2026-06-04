---
name: project_jira-ac-spotcheck-limitation
description: Atlassian MCP getJiraIssue and fetch tools return Description field only — AC is in a custom field not surfaced by either tool. Use tickets-cache.md as ground truth for AC spot-checks; it was populated by the SME agent via live Jira during Task 3.
metadata:
  type: project
---

The Atlassian MCP `getJiraIssue` and `fetch` (ARI form) tools both return only the Description field and issue metadata. The Acceptance Criteria text is stored in a custom Jira field not exposed by either tool's default response.

**Why:** NXT project AC is in a custom field (not `description`). The `fields` parameter on `getJiraIssue` supports custom field IDs (customfield_NNNNN) but the correct field ID for AC in this Jira instance is not yet identified.

**How to apply:** For AC spot-checks, use `tickets-cache.md` in the pipeline's log directory as ground truth. This cache was populated verbatim from live Jira by the SME agent (Task 3) using direct MCP reads. It is the most authoritative AC source available. Cross-reference draft quotes against the cache rather than re-querying Jira. If a quote is not in the cache, flag it for manual verification — do not pass it silently.

**Do not** treat the live-Jira Description field returned by these tools as AC — it is TIER 3 and cannot confirm AC-labeled citations in the draft.
