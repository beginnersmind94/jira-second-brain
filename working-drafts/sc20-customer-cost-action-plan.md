# SchoolCafé 2.0 — Customer-Cost Action Plan
**Engagement-lead synthesis of a 5-consultant team · Principal: Rahul Mehta · Sponsor: Dallas · Anchor date: 2026-06-03 · Hard revisit gate: summer-2026 boundary**

> This is a **plan of action**, not a solution and not a re-analysis. The analysis in the case is treated as given. The five workstream plans (Appendices A–E) are integrated here into one sequenced program: a critical path, a decision-forcing register for Dallas, a consolidated RACI, KPIs, risks/kill-criteria, and a combined first-week list.

---

## 0. The shape of the plan in one paragraph
Customer cost is real, material, and invisible because it lives in three systems with no shared customer key. The plan does three things in sequence: **(1) make it visible** (one canonical customer ID + a re-runnable tiered cost report), **(2) feed the constraint** (migration-defect QA on Menu Planning + Eligibility, fed by complexity-based onboarding triage that keeps the cheap 96% off scarce migration engineering), and **(3) govern the re-decision** (a mid-June decision meeting that converts the analysis into authority, and a summer-2026 gate that re-measures before anyone re-invests). The whole program races one clock: the May-2026 uptick says the next onboarding wave is already arriving, so controls must be live *before* the next complex district lands.

---

## 1. The critical path (the lead's job)

Five workstreams, but they are not equal in the schedule. The dependency map:

```
        ┌─────────────────────────────────────────────────────────┐
        │  TOC constraint definition (fast, ~0 dependencies)        │
        │  → feeds DATA module-mapping, OPS triage, the Dallas line │
        └───────────────┬─────────────────────────────────────────┘
                        │
   DATA (UPSTREAM GATE) ▼  freeze baseline · canonical district_id ·
   FD#→NXT join · per-bug detail on the 78 constraint-module defects
        │            │            │              │
        ▼            ▼            ▼              ▼
   FP&A cost-    OPS leading   TOC regression  GOV Dallas memo
   to-serve +    indicator +   suite + KPI     (needs final
   forward model triage feed   feed            hard numbers)
        └────────────┴────────────┴──────────────┘
                        │
                        ▼
        ★ Dallas decision meeting (~mid-June) ★  → decisions unlock spend
                        │
                        ▼
        Summer-2026 boundary  → re-measure, apply kill criteria, re-decide
```

Three facts drive everything:

1. **DATA is the upstream gate.** FP&A's cost model, OPS's leading indicator, and TOC's regression suite all consume DATA's canonical district view, effort proxies, and per-bug defect detail. DATA's Week-1 work is on the critical path for all of them. Good news: the Data consultant found the reproducible scaffolding (`classify_final.py`, `build_audit.py`) already exists — so this is *hardening*, not greenfield.
2. **TOC's constraint definition is the cheap, fast unlock.** It needs almost nothing, feeds three other workstreams, and gives Dallas his one-sentence through-line. Lock it in Week 1. (Note the one tight coupling: DATA needs TOC's authoritative module-to-constraint mapping while TOC needs DATA's per-bug detail — they must sync on day 1, not hand off serially.)
3. **The mid-June Dallas meeting is the hinge.** It is gated only by the *hard* numbers (already reproducible) + TOC's constraint sentence + FP&A's 3-tier framing + OPS's triage feasibility yes/no — all achievable in two weeks. The decisions made there (reporting scope, triage pilot, defect-costing direction) authorize the Phase-1/2 spend. **Do not let the build run ahead of the decision.**

---

## 2. Master timeline (4 phases × 5 workstreams)

Abbreviations: **DATA** (measurement) · **TOC** (constraint ops) · **FP&A** (unit economics) · **OPS** (product-ops/migration) · **GOV** (exec advisory/governance). `★` = critical-path item.

### Phase 0 — Now → ~mid-June (≤2 weeks): *Lock the baseline & force the decision*
**Milestone: Dallas decision meeting (~mid-June).**
- **DATA ★** — Freeze + hash the source extracts (3,661 NXT / 32,378 FD) as an immutable dated baseline; build canonical `district_id` registry v0 + seed exclusions (Edge District, Simplot, global/training sites); resolve **Mankato** (4 spellings → 1); promote **FD#→NXT** to a typed join key; pull per-bug detail on the **78 constraint-module defects**.
- **TOC ★** — Publish the one-page constraint definition + the "constraint has moved" signal rule (provisional thresholds); hand DATA the authoritative module-to-constraint mapping.
- **FP&A** — Lock the 3-tier scope framing; draft the migration-defect-costing **options memo** (dollar impact on Dilworth/Washburn each way); begin effort-band decomposition of the 27 + 156 items.
- **OPS** — Triage rubric v0 (three depth dimensions, *distinct meanings*: Menu Planning/Eligibility = migration-defect risk; Item Management = onboarding-friction signal, not breakage); back-test against the 4 known migrations; co-define the leading-indicator metric with DATA.
- **GOV ★** — Build the 2-page Dallas decision memo (5 messages + 3 decisions + the honesty ladder); pre-wire Dallas in a 15-min 1:1; stand up decision log + RACI v1; send every lead the dependency list with a "need-by 3 business days pre-meeting."
- **Gate:** 3 decisions made (or deferred *with a date*); triage pilot authorized for the incoming wave.

### Phase 1 — Weeks 3–6 (late June): *Build the system & reconcile*
**Milestone: reproducible tiered report + leading-indicator dashboard live.**
- **DATA** — Unified customer-cost view v1 (keyed on `district_id`, carries an `attribution_method` flag: structured / text-derived / inferred); parameterize the 3 tiers as one re-runnable report (wrap `classify_final.py` / `build_audit.py`); wire the leading-indicator feed.
- **TOC** — *Exploit:* QA-hardening sprint; build a migration-defect regression suite from the 78 known bugs; migration data-fidelity checklist for the two modules; publish the subordination principle to OPS.
- **FP&A** — Cost-to-serve-per-district model v1 (structurally separates cheap-tail vs. expensive-few); forward-exposure planning model (baseline ~$0.5–1M/yr, tail $2M+ — every cell labeled *modeled, not forecast*); price TOC's ~$100K-per-complex-migration lever as a lever, not a baseline.
- **OPS** — Harden the self-serve path (import/config/training, Freshdesk-absorbed); wire the indicator dashboard + monthly cadence (May-2026 baseline); sequence the migration-tooling roadmap for the two constraint modules.
- **GOV** — Stand up the decision log + summer-2026 revisit calendar; run the stakeholder roadshow (Finance, Support/Freshdesk, Migration-eng, Product); issue the "stop optimizing X" one-pager; codify the kill criteria as standing governance.

### Phase 2 — Weeks 7–12 (July–Aug, pre-summer boundary): *Operate & instrument ahead of the wave*
**Milestone: live triage on the summer cohort; first migration-tooling increment shipped.**
- **DATA** — Publish data-governance/ownership (named `district_id` owner; the `$5K/ticket` convention as a *governed parameter*, not a buried constant); push for a structured Customer/Contract field in NXT; ship the reconciliation/exception report.
- **TOC** — *Elevate:* ship/sequence migration tooling for the constraint modules (with OPS); protect the migration-engineering buffer during any live complex migration.
- **FP&A** — Embed the anti-linear-extrapolation test (the retired "$250K × 30 = $2–4M" baked in as a visible counter-example); refresh the model against the growing window; carry Adams 12 as a labeled scenario, never as baseline.
- **OPS** — Run live triage on incoming summer districts; ship the first migration-tooling increment for Menu Planning + Eligibility; stand up staffing triggers tied to the indicator.
- **GOV** — Operationalize triage adoption + the change message; get the leading indicator + the constraint-location KPI onto Dallas's dashboard; run a mid-cycle alignment check across all five workstreams.

### Phase 3 — Summer-2026 boundary: *Re-measure & re-decide (the gate)*
- **DATA** — Re-run all 3 tiers on the now-complete window; diff vs. the frozen June baseline (the delta *is* the predicted summer growth); re-classify migration defects under the leadership decision; refresh the registry with the new cohort.
- **TOC** — Re-measure constraint location after the next complex migration; confirm the constraint held or declare it moved.
- **FP&A** — Full re-run; apply kill criteria; deliver a re-invest / stand-down recommendation.
- **OPS** — Recalibrate the triage rubric against actuals (predicted-tier vs. realized-effort confusion matrix); tune thresholds.
- **GOV** — Convene the revisit gate; Dallas re-decides *before* any re-investment.

---

## 3. Decision-forcing register (owner: Dallas)

The plan's job is to put *decisions* in front of Dallas, with options and a recommended default — not to ask permission. Consolidated and de-duplicated across the five workstreams:

### A. Reporting & costing (finance credibility)
| # | Decision | Options | Recommended default | Informed by | Need-by |
|---|---|---|---|---|---|
| 1 | Official customer-cost **reporting scope** | (a) $135K dev-only · (b) all 3 tiers ($135K / +fixes / full footprint) | **(b)** — the headline is never read alone | FP&A, DATA | mid-June |
| 2 | Do migration **DEFECT tickets count at $5K**? *(the single biggest forward-figure lever)* | (a) yes, uniform · (b) discounted defect rate · (c) excluded / separate line | **Model all three; default to a separate labeled line** until TOC supplies an effort basis — make the swing explicit, never hidden | TOC (effort), FP&A (options memo) | present at mid-June; resolve before summer re-run |
| 3 | Fund a **structured Customer/Contract field** in NXT | (a) add + backfill (ends text-derived attribution) · (b) external registry only (cheaper, fragile) | **(a)** | DATA, Rahul | Phase 2 |

### B. Operating policy
| # | Decision | Options | Recommended default | Informed by | Need-by |
|---|---|---|---|---|---|
| 4 | Adopt **complexity-based onboarding triage**? | (a) yes now · (b) pilot on the imminent wave · (c) no | **(b)** — pilot now so it catches the wave; ratify at summer | OPS, TOC | mid-June |
| 5 | **Triage structure** | binary (self-serve / migration) · 3-tier (self-serve / assisted / migration-project) | **3-tier** | OPS | mid-June |
| 6 | **Staffing-trigger authority** when the indicator crosses threshold | pre-authorized within a band · per-instance approval | **Pre-authorized band** | OPS, GOV | Phase 2 |

### C. Governance & resourcing
| # | Decision | Options | Recommended default | Informed by | Need-by |
|---|---|---|---|---|---|
| 7 | Ratify **governance** (decision log, RACI, kill criteria, summer revisit as a hard gate) | approve · modify · defer | **Approve** | GOV | mid-June |
| 8 | Set **provisional KPI thresholds** (constraint-location floor; indicator trigger slope) | adopt provisional now · wait for summer data | **Adopt provisional now, tune at summer** | TOC, OPS | mid-June |
| 9 | Name/fund **role owners** (MDM/registry owner, Analytics Eng, Data-Governance lead, Support/Freshdesk owner) | name them · leave implicit | **Name them** | DATA, OPS | Phase 1 |
| 10 | **Adams 12** — does a contract underlie the recurring integration asks? | confirmed contract → model recurring · ad-hoc → leave in tail · unknown → carry both | **Assign someone to verify; do not assume** | FP&A, OPS, DATA | before it is costed |

---

## 4. Consolidated RACI (role-level; names to confirm — see Decision 9)

| Work item | R | A | C | I |
|---|---|---|---|---|
| Canonical customer ID / entity resolution | MDM Lead | Rahul | OPS, TOC | FP&A, GOV |
| Reproducible tiered cost report | Analytics Eng | Rahul | FP&A (cost rule), TOC (scope) | Dallas |
| Constraint definition + location KPI | TOC Lead | TOC Lead | DATA | Dallas |
| Migration-defect QA / regression suite | QA Lead, Migration-eng | TOC Lead | Module eng leads | Dallas |
| Cost-to-serve + forward model | FP&A | FP&A | DATA, TOC | Dallas, Rahul |
| Complexity triage rubric | OPS Lead | **Dallas** | TOC, Support | FP&A, GOV |
| Self-serve onboarding path | OPS Lead | **Dallas** | Support/Freshdesk | TOC |
| Leading indicator feed | Analytics Eng | OPS Lead | TOC | Dallas, FP&A |
| Migration-tooling delivery | OPS Lead | **Dallas** | TOC (constraint exec) | DATA |
| Decision log, RACI, revisit cadence | GOV | **Dallas** | All leads | Org |
| Kill-criteria / re-run trigger | TOC + DATA | **Dallas** | Rahul | Leadership |
| Stakeholder engagement + change mgmt | GOV | Rahul | Dallas | Stakeholders |

*Proposed roles that should exist:* **MDM Lead** (owns `district_id`), **Analytics Eng** (owns the reproducible report), **Data-Governance Lead** (owns governed parameters + merge approvals), plus confirmed **Support/Freshdesk** and **Migration-eng** owners.

---

## 5. KPIs

**North-star (governance) KPI — constraint location:** % of migration-bug volume sitting in Menu Planning + Eligibility. When it **de-concentrates**, the constraint has moved — that is the signal to re-run before re-investing. The KPI is the constraint's *location*, not a static dollar.

**Leading indicators**
- New-district SC 2.0 **back-office implementation tickets / month** (the wave early-warning; May-2026 baseline; compare to the 2025 summer-ramp slope, not raw counts).
- **Triage false-negative rate** — complex districts mis-routed as simple (the one error that matters most).
- **Attribution quality** — % of customer-cost rows that are `structured` vs. `text-derived` (rises once the NXT field ships).
- **Defect recurrences caught pre-migration** by the regression suite.

**Lagging indicators**
- **Tickets per complex migration** (~50 → ~30 target; ≈ $100K saved each).
- **Expensive-migration conversion rate** stays ≤ ~2–4% of implementing districts.
- **Reproducibility** — the tiered report reproduces to the exact digit on independent re-run.
- **Reporting discipline** — the $135K headline is never reported alone (100% of reports carry all 3 tiers); zero test/vendor entities in any finance rollup.

---

## 6. Risks, caveats & kill criteria

**Standing kill criteria (governance):** if a full year of data shows expensive-migration conversion materially above ~2–4%, **OR** migration defects de-concentrate away from Menu Planning + Eligibility, the constraint has moved — **re-run before re-investing.** Hard revisit at the summer-2026 boundary.

**Top risks → mitigations**
- **$135K read in isolation** → "customers are cheap." → Decision 1 forces all 3 tiers; the number never ships naked.
- **Org resists subordination** (teams defend their volume metrics). → The "stop optimizing X" one-pager pairs each retired metric with its replacement; Dallas sponsors it, doesn't merely suggest it.
- **Mis-triaging a complex district as simple.** → Asymmetric thresholds: any Menu Planning / Eligibility signal biases a district *up* a tier and requires a human confirm before self-serve routing.
- **Text-derived attribution leaks** (no structured Customer field). → Flag `attribution_method` on every row; push Decision 3; never present text-derived counts as audited without the flag.
- **Created-based, AY-to-date window inflates through summer.** → Freeze a dated baseline now; the summer re-run *diffs against it*; no annualizing before the gate.
- **Clustering tail risk ($2M+)** — two districts are already 66% of migration items. → Staffing trigger fires on *clustering*, not average volume; triage *sequences* complex migrations, not just routes them.
- **$5K uniform proxy + unresolved defect-costing.** → Encode cost as a governed parameter; resolve via Decision 2; model both ways.
- **Retired "$2–4M wave" model weaponized against Rahul.** → Pre-empt it: present the self-correction as the credibility spine, not a flaw.
- **Azure DevOps specs unreadable** (e.g., NXT-67479). → Logged as a known coverage gap, not silently dropped.
- **Key-person risk** (analysis lives in Rahul's head). → Decision log + evidence ladder make the reasoning durable and auditable.

**Honesty caveats kept in frame (on every artifact):** one academic year · created-based window (grows through summer) · uniform $5K proxy (defect-costing unresolved) · text-derived attribution · Azure DevOps blind spot · test/vendor entities excluded (Edge District, Simplot) · "Mankato" ×4 spellings · Adams 12 unconfirmed. **The promotion-grade move is to say all of this *and act anyway* — the constraint logic holds regardless of exactly where the dollar lands.**

---

## 7. Week-1 combined action list ("Monday morning")

Merged and de-duplicated across the five workstreams, ordered by criticality:

1. **GOV** — Draft the 2-page Dallas decision memo (5 messages + 3 decisions + honesty ladder); book the pre-wire 1:1 *and* the formal decision meeting; send every lead the dependency need-by list (3 business days pre-meeting).
2. **DATA ★** — Freeze + hash the two source extracts (record 3,661 / 32,378 baselines); create the `district_id` registry and seed exclusions (Edge District, Simplot, global/training); resolve **Mankato** (4 → 1); promote **FD#→NXT** to a typed join key; pull per-bug detail on the **78 constraint-module defects**.
3. **TOC ★** — Publish the one-page constraint definition + the "moved" signal rule (provisional thresholds); send DATA the module-to-constraint mapping; send FP&A the ~$100K throughput logic; send OPS the subordination principle in writing. *(Sync with DATA same-day on the mutual dependency.)*
4. **FP&A** — Draft the 3-tier scope one-pager; write the migration-defect-costing options memo (Dilworth/Washburn impact each way); send DATA the per-ticket effort-proxy request.
5. **OPS** — Draft triage rubric v0; back-test it against the 4 known migrations; send DATA the back-office-ticket-tagging + canonical-ID asks; document the current self-serve Freshdesk reality (Closed %, Training/Demo/Question mix) as the hardening baseline; set the May-2026 indicator baseline.
6. **ALL** — Open the two tracked open questions — **Adams 12 contract** and **role-owner gaps** — as items, *not* assumptions.

---

## 8. The Dallas meeting — narrative arc & positioning Rahul

**Narrative arc**
- **Open (the literal answer):** "You asked how much customer-specific work we did and what it cost. Clean answer: 27 dev items, ~$135K, 2.4% of in-scope dev. Correct and defensible."
- **Pivot:** "That's the answer you asked for. Here's the one you actually need — read alone, $135K says customers are cheap, and that's the wrong lesson. The cost that matters isn't features; it's migration, and it's concentrated."
- **The ask (decisions, not discussion):** report all three tiers; decide whether migration defects count at $5K; pilot complexity-based triage on the incoming wave — each with an owner and a summer revisit.
- **Close (the lever):** "The fix is bounded and cheap — migration QA on Menu Planning and Eligibility saves ~$100K per complex migration. We're not asking for a big bet. We're asking to stop measuring the wrong thing and feed the constraint. Revisit at summer; if the constraint moves, we re-run before we re-invest."

**Positioning Rahul (operator → leader)**
1. **Lead with the reframe, not the data** — his value is recognizing the count answered the wrong question ("the question behind the question").
2. **Make the retired model the credibility asset** — "My earlier framing was $2–4M. When the full export didn't carry it, I killed it." Honesty-as-rigor is the differentiator.
3. **Offer decisions, don't seek approval** — walk in with recommended defaults and revisit dates: the posture of someone who governs.
4. **Name the constraint in one sentence** and own it as the through-line — TOC applied, not just numbers gathered.
5. **Hand Dallas an upward-portable story** he can repeat to *his* leadership without Rahul in the room — that is what makes Rahul look like a leader.

---
---

# Appendices — the five workstream plans (verbatim)

## Appendix A — Data & Measurement Systems (canonical customer-cost data system)

> **Workstream objective.** Make SC 2.0 customer cost a single, re-runnable system of record: one canonical district identity that collapses the four "Mankato" spellings and excludes test/vendor entities, joined across Jira-NXT + Freshdesk + Migrations, producing the three cost tiers ($135K / +fixes / full footprint) reproducible to the digit and defensible under finance/audit — so the number stops being text-derived guesswork.

**Key findings from the repo (accelerators, to confirm against the frozen baseline):** FD# IDs are the existing cross-system link; `named_customer` is the text-derived district field; reproducible scripts already exist (`classify_final.py` → CSVs, `build_audit.py` → audit doc); the three tiers are already computed ($135K / +fixes ~$755K / full footprint ~$1.245M); Edge District = 12 internal-test FD tickets; Simplot = vendor; Adams 12 spans 5 FD tickets + NXT-65504/69492/70309/71628; no structured Customer/Contract field exists.

**Sequenced plan.** *Now→2wk:* snapshot + hash the source-of-record; stand up `district_id` registry v0 with `entity_class`; resolve Mankato + open the Adams 12 confirmation; promote FD#→NXT to a typed join key. *Wk3–6:* unified customer-cost fact table with `attribution_method` flag; parameterize the 3 tiers as one re-runnable report; wire the leading-indicator feed (input from TOC on constraint modules). *Wk7–12:* publish data-ownership/governance ($5K as a governed parameter); push for the structured Customer/Contract field; reconciliation + exception report. *Summer gate:* re-run all tiers on the complete window and diff vs. baseline; re-classify migration defects under the leadership decision; refresh the registry.

**Decisions for Dallas:** (1) fund the structured Customer/Contract field (rec: yes); (2) migration-defect costing in/out of tiers (owner of the dollar rule: FP&A; go/no-go: Dallas); (3) designate the MDM/registry owner of record.

**First week:** freeze + hash the two extracts; create `district_id` + seed exclusions; resolve Mankato + open Adams 12 to OPS; promote FD#→NXT and backfill the two already hand-resolved (NXT-63908, NXT-71417); send FP&A the costing-parameter request and TOC the module-mapping request; put the three decisions on Dallas's desk.

*Assumptions flagged:* MDM Lead / Analytics Eng / Data-Governance Lead roles are proposed, not extant; Adams 12 unconfirmed pending OPS; mid-June frozen extracts assumed to be the agreed summer-diff baseline. No counts/dollars/classifications were re-derived.

---

## Appendix B — Theory-of-Constraints Operations (migration-defect bottleneck)

> **Workstream objective.** Wring maximum migration throughput from the two constraint modules (Menu Planning, Eligibility) before the next complex back-office district lands, and stand up a re-measurement cadence so investment tracks the constraint *as it moves*.

**Sequenced plan (five focusing steps).** *Identify (now→mid-June):* name the constraint precisely (migration-defect remediation capacity in Menu Planning 63 + Eligibility 15 bugs, triggered only by complex back-office districts; Item Management explicitly excluded — its volume is onboarding tasks/stories); define the constraint-location signal. *Exploit (wk3–6):* QA-hardening sprint; migration-defect regression suite from the 78 known bugs; data-fidelity checklist; protect the migration-engineering buffer. *Subordinate (principle set now):* scarce migration-engineering hours reserved for complex back-office districts only — simple/self-serve onboardings must never consume constraint-module capacity (TOC owns the principle; OPS owns the mechanics). *Elevate (wk7–12):* frame migration tooling as throughput economics (~50→~30 tickets ≈ ~$100K saved per complex migration; few per year → ROI sharp but bounded — don't over-build; FP&A prices it). *Don't let inertia set the constraint (summer gate):* re-measure constraint location; it will likely move (Menu Planning → Eligibility → elsewhere).

**Decisions for Dallas:** D1 KPI thresholds (rec: adopt provisional now); D2 defect-ticket costing convention (gates the Elevate dollar figure); D3 tooling go/no-go at M3 against the FP&A-priced case; D4 ratify kill criteria as the binding re-investment gate.

**First week:** publish the one-page constraint definition + location-signal rule (draft thresholds); request per-bug detail on the 78 defects from DATA; send FP&A the throughput logic for pricing; send OPS the subordination principle in writing; book the summer revisit gate and put D1–D4 on Dallas's 1:1.

*Risks/kill criteria:* constraint already moving (>~2–4% conversion or defect de-concentration → stop, re-run); clustering tail ($2M+) — triage must *sequence* complex migrations; measurement artifacts (created-based window; $5K proxy; defect-ticket convention open); unreadable Azure DevOps specs; two-district baseline may not generalize (regression suite is v1, refresh at the gate).

*What to STOP:* spending migration-eng hours on simple onboardings; optimizing the feature-only metric as the management number; front-loading Item Management as if it were a migration bottleneck; treating all 103+ implementing districts as equivalent demand.

---

## Appendix C — FP&A / Unit Economics (defensible dollars)

> **Workstream objective.** Make the dollars defensible: replace the uniform $5K/ticket proxy with an effort/phase-aware basis, deliver a cost-to-serve-per-district model that separates the cheap many from the expensive few, and give Dallas a clearly-labeled forward-exposure planning model with a built-in test that breaks linear extrapolation before it reaches a board.

**Sequenced plan.** *Now→2wk:* lock the 3-tier reporting framing; resolve the $5K-proxy basis (decompose 27 dev + 156 migration items into effort bands using points / cycle-time / comment-volume proxies); frame the migration-defect costing decision as an options memo. *Wk3–6:* cost-to-serve-per-district model v1 (cheap-tail vs. expensive-few); forward-exposure model (baseline ~$0.5–1M; tail $2M+, every cell "modeled, not forecast"); price TOC's ~$100K/migration lever. *Wk7–12:* embed the anti-linear-extrapolation test (the discredited "$250K × 30 = $2–4M" as a visible counter-example with the failure explanation baked in); refresh against the growing window; carry Adams 12 as a labeled scenario. *Summer gate:* full re-run; apply kill criteria.

**Decisions for Dallas:** (1) official reporting scope — pick the headline (rec: lead with +fixes or full footprint so 2.4% is never read alone); (2) do migration defect tickets count at $5K (rec: discounted rate pending TOC's effort basis — the single biggest forward-figure lever); (3) Adams 12 contract or ad-hoc (rec: carry both until OPS confirms; do not assume).

**First week:** draft the 3-tier one-pager to Dallas; ask DATA for the reconciled district view + per-ticket effort proxy; ask TOC for the defect-remediation effort basis + the 50→30 throughput numbers; write the defect-costing options memo (Dilworth/Washburn impact each way); open the Adams 12 question with OPS as an unconfirmed scenario.

*What to STOP:* quoting $135K without the 3-tier wrapper; any per-district uniform-cost math (the $250K × N pattern); precision-chasing on the cheap 96% — spend analytic effort on the expensive few.

*Assumptions flagged:* effort bands proposed, not given; "discounted defect rate" is a placeholder pending TOC; all forward dollars remain MODELED.

---

## Appendix D — Product-Ops / Migration (operating process)

> **Workstream objective.** Stand up a complexity-triage intake that routes the ~96% of districts to a hardened self-serve onboarding path and reserves migration engineering for the few constraint-module districts — with a live back-office-implementation-ticket leading indicator running *before* the summer-2026 wave lands.

**Sequenced plan.** *Now→2wk:* draft triage rubric v0 scoring three depth dimensions with distinct meanings (Menu Planning depth → migration-defect risk; Eligibility depth → migration-defect risk; Item Management depth → onboarding-friction signal, *not* breakage), output routing flag self-serve / assisted / migration-project; define the leading indicator with DATA; back-test the rubric against the ~103 implementing districts and the 4 known migrations. *Wk3–6:* harden the self-serve path (Freshdesk-absorbed); wire the indicator dashboard + monthly cadence (May-2026 anchor); sequence the migration-tooling roadmap for the two modules. *Wk7–12:* run live triage on incoming summer districts; ship the first tooling increment; stand up staffing triggers tied to the indicator. *Summer gate:* recalibrate the rubric against actuals (predicted-tier vs. realized-effort).

**Decisions for Dallas:** D1 triage tiers (rec: 3-tier); D2 staffing-trigger authority (rec: pre-authorized band); D3 confirm/fund Data & Support owner roles; D4 cost convention for tiering (with FP&A).

**First week:** draft rubric v0 and circulate to TOC + Dallas; send DATA the back-office-ticket-tagging + canonical-ID asks (with Mankato/test-entity exclusions named); back-test against the 4 known migrations; book the monthly indicator review and set the May-2026 baseline; document the current self-serve Freshdesk reality as the hardening starting point; put D1–D4 to Dallas as a one-pager.

*Primary risk:* mis-triaging a complex district as simple → asymmetric thresholds bias constraint-module signals *up* a tier and require human confirm before self-serve. *What to STOP:* treating every onboarding as a project; optimizing raw onboarding headcount; non-constraint-module tooling ahead of Menu Planning + Eligibility; using the feature-only metric as the implementation signal.

---

## Appendix E — Executive Advisory, Decision Governance & Change

> **Workstream objective.** Convert the completed analysis into a governed decision — Dallas walks out having chosen a reporting scope, a costing convention, and a triage policy, each with an owner and a summer-2026 revisit — and shift the org from rewarding volume (support tickets, onboarding headcount) to feeding the real constraint.

**Sequenced plan.** *Now→mid-June (Dallas meeting is the milestone):* build the 2-page decision memo (five messages + three decisions + honesty ladder); lock the decision-forcing register; pre-wire Dallas; draft RACI v1 + decision-log template. *Wk3–6:* stand up the decision log + revisit calendar; stakeholder roadshow (Finance, Support/Freshdesk, Migration-eng, Product); issue the "stop optimizing X" one-pager; codify kill criteria as standing governance. *Wk7–12:* operationalize triage adoption + change message; instrument the leading indicator onto Dallas's dashboard; mid-cycle alignment check. *Summer gate:* re-run vs. kill criteria; re-decide before re-investing.

**Decisions for Dallas:** (1) reporting scope (rec: all 3 tiers); (2) defect tickets at $5K (rec: yes, flagged definition-sensitive — make the swing explicit); (3) adopt complexity triage (rec: pilot on the imminent wave); (4) approve governance (decision log + RACI + kill criteria + summer gate); (5) Adams 12 — assign verification, don't assume.

**Dependencies needed BEFORE the meeting:** from DATA — finalized $135K/27/2.4% + the two-district 66% + the 195/~96%/~2-of-~103 figures, reproducible; from TOC — the Menu Planning 63 + Eligibility 15 concentration in one repeatable sentence; from FP&A — the 3-tier framing + ~$0.5–1M baseline / $2M+ tail, labeled MODELED; from OPS — complexity-flag feasibility yes/no.

**First week:** send DATA/TOC/FP&A the dependency list (need-by 3 days pre-meeting); draft the 2-page memo; schedule the pre-wire 1:1 + the formal decision meeting; stand up the decision-log template + RACI v1; open the two questions (Adams 12; role owners) as tracked items.

*Narrative arc and Rahul positioning:* see §8 of the integrated plan above.

*Flagged assumptions:* role owners are placeholders pending confirmation; Adams 12 status is open; mid-June meeting date and summer-2026 boundary taken from the engagement timeline.
