# Next evals — plan

*Offline-evaluation roadmap for Learning Studio. Framed against the offline-evals
reference (canonical vs. diagnostic layers, metric-per-component, LLM-as-judge as a
calibrated method, data discipline, online/offline limits). Plan only — nothing built yet.*

## Framing (from the offline-eval method)

- **Two layers.** *Canonical* = a fixed dataset + consistent rubric + defined metrics,
  rerun on every change to compare versions. *Deep-dive diagnostic* = slices, segments,
  and failure-mode analysis closer to the product. We need both; canonical is the stable
  reference, diagnostics explain *why* it fails.
- **Metric follows the component.** Pick the metric category that matches what each
  piece is supposed to do (classification, ranking/retrieval, generative/LLM, agentic).
- **LLM-as-judge is a *method*, not a metric, and it must be calibrated.** It emits a
  signal, not truth; validate it against human labels before trusting it.
- **Data discipline.** Hold out data not used while designing prompts; use synthetic
  cases for rare/adversarial coverage but validate them; watch for drift on fresh data.
- **Offline ≠ the whole story.** Offline can verify grounding and quiz quality; it cannot
  tell us whether a learner actually learned or whether the format works in the LMS.

## Component → metric mapping

| Component | Metric category | Primary metric(s) | Dangerous direction |
|---|---|---|---|
| Grounding gate (verbatim + lane) | Invariant / deterministic | tier-lie=0, not-found=0, invalid-cite=0 | silent pass on wrong fixture |
| Semantic-support judge (LLM) | Generative / LLM (method = LLM-judge) | judge↔human agreement | **false negatives** (bad passed as good) |
| Lane purity | Ranking/retrieval-flavored | cross-lane leak rate (→ 0) | a product question citing a compliance source |
| Triage scorer (auto vs human) | Classification | precision/recall, weighted to **recall on `needs_human`** | auto-approving an item that needed a human |
| Quiz / flashcard generation | Generative / LLM | groundedness (by construction), relevance, **coverage** | confident omission of must-cover material |
| Bank freshness / drift | Production observability | % of bank "still true" at source checkpoints | stale-but-green (bytes unchanged, meaning shifted) |

## Prioritized roadmap

### 1. Calibrate the semantic-support judge — **do first**
Our one LLM-as-judge gates whether a verbatim-but-misleading item ships, so it must be
validated. Build a labeled gold set (~50) of `(quote, stem, answer)` triples: clearly
supported vs. *subtly* unsupported — inversions (e.g. a minimum stated as a maximum),
unit/number swaps, over-claims, right-quote-wrong-answer. Measure judge↔human agreement
and especially the **false-negative rate** (the dangerous direction). Calibrate the
prompt/threshold against it. Cross-functional: PM defines the "good" bar; eng runs it; DS
validates the labels.
- Layer: canonical · Data: hand-labeled gold + validated synthetic.

### 2. Lane-purity adversarial battery
Grow the current 5-case fixture to ~30 cross-lane near-misses on shared vocabulary
("item", "temperature", "hold", "save"). Metric = **leak rate, target 0**. Reruns on every
change as a release gate.
- Layer: canonical · Data: synthetic adversarial (validated).

### 3. Triage scorer balanced set
~30 labeled candidates spanning should-auto vs should-human (low-confidence,
sensitive-topic, weak-support, statistical outlier). Metrics = precision/recall, weighted
to **recall on `needs_human`** (auto-approving a bad item costs far more than
over-flagging). Explicitly balanced to avoid one-sided optimization.
- Layer: canonical · Data: hand-labeled.

### 4. Coverage / omission for generated sets
The gate checks *emitted* citations, never what a quiz *omits*. Per topic, define a
"must-cover" keypoint list and measure % covered by a generated quiz/study-set. This is
the currently-unmeasured gap.
- Layer: diagnostic · Data: per-topic keypoint lists (SME-defined).

### 5. Drift / bank-freshness
On each ICN pack re-import: recompute verbatim verification across the whole bank + a
**sampled support re-grade**; report **"% still true."** End-state, not bytes — a hash can
sit still while the meaning around a quote shifts.
- Layer: production observability · Data: fresh pack + bank snapshot.

### 6. Canonical harness + `gate_log` (the repeatable backbone)
A versioned golden set (topics/assets **held out** from prompt-writing) + fixed rubric +
**pass@k / pass^k**, with k raised to **≥3** (k=2 is underpowered for a publish gate), and
a `gate_log` capturing every gate decision for offline scoring. This makes 1–5 rerunnable
on every change.
- Layer: canonical backbone · Data: held-out golden set.

## Data discipline (applies to all)
- **Holdout:** keep a set of topics/assets that were NOT used while writing prompts, for
  an honest read on new inputs.
- **Synthetic:** fine for rare/adversarial cases (#1, #2), but validate against real
  chunks; never treat as a substitute for real data.
- **Drift:** re-run #5 on every pack import; slice metrics by import to catch decay.
- **Power:** k ≥ 3 trials for any publish-blocking metric.

## When offline won't tell us (don't over-trust the dashboard)
These validate *grounding and quiz quality*. They cannot tell us whether a cashier
actually **learned**, or whether the quiz/flashcard format works inside PrimeroEdge — that
is a learner-outcome / online signal available only once it's live with the real roster.
Pair these offline gates with eventual learner-outcome signals before claiming efficacy.

## Recommended first build
**#1 — the semantic-support judge gold set + scorer.** It's the linchpin the whole trust
story rests on, and it directly extends the external eval-expert brief
(`~/Downloads/Learning-Studio-eval-context.md`) and the planned `gate_log` work.
