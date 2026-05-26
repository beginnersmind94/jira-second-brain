---
id: elig-reports-quick-reference
title: "Eligibility Reports — Quick Reference"
platform: schoolcafe
module: Eligibility
page: "Eligibility Reports"
content_type: quick-reference
roles: ["director","manager"]
tags: ["reporting","compliance","frequency:on-demand"]
status: draft
template: quick-reference
source_refs:
  - "raw/tickets/NXT-56345.md"
  - "raw/tickets/NXT-56318.md"
  - "raw/tickets/NXT-60134.md"
  - "raw/tickets/NXT-63982.md"
  - "raw/tickets/NXT-21564.md"
updated: 2026-05-13
---

# Eligibility Reports — Quick Reference

**Goal:** pick the right report for the question you're being asked, run it, export it.
**Who:** child-nutrition director or manager.
**When:** monthly compliance review, state audit prep, ad-hoc questions from leadership.

## Pick the right report

| Question you need to answer | Report | Notes |
|---|---|---|
| "How many applications did we receive, by status and reason?" | **Application Counts** | Multi-site, date-filtered |
| "Which students are CEP-identified as of today?" | **CEP Identified Students** | Summary or Detailed; Power BI runner |
| "How many students are DC-eligible, by site?" | **Direct Certification Counts** | Site Code / Site Name is **multi-select** — pick all the sites you need on one run. Source: [[raw/tickets/NXT-63982\|NXT-63982]] |
| "How many students at each price-type reason, by site?" | **Eligibility Summary** (Detailed) | **Compact** groups some price-type reasons under "DC" / "Other"; **Detailed** lists every reason individually. Source: [[raw/tickets/NXT-56345\|NXT-56345]] |
| "Which students changed eligibility in this date range?" | **Eligibility Status Changes** | Date filter applies to the **Process Date**, not Effective Date. Source: [[raw/tickets/NXT-56318\|NXT-56318]] |
| "How many income surveys did we get, by household size and income?" | **Income Surveys** | The Eco-Disadvantaged % option was removed — that wording was confusing when surveys were on. Source: [[raw/tickets/NXT-60134\|NXT-60134]] |
| "Counts of Free / Reduced / Paid by household size?" | **Income Range Count** | Multi-site |
| "Per-student DC matches — the report the USDA review asks for?" | **By Direct Certification** | Migrated from Dundas to native HTML — old bookmarked URLs may 404. Re-bookmark from the Reports page. Source: [[raw/tickets/NXT-21564\|NXT-21564]] |

## Do this

1. Open **Eligibility → Reports**.
2. Click the report name from the table above.
3. Pick **Site(s)**, **Date** (or Date Range), and any report-specific options.
4. Click **GENERATE** (or **APPLY** for grid reports, or **POWERBI (BETA)** for CEP Identified Students).
5. **EXPORT** or **DOWNLOAD** in your preferred format (PDF, Excel).
6. Click **BACK** to return to the Reports landing page.

## Watch out for

- **Eligibility Status Changes** — Grade, Site, and Patron Status reflect **current** state, not historical values at the time of the change.
- **Eligibility Status Changes "Only show Last Eligibility Change"** — dedupes per account; leave it off if you need every change in the range.
- **Compact vs Detailed (Eligibility Summary)** — switching format mid-audit changes the number bucketing. Be explicit about which you ran.
- **Inactive eligibility lines are excluded** from Eligibility Status Changes — won't show on the grid.

## Source

[[raw/tickets/NXT-56345]] · [[raw/tickets/NXT-56318]] · [[raw/tickets/NXT-60134]] · [[raw/tickets/NXT-63982]] · [[raw/tickets/NXT-21564]]
