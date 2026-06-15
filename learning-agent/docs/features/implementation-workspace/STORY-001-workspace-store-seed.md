# Story 001: Workspace store + seed + 5 contract endpoints

**Epic:** [Implementation Workspace](EPIC.md)
**Status:** Done ✓
**Points:** 5   ·   **Persona:** CS / Implementation (Sam/Jaime)   ·   **Depends on:** [`tenancy.py`](../../../tenancy.py)

## TL;DR
The backend foundation for the implementation cockpit: a per-district project workspace
(milestone checklist · tasks · notes · activity), seeded so each demo district looks alive at a
distinct point, persisted to disk, tenant-guarded. Demo-real: synthetic seed, real persistence.

## Scope
**In scope:** `project_workspace_store.py`; the 5 LOCKED contract endpoints; seed for the demo
districts + a never-empty fallback for any id; tenant guard on every route.
**Out of scope:** all UI (STORY-002+); training-lane auto-fill from completion (later); real
SchoolCafe/PrimeroEdge data.

## Requirements
1.1 New `project_workspace_store.py` persists raw state to `data/workspaces/<safe-id>.json` (existing store pattern).
1.2 Read payload computed from a synthetic onboarding template + raw overrides: milestones (per-item + per-milestone %), `overall_pct`, derived `status` (`blocked`>`at_risk`<60%>`on_track`), `current_milestone`, tasks, notes, activity (newest-first).
2.1 Endpoints exactly per the epic contract: `GET /workspace`, `POST /items/{id}/toggle`, `POST /tasks`, `POST /tasks/{id}/toggle`, `POST /notes` — all under `/api/districts/{isd}/`.
2.2 Every route calls `assert_district_access(current_user, isd)` before touching data.
3.1 Seed stars at distinct points: Houston mid-Configuration, Aldine **blocked** on Data Migration, Klein near Go-Live.
3.2 Every mutation appends an activity entry (actor + timestamp) and persists.

## Edge / Empty / Error states
| Case | Behavior |
|---|---|
| District never seen before | deterministic mid-onboarding seed (never empty) |
| Cross-tenant GET/POST | `403` via `assert_district_access` |
| Toggle unknown item id | `404` (store raises `KeyError`) |
| Empty task title / note body | `400` (store raises `ValueError`) |
| Corrupt/unreadable JSON on disk | reseed rather than crash |
| Blocked item | never also seeded as done |

## Defaults
- New task owner `Shared`, status `open`; item default `todo`; template `schoolcafe-onboarding`; note body capped 2000 chars.

## Acceptance criteria
- [x] **AC1 — seeded & distinct.** *Given* the demo districts, *When* `GET /api/districts/{isd}/workspace`, *Then* each returns 5 milestones with believable, distinct progress.
      ✓ Live (sam-trainer): Houston `at_risk 53%` current=config · Aldine `blocked 27%` · Klein `on_track 93%`. Test `test_seed_variety`.
- [x] **AC2 — tenant isolation.** *Given* sam-trainer (houston/aldine/klein), *When* GET `austin-isd/workspace`, *Then* `403`.
      ✓ Live: `austin-isd → HTTP 403`.
- [x] **AC3 — toggle persists + recomputes + logs.** *Given* Houston, *When* POST toggle `config-pos`, *Then* item→done, overall rises, activity logs `Checked “POS hardware check” by Sam Rivera`, and a fresh GET still shows done.
      ✓ Live: 53%→60%, activity logged, re-GET persisted, toggle-back restored. Test `test_toggle_persists_and_logs`.
- [x] **AC4 — never empty.** *Given* an unseen district id, *When* GET, *Then* a full mid-onboarding workspace (no blank).
      ✓ Test `test_never_empty`.
- [x] **AC5 — validation.** Unknown item→404; empty task title / note body→400.
      ✓ Tests `test_toggle_unknown_item_raises`, `test_task_and_note_validation`.

> **Done evidence:** live API run on :8011 (sam-trainer) + `tests/test_project_workspace.py` **6 passed**; `py_compile` clean; server boots with the new module. No dead clicks introduced (backend-only). Out-of-scope (UI, auto-training) untouched.

## Future option
Training milestone auto-fills from `completion_store` (STORY-003 area); real roster/stage from PrimeroEdge/SchoolCafe (post-approval).

## Notes
Two district id namespaces exist (`_DEMO` ids vs `_DISTRICTS`); the district page passes `_DEMO` ids (`houston-isd`/`aldine-isd`/`klein-isd`), which are the seeded stars. The PowerShell console renders the stored curly quotes as mojibake — the on-disk JSON is correct UTF-8 (`ensure_ascii=False`).
