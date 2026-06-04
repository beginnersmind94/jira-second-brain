# SC 2.0 (NXT) — Customer Cost & Onboarding Exposure
### Comprehensive analysis, AY 2025/26 (2025-07-01 → 2026-06-02)

**For:** Dallas (Director) · **Prepared by:** Delivery Analysis · **Date:** 2026-06-02

**Evidence base (all figures trace to source):**
1. `Perseus Jira (5).csv` — full NXT export, 3,661 issues created in-window; classified per-ticket.
2. `Data for Dallas June 2 2026.xlsx` — Freshdesk export: 32,378 tickets (`RAW Data`), 93 not-marked-to-NXT (`PCS NXT Not Marked`).
3. `conversations_batch.jsonl` — full Freshdesk message bodies (verbatim quotes).

---

## 1. Executive summary — three numbers, three confidence levels

| # | Finding | Number | Confidence |
|---|---|---|---|
| 1 | **Customer-specific product development** delivered in NXT | **27 items · $135K · 2.4% of dev** | **Hard** (per-ticket verified) |
| 2 | **Migration cost is concentrated, not broad** — 2 complex districts = 66% of it | **Dilworth ~$285K + Washburn ~$230K** | **Hard** (ticket counts) |
| 3 | **SC 2.0 onboarding is large & ongoing but mostly absorbed as support** | **195 districts on 2.0; 103 implementing; ~4 needed major NXT migration** | **Hard base / modeled forward** |

**The one-paragraph story for Dallas:** You asked what customer-specific work cost NXT this year. The clean answer is **$135K of dedicated product development (27 items, 93% via Freshdesk) — ~2.4% of dev.** That number is small *by design of the question*, because in SC 2.0 the customer-specific effort overwhelmingly lands as **support and migrations, not net-new features.** The bigger financial signal is migration: **two complex district migrations (Dilworth, Washburn) each consumed ~$230–285K of ticketed work.** But the headline finding from the full Freshdesk data is that **onboarding cost is concentrated, not linear** — **103 districts implemented on SC 2.0 this year, yet only ~4 generated a major NXT migration.** Most districts onboard cheaply (self-serve imports, config, training, all closed in Freshdesk). **Forward exposure is therefore a function of migration *complexity mix*, not district headcount** — which is both more defensible and more actionable than a flat "$X per district."

---

## 2. Customer-specific development (the question as asked)

- **27 customer-specific development items**, $5K each = **$135,000**, **2.39%** of the 1,130 in-scope dev items (Story/Enhancement/New Feature, less migrations/dead tickets).
- **Intake:** 25 Freshdesk-originated, 2 direct customer requests, **0 explicit contractual**.
- **Completion:** 20 of 27 are Done (`$100K` delivered; remainder in flight).
- **Concentration:** Accountability 9, Family Hub 4, Menu Planning 4, Eligibility 3 = **20 of 27 (74%)**; Accountability alone 33%.
- **Named customers** behind these: Adams 12, Texas City, Hill City ISD, Stillwater, Mankato, Wadena–Deer Creek, Tullahoma, Carl Junction (the rest are FD-originated without a named district).
- *Per-ticket evidence: `nxt_customer_specific_AY2025-26.csv`; audit chain: `NXT_customer_cost_AUDIT.md`.*

This figure is **rock-solid** and is the defensible answer to "customer-specific work at $5K/ticket."

---

## 3. Migration program — the real money, and it's concentrated

| Metric | Value |
|---|---|
| NXT migration items (all types) | **156** (Bug 100 · Task 43 · Story 12 · Feature 1) |
| Dominated by | **defects** (100 of 156) |
| Two largest clusters | **Dilworth 57 tix (~$285K) · Washburn 46 (~$230K)** |
| Concentration | **Dilworth + Washburn = 103 of 156 (66%)** |
| Other named migrations | Mankato 5, Anchorage 3 — **far smaller** |
| Per-district range | **3 → 57 tickets (~$15K → ~$285K)** |

**Takeaway:** migration cost is **bimodal** — a couple of complex, defect-heavy migrations dominate, while others are light. Costing "every migration at ~$250K" overstates; the ~$250K figure is the *complex* case (Dilworth/Washburn), not the average.

---

## 4. The full SC 2.0 customer landscape (from 32,378 Freshdesk tickets)

Most Freshdesk volume is PE Classic; SC 2.0 is a distinct, smaller, fast-growing slice:

| Cut | Value |
|---|---|
| Total Freshdesk tickets (AY-to-date) | **32,378** |
| Touching **SC 2.0** | **2,364 (7%)** |
| SC 2.0 tickets **Closed** | **2,219 (94%)** |
| SC 2.0 "Training/Demo/Question" | **1,562 (66%)** |
| **Distinct districts touching SC 2.0** | **195** |
| **Distinct districts with implementation activity** | **103** |
| SC 2.0 **implementation/migration tickets** | **321** |

**Onboarding is cyclical and re-accelerating** (SC 2.0 implementation tickets / new districts by month):

| Month | Impl tickets | New districts |
|---|---|---|
| 2025-07 | 106 | **37** |
| 2025-08 | 72 | 13 |
| 2025-09 → 12 | 23 / 21 / 8 / 6 | 6 / 11 / 3 / 1 |
| 2026-01 → 04 | 13 / 15 / 18 / 14 | 6 / 4 / 7 / 2 |
| **2026-05** | **25** | **13** ← next wave starting |

- The **summer 2025 ramp** (50 new districts in Jul–Aug) is the start-of-school-year onboarding wave; the **May 2026 uptick (13 new districts)** signals the next one beginning.
- **0 implementation tickets are open** — onboarding work is resolved in Freshdesk, not sitting as backlog.

---

## 5. Forward exposure — modeled honestly, not extrapolated

**The key relationship:** ~103 districts implemented on SC 2.0 this year; only **~4 generated a major NXT migration** (Dilworth, Washburn, Mankato, Anchorage), and **only 2 of those were expensive** (~$250K). So:

- **Onboarding ≠ migration cost.** ~96% of implementing districts cost little in NXT — they onboard via self-serve import/config/training, closed in Freshdesk.
- **The cost driver is complexity** (data volume, BO module depth, defect surface), not the number of districts.
- **Forward model:** budget for a **small number of complex migrations per year at ~$230–285K each**, plus a long tail of light onboardings absorbed by support. If next year's cohort resembles this one, NXT migration cost is **~$0.5M–$1M**; it spikes toward **$2M+ only if several large/complex districts land in the same window** (the genuine tail risk).
- **Leading indicator to watch:** new SC 2.0 districts/month with **back-office (Inventory/Production/Item-Management) implementation tickets** — those are the ones that become Dilworth/Washburn-scale. (Item Management + Menu Planning dominate onboarding friction.)

> Prior framing floated "~30 districts → $2–4M." The full data corrects this: the base is **larger** (103 implementing) but the **conversion to expensive migration is rare (~4%)**, so a flat per-district multiplier overstates. The defensible number is "a few complex migrations/year at ~$250K," with $2M+ as a *concentration-risk* scenario, not a baseline.

---

## 6. What to do with it (recommendations)

1. **Harden Item Management + Menu Planning in the migration path.** They dominate onboarding friction and migration defects. Reducing defects on a complex migration from ~50 to ~30 tickets saves ~$100K/migration — directly attacks the concentrated cost.
2. **Triage onboarding by complexity at intake**, not by count. Flag back-office-heavy districts early; those are the ~$250K cases. Light districts need no migration project.
3. **Track the leading indicator:** new-district SC 2.0 BO implementation tickets/month. The May-2026 uptick (13 new districts) is the signal the next wave is starting — staff ahead of it.
4. **Canonical customer ID.** District names appear in many variants (Mankato ×3 spellings) and the data contains internal/test entities (**Edge District** test env, **Simplot** vendor) — any finance rollup must exclude these and de-dupe, or it will both over- and under-count.
5. **Decide the reported "customer cost" scope** (enhancements $135K / + fixes / full footprint) and report it as tiers, so $135K is never read as the whole.

---

## 7. Confidence, limits, and exclusions (for audit)

- **Hard numbers:** the 27 / $135K / 2.4%; the 156 migration items and Dilworth/Washburn counts; the 32,378 FD / 2,364 SC-2.0 / 195 districts / 103 implementing / 321 implementation-ticket counts. All directly counted from source.
- **Modeled (labeled as such):** the forward dollar exposure. It rests on the observed complex-migration rate (~4 of ~103) and the Dilworth/Washburn unit cost — a planning model, not a forecast.
- **Scope:** created-based, AY-to-date (through 2026-06-02); grows through summer. `$5K/ticket` is a uniform convention that ignores effort and phase-splits.
- **Excluded as non-customer:** **Edge District** (internal test environment), **Simplot** (food-service vendor), "All Districts"/global changes, and SC Training sites.
- **No structured Customer/Contract/State field exists in NXT** — customer attribution is text-derived; an explicit uncertain list is maintained (`nxt_uncertain_AY2025-26.csv`).

---

## 8. Deliverables index

| File | Purpose |
|---|---|
| `NXT_SC2.0_customer_cost_COMPREHENSIVE.md` | this analysis (authoritative) |
| `NXT_customer_cost_GAMMA_brief.md` | 2-page visual brief (Gamma input) |
| `NXT_customer_cost_AUDIT.md` | figure-by-figure citations for the 27/$135K |
| `NXT_onboarding_pipeline_PROOF.md` | district-by-district Freshdesk + NXT proof (the 93 not-marked) |
| `nxt_customer_specific_AY2025-26.csv` · `nxt_migration_program_categorized.csv` · `nxt_classification_all_inscope.csv` · `nxt_uncertain_AY2025-26.csv` | underlying data |
