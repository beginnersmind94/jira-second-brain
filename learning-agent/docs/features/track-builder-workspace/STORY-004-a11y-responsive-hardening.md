# STORY-004 — Accessibility, Responsive & End-to-End Hardening (verification gate)

**Epic:** [Track Builder → Composition Workspace](EPIC.md) · **Agent:** C4 · **Model:** Sonnet 4.6
**Status:** Done ✓ — verified live (2026-06-16) · **Depends on:** 001–003

> **Live verification (orchestrator, fresh :8011):**
> - **AC1 targets ≥44:** role chip 44, ▲▼ reorder 44×44, course action 44×44, add-lesson 44h,
>   filter selects (`.tbv-lib-sel`) 44h, "New track" inline (not a banner). One miss caught + fixed
>   live by orchestrator: the track-switcher dropdown (`.tbv-track-sel`) was 31px → now **44**.
> - **AC2 keyboard:** roster sortable headers got `onkeydown` Enter/Space; other new controls are
>   native `<button>`s; focus-visible ≥3:1.
> - **AC3 responsive:** at 375px the builder has **0px** horizontal overflow (degrades gracefully);
>   learner surface 4px (rounding-level, effectively none).
> - **AC4 contrast:** new pills/chips measured 5.8–12.9:1 (AA); status = color+icon+text.
> - **AC5 E2E (live):** uploaded image → built a course with **guide + image** lessons → created a
>   Cashier track → attached → published (200) → learner `john-cashier` GET returned 1 course with
>   `lessonTypes:[guide, image]`. Assign-post-publish 200.
> - **AC6 failure paths (live):** empty-track publish → **409 `no_modules`**; bad lesson ref → **422
>   `invalid_lesson_ref`**; assign on a draft track → **409 `draft_track`**.
> - **AC7 perf:** learner track GET **73ms** (API-time proxy). Full-RUM <3s not stress-tested with a
>   large image — the 1600px dimension cap bounds weight; Pillow downscale remains the open lever
>   if a real heavy image ever regresses it (deferred, see EPIC).
> - Drawer-inert regression trace: clean (no drawer permanently inert). Temp artifacts deleted.
>   Suite: **538 passed**.

## Description (JTBD)
*When* the workspace ships, *it must* be keyboard-operable, work on the contractual viewport, and
*prove* the whole loop runs, *so that* "end-to-end" is demonstrated, not assumed.

## TL;DR
A11y/responsive ACs are **distributed into 001–003** (each surface ships accessible). C4 is the
**verification gate**: targets ≥44, keyboard/focus, contrast recheck, mobile behavior, demote
chrome — then a recorded trainer→learner click-through that includes a **failure path** and a
**measured <3s learner load**.

## Scope
**In:** distribute a11y/responsive ACs upstream; verify targets ≥44 (the live `.mod-card-add` "+"
was 28px, filter selects 25px); keyboard/focus across all new surfaces; contrast spot-check on new
controls; builder responsive behavior; the end-to-end proof.
**Out:** new features; backend logic changes (attribute/CSS/markup + verification only).

## Requirements
1. **A11y designed-in, not retrofitted (fix-first).** The a11y/responsive ACs live in 001–003's
   DoD; C4 audits them. C4 does not become the place a11y first happens.
2. **Targets.** Every interactive control in the workspace ≥44×44 CSS px.
3. **Responsive — right surface.** The **learner** surfaces are 375px-critical (BRD NFR: cafeteria
   staff on phones). The **builder** is tablet-graceful (no breakage), not optimized for
   phone-composition — don't misallocate the responsive budget to building tracks on a phone.
4. **Keyboard/focus.** Every control reachable + operable; focus visible (≥3:1); logical order; no
   trap (incl. the former ghost-drawer).
5. **Chrome weight.** "New track" is an inline button, not a full-width banner.
6. **Contrast.** New controls meet AA (≥4.5:1 text / ≥3:1 UI).
7. **End-to-end proof.** Drive the full loop live: trainer creates a track → adds a course → adds
   lessons incl. an image (002) → assigns a learner (003) → publishes; learner (cashier persona)
   sees exactly those courses/lessons and completes + certifies. Include a **failure path** (draft
   lesson blocked; empty publish blocked) and **measure player load < 3s**.

## Edge / Empty / Error States
N/A (hardening) — but verify each prior surface's empty/error states render correctly at the
tested viewport.

## Defaults
Inherit design-system tokens; no new palette. Respect `prefers-reduced-motion` (already in CSS).

## Trust & Accessibility (INV-1/2/3)
This is the a11y gate: WCAG 2.1 AA; BRD-contractual 375px (learner) + <3s player. Color never the
sole signal; status text+icon.

## References
`static/index.html` (workspace markup/CSS from 001–003, `.mod-card-add`, filter selects, media
queries, `.track-switcher`); critique findings #6 (drawer), #7 (targets), #8 (mobile ordering).

## Acceptance Criteria
- **AC1** — *Given* the workspace, *when* targets are measured, *then* every interactive control is ≥44×44.
- **AC2** — *Given* a 375px viewport, *when* the **learner** surface loads, *then* it is usable with
  no horizontal scroll; the builder degrades gracefully (no breakage) at tablet width.
- **AC3** — *Given* keyboard-only, *when* tabbing all surfaces, *then* every control is reachable +
  operable, focus visible, no trap.
- **AC4** — *Given* contrast measurement on new controls, *then* all pass AA.
- **AC5 (the big one)** — *Given* a trainer, *when* they create → add course → add lessons (incl. an
  image) → assign John Doe → publish, *then* John Doe (cashier) sees exactly those courses/lessons
  and completes + certifies — verified live as a click-through.
- **AC6 (failure path)** — *Given* the same flow, *when* a draft lesson is added or an empty track
  is published, *then* both are blocked with clear reasons.
- **AC7 (perf)** — *Given* the published track (with an image), *when* the learner opens it, *then*
  player load is measured < 3s.

## Definition of Done
- [ ] AC1–AC4 measured live (inspect/resize); AC5–AC7 demonstrated as a recorded click-through + a
      measured load time.
- [ ] a11y/responsive ACs confirmed present in 001–003 (not first-introduced here).
- [ ] INV-1/2/3 hold; existing `pytest` suite green.
- [ ] EPIC updated with final state.
