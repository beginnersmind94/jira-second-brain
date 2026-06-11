---
name: learning-studio-jtbd
description: >
  The jobs-to-be-done, end-user personas, the trust non-negotiable, and the stakeholder
  landscape for Cybersoft's Learning Studio / CN-LMS (a.k.a. "the learning agent," "the
  Learning Academy"). Load this BEFORE critiquing, designing, or building any of its
  screens or flows — it supplies the "who it's for and what's their job" that a UX critique
  needs but can't infer, the one bar that overrides everything here (trust), and the
  competing stakeholder visions (Dallas vs. Matt vs. Jaime) that decide what "good" means.
  Pair it with the design-critique / ux-critique / accessibility-review skills: those judge
  generic UX quality; this one tells them what the product is actually for and whose
  approval it needs. Trigger when the user asks to review/critique/improve the Learning
  Studio or learning-agent UI, design a new surface for it, or asks "is this good UX for our
  learners / trainers / Jaime's team?" — or asks you to critique it "as Matt would" / "as
  Dallas would" / "for the cashier."
argument-hint: "<the Learning Studio surface or flow under review — and, if known, the persona it serves or the stakeholder lens to apply, e.g. 'the learner Track view for John' or 'critique the approval flow as Matt would'>"
---

# Learning Studio / CN-LMS — JTBD & Stakeholder Context (critique companion)

This is a **context pack**, not a second critique engine. The `design-critique` / `ux-critique`
skills say the single most important input is *who it's for and their job*, and that the
critique is provisional without it. This file supplies that — grounded in the actual build,
the BRD, and the stakeholder calls — and adds the two things generic critique can't know for
this product: **trust is the job**, and **two stakeholders want two different products.**

## How to use this with a critique
1. Identify the surface's **primary end-user persona** (below) and pass it to the critique as
   "who it's for + their job-to-be-done." If a screen serves two personas (e.g. a *trainer*
   building what a *learner* consumes), critique each separately — their jobs diverge.
2. Run the critique's layers, but read **Layer 1 ("does it do the job?") as "does it do the
   job AND keep trust legible?"** A screen that completes the task while letting an
   un-verified / un-cited claim through, blurring AI-vs-human authorship, or hiding
   provenance has **failed Layer 1**, not committed a polish nit.
3. Apply the requested **stakeholder lens** (Dallas / Matt / Jaime) to set severity and
   framing. If none is named, default to: judge the end-user job first, apply the trust bar
   as a Layer-1 gate, and **explicitly flag when a design serves one stakeholder's vision at
   another's expense** — that fork is the decision the PM is actively managing.
4. Accessibility & mobile are **contractual** here, not nice-to-have (BRD §6): WCAG 2.1 AA,
   usable to 375px, course player loads < 3s. Cite the FR/NFR id when flagging.

## The product — and the tension you're managing
"The learning agent" is one roadmap item ("Learning Academy") with **two competing shapes**:

- **Content-engine-first (Dallas's vision; what's built today).** Turn a training transcript /
  PDF / Jira into a fact-checked, role-tagged guide + quiz in minutes; review, approve, serve
  it in a clean HTML library; replace a *"$50–100k/yr documentation tool"* (Dallas, Jun-04
  [27:17], [41:13]). Don't over-engineer; don't wait on Jaime; *show the value, then ask
  what's next.* The built app (`learning-agent/`) is this: a content factory + a façade LMS.
- **Platform-first (Matt's BRD; the spec).** A from-scratch, API-integrated **delivery** LMS:
  SSO via existing product logins, roster sync + completion writeback to SchoolCafe /
  PrimeroEdge, multi-tenant (one district = one isolated tenant), SCORM/xAPI, state-agency
  compliance reporting. **The BRD puts content *creation* explicitly OUT OF SCOPE** ("the LMS
  is a delivery platform; content is authored separately") and pushes AI-assisted authoring
  to **V3.**

> **The inversion to keep in mind (Observation):** the thing that's built *is* the
> content-authoring engine that Matt's BRD defers to V3, while the LMS plumbing the BRD makes
> MVP (SSO, rostering, real per-learner persistence) is **façade** in the build (`FEATURES.md`
> tags it so). So the **same screen earns opposite verdicts** depending on which product it's
> being judged as. Always establish that frame first.

Rahul's own stated instinct (May-26 [03:31]) was platform-first too — *"it might be better to
just first build an LMS … and then merge in the AI stuff"* — which Dallas overruled toward
content-first. The PM now leans back toward Matt's caution. Hold both; the job is to manage
the gap, not to pick a side in a critique.

## The non-negotiable: trust (this reframes Layer 1 for every screen)
Said almost identically across both calls — this is the bar the whole product lives or dies on:
- Rahul, May-26 [23:06]: *"you make one mistake with AI and it loses credibility very quickly."*
- Rahul, Jun-04 [25:55]: *"a human can make one mistake … but if an AI makes it, immediately
  kills trust in the product."*
- Matt, Jun-04 [26:37]: *"there's a much stricter lead to distrust once the human element is
  taken out."*

The product's answer is **grounding by construction + a human SME approval gate**: every
product-fact claim traces to a verbatim source span at the correct trust tier (AC > Release
Notes > Description) or it's cut; a human approves before anything reaches the library; the
agent never auto-approves (`FEATURES.md`, `CLAUDE.md` → *Status Gating*). For a critique, this
means the **trust affordances are load-bearing** — flag any redesign that removes or weakens
them as at least 🟠 Serious, usually 🔴 Blocker (trust is a one-way door):
- provenance / origin badges everywhere (AI-grounded · human-authored · outside-vendor/ICN);
- per-claim "show source" with the verbatim quote + tier; the "✓ every claim cited" badge;
- the **Customer-view banner / chrome** (a named safety fix so a trainer never screen-shares
  internal content as customer-facing);
- **honest under-claiming** — imported guides are human-authored, *not* gate-grounded; ICN /
  USDA content is link-out + credited, never reproduced. The UI must not paint the
  verbatim-cited guarantee onto content that doesn't carry it;
- **no free-claim authoring** — builders *sequence + grounded-generate*; there is deliberately
  no canvas where a human types an un-cited product claim. A new free-text field that accepts
  product facts is a moat violation, not a feature.

## End-user personas & their jobs — judge the design against these
Sources: BRD §4 (User Roles & Personas) + §5.3 (enrollment) + the built views in
`learning-agent/static/index.html`. Persona names per the PM's framing.

### 1. Jaime's team — the internal customer (Customer Success / Implementation)
- **Who:** BRD's *"primary internal user of the platform."* In the calls, Jaime is the
  understaffed head of Implementation; her team runs onboarding/training for new customers.
- **Job (JTBD):** *"Turn our training recordings into consistent, trustworthy, role-tagged
  content fast, review/approve it, and get leverage — without hiring a content team or buying
  a $50–100k tool."* Plus (BRD FR-RP-01/03): *see each customer's onboarding progress against
  go-live milestones in real time.*
- **Where:** the Trainer view — Create (upload → generate), Library/Studio (review/edit/approve),
  Districts/Manage (customer portfolio + roster), Quality (grounding QA).
- **Success:** a trustworthy guide is published and assigned faster than hand-writing it, and
  she can *prove* every claim is cited. **Failure:** can't tell grounded from not; approves
  blind; or screen-shares internal chrome to a customer by accident.
- **Design caution (from the calls):** Jaime *"just wants to be told what to do,"* gives
  feedback as complaint, and *"half of them don't even know what LMS stands for"* (Dallas,
  Jun-04 [28:09], [38:36]). Design for **low ceremony, show-don't-spec** — no prompt-craft, no
  LMS jargon, a path obvious to a reluctant non-technical user.

### 2. John Doe — Cashier at ABC ISD — the Learner
- **Who:** BRD *"Learner: cafeteria staff, cashiers, cooks."* Roles in the build: Cashier /
  Site Manager / CN Director.
- **Job (JTBD):** *"On day one, find the training for **my** role, finish it on my phone, and
  prove I did it — with no setup and no training on the tool."*
- **Where:** the Customer "Learn" view (Track → Courses → Lessons → quiz/certify).
- **Success:** zero-setup, short modules, mobile-first, an obvious "what do I do next."
  **Failure:** desktop-only, can't find his role's track, training fatigue, a dead first-run.
- **Hard constraints (BRD, not optional):** mobile-responsive to **375px** ("cafeteria staff do
  not sit at desks," NFR), player loads **< 3s** (NFR), modules short (Risk mitigation: *"< 10
  min with clear progress indicators"*), downloadable completion certificate (FR-CP-08).

### 3. Dana — CN Director at ABC ISD — the district manager
- **Who:** BRD *"CN Director: district-level admin — manage district users, view district
  compliance, produce reports."*
- **Job (JTBD):** *"Assign the right training to my staff by role/site, see who's overdue
  against a deadline, and nudge them — without authoring any content myself."* In V2: *produce
  a state-agency-ready compliance report.*
- **Where:** the Customer "My Team" view (compliance by site/role vs. deadline; nudge-one /
  nudge-all-overdue; self-assign a track); locked to her own district.
- **Success:** at-a-glance who's behind + a one-click nudge + export. **Failure:** compliance
  illegible against the deadline; no clear action; cross-tenant data leak (NFR: tenants are
  isolated "at any layer").

### 4. Site Manager (single-site) — brief
- BRD: *"monitor site staff completion, assign courses, view overdue alerts."* A narrower Dana;
  one site, not a district. Critique its overdue-alert legibility and assign flow.

> **V2+ personas — note, don't deep-dive:** State Reviewer (read-only compliance auditor),
> FSMC Admin (multi-district), District Admin (SSO/provisioning). They shape the data model now
> but aren't MVP surfaces — flag if a screen quietly assumes them.
>
> **Not a target user:** Charlie (writes content "as told"). The build *sidesteps* him by
> design (Dallas, Jun-04 [13:21]). Don't optimize a screen for a hand-author; that's the
> workflow the engine replaces.

## Stakeholder lenses — whose approval the design needs (use to set severity & framing)
End-users have *jobs*; these people have *concerns that decide what ships.* Critique through
the named lens, or run all three and show where they conflict.

| Lens | What they optimize for | Apply when judging… |
|---|---|---|
| **Dallas** (PM's boss; champion) | Vision, speed, leverage, "don't over-engineer," replace the $50–100k tool, *sell the foundation not the robot.* Forgives rough edges; won't forgive slow or "no wow." | Demo impact, time-to-value, whether the screen advances the Academy narrative. |
| **Matt** (cautious / skeptical; **the lens the PM leans toward**) | The BRD-grade foundation: real SSO, multi-tenancy, roster sync, completion writeback, accuracy, phased rigor. Trust *enforced*, not hoped. | Anything claiming production-readiness; data model; whether a "Built" thing is real or façade. **Default lens for credibility/trust calls.** |
| **Jaime** (internal customer; primary user but reluctant) | Will her understaffed, non-technical team *actually use it* without being told to? Her adoption is the win condition — *"if her team balks … we're wasting our money"* (Matt, Jun-04 [19:42]). | First-run friction, jargon, ceremony, whether it respects how her team really works. |

Audienne (Jaime's-side leadership) is a perception stakeholder: *frame this as the beginning,
not the finished academy* — manage expectations so the room reads it as foundation + leverage,
not "watch the robot write." Relevant when critiquing demo/first-impression surfaces.

**Severity adaptation:** escalate any **trust/provenance regression one level** over what its
visual impact suggests (a hidden badge or a possible persona leak is a one-way door — a single
visible AI mistake "kills trust"). And **name the vision fork** when present: e.g. "this is
fast and demo-ready (Dallas ✓) but presents façade rostering as real (Matt ✗) — decide which
frame this screen is making a promise in."

## Trust-specific blockers to hunt (add to the generic anti-pattern list)
1. **Persona leakage** — internal/trainer chrome reachable or visible in Customer view; ambiguous which mode a screen-share is in.
2. **Over-claiming the guarantee** — "every claim cited" framing shown on imported or ICN content that isn't gate-grounded.
3. **Provenance invisible** — a guide/quiz/answer with no origin badge and no path to its source.
4. **Un-cited claim slips in** — any field/flow that lets a human or the model put a product fact on screen without a citation.
5. **Silent / auto approval** — draft → approved without a visible human decision (the agent must never approve itself).
6. **Reproduced vendor content** — ICN/USDA shown inline instead of linked + credited.
7. **Empty / first-run dead-air** — a library that defaults to an empty "approved" filter and shows nothing.
8. **Quiz ungrounded from its guide** — a question whose answer isn't a verbatim span of the published content it claims to test.
9. **Desktop-only learner surface** — breaks the cafeteria-staff-on-a-phone reality (and the 375px NFR).

## Grounding (re-verify before relying on a specific label, number, or quote)
- **Built product, moat, provenance, honesty caveats, façade-vs-real:** `learning-agent/FEATURES.md`.
- **Grounding-by-construction rules, status gating, templates, regeneration ("16 guides"):** `learning-agent/CLAUDE.md`.
- **Personas, view-modes, roles, customer-view banner:** `learning-agent/static/index.html` (`applyViewMode`, `persona-toggle`, role/district seeds, `customer-banner`).
- **The platform-first spec (SSO, multi-tenant, SCORM, compliance, MVP/V2/V3, NFRs, personas §4):** `CN_LMS_BRD.docx` (Matt's BRD).
- **The trust bar, the $50–100k framing, Jaime/Charlie dynamics, content-engine-first decision:** the May-26 call (`LMS-and-AI-Content-Authoring`, Dallas + Rahul) and the Jun-04 call (`Jun-04-01-13-PM…`).
- **Demo framing / first-impression surface / audience:** `learning-agent/docs/jun11/DEMO-RUNOFSHOW.md`, `docs/CASE-STUDY-learning-studio.md`.

> *Attribution note (Inference):* the Jun-04 transcript labels speakers numerically. Mapped
> Speaker 1 = Dallas, 2 = Rahul, 3 = Matt, consistent with the PM's stakeholder framing and with
> Matt being the BRD author (Rahul, May-26: *"Matt actually also had a brd"*). If a future
> source contradicts this, re-check the quote attributions above.
