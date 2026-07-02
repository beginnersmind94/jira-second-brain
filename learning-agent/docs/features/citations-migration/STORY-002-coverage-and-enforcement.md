# STORY-002 — Coverage layer + enforcement at the two live gates

**Status:** `Done ✓` (2026-07-02)  ·  **Points:** 3  ·  **Persona:** Product Owner / SME reviewer
**Depends on:** STORY-001 (`run_gate`), `demo_app.publish_pending` + `demo_app.approve_resource`
(exist), `auth.get_current_user` (`is_trainer`).
**Epic:** [Two-version Citations-API grounding](EPIC.md)

## Scope
**In scope:** the coverage computation `_uncited_claim_blocks(html)` (claim-bearing `<p>/<li>` before
the Sources `<h2>` must carry a `<!-- Source -->`); wiring `publish_pending` and `approve_resource` to
block on `not _gate["passed"]` (so Version B additionally enforces coverage); the pure rename of the 6
reporting call sites to `run_gate(...)["substring"]`.
**Out of scope:** the Citations writer (STORY-003); enforcing coverage on Version A (it defaults to
`substring`, coverage off); changing the 409 response body/shape; touching `validate_citations`.

## Requirements
1.1 `_uncited_claim_blocks` counts a `<p>/<li>` as a *claim* only if it has visible text after
stripping tags **and** comments; a block is *uncited* if it lacks a `<!-- Source: -->`.
1.2 Blocks at or after the `Sources` `<h2>` are excluded (the deterministic Sources list is not a claim).
1.3 A transcript-voice citation (`<!-- Source: transcript 03:12 -->`) counts as a citation (not flagged).
2.1 `publish_pending`: when `gate_mode ∈ {citations,both}` **or** there is no stored `citation_integrity`,
it re-runs `run_gate` live and blocks on `not _gate["passed"]`; a Version-A draft with a stored clean
result keeps its existing fast path (`violations > 0`).
2.2 `approve_resource`: always re-runs `run_gate` live and blocks on `not _gate["passed"]`; on pass it
stores `citation_integrity` including the new `citations` sub-field and flips `status→approved`.
2.3 Both endpoints keep the existing `HTTPException(403)` trainer gate and the `409 grounding_not_clean`
body unchanged.
2.4 The 6 reporting sites (`_deterministic_eval`, `_stream_celld`, `_stream_celld_transcript`,
`_stream_from_scope`, `revise_resource`, `demo_run_refusal`) call `run_gate(...)["substring"]` — same
`integ` dict shape, no downstream read changed.

## Edge / Empty / Error
| Case | Behavior |
|---|---|
| Version A (substring) clean draft → approve | 200, `status: approved`, `citation_integrity.citations: null` |
| Draft with a `quote_not_found` citation → approve | 409 `grounding_not_clean`, `not_found ≥ 1` |
| Version B draft with an uncited claim → approve | 409 with `citations.uncited_claims > 0` |
| Non-trainer POSTs approve/publish | 403 (before any grounding work) |
| Draft with no stored `citation_integrity` on publish | computed live (both versions), then gated |

## Defaults
Version A: coverage off, existing fast path preserved. Approve always re-validates live (never trusts a
possibly-stale stored result).

## Acceptance criteria
- [x] **AC1** — *Given* `GATE_MODE=both`, a cited claim + one invented uncited claim, *When* `run_gate`,
  *Then* `passed False`, `citations.uncited_claims ≥ 1`; substring/Version A passes the same draft.
      ✓ `eval/test_overreach.py` (2 passed): B blocks, A passes-through.
- [x] **AC2** — *Given* the running server + a real substring-clean draft, *When* a trainer POSTs
  `/resources/{rid}/approve`, *Then* HTTP 200 and body `status: "approved · in Library"` with
  `citation_integrity.citations: null`.
      ✓ live `:8001` drive on `20260601-091452-item-management-micro-guide-7b2021` → HTTP 200, approved.
- [x] **AC3** — *Given* a draft with a `quote_not_found` citation, *When* a trainer POSTs approve,
  *Then* HTTP 409 `{"error":"grounding_not_clean", ... "not_found":1}`.
      ✓ live drive on a throwaway dirty draft → HTTP 409, `not_found:1` (draft deleted after).
- [x] **AC4** — *Given* a non-trainer (`john-cashier`), *When* they POST approve, *Then* HTTP 403.
      ✓ live drive → HTTP 403.
- [x] **AC5** — *Given* the wiring is applied, *When* the codebase is scanned, *Then* `integ =
  validate_citations(` appears 0× in `demo_app.py` and `demo_d.py`, and REG is 16/16 unchanged.
      ✓ `grep` counts 0/0; `python -m eval.regression` 16/16; existing suites (`test_builder_beats`,
        `test_evaluator_task5`) 37 passed.

## Future option
Surface the coverage number in the reviewer UI (`citation_integrity.citations.uncited_claims`) as an
"N uncited claims" badge before approve — additive; the field is already persisted on approve.
