# Eval next-steps build index

*Everything produced in the eval build-out run that followed `NEXT-EVALS-PLAN.md`: each
artifact with its path, what it delivers, and a verification verdict; what is now runnable
vs. design-only; what is still TODO; and the prioritized sequence to finish. Companion to
`docs/EVAL-GAP-AUDIT.md` (the honest principle-by-principle status) and `STATE-OF-EVAL-
2026-06-03.md` (the measured scorecard). Tone matches both: verdicts are earned, not awarded.*

> **Scope of "verified" in this doc.** Verdicts below were established by running the
> deterministic, **SDK-free** paths (offline self-checks, ad-hoc validation against the real
> `qbank_gate` deterministic functions) and by direct source reads. **No `--live` path was
> run** (those need Claude SDK auth, intentionally out of scope this run). So every verdict is
> either "offline-verified" (a stdlib check actually executed) or "design-only / live-pending"
> (correct on inspection but its gated number is unmeasured). Nothing here claims a live judge
> agreement number.

---

## 1. Files produced this run

### `eval/judge_gold_set.jsonl` — semantic-support judge gold set (roadmap #1)
**Delivers:** 32 hand-authored `(quote, stem, answer, ground_truth_support, defect_type,
rationale, lane, source_anchor)` cases for calibrating `qbank_gate.llm_support_judge`. Balanced
**15 supported / 17 unsupported**; defects **inversion 4 / number_swap 4 / over_claim 5 /
wrong_answer 4**. Each unsupported trap is paired with a genuine supported control so an
always-"supported" rubber-stamp is exposed. Quotes grounded in real ICN food-safety /
menu-planning workbooks and NXT demo fixtures (spot-checked verbatim against source files per
the project's read-the-source rule).
**Verdict: offline-verified, valid data.** `python -m eval.judge_eval` parses all 32 lines,
oracle scores FNR/FPR=0, both degenerate baselines assert correctly (always-supported →
FNR=100%; always-unsupported → FPR=100%). Round-trips through `json.loads`.
**Caveats (honest):** some compliance `source_anchor` page numbers are approximate / `p~`
placeholders — the **quotes** verify but the page citations are loose (fine for a judge eval,
which shows the judge quote+stem+answer, not the anchor; do **not** propagate these anchors as
authoritative citations). Two product cases (`c06`/`c06b`) are deliberately tricky
quote/answer-mismatch boundary probes the author labeled "supported" — kept as-is; reviewers
should expect them to be the judge's hardest calls.

### `eval/judge_eval.py` — deterministic FNR-gated judge scorer (roadmap #1)
**Delivers:** the scorer for the gold set, mirroring the `triage_eval.py` / `scope_eval.py`
house pattern (argparse shape, `sys.path` shim, oracle + two degenerate baselines offline,
`--live` mode, separate FNR/FPR, exit-code gate). FNR = (#unsupported judged supported) /
(#unsupported) is the **gated** metric (`--fnr-gate 0.0`); FPR is tracked-only. Offline path is
stdlib-only (no SDK/no auth); `--live` runs the real `qbank_gate.llm_support_judge`.
**Verdict: offline-verified, runnable.** Offline self-check passes end-to-end (run above).
`--live` is **live-pending** — needs SDK auth; the gated FNR is therefore **not yet measured**.

### `eval/lane_purity_cases.jsonl` — cross-lane adversarial battery (roadmap #2)
**Delivers:** the 5-case fixture grown to **31 data cases + 1 header `_comment`** (32 non-blank
lines): cross_lane 23 / same_lane_positive 6 / same_lane_control 2. Shared-vocabulary coverage
(item/temperature/hold/save/production/menu), balanced cross-lane direction, and hard near-misses
beyond plain prefix mismatch (a product span literally containing "135 degrees" copied from the
food-safety domain; mislabel traps where the span's declared lane disagrees with its id prefix;
an invalid lane; a span_id with no `:` prefix). All spans **synthetic, clearly labeled** in the
header; schema matches `data/qbank/adversarial_fixture.json` so
`gate_question(case['question'], {s['span_id']: s for s in case['spans']})` runs unchanged.
**Verdict: offline-verified data, NO runner.** Validated against the **real** `qbank_gate`
deterministic functions: 31 cases parse, **`leak_rate=0.000`** (0/23 cross-lane cases accepted
by `check_lane`), all 6 same_lane_positive cases pass lane **and** verbatim. The data is sound.
**The committed runner `eval/lane_purity_eval.py` does not exist** — this is design-only as a
repeatable gate.
**Caveat (must-fix, found by direct read):** the span_id `compliance:icn-fs:p12:01` maps to
**two different verbatim texts** across files that share the convention — `"Hot foods must be
held at 135°F or higher to remain safe for service."` in `data/qbank/adversarial_fixture.json`
vs. `"Hot foods must be held at 135 degrees Fahrenheit or higher to remain safe for service."`
in this battery. It does **not** affect `leak_rate` (lane reads only the id prefix), but it
breaks the "one canonical id → one verbatim text" invariant and would corrupt any future
verbatim check that resolves this id against the fixture. Fix before wiring a runner.

### `eval/triage_cases_additions.jsonl` — triage balanced-set additions (roadmap #3)
**Delivers:** 6 new cases (3 stylistic STY-13/14/15, 3 substantive SUB-13/14/15) extending the
boundary axes the existing 24 didn't cover: conditional→absolute (SUB-13), new-unsourced-claim
(SUB-14), statistical-outlier number (SUB-15), low-confidence over-trigger (STY-13),
sensitive-topic (STY-14), non-sequential reorder (STY-15). All use `find`/`replace` ops so they
run live unchanged; all tagged `source:"synthetic"`.
**Verdict: offline-verified, valid data — sidecar, not yet merged.** Merging into
`triage_cases.jsonl` yields **30 cases, balanced 15/15** (verified); every addition carries
`find`/`replace` ops (verified). Held in a **sidecar** per the never-overwrite rule.
**To activate:** append to the canonical set —
`Get-Content eval\triage_cases_additions.jsonl | Add-Content -Encoding utf8 eval\triage_cases.jsonl`
(PowerShell) — then re-run `python -m eval.triage_eval` (offline oracle + baselines are the merge
regression guard). **On merge, update the stale "24 balanced cases" count in `CLAUDE.md` and
`EVAL-SPEC.md` §7 / §7.7 → 30.**

### `docs/EVAL-GAP-AUDIT.md` — consolidated honest gap audit (this run)
**Delivers:** principle-by-principle (C01–C09) status across guide / lane / triage /
judge-calibration / coverage areas, the dangerous direction per principle, a per-principle×area
status matrix, and an explicit "where a green gate is still wrong" ranking.
**Verdict: complete.** Statuses checked against code by direct read; doc-vs-code drift on
`match_tickets` flagged and corrected.

### Reference & design docs also produced this run
- `docs/eval-methodology-digest.md` — the quote-backed methodology checklist (C01–C18) distilled
  from the two Anthropic eval references; the contract the gap audit grades against.
- `docs/JUDGE-CALIBRATION-PLAN.md` (roadmap #1) — protocol to calibrate `llm_support_judge`
  against the gold set (labeling, FNR gate, threshold tuning, holdout, k≥3). **Design-only / live-pending.**
- `docs/EVAL-COVERAGE-METHOD.md` (roadmap #4) — coverage/omission method + a 12-keypoint sample
  list for `temperature-danger-zone` (verbatim ICN-sourced). **Design-only, no runner.**
- `docs/EVAL-DRIFT-METHOD.md` (roadmap #5) — bank-freshness re-grade method ("% still true",
  end-state not byte-hash). **Design-only, no runner.**
- `docs/EVAL-HARNESS-GATELOG-DESIGN.md` (roadmap #6) — held-out golden set + pass^k at k≥3 + a
  concrete `gate_log` schema. **Design-only.**

### `docs/EVAL-NEXT-STEPS-BUILD.md` — this file.

---

## 2. Runnable now vs. design-only

**Runnable now (offline, no SDK/no auth — these execute on every commit):**
- `python -m eval.judge_eval` — gold-set + scorer offline self-check (oracle + 2 baselines). ✅
- `python -m eval.triage_eval` — triage offline self-check; same after the additions are merged. ✅
- `python -m eval.scope_eval` — pre-existing scope-resolution offline self-check. ✅
- `python -m eval.regression` — pre-existing 15/15 deterministic guide regression gate. ✅
- Ad-hoc lane validation against real `qbank_gate.check_lane`/`check_verbatim` (leak_rate=0). ✅
  *(ad-hoc only — not yet a committed `-m eval.lane_purity_eval`.)*

**Live-pending (built and correct, but the gated number is unmeasured — needs SDK auth):**
- `python -m eval.judge_eval --live` — records the support judge's real FNR/judge↔human
  agreement. **Until this runs, the support judge is uncalibrated and not cleared to gate.**
- `python -m eval.triage_eval --live` — records the triage classifier's real FNR (today a
  **k=1, temperature-unset** single draw — see TODO #2).

**Design-only (no runner exists):**
- **Lane-purity gate** `eval/lane_purity_eval.py` — data exists, runner does not.
- **Coverage/omission** (roadmap #4) — method + a 12-keypoint sample list documented
  (`docs/EVAL-COVERAGE-METHOD.md`); no scorer/runner and no per-topic lists beyond the sample yet.
- **Drift / bank-freshness** (roadmap #5) — method documented (`docs/EVAL-DRIFT-METHOD.md`); no runner.
- **Canonical harness + `gate_log`** (roadmap #6) — designed (`docs/EVAL-HARNESS-GATELOG-DESIGN.md`);
  k still 2 in the only measured run.

---

## 3. Still TODO (prioritized)

Ordered by *how silent the failure it closes is* — the quietest green-but-wrong first.

1. **Wire lane purity into the production curation path AND ship `eval/lane_purity_eval.py`.**
   *Highest priority — this is the most dangerous green light in the suite.* `check_lane` is
   correct but `qbank_curation.score_candidate`/`commit_to_bank` and `commit_gate_hook` never
   call it (they gate on `support_ok`/`confidence`/`topic`/`status`); the leak guarantee lives
   only in a 5-case test + a throwaway script. (a) Add a lane re-derivation to the committable
   path (or make `support_ok` insufficient without a passed lane check). (b) Build the offline
   runner: load the battery, run `check_lane`/`check_verbatim` deterministically, assert
   `leak_rate==0` over the 23 cross-lane cases and lane+verbatim pass on the 6 positives; add a
   `--live` mode for the 7 judge-dependent cases with an **injectable/stub judge** so the
   same-lane positives are checkable offline. (c) Fix the `compliance:icn-fs:p12:01`
   span_id/text collision (one id → one verbatim text). (d) Correct the header so it does not
   imply `test_qbank_gate.py` loads this file (it does not), and define `expected_gate`
   precisely (`refuse` = failed the deterministic lane check; `accept` = passed lane regardless
   of later verbatim/support) so the `SL-CTL-01/02` labels aren't ambiguous.

2. **Add a trial loop + determinism controls to triage, then run `--live` to record a defensible
   FNR.** Set `effort`/temperature/seed on `revise.build_triage_options` (it sets none today,
   unlike the edit agent's `effort="medium"`), add a `--trials` loop to `predict_live` (k=1
   today), and aggregate FNR as pass^k with **k≥3**. A green `FNR=0` at k=1 against a
   non-deterministic classifier is statistically indefensible and is the exact number a reviewer
   trusts to keep the router advisory-safe.

3. **Run `python -m eval.judge_eval --live` and record the support judge's FNR / judge↔human
   agreement.** The gold set + scorer are built; the *measurement* — the thing that actually
   calibrates the judge and clears it to gate publish — has not happened. Until it does, "gold
   set built" must not be read as "judge calibrated." Raise k≥3 here too for the live path.

4. **Build the coverage/omission runner (roadmap #4).** The method + a 12-keypoint sample list
   now exist (`docs/EVAL-COVERAGE-METHOD.md`); the *scorer* does not. The single unmeasured blind
   spot that makes a green dashboard most misleading: every grader scores *emitted* citations (G4
   density); none scores what the output *omits*. Remaining: SME-authored keypoint lists per topic
   + a scorer that measures % of keypoints covered by a generated quiz/guide. Pairs with #5.

5. **Build the should-NOT generation tasks (CAP-09/CAP-10/CAP-14, `EVAL-SPEC.md` §2).** The
   generation capability suite runs no negative task; the correct answer "withhold and raise an
   Open question" is never tested, and G4 actively rewards over-citing. These exercise model
   judgment and will start well below 100% (a real hill to climb).

6. **Give every LLM judge an `Unknown`/abstain escape.** `llm_support_judge` forces strict
   YES/NO (qbank_gate.py:60); triage forces `stylistic`|`substantive`. Add an
   insufficient-evidence verdict (mapped to the safe side for gating) so a borderline case can
   abstain instead of fabricating a confident grade. Low effort, closes C06.

7. **Merge the triage additions + fix stale counts** (24→30 in `CLAUDE.md` and `EVAL-SPEC.md`).
   Mechanical; do it alongside #2.

8. **Raise the guide suite to k≥3 and stand up the canonical harness + `gate_log` (roadmap #6).**
   The only measured run is k=2. The harness makes #1–#5 rerunnable on every change and is the
   backbone the rest hangs off.

9. **Drift / bank-freshness runner (roadmap #5)** and **mine real cases** to replace synthetic
   ones in the triage / judge / lane sets (all synthetic today, correctly flagged). Lower
   urgency but required before any of these gates is trusted on real traffic.

**Suggested sequence:** #1 (lane wiring + runner) → #2 (triage trials) → #3 (judge `--live`) →
#7 (merge/counts, trivially alongside #2) → #4+#5 (coverage + should-not, the generation gap) →
#6 (abstain) → #8 (k≥3 + harness) → #9 (drift + real data). #1–#3 convert the three most
indefensible green lights into measured gates; #4–#5 close the coverage blind spot; #8 makes it
all repeatable.

---

## 4. Eval-expert brief addendum — summary of what changed

*For appending to `~/Downloads/Learning-Studio-eval-context.md`. This run executed
`NEXT-EVALS-PLAN.md` items #1–#3 (data + scorers) and produced a consolidated gap audit.*

**Built and offline-verified this run:**
- **Roadmap #1 (semantic-support judge) is now built, not just planned.** A 32-case
  human-authored gold set (`eval/judge_gold_set.jsonl`, balanced 15/17, four defect families
  with paired supported controls) + a deterministic FNR-gated scorer (`eval/judge_eval.py`,
  same house pattern as triage/scope). Offline self-check passes (oracle FNR/FPR=0; degenerate
  baselines assert). **The single largest gap the methodology digest flagged — "no calibration
  set, no measured judge↔human agreement" — now has its ruler.** The *measurement* (`--live`
  FNR) is still outstanding; the judge is **not yet calibrated/cleared to gate**.
- **Roadmap #2 (lane-purity battery)** grown 5→31 cases (23 cross-lane / 6 positive / 2 control),
  validated against the real deterministic gate: **`leak_rate=0.000`**, positives pass
  lane+verbatim. Data is sound.
- **Roadmap #3 (triage balanced set)** extended +6 to a balanced 30 on new boundary axes;
  offline merge regression guard passes.

**What the gap audit surfaced (the parts that change the eval-expert's risk picture):**
- **The lane guarantee is fixture-deep, not path-deep.** `check_lane` is correct, but the
  production bank-writing path (`qbank_curation`, `commit_gate_hook`) never calls it — the
  leak-rate-0 guarantee is a property of a unit test + a throwaway script. **This is the most
  dangerous green light in the suite** and is now TODO #1.
- **pass^k is missing in all three live areas (C07):** guide suite still k=2; triage is k=1
  against a temperature-unset classifier; the judge/lane `--live` paths have no trial loop. A
  green FNR at k=1 is indefensible.
- **Coverage/omission (roadmap #4) remains entirely unbuilt (C09)** and the **should-not
  generation tasks (C08, CAP-09/10/14) remain TODO** — together, the suite rewards citing and
  never penalizes omitting or "helpful-yes" over-citing.
- **No judge has an abstain escape (C06):** `llm_support_judge` forces YES/NO. The binary
  collapses to the safe side on *errors*, but a genuinely ambiguous case is still forced.
- **Doc-vs-code drift corrected:** `STATE-OF-EVAL` §5's in-fixture wrong-module lexical-leak
  claim is superseded — `demo.match_tickets` now filters by module (demo.py:206–208). The
  wrong-module silent failure now needs the narrower preconditions (no/mis-captured fixture),
  not generic word overlap inside a loaded fixture. Audit against code, not the older report.

**Net:** the trust story's linchpin (the support judge) now has a built, balanced, offline-green
calibration harness; three roadmap data sets exist and validate. The suite is materially
stronger on *judge method* and *balanced data*, and materially unchanged on *statistical power
(k)*, *coverage*, and *the lane guarantee's reach into production* — which are now the top three
TODOs.
