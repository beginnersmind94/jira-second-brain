# Customer-Specific Work Across NXT Modules — Academic Year 2025/26

**Prepared for:** Dallas
**Prepared by:** Delivery analysis (Jira MCP + offline classification)
**Date:** 2026-06-02
**Source of record:** `Perseus Jira (5).csv` — full Jira export of the NXT project, 3,661 issues, every issue `Created` between **2025-07-01 and 2026-06-02** (AY25/26 to date), standard issue types only (no sub-tasks).
**Canonical scope query:**
`project = NXT AND issuetype in standardIssueTypes() AND created >= "2025-07-01" AND created < "2026-07-01" ORDER BY created ASC`

> Every figure below traces to a Jira issue key + field in the source CSV. Classification was done by reading each candidate's **Summary + Description + Acceptance Criteria (`customfield_10131`) + Comments** — not by keyword matching. Where a call is debatable it is listed in **§7 Uncertain**, not hidden in a total.

---

## 1. Executive summary

| Headline | Value | Basis |
|---|---|---|
| **Customer-specific development items (AY25/26)** | **27** | qualifying tickets, §4 |
| **Estimated cost @ $5,000/ticket** | **$135,000** | 27 × $5,000 |
| **Share of in-scope development** | **2.39%** | 27 ÷ 1,130 in-scope dev items (§3) |
| Completed (Done) subset | 20 of 27 → **$100,000** | `Resolution=Done` ∪ `Status Category=Done` |

**In one line:** Of ~1,130 enhancement / new-development items worked in NXT this academic year, **27 (2.4%) were tied to a specific customer**, representing **$135K** of dedicated capacity at the $5K/ticket rate. The overwhelming majority of these (25 of 27) entered through **Freshdesk**.

Reported **separately** (see §6) is a **district-migration / implementation program** of **156 items** across all issue types — customer-specific by nature but implementation/services rather than product development, so it is excluded from the percentage above to keep `numerator ⊆ denominator` clean. If it were costed at the same $5K/ticket rate it would add **$415K–$915K** of exposure.

---

## 2. What counts (definitions applied literally)

- **Customer request** = a work item tied to **a single named customer** that required dedicated sprint capacity — including **Freshdesk (FD)-originated** items, **direct** customer requests, and **contractual** obligations.
- **In scope:** enhancements and new development only — issue types **Story, Enhancement, New Feature** (plus any genuine customer enhancement found in Task/Tech-Debt; one was, NXT-70265).
- **Excluded:** Bug fixes and general "fixes" (Bug 1,586; the FD "RCA and Fix" / "BO multiple tasks" debugging tasks), Tech-Debt (88, internal), Epic/Feature containers (would double-count children), Sub-tasks (none in export), and explicit dead tickets ("Ignore, old …": NXT-67060, NXT-67061).
- **Module** = the dedicated `Custom field (Module)` tag (the pre-categorized field, more reliable than parsing summaries).
- **Cost rule:** $5,000 per qualifying ticket (literal).

**Note on "FD":** in this report **FD = Freshdesk** (a request origin). There is also a Jira project keyed `FD = Food Distribution`; it is unrelated and out of scope.

---

## 3. The denominator — in-scope development

| Step | Count |
|---|---|
| Story + Enhancement + New Feature (created in window) | 1,143 |
| − migration dev-type stories (moved to §6) | −12 |
| − "Ignore, old" dead tickets (NXT-67060/67061) | −2 |
| + genuine customer enhancement recovered from Task (NXT-70265) | +1 |
| **In-scope development denominator** | **1,130** |

For context, the full created-in-window population is 3,661: Bug 1,586 · Story 1,058 · Task 718 · Epic 125 · Tech-Debt 88 · Enhancement 78 · New Feature 7 · Feature 1.

---

## 4. Customer-specific development — the 27 qualifying items

### By request type
| Request type | Items | Cost @ $5K |
|---|---|---|
| **Freshdesk (FD)-originated** | 25 | $125,000 |
| **Direct customer request** | 2 | $10,000 |
| Contractual (explicit) | 0 identified | — |
| **Total** | **27** | **$135,000** |

*No item carried explicit contract/SOW/MOU language. Adams 12's Oracle-export work (NXT-69492) is the closest to a contractual integration obligation but entered via Freshdesk #309264, so it is counted as FD.*

### By module
| Module | Qualifying items |
|---|---|
| Accountability | 9 |
| Family Hub | 4 |
| Menu Planning | 4 |
| Eligibility | 3 |
| Inventory · Production · Platform–Data Exchange · SCTV · Item Management · Account Management · Financials | 1 each |

### Named customers (where the ticket names one)
Texas City (3) · Adams 12 (2) · Hill City ISD · Stillwater Area Schools · Mankato · Wadena–Deer Creek Public Schools · Tullahoma. The other **17** qualifying items are FD-originated where the ticket cites the Freshdesk number but not the district by name.

### High-level item list (citations = issue key + field)
**Accountability (9)** — NXT-65541 (FD #289187/213/232/234), NXT-69492 *(Adams 12, FD #309264 — Oracle financial exports)*, NXT-69710 (FD #309797), NXT-70214 (FD #308434), NXT-70215 (FD #308434), NXT-70424 (FD #305261), NXT-70586 (FD #312058), NXT-70587 (FD #311719), NXT-73278 *(Wadena–Deer Creek Public Schools)*.
**Family Hub (4)** — NXT-65504 *(Adams 12, FD #289943)*, NXT-67947 (FD #302464/303154), NXT-70381 (FD #310993), NXT-71821 (FD #264863/279685).
**Menu Planning (4)** — NXT-68249 *(Texas City, FD #303802)*, NXT-68250 *(Texas City — direct)*, NXT-69292 *(Hill City ISD, FD #308059)*, NXT-69463 (FD #303802, Texas City Pre-K).
**Eligibility (3)** — NXT-66821 (FD #295727/296439/314274), NXT-68256 (FD #298990), NXT-70380 (FD #267487).
**Singletons** — Inventory NXT-63908 (FD #287828); Production NXT-71417 (FD #315146); Platform–Data Exchange NXT-71744 (FD #316155, PowerSchool); SCTV NXT-72038 *(Stillwater Area Schools, FD #317174)*; Item Management NXT-72790 *(Mankato, FD #318430/321324)*; Account Management NXT-70265 (FD #311711, recovered from Task); Financials NXT-67479 *(Tullahoma — direct)*.

*Full per-ticket detail, status, dates and evidence quote: `nxt_customer_specific_AY2025-26.csv`.*

---

## 5. Freshdesk cross-check query

```
project = NXT AND issuetype in standardIssueTypes()
  AND created >= "2025-07-01" AND created < "2026-07-01"
  AND text ~ "freshdesk"
```
This is a **cross-check, not the authority.** Jira's `text ~` is a tokenized match that (a) also hits comments and (b) misses bare Freshdesk URLs/IDs. The authoritative FD set is the one read ticket-by-ticket from the CSV (Description + AC + Comments). 2 of the FD-origin items were found only via a **comment** (NXT-69292, NXT-71417), which a description-only scan would have missed.

---

## 6. Migration / implementation program (reported separately)

District migrations name a single customer and consume dedicated capacity, but they are **implementation/data-migration/services work, not product enhancement** — so they are held out of §3/§4. Issue-type-agnostic footprint (any item whose summary references a migration):

| Category | Items |
|---|---|
| Customer-district migrations | 111 |
| Generic / infrastructure migration (e.g. "Inventory Module Migration", untitled "District Migration Testing") | 44 |
| Payment-gateway migration (Authorize.Net → WoodForest) | 1 |
| **Total** | **156** |

By issue type: **Bug 100 · Task 43 · Story 12 · Feature 1.** By customer (where named): **Dilworth 57 · Washburn 46 · Mankato 5 · Anchorage 3.** *(Detail: `nxt_migration_program_categorized.csv`.)*

**Cost-exposure sensitivity** (if the $5K/ticket rule were applied to migration too — flagged because migration is services, where $5K/ticket is a weak proxy):

| View | What it counts | Items | @ $5K |
|---|---|---|---|
| **1 — headline** | Customer-specific development only | 27 | **$135,000** |
| 2 | + migration implementation (Story/Task/Feature, non-bug) | 83 | $415,000 |
| 3 | + migration defects (the 100 migration Bugs) | 183 | $915,000 |

---

## 7. Uncertain / judgment calls (not in the headline 27)

| Ticket | Module | Why uncertain |
|---|---|---|
| NXT-70309 | Financials | General GL posting-frequency feature; Adams 12 cited only as a use-case driver |
| NXT-71628 | Accountability | General deposit/credit-card feature; only the alphanumeric Bank Deposit Slip # is Adams-12-specific |
| NXT-69341 | Family Hub | Austin ISD named as one complainant, but shipped as 5 general settings for all districts |
| NXT-65573 | Accountability | State-level (North Carolina) compliance; names New Brunswick County Schools only as an example |
| NXT-72140 | Eligibility | Federal 2026-27 eligibility guidelines (all districts / regulatory); FD #316868 referenced |
| NXT-68910 | Family Hub | Q1 catch-all of small changes; only one sub-item (FD #307409) is customer-driven |
| NXT-67945 | Family Hub | FD-flagged but reads as a general configurable privacy setting; no single customer |
| NXT-65729 | Family Hub | FD #292500 (Benton School District) but a default-setting flip (Task), minimal dev |
| NXT-70622 | Inspections | Yotta / Clear Creek ISD app-crash fix (Task) — customer-named but a *fix*, not enhancement |

If you decide the productized-but-customer-driven items (NXT-70309, NXT-71628, NXT-69341, NXT-65729) should count, the headline moves to **31 items / $155,000 / 2.7%**.

---

## 8. Insights

- **Freshdesk is the dominant intake channel** for customer-specific work: 25 of 27 (93%). Direct/contractual asks barely register as distinct dev tickets — they mostly arrive as migrations (§6) or via FD.
- **Concentration by module:** Accountability alone holds **9 of 27** (33%), all front-office (Edit Check, claims, attendance, transactions). Family Hub + Menu Planning + Eligibility add another 11. These four modules = **24 of 27 (89%)** — that's where customer escalations turn into dev work.
- **Concentration by customer:** A small set of large/active customers drives most named work — **Adams 12** (Oracle/financial integration, 2 dev items + deposit-slip uncertain) and **Texas City** (Pre-K meal pattern, 3 items) recur. The migration program is even more concentrated: **Dilworth + Washburn = 103 of 156 migration items (66%)**.
- **Future cost exposure:**
  - *Customer-specific dev* runs ~$135K/year and is demand-driven by Freshdesk volume — predictable, modest, hard to cap without changing FD triage.
  - *Migrations are the real lever.* Each onboarding district (Dilworth, Washburn) generated 45–57 tickets, dominated by defects. At $5K/ticket the migration program is a **$415K–$915K** envelope — **3×–7× the entire customer-specific dev spend.** Every new district migration this size adds roughly **$230K–$285K** of ticketed work. If the goal is to bend customer-specific cost, migration defect-reduction (better data-migration tooling/QA) has far more leverage than FD-enhancement throttling.
- **Adams 12 is a watch-item for contractual creep:** its integration needs (Oracle exports, daily GL aggregation, alphanumeric deposit slips) recur across Accountability + Financials and read like contractual obligations even though they enter via FD. Worth confirming whether a contract underlies them.

---

## 9. Limitations & assumptions

- **Created-based window.** Per the agreed query, scope is by **`created`** (work *raised* in AY25/26), 2025-07-01 → 2026-06-02 (today), not a full year and not completion-based. A `resolutiondate` view differs at the edges and was not used because `resolutiondate` is blank on ~11% of even Done items.
- **No structured origin data.** NXT has no Customer / Request-Type / State field (all blank), so customer-specificity and FD/direct/contractual are **text-derived** — hence the explicit Uncertain list and per-ticket reads.
- **Some specs live in Azure DevOps** (`dev.azure.com/.../PrimeroEdge Classic`), unreadable from the CSV (e.g. NXT-67479 Tullahoma); classified from available text and noted.
- **$5K/ticket is uniform** and ignores effort. The phase-split risk (one deliverable split into Planning/Development/Delivery tickets) and the migration services-vs-dev distinction are surfaced as separate views rather than silently folded in.
- **Figures are AY-to-date** (through 2026-06-02); they will grow through the summer boundary.

---

## 10. Deliverables (in `jira-brain/jira-export/`)

| File | Contents |
|---|---|
| `nxt_customer_specific_AY2025-26.csv` | The 27 qualifying items: request type, named customer, module, status, dates, evidence quote |
| `nxt_uncertain_AY2025-26.csv` | The 9 judgment calls with reasons |
| `nxt_migration_program_categorized.csv` | The 156 migration items, categorized + by customer |
| `nxt_classification_all_inscope.csv` | All 1,143 dev tickets labelled (customer-specific / general-product / migration / uncertain / dropped) — full audit trail / denominator |
| `Perseus Jira (5).csv` | Source of record (your upload) |
