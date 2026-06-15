# Story 001: Bind overdue to one real, timezone-aware deadline computation

**Epic:** [Real overdue](EPIC.md)
**Status:** Pending
**Points:** 5   ·   **Persona:** CN Director (Dana) + Implementation (Jaime's team)   ·   **Depends on:** [`deadline_store.py`](../../../deadline_store.py) (exists)

> This story is also the in-repo **reference exemplar** for [`docs/STORY-SPEC-STANDARD.md`](../../../../docs/STORY-SPEC-STANDARD.md).
> It is intentionally `Pending` with all acceptance criteria unchecked — it models the *spec shape*,
> not a finished story.

## TL;DR
Replace three contradictory definitions of "overdue" with one server-side computation bound to a real
per-assignment due date, evaluated in the district's timezone. The KPI, the roster status pill, and
the compliance report all read the same value, so changing a due date moves all three together. The
thing that makes it real: it responds to data — a hardcoded `'Overdue'` label or a `<20%` proxy does
not.

## Scope
**In scope:** one computation function; the `due_date` (assignment) and `timezone` (district) fields
it reads; the three surfaces reading it via the API; demonstrated end-to-end on `austin-isd`.
**Out of scope:** recurring recertification / expiry (separate epic); real email/SMS delivery;
resolving relative dues like "7 days from join" to absolute dates; a UI to edit a district's timezone;
rolling the wiring out to all districts beyond the demonstration. Each is additive later (see Future).

## Requirements
**1. One computation, read everywhere**
1.1 Add `is_overdue(completed: bool, due_date: str | None, now: datetime, tz: str) -> bool` (new module `overdue.py`). Returns `False` if `completed`; `False` if `due_date is None`; else `True` when `now` (converted to `tz`) is past `23:59:59` of `due_date` in `tz`.
1.2 No surface computes overdue inline. The `<20%` proxy at [`demo_app.py:7103`](../../../demo_app.py:7103) and the `status === 'Overdue'` string match at [`index.html:12760`](../../../static/index.html:12760) are both removed and replaced by reads of 1.1's result.

**2. Data the computation needs**
2.1 An assignment record carries `due_date` (`YYYY-MM-DD`) or `null`. (Today [`_initAssignments`](../../../static/index.html:13054) stores free-text `due` like `"Jun 8"` / `"7 days from join"`; absolute dates are used as-is, anything non-absolute is treated as `null` for this slice.)
2.2 A district record carries `timezone` (IANA, e.g. `America/Chicago`), default `America/Chicago`. Added to the four entries in [`_DISTRICTS`](../../../demo_app.py:1564).

**3. Compliance report reads the computation** ([`_build_compliance_report`](../../../demo_app.py:7088))
3.1 `summary.overdue` = count of staff where `is_overdue(...)` is `True`, using the assignment's `due_date` and the district's `timezone`.
3.2 Each staff row's `status` shows `Overdue` when `is_overdue(...)` is `True` (and they are not Complete).
3.3 When the assignment has `due_date = null`, those staff are counted in a new `summary.no_deadline` field and are **not** counted as overdue.

**4. District-detail surfaces read the computation** (UI)
4.1 The KPI "Overdue" tile ([`_ddRenderStateB`](../../../static/index.html:12756)) renders the server-provided overdue count, not a `status === 'Overdue'` filter.
4.2 The roster grid status pill ([`_ddGridRows`](../../../static/index.html:12836)) shows `Overdue` from the server-provided `is_overdue` flag per row.

**5. Consistency by construction**
5.1 `/api/roster` returns `is_overdue` per learner row and an `overdue` (+ `no_deadline`) summary; the UI reads these and does not recompute. The report endpoint and the roster endpoint call the **same** 1.1 function.

## Edge / Empty / Error states
| Case | Behavior |
|---|---|
| District has zero learners | `overdue = 0`, `no_deadline = 0`; no divide-by-zero in completion math |
| Assignment `due_date = null` | learners not overdue; counted in `summary.no_deadline`; report shows "No deadline set" |
| Learner Complete *before* a past due date | not overdue (1.1 short-circuits on `completed`) |
| `now` is the due date, 23:00 district-tz | **not** overdue (due = end of day) |
| `now` is the day after due, 00:30 district-tz | overdue |
| Unknown district id | existing `404` path in the report endpoints unchanged |

## Defaults
- New / non-absolute assignment due → `due_date = null` → not overdue.
- District `timezone` default `America/Chicago`.
- Day boundary = `23:59:59` of `due_date`, evaluated in the district timezone.

## Acceptance criteria  (Given / When / Then — each an executable test on real data)
- [ ] **AC1 — overdue responds to the due date (past).** *Given* `austin-isd`'s cashier assignment `due_date = 2026-06-14` and `now = 2026-06-15`, *When* `/api/roster?isd=austin-isd` is fetched, *Then* every not-Complete cashier row has `is_overdue: true` and `summary.overdue` equals that count.
- [ ] **AC2 — overdue responds to the due date (future).** *Given* the same assignment with `due_date = 2026-06-20`, *When* the roster is fetched on `2026-06-15`, *Then* `summary.overdue = 0` and no row has `is_overdue: true`.
- [ ] **AC3 — Complete is never overdue.** *Given* a learner with `status = Completed` and `due_date = 2026-06-01` (past), *When* the roster is fetched, *Then* that row has `is_overdue: false`.
- [ ] **AC4 — timezone boundary.** *Given* `due_date = 2026-06-15`, district tz `America/Chicago`, *When* evaluated at `2026-06-15T23:00:00-05:00`, *Then* `is_overdue = false`; *When* evaluated at `2026-06-16T00:30:00-05:00`, *Then* `is_overdue = true`. (Unit test against `overdue.is_overdue`.)
- [ ] **AC5 — the proxy is gone.** *Given* the codebase after this change, *When* `_build_compliance_report` is read, *Then* it contains no `< 20` completion-percentage proxy; overdue is computed via `overdue.is_overdue`. (Test asserts the proxy expression is absent / asserts behavior diverges from the old proxy on a crafted row.)
- [ ] **AC6 — cross-surface consistency.** *Given* `austin-isd` with `due_date = 2026-06-14` on `2026-06-15`, *When* the district-detail KPI, the count of roster rows showing the `Overdue` pill, and `GET /api/districts/austin-isd/compliance-report` `summary.overdue` are compared, *Then* all three are the **same number**.
- [ ] **AC7 — no deadline ≠ overdue.** *Given* an assignment with `due_date = null`, *When* the report is built, *Then* those staff appear in `summary.no_deadline`, `summary.overdue` does not include them, and the report renders "No deadline set" for that cohort.

> **Done means:** every AC above checked **with a one-line evidence note** (the request run + observed
> JSON, the screenshot of the three matching numbers for AC6, the test name for AC4/AC5), out-of-scope
> untouched, every edge row exercised, and no new façade — per the Definition of Done in the standard.

## Future option (deferred — nothing built now is thrown away)
- **Recurring recertification / expiry** (own epic): once a learner completes, set `due_date = completion + valid_for`; this same `is_overdue` computation then drives annual recert with zero change. The function is the reuse point.
- **Relative-due resolution** ("7 days from join"): resolve to an absolute `due_date` at assignment time; downstream code already only sees absolute dates, so nothing here changes.
- **Timezone-configuration UI:** the `timezone` field already exists and is read; this only adds an admin control to edit it.

## Notes
- Production-vs-demo: learner identities stay seeded, but overdue becomes a *real computation* over a real `due_date` + the learner's real completion state (live users via `completion_store`, seeded rows via their progress). That is the point — it is no longer a label, so it cannot be faked.
- No spikes in this story. If `zoneinfo` timezone handling on the Windows host needs `tzdata`, that is a real dependency to add, not a stub.
