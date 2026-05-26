# Brio — Project Handoff (LLM context, not for humans)

> This doc exists so the next LLM picking up the project has full context. Dense facts > narrative voice. State changes called out explicitly. Selectors and function names inline.

## TL;DR

We're building **Brio** — an AI-powered training design + outcomes platform for Cybersoft's internal implementation team. Brio is the product Cybersoft's team uses every day to design training content and manage learner/site outcomes.

**Naming — critical, do not confuse:**
- **Brio** = the product (the platform; what the internal team buys and uses; sits alongside Cybersoft's existing SchoolCafé + PrimeroEdge)
- **Schoolie** = the AI assistant *inside* Brio (the chatbot in the customer chat, the engine that drafts content). Like Einstein lives inside Salesforce or Copilot lives inside Microsoft 365.
- The customer-facing experience that districts see is the rendered output of Brio's content engine, with Schoolie as the AI face.

**The pitch in one sentence:** today Cybersoft sends 2 trainers to LA to clear 100+ sites manually; Brio complements and significantly improves on that — Brio-shipped tracks plus a small in-person trainer presence get sites cleared in days instead of weeks.

**Two deadlines:**
| Deadline | Audience | Goal |
|---|---|---|
| **Friday, May 16, 2026** | Internal: Dallas + Charlie (SME liaison) + 3–4 SMEs | Convince SMEs to commit to producing recordings |
| **ANC, mid-July 2026** | District buyers + competitors at the trade-show booth | Customer-grade demo that wins the change-management story |

**The build:** single self-contained HTML — `wiki/training/resource-center-v2.html` (~400 KB, opens in any browser, no server needed). Two surfaces behind a top-right toggle: **Customer view** (what districts see, branded Schoolie) and **Brio** (the workspace — default landing). The default mode is now Brio: `<body class="builder-mode">`.

**Naming history this session (so the next LLM doesn't re-litigate):** user rejected "Schoolie Studio" because Schoolie is the AI, not the product. Then rejected "Cybersoft Curriculum / Train / Cohort" (too dry), "Cadence / Forte / Helm" (still not landing), then said *"just go with Brio for now"* with the caveat *"sounds like detergent but better than the previous rec."* Brio is **"good for now," not validated with Dallas, may change.** If the name moves, update: the toggle button (`#view-toggle button[data-mode="builder"]`), the `aria-label` on `.builder-workspace`, and the "Back to Brio" copy in the verification-view done overlay (`#vv-done-back`).

---

## What this project is

Cybersoft makes **SchoolCafé** and **PrimeroEdge** — software that school-district nutrition departments use to run meal programs (Eligibility, Accountability, Menu Planning, Inventory, etc.). Customer documentation today lives in stale PDFs and a learning portal called **Amigo** that nobody loves. The current process: hire technical writers → schedule SME meetings → take notes → produce documents → ship slowly.

The biggest fear districts have when switching to Cybersoft's platform is **change management** — will their cashiers and managers be able to learn the new system fast? Cybersoft loses deals over this. The solution Dallas is pitching: replace documentation with an AI-driven, role-aware, multi-format resource center that turns SME expertise into customer-facing content automatically. At the kickoff, Dallas said *"Brand it Schoolie. Win the change-management story."* — but mid-session the user clarified that **Schoolie is the AI/chatbot**, and the broader product (the platform the internal team uses to design + manage outcomes) was renamed **Brio**. The customer-facing experience is still Schoolie-branded; the internal product is Brio.

---

## Dallas's vision (from the May 13 kickoff)

### The five content types ("the boilerplate")

Dallas explicitly asked for these five output shapes by Friday:

1. **Long-form guide** — 30–60 min read, canonical reference
2. **Micro guide** — 5–10 min, single workflow
3. **Quick reference** — under 2 min, one-page printable
4. **FAQ** — 8–15 Q&A pairs
5. **SOP / how-to** — procedural, role-specific

### The premium-tier vision

- **Standard mode** — read the content
- **Mastery mode** — interactive checkpoints, badges, mandatory training for new district hires. Dallas's pitch: this replaces hiring on-site trainers for new districts (he estimates ~$120k saved per large district like Los Angeles). The premium feature districts will pay extra for.

### The longer-term capabilities Dallas gestured at

- **AI chatbot embedded inside the product** ("why are my reconciliations always off?" → real diagnosis using the district's actual data)
- **Role-based filtering** (a dietitian shouldn't see cashier content; cafeteria managers don't need menu planning)
- **Voice-conversational interface**
- **Language translation** (Spanish + Vietnamese mentioned by name)
- **Embedded learning paths**, progress tracking, badges, gamification

### The actual bottleneck Dallas named

**Content collection** — *not* the engine. Dallas said the engine isn't the hard part. SMEs need to **click record on their phones** and walk through their expertise area for 30 seconds at a time. AI handles the rest.

### The two deadlines

| Deadline | Audience | Goal |
|---|---|---|
| **Friday, May 16** | Internal: Dallas + Charlie (SME liaison) + 3–4 SMEs | Get the SMEs to commit to producing recordings. We need to ship the boilerplate (5 templates) + a working demo that makes the team want to participate. |
| **ANC, mid-July** | District buyers + competitors at the trade-show booth | Customer-grade demo that wins the change-management story and closes deals. |

---

## What we have to work with

The project has been seeded with substantial source material — we are **not** starting from zero:

- **8,849 Jira tickets** with full descriptions and acceptance criteria
- **20+ wiki concept pages** covering every Cybersoft module (Eligibility, Accountability, Menu Planning, Inventory, Family Hub, Inspections, Production, Item Management, Mobile App, Financials, Insights, Platform, Professional Standards…)
- **8+ wiki workflow pages** documenting end-to-end flows
- **22 raw PDF-extracted guides** for Eligibility (from the official `docs.schoolcafe.com` library)
- **5 content templates** defined as markdown skeletons
- **A polished internal HTML prototype** the team built earlier (`eligibility_onboarding_design_pass.html`) — establishes the visual language we're borrowing from
- **A CSV of every Eligibility ticket** as a bulk-data backup

**Important constraint** (per the project's anti-hallucination ruleset in `jira-brain/CLAUDE.md`): every customer-facing claim has to cite a real ticket or wiki page. Ambiguous capabilities default to *"not supported today"* rather than fabricated answers. The `raw/transcripts/` directory is reserved but the demo never depends on transcripts existing.

---

## What we've built

A single ~400 KB self-contained HTML file — **`wiki/training/resource-center-v2.html`** — that opens in any browser, needs no server, and is shareable as one attachment. It has **two co-existing surfaces** behind a top-right toggle.

### Surface 1: Customer view — what districts see

A polished customer-facing resource center, branded "Schoolie." Audience is a district admin or cafeteria manager evaluating or learning the platform.

- **Live context strip** at the top identifies the user, role, district, and surfaces a today-relevant nudge ("23 applications pending verification today") — sells the role-awareness vision in two seconds.
- **Chat-first hero** with the change-management headline. Glass-morphism input. Mic button for voice. Language toggle (EN / ES / VI) flips the chrome.
- **Five starter prompt chips** map to questions a real district admin would ask: configure a Summer EBT form · find CEP-identified students · why is my application stuck in Pending · run the FNS-742 worksheet · onboard me as a new admin.
- **Streamed AI answers with citations** — picking a starter streams a grounded answer with inline `[1] [2]` chips. The right-side **sources rail** lights up as citations get typed, each card showing the cited guide's content-type as a colored chip. So when someone asks "onboard me," they visually watch Schoolie pull from a long-form, two micro-guides, a quick reference, an FAQ, and two SOPs to assemble the answer — the content-type matrix made visible.
- **Inline sandbox embeds** — after each answer, a mini animated UI auto-plays the in-product workflow (cursor moves, fields fill, primary button flashes, success state).
- **Related questions + Common pitfalls** appear below each answer.
- **Mastery mode** — toggle in the hero. When on, every answer ends with a 2–3 question interactive checkpoint quiz with real feedback and a Mastery badge on completion. This is Dallas's premium tier, made tangible.
- **Catalog browse** — module pills, content-type pills, card grid of all 33 published drafts. Each card click opens a **premium reader drawer** with sticky table-of-contents, reading-time estimate, reading-progress bar, drop-cap on long-form, auto-styled callout boxes (note / warning / tip / trigger), and content-type color stripe in the header.
- **Yellow "Needs your review" callouts** inside any guide where Schoolie couldn't fully confirm a detail. Each has an *"Answer this with Schoolie →"* CTA that opens the edit panel pre-loaded with that question.
- **Edit with Schoolie panel** — slides up from the bottom of the drawer. SME types a refinement (or accepts a suggested chip). Schoolie produces a diff card with Apply / Discard buttons. Apply persists the edit and re-renders the doc live. Pre-canned for demo reliability but the diffs are real-Claude-quality output.
- **Edit directly** — manual markdown editor option for SMEs who'd rather type the fix themselves.

### Surface 2: Brio (workspace) — the internal team's product

**This is the default landing.** Toggle in the context strip flips between `Customer view` and `Brio`. The split-view design was killed — Brio takes the full viewport when active. `body.builder-mode` is set in HTML so Brio opens by default.

**Iteration 4 — track-first, not inbox-first** (see *Design iteration history* below for the full evolution). The Cagan call this session: the unit of value is a *trained learner / cleared site*, NOT an approved doc. So Brio leads with track approval, not a 9-row doc-review queue. The previous handoff described an inbox-first Iteration-3 design that no longer exists.

**Brio layout (top to bottom):**

- **Live context strip (`.ctx`)** — dark navbar pinned at top in BOTH modes (moved above `.builder-workspace` in DOM order this session — was below it before, which meant the toggle was invisible at `top: 2269px` in builder mode). Holds the persona greeting, "Live data" dot, applications-pending nudge, language picker, and the `#view-toggle` (Customer view / Brio).
- **Floating "+ Generate from source" CTA (`#bw-add-fab`)** — top-right, always present in builder mode. Opens `#bw-add-scrim` modal which contains the drop-zone (`#bw-drop`) PLUS the 6 template cards (moved here this session from a bottom workspace section). Templates are framed as *"Shapes Schoolie generates against"* with a single per-card action: **See examples →** (closes modal, flips to customer view, filters catalog by content_type).
- **Outcome banner (`#bw-outcome`, track-anchored, purple gradient)**:
  - Trainer chip: *rahul · Product · Eligibility content*
  - Eyebrow: *Friday launch · ready to ship*
  - Headline: *Approve **Cashier Day 1** to launch Friday.*
  - Right side: 3 readiness signals
    - `✓ Grounding audit · 47 claims · all sourced` (`#bw-outcome-claims`)
    - `✓ Quiz coverage · all 4 role lenses`
    - `⚠ N spots AI wants your eyes · peek?` (`#bw-outcome-light-evidence`, live-computed in `renderOutcomeBanner()` from `markerState`)
  - Primary CTA: **▸ Approve & ship the track** (`#bw-approve-track`, wired to `approveTrack()`)
  - Secondary link: *Spot-check 9 resources individually →* (`#bw-spotcheck-link`, scrolls to `#bw-inbox-anchor`)
- **Training tracks board (`#bw-tracks`, PROMOTED to primary surface)** — Cashier Day 1 gets `.bw-track--hero` class (full-width, soft-purple gradient, *Friday launch* badge). Other 3 tracks (Manager Onboarding, Eligibility Admin Core, Director Executive Tour) sit in a 3-column row below. "Compose with AI" buttons on non-hero tracks call `composeTrackWithAi()` which fills empty slots one at a time over ~3 seconds. Filled slots with a `source` field open the customer-side drawer on click; ones without source are non-clickable (no silent no-op).
- **Outcomes section (`#bw-outcomes-anchor`, NEW this session)** — the "manage" half of Brio. Live pulse pill in header. **Site-anchored metrics** (NOT learner-count anymore — the unit of operational readiness is the site, because that's what the implementation team ships to LA-style districts):
  - `5` Sites cleared this week · ↑ 2 vs last week · 47 cleared to date
  - `18 / 124` Sites in progress · across 3 active districts
  - `6.4d` Avg site time-to-clear · **vs ~14d in-person baseline** ← the LA-trainer comparison; load-bearing for the pitch
  - `6` Resources flagged for review · spot-check below →
  - Below the cards: per-track performance table (4 rows, role-colored left borders) with `learners cleared / pass rate / avg time` per track
  - **Numbers are demo-static.** Real data layer is not wired. For ANC need either real data or label section *"(illustrative)"*.
- **Spot-check inbox (`.bw-inbox--secondary` with `#bw-inbox-anchor`, DEMOTED)** — doc-by-doc review queue, no longer the primary surface. Header: *Spot-check individual resources OPTIONAL*. Meta: *"All 9 resources passed the grounding audit. Open any to read the source before shipping — or trust the audit and approve the track above."* Row click opens `#verification-view` (separate full-page doc + rail; preserved from Iteration 3).
- **Work saved this week strip** — 4 stat blocks: *12 repeated explanations captured · 6 resources generated from existing calls · 1 Product approval to ship · 0 Implementation reviews assigned*. The last column is load-bearing politically: tells Implementation team "this isn't another queue for you."

**Approve-track interaction (the Friday demo's headline moment):**

`approveTrack()` is theatrical (does not bulk-approve `markerState`/`questionState`; the inbox stays available for spot-checking). When clicked:
- Banner gets `.shipped` class → adds top-right `✓ Shipped to learners` badge
- CTA flips to green, disabled, reads "✓ Shipped to learners"
- Eyebrow → *"Cashier Day 1 · live for learners"*
- Headline → *"Cashier Day 1 is live. Cafeteria Manager is next."*
- Hero track badge swaps from amber *"Friday launch"* → green *"✓ Shipped Friday"*
- Hero track's compose button → *"Composed · live"* (disabled)
- Idempotent: clicking again is a no-op (`_cashierDay1Shipped` guard)

### What's in the catalog today

All Eligibility. **`catalog/resources.json` has 14 catalogued resources**; the handoff previously claimed 33 because it counted raw PDF-extracts in `raw/guides/markdown/SC/Eligibility/Quick-Guide/` (19 of them) that haven't been ingested into the catalog yet. The dashboard reads from the catalog only, so the in-modal template counts show 14, not 33.

| Content type | In catalog | Notes |
|---|---|---|
| Long-form guide | 3 | DC full guide · Forms in Eligibility full guide · **Eligibility Onboarding** (the flagship, ~4,800 words, cross-cuts the module — cites 21 sources spanning wiki + tickets) |
| Micro guide | 5 | Hand-authored. 19 additional micro-guides exist as raw PDF-extracts in `raw/guides/markdown/SC/Eligibility/Quick-Guide/` but aren't catalogued |
| Quick reference | 2 | DC Potential Matches one-pager · Eligibility Reports cheat-sheet |
| FAQ | 2 | Direct Certification · Forms |
| SOP / how-to | 2 | Daily DC Potential Matches Review · Daily Pending Applications & Pending Students Review |

Every customer-facing claim is grounded in a real source. Customer view never shows internal markers (`NXT-####` ticket IDs, draft/review status fields) — those exist in the source files for audit but are stripped at render time.

---

## The Friday demo arc (current — track-first; Brio is the default landing)

**This replaces the prior inbox-first 7-step arc.** Page opens in Brio. ~5 min walkthrough:

1. **Page loads → already in Brio.** Banner reads *"Approve Cashier Day 1 to launch Friday."* Dallas: *"This is what our implementation team sees every day. Today's job: approve the Cashier Day 1 track for Friday's launch."*
2. **Point at the readiness signals on the banner** (47 claims sourced, quiz coverage complete, N AI-flagged spots). *"Schoolie did the lift. Product approves the track. SMEs only get pulled in for the rare AI-flagged field-reality question."*
3. **Click ▸ Approve & ship the track.** Banner flips to shipped state; hero track badge turns green. *"That's how a track ships. ~30 seconds of Product time."* — Friday's headline moment.
4. **Scroll to Outcomes section.** Point at `5 sites cleared this week · vs ~14d in-person baseline`. *"This is what Brio improves on. Two trainers in LA take 14 days per site. Brio is hitting 6.4."* — connects to the broader Cybersoft pitch.
5. **Click "Continue composing" on Manager Onboarding track.** Empty slots fill one at a time over ~3 seconds. *"And this is how the next track gets composed. AI proposes, Product approves, ships to the next role."*
6. **Click *Customer view* in the top toggle.** Click the **Onboard me as a new admin** starter chip. The 21-source streamed answer plays. Sources rail demonstrates all 5 content types contributing. *"And this is what a district admin sees when they ask Schoolie a question. Powered by everything you just saw on the Brio side."*
7. **(optional) Flip Mastery mode + click the same chip.** Answer ends with interactive quiz; Mastery badge on completion. *"Premium tier — what we charge districts extra for."*
8. **(optional) Flip language EN → ES.** Page chrome translates. *"Multi-language built in."*
9. **(optional, to address recording mechanic) Click ✦ Edit with Schoolie on any guide.** Yellow `[SME QUESTION]` markers surface. Schoolie drafts an answer → Apply → gap closes live. *"This is the lighter contribution path — SMEs can answer one question at a time in chat. Recording's the bigger lift but optional."*

**Narrative the arc lands as:** Brio (internal product) ships outcomes → Schoolie (the AI) is the engine inside it → customer view is the rendered result. SMEs see Brio FIRST so the framing they leave with is *"my recordings become outcomes the implementation team ships."* Not *"verify these docs."*

---

## What's missing / risky for Friday

### Critical — high risk, address before Friday

- **Brio name not validated with Dallas.** The name was decided in this session in a 90-second copy iteration ("just go with Brio for now"). Dallas hasn't seen it. If he wants something else, the toggle, aria-label, and "Back to Brio" copy all need updating (low effort, but coordinate). Riskiest open item.
- **Dallas hasn't seen the track-first reframe.** The previous (Iteration 3) handoff documented an inbox-first design. If Dallas walks in expecting "verify these 9 docs" and sees "approve this learning plan," the meeting opens with a recalibration moment, not the pitch. **Send Dallas a 60-second async note before Friday.**
- **Outcomes numbers are demo-static.** *"5 sites cleared · 6.4d vs 14d baseline"* etc. are made up — Brio has zero live customers. If an SME asks where the numbers come from, you need a clean answer. Either label *"(illustrative — projected once districts are live)"* or own the demo-state in narration.
- **Module roadmap visibility.** The catalog is Eligibility-only. 20+ other modules exist on disk as wiki content but don't surface. SMEs from other module areas will look for their slot and not see one. ~30-min fix: a "Coming soon" tile row showing named modules with current state.
- **"What happens after Friday" workflow.** SMEs need to know what action they're being asked to commit to. The drop-zone visualizes the mechanism but there's no follow-up — no calendar invite, no email queue. Charlie's role is implicit; make it explicit in narration ("Charlie will reach out by [date] to schedule your session").

### Useful — would strengthen Friday, won't block it

- **Real AI for free-form questions.** All 5 starter-prompt answers are pre-canned for demo reliability; free-form input hits a graceful "I don't have a confident answer yet" fallback. Fine for Friday's 5-starter demo, known gap for ANC.
- **Real transcript ingestion.** The drop-zone is theater. `raw/transcripts/` is reserved per `jira-brain/CLAUDE.md` anti-hallucination rules. Future-state, not Friday-state.

### Out of scope (explicitly mentioned, not pursued)

- Embedded chatbot inside SchoolCafé / PrimeroEdge (long-term vision)
- CEU / Professional Standards tracking integration (next-module play)
- Real role-based content filtering (claimed in `.ctx` strip, not enforced in catalog)
- PDFs for all 33 docs (only 4 original SchoolCafé quick-guides have PDFs)
- SSO / user accounts (future role-based gating)

### Click-safety bugs FIXED this session (do not re-introduce)

1. **`renderBwTracks` was inside `/* DEAD_BLOCK_START ... DEAD_BLOCK_END */`** — tracks board wasn't rendering at all in the prior build. Extracted to live code; verified renders 4 tracks. `composeTrackWithAi()` also extracted from the dead block.
2. **Templates "Generate from source"** scrolled to `#bw-drop` which lives inside a hidden modal. Now calls `openAddSourceModal()`.
3. **Outcome banner had stale ID wiring** — JS updated `bw-outcome-count/time/percent/bar`; HTML defined `bw-outcome-counts/published/total/ready/generating`. Replaced banner HTML + `renderOutcomeBanner()` together.
4. **Hero track filled slots without `source`** silently no-op'd on click. Now they only get `data-clickable="1"` (and pointer cursor) when a real source exists.
5. **`.ctx` was below `.builder-workspace` in DOM order** — at `top: 2269px` in builder mode, well below the 720px viewport. Moved above the workspace in source order. Toggle now reachable in both modes.
6. **Body wasn't `builder-mode` on load** — the page opened in customer view despite Brio being the intended landing. Added `class="builder-mode"` to `<body>` and moved `.active`/`aria-selected="true"` to the Brio toggle button.

---

---

## The bigger vision (what Brio *becomes* past Friday)

Dallas's two-deadline view is the surface goal. Underneath it is a longer-arc product the team is converging on. This section captures where the framework conversation landed across multiple rounds — what makes this a *platform*, not just a doc site.

### The two real hurdles for districts switching software

Every district eval comes down to two anxieties:

1. **Data onboarding** — moving their existing items, menus, students, eligibility records into the new platform without losing anything. Mostly an engineering / data-migration problem.
2. **Change management** — getting their cashiers, cafeteria managers, eligibility admins, and director comfortable enough that **day 1 doesn't break**. This is what Brio is for (Schoolie is the AI inside it that makes the content engine work).

Brio's whole reason for existing is to make the change-management hurdle disappear. The concrete pitch a new collaborator should internalize and repeat:

> *"Within 4 hours of granting a new cashier system access, they've completed their Day 1 track, passed the scenario quiz, and you have a cert showing they're cleared to operate the POS. That replaces the ~$120k of on-site trainer time you'd otherwise pay. Same engine onboards your eligibility admin in two days, your cafeteria managers in a week, your director in an hour."*

That's the line. Everything below supports it.

### The platform, in five layers

The current demo only fully covers Layer 1 (Content) plus the chat/answer surface on top. The framework Dallas is actually moving toward has five layers:

| Layer | What | Status |
|---|---|---|
| **1. Content** | Resources, Templates | ✓ Built (33 docs, 5 templates) |
| **2. Assessment** | Questions, Quizzes | Partial — Mastery checkpoints exist but questions aren't first-class |
| **3. Sequencing** | Lesson Plans, Training Tracks | Not built |
| **4. Learners** | Profiles, Progress, Badges | Not built |
| **5. Authoring** | AI-suggest + SME-approve workflow | Partial — Edit-with-Schoolie exists for resources, not for questions |

### The data model in one minute

```
Question {
  id, stem, options[], correct_index, explanation,
  bloom_level,           // recall / apply / analyze / evaluate
  difficulty,            // 1–5
  topics[],              // tags
  role_applicability[],  // cashier, manager, admin, director — who this question is FOR
  source_refs[],         // grounding (same ticket/wiki refs as resources)
  status,                // ai_drafted, sme_approved, deprecated
  bank_owner,            // which SME owns it (federated)
}

Quiz {
  id, title, attached_to: { resource_id?, lesson_plan_id? },
  question_ids[],
  scope_roles[],         // who this quiz instance is for
  pass_threshold, randomize, time_limit
}

LessonPlan {
  id, title, target_role,
  items[]: [{ kind: "resource", id }, { kind: "quiz", id }, ...]
  learning_objectives[]
}

TrainingTrack {
  id, title, target_role,
  lesson_plan_sequence[],
  prerequisite_tracks[],
}
```

### Federated SME-owned question banks (locked decision)

Each SME owns the question bank for their domain. No centralized curator, no committee bottleneck. The federation is glued together by **role-applicability tags** on every question — a question authored by the Eligibility SME tagged `cashier + manager` can be pulled into a cross-cutting Cafeteria Manager Onboarding track without the Eligibility SME doing any coordination.

This decision unlocks parallel authoring (every SME can work simultaneously), avoids the bottleneck pattern that killed previous documentation efforts, and keeps each module's quality bar with the person closest to it.

### Role-specific quizzes for the same training (the strong version)

There's a weak version and a strong version:

- **Weak**: same questions, different presentation per role — useless
- **Wrong**: different difficulty per role (manager harder, cashier easier) — patronizing
- **STRONG**: same content, different *cognitive focus* per role, mapped to Bloom's taxonomy:

| Role | Cognitive focus | Bloom levels | Example for "Pending Application at CEP site" |
|---|---|---|---|
| **Cashier** | Procedural execution | Recall · Apply | *"You see a Pending Application alert at your POS. Who do you tell?"* |
| **Cafeteria Manager** | Decision-making | Apply · Analyze | *"A Pending Application has students at a CEP site. What's the right call and why?"* |
| **Eligibility Admin** | Synthesis | Analyze · Evaluate | *"Walk through the relationship between DC, Household Apps, Forms, and CEP — when do they conflict?"* |
| **Director** | Audit-readiness | Evaluate | *"You're being audited tomorrow. Walk me through the evidence trail you'd produce."* |

Each question carries both a Bloom tag AND a role-applicability list. A "Cafeteria Manager quiz" auto-pulls questions tagged `manager + (apply OR analyze)`. Same source content, different cognitive lens.

### Learning-science patterns to bake into the data model (not bolt on)

Five research-backed patterns that shape the framework, not just the UI:

1. **Retrieval practice beats re-reading.** A quiz BEFORE the resource boosts retention more than after. Lesson plans need to support `pre-quiz → resource → post-quiz`.
2. **Spaced repetition.** Once a learner answers a question, schedule it to resurface at expanding intervals. Implies a cross-cutting queue/scheduler outside any specific lesson plan.
3. **Interleaving over blocking.** A quiz that mixes related topics outperforms one that drills a single topic. Default to interleaved question selection.
4. **Elaborative interrogation.** "Why does this matter?" / "What would happen if X?" beats fact recall. Open-ended question type alongside multiple-choice.
5. **Transfer over recall.** Test the rule applied to a situation NOT in the source resource. Tag each question `recall` vs `transfer`.

### The four end-user training tracks

The internal SMEs are the *authors*. The end-users — cashiers, cafeteria managers, eligibility admins, directors — are the *learners*. The four tracks Schoolie should produce:

**Cashier — Day 1 Track (~30 min, sandbox-heavy)**

Most numerous, least technical, lowest cognitive load. Cashiers learn by *doing*, not reading.

- POS basics (interactive sandbox, no reading)
- Serving a meal start-to-finish (sandbox)
- The 4 things that go wrong + what to do
- Scenario quiz → Day 1 cert

Almost no multiple-choice. 95% scenario / tap-the-right-thing on a simulated POS.

**Cafeteria Manager — Onboarding (~4–6 hours over a week)**

Daily ops + judgment calls. Cross-cuts Accountability + Eligibility + Inventory. Pulls from at least 3 SMEs' question banks — the federated model earns its keep here.

- Dashboard + daily routine
- Reconciliation & deposits (the SOP we already wrote)
- Working with applications (the Pending review SOP we already wrote)
- Reports your director will ask for
- Common issues + escalation
- Scenario final ("walk through your typical Monday morning")

**Eligibility Admin — Multi-day (~8–16 hours)**

The expert user. Higher-Bloom questions (analyze, evaluate). Heavy reading + analysis.

- Track A: Eligibility core (the 4 paths a student gets to a meal price)
- Track B: Forms framework
- Track C: Verification cycle (annual)
- Track D: Reports + audit prep

Pulls heavily on the long-form guides already authored.

**Director — Executive Tour (~1 hour)**

Oversight role. Audit-scenario questions. Short, high-density, evaluative.

- What reports answer what questions
- Where to look during an audit
- Red flags + escalation paths

### The 6th content type Dallas didn't ask for (but probably needs)

The 5 templates Dallas specified are all **reading-friendly**: long-form, micro, quick reference, FAQ, SOP. They fit Eligibility Admin and Director learners. They do NOT fit Cashier learners.

**Proposed 6th type: Interactive Procedure.** Defined by:
- A sandbox (the in-product workflow, faithfully simulated)
- A scenario script (branches based on learner action)
- A checkpoint (proof the learner can execute the procedure)

No long reading body. Pulled into Cashier and Cafeteria-Manager tracks as the default unit. **Additive, not a swap-out**. The 5 reading templates still serve admin/director audiences perfectly.

### The "approve, don't author" workflow

The single most important UX principle for the SME-facing build:

**Don't make "build a quiz from scratch" the primary verb. Make "approve Schoolie's draft" the primary verb.**

SMEs are busy. If "build a quiz" is the workflow, you get 0 quizzes built. If "approve / kill / edit Schoolie's draft questions" is the workflow, you get hundreds.

The flow:

1. SME publishes / edits a resource
2. Schoolie auto-drafts 8–15 candidate questions, tagged by Bloom + role
3. SME verifies the doc — candidate questions appear in a sticky rail beside the rendered doc as the SME reads it
4. Per item: *Looks good ✓ / Edit ✎ / Kill ✗* — approved questions land in their federated bank
5. When the doc is verified, the quiz ships with it automatically
6. Quizzes get role-scoped at composition time (auto-pulled from bank by tag intersection)

**The SME never sees the words "build a quiz."** They verify a doc; the quiz is a byproduct of that single verification pass. See the inbox + verification model section below for the concrete UX.

Same pattern as the Foundation framing for resources: AI does 80% of the lift, SME polishes the 20%.

### Additional primitives worth adding (beyond quizzes)

Two engagement-side question types that go beyond multiple-choice:

- **Scenarios** — story-based, branching prompts. *"An application lands in Pending. Walk through your decisions, you'll be asked at each step."* Tests high-Bloom reasoning, beats MC for transfer.
- **Reflections** — open-ended prompts at the end of a track. *"Describe a time at your district when X happened. What would you do differently now?"* Not graded — but answers feed Schoolie's understanding of that district's specific context for future personalization.

### The manager dashboard (where the gamification idea actually fits)

Earlier in the build conversation we explicitly killed the public leaderboard concept ("don't make SMEs compete in front of each other"). The leaderboard / gamification energy still has a home — but at the **manager-internal** level:

- A cafeteria manager sees their 8 cashiers' Day 1 completion state
- A district director sees the same for their managers
- Stakes are clear, accountability is local, no cross-district shame

That's the right shape for the gamification primitive. Builder side has stat snapshots (collective, no names). Manager side has individual progress (within their own team, private).

---

## Brio architecture reference (selectors, functions, state)

For an LLM resuming this work — what's wired where:

| Element / behavior | ID or selector | Notes |
|---|---|---|
| Default mode | `<body class="builder-mode">` | Brio opens by default; customer view reached via toggle |
| View toggle | `#view-toggle` with two buttons `data-mode="customer"` / `data-mode="builder"` | Inside `.ctx` strip. `.ctx` was moved ABOVE `.builder-workspace` in source order this session so the toggle is reachable in both modes |
| Brio workspace root | `<main class="builder-workspace" id="builder-workspace" aria-label="Brio">` | Shown when `body.builder-mode`; hidden otherwise |
| Verification view root | `<section class="verification-view" id="verification-view">` | Shown when `body.verification-mode`; hides Brio workspace |
| Outcome banner | `#bw-outcome` | Gets `.shipped` class after `approveTrack()` |
| Banner readiness signals | `#bw-outcome-claims` / `#bw-outcome-light-evidence` / `#bw-outcome-flag-label` | Live-updated by `renderOutcomeBanner()` |
| Primary CTA | `#bw-approve-track` | Wired to `approveTrack()`. Idempotent (`_cashierDay1Shipped` guard) |
| Spot-check link in banner | `#bw-spotcheck-link` (`href="#bw-inbox-anchor"`) | Generic `a[href="#bw-inbox-anchor"]` handler scrolls to inbox |
| Tracks board | `#bw-tracks` | Rendered by `renderBwTracks()`. **Was previously inside `/* DEAD_BLOCK_START ... DEAD_BLOCK_END */`** and not rendering. Extracted to live code this session. |
| Hero track class | `.bw-track--hero` applied to first track | Full-width, soft-purple gradient, *Friday launch* → *✓ Shipped Friday* badge |
| Outcomes section | `#bw-outcomes-anchor` | NEW this session. Static demo data — no real data layer |
| Outcomes stat cards | `.bw-outcome-card` (4 of them) | Site-anchored: sites cleared / in progress / avg time-to-clear / flagged. The `vs ~14d in-person baseline` chip is load-bearing for the LA pitch |
| Per-track outcomes table | `.bw-outcomes-track-row` (4 rows) | Role-colored left borders: `.role-cashier` / `.role-manager` / `.role-admin` / `.role-director`. Shows learners cleared / pass rate / avg time |
| Spot-check inbox | `.bw-inbox--secondary` with `#bw-inbox-anchor` | Demoted from primary. Row click → verification view via `openVerification()` |
| +Generate FAB | `#bw-add-fab` | Opens `#bw-add-scrim` modal |
| Generate modal | `#bw-add-scrim` → `.bw-add-modal` (max-width 780px, scrollable) | Contains: drop-zone (`#bw-drop`) + dashed divider + templates section (`.bw-add-templates`) |
| Templates grid | `#bw-template-grid` (INSIDE the modal — moved from a standalone bottom section this session) | 6 cards: long-form, micro, quick-reference, faq, sop-how-to, interactive-procedure (NEW). Single per-card action: *See examples →* (closes modal, flips to customer, filters by `content_type`) |
| Verification view | `openVerification(resourceId)` → `vvBulkApprove()` / `vvAction()` / `vvMarkVerified()` / `closeVerification()` / `nextDocInInbox()` | Preserved from Iteration 3. Markers + questions per-doc, bulk-approve, success overlay, chain-to-next |

**Key state:**
- `_cashierDay1Shipped` (boolean) — set true after `approveTrack()`. Read by `renderOutcomeBanner()` and `renderBwTracks()` to toggle shipped UI
- `markerState` (map) — `${resourceId}:m${index}` → `pending | approved | rejected | skipped`. Synthesized from `[SME QUESTION:...]` regex in inline markdown
- `questionState` (map) — per-question-id → same states. Initialized from `questionsDb.candidates` JSON
- `currentVerificationResourceId` (string) — which resource the verification view is currently showing
- `BW_TRACKS` (const array) — 4 tracks hardcoded. Cashier Day 1 slots have NO `source` fields (track is theatrical for demo); other tracks have some real sources pointing into the catalog
- `BW_TEMPLATES` (const array) — 6 templates. `isNew: true` on `interactive-procedure` → renders compact lavender `NEW` pill (was a heavy purple "NEW · proposed" pill; lightened this session for visual balance)

## Naming + persona

**Brio is the product. Schoolie is the AI inside it. Do not conflate.** (See TL;DR for naming history.)

**Internal user persona is Product (Product Manager doing content-launch approval).** Implementation, Training, and SMEs are NOT on the hook for routine doc verification. The outcome-banner trainer chip *"rahul · Product · Eligibility content"* makes this load-bearing on screen. The "Work saved this week" footer strip ends with *"0 Implementation reviews assigned"* — that line is the political move that says *"this is not another queue for the implementation team."*

The user clarified mid-session that Charlie is purely a coordinator/liaison. Charlie does NOT review docs. Product owns guide accuracy via grounding-audit signals (47 claims sourced / N AI-flagged spots), not via SME-consultation by default. SME consult is a rare escape hatch (the `Blocked · SME consult needed` status), not a workflow.

## Design iteration history

**Iteration 1** — four-stat dashboard + tiles + Tinder-swipe modal. Dashboard pattern fit ops/monitoring, not focused review work. Killed.

**Iteration 2** — inbox + verification model. Each doc had "PM-approved · awaiting your SME sign-off" pill. Wrong ownership read (SME framed as approver) and status contradiction. Killed.

**Iteration 3** — same inbox + verification shape, with ownership reframed: every label said *Product owns this.* Inbox header *"Product review inbox · Cashier Day 1 launch."* Lifecycle pills (*Needs Product review / Blocked · SME consult needed / Ready to publish*). This is what the original handoff documented as "current." **No longer current.**

**Iteration 4 (current)** — **track-first.** Cagan call this session: the unit of value is a *cleared site* (then *trained learner*), NOT an approved doc. Doc approval is bookkeeping; should not be the front door. Reframe:
- Outcome banner anchors on the *track to ship Friday* (Cashier Day 1), not the 9 docs to review
- Tracks board promoted to the primary surface below the banner
- Cashier Day 1 gets `.bw-track--hero` treatment
- Doc-by-doc inbox demoted to "Spot-check individual resources · OPTIONAL"
- Quality gate moves from per-doc approval to **grounding-audit signals on the banner** (47 claims sourced, 0 ungrounded, N AI-flagged spots). Product trusts the AI by default; drills in only when the AI itself flags low confidence
- **Outcomes section added** below tracks — site-anchored metrics + per-track learner performance
- **Templates moved into the +Generate modal** (no longer a bottom workspace section)
- Brio brand applied to the toggle button (was "Workspace", before that "Product review")
- Brio is the default landing (`<body class="builder-mode">`)
- Verification view from Iteration 3 PRESERVED (still works for spot-check drill-down)

## Why track-first works for the Friday SME room

- **Single primary verb:** "Approve the track." Not "review 9 docs."
- **Outcome over output:** the banner anchors on what ships to learners, not on what's pending review
- **Soft-ask for SMEs:** Product approves the track; SMEs see they're not on the hook for routine review
- **Brand-forward:** "Brio" labels the internal surface so SMEs perceive it as a product, not an internal tool
- **Outcome story baked in:** the Outcomes section gives a concrete answer to *"so what does this produce?"* — sites cleared faster than the in-person trainer baseline

---

## Questions a next collaborator (LLM or human) should resolve before Friday

1. **Has Dallas seen the track-first reframe and the Brio name?** Riskiest open item. The previous handoff documented an Iteration-3 inbox-first design and called the workspace "Product review." Both are gone. If Dallas walks in expecting the old model or a different product name, the demo opens with recalibration instead of pitch. **Recommend a 60-second async note to Dallas before Friday.**
2. **Are the Outcomes numbers OK as demo-static, or do they need an *(illustrative)* label?** "5 sites cleared · vs ~14d in-person baseline" reads as live data but isn't (Brio has no customers yet). If an SME asks where the numbers come from, you need a clean answer.
3. **Who's in the Friday room?** If it's Charlie + 3 SMEs, the current demo is sufficient. If Banu (engineering lead) or anyone from product/sales is there too, a separate 60-second "path to production" answer is needed (cost, scale, data privacy, hosting).
4. **Is the "recording is the bonus path / Product owns review" framing aligned with Dallas?** Deliberate softening from the original "click record yesterday" energy. SMEs feel less pressured but urgency might dilute.
5. **Are real SME names usable on any placeholder content, or strictly off-limits?** Landed on no real names previously. Worth re-confirming.
6. **What's the followup mechanism after Friday?** Without it, the meeting is theater. The drop-zone in the modal visualizes the mechanism but there's no real follow-up (calendar invite, email queue, SME-assignment sheet). Charlie's role is implicit.

---

## File pointers (for next-session orientation)

| What | Where |
|---|---|
| **The demo** | `wiki/training/resource-center-v2.html` — open in any browser, ~400 KB self-contained |
| **This handoff** | `wiki/training/CHAT_HANDOFF.md` — update it when you make non-trivial design moves |
| Templates (on disk) | `templates/` (Interactive Procedure type is proposed, may not be in this dir yet) |
| Hand-authored Eligibility docs | `resources/eligibility/` |
| Raw PDF-extracted guides | `raw/guides/markdown/SC/Eligibility/Quick-Guide/` (19 files; not in catalog) |
| Catalog of record | `catalog/resources.json` (14 resources currently — dashboard reads from here) |
| SME review tracker | `wiki/guides/eligibility/sme_review_log.md` |
| Anti-hallucination ruleset | `jira-brain/CLAUDE.md` (read first if generating new content) |
| The kickoff transcript | `May-13-11-01-AM-dedfd722-531f.md` (in user's Downloads) |
| Dallas's design-pass HTML | `eligibility_onboarding_design_pass.html` (in user's Downloads) |
