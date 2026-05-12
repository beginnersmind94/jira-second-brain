---
title: "Eligibility Onboarding — Citation Audit Trail"
companion_to: "output/eligibility_onboarding.html"
date_compiled: 2026-05-12
verification_pass: 2026-05-12
maintainer_note: "Re-verify public regulatory entries annually. IEG numbers refresh every spring; reimbursement rates refresh each July; CEP/direct-certification/verification rules refresh on rulemaking cadence."
---

# Eligibility Onboarding — Citation Audit Trail

This is the audit trail for `output/eligibility_onboarding.html`. Two pools, never mixed: **regulatory sources prove federal rules**; **ticket sources prove product behavior**. This 2026-05-12 pass focused on public regulatory research and deliberately did not expand internal product-context references.

---

## Verification status

The prior version of this file contained a sandbox caveat saying regulatory URLs were only `snippet-confirmed`. This pass replaced that with direct reads of primary public sources wherever possible: USDA FNS pages, Federal Register notices, and current eCFR sections.

### Corrections and additions made in this pass

- Corrected the SY 2025-2026 household-of-4 IEG figure for the 48 contiguous states, District of Columbia, Guam, and territories from the prior document's **$42,107 free / $59,922 reduced** to **$41,795 free / $59,478 reduced**.
- Added the full SY 2025-2026 IEG table for household sizes 1-8 for the 48 contiguous states, District of Columbia, Guam, and territories.
- Replaced secondary/summary citations for verification sampling with current **7 CFR 245.6a** primary-source citations.
- Replaced the Medicaid Direct Certification state-count source with USDA FNS's own DC-M page.
- Added SY 2025-2026 federal reimbursement rates for NSLP, SBP, afterschool snacks, and Special Milk Program.
- Marked 2026-2027 IEG as an upcoming refresh source, not the current training source, because the companion onboarding remains grounded in SY 2025-2026 figures.

---

## A. Regulatory citations

### A1. Income Eligibility Guidelines

| Tag | Claim | URL | Retrieved | Verification |
|---|---|---|---|---|
| `USDA-IEG-2025-FNS` | USDA FNS SY 2025-2026 IEG notice. Effective **July 1, 2025 - June 30, 2026**. Free = 130% × Federal Poverty Guidelines; Reduced = 185% × Federal Poverty Guidelines; rounded upward to the next whole dollar. USDA stated the family-of-4 figures increased **3.0%** over the prior year. | https://www.fns.usda.gov/cn/fr-031325 | 2026-05-12 | direct-read |
| `USDA-IEG-2025-FR` | Federal Register publication of the same SY 2025-2026 IEG notice. Primary source for the full IEG table by household size and payment frequency. | https://www.federalregister.gov/documents/2025/03/13/2025-03821/child-nutrition-programs-income-eligibility-guidelines | 2026-05-12 | direct-read |
| `USDA-IEG-INDEX` | USDA FNS landing page for annual IEG announcements. Use this URL each spring to locate the new school year's announcement. | https://www.fns.usda.gov/schoolmeals/income-eligibility-guidelines | 2026-05-12 | direct-read |
| `USDA-IEG-2026-FR` | SY 2026-2027 IEG notice exists and is effective **July 1, 2026 - June 30, 2027**. Use it when refreshing the training for SY 2026-2027; do **not** mix 2026-2027 values into a 2025-2026 training module. | https://www.federalregister.gov/documents/2026/04/09/2026-06842/child-nutrition-programs-income-eligibility-guidelines | 2026-05-12 | direct-read for effective dates/formula; table not transcribed here |

#### SY 2025-2026 IEG table — 48 contiguous states, District of Columbia, Guam, and territories

Source: `USDA-IEG-2025-FR`.

| Household size | Free annual | Free monthly | Free twice monthly | Free every two weeks | Free weekly | Reduced annual | Reduced monthly | Reduced twice monthly | Reduced every two weeks | Reduced weekly |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | $20,345 | $1,696 | $848 | $783 | $392 | $28,953 | $2,413 | $1,207 | $1,114 | $557 |
| 2 | $27,495 | $2,292 | $1,146 | $1,058 | $529 | $39,128 | $3,261 | $1,631 | $1,505 | $753 |
| 3 | $34,645 | $2,888 | $1,444 | $1,333 | $667 | $49,303 | $4,109 | $2,055 | $1,897 | $949 |
| 4 | $41,795 | $3,483 | $1,742 | $1,608 | $804 | $59,478 | $4,957 | $2,479 | $2,288 | $1,144 |
| 5 | $48,945 | $4,079 | $2,040 | $1,883 | $942 | $69,653 | $5,805 | $2,903 | $2,679 | $1,340 |
| 6 | $56,095 | $4,675 | $2,338 | $2,158 | $1,079 | $79,828 | $6,653 | $3,327 | $3,071 | $1,536 |
| 7 | $63,245 | $5,271 | $2,636 | $2,433 | $1,217 | $90,003 | $7,501 | $3,751 | $3,462 | $1,731 |
| 8 | $70,395 | $5,867 | $2,934 | $2,708 | $1,354 | $100,178 | $8,349 | $4,175 | $3,853 | $1,927 |
| Each additional household member | +$7,150 | +$596 | +$298 | +$275 | +$138 | +$10,175 | +$848 | +$424 | +$392 | +$196 |

**Maintenance note:** Alaska and Hawaii have separate higher tables in the same Federal Register notice. The companion onboarding currently uses only the 48-contiguous/DC/Guam/territory table. Add Alaska/Hawaii values only if the training needs state/territory-specific examples.

### A2. Community Eligibility Provision (CEP)

| Tag | Claim | URL | Retrieved | Verification |
|---|---|---|---|---|
| `USDA-CEP-FINAL-FNS` | Final Rule: "Child Nutrition Programs: CEP — Increasing Options for Schools." Published September 26, 2023; effective October 26, 2023. The final rule lowered the minimum identified student percentage (ISP) from **40% to 25%**. | https://www.fns.usda.gov/cn/fr-092623 | 2026-05-12 | direct-read |
| `USDA-CEP-FINAL-FR` | Federal Register version of the same final rule. Confirms CEP reimbursement uses **ISP × 1.6**, capped at 100% free claiming; confirms USDA may set the multiplier between **1.3 and 1.6**. | https://www.federalregister.gov/documents/2023/09/26/2023-20294/child-nutrition-programs-community-eligibility-provision-increasing-options-for-schools | 2026-05-12 | direct-read |
| `USDA-CEP-SUMMARY` | USDA FNS plain-language final-rule summary. Useful non-legal source for training language: lower ISP threshold, 1.6 multiplier, four-year cycle, grace-year framing. | https://www.fns.usda.gov/cn/cep-final-rule-summary | 2026-05-12 | direct-read |
| `USDA-CEP-ECFR-245.9` | Current rule for CEP. **ISP = identified students ÷ enrolled students × 100**. Minimum ISP is **at least 25% as of April 1** of the school year before participating. CEP may be individual-school, group, or LEA-wide. Free claiming percentage = applicable ISP × **1.6**, capped at 100%; paid percentage = remainder. The **1.6 multiplier must be used for the entire four-year cycle**. | https://www.ecfr.gov/current/title-7/subtitle-B/chapter-II/subchapter-A/part-245/section-245.9 | 2026-05-12 | direct-read |
| `USDA-CEP-ELECTION-ECFR` | CEP election documentation deadline. An LEA/group/school intending to elect CEP for the following year must submit documentation to the State agency by **June 30** with counts of identified students and enrolled students as of **April 1** of the prior school year. | https://www.ecfr.gov/current/title-7/subtitle-B/chapter-II/subchapter-A/part-245/section-245.9 | 2026-05-12 | direct-read |
| `USDA-CEP-GRACE-ECFR` | Grace-year rule. A CEP LEA/group/school with ISP below 25% but at least 15% as of April 1 of the fourth year may continue CEP for one additional grace year; if it does not regain the 25% threshold during the grace year, it returns to household applications the following year. | https://www.ecfr.gov/current/title-7/subtitle-B/chapter-II/subchapter-A/part-245/section-245.9 | 2026-05-12 | direct-read |
| `USDA-CEP-NOTIFICATION-ECFR` | Annual public notification thresholds: by April 15, LEAs submit lists of schools with ISP at least 25%, less than 25% but at least 15%, and year-4 CEP schools in the 15%-25% grace-year band; by May 1, State agencies publish the required lists. | https://www.ecfr.gov/current/title-7/subtitle-B/chapter-II/subchapter-A/part-245/section-245.9 | 2026-05-12 | direct-read |

### A3. Direct Certification

| Tag | Claim | URL | Retrieved | Verification |
|---|---|---|---|---|
| `USDA-DC-ECFR-245.6` | Current rule for application, eligibility, and direct certification. SNAP direct certification is mandatory for LEAs conducting eligibility determinations. FDPIR/TANF direct certification is permitted based on appropriate agency documentation. Foster, homeless, migrant, runaway, and Head Start children may be certified free based on documentation from the appropriate agency/official, without further application. | https://www.ecfr.gov/current/title-7/subtitle-B/chapter-II/subchapter-A/part-245/section-245.6 | 2026-05-12 | direct-read |
| `USDA-DC-SNAP-MATCH-ECFR` | Beginning in SY 2012-2013, SNAP direct certification must be conducted using a data-matching technique; household letters may be used only as an additional notice method, not as the primary method. LEAs must conduct SNAP matching at least at the beginning of the school year, three months after the initial effort, and six months after the initial effort. | https://www.ecfr.gov/current/title-7/subtitle-B/chapter-II/subchapter-A/part-245/section-245.6 | 2026-05-12 | direct-read |
| `USDA-DC-HOUSEHOLD-EXTENSION-ECFR` | Household extension applies to SNAP/FDPIR/TANF: if any child is identified as a member of a household receiving SNAP, FDPIR, or TANF, all children in the family are categorically eligible for free meals/milk. It does **not** extend from foster/homeless/migrant/runaway/Head Start status to other household children. | https://www.ecfr.gov/current/title-7/subtitle-B/chapter-II/subchapter-A/part-245/section-245.6 | 2026-05-12 | direct-read |
| `USDA-DC-BENEFIT-TIMING-ECFR` | Once appropriate direct-certification documentation is received, free benefits must be made available as soon as possible and no later than **three operating days** after receipt. | https://www.ecfr.gov/current/title-7/subtitle-B/chapter-II/subchapter-A/part-245/section-245.6 | 2026-05-12 | direct-read |
| `USDA-DC-MEDICAID-FNS` | USDA FNS Direct Certification with Medicaid demonstration page. DC-M uses Medicaid files to identify children eligible for free or reduced-price NSLP/SBP meals without an application. For SY 2024-2025, USDA approved six additional states, bringing participating states to **44**. | https://www.fns.usda.gov/cn/direct-certification-medicaid-demonstration-project | 2026-05-12 | direct-read |
| `USDA-DC-95-ECFR` | Direct Certification benchmark. State agencies must directly certify **95%** of school-age children in SNAP households for SY 2013-2014 and each school year thereafter. A state below the benchmark must submit a Continuous Improvement Plan (CIP) to FNS. | https://www.ecfr.gov/current/title-7/subtitle-B/chapter-II/subchapter-A/part-245/section-245.13 | 2026-05-12 | direct-read |

### A4. Verification

| Tag | Claim | URL | Retrieved | Verification |
|---|---|---|---|---|
| `USDA-VERIFICATION-TOOLKIT` | USDA FNS Verification Toolkit. Useful training source for workflow explanations, notices, and operational resources; use eCFR for primary legal claims. | https://fns.usda.gov/school-meals/verification-toolkit | 2026-05-12 | direct-read |
| `USDA-VERIFICATION-ECFR` | Current primary source for verification requirements. Deadline: LEA verification efforts must be completed by **November 15** each school year; State agency may approve an extension up to **December 15** for specified disruptions. Final required sample size is based on approved applications on file as of **October 1**. | https://www.ecfr.gov/current/title-7/subtitle-B/chapter-II/subchapter-A/part-245/section-245.6a | 2026-05-12 | direct-read |
| `USDA-VERIFICATION-STANDARD-ECFR` | Standard sample size: verify the lesser of **3% of all approved applications as of October 1, selected from error-prone applications**, or **3,000 error-prone applications**. If error-prone applications are insufficient, fill the sample randomly from other approved applications. | https://www.ecfr.gov/current/title-7/subtitle-B/chapter-II/subchapter-A/part-245/section-245.6a | 2026-05-12 | direct-read |
| `USDA-VERIFICATION-ALT1-ECFR` | Alternative One sample size: verify the lesser of **3,000 approved applications selected at random** or **3% of all approved applications selected at random**, as of October 1. | https://www.ecfr.gov/current/title-7/subtitle-B/chapter-II/subchapter-A/part-245/section-245.6a | 2026-05-12 | direct-read |
| `USDA-VERIFICATION-ALT2-ECFR` | Alternative Two sample size: verify the lesser of **1,000 error-prone applications** or **1% of approved applications selected from error-prone applications**, plus the lesser of **500 case-number applications** or **0.5% of applications with case numbers** showing participation in SNAP/FDPIR/TANF. This is about case-number applications, not directly certified households. | https://www.ecfr.gov/current/title-7/subtitle-B/chapter-II/subchapter-A/part-245/section-245.6a | 2026-05-12 | direct-read |
| `USDA-EP-DEF-ECFR` | Error-prone definition: an approved household application indicating monthly income within **$100** or annual income within **$1,200** of the applicable income eligibility limit for free or reduced-price meals. | https://www.ecfr.gov/current/title-7/subtitle-B/chapter-II/subchapter-A/part-245/section-245.6a | 2026-05-12 | direct-read |
| `USDA-VERIFICATION-EXEMPTIONS-ECFR` | Verification is not required for households when all children are determined eligible based on SNAP/FDPIR/TANF documentation from the responsible State/local agency, or when all children are determined foster, homeless, migrant, or runaway. Verification also does not delay approval of applications. | https://www.ecfr.gov/current/title-7/subtitle-B/chapter-II/subchapter-A/part-245/section-245.6a | 2026-05-12 | direct-read |
| `USDA-ELIG-MANUAL-FNS` | USDA FNS Eligibility Manual for School Meals: Determining and Verifying Eligibility, FNS Document # SP 36-2017, CACFP 15-2017, SFSP 11-2017. Use as operational guidance, not as the sole citation when an eCFR rule is available. Page updated February 19, 2026. | https://www.fns.usda.gov/cn/eligibility-manual-school-meals | 2026-05-12 | direct-read |
| `USDA-APPLICATION-10DAY-ECFR` | Income applications: LEA must notify the household of eligibility and provide eligible children the benefits to which they are entitled within **10 operating days** of receiving the application. | https://www.ecfr.gov/current/title-7/subtitle-B/chapter-II/subchapter-A/part-245/section-245.6 | 2026-05-12 | direct-read |

### A5. Federal reimbursement rates

| Tag | Claim | URL | Retrieved | Verification |
|---|---|---|---|---|
| `USDA-RATES-2025-FR` | Federal Register notice for SY 2025-2026 NSLP, Special Milk, and SBP national average payments / maximum reimbursement rates. Effective **July 1, 2025 - June 30, 2026**. | https://www.federalregister.gov/documents/2025/07/24/2025-13879/national-school-lunch-special-milk-and-school-breakfast-programs-national-average-paymentsmaximum | 2026-05-12 | direct-read |
| `USDA-RATES-2025-FNS` | USDA FNS reimbursement rates resource page for SY 2025-2026. Use Federal Register notice above as the primary source when citing exact rates. | https://www.fns.usda.gov/cn/fr-072425 | 2026-05-12 | direct-read |
| `USDA-RATES-INDEX` | USDA FNS reimbursement rates landing page. Use this page each July to find the new annual rate notice. | https://www.fns.usda.gov/schoolmeals/rates-reimbursement | 2026-05-12 | direct-read |

#### SY 2025-2026 reimbursement quick reference — contiguous states / District of Columbia

Source: `USDA-RATES-2025-FR`. Amounts are dollars per meal/snack unless noted.

| Program / rate type | Paid | Reduced-price | Free | Notes |
|---|---:|---:|---:|---|
| NSLP lunch — less than 60% free/reduced in second preceding SY | $0.44 | $4.20 | $4.60 | Includes Section 4 + Section 11 for free/reduced lunches. |
| NSLP lunch — less than 60% + performance-based reimbursement | $0.53 | $4.29 | $4.69 | Performance-based reimbursement adds $0.09. |
| NSLP lunch — 60% or more free/reduced in second preceding SY | $0.46 | $4.22 | $4.62 | Higher Section 4 payment level. |
| NSLP lunch — 60% or more + performance-based reimbursement | $0.55 | $4.31 | $4.71 | Higher level plus $0.09 performance-based reimbursement. |
| NSLP maximum lunch rate | $0.52 | $4.37 | $4.77 | Maximum Federal reimbursement rate before performance-based add-on. |
| NSLP maximum lunch rate + performance-based reimbursement | $0.61 | $4.46 | $4.86 | Maximum rate plus $0.09 performance-based reimbursement. |
| SBP breakfast — non-severe need | $0.40 | $2.16 | $2.46 | Contiguous states / DC. |
| SBP breakfast — severe need | $0.40 | $2.64 | $2.94 | Contiguous states / DC. |
| Afterschool snack | $0.11 | $0.63 | $1.26 | NSLP afterschool care snack rates. |
| Special Milk Program — non-needy half-pint | $0.2675 | N/A | Average cost per 1/2 pint where free milk option applies | Rate is for a half pint of milk; free milk reimbursement is average cost per 1/2 pint in programs with a free option. |

**Maintenance note:** These rates do **not** include USDA Foods or cash-in-lieu of USDA Foods; USDA publishes those values separately.

### A6. General federal reference

| Tag | URL | Retrieved | Verification |
|---|---|---|---|
| `USDA-FNS-SCHOOLMEALS` | https://www.fns.usda.gov/schoolmeals | 2026-05-12 | general reference only |

---

## B. Ticket citations

**Research-pass note (2026-05-12):** per the requested scope, this pass focused on public regulatory research. The internal ticket/product-context citations below are retained for traceability but were not re-verified or expanded in this pass.

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

1. **Annually / each spring:**
   - [ ] Update the IEG source to the new school year's announcement.
   - [ ] Replace the worked example and any embedded IEG table values with the new Federal Register table.
   - [ ] Check whether the companion training should keep using 48-contiguous/DC examples or add Alaska/Hawaii/territory examples.
   - [ ] Update the "current as of" date in the HTML header and this citation file.

2. **Annually / each July:**
   - [ ] Update federal reimbursement rates from the new USDA/Federal Register annual rate notice.
   - [ ] Confirm whether performance-based reimbursement has changed.
   - [ ] Confirm whether USDA Foods / cash-in-lieu values need separate mention.

3. **On rulemaking events or FNS guidance changes:**
   - [ ] CEP minimum ISP threshold: verify 7 CFR 245.9 and the latest FNS CEP guidance.
   - [ ] CEP multiplier: verify whether the statutory/regulatory multiplier remains 1.6 and whether USDA has changed it within the allowed range.
   - [ ] CEP election/public-notification deadlines: verify 7 CFR 245.9.
   - [ ] Direct Certification sources, frequency, household-extension rules, and Medicaid demonstration scope: verify 7 CFR 245.6, 7 CFR 245.13, and the FNS DC-M page.
   - [ ] Verification sample-size rules/deadlines: verify 7 CFR 245.6a and any current FNS verification guidance.

4. **On product changes:**
   - [ ] Year-begin behavior change (NXT-10945 area): refresh Module 7.
   - [ ] DC household extension criteria change (DCSBAUTO): refresh Module 3.
   - [ ] Verification sample percentage change (system settings): refresh Module 6.
   - [ ] Notifications hub structural change (NXT-10913): refresh Modules 3, 4, 7.

5. **Persona drift check:** Re-run `grep -h "^As a\|^As an" raw/tickets/*.md | sort -u` and confirm the ownership tags still map to real personas. If a new persona has emerged in recent tickets, decide whether to map it to an existing tag or add a new one — don't silently merge.

---

## E. What remains deliberately out of scope

- **State-specific Direct Certification rules and file formats.** Federal rules are now verified here; state-level cadence, file layout, and data-sharing details vary and should be researched only when the training is tailored to a particular state.
- **State/local application forms and disclosure language.** This file cites federal application/eligibility rules, but does not attempt to maintain every state agency's household application packet or translated materials.
- **CEP financial modeling beyond federal mechanics.** The formula and federal rate structure are cited, but the training should not advise customers whether CEP is financially optimal. That depends on district participation, meal counts, local costs, State reimbursements, and non-Federal funding assumptions.
- **Internal product behavior beyond the existing ticket map.** Per the 2026-05-12 research scope, this pass did not re-research or rewrite internal product-context references. Use Section B/C only as the product-behavior audit trail.
