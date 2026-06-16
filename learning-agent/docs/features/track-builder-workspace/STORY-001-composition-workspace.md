# STORY-001 — Composition Workspace (Track → Course → Lesson editor)

**Epic:** [Track Builder → Composition Workspace](EPIC.md) · **Agent:** C1 · **Model:** Sonnet 4.6
**Status:** Done ✓ — verified live end-to-end (2026-06-15) · **Depends on:** A (data model), B (role-at-source), Spine (`PUT /api/tracks/{id}/courses`)

> **Live verification (orchestrator, :8011):** Opened builder via `openTrackBuilder()` → dedicated
> `#view-track-builder` active at 1035×785, author view inactive, "Build a track" tab gone (AC1).
> Created a Cashier track through the modal → added a section (`PUT …/courses`, `course_ids:1`) →
> added a guide lesson (`PUT /api/courses/{id}`, renders with title + provenance badge) → published
> (200) → learner `john-cashier` GET returned 1 course / 1 lesson (the published-but-empty bug is
> dead). Role chips (Cashier/Site Manager/CN Director/All roles), Preview, focal-course disclosure
> all present. Temp track+course deleted after.
>
> **Follow-ups (not blockers):**
> - 🟡 Lesson rows print the raw enum `human_authored` instead of a human label (library cards use
>   "Cybersoft guide"/"AI-generated"). Fix in C4 polish — INV-1 still satisfied (badge present).
> - Raw stored lesson has `title:""` (resolved at render); harmless but worth populating on write.
> - Test-hygiene debt (pre-existing, not C1): `_temp_hold/test_tenancy.py` collides with
>   `tests/test_tenancy.py` at collection; `test_attach_quiz_to_track` leaks state in full-suite
>   runs (passes in isolation). Run suite with `--ignore=_temp_hold` for a clean signal: 498 passed.

## Description (JTBD)
*When* a trainer has approved content and a role to train, *they want to* assemble courses and
lessons into a track on one screen, *so that* a learner in that role gets a path the player
renders exactly as built.

## TL;DR
Promote the builder out of the "Create" page's tab strip into its own full-screen view
(`#view-track-builder`). It edits the real hierarchy: **courses** via `PUT /api/tracks/{id}/courses`,
**lessons** via `PUT /api/courses/{id}` (refs server-validated). Library defaults to the track's
role and is grouped, not a flat 141-item scroll. **Progressive disclosure** (one focal course),
deterministic entry, keyboard reorder, learner-preview. The old `#mode-track` tab is retired;
every "New track" entry routes here.

## Scope
**In:** dedicated view + routing; track header (title/desc/product/role via `ROLE_VOCAB`); course
CRUD + reorder; lesson CRUD + reorder within a course (picked from the library, refs validated);
role-defaulted + grouped + badged library; progressive disclosure; keyboard reorder;
learner-preview; publish; read-only handling of `_from_courses`/legacy module tracks.
**Out:** image upload (002); roster/assign (003); final a11y/responsive audit (004 — but ship
this surface accessible per INV); any change to the grounding gate or ref-validation rules.

## Requirements
1. **Entry & routing.** `openTrackBuilder()` deterministically `showView('track-builder')` and
   bootstraps regardless of prior active view (kills the observed 0×0 bug). All entries (Home
   "+ Create → New track", Tracks "+ New Track") land here. Remove the "Build a track" tab from
   `#view-author`; that page is generate-only. No entry silently vanishes (INV-3).
2. **Track header.** Edit title, description, product, role tags (`ROLE_VOCAB` checkboxes,
   reuse B's constant) inline; persists via `PUT /api/tracks/{id}`.
3. **Course management.** Add a course (new draft via `POST /api/courses`, or attach existing),
   reorder, remove — written through `PUT /api/tracks/{id}/courses`. **Re-fetch `GET /api/tracks/{id}`
   after every write** so state stays whole. "Add course" reads as **"Add section"** — hide the
   reusable-Course-entity ceremony; surface course reuse only when relevant.
4. **Lesson management.** Within a course, add a lesson by selecting a library item, reorder,
   remove — via `PUT /api/courses/{id}` (server validates each ref via
   `course_store.validate_lesson_ref`; surface its 422 reason verbatim).
5. **Library pane.** Role filter **defaults to the open track's `role_tags`**; **always shows
   untagged/global modules**; "All roles" escape; grouped by module/source with section headers;
   provenance badge on every card; shows a hidden-count when filtered.
6. **Progressive disclosure (altitude).** Courses are collapsible; the workspace keeps **one
   focal course** expanded at a time. The library is a secondary *source palette*, not a co-equal
   pane competing for "primary." (Critique fix-first.)
7. **Keyboard reorder.** Courses and lessons reorder by drag **and** by keyboard (up/down) —
   precision + a11y.
8. **Learner-preview.** A reachable "preview as learner" affordance so the trainer can see what
   the learner sees before publishing.
9. **Publish.** Disabled until the track has ≥1 course with ≥1 lesson; uses
   `POST /api/tracks/{id}/publish`. A track with no quiz/assessment publishes with a **soft
   warning**, not a block.
10. **Read-only safety.** Items flagged `_from_courses` render without remove/drag; a legacy
    module-based track is editable only via its modules path (server already 409s) — and the UI
    **explains why** it's read-only ("course-based — edit its courses").
11. **Type ramp.** Establish a visible hierarchy: Track title > Course header > Lesson row.
    Demote the full-width "New track" CTA to an inline button (observed: it reads as a banner).

## Edge / Empty / Error States
| Case | Behavior |
|---|---|
| Track has no courses | Empty state: "No sections yet — add one to start" (not a dead pane) |
| Course has no lessons | Course shows "0 lessons"; blocks publish |
| Role filter matches nothing tagged | Untagged content still shows; "N role-tagged items hidden" |
| `PUT /api/courses` ref rejected (422) | Inline error with the server's verbatim reason; no partial write |
| Same guide added to two courses | Library card marks "already in this track" |
| Legacy module-based track opened | Modules render read-only + a "course-based — edit its courses" hint; never forks |
| Customer persona | View unreachable (INV-2) |
| Trainer navigates away mid-edit | No dirty-state loss — every action writes through (no unsaved local buffer) |

## Defaults
New course = `draft`, product/role inherit track. Library defaults to track role + untagged.
Track stays `draft` until explicit publish. One course expanded by default.

## Trust & Accessibility (INV-1/2/3)
Every library/lesson card keeps its origin badge. No free-text claim field anywhere. Contrast
passes (measured); add tree/treeitem (or nested-list) semantics, focus management on add/remove,
keyboard reorder, targets ≥44 (audited in 004).

## References
`static/index.html` (`#view-track-builder`, `#mode-track`, `openTrackBuilder`, `showView`, `tb*`
fns, `const ROLE_VOCAB`); `demo_app.py` (`PUT /api/tracks/{id}/courses`, `/api/courses/*`,
`GET /api/tracks/{id}`); `course_store.validate_lesson_ref`; `static/track_builder_view.html`
(top-bar reference).

## Acceptance Criteria
- **AC1** — *Given* any prior view, *when* a trainer clicks any "New track" entry, *then* the
  full-screen builder view becomes active at non-zero size (no 0×0).
- **AC2** — *Given* an open track, *when* the trainer adds two courses and reorders them, *then*
  `GET /api/tracks/{id}` returns `course_ids` in the new order and the learner player reflects it.
- **AC3** — *Given* a course, *when* the trainer adds a library guide as a lesson, *then*
  `PUT /api/courses/{id}` persists it and it appears under that course with its provenance badge.
- **AC4** — *Given* a draft lesson ref, *when* added, *then* the server 422s and the UI shows the
  verbatim reason; nothing is written.
- **AC5** — *Given* a Cashier-tagged track, *when* the library loads, *then* Cashier-tagged +
  untagged items show, other-role items are hidden, and "All roles" reveals everything.
- **AC6** — *Given* a track with 0 courses, *when* Publish is clicked, *then* it's blocked with a
  clear reason; *given* ≥1 course with ≥1 lesson, publish succeeds (no-quiz = soft warning only).
- **AC7** — *Given* Customer persona, *when* navigating, *then* the builder is not reachable.
- **AC8 (altitude)** — *Given* a track with 3 courses, *when* the workspace loads, *then* courses
  are collapsible with one focal course expanded — not all lessons of all courses at once.
- **AC9 (keyboard)** — *Given* keyboard only, *when* reordering a course or lesson, *then* it can
  be moved up/down without a mouse, with visible focus.
- **AC10 (preview)** — *Given* an open track, *when* the trainer opens "preview as learner",
  *then* they see the learner rendering without leaving the workspace.
- **AC11 (mental model)** — *Given* a trainer, *when* they "add a section", *then* a course is
  created+attached without exposing the standalone Course-entity ceremony.

## Definition of Done
- [ ] AC1–AC11 demonstrated live (orchestrator drives the preview browser).
- [ ] "Build a track" tab removed from `#view-author`; every "New track" entry routes to the new view.
- [ ] **Working core never left broken:** create track → add course → add lessons → persists →
      learner player reflects it, before any refinement.
- [ ] INV-1/2/3 hold; no JS console errors; existing `pytest` suite green.
- [ ] EPIC implementation notes updated.
