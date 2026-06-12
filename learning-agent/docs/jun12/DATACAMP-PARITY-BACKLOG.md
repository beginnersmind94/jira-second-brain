# DataCamp-Parity Backlog — Creation + Consumption Audit

**Date:** 2026-06-12 · **Status: AWAITING APPROVAL — no work dispatched, no code changed.**
**Audited build:** `jira-brain/learning-agent/` (demo_app.py + static/index.html as of commit b31d290).
**Gold standard:** the educator + learner experience on DataCamp (course builder with typed lessons/exercises, tracks, skill assessments, practice/spaced repetition, XP/streaks, unified mobile course player, certificates).

How to use this doc: each to-do below is a self-contained agent brief. On approval, dispatch one agent per to-do (or per wave — see §5). Briefs assume no memory of this session; evidence pointers are included so the agent can verify current state before building.

---

## 1. Current-state snapshot (what the audit found)

### Creation side
| Capability | Status | Evidence |
|---|---|---|
| Transcript → generate → grounding gate → human approve → revise | **Real** | `/generate`, `demo.validate_citations`, `/resources/{rid}/approve`, `revise.py` |
| Quiz generation from published guides | **Real, MCQ-only** | `/api/resources/{rid}/quiz`, `qbank_gate.py` (3-gate: lane + verbatim + semantic judge), `quiz_store.py` (provenance + drift hash + approval gate) |
| Other question types (T/F, fill-blank, ordering, scenario) | **Absent** | — |
| Flashcards | **ICN only, on-demand, not persisted** | `/api/icn/flashcards`; guide flashcards parked V1.5 |
| Skill assessments / exams / practice | **Absent** | `/api/certificates` exists but no exam builder |
| Video lesson type | **Façade** | `cbAddVideo()` stores `{type:'video', title, dur}` — no URL, no player, no embed anywhere in the app |
| ICN/USDA catalog | **Real (license-aware)** | `/api/icn` with `license_posture` (`link_only` / `embed_only` / `download_allowed`), content-type tags incl. `youtube`; quiz + flashcard generation from ICN chunks |
| Course builder | **Façade** | `openCourseBuilder()` → `_demoState.userCourses` (client-side only; lost on reload; no server entity) |
| Track builder | **Real backend** | `/api/tracks` CRUD + publish + `role_tags` + `module_ids` (flat — tracks hold modules directly, no course layer), `data/tracks/*.json` |
| SCORM export | **Real (single-SCO, no suspend/resume)** | `/api/tracks/{tid}/scorm`; xAPI stub → `logs/xapi-stub.jsonl` |
| No free-claim authoring | **Enforced** | No rich-text editor; `revise.py` rejects ops touching `<!-- Source -->`; structured inputs only |

### Consumption side
| Capability | Status | Evidence |
|---|---|---|
| Track → module navigation, resume hero, role filtering | **Real** | `loadLearn()`, `openRealTrack()`, `/api/tracks` role_tags filter |
| Per-user progress + certificates | **Real (disk)** | `completion_store.py` → `data/completion/<user>/<track>.json`, `/api/certificates` |
| Quiz taking + scoring | **Real** | `openTaker()`, `/api/quizzes/{qid}/score` (per-question source quote in feedback) |
| Lesson rendering | **Partial** | Module list + PDF preview link — no unified in-page lesson player |
| Gamification (XP, streaks, badges, leaderboards) | **Absent** | — |
| Practice / spaced repetition | **Absent** | — |
| Bookmarks / notes / completed-history | **Absent** | Search is client-side title filter only |
| Mobile | **Built, needs polish** | Breakpoints down to 375px; DEMO-RUNOFSHOW: "needs polish, not net-new"; <3s NFR unmeasured |
| My Team (Dana) | **Façade data, real export** | Seeded roster (`_roster_for`), in-memory nudges, compliance PDF watermarked "DEMO DATA" |
| Auth / tenancy | **Demo personas, real isolation** | `auth.py` (3 seeded users), `tenancy.py` 403 enforcement; SSO stubbed (ADR-001) |

---

## 2. DataCamp parity map (delta → to-do)

| DataCamp feature | Our state | To-do |
|---|---|---|
| Course = chapters of typed lessons (video / slides / exercises) | Course is client-side façade; tracks hold flat module lists | **A1, A2** |
| Career/skill tracks with milestones, prerequisites | Tracks real but flat; no milestones/prereqs/deadlines persisted | **A3** |
| Multiple exercise types (MCQ, fill-blank, ordering, drag-drop, coding) | MCQ only | **B1, B5** |
| Daily practice / spaced repetition | Absent | **B2, D4** |
| Skill assessments (timed, scored, placement) | Absent | **B3** |
| Video lessons with player | Façade (no URL, no player) | **C1, C2** |
| Unified course player (rail, prev/next, inline content, resume-at-lesson) | Module list + PDF links | **D1** |
| Onboarding → recommended track | Hero exists; no role-confirm first-run | **D2** |
| XP, streaks, badges | Absent | **D3** |
| Bookmarks, notes, history | Absent | **D5** |
| Mobile-first player | Breakpoints exist, unpolished, perf unmeasured | **D6** |
| Statement of accomplishment / verified certificate | Real HTML cert; no PDF/verification id/exam gate | **D7** |
| Educator analytics (drop-off, item stats) | Absent | **E3** |
| Instructor dashboard of learner progress | Façade roster | **E1, E2** |

---

## 3. Decisions needed before dispatch (Rahul)

- **DEC-1 — Content hierarchy.** Adopt **Track → Course → Lesson** (DataCamp model; recommended) vs keeping flat Track → Module. A1/A2/A3/D1 assume the three-level model with a migration path (existing `module_ids` tracks become single-course tracks).
- **DEC-2 — Video embedding posture.** ICN assets already carry `license_posture`. Proposal: YouTube **iframe embed** for `embed_only`/`download_allowed` assets counts as credited streaming (content stays on YouTube's servers, attribution card required); `link_only` stays a link-out card. If you want zero embedding risk, C1 ships in "simulate" mode (player chrome + seeded ICN video IDs behind the existing `EXTERNAL_LEARNING` flag) with the iframe one flag away.
- **DEC-3 — Free-text metadata policy.** Course/track titles + descriptions are human-authored sequencing metadata, not product claims. Proposal: allow short free-text descriptions but (a) badge them `human-authored · not gate-grounded`, (b) lint them for product-claim patterns (numbers, field names, "the system will…") and warn. The no-free-claim moat stays intact for lesson *content*.
- **DEC-4 — Gamification depth.** Proposal: XP + streaks + completion badges only (lightweight, honest). No leaderboards in this pass — cross-learner comparison has morale/tenancy implications and Jaime's team optimizes for low ceremony.

---

## 4. Backlog — agent briefs

Severity of trust constraints follows the JTBD skill: any provenance/grounding regression is a blocker, not a polish nit. Every brief inherits §6.

### Workstream A — Course & track architecture (the foundation)

---

**A1 — Promote Course to a real server entity** · P0 · Size L · Depends: DEC-1
- **Persona/lens:** Trainer-creator (Jaime's team assigns what this produces); Matt lens (real, not façade).
- **Current state:** `cbSave()` (index.html ~4770) appends to `_demoState.userCourses` — client-side, lost on reload. Tracks are real (`data/tracks/<id>.json`) but hold flat `module_ids`.
- **Scope:** Server-side course entity: `data/courses/<id>.json` with `{id, title, description, product, role_tags, lessons:[{type: guide|quiz|video|external_icn|exercise, ref, title, duration_est}], status: draft|published, created_at}`. CRUD + publish endpoints mirroring `/api/tracks` (tenancy-gated via `assert_district_access` patterns). Track schema gains `course_ids` (ordered); migration shim: a track with legacy `module_ids` renders as one implicit course so nothing existing breaks.
- **Acceptance:** course survives restart; only **approved** library resources / published quizzes / ICN catalog items selectable as lesson refs (enforced server-side, not just UI); publish requires ≥1 lesson; existing seeded tracks still render.
- **Trust:** lesson refs may only point at approved/gate-passed content ids — server rejects unknown or draft refs. Description field follows DEC-3 policy.

---

**A2 — Course builder UI on the real API** · P0 · Size M · Depends: A1
- **Persona/lens:** Trainer-creator; Dallas lens (this is the demo-able "build a course in minutes" moment).
- **Current state:** `openCourseBuilder()` UI exists (add guide/quiz/video, reorder via `cbMove`), wired to demo state.
- **Scope:** Rewire builder to A1 endpoints: create/edit/reorder/delete/publish; per-lesson type picker; "Preview as learner" (renders the D1 player read-only); draft/published status chips; familiar labels preserved (per nav-preservation feedback — don't rename "Courses").
- **Acceptance:** full create→edit→publish→appears-in-track loop with no page-state loss; preview shows exactly what a learner sees including provenance badges; reload-safe.
- **Trust:** preview must carry the same origin badges as the live player (no internal chrome leaking into preview screenshots).

---

**A3 — Track builder: courses, milestones, deadlines, assignment** · P1 · Size M · Depends: A1
- **Persona/lens:** Jaime's team (assign fast, see deadlines); Dana (receives the deadline).
- **Current state:** `/api/tracks` real; `role_tags` filtering real; no milestones, prerequisites, or due dates; My Team deadline is hardcoded `"Jun 30"`.
- **Scope:** Track schema gains `course_ids` (ordered), optional `milestones` (named groups of courses), optional `prerequisite` edges (course B locked until A complete), `assignments: [{district_id|role, due_date}]` persisted server-side. Builder UI: drag/arrow ordering of courses, milestone grouping, assignment + due-date picker. My Team and Learn views read the real due date instead of the hardcoded one.
- **Acceptance:** assignment with due date persists and drives both the learner "due by" chip and the My Team overdue computation; prerequisites actually lock the player navigation; legacy tracks unaffected.
- **Trust:** assignment is a trainer action — confirm it never auto-fires from generation/approval.

---

**A4 — SCORM/xAPI hardening** · P1 · Size M · Depends: A1 (nice-to-have), none (hard)
- **Persona/lens:** Matt lens (BRD: SCORM/xAPI is platform credibility).
- **Current state:** `/api/tracks/{tid}/scorm` builds a real SCORM 1.2 zip but single-SCO, no `cmi.suspend_data` (mid-track close restarts navigation); xAPI stub logs to `logs/xapi-stub.jsonl`.
- **Scope:** Persist/restore `cmi.suspend_data` (lesson position + done-set); optional per-course SCO mode in the manifest; xAPI statements extended to new lesson types (video watched, exercise attempted, assessment passed); document LRS env wiring.
- **Acceptance:** export → import into a SCORM test harness (e.g. SCORM Cloud trial or a local RTE shim) → close mid-track → relaunch resumes at the right lesson; statement vocabulary documented.
- **Trust:** exported HTML must remain the citation-stripped, approved-only variant (current behavior — keep the test).

### Workstream B — Assessment depth (creation)

---

**B1 — Grounded question types beyond MCQ** · P0 · Size L
- **Persona/lens:** Trainer-creator + Learner; Dallas (visible capability jump) with Matt-grade gating.
- **Current state:** MCQ-only (4 options, single correct) through `qbank_gate.py` (lane-match + verbatim + semantic judge) and `quiz_store.py` (provenance, drift hash, approval re-gate).
- **Scope:** Add three types, each with a *deterministic* grounding strategy:
  - **True/False** — statement must be a verbatim span (true) or a minimally-negated span where the negation is mechanical and the source span is shown (false).
  - **Fill-in-the-blank** — blank is a verbatim span from the published guide; the surrounding stem is the literal sentence. Grounding check: stem+answer reassembles to an exact source substring.
  - **Step-ordering** — items are the actual workflow steps from the guide (sourced from AC-cited sections), shuffled; no invented steps as distractors.
  Extend `qbank_gate.py` with a lane per type; extend quiz builder UI + `openTaker()` rendering + `/score` for each type.
- **Acceptance:** each type round-trips generate → gate → approve → take → score with per-question source quote in feedback; CLAUDE.md quiz rules hold (3–10 questions, distinct concepts, section citation per question); regression cases added per type to the gate's test set.
- **Trust:** distractors/false-statements may not introduce uncited product claims — false options must be transformations of real spans, flagged as such in the stored question (`distractor_basis`). This is the blocker line for this item.

---

**B2 — Guide flashcards (persistent + gated)** · P1 · Size M
- **Persona/lens:** Learner (feeds D4 practice); Trainer approves.
- **Current state:** `/api/icn/flashcards` generates grounded cards from ICN assets on-demand, nothing persisted; guide flashcards explicitly parked (FEATURES.md, CLAUDE.md V1.5).
- **Scope:** Port the ICN flashcard generator to published guides; persist to `data/flashcards/<id>.json` mirroring `quiz_store.py` (per-card `source_quote`, provenance flags, `source_content_hash` drift detection, approval endpoint that re-runs the verbatim gate). Builder UI alongside the quiz builder; attachable to courses as a lesson ref (A1).
- **Acceptance:** CLAUDE.md flashcard rules enforced: every card traces to a specific section of the *published* content; procedural cards ("what do you do when X") preferred ordering; drifted source reverts deck to draft.
- **Trust:** cards generate from published content only — never transcripts or drafts (this is already the documented rule; make it the code path).

---

**B3 — Skill assessment / track exam builder** · P0 · Size L · Depends: B1 (richer pool), A1
- **Persona/lens:** Dana (proof of competence), Matt (compliance credibility), Learner (DataCamp signature feature).
- **Current state:** Absent. Certificates issue on module completion only — no knowledge check gates the cert.
- **Scope:** Assessment entity assembled from **approved** questions across a track's guides (question bank pull, not fresh generation): `{question_ids, time_limit, pass_pct, attempts_allowed}`. Builder UI: pick track → see eligible approved questions grouped by guide → assemble → publish. Taker: timed, randomized order, scored server-side, attempt history persisted in `completion_store`. Option on track: "certificate requires passing the assessment." Optional stretch: placement mode ("test out" — passing marks the track's modules done).
- **Acceptance:** failing blocks cert when the gate option is on; attempts logged with timestamps; per-question feedback withholds source quotes until pass/fail to protect retakes; works at 375px.
- **Trust:** only approved, undrifted questions are eligible; an assessment containing a question whose source guide was re-opened to draft reverts to draft itself.

---

**B4 — Question bank manager** · P2 · Size S · Depends: B1
- **Current state:** Quizzes are per-guide JSON files; no cross-guide browse/reuse view.
- **Scope:** Trainer surface listing all approved questions with filters (guide, module, type, drift status); retire/restore; per-question provenance popover (source quote + tier + drift state); reuse into assessments (B3).
- **Acceptance:** retiring a question removes it from future assessment assembly without breaking published quizzes that already contain it.
- **Trust:** provenance popover is read-only; no edit path that bypasses the quiz approval gate.

---

**B5 — Scenario walkthrough exercise type (DataCamp "exercise" analog)** · P2 · Size L · Depends: A1, B1
- **Persona/lens:** Learner (the interactive-practice feel that makes DataCamp sticky); Dallas (wow factor).
- **Current state:** Course builder has an `exercise` placeholder lesson type with no implementation.
- **Scope:** Interactive guided scenario rendered from a guide's AC-cited workflow: learner is shown the scenario ("a parent asks for a refund…") and steps through "what do you do next?" choices where every step and every choice is a real step from the cited workflow (wrong choices = real steps out of order or steps from a *labeled* different workflow in the same guide — never invented). Simulation-only: no live product, screenshot placeholders allowed if sourced from existing guide assets.
- **Acceptance:** every node in the scenario tree carries a source span; completion reports to progress + xAPI; mobile-usable.
- **Trust:** this is the highest-risk item for invented specifics — the agent must build it as a *renderer over gated step data*, not a free-form scenario author. If a step can't be cited, the scenario is ineligible.

### Workstream C — Video & ICN (the YouTube ask)

---

**C1 — Real video lesson type with license-aware ICN embedding** · P0 · Size M · Depends: DEC-2
- **Persona/lens:** Trainer-creator + Learner; trust bar front-and-center.
- **Current state:** `cbAddVideo()` stores title+duration only; zero iframe/player code in the app. ICN catalog (`/api/icn`) already has `youtube`-typed assets and `license_posture` per asset (`link_only` excluded from embedding today).
- **Scope:** Video lesson ref points at an ICN asset id (not a raw URL — keeps provenance). Player card: YouTube iframe embed for embed-permitted postures, with a **persistent attribution band** (ICN/USDA source, asset title, license badge, outbound link); `link_only` assets render as a credited link-out card with thumbnail, never an embed. Simulation mode (default until DEC-2 confirms): identical chrome with seeded ICN video IDs behind the existing `EXTERNAL_LEARNING` env switch, and a visible `SIMULATED` chip so a demo never over-claims.
- **Acceptance:** embed/link-out branch driven entirely by `license_posture` from the catalog (no per-lesson override); attribution band cannot be hidden by CSS at any breakpoint; works at 375px.
- **Trust (blocker lines):** never reproduce ICN content inline (no downloading/transcoding/transcript-scraping); no "every claim cited" badge on video lessons — they are `outside-vendor` provenance, badge accordingly; raw free-text URL entry is **not** allowed (only catalog refs), so no path to embed arbitrary uncredited video.

---

**C2 — Video completion tracking** · P1 · Size S · Depends: C1
- **Current state:** No watch tracking (no player exists).
- **Scope:** YouTube IFrame API `onStateChange` → "watched" at ≥90% (configurable) with a manual "Mark watched" fallback (works in simulation mode and where the API is blocked); posts to the existing `/api/tracks/{tid}/progress` path; emits xAPI `experienced`/`completed`.
- **Acceptance:** watching to threshold advances course progress identically to finishing a guide; fallback button present and keyboard-accessible.
- **Trust:** none beyond C1's; no analytics payload beyond completion (don't ship watch-time surveillance for cafeteria staff without a decision).

---

**C3 — ICN lesson metadata polish** · P2 · Size S · Depends: C1
- **Scope:** Auto-populate duration/thumbnail from the ICN catalog entry; consistent license badges across Catalog view, course builder picker, and player; dead-link check job for `link_only` assets.
- **Acceptance:** no hand-typed durations for ICN lessons; broken outbound links surface in a trainer-visible report, not a learner 404.

### Workstream D — Learner course player & engagement (consumption core)

---

**D1 — Unified course player** · P0 · Size L · Depends: A1 (DEC-1)
- **Persona/lens:** John the cashier — *this is the single biggest DataCamp delta.* BRD hard constraints apply (375px, <3s, <10-min modules, FR-CP-08 cert).
- **Current state:** `openRealTrack()` renders a module list with PDF preview links; quizzes open in a modal; no prev/next, no in-page lesson rendering, no lesson-level resume.
- **Scope:** One player shell: left rail (collapsible to bottom bar at mobile) listing courses→lessons with done-state; main pane renders the lesson inline by type — guide HTML (citation-stripped approved render, not a PDF link), quiz (existing taker inline), video (C1 card), flashcards (B2 deck), exercise (B5). Prev/next, lesson-level progress + resume (extend `completion_store` records from `modules_done` to `lessons_done`), "continue" deep-links to the exact lesson. Keep PDF download as a secondary action — don't remove the familiar entry point.
- **Acceptance:** cashier persona can complete a full mixed-type course start-to-finish on a 375px viewport without horizontal scroll; resume returns to exact lesson after server restart; per-lesson done-state survives restart; player initial render <3s on the demo box (measured, number recorded in the PR notes).
- **Trust:** every lesson pane shows its origin badge (AI-grounded / human-authored / outside-vendor) and, for grounded guides, the "show source" affordance; the customer-view banner logic must hold inside the player (no trainer chrome reachable).

---

**D2 — First-run onboarding & empty states** · P1 · Size S
- **Persona/lens:** John + Jaime (low ceremony, "told what to do").
- **Current state:** "Up next for you" / "Continue" heroes exist; empty state is a flat "No tracks assigned yet" with a Catalog link; no role confirmation moment.
- **Scope:** First-visit flow: confirm role (pre-filled from persona) → show the assigned/recommended track with a one-line "why you're seeing this" → single primary CTA ("Start — 8 min"). Empty states for: no tracks for role (suggest global tracks), track with no published courses, finished-everything state (route to D4 practice when built).
- **Acceptance:** zero-dead-air on first run for each of the three demo personas; no LMS jargon in any learner-facing string ("track/course/lesson" stay, "SCO/module/tenant" never appear).

---

**D3 — Gamification lite: XP, streaks, badges** · P1 · Size M · Depends: D1, DEC-4
- **Persona/lens:** John (the DataCamp habit loop); Jaime adoption lens.
- **Current state:** Absent; progress bars and status chips only.
- **Scope:** Server-side in `completion_store` (not localStorage): XP per lesson/quiz/assessment completion (flat, documented values), daily streak (any completed lesson keeps it; freeze rules simple), completion badges (per-track + milestone). Learner home shows streak + XP + next badge; subtle, not casino — Jaime's users are reluctant adults.
- **Acceptance:** values persist server-side per user; no leaderboard (DEC-4); badge icons appear on the cert and the My Progress strip; degrades gracefully if a user ignores it entirely.
- **Trust:** XP/badges must never be derivable as a manager surveillance feed in this pass — visible to the learner and aggregate-only to Dana (counts, not per-learner XP rankings).

---

**D4 — Practice mode (spaced repetition)** · P1 · Size M · Depends: B2 (and B1 helps)
- **Persona/lens:** John; the DataCamp "daily practice" loop.
- **Current state:** Absent.
- **Scope:** "Practice" tab in the learner view: daily deck drawn from **approved** flashcards + missed quiz questions for the learner's completed/in-progress tracks; simple SM-2-style scheduling persisted per user; 5-card default session (respects the <10-min reality); streak credit (D3).
- **Acceptance:** practice session works end-to-end on mobile; cards always show their source affordance; missed-question reuse pulls only approved questions; empty state when nothing is eligible explains why.
- **Trust:** practice content is approved-content-derived only — never drafts, never transcripts.

---

**D5 — Bookmarks, notes, history, search upgrade** · P2 · Size M
- **Current state:** Absent; search is a client-side title filter; `/api/modules?q=` is JQL keyword.
- **Scope:** Per-user server-persisted bookmarks ("save for later" on any lesson/guide) and short private notes (plain text, learner-private); "Completed" history list for re-access; library search across guide *content* (server-side text index is fine; Chroma stays V1.5 per ADR-001 — don't gold-plate).
- **Acceptance:** bookmarks/notes survive restart and stay tenant-isolated; notes are explicitly excluded from any manager/trainer view.
- **Trust:** notes are learner-private free text — they must never render into any shared/exported surface (the one acceptable free-text box, because it's not published content).

---

**D6 — Mobile + performance pass (contractual)** · P0 · Size M · Depends: best run after D1 lands
- **Persona/lens:** John; BRD NFRs are contractual: usable to **375px**, player loads **<3s**, WCAG 2.1 AA.
- **Current state:** Breakpoints exist (1040→375); DEMO-RUNOFSHOW's own note: "needs polish, not net-new"; <3s never measured; touch targets claimed ≥44px but unaudited.
- **Scope:** Audit + fix the learner surfaces (Learn, player, quiz taker, practice, cert) at 375px: no horizontal scroll, tap targets ≥44px, focus order, contrast (AA), quiz modal vs small-viewport behavior. Instrument and record player load time (simple `performance.now()` marks logged once, plus a documented measurement); fix the top offenders (index.html is a single huge SPA — likely defer non-learner JS/CSS).
- **Acceptance:** screenshot evidence at 375px for each learner surface; measured load number in the report; WCAG quick-audit findings filed (fix blockers, list the rest); cite the NFR ids in the summary.
- **Trust:** customer-view banner must remain visible-but-unobtrusive at 375px (persona-leak guard).

---

**D7 — Certificate polish + exam linkage** · P2 · Size S · Depends: B3
- **Current state:** Real HTML cert with learner name/track/date, persisted JSON; no PDF, no verification id, no knowledge gate.
- **Scope:** PDF render (reuse the existing guide-PDF path), verification code on the cert resolvable at a public-ish lookup endpoint, "passed assessment with N%" line when B3's gate is on, badge strip (D3).
- **Acceptance:** FR-CP-08 satisfied with a downloadable PDF; verification lookup returns issued/not-found only (no PII beyond name + track + date).

### Workstream E — Manager & educator surfaces (Dana / Jaime)

---

**E1 — Real progress in My Team** · P1 · Size M · Depends: A3 (deadlines)
- **Persona/lens:** Dana; Matt lens (façade-presented-as-real is the credibility risk).
- **Current state:** `GET /api/roster` returns hash-seeded fake learners; real `completion_store` data is never joined in; compliance PDF watermarked "DEMO DATA".
- **Scope:** Join roster rows with real `completion_store` progress for real user ids; seeded demo rows remain but stay visually tagged demo; overdue computed from A3's real due dates; compliance report drops the watermark **only** for rows backed by real completion data.
- **Acceptance:** John's actual progress moves Dana's dashboard in real time; demo rows can't be mistaken for real ones (explicit tag); tenancy 403s still hold.
- **Trust:** honest under-claiming — the watermark rule above is the point of the item.

---

**E2 — Nudge persistence + outbox** · P2 · Size S
- **Current state:** `nudgeOne()` flips `_demoState.nudged` in memory; resets on reload; nothing sends.
- **Scope:** Persist nudges server-side (`data/nudges/`), render an "outbox" log (who nudged whom, when, for what track), simulate delivery (no real email/SMS without a separate decision); nudged-state survives reload; "nudge all overdue" writes one batch record.
- **Acceptance:** nudge state durable; outbox visible to the nudger; clearly labeled simulated delivery.

---

**E3 — Educator analytics (drop-off + item stats)** · P2 · Size M · Depends: D1, B-items for richer events
- **Persona/lens:** Trainer/PO improving content; the DataCamp instructor-dashboard analog.
- **Current state:** Absent; raw material exists in xAPI stub log + completion records + quiz attempt scores.
- **Scope:** Per-course funnel (started → each lesson → completed), per-question difficulty (% correct) and discard-candidates list, average time-to-complete; aggregate-only (no per-learner drill-down in this pass — see D3 trust note); reads from completion store + xAPI log, no new tracking.
- **Acceptance:** a trainer can answer "where do learners drop off in this course" and "which quiz question is broken" from one screen.

### Workstream F — Trust & QA cross-cutting (gates for everything above)

---

**F1 — Provenance system extension to all new surfaces** · P0 · Size S · Runs alongside waves, must land before any wave demos
- **Current state:** Origin badges + "show source" exist on guides/quizzes in current surfaces.
- **Scope:** Badge + source-affordance coverage matrix for every new surface (player lesson panes, video cards, flashcard decks, assessments, practice cards, scenario steps); implement the gaps; explicit *absence* of the "every claim cited" framing on outside-vendor and human-authored content.
- **Acceptance:** a screenshot sweep of every new surface shows correct provenance; an over-claiming check (grep-level + visual) is documented as a repeatable checklist.

---

**F2 — Trust-regression eval additions** · P1 · Size M · Depends: B1 (first consumer)
- **Current state:** `eval/regression.py` pins guide grounding (REG-01…16); quiz gate has its own tests; nothing covers new question types, video provenance, or persona-leak in the player.
- **Scope:** Add regression cases per new question type (verbatim/lane checks), a persona-leak check for the player (customer view cannot reach trainer routes/chrome), an ICN reproduction check (no inline ICN content in any export), and a SCORM-export grounding check (citation-stripped approved-only — pin current behavior).
- **Acceptance:** suite runs green pre/post each wave; failures name the violated guarantee.

---

## 5. Suggested dispatch waves

| Wave | Items | Theme | Unblocks |
|---|---|---|---|
| **0** | DEC-1…4 (you) | Decisions | everything |
| **1** | A1 → A2, B1, C1, F1 | Real course entity + question types + video + provenance | the whole DataCamp shape |
| **2** | D1, D6, B3 | The player + mobile/perf + assessments | the learner demo |
| **3** | A3, B2, C2, D2, D3, E1, F2 | Deadlines, flashcards, watch-tracking, onboarding, gamification, real My Team | the habit loop + Dana |
| **4** | A4, B4, B5, C3, D4, D5, D7, E2, E3 | Practice, scenarios, analytics, polish | DataCamp parity tail |

Parallelism notes: within Wave 1, A1 must finish before A2; B1/C1/F1 are independent of A1 and of each other. D1 should not start until A1's schema is merged. F1 reviews each wave's output before it's demoed.

## 6. Standing trust guardrails (apply to every brief)

From the JTBD skill's blocker list — any agent working these items treats the following as Layer-1 failures, not polish:
1. No persona leakage (trainer chrome in customer view, including previews and the new player).
2. No over-claiming — the verbatim-cited guarantee is never painted onto imported/ICN/human-authored content.
3. Provenance visible on everything new (origin badge + path to source).
4. No new channel for uncited product claims (the only sanctioned free text: learner-private notes (D5) and DEC-3-governed descriptions).
5. No silent/auto approval — every new content type (flashcards, assessments, courses) gets the same human gate as guides and quizzes.
6. ICN/USDA: embed-with-attribution per license posture or link-out; never reproduced.
7. No dead first-runs (D2 owns this, every surface respects it).
8. Quiz/assessment answers stay verbatim spans of published content.
9. Learner surfaces work at 375px — checked per item, audited in D6.

## 7. The vision-fork note (for your approval framing)

This backlog deliberately converges the two visions: Workstreams B/C deepen **Dallas's content engine** (more generatable, gated content types), while A/D/E build out the **delivery-platform layer Matt's BRD makes MVP** (real entities, real progress, real compliance signals) — replacing today's façades rather than adding new ones. Approving Waves 1–2 is implicitly a decision that the build stops being "content factory + façade LMS" and becomes a real (small) LMS. That's the right move for a DataCamp-grade experience, but it's worth saying out loud to Dallas before dispatch, since it spends effort on plumbing he previously deprioritized — the E1 watermark rule and F1 provenance sweep give Matt the honesty story in the same breath.
