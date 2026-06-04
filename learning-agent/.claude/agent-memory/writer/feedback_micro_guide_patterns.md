---
name: feedback-micro-guide-patterns
description: Structural patterns validated for micro-guide template — section order, pitfall framing, citation discipline, [TO VERIFY] placement, evaluator-flagged failure patterns
metadata:
  type: feedback
---

## Rule: Split multi-part workflows into inline sub-headers rather than separate `<h3>` blocks

When a single workflow (e.g., allergens) has two sequential phases (standard + custom), use `<p><strong>Phase:</strong></p>` with `<ol>` continuing from a numbered start — keeps it as one workflow slot without adding a sixth workflow.

**Why:** The micro-guide hard ceiling is 5 workflows. A two-phase workflow that gets split into separate `<h3>` blocks would eat two slots and risk pushing past the limit.

**How to apply:** Any time a single workflow has a natural A→B structure (e.g., "configure standard, then add custom"), use the inline sub-header pattern. Do not count the two phases as two separate workflows in the ceiling count.

---

## Rule: "Also in this module" section for demoted features

The plan demotes several features to one-line mentions. Rather than scattering them through workflow steps, collect them in a `<h2>Also in this module</h2>` section between "Top workflows" and "Common mistakes." This keeps the word count tight and makes the section predictable for reviewers.

**Why:** Demoted items embedded as prose inside a workflow add noise and risk inflating step counts. A dedicated "Also in this module" `<ul>` keeps them visually distinct and easy to strip if word count runs long.

**How to apply:** For any plan-demoted feature (M1–M8), write one `<li>` sentence max in "Also in this module," not inside a workflow.

---

## Rule: [TO VERIFY] carries the ticket reference in the comment

Always pair `[TO VERIFY]` in body text with a `<!-- Source: ... -->` comment explaining which ticket was checked and why the claim can't be asserted (e.g., "Description-only per NXT-xxxxx").

**Why:** Without the comment, a reviewer can't quickly see where to go to resolve the TO VERIFY. The comment is stripped at publish but is essential during SME review.

**How to apply:** Every `[TO VERIFY]` in body text must have an adjacent HTML comment naming the ticket and stating the tier limitation.

---

## Rule: Common Mistakes pitfall for D1 (Yield Factor location) is always present in micro-guides for this module

Discrepancy D1 (Yield Factor moved from Ingredient Info to Units card per NXT-47249) is high severity. Even though the Ingredient Info workflow is omitted from the micro guide, a Common Mistakes bullet must explicitly warn staff away from the old presenter-described location.

**Why:** Without this bullet, staff who watched the recording will set Yield Factor on the wrong card. The Common Mistakes section is the safety net.

**How to apply:** Always include the D1 Yield Factor warning in Common Mistakes for any Item Management micro-guide or short-form content generated from this transcript.

---

## Rule: NXT-30155 "Set All Prices" — cite from AC not Description

NXT-30155 AC says "Provide the 'Set All Prices' option which can be used on one tab at a time (in Edit only)" — this is TIER 1 citable. But all individual POS field names (Button Name, Meal Type, etc.) are Description-only. Keep the distinction sharp: cite Set All Prices from AC; mark field names [TO VERIFY].

**Why:** Previous drafts risked citing Description-tier field names as AC. The field-name caution list is long for this ticket.

**How to apply:** For Workflow 3 (Menu Info / POS Pricing), only assert: Show on POS toggle (V27/NXT-39594), Students/Adults tabs + Set All Prices (V28/NXT-30155), Taxable Adults-only (V29/NXT-58442). Everything else is [TO VERIFY].

Related: [[feedback_tldr_patterns]]

---

## Rule: "Also in this module" must NOT be an `<h2>` section — fold into Related content

The micro-guide template allows EXACTLY 7 `<h2>` sections. "Also in this module" is not one of them. Demoted-feature one-liners must go inside the Related content `<ul>` as the final `<li>` (semicolon-separated inline list), not as a standalone `<h2>`.

**Why:** The Evaluator failed a draft that added an 8th `<h2>` for "Also in this module." The template section constraint is hard.

**How to apply:** Collect all plan-demoted features into a single `<li>` inside Related content, starting with "Also in this module:". One sentence per feature max, separated by semicolons. Do not create a new `<h2>` block.

---

## Rule: Word count must be verified before submission — target ≤1,200, hard ceiling 1,500

Draft retry 1 of 3 required multiple rounds of trimming to get from ~1,890 to ≤1,200. Primary culprits in order: (1) demoted-feature section with multi-sentence prose, (2) workflow step verbosity, (3) Common Mistakes bullet bodies, (4) Sources list verbosity.

**Why:** The Evaluator blocks on ceiling violations. Counting before emit saves a retry.

**How to apply:** After drafting, strip comments and tags mentally and estimate word count. Compression priority: Sources list first (use shorthand), then Related content one-liners, then workflow step prose, then Common Mistakes. Keep pitfall blockquotes to 2 sentences max.

---

## Rule: NXT-39594 AC is "Create a Menu Item tab" only — Show-on-POS behavior cites NXT-30155

Verified live 2026-05-29 via MCP. NXT-39594 AC contains only three bullets about Recipe redesign and Menu Item tab creation. "Show on POS toggle will control the presence of the POS attributes and Pricing table" is NXT-39594 **Description (TIER 3)**, not AC.

**Why:** The Evaluator failed a draft that cited NXT-39594 AC for Show-on-POS behavior. This is a source-grounding failure.

**How to apply:**
- Menu Item tab existence → `NXT-39594 AC: "Create a Menu Item tab"`
- Show on POS → POS attributes + Pricing behavior → `NXT-30155 AC: "Enable the POS Info tab if the user specifies the item as a POS Item; Load the POS attributes and Pricing section under the POS tab"` + `transcript [27:12]`
- Never cite NXT-39594 AC for anything beyond the tab's existence.
