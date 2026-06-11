# Eval methodology digest — merged reference

*Two source documents, merged and deduped into one offline-evaluation methodology for
Learning Studio. Each principle carries a **verbatim quote** (reproduced exactly from the
page cited, including the source's own typos/odd punctuation) and a concrete suite
implication. Where the two docs overlap, the entry notes both; where only one supports a
claim, only that one is cited. Where a concept commonly attributed to "eval best practice"
is **absent** from both docs, it is flagged as absent rather than invented.*

## Source documents
- **Doc 1** — *"Setting the stage for offline evaluations"* (MEAP v4, chapter one), 28 pages.
  File: `C:/Users/rahul.mehta/Downloads/eval-doc1-setting-the-stage-offline-evals.txt`.
  An introductory/framing chapter on the **offline-eval method for AI products in general**
  (recommenders, classifiers, RAG, agents).
- **Doc 2** — *"Demystifying evals for AI agents"* (Anthropic, *Engineering at Anthropic*,
  published Jan 09, 2026; authors Mikaela Grace, Jeremy Hadfield, Rodrigo Olivares, Jiri De
  Jonghe), 28 pages.
  File: `C:/Users/rahul.mehta/Downloads/eval-doc2-demystifying-evals-agents.txt`.
  Agent-specific eval guidance (graders, trials, task banks, saturation, isolation).

> Quotes below are reproduced **verbatim** from the named reference at the page indicated.
> Minor source artifacts (PDF-extraction garbling, curly quotes, em dashes) are preserved
> as-is where quoted. Anything labeled *Interpretation* or *Suite implication* is this
> digest's bridging, **not** a source claim.

### Honesty flags carried from the source read (do not silently "fix" these)
Doc 1 is a framing chapter, not an agent-eval cookbook. Several terms in common circulation
were searched for and are **genuinely absent** from Doc 1 — they are supplied **only by Doc
2**, and the merge does not back-fill Doc 1 quotes to cover them:
- **`pass@k` / `pass^k` / running multiple trials** — absent from Doc 1 (0 matches); Doc 2
  only (Theme E).
- **"grade the outcome, not the path"** — absent as a stated principle in Doc 1; Doc 2 only
  (Theme A). Doc 1's nearest adjacent idea is outcome-flavored ("Did the agent actually help
  the user find a movie…", p16) but never contrasts outcome vs path.
- **One-sided evals / should-not tasks / balanced tasks** — explicit framing absent from Doc
  1; Doc 2 only (Theme F). Doc 1's grounded adjacent is single-metric *gaming* (P-Guardrail).
- **Saturation (0%/100% "look closer")** — absent from Doc 1 (0 matches); Doc 2 only (Theme
  G). Doc 1 has a narrower component-specific "low recall ⇒ bug" diagnostic (P-BugSignal).
- **Three named grader families (code/model/human)** — the explicit taxonomy is Doc 2's;
  Doc 1 distinguishes engineering-computable metrics vs human/LLM-judge scoring without
  naming a three-family taxonomy. Merged in Theme B, attributed correctly.
- **Task-bank size (20–50)** — absent from Doc 1 (0 matches); Doc 2 only (Theme H).

---

## Theme A — Grade the outcome (end state), not the path

### A1. Grade what the agent produced, not the trajectory it took
> "There is a common instinct to check that agents followed very specific steps like a sequence of tool calls in the right order. We've found this approach too rigid and results in overly brittle tests, as agents regularly find valid approaches that eval designers didn't anticipate. So as not to unnecessarily punish creativity, it's often better to grade what the agent produced, not the path it took."
> — **Doc 2, p16**

**Suite implication.** The canonical pass/fail grader for each task asserts on the **end-state
artifact** (the curated `.md` / citation packet actually contains the grounded claim; the
question-bank gate actually rejected an ungrounded item), never on a fixed sequence of
intermediate tool calls. Transcript / tool-call checks are **diagnostic overlays** that
explain a failure — never the sole gate — otherwise a correct ground-by-construction output
that took a different path is wrongly failed.

> **Caveat (from Doc 1's honesty read).** Doc 1 does **not** state a general "grade outcome
> not path" rule. It supports *outcome + constraint* scoring for agents (see P-Constraints in
> Theme C) but never contrasts outcome vs path. Attribute A1 to Doc 2 only.

### A2. The outcome is the final environment state, not what the transcript claims
> "The outcome is the final state in the environment at the end of the trial. A flight-booking agent might say "Your flight has been booked" at the end of the transcript, but the outcome is whether a reservation exists in the environment's SQL database."
> — **Doc 2, p3**

**Suite implication.** Do not let the suite pass a task because the agent *said* it cited a
ticket or grounded a claim. The canonical grader inspects the **produced artifact's actual
state** — parse the resource/packet and confirm each non-obvious claim carries a real
citation that resolves to a directly-read ticket/wiki source. This mirrors the project's
*cite-or-cut* and *verify-before-ready* rules at the grader level.

---

## Theme B — Grader families and who/what can grade (cost & latency lanes)

### B1. Three grader families; prefer deterministic, use LLM where needed, human judiciously
> "We recommend choosing deterministic graders where possible, LLM graders where necessary or for additional flexibility, and using human graders judiciously for additional validation."
> — **Doc 2, p16**

### B2. (Doc 1's grounded version) Not every metric can be computed instantly or automatically
> "The important caveat is that not every offline metric can be computed immediately or automatically. Some require delayed labels, human review, or LLM-as-a-judge scoring."
> — **Doc 1, p25**

*Interpretation (merge).* Doc 1 distinguishes (a) simpler metrics "implemented and maintained
primarily by engineering" (recall/precision) from (b) human review and (c) LLM-as-a-judge as
costlier mechanisms requiring delayed labels (Doc 1, pp25–26). Doc 2 names the same split as
the three grader **families**. Same idea, two vocabularies.

**Suite implication.** Layer the suite by grader family and **tag each grader with its
mechanism + latency** so CI knows what blocks a merge vs what is reviewed asynchronously.
- **Deterministic lane (every commit):** mechanically checkable in a ground-by-construction
  engine — does every claim carry a citation token? does each citation resolve to an existing
  ticket file? did the question-bank gate block the unsupported item? is synthetic data
  labeled synthetic? (`learning-agent/eval/graders.py` G1–G6 + `qbank_gate.py` checks 1–2.)
- **Model lane (cadence / sampled):** LLM-rubric scoring of subjective dimensions (is the
  claim *faithfully* grounded; is jargon translated not quoted; is the customer-facing voice
  right). Advisory; never the publish authority.
- **Human lane (judicious):** SME calibration + ambiguous cases (the existing approval gate
  and `mark_guide_reviewed` loop).

### B3. Code-based graders: fast/cheap/objective but brittle to valid variation
> "• Brittle to valid variations that don't match expected patterns exactly
> • Lacking in nuance
> • Limited for evaluating some more subjective tasks"
> — **Doc 2, p7**

**Suite implication.** When writing deterministic citation/grounding graders, anticipate
*valid* variation: a claim can be grounded by Acceptance Criteria **or** Release Notes (per
the project field-priority rule); citations may be inline `<!-- Source: -->` comments **or**
changelog blockquotes; in Learning Studio a span carries a lane prefix (`product:` /
`compliance:`) that the grader reads rather than infers (`qbank_gate.lane_of_span_id`). A
regex that matches only one citation shape will brittle-fail correct outputs — pair brittle
string checks with a model-based check for the nuance they miss.

---

## Theme C — Metric follows the component; score accomplishment + constraints

### C1. Metric selection is a product decision; the metric must match the component's job
> "This is why metric selection is not just a technical detail. It is a product decision. The best offline metrics are the ones that reflect what the system is supposed to accomplish in the user experience. For a recommender, that might mean surfacing relevant titles. For an LLM-generated explanation, that might mean producing a grounded and useful reason. For an agentic recommender, that might mean completing a multi-step user request successfully."
> — **Doc 1, p16**

**Suite implication.** Do not apply one global score across heterogeneous components. Map
each component to a metric tied to its job and justify it in the suite config:
retrieval/ranking → Precision@K / Recall@K / NDCG@K; generated explanation →
groundedness/relevance/factuality; agent → task-completion / constraint-adherence / tool-call
accuracy. Re-confirm the mapping rather than reusing a sibling component's metric. (Learning
Studio's `NEXT-EVALS-PLAN.md` already does this in its Component→metric table — Theme J maps
the correspondence.)

### C2. (Doc 2's equivalent) Choose the right graders for the job; decompose multidimensional success
*Interpretation (merge).* Doc 2 has no verbatim "metric follows the component" line. Its
grounded equivalents are "choose deterministic where possible, LLM where necessary" (B1) and
**partial-credit decomposition** of a task into per-component sub-checks (state check +
transcript constraint + LLM rubric, Doc 2 p10; see Theme I). Treat C1 as Doc 1's; do not
attribute the phrase to Doc 2.

### C3. For agents/LLM features, score task accomplishment AND stated constraints — not surface plausibility
> "If an agent is helping users find something to watch through a conversational interface, you may need metrics like task completion rate, constraint adherence, or tool-call accuracy. Did the agent actually help the user find a movie that matched their request? Did it respect constraints like "nothing scary" or "under 90 minutes"? Did it call the right retrieval or ranking tool?"
> — **Doc 1, p16**

**Suite implication.** For agentic test cases assert on accomplishment + per-constraint
satisfaction, not just well-formed text: (a) task-completion check, (b) explicit per-constraint
pass/fail predicates (encode each named constraint as its own predicate), (c) tool-call
correctness. **Do not over-generalize:** Doc 1 supports outcome+constraint scoring; it does
not state a general "grade outcome not path" rule (that is A1, Doc 2).

---

## Theme D — LLM-as-judge is a calibrated METHOD, not a metric

### D1. (Doc 1) The judge is a scoring mechanism producing a signal — validate, calibrate, interpret
> "One important nuance: LLM-as-a-judge is not really a metric category on its own. It is better understood as an evaluation method or scoring mechanism. For example, the metric might be groundedness, relevance, factual consistency, instruction following, or task success. An LLM judge can be used to score those dimensions, often with a rubric or grading prompt. This distinction matters because the judge is producing an evaluation signal, not absolute truth. Like any evaluation method, LLM-as-a-judge outputs should be validated, calibrated, and interpreted carefully."
> — **Doc 1, p14**

### D2. (Doc 2) Model grading takes careful iteration; calibrate closely against human experts
> "Model grading often takes careful iteration to validate accuracy. LLM-as-judge graders should be closely calibrated with human experts to gain confidence that there is little divergence between the human grading and model grading."
> — **Doc 2, p16**

*Merge.* Both docs say the same thing from two angles: name the **metric** (groundedness /
relevance / instruction-following / task-success) separately from the **judge** that scores
it, and treat the judge as an instrument with known error that must be shown accurate before
its scores are trusted.

**Suite implication.** Any LLM-judge in the suite — including Learning Studio's one real
judge, `qbank_gate.llm_support_judge` (the semantic-support check that decides whether a
verbatim-but-misleading item ships) — ships with a **calibration set**: human/SME-labeled
examples and a measured **judge↔human agreement** number before the judge's scores gate
anything. Report agreement as a maintained metric; recalibrate when the rubric or judge model
changes. The judge's own pass-rate is **not** the headline metric.

### D3. (Doc 1) The calibration anchor is human-labeled outcomes; replay against known resolutions
> "The system can be evaluated offline by replaying historical tickets and assessing the agent's outputs against known resolutions or human-written responses. Metrics in this setting might include relevance, factual consistency, adherence to company guidelines, or agreement with human reviewers."
> — **Doc 1, p10**

**Suite implication.** Maintain a human-labeled gold set; compute "agreement with human
reviewers" as the calibration metric for any LLM-judge or automated scorer. If agreement
drops below threshold the judge is not trustworthy yet and its scores do not gate releases.
For Learning Studio this is `NEXT-EVALS-PLAN.md` item #1 — the ~50-triple `(quote, stem,
answer)` gold set with **false-negative rate** as the dangerous direction.

### D4. (Doc 2) Reduce judge hallucination: give it a way out, isolate one judge per dimension
> "To avoid hallucinations, give the LLM a way out, like providing an instruction to return "Unknown" when it doesn't have enough information. It can also help to create clear, structured rubrics to grade each dimension of a task, and then grade each dimension with an isolated LLM-as-judge rather than using one to grade all dimensions."
> — **Doc 2, p16**

**Suite implication.** Build separate single-purpose judges per dimension (one for
groundedness/support, one for persona/agency correctness, one for jargon-translation, one for
voice) rather than one mega-rubric. Each judge prompt must permit an `Unknown` / `insufficient
evidence` verdict so it abstains rather than fabricating a grade — directly aligned with the
project's "safe default is not-supported" stance. (Today `qbank_gate.llm_support_judge` is a
single strict YES/NO support judge with no explicit `Unknown` escape — see Theme J / gap.)

---

## Theme E — Run multiple trials; report pass@k and pass^k

### E1. Each attempt is a trial; outputs vary, so multiple trials are required
> "Each attempt at a task is a trial. Because model outputs vary between runs, we run multiple trials to produce more consistent results."
> — **Doc 2, p3**

### E2. pass@k vs pass^k — and why consistency-critical agents need pass^k
> "pass^k measures the probability that all k trials succeed. As k increases, pass^k falls since demanding consistency across more trials is a harder bar to clear. If your agent has a 75% per-trial success rate and you run 3 trials, the probability of passing all three is (0.75)³ ≈ 42%. This metric especially matters for customer-facing agents where users expect reliable behavior every time."
> — **Doc 2, p13**

**Suite implication.** The harness supports N-trials-per-task as a first-class feature and
aggregates per-task success rate + variance — one green run is not "passes". Because the
deliverable is **customer-facing** (`resources/`, `onboarding/`, published guides), report
**pass^k** for any publish-blocking grounding grader, not just pass@1: an engine that
fabricates a citation 1 run in 4 looks fine at pass@1 but its pass^3 ≈ 42% exposes the real
risk. Learning Studio's measured run was **k=2** (`STATE-OF-EVAL-2026-06-03.md`) and
`NEXT-EVALS-PLAN.md` item #6 explicitly raises k to **≥3** ("k=2 is underpowered for a publish
gate"). Capability/coverage graders may stay pass@k.

> **Doc 1 cross-check (honesty).** Doc 1 never discusses repeated sampling, k trials, or
> pass-rate-over-trials — Theme E is Doc 2 only. Doc 1 *separately* warns that small offline
> deltas may not be statistically significant (Theme K / P-Filter), which motivates a
> **minimum meaningful delta**, a different concern from trial count.

---

## Theme F — Test both sides; one-sided evals cause one-sided optimization

### F1. Test where the behavior should occur AND where it should not
> "Test both the cases where a behavior should occur and where it shouldn't. One-sided evals create one-sided optimization. For instance, if you only test whether the agent searches when it should, you might end up with an agent that searches for almost everything."
> — **Doc 2, p15**

**Suite implication.** For every "the engine SHOULD emit a grounded claim" task, add a paired
"should-NOT" task: Acceptance Criteria and Release Notes both empty → the engine must
**withhold** the claim and raise an Open question (per the project rules), not manufacture a
plausible bridge. Without negative tasks the engine optimizes toward over-citing / "helpful
yes" hallucinations. Track over-trigger vs under-trigger balance explicitly. **Learning
Studio status (direct read):** `eval/capability.py` re-runs the three production formats and
grades happy-path quality; it runs **no should-not task** — the balanced pairs (CAP-09 flag
planted conflict, CAP-10 hedge a Description-only claim, CAP-14 drop un-citable specifics) are
specced in `eval/EVAL-SPEC.md` §2 but are **TODO** (confirmed: no `CAP-09`/`should-not` symbols
in `capability.py`). This is `NEXT-EVALS-PLAN.md` item #3 (triage balanced set) and the
should-not capability tasks.

### F2. (Doc 1's grounded adjacent) A single metric can be gamed — add guardrail metrics
> "A model could have strong Precision@K while still recommending the same narrow set of titles over and over again. That might look good in one offline metric while still creating a stale user experience."
> — **Doc 1, p15**

**Suite implication.** Never optimize/report a lone headline metric. Pair the primary quality
metric with guardrail metrics that catch its blind spot (Doc 1's example: Coverage + Diversity
alongside Precision@K). In CI, a primary-metric gain that comes with a coverage/diversity
regression should flag, not auto-pass. For Learning Studio the unmeasured blind spot is
**omission/coverage** — the gate checks *emitted* citations, never what a quiz/guide *omits*
(`NEXT-EVALS-PLAN.md` item #4). *This is Doc 1's grounded version of the one-sided concern;
the explicit "should-not task" construct is Doc 2's (F1), not Doc 1's.*

---

## Theme G — Saturation: 0% and 100% both mean "look closer"

### G1. (Doc 2) 0% pass@100 usually means a broken task/grader, not an incapable agent
> "With frontier models, a 0% pass rate across many trials (i.e. 0% pass@100) is most often a signal of a broken task, not an incapable agent, and a sign to double-check your task specification and graders."
> — **Doc 2, p15**

### G2. (Doc 1's narrower analog) An implausible metric reading on a deterministic component signals a BUG
> "A high recall is ideal because the goal is to display all relevant prior orders without omissions. If there is a low recall, the algorithm that computes Your Recent Shows should be looked into for bugs."
> — **Doc 1, p8**

*Merge / scope.* Doc 2 states the **generic** saturation rule for both ends (0% ⇒ suspect the
task/grader; 100% ⇒ no improvement signal). Doc 1 has only a **component-specific** "low
recall ⇒ go find the bug" diagnostic — not a generic 0%/100% rule. Use Doc 2 as the rule, Doc
1 as a concrete instance.

**Suite implication.** Wire two saturation alarms.
- **0% across many trials** → suspect the grader/regex or the task spec **first** (e.g. the
  citation-shape matcher is wrong) before concluding the engine can't ground.
  `STATE-OF-EVAL-2026-06-03.md` records this done right: tldr's 0% was correctly diagnosed as a
  real **length** regression with grounding intact, not a grounding failure.
- **100%** (Learning Studio's two formats at 100% + 15/15 regressions) tracks regressions but
  yields no hill to climb — **add harder grounding tasks** (the capability tier, Theme L).

### G3. (Doc 2) Do not take eval scores at face value until someone reads transcripts
> "You won't know if your graders are working well unless you read the transcripts and grades from many trials. At Anthropic, we invested in tooling for viewing eval transcripts and we regularly take the time to read them. When a task fails, the transcript tells you whether the agent made a genuine mistake or whether your graders rejected a valid solution."
> — **Doc 2, p17**

**Suite implication.** Store the full record per trial (outputs, which ticket fields were read,
which citations emitted) and make reading failures routine. For a grounding engine this is how
you catch the **inverse** failure: a *correct withhold* (AC empty → claim cut) marked FAIL by
an over-eager "must produce a claim" grader. Without transcript review the suite silently
penalizes exactly the cautious behavior the project wants.

---

## Theme H — Task-bank construction: size, sourcing, solvability

### H1. Don't wait for hundreds of tasks; 20–50 from real failures is a strong start
> "We see teams delay building evals because they think they need hundreds of tasks. In reality, 20-50 simple tasks drawn from real failures is a great start. After all, in early agent development, each change to the system often has a clear, noticeable impact, and this large effect size means small sample sizes suffice. More mature agents may need larger, more difficult evals to detect smaller effects, but it's best to take the 80/20 approach in the beginning."
> — **Doc 2, p14**

**Suite implication.** Seed with 20–50 tasks from **real, observed** grounding failures. The
project already has a documented corpus: the 2026-05-18 Accountability re-pass where 6/12 edits
had material gaps from Description-only reading (`jira-brain/raw/guides/ticket-updates/
2026-05-18.md`) and the rejected-tickets FAQ corpus. Don't block on volume. As pass rates
climb, expand toward harder, smaller-effect-size cases (subtle citation theater, jargon
leakage). **Learning Studio status:** the measured run is ~3 formats × 1 transcript × 1 module
(`STATE-OF-EVAL` §3) — below the 20–50 floor.

### H2. Source realistic tasks from real failures (bug tracker, support queue, pre-release checks)
> "Begin with the manual checks you run during development—the behaviors you verify before each release and common tasks end users try. If you're already in production, look at your bug tracker and support queue. Converting user-reported failures into test cases ensures your suite reflects actual usage; prioritizing by user impact helps you invest effort where it counts."
> — **Doc 2, p14**

### H3. Unambiguous tasks + a reference solution per task
> "A good task is one where two domain experts would independently reach the same pass/fail verdict. Could they pass the task themselves? If not, the task needs refinement. Ambiguity in task specifications becomes noise in metrics. The same applies to criteria for model-based graders: vague rubrics produce inconsistent judgments."
> — **Doc 2, p15**

**Suite implication.** Each grounding task needs an unambiguous spec (given THIS ticket with
THIS AC/RN state, the correct output is precisely X claims with precisely these citations, or a
withhold) **and** a hand-verified **reference solution** that passes all graders — proving the
task is solvable and the graders aren't broken. Ambiguous tasks become noise that masks real
regressions. Learning Studio's `eval/regression.py` (15 deterministic REG checks) is the
closest existing instance of pinned, unambiguous, solvable tasks.

> **Doc 1 cross-check.** Task-bank *size* (20–50) and *count* are absent from Doc 1 (Doc
> discusses dataset windows/holdout, not a task-bank count). Theme H is Doc 2 only.

---

## Theme I — Partial credit and grader integrity (anti-bypass)

### I1. Build in partial credit for multi-component tasks
> "For tasks with multiple components, build in partial credit. A support agent that correctly identifies the problem and verifies the customer but fails to process a refund is meaningfully better than one that fails immediately. It's important to represent this continuum of success in results."
> — **Doc 2, p16**

**Suite implication.** Decompose multi-part grounding tasks (e.g. "apply ticket to guide":
correct AC read + verbatim quote captured + jargon translated + Open question raised for
missing label) into independently scored sub-assertions, not one all-or-nothing boolean.
Learning Studio's `eval/graders.grade_all` already computes `partial_credit` = mean of per-grader
scores (and `STATE-OF-EVAL` notes tldr correctly scores 0.833 = 5/6, not 0).

### I2. Make graders resistant to bypasses/hacks
> "Make your graders resistant to bypasses or hacks. The agent shouldn't be able to easily "cheat" the eval. Tasks and graders should be designed so that passing genuinely requires solving the problem rather than exploiting unintended loopholes."
> — **Doc 2, p17**

**Suite implication.** A naive grounding grader ("does a `<!-- Source -->` comment exist near
the claim?") is trivially gamed by emitting a citation that does **not** support the text — i.e.
citation theater, the exact failure the project's resource rule #7 names. The grader must
verify the cited source **actually supports** the claim (resolve the citation; check the quoted
text exists in that ticket's AC/RN; check the lane matches), not merely that a citation token is
present. Learning Studio enforces this in layers: `qbank_gate` runs **lane-match →
verbatim-substring → semantic-support** in that order, deterministic checks first (free) and the
LLM support judge only when they pass. EVAL-SPEC also bans `enforce_citations` from the grade
path (anti-circularity) and co-scores G1+G2+G4 so "zero tier-lies because zero citations" must
FAIL.

---

## Theme J — Isolation: each trial from a clean environment

### J1. Isolate each trial; unnecessary shared state inflates or correlates results
> "Each trial should be "isolated" by starting from a clean environment. Unnecessary shared state between runs (leftover files, cached data, resource exhaustion) can cause correlated failures due to infrastructure flakiness rather than agent performance. Shared state can also artificially inflate performance. For example, in some internal evals we observed Claude gaining an unfair advantage on some tasks by examining the git history from previous trials."
> — **Doc 2, p16**

**Suite implication.** Reset state between trials: fresh copies of ticket/guide inputs, no
carryover of a previously-generated packet or changelog, no reuse of a prior trial's emitted
citations. A grounding engine that "passes" because a prior trial's packet is still on disk (or
because it read a prior trial's correct output) is measuring contamination, not grounding.
Learning Studio's `eval/EVAL-SPEC.md` §4 already isolates: the only shared mutable state is
`demo._FIX` (lock-guarded around the fast deterministic window), and `pipeline.py` omits the
`DRAFTS/` side-effect writes so trials don't collide.

> **Doc 1 cross-check.** Trial isolation is an agent-eval-harness concern absent from Doc 1's
> framing chapter. Theme J is Doc 2 only.

---

## Theme K — Data discipline: holdout, validated synthetic, drift, fresh data

### K1. (Doc 1) Three data roles — training / validation / holdout; validation ≠ final assessment
> "It is important to remember that validation data is not the final assessment dataset, because repeated use during development can indirectly shape model decisions. Holdout data, by contrast, is kept separate from both training and tuning and reserved for a more independent assessment of model performance once the model or approach is mostly finalized."
> — **Doc 1, p10**

**Suite implication.** Physically separate the eval holdout from any data used to tune
prompts/models/thresholds, and freeze it. Report the headline ship-decision number **only** on
the untouched holdout; numbers from data you iterated against are development comparisons, not
the final claim. Guard against holdout leakage in CI (hash/lock the split). `NEXT-EVALS-PLAN.md`
"Data discipline" makes this concrete: hold out topics/assets that were **not** used while
writing prompts.

### K2. (Doc 1) Synthetic data must be bounded and validated against production patterns
> "However, synthetic data should be used carefully: it can expand evaluation coverage, but it should not be treated as a perfect substitute for real historical data unless it has been validated against realistic production patterns."
> — **Doc 1, p11**

### K3. (Doc 2) Validated synthetic + real-failure sourcing; reference solution proves solvability
> "Begin with the manual checks you run during development—the behaviors you verify before each release and common tasks end users try. If you're already in production, look at your bug tracker and support queue. Converting user-reported failures into test cases ensures your suite reflects actual usage; prioritizing by user impact helps you invest effort where it counts."
> — **Doc 2, p14** *(same passage as H2; here it anchors the "prefer real over synthetic" half of the synthetic-data rule)*

**Suite implication.** Label **every** synthetic example as synthetic (a provenance tag) and
gate its use: synthetic cases may extend edge/rare coverage, but headline pass/fail claims rest
on real holdout data unless the synthetic set has a documented validation against production
distributions. Give each synthetic/constructed task a validated reference solution so a contrived
task can't be silently unsolvable-by-construction and poison the metric. **Learning Studio
status:** `eval/triage_cases.jsonl` (24 cases) and `eval/scope_cases.jsonl` (18 cases) are
**synthetic** and the runners *announce* it ("NOTE: all cases are synthetic. Collect REAL
reviewer edits…"); both have offline oracle + degenerate baselines proving the scorer. The TODO
is real-traffic cases mined from `logs/review-decisions.jsonl`.

### K4. (Doc 1) Watch for data drift; run on FRESH production data; re-run the SAME metrics
> "Even if your model performs well on offline metrics, it can still struggle in production if user behavior or product dynamics have shifted over time. This kind of shift is called data drift, and it's a common reason models underperform once they're in an online setting. To combat this, try using more recent data for holdout evaluations, slice metrics by time periods to see if performance is degrading, or implement data drift monitoring that compares distributions between training and live product data."
> — **Doc 1, p12**

### K5. (Doc 2) Evals are living artifacts; ground truth shifts as reference content changes
> "Research evals face unique challenges: experts may disagree on whether a synthesis is comprehensive, ground truth shifts as reference content changes constantly, and longer, more open-ended outputs create more room for mistakes."
> — **Doc 2, p11**

**Suite implication.** Keep the holdout recent/representative; add time-sliced metric
breakdowns; build a recurring job that recomputes the **identical** pre-launch metrics on fresh
production logs (Doc 1, p25: "when the same metrics used before launch are recomputed on fresh
production logs") so regressions surface without an A/B test. Because the project's ticket files
**mirror Jira** and guides **drift** when Cybersoft updates a PDF, a grounding eval's expected
answers can go stale when the underlying AC/RN/guide changes: (a) periodically re-validate gold
answers against current ticket/guide state, (b) flag tasks whose source changed since the gold
was set, (c) never assume a fixed snapshot is permanently correct. This is `NEXT-EVALS-PLAN.md`
item #5 — on each ICN pack re-import, recompute verbatim verification across the whole bank +
sampled support re-grade, report **"% still true"** (end-state, not bytes — a hash can sit still
while the meaning around a quote shifts).

---

## Theme L — Capability vs regression tiers; graduation

### L1. Capability evals start low (a hill to climb); regression evals sit near 100%
> "Capability or "quality" evals ask, "What can this agent do well?" They should start at a low pass rate, targeting tasks the agent struggles with and giving teams a hill to climb. Regression evals ask, "Does the agent still handle all the tasks it used to?" and should have a nearly 100% pass rate."
> — **Doc 2, p8**

*Merge with Doc 1's two-layer framing.* Doc 1 frames the same split as **canonical** (stable
reference, same dataset + metric definitions across versions) vs **deep-dive diagnostic**
(slices/segments/failure modes) — see L2/L3. The two framings are compatible: regression ≈
canonical-stable-floor; capability ≈ the improvement target whose failures the diagnostics
explain.

**Suite implication.** Split the grounding suite into two tiers. A **capability tier** of HARD
cases the engine currently flubs (subtle citation theater, AC-vs-RN contradiction handling,
internal jargon like `BABECL` needing translation) — starts low, is the improvement target. A
**regression tier** of behaviors that already work — runs on every change, expected ~100%, any
dip flags. As capability tasks reach high pass rates, **graduate** them into the regression tier.
Learning Studio today has the regression tier (`eval/regression.py`, 15/15) but the capability
tier is, in `STATE-OF-EVAL`'s words, "a saturated regression check, not a low-pass-rate 'can it
ever' bank" — the genuine capability tasks are unbuilt (Theme F).

### L2. (Doc 1) Two complementary layers — canonical + deep-dive diagnostic
> "In practice, it's helpful to think about offline evaluations as having two complementary layers: canonical offline evaluations and deep-dive diagnostic evaluations. These are not rigid categories, and different teams may use different terminology, but the distinction is useful because each layer answers a different kind of question."
> — **Doc 1, p19**

### L3. (Doc 1) Canonical = stable reference, but winning the benchmark ≠ good in production
> "Canonical offline evaluations are useful because they create a stable reference point. If every model version is evaluated against the same dataset and metric definitions, teams can make more apples-to-apples comparisons. In LLM evaluations, this might include using a fixed set of prompts and a consistent rubric, with either human reviewers or an LLM-as-a-judge scoring outputs for dimensions like relevance, groundedness, or instruction following. However, this type of evaluation may not capture all of the complexity of the live product experience. A model can improve on a benchmark while still creating unexpected behavior once it is integrated into the broader product system."
> — **Doc 1, p19**

**Suite implication.** Version the canonical dataset, prompt set, rubric, and metric
definitions; never silently mutate them between runs (a changed dataset invalidates cross-version
comparison). Treat a canonical-score win as a **gate to deeper checks, not a ship signal** — pair
it with diagnostics before promoting a version. This is `NEXT-EVALS-PLAN.md` item #6 — a
versioned golden set (held out from prompt-writing) + fixed rubric + pass@k/pass^k + a `gate_log`
capturing every gate decision, which makes items #1–5 rerunnable on every change.

---

## Theme M — Offline is a filter, not a verdict on real-world impact

### M1. (Doc 1) Offline is a first reality check; small offline gains may not be significant
> "Sometimes there may even be a small difference in offline metrics that may not be statistically significant enough to be sure the model is actually performing better in an online state. Said otherwise, small gains in offline metrics might not translate to any meaningful lift in real user engagement or conversions."
> — **Doc 1, p23**

**Suite implication.** Position the suite as a **go/iterate filter**, not the final ship
authority. Define a **minimum meaningful delta** (not just delta > 0) before calling a version
"better"; in reporting, state that a passing offline result is a candidate-promotion signal, not
proof of user impact.

### M2. (Doc 1) Hard limit: offline cannot measure feedback loops / UX-coupled behavior / real impact
> "This cascading effect can't be captured in static offline evaluations, which assume independence between the model's actions and future data distributions. When your product's success heavily depends on capturing these feedback dynamics correctly, offline evaluations should be supplemented with simulation-based approaches or online tests designed specifically to measure long-term effects."
> — **Doc 1, p26**

### M3. (Doc 2) Offline can create false confidence if it doesn't match real usage (Swiss-cheese layering)
> "Requires ongoing maintenance as product and model evolves to avoid drift
> Can create false confidence if it doesn't match real usage patterns"
> — **Doc 2, p20**

**Suite implication.** Document as **out-of-scope** for the offline suite and route to
online/human signal: (1) feedback loops where outputs reshape future inputs; (2) UX-coupled
failures (Doc 1 p26–27: a voice answer "technically accurate" offline but "too verbose for the
spoken medium"); (3) whether a learner actually **learned** or whether the quiz/flashcard format
works inside PrimeroEdge. An offline grounding suite can prove the engine produces
faithfully-cited, persona-correct artifacts — it **cannot** prove a new hire learned from them or
that an SME accepted them. Treat the offline suite as the pre-launch/CI first line of defense,
and pair it with the existing human/SME review gate (`mark_guide_reviewed`, the Library approval
gate) and real feedback for ground truth. State this limit explicitly so high offline scores
aren't mistaken for proof of real-world learning outcomes. This is `NEXT-EVALS-PLAN.md`'s closing
section ("When offline won't tell us") almost verbatim.

---

## How this maps to Learning Studio's 6-item roadmap (`NEXT-EVALS-PLAN.md`)

The roadmap's framing block already cites the offline-eval method (Doc 1) and Anthropic's agent
guidance (Doc 2). The mapping below ties each roadmap item to the merged themes and names the
**code surface** an audit can check. (Direct-read note: `STATE-OF-EVAL-2026-06-03.md` reported
`match_tickets` did **not** filter by module; the current `demo.match_tickets` *does* — lines
~206–207, `if module and (rec.get("module") or "") != module: continue`. Audit against the code,
not the older report.)

| Roadmap item | Maps to themes | Code surface to audit | Dangerous direction (roadmap's own) |
|---|---|---|---|
| **1. Calibrate the semantic-support judge — do first** | D1–D4 (judge is a calibrated method), E (k≥3), B (model lane) | `qbank_gate.llm_support_judge`, `gate_question`; gold set ~50 `(quote,stem,answer)` (to build) | **false negatives** — a verbatim-but-misleading item passed as good |
| **2. Lane-purity adversarial battery** | F1 (should/should-not), I2 (anti-bypass), B3 (brittle-to-variation) | `qbank_gate.check_lane` / `lane_of_span_id`; grow 5→~30 cross-lane near-misses | a product question grounded in a compliance span (cross-lane leak) |
| **3. Triage scorer balanced set** | F1 (one-sided optimization), I1 (partial), H (sourcing) | `eval/triage_eval.py` (FNR-gated), `eval/triage_cases.jsonl` (synthetic→add real) | auto-approving an item that needed a human (under-trigger / FNR) |
| **4. Coverage / omission for generated sets** | F2 (guardrail metric for the unmeasured blind spot), C1 (metric-per-component) | *unbuilt* — gate checks emitted citations only (`graders.G4` density, not coverage) | confident **omission** of must-cover material |
| **5. Drift / bank-freshness** | K4–K5 (drift, fresh data, re-run same metrics), G2 (implausible reading ⇒ investigate) | re-run `qbank_gate` verbatim+sampled-support across bank on each ICN re-import; "% still true" | stale-but-green (bytes unchanged, meaning shifted) |
| **6. Canonical harness + `gate_log`** | L1–L3 (canonical/regression tiers), E2 (pass@k/pass^k, k≥3), K1 (holdout), J1 (isolation) | `eval/capability.py`, `eval/graders.py`, `eval/regression.py`, `eval/EVAL-SPEC.md` §4; `gate_log` (to build) | a saturated suite with no improvement signal / k=2 underpowered |

**Cross-cutting roadmap "Data discipline" → Theme K** (holdout not used in prompt-writing;
validated synthetic; drift re-run per pack; **k ≥ 3** for any publish-blocking metric).
**Roadmap "When offline won't tell us" → Theme M** (offline proves grounding + quiz quality,
never learner outcome or in-LMS format fit; pair with eventual learner-outcome/online signals).

**Standing gaps the merge surfaces against current code (audit-true as of this writing):**
- The one real LLM judge (`qbank_gate.llm_support_judge`) has **no calibration set and no
  measured judge↔human agreement** yet (Theme D2/D3 unmet) — roadmap item #1, "do first".
- The judge prompt forces a strict YES/NO and gives the model **no `Unknown`/abstain escape**
  (Theme D4 unmet).
- `eval/capability.py` runs **no should-not / negative task** (Theme F1 unmet); CAP-09/10/14 are
  TODO in `EVAL-SPEC.md`.
- **Coverage/omission is unmeasured** end-to-end (Theme F2 unmet) — roadmap item #4.
- Measured trials were **k=2** (Theme E2 under-powered) — roadmap item #6 raises to ≥3.
- Balanced eval datasets (`triage_cases.jsonl`, `scope_cases.jsonl`) are **synthetic-only**
  today (Theme K3 partially met — labeled as synthetic, baselines present; real-traffic cases
  outstanding).
