# Story 005: Notes + activity feed

**Epic:** [Implementation Workspace](EPIC.md)
**Status:** Done ✓
**Points:** 3   ·   **Persona:** CS / Implementation (Sam)   ·   **Depends on:** STORY-001 (endpoints), STORY-002 (panel)

## TL;DR
The district workspace now has a running **note log** (authored, timestamped) and an **activity feed**
that aggregates every action — milestone check-offs, task add/complete, and notes — newest-first. The
trainer's working context lives in the tool instead of her head.

## Scope
**In scope:** render `ws.notes` + an add-note input → `POST /notes`; render `ws.activity` (top 8, newest-first); both update on any workspace mutation.
**Out of scope:** per-learner notes UI (subject_type=learner is supported by the API, not yet surfaced); edit/delete a note; @mentions; pagination of activity.

## Requirements
1.1 `_wsSections` renders a "Notes" list from `ws.notes` (body · author · when); empty → "No notes yet."
1.2 Add-note input (Enter or "Add") → `_wsAddNote` → `POST /notes` → re-render; empty body rejected.
1.3 "Activity" list renders `ws.activity` (server returns newest-first), capped at 8, each `label · actor · when`.
1.4 `_wsFmtWhen` shows "today" for 2026-06-15, else "Mon DD".

## Edge / Empty / Error states
| Case | Behavior |
|---|---|
| No notes | "No notes yet." |
| Empty note body | rejected, input refocused, no POST |
| POST fails | toast; panel unchanged |

## Defaults
- Notes default `subject_type=district`; activity shows the 8 most recent.

## Acceptance criteria
- [x] **AC1 — seeded notes + activity render.** ✓ Houston: 1 seeded note, 5 activity entries on load.
- [x] **AC2 — add note persists + logs.** *When* a note is added, *Then* notes 1→2, activity top = "Added a note"; server GET confirms 2 notes.
      ✓ Live + server-confirmed.
- [x] **AC3 — activity aggregates all actions.** ✓ Across one session (add task + complete task + add note) the feed grew 5→8, newest-first — and milestone check-offs log too (STORY-003).
- [x] **AC4 — no dead clicks / no errors.** ✓ console errors = none.

> **Done evidence:** verified live on :8011 (sam-trainer); independent GET confirmed 2 notes and the aggregated feed; mutated seed reset afterward.

## Notes
Built together with STORY-004 (`_wsSections`). The API already supports learner-scoped notes (`subject_type`/`subject_id`) for a future per-learner notes surface.
