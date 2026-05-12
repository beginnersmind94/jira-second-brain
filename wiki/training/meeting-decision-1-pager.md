---
title: "Meeting Decision 1-Pager — context-switching aid for PMs"
type: training
audience: "PM (Matt, supporting Dallas — Director of PM)"
product: "SchoolCafe 2.0 / Perseus-NXT (the B2B district-staff platform), not the consumer SchoolCafe app"
---

# Meeting Decision 1-Pager
*A 30-second reset to run between back-to-back district calls and internal stakeholder reviews.*

## Before you walk in (30 seconds)
Three questions, in order:
1. **What is actually being asked of me?** Reframe it as one sentence ending in "...so we need to decide whether to ___."
2. **Is the door one-way or two-way?** (table below)
3. **Who is the DRI on this decision when the meeting ends?** Name them out loud. If unnamed, the default is you — claim it or hand it off, but don't let it leave the room ambiguous.

## The two doors (Bezos)
| | **Two-way door** (most asks) | **One-way door** (rare; slow down) |
|---|---|---|
| Reversibility | Cheap to undo or change | Costly or impossible to undo |
| Velocity | Decide at ~70% certainty | Aim for ≥90%; sleep on it |
| Who decides | One DRI, in the room | Decision doc, scheduled date, broader consult |
| Default move | Ship the smallest version, learn | Write it down, name the risks, list the un-undoables |

> Bezos's 2016 letter: *"Most decisions should probably be made with somewhere around 70 percent of the information you wish you had. If you wait for 90 percent, in most cases, you're probably being slow."* The common failure mode is large orgs applying the one-way-door process to two-way-door decisions — a tax on velocity for no upside.

## Six question archetypes you hear every week
*If a meeting topic fits one of these, the door is pre-classified — don't re-derive it.*

| # | What they're really asking | Door | Why it's that door | Right next step | Pattern in our corpus |
|---|---|---|---|---|---|
| 1 | "Can we get this report sliced a different way?" (by site / grade / device / eligibility) | **Two-way** | Column add or grouping change; no schema impact, no customer commitment, no public agency claim | Decide live. Route to the reporting backlog. Don't write a doc. | [[concepts/Accountability\|Accountability]] has shipped 100+ report variants — e.g. [[raw/tickets/NXT-10937\|NXT-10937 (by grade group)]], [[raw/tickets/NXT-10938\|NXT-10938 (by device)]], [[raw/tickets/NXT-10907\|NXT-10907 (by site)]] |
| 2 | "Add a Bulk Apply / Find-and-Replace button on this edit screen." | **Two-way** | Bulk patterns already shipped with audit-trail capture built in; this is incremental | Decide live; confirm history-capture is in scope before closing | [[concepts/Item-Management\|Item Management]] bulk pivot — [[raw/tickets/NXT-39922\|NXT-39922]] adds Bulk Apply, [[raw/tickets/NXT-69359\|NXT-69359]] captures per-item history so it's still auditable |
| 3 | "Can pack-size be changed *after* inventory has been received against it?" | **One-way** *(data-model)* | Constraint sits at the join between Items, Inventory, and Recipes; reversing it ripples through Production downstream | Decision doc. Loop in Inventory + Production owners. Don't decide in the customer's meeting. | [[workflows/item-onboarding-pack-size\|Item Onboarding & Pack-Size Changes]] — [[raw/tickets/NXT-30168\|NXT-30168]] establishes the rule ("expand only if no inventory transactions yet") |
| 4 | "Stop letting users adjust X exception / variance." | **One-way** *(auditor trust)* | Tightening an override surface re-sets what district auditors expect to see; loosening back later is hard | Decision doc + customer comms plan before shipping | [[raw/tickets/NXT-70214\|NXT-70214]] removed a previously-permissive adjustment flow (closed-period exceptions); [[raw/tickets/NXT-12111\|NXT-12111]] for the surface |
| 5 | "Should we build payment processing ourselves or partner (Square-style)?" | **One-way** *(capital + integration)* | Hardware, partner contract, customer terminal commitments, multi-year unwind | Decision doc. Multi-week. RAPID roles explicit. | Square integration arc — see ch. 7 of the [accountability primer](accountability-expert.html) |
| 6 | "In the customer onboarding doc — does *the district admin* set up the form, or *Cybersoft Implementation*?" | **One-way** *(customer trust)* | Implied agency in customer-facing copy is quoted back at us; hard to retract once shipped | Persona-grep the source tickets *first*. If unclear, default to "not supported today." | This is the failure mode that produced rules 1, 4, 5 of [[../../CLAUDE.md\|CLAUDE.md]]. See the [forms onboarding draft](forms-customer-onboarding.html). |

## When you need a doc (one-way doors only)
*Coinbase-influenced template. Fits in 15 minutes for small one-way doors, expand for big ones.*

1. **Problem** — one paragraph. End with "...so we need to decide whether to ___."
2. **Options** — at least two. Spell out tradeoffs, not just pros/cons. ("Option A buys us speed at the cost of N months of catalog cleanup later.")
3. **Recommendation + confidence %** — what you'd do, with a rough percentage. The % forces honesty about uncertainty and tells the decider how much to push back.
4. **RAPID roles** — *Recommend* (usually you) · *Agree* (must sign off; assign sparingly) · *Perform* (who delivers) · *Input* (SMEs — legal, finance, eng leads) · *Decide* (one person; usually Dallas or you on his behalf).
5. **Decision date** — pick it in advance. Prevents analysis paralysis; gives anyone blocked a known unblock.
6. **What we are *not* deciding here** — protects against scope creep mid-doc.

## After the call
- **Disagree privately, commit publicly.** Once a decision is made, re-open it only with *new* information, not the same objection in new words.
- **Two-way default**: ask "what's the smallest version we can ship to learn?" If the honest answer is "we'd have to commit to it publicly first" or "we'd have to migrate data first," it isn't two-way after all — re-classify and slow down.

## Quiet door-flippers (two-way decisions that are secretly one-way)
Watch for these. They look reversible until they aren't:
- **Customer-facing copy** going out the door (rule 1, 2, 4 in [[../../CLAUDE.md\|CLAUDE.md]] — persona, citation, ownership).
- **Schema or data-exchange contracts** once even one district has integrated against them.
- **Pricing or SLA promises** to a single district that other districts will eventually hear about.
- **Public roadmap statements** ("we'll ship X by Q3") — quoted back at you for the next year.
- **Persona / agency claims** in onboarding docs — the specific failure mode that produced our anti-hallucination rules.

---

## Sources
- Bezos, J. *2016 Letter to Shareholders.* `source_type: vendor-marketing` (Amazon IR). Origin of Type 1 / Type 2 framing and the 70% certainty rule. https://www.aboutamazon.com/news/company-news/2016-letter-to-shareholders
- Bezos, J., summarized in *Amazon's Jeff Bezos: This simple framework…*, CNBC, Nov 19 2018. `source_type: independent`. https://www.cnbc.com/2018/11/19/jeff-bezos-simple-strategy-for-answering-amazons-hardest-questions--.html
- Armstrong, B. *How we make decisions at Coinbase.* Medium. `source_type: vendor-marketing` (Coinbase CEO). Single-DRI emphasis, Problem/Proposed Solutions, RAPID, "pick a decision date." https://barmstrong.medium.com/how-we-make-decisions-at-coinbase-cd6c630322e9
- Bain & Company. *RAPID Decision Making Framework.* `source_type: vendor-marketing` (Bain owns the trademark). Recommend / Agree / Perform / Input / Decide role definitions. https://www.bain.com/insights/rapid-decision-making/
- Internal: [[../../CLAUDE.md\|CLAUDE.md]] anti-hallucination rules. The "quiet door-flippers" list and the rule-of-thumb for archetype #6 come directly from rules 1, 4, and 5.

*Compiled 2026-05-12. SchoolCafe 2.0 = the next-gen B2B platform for district nutrition staff (the corpus this wiki indexes, internally tagged Perseus / NXT). Not to be confused with the consumer-facing SchoolCafe app for parents.*
