# Story 004: Tasks / follow-ups

**Epic:** [Implementation Workspace](EPIC.md)
**Status:** Done ✓
**Points:** 3   ·   **Persona:** CS / Implementation (Sam)   ·   **Depends on:** STORY-001 (endpoints), STORY-002 (panel)

## TL;DR
A real follow-up list on the district workspace: seeded tasks render; an inline form adds one
(title · owner · due) that persists; checking a task completes it. Every add/complete logs to the
activity feed. The "boring thing made easy" that replaces her spreadsheet line-items.

## Scope
**In scope:** render `ws.tasks`; add-task form → `POST /tasks`; complete/reopen → `POST /tasks/{id}/toggle`; due-this-week highlight.
**Out of scope:** edit/delete a task; assignee = a specific person record; recurring tasks.

## Requirements
1.1 `_wsSections` renders a "Follow-ups" list from `ws.tasks` (title · owner · due); empty → "No follow-ups yet."
1.2 "+ Add" toggles an inline form (`_wsShowTaskForm`); Save → `_wsAddTask` → POST → re-render. Empty title is rejected (focus, no POST).
1.3 Each task has a `role=checkbox` button → `_wsToggleTask` → POST → re-render; done = strike-through.
1.4 Due within 2026-06-15…06-22 renders `.soon` (amber) unless done.

## Edge / Empty / Error states
| Case | Behavior |
|---|---|
| No tasks | "No follow-ups yet." |
| Empty title on Save | rejected, input refocused, no POST |
| POST fails | toast; panel unchanged |

## Defaults
- New task owner defaults to `Shared`, status `open`.

## Acceptance criteria
- [x] **AC1 — seeded tasks render.** ✓ Houston shows seeded "Chase POS vendor on terminal delivery".
- [x] **AC2 — add persists + logs.** *Given* the form, *When* "Confirm Direct Cert walkthrough booked / Cybersoft / 2026-06-20" is saved, *Then* tasks 1→2, activity top = `Added task "…"`; server GET confirms 2 tasks.
      ✓ Live + server-confirmed.
- [x] **AC3 — complete persists + logs.** *When* the new task's checkbox is clicked, *Then* it's struck through (`is-done`) and the server shows 1 done task.
      ✓ Live + server-confirmed.
- [x] **AC4 — no dead clicks / no errors.** ✓ Add/complete both do real persisted things; console errors = none.

> **Done evidence:** verified live on :8011 (sam-trainer) via the real form + checkbox; independent GET confirmed 2 tasks / 1 done; mutated seed reset afterward. Out-of-scope untouched.

## Notes
Built together with STORY-005 (same `_wsSections` render). Frontend-only.
