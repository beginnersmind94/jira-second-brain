---
name: feedback-to-verify-marker-density
description: 24 [TO VERIFY] markers embedded in a TLDR one-pager is too many; markers should be quarantined, not embedded in scan-speed content
metadata:
  type: feedback
---

The TLDR draft for Item Management (20260529) contained 24 [TO VERIFY] markers inline in the rendered content. The TLDR template's goal is scan speed — a staff member seeing every feature at a glance. Embedding 24 unresolved markers defeats this goal and inflates word count.

**Why:** The plan correctly catalogued which items needed [TO VERIFY], but the Writer treated the plan's list as instructions to embed the markers inline rather than quarantine them in citation comments only.

**How to apply:** In a TLDR draft, [TO VERIFY] markers should appear ONLY inside <!-- Source: --> HTML comments or as a single end-note, never in the visible user-facing text rows. Count of inline [TO VERIFY] markers in rendered text is a template fit metric — more than 3 inline markers in a TLDR is a fail signal even if word count is acceptable.
