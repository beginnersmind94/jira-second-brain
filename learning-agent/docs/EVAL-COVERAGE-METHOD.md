# Coverage / Omission Measurement Method

*Next-step artifact for the **coverage** area. Companion to `docs/NEXT-EVALS-PLAN.md`
item #4 ("Coverage / omission for generated sets"). Plan + method spec — nothing built
yet. Tone follows `docs/STATE-OF-EVAL-2026-06-03.md`: no whitewashing.*

---

## 1. The gap, stated plainly

**Today, nothing that blocks publish measures what a generated quiz or study-set
*omits*. Every gate we have grades only the citations the artifact chose to emit.**

This is not a hunch — the team already wrote it down. From
`docs/STATE-OF-EVAL-2026-06-03.md:45`, verbatim:

> G1–G6 only validate that *emitted* citations are well-formed; they never check what
> the guide **omits** or whether it covers the facts a good guide must include.

and on the same line:

> **Coverage and source-quality — the core of research-agent eval — are unmeasured.**

The roadmap entry, `docs/NEXT-EVALS-PLAN.md:58-62`, verbatim:

> The gate checks *emitted* citations, never what a quiz *omits*. Per topic, define a
> "must-cover" keypoint list and measure % covered by a generated quiz/study-set. This is
> the currently-unmeasured gap.
> - Layer: diagnostic · Data: per-topic keypoint lists (SME-defined).

This document specifies *how* to build that keypoint list and *how* to score coverage.

### Why no existing gate can fire on an omission

Trace the publish path. A banked question reaches `verified` only if all three gate
checks pass (`qbank_gate.py:1-21` docstring; `gate_question`, `qbank_gate.py:77-105`):

1. **lane-match** — `check_lane` (`qbank_gate.py:37-43`): the cited span's lane equals the
   question's lane.
2. **verbatim** — `check_verbatim` (`qbank_gate.py:46-48`): the quote is a normalized
   substring of `span.get("text", "")`.
3. **support** — `llm_support_judge` (`qbank_gate.py:51-74`): does the cited quote support
   *this* stem + answer?

All three are **per-emitted-item**. The commit path gates only on per-item status:
`commit_gate_hook` (`qbank_gate_hooks.py:49-65`) allows the write iff the item's status is
in `COMMITTABLE`; the bank is append-only and, in `qbank_curation.py:15-16` verbatim:

> The bank is append-only and ONLY commit_to_bank() writes to it.

Nothing in this path models the *set* of facts a topic requires. An omitted keypoint
produces no item, so it produces no failing item, so no gate observes it. The guide suite
is the same shape — `eval/graders.py` G1–G6 (`graders.py:32-103`) all read the artifact's
*own* emitted content (`art["integ"]`, `art["html"]`, `art["sections"]`, `art["words"]`)
and never compare it to a required fact set.

**Consequence:** a compliance-lane quiz that skips the single most important fact a cashier
must know can still pass every gate, all-green. That is the dangerous direction this
metric exists to catch (see §4).

---

## 2. What a "keypoint" is, and who defines it

A **keypoint** is one atomic, must-cover fact for a topic — the kind of fact where
*omitting it* makes the study-set materially incomplete or unsafe, regardless of how
polished the emitted items are.

A keypoint is **not** a question and **not** a quote. It is a target the generated set is
measured against. Each keypoint carries:

| Field | Meaning |
|---|---|
| `keypoint_id` | Stable id, e.g. `tdz-01`. |
| `topic` | The topic slug this list belongs to, e.g. `temperature-danger-zone`. |
| `lane` | `compliance` or `product` — must match the lane vocabulary the gate enforces (`qbank_gate.py:25`, `VALID_LANES = ("product", "compliance")`). |
| `statement` | The fact, in plain language (SME-authored). |
| `source_quote` | A **verbatim** quote from the source that establishes the fact. |
| `source_ref` | Where the quote lives: source `.md` path + line(s), and the real content-layer `chunk_id` (see §3). |
| `severity` | `safety-critical` \| `core` \| `supporting`. Drives the weighted score in §5. |

### Who defines keypoints, and why it is not the model

Per `docs/NEXT-EVALS-PLAN.md:62`, the data source is **per-topic keypoint lists
(SME-defined)**. This is deliberate and load-bearing:

- **The model must not author its own answer key.** If the generator proposes the keypoint
  list and is then scored against it, coverage is circular — it measures whether the model
  agreed with itself, not whether it covered what a domain expert says matters. This mirrors
  the anti-circularity discipline already in the grade path (`eval/graders.py:8`: "NEVER call
  demo.enforce_citations in the grade path").
- **SME authorship is the calibration anchor.** A school-nutrition SME (or the published
  ICN assessment, where one exists) decides which facts are must-cover. The keypoint list is
  reviewed and version-pinned the same way a golden set is (`NEXT-EVALS-PLAN.md:70-75`).
- **A model MAY draft candidate keypoints to reduce SME toil, but the SME owns the final
  list** — drafting is not authoring. Any model-drafted keypoint is `draft` until an SME
  accepts it. (Same gating philosophy as resource `status` in the parent project's
  `CLAUDE.md`.)

> **Calibration note (do this before trusting the metric).** A keypoint list is only as
> good as its agreement with what real SMEs consider must-cover. Have ≥2 SMEs independently
> mark must-cover facts for the same topic and reconcile; a keypoint that one SME calls
> safety-critical and another omits entirely is a list-quality defect to resolve *before*
> the list gates anything. Without this, "82% covered" is precision theater on an
> unvalidated denominator.

---

## 3. Source-grounding rule for keypoints (read before authoring)

Each keypoint's `source_quote` must be **verbatim** from the source — same standard the
parent project's `CLAUDE.md` applies to guide edits ("Quote, don't paraphrase"). Two
distinct identifiers exist in this repo and must not be conflated:

- **Source `.md` line** — e.g.
  `data/icn/extracted/text/icn-food-safety-in-schools-participant-s-workbook.md:469`.
  This is the human-readable extraction; use it to quote the fact verbatim.
- **Content-layer `chunk_id`** — e.g.
  `icn-food-safety-in-schools-participant-s-workbook__p025__c001`
  (`data/icn/chunks/chunks.jsonl:904`). This is the unit the generator actually retrieves
  and a banked item cites. Format observed in the real file: `<asset_id>__p<NNN>__c<NNN>`.

> **Caveat I verified, do not skip.** The content-layer `chunk_id` page number is **not**
> the printed workbook page. The "Temperature Danger Zone — Here Are the Facts" text prints
> on workbook page "19" but lives in chunk **`__p025__c001`** (`chunks.jsonl:904`). Always
> resolve the real `chunk_id` by searching `chunks.jsonl` for the quote; never infer it
> from the printed page label.

> **Second caveat — the lane-prefixed span_id is NOT what `chunks.jsonl` uses today.** The
> gate's `lane_of_span_id` splits a span_id on the first `:` (`qbank_gate.py:32-34`), and the
> adversarial fixture uses ids like `compliance:icn-fs:p12:01`
> (`data/qbank/adversarial_fixture.json:13`). But that fixture's own header says its spans
> are *"AUTHORED test data (public-standard facts phrased here), not source reproductions"*
> (`adversarial_fixture.json:2`). The **real** content layer keys on `chunk_id`, with no
> `lane:` prefix (`chunks.jsonl:898,904`). So a keypoint's `source_ref` should record the
> real `chunk_id` and carry `lane` as its own field; do not pretend a `compliance:...` span_id
> already exists in `chunks.jsonl`. Mapping `chunk_id → lane-prefixed span_id` is its own
> (unbuilt) wiring step, not something to assume here.

---

## 4. Layer and dangerous direction (the honest framing)

**Layer: diagnostic — NOT canonical/publish-blocking (yet).** This matches
`NEXT-EVALS-PLAN.md:62` ("Layer: diagnostic") and the two-layer framing in
`NEXT-EVALS-PLAN.md:9-12` (canonical = stable reference rerun on every change; diagnostic =
slices and failure-mode analysis that explain *why*). Coverage starts diagnostic for three
honest reasons:

1. The denominator (the keypoint list) is **human-authored and not yet calibrated** across
   SMEs (§2). A gate built on an unvalidated denominator would block merges on a number we
   cannot yet defend.
2. Coverage of a *generated set* depends on retrieval + generation breadth, not on a single
   item's correctness; turning it into a hard gate without a calibrated target risks the
   brittle-failure direction the project warns against (`STATE-OF-EVAL:...` and methodology
   principle C01: failing a correct output that took a valid unanticipated path).
3. It needs a real corpus of generated sets to set a defensible threshold, which does not
   exist yet.

**Promotion path:** once the keypoint lists are SME-calibrated (§2 note) and a threshold is
justified against real generated sets, the `safety-critical` slice (§5) is the first
candidate to graduate into a canonical, publish-blocking check — because that is the slice
whose omission is unsafe, not merely incomplete.

**Dangerous direction (state it the way the plan does).**
`docs/NEXT-EVALS-PLAN.md:30`, verbatim, names the dangerous direction for the
generation component:

> confident omission of must-cover material

That is the whole point of this metric. The costly failure is **not** a fabricated fact —
the grounding gate already makes fabricated quotes hard (`qbank_gate.py:46-48` +
`:51-74`). The costly failure is a **silent omission inside the validated happy path**: an
item that is right-lane, verbatim, and supported, shipped all-green, while the one fact a
learner most needed never appears. A coverage metric is the only instrument that can fire
on "the safety-critical keypoint has zero grounded items in this set."

A directional asymmetry follows: **a false "covered" verdict is far more dangerous than a
false "missing" verdict.** Marking a safety-critical keypoint "covered" when no item truly
teaches it ships an unsafe gap as green. So the scoring (§5) requires a *grounded* item to
count a keypoint as covered, and the calibration target for any future keypoint-match judge
is its **false-"covered" rate** (the analogue of the false-negative emphasis the support
judge carries in `NEXT-EVALS-PLAN.md:27,40`).

---

## 5. How to measure coverage

### 5.1 Inputs
- A **generated set** for a topic: the quiz / study-set items, each with its `lane`,
  `stem`, options, and its grounding citation (`cite_span_id` + `quote`), exactly as the
  gate consumes them (`qbank_gate.py:82-100`).
- The **SME keypoint list** for that topic (§2), version-pinned.

### 5.2 Coverage of a single keypoint
A keypoint *K* is **covered** iff there exists at least one item in the generated set that:

1. **is on-keypoint** — the item's stem/answer teaches or tests the fact in `K.statement`
   (see matcher below), **and**
2. **is grounded** — that same item already passes the existing three-check gate
   (`gate_question`, `qbank_gate.py:77-105`): right lane, verbatim quote, support OK.

Condition (2) is what stops coverage from being gamed by an ungrounded item that merely
*mentions* the topic. **Coverage reuses grounding; it does not replace it.** An item that
merely mentions the danger zone but fails support does not cover the danger-zone keypoint.

> The **on-keypoint matcher** is the only judgment step. Start with the cheapest instrument
> that works and escalate only if needed:
> - **Tier 1 (deterministic pre-filter):** does the item cite the same `chunk_id`/`source_ref`
>   the keypoint points at, and/or share the keypoint's required tokens (e.g. `41`, `135`,
>   `danger zone`)? Free, runs first, mirrors the deterministic-before-LLM ordering the gate
>   already uses (`qbank_gate.py:20-21`).
> - **Tier 2 (LLM-as-judge, advisory):** "does this item teach/test keypoint *K*?" Treat it
>   as a **method, not a metric** — calibrate against SME labels before trusting it
>   (`NEXT-EVALS-PLAN.md:15-16`), and report its agreement + false-"covered" rate. Demote to
>   advisory until calibrated, exactly as the support judge is demoted relative to the
>   deterministic checks.

### 5.3 Topic coverage scores
Let *N* = number of keypoints for the topic.

- **Raw coverage** = (# keypoints covered) / *N*.
- **Severity-weighted coverage** — weight by severity so a missing `safety-critical`
  keypoint dominates a missing `supporting` one. Suggested weights (config-driven, not
  hardcoded — same posture as `TriageConfig` in `qbank_curation.py:56-62`):
  `safety-critical = 3`, `core = 2`, `supporting = 1`.
  Weighted coverage = Σ(weight of covered keypoints) / Σ(weight of all keypoints).
- **Safety-critical coverage (report separately, never average it away)** =
  (# covered `safety-critical` keypoints) / (# `safety-critical` keypoints).
  This is the slice that graduates to a gate first (§4). A single uncovered
  `safety-critical` keypoint should surface as a **named failure**, not a fractional dip in
  an aggregate — the danger is a *specific* missing fact, and an average hides it.

### 5.4 What the report must show
For each topic and generated set: the three scores above, **plus the explicit list of
uncovered keypoints by `keypoint_id` and `statement`.** The omission list is the product;
the percentage is the summary. A green percentage with a hidden uncovered `safety-critical`
keypoint is precisely the failure this metric exists to expose.

---

## 6. Concrete sample keypoint list — one real topic

**Topic:** `temperature-danger-zone` · **Lane:** `compliance`

**Source (read directly for this artifact):**
`data/icn/extracted/text/icn-food-safety-in-schools-participant-s-workbook.md`
("Temperature Danger Zone" section, lines 461–506; biological-hazard holding facts at
lines 330–347). Content-layer chunks: the "Here Are the Facts" + receiving/storing/
holding/serving facts are in `icn-food-safety-in-schools-participant-s-workbook__p025__c001`
(`data/icn/chunks/chunks.jsonl:904`); the cooling / reheating / transporting facts are in
`...__p026__c001` (`chunks.jsonl:905`).

> **Grounding status of this list:** every `source_quote` below is reproduced **verbatim**
> from the source `.md` at the cited line (degree symbols and en-dashes preserved as
> extracted). The `keypoint_id`s, `severity` ratings, and the plain-language `statement`s
> are **authored for this method spec** (the SME-authorship step in §2) and are clearly
> labeled as such — they are not reproduced from an ICN answer key. An actual deployment
> would have an ICN SME confirm the must-cover set and severities.

| id | severity | statement (authored) | source_quote (verbatim) | source_ref |
|---|---|---|---|---|
| tdz-01 | safety-critical | The temperature danger zone is 41 °F–135 °F. | "The FDA Food Code has identified the temperature danger zone as 41 °F–135 °F." | workbook.md:469 · chunk `__p025__c001` |
| tdz-02 | safety-critical | The danger zone matters because microorganisms grow quickly there and can make people ill. | "The temperature danger zone is the temperature range in which microorganisms grow quickly and sometimes reach levels that can make people ill." | workbook.md:463-464 · chunk `__p025__c001` |
| tdz-03 | safety-critical | Hold cold foods at 41 °F or below. | "Hold cold food at 41 °F or below." | workbook.md:336 · chunk `__p025__c001` (restated, Holding) |
| tdz-04 | safety-critical | Hold hot foods at 135 °F or above. | "Hold hot food at 135 °F or above." | workbook.md:335 · chunk `__p025__c001` (restated, Holding) |
| tdz-05 | core | Receive refrigerated foods at 41 °F or below and frozen foods at 32 °F or below. | "Receiving—Receive refrigerated foods at 41 °F or below, and frozen foods at 32 °F or  below." | workbook.md:482-483 · chunk `__p025__c001` |
| tdz-06 | core | Store refrigerated foods at 41 °F or below and frozen foods at 0 °F or below. | "Storing—Store refrigerated foods at 41 °F or below, and store frozen foods at 0 °F or below." | workbook.md:484-485 · chunk `__p025__c001` |
| tdz-07 | safety-critical | Cool food from 135 °F to 70 °F within 2 hours, and from 135 °F to 41 °F within a total of 6 hours. | "The FDA Food Code requires that foods be  cooled from 135 °F–70 °F within 2 hours and from 135 °F–41 °F within a total of 6  hours." | workbook.md:497-499 · chunk `__p026__c001` |
| tdz-08 | safety-critical | If food is not cooled from 135 °F to 70 °F within 2 hours, reheat to 165 °F for 15 seconds and start cooling over. | "If food is not cooled from 135 °F–70 °F within 2 hours, the food must be reheated to 165 °F for 15 seconds and the cooling process started over." | workbook.md:499-500 · chunk `__p026__c001` |
| tdz-09 | safety-critical | Reheat all leftover foods to 165 °F for 15 seconds within 2 hours. | "Reheating—Reheat all leftover foods to 165 °F for 15 seconds within 2 hours." | workbook.md:503 · chunk `__p026__c001` |
| tdz-10 | core | Transport cold foods at 41 °F or below and hot foods at 135 °F or above. | "T ransporting—T ransport cold foods cold at 41 °F or below, and hot foods hot at 135 °F or above." | workbook.md:504-505 · chunk `__p026__c001` |
| tdz-11 | core | Use a clean, sanitized, calibrated thermometer to take temperatures, and record them / keep logs. | "Use a clean, sanitized, and calibrated thermometer to take food temperatures." | workbook.md:477 · chunk `__p025__c001` |
| tdz-12 | supporting | Limit time in the danger zone during preparation; batch cooking is the best way to limit time. | "Preparing—Limit the time that food is in the temperature danger zone during  preparation. Batch cooking is the best way to limit time." | workbook.md:486-487 · chunk `__p025__c001` |

*(Extraction artifacts left intact and quoted as-is: the double space in "32 °F or  below",
the OCR spacing "T ransporting" / "T ransport", and the en-dash "135 °F–70 °F". A keypoint's
`source_quote` must match the source byte-for-byte so the existing verbatim check
(`qbank_gate.py:46-48`, which normalizes whitespace via `_norm`) resolves cleanly.)*

### 6.1 Worked example of the dangerous direction

Suppose a generated `temperature-danger-zone` quiz emits 8 items, each right-lane, verbatim,
support-OK — all-green on every existing gate. If those 8 items happen to cover tdz-03,
tdz-04, tdz-05, tdz-06, tdz-10, tdz-11, tdz-12 **but not tdz-01**, then:

- Every gate passes (the emitted items are all grounded).
- Raw coverage = 11/12 ≈ **0.92** — looks great.
- **Safety-critical coverage = 4/6 ≈ 0.67**, and the uncovered-keypoint list names
  **tdz-01 (the 41 °F–135 °F danger-zone definition itself) and tdz-07/08/09 if cooling was
  also skipped** — the single most foundational fact of the topic, silently missing inside a
  green dashboard.

This is the "confident omission of must-cover material" (`NEXT-EVALS-PLAN.md:30`) made
observable. No existing check fires on it; this one does — and it fires *by name*, not as a
fractional dip an aggregate would bury.

---

## 7. Scope, limits, and what this is NOT

- **This is diagnostic, not a publish gate (today).** It does not block merges; it produces
  a coverage report and a named omission list. Promotion of the `safety-critical` slice to a
  gate is gated on SME calibration of the keypoint lists and a defensible threshold (§4).
- **Coverage ≠ correctness ≠ learning.** Per `NEXT-EVALS-PLAN.md:85-89`: offline checks
  validate grounding and quiz quality; they "cannot tell us whether a cashier actually
  **learned**." A 100%-coverage set can still be pedagogically poor. Coverage answers one
  question only: *did the set include the facts an expert says it must?*
- **The keypoint list is the new attack surface.** A wrong, stale, or one-SME keypoint list
  produces confidently-wrong coverage numbers. Treat the list as version-pinned golden data
  with the same drift discipline as the bank (`NEXT-EVALS-PLAN.md:64-68`): when an ICN pack
  is re-imported, re-resolve every `source_quote`/`chunk_id` and re-confirm the must-cover
  set, because a hash can sit still while the meaning around a quote shifts.
- **No cross-topic borrowing.** A keypoint list is per-topic and per-lane. Do not reuse a
  compliance topic's keypoints to score a product topic — that is the cross-feature
  pattern-matching failure the parent `CLAUDE.md` anti-hallucination rules forbid.

---

## 8. Build checklist (for whoever picks this up)

1. Pick one topic; have an ICN SME (or use the published ICN assessment if it maps) confirm
   the must-cover keypoint set and severities. Start from the §6 list as a *draft*, not an
   answer key.
2. Run the §2 calibration note: ≥2 SMEs mark must-cover independently; reconcile.
3. Resolve each `source_quote` to a real `chunk_id` by searching `chunks.jsonl` (do **not**
   trust printed page numbers — §3 caveat).
4. Implement §5.2 coverage with the Tier-1 deterministic matcher first; only add the Tier-2
   LLM matcher if Tier-1 underperforms, and calibrate it (false-"covered" rate) before
   trusting it.
5. Emit the §5.4 report: three scores + the named uncovered-keypoint list, with
   `safety-critical` omissions surfaced as named failures.
6. Re-run on real generated sets to set a defensible threshold *before* proposing the
   `safety-critical` slice for promotion to a publish gate.
