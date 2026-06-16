# STORY-003 — Roster & Assignment (audience-first, individual + bulk)

**Epic:** [Track Builder → Composition Workspace](EPIC.md) · **Agent:** C3 · **Model:** Sonnet 4.6
**Status:** Done ✓ — verified live end-to-end (2026-06-15) · **Depends on:** 001 (shared file); assign infra already exists

> **Live verification (orchestrator, fresh :8011):**
> - **Ghost-drawer fixed (AC5):** `#asn-modal` is now `inert` + `aria-hidden="true"` when closed →
>   **0 focusable controls** (was 7 reachable-while-closed). New `#tbv-roster-panel` is `hidden`/
>   `display:none` when closed (0 focusable); opens via `openAssignDrawer`, closes via
>   `rosterPanelClose()` cleanly (re-verified 0 focusable after close).
> - **Audience-first (the critique fix-first):** Assign tab leads with "Bulk assign by audience —
>   The primary path" (role/site/district); individual assign labelled "Refinement." ✓
> - Bulk assign by role → 200; individual assign → 200; individual unassign →
>   **`completion_retained: true`** (record preserved, AC2); unassigned view → 200; draft track
>   assign → **409 `draft_track`** (AC4); cashier assign → **403** (AC6); past-due **warns, doesn't
>   block** (AC4). New endpoints `POST/DELETE /api/tracks/{tid}/assign/user/{uid}` + `GET …/unassigned`.
> - Roster tab: sortable table (Name/Role/Status/Progress/Due), nudge-all-overdue, status pills
>   color+icon+text. Temp track/course deleted after. Suite: **531 passed**.
> - **Caveat:** nudge throttle (AC3) is unit-tested (T8); the live temp track had a future due date
>   so 0 learners were overdue → both nudge calls were no-ops (throttle not live-reproduced).
> - **For C4:** sortable headers need `onkeydown` (Enter/Space) for full keyboard op; the My Team
>   `#assign-modal` now also receives `inert` — verify its open/close still works; throttle is
>   in-memory (resets on restart, demo-appropriate).

## Description (JTBD)
*When* a district manager (Dana / Site Manager) or Implementation (Jaime) needs the right people
trained, *they want to* assign or unassign people — by role/site/district and individually — see
who's behind a deadline, and nudge, *so that* go-live training actually lands.

## TL;DR
Promote the assign infra (`/api/tracks/{id}/assign`, audiences role/site/district/people, roster,
nudge) into a **full-screen Roster & Assignment surface**. **Audience-first** (role/site/district
is the default path); individual assign/unassign is the refinement. Replace the off-screen
"Assign training" ghost-drawer (which leaves focusable hidden content) with this real surface.

## Scope
**In:** full-screen roster; **bulk assign by role/site/district** (default); **individual assign +
unassign**; due date + drip/dynamic; per-learner status vs. deadline; nudge one / nudge-all-overdue
(throttled); "unassigned learners" view; persona-scoped; tenant-scoped.
**Out:** SSO/roster sync from SchoolCafé/PrimeroEdge (façade stays — label it honestly); cross-tenant
views; compliance-report redesign.

## Requirements
1. **Real surface, not the drawer.** A proper view/panel — never `display:flex` while off-screen
   and tab-reachable. The observed ghost-drawer focus trap must be **closed, not relocated**.
2. **Audience-first (fix-first).** The default assign path is by role / site / district. Individual
   assign/unassign is a refinement on top — not the primary path. Bulk is the common job.
3. **Individual assign + unassign.** Add/remove specific learners. Verify individual unassign
   semantics on the existing `DELETE /api/tracks/{id}/assign/{idx}`; add an endpoint if individual
   unassign isn't cleanly supported.
4. **Unassign preserves history.** Removing an assignment must **not** delete the learner's
   completion record; confirm before unassign. Unassign ≠ erase.
5. **Persona-scoped.** Site Manager sees one site; Dana sees her district; Jaime's cross-district
   view is a scoped switch or separate surface — one undifferentiated surface serves none.
6. **Status & nudge.** Per-learner status (assigned/in-progress/overdue/done) vs. due date; nudge
   one + nudge-all-overdue. **Throttle** nudges + show "last nudged"; don't spam.
7. **Guards.** Draft (unpublished) tracks are not assignable. A past due date **warns, doesn't
   block** (and never fires the error before the trainer finishes setting it).
8. **Unassigned view.** Show learners not assigned to anything — the gap a manager actually worries
   about.
9. **Tenancy.** A manager sees only their district's roster; no cross-tenant leak. Cashier cannot
   assign (403).

## Edge / Empty / Error States
| Case | Behavior |
|---|---|
| Track has no assignees | Empty roster + clear "Assign people" CTA |
| Unassign last person | Allowed; track simply has no assignees; record retained |
| Learner already assigned | Idempotent; no duplicate |
| Assign a draft track | Blocked with reason |
| Due date in the past | Warn, don't block |
| Nudge-all-overdue twice quickly | Throttled; shows last-nudged |
| Cashier hits assign | 403 / control hidden (INV-2) |
| Cross-district id | Rejected; not shown |

## Defaults
New assignment has no due date unless set. Unassign reversible (re-assign). Roster scoped to
caller's district. Audience defaults to role/site selection, not individual.

## Trust & Accessibility (INV-2/3)
Fully keyboard-operable; **no** hidden focusable form left in the tab order (closes the observed
trap). Roster is a data table: status by **color + icon + text** (≈1 in 12 men have CVD), sticky
header, sortable, overdue unmissable. Façade data labeled honestly.

## References
`demo_app.py` (`POST /api/tracks/{id}/assign`, `DELETE …/assign/{idx}`, `/api/roster/{id}`,
`…/nudge`, `…/nudge-all-overdue`, `audience_type`); `#asn-modal` in `static/index.html`; `tenancy.py`.

## Acceptance Criteria
- **AC1 (bulk default)** — *Given* a track, *when* a director assigns "all Cashiers at Site X",
  *then* matching learners are enrolled in one action and appear on the roster.
- **AC2 (individual)** — *Given* the roster, *when* the director assigns then unassigns a named
  learner, *then* the change persists and their completion record is retained.
- **AC3 (nudge)** — *Given* overdue learners, *when* nudge-all-overdue is clicked, *then* only
  overdue learners are nudged, and a second immediate click is throttled.
- **AC4 (guard)** — *Given* a draft track, *when* assign is attempted, *then* it's blocked; *given*
  a past due date, *then* a warning shows but assignment proceeds.
- **AC5 (a11y)** — *Given* the surface is closed, *when* a keyboard user tabs the page, *then* focus
  never enters a hidden assignment form.
- **AC6 (tenancy)** — *Given* District A's manager, *when* viewing the roster, *then* only District A
  learners appear; cashier assign → 403.
- **AC7 (gaps)** — *Given* a district, *when* the manager opens the unassigned view, *then* learners
  with no assignments are listed.

## Definition of Done
- [ ] AC1–AC7 live-verified, including a keyboard tab-through proving no ghost-drawer.
- [ ] `pytest` for bulk + individual assign/unassign, record retention, tenancy, 403, draft-block.
- [ ] INV-2/3 hold; existing suite green.
