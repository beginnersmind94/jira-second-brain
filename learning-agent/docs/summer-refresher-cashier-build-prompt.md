# Build Prompt — "Cashier Summer Refresher" course

> **What this is:** a hand-off prompt that decomposes building one fun, trust-safe summer
> refresher course for POS cashiers into clear to-dos for several **Sonnet 4.6** worker
> agents. An orchestrator (you) reads §0–§1, then runs the §2 to-dos. Total agent
> wall-clock budget: **≤ 1 hour.** The course itself stays short for the learner
> (≤ ~8 min per lesson, ≤ ~45 min total — cafeteria staff do not sit at desks).
>
> **Model pin:** every worker agent runs on `claude-sonnet-4-6`. Do not inherit Opus.
> **Run target:** the canonical build at `jira-brain/learning-agent/`, served by
> `python demo_app.py` (Windows Proactor loop), reachable on its local port.

---

## 0. The one rule that overrides everything (read before any other instruction)

This product's entire value is **trust**: "you make one mistake with AI and it loses
credibility very quickly." So:

1. **Fun lives in framing, not in facts.** The summer-camp theme, voice, lesson titles,
   and a light intro can be playful. **Every product/POS fact must trace to an approved
   source** (an approved guide, an approved quiz grounded in published content, or a Jira
   ticket span). If a specific POS label / menu path / number / error string is not in an
   approved source, **do not invent it** — write a `[TO VERIFY]` marker for the human.
2. **The agent never approves and never auto-publishes a new claim.** New atoms (a quiz,
   any generated guide) are created as **draft** and handed to a **Product Owner** to
   approve. Worker agents stop at that gate.
3. **Honest provenance.** Imported SchoolCafé guides are **human-authored, not
   gate-grounded** — never paint "every claim cited" on them. ICN/USDA content is
   **link-out + credited, never reproduced inline.** The course's own description is
   human-authored metadata and is **never** badged as cited.
4. **A course can only contain *approved* lessons.** The server (`course_store.validate_all_lessons`)
   rejects any lesson whose ref isn't approved/published — so assemble from approved atoms,
   or get the new atom approved first. There is no way around this, and that's the point.

If any to-do below seems to require breaking 1–4 to be "mind-blowing," it is wrong — stop
and surface it. Wow comes from a delightful, well-sequenced, *correct* experience, not from
a fabricated capability.

---

## 1. Shared context — paste this into EVERY worker agent

**Who it's for (judge every choice against this):** *John Doe, a POS cashier at a school
district.* JTBD: *"On day one, find the training for my role, finish it on my phone, and
prove I did it — with no setup and no training on the tool."*

**Hard constraints (BRD NFRs — not optional):**
- Mobile-responsive down to **375px** (cafeteria staff are on phones, not desks).
- Course player loads **< 3s**; each lesson **< 10 min** with clear progress.
- Ends in a **downloadable completion certificate**.
- Accessibility: **WCAG 2.1 AA** (contrast, keyboard, touch targets). Reuse existing tokens
  and components in `static/index.html` — do **not** hardcode colors or ship new CSS that
  bypasses the design system.

**The data model (real, in this repo):**
- **Track → Courses → Lessons.** A *Course* (`/api/courses`, `course_store.py`) has typed
  `lessons[]`; a *Track* (`/api/tracks`, `modules_store.py`) bundles `course_ids` + a
  `due_date` + `assessment_gate_id` + district `assignments` (the assignable unit).
- Lesson types and what each ref must resolve to (enforced server-side):
  - `guide` → an approved resource (`drafts/<ref>.json` or `published/metadata/<ref>.json`
    with `approved:true` or `status` in {approved, published}). Badge: `ai_grounded` for
    AI guides, `human_authored` for imported (`origin:internal`) guides.
  - `quiz` → `quizzes/<ref>.json` with `status:"approved"`. Badge: `ai_grounded`.
  - `video` / `external_icn` → an `asset_id` present in the ICN manifest. Badge:
    `outside_vendor` (link-out + credited).
  - `flashcards` → approved deck in `data/flashcards/`. `assessment` → published assessment.
  - `exercise` → always valid (human-assembled interactive). Badge: `human_authored` —
    so its content must still come only from approved-source steps; mark gaps `[TO VERIFY]`.
- **Everything is created `draft`.** `course_store.create_course` hardcodes `status:"draft"`;
  there is no auto-publish path. Publishing a course is a deliberate trainer/human action.

**Auth / how to call the API (demo bypass header):**
- Trainer actions (create/update/publish course, build track): header `X-Demo-User: sam-trainer`.
- Learner view (to verify what a cashier sees): `X-Demo-User: john-cashier`.
- District manager: `X-Demo-User: dana-director`.

**Sources of truth — and their roles (do not blur these):**
- `wiki/concepts/Accountability.md` + `wiki/entities/meal-service-accountability.md` =
  the **topic map + ticket anchors** for real POS/cashier work: ringing meals at the line,
  meal counts (by site / grade / device — e.g. NXT-10907), cash collection (NXT-10909),
  end-of-day session close & drawer reconciliation (NXT-13312), meal/eligibility exceptions
  (NXT-10941, NXT-70214), item lookup. **Use the wiki to decide *what topics* a cashier
  refresher should cover and to fact-check** — its prose is an analyst lens, NOT cashier
  how-to. **Do not turn wiki sentences into invented POS UI steps.**
- **Approved imported SchoolCafé guides** (the `GUIDE-NNN` / dated AI drafts that are
  `approved`) = the actual **teachable navigation/procedure** a lesson can present. Query
  them, don't guess which exist: `GET /api/modules?role=Cashier` and
  `GET /api/modules?q=item` / `q=accountability` / `q=point of sale`.
- **ICN/USDA catalog** (`GET /api/icn`) = food-safety / hygiene video, embeddable only if
  `license_posture != link_only`; otherwise link-out. Always credited.
- `search_kb` (the generator's fact-check tool) reads `wiki/concepts/*.md` +
  `wiki/workflows/*.md` + curated guide markdown — use it for verification, not as content.

**Known constraint — read before planning content:** the offline grounding gate has Jira
fixtures only for **Item Management, Eligibility, Financials** (transcript-only). **There is
no Accountability fixture**, so you **cannot** freshly AI-author *grounded* POS product
claims and pass the gate. ⇒ The spine of this course is **assembly of already-approved
atoms** + a **grounded quiz** + an optional **exercise**, themed for summer. Do not attempt
to generate a new grounded "POS Accountability" guide unless the human supplies a transcript
and explicitly opts into transcript-only mode (and even then it lands as draft for PO approval).

---

## 2. The to-dos (dependency-ordered — `‖` marks tasks that run in parallel)

> Each worker is a `claude-sonnet-4-6` agent. Give it §1 verbatim + its own block below.
> Keep outputs as small structured JSON where noted, so the orchestrator can chain them.

### Agent A — Grounding & content map  ·  ~10 min  ·  (blocks B/C/D)
**Goal:** produce the factual skeleton so no later agent has to guess.
**Steps:**
1. Read `wiki/concepts/Accountability.md` + `wiki/entities/meal-service-accountability.md`.
   Extract the 5–7 cashier-relevant topics a *refresher* should cover (line transactions,
   item lookup, meal counts/claiming basics, cash collection, end-of-day close & drawer
   reconcile, meal/eligibility exceptions, food safety/hygiene). For each, note the anchor
   ticket id(s) cited in the wiki.
2. Inventory **approved** atoms available to reference:
   `GET /api/modules?role=Cashier`, plus `q=item`, `q=accountability`, `q=food` searches;
   `GET /api/icn` (note which assets are embeddable vs link-only + their `source_url`);
   `GET /api/quizzes` (which are already `status:approved`, e.g. an existing cashier quiz).
3. Map each chosen topic → the approved atom that can teach it. Flag any topic with **no**
   approved atom as "framing-only / [TO VERIFY]" (it can be named in the intro but not
   taught as fact).
**Output contract (JSON):** `{ topics:[{name, anchor_tickets:[...], approved_atom:{type,ref,title}|null, gap:bool}], icn_video:{ref,title,source_url,embeddable}|null, existing_approved_quiz:{ref,title}|null }`
**Guardrail:** every `approved_atom.ref` must be confirmed approved via the API — no invented refs.
**Done-check:** at least 3 topics map to a real approved atom; gaps are explicitly flagged.

### Agent B — Course spine + summer framing/copy  ·  ~10 min  ·  (needs A) ‖ C ‖ D
**Goal:** the course shell + playful, fact-free framing copy.
**Steps:**
1. From A's map, pick **4–6 lessons** ordered as a refresher arc (warm-up → core POS →
   end-of-day → food safety → knowledge check → certify). Each lesson `duration_est ≤ 8`.
2. Write the summer theme **as framing only**: a course `title` (e.g. *"Cashier Summer
   Refresher: Back-to-School Tune-Up"*), a 1–2 sentence `description` (human-authored
   metadata — no product claims, no "cited" badge), and a short, warm lesson-intro line per
   lesson. Tone: friendly camp-counselor, not corporate. Zero invented features.
3. Emit the **draft course create body** (do not POST yet — E does that): `role_tags:["Cashier"]`,
   `product:"SchoolCafé"`, `lessons:[{type,ref,title,duration_est}]` using **only** A's
   confirmed approved refs. Leave a placeholder slot for C's quiz (filled at assembly).
**Output contract:** the JSON body for `POST /api/courses` + a one-line rationale per lesson.
**Guardrail:** no lesson ref that A didn't confirm approved; description carries no product fact.
**Done-check:** body validates conceptually against §1 lesson-type rules; ≤ 6 lessons, each ≤ 8 min.

### Agent C — Grounded "cookout pop-quiz"  ·  ~10 min  ·  (needs A) ‖ B ‖ D
**Goal:** a knowledge check that's fun in tone but **grounded in published content**.
**Steps:**
1. Pick the strongest **approved guide** from A as the quiz source.
2. `POST /api/quizzes/generate` with `{source_type:"resource", source_id:"<that guide id>", n:5}`.
   Questions are auto-grounded against the source text by the quiz gate. Light, summery
   question *wording* is fine; **answers must be verbatim-grounded spans** — the gate enforces.
3. Save it (draft). **Do NOT approve it.** Output the new quiz id and flag it for the PO queue.
   (If the human wants the course publishable *now*, B/E should instead reference the
   already-approved existing cashier quiz from A; a freshly generated quiz needs PO approval
   before it can be a course lesson.)
**Output contract:** `{ new_quiz_id, source_guide_ref, needs_PO_approval:true }`.
**Guardrail:** never call `/api/quizzes/{id}/approve`. No manual/un-sourced questions.
**Done-check:** quiz exists as draft; every question carries a source span.

### Agent D — Interactive "exercise" lesson (optional wow)  ·  ~10 min  ·  (needs A) ‖ B ‖ C
**Goal:** one delightful interactive beat — e.g. a "close your drawer" step-ordering mini-game.
**Steps:**
1. Build it **only** from approved-source steps (A's end-of-day / reconcile atom). Where a
   specific UI label or value isn't in an approved source, use a generic phrasing and a
   `[TO VERIFY]` note — never a fabricated label.
2. Implement within the existing `exercise` lesson mechanism / `static/index.html` components;
   reuse design tokens; keep it usable at 375px and keyboard-accessible (WCAG AA).
3. Badge honestly: exercises are `human_authored`, **not** "every claim cited."
**Output contract:** the `exercise` lesson object `{type:"exercise", ref, title, duration_est}` + a note of any `[TO VERIFY]` markers.
**Guardrail:** no new product claim that isn't in an approved source; no design-system bypass.
**Done-check:** renders at 375px, keyboard-navigable, all facts trace to A's atoms or are marked.

### Agent E — Assemble, wire into the website, verify  ·  ~15 min  ·  (needs B, C, D)
**Goal:** the course exists in the app and a cashier can actually take it.
**Steps:**
1. `POST /api/courses` (header `X-Demo-User: sam-trainer`) with B's body, inserting D's
   exercise lesson and the quiz lesson (use the **approved** quiz; if only C's new draft quiz
   exists, leave the quiz slot out and flag that it joins after PO approval). A 422 here means
   a ref isn't approved — fix the ref, don't force it.
2. (Optional, if the human wants it assignable) add the course to a **Track** for Cashiers
   with a summer `due_date`, mirroring `track-g1-cashier-onboarding.json`.
3. **Verify with preview tools, don't ask the human to check manually:** start/reload the
   server; as `john-cashier`, open the Learn view → the new course → each lesson; confirm
   provenance badges render (`human_authored` on guides, `outside_vendor` on the ICN video,
   `ai_grounded` on the quiz), the customer-view banner/chrome is correct, it loads < 3s, and
   it works at **375px** (`preview_resize`). Capture a screenshot as proof.
**Output contract:** the new `course_id` (+ `track_id` if built), a screenshot, and the
verification result (badges OK / mobile OK / load time).
**Guardrail:** **do not** publish to learners autonomously beyond what's needed to verify —
publishing the course for real is the human's call (see the gate below). Never approve a guide
or quiz atom.
**Done-check:** course renders correctly to a cashier in preview; all provenance honest; mobile OK.

### 🚦 Human gate — Product Owner (terminal, NOT an agent)
- A **Product Owner** approves any new atom C/D created (the draft quiz; the exercise content),
  re-validating grounding live. The agent surfaces these in the review queue; it never approves.
- The PO (or trainer) makes the final call to **publish the course** so it goes live to
  cashiers (`POST /api/courses/{cid}/publish`). Until then it sits as a draft / in the queue.

---

## 3. Definition of done
- A draft (or human-published) **Cashier Summer Refresher** course exists in the app,
  4–6 short lessons, role-tagged `Cashier`, themed for summer.
- Every lesson references an **approved** atom (or is flagged as pending PO approval); every
  product fact traces to an approved source; gaps are `[TO VERIFY]`, not invented.
- Provenance badges are honest (human-authored guides, outside-vendor ICN, ai-grounded quiz);
  nothing imported is mislabeled "every claim cited."
- Verified in preview as a cashier: loads < 3s, works at 375px, keyboard/contrast OK, ends in
  a certificate path.
- New atoms + final publish are left for the **PO/human** — the agents stopped at the gate.

## 4. Decisions left for the human (the forks I did not pre-empt)
1. **Publish now vs. leave as draft for PO?** Default here = build the draft + verify, human
   publishes. Say the word to have E publish the course container (its atoms are all approved).
2. **Use the existing approved cashier quiz (publishable now) vs. generate a fresh grounded
   quiz (richer, but needs PO approval before it can be a lesson)?** Default = use existing
   approved quiz for an immediately-live course; generate the fresh one in parallel for the PO.
3. **Course only, or also wrap it in an assignable Track with a summer due date?** Default =
   course only; add the Track if you want districts to be able to assign + track completion.
