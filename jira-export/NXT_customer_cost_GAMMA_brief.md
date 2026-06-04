# Customer-Specific Work & Forward Cost Exposure — NXT, AY 2025/26

**For:** Dallas (Director) · **From:** Delivery Analysis · **Date:** 2026-06-02
**Scope:** All NXT modules · `created` 2025-07-01 → 2026-06-02 (academic-year-to-date)
**Evidence base:** 3,661 NXT issues read from a full Jira export; 110 candidates classified by reading Description + Acceptance Criteria + Comments per ticket; cross-checked against 93 Freshdesk customer conversations. Every figure traces to an issue key + field.

---

## ⭐ Bottom line up front

> **You asked how much customer-specific work NXT did this year and what it cost. The answer: 27 customer-specific development items, $135K, 2.4% of development — 93% via Freshdesk. That figure is solid. The reason it's worth your time: in SC 2.0, customer effort lands mostly as support and migrations, not features — and migration cost is concentrated in a few complex districts (~$230–285K each), which is the real number to manage and the one with tail risk.**

- **The answer to your question:** **27** customer-specific development items = **$135K** = **2.4%** of in-scope development (93% Freshdesk-originated).
- **Why that's only part of the picture:** it counts net-new dev only; customer bug-fixes + migrations push the full customer footprint to ~**$1.25M** to date.
- **The real cost engine is concentrated, not broad:** two complex migrations — **Dilworth (~$285K) + Washburn (~$230K)** — are **66% of all migration tickets**. **103 districts onboarded on SC 2.0 this year, but only ~4 needed a major NXT migration** — so cost tracks *complexity*, not district count.
- **The decision it points to:** harden **Item Management + Menu Planning** in the migration path (≈$100K saved per complex migration) and triage onboarding **by complexity, not headcount**. Tail risk: several large districts migrating in one window.

---

## 1 · The headline metrics

| Metric | Value | Source |
|---|---|---|
| In-scope development (enh / new dev) | **1,130 tickets** | Story+Enh+NewFeat, less migrations & dead tickets |
| **Customer-specific development items** | **27** | per-ticket verified |
| **Estimated cost @ $5K/ticket** | **$135,000** | 27 × $5,000 |
| **Share of in-scope dev** | **2.39%** | 27 ÷ 1,130 |
| Completed (Done) subset | 20 → $100,000 | resolution/status = Done |
| Intake channel | **93% Freshdesk** (25 of 27) | 2 direct, 0 contractual |

---

## 2 · What the headline number leaves out

The $135K answers the question as scoped — enhancements only. Worth knowing *why* it's small: in this product, customer-specific work shows up mostly as **bug fixes and migrations**, both scoped out of that figure. Across all 3,661 issues, **249 carry a customer signal** (Freshdesk / named district / migration):

| Customer-signal footprint, by issue type | Items |
|---|---|
| Bug fixes (customer/district defects) | 124 |
| Migration / QA / onboarding tasks | 74 |
| Story | 34 |
| Enhancement | 14 |
| Tech-Debt · Feature | 3 |
| **Total (deduped union)** | **249** |

*Of the 48 Story+Enhancement that carry a signal, **27 are verified customer-specific development** (per-ticket); the rest are migrations, false positives, or uncertain. Only that 27 is in the $135K.*

**Tiered cost view — pick the scope deliberately:**

| Scope | Items | Cost @ $5K | Basis |
|---|---|---|---|
| Verified customer-specific development *(headline)* | 27 | **$135K** | per-ticket |
| + customer-specific bug fixes | 151 | $755K | 27 + 124 (no type overlap) |
| **Deduped customer-signal footprint** | **249** | **≈$1.25M** | union — each issue once (ceiling) |
| Gross additive (also stacks the 156 migration bucket) | 307 | $1.54M | ⚠️ double-counts migration defects already in the 249 |

*The 27 is per-ticket verified; the 249 is a signal-based ceiling (includes some "example-not-customer" mentions). Truth sits between — but ~an order of magnitude above $135K.*

---

## 3 · The real cost engine: district migrations

District migrations are customer-specific and dominate customer cost. The migration bucket holds **156 items** (111 customer-district · 44 generic/infra · 1 payment-gateway):

| | |
|---|---|
| Total migration items | **156** (Bug 100 · Task 43 · Story 12 · Feature 1) |
| Two largest observed clusters | **Dilworth = 57 tickets (~$285K)** · **Washburn = 46 (~$230K)** |
| Observed range per district | **3 → 57 tickets (~$15K–$285K)** — varies sharply by district size |
| Dominated by | **defects** (100 of 156 are bugs) |

**The two largest districts generated 46–57 tickets each; smaller ones far fewer (Mankato 5, Anchorage 3). Large-district migrations are the cost driver — that's the unit economics to manage.**

---

## 4 · 🌊 What's coming — onboarding is large, but cost is concentrated

The full Freshdesk export (32,378 tickets) shows the real SC 2.0 footprint: **195 districts touch SC 2.0; 103 have implementation activity this year** — far more than the brief's earlier "~30." Onboarding is **cyclical**: a summer-2025 ramp (50 new districts in Jul–Aug) and a fresh uptick (**13 new districts in May 2026** = next wave starting).

**But — and this is the key finding — onboarding volume does not equal NXT cost:**

| SC 2.0 reality (AY-to-date) | Value |
|---|---|
| Districts implementing on SC 2.0 | **103** |
| …that generated a **major NXT migration** | **~4** (Dilworth, Washburn, Mankato, Anchorage) |
| …that were **expensive** (~$250K) | **2** (Dilworth, Washburn) |
| SC 2.0 implementation tickets still **open** | **0** (all closed in support) |

> Cost tracks **complexity, not headcount.** ~96% of implementing districts onboard cheaply (self-serve import/config/training, closed in Freshdesk); only complex back-office migrations become Dilworth/Washburn-scale. **Forward model:** budget for a *few* complex migrations/year at ~$230–285K (≈ **$0.5M–$1M** if next year resembles this one); **$2M+ is the tail-risk scenario** if several large districts migrate in the same window — not a baseline. *(Modeled from the observed ~4-of-103 complex-migration rate × the Dilworth/Washburn unit cost — planning model, not forecast.)*

---

## 5 · 🔧 Where the cost is generated — and the lever to cut it

**Migration cost = defects, and the defects concentrate by module** (NXT migration bucket, 156 items):

| Module | Migration defects | Share |
|---|---|---|
| **Menu Planning** | **70** | **45%** |
| **Eligibility** | 29 | 19% |
| **Item Management** | 18 | 12% |
| Platform–Data Exchange · Accountability | 14 · 10 | — |

Separately, SC 2.0 *onboarding-support* volume (Freshdesk) is heaviest in **System/general setup (768 tix), Accountability (626), Eligibility (261)** — the broad live-support load, distinct from the migration-defect concentration above.

**The lever:** harden **Menu Planning + Eligibility + Item Management** data fidelity in the migration path — that's where ~76% of migration defects land. **Cutting a complex migration from ~50 to ~30 tickets saves ≈$100K per migration** — applied to the few complex migrations/year, not every onboarding district.

---

## 6 · 👥 Customer concentration (who drives it)

- **SC 2.0 base (full Freshdesk export):** **195 districts** touch SC 2.0; **103** have implementation activity — a broad base, but the *cost* concentrates in a few complex districts (below).
- **Migration spend:** **Dilworth + Washburn = 103 of 156 items (66%).** Two districts.
- **Named enhancement demand:** Texas City (3), Adams 12 (2), then Hill City ISD, Stillwater, Mankato, Wadena–Deer Creek, Tullahoma.
- **Highest-touch active onboardings** (turn-count = friction / go-live risk): **Southwest ISD (13 tickets, 135 turns)**, Carl Junction (84 turns), Healdsburg (7 tickets), Glastonbury (23 turns on one ticket).
- **Watch — possible contractual creep (needs confirmation):** **Adams 12** integration asks (Oracle exports, daily GL aggregation, alphanumeric deposit slips) recur across Accountability + Financials. No explicit contract language is in the tickets — all entered via Freshdesk — so flag to confirm whether a contract underlies them, don't assume it.

---

## 7 · By module (where customer-specific work lands)

| Module | Customer-specific dev items |
|---|---|
| Accountability | **9** |
| Family Hub | 4 |
| Menu Planning | 4 |
| Eligibility | 3 |
| Inventory · Production · Platform-Data Exchange · SCTV · Item Mgmt · Account Mgmt · Financials | 1 each |

Four modules (Accountability, Family Hub, Menu Planning, Eligibility) = **20 of 27 (74%)** of customer-specific development — front-office, where escalations convert to product. **Accountability alone is 9 of 27 (33%).**

---

## 8 · ✅ Recommendations & decisions needed

1. **Invest in migration QA for Menu Planning + Eligibility + Item Management** *(highest ROI).* These hold ~76% of migration defects (Menu Planning alone 45%). Cutting a complex migration from ~50→~30 tickets saves ≈$100K *per complex migration*.
2. **Triage onboarding by complexity, not count.** Flag back-office-heavy districts at intake — those become the ~$250K cases; the other ~96% onboard cheaply via support. Watch the leading indicator: new-district SC 2.0 *back-office* implementation tickets/month (the May-2026 +13 is the next wave starting).
3. **Decide the official "customer cost" scope** *(two-way door)* — enhancements only ($135K), +fixes ($755K), or full footprint ($1.25M). Recommend reporting all three tiers so the number is never read in isolation.
4. **Create a canonical customer ID.** "Mankato" appears in 4 spellings; any finance rollup that string-matches will fragment. Fix before this reaches the books.
5. **Confirm whether an Adams 12 contract underlies its recurring integration asks** — potential contractual obligation currently logged as ad-hoc FD work.

---

## 9 · How we know (provenance & confidence)

- **Population:** 3,661 NXT issues, single JQL, 100% within the AY window — verified, 0 out-of-range.
`project = NXT AND issuetype in standardIssueTypes() AND created >= "2025-07-01" AND created < "2026-07-01"`
- **Classification:** every one of the 110 candidates read at ticket level (Summary + AC + Description + Comments) — not keyword-matched. False positives caught and excluded (e.g. "response contract" ≠ customer contract; "freshdesk" mentioned as a forum; example districts).
- **Cross-checked** against the full Freshdesk export (**32,378 tickets**; 2,364 SC 2.0; 195 districts; 103 implementing) and 93 not-marked conversations; resolved hidden customer names (e.g. FD#287828 Carl Junction → NXT-63908). Excluded internal/test (**Edge District**) and vendor (**Simplot**) entities.
- **Confidence:** the 27 / $135K / 2.4%, the migration counts, and the 32k/195/103 SC-2.0 counts are **hard** (directly counted). The **forward $ is modeled** (observed ~4-of-103 complex-migration rate × Dilworth/Washburn unit cost) — a planning model, explicitly not a forecast.

**Known limits:** created-based & AY-to-date (grows through summer); no structured Customer/Contract field in NXT (text-derived); some specs live in Azure DevOps (unreadable here); $5K/ticket is uniform and ignores effort/phase-splits. Full narrative + model: `NXT_SC2.0_customer_cost_COMPREHENSIVE.md`.

---

## 10 · Appendix — deliverables (auditable)

| File | Contents |
|---|---|
| `nxt_customer_specific_AY2025-26.csv` | the 27, with FD#/customer/evidence per row |
| `nxt_migration_program_categorized.csv` | the 156 migration items by customer |
| `nxt_classification_all_inscope.csv` | all 1,130 dev tickets labelled (full audit trail) |
| `nxt_uncertain_AY2025-26.csv` | 9 judgment calls (would move headline to 31 / $155K) |
| `Perseus Jira (5).csv` | source of record |

*The 27 customer-specific enhancements, in brief: Accountability NXT-65541, 69492 (Adams 12), 69710, 70214, 70215, 70424, 70586, 70587, 73278 (Wadena–Deer Creek) · Family Hub NXT-65504 (Adams 12), 67947, 70381, 71821 · Menu Planning NXT-68249/68250 (Texas City), 69292 (Hill City ISD), 69463 · Eligibility NXT-66821, 68256, 70380 · + Inventory 63908 (Carl Junction), Production 71417, Platform-DX 71744, SCTV 72038 (Stillwater), Item Mgmt 72790 (Mankato), Account Mgmt 70265, Financials 67479 (Tullahoma).*
