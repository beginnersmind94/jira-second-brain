# SC 2.0 Customer-Cost Action Plan — Analysis Execution Results
**Run:** 2026-06-03 · **Inputs:** Perseus Jira (5).csv (NXT), Data for Dallas June 2 2026.xlsx (Freshdesk), migration bucket. **Numbers as given; this is the build, not a re-derivation of the headline.**

This executes the analytical workstreams (DATA / TOC / FP&A / OPS). Two results **change a conclusion** in the plan — flagged ⚠️.

---

## 1. DATA — entity resolution & joins (the measurement system)
- **District registry built: 199 entities** → **196 customers**, 2 internal/test (Edge District + Cybersoft), 1 vendor (Simplot), 0 global. → `district_registry.csv`
- **Mankato collapsed** 4 spellings → 1 canonical id (`mankato area`). Test/vendor entities carry an `entity_class` flag and are excluded from customer counts.
- **FD#→NXT join key built:** **89 distinct (NXT, FD#) links across 65 NXT issues.** This is the durable cross-system join the plan asked for. → `fd_nxt_join.csv` (broader than the 30 dev-only FD items — it catches FD refs in bugs/tasks too).
- The 3 tiers ($135K / $755K / $1.245M) remain reproducible from `classify_final.py`; this run adds the keyed customer layer underneath them.

## 2. TOC — the constraint, catalogued
- **The 78 constraint defects are now a line-item catalog** (`constraint_defects_78.csv`): Menu Planning 63 + Eligibility 15 bugs, **median cycle time 21 days**, with per-bug comment/sprint detail → seeds the regression suite.
- **Constraint-location KPI baseline = 78%** of migration bugs sit in Menu Planning + Eligibility. That's the north-star; when it falls, the constraint has moved.

## 3. FP&A — effort bands ⚠️ **(this changes Decision 2)**
Replacing the flat $5K with effort signals (story points, cycle time, comment volume, sprint count):

| Class | Small | Medium | Large |
|---|---|---|---|
| Customer dev (27) | 8 | 10 | 9 |
| **Migration (156)** | **137** | **18** | **1** |

**⚠️ Finding:** the 27 dev items are genuinely mixed-size (flat $5K is roughly fair), but **88% of migration tickets are Small-effort** (quick defect fixes, ~21-day median, few comments) — only 1 is Large. **So costing migration at a flat $5K/ticket materially overstates it.** Dilworth's "~$285K" is 57 tickets × $5K, but by effort those 57 are overwhelmingly small. **This is the data answer to Decision 2 (do migration defects count at $5K?): default to a discounted defect rate — the effort isn't there to justify full $5K.** FP&A still needs a $/band rate to finalize the dollar, but the direction is unambiguous: **the migration dollar figures are effort-inflated and should come down.**

## 4. OPS — triage back-test & the leading indicator ⚠️ **(this fixes the indicator)**
- **Cost-to-serve segmentation** (`cost_to_serve_by_district.csv`): of 196 customer districts, the vast majority are **support-only (cheap tail)**; only 4 carry any NXT migration; **2 are "expensive-few"** (Dilworth 57, Washburn 46).
- **Triage rubric back-test — it works on outcome:** routing on migration-ticket volume correctly sends **Dilworth + Washburn → MIGRATION-PROJECT** and **Mankato + Anchorage → assisted**. The 3-tier structure separates the expensive from the light.
- **⚠️ But the leading indicator as specified is broken.** The plan's early-warning = "new-district *Freshdesk* back-office implementation tickets/month." Yet **Dilworth and Washburn — the two expensive migrations — have ZERO Freshdesk implementation tickets** (`fd_impl=0`). They were run as NXT migration projects directly; they never appeared in the FD onboarding stream. **So the FD implementation signal predicts the cheap support-heavy tail, not the expensive migrations.** The correct leading indicator for *cost* is **new `"District Migration — <x>"` items appearing in NXT**, watched alongside the FD stream — not the FD stream alone.

## 5. Forward model — grounded, not extrapolated
| | |
|---|---|
| Implementing customer districts (this year) | **102** |
| …with any NXT migration | 4 (**3.9%**) |
| …with an **expensive** (≥20-ticket) migration | 2 (**2.0%**) — Dilworth, Washburn |
| Expected expensive migrations per ~100 implementing districts | **~2** |
| Forward NXT migration exposure, next comparable cohort | **~2 complex × $230–285K (ticket-count basis) → less on an effort basis (§3)** |

**Net:** baseline forward exposure is **~$0.5M (ticket-basis), lower effort-weighted**; the $2M+ figure is purely the clustering tail (several large districts in one window). The earlier "$2–4M wave" is not supported.

---

## What changed vs. the plan (run it, don't just plan it)
1. **Migration dollars are effort-inflated.** 88% of migration tickets are small-effort → Decision 2 should default to a **discounted defect rate**; the $230–285K per-migration figures drop on an effort basis. *(FP&A)*
2. **The leading indicator was watching the wrong stream.** The expensive migrations bypass Freshdesk entirely (`fd_impl=0`) → watch **new NXT "District Migration" items**, not FD implementation tickets. *(OPS)*
3. **Everything else held:** 78-defect constraint (78% KPI), entity resolution (196 customers, Mankato collapsed), the FD→NXT join, the ~2% expensive-conversion rate, and the triage structure's ability to separate expensive from light.

## Artifacts (`jira-export/analysis/`)
`district_registry.csv` · `fd_nxt_join.csv` · `constraint_defects_78.csv` · `effort_bands.csv` · `cost_to_serve_by_district.csv` · `RESULTS.md`
