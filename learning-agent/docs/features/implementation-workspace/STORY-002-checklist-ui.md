# Story 002: Milestone checklist UI + working check-off (002 + 003 merged)

**Epic:** [Implementation Workspace](EPIC.md)
**Status:** Done ✓
**Points:** 5 (+3, STORY-003 folded in)   ·   **Persona:** CS / Implementation (Sam)   ·   **Depends on:** STORY-001

## TL;DR
The decorative stepper is now a real cockpit: the district page renders the seeded milestone
checklist from the workspace API, the 4-stage stepper **derives** from milestone progress, and
ticking an item is **real** — it persists server-side, moves the bar, recomputes status, and logs
activity, all without a reload. STORY-003 (check-off) was merged in because a render-only checkbox
would have been a dead click, which the demo-real bar forbids.

## Scope
**In scope:** render the checklist on district-detail State B; derive the stage stepper; wire real
toggle for manual items; auto (training) items render read-only.
**Out of scope:** tasks UI (STORY-004), notes/activity panel (STORY-005), portfolio roll-up
(STORY-006); the training lane's *real* auto-fill from completion (still seeded).

## Requirements
1.1 `_ddRenderStateB` injects `<div id="dd-workspace">` after the KPI strip; `renderDistrictDetail` calls `_loadWorkspace(d)`.
1.2 `_loadWorkspace` GETs `/api/districts/{id}/workspace` (X-Demo-User) → `_wsRenderPanel`; on error shows a message, never a blank.
2.1 Panel: status badge (On track/At risk/Blocked) + overall %; each milestone shows label, X/Y, a progress bar; each item shows status icon, label, owner.
2.2 Auto milestones (training) render items as non-interactive (`dd-ws-check--auto`, labeled "auto · training") — not buttons.
3.1 Manual items are `role=checkbox` buttons; click → `_wsToggle` → POST toggle → re-render from the returned workspace.
3.2 The 4-stage stepper derives via `_wsStage(ws)` (current_milestone → stage; 100% → Live); replaces the hand-set `d.stage`.

## Edge / Empty / Error states
| Case | Behavior |
|---|---|
| Workspace fetch fails | "Couldn't load the implementation checklist." (not blank) |
| Auto (training) item | rendered read-only; not clickable (no dead click) |
| Toggle POST fails | toast "Could not update the checklist."; panel unchanged |
| Blocked item | ⚠ + red check styling; clicking resolves it to done |

## Defaults
- Panel sits directly under the KPI strip; status colors reuse the design tokens (ok=green, at_risk=marigold, blocked=red).

## Acceptance criteria
- [x] **AC1 — renders from the API.** *Given* Houston, *When* the district page opens, *Then* the checklist shows 5 milestones with per-milestone X/Y + overall % + status.
      ✓ Live: Kickoff 3/3 · Data 3/3 · Config 2/3 · Training(auto) 0/3 · UAT 0/3 · **53% · At risk**.
- [x] **AC2 — stepper derives from progress.** ✓ Houston (current=config) → stepper current = "Onboarding"; not the static field.
- [x] **AC3 — check-off is real + persists.** *Given* Config 2/3, *When* the POS item is clicked in the UI, *Then* it goes 3/3, overall 53%→60%, status **At risk→On track**, live; an independent GET confirms `config-pos: done` + activity `Checked "POS hardware check" / Sam Rivera`. Toggle-back restores.
      ✓ Live + server-confirmed.
- [x] **AC4 — auto items aren't clickable.** ✓ Training items render "auto · training", no button (12 manual buttons + 3 auto spans).
- [x] **AC5 — no dead clicks / no errors.** ✓ Every manual checkbox does a real persisted thing; `preview_console_logs` (error) = none.

> **Done evidence:** verified live on :8011 (sam-trainer) via reload + click-through; server GET confirmed persistence; no console errors. Out-of-scope (tasks/notes/portfolio) untouched. Screenshot omitted — the preview can't rasterize this 700KB page (tooling limit); structure/behavior verified via snapshot+eval per the skill.

## Future option
Training milestone auto-fills from `completion_store`; tasks (004) and notes/activity (005) panels add to the same container.

## Notes
Frontend-only (no server restart needed — index.html serves fresh on reload). Reuses `escapeHtml`/`escAttr`/`_demoUserHeader`/`_showToast`/`_stageStepper`.
