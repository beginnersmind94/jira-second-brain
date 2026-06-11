# Eval gap audit — methodology checklist vs. the shipping suite

*Consolidated, honest audit of the Learning Studio eval suite against the merged
offline-evaluation methodology (`docs/eval-methodology-digest.md`, Doc 1 "Setting the
stage for offline evaluations" + Doc 2 "Demystifying evals for AI agents"). Same candor
as `STATE-OF-EVAL-2026-06-03.md`: this is written to find the place where a **green gate
is still wrong**, not to award points. Every status below was checked against code by
direct read, not inferred from a sibling doc.*

> **Read this first — the one-line verdict.** The deterministic spine is real and, where
> built, correct: verbatim + lane + tier are genuine by-construction invariants, and the
> three new artifacts this run produced (judge gold set, lane battery, triage additions)
> are valid data with passing offline scorers. **But the suite still certifies plumbing,
> not coverage, and two of its strongest-looking guarantees are guarantees of a *test
> fixture*, not of the *shipping path*.** The single most dangerous green light is the
> **lane-purity gate**: `check_lane` is correct and the 23 cross-lane traps all get
> refused (`leak_rate=0.000`, verified) — but the production bank-writing path never
> calls it. A cross-lane leak would show green everywhere a reviewer looks.

---

## How to read the status column

- **met** — the principle is enforced in code on the path that actually ships, and there
  is a test or a verified run behind it.
- **partial** — the mechanism exists but its authority is narrower than it looks: it
  guards a test fixture/throwaway script and not the production path, or it is built as
  *data* with no runner, or it is correct for the demo path but unmeasured on the path a
  customer hits.
- **missing** — not built, or built in a way that cannot catch the failure the principle
  names.

Statuses are reported **per area** (lane-purity, triage, judge-calibration, capability/
coverage) because the same principle has different status in different corners of the
suite. A single global "C07: missing" hides that pass^k is missing in *three* places for
*three* different reasons.

---

## Principle-by-principle, across the suite

### C01 — Grade the end-state artifact, not the tool-call trajectory
**Source:** Doc 2 p16 (digest Theme A1). **Status: met (guide suite) / partial (curation path).**

`eval/graders.py` G1–G6 read only the final artifact dict (`art["html"]`, `art["integ"]`,
`art["asm"]`, `art["sections"]`, `art["words"]`) — no grader asserts on a sequence of tool
calls. `EVAL-SPEC.md` §1 bans `enforce_citations` from the grade path (anti-circularity),
and the digest records this done right. **Met for the guide generation suite.**

The **partial** is on the curation side: the lane/verbatim/support gate is path-shaped
(`gate_question` runs the three checks *in order*), and the only callers that exercise it
end-to-end are a 5-case unit test and a self-labeled throwaway script (see C03/lane-purity
below). That is closer to a trajectory assertion than an end-state one — it grades "did
someone remember to run the gate function," not "is the banked artifact actually clean."

**Dangerous direction:** a correct ground-by-construction output that took an unanticipated
valid path is failed. **Not currently realized** — the guide graders are outcome-shaped, so
this is a clean met for the part of the suite that has a runner.

---

### C02 — The outcome is the artifact's real state, not what the transcript claims
**Source:** Doc 2 p3 (digest Theme A2). **Status: met.**

The grounding gate does not believe a citation token. `qbank_gate.check_verbatim`
(qbank_gate.py:46–48) resolves the quote to the immutable source span and confirms the
normalized quote is an actual substring of `span["text"]`. A `<!-- Source -->` token with
no backing span fails. On the cell_d guide path, `assemble._render` builds tier+span text
from the registry, never from the model, so "cited" means "resolves to a real span," not
"the model said it cited." **Met — citation theater (a token without backing text) is
caught.**

**Where a green gate is still wrong (the caveat that keeps this from being a coverage
claim):** the gate proves the quote is *verbatim and correctly-tiered*; it does **not**
prove the quote is about what the sentence claims, nor that the fixture's field→tier
mapping is correct. `STATE-OF-EVAL` §4 documents this precisely — the gate and the registry
share one ground truth (`demo._FIX`), so a fixture that wrote AC text into the desc field
would mint a confidently-wrong-but-self-consistent citation and every grader would still
pass. **C02 is met for "the text exists in the source"; it is silent on "the source is the
right source."** That silence is C09's territory.

---

### C03 — Layer graders by family; deterministic lane is the publish authority, LLM judge demoted to advisory
**Source:** Doc 2 p16 + Doc 1 p25 (digest Theme B). **Status: partial.**

The *posture* is correct and well-documented: `graders.py` is labeled "the PUBLISH
authority," the LLM support judge runs **only after** deterministic checks pass
(`gate_question` short-circuits on lane then verbatim before any model call, qbank_gate.py:
88–97), and `EVAL-SPEC.md` §3 marks G7/G8 advisory-only. The new `judge_eval.py` keeps the
judge honest with an offline stdlib-only path (no SDK) so the deterministic self-checks run
on every commit without auth. **This is the right architecture.**

**Why partial, not met — the deterministic lane is not wired into CI as a per-commit gate
for the curation suite.** The guide regression suite (`eval/regression.py`, 15/15) runs
deterministically with an exit code. But the **lane** check — the deterministic backstop
for purity — has **no runner at all** (`eval/lane_purity_eval.py` does not exist; the data
file does). The canonical guide grader set `graders.py` G1–G6 has **no lane grader**. So
the deterministic family's authority over lane purity is asserted in prose and proven on
one unit-test fixture, not run as a commit gate. A family that does not run on every commit
is not yet the publish authority for the dimension it owns.

**Dangerous direction:** a slow/unreliable LLM judge becomes the de-facto gate. **Not
realized** (the judge is correctly gated behind the deterministic checks). The realized
risk is the inverse: a deterministic check (lane) that *exists* but *does not run* on the
shipping path, so nothing gates the dimension at all.

---

### C04 — Metric follows the component; no one global score
**Source:** Doc 1 p16 (digest Theme C1). **Status: partial.**

`NEXT-EVALS-PLAN.md`'s Component→metric table assigns a distinct, job-appropriate metric to
each component (gate→invariants; support-judge→judge↔human agreement; lane→leak rate;
triage→recall on `needs_human`/FNR; generation→coverage; drift→% still true). The metrics
*as designed* are correct and not reused across components. **Met at the design level.**

**Why partial — three of the six rows have no built scorer that computes the named metric
on the shipping path:**
- **lane → leak rate:** the metric is computed in an ad-hoc validation script (verified
  `leak_rate=0.000` on the 23 cross-lane cases) but there is no committed `lane_purity_eval.py`.
- **generation → coverage:** **unbuilt** (see C09). The only generation metric that runs is
  G4 *density* of emitted citations — which is a different metric measuring a different thing.
- **drift → % still true:** design-only (`docs/EVAL-DRIFT-METHOD.md`); no runner.

So the table is a correct map of metrics that, for half the components, do not yet exist as
code. A map is not a measurement.

**Dangerous direction:** a sibling's metric is reused where it doesn't fit, so the real
failure is never measured. **Partially realized for generation:** G4 density is, in effect,
standing in for coverage in the only place generation is graded today — and density cannot
see omission (C09). An engine that omits a must-cover fact scores a perfect G4.

---

### C05 — LLM-as-judge is a calibrated method; it must show measured judge↔human agreement before it gates
**Source:** Doc 1 p14 + Doc 2 p16 (digest Theme D). **Status: judge-calibration: met (gold set + scorer built, calibration not yet run) · triage: missing.**

**This is the headline build of the run, and it genuinely closes the largest single gap in
the methodology digest** (digest lines 520–521 flagged "no calibration set and no measured
judge↔human agreement"). `eval/judge_gold_set.jsonl` is a **32-case human-authored gold set**
(15 supported / 17 unsupported; defects: inversion 4, number_swap 4, over_claim 5,
wrong_answer 4 — distribution verified) and `eval/judge_eval.py` is a deterministic
FNR-gated scorer that runs offline (oracle FNR/FPR=0; degenerate baselines assert correctly
— **verified by running `python -m eval.judge_eval`**). Roadmap item #1 is therefore **built,
not just planned** — the data and the harness exist and the offline self-check passes.

**Why this is "met (built)" and NOT "calibrated":** the gated number — the **live judge↔human
agreement / FNR of `qbank_gate.llm_support_judge`** — **has not been measured.** `--live`
requires SDK auth and was (correctly, per this run's constraints) not executed. So the
support judge **is not yet cleared to gate publish**: the threshold exists (`--fnr-gate 0.0`)
but the judge's actual FNR against the gold set is unknown. **A reviewer must not read
"gold set built" as "judge calibrated."** Until a `--live` run records the FNR, the support
check is an *uncalibrated* method — exactly the state Doc 1 p14 warns against trusting.

For **triage**, C05 is **missing**: `revise.build_triage_options` (revise.py:176–183) sets
no `effort`, no temperature, no seed (unlike the edit agent's `effort="medium"` at line 118),
and `triage_eval.predict_live` runs each case exactly **once** (triage_eval.py:134–144, no
trial loop). The triage classifier has never had a recorded live FNR either, and when it is
measured it will be a single non-deterministic Bernoulli draw per case (see C07).

**Dangerous direction:** false negatives — a verbatim-but-misleading item (a minimum stated
as a maximum) judged "supported" and shipped. **The gold set is built precisely to measure
this; the measurement has not happened.** That is the gap between "we built the ruler" and
"we measured the thing."

---

### C06 — Each judge gets an explicit "Unknown"/abstain escape; one isolated judge per dimension
**Source:** Doc 2 p16 (digest Theme D4). **Status: partial — isolation met, abstain missing.**

**Isolation: met.** The judges are single-purpose and separated — `llm_support_judge`
(semantic support), the triage classifier (stylistic vs substantive), and the scope
resolver are three distinct judges, not one mega-rubric. This matches D4's "isolated
LLM-as-judge per dimension."

**Abstain: missing, and this is a real defect, not a nitpick.** `qbank_gate.llm_support_judge`
forces a strict binary: *"Reply with exactly YES or NO on the first line"* (qbank_gate.py:60),
and the parser treats anything not starting with Y as NO (`ok = text.upper().lstrip()
.startswith("Y")`, line 73). There is **no `Unknown`/insufficient-evidence verdict.** The
digest (Theme D4, lines 191–192) already flagged this. The triage prompt has the same shape
(forced `stylistic`|`substantive`, revise.py:199). Doc 2's guidance is explicit: forcing a
choice on insufficient evidence invites a fabricated confident grade instead of abstention.

**Mitigating nuance (stated honestly):** the binary collapses *toward the safe side by
construction* — an unparseable/errored judge result maps to `unsupported` in `judge_eval`
(SAFE_DEFAULT, judge_eval.py:58) and to `substantive` in triage. So a missing abstain cannot
*directly* wave a bad item in via the error path. But that is the harness being defensive
about judge *failure*, not the judge being allowed to *abstain on a genuinely ambiguous
case*. A borderline-but-not-erroring case is still forced to a confident YES/NO. **Partial.**

**Dangerous direction:** forced to choose, the judge fabricates a confident grade on
insufficient evidence instead of abstaining. **Live, unmeasured** — and it interacts with
C05: the gold set's deliberately-tricky boundary cases (the author flagged `wrong_answer-c06`
/ `c06b` as quote/answer-mismatch probes) are exactly where a forced binary is most likely
to err, and exactly where an abstain option would help most.

---

### C07 — Run multiple trials; report pass^k (k≥3) for publish-blocking graders
**Source:** Doc 2 p13 (digest Theme E). **Status: missing across the run's three areas — for three distinct reasons.**

This is the most pervasive gap and the run did **not** close it anywhere:

- **Guide suite:** the only measured run (`eval/runs/20260603T183555Z`) is **k=2**.
  `STATE-OF-EVAL` and the digest (Theme E2) both call k=2 underpowered; `NEXT-EVALS-PLAN.md`
  item #6 raises it to ≥3. **Still k=2 — not raised this run.**
- **Triage:** **k=1** and against a non-deterministic classifier (no effort/temp/seed). A
  classifier that mislabels a given substantive edit ~1-in-3 runs can show FNR=0 on a single
  sweep and pass `--fnr-gate 0.0` by luck. The eval reports FNR to two decimals as if it were
  a point estimate of a deterministic system; it is one Bernoulli draw per case.
- **Lane-purity & judge gold set:** the deterministic checks (`check_lane`, `check_verbatim`)
  *are* deterministic, so pass^k on them is trivially 1 and k is moot there. **But the
  support half** — the 7 judge-dependent lane cases (`same_lane_positive` + `SL-CTL-02`) and
  the entire judge gold set's `--live` path — runs the non-deterministic LLM judge and has
  **no trial loop and no pass^k aggregation.** When those `--live` numbers are eventually
  recorded, a single-trial FNR is exactly the underpowered estimate Doc 2 p13 warns about.

**Dangerous direction:** an engine/judge/classifier that fabricates or misclassifies ~1 run
in 4 looks green at pass@1/k=2 and ships an unreliable guarantee. **Realized in the triage
harness today** (k=1 on a non-deterministic classifier is the costliest version of this —
it is the exact number a reviewer would trust to keep the router advisory-safe, and the one
number the harness cannot defend). **A green FNR=0 from a k=1 triage run would be wrong.**

---

### C08 — Test both where a behavior should occur AND where it must not (balanced / should-not tasks)
**Source:** Doc 2 p15 (digest Theme F1). **Status: partial — newly balanced for triage/lane/judge; still missing for generation.**

**Improved this run for three components:**
- **Judge gold set:** balanced 15 supported / 17 unsupported, with each unsupported trap
  paired against a genuine supported control (e.g. the `number_swap-003` trap kept with its
  genuine pair `-008`; `supported-prod-cndb-overclaim` kept with its control
  `supported-prod-cndb-cadence`). An always-"supported" rubber-stamp scores FNR=100% and is
  exposed (verified). **Both-sided.**
- **Lane battery:** 23 cross-lane traps + 6 same-lane positives + 2 same-lane controls, so an
  always-refuse grader scores 0 on the positives and is caught. Cross-lane direction is
  balanced (product-stem-citing-compliance *and* compliance-stem-citing-product for each
  shared word). **Both-sided.**
- **Triage additions:** 3 stylistic + 3 substantive across new boundary axes
  (conditional→absolute, new-unsourced-claim, statistical-outlier, low-confidence over-trigger,
  sensitive-topic, non-sequential reorder), merging to a balanced 15/15 set (verified).
  **Both-sided.**

**Still missing — the generation capability suite (`eval/capability.py`):** it runs **no
should-NOT task.** The balanced pairs specced in `EVAL-SPEC.md` §2 — **CAP-09** (flag a
planted transcript-vs-Jira conflict), **CAP-10** (hedge a Description-only claim as
`[TO VERIFY]`), **CAP-14** (drop un-citable specifics) — are **TODO** (confirmed in the
digest's direct read: no `CAP-09`/`should-not` symbols in `capability.py`). The capability
suite re-runs the three production formats and grades happy-path quality — a saturated
regression check, not a low-pass-rate "can it ever withhold" bank.

**Dangerous direction:** the engine optimizes toward over-citing / "helpful yes," and a
grader that passes by *always emitting a citation* is never caught. **Realized for the
generation engine** — there is still no task where the correct answer is *withhold and raise
an Open question*, which is precisely the behavior the project's anti-hallucination rules
demand and the one G4 density actively rewards against.

---

### C09 — Pair the headline metric with a guardrail covering its blind spot (omission/coverage)
**Source:** Doc 1 p15 (digest Theme F2). **Status: missing.**

There is **no coverage/omission metric anywhere in the suite.** Every grounding grader scores
**emitted** output: G4 measures citation *density* (`tokened >= ceil(words/250)`, graders.py:
57–79) — it can only ask "are the things you said cited," never "did you say the things you
must." `NEXT-EVALS-PLAN.md` item #4 names this as "the currently-unmeasured gap" and it
remains unbuilt after this run. No per-topic must-cover keypoint list, no scoring of a
generated quiz/guide against required keypoints, exists.

**This is the blind spot that makes a green dashboard most misleading**, because it compounds
with C08: the suite rewards citing (G4) and never penalizes omitting (no coverage), so the
optimization gradient points straight at "cite a few safe things well and stay silent on the
hard, must-cover material." A guide that omits a critical workflow, or a quiz that never tests
the one allergen rule that matters, passes every grader the suite runs today.

**Dangerous direction:** confident omission of must-cover material. **Fully unmeasured —
realized by absence.** A green suite says nothing about what the output left out.

---

## The places a green gate is still wrong (consolidated)

These are the specific configurations where every check a reviewer runs is green and the
output is nonetheless unsafe. Ranked by how silent the failure is.

1. **Cross-lane leak through the production curation path (most dangerous).** `check_lane` is
   correct and the battery proves it refuses 23/23 cross-lane traps — **but
   `qbank_curation.score_candidate`/`triage`/`commit_to_bank` (qbank_curation.py:108–199) and
   `commit_gate_hook` (qbank_gate_hooks.py:49–65) gate on `confidence`/`support_ok`/`topic`/
   `status` and NEVER call `check_lane` or `lane_of_span_id`.** `support_ok` is a precomputed
   boolean handed to `score_candidate`; nothing in the committable path re-derives lane. The
   only end-to-end callers of `gate_question` are `test_qbank_gate.py` (5 cases) and
   `curator_walkthrough.py` (self-labeled "throwaway… disposable. Not production code"). So
   the "leak rate → 0" guarantee is a property of one test fixture and a throwaway script, not
   of the bank-writing pipeline — and `graders.py` G1–G6 has no lane grader, so a leak shows
   green everywhere. **A green check certifies the comparison works on one example, not that
   lanes cannot cross in the shipping path.**

2. **Wrong-source-but-verbatim citation (C02 caveat).** The gate proves the quote is verbatim
   and correctly-tiered against `demo._FIX`; it cannot prove the source is the *right* source
   for the sentence, nor that the fixture's field→tier mapping is correct. A fixture with AC
   text in the desc field grounds a confidently-wrong citation that passes every grader
   (`STATE-OF-EVAL` §4, open-q #2).
   - *Doc-drift correction (verified this run):* `STATE-OF-EVAL` §5's "wrong-MODULE lexical
     leak inside a loaded fixture" is now **mitigated in code** — `demo.match_tickets` filters
     by module (demo.py:206–208, `if module and (rec.get("module") or "") != module:
     continue`). The wrong-module *silent* failure now requires the older preconditions
     (no fixture for the module → loud `SystemExit`, the safe failure; or a genuinely
     mis-captured/merged fixture). Cite the **code**, not the older report, on this point.

3. **k=1 triage FNR (C07).** A green `FNR=0` from the triage harness is one Bernoulli draw per
   case against a temperature-unset classifier. It is the number a reviewer would trust to
   keep the router advisory-safe, and it is statistically indefensible at k=1.

4. **Coverage (C09) and the unbuilt should-not generation tasks (C08).** A guide/quiz that
   omits must-cover material, or an engine that emits a plausible citation where it should have
   withheld, passes a fully green suite — because neither omission nor "should-not" is tested
   for the generation component.

---

## Status matrix (per principle × area)

`met` = enforced on the shipping path with a test/verified run · `partial` = mechanism exists
but authority is narrower than it looks (fixture-only, data-without-runner, or demo-path-only)
· `missing` = not built or cannot catch the named failure · `n/a` = principle does not bind
this area.

| Principle | Guide suite | Lane-purity | Triage | Judge-calibration | Coverage/gen |
|---|---|---|---|---|---|
| C01 outcome-not-path | met | partial | met | met | n/a |
| C02 outcome-is-env-state | met | met | met | met | partial |
| C03 grader-families/lanes | met (regression) | partial | partial | met | missing |
| C04 metric-per-component | met | partial | met | met | partial |
| C05 judge-calibrated-method | n/a | met | **missing** | **met (built, not yet calibrated)** | n/a |
| C06 judge-abstain/isolated | n/a | met | partial | partial (no abstain) | n/a |
| C07 pass^k (k≥3) | **missing (k=2)** | met (det) / missing (support) | **missing (k=1)** | met (det) / missing (live) | missing |
| C08 balanced should-not | partial | met | met | met | **missing** |
| C09 guardrail/coverage | missing | n/a | n/a | n/a | **missing** |

*Reading the matrix:* the deterministic columns (C01, C02) are solid. The judge-method
columns (C03/C05/C06) are strong on architecture and newly strong on the **support-judge gold
set**, but uncalibrated live and missing the abstain escape. **C07 is red across the board**
and **C09 is red by absence** — those two, plus the lane-wiring gap behind C03, are where a
green dashboard is most likely to be lying.

---

## What this audit does NOT claim (honesty boundary)

- It does **not** claim any LLM judge's live agreement number, because none was measured this
  run (`--live` requires SDK auth, intentionally not exercised). The judge-calibration status
  is "ruler built, thing not yet measured."
- It does **not** re-assert `STATE-OF-EVAL`'s in-fixture wrong-module lexical-leak claim;
  direct read of `demo.match_tickets` shows that path is now module-filtered. Treat the older
  report as superseded on that single point.
- The lane `leak_rate=0.000`, the judge offline self-check, and the triage/judge balance were
  **verified by running the deterministic, SDK-free paths** — not by trusting the produced
  notes. The production-path lane gap (#1 above) was verified by reading
  `qbank_curation.py`/`qbank_gate_hooks.py` and confirming neither calls `check_lane`.
