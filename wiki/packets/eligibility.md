---
title: Eligibility Citation Packet
packet_for: wiki/concepts/Eligibility.md
module: Eligibility
status: draft
visibility: internal
sme_status: pending
last_reviewed:
revisit_after: 2026-08-03
resource_dependencies:
  - long-form-guide
  - micro-guide
  - quick-reference
  - faq
  - sop
source_tickets:
  - NXT-70453
  - NXT-70452
  - NXT-70451
  - NXT-70450
  - NXT-70092
  - NXT-69982
  - NXT-66798
  - NXT-63985
---

# Eligibility Citation Packet

> Internal evidence workbench for the Eligibility module — ANC mid-July 2026 pilot, Direct Certification vertical slice. Not customer-visible. Five customer-facing resources draft **against** this packet; their published citations trace to the underlying tickets, never to the packet itself.

> Concept page: [[concepts/Eligibility|Eligibility]] · Component ticket count in the corpus: **432**

## Safe claims

Claims verified against at least one source ticket read directly. Anti-hallucination rule 5 applies: a ticket-title scan is not a read.

| Claim | Source ticket(s) | Confidence | Customer-facing OK |
|---|---|---|---|
| _To be populated. The 8 representative tickets below have not yet been read directly; until they are, this section stays empty._ | | | |

## Unsafe / unsupported claims

- **Eligibility integrates with Forms in some way.**
  **Reason:** Ticket-title co-occurrence is high — 6 of 8 representative tickets on the concept page mention "Forms," "Form Configuration," or "Forms Framework" (NXT-70452, NXT-70451, NXT-70450, NXT-70092, NXT-69982, and arguably NXT-70453's FRE Application Image work). But ticket titles are not evidence (anti-hallucination rule 3 — no cross-feature pattern matching). No ticket body has been read to confirm whether the Forms relationship is (a) a direct dependency, (b) a shared configuration touchpoint, or (c) an artifact of "Forms Framework" being a cross-cutting platform capability.
  **SME question (blocking):** see below.

- _Add additional unsafe claims here as ticket-title patterns surface without body-level confirmation._

## Related workflows

Workflows confirmed by ticket-level evidence (rule 3 — no cross-feature pattern matching).

- _To be verified._ Candidate with high prior: [[workflows/direct-certification|Direct Certification Matching]] — Direct Cert is explicitly the ANC pilot vertical slice and is structurally how part of an eligibility determination is computed. Promotion to a confirmed Related Workflow is pending a direct read of NXT-66798 and the Direct-Cert workflow's own example tickets.

## SME questions

### Blocking (must resolve before publication)

- **Forms relationship.** Is "Forms Framework" a shared platform capability used by Eligibility (and other modules), or an Eligibility-specific subsystem? Resolution determines how Forms is described in every Eligibility resource — and whether Forms gets its own entries in Related Workflows.
- **Direct Certification multi-match policy.** When a student has multiple direct-cert matches (NXT-66798), what is the resolution policy customers should follow? This is load-bearing for the SOP and the FAQ.
- **Income Survey vs. FRE application.** What is the relationship between the Income Survey workflow (NXT-63985) and the standard FRE (Free/Reduced Eligibility) application? Are these alternative paths, sequential, or used by different district types? Determines whether resources describe one funnel or two.

### Non-blocking (resolve when convenient)

- **FRE Application Image.** Is NXT-70453's "FRE Application Image" work a customer-visible capability (district admins configure their own form images) or an internal Cybersoft configuration step (Implementation team configures during onboarding)? Anti-hallucination rule 1 (persona-first) means we cannot describe this until ownership is confirmed.
- **Pending Students transitions.** What triggers a student moving in or out of "Pending" status in NXT-66798?

## Resource dependencies

- [ ] Long-form guide — Eligibility end-to-end
- [ ] Micro-guide — Direct Certification quick path
- [ ] Quick-reference one-pager — Eligibility statuses and transitions
- [ ] FAQ — common district questions about eligibility
- [ ] SOP — how to run a direct-certification import

## Source ticket inventory

Starting set: the 8 representative tickets surfaced on the concept page. Full corpus is 432 Eligibility-tagged tickets — expand via `scripts/component_tickets.json` once initial reads are complete.

| Key | Title (truncated) | Read status |
|---|---|---|
| NXT-70453 | Eligibility - Configuration - FRE Application Image | Not yet read |
| NXT-70452 | Eligibility - Forms - Form Configuration - Form Image Templates Tab | Not yet read |
| NXT-70451 | Eligibility - Forms - Form Configuration - Form Image Templates Tab - Add new im | Not yet read |
| NXT-70450 | Eligibility - Forms - Form Configuration - Forms Tab - Add New Form to grid | Not yet read |
| NXT-70092 | Eligibility - Forms Framework - Form Configuration - Add ability to add/update F | Not yet read |
| NXT-69982 | Eligibility - Forms Framework - Add/update necessary operations, and permissions | Not yet read |
| NXT-66798 | Elig - Apps - Pending Students with multiple matches | Not yet read |
| NXT-63985 | Elig - Reports - Income Survey - Page / Report Updates | Not yet read |

**Suggested next read priority:** NXT-66798 (informs Direct Certification workflow + the blocking multi-match SME question) and NXT-70092 (informs the Forms safe/unsafe question by clarifying whether "Forms Framework" is shared or Eligibility-specific).
