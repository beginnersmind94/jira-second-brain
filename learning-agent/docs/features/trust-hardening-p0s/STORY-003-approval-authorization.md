# Story 003: Add role authorization to approval / edit endpoints

**Epic:** [Trust hardening](EPIC.md)
**Status:** Done ✓ — code + `tests/test_approval_authz.py` landed 2026-06-15. ⚠️ The live `:8001` server runs `reload=False`, so it serves the fix only after a restart.
**Severity:** P0 · **Audit ref:** P0-3 (Agent 2 F-01)

## Requirement

> Only an authorized Product Owner / trainer can approve content or request edits. The "human approves" invariant must become "an *authorized* human approves."

## Why

Confirmed live: `john-cashier` (a learner) POSTed `/resources/GUIDE-002/approve` and got `200 approved:true`. The approval gate checks that a human POSTed, but not *who*. `CLAUDE.md` is explicit that the reviewer is a PO and that approval rights must not reach downstream/implementation users — this endpoint contradicts that.

## Acceptance criteria

- [x] These endpoints take `Depends(get_current_user)` and require PO/trainer role: `POST /resources/{rid}/approve`, `/resources/{rid}/publish_pending`, `/resources/{rid}/revise`, `/api/quizzes/{qid}/approve`, `/api/flashcards/{deck_id}/approve`, `/api/tracks/{tid}/publish`.
- [x] A learner (`john-cashier`) — and a CN Director — POST to any of them → `403`.
- [x] Grounding re-validation on approve is unchanged (only the authZ layer was added; `validate_citations` untouched — REG-01…16 still green).
- [x] Regression test: learner & director → 403; trainer passes the gate (→ non-403). `tests/test_approval_authz.py`, 3/3 pass.

## Notes

Pattern copied from `api_publish_course` (`if not current_user.is_trainer: raise 403`). Applied to all 6 handlers as the first statement (the gate fires before any resource resolution, so a learner is rejected before lookups). Verified: no handler is called internally (HTTP-only), so adding the `Depends` param is safe.

**Implementation note (2026-06-15):** added `current_user: CurrentUser = Depends(get_current_user)` + an `is_trainer` 403 to `approve_resource`, `publish_pending`, `revise_resource`, `quizzes_approve`, `flashcards_approve`, `api_publish_track`. Test = `tests/test_approval_authz.py` (side-effect-free: non-existent ids; learner/director → 403, trainer → 404). **Not yet live on `:8001`** — needs a server restart.
