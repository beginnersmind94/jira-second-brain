---
name: longform-patterns
description: Structural and citation patterns that work well for long-form guides; validated on Item Management 2026-05-29 generation
metadata:
  type: feedback
---

## Long-form guide: validated patterns

**Workflow section ordering:** Follow the presenter's actual demo sequence (non-food first as the simpler case, then food building on it). Within food items, cover tabs in the order the presenter walked through them. Users find it easier to follow a guide that mirrors a real demo.

**Why:** Sarah's training followed non-food → food → tabs in order. Matching that structure maps directly to what Brunswick County staff experienced and reduces cognitive switching.

**How to apply:** For any long-form guide derived from a live training transcript, default to the presenter's demonstrated sequence for Full Workflows (Section 4), not alphabetical or complexity-sorted order.

---

## Discrepancy callout rendering

Use `<blockquote>` with a bold heading line like `[!warning] Discrepancy D1 — Severity: HIGH`. Inside, quote both sources verbatim and add a "Human editor action required:" line explaining what needs to be resolved before publish.

**Why:** The template says to surface both quoted verbatim; the blockquote makes the discrepancy visually distinct from instructional content in the HTML draft.

**How to apply:** Every discrepancy from the factcheck must become a blockquote callout placed inline in the relevant workflow step, not collected in a separate appendix. D1 (Yield Factor) goes inside the Ingredient Info section. D2 (Merge/promote) goes inside the food Units Card section.

---

## [TO VERIFY] placement discipline

Place the [TO VERIFY] marker immediately after the claim it qualifies, on the same paragraph line, in brackets. Do not aggregate them. This keeps context for the human editor — they see the claim and its doubt status together.

**Why:** The evaluator checks that every AC-thin claim has a marker. Inline placement ensures nothing slips past review.

---

## Citation tier honesty pattern

For Description-only field names (labels like "Missing Costing," "Manage Costing," "Brand Name," etc.): assert the claim but immediately follow with `[TO VERIFY: label appears in NXT-XXXXX Description only, not AC]`. Do not skip these claims — the field exists, the label is just unverified.

**Why:** Cutting Description-tier field names entirely would leave the guide unusable (staff can't find the field if it has no name). The TO VERIFY pattern preserves usability while flagging verification need.

---

## Cross-module sentence pattern (one-line rule)

Template: "See <strong>Related Content — [Module name] module</strong>." followed by `[[link: Module guide]]` in a `<code>` tag.

Only use this sentence — do not add any further explanation about what the other module does. The Related Content section (Section 9) has the one-liner for each cross-module reference.

---

## Table structure for Key Fields section

Fields table: columns = Field | Required? | Valid values / behavior | Source
Status table: columns = Status | Trigger | Source
Identifiers table: columns = Icon | Meaning | Source
Keep inline source comments inside each `<td>` cell rather than in a separate column — this keeps the HTML comments attached to the specific claim they support without adding a visible column.

---

## Sources section structure for long-form

Two sub-sections: (1) Tickets table with columns Ticket | Summary | Tier used — this serves as the authoritative list matching all inline `<!-- Source: NXT-XXXX -->` comments. (2) Transcript metadata block. (3) Omissions list — required by template; one line per excluded feature with reason and transcript timestamp.

**Why:** Evaluator checks that inline citations match Sources. Keeping the tickets in a table with Tier column makes tier compliance auditable in one scan.

Related: [[micro-guide-structural-patterns]]
