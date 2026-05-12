---
title: "Eligibility Onboarding — Citation Audit Trail"
companion_to: "output/eligibility_onboarding.html"
date_compiled: 2026-05-12
maintainer_note: "Re-verify each entry annually. IEG numbers refresh every spring; CEP rules refresh on rulemaking cadence."
---

# Eligibility Onboarding — Citation Audit Trail

This is the audit trail for `output/eligibility_onboarding.html`. Two pools, never mixed: regulatory sources prove federal rules, ticket sources prove product behavior. Every claim in the training cites one or the other.

---

## Verification constraint (important context for the next maintainer)

The HTML rendering tool in the environment that produced this document was blocked from directly fetching `usda.gov`, `fns.usda.gov`, state DOE PDFs, and most regulatory URLs (sandbox returned `host_not_allowed`). Regulatory claims below were extracted from **web-search-surfaced text snippets** that originate from the listed URLs. The URLs are correct and resolve outside the sandbox — but the next person maintaining this document should re-open each URL and confirm the specific fact attributed to it.

This matters because CLAUDE.md's "Cite or cut" and "Verify before ready" rules require direct read of every source. Where direct read was not possible, the citation is annotated `(snippet-confirmed)` so the gap is visible. Treat any `(snippet-confirmed)` row as a "high probability correct, but please re-verify before relying on it for compliance work" entry.

---

## A. Regulatory citations

### A1. Income Eligibility Guidelines

| Tag | Claim | URL | Retrieved | Verification |
|---|---|---|---|---|
| `USDA-IEG-2025` | SY 2025-2026 IEG. Effective **July 1, 2025 – June 30, 2026**. Free = 130% × Federal Poverty Level, Reduced = 185% × FPL, rounded up to next whole dollar. Family of 4 (48 contiguous states + DC + Guam + territories): **$42,107** free / **$59,922** reduced annual. 3.0% YoY increase. Alaska and Hawaii have separate higher tables. | https://www.fns.usda.gov/cn/fr-031325 | 2026-05-12 | snippet-confirmed |
| `USDA-IEG-FR` | Federal Register publication of the same SY 2025-2026 IEG notice (March 13, 2025). | https://www.federalregister.gov/documents/2025/03/13/2025-03821/child-nutrition-programs-income-eligibility-guidelines | 2026-05-12 | snippet-confirmed |
| `USDA-IEG-INDEX` | USDA FNS landing page for all annual IEG announcements. Use this URL each spring to locate the new SY's announcement. | https://www.fns.usda.gov/schoolmeals/income-eligibility-guidelines | 2026-05-12 | snippet-confirmed |
| `USDA-IEG-2026` | SY 2026-2027 IEG announcement (next year — verify availability when refreshing this document). | https://www.fns.usda.gov/schoolmeals/fr-040926 | 2026-05-12 | URL-known, content not retrieved |

**Gap to fix on next maintenance pass:** The full IEG table by household size (1–8) for SY 2025-2026 was not embedded in the training because the source URLs could not be directly fetched in this environment. A maintainer with network access should open USDA-IEG-2025, confirm the family-of-4 figure ($42,107 / $59,922), and replace the partial table in Module 2 with the full HH-size table.

### A2. Community Eligibility Provision (CEP)

| Tag | Claim | URL | Retrieved | Verification |
|---|---|---|---|---|
| `USDA-CEP-FINAL` | Final Rule: "Child Nutrition Programs: CEP — Increasing Options for Schools." Published Sept 26, 2023; effective Oct 26, 2023. CEP multiplier is **1.6**; USDA may set it between **1.3 and 1.6**; multiplier locks for the four-year cycle once elected. | https://www.fns.usda.gov/cn/fr-092623 | 2026-05-12 | snippet-confirmed |
| `USDA-CEP-FINAL-FR` | Federal Register version of the same final rule. | https://www.federalregister.gov/documents/2023/09/26/2023-20294/child-nutrition-programs-community-eligibility-provision-increasing-options-for-schools | 2026-05-12 | snippet-confirmed |
| `USDA-CEP-SUMMARY` | USDA FNS plain-language summary of the CEP final rule. | https://www.fns.usda.gov/cn/cep-final-rule-summary | 2026-05-12 | snippet-confirmed |
| `USDA-CEP-NEW-MIN` | Implementation guidance for the new minimum ISP. **Eligible LEAs/schools: ISP ≥ 25%.** **Nearly eligible: 15% ≤ ISP < 25%.** Previous threshold was 40%. | https://www.fns.usda.gov/cn/cep-new-minimum-isp | 2026-05-12 | snippet-confirmed |
| `USDA-CEP-CYCLE` | Four-year CEP cycle rules. **ISP is calculated as (Identified Students ÷ Enrolled Students) × 100 as of April 1** of the SY prior to electing CEP. Annual recalculation allowed; higher ISP can be adopted in years 2-4 of the cycle. Multiplier and base eligibility lock at year 1. | https://www.fns.usda.gov/cn/cep-statutory-annual-notification-and-publication-requirements | 2026-05-12 | snippet-confirmed |
| `USDA-CEP-ELECTION` | CEP election deadline guidance. **LEAs intending to elect CEP for the following school year must submit a letter of intent to the state agency by June 30** with the April 1 identified-student and enrolled counts. | https://www.fns.usda.gov/cn/cep-statutory-annual-notification-publication-requirements-election-deadline | 2026-05-12 | snippet-confirmed |

### A3. Direct Certification

| Tag | Claim | URL | Retrieved | Verification |
|---|---|---|---|---|
| `USDA-DC` | Federal Register rule on Direct Certification (2011-9457). Categorical sources include **SNAP** (mandatory DC; Healthy Hunger-Free Kids Act 2010), **TANF** (optional DC), **FDPIR** (optional), **foster, homeless, migrant, runaway, Head Start** (categorical but typically via designation rather than DC file). | https://www.federalregister.gov/documents/2011/04/25/2011-9457/direct-certification-and-certification-of-homeless-migrant-and-runaway-children-for-free-school | 2026-05-12 | snippet-confirmed |
| `USDA-DC-MEDICAID` | Medicaid Direct Certification demonstration project. As of 2024, **44 states participate**. | https://frac.org/blog/medicaid-direct-certification-2024 | 2026-05-12 | snippet-confirmed |
| `USDA-DC-95` | Direct Certification Benchmarks and Continuous Improvement Plans. Since SY 2013-2014, states are required to **directly certify 95% of school-age children in SNAP households**. States below 95% must submit a Continuous Improvement Plan to FNS. | https://fns-prod.azureedge.us/cn/direct-certification-benchmarks-and-continuous-improvement-plans | 2026-05-12 | snippet-confirmed |
| `USDA-FNS-DC-PAGE` | USDA FNS Direct Certification overview page (general reference). | https://www.fns.usda.gov/cn/direct-certification | 2026-05-12 | URL-known, not directly retrieved |

### A4. Verification

| Tag | Claim | URL | Retrieved | Verification |
|---|---|---|---|---|
| `USDA-VERIFICATION` | USDA FNS Verification Toolkit. **Standard method ("Error-Prone Sampling"):** verify the lesser of **3% of approved applications on file as of October 1, or 3,000 applications**, rounded up. Draws first from error-prone applications; remainder filled randomly. **Deadline:** complete verification by **November 15**. | https://fns.usda.gov/school-meals/verification-toolkit | 2026-05-12 | snippet-confirmed |
| `USDA-VERIFICATION-ALT` | Two alternate sampling methods. **Alternate One — Random:** verify 3% (or 3,000) of all approved apps, random selection. **Alternate Two — Focused:** verify 1% (or 1,000) of error-prone apps **plus** 0.5% (or 500) of categorically-eligible apps. Alternate Two is the only method that touches categorical apps. | https://www.cde.ca.gov/ls/nu/sn/mb06115.asp (California DOE reproduces federal rule) | 2026-05-12 | snippet-confirmed |
| `USDA-EP-DEF` | Federal statutory definition of error-prone: approved application with reported income **within $100 of the monthly benefit level or $1,200 of the annual benefit level**. Codified in 7 CFR Part 245 and the Eligibility Manual. | https://www.gao.gov/products/gao-15-634t (GAO summary citing federal definition) | 2026-05-12 | snippet-confirmed |
| `USDA-ELIG-MANUAL` | USDA FNS "Eligibility Manual for School Meals: Determining and Verifying Eligibility" — SP36, CACFP15, SFSP11 (July 2017 revision). Reference for categorical eligibility, application processing, and verification. **Eligibility and benefits must be provided within 10 operating days of receiving a complete application.** | https://www.fns.usda.gov/cn/eligibility-manual-school-meals | 2026-05-12 | snippet-confirmed |
| `USDA-ELIG-MANUAL-PDF` | 2017 PDF of the Eligibility Manual (SP36 etc.). | https://fns-prod.azureedge.us/sites/default/files/cn/SP36_CACFP15_SFSP11-2017a1.pdf | 2026-05-12 | snippet-confirmed |

### A5. General reference

| Tag | URL | Retrieved |
|---|---|---|
| `USDA-FNS` | https://www.fns.usda.gov/schoolmeals | 2026-05-12 |

---

## B. Ticket citations

Every product-behavior claim in the training maps to one or more of these tickets. Each ticket lives at `raw/tickets/<KEY>.md` in this repo and was read directly (not surfaced via search).

| Ticket | Summary | Used to ground |
|---|---|---|
| `NXT-141` | Accountability Report - Edit Check Worksheet | Module 7: Edit Check meal-count × eligibility cross-check |
| `NXT-154` | Configuration - Special Assistance Programs | Module 5: CEP/P2 site designation; start/end dates; monthly claiming percentages |
| `NXT-212` | System - Configuration - Special Assistance Programs - CEP Student Analysis | Module 5: CEP configuration flow (district + site level) |
| `NXT-1505` | Eligibility - Reports - Roster tab & grid | Module 7: point-in-time Eligibility Roster with "As of" date |
| `NXT-5228` | Application Entry - Processed: Determination Panel | Modules 2 & 4: Determination Panel (Eligibility + Basis); mixed-application logic; IEG lookup |
| `NXT-5235` | Direct Certification List | Module 3: DC file grid; Assistance Program vs Other Source Categorical distinction |
| `NXT-5591` | Application Details - Eligibility | Module 4: Determination display; IEG graphic on income apps |
| `NXT-5926` | SE - Eligibility Guidelines - Setup | Modules 2 & 4: IEG configuration page; frequency conversion divisors (12 / 24 / 26 / 52) |
| `NXT-5927` | Eligibility - Income Eligibility Guidelines - Get Guidelines | Module 4: IEG pull from hosted platform for self-hosted districts |
| `NXT-10082` | Meal Exceptions - View/Export Eligibility Variance | Module 7: Meal Exceptions list; bulk re-pricing to current eligibility |
| `NXT-10101` | Verification - Dashboard call-to-actions | Module 6: countdown CTAs to verification start/end |
| `NXT-10262` | Notifications Templates - Email Subject Line | Module 4: notification template configuration |
| `NXT-10364` | Verification - Sampling - Generate Sample Backend | Module 6: automated sample generation; Alternate Two rounding system setting; Texas audit-finding rationale |
| `NXT-10517` | Special Assistance Programs - P2 Claiming Percentages - Need to select sites | Module 5: per-site CEP/P2 selection; Paid % auto-recalc |
| `NXT-10703` | Scanning Tool - Allow user to Scan paper form(s) | Module 4: paper-application scanning + OCR + auto application ID |
| `NXT-10706` | Applications - Add - Long form | Module 4: long-form data entry vs wizard |
| `NXT-10707` | Applications - Auto Notify on Process Complete | Module 4: auto-notify-on-processed setting |
| `NXT-10868` | Verification - Sampling - Schedule sampling | Module 6: scheduled sample generation; rolling verification logic |
| `NXT-10880` | Notifications - Household | Module 7: Outreach (household) notifications tab |
| `NXT-10913` | Eligibility - Notifications - Page | Modules 3, 4, 7: Notifications hub with 4 tabs (Applications / DC / Carryover / Outreach) |
| `NXT-10914` | Eligibility - Notifications - Direct Certification | Module 3: DC notifications surfaced on the Notifications page |
| `NXT-10945` | Year Begin - Student Eligibility Updates | Module 7: July 1 carryover insert; CEP free-grace branch; Paid-Default record for non-F/R students |
| `NXT-10955` | Applications - Sessions List | Module 4: per-processor application processing sessions |
| `NXT-10968` | Dashboard (Insights) - Eligibility - Changes Widget | Modules 1 & 7: Insights changes widget; source attribution (Application / DC File / Manual) |
| `NXT-10978` | Routing Navigation - Eligibility | Module 1 context: Eligibility module shape (Insights / Forms / Verification / Direct Certification / Notifications / Reports / Settings) |
| `NXT-11022` | Direct Certification - Automation - Household Extensions | Module 3: auto household extension; DCSBAUTO setting; 2-of-3 criteria match (household / guardian / address) |
| `NXT-11023` | Notifications - Automation - Emails (Applications and DC) | Modules 3 & 4: auto-email setting for applications and DC |
| `NXT-11024` | Auto Notify Completed Applications | Module 4: end-to-end auto-notify on application completion with Family Hub linkage |
| `NXT-11064` | Notifications - SchoolCafe - Direct Certification Notification | Modules 3 & 7: Family Hub linkage when guardian has a SchoolCafé account |
| `NXT-14223` | Direct Certification - Trigger Secondary Matching | Module 3: secondary matching pass for borderline candidates |
| `NXT-14658` | Accountability - Claims - Inclusion of Special Provision programs (CEP/P2) | Modules 5 & 7: claim generation applies CEP/P2 percentages per site |
| `NXT-15507` | Verification - Tracking - Delete application from sample | Module 6: 5% deletion cap; MAXRMVSAMP system setting; replacement application logic |
| `NXT-15895` | Verification - Sampling - Snapshot | Module 6: sample pool snapshot; verification rounding control (Once vs Twice) |
| `NXT-43891` | FO/System - Special Assistance Programs - CEP down to 25% for Identified | Module 5: product update to reflect USDA 40% → 25% threshold change |
| `NXT-66798` | Elig - Apps - Pending Students with multiple matches | Modules 2, 3, 4: Pending Students manual match workflow; Active/Inactive flag on candidate accounts |

---

## C. Persona grounding (per CLAUDE.md Rule 1 — Persona-first)

Before writing role-voiced sentences, I grep'd `raw/tickets/*.md` for `^As a` / `^As an` and listed the personas that appear in Eligibility-adjacent tickets. The training uses only these personas, tagged via ownership pills:

| Ownership tag | Maps to ticket personas | Tickets where verified |
|---|---|---|
| `District` | "Central Office Admin", "Central Office Administrator", "central office user", "district admin", "central office admin", "Application Processor (Anna)", "Director (Vera)", "School Business Official" | NXT-154, NXT-10101, NXT-10913, NXT-15507, NXT-43461, NXT-10945, NXT-10968, NXT-10706, NXT-10913 |
| `Cybersoft` | "Cybersoft Admin", "Cybersoft Implementation team member", "Cybersoft employee", "SchoolCafé Admin" | NXT-10703, NXT-10914 setup work, FRE app HTML template tickets |
| `Parent` | "SchoolCafé parent/guardian", "Family Hub parent/applicant", "applicant" | NXT-11064, NXT-11023, NXT-5228 |
| `System` | The automated background job, written in passive voice in tickets but called out explicitly when a setting drives it | NXT-10945 (year-begin), NXT-11022 (DC household extension), NXT-10868 (verification scheduler), NXT-14223 (secondary matching) |

The training does **not** invent personas. If a step in the training is owned by `District`, it traces back to a ticket where a District-role persona drives that work. If a step is owned by `Cybersoft`, it traces to a ticket where the Cybersoft Implementation or Admin role drives that work.

---

## D. Maintenance checklist

When refreshing this onboarding module:

1. **Annually (each spring/summer):**
   - [ ] Update `USDA-IEG-2025` to the new SY's announcement. Replace the worked example in Module 2 with new HH-of-4 figures.
   - [ ] Update the "current as of" date in the HTML header.
   - [ ] Check USDA Verification Memo for any sample-size tweaks.
   - [ ] Check FRAC Medicaid DC tracker for state count updates.

2. **On rulemaking events:**
   - [ ] CEP multiplier change (1.3–1.6 range): update Module 5 and `USDA-CEP-FINAL`.
   - [ ] ISP threshold change: update Module 5 and `USDA-CEP-NEW-MIN`.
   - [ ] Verification deadline change: update Module 6 and `USDA-VERIFICATION`.

3. **On product changes:**
   - [ ] Year-begin behavior change (NXT-10945 area): refresh Module 7.
   - [ ] DC household extension criteria change (DCSBAUTO): refresh Module 3.
   - [ ] Verification sample percentage change (system settings): refresh Module 6.
   - [ ] Notifications hub structural change (NXT-10913): refresh Modules 3, 4, 7.

4. **Persona drift check:** Re-run `grep -h "^As a\|^As an" raw/tickets/*.md | sort -u` and confirm the ownership tags still map to real personas. If a new persona has emerged in recent tickets, decide whether to map it to an existing tag or add a new one — don't silently merge.

---

## E. What was deliberately left out (and why)

- **Federal per-meal reimbursement rates.** I could not directly verify SY 2025-2026 rates in this environment, so the training describes the rate structure qualitatively ("free pays the district more than paid") without inventing dollar amounts. Add specific rates when a maintainer can verify the annual rate notice on USDA FNS.
- **Full IEG table for all household sizes 1–8.** Same reason — only the family-of-4 figure was confirmed via search-surfaced snippets. The training links to the source URL so a maintainer can fill in the rest.
- **State-specific Direct Certification rules.** The brief defaulted to federal-only; state-level rules vary widely and would expand this document significantly. If training is later tailored to a single state, add a Module 3.5 covering that state's DC file format, cadence, and any state-specific categorical sources.
- **CEP financial modeling.** Module 5 explicitly tells new hires not to advise customers on whether CEP is the right choice — that's the customer's CFO's job. Modeling tools (FRAC, USDA) are referenced but not reproduced.
