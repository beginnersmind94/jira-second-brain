---
title: <Module> Citation Packet
packet_for: wiki/concepts/<Module>.md
module: <Module>
status: draft
visibility: internal
sme_status: pending
last_reviewed:
revisit_after:
resource_dependencies: []
source_tickets: []
---

# <Module> Citation Packet

> Internal evidence workbench. Not customer-visible. The packet exists to ground customer-facing resources in claim-level source citations *before* the resource is drafted. Resources draft **against** this packet; they publish citations to the underlying ticket / wiki source chain, never to the packet itself. The packet is a drafting control, not the final authority.

## Safe claims

Claims verified against at least one source ticket read directly. Anti-hallucination rule 5 applies: a ticket-title scan is not a read.

| Claim | Source ticket(s) | Confidence | Customer-facing OK |
|---|---|---|---|
| _Fill in as tickets are read._ | | | |

## Unsafe / unsupported claims

Claims that sound plausible — often from ticket-title co-occurrence or cross-feature pattern matching — but lack direct ticket-body evidence. Listed here so a future drafter does not import them into a resource, and so an SME can convert them to safe or strike them entirely.

Format for each entry:

- **Claim** — one sentence.
  **Reason** — why this is unsafe (what evidence is missing or which anti-hallucination rule would be violated by treating it as safe).
  **SME question** — what to ask to resolve.

- _Fill in as ticket-title patterns are observed without body-level confirmation._

## Related workflows

Workflows that connect to this module *with evidence in the ticket corpus*. Anti-hallucination rule 3 (no cross-feature pattern matching) applies — a workflow appears here only if at least one ticket explicitly ties the module to the workflow.

- _Fill in as workflow connections are verified._

## SME questions

### Blocking (must resolve before publication)

- _Fill in as packet authoring surfaces gaps._

### Non-blocking (resolve when convenient)

- _Fill in as packet authoring surfaces curiosities._

## Resource dependencies

Which of the five customer-facing content types this module's packet feeds. Update as resources are drafted.

- [ ] Long-form guide
- [ ] Micro-guide
- [ ] Quick-reference one-pager
- [ ] FAQ
- [ ] SOP

## Source ticket inventory

The Jira tickets from which this packet draws its evidence. The list grows as the packet matures.

Initial inventory typically comes from the linked concept page's "Representative tickets" section, then expands via `scripts/component_tickets.json` for the module.

| Key | Title (truncated) | Read status |
|---|---|---|
| _Fill in._ | | |
