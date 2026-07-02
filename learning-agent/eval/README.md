# `eval/` — what belongs here (and what doesn't)

There are three distinct things. Keep them straight — conflating them is what caused a
deterministic roster-arithmetic test to get treated as an "AI eval."

## 1. The deterministic grounding gate — the machine floor
`regression.py` (REG-01..16) · run: `python -m eval.regression`

Deterministic **by design**, and that's the point: the content pipeline grounds by
construction (the writer can't type a quote or tier; `citation_gate.run_gate` +
`demo.validate_citations` verify verbatim spans + coverage). So grounding's "eval" is a
pass/fail **gate**, not a judge. This is a strength, not a smell.

## 2. Model-graded evals — the real "is the generation good?"
These grade **non-deterministic model output**. Most need a live model / API key:
`capability.py`, `judge_eval.py`, `source_faithfulness.py`, `source_quality.py`,
`quiz_reliability.py`, `quiz_qa_agent.py`, `scope_eval.py`, `triage_eval.py`,
`coverage.py`, `scoring.py`, `report.py`, `graders.py`, `pipeline.py`
(+ `*.jsonl` gold sets, `EVAL-SPEC.md`, `EVAL-WIKI-IMPL.md`).

## 3. Deterministic content/grounding tests — pytest, keyless, belong with the gate
`test_overreach.py` (coverage gate), `parity.py`, `coverage_report.py`,
`test_provenance.py`, `test_grounding_audit.py`, `test_builder_beats.py` (grounding-refusal
demo), `test_model_pinning.py` (pins the pipeline's model ids).

---

## What is NOT an eval and now lives in `tests/`
Deterministic unit/integration tests of the **LMS / district platform** — course store,
assignments, certificates, rosters, My Team, gamification, insights, quiz/flashcard stores,
stat overlays, onboarding, what's-new/next, completion mechanics, etc. — were moved to
`tests/` on 2026-07-02. They assert platform *code* behavior, not what the AI generates, so
they are **not evals**. (`tests/` was made a package — `tests/__init__.py` — so moved files
namespace as `tests.*` and don't collide with repo-root `test_*.py`, e.g. `test_assignments.py`.)

**Rule of thumb:** grades model output quality, or is the grounding gate/its tests → `eval/`.
Asserts deterministic platform behavior → `tests/`.

## Running each bucket
```
python -m eval.regression       # 1: grounding gate (deterministic, keyless)
python -m pytest eval/ -q        # 3: keyless content/grounding tests
python -m pytest tests/ -q       # platform unit tests (not evals)
#   2: model-graded evals need a key — see EVAL-SPEC.md
```
