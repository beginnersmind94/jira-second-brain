# Learning Content Producer — Eval Suite Spec

> Designed via the `design-eval-suite` workflow, grounded in Anthropic's
> "Demystifying evals for agents" (Jan 2026) + the failures we measured across
> Cells A–D. The deterministic regression suite (`eval/regression.py`) is built
> and green (15/15). The rest (capability suite, harness, LLM graders) is specced
> below for build-out.

## 1. Agent-type framing
A **generative, customer-facing document agent**: transcript + Jira fixture → grounded HTML guide (long-form / micro-guide / tldr). Defining risk = **provenance fraud** (Tier-3 Description quote presented as Tier-1 Acceptance Criteria — the "cardinal sin", e.g. NXT-53316). Non-deterministic (calls `claude-sonnet-4-6`), so: **deterministic-first graders**, a **trial loop** (run N times), and **pass^k for anything publish-blocking**.

**Two generation paths, different eval semantics:**
- **`demo_single`** (`demo.py`, model types quote text): `tier_lie`/`quote_not_found` *can fire* — the cardinal sin lives here.
- **`cell_d`** (`demo_d.py`, model emits only `[CITE:id]`; `assemble()` renders verbatim span+tier from the registry): `tier_lie`/`quote_not_found` are **0 by construction** — on this path they're **invariants** (plumbing-intact assertions), not graders (model-skill measures). The only model-caused failure Cell-D surfaces is `invalid_cite_id`.

> **Anti-circularity rule:** never run `enforce_citations` inside the grading path — it mutates the artifact to pass (a built-in bypass). Grade the **raw** draft; test enforcement separately (REG-01).

## 2. Task bank (35 tasks)
- **Capability (22)** → pass@k ("can it ever"). Start at low pass-rate.
- **Regression (13)** → pass^k ("does it reliably never regress"). ≈100% bar. All deterministic, no SDK.
- **Balanced pairs** (tagged so a non-discriminating always-pass grader is exposed):
  - mark DESC-only claim `[TO VERIFY]` (CAP-10) **vs** don't hedge genuine-AC (CAP-11)
  - flag planted transcript-vs-Jira conflict (CAP-09) **vs** no phantom discrepancy on clean transcript (CAP-21)
  - use transcript specifics (CAP-08) **vs** drop un-citable specifics (CAP-14)
  - never emit `[[NXT:AC]]` for empty-AC ticket (CAP-20) **vs** DO cite RN where present (CAP-13)
  - enforce fixes a tier-lie (REG-01) **vs** enforce leaves correct cite byte-identical (REG-05)

## 3. Grader set
**Code-based (deterministic — the publish authority):**
- **G1 tier-lie** `validate_citations['tier_lie']` == 0 → pass^k
- **G2 quote-not-found** `['quote_not_found']` == 0 → pass^k (gate independently of G1; enforce leaves these)
- **G3 invalid-cite-id** `assemble` report + no literal `INVALID_CITE_ID` → pass^k
- **G4 grounding-density** `tokened >= ceil(_words/250)` AND `ok/tokened >= 0.9` AND `tokened > 0` → pass@k
- **G5 section/template-fit** `<h2>` vs `_FORMAT_SPEC`, count ≥ `min_sections`, no `[ERROR: section failed` → pass^k
- **G6 length/truncation** no `stop_reason=='max_tokens'`; `_words` vs `_FORMAT_BUDGET` (tldr≤500, micro≤1500, long≤6000) → both

Each grader returns `{passed, score∈[0,1]}`; trial passes iff all *required* graders pass; `partial_credit` = mean score (one truncated section of twelve ≈ 0.9, not 0).

**Model-based (ADVISORY ONLY — never gates publish):**
- **G7 semantic support** `evaluate_draft` checks (Citation spot-check, Source grounding, Unverifiable specifics) → pass@k
- **G8 transcript coverage/discrepancy** `evaluate_draft` Discrepancy + deterministic backstop (`transcript>=1`, regex for `[TO VERIFY]`/`blockquote.discrepancy`)
- **G9 voice/jargon** (human spot-check, tracked-only)

**pass@k vs pass^k:** grounding/hallucination/template graders (G1,G2,G3,G5,G6-truncation) → **pass^k** (publish-gated). Capability/voice/coverage (G4,G7,G8,G9) → **pass@k**. Default `trials: 3`; report both columns.

**Bypass mitigations:** co-score G1+G2+G4 as a unit (zero tier-lies because zero citations must FAIL); precondition `_FIX` set for same module AND `tokened>0 AND ok>0`; never enforce in grade path; on cell_d report G1/G2 as invariants (integrity alarm if non-zero); one ground truth (LLM grader reads the SAME fixture, never live Jira; deterministic gate always overrides; `verdict=='error'` is no-signal, not fail); reconcile `evaluate_draft` budgets with `_FORMAT_BUDGET`.

## 4. Harness design (`eval/`)
```
eval/__init__.py     # sys.path insert so import demo, demo_d survives cwd-reset  [DONE]
eval/regression.py   # REG-01..15, deterministic, no SDK, exit-code gate          [DONE — 15/15 green]
eval/fixtures.py     # load_module_fixture(module) sets demo._FIX; fixture_lock    [TODO]
eval/pipeline.py     # ~40 lines: re-sequence run_cell_d STAGES to RETURN artifacts (no side-effect writes)  [TODO]
eval/tasks/*.yaml    # capability tasks                                            [TODO]
eval/graders.py      # G1–G6 registry (+ co-scoring, preconditions)               [TODO]
eval/runner.py       # run_task -> trials -> grades; fresh registry+semaphore per trial  [TODO]
eval/aggregate.py    # pass@k / pass^k / partial-credit / BROKEN_TASK flag (pass@k==0)    [TODO]
eval/report.py       # runs/<id>/report.{json,html} + per-claim evidence table     [TODO]
```
Isolation: only shared mutable state is `demo._FIX` (lock-guarded around the fast swap+deterministic window; slow generation runs unlocked). `pipeline.py` reuses every stage function verbatim and omits the `DRAFTS/` side-effect writes so trials don't collide. Exit non-zero iff any **regression** task has `pass^k==0`; capability misses are non-blocking.

## 5. What to build next (80/20 order)
1. ~~`eval/__init__.py` + regression suite~~ **DONE.**
2. `eval/fixtures.py` + `eval/pipeline.py` (+ smoke test: pipeline `integ` matches a `run_cell_d` run).
3. Deterministic graders G1–G6 + co-scoring + `tokened>0 AND ok>0` precondition.
4. 3 balanced capability tasks on a real transcript (CAP-01/03 demo_single; CAP-02/05/06 cell_d) + corpora negatives (no-backing-ticket → should-cut; planted-conflict → should-flag; clean → should-not-flag).
5. `aggregate.py` + `report.py` with the per-claim evidence table + `pass@k==0` broken-task flag.
6. **Defer:** G7/G8 (LLM, advisory), G9 (human), saturation watcher, full 22-task set. Wire `--no-llm-grader` from day one.

## 7b. Scope-resolution eval (intent-and-scope front end)

The "describe what you need" agent's dangerous error is the DP9 failure — confidently resolving a request to the **wrong module** (or grounding a not-built area onto a present module). Mirroring the triage FNR, the **wrong-module rate is the gated metric**; over-asking/over-refusing is friction (tracked).

**Built:** `eval/scope_cases.jsonl` (18 balanced cases: 9 module / 4 ambiguous / 5 no-fixture) + `eval/scope_eval.py` (deterministic scorer; offline oracle + degenerate "always pick a module" baseline that scores ~94% wrong-module; `--live` gates on `--wrong-gate`, default 0). **Live baseline (k=1, 18 cases): 0% wrong-module, 0% friction, 100% accuracy** — resolved all module cases, asked on all ambiguous, refused all not-built areas (Family Hub / Mobile POS / Production declined, not mapped to a present module). TODO: real-traffic cases (mine `logs/review-decisions.jsonl` `action:intent_resolve`), multi-turn (the eval scores single-turn resolution), and a larger/k≥3 run.

## 6. Open calibration questions
1. G4 density floor (`_words/250`) and G7/G8 0.9 thresholds are asserted, not derived — calibrate from a baseline distribution.
2. Cell-D registry circularity: grading registry tier-assignment needs an independent ground-truth field map separate from `_FIX`; until then the `demo_single` path is the only place tier-assignment is genuinely tested.
3. `evaluate_draft` needs a fixture-backed `read_ticket` (eval mode) — `tools_sdk.py` currently hits live Jira; G7 unreliable once Jira drifts past `captured_at`.
4. Need a labeled calibration corpus (known-good + known-defect drafts) to measure the LLM grader's false-pos/neg per release; gate trust at ≥90% agreement on tier-lie cases.
5. Only `item-management-fixture.json` exists — a second module fixture is needed for cross-module tasks.
6. Confirm whether `demo_single` quote-typing is still live; if dead, the cardinal-sin capability signal is constructed-HTML only (REG-01/02/03).
7. Edit-triage classifier (sec 7): dataset (24, synthetic) + deterministic FPR/FNR scorer are **built**; still need a `--live` calibration run to record a baseline FNR, **real** reviewer-edit cases (not just synthetic), and the two-stage fast-filter optimization.

## 7. Edit-triage classifier (review-gate router) — its own balanced eval

The human-review gate adds an **edit-triage classifier**: after a reviewer requests an AI-assisted edit, it tags the change `stylistic` (wording/format — fast-path to approve) vs `substantive` (a cited claim/quote/tier/number/label/step may have changed — read closely). It is a **router, not a grader, and advisory only** — the deterministic grounding gate re-runs after *every* edit regardless, so the classifier can never weaken grounding; at worst it routes a safe edit for an extra (free) check.

It still needs its **own eval**, because the live risk (per "Demystifying evals") is **over/under-triggering**:
- **Under-trigger** (calls a substantive edit `stylistic`) is the dangerous direction — it lets a changed claim fast-path. Target: near-zero. Treat as the publish-blocking-direction metric.
- **Over-trigger** (calls a stylistic edit `substantive`) only costs an extra check — track it as a cost/latency signal, not a failure.

**Balanced set (~20–50 real edits), tagged so a degenerate always-`substantive` classifier is exposed:**
- reword intro / fix typo / reorder bullets / tighten prose → **should be `stylistic`**
- change a number, field label, menu path, or step; add a new sentence about behavior; insert a `[TO VERIFY]`; alter text adjacent to a citation → **should be `substantive`**
- the always-`substantive` baseline must score 0 on the stylistic half (catches no-discrimination).

**Graders:** deterministic confusion-matrix over the labeled set (under-trigger rate = primary, gated; over-trigger rate = tracked). Run as its own task family in `eval/` with the same trial loop + pass-consistency + latency/cost logging as the guide suite. The grounding-gate re-run is a separate deterministic check (already G1–G3) and is the real safety net — the classifier eval measures routing quality, not grounding.

**Built (2026-06-04):** `eval/triage_cases.jsonl` (24 balanced cases, clearly-labeled) + `eval/triage_eval.py` (deterministic scorer, separate FPR/FNR, gated on FNR). Offline mode validates the dataset + scorer via an oracle and the two degenerate baselines (always-`substantive` → FNR 0 / FPR 1; always-`stylistic` → FNR 1 / FPR 0) with **no SDK**: `python -m eval.triage_eval`. `--live` scores the real `revise.build_triage_*` classifier and exits non-zero if `FNR > --fnr-gate`. The router was also made **reasoning-blind** — it judges the before→after diff, not the reviewer's stated intent (e.g. "make it punchier" that flips a conditional to absolute).

**Still TODO:** (a) `--live` calibration run + record a baseline FNR/FPR; (b) collect **real** reviewer edits from `logs/review-decisions.jsonl` (every applied/refused/no-change decision is now logged with instruction + ops + triage verdict — mine these into labeled cases; all 24 current cases are synthetic, flagged in the runner output); (c) the **two-stage classifier** optimization — a fast single-token stylistic/substantive filter that errs toward `substantive`, with chain-of-thought reasoning only on what it flags (keeps latency off the common stylistic path). Sequence: live-calibrate first, then add two-stage, then the end-to-end live demo run.

**Source (verified by direct read):** Anthropic, *How we built Claude Code auto mode: a safer way to skip permissions* (Mar 2026) — model-based approval classifier with a human backstop; report **FPR (needless friction) and FNR (dangerous misses) separately**, weight toward FNR (theirs ~17% on real overeager actions, and explicitly "not a drop-in replacement for careful human review"); two-stage fast-filter-then-reason; reasoning-blind design (judge what was done, not what was argued). Directly mirrors this router's advisory-with-deterministic-backstop posture.
