---
name: project_sarah-chen-transcript-patterns
description: Sarah Chen (Implementation Specialist) transcripts have a recurring pattern: presenter describes outdated UI locations (pre-ticket state), uses informal terminology differing from AC, and admits uncertainty on several features. Expect 2-3 high/medium discrepancies per transcript.
metadata:
  type: project
---

Sarah Chen's transcripts (item management training, 2026-05-15) show a consistent pattern of presenter knowledge gaps:

1. **Outdated UI locations**: Sarah described Edible Yield Factor on the Ingredient Info card — but NXT-47249 (Done Done) moved it to the Units card. This suggests her training materials lag behind sprint releases.
2. **Informal terminology**: Uses "promote" and "BASE UNIT chip" where AC says "Merge" and "Merge w/ Serving button." Functional behavior is correct but exact UI label differs.
3. **Admitted unknowns**: Explicitly said "I'm not sure" or "I'll follow up" on: allergen bulk import, item copy/clone, data sharing, sales tax calculation, Inventory receiving workaround. These should always be excluded from content.

**How to apply:** When reviewing drafts from Sarah Chen transcripts, expect D1-class (HIGH) discrepancies and budget for 2-3 `[!warning]` callouts. Verify all UI element names against AC — her informal labels are often consistent with the behavior but diverge on exact strings. The factcheck agent should be flagged to pay special attention to "moved" features (anything where she says "this is where you do X" — verify against Done Done tickets that may have relocated X).
