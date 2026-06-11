# Judge calibration plan — the semantic-support judge

*The protocol to calibrate `qbank_gate.llm_support_judge` against the human-labeled gold
set (`eval/judge_gold_set.jsonl`) using a to-be-built scorer (`eval/judge_eval.py`), before
its verdict is allowed to block a publish. This is `NEXT-EVALS-PLAN.md` item #1 ("do first")
and the build that closes `eval/EVAL-SPEC.md` open-q #4.*

> **Status check, read first (no whitewashing).** The gold set **exists** (32 cases,
> verified by direct read — see §1). The scorer **does not** — `eval/judge_eval.py` is
> not on disk; `eval/triage_eval.py` and `eval/scope_eval.py` are the proven sibling
> patterns it must follow. And there is a **schema mismatch** between the gold set and the
> judge's calling convention that the scorer must bridge (§4.1) — this is real work, not a
> wiring detail. Until the scorer is built and a baseline agreement number is recorded, the
> judge is an **uncalibrated instrument** and its verdict must not gate anything. The merged
> methodology digest names this exact standing gap: "The one real LLM judge
> (`qbank_gate.llm_support_judge`) has **no calibration set and no measured judge↔human
> agreement** yet" (`docs/eval-methodology-digest.md`, "Standing gaps").

---

## 0. Why this is item #1

The judge is the *only* place in the entire grounding architecture where an LLM judges
**meaning**. The two deterministic checks ahead of it — lane-match and verbatim-substring —
cannot see semantics: a quote can be in the right lane and a perfect verbatim substring and
still not support the answer. The canonical example, from the gate's own docstring:

> "Catches the inversion verbatim cannot: 'held at 135°F or higher' is a MINIMUM; a stem
> asking the MAXIMUM with answer '135°F' is verbatim-true yet semantically false. This is a
> GATE failure, not a generator-quality issue, so it lives here — not in a separate eval."
> — `qbank_gate.py`, module docstring

So the judge decides whether a verbatim-but-misleading question ships. That makes its
**false-negative rate** (a bad item judged "supported") the thing the whole trust story rests
on — and an LLM judge is a *method, not a metric*, which "must be validated, calibrated, and
interpreted carefully" before its scores are trusted (Doc 1, p14, quoted in
`eval-methodology-digest.md` Theme D1). This plan is how we earn that trust, or find the
judge isn't trustworthy yet.

---

## 1. The gold set — what's actually on disk (`eval/judge_gold_set.jsonl`)

Verified by direct read + count, **2026-06-07**. **32 cases** (the roadmap target is ~50 —
this set is **below target and must grow before the calibration number is treated as the ship
gate**; see §8).

**Distribution (counted, not estimated):**

| Axis | Breakdown |
|---|---|
| `ground_truth_support` | `supported` = 15, `unsupported` = 17 |
| `defect_type` (on the 17 unsupported) | `inversion` = 4, `number_swap` = 4, `over_claim` = 5, `wrong_answer` = 4; `null` on all 15 supported |
| `lane` | `compliance` = 24, `product` = 8 |
| `quote_verbatim` | `true` for all 32 |

**Schema (keys present on every row):** `id`, `lane`, `source_anchor`, `quote`,
`quote_verbatim`, `stem`, `answer`, `ground_truth_support`, `defect_type`, `rationale`.

**Two properties that make this set usable as a calibration anchor:**

1. **It is two-sided by construction.** 15 supported / 17 unsupported. This is the
   anti-one-sided-optimization discipline: "Test both the cases where a behavior should occur
   and where it shouldn't. One-sided evals create one-sided optimization" (Doc 2, p15, digest
   Theme F1). A set of only-unsupported cases would reward a judge that says NO to everything;
   the 15 supported near-misses make that degenerate judge fail on FPR. Several supported
   cases are *deliberately adversarial against the judge* — e.g. `over_claim-06` uses "for
   every age/grade group," which superficially looks like over-claiming but is **licensed** by
   the quote ("for all age/grade group meal patterns ... is the same, 1 cup"). That case exists
   precisely to catch a judge that "reflexively fail[s] any 'every/all' answer."

2. **`quote_verbatim` is `true` on all 32.** This is intentional and important: the gold set
   isolates the **support** decision. Verbatim and lane are already settled deterministically
   upstream (and are 0-by-construction failures on this set), so every case is one the first
   two checks would *pass* — the judge is the only thing standing between it and the bank. We
   are calibrating the judge on exactly the inputs it will actually see in production: lane-OK,
   verbatim-OK, support-unknown.

### 1.1 Defect taxonomy (the four unsupported families + the supported control)

Each family is a distinct *way a verbatim quote can fail to support an answer*. The rationales
in the file are the labeling rubric — they state the trap and why a shallow judge falls for it.
Quoted verbatim from the gold set:

- **`inversion`** (4) — a bound flipped in direction (min↔max, floor↔ceiling). Canonical
  dangerous case. From `supported-icn-hothold-inversion`: *"the quote says hot food must be
  held at 135 °F OR ABOVE (a floor); the answer flips the direction to '135 °F or below' (a
  ceiling), which would license holding hot food in the danger zone ... a shallow token-overlap
  judge sees a match and wrongly says 'supported'."* This is the **C05 dangerous direction** in
  the methodology checklist — "a minimum stated as a maximum."
- **`number_swap`** (4) — right field, wrong figure or unit. From `number_swap-002`: the
  temperature and time-to-reheat match the quote exactly, but *"the quote says '15 seconds', the
  answer says '15 minutes'. Seconds-vs-minutes is the single most consequential and
  easiest-to-miss unit error."*
- **`over_claim`** (5) — a scope/quantifier dropped or inflated. From `over_claim-01`: *"the
  quote licenses an exclusive-OR ('either... or... only toward one meal component ... not
  both'). The answer inverts the explicit 'not both' into 'always both' while reusing the
  quote's exact component names, so it reads as grounded."*
- **`wrong_answer`** (4) — on-topic but non-responsive; lifts an adjacent noun/clause from the
  quote and offers it for a different question. From `wrong_answer-c03`: *"the quote tells you
  WHAT production records are part of ... The stem asks WHO verifies and signs them ... A process
  is not a person; the quote does not name a signer. On-topic, non-responsive."*
- **`null` / supported control** (15) — faithful restatements that preserve every threshold,
  direction, unit, and scope. These measure **FPR** (a clean restatement wrongly rejected). From
  `supported-icn-coldhold`: *"A judge that flags this as unsupported is a false positive — this
  case measures FPR on a clean direct-restatement."*

**Paired-trap design (a property to preserve when the set grows).** Several cases come in
matched supported/unsupported pairs that share a quote or topic, isolating the *single bit* that
flips the verdict: `number_swap-003` (corrupted, 140→240) vs `number_swap-008-SUPPORTED` (the
genuine 140 mg entailment); `supported-prod-cndb-cadence` vs `supported-prod-cndb-overclaim`
(same CNDB quote, faithful cadence vs fabricated "automatic ... no action required" rollout). A
judge that scores a pair inconsistently is revealing it keys on topical overlap, not the
load-bearing clause. **New cases should be added in pairs**, not as one-off positives or
negatives.

### 1.2 Synthetic vs. real provenance (must be labeled — and currently is, implicitly)

`source_anchor` is the provenance field. By direct read, most cases anchor to **real**
ICN/USDA extractions (`data/icn/extracted/text/...`), and a minority to the **demo product
fixtures** (`item-management-fixture.json`, `menu-planning-fixture.json`). The two `product`
over-claim cases (`over_claim-07`, `over_claim-08`) carry an explicit in-rationale tag:
*"Synthetic EVAL FIXTURE; not product guidance."*

This honors the project rule that synthetic data must be labeled, and the methodology: synthetic
data "should not be treated as a perfect substitute for real historical data unless it has been
validated against realistic production patterns" (Doc 1, p11, digest Theme K2). **Action for the
scorer (§4):** add a first-class `provenance` field (`real` | `synthetic`) rather than relying
on a rationale substring, and report agreement **sliced by provenance** so a number inflated by
synthetic cases is visible. This mirrors what `triage_eval.py` already does with its `source`
field and the runner banner: *"NOTE: all cases are synthetic. Collect REAL ... edits ...
(Anthropic: evaluate on real traffic, not only synthetic)."*

---

## 2. Labeling protocol — who defines, runs, and validates

`NEXT-EVALS-PLAN.md` item #1 assigns three roles explicitly: *"Cross-functional: PM defines
the 'good' bar; eng runs it; DS validates the labels."* This plan operationalizes that split so
the label set is not graded by the same hand that wrote it.

| Role | Owns | Concretely |
|---|---|---|
| **PM** | The "good" bar | Defines, in prose, what "the quote supports the answer" *means* for this product — anchored to the existing stance: "the safe default is 'not supported,' never an invented capability" (`Learning-Studio-eval-context.md` §2). PM signs off the defect taxonomy (§1.1) and adjudicates disputed labels. PM does **not** see the judge's predictions before fixing the gold labels (avoids anchoring the bar to the instrument). |
| **Eng** | Runs the harness | Builds and owns `eval/judge_eval.py`, runs the trials, computes agreement/FNR/FPR, maintains the holdout lock. Eng does **not** relabel cases to make a number move. |
| **DS** | Validates the labels | Independent of label authorship. Re-labels a sample blind, computes **human↔human agreement** as the noise floor (see below), reviews every PM-eng disagreement, and signs that the gold labels are sound *before* any judge number is reported against them. |

**The noise floor comes first.** Before measuring judge↔human agreement, DS establishes
**human↔human agreement** on a blind re-label of a sample (target the full 32 while the set is
small). This is the ceiling the judge can possibly hit and the test of whether the labels are
clean enough to grade against: "A good task is one where two domain experts would independently
reach the same pass/fail verdict ... Ambiguity in task specifications becomes noise in metrics"
(Doc 2, p15, digest Theme H3). If two humans disagree on a case, the *judge's* disagreement on
that case is uninterpretable — quarantine it (§2.1), don't score it.

**Reading failures is part of the protocol, not optional.** Eng + DS read the judge's
transcript on every disagreement: "When a task fails, the transcript tells you whether the agent
made a genuine mistake or whether your graders rejected a valid solution" (Doc 2, p17, digest
Theme G3). For this judge the inverse matters most — a *correct* NO on a case a human mislabeled
"supported" must not be charged against the judge.

### 2.1 The boundary probe is a label-discipline test, not a judge test

`wrong_answer-c06` is flagged in its own rationale as a case where, **on the displayed quote
alone**, the ground truth should read *unsupported* even though its `ground_truth_support` is
recorded as `supported` and the answer is independently true in the ticket: *"Under the gate's
contract the judge sees only quote+stem+answer, so on the displayed quote alone this should read
as UNSUPPORTED ... Kept to test judge consistency on quote/answer mismatch where the answer is
independently true in the ticket but not in THIS quote."* Its corrected partner `c06b` is the
clean supported version.

This is a deliberate landmine. The labeling protocol must resolve it before scoring, because the
judge's contract is **quote+stem+answer only** (verified: `gate_question` passes
`q["quote"], q["stem"], correct` to the judge — `qbank_gate.py` line 100). DS decision required,
documented in the case, one of:
(a) **relabel** `c06`'s `ground_truth_support` to `unsupported` to match the judge's actual
contract (the contract-faithful choice), or
(b) **move** `c06` to a quarantined `boundary_probe` split scored separately and excluded from
the headline agreement number.
Either is defensible; leaving it as a silently-contradictory `supported` case in the headline
set is not — it would charge the contract-faithful judge with a false negative.

---

## 3. Metrics — agreement, the FNR gate, FPR as tracked friction

### 3.1 The primary metric is judge↔human agreement (per-component, not a global score)

The metric must follow the component: "metric selection is not just a technical detail. It is a
product decision" (Doc 1, p16, digest Theme C1). The support judge's job is *to agree with a
human on whether a quote supports an answer*, so its primary metric is **judge↔human agreement**
— not the judge's own pass-rate, and not a score borrowed from a sibling component.
`NEXT-EVALS-PLAN.md`'s Component→metric table assigns exactly this: "Semantic-support judge
(LLM) → judge↔human agreement." This is distinct from every neighbor's metric (gate=invariants,
lane=leak rate, triage=recall on `needs_human`, generation=coverage) — satisfying methodology
checklist **C04** (metric-per-component).

Report agreement three ways, never collapsed to one number:
- **Overall agreement** = (judge verdict == human label) / N.
- **Per-class agreement** = agreement on the 15 supported and the 17 unsupported, separately
  (an aggregate hides a judge that aces one class and fails the other).
- **Per-defect-family agreement** = agreement within `inversion` / `number_swap` / `over_claim`
  / `wrong_answer` (which trap leaks?).

### 3.2 The FNR gate (the dangerous direction)

Define the **unsupported** label as the positive/must-catch class (the judge saying NO to a bad
item is the catch). Then, mirroring `triage_eval.py`'s confusion-matrix scorer exactly:

- **FNR (false-negative rate) = (unsupported cases the judge called "supported") / (17
  unsupported cases).** This is **the dangerous direction** — a verbatim-but-misleading item
  judged "supported" and shipped. It is methodology checklist **C05**'s named danger ("a minimum
  stated as a maximum ... is judged 'supported' and ships") and `NEXT-EVALS-PLAN.md`'s
  Component→metric "Dangerous direction" for this row: "**false negatives** (bad passed as
  good)." **This is the gated metric.** The `--live` scorer exits non-zero when `FNR > gate`,
  identically to how `triage_eval.py --live` exits non-zero when `FNR > --fnr-gate` and
  `scope_eval.py --live` exits non-zero when `wrong_module_rate > --wrong-gate`.

- **FPR (false-positive rate) = (supported cases the judge called "unsupported") / (15 supported
  cases).** This is **tracked friction, not a failure**: a false positive demotes a *good*
  question to `needs_human`, costing reviewer time but never shipping a wrong answer. Track it,
  report it, do not gate on it. Same posture `triage_eval.py` takes: *"FPR — over-trigger ...
  Only costs an extra (free) check — tracked as friction, not failure."*

> **Why separate, asymmetric rates (not one accuracy number).** This is the explicit lesson the
> sibling evals import from Anthropic's auto-mode classifier: "report **FPR (needless friction)
> and FNR (dangerous misses) separately**, weight toward FNR" (`EVAL-SPEC.md` §7, citing *How we
> built Claude Code auto mode*, Mar 2026). A single accuracy figure lets a low-FPR/high-FNR judge
> — the exact dangerous shape — hide behind good aggregate numbers.

### 3.3 What gate threshold to set

`EVAL-SPEC.md` open-q #4 proposes the trust bar: *"gate trust at ≥90% agreement on tier-lie
cases."* For this judge the analogue is **agreement on the unsupported (defect) cases ≥ a PM/DS-set
floor, with FNR as the hard gate.** Concretely, the recommended starting policy (PM+DS to ratify
on the first calibrated run, §6):

1. **FNR gate is the hard, exit-code gate.** Start the *measurement* at `--fnr-gate 0.0` to make
   every miss visible in CI output (this is what `triage_eval.py`/`scope_eval.py` default to on
   their curated clear-cut sets), then have PM+DS set the **shippable FNR** explicitly from the
   observed baseline distribution. Do **not** assert a threshold a priori — `EVAL-SPEC.md`
   open-q #1 already flags that the project's thresholds (G4 density, the 0.9 ratios) are
   "asserted, not derived"; do not repeat that mistake here. The auto-mode precedent is that a
   *named* non-zero FNR (theirs ~17% on real overeager actions) shipped *with a human backstop* —
   so a non-zero FNR can be acceptable here too, **because** the judge sits in front of triage +
   human approval, not because the judge is trusted alone.
2. **FPR has no gate, only a tracked budget.** PM sets a friction ceiling above which the judge is
   "too trigger-happy to be worth it" — a product call, reported, not enforced by exit code.
3. **Until a baseline is recorded and a floor ratified, the judge's verdict does not gate
   publish** (§5).

---

## 4. The scorer — `eval/judge_eval.py` (to build, mirroring the proven siblings)

Build it as a near-twin of `eval/triage_eval.py` and `eval/scope_eval.py` — same shape, same
guarantees, so it inherits their proven discipline. Required structure:

1. **Offline mode (default, no SDK, no auth): prove the dataset + scorer before trusting any
   judge.** Run an **oracle** (predict = gold label) that MUST score FNR=0 / FPR=0, and **two
   degenerate baselines** that MUST land where theory says, with `assert`s that fail loudly if
   the scorer is wrong:
   - **always-"unsupported"** (judge says NO to everything) → FNR = 0, FPR = 1.0. Catches a
     no-discrimination judge that passes the FNR gate by rejecting everything.
   - **always-"supported"** (judge says YES to everything) → FNR = 1.0, FPR = 0. The worst,
     dangerous degenerate — ships every defect.
   This is exactly the `triage_eval.py` offline contract (oracle + always-substantive +
   always-stylistic, each `assert`ed) and `scope_eval.py`'s (oracle + always-pick-first-module).
   It guards the **eval itself**: a green dashboard from a broken scorer is worse than no scorer.

2. **`--live` mode: score the real judge, exit non-zero on `FNR > --fnr-gate`.** Call the real
   `qbank_gate.llm_support_judge` (or `gate_question` with the live judge) under a concurrency
   semaphore, parse YES/NO, and on any parse/SDK error fall back to the **safe** verdict — for
   this judge the safe fallback is **"unsupported"/NO** (abstain conservatively), the analogue of
   `triage_eval.py`'s `SAFE_DEFAULT = "substantive"`. Print the confusion matrix, the three
   agreement cuts (§3.1), FNR (gated) and FPR (tracked), and the **ID lists** of misses
   (`under_trigger`-style) so failures are inspectable — `triage_eval.py` prints
   `under_trigger_ids`; do the same here as `false_negative_ids` / `false_positive_ids`.

3. **`--trials` with k≥3 default and pass^k aggregation for the gated direction** (§4.2).

4. **Slice every reported number by `lane` and `provenance`** (compliance vs product; real vs
   synthetic), so a headline inflated by one slice is visible.

### 4.1 The schema-adapter gap (real work — do not paper over it)

**Verified mismatch.** The gold set rows carry `{quote, stem, answer, ground_truth_support}`.
But `gate_question` expects a question dict with `options` + `correct_index` and derives the
answer as `correct = (q.get("options") or [None])[q.get("correct_index", 0)]`
(`qbank_gate.py` line 99). The gold set has **no `options`/`correct_index`** — it has a flat
`answer` string. So the scorer cannot feed gold rows straight into `gate_question`.

Two clean options; pick one and document it:
- **(Recommended) Call the inner judge directly.** `llm_support_judge(quote, stem, answer)`
  takes exactly the three fields the gold set has and returns `{ok, reason}`. The scorer maps
  `ok==True → "supported"`, `ok==False → "unsupported"`, and compares to
  `ground_truth_support`. This tests the *judge* in isolation — the right unit, since lane and
  verbatim are out of scope here by construction (§1, `quote_verbatim:true`).
- **(Alternative) Adapt each gold row into a question dict** (`options=[answer]`,
  `correct_index=0`, plus a synthetic in-lane `cite_span_id`/span so lane+verbatim pass) and
  run full `gate_question`. Heavier, and it re-introduces the upstream checks the gold set
  deliberately holds constant — only do this if you specifically want the end-to-end gate path.

This adapter is **not** a throwaway: it is the contract seam between the human-labeled data and
the instrument. Getting it wrong (e.g. silently dropping the `answer` and judging the stem
alone) would make the whole agreement number meaningless. Unit-test the adapter against 2–3
hand-traced rows.

### 4.2 Trials and pass^k for the gated direction

"Because model outputs vary between runs, we run multiple trials" (Doc 2, p3, digest Theme E1);
and for a customer-facing publish-blocking signal, report **pass^k** — "the probability that all
k trials succeed ... an agent [with] a 75% per-trial success rate ... passing all three is
(0.75)³ ≈ 42%" (Doc 2, p13, digest Theme E2). Apply this to the **per-case catch** on the
dangerous direction:

- **Default `--trials 3` (k≥3).** The roadmap is explicit: "k=2 is underpowered for a publish
  gate" (`NEXT-EVALS-PLAN.md` item #6). The last measured guide run was **k=2**
  (`eval/runs/20260603T183555Z`, confirmed on disk; `STATE-OF-EVAL-2026-06-03.md` §2). Do not
  inherit k=2 here — methodology checklist **C07** names the failure: a behavior that fabricates
  a citation ~1 run in 4 "looks green at pass@1/k=2."
- **For each unsupported gold case, the judge must catch it in *all* k trials (pass^k) to count
  as caught.** A defect the judge rejects only 2 of 3 times is a defect that ships a third of the
  time — pass^k is what surfaces that; pass@k (caught *at least once*) would hide it. The headline
  **FNR is computed on the pass^k catch**, so a flaky judge cannot luck past the gate.
- Supported cases (the FPR side) may be reported at pass@k — friction tolerance is looser than the
  dangerous direction, consistent with the suite's "grounding/hallucination → pass^k;
  capability/voice → pass@k" split (`EVAL-SPEC.md` §3).

---

## 5. Where the judge sits in the gate, before and after calibration

The deterministic lane is the **publish authority**; the LLM judge is **advisory until
calibrated**, and even after, it is the *third* check, gated behind the two free deterministic
ones. This ordering is methodology checklist **C03** (grader families / lanes — deterministic
runs every commit as the authority; the LLM judge "explicitly demoted to advisory and run only
after deterministic checks pass") and is already how the gate is wired:

> "Deterministic checks run first (free); the LLM judge runs only when they pass, so cross-lane
> and fabricated-quote questions are rejected with zero model calls." — `qbank_gate.py` docstring

- **Before this calibration lands:** the judge's NO can still *route to human* (demote to
  `needs_human`), which is safe and free — but its verdict must **not** be treated as a
  trustworthy publish-block until a baseline agreement/FNR is recorded. "If agreement drops below
  threshold the judge is not trustworthy yet and its scores do not gate releases" (digest Theme
  D3, from Doc 1 p10). The deterministic checks (lane, verbatim) remain the real gate throughout;
  this matches the demonstrated posture that "the LLM grader threw both a false-pos and false-neg
  while the deterministic gate was right" (`STATE-OF-EVAL-2026-06-03.md` §4).
- **After calibration, if it clears the bar:** the judge's pass^k-aggregated verdict may gate the
  *support* dimension — but only the support dimension, behind lane+verbatim, and with FNR
  re-checked on every release (§7). It never overrides a deterministic failure, and a
  `verdict=='error'`/unparseable result is **no-signal → safe fallback (route to human)**, never
  a silent pass (`EVAL-SPEC.md` §3 "verdict=='error' is no-signal, not fail").

This keeps the slow, non-deterministic judge from becoming "the de facto gate, blocking or waving
merges on a non-deterministic signal" — methodology checklist **C03**'s danger direction.

---

## 6. The tuning loop (prompt/threshold), and holdout discipline

When the baseline FNR is above the PM/DS floor, tune — but tune against a **dev split** and prove
the gain on an **untouched holdout**, or the number is a development comparison, not a ship claim.

> "Holdout data ... is kept separate from both training and tuning and reserved for a more
> independent assessment ... once the model or approach is mostly finalized" (Doc 1, p10, digest
> Theme K1). "validation data is not the final assessment dataset, because repeated use during
> development can indirectly shape model decisions" (same).

**The loop:**

0. **Split and freeze.** DS partitions the gold set into a **dev split** (tune here) and a
   **frozen holdout** (touch only to report the ship number). Lock the split by hashing case IDs;
   the scorer refuses to run if the holdout hash changed (guards against silent leakage). With
   only 32 cases the holdout is necessarily small — so **growing the set (§8) is a prerequisite
   for a statistically honest holdout**; until then, report the holdout number *with its small-n
   caveat stated*, never as if it were tight.
1. **Measure baseline** on the dev split: overall/per-class/per-defect agreement, FNR, FPR, +
   read every miss's transcript (§2).
2. **Diagnose by defect family.** A judge leaking `inversion` needs different prompt work
   (direction-of-bound reasoning) than one leaking `wrong_answer` (responsiveness). The
   per-defect cut (§3.1) tells you which.
3. **Tune one lever at a time, on the dev split only:**
   - **Prompt.** The current judge prompt already names the trap families — *"Watch for:
     inversions (a minimum stated as a maximum or vice-versa), number/unit mismatches, and claims
     the quote does not actually make"* (`qbank_gate.py`). The highest-value **non-prompt-wording**
     change is adding an **abstain escape** (§6.1).
   - **Threshold.** Adjust the FNR gate / FPR budget against the *observed* dev distribution, with
     PM+DS sign-off — never a priori (§3.3).
4. **Re-measure on the dev split.** Iterate until the dev FNR clears the floor.
5. **Report once on the frozen holdout.** That number, at k≥3 pass^k, is the calibration result of
   record. If it diverges materially from dev, the dev gains were partly overfit — say so.
6. **Re-validate labels if the judge keeps disagreeing on the same case.** Persistent
   judge-vs-label conflict on a case two humans *also* split on is a **label** problem, not a judge
   problem — route back to DS (§2), don't tune the judge to fit a noisy label.

### 6.1 The single highest-value prompt change: an abstain escape

**Verified gap.** The judge prompt forces a binary: *"Reply with exactly YES or NO on the first
line"* and *"If the quote does not clearly and literally support the answer, say NO"*
(`qbank_gate.py` lines 60, 73 read `ok = text.upper().lstrip().startswith("Y")`). There is **no
`Unknown`/insufficient-evidence path** — exactly the gap the methodology digest flags: *"Today
`qbank_gate.llm_support_judge` is a single strict YES/NO support judge with no explicit `Unknown`
escape"* (digest Theme D4 / Theme J).

The methodology prescription is direct: *"To avoid hallucinations, give the LLM a way out, like
providing an instruction to return 'Unknown' when it doesn't have enough information ... grade each
dimension with an isolated LLM-as-judge rather than using one to grade all dimensions"* (Doc 2,
p16, digest Theme D4). This is methodology checklist **C06**. Recommended change, to be A/B'd in
the loop:

- Add a third verdict — **`UNKNOWN` / insufficient evidence** — and map it to the **safe side**:
  treat `UNKNOWN` as **not-supported for gating** (route to human), so abstention is conservative,
  matching the project's "safe default is not supported" stance. Measure whether adding the escape
  **lowers FNR** (the judge stops forcing a confident wrong YES) without ballooning FPR/friction.
  The danger direction for C06: *"Forced to choose, the judge fabricates a confident grade on
  insufficient evidence instead of abstaining."*
- **Keep it single-purpose.** This judge grades **support only**. Do not bolt voice/jargon/coverage
  onto the same rubric — "each quality dimension graded by a separate single-purpose judge rather
  than one combined rubric" (C06; digest Theme D4). The support judge stays isolated; other
  dimensions get their own judges if/when built.

> **Changing the prompt or the judge model invalidates the prior calibration.** "Report agreement
> as a maintained metric; recalibrate when the rubric or judge model changes" (digest Theme D2,
> from Doc 2 p16). Any edit to the §6.1 prompt or a bump off `claude-sonnet-4-6` (the model pinned
> in `qbank_gate.py`) requires re-running §6 end-to-end. Record the judge model + prompt hash in
> every run's output.

---

## 7. How and when to re-run — release gate via `gate_log`

This calibration is not a one-time event; it is a **canonical** check that re-runs as a release
gate, plus a recurring drift re-check. "If every model version is evaluated against the same
dataset and metric definitions, teams can make more apples-to-apples comparisons" (Doc 1, p19,
digest Theme L3).

**Re-run triggers (any one fires the calibration):**
1. **Judge prompt change** (incl. the §6.1 abstain escape) — the calibration is prompt-specific.
2. **Judge model change** — off `claude-sonnet-4-6`.
3. **Gold set change** — cases added (§8), relabeled (§2.1), or reprovenanced.
4. **Every release that lets the judge gate publish** — the FNR gate is re-confirmed on the
   holdout before the judge's verdict is trusted for that release.
5. **On each ICN pack / fixture re-import** — a *sampled support re-grade*, because the ground
   truth shifts under the judge even when the judge is unchanged (§7.1).

**`gate_log` integration (the offline-scoring backbone — to build, per `NEXT-EVALS-PLAN.md`
item #6).** Every judge verdict in production is appended to an append-only `gate_log` (the
external brief already plans "a `gate_log` capturing every gate decision for offline scoring",
`Learning-Studio-eval-context.md` §7; this mirrors the existing append-only decision logs
`logs/review-decisions.jsonl` and the curation audit log). The release gate is then:
**`python -m eval.judge_eval --live --trials 3 --fnr-gate <ratified>` exits zero**, and the
`gate_log` lets us *re-score historical decisions offline* against the current gold labels without
re-calling the model — the way `triage_eval.py` is designed to be re-pointed at mined
`logs/review-decisions.jsonl` cases. CI blocks the release on a non-zero exit, exactly as the
regression suite is "exit-code gated" (`STATE-OF-EVAL` §2) and `triage_eval`/`scope_eval` exit
non-zero past their gates.

### 7.1 Drift — the judge's ground truth moves even when the judge doesn't

A calibrated judge can silently decay because the **sources move**: "ground truth shifts as
reference content changes constantly" (Doc 2, p11, digest Theme K5) and offline expected-answers
go stale on data drift (Doc 1, p12, Theme K4). For this judge that means a `source_anchor` line/
page can shift, or a Jira AC/RN behind a `product`-lane case can be edited, so a quote the gold
set calls `supported` may no longer be verbatim-present or may now support a *different* reading.
This is `NEXT-EVALS-PLAN.md` item #5 ("% still true," end-state not bytes — "a hash can sit still
while the meaning around a quote shifts"). The recurring job: on each pack/fixture re-import,
(a) re-verify every gold `quote` is still a verbatim substring of its `source_anchor`, (b) flag
any gold case whose source changed since the label was set, (c) run a **sampled** support re-grade
and report agreement. A drop is a signal to **re-validate labels first** (Theme G2 — an
implausible reading on a stable instrument means investigate the data/grader before blaming the
model), not to silently re-tune.

---

## 8. Honest limits of this calibration

State these in the run output so a passing number is not over-read (Doc 1, p23/p26 and Doc 2,
p20, digest Theme M — offline is a filter, not a verdict on real-world impact):

1. **n = 32 today, target ≥ 50.** Below the roadmap's ~50 and Doc 2's "20–50 ... from real
   failures" floor (p14, Theme H1/H2). The unsupported classes are thin — **4** cases each for
   `inversion`/`number_swap`/`wrong_answer` — so a per-family agreement number swings ~25% on a
   single case. **Grow each unsupported family and the supported controls in matched pairs (§1.1)
   before the holdout number is treated as the ship gate**, and source new cases from **real**
   observed gate decisions in `gate_log` / `logs/review-decisions.jsonl`, not only hand-authored
   ones ("Converting user-reported failures into test cases ensures your suite reflects actual
   usage," Doc 2, p14, Theme H2).
2. **Mostly synthetic on the product lane; ICN-heavy overall.** 24 compliance / 8 product; the
   product over-claim cases are explicitly synthetic fixtures. Agreement must be reported sliced by
   provenance (§4) and not generalized past where the data supports it — no cross-feature pattern
   matching from the compliance lane onto product behavior.
3. **The judge is a method emitting a signal, never truth** (Doc 1, p14, Theme D1). A high
   agreement number means the judge tracks the human bar **on this set**; it does not prove the
   bar is right, nor that the judge generalizes to unseen defect shapes. It is a *go/iterate
   filter* behind the deterministic gate and the human approval floor — not a standalone shipping
   authority.
4. **Offline cannot tell us the downstream truth.** Whether a learner is harmed by a defect that
   slips, or helped by one that's caught, is a learner-outcome/online signal "available only once
   it's live with the real roster" (`NEXT-EVALS-PLAN.md`, "When offline won't tell us"). This
   calibration proves the judge's agreement with humans on a frozen set — pair it with the human
   approval gate and eventual learner-outcome signals before claiming the judge makes the product
   safe.

---

## 9. How this extends the external eval-expert brief

The brief (`~/Downloads/Learning-Studio-eval-context.md`) names the semantic-support judge as
**evaluation mandate #1** and poses three opening questions; this plan is the concrete answer to
the first and feeds the others.

- **Brief §7.1 / opening Q1:** *"how would you build the labeled set for the semantic-support
  judge, and what false-negative rate would you consider shippable?"* → §1 documents the set as
  built (32 cases, four defect families, two-sided, paired traps); §3.2–§3.3 make **FNR the hard
  gate** and refuse to assert a shippable rate a priori — PM+DS ratify it from the baseline, with
  the auto-mode precedent that a *named, backstopped* non-zero FNR can ship (the judge sits behind
  triage + human approval).
- **Brief opening Q2** (catch a one-sided "always-cite/always-pass" optimizer) → the offline
  oracle + two degenerate baselines (§4) operationalize this: **always-"supported"** is the
  always-pass degenerate (FNR=1.0, fails hard) and **always-"unsupported"** is the always-reject
  degenerate (FPR=1.0, fails the friction side). A judge can't game the gate by collapsing to one
  verdict.
- **Brief opening Q3** (drift/freshness sampling) → §7.1 ties the judge's recurring re-grade to the
  bank-freshness "% still true" work, with the sampling decision flagged as a PM/DS call.
- **Brief §7 "Planned eval scaffolding" (`gate_log`, pass@k vs pass^k)** → §7 wires the calibration
  into the `gate_log` release gate; §4.2 sets **k≥3 pass^k on the dangerous direction**, the bar
  the brief itself asks for ("publish-blocking checks gated on the stricter pass^k").

The brief was written for an external expert who *"do[es] not need to know our codebase"*; this
plan is the internal build doc that turns mandate #1 into a runnable, CI-gated scorer and names the
real work between here and there — **the scorer doesn't exist yet, the schema needs an adapter
(§4.1), the set is below target (§8), and the judge needs an abstain escape (§6.1).**

---

## 10. Build checklist (in order)

1. **Add `provenance` (`real`|`synthetic`) to every gold row**; resolve the `c06` boundary probe
   per §2.1 (DS decision). *(label discipline first — §1.2, §2.1)*
2. **DS noise floor:** blind human↔human re-label of all 32; quarantine cases two humans split on.
   *(§2)*
3. **Build `eval/judge_eval.py`** as a `triage_eval.py`/`scope_eval.py` twin: offline oracle + two
   degenerate baselines (asserted), `--live` with `--fnr-gate`, `--trials` k≥3 pass^k on the
   dangerous direction, lane+provenance slices, miss-ID lists. *(§4, §4.2)*
4. **Build + unit-test the schema adapter** (recommended: call `llm_support_judge` directly with
   `quote/stem/answer`). *(§4.1)*
5. **Run the offline self-test** — oracle FNR=0/FPR=0; always-"unsupported" FNR=0/FPR=1.0;
   always-"supported" FNR=1.0/FPR=0. Green = scorer trustworthy. *(§4)*
6. **Freeze dev/holdout split** (hash-locked). *(§6 step 0)*
7. **Record the live baseline** (k≥3) on dev: agreement (overall/per-class/per-defect), FNR, FPR;
   read every miss transcript. *(§3, §6)*
8. **Tune** — add the abstain escape (§6.1) and adjust thresholds on dev only; PM+DS ratify the
   shippable FNR + FPR budget. *(§3.3, §6)*
9. **Report once on the frozen holdout** at k≥3 pass^k, with the small-n caveat. That is the
   calibration of record. *(§6 step 5)*
10. **Wire the release gate** (`--live --fnr-gate <ratified>`, exit-code, into CI) and the
    `gate_log` re-score + drift re-grade jobs. *(§7)*

> Only after steps 5–9 pass may the judge's verdict gate the *support* dimension — behind
> lane+verbatim, on the pass^k catch, with FNR re-checked every release (§5, §7). Until then it
> routes to human and the deterministic checks remain the gate.
