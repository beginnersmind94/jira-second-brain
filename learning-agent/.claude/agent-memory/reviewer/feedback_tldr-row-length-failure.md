---
name: feedback_tldr-row-length-failure
description: TLDR Writer fails on row-length compression across retries — retry 1 still had 15 of 25 rows with description >15 words and 1,035 visible words vs ~750 ceiling. Retry 2 PASSED at 687 words with 0 rows over 15 words (1 row at 13 words, all others ≤12). Resolution: explicit ≤12-word description-cell budget with semicolon-compound ban.
metadata:
  type: feedback
---

The TLDR Writer successfully removed all `[TO VERIFY]` markers from visible text (0 in retry 1) and correctly fixed the NXT-39594 citation (Menu Item tab → AC; toggle→pricing → NXT-30155 AC). However, the core one-page constraint failed on first two retries:

- Retry 0: ~1,278 visible words, many rows 20-31 words
- Retry 1: 1,035 visible words, 15 of 25 rows still exceed 15 words in description column alone (avg 16.2 words/row)
- Retry 2: 687 visible words, 0 rows over 15 words, 1 row at 13 words, all others ≤12 → PASSED

**Why it took 3 attempts:** The Writer interprets "≤15 words" as a target for the combined row (feature name + description), not the description cell alone. When feature names like "Menu Info tab / Direct Menu Item" (7 words) are included, the apparent compliance looks plausible — but the description cell itself runs to 17-25 words. The fix was adding an explicit per-row description-cell budget.

**How to apply:** On the TLDR Task 4 routing, add an explicit per-row budget: **description cell must be ≤12 words** (not 15), because the feature-name column adds 3-7 words which get counted in any whole-row measurement. Total visible word target: ≤750. The 25 rows together must average ≤10-11 description words. Compound sentences with semicolons (";") must be split to single clauses or the second clause dropped.

**What worked in retry 2:** Writer kept semicolons only where both clauses together fit ≤12 words (e.g., "Enter cost for one tier; system scales to all others; FMV required." = 12w). Rows that previously had long compound sentences were rewritten as single clauses.

**Non-blocking plan deviation (not a fail trigger):** The plan listed 7 common workflows; the draft has 6 (HACCP workflow silently dropped). HACCP is represented in the Key Features table (row 22), so the feature is not omitted — only the workflow example is absent. Acceptable on a one-pager where compression is required. Family Hub dropped from "Where to go next" — plan had 5 bullets; template cap is 4; dropping to 4 is template-compliant.

**Do NOT** route to plan (Task 2) — the plan is correct and complete at 25 rows. Route only to Writer (Task 4) with compress budget.
