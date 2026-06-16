# EPIC — Track Builder → Composition Workspace

**Status:** Complete ✓ — all 4 stories Done + verified live (2026-06-16); pending commit + human review
**Owner:** Rahul (PM) · build via sequenced Sonnet 4.6 agents
**Created:** 2026-06-15

## Problem

The Track Builder was a flat *module-sequencer* bolted on as tab 4 of the "Create"
(guide-authoring) page. But the product's real content hierarchy — the one the learner
player renders — is **Track → Course → Lesson(s) → quiz/assessment**. The builder spoke
only `module_ids`, one layer too shallow. Symptoms seen live:

- **Published-but-empty:** 3 of 4 published tracks (e.g. *Cashier Summer Refresher*) are
  composed via `course_ids` and showed as "0 modules / No modules yet" in the builder.
- **No role scoping:** library showed all 141 modules flat; `?role=Cashier` returned 0
  because content wasn't tagged.
- **Ghost-drawer a11y trap:** the off-screen "Assign training" drawer was `display:flex`,
  not `inert`/`aria-hidden`, with 7 focusable controls reachable while "closed."
- **No media; individual assign buried in a modal.**

## Solution

Promote the builder into a **dedicated full-screen composition workspace** that speaks the
player's language (courses + lessons), with media, roster/assignment, and accessibility
**designed-in, not retrofitted.** "Not a drawer" means a workspace that lets a trainer
*think* — not a wall that shows everything at once.

## Already shipped (DoD met, tests green)

| Agent | What | Verified |
|---|---|---|
| **A — Data model** | `expand_track()` reads `course_ids→courses→lessons`; `PUT …/modules` 409-guards course-based tracks; publish guard fixed | 35 tests |
| **B — Role-at-source** | `ROLE_VOCAB=["Cashier","Site Manager","CN Director"]`; generation+approval write `role_tags`; `PUT /api/modules/{id}/role-tags`; vocab pickers | 56 tests |
| **Spine** | `PUT /api/tracks/{id}/courses` — trainer-gated, rejects phantom courses, won't orphan legacy module tracks | 29 tests |

## Stories

| # | Story | Surface | Depends on |
|---|---|---|---|
| [001](STORY-001-composition-workspace.md) | Composition Workspace ✓ **Done (verified live)** | dedicated Track→Course→Lesson editor | A, B, Spine |
| [002](STORY-002-lesson-media.md) | Lesson Media (images) ✓ **Done (verified live)** | upload + placement in lesson | 001 |
| [003](STORY-003-roster-assignment.md) | Roster & Assignment ✓ **Done (verified live)** | full-screen roster, individual + bulk assign/unassign | 001 |
| [004](STORY-004-a11y-responsive-hardening.md) | A11y / Responsive / Hardening ✓ **Done (verified live)** | verification gate + distributed a11y | 001–003 |

**Sequence:** 001 → 002 → 003 → 004 (serial — they share `static/index.html` + `demo_app.py`).
All agents **Sonnet 4.6, max reasoning, no commit until reviewed.**

## Standing invariants (referenced by every story as INV)

- **INV-1 Trust:** provenance/source badges on every content item; **no free-text product-claim
  authoring**; grounding gate + `<!-- Source -->` citations untouched; honest origin labels
  (never paint "✓ AI-grounded" on human/vendor content).
- **INV-2 Persona:** trainer-only surfaces unreachable in Customer view; customer-banner kept.
- **INV-3 No-regression:** full `pytest` suite stays green (run from `learning-agent/` with the
  sibling `.venv`); no existing entry point silently vanishes (re-point, don't delete).

## Design decisions (from the UX critique pass)

1. **Altitude over size.** The workspace uses progressive disclosure (one focal course at a
   time), not an everything-at-once tree. A wall is just a bigger drawer.
2. **Audience-first assignment.** Assign by role/site/district is the default path; individual
   assign/unassign is the refinement — because bulk is the common job (Jaime's team).
3. **Media has a defined home — `image` lesson type (C2 decision, locked).** A lesson is a
   *pointer*; images attach as a **first-class `image` lesson type** in the existing lesson list.
   Chosen over a figure-list field on a guide lesson because: (a) it reuses C1's lesson-list UI
   (drag-reorder, remove, badge) with zero new container code; (b) a guide's ref points to
   grounded approved content — adding a media[] slot introduces ambiguous render order; (c) an
   image lesson is reorderable and composable alongside any other lesson type, matching the trainer
   JTBD ("place a screenshot *in the sequence*"). Schema: `{type:'image', ref:<hash-filename>,
   alt:<required>, caption?}`. `alt` mandatory (WCAG 1.1.1 — blocked client+server).
   Origin badge: always `human_authored` — NEVER `ai_grounded` (INV-1, enforced in
   `course_store.lesson_origin_badge`). Downscale: Pillow unavailable in venv; dimension cap
   (max 1600 px either axis) enforced via stdlib struct header parsing at upload — trainer resizes
   externally. Upload endpoint: `POST /api/courses/images` (trainer-only, content-hash filename,
   `static/course-img/`). 12 new tests in `eval/test_lesson_media.py` (T1–T12), all green.
4. **A11y designed-in.** Each surface ships accessible; C4 *verifies*, it is not where a11y
   first happens.

## Verification

Backend: `pytest` per story. Front-end: orchestrator drives the live preview browser
(`learning-studio` :8001 / `learning-studio-preview` :8011) — agents build valid in-place
edits and run backend tests; live UX verification is the orchestrator's gate. Final proof
(004): a recorded trainer→learner click-through + a measured <3s learner load.
