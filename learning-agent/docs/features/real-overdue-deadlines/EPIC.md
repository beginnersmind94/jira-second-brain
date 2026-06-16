# Epic: Real overdue — one deadline-bound computation across every surface

**Status:** Done ✓ — STORY-001 shipped (3 slices), verified live (2026-06-15)
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
- **Slice 1 (done):** `overdue.py` — one `is_overdue(completed, due_date, now, tz)` (pure, defensive, end-of-day in tz with a naive fallback) + `tests/test_overdue.py` (7 tests). Wired into `demo_app._build_compliance_report`: the old `<20% complete` proxy is replaced by the real computation for both `summary.overdue` and per-staff status. Verified: report builds, `summary.overdue=0` honestly (deadline 2026-06-30 is future vs report_date 2026-06-15) where the proxy used to show a fake count.
- **Slice 2 (done):** `static/index.html` `_isOverdue` (client mirror of overdue.py); every demo learner seeded with a real `due` date and `status` DERIVED from it (overdue cohort = passed deadline). District KPI / roster pill / My Team / Home overdue counts all became deadline-driven with no call-site changes (they read `l.status`). Verified: Houston 2 / Aldine 3 / Klein 3, derivation consistent.
- **Slice 3 (done):** per-assignment due dates drive overdue — `asnSave` stamps the chosen ISO deadline on matching learners (`_asnLearnerMatch`) + recomputes status; per-district `timezone` added to `_DISTRICTS` and threaded into the compliance report's `is_overdue`. Verified: past deadline → matching learners Overdue; report builds tz-aware.
- **Status:** STORY-001 complete — one deadline-driven, tz-aware "overdue" across the compliance report, district surfaces, and assignment flow. The three-definitions problem is closed. (Future polish: client `_isOverdue` could compute per-district tz via `Intl` instead of local end-of-day; all seeded districts are Central so it's not observable today.)
