# Cybersoft's Second Brain: Wiki, or Citation Backbone?

**Case 2026-051 · Internal Knowledge Architecture · Cybersoft, Inc.**
*Prepared for internal discussion. May 15, 2026.*

---

## I. The Click

It was a Thursday morning in mid-May 2026, two months before the Annual National Conference, when Rahul Mehta opened the wiki he had been building for six weeks and clicked into the Eligibility page.

Four sentences.

The page described what eligibility was — household applications, direct certification, paid/reduced/free meal benefits — and listed eight Jira tickets. There were no links to related concepts. No mention of the Direct Certification workflow that lived two folders away. No connection to Forms, even though half the ticket titles on the page included the word "Forms." A footer noted: *Fill in as SMEs review.*

Rahul leaned back. The wiki had 22 concept pages. Three of them — Item Management, Inventory, Accountability — were dense, narrative, cross-linked. The other 19, including Eligibility, looked exactly like this one. A template waiting for a soul.

Eligibility was the pilot module. The deadline for the Annual National Conference, where Cybersoft would unveil its customer-facing content engine, was in mid-July. The Eligibility resources had to be ready by then. And the resources cited the wiki.

The question that had been forming all week now had a shape: *Was he building the wrong thing?*

## II. The Architecture, in Brief

Cybersoft is the school-nutrition software vendor behind SchoolCafe, NXT, and Perseus — a portfolio of integrated modules used by school nutrition departments across the United States. Its product organization runs on Jira: 8,847 tickets across roughly 22 product components, five years of accumulated work, multiple active sprint boards.

In April 2026, Rahul began building **jira-brain**, an internal pipeline that turned Jira into institutional knowledge. The architecture had five layers, documented in `REPO_STRUCTURE.md`:

```
   Jira CSV
      │
      ▼
   raw/tickets/        — 8,847 markdown files, one per Jira issue
      │
      ▼
   wiki/               — Internal compiled knowledge
   ├── concepts/       — 22 product modules (Eligibility, Inventory, …)
   ├── workflows/      —  8 recurring patterns
   ├── entities/       —  5 team / module groupings
   ├── decisions/      — empty by design
   ├── onboarding/     — empty by design
   └── training/       —  3 standalone HTML artifacts
      │
      ▼
   resources/          — Customer-facing publishable entries
   ├── (templates/)    —  5 content types: long-form, micro-guide, quick-ref, FAQ, SOP
   └── catalog/        —  resources.json indexes every published entry
      │
      ▼
   output/site/        — Static HTML, regenerable from the layers above
```

The intent was clean separation. `wiki/` held internal narrative — the institutional memory a new hire could absorb. `resources/` held customer-facing deliverables — what the field team would hand to a district administrator. Each resource had to cite at least one wiki page or ticket. Wiki pages cited tickets in `raw/`.

The team was small. Rahul built the pipeline. Sam led design and product strategy. Charlie served as the liaison to subject-matter experts inside Cybersoft. There were no other engineers on the wiki project.

By mid-May, the pipeline worked end-to-end:

- `ingest.py` mirrored Jira into `raw/tickets/`.
- `analyze.py` produced corpus statistics — component frequencies, sprint groupings, phrase counts.
- `compile_wiki.py` auto-generated concept and workflow stubs.
- `build_site.py` rendered the entire collection to static HTML.

The first compilation pass, on April 20, produced two narrative concept pages. A second pass the same day, using a generic template, emitted 20 more concept pages — including Eligibility — plus 8 workflow pages. The auto-compiler followed a strict write-if-absent rule: it would never overwrite a page that already existed. The narrative pages had been preserved across subsequent runs; the stubs had stayed stubs ever since. Accountability was later hand-enriched, bringing the count of narrative pages to three.

## III. The Anti-Hallucination Rules

In an earlier session, Rahul had discovered that Claude — the AI assistant used throughout the pipeline — could quietly fabricate plausible-sounding capabilities when asked to write customer-facing copy. A persona drift bug in an onboarding draft had taught the team that "reads well" and "is accurate" were different standards. The lesson was hard enough that he had encoded five anti-hallucination rules into `CLAUDE.md`:

> 1. **Persona-first, always** — verify the actor in every sentence against source tickets.
> 2. **Cite or cut** — every non-obvious claim names its source before it ships.
> 3. **No cross-feature pattern matching** — capability claims do not import between feature areas.
> 4. **Tag ownership on every action** — every step in an onboarding doc names its owner.
> 5. **Verify before ready** — every claim traces to a source that has been read directly.

These rules constrained the wiki in a specific way: a "Related concepts" cross-link could not be invented from gut feel. It had to derive from evidence — usually ticket-level co-occurrence in `component_tickets.json`. The rules made the wiki trustworthy. They also made it slow to write.

## IV. What Worked, and What Didn't

By the second week of May, the wiki was technically complete and architecturally clean. It also felt thin.

**Exhibit 1: Concept page depth (source markdown, 22 pages)**

| Page | Source lines | Outbound wiki cross-links | Ticket links |
|---|---:|---:|---:|
| Item Management | 46 | 5 | 20 |
| Inventory | 48 | 5 | 20 |
| Accountability | 50 | 4 | 17 |
| Eligibility | 44 | **0** | 8 |
| Financials | 42 | **0** | 8 |
| Menu Planning | 44 | **0** | 8 |
| Production | 44 | **0** | 8 |
| Account Management | 44 | **0** | 8 |
| (14 more concept pages) | 38–44 | **0** | 8 |

Three pages had narrative substance. Nineteen pages were stubs that had not been touched in 25 days.

**Exhibit 2: Connectivity audit (May 15, 2026)**

A static crawl of the rendered site, starting from the five top-level navigation pages and following every `<a href>`:

- **8,891** pages crawled (including all 8,847 ticket pages).
- **0** broken links.
- **4** orphan wiki pages with no inbound link from the navigation tree:
  - `wiki/index.html` — legacy build artifact, superseded by the top-level index.
  - `wiki/log.html` — append-only ingestion log.
  - `wiki/training/forms-onboarding.html` — Configurable Forms summary for internal / leadership audience.
  - `wiki/training/forms-customer-onboarding.html` — Configurable Forms one-pager for customers.

The two Forms training pages were not abandoned content. `REPO_STRUCTURE.md` documented them explicitly as legitimate deliverables. They had simply never been added to the index.

**Exhibit 3: Inbound-link distribution per wiki page**

The three narrative concepts had 5–6 inbound links each. Most stubs had 2–4. The Forms training pages, the log page, and the legacy index had 0. Connectivity was structurally adequate at the index level — every page that *should* be reachable from the top navigation, was — but density inside the wiki was concentrated in a handful of nodes.

## V. Two Doors

When Rahul described the problem to Sam over Slack — "click any of the 19 stubs and you see four sentences" — the conversation surfaced two genuinely different ways forward, neither of which was free.

### Door A: The wiki is a destination.

Treat the wiki as the place a new hire opens on day one and learns the product from. Each of the 19 stubs gets the Item Management treatment: a narrative author reads the source tickets, identifies 3–5 sub-themes, writes prose that explains how the module shows up in practice, and cross-links to the related concepts, workflows, and entities. The "Fill in as SMEs review" placeholder becomes a stable, browseable, citation-rich article.

**Cost:** roughly 19 modules × 4–8 hours of authoring per module, plus SME review cycles for each. Two months to the ANC deadline; only one of those months is fully available before Eligibility resources need to ship. The work cannot be parallelized without more authors. The five anti-hallucination rules apply to every paragraph.

**Benefit:** a wiki that justifies its name. New hires onboard against it. Engineers reference it before they ask. The customer-facing resource center cites a substrate that is itself worth reading. The wiki becomes a recruiting and retention asset, not just a pipeline output.

### Door B: The wiki is a citation backbone.

Treat the wiki as the canonical, citable source the customer-facing `resources/` consumes. Stop trying to make the stubs into articles. Invest instead in **citation infrastructure**:

- **Backlinks rendered everywhere.** Every wiki page shows what cites it — including which published `resources/` entries depend on it. This is generated from the existing forward-link index in `build_site.py`; the cost is one pass at build time.
- **Search that knows what a concept is.** The current site has none. Twenty-two pages and 8,847 tickets are not navigable without it.
- **Freshness signals.** `CLAUDE.md` already documents a linting rule — *flag pages with no new tickets in 90+ days as stale* — that the pipeline does not enforce. Surface it on every page.
- **Wiki ↔ resources bidirectional index.** When `resources/eligibility/eligibility-faq.md` cites `wiki/concepts/Eligibility.md`, the concept page shows "Cited by 3 published resources." The wiki becomes visibly upstream of customer work.

**Cost:** roughly 1–2 weeks of pipeline work and zero new authoring.

**Benefit:** a wiki that does one job exceptionally well, defers narrative depth to the system already designed to handle it (`resources/`), and survives the team's bandwidth limits before ANC. Trust comes from citation accuracy, not prose quality.

**Risk:** the wiki becomes invisible — a backend store nobody opens. If `resources/` carries all the readable content, the wiki is reduced to a metadata layer. New hires onboard against `resources/` and the customer-facing surface, not against the institutional memory the wiki was supposed to be.

## VI. The Stakeholder Map

Each stakeholder had a different stake in the choice.

- **Sam (design / PM)** wanted the customer-facing content engine to ship on time. Sam's evaluation criterion was: *does the ANC demo work?* Door B was lower-risk against that criterion.
- **Charlie (SME liaison)** routed SME review cycles. Charlie's bandwidth was the bottleneck for Door A — every narrative page needed at least one SME read. Door A made Charlie the critical path. Door B did not.
- **The SMEs themselves** were the long-run authority. They had asked twice in the past month whether they could trust the wiki. The five anti-hallucination rules existed because of an SME who had caught a fabricated capability in a draft. The SMEs valued *cite-able* over *readable*.
- **New hires** — there were no new hires on the team in the near term, though hiring was expected later in the year. The "new hire reads the wiki on day one" use case was prospective, not current.
- **Rahul himself** had built the pipeline expecting Door A. The narrative pages on Item Management, Inventory, and Accountability were proofs-of-concept for the destination model. Acknowledging that Door B was the better fit would mean letting that work be the high-water mark rather than the start of a wave.

## VII. The Clock

The ANC deadline was firm. The pilot module was Eligibility. The five content types in `resources/` (long-form guide, micro-guide, quick-reference, FAQ, SOP) had not yet been written for any module. The customer-facing demo was the ANC showpiece. The wiki was the internal asset that made the demo defensible — but only insofar as the resources cited it credibly.

Sixty days to ANC. Approximately 30 working days. The arithmetic did not support both doors at once.

## VIII. The Question

Rahul closed the Eligibility stub and opened a blank document.

The question was not whether the wiki was useful. It was, in three distinct measures. The question was whether it was useful **as the thing he had been building it as** — a narrative knowledge base — or whether the gravity of the surrounding architecture had been pulling it toward something else the whole time.

The 22 concept pages, the 8 workflows, the 5 entities, the 8,847 tickets — all of it sat upstream of a customer-facing content engine that would ship in eight weeks. The wiki's job, viewed from that downstream point, was to be a substrate of evidence the customer-facing team could cite without fabrication. Not a destination. A foundation.

But the destination version was also real. Onboarding mattered. Trust was built by reading, not by citation tags. And the three narrative pages — the ones that had been written by hand, with sub-themes and cross-links and open questions — were the only pages in the wiki that felt like they had been touched by a person who understood the product.

He had until the end of the week to commit. The Eligibility pilot resources had to start drafting on Monday, and the resources had to know what they were citing into.

---

## Discussion Questions

1. **What is the wiki for?** Distinguish the *built* job (compile Jira into narrative knowledge) from the *latent* job (be the citation backbone for a customer-facing content engine). Which one is load-bearing for Cybersoft's mid-July ANC reveal, and which one is a path Rahul could justifiably defer?

2. **Door A or Door B — and why?** Pick one of the two strategic frames. Defend the choice against the stakeholder map in Section VI. What does your choice cost the stakeholders you did *not* prioritize?

3. **The sunk-cost question.** Item Management, Inventory, and Accountability were written under the destination model. If Rahul commits to the backbone model, are those three pages an asset (proof that the destination model was feasible) or a liability (a higher bar that the other 19 modules can never meet)?

4. **The anti-hallucination rules cut both ways.** If the wiki shifts to citation backbone, the rules tighten — every stub needs accurate frontmatter and verifiable ticket links, but no narrative is required. If it stays a destination, the rules apply with even greater force because more prose means more surface area for invention. Which model is structurally *easier* to keep grounded?

5. **What is the test for "the wiki is working" three months after ANC?** Define a measurable outcome for each door. Which measurement is more defensible, and which is more game-able?

6. **The unused affordances.** `wiki/decisions/` and `wiki/onboarding/` are empty by design. Under which door — destination or backbone — do these folders ever get populated? Is the empty state of these folders evidence that the wiki was already drifting toward the backbone model before Rahul noticed?

7. **The asymmetric reversibility.** Door B is two weeks of pipeline work; if it fails, Door A is still available afterwards. Door A is two months of authoring; if it fails, Door B's window has closed. How should that asymmetry weight the decision, independent of which door is "better" on the merits?

---

*This case is internal to Cybersoft and reflects the state of the jira-brain pipeline as of May 15, 2026. Exhibits are derived from a live crawl and grep of the repository on that date.*
