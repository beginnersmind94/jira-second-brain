# STORY-004 — Eval coverage for the two-version split

**Status:** `Done ✓` (2026-07-02)  ·  **Points:** 2  ·  **Persona:** platform maintainer / eval owner
**Depends on:** STORY-001 (`run_gate`), STORY-002 (coverage layer), `eval/regression.py` (baseline).
**Epic:** [Two-version Citations-API grounding](EPIC.md)

## Scope
**In scope:** `eval/test_overreach.py` (proves the capability B adds over A); `eval/parity.py` (B never
fails a clean draft A passes); `eval/coverage_report.py` (informational, keyless, fixture-free — shows
how the coverage layer scores real drafts).
**Out of scope:** a live Version-B pass@k eval (needs a key — belongs with STORY-003); an LLM-judge
eval; changing REG-01..16 (they stay the substring authority, unchanged).

## Requirements
1.1 `test_overreach.py`: in `both` mode a draft with one cited + one uncited claim → `passed False`,
`uncited_claims ≥ 1`; in `substring` mode the same draft → `passed True, citations None`.
1.2 `parity.py`: on hand-built KNOWN-clean drafts (every claim cited), `both` mode must not fail
anything the substring layer passes; exits 0 iff `divergences == 0`.
1.3 `coverage_report.py`: prints `uncited / total` claim blocks per draft, calls **only** the coverage
layer (`_uncited_claim_blocks`) so it needs no fixture and no key; always exits 0 (informational).

## Edge / Empty / Error
| Case | Behavior |
|---|---|
| `coverage_report` with no drafts | prints "no draft html found", exits 0 |
| An imported human guide (no `<!-- Source -->`) | reported as fully uncited — expected (never run through coverage; Version A only) |
| `parity` on a clean draft | 0 divergences (coverage must not regress the substring pass) |

## Defaults
`coverage_report` scans `drafts/*.html` when given no args; never fails a build.

## Acceptance criteria
- [x] **AC1** — *Given* the overreach fixture, *When* `pytest eval/test_overreach.py`, *Then* 2 passed
  (B catches the over-claim; A passes it through).
      ✓ `python -m pytest eval/test_overreach.py -q` → 2 passed.
- [x] **AC2** — *Given* the clean-draft fixtures, *When* `python -m eval.parity`, *Then* final line
  `divergences: 0`, exit 0.
      ✓ ran → `divergences: 0`.
- [x] **AC3** — *Given* the repo's real drafts, *When* `python -m eval.coverage_report`, *Then* it
  prints per-draft `uncited/total` and exits 0 (surfaced the real range 0→199 uncited on AI drafts and
  full-uncited on imported guides — the signal that Version B's writer must cite every sentence).
      ✓ ran on `drafts/*.html` + real Cell-D drafts → exit 0; numbers recorded in the epic notes.

## Future option
Add a `--batch` live pass@k harness (runbook §8) once a key exists — asserts batch pass@k equals the
non-batch path at `temperature`-free determinism; additive, no change to these keyless evals.
