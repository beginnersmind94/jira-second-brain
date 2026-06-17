# Story 005: Re-validate lesson approval at course/track publish

**Epic:** [Trust hardening](EPIC.md)
**Status:** Not started
**Severity:** P1 · **Audit ref:** P1-3 (Agent 2 F-02, Agent 5 F-01)

## Requirement

> A published course must never contain a lesson whose underlying atom is no longer approved.

## Why

`api_publish_course` checks only "≥1 lesson"; it does not call `validate_all_lessons`. Validation runs at create and update, but not at the publish transition, and `api_get_course` does not re-check on serve. TOCTOU: add an approved atom → publish → a reviewer revises that atom back to `draft` → the course stays `published` and the learner still reaches the demoted atom.

## Acceptance criteria

- [ ] `api_publish_course` calls `validate_all_lessons` before flipping to `published` (or stores an approval snapshot at publish and re-checks on serve).
- [ ] Publishing a course whose lesson ref is draft/invalid → `409` with the named reason.
- [ ] Regression test covering publish-with-demoted-ref.

## Notes

`validate_all_lessons` already exists and is correct (`course_store.py:281-296`) — it's just not wired to publish. Defect at `demo_app.py:~897`.
