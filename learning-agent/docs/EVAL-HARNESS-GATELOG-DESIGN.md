# Canonical eval harness + `gate_log` — design

*The repeatable backbone for Learning Studio's offline evals: a **versioned golden set**
(topics/assets held out from prompt-writing), a **fixed rubric**, **pass@k vs pass^k with
k ≥ 3**, and a concrete **`gate_log` schema** that records every gate decision so the whole
suite is rerunnable on every change and so the recorded decisions feed judge calibration (#1)
and drift (#5).*

This is `NEXT-EVALS-PLAN.md` **item #6** — explicitly *"the repeatable backbone … nothing built
yet"* (`NEXT-EVALS-PLAN.md:70-75`, and the plan's own header line 6: *"Plan only — nothing
built yet."*). This document is the build spec for that item. It does **not** re-derive the
judge metrics (owned by `docs/JUDGE-CALIBRATION-PLAN.md`, item #1) or the methodology citations
(owned by `docs/eval-methodology-digest.md`); it references both and stays in its lane.

> **Status check, read first (no whitewashing).** Nothing in this document is built. The
> harness that exists today — `eval/capability.py` + `eval/pipeline.py` + `eval/graders.py` —
> runs **one module, one transcript, code-graders only**, and the single recorded canonical run
> (`eval/runs/20260603T183555Z/report.json`) was **k=2** (`"trials": 2`, line that file). There
> is **no held-out golden set**, **no `gate_log`**, and **no offline re-scorer** for the guide
> pipeline. The three sibling offline scorers that *do* exist — `eval/judge_eval.py`,
> `eval/scope_eval.py`, `eval/triage_eval.py` — are the proven house pattern this backbone must
> extend (oracle + degenerate baselines that assert the scorer itself, FNR/FPR separation, a
> single gated dangerous direction, a validated jsonl dataset). This doc converges them onto one
> shared `gate_log` substrate. Until it is built and a baseline is recorded on a frozen holdout,
> the green dashboard proves what `STATE-OF-EVAL-2026-06-03.md` §1 says it proves: *"one happy
> path (one module, one fixture, code-graders only)"* with *"no hill to climb."*

---

## 0. The two failures this backbone is built to stop

The dominant risk in this area is a **publish gate that is green for reasons that are not model
correctness.** There are two independent ways that happens today, and the backbone closes the
first fully and instruments the second.

**Failure A — under-powered gate (the power half).** The recorded canonical run is k=2. At k=2,
a behavior that is only 75 %-reliable still clears `pass^k` by luck **≈56 %** of the time
(0.75² = 0.5625). `STATE-OF-EVAL-2026-06-03.md` §3 states this directly: *"k=2 is underpowered
… At k=2 a 75 %-reliable behavior still shows clean pass^k ~56 % of the time by luck."* The
`eval-methodology-digest.md` Theme E2 carries the Anthropic quote the number comes from (Doc 2,
p13) and notes Learning Studio's *"measured run was k=2."* §3 of this doc fixes this: k ≥ 3,
reported per format, on a frozen set.

**Failure B — by-construction-green grounding (the relevance half).** On the `cell_d` path
(`demo_d.py`), the section writer emits only `[CITE:id]`; `assemble._render` writes the quote
and tier verbatim from the registry. So `demo.validate_citations` *cannot* return a non-zero
`tier_lie`/`quote_not_found` on that path — `eval/graders.py:33,41` literally label G1/G2
*"invariant: 0 by construction."* That makes the grounding invariant anchored to **fixture
trust, not relevance.** `STATE-OF-EVAL-2026-06-03.md` §5 states the boundary in one line:

> *"the gate proves the quote is verbatim and correctly-tiered; it does NOT prove the quote is
> about what the sentence claims."*

The costliest manifestation is the **silent wrong-module ground**: `match_tickets` does not
filter by module (`STATE-OF-EVAL-2026-06-03.md` §5 outcome (B)), so a transcript run against the
wrong fixture produces real, verbatim, correctly-tiered citations *about the wrong feature* —
and **every grader still passes.** This backbone cannot turn an invariant into a relevance proof
on its own (that needs the lane-purity battery #2, coverage #4, and the module-filter fix the
STATE-OF-EVAL §6 ranks first). What it **can** do is make Failure B **measurable and
non-silent**: the `gate_log` records the `fixture_hash` and `module` on every decision, the
golden set includes a held-out **wrong-module negative** whose expected verdict is *block*, and a
green run on that case is then a recorded, reviewable lie rather than an invisible one. §6.3.

> **Scope honesty.** Item #6 is the **canonical backbone** — power + repeatability +
> recorded decisions. It is necessary but not sufficient for the relevance half. The
> `gate_log` is the substrate the relevance gates (#1, #2, #4) write into and are scored from;
> it does not itself decide relevance.

---

## 1. What "canonical" means here (and what it is not)

From the offline-eval method as merged in `eval-methodology-digest.md` Theme L and
`NEXT-EVALS-PLAN.md` Framing:

- **Canonical layer** = a **fixed dataset + a consistent rubric + defined metrics**, rerun on
  every change to compare versions. Stable reference. *This document.*
- **Deep-dive diagnostic layer** = slices, segments, failure-mode analysis closer to the
  product. Explains *why* the canonical number moved. The `gate_log` (§4) is what the diagnostic
  layer queries.

The canonical/regression mapping already in the codebase:
`eval/regression.py` (REG-01…15, deterministic, no-SDK, 15/15 in the recorded run) **is** the
canonical-stable floor. `eval/capability.py` is the improvement target. `eval-methodology-digest.md`
Theme L states the equivalence: *"regression ≈ canonical-stable-floor; capability ≈ the
improvement target whose failures the diagnostics"* explain. The backbone in this doc adds the
**third leg the canonical layer is missing: a versioned, held-out golden set and a recorded
decision log**, so that "rerun on every change to compare versions" is actually possible — today
each `eval/capability.py` run mints a *fresh* stamp dir and there is no version-over-version
comparison artifact.

**Canonical is not:** the LLM support judge (a *method*, not the canonical metric — see
`JUDGE-CALIBRATION-PLAN.md` §0 and methodology Theme D1), nor the live demo server, nor a number
computed on data the prompts were tuned against (that is a development comparison, not a ship
claim — methodology K1, §2 below).

---

## 2. The versioned golden set (held out from prompt-writing)

### 2.1 Why holdout, stated from the source

`eval-methodology-digest.md` Theme K1 quotes Doc 1 directly:

> *"Holdout data … is kept separate from both training and tuning and reserved for a more
> independent assessment of model performance once the model or approach is mostly finalized."*

and the suite implication (K1): *"Report the headline ship-decision number **only** on the
untouched holdout; numbers from data you iterated against are development comparisons, not the
final claim. Guard against holdout leakage in CI (hash/lock the split)."* `NEXT-EVALS-PLAN.md`
Data-discipline says the same in product terms: *"keep a set of topics/assets that were NOT used
while writing prompts, for an honest read on new inputs."*

The Learning Studio-specific reason this matters more than usual: the generation prompts in
`templates/` and the planning prompt in `demo_d.plan_system_prompt` were written and tuned
against the **Item Management** transcript and fixture. Any number computed on Item Management is
therefore a *development* number. The recorded canonical run is Item Management
(`report.json` line `"module": "Item Management"`). **It is not a holdout read**, and the
backbone must stop treating it as one.

### 2.2 What is held out — and the state change since STATE-OF-EVAL

`STATE-OF-EVAL-2026-06-03.md` (dated 06-03) repeatedly says *"only `item-management-fixture.json`
is present."* **That is now stale.** As of 2026-06-07, `data/demo/` contains **eight** module
fixtures (verified by direct read):

```
account-management   accountability   eligibility   financials
insights             inventory        item-management  menu-planning
```

all `captured_at: "from-csv:Perseus Jira (…).csv"` (CSV-sourced, not live-Jira capture). This is
the raw material that makes a held-out split possible for the **first time** — but it is *raw
material, not a golden set*. A fixture is a ticket corpus; a golden-set case is a
`(transcript, module, format, expected-verdicts)` tuple with a frozen reference. The split:

| Split | Used for | Rule |
|---|---|---|
| **Dev** (Item Management) | Tuning prompts/templates/thresholds. The current k=2 run lives here. | May be iterated against freely. Numbers from it are dev comparisons, never the ship claim. |
| **Holdout** (≥2 of the other 7 modules, transcript + fixture, chosen *after* prompts froze) | The **headline ship-decision number** at k ≥ 3. | **Frozen and locked.** Never read while editing prompts. Leakage-guarded in CI (§2.4). |
| **Adversarial negatives** (synthetic, labeled) | The should-NOT cases (wrong-module, empty-AC, planted conflict). | Synthetic, validated against real chunks, clearly labeled `provenance: synthetic`. §6.3. |

> **Honest caveat on the holdout's independence.** All eight fixtures came from the **same
> CSV import** (`Perseus Jira (5).csv` for seven of them). They are different *modules* but the
> same *extraction pipeline and vintage*. That makes them a genuine cross-module holdout for
> *generation* and *grounding-plumbing*, but **not** an independent test of the extraction/capture
> step — a capture bug (e.g. AC written into the desc field, the exact `EVAL-SPEC.md` open-q #2
> scenario) would be correlated across all of them. A true capture-independent holdout needs a
> live-Jira `demo_capture.py` pull or a second import vintage. Record this limitation in the
> golden-set manifest; do not claim more independence than the data has.

### 2.3 Versioning the golden set

The set is **versioned**, not ad-hoc, because "rerun on every change to compare versions"
requires the dataset itself to be a stable, identifiable thing:

- The golden set lives at `eval/golden/golden_set.jsonl` (one case per line, same jsonl idiom as
  `judge_gold_set.jsonl` / `scope_cases.jsonl` / `triage_cases.jsonl`).
- It carries a `golden_set_version` (semver: `MAJOR.MINOR`). **MINOR** = added cases;
  **MAJOR** = changed/removed a case or changed the rubric. The version is stamped into every
  `gate_log` row (§4) so a metric is always attributable to the exact set that produced it.
- Each case carries a `frozen_at` date and the `fixture_hash` of the fixture it binds to (§4.2),
  so a fixture re-import (drift, #5) that changes the corpus is detected as a hash mismatch
  rather than silently re-scoring against moved ground truth.

**Case schema** (`eval/golden/golden_set.jsonl`), mirroring the sibling sets' label-first style:

```json
{
  "id": "GOLD-menuplanning-longform-01",
  "split": "holdout",                         // dev | holdout | adversarial
  "module": "Menu Planning",
  "transcript": "raw/transcripts/<...>.md",
  "format": "long-form",                      // long-form | micro-guide | tldr
  "fixture_hash": "sha256:…",                 // the fixture this case is bound to (§4.2)
  "golden_set_version": "1.0",
  "frozen_at": "2026-06-07",
  "provenance": "real",                       // real | synthetic (synthetic MUST be labeled)
  "expected": {                               // the fixed rubric's expected verdicts (§3.1)
    "final_verdict": "pass",                  // pass | block  (block for adversarial negatives)
    "must_block_grader": null,                // e.g. "G6_length" for a known-overrun case
    "must_cover": ["…keypoint…"]              // SME-defined coverage anchors (feeds #4); [] if not yet defined
  },
  "rationale": "Why this case is in the set and what it tests."
}
```

`must_cover` is intentionally present-but-often-empty: coverage/omission (#4) is a *diagnostic*
layer that needs SME-defined keypoint lists (`NEXT-EVALS-PLAN.md` #4), and wiring the field now
means the golden set is ready to carry it without a schema MAJOR bump later.

### 2.4 Leakage guard (CI)

Methodology K1: *"Guard against holdout leakage in CI (hash/lock the split)."* Concretely:

- `eval/golden/HOLDOUT.lock` records the sha256 of each holdout case's `(transcript, fixture)`
  pair at freeze time.
- A pre-run check (`eval/golden_check.py`, offline, no-SDK) recomputes those hashes and **exits
  non-zero** if a holdout transcript or its bound fixture changed since freeze — the same
  exit-code discipline `judge_eval.py` / `scope_eval.py` / `triage_eval.py` use. A changed
  holdout is either intentional (bump `golden_set_version`, re-freeze, re-baseline) or a leak
  (someone tuned against the holdout); either way it must be a loud failure, never silent.

---

## 3. The fixed rubric and the metric

### 3.1 The rubric is the existing deterministic grader set — frozen and named

The fixed rubric is **`eval/graders.py` G1–G6**, run by `grade_all`. It is already the publish
authority (`EVAL-SPEC.md` §3, `graders.py:1` docstring) and already returns per-grader
`{name, passed, score, metric, detail}`. The backbone's contribution is to **freeze and version
it** alongside the golden set: a `rubric_version` stamped into every `gate_log` row, bumped when
any grader's logic or threshold changes. The grader→metric assignment is the one already in code
(`graders.py:118`, `EVAL-SPEC.md` §3, methodology C04 — metric-per-component):

| Grader | What it asserts (end-state, not path) | Metric |
|---|---|---|
| G1 tier_lie | `art["integ"]["tier_lie"] == 0` — *invariant on cell_d* | pass^k |
| G2 quote_not_found | `art["integ"]["quote_not_found"] == 0` — *invariant on cell_d* | pass^k |
| G3 invalid_cite_id | `art["asm"]["invalid_cite_id"] == 0` and no `INVALID_CITE_ID` in html | pass^k |
| G4 density | `tokened>0` AND `ok/tokened ≥ 0.9` AND `tokened ≥ ceil(words/250)` | **pass@k** |
| G5 section_fit | `<h2>` count ≥ `_MIN_SECTIONS[fmt]`, no failed-section placeholder | pass^k |
| G6 length | no section `stop_reason=='max_tokens'` AND `words ≤ _CEILING[fmt]` | pass^k |

This satisfies methodology **C01** (grade the end-state artifact, not the trajectory): every
grader reads the artifact dict (`art["html"]`/`["integ"]`/`["asm"]`/`["sections"]`/`["words"]`)
— none asserts a tool-call sequence. The audit confirmed this is **met**.

> **Two honest rubric caveats to keep in the doc, not paper over.**
> 1. **G1/G2 are invariants on the `cell_d` path, not skill measures.** `graders.py:33,41` say so.
>    On the golden set's *holdout* cases (all `cell_d`), G1/G2 being 0 proves plumbing, not model
>    choice. The only place tier-assignment is genuinely *tested* by the model is the `demo_single`
>    path (`EVAL-SPEC.md` open-q #2,#6) and the constructed-HTML regressions REG-01/02/03. The
>    `gate_log` records G1/G2 with an `invariant: true` flag on cell_d rows so a reader never
>    mistakes a green invariant for a passed skill test. §4.1.
> 2. **G5 duplicates a constant.** `graders.py:22 _MIN_SECTIONS` must stay in sync with the
>    inline `min_sections` in `demo_d.run_cell_d` (REG-09 already checks the demo_d side; the
>    recorded run shows `min_sections 5/6/8 inline`). The audit flagged this as a duplicated-constant
>    drift risk, not a path-assertion. A one-line assert that `graders._MIN_SECTIONS` /
>    `_CEILING` match `demo_d._FORMAT_*` belongs in the regression suite; the rubric version must
>    bump if either changes.

### 3.2 pass@k vs pass^k, and why k ≥ 3 for a publish gate

Definitions, exactly as the existing harness computes them (`capability.py:81-83`):

- **`pass@k`** = "can it ever" — `any(trial_passed for the k trials)`. Capability/quality signal.
  G4 (density) uses this.
- **`pass^k`** = "does it reliably never regress" — `all(trial_passed for the k trials)`.
  Consistency signal. The grounding/structure graders (G1,G2,G3,G5,G6) use this.

**Why k=2 is underpowered for a publish gate (the core of this item).** `pass^k` is the
probability all k independent trials pass; for a per-trial reliability p it is pᵏ. The
methodology digest Theme E2 quotes Doc 2 (p13) verbatim:

> *"If your agent has a 75 % per-trial success rate and you run 3 trials, the probability of
> passing all three is (0.75)³ ≈ 42 %. This metric especially matters for customer-facing agents
> where users expect reliable behavior every time."*

The publish gate here is customer-facing (published guides, `CLAUDE.md` Status Gating). The table
shows why k=2 is too weak a sieve and k ≥ 3 is the floor:

| per-trial reliability p | pass^2 (k=2, today) | pass^3 (k=3, floor) | pass^5 |
|---|---|---|---|
| 0.99 | 0.980 | 0.970 | 0.951 |
| 0.95 | 0.903 | 0.857 | 0.774 |
| 0.90 | 0.810 | 0.729 | 0.590 |
| **0.75** | **0.563** | **0.422** | 0.237 |
| 0.50 | 0.250 | 0.125 | 0.031 |

At k=2 a badly-unreliable 0.75 behavior clears `pass^k` more often than not (0.563). That is the
exact number `STATE-OF-EVAL-2026-06-03.md` §3 calls out (*"~56 % of the time by luck"*). At k=3
it drops to 0.422 — still not a *pass*, but now the gate *fails it most of the time*, which is the
point of a consistency gate. **k ≥ 3 does not make an unreliable behavior pass; it stops an
unreliable behavior from passing by luck.** `NEXT-EVALS-PLAN.md` Data-discipline states the rule
flatly: *"Power: k ≥ 3 trials for any publish-blocking metric."* `EVAL-SPEC.md` §3 already sets
*"Default `trials: 3`"* and `capability.py:144` already defaults `--trials 3` with the inline
comment *"≥3 for a real pass^k publish-gate reading"* — **the default was raised, but the recorded
canonical artifact is still k=2.** The backbone's job is to make the *recorded* canonical run k ≥ 3
on the *holdout*, and to refuse to publish a ship number computed at k < 3.

> **Power is necessary, not sufficient.** k ≥ 3 fixes Failure A (luck). It does nothing for
> Failure B (by-construction-green on a wrong fixture) — a wrong-module ground passes at k=3 just
> as cleanly as at k=2, because every trial grounds against the same wrong fixture. Do not let a
> green pass^3 be read as a relevance proof. That is what #1/#2/#4 and the wrong-module negative
> (§6.3) are for.

### 3.3 What the harness must add to compute this honestly

`capability.py` already computes `pass_at_k`/`pass_caret_k`/`pass_rate`/`mean_partial_credit`
per format (`_aggregate`, lines 57-88) and re-creates a fresh registry+semaphore per trial via
`pipeline.run_pipeline` (the isolation `EVAL-SPEC.md` §4 requires). The deltas for the canonical
backbone:

1. **Default and *enforce* k ≥ 3 for any run tagged `ship`.** A `--profile ship` run exits
   non-zero if `--trials < 3`. `--profile dev` may use k=1/2 for fast iteration but its numbers
   are never written to the ship-baseline.
2. **Run the loop over the golden set, not a single `--module`/`--transcript`.** Iterate the
   `holdout` split's `(module, transcript, format)` cases; load each case's fixture by
   `fixture_hash` (verifying the hash, §4.2).
3. **Emit a `gate_log` row per (case × trial)** (§4) in addition to the existing `report.json`.
4. **Write a stable `eval/golden/baseline.json`** = the headline holdout numbers at the current
   `golden_set_version` + `rubric_version`, so the *next* run can diff against it (version
   comparison — the thing the canonical layer is for).

---

## 4. The `gate_log` schema

### 4.1 One row per gate decision

The `gate_log` is an append-only **JSONL** ledger: one row per **gate decision** = one item
evaluated by the rubric in one trial. It is the offline-scoring substrate — the thing that makes
#1–#5 rerunnable and the thing #1 (judge calibration) and #5 (drift) read from. It deliberately
records **everything needed to re-score offline without re-running the model**, and the
provenance fields (`fixture_hash`, `*_version`) needed to attribute any number to its inputs.

Path: `eval/gate_log/<run_stamp>.jsonl` (run_stamp = the UTC stamp `capability.py` already mints,
`datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")`). Append-only; never edited in place (drift #5
appends new rows on each re-import, it does not mutate old ones).

Every field below maps to something that already exists in the codebase — no invented metrics.

```json
{
  // ── identity / provenance ────────────────────────────────────────────────
  "timestamp": "2026-06-07T18:35:55Z",        // when this decision was recorded
  "run_stamp": "20260607T183555Z",            // groups all rows of one harness run
  "item_id": "GOLD-menuplanning-longform-01", // golden-set case id (§2.3) OR an ad-hoc id
  "source": "golden:holdout",                 // golden:holdout | golden:dev | golden:adversarial
                                              //   | server:approve | regression
  "trial": 1,                                 // 1..k
  "k": 3,                                      // trials configured for this run (power audit)
  "module": "Menu Planning",
  "format": "long-form",                      // long-form | micro-guide | tldr
  "path": "cell_d",                           // cell_d | demo_single (decides invariant semantics)

  // ── the inputs that make the decision reproducible / attributable ─────────
  "fixture_hash": "sha256:…",                 // §4.2 — the ground-truth corpus this ran against
  "transcript_hash": "sha256:…",              // the immutable transcript (raw/transcripts/ is immutable)
  "golden_set_version": "1.0",
  "rubric_version": "1.0",                    // bumps when any grader logic/threshold changes
  "judge_version": "none",                    // §4.3 — judge id+prompt hash, or "none" if no judge ran
  "model": "claude-sonnet-4-6",               // generator model (from art["cost"]["model"])
  "code_rev": "git:19735cc",                  // repo commit, for full reproducibility

  // ── the three grounding sub-results (named exactly as the gates emit them) ─
  "verify_result": {                          // VERBATIM check — qbank: check_verbatim / guide: integ
    "tier_lie": 0, "quote_not_found": 0,      //   guide path: from demo.validate_citations (art["integ"])
    "tokened": 173, "ok": 173,
    "invariant": true                         //   true on cell_d (graders.py:33,41) — NOT a skill pass
  },
  "lane_result": {                            // LANE check — qbank_gate.check_lane (qbank items only)
    "checked": false,                         //   false for guide-pipeline rows (no lane concept there)
    "lane_ok": null, "q_lane": null, "span_lane": null
  },
  "support_result": {                         // SEMANTIC support — qbank_gate.llm_support_judge (advisory)
    "ran": false,                             //   false unless a judge ran (guide pipeline: usually false)
    "ok": null, "reason": null
  },

  // ── the rubric verdict (the deterministic publish authority) ──────────────
  "graders": [                                // verbatim from grade_all(art, fmt)["graders"]
    {"name": "G1_tier_lie",  "passed": true,  "score": 1.0, "metric": "pass^k", "detail": "tier_lie=0 (invariant: 0 by construction)"},
    {"name": "G6_length",    "passed": false, "score": 0.0, "metric": "pass^k", "detail": "truncated=0 words=794 ceiling=500"}
    // … G2–G5 …
  ],
  "trial_passed": false,                      // grade_all(...)["trial_passed"] — all REQUIRED graders pass
  "partial_credit": 0.833,                    // grade_all(...)["partial_credit"] — mean grader score

  // ── the final gate decision ──────────────────────────────────────────────
  "final_verdict": "block",                   // pass | block. pass == trial_passed AND (no judge OR support_result.ok)
  "expected_verdict": "block",                // from the golden case (§2.3); null for ad-hoc/server rows
  "verdict_matches_expected": true,           // final_verdict == expected_verdict (the offline-scorable bit)
  "cost_usd": 0.5128,                          // art["cost"]["cost_usd"] — per-trial cost
  "html_file": "long-form-trial2.html"        // pointer to the persisted artifact for transcript review
}
```

**Field-to-source map (every field is grounded, none invented):**

| `gate_log` field | Source in code |
|---|---|
| `verify_result.{tier_lie,quote_not_found,tokened,ok}` | `demo.validate_citations(html)` → `art["integ"]` (`pipeline.py:65`); `report.json` `integ` block |
| `verify_result.invariant` | `true` on `cell_d` per `graders.py:33,41`; the *fact* that cell_d forces 0 |
| `lane_result.*` | `qbank_gate.check_lane` → `gate_question` `{lane_ok}` (`qbank_gate.py:37,87`); guide rows set `checked:false` |
| `support_result.*` | `qbank_gate.llm_support_judge` → `{ok,reason}` (`qbank_gate.py:51,101`) |
| `graders[]`, `trial_passed`, `partial_credit` | `eval/graders.py grade_all(art, fmt)` (`graders.py:109-122`) |
| `fixture_hash` | sha256 of the loaded fixture json (§4.2; `demo._FIX`) |
| `cost_usd`, `model` | `art["cost"]` via `pricing.cost_of` (`pipeline.py:71`) |
| `run_stamp` | `capability.py:156` UTC stamp |

The three sub-results (`verify_result` / `lane_result` / `support_result`) are exactly the three
checks `qbank_gate.gate_question` runs in order (`qbank_gate.py` docstring: *"reaches `verified`
only if ALL THREE pass … lane-match → verbatim → support"*). The guide pipeline today only runs
the verify check (the integ report) and has **no lane and no live support judge** — so guide-row
`lane_result.checked` and `support_result.ran` are `false`, and the row faithfully records *that
those checks did not run*. This is the honest representation: the log shows which gates fired, so
a reader never assumes lane/support were enforced on a row where they were not.

### 4.2 `fixture_hash` — what it is and why it's load-bearing

There is no existing `fixture_hash` in the codebase (verified by grep: `sha256` appears only in
`data/icn/data/asset_manifest.json` for ICN assets, and `captured_at` is a *string label*, not a
content hash). The backbone introduces it: **`fixture_hash = "sha256:" + sha256(canonical-json
of the loaded fixture)`**, computed once when `demo._FIX` is set, recorded on every row.

It is load-bearing for three of the five reasons this whole area exists:

1. **Attribution.** A green run is only meaningful relative to the corpus it ran against.
   `EVAL-SPEC.md` open-q #2 names the residual risk: the gate and the registry *share one ground
   truth* (`demo._FIX`). The hash makes the shared ground truth an explicit, recorded input — so
   "all-PASS" is always qualified by *"against fixture sha256:abc…"*, never an unqualified claim.
2. **Wrong-module detection (Failure B).** The golden case binds a `fixture_hash`; the harness
   verifies the loaded fixture's hash equals the case's. A mismatch — the silent wrong-module trap
   (`STATE-OF-EVAL-2026-06-03.md` §5(B)) where `--module` defaulted to Item Management — is caught
   as a hash mismatch **before** generation, not discovered post-hoc by eyeballing citations.
3. **Drift (#5).** When an ICN/Jira pack is re-imported, the fixture content changes → its hash
   changes. A changed `fixture_hash` on the same `item_id` is the drift signal: re-score that
   item's bank and report *"% still true"* (`NEXT-EVALS-PLAN.md` #5). §7.2.

### 4.3 `judge_version` — and why it's mostly `"none"` today

`judge_version` = an identifier for the semantic-support judge that produced `support_result`,
defined as `"<model>+<sha256(system_prompt)[:8]>"` (e.g. `claude-sonnet-4-6+a1b2c3d4`). There is
no `JUDGE_VERSION` constant today (verified by grep) — the backbone introduces it, hashing
`qbank_gate.llm_support_judge`'s `sys_prompt` (`qbank_gate.py:54-61`) so a prompt edit is visibly
a new judge version in the log.

On guide-pipeline rows it is `"none"` because **no judge runs in the guide gate** — the publish
authority is deterministic (`EVAL-SPEC.md` §3, methodology C03: the LLM judge is *advisory only*
and must not gate). `judge_version` is populated on **qbank rows** (quiz/flashcard gating, where
`llm_support_judge` is the third check) and is the join key the judge-calibration loop reads (§7.1).

> **Methodology C03 (deterministic lane is the authority).** The audit's methodology checklist
> item C03 requires the deterministic lane to be the publish authority and the LLM judge demoted
> to advisory. The `gate_log` encodes this structurally: `final_verdict` is computed from
> `trial_passed` (deterministic) **first**; `support_result` only *further* blocks (an advisory
> judge can demote a question to `needs_human`, never *promote* a deterministically-failed one).
> A row can never show `final_verdict: pass` while `trial_passed: false`. The log makes a
> "judge waved it through" bug impossible to hide.

---

## 5. How this makes builds #1–#5 rerunnable on every change

The canonical backbone is the harness loop + the golden set + the `gate_log`. Each of #1–#5 is
either *run by* this loop or *scored from* the log it produces. "Rerunnable on every change" means:
on any change (prompt edit, model bump, fixture re-import, rubric tweak), re-run the loop and diff
the new `baseline.json` / `gate_log` against the frozen one.

| Build | How the backbone makes it rerunnable |
|---|---|
| **#1 judge calibration** | The judge is scored **offline from `gate_log`** `support_result` + `judge_version`, joined to `judge_gold_set.jsonl` labels — no model re-run needed to recompute agreement after a label fix. §7.1. Owned by `JUDGE-CALIBRATION-PLAN.md`; this doc supplies the substrate. |
| **#2 lane purity** | Lane-purity cases run through the same loop; their decisions land in `gate_log` `lane_result`. Leak rate = rows where `lane_result.lane_ok == false` over cross-lane cases. Rerun on every change; target 0 (`NEXT-EVALS-PLAN.md` #2). |
| **#3 triage** | `triage_eval.py` already exists with the house pattern; the backbone unifies its output into the `gate_log` shape (item_id, expected vs final, dangerous-direction rate) so triage is diffed version-over-version like everything else. |
| **#4 coverage/omission** | The golden case carries `expected.must_cover`; a coverage scorer reads the produced artifact (pointed to by `html_file`) and the keypoint list, writes `% covered` as a diagnostic metric. The field is already in the schema (§2.3) so no MAJOR bump is needed when #4 lands. |
| **#5 drift** | On each pack re-import, fixtures change → `fixture_hash` changes → the loop re-runs the affected golden cases, appends fresh `gate_log` rows, and reports *"% still true"* by comparing new verdicts to the frozen baseline for the same `item_id`. §7.2. |

The unifying property: **every gate decision in the system — guide publish gate, qbank gate,
triage, scope — writes the same `gate_log` row shape.** That is what turns five separate evals
into one rerunnable canonical suite instead of five bespoke scripts. The four scorers that exist
(`judge_eval`, `scope_eval`, `triage_eval`, and `capability`'s `report.json`) already share a
house style; this backbone makes them share a *substrate*.

---

## 6. Offline scoring from the `gate_log` (the rerun, without re-running the model)

### 6.1 Why offline re-scoring is the point

Generation is expensive and non-deterministic (the recorded run cost **$4.43** for k=2 across 3
formats — `report.json` `total_cost_usd`). Re-running the model every time a *label* is fixed or a
*threshold* is tuned is wasteful and, worse, changes two things at once (you can't tell if the
number moved because of the model or the relabel). The `gate_log` records the model's *actual
outputs* (`verify_result`, `support_result`, `graders[]`), so:

- **Re-scoring after a label fix** (#1: DS relabels a disputed judge case) = re-read the log's
  `support_result.ok` against the new label. No model call. This is exactly how `judge_eval.py`'s
  offline mode already works (oracle/baselines over a static dataset, *"stdlib only — NO SDK / no
  auth"*, `judge_eval.py:28-31`).
- **Re-scoring after a threshold change** (e.g. G4's 0.9 ok-ratio, `EVAL-SPEC.md` open-q #1) =
  re-evaluate the rubric arithmetic over the logged `integ`/`words`. No model call.

### 6.2 The offline scorer follows the proven house pattern

`eval/gate_log_score.py` (offline, no-SDK) mirrors `judge_eval.py` / `scope_eval.py` /
`triage_eval.py` exactly — because that pattern has already been validated three times in this
codebase:

1. **Load + validate the log** (assert rows well-formed, both expected verdicts present in the
   adversarial split — the anti-one-sided-optimization check, `EVAL-SPEC.md` §2, methodology F1).
2. **Oracle + degenerate baselines that assert the scorer itself.** Just as `judge_eval.py:188-200`
   asserts an oracle is perfect and an always-`supported` baseline is FNR=1.0/FPR=0.0, the gate_log
   scorer asserts: an oracle (`final_verdict == expected_verdict` for all rows) scores perfect, and
   a degenerate **always-`pass`** scorer scores **wrong on every adversarial `block` case** (so a
   gate that rubber-stamps everything is exposed). This is the guard that *the scorer can't hide a
   model failure behind a broken metric.*
3. **Compute the headline numbers, gated on the dangerous direction:**
   - `pass^k` / `pass@k` per (module, format) — recomputed from the logged per-trial `trial_passed`.
   - **The dangerous-direction metric: `missed_block_rate`** = adversarial `block` cases the gate
     let `pass` ÷ adversarial `block` cases. This is the gate_log analogue of judge FNR /
     scope wrong-module-rate / triage `needs_human` recall. The `--live`-equivalent (here:
     `--gate`) exits non-zero when `missed_block_rate > 0`, identical to the three siblings.

```
python -m eval.gate_log_score eval/gate_log/<stamp>.jsonl            # OFFLINE: oracle + baselines, assert scorer
python -m eval.gate_log_score eval/gate_log/<stamp>.jsonl --gate     # exit non-zero if missed_block_rate>0 or any ship pass^k<floor at k<3
```

### 6.3 The wrong-module negative (the case that makes Failure B non-silent)

The single most important adversarial case, because it targets the costliest failure
(`STATE-OF-EVAL-2026-06-03.md` §5(B), and the audit's `dominant_risk`):

- **`GOLD-wrongmodule-01`** (`split: adversarial`, `provenance: synthetic`, clearly labeled): a
  transcript for module X deliberately run against module Y's fixture. `expected.final_verdict:
  "block"`.
- **Today, the rubric would pass it** — `tier_lie=0`, `quote_not_found=0`, `invalid_cite_id=0`,
  all-PASS, because the gate has no notion of module relevance (`STATE-OF-EVAL-2026-06-03.md` §5:
  *"The grounding gate STILL PASSES … because the gate has no notion of module relevance."*).
- So the `gate_log` row will show `final_verdict: pass`, `expected_verdict: block`,
  **`verdict_matches_expected: false`** — and the offline scorer's `missed_block_rate` is **> 0**,
  so `--gate` **exits non-zero.** The by-construction-green failure is now a **recorded, CI-failing
  fact** instead of an invisible one.

> **Critical honesty.** This case **does not fix** wrong-module grounding — that needs the
> module filter in `match_tickets` (STATE-OF-EVAL §6 ranks it #1) and/or the lane battery (#2).
> What it does is make the gap **measurable and loud**: a red `missed_block_rate` is the standing
> alarm that the relevance half is unsolved. When the module filter lands, *this same case* flips
> to `block` and the alarm clears — that is the case being rerunnable on the change that fixes it.
> The `fixture_hash` mismatch guard (§4.2) is the *belt*; this scored negative is the *suspenders*.

---

## 7. Two consumers of `gate_log`, concretely

### 7.1 Feeds judge calibration (#1)

`JUDGE-CALIBRATION-PLAN.md` owns the judge metrics (agreement, FNR gate, FPR-as-friction,
per-defect-family slices, the noise floor, the synthetic/real `provenance` slice). The `gate_log`
is the **substrate** that plan reads:

- Each qbank gate decision logs `support_result.{ok,reason}` + `judge_version` + `item_id`.
- For calibration, `item_id` joins to a `judge_gold_set.jsonl` case's `ground_truth_support`; the
  scorer computes judge↔human agreement and **FNR** (the gated dangerous direction) **offline from
  the log** — no re-run when DS fixes a label (e.g. the `wrong_answer-c06` boundary-probe relabel
  the judge plan flags in its §2.1).
- `judge_version` in the log means *every recorded judge verdict is attributable to an exact
  prompt*. When the judge prompt changes, the version changes, and the calibration number is
  recomputed against the *new* version's logged verdicts — version-over-version comparison, which
  is the whole point of the canonical layer.

> **Schema-bridge caveat (carried from `JUDGE-CALIBRATION-PLAN.md` §4.1).** The judge's calling
> convention (`gate_question` passes `quote, stem, correct` — `qbank_gate.py:100`) and the gold
> set's row schema are not identical; the judge plan flags this as *"real work, not a wiring
> detail."* The `gate_log` `support_result` records what the judge **actually saw and returned**,
> so it sidesteps the bridge for *scoring* (you score the logged verdict against the label) — but
> the bridge still matters for the **`--live`** path that produces those verdicts. This doc does
> not solve the bridge; it records its output faithfully and points at the judge plan.

### 7.2 Feeds drift / bank-freshness (#5)

`NEXT-EVALS-PLAN.md` #5: on each ICN/Jira pack re-import, *"recompute verbatim verification across
the whole bank + a sampled support re-grade; report '% still true.' End-state, not bytes — a hash
can sit still while the meaning around a quote shifts."*

The `gate_log` is the before/after ledger:

- A re-import changes fixtures → `fixture_hash` changes → the loop re-runs affected golden cases
  → appends new rows under a new `run_stamp` for the same `item_id`s.
- *"% still true"* = the fraction of `item_id`s whose `final_verdict` is unchanged (still `pass`)
  against the new `fixture_hash`, vs the frozen baseline. A `pass → block` flip on re-import is a
  drift hit: the quote's verbatim anchor or its tier moved under it.
- The append-only design is what makes the time-series possible (methodology K4: *"recompute the
  identical pre-launch metrics on fresh data"* and slice by import). Each import is a new
  `run_stamp`; `fixture_hash` distinguishes vintages; the rubric is held fixed (`rubric_version`)
  so a metric move is attributable to the *data*, not the grader.

> **The drift failure mode this guards (`NEXT-EVALS-PLAN.md` #5 / methodology K4).**
> **stale-but-green**: the bytes a citation points at are unchanged, but the surrounding meaning
> shifted, so a verbatim-true quote is now misleading. Verbatim re-check alone (`verify_result`)
> can't see this — it needs the **sampled support re-grade** (`support_result`, the judge), which
> is exactly why #5 depends on #1 being calibrated first. The `gate_log` carries both columns so
> the re-grade is recorded next to the verbatim check, not in a separate place.

---

## 8. Build order (80/20), and what it does NOT claim

Sequenced so each step is independently checkable and the cheapest guards land first. This slots
into `EVAL-SPEC.md` §5's existing order (G1–G6 + co-scoring are DONE; this is the harness/golden
layer above them).

1. **`fixture_hash` + `eval/golden/golden_set.jsonl` schema + the holdout split + `HOLDOUT.lock`
   + `eval/golden_check.py`** (offline, no-SDK). Freeze ≥2 non-Item-Management modules as holdout.
   *Cheapest, highest-leverage: it makes every later number attributable and leak-guarded.*
2. **Emit `gate_log` rows from `capability.py`** (the existing loop already produces `art` +
   `grade`; this adds the row writer and the provenance fields). No model logic changes.
3. **`eval/gate_log_score.py`** (offline scorer, oracle + degenerate-always-pass baseline that
   asserts the scorer, `missed_block_rate` gated). Mirror `judge_eval.py` structure exactly.
4. **Add the adversarial negatives** — `GOLD-wrongmodule-01` first (§6.3), then empty-AC and
   planted-conflict (the balanced should/should-not pairs `EVAL-SPEC.md` §2 specs as CAP-09/10/14).
   This is where the suite stops being one-sided.
5. **Enforce k ≥ 3 on `--profile ship`** and record the **first holdout `baseline.json` at k ≥ 3**.
   This is the moment the canonical layer has a real, comparable ship number for the first time.
6. **Defer / hand off:** the *judge-calibration* scoring of `support_result` (owned by
   `JUDGE-CALIBRATION-PLAN.md` #1 — build that scorer there), coverage `% covered` (#4, needs
   SME keypoint lists), and the drift time-series job (#5, runs on the next real pack import).

**What this backbone does NOT claim (the brutally-honest boundary):**

- It does **not** make the grounding gate prove **relevance**. G1/G2 stay invariants on `cell_d`
  (`graders.py:33,41`); a verbatim, correctly-tiered, *contextually-misleading* citation still
  passes the rubric (`STATE-OF-EVAL-2026-06-03.md` §5; `CLAUDE.md` "The gate proves provenance,
  not relevance or completeness"). The wrong-module negative makes that gap *visible and CI-red*;
  it does not close it. Closing it is #1/#2/#4 + the `match_tickets` module filter.
- It does **not** measure **coverage/omission**. The gate checks *emitted* citations, never what a
  guide omits (`NEXT-EVALS-PLAN.md` #4, `CLAUDE.md`). `must_cover` is wired but empty until SMEs
  fill it.
- The holdout is **cross-module but single-vintage** (all from one CSV import, §2.2). It is not an
  independent test of the capture/extraction step. A capture bug is correlated across all eight
  fixtures; a live-Jira or second-vintage pull is required for that independence.
- A green `pass^3` on the holdout is a **reliability** claim about the *generator on that frozen
  data*, not a learner-outcome claim. `NEXT-EVALS-PLAN.md` "When offline won't tell us": these
  gates *"cannot tell us whether a cashier actually learned"* — that is an online signal, available
  only with the real roster.

---

## Sources (verified by direct read, 2026-06-07)

- `eval/graders.py` — G1–G6, the fixed rubric; `_MIN_SECTIONS` (l.22), G1/G2 *"invariant: 0 by
  construction"* (l.33,41), `grade_all` (l.109-122), metric assignment (l.118).
- `eval/capability.py` — the existing harness; `_aggregate` pass@k/pass^k (l.57-88), `--trials`
  default 3 with *"≥3 for a real pass^k publish-gate reading"* (l.144), UTC stamp (l.156).
- `eval/pipeline.py` — `run_pipeline`; `integ = demo.validate_citations(html)` (l.65), `cost`
  (l.71), returned `art` shape (l.73-84).
- `eval/runs/20260603T183555Z/report.json` — the canonical run: `"trials": 2`, `"module": "Item
  Management"`, `total_cost_usd: 4.4297`, regression 15/15, the tldr G6 failure (words 877/794 vs
  ceiling 500).
- `qbank_gate.py` — the three ordered checks; `check_lane` (l.37), `check_verbatim` (l.46),
  `llm_support_judge` `{ok,reason}` (l.51), `gate_question` `{lane_ok,verbatim_ok,support_ok,
  verdict}` (l.77-105), `sys_prompt` for `judge_version` (l.54-61).
- `eval/judge_eval.py`, `eval/scope_eval.py` (and `eval/triage_cases.jsonl`/`triage_eval.py` per
  `EVAL-SPEC.md` §7) — the proven offline-scorer house pattern: jsonl dataset, load+validate,
  oracle + degenerate baselines asserting the scorer, FNR/FPR separation, single gated dangerous
  direction, `--live` exit-code gate.
- `docs/STATE-OF-EVAL-2026-06-03.md` — §1 (one happy path, no hill), §3 (k=2 underpowered,
  ~56 % by luck), §5 (wrong-module silent failure; *"proves verbatim and correctly-tiered … NOT
  about what the sentence claims"*), §6 (module filter ranked #1).
- `docs/NEXT-EVALS-PLAN.md` — item #6 (the backbone, *"nothing built yet"*, l.70-75), Component→
  metric table, Data discipline (*"k ≥ 3 … for any publish-blocking metric"*), #1/#2/#4/#5.
- `docs/eval-methodology-digest.md` — Theme E2 (pass^k math, Doc 2 p13 quote, *"measured run was
  k=2"*), Theme K1 (holdout, *"hash/lock the split"*), K4 (drift, recompute identical metrics on
  fresh data), Theme L (canonical/diagnostic ↔ regression/capability mapping), C01/C03/C04/F1.
- `docs/JUDGE-CALIBRATION-PLAN.md` — owns the judge metrics (item #1); §4.1 schema-bridge caveat,
  §2.1 boundary-probe relabel, the `provenance` slice; this doc references rather than re-derives.
- `data/demo/` — eight module fixtures present 2026-06-07 (account-management, accountability,
  eligibility, financials, insights, inventory, item-management, menu-planning), all
  `captured_at: "from-csv:Perseus Jira (…).csv"` (supersedes STATE-OF-EVAL's *"only
  item-management … is present"*).
- `learning-agent/CLAUDE.md` — Enforcement-vs-documentation (provenance not relevance/
  completeness); `raw/transcripts/` immutability (basis for `transcript_hash`).
