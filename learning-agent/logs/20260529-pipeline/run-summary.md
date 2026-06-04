# Producer Pipeline Run — 2026-05-29

**Transcript:** `raw/transcripts/20260529-070600-item-management-2026-05-28-item-management-create-items-training.md`
**Module:** Item Management
**Jira source:** live NXT project (`primeroedgenext.atlassian.net`, cloudId `f946bf46-…786e9`) via Atlassian MCP — no CSV/stub.
**Agent sequence:** mapper → pm → sme → writer → reviewer (generator on Opus; reviewer on Sonnet — separate model per CLAUDE.md Task 5).

## Field map (verified live)
AC (TIER 1) = `customfield_10131` (ADF) · Release Notes = `10148` · RN Title = `10285` · RN Internal = `10219` · Module = `10147` · Description = TIER 3 (never cited as AC).

## Shared stages (computed once, reused by all 3 templates)
- **Task 1 — mapper:** 39 matched tickets, 8 unmatched, 9 cross-module. → `mapper-inventory.md`, `mapper-metadata.json`, `tickets-cache.md` (tier-labeled evidence cache).
- **Task 3 — sme:** comprehensive fact-check. 37 verified claims, 3 discrepancies (D1 Yield Factor HIGH, D2 Merge/Vitamin A-C MEDIUM, D3 Images limits LOW), 14 unsupported, 3 ambiguous, 10 cross-module. → `factcheck.md`.
  - **Mid-run correction (Task-3 re-verify, evaluator-routed):** fact-check entry **V27 corrected** — NXT-39594 AC is only "Create a Menu Item tab"; the "Show on POS toggle controls POS attributes/Pricing" text is NXT-39594 **Description (TIER 3)**. AC-grounded source for that behavior is **NXT-30155**. Verified live via MCP.

## Per-template stages (Task 2 plan → Task 4 write → Task 5 review)
| Template | Plan | Draft | Final words | Retries | Final verdict |
|---|---|---|---|---|---|
| Long-form | `plan-long-form.md` | `drafts/20260529-item-management-long-form-draft.html` | 5,983 (ceiling 6,000) | 1 (Task 4: compress 9,426→5,983 + NXT-39594 fix) | **PASS** |
| Micro-guide | `plan-micro-guide.md` | `drafts/20260529-item-management-micro-guide-draft.html` | 1,198 (ceiling 1,500) | 1 (Task 4: drop 8th section + compress 1,890→1,198; Task 3: V27 fix) | **PASS** |
| TLDR | `plan-tldr.md` | `drafts/20260529-item-management-tldr-draft.html` | 687 (one page) | 2 (Task 4: 1,278→1,035→687, [TO VERIFY] → comments, row cells ≤12 words) | **PASS** |

All within the 3-retry-per-job ceiling. Eval verdicts: `drafts/*-draft.eval.json`.

## Evaluator routing observed
- Long-form retry-0 → Task 4 (length only; grounding/plan clean).
- Micro retry-0 → Task 3 (V27 grounding defect) + Task 4 (extra section + length).
- TLDR retry-0 → Task 4 (overflow + visible [TO VERIFY]); retry-1 → Task 4 (still over one page).

## Status gate
All three remain **`draft`**. The agent does not publish autonomously (CLAUDE.md "Status Gating"). Next step is human/SME review → `review` → `published`. The HIGH-severity D1 (Edible Yield Factor location) is surfaced as a `> [!warning] Discrepancy` callout in the long-form draft and a one-line discrepancy in TLDR; a human editor must resolve it before publish. ~22 (long-form) / 9 (micro) / 11-in-comments (tldr) `[TO VERIFY]` markers remain for the editor.
