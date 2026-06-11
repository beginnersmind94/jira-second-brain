# Support-judge calibration — 2026-06-08 (live)

The semantic **support judge** (`qbank_gate.llm_support_judge`) is the layer that does the flagging in
the quiz gate AND in the source-faithfulness eval. Every reliability number we quote is only as trustworthy
as this judge. This run measures *its own* discrimination against gold sets, live, via the real `claude` CLI.

Two framings of the **same** judge were scored back-to-back:

## Results

### 1. Quiz framing — `python -m eval.judge_eval --live` (32 cases: 17 unsupported, 15 supported)
The judge sees `(quote, stem, proposed-correct-answer)` exactly as the quiz gate gives it.

| Metric | Value | |
|---|---|---|
| **FNR** (unsupported judged "supported" — **DANGEROUS, gated**) | **5.88%** [1/17] | a wrong fact waved in |
| FPR (supported judged "unsupported" — friction) | 6.67% [1/15] | a good question rejected |
| agreement | 93.75% | |
| Gate (`--fnr-gate 0.0`) | **FAIL** | 5.88% > 0% |

- **FN — `wrong_answer-c05` (the one real miss).** quote: *"It allows vendors to plan in advance the quantity
  of foods needed in the course of the month, semester, and year."* · stem: *"Who prepares the food-quantity
  forecast?"* · keyed: *"Vendors plan the quantity…"* Gold = **unsupported**: the manager forecasts; vendors
  are *beneficiaries*, not the forecasters. The judge fell for the surface match (*"allows vendors to plan"* ≈
  *"vendors plan"*). A **beneficiary-as-actor** trap — the subtlest defect class, and the dangerous direction.
- **FP — `wrong_answer-c06` (not real friction).** A deliberate boundary probe: the stem asks column
  *placement* but the quote shown is the *formula* line. Its own gold rationale says *"on the displayed quote
  alone this should read as UNSUPPORTED."* It's labeled "supported" only because the answer is true *in the
  ticket*. So the judge's "unsupported" call is **defensible under the quote-only contract** — effective FP on
  legitimately-clean cases ≈ 0.

### 2. Faithfulness framing — `python -m eval.source_faithfulness --live` (6 rows: 3 over_reach, 3 faithful)
The same judge, asked whether a generated-guide CLAIM stays within its CITED span.

| Metric | Value | |
|---|---|---|
| **FN** (over-reach judged faithful — **DANGEROUS, gated**) | **0.0%** [0/3] | drift shipped |
| FP (faithful flagged over-reach — friction) | 66.7% [2/3] | |

Per-row (verified, `_faith_rows.py`):

| Row | Gold | Judge | |
|---|---|---|---|
| `FAITH-Q4-REAL` — the real Inventory-Distribution drift | over_reach | **over_reach** | ✓ caught |
| `FAITH-NUM-SYN` — 135°→140° number drift | over_reach | over_reach | ✓ |
| `FAITH-SCOPE-SYN` — "always / no exceptions" over-generalization | over_reach | over_reach | ✓ |
| `FAITH-HOTSHOT-REAL` — near-verbatim restatement | faithful | faithful | ✓ |
| `FAITH-SITETYPE-REAL` — *"distribution site type"* vs quote's *"that site type"* | faithful | **over_reach** | ✗ FP |
| `FAITH-ROLLBACK-REAL` — *"rollback"* vs quote's *"red … backwards arrow"* | faithful | **over_reach** | ✗ FP |

Both FPs are the **same pattern**: the claim *names* a thing the quote refers to only **anaphorically /
descriptively**, and the judge won't credit the unstated name. It flagged `SITETYPE` *even with the good span*.

## Interpretation — the judge is strictly quote-faithful

One consistent behavior explains every number above: **the judge credits only what the shown quote literally
states.** It does not resolve anaphora, import context, or trust ticket-knowledge outside the quote.

- That makes it **strong in the dangerous direction**: it caught every contradiction, number-swap, and
  over-generalization across both sets — including the **real Q4 guide drift**. FN is low (1/17 quiz, 0/3
  faithfulness).
- It makes **every FP a conservatism artifact** — declining to credit unstated specifics. For an
  anti-hallucination gate that bias is **correct**: an FP costs a re-review; it never ships a wrong fact.
- The **one genuine weakness is the residual FN**: subtle *wrong-actor / on-topic-but-non-responsive* traps
  (c05) slip ~6%. Surface lexical overlap is its blind spot.

## What this means for everything downstream

1. **The judge is a strong second layer, NOT a sufficient sole gate.** FNR > 0 means **"0 judge flags ≠
   provably clean."** Keep it layered behind the deterministic verbatim gate (exact) with a human in the loop.
   The two miss *different* things — verbatim gate misses semantic wrong-keys; the judge misses ~6% of
   surface-overlap traps — so the layered system is materially stronger than either alone, and neither is
   enough by itself.
2. **For guide-drift (source-faithfulness), it works end-to-end:** FN 0% including the real Q4. Layer it on
   the verbatim gate at publish — it catches drift the verbatim gate structurally cannot.
3. **Flag *counts* overstate the real-defect rate.** Because FP is high-by-design (conservatism), a raw
   "N flagged" must be **triaged**, never quoted as the defect rate. This is exactly what the 2026-06-08 quiz
   reliability sweep showed: 14 flagged → ~2–3 real wrong-keys after triage. The judge's own FNR also makes
   that 2–3 a **floor**, not a ceiling (it can miss a c05-style trap).
4. **Gate policy is an SME/Jaime decision, not mine to set.** The 0% FNR gate is aspirational for an LLM judge
   on hand-built adversarial traps. Options: (a) keep 0% as a *monitored* metric with the verbatim gate +
   human as the real safety net; (b) set a tolerance (e.g. FNR ≤ 10%) and invest in judge-prompt work to close
   c05-type beneficiary/actor traps. **Flagged for decision — not decided here.**

## Caveats
- Small gold sets (32 + 6). These are *discrimination* numbers on deliberately-hard cases, not a population
  defect rate.
- Numbers are REAL (live `claude` CLI judge vs hand-labeled gold), not offline fixtures.
- Re-run: `python -m eval.judge_eval --live` and `python -m eval.source_faithfulness --live` (needs `claude`
  auth; use the sibling `.venv` python).

---

## Update (same day) — judge prompt v2 closes the c05 FN

The v1 weakness above (FNR 5.88%, the `c05` *beneficiary-as-actor* miss) was fixed at the prompt level and
re-measured live. **This is a model-prompted calibration, not a hard guarantee** — per the learning-agent
CLAUDE.md *Enforcement vs. documentation* rule, the judge is a *calibrated capability / advisory* second layer;
the deterministic verbatim + lane gates remain the hard floor.

**The fix** (`qbank_gate.llm_support_judge` system prompt): added two general conditions beyond "does the quote
support the answer" — **(1) responsiveness** (the answer must answer *this* stem) and **(2) actor vs.
beneficiary** (if the stem asks *who/what does X*, the quote must show the named party *does* it, not merely
benefits/receives/is-enabled). Explicitly: *"allows / enables / lets / permits [party] to do X"* grants a
capability, and does **not** make that party the originator of X. No c05-specific text — it targets the class.

**Anti-overfit guard:** the gold set was grown 32 → 34 with two **held-out** same-class probes in *different*
domains, written to test the rule, not to author it:
- `wrong_answer-c10` — product / inventory actor-swap ("the system creates orders on behalf of the receiving
  sites" → answer wrongly keys the receiving sites as creators).
- `wrong_answer-c11` — compliance / food-safety non-responsive (a true, quote-supported temp statement keyed to
  a "who records it?" stem).

**Result (live, patched judge, 34 cases):**

| Metric | v1 (32 cases) | v2 (34 cases) | |
|---|---|---|---|
| **FNR** (dangerous, gated) | 5.88% [1/17] | **0.00% [0/19]** | c05 now caught; **c10 + c11 also caught** |
| FPR (friction) | 6.67% [1/15] | 6.67% [1/15] | **unchanged** — still only `c06` (the defensible boundary probe); no over-correction |
| agreement | 93.75% | 97.06% | |
| FNR gate (0%) | FAIL | **PASS** | |

**Reading it honestly:**
- The failure *class* is closed, and it **generalizes**: two cases in domains the rule wasn't written against
  both catch. But c10/c11 are *same-author* held-out probes, not a blind external set — "generalizes" is
  **evidenced, not proven at scale.** A truly independent holdout (SME-authored wrong-actor cases) is the next
  rigor step.
- **FPR did not move** — the responsiveness/actor rule did not make the judge reject any of the 15 supported
  controls. The judge's strict-quote-faithful conservatism (the desirable bias) is intact.
- **Scope:** one model (`claude-sonnet-4-6`), this prompt, 34 hand-built adversarial cases. **Recalibrate on
  model swap** (wiki §11.3).
- **The 2026-06-08 reliability sweep predates this fix** — it ran against the 5.88%-FNR judge, so its "2–3
  wrong-keys is a floor" caveat stands for that run; a re-run on the patched judge would likely catch more.
- **Uncommitted (HITL).** Prompt change + 2 gold rows not yet committed; no number is cleared for Jaime until
  an independent holdout backs the generalization claim.
