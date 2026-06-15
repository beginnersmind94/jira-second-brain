# Epic: Implementation Workspace — make the district page a project-managed onboarding cockpit

**Status:** Done ✓ — all 7 stories shipped + verified live (2026-06-15)
**Component:** Districts · trainer/Implementation surface   ·   **Persona:** CS / Implementation team (Jaime) — *"Primary internal user of the platform"* (BRD §2)
**Last updated:** 2026-06-15
**Depends on:** [`projects.py`](../../../projects.py), [`tenancy.py`](../../../tenancy.py), the seeded `_DEMO` districts + `completion_store` (training lane), [`static/index.html`](../../../static/index.html)
**Standard:** every child story is written to and closed against [`docs/STORY-SPEC-STANDARD.md`](../../../../docs/STORY-SPEC-STANDARD.md) (seven-part contract + Definition of Done).

---

## TL;DR
The trainer's district page is a read-only dashboard with a **decorative** Onboarding→Training→Pre-launch→Live stepper and a "project" that's really a CRM record ([`projects.py`](../../../projects.py): roster + status + assignments, no tasks/notes/checklist). Turn it into a real **implementation project workspace**: a seeded, working **milestone checklist** + **tasks** + **notes** + **activity log**, with the training lane auto-filling from completion data. Build it **demo-real** — synthetic data, real behavior, no dead clicks — so it looks like it already does everything for the approval pitch.

## Problem statement
The BRD names the **CS/Implementation team as the primary internal user** (§2) and makes **"90%+ of CS team using the onboarding dashboard weekly"** a hard MVP success metric (§9). The top adoption risk it lists (§10): *"CS team does not adopt the dashboard, continuing to track onboarding manually."* That is the whole ballgame — **Jaime is the kingmaker.** If she shrugs and stays in her spreadsheet, the MVP fails its own metric and she gets removed from the loop, and we build what the users route around.

The build skipped exactly this layer. It shipped the content/grounding engine + a façade dashboard, and left the BRD's actual MVP — the **onboarding-management workspace** — as a decorative stepper. The boring-but-essential PM tools the BRD tags **MVP** are unbuilt as *working* tools: checklist/task steps (FR-CP-05), onboarding-progress-by-milestone (FR-RP-03), behind-milestone alerts (FR-NA-03), CSV import/export (FR-UM-07 / FR-RP-04), integration event log (FR-IN-06).

## Goal & success
**Demo success (this epic):** in a live click-through, the demoer opens a district, **checks off a milestone item** and watches the bar move and the stage advance, **adds a task and a note** and sees them in the activity log, and the **portfolio reflects it** — with **zero dead clicks** on the path. It looks like it already runs real onboarding projects.
**North-star (BRD):** a CS person would rather run a go-live here than in Excel → drives the 90%-weekly-adoption metric.

## Scope
**In scope:** a seeded, persistent implementation workspace per district — milestone checklist, tasks/follow-ups, notes, activity log, derived status; the stage stepper *derived from* milestone completion; portfolio roll-up + "needs me" view; removal of dead/fake clicks on the demo path.
**Out of scope (post-approval / later phase):** real SchoolCafe/PrimeroEdge roster & stage integration; real SSO; real email/SMS delivery of reminders; the *actual* onboarding runbook content (synthetic runbook ships now — real one comes after the yes); USDA Professional-Standards **training-hours** tracking (BRD V2, FR-RP-05/08); template *editing* UI.

## Design decisions
1. **Synthetic data, real behavior.** Seed rich, lived-in data; but every click on the demo path performs a real, persisted action. No `alert()`-only actions, no fake "Reply sent," no pickers that discard input. (This is the line between good demo seeding and the façade that breaks a live pitch — "one mistake kills trust.")
2. **Demo-real DoD.** For this phase, read the standard's *"real (non-seeded) data"* clause as **demo-real**: works end-to-end on seeded data, persists across the session (server store, survives reload), no dead clicks. Production integration is a later epic.
3. **Server-persisted, tenant-guarded.** New `project_workspace_store.py` writing `data/workspaces/<district-id>.json` (matches existing store pattern; survives reload — robust for a live demo). All routes call `assert_district_access` ([`tenancy.py`](../../../tenancy.py)) — reuse the real isolation.
4. **The stepper becomes a readout, not a label.** Stage = first milestone with incomplete items; it stops being a hand-set field.
5. **Training is one lane, auto-filled.** The "Staff Training" milestone derives from existing completion data; manual lanes (data migration, config, hardware) are one-tap check-offs — never forms.

## API & Data Contract (LOCKED — all stories build to this)
Endpoints (all tenant-guarded; `{isd}` = district id as passed by the district page):
```
GET  /api/districts/{isd}/workspace                      → {milestones[], tasks[], notes[], activity[], status}
POST /api/districts/{isd}/workspace/items/{item_id}/toggle   → updated workspace
POST /api/districts/{isd}/workspace/tasks                 {title, owner, due} → task
POST /api/districts/{isd}/workspace/tasks/{task_id}/toggle    → task
POST /api/districts/{isd}/workspace/notes                 {body, subject_type?, subject_id?} → note
```
Shapes:
```
milestone = {key, label, items:[item], auto?:bool}
item      = {id, label, owner:"Cybersoft"|"District"|"Shared", status:"todo"|"done"|"blocked", done_at?, source:"manual"|"auto"}
task      = {id, title, owner, due:"YYYY-MM-DD", status:"open"|"done", created_at}
note      = {id, subject_type:"district"|"learner", subject_id, body, author, created_at}
activity  = {id, type, label, actor, at}     // newest-first; aggregates toggles, tasks, notes, status, assignment, roster import
status    = "on_track" | "at_risk" | "blocked"   // derived (any blocked item → blocked; behind milestone vs go-live → at_risk)
```
Synthetic runbook (default template, plausible SchoolCafe/PrimeroEdge onboarding — seed, not authoritative):
`Kickoff & Discovery → Data Migration → Configuration → Staff Training (auto) → UAT & Go-Live`.

## Agent operating notes (devs = Sonnet 4.6)
- **One story = one focused agent run = one vertical slice.** Don't bundle. Each story's ACs are independently verifiable.
- **Locate code by symbol, not line number.** [`static/index.html`](../../../static/index.html) shifts under concurrent edits — grep for the function name (`renderDistrictDetail`, `_stageStepper`, `renderManage`, `respondHelp`, `_ddOpenStaffDrawer`, `asnSave`).
- **Persist via the store pattern** already used by `nudge_store.py`/`comment_store.py` (`data/<thing>/<id>.json`). Client state may mirror it in `_demoState`, but the server is the source of truth.
- **Gotcha — two district id namespaces:** the frontend portfolio uses `_DEMO.districts` ids (`houston-isd`/`aldine-isd`/`klein-isd`); the API roster uses `_DISTRICTS` (`houston/dallas/austin/cy-fair`). Seed the workspace for **whatever id the district page actually passes to the workspace fetch** — verify in code before seeding.
- **Verify live on :8011** (preview config `learning-studio-preview`); a click-through is the proof, per the DoD. **No dead clicks** is a release gate, not a nicety.
- **Keep DEMO DATA labeling** where synthetic data could be mistaken for a real customer's. Do not paint the verbatim-citation guarantee onto anything that isn't gate-grounded.

## User stories (sized for one Sonnet 4.6 run each)
- [x] **STORY-001 — Workspace store + seed** ✓ *(foundation; blocks all)* → [STORY-001](STORY-001-workspace-store-seed.md). `project_workspace_store.py` + the 5 contract endpoints; seeded distinct (Houston mid-Config / Aldine blocked / Klein near go-live); tenant-guarded; persists to disk. **Verified:** live API on :8011 + `tests/test_project_workspace.py` (6 passed).
- [x] **STORY-002 — Milestone checklist UI** ✓ *(dep: 001)* → [STORY-002](STORY-002-checklist-ui.md). Renders the seeded checklist on the district page; stepper derives from milestone progress. **Verified live:** Houston 5 milestones, Config 2/3, 53% / At risk.
- [x] **STORY-003 — Check-off works end-to-end** ✓ *(merged into STORY-002 — a render-only checkbox is a dead click)*. **Verified live:** clicking Config POS item → 3/3, 53→60%, At risk→On track, server-persisted, activity logged; toggle-back restores.
- [x] **STORY-004 — Tasks / follow-ups** ✓ *(dep: 001/002)* → [STORY-004](STORY-004-tasks.md). Seeded tasks render; add via form + complete, both persist + log. **Verified live:** tasks 1→2, completed, server-confirmed.
- [x] **STORY-005 — Notes + activity log** ✓ *(dep: 001/002)* → [STORY-005](STORY-005-notes-activity.md). Running notes + activity feed aggregating check-offs/tasks/notes, newest-first. **Verified live:** note 1→2, feed grew 5→8, server-confirmed.
- [x] **STORY-006 — Portfolio roll-up & "needs me"** ✓ *(dep: 001/002)* → [STORY-006](STORY-006-portfolio-rollup.md). Districts list shows per-district implementation health + % of plan, severity-sorted, with a "Need attention" KPI; Stage derives from the workspace. **Verified live:** Aldine Blocked 27% · Houston At risk 53% · Klein On track 93%; KPI=2; %s match district pages.
- [x] **STORY-007 — Kill the demo landmines** ✓ *(dep: 005; trust gate)* → [STORY-007](STORY-007-kill-dead-clicks.md). View-progress alert → real inline detail; fake "Reply sent" → real persisted workspace note; people-picker → captures identities. **Verified live:** `window.alert` spied across all three → 0 fake/dead clicks.

## Sequencing
```
001 ─┬─ 002 ── 003 ──┬── 006
     ├─ 004           │
     └─ 005 ──────────┴── 007
```
001 first (data contract). 002→003 is the spine. 004/005 parallel after 001. 006 after 003. 007 after 005. Stories touching `index.html` in parallel should run sequentially or in separate worktrees to avoid collisions.

## Risks
- **`index.html` concurrency** — large parallel edits collide; serialize index.html stories or isolate in worktrees.
- **Dead-click regressions** — any new control that no-ops on the demo path fails the trust gate; AC for every story includes "the control I added does a real thing."
- **Id-namespace mismatch** (see agent notes) — seeding the wrong id space → empty workspace in the UI. Verify the id flow first.
- **Over-claiming** — the synthetic runbook must not be presented as the authoritative SchoolCafe/PrimeroEdge process; keep DEMO DATA labeling.

## Implementation notes
- **STORY-001 (done):** [`project_workspace_store.py`](../../../project_workspace_store.py) — synthetic `_TEMPLATE` (5 milestones), `_SEED_PROFILES`, `get_workspace`/`toggle_item`/`add_task`/`toggle_task`/`add_note`, persists `data/workspaces/<id>.json`. 5 routes added to [`demo_app.py`](../../../demo_app.py) (`api_workspace_*`, all `assert_district_access`). Tests: [`tests/test_project_workspace.py`](../../../tests/test_project_workspace.py).
- **STORY-002+003 (done):** [`static/index.html`](../../../static/index.html) — `_loadWorkspace`/`_wsRenderPanel`/`_wsToggle`/`_wsStage` + `.dd-ws-*` CSS; container injected in `_ddRenderStateB`, call added to `renderDistrictDetail`; stepper derives via `_wsStage`. Frontend-only (no restart). Verified live + no console errors.
- **STORY-004+005 (done):** `_wsSections` (tasks + notes + activity) + `_wsShowTaskForm`/`_wsAddTask`/`_wsToggleTask`/`_wsAddNote`/`_wsDueSoon`/`_wsFmtDue`/`_wsFmtWhen` + CSS. The district cockpit is now complete (checklist · tasks · notes · activity), all real + persisted. Verified live; mutated seed reset after testing.
- **STORY-006 (done):** `_wsCache` + `_loadPortfolioWorkspaces` in `loadManage`; `renderManage` Implementation column (status + % of plan), "Need attention" KPI, severity sort, workspace-derived Stage. Retires the old "Behind"/"Needs help" amber pill collision (now green/amber/red).
- **STORY-007 (done):** `_ddToggleProgress` (real progress reveal) + async `respondHelp` (real workspace note, honest toast) + people-picker `value`/array collection in `asnAudChange`/`asnSave`/`_asnAudLabel`/`_asnCount`. No `alert()`-only actions remain on the demo path.
- **Epic complete.** All 7 stories shipped and verified live on :8011; backend has unit tests; no console errors; mutated seeds reset. Demo-clean (synthetic data, real behavior, no dead clicks).

## Future (post-approval / later epics)
Real PrimeroEdge/SchoolCafe roster + stage sync (FR-IN-01/02/03), real reminder delivery (FR-NA-01/02), the *actual* onboarding runbook co-authored with CS, USDA Professional-Standards **training-hours** compliance (FR-RP-05/08, V2), template editing.
