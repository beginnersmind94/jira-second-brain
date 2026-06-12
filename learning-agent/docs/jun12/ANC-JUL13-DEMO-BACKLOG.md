# ANC July 13 — Demo Build Plan & Agent Backlog

**Date:** 2026-06-12 · **Status: AWAITING RAHUL'S FINAL NOD — nothing dispatched, no code changed.**
**Supersedes priorities in** `DATACAMP-PARITY-BACKLOG.md` (same audit evidence; that doc remains the parity reference).
**Mission:** Two outcomes at ANC on **July 13** (31 days out): (1) customers walk away excited enough to ask "when can my district have this," and (2) leadership sees a product, not a prototype, and funds the dev team. Everything below is judged by one question: *does it make the demo undeniable?*

**Operating posture:** This is a demo build, not a production hardening pass. Façades are acceptable wherever they photograph perfectly and we don't verbally claim them as live integrations. The one thing that is never façade is **grounding** — the citation gate is the moat and the sales story; it stays real on every new content type. MVP/BRD rigor (SSO, real roster sync, SCORM suspend-data, multi-node) is explicitly parked for when dev investment lands — it becomes the *roadmap slide*, which is exactly where it earns money.

---

## 1. The demo storyline (every to-do exists to power a beat in this script)

### Act 1 — "Watch it build" · ~8 min · the investment moment
Dallas uploads a real training transcript → picks a template → generation runs (pre-warmed; trace replays on screen) → **the gate moment:** "158 claims. 158 verified against Jira, verbatim, correct tier. Zero hallucinations — by construction, not by hope." → PO approves into the Library → one click generates a quiz, every answer carrying its source quote → Dallas assembles a **course** in under 2 minutes: the new guide + an ICN/USDA food-safety YouTube video + the quiz + a flashcard deck → drops it into the **"New Cashier Onboarding" track** → assigns to Houston ISD cashiers, due July 31. Stat overlay: **"~11 minutes. About a dollar. Every claim cited."** (vs. the ~$100k/yr documentation tool.)

### Act 2 — "Meet John" · ~5 min · the customer-excitement moment
A phone (projected in a device frame). John the cashier opens his link: **"Up next for you — New Cashier Onboarding, 12 min."** He moves through the course player: a 4-minute lesson, the embedded ICN video with its USDA attribution band, a quiz with instant source-backed feedback ("Correct — here's the exact line from the approved guide"), **streak +1, XP, badge**, track complete → short assessment → **certificate with his name on it**, downloaded on the spot.

### Act 3 — "Dana sees it land" · ~3 min · the compliance moment
Dana's **My Team** dashboard — John's completion has *already appeared* (live, because progress is real). The overdue list against the July 31 deadline. One-click nudge ("Reminder sent"). Download the board-ready compliance report. Close: "Your state review packet, one button."

### Booth loop — "Your turn" · runs all day · the lead machine
QR code on the booth banner → attendee's **own phone** → they enter a first name, pick "Cashier" → a 3-minute micro-course (lesson + ICN clip + 3-question quiz) → a **personalized certificate** with their name, downloadable, optional email field for follow-up. Reset-to-pristine between visitors. *Nothing converts a hallway crowd like earning a certificate on your own phone in 3 minutes.*

---

## 2. Calendar (working back from July 13)

| Window | Wave | Theme |
|---|---|---|
| **Jun 13–20** | Wave 1 | Foundations: real course entity, question types, video embedding, provenance sweep, demo-mode flag |
| **Jun 21–28** | Wave 2 | The player: unified course player, mobile/perf, assessments, flashcards, onboarding |
| **Jun 29–Jul 5** | Wave 3 | Delight: gamification, practice, deadlines/assignment, live My Team, demo content library, stat overlays |
| **Jul 6–9** | Wave 4 | Demo ops: booth flow, run-of-show, rehearsal fixes only. **FEATURE FREEZE Jul 9 EOD.** |
| **Jul 10–11** | — | Dress rehearsals on final data; record the fallback video; pack list |
| **Jul 13** | — | ANC |

**Cut-line discipline:** CORE items ship or the storyline breaks. ENHANCER items ship only if their wave is green by its midpoint; otherwise they fall to post-ANC without discussion. DEFER items are already post-ANC — they appear on the roadmap slide, not the screen.

---

## 3. Decision defaults (baked in — veto by Jun 13 or these stand)

- **DEC-1 → ADOPTED: Track → Course → Lesson.** The demo needs the DataCamp shape. Legacy flat tracks render as single-course tracks via shim.
- **DEC-2 → ADOPTED: real YouTube iframe embeds** for ICN assets whose `license_posture` permits, with a persistent USDA/ICN attribution band; `link_only` assets get a credited link-out card. Standard YouTube embedding is the credited-streaming mechanism. Offline fallback chrome built for the booth (conference Wi-Fi is a known enemy).
- **DEC-3 → ADOPTED: free-text course/track descriptions allowed**, badged `human-authored`, linted for product-claim patterns (numbers, field names, "the system will…") with a warn-not-block. Lesson *content* keeps the no-free-claim moat.
- **DEC-4 → ADOPTED: XP + streaks + completion badges. No leaderboards.** Tasteful, not casino. Aggregate-only visibility to managers.

---

## 4. The backlog — detailed agent briefs with success criteria

Conventions: **Tier** = CORE (storyline breaks without it) / ENHANCER (ships if wave is green) / DEFER (post-ANC, roadmap slide). Every brief is self-contained for a cold agent. Every item inherits §6 (trust guardrails) and §7 (what we don't claim). Evidence pointers reference the audited build (`demo_app.py`, `static/index.html`, `quiz_store.py`, `qbank_gate.py`, `completion_store.py`, `modules_store.py`, `auth.py`, `tenancy.py`).

---

### WAVE 1 — Foundations (Jun 13–20)

---

#### A1 — Promote Course to a real server entity
**Tier:** CORE · **Wave:** 1 · **Size:** L · **Depends:** none (DEC-1 adopted)
**Demo moment:** Act 1's course-assembly beat; the entire Act 2 player stands on this.
**Agent brief:** Today `cbSave()` (index.html ≈4770) writes courses to `_demoState.userCourses` — client-side, gone on reload. Tracks are real (`data/tracks/<id>.json`) but hold flat `module_ids`. Build the course entity:
- `data/courses/<id>.json`: `{id, title, description, product, role_tags, lessons: [{type: 'guide'|'quiz'|'video'|'flashcards'|'external_icn'|'exercise', ref, title, duration_est}], status: 'draft'|'published', created_at, updated_at}`.
- CRUD + publish endpoints mirroring the `/api/tracks` pattern, tenancy-gated the same way (`assert_district_access` style).
- Server-side ref validation: a lesson `ref` must resolve to an **approved** library resource, a **published** quiz/flashcard deck, or an ICN catalog id. Unknown/draft refs → 422 with a named reason.
- Track schema gains ordered `course_ids`. Migration shim: a track with legacy `module_ids` and no `course_ids` exposes one implicit course ("Course 1") so every existing seeded track renders unchanged.
**Success criteria:**
1. Create → restart server → course intact with lesson order preserved.
2. POST a lesson ref pointing at a draft guide → 422, named error; approved guide → 201.
3. Every pre-existing seeded track renders identically to today (screenshot diff acceptable).
4. Publish requires ≥1 lesson; published course is immediately visible to `GET /api/tracks/{tid}` expansion.
5. Tenancy: learner persona requesting another district's course → 403.
**Demo check:** Dallas builds a 4-lesson course, refreshes the browser mid-demo, nothing is lost.

---

#### A2 — Course builder UI on the real API
**Tier:** CORE · **Wave:** 1 · **Size:** M · **Depends:** A1
**Demo moment:** Act 1 — "assemble a course in under 2 minutes," live on stage.
**Agent brief:** Rewire `openCourseBuilder()` to A1's endpoints. Required interactions: create, rename, add lesson by type (guide picker shows approved library only; quiz picker shows published quizzes; video picker shows ICN catalog filtered to embeddable; flashcards picker per B2), reorder (drag or arrows), remove, publish, delete-with-confirm. Add **"Preview as learner"** — renders the D1 player read-only in a modal/route, with full provenance badges and the customer-view chrome. Keep existing labels ("Courses," "Tracks") — no renames (standing nav-preservation feedback).
**Success criteria:**
1. Full loop create → edit → reorder → publish → appears inside a track → visible in learner view, with zero page-state loss on reload at any step.
2. Preview-as-learner is pixel-identical to the real player for the same course (same badges, same chrome).
3. Adding 4 mixed-type lessons takes ≤8 clicks/taps beyond the pickers themselves — count them; ceremony is the enemy (Jaime lens).
4. Builder unreachable in customer view mode.
**Demo check:** timed rehearsal — transcript-approved guide to published course in **<2 minutes** without rushing.

---

#### B1 — Grounded question types beyond MCQ (T/F, fill-in-blank, step-ordering)
**Tier:** CORE · **Wave:** 1 · **Size:** L · **Depends:** none
**Demo moment:** Act 1's quiz beat and Act 2's taking experience stop looking like a toy ("it's not just multiple choice").
**Agent brief:** Extend the existing 3-gate pipeline (`qbank_gate.py`: lane-match + verbatim + semantic judge; `quiz_store.py`: provenance, drift hash, approval re-gate) with three deterministic-groundable types:
- **True/False** — TRUE statements are verbatim spans. FALSE statements are *mechanical* negations of a span (stored with `distractor_basis: {span, transform: 'negation'}`); the source span ships with the question for feedback.
- **Fill-in-the-blank** — the blank is a verbatim span; the stem is the literal surrounding sentence. Gate check: `stem.replace('___', answer)` reassembles to an exact source substring (normalized whitespace).
- **Step-ordering** — items are the actual ordered steps from an AC-cited workflow section, shuffled. No invented steps; wrong orderings are the only "distractor."
Extend generation prompts per type, gate lanes per type, the quiz builder UI (type chips + per-type editor), `openTaker()` rendering (T/F buttons, text/select blank input, drag-or-tap ordering), and `/api/quizzes/{qid}/score` per type. CLAUDE.md quiz rules hold: 3–10 questions, distinct concepts, each question cites its guide section.
**Success criteria:**
1. Each type round-trips generate → gate → approve → take → score, with the per-question source quote in post-answer feedback.
2. Gate red-team: hand-craft one violation per type (paraphrased blank, invented step, non-mechanical false statement) → all three rejected with named reasons.
3. Ordering interaction works by touch on a 375px viewport (tap-to-swap acceptable; drag optional).
4. Regression cases added per type and green.
5. A mixed-type 6-question quiz generates from a published guide in one click in <60s.
**Demo check:** Act 2 quiz contains at least 3 question types; feedback shows the verbatim source line each time.

---

#### C1 — Real video lessons: license-aware ICN YouTube embedding
**Tier:** CORE · **Wave:** 1 · **Size:** M · **Depends:** none (DEC-2 adopted)
**Demo moment:** Act 1 (drop a USDA food-safety video into a course in one click) and Act 2 (the embedded clip that makes the player feel alive). This is the single cheapest "wow per engineering hour" in the plan.
**Agent brief:** Today video is `{type:'video', title, dur}` with no URL or player anywhere. The ICN catalog (`/api/icn`) already has `youtube`-typed assets and per-asset `license_posture`. Build:
- Video lesson refs point at **ICN asset ids only** (no raw URL entry — provenance by construction).
- Player card: YouTube iframe embed (`youtube-nocookie.com` domain) for embed-permitted postures, inside a card with a **persistent attribution band** — ICN/USDA logo treatment, asset title, license badge, outbound "View on source" link. The band is structural (not a dismissible overlay) and survives every breakpoint.
- `link_only` assets render as a credited link-out card (thumbnail, title, attribution, external-link affordance) — never an iframe.
- **Offline/booth fallback:** if the iframe fails to load in N seconds or an `OFFLINE_DEMO` flag is set, swap to the same card chrome with the cached thumbnail and a play-overlay that opens the link-out — the layout never breaks on dead Wi-Fi.
**Success criteria:**
1. Embed vs link-out branch driven 100% by catalog `license_posture` — no per-lesson override exists.
2. Attribution band visible at 1440px and 375px; cannot be removed via the builder.
3. Kill the network → player card degrades to fallback chrome with no layout shift or console-error toast.
4. No ICN content is downloaded, transcoded, or scraped — embed or link only (code-reviewable assertion).
5. Course builder video picker lists only embeddable assets under "Embed" and the rest under "Link-out," visually distinct.
**Demo check:** Act 2 plays 20 seconds of a real USDA/ICN food-safety video inside the lesson with the attribution band on screen.

---

#### F1 — Provenance sweep: badges + "show source" on every new surface
**Tier:** CORE · **Wave:** 1, re-run at each wave end · **Size:** S · **Depends:** runs alongside everything
**Demo moment:** The trust story Dallas *tells* must be the trust story the screen *shows*. Provenance badges are a selling point on stage ("see this badge? AI-grounded, every claim cited — this one's a USDA video, credited and linked").
**Agent brief:** Build the coverage matrix (surface × content origin × required affordance) for: player lesson panes, video cards, flashcard decks, assessments, practice cards, scenario steps, course/track cards, certificates. Implement gaps: origin badge (`AI-grounded` / `human-authored` / `outside-vendor`) + "show source" affordance on grounded content. Verify the **absence** of "every claim cited" framing on outside-vendor and human-authored content. Document as a repeatable per-wave checklist.
**Success criteria:**
1. Screenshot sweep: every surface in the matrix shows the correct badge — zero unlabeled content.
2. "Show source" on a grounded lesson opens the verbatim quote + tier within 1 click/tap.
3. Grep-level + visual over-claiming check passes (no cited-guarantee styling on ICN/imported content).
4. Checklist re-run recorded at the end of Waves 2 and 3.
**Demo check:** Dallas can tap any piece of content in any act and truthfully narrate its origin.

---

#### G4 — Conference demo mode (presentation flag + pristine reset)
**Tier:** CORE · **Wave:** 1 · **Size:** S · **Depends:** none
**Demo moment:** All of them — this is the stage rig.
**Agent brief:** A `DEMO_MODE=conference` env flag that: (1) swaps "DEMO DATA" watermarks on seeded artifacts for clean styling (compliance PDF included) — at a conference, *everything* is a demo and the watermark just undercuts the moment; (2) suppresses any internal/debug chrome; (3) adds an operator-only **"Reset demo"** action (hidden route or hotkey) that restores seeded state to pristine in <10s — John un-completes, booth visitors cleared, Dana's dashboard back to baseline; (4) pre-warms caches on boot (library, tracks, ICN thumbnails) so first paint is instant. Default remains today's honest-watermark behavior — the flag is opt-in and its existence is documented.
**Success criteria:**
1. Flag off → identical to today (watermarks intact).
2. Flag on → no watermark, no internal chrome, demo data renders clean.
3. Reset completes <10s and a full Act 2 run-through works immediately after, repeated 5× without drift.
4. Operator action is unreachable from customer view and not discoverable by a booth visitor.
**Demo check:** two consecutive booth visitors get identical pristine experiences 60 seconds apart.

---

### WAVE 2 — The player (Jun 21–28)

---

#### D1 — Unified course player
**Tier:** CORE · **Wave:** 2 · **Size:** L · **Depends:** A1 (schema), C1 (video card), B1 (taker types)
**Demo moment:** Act 2, all of it. This is the single biggest "it feels like DataCamp" item in the plan.
**Agent brief:** Replace the module-list-plus-PDF-links experience (`openRealTrack()`) with one player shell:
- **Left rail** (collapses to a bottom progress bar at mobile): courses → lessons with done-state checkmarks, locked state for prerequisites (A3), current-lesson highlight.
- **Main pane** renders lessons inline by type: guide HTML (the citation-stripped approved render — not a PDF link; PDF stays as a secondary download action), quiz (taker inline, not modal), video (C1 card), flashcards (B2 deck), exercise (B5 if it lands).
- **Prev/next** navigation; auto-advance prompt on lesson completion ("Nice — next: Food Safety Basics, 3 min").
- **Lesson-level progress:** extend `completion_store` records from `modules_done` to `lessons_done` (keep `modules_done` for legacy tracks via the shim); "Continue" deep-links to the exact lesson; progress ring on the track card.
- Per-lesson origin badge + show-source affordance (F1); customer-view banner logic holds inside the player.
**Success criteria:**
1. The cashier persona completes a full mixed-type course (guide → video → quiz → flashcards) start-to-finish on a **375px** viewport with no horizontal scroll and no dead end.
2. Close browser mid-course → reopen → "Continue" lands on the exact lesson; survives server restart.
3. Initial player render **<3s** measured on the demo laptop (performance marks logged; number recorded).
4. Every lesson pane shows its origin badge; trainer chrome unreachable from inside the player.
5. Legacy flat tracks play through the shim without visual regression.
**Demo check:** Act 2 runs end-to-end on the phone frame in under 5 minutes with zero navigation confusion — rehearsed and timed.

---

#### D6 — Mobile + performance + polish pass
**Tier:** CORE · **Wave:** 2 (after D1 merges) · **Size:** M · **Depends:** D1
**Demo moment:** Act 2 and the booth loop live on phones. A janky phone moment kills both.
**Agent brief:** Audit + fix all learner surfaces (Learn home, player, quiz taker, flashcards, practice when it lands, certificate) at 375px: no horizontal scroll, tap targets ≥44px, focus order sane, AA contrast on the new components, quiz/ordering interactions thumb-friendly, video card letterboxing correct. Performance: measure player load (`performance.now()` marks), attack the top offenders — index.html is one huge SPA, so lazy-load trainer-only JS/CSS away from the customer path; preload the demo course's assets in demo mode (G4). Visual polish to "DataCamp feel": consistent course-card imagery, progress rings, completion check animations — tasteful motion, no confetti storms (Jaime's users are reluctant adults; one celebration moment at certificate is enough).
**Success criteria:**
1. Screenshot evidence at 375px and 768px for every learner surface, no horizontal scroll anywhere.
2. Measured player load <3s on the demo laptop AND <5s on a mid-range phone over hotspot (booth reality); numbers recorded.
3. Tap-target audit: zero interactive elements <44px on learner surfaces.
4. Customer-view banner visible-but-unobtrusive at 375px.
5. One certificate-moment animation exists and is skippable.
**Demo check:** booth dry-run on an actual phone over a phone hotspot — full loop, no jank you can feel.

---

#### B3 — Skill assessment / track exam
**Tier:** CORE · **Wave:** 2 · **Size:** L · **Depends:** B1, A1
**Demo moment:** Act 2's finale — "prove it, get certified" — and the customer line "your state reviewer will love this."
**Agent brief:** Assessment entity assembled from **approved** questions across a track's guides (bank pull, not fresh generation): `data/assessments/<id>.json` with `{question_ids, time_limit_min, pass_pct, attempts_allowed, track_id}`. Builder: pick track → eligible approved questions grouped by guide → assemble (or "auto-assemble 8 questions" one-click for demo speed) → publish. Taker: timed (visible countdown), randomized question order, server-side scoring, attempt history in `completion_store`. Track option: **"certificate requires passing"** — wired into the cert issuance path. Source-quote feedback is withheld until after submission (protects retakes), then shown per question.
**Success criteria:**
1. Failing below `pass_pct` blocks the certificate when the gate option is on; passing issues it with the score recorded.
2. Attempts logged with timestamps; `attempts_allowed` enforced server-side.
3. Auto-assemble produces a valid 8-question mixed-type assessment from the demo track in one click.
4. Timer, navigation, and submission all work at 375px.
5. A question whose source guide drops back to draft is automatically ineligible; an assessment containing it reverts to draft (drift rule).
**Demo check:** Act 2 — John passes an 8-question timed assessment and the certificate records "Passed — 88%."

---

#### B2 — Guide flashcards (persistent, gated, attachable)
**Tier:** CORE · **Wave:** 2 · **Size:** M · **Depends:** A1 (lesson type)
**Demo moment:** Act 1 ("and flashcards, same click") + Act 2's deck + Wave 3's practice mode is built on this.
**Agent brief:** Port the ICN flashcard generator (`/api/icn/flashcards` — already grounded, on-demand) to published guides, with persistence: `data/flashcards/<id>.json` mirroring `quiz_store.py` (per-card `source_quote` + section ref, provenance flags, `source_content_hash` drift detection, approval endpoint re-running the verbatim gate). Deck builder UI alongside the quiz builder; deck attachable to courses as a lesson type (A1). Learner-side deck component: card flip interaction, "got it / review again" sorting, progress through deck — touch-first.
**Success criteria:**
1. Generate → gate → approve → attach → flip through in player, end to end.
2. Every card traces to a specific section of the **published** guide (CLAUDE.md rule); cards generate from published content only — never drafts/transcripts (code path, not convention).
3. Drifted source guide → deck reverts to draft and disappears from new course pickers.
4. Procedural cards ("What do you do when…") are preferred by the generation prompt and visibly present in the demo deck.
5. Deck interaction is satisfying on a phone — flip animation <200ms, swipe or tap both work.
**Demo check:** Act 1 generates a deck in one click; Act 2 John flips through 5 cards without instruction.

---

#### D2 — First-run onboarding & empty states
**Tier:** CORE · **Wave:** 2 · **Size:** S · **Depends:** D1
**Demo moment:** The first 10 seconds of Act 2 and the booth loop. Dead air on first run is the #1 listed trust blocker for demos.
**Agent brief:** First-visit flow: confirm role (pre-filled from persona; booth flow gets the picker) → assigned/recommended track hero with one-line "why you're seeing this" ("Assigned to all Houston ISD cashiers") → single primary CTA with honest time estimate ("Start — 12 min"). Empty states designed (not default-text) for: no tracks for role → show global tracks; track with no published courses; everything-finished → route to Practice (D4) or "more coming from your district." Zero LMS jargon in learner-facing strings: "track/course/lesson" allowed; "SCO/module/tenant/LMS" never.
**Success criteria:**
1. All three demo personas land on a designed, actionable first screen — zero blank or default states reachable.
2. String audit: no jargon terms in any learner-visible copy.
3. Booth persona path: role picker → recommended micro-course in ≤2 taps.
4. "Why you're seeing this" line present on the hero.
**Demo check:** hand the phone to someone who's never seen the app; they start the course within 15 seconds, unprompted.

---

### WAVE 3 — Delight & the live dashboard (Jun 29–Jul 5)

---

#### D3 — Gamification lite: XP, streaks, badges
**Tier:** CORE · **Wave:** 3 · **Size:** M · **Depends:** D1 (DEC-4 adopted)
**Demo moment:** Act 2's habit-loop beat ("your staff will *want* to finish") — the single most customer-legible DataCamp signature.
**Agent brief:** Server-side in `completion_store` (never localStorage): XP per completed lesson/quiz/assessment (flat documented values, e.g. lesson 10 / quiz 20 / assessment 50), daily streak (any completed lesson sustains it; missed day resets; keep rules simple enough to say aloud), badges (per-track completion + milestone). Learner home strip: streak flame, XP total, next-badge progress. Certificate carries earned badges. Aggregate-only to managers (counts, never per-learner XP rankings). Subtle visual language — celebration at cert, restraint everywhere else.
**Success criteria:**
1. XP/streak/badges persist server-side per user and survive restart.
2. Completing a lesson visibly increments XP and sustains the streak within 1s of the action.
3. No leaderboard exists; Dana's view shows aggregates only.
4. A learner who ignores gamification entirely loses zero functionality.
5. Badge renders on the certificate.
**Demo check:** Act 2 — the streak/XP moment lands in one glance without Dallas explaining it.

---

#### D4 — Practice mode (spaced repetition)
**Tier:** ENHANCER · **Wave:** 3 · **Size:** M · **Depends:** B2, B1
**Demo moment:** Act 2 epilogue / booth small-talk: "and tomorrow it asks him 5 questions to make it stick" — the retention story customers don't expect.
**Agent brief:** "Practice" tab in learner view: daily session drawn from **approved** flashcards + previously-missed quiz questions across the learner's in-progress/completed tracks; simple SM-2-style scheduling persisted per user (`data/practice/<user>.json` or inside completion store); 5-item default session (<10-min reality); completing practice sustains the streak (D3). Cards/questions always carry their source affordance. Designed empty state explaining when practice unlocks.
**Success criteria:**
1. Full practice session works end-to-end on mobile in <3 minutes.
2. Pool contains only approved, undrifted content; missed-question reuse pulls only approved questions.
3. Scheduling state persists; tomorrow's session differs from today's (simulate clock for verification).
4. Streak credit fires on completion.
**Demo check:** Dallas opens Practice on the demo account and a ready 5-card session is waiting.
**Cut criterion:** if Wave 3 is amber by Jul 2, D4 ships as a seeded-session façade (real UI, hand-picked items) and the scheduler goes post-ANC.

---

#### A3 — Track assignment, deadlines & milestones
**Tier:** CORE · **Wave:** 3 · **Size:** M · **Depends:** A1
**Demo moment:** Act 1's closing beat (assign to Houston ISD, due July 31) and the spine of Act 3's overdue math.
**Agent brief:** Track schema gains ordered `course_ids`, optional `milestones` (named course groups), optional course prerequisites (B locked until A complete — player lock state in D1), and persisted `assignments: [{audience: role|district, due_date}]`. Builder UI: course ordering, milestone grouping, assign-with-due-date picker (low ceremony: audience dropdown + date + one button). Learn view shows the real "Due Jul 31" chip; My Team overdue computation reads the real due date (replaces hardcoded `"Jun 30"`).
**Success criteria:**
1. Assignment persists and drives both the learner due chip and My Team's overdue counts from the same record.
2. Prerequisite lock visibly works in the player (locked lesson shows why).
3. Assign flow is ≤3 interactions (Jaime lens).
4. Legacy tracks without assignments render unchanged.
**Demo check:** Act 1 assigns with a due date; Act 3 shows that same date driving the overdue list.

---

#### E1 — Real progress in My Team (+ lite nudge persistence)
**Tier:** CORE · **Wave:** 3 · **Size:** M · **Depends:** A3
**Demo moment:** Act 3's money shot — John finishes in Act 2 and Dana's dashboard *has already changed*. "This is live" is worth more than ten slides.
**Agent brief:** Join roster rows with real `completion_store` data for real user ids (today `GET /api/roster` is 100% hash-seeded and real completions never surface). Seeded demo learners remain to fill out the table (a roster of 3 looks sad; a roster of 28 with one *live* row looks real). Overdue computed from A3 due dates. Compliance report includes the live rows. Fold in nudge persistence (was E2): nudges write to `data/nudges/`, survive reload, "Nudge all overdue" writes a batch record, toast reads "Reminder sent" (delivery itself is simulated — we don't claim SMS/email on stage, see §7).
**Success criteria:**
1. John completes a lesson on the phone → Dana's row updates on next refresh (≤5s) without server restart.
2. Overdue list derives from the real due date; counts reconcile with the roster table.
3. Nudge state survives reload; nudged rows show "reminded" state.
4. Tenancy holds: Dana sees Houston ISD only; 403 on cross-district.
5. In `DEMO_MODE=conference`, the compliance PDF is watermark-free and includes John's live completion.
**Demo check:** Act 2 → Act 3 handoff rehearsed: completion appears on Dana's screen in under 10 seconds of stage time.

---

#### G1 — Demo content library: the showcase tracks
**Tier:** CORE · **Wave:** 3 · **Size:** M · **Depends:** A1, B1, B2, C1 (consumes all of them)
**Demo moment:** Every act. Demos are only as good as their content — this is the set dressing AND the proof.
**Agent brief:** Curate and build (through the real pipeline — generated, gated, approved, no hand-edits outside the sanctioned path) **three showcase tracks**:
1. **"New Cashier Onboarding"** (the Act 1/2 star): 2 courses, mixed lessons — generated guide(s), 1–2 embeddable ICN/USDA food-safety videos, mixed-type quizzes, a flashcard deck, a final assessment with cert gate.
2. **"Manager Essentials"** (Dana's own track — shows breadth): 1 course, includes a link-out ICN asset to demonstrate the license-aware behavior.
3. **"3-Minute Food Safety"** (the booth micro-course): 1 lesson + 1 short ICN clip + 3-question quiz + instant certificate. Tuned relentlessly for the 3-minute loop.
Plus: course-card imagery, accurate duration estimates, role tags (Cashier/Site Manager/CN Director), and a seeded library state where the Learn home looks *abundant* (no thin shelves).
**Success criteria:**
1. All three tracks pass the grounding gate and human approval — zero content bypasses the pipeline.
2. Every ICN asset used has verified license posture and a working embed/link.
3. Booth track completes in ≤3:30 by a first-time user (tested on 3 people).
4. Learn home for each persona shows a full, designed shelf — no empty states reachable in demo mode.
5. Content reviewed aloud once for jargon and tone (customer-facing voice).
**Demo check:** full Act 1→2→3 dress rehearsal runs exclusively on this content.

---

#### G2 — Stat overlays & the "reveal" moments
**Tier:** ENHANCER · **Wave:** 3 · **Size:** S · **Depends:** G1
**Demo moment:** Act 1's gate moment and the investment close. Numbers make the pitch repeatable by people who aren't Dallas.
**Agent brief:** Presenter-friendly surfaces (demo-mode only, operator-triggered): (1) the **gate reveal** — full-screen-able citation integrity panel ("158 claims · 158 verified · 0 failures" with the tier breakdown), built from the existing `citation_integrity` metadata; (2) the **economics card** — generation time + token cost per guide (from existing `gen_seconds` + `usage` metadata), framed against the documentation-tool spend; (3) a **pipeline counter** for the closing slide ("N guides · N quizzes · N flashcards · all human-approved"). No invented numbers — every stat reads from real metadata.
**Success criteria:**
1. Every displayed number traces to stored metadata (spot-checkable live if a customer asks).
2. Gate reveal is legible from the back of a room (type size, contrast).
3. Operator can summon/dismiss each overlay in one action mid-demo.
**Demo check:** Act 1's "158/158" moment lands on one keypress.

---

#### D7 — Certificate polish + exam linkage
**Tier:** ENHANCER · **Wave:** 3 · **Size:** S · **Depends:** B3
**Demo moment:** Act 2's finale artifact and the booth keepsake — the thing attendees show their colleagues.
**Agent brief:** Certificate upgrade: clean PDF render (reuse the guide-PDF path), design pass (this is the most-photographed artifact of the booth — make it gorgeous), "Passed assessment — N%" line when the B3 gate is on, badge strip (D3), verification code with a lookup endpoint returning issued/not-found (name + track + date only).
**Success criteria:**
1. PDF downloads on a phone and looks correct in a phone PDF viewer.
2. Verification lookup round-trips; returns no PII beyond name/track/date.
3. Design approved by Rahul before freeze (it's the keepsake).
**Demo check:** booth visitor downloads a certificate with their name and it looks frame-worthy.

---

#### B5 — Scenario walkthrough exercise (interactive "what do you do next?")
**Tier:** ENHANCER · **Wave:** 3–4 · **Size:** L · **Depends:** A1, B1
**Demo moment:** The "whoa" beat of Act 2 if it lands — the closest thing to DataCamp's interactive exercises and a genuine differentiator vs every LMS at ANC.
**Agent brief:** Interactive guided scenario rendered from a guide's AC-cited workflow: scenario framing ("A parent asks for a refund at the register…"), learner steps through "what do you do next?" choices where **every step and every choice is a real cited step** — wrong choices are real steps out of order or steps from a *labeled* different workflow in the same guide, never invented. Built as a renderer over gated step data (the B1 step-ordering lane supplies the substrate), not a free-form author. Wrong choice → gentle correction with the source line. Completion reports to progress + XP.
**Success criteria:**
1. Every node carries a source span; an uncitable step makes the scenario ineligible (gate, not guideline).
2. One polished scenario exists in the Cashier showcase track and plays well on a phone.
3. Wrong-answer feedback quotes the verbatim source step.
4. Completion advances course progress like any lesson.
**Demo check:** rehearsal audience audibly reacts. (Seriously — if it doesn't demo hot, it ships silent and we don't stage-feature it.)
**Cut criterion:** if not demo-polished by **Jul 7**, it's cut from the script (the feature can still exist un-featured) — no half-impressive interactives on stage.

---

#### E3-lite — Educator insight panel (seeded)
**Tier:** ENHANCER · **Wave:** 3 · **Size:** S · **Depends:** D1
**Demo moment:** A 20-second Act 3 aside for district admins: "and you can see exactly where people get stuck."
**Agent brief:** A read-only trainer panel: per-course funnel (started → per-lesson → completed) and per-question % correct, rendered beautifully from a **seeded** dataset (labeled internally as seeded; real-event wiring is post-ANC). Use the real xAPI stub log + completion records where they exist; backfill with seeded aggregates for visual fullness.
**Success criteria:**
1. Panel renders a legible funnel + question-difficulty list for the showcase track.
2. No per-learner drill-down (aggregate only).
3. Internally documented as seeded; on-stage narration says "see where learners drop off" (true of the panel's design) — not "this is your district's live data."
**Demo check:** one glance communicates "the content improves itself."

---

### WAVE 4 — Demo ops (Jul 6–9, then FREEZE)

---

#### G5 — Booth loop: QR → attendee phone → certificate
**Tier:** CORE · **Wave:** 4 (build starts Wave 3) · **Size:** M · **Depends:** G1 (booth track), D1, D6, G4
**Demo moment:** The lead machine. This converts hallway curiosity into named follow-ups.
**Agent brief:** Self-serve flow: QR → mobile web route → first-name entry + role picker (no account, no password) → "3-Minute Food Safety" micro-course → personalized certificate (their name) download + optional email field ("send me my certificate + product updates") writing to a leads log (`data/leads/anc.jsonl`). Session-isolated per visitor (ephemeral learner ids); operator reset (G4) clears between visitors; works over hotspot; offline-degrades per C1's fallback. First-name-only + optional email keeps PII handling trivial — no other personal data collected.
**Success criteria:**
1. Stranger test ×5: QR-to-certificate, median ≤3:30, zero staff assistance.
2. Leads log captures name+email only when the visitor opts in; nothing else stored.
3. Two visitors 60s apart: zero state bleed between sessions.
4. Full loop tested over a phone hotspot, not venue Wi-Fi assumptions.
5. Certificate (D7 design) downloads to the visitor's phone.
**Demo check:** 10 consecutive clean loops on rehearsal day.

---

#### G3 — Run-of-show, rehearsal & fallback kit
**Tier:** CORE · **Wave:** 4 · **Size:** M · **Depends:** everything CORE
**Demo moment:** Insurance on all of it. Demos fail on logistics, not features.
**Agent brief:** Produce: (1) the **ANC run-of-show script** (3 acts, per-beat clicks, timings, talk-track bullets in Dallas's framing — "sell the foundation," the –100k line, the trust line; modeled on `docs/jun11/DEMO-RUNOFSHOW.md`); (2) the **generation-theater plan** — live generation takes 2–4 min, so: kick off a real generation at talk open and return to it ("while we talked, it built"), with a pre-recorded SSE trace replay as the backup beat, honestly narrated as a replay; (3) the **fallback video** — a clean screen-recording of all three acts, in case of total A/V or network failure; (4) **pack list + venue checklist** (laptop + backup, phones charged, hotspot, QR prints, local-server boot script, reset hotkey card); (5) two timed dress rehearsals with notes filed as fix-tickets (freeze allows rehearsal fixes only).
**Success criteria:**
1. Full run-through ×2 inside the time box (Act 1 ≤8min, Act 2 ≤5, Act 3 ≤3) with someone *other than the builder* driving once.
2. Fallback video exists, is current to frozen build, and plays offline.
3. Generation-theater path rehearsed both ways (live-return and replay).
4. Every rehearsal issue either fixed or scripted around — zero "we'll wing it" notes at freeze.
**Demo check:** Dallas (or proxy) runs the entire demo from the script alone, cold.

---

### DEFERRED to post-ANC (the roadmap slide, not the screen)

These remain fully specced in `DATACAMP-PARITY-BACKLOG.md` and become the *investment narrative* — "here's what your funding builds next":
- **A4** SCORM suspend-data/per-SCO hardening + real LRS wiring (mention SCORM export exists — it does, truthfully).
- **B4** Question bank manager.
- **D5** Bookmarks, notes, content search upgrade.
- **E2-full** Real nudge delivery (email/SMS) — lite persistence shipped in E1.
- **E3-full** Live-event educator analytics.
- **Platform layer:** SSO/JWT (`auth.py` stub), live roster sync writeback, multi-node persistence, async generation jobs, Chroma retrieval (ADR-001 Phases 1–2). This list, presented as the funded roadmap, is how the demo converts into investment — it shows leadership exactly what the money buys, anchored by a working product they just watched.

---

## 5. Risk register (what kills demos, and the mitigation already in the plan)

| Risk | Mitigation |
|---|---|
| Live generation latency (2–4 min) on stage | G3 generation-theater: start-at-open + honest replay backup |
| Conference Wi-Fi / dead network | C1 offline fallback chrome; G4 pre-warm; G5 hotspot-tested; G3 local-server + fallback video |
| Giant single-file SPA jank on phones | D6 lazy-load trainer code off the customer path; measured budgets |
| Booth state bleed between visitors | G4 pristine reset, tested ×5; G5 ephemeral sessions |
| Scenario exercise (B5) lands half-baked | Hard cut criterion Jul 7 — un-featured, not half-featured |
| Agent throughput vs 31 days | CORE-first ordering; ENHANCER auto-drops at wave midpoints; freeze Jul 9 is immovable |
| A trust slip on stage (the one unforgivable) | F1 sweep per wave; §7 claims discipline in the script itself |

## 6. Standing trust guardrails (unchanged — they're the product)

Inherited by every brief; Layer-1 failures, not polish: no persona leakage (incl. previews, player, booth); no over-claiming the cited guarantee onto ICN/imported content; provenance visible on everything; no new uncited-claim channels (sanctioned free text: DEC-3 descriptions only in this plan); no silent/auto approval for any new content type; ICN embedded-with-attribution or linked-out per license, never reproduced; no dead first-runs; quiz/assessment answers stay verbatim spans; 375px is the floor.

## 7. Claims discipline at ANC (what Dallas says vs doesn't)

The demo can be theatrical; the *claims* stay true — one caught overstatement costs more than ten missing features (the trust quote applies to us, too):
- **Say:** "Every fact is verified verbatim against the source system before a human approves it." (True, enforced.)
- **Say:** "Your staff's progress shows up for your director in real time." (True — E1 makes it real.)
- **Say:** "Exports standard SCORM packages." (True.) **Don't say:** "drops into your existing LMS seamlessly" (suspend/resume is post-ANC).
- **Don't claim:** live SSO with SchoolCafé logins, automated email/SMS reminders, or live roster sync — those are roadmap-slide items ("integrates with your SchoolCafé accounts — that's what this next phase of investment builds").
- **ICN content:** "Official USDA/ICN training, embedded with full credit, always linked to the source." Never "our content."
- The seeded roster is demo scenery; if asked directly, the answer is honest: "demo district — your real data arrives via the integration phase."

---

## 8. Approval ask

A nod on this doc green-lights **Wave 1 dispatch immediately** (A1 → A2, B1, C1, F1, G4 — five parallel agents after A1's schema merges). Defaults in §3 stand unless vetoed by Jun 13. Freeze Jul 9. Rehearsals Jul 10–11. ANC Jul 13.
