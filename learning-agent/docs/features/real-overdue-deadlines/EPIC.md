# Epic: Real overdue — one deadline-bound computation across every surface

**Status:** In progress
**Component:** Districts (Manage / district-detail / compliance report)   ·   **Persona:** CN Director (Dana) + Implementation (Jaime's team)   ·   **Last updated:** 2026-06-15
**Depends on:** `deadline_store.py` (exists); per-track due dates already used by the E1 roster (`demo_app.py` `/api/roster/{track_id}`)

## Problem statement
"Overdue" drives the whole Districts management story — KPIs, status pills, nudge-all-overdue, the
compliance report — but today it means three different, non-real things on three surfaces:

- **District-detail KPI** counts learners whose status string `=== 'Overdue'` ([`_ddRenderStateB`](../../../static/index.html:12760)) — but seeded rosters from [`_roster_for`](../../../demo_app.py:1582) only ever produce `Not started / In progress / Completed`, so the KPI reads **0** for real seeded districts.
- **Compliance report** defines overdue as "In Progress with `< 20%` completion" ([`_build_compliance_report`](../../../demo_app.py:7103)) — a proxy, unrelated to any deadline.
- **E1 roster** computes `is_overdue` from a real per-track due date — the only surface that's real.

None of them reads [`deadline_store.py`](../../../deadline_store.py). A director acting on these numbers
is acting on three contradictory fictions. This is the canonical façade: it renders, it looks done,
it isn't wired.

## Solution
One server-side computation — `is_overdue(completed, due_date, now, tz)` — bound to a real
per-assignment due date, evaluated in the district's timezone, surfaced once by the API and **read**
(never recomputed) by the KPI, the roster pill, and the compliance report. Change the due date or the
learner's completion and all three move together, because there is only one source of truth.

## Scope
**In scope:** the single computation + data fields it needs (assignment `due_date`, district
`timezone`); the three surfaces above reading it; demonstrated end-to-end on one district (austin-isd).
**Out of scope:** recurring recertification / expiry (separate epic — the bigger CN compliance gap);
real notification delivery; relative-due resolution ("7 days from join"); a timezone-configuration UI
(the field exists and is used; editing it in-app is later); multi-district rollout beyond the demo.

## Design decisions
- **Server computes, UI reads.** The API returns `is_overdue` per roster row + an `overdue` summary; no surface recomputes. This is what makes cross-surface consistency structural, not coincidental.
- **End-of-day, district timezone.** A due date is "end of that calendar day in the district's tz," not a UTC instant — "overdue at midnight" must mean the district's midnight.
- **No due date = not overdue.** Open-ended assignments are surfaced as `no_deadline`, never silently counted overdue.

## User stories
- [ ] [STORY-001: Bind overdue to one real, timezone-aware deadline computation](STORY-001-bind-deadline-to-overdue.md) — the vertical slice.

## Implementation notes
- _(filled as code lands — new module for the computation, `due_date`/`timezone` fields, the three call sites, tests.)_
