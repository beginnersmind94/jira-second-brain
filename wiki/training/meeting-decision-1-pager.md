---
title: "Meeting Decision 1-Pager — context-switching aid for PMs"
type: training
audience: "PM (Matt, supporting Dallas — Director of PM)"
product: "SchoolCafe 2.0 / Perseus-NXT (the B2B district-staff platform), not the consumer SchoolCafe app"
---

# Meeting Decision 1-Pager
*A reset to run between back-to-back district calls and internal stakeholder reviews. The first half is the framework. The second half is what to do when the room isn't acting in good faith — because not all of them are.*

## Step 0 — Read the room (do this first)
Misclassifying the room is the most expensive mistake on this page. The framework underneath assumes a collaborative room; if the room is hostile, applying it as-written is how you become the sole blame target.

| Mode | Tells | Default ruleset |
|---|---|---|
| **Collaborative** | Shared goals stated up front; people surface unknowns; criticism aimed at the problem | Framework as written below — decide live, claim DRI, ship the smallest version |
| **Mixed** (most rooms) | Some good-faith actors, one or two positioning; norms inconsistent | Framework + paper trail. Get decisions in writing the same day. Don't claim DRI on contested items live; offer to write it up. |
| **Hostile** | Retroactive blame ("you should have known"), weaponized expertise, leading questions, surprise +1s, recording without notice | **Hostile-room playbook** (bottom of page). Don't decide live. Don't claim sole DRI. Write everything down. |

Most district calls land collaborative or mixed. The expensive ones are the internal reviews that drift hostile under cover of process. The cost of mis-reading collaborative as hostile is looking defensive. The cost of mis-reading hostile as collaborative is owning a decision someone else is already positioning to blame you for.

## Before you walk in (30 seconds)
1. **What is actually being asked of me?** Reframe as "...so we need to decide whether to ___."
2. **Door — one-way or two-way?** (table below)
3. **Who is DRI when the meeting ends?** In collaborative/mixed rooms, name them out loud. In hostile rooms, do not volunteer for it — see playbook.

## The two doors (Bezos)
| | **Two-way door** (most asks) | **One-way door** (rare; slow down) |
|---|---|---|
| Reversibility | Cheap to undo or change | Costly or impossible to undo |
| Velocity | Decide at ~70% certainty | Aim for ≥90%; sleep on it |
| Who decides | One DRI, in the room *(if room is collaborative)* | Decision doc, scheduled date, broader consult |
| Default move | Ship the smallest version, learn | Write it down, name the risks, list the un-undoables |

> Bezos's 2016 letter: *"Most decisions should probably be made with somewhere around 70 percent of the information you wish you had. If you wait for 90 percent, in most cases, you're probably being slow."* This rule assumes the room rewards velocity. In rooms that punish hindsight, even two-way doors deserve a paper trail.

## Six question archetypes
*If a meeting topic fits one of these, the door is pre-classified — don't re-derive it.*

| # | What they're really asking | Door | Why it's that door | Right next step | Pattern in our corpus |
|---|---|---|---|---|---|
| 1 | "Can we get this report sliced a different way?" (by site / grade / device / eligibility) | **Two-way** | Column add or grouping change; no schema impact, no customer commitment, no public agency claim | Decide live (collaborative) / decide in writing same day (mixed). Route to reporting backlog. | [[concepts/Accountability\|Accountability]] has shipped 100+ report variants — e.g. [[raw/tickets/NXT-10937\|NXT-10937 (by grade group)]], [[raw/tickets/NXT-10938\|NXT-10938 (by device)]], [[raw/tickets/NXT-10907\|NXT-10907 (by site)]] |
| 2 | "Add a Bulk Apply / Find-and-Replace button on this edit screen." | **Two-way** | Bulk patterns already shipped with audit-trail capture built in; this is incremental | Decide live; confirm history-capture is in scope before closing | [[concepts/Item-Management\|Item Management]] bulk pivot — [[raw/tickets/NXT-39922\|NXT-39922]] adds Bulk Apply, [[raw/tickets/NXT-69359\|NXT-69359]] captures per-item history |
| 3 | "Can pack-size be changed *after* inventory has been received against it?" | **One-way** *(data-model)* | Sits at the join between Items, Inventory, Recipes; reversing it ripples through Production | Decision doc. Loop in Inventory + Production owners. Don't decide in the customer's meeting. | [[workflows/item-onboarding-pack-size\|Item Onboarding & Pack-Size]] — [[raw/tickets/NXT-30168\|NXT-30168]] establishes the rule |
| 4 | "Stop letting users adjust X exception / variance." | **One-way** *(auditor trust)* | Tightening an override re-sets what district auditors expect to see; loosening is hard later | Decision doc + customer comms plan before shipping | [[raw/tickets/NXT-70214\|NXT-70214]] removed a permissive adjustment flow (closed-period exceptions); [[raw/tickets/NXT-12111\|NXT-12111]] for the surface |
| 5 | "Should we build payment processing ourselves or partner (Square-style)?" | **One-way** *(capital + integration)* | Hardware, partner contract, customer terminal commitments, multi-year unwind | Decision doc. Multi-week. RAPID roles explicit. | Square arc — ch. 7 of the [accountability primer](accountability-expert.html) |
| 6 | "In the customer onboarding doc — does *the district admin* set up the form, or *Cybersoft Implementation*?" | **One-way** *(customer trust)* | Implied agency in customer-facing copy is quoted back at us | Persona-grep source tickets first. If unclear, default to "not supported today." | Failure mode that produced rules 1, 4, 5 of [[../../CLAUDE.md\|CLAUDE.md]]. See [forms onboarding draft](forms-customer-onboarding.html). |

## Decision-doc template (one-way doors)
*Coinbase-influenced. Fits in 15 minutes for small one-way doors; expand for big ones. Fields 7 and 8 are the retroactive-blame defense — non-optional in mixed and hostile cultures.*

1. **Problem** — one paragraph ending in "...so we need to decide whether to ___."
2. **Options** — ≥2, tradeoffs spelled out (not pros/cons): *"Option A buys speed at the cost of N months of catalog cleanup later."*
3. **Recommendation + confidence %** — forces honesty about uncertainty; tells the decider how much to push back.
4. **RAPID roles** — *Recommend* (you) · *Agree* (sparingly) · *Perform* · *Input* (legal, finance, eng) · *Decide* (one person; usually Dallas or you on his behalf).
5. **Decision date** — pick in advance. Prevents analysis paralysis; gives blocked parties a known unblock.
6. **Explicitly out of scope** — what this doc is *not* deciding.
7. **What we knew on [date]** — known, unknown, deliberately deferred. This is your contemporaneous record. Hindsight bias retrofits "you should have known" onto decisions made with the information available; this field is the defense ([blameless-postmortems guide](https://postmortems.pagerduty.com/culture/blameless/) — the technique generalizes from incidents to decisions).
8. **Reversal cost** — what it would cost (in $, weeks, customer trust) to undo. If this number is small, you may have mis-classified the door.

---

## When the room is hostile — playbook
*Apply selectively. Over-applying in a collaborative room reads as defensive and alienates allies. Under-applying in a hostile room is where damage compounds.*

### Deflect without conceding
Neither agree nor escalate. Park the question, create paper.
- **"Help me understand the user impact in one sentence."** — Forces translation. If the speaker can't produce one, the objection is decorative.
- **"What outcome are you protecting?"** — Re-anchors to substance. Reveals whether the objection is about the work or about positioning.
- **"Good question — I want to get it right. Let me come back with something written."** — Parks without conceding; creates paper.
- **"I'm not going to land that here. Let me circle and put it on paper."** — Procedural refusal.

Avoid hedges: *"Maybe...", "I think we could...", "Possibly..."*. They read as weakness in hostile rooms and get quoted back as commitment.

### Invoke Dallas without looking weak
The wrong frame is *"I need to check with my boss."* The right frame is procedural: Dallas owns the *category*, not the rescue.
- **Pre-establish categories with Dallas, in writing.** Customer commitments, build-vs-buy, schema changes, public roadmap → Dallas decides, you recommend. Once written, invoking him is enforcing *his* policy.
- Say: **"This is a Dallas-level call by category. I'll have a doc for him by [date]."** Procedural, dated, lifts the decision out of the room.
- Don't say: *"I'll need to ask Dallas."* (rescue framing)
- If pushback on the category itself: **"Dallas asked for a doc on anything in this bucket. Want to give me your inputs in the doc?"** Reframes as participation, not obstruction.

### Refuse to engage (when not playing is the move)
Some questions are rhetorical, traps, or retroactive blame fishing. Engaging legitimizes the framing.
- **"I don't have what I'd need to decide that here."** — Factual. No apology, no hedge.
- **"Let me write up what I just heard and circulate it."** — Forces concreteness. Vague accusations die when written down.
- **"That's a separate question. Want to add it to a parking lot?"** — Boundary + procedural.
- **"I won't speculate on that publicly. Happy to take it offline."** — Boundary, with an exit.
- **Silence + note-taking.** When someone fishes for an admission, the room often fills with someone else's voice. Let it.

### Handle weaponized technical asymmetry
The pattern: a technical lead answers a strategic question with jargon, then frames any lack of follow-up as your incompetence. You can't win this on the fly in their domain. Don't try.
- **Never decide live on technical-asymmetry questions.** Always: *"Let me see this in writing."*
- **Force translation.** *"In one sentence, what does this break for the customer?"* If they can't, the complexity is a smokescreen.
- **Don't fight in their domain.** Bring a second engineer voice — a peer, not a subordinate. Dilute the asymmetry instead of overcoming it.
- **Make the asymmetry visible procedurally.** *"I want to represent this accurately to Dallas — can you write me a paragraph?"* Writing exposes thin arguments.
- **Use the doc as the venue.** A claim in a doc gets reviewed by everyone; a claim in a meeting gets reviewed only by whoever said it last and loudest.

### Defend against retroactive blame
Hindsight bias is the most expensive failure mode in adversarial cultures — people retrofit "you should have known" onto a call made with whatever info was actually available. Defense is contemporaneous and written.
- **Write decisions down at the time** — fields 7 and 8 of the template.
- **Name the Decide role explicitly.** Sole ownership is the trap; named, shared ownership in RAPID is the defense.
- **Date everything.** When the retroactive frame appears, cite the doc: *"As of [date] we knew X, didn't know Y, deferred Z. New information would update the call."*
- **Don't apologize for a decision made with the info you had.** Memorize: *"Given what we knew on [date], this was the call."* Not defensive — factual.
- **Send a written recap within 24 hours of any consequential meeting**: *"Decisions: A, B. Open: C, D. DRIs as noted."* Three sentences. The recap is the record that wins the argument six months later.

### The DRI trap
The original framework says *"single DRI moves fast."* True in collaborative rooms. In hostile rooms, sole DRI = sole blame target. Before claiming the hat:
- **Will this look obvious in hindsight if it goes badly?** If yes, get a co-decider on paper.
- **Does it match a Dallas category?** If yes, route procedurally (above).
- **Is the contestation theater for a different agenda?** If yes, refuse to decide live.

---

## Quiet door-flippers
Two-way decisions that are secretly one-way. Watch for these.
- **Customer-facing copy** going out (rules 1, 2, 4 in [[../../CLAUDE.md\|CLAUDE.md]] — persona, citation, ownership).
- **Schema or data-exchange contracts** once even one district has integrated.
- **Pricing or SLA promises** to one district that others will eventually hear about.
- **Public roadmap statements** — quoted back at you for a year.
- **Persona / agency claims** in onboarding docs — the failure mode that produced our anti-hallucination rules.

---

## Sources

**Decision frameworks**
- Bezos, J. *2016 Letter to Shareholders.* `source_type: vendor-marketing` (Amazon IR). Type 1 / Type 2 framing, 70% rule. https://www.aboutamazon.com/news/company-news/2016-letter-to-shareholders
- Bezos, J., summarized in CNBC, Nov 19 2018. `source_type: independent`. https://www.cnbc.com/2018/11/19/jeff-bezos-simple-strategy-for-answering-amazons-hardest-questions--.html
- Armstrong, B. *How we make decisions at Coinbase.* `source_type: vendor-marketing` (Coinbase CEO). Single-DRI emphasis, RAPID, decision-date discipline. https://barmstrong.medium.com/how-we-make-decisions-at-coinbase-cd6c630322e9
- Bain & Company. *RAPID Decision Making Framework.* `source_type: vendor-marketing` (Bain owns the trademark). Recommend / Agree / Perform / Input / Decide. https://www.bain.com/insights/rapid-decision-making/

**Hostile-room playbook**
- Wikipedia. *Hindsight bias.* `source_type: independent`. Background for the retroactive-blame section. https://en.wikipedia.org/wiki/Hindsight_bias
- PagerDuty. *The Blameless Postmortem.* `source_type: vendor-marketing` (PagerDuty sells incident-response). Generalizable defense pattern: contemporaneous record over hindsight narrative. https://postmortems.pagerduty.com/culture/blameless/
- The Pragmatic Engineer. *Ask the EM: How can I work better with my PM, as an engineering lead?* `source_type: independent`. Background on healthy PM/engineering working relationships — useful as the contrast to the weaponized-asymmetry pattern. https://blog.pragmaticengineer.com/how-engineering-can-work-better-with-product-managers/

**Internal**
- [[../../CLAUDE.md\|CLAUDE.md]] — anti-hallucination rules. Source for the door-flippers list and archetype #6.

*Compiled 2026-05-12. SchoolCafe 2.0 = the next-gen B2B platform for district nutrition staff (the corpus this wiki indexes, internally tagged Perseus / NXT). Not the consumer-facing SchoolCafe app for parents.*
