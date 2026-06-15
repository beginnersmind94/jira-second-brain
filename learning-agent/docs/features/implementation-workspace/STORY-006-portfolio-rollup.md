# Story 006: Portfolio roll-up + "needs me"

**Epic:** [Implementation Workspace](EPIC.md)
**Status:** Done ✓
**Points:** 3   ·   **Persona:** CS / Implementation (Jaime/Sam)   ·   **Depends on:** STORY-001, STORY-002

## TL;DR
The Districts list now shows each district's **implementation health** (status + % of plan) rolled up
from the workspace — sorted worst-first, with a "Need attention" KPI. Jaime sees her whole book at a
glance and knows where to go, without opening anything.

## Scope
**In scope:** fetch each district's workspace on portfolio load; show status (green/amber/red) + "% of plan" per row; "Need attention" KPI (blocked+at_risk); sort by severity; derive the Stage pill from the workspace.
**Out of scope:** a dedicated "needs me" filtered view/tab (the sort + KPI cover it for now); editing from the portfolio; created-district workspaces (seeded fallback covers them).

## Requirements
1.1 `loadManage` awaits `_loadPortfolioWorkspaces()` → fills `_wsCache[id] = {status, pct, stage}` (parallel fetch, tenant-guarded GET).
1.2 The table's last column is **Implementation**: a status pill (blocked→`pill--urgent`, at_risk→`pill--warning`, on_track→`pill--success`) + "`{pct}% of plan`". Falls back to `_districtStatus` if no workspace.
1.3 KPI strip gains "**Need attention**" = count(blocked or at_risk).
1.4 Rows sort by severity (blocked < at_risk < on_track), then by help request.
1.5 The Stage pill derives from the workspace (`ws.stage`), falling back to `d.stage`.

## Edge / Empty / Error states
| Case | Behavior |
|---|---|
| Workspace fetch fails for a district | falls back to `_districtStatus`/`d.stage`; row still renders |
| No districts blocked/at_risk | "Need attention" KPI hidden |

## Defaults
- Severity order blocked→at_risk→on_track; status colors green/amber/red (also retires the old amber pill collision between "Behind" and "Needs help").

## Acceptance criteria
- [x] **AC1 — per-district implementation health.** ✓ Aldine **Blocked 27%** · Houston **At risk 53%** · Klein **On track 93%**.
- [x] **AC2 — cross-surface consistency.** ✓ Portfolio "% of plan" (27/53/93) equals each district page's workspace overall_pct.
- [x] **AC3 — needs-me surfacing.** ✓ "Need attention" KPI = **2** (Aldine + Houston); rows sort worst-first (Aldine → Houston → Klein).
- [x] **AC4 — stage derives.** ✓ Klein → "Pre-launch" (from uat milestone), not a hand-set field.
- [x] **AC5 — no dead clicks / no errors.** ✓ console errors = none.

> **Done evidence:** verified live on :8011 (sam-trainer) — portfolio read shows the table above, KPI=2, severity sort; %s matched the district pages. No console errors.

## Notes
Frontend-only. `_wsCache` is populated once per portfolio load; the district page remains the source of truth for the detailed view.
