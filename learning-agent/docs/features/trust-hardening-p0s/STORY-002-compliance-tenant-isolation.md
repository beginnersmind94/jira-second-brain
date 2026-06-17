# Story 002: Enforce tenant isolation on compliance-report endpoints

**Epic:** [Trust hardening](EPIC.md)
**Status:** Not started
**Severity:** P0 · **Audit ref:** P0-2 (Agent 4 F-02)

## Requirement

> A district user can never read another district's data. `/api/districts/{isd}/compliance-report` and `/api/districts/{isd}/compliance-report/pdf` must authenticate the caller and authorize the requested district.

## Why

Confirmed live: `dana-director` (district `houston-isd`) requested `/api/districts/dallas-isd/compliance-report` and got `200` with 24 Dallas ISD staff names. The endpoints have no `current_user` dependency and no `assert_district_access`. With real SSO + roster sync, this is a direct cross-tenant staff-PII leak — a one-way trust break (NFR: tenants isolated "at any layer").

## Acceptance criteria

- [ ] Both endpoints take `current_user: CurrentUser = Depends(get_current_user)` and call `assert_district_access(current_user, isd)` (the same guard `/api/roster` already uses).
- [ ] A director scoped to district A requesting district B's report (json and pdf) → `403`.
- [ ] Sweep all `/api/districts/*` + analytics/compliance routes for the same missing-guard pattern; list any others as follow-up.
- [ ] Regression test for the cross-district `403`.

## Notes

Pattern to copy: `/api/roster?isd=` and `/api/roster/{track_id}` already 403 correctly. Defect at `demo_app.py:~6632 / ~7288`.
