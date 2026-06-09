# Trace-back audit — Inventory Distribution guide

**The backstop the automated gates can't be.** Per the eval wiki's *Grounding chain* section: "A 0% automated
FN-rate with no trace-back run is not a safe guide — it is an unmeasured one." Every automated layer we have
(verbatim gate, support judge, source-faithfulness grader) checks a claim against its *immediate* parent. This
audit traces a sampled claim **all the way to the root source** — Justin Miller's Inventory Distribution
Showcase transcript — because that's the only thing that catches guide↔transcript drift below a clean per-hop
gate.

| | |
|---|---|
| Guide under audit | `drafts/20260608-155920-inventory-long-form-af5d2c.html` (live-generated from the transcript) |
| Root source | `raw/transcripts/20260608-155920-inventory-inventory-distribution-transcript-md.md` (Justin Miller, Feb 5 2026) |
| Sample basis | the 10×6 quiz reliability sweep (`docs/QUIZ-RELIABILITY-INV-DISTRIBUTION.md`) |
| Sampling rule (wiki) | weighted to **P0** facts and to claims the **support judge PASSED** — we are hunting the judge's *misses*, not re-checking its hits |
| Judge calibration context | support judge measured FNR **5.88%** (`docs/JUDGE-CALIBRATION-2026-06-08.md`) — a real, non-zero miss rate, which is *why* this human sample exists |
| Prepared | 2026-06-08 (scaffold — **not yet run**) |
| Tracer | **SME or independent reviewer — NOT the author.** This sheet was scaffolded by the content generator; an independent SME must fill every verdict. Candidate root spans below were located by the author and may be incomplete — confirm them, don't assume them. |

## How to run this (SME, ~30–45 min)

For each row: read the **quiz claim**, read the **candidate root span(s)** at the cited timestamp in the
transcript (confirm the quote and that it's the *right* root — find a better one if mine is incomplete), then
answer the **faithfulness question** and set a verdict:

- **PASS** — the claim is fully supported by the root, at the root's level of confidence.
- **DRAFT** — the claim drifts: over-reaches, reframes, conflates two rules, or states something the source
  hedged as if it were settled. **Per the wiki: any source-faithfulness drift on a P0 claim → the guide goes
  to DRAFT, regardless of a green automated dashboard.**

Then fill the **Results rollup** at the bottom. That rollup *is* the gold-label pipeline that makes the
automated FN-rate real — it is not extra work.

## Sample summary

| # | Priority | Claim (short) | Judge verdict | SME verdict |
|---|---|---|---|---|
| 1 | **P0** | Distributions started before the seasonal contract stay on the main contract | **PASSED** | ☐ PASS ☐ DRAFT |
| 2 | **P0** | Seasonal contract auto-reverts to main when its date range ends | **PASSED** | ☐ PASS ☐ DRAFT |
| 3 | **P0** | The internal vendor contract controls item grouping, site grouping, schedule | **PASSED** | ☐ PASS ☐ DRAFT |
| 4 | **P0** | Revert is available at Pending Receipt, gone once a site creates a receipt (Partly Received) | **PASSED** | ☐ PASS ☐ DRAFT |
| 5 | **P0** | Rollback is gated by a single permission | **PASSED** | ☐ PASS ☐ DRAFT |
| 6 | **P0** | A site becomes eligible to link to an internal vendor by being assigned the distribution site type | flagged* | ☐ PASS ☐ DRAFT |
| 7 | P1 | The available-quantity display updates in real time | **PASSED** | ☐ PASS ☐ DRAFT |
| 8 | P1 | A hotshot is a manual distribution created from scratch, not from received orders | **PASSED** | ☐ PASS ☐ DRAFT |
| 9 | P1 | In a hotshot, the system auto-creates orders when the distribution site marks the shipment shipped | **PASSED** | ☐ PASS ☐ DRAFT |

\* Row 6 was *flagged* by the judge, not passed — included as a cross-check that our triage ("answer correct,
citation weak — not BS") holds against the root. Every other row is a judge **pass** (the hunt-the-misses set).

Priorities are the author's proposal — **SME may re-tier.**

---

## Audit rows

### Row 1 — Contract precedence for already-started distributions  · **P0 · judge PASSED · ⚠ highest-value check**

**Quiz claim (keyed correct, appeared runs 1, 2, 8):** *"What happens to distributions that were started before
a seasonal contract was created? → They remain bound to the main contract."*

**Why it's here:** the support judge passed this every time (the guide states it near-verbatim, so quiz↔guide is
clean). But this is the original Q4 drift suspect, and the root has **two distinct rules** the claim sits
between:

- **Candidate root A — order-date rule (17:01):** *"from June 1st to July 24th, this contract will basically
  take over and override…supersede the main contract. So if I'm placing orders as a site for May 30th, I'm
  going to be part of the main contract here. If I'm placing an order for July 1st, I'm going to be part of the
  seasonal contract."* → which contract applies is decided by the **order's date**.
- **Candidate root B — already-started rule (47:48):** *"Technically, these three distributions also fall
  within the seasonal contract. However, I started these before the seasonal contract was active. So…this
  distribution will still be bound to the regular contract because that's when I started it. **At least I'm
  pretty sure.**"*

**Faithfulness question:** The claim traces to root B — but (a) Justin **hedges it** ("at least I'm pretty
sure"); does the guide state it as settled fact? (b) Is the guide **conflating** the start-date rule (B) with
the distinct order-date rule (A)? (c) Is "started before the seasonal contract **was created**" the same as
Justin's "before it **was active**"? Created ≠ active if a contract is configured ahead of its date range.

**SME verdict:** ☐ PASS ☐ DRAFT  **Notes:** ______________________________________________

---

### Row 2 — Seasonal contract auto-revert  · **P0 · judge PASSED**

**Quiz claim (runs 3, 5):** *"What happens automatically when a seasonal contract's date range ends? → The
system reverts automatically to the main contract."*

**Candidate root (49:45):** *"when the date range ends, it just it just reverts back."* Supporting (17:01):
*"as long as this date range is applicable…this contract will basically take over and override…supersede the
main contract."*

**Faithfulness question:** Is "reverts automatically to the main contract" faithful to "it just reverts back"?
(Justin doesn't name *what* it reverts to in the 49:45 line — confirm the main-contract target is supported by
the surrounding context, not added.)

**SME verdict:** ☐ PASS ☐ DRAFT  **Notes:** ______________________________________________

---

### Row 3 — What the internal vendor contract controls  · **P0 · judge PASSED**

**Quiz claim (runs 1, 5, 7, 8):** *"What does the internal vendor contract control? → How items are grouped,
how sites are grouped, and how the distribution schedule is executed."*

**Candidate root (0:59):** *"the vendor contracts…dictates basically everything. It dictates how the items are
grouped, how the sites are grouped, how the schedule is executed."*

**Faithfulness question:** This one looks cleanly supported — confirm. **Calibration note for the SME:** in two
*other* runs the generator keyed this same stem to **"physical location and warehouse capacity"** (run 6) and
**"which staff hold the rollback permission"** (run 10); the support judge correctly **caught both** as
unsupported. Confirm those two are indeed wrong against this root (they should be) — it validates the judge's
true positives.

**SME verdict:** ☐ PASS ☐ DRAFT  **Notes:** ______________________________________________

---

### Row 4 — When revert is / isn't available  · **P0 · judge PASSED**

**Quiz claims (runs 2, 4, 6, 7, 9, 10):** *"At Pending Receipt a shipment can still be reverted"* and *"once at
least one site has created a receipt (Partly Received), revert is no longer available."*

**Candidate root (36:25):** *"Until sites create a receipt, so you see here we got pending receipt, I can
technically revert it."* And (37:14): *"Partly received. Now I can no longer revert it…because Johnson High
already created their receipt."*

**Faithfulness question:** Both halves appear directly supported — confirm the status labels ("Pending
Receipt", "Partly Received") match the product UI and aren't paraphrased into something subtly off.

**SME verdict:** ☐ PASS ☐ DRAFT  **Notes:** ______________________________________________

---

### Row 5 — Rollback gated by a single permission  · **P0 · judge PASSED**

**Quiz claim (run 8):** *"What happens when a staff member does not have the rollback permission? → They cannot
reverse any of the rollback-covered steps."*

**Candidate root (56:51):** *"we have this function, the rollback, tied to like a distinct permission…not
everybody has that ability to rollback…they're all tied to a single permission. So if you want to prevent
people from doing that, they can."*

**Faithfulness question:** "cannot reverse any of these steps" is a reasonable read of "prevent people from
doing that" — confirm it's not over-stated (e.g., scope of "any" steps: shipping → review, per "we have it all
the way from shipping all the way back to review").

**SME verdict:** ☐ PASS ☐ DRAFT  **Notes:** ______________________________________________

---

### Row 6 — Distribution site type → eligibility  · **P0 · judge FLAGGED (cross-check)**

**Quiz claim (every run, 10×):** *"What makes a site eligible to be linked to an internal vendor? → Being
assigned the distribution site type."* The support judge **flagged** this every time ("the quote says *that
designation* / *that site type*, not *distribution site type*").

**Candidate root (0:01):** *"any site with an inventory license can be assigned with the inventory distribution
site type…any site can be assigned with that site type, which then makes them eligible to be linked to an
internal vendor."*

**Faithfulness question:** Against the *root*, is the answer **correct**? (Our triage says yes — "inventory
distribution site type" is in the transcript at 0:01 — the judge flag was citation-weakness, not a wrong
answer.) If you agree, the open decision is for the **generator**, not the quiz: should the guide cite the
0:01 naming span instead of the anaphoric "that site type" span, or is some friction irreducible?

**SME verdict:** ☐ PASS ☐ DRAFT  **Notes:** ______________________________________________

---

### Row 7 — Available-quantity display updates in real time  · P1 · judge PASSED

**Quiz claim (runs 1, 2, 4, 6, 9, 10):** *"Which distribution-preference setting updates in real time while a
site is actively placing an order? → The available-quantity display."*

**Candidate root (43:31):** *"when I'm ordering from an internal vendor, I see this available quantity…If you
were to change that setting, this would immediately update. So if I'm a site and I'm placing an order…if I come
here and I just click apply again and I refresh the screen, it's possible that this might switch."* Caveat
(42:15): *"the distribution at the time you create it…will anchor itself to that…Some of the settings will
[carry over]."*

**Faithfulness question:** Justin hedges ("if I refresh the screen", "it's possible that this might switch") and
draws a line: the **display while ordering** updates, but **distributions already created are anchored**. Does
the guide preserve that distinction, or imply the setting updates live everywhere?

**SME verdict:** ☐ PASS ☐ DRAFT  **Notes:** ______________________________________________

---

### Row 8 — Hotshot definition  · P1 · judge PASSED · clean control

**Quiz claim (runs 3–7, 9, 10):** *"How does a hotshot distribution differ from a standard one? → It is a manual
distribution created from scratch rather than from received orders."*

**Candidate root (23:26):** *"They're simply manual distributions that you create from scratch instead of from
received orders."*

**Faithfulness question:** Near-verbatim — included as a **clean control** (a row that should obviously PASS; if
an SME marks it DRAFT, the audit rubric itself needs review).

**SME verdict:** ☐ PASS ☐ DRAFT  **Notes:** ______________________________________________

---

### Row 9 — Hotshot auto-order timing  · P1 · judge PASSED

**Quiz claim (runs 1, 8):** *"In a hotshot, at what point does the system automatically create orders for
receiving sites? → When the distribution site marks the shipment as shipped."*

**Candidate root (36:25):** *"the sites creating their receipts is true. Triggered by the distribution site
marking the shipment as shipped."* Supporting (25:10): *"when I ship that product to them, an order will be
created in the system on their behalf."*

**Faithfulness question:** Confirm the trigger is "marks the shipment as shipped" and not conflated with a
different step (e.g., completing assignment or picking).

**SME verdict:** ☐ PASS ☐ DRAFT  **Notes:** ______________________________________________

---

## Results rollup (SME completes — this is the gold-label output)

```
Trace-back audit: Inventory Distribution guide
Date run:        ____________      Tracer: ____________ (must not be the content author)
Claims sampled:  9  (P0: 6, P1: 3; judge-passed: 8, judge-flagged cross-check: 1)
Source-drift found:        ___ / 9
  └ on P0 claims:          ___ / 6     ← any P0 drift ⇒ guide to DRAFT
Guide decision:  ☐ PASS (publish-eligible)   ☐ DRAFT (drift on ≥1 P0 claim)
Notes / new fixtures to add: ____________________________________________
```

**Feed the result back, per the wiki:**
1. Any DRAFT row → the guide returns to draft until the generator is corrected.
2. Each confirmed drift becomes a **new `faithfulness_fixture.jsonl` row** (like `FAITH-Q4-REAL`), so the
   automated grader regresses against it forever.
3. The drift count vs. the support judge's automated FN-rate is the **judge's real-world blind-spot estimate** —
   it calibrates the headline number for Jaime.
4. Update the dashboard line: `Trace-back audit: 9 sampled, D drift, last run <date>` — kept **distinct** from
   the automated FN-rate, never substituted for it.

## Provenance & caveats
- Quiz claims are **REAL** (from the live 10×6 sweep, `quiz-reliability-results.json`). Root spans are verbatim
  from the transcript with timestamps; minor OCR spacing was tidied for readability — verify against the file.
- This is **one guide, one topic.** A clean audit here does not certify the generator everywhere.
- The author located candidate root spans to save SME time; the wiki requires the **tracer be independent of
  the author**, so treat my candidates as leads to verify, not findings.
