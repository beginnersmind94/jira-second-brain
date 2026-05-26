---
title: "Wiki as citation backbone (ANC posture)"
type: decision
date: 2026-05-15
status: committed
revisit: 2026-08-03
---

# Wiki as Citation Backbone — ANC Posture

## Context

By mid-May 2026, jira-brain had compiled 8,847 Jira tickets into 22 concept pages, 8 workflows, and 5 entities. Three concept pages had been hand-enriched into narrative articles (Item Management, Inventory, Accountability). The other 19 — including the Eligibility pilot module — remained four-sentence auto-generated stubs with eight ticket links and no cross-links to other wiki pages.

The Annual National Conference (mid-July 2026) is the deadline for the customer-facing content engine. Five resource types (long-form guide, micro-guide, quick-reference, FAQ, SOP) must be ready for Eligibility by then. Each resource cites the wiki.

Two strategic frames surfaced:
- **Door A — destination.** Bring all 19 stubs to Item-Management-grade narrative before ANC. Cost: ~19 × 4–8 authoring hours plus SME review per page. Charlie becomes the critical path.
- **Door B — citation backbone.** Treat the wiki as the canonical, citable substrate the customer-facing `resources/` consumes. Invest in citation infrastructure (backlinks, search, freshness flags, bidirectional wiki↔resources index) instead of narrative depth. Cost: ~1–2 weeks of pipeline work. Zero new authoring.

Full case context in [WIKI_STRATEGY_CASE.md](../../WIKI_STRATEGY_CASE.md).

## Options considered

1. **Door A** — destination wiki. Rich narrative on all 22 concept pages by ANC.
2. **Door B (naive)** — citation backbone. Draft Eligibility resources directly against the existing stub.
3. **Door B (amended)** — citation backbone with an intermediate **citation packet** artifact per module. Resources draft against the packet, not the stub.

Option 2 was rejected because it produces *citation theater*: the resource cites a wiki page, the wiki page is a thin index of ticket titles, the citation pointer doesn't equal evidence. Anti-hallucination rule 2 (cite or cut) and rule 5 (verify before ready) are violated in spirit even when followed in form.

## Decision

> For ANC, the wiki will operate as a citation backbone. Eligibility will be promoted from stub to **citation packet**, not full narrative article. Narrative wiki enrichment is deferred until after ANC and will be prioritized by customer-resource dependency, SME risk, and observed usage.

The citation packet is a new intermediate artifact, sitting between a wiki concept stub and a customer-facing resource. Packets live at `wiki/packets/<module-slug>.md`, carry `visibility: internal` in frontmatter, and are excluded from customer-facing output. Template at [`templates/citation-packet.md`](../../templates/citation-packet.md). Shape:

- **Safe claims** — claim · source ticket(s) · confidence · customer-facing allowed Y/N
- **Unsafe / unsupported claims** — claims that sound plausible but lack source support
- **Related workflows** — only relationships supported by ticket evidence
- **SME questions** — blocking vs. non-blocking
- **Resource dependencies** — which of the five content types each claim supports

The three existing narrative pages (Item Management, Inventory, Accountability) are reframed as **gold-standard examples** — not as the bar the other 19 must clear by July 14.

## Consequences

**This week:**
1. Add backlinks rendered everywhere (one pass in `build_site.py`).
2. Add `resources/ ↔ wiki/` bidirectional dependency index.
3. Add freshness flags (enforce the existing 90-day stale rule from CLAUDE.md).
4. Add the two Forms training pages to the index navigation.
5. ✓ Eligibility citation packet scaffolded at [`wiki/packets/eligibility.md`](../packets/eligibility.md) from [`templates/citation-packet.md`](../../templates/citation-packet.md). Frontmatter, sections, the worked unsafe-claim example, and three blocking SME questions are in place. Full population (safe claims, related-workflow confirmation, ticket-body reads) is a separate authoring pass.

**Operational changes:**
- ✓ New rule added to CLAUDE.md "Resource & Template Rules" as **Rule 7**: customer-facing resources draft against a citation packet at `wiki/packets/<module-slug>.md`, not directly against a concept stub. Packets carry `visibility: internal` and are excluded from customer-facing output. Published resource citations trace to the underlying ticket / wiki source chain, not the packet itself. Failure mode guarded: citation theater.
- Charlie's bandwidth is protected — SME review attaches to citation packets and the resources that derive from them, not to 19 narrative articles.

**Trade-offs accepted:**
- The wiki becomes less browseable as a destination in the short term. New hires arriving before Q4 may need to onboard against `resources/` rather than `wiki/`.
- The three narrative pages remain the only "readable" concept pages until post-ANC enrichment begins.
- `wiki/decisions/` and `wiki/onboarding/` remain empty through ANC; both are explicitly post-ANC work.

## Kill criteria

Reverse this decision (return to Door A or hybrid) only if:

1. Sam confirms the internal wiki itself is part of the ANC demo (changes the audience from SMEs/team to prospects).
2. Eligibility resources cannot be drafted from the citation packet — i.e., the packet is found to be insufficient as a drafting substrate.
3. SMEs say ticket-level traceability is still insufficient (citation packets don't move the trust needle).
4. Backbone pipeline work takes more than two weeks and starts eating resource-writing time.

## Revisit

**Monday, August 3, 2026** — two weeks after ANC.

Decide at that point which concept pages graduate from evidence pages / citation packets to full narrative articles. Prioritize by:
- Customer-resource dependency (which modules' resources are shipping next)
- SME risk (which modules have had SME-caught accuracy issues)
- Observed usage (which wiki pages are actually being clicked through from resources)

## Sources

- [WIKI_STRATEGY_CASE.md](../../WIKI_STRATEGY_CASE.md) — full case context
- [CLAUDE.md](../../CLAUDE.md) — anti-hallucination rules (load-bearing for the rejection of Door B naive)
- [REPO_STRUCTURE.md](../../REPO_STRUCTURE.md) — wiki/resources separation already encoded in the architecture
- Connectivity audit run 2026-05-15: 0 broken links, 4 orphans, 19 of 22 concept pages have 0 outbound wiki cross-links

No source tickets — this is a meta-decision about the wiki itself, not a product decision derived from Jira.
