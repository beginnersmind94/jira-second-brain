# Story 004: Fix the quiz citation chain + make the badge honest

**Epic:** [Trust hardening](EPIC.md)
**Status:** In progress — partial. The summer-refresher course no longer references the broken quiz (swapped to grounded `quiz-seed-food-safety-3q` on 2026-06-15, verified). Still open: the broken `quiz-seed-cashier-demo` data itself, and the unconditional `ai_grounded` badge in `lesson_origin_badge`.
**Severity:** P0 · **Audit ref:** P0-4 (Agent 1 F-01/F-02, Agent 5 F-03)

## Requirement

> A lesson badged `ai_grounded` must mean every answer traces to a verbatim span of the source it cites. `quiz-seed-cashier-demo` does not meet this and is in a published, learner-facing course.

## Why

`quiz-seed-cashier-demo` is badged `ai_grounded`, but: its `source_id` points to `course-20260613-cashier-onboard`, which contains no POS content; 3–4 of 8 questions are `grounded:true` with an **empty `source_quote`**; `source_content_hash` is a placeholder. "Show source" would not substantiate the answers. Separately, `course_store.lesson_origin_badge` returns `ai_grounded` for *any* quiz unconditionally — so a manually-seeded, un-gated quiz wears the strongest trust badge.

## Acceptance criteria

- [ ] `quiz-seed-cashier-demo`: `source_id` points to content that actually contains the tested facts; every question has a non-empty `source_quote` that verbatim-supports its answer; real `source_content_hash`. (Or: replace it in the course with a properly-grounded quiz / regenerate once the SDK path is available.)
- [ ] `lesson_origin_badge` (`course_store.py:314-316`) does not return `ai_grounded` for a quiz with no recorded gate passage — un-gated quizzes are badged honestly.
- [ ] No quiz with `grounded:true` + empty `source_quote` can be approved (gate check) — with a test.

## Notes

This is pre-existing seed data (`provenance: manual_grounded`) that the summer build *exposed* by selecting it. Owner: content (data) + platform (badge logic). Until fixed, consider dropping the quiz lesson from the published course.
