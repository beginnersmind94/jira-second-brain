# EVAL-WIKI → repo implementation map

How the conceptual eval wiki (`docs/EVAL-WIKI.md`) maps onto the **real** files in this
repo, how to run each, and where the repo's artifacts differ from the wiki's names. Read
`docs/EVAL-WIKI.md` first for the *why*; this file is the *where* and *how-to-run*.

Everything here is **stdlib-only** and **offline by default** — no Claude SDK, no model
calls, no server. Each module ships an in-module offline self-test (oracle + degenerate
baselines + exit-code gate) in the house style of `eval/triage_eval.py`. All fixtures
under `data/qbank/` are **SYNTHETIC** (labeled per-row); they prove the graders' wiring,
not real safety. Real SME-owned fixtures come later (wiki §7, §11.1.1, §11.2.1).

---

## Real-artifact remappings (wiki §0 "real-artifact wins")

The wiki names some artifacts that the repo spells differently or doesn't have. Per wiki
§0, **the real artifact wins** — the doc is remapped to the code, and the mismatch is
logged here:

| Wiki name | Real repo artifact | Note |
|---|---|---|
| `evals/` (package, §14.1) | **`eval/`** (singular) | The Python package is `eval/`. All run commands are `python -m eval.<mod>`. |
| `tests/evals/test_*.py` (§14.1) | **in-module offline self-tests** | There is no separate `tests/evals/` tree. Each grader's `python -m eval.<mod>` (no args) runs an oracle + degenerate-baseline self-test that asserts the metric semantics — the §12.2 "minimum test cases" live inside the module, not in a sidecar test file. |
| `data/qbank/...` fixtures | **`data/qbank/...`** | Exact match — no remap. |
| `gate_log` (§0, §10.1, §9.6) | not present in this repo | Referenced as a future artifact; the offline scorers read fixtures, not a live gate log. |
| §14.3 "Broken citation rate" line | **no fixture / grader** | The §8.3/§12.3 citation-verifiability grader is **unbuilt**; `eval/report.py` prints this line as `n/a (no fixture)` rather than fabricate a number (§0 + cite-or-cut). |

`eval/scoring.py` and `eval/coverage.py` both carry this remap note in their own module
docstrings as well, so it is visible at the point of use.

---

## Section → file map

| Wiki section | Real file | What it implements |
|---|---|---|
| §10 "Reference implementation — scoring layer" (§10.1–§10.6) | `eval/scoring.py` | Trial-log scorer over `judge_run.jsonl`: headline should-FAIL **FN rate**, FN-by-gate and FN-by-neg_class diagnostic slices, **pass^k vs pass@k** (k≥3), and the two abstention rates. No model calls — the judge is an *input* here. |
| §11.1 / §13.1 Coverage grader | `eval/coverage.py` | Required-facts-present %, P0/P1 per-guide-type thresholds, partial credit, the hard rule **any missing P0 → DRAFT**. |
| §11.2 / §13.2 Source-quality grader | `eval/source_quality.py` | Authority-tier lookup, per-claim then per-guide average authority (0–5), the §4.5.6 low-authority-when-better-existed flag, strict gate (any flag OR avg < `MIN_AUTHORITY` → DRAFT). Deterministic; no model path. |
| §14.3 "Dashboard rollup Jaime should see" | `eval/report.py` | **This task.** Imports the three layers above and prints the §14.3 dashboard lines in order: FN rate [n/N], pass^3, confabulation rate, over-refusal rate, coverage P0/P1, authority /5, guides in DRAFT, top draft reasons, broken-citation rate. Display-only (exit 0); `--gate` makes it fail on FN rate. |
| §3 semantic-support **judge** (the gold-set judge it scores) | `eval/judge_eval.py` *(pre-existing)* | Gold-set judge scorer: FNR/FPR on the `supported`/`unsupported` class, with a `--live` path that calls the real judge (`qbank_gate.llm_support_judge`). See "scoring.py vs judge_eval.py" below. |
| §1/§4 three gates; edit-triage classifier | `eval/triage_eval.py` *(pre-existing, the template)*, `qbank_gate.py` | `triage_eval.py` is the house-style template all the new modules mirror. Lane/verify/support gating lives in `qbank_gate.py` (exercised by `data/qbank/adversarial_fixture.json`). |

---

## How to run each (all offline, stdlib, no SDK)

Run **from the `learning-agent/` directory** so `python -m eval.<mod>` resolves the package:

```bash
# Dashboard rollup (this task) — §14.3. Always exit 0 (display); --gate to fail on FN.
python -m eval.report
python -m eval.report --gate            # exit 1 if headline FN rate > --fn-gate (default 0.0)

# The three single-dimension layers the rollup reads (each: offline self-test, exit 0):
python -m eval.scoring                  # §10 scorer — oracle + known-FN + <k warning
python -m eval.coverage                 # §11.1 coverage — oracle + degenerate baselines
python -m eval.source_quality           # §11.2 source-quality — oracle + degenerate baselines

# Pre-existing judge scorer (offline self-test, exit 0):
python -m eval.judge_eval

# Release-gate modes (exit non-zero when a real fixture fails a gate):
python -m eval.scoring --run data/qbank/judge_run.jsonl --fn-gate 0.0
python -m eval.coverage --gate-on
python -m eval.source_quality --live
```

**Last verified run (synthetic fixtures, this session):** every self-test exits **0** —
`eval.coverage`, `eval.source_quality`, `eval.scoring`, `eval.report`, and the
pre-existing `eval.judge_eval`. `eval.report --gate` exits **1** by design, because the
synthetic `judge_run.jsonl` contains one engineered should-FAIL leak (FN rate 6.7%) —
that is the rollup correctly surfacing the dangerous direction, not a wiring failure.

---

## `scoring.py` vs `judge_eval.py` — two different layers, do not unify

Both touch the **same dangerous event** — `gold = FAIL`, `judge = PASS` (a bad claim
waved through, wiki §3) — but at different granularities and off different inputs:

| | `eval/judge_eval.py` (§3 judge) | `eval/scoring.py` (§10 scorer) |
|---|---|---|
| **Input** | `judge_gold_set.jsonl` — one row per item, `ground_truth_support` ∈ `supported`/`unsupported` | `judge_run.jsonl` — one row per **trial**, k≥3 trials/item, `gold_label`/`judge_label` ∈ `PASS`/`FAIL`/`ABSTAIN` × `PASS`/`FAIL`/`UNKNOWN` |
| **Calls a model?** | Yes in `--live` (calls `qbank_gate.llm_support_judge`); offline self-test does not | **Never** — the judge's verdicts are an *input*; this layer only re-scores a log |
| **Measures** | the judge's *discrimination* on one trial each (FNR/FPR on the `unsupported` class) | what a single-trial scorer cannot: FN **slices** (by gate, by neg_class), **pass^k vs pass@k** consistency, and the two **abstention** rates |
| **Headline** | FNR on `unsupported` | FN rate on should-FAIL |

So: `judge_eval.py` answers *"is the judge good enough?"* (and can run the real judge).
`scoring.py` sits one layer up and answers *"across many trials, is the system
consistent and where is it leaking?"* — purely from the logged verdicts. Their schemas
**deliberately differ** (`judge_gold_set.jsonl` ≠ `judge_run.jsonl`); do not merge them.
`eval/report.py` reads `scoring.py` (the trial-log layer) for its headline FN/pass^k/
abstention lines.

---

## The §8/§11.3 "do not merge" rule, as built

Coverage (§11.1) and source-quality (§11.2) are **independent single-dimension graders**.
Neither touches the §10 should-FAIL scorer, and `eval/report.py` does **not** fold them
into a composite score — it lays their already-separate numbers side by side and reports
each gate's DRAFT decisions independently (coverage holds for missing P0; source-quality
holds for a flagged low-authority citation or avg authority below the SME floor). A guide
in DRAFT shows *which* gate held it. This mirrors wiki §11.3: partial credit is reported
for diagnostics, never as a bypass; each dimension forces DRAFT on its own.

---

## Cross-references

- `docs/EVAL-WIKI.md` — the conceptual wiki this file maps (sections cited throughout).
- `eval/triage_eval.py` — the house-style template (offline self-test shape) all new modules mirror.
- `eval/scoring.py`, `eval/coverage.py`, `eval/source_quality.py` — the three layers `eval/report.py` rolls up; each carries its own §-cited docstring and the §0 remap note.
- `data/qbank/{judge_run,coverage_fixture,source_fixture}.jsonl` — the synthetic fixtures (labeled per-row); replace with SME-owned data before quoting any dashboard line (§7).
