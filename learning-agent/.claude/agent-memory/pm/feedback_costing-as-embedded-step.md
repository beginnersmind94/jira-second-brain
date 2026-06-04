---
name: feedback_costing-as-embedded-step
description: Costing workflow in Item Management should be embedded within item creation workflows, not split out as a standalone workflow in a micro guide
metadata:
  type: feedback
---

In the Item Management micro guide plan (2026-05-29), costing (NXT-37568) was considered as a standalone workflow #3 but correctly kept embedded within the non-food and food creation workflows instead.

**Why:** Costing is initiated mid-workflow after all pack sizes are added — it cannot be performed independently. Extracting it wastes the 5-workflow budget and forces repetition of pack size context already established in workflows 1 and 2. The key behavioral detail (add all packs before touching costing) is better surfaced as a Common Mistakes bullet than a full workflow.

**How to apply:** When Item Management content is planned for any template, treat costing as a step within pack size configuration, not a standalone workflow. Reserve standalone workflow slots for tasks users initiate independently.
