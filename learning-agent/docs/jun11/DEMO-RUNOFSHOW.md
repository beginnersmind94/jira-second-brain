# Jun 11 Demo — Run of Show (15-minute click-through)

**Meeting:** Jun 11, 10:30–11:30 (the slot Dallas set: "10:30 To 11:30. I think everybody's free" — Jun-04 [45:10]; Audienne pushed back on going to 12: "No, one hour. One hour." — [45:16]).
**Audience:** Jamie (head of Implementation — understaffed on trainers/content), Audienne, Matt, Dallas.
**Driver:** Rahul (screen-share + narration). Dallas opens with framing.
**Goal of the meeting (per Audienne, Jun-04 [38:08]):** "set the scene that this is the beginning and the end product is more geared towards shaping training classes." If we don't, "what I'll hear privately later is going to be a lot of negativity." So we sell *foundation + leverage*, not "look at the robot writing."

> **One sentence to hold the whole room:** *This is Phase 1 of the Learning Academy — a content engine that turns a training recording into a cited, customer-ready guide in minutes, with a built-in quiz, so your team gets leverage instead of another blank Word doc to fill.*

---

## 0. The cardinal rule of the open (READ THIS FIRST)

**Do NOT open by uploading a transcript and watching the AI write.** For this audience that detonates the exact fear that runs the room. The fear is named explicitly and repeatedly in both transcripts:

- Rahul, May-26 [23:06]: "my only concern here is again, just accuracy because I feel like you make one mistake with AI and it loses credibility very quickly."
- Rahul, Jun-04 [25:55]: "if it even just has one mistake… a human can make one mistake… But if an AI makes it, immediately kills trust in the product."
- Audienne, Jun-04 [26:37]: "there's a much stricter lead to distrust once the human element is taken out."

So we open on the **finished, beautiful, trustworthy customer experience** — content that is real, cited, and (critically) *not AI-generated* — and we earn the right to show generation only after trust is established. We reveal speed last, framed as "and here's how the library fills itself."

**Opening surface = the "Content" tab (ICN / USDA library), in Customer view.** Why this exact surface and not the "Library":
- The published Library is **empty today** — `published/metadata/` has 0 entries (verified: dir is empty), so the Library's default "In Library (approved)" filter (`static/index.html:1532`) shows nothing. Opening there = dead air. (This gap is being handled separately by the lead; do not try to fix or explain it live.)
- The **Content tab is populated and customer-safe**: it's the externally-authored ICN/USDA pack (`demo_app.py:358-363`), explicitly a *browse/reference* lane that, by design, never claims the "verified by us" guarantee — it surfaces attribution + links only. The hero copy says it outright: *"Every asset is cited and attributed; nothing here is AI-generated."* (`static/index.html:1580`). That is the perfect first thing a hallucination-wary head of Implementation sees.

**Pre-flight checklist (do before the call, screen NOT shared):**
1. Server running locally (`python demo_app.py` per project run notes). Confirm `/api/icn` returns data (Content hero stats populate — `static/index.html:1583-1587`).
2. Browser zoom 100%, window wide enough to be in desktop layout (first responsive breakpoint is 1040px — `static/index.html:974`).
3. Set the header toggle to **Customer** (`setViewMode('customer')`, `static/index.html:1361-1362`). Confirm: Create, Quality, and the per-claim author chrome are hidden; the district switcher is locked (`static/index.html:1821-1830`).
4. Have **one transcript file** ready on the desktop for the Act 2 upload (any of the 8 fixtures has ticket backing — `data/demo/*.json`: item-management, inventory, eligibility, menu-planning, financials, accountability, account-management, insights). **Recommended: a module you can name a workflow for out loud** (e.g. inventory or item-management — these are the ones already exercised in the Jun-04 call).
5. Open `static/demo-item-management-long-form.html` in a second tab as a **fallback** in case live generation is slow or the API key hiccups (Rahul's Jun-04 note that the cost/latency tuning was the hard part — [06:14]–[08:34]). If anything stalls, switch tabs and keep talking; never let the room watch a spinner in silence.

---

## Timeline at a glance (15 min of a 60-min slot)

| Time | Act | What's on screen | The point |
|---|---|---|---|
| 0:00–2:00 | **Dallas framing** | (slide or just talk) | Phase 1 of the Learning Academy; replacing a $50–100k/yr tool; foundation for what your team asked for |
| 2:00–4:30 | **Act 1 — Customer experience** | Content tab → search/filter → open a course path | Beautiful, self-serve, cited, role-ready. *Customer* view. |
| 4:30–6:00 | **Act 1b — Trust + phone + PDF** | "Check your knowledge" source quote → resize to phone → Download PDF | Trust is visible per-claim; reads on a phone; prints clean |
| 6:00–9:00 | **Act 2 — Speed reveal** | Switch to Trainer → upload transcript → **source toggle** → Create draft | THIS is how the library fills — minutes, not days |
| 9:00–11:00 | **Act 3 — Grounding made visible** | "Show sources" chips on the fresh draft + Quality dashboard | Every claim traces to a real ticket at its trust tier |
| 11:00–12:30 | **Act 4 — Learning validation** | Generate a quiz from the content | "Not just reading — we prove they learned it" |
| 12:30–13:30 | **Act 5 — Bonus: release notes** | Format dropdown → "customer release notes" | "Same engine, more than learning content" |
| 13:30–15:00 | **The ask** | (talk) | Specific forward question — NOT "what do you think?" |

Buffer the remaining ~45 min for Jamie's discovery discussion (the real purpose — Audienne, Jun-04 [24:18], [67]).

---

## Act 0 — Dallas opens (2 min, Dallas talks; Rahul not yet sharing)

Dallas should set the frame himself — Audienne explicitly assigned him the instigator role (Jun-04 [44:07]: "things are always better accepted when you're the instigator"; [48]: "Why don't I kick off this meeting? I'll set up with Jamie and you and Matt and Audienne"). Suggested beats, all traceable to what Dallas already said:

1. **"This is the foundation, not the finished academy."** Jun-04 [15:18]: "This is the first phase of it… I can't have quizzes if I don't actually have content." Frame the rest of the academy (SSO, learning tracks, assign/monitor — Audienne [33]) as *next*, built on this.
2. **"We're replacing a $50–100k/yr tool we'd otherwise have to buy."** Jun-04 [27:17]: "we don't want to purchase a hundred thousand dollar documentation solution for something that we could build and house"; [41:13] "we've essentially removed the hook of paying 50 to $100,000 a year." This is the budget argument that makes the project safe to back.
3. **"This is leverage for your team, Jamie — not a replacement for it."** Tie to the staffing pain (see wedge below). Dallas's own words, Jun-04 [39:16]: "Jamie, you stick to training and interacting with customers, onboarding and implementation" while the tool does the content turnaround.
4. Hand to Rahul: *"Rahul's going to walk us through what we built, and then this becomes a working session with you on what the guides should contain."* (Audienne [126]: "do the hand[off]".)

**Rahul shares screen now — already on the Content tab, Customer view.**

---

## Act 1 — The finished customer experience (2:00–4:30)

> Narration anchor: *"This is what a district staff member sees when they log in to learn. No setup, no training on the tool — they just find what they need."*

### Beat 1.1 — The library, populated and beautiful (Content tab)
- We're on **Content** (`static/index.html:1575`, `view-content`). The hero reads: *"Sourced, role-ready training for your nutrition team … Every asset is cited and attributed; nothing here is AI-generated."* (`static/index.html:1579-1580`).
- Point at the trust stat strip: assets / roles / downloadable / quizzable / **100% cited & attributed** (`static/index.html:1583-1587`).
- **Say:** *"Everything here is real ICN and USDA training — food safety, handwashing, thermometers, menu planning. We've made it searchable, role-filtered, and we attribute every source."* (Matches the engine's design note — `demo_app.py:358-362`: browse/reference lane, attribution travels with every card.)

### Beat 1.2 — Search and filter (this is the self-serve story Dallas asked for)
- Use the **Filters & paths** panel (`static/index.html:1591-1593`). Filter by role/topic so the list shortlists.
- **Tie to the ask in the room.** Dallas, May-26 [08:40]: "basic, simple filter… we already know what product platform you're in… pre filter School Cafe guides only." And Jun-04 [16:14]: "a simple library that a user or users can go through and search for keywords or modules… it shortlists." This beat *is* that requirement, shipped.
- **Say:** *"A back-office user never sees point-of-sale guides; an inventory specialist sees only what's tied to their role."* (Exactly Audienne/Dallas's role-scoping intent — Jun-04 [52], [95].)

### Beat 1.3 — Open a course path
- Click into a path (`openPath`, `static/index.html:3060`). Show the numbered module list, the per-module attribution badges, and the **"Sources & attribution"** aside: *"Every module is externally authored and cited at its source — nothing in this path is AI-generated."* (`static/index.html:3094-3096`).
- **Say:** *"This is structured into a guided path — the start of a learning track."* (Plants the seed for Audienne's learning-tracks point, Jun-04 [33], without overclaiming we built tracks yet.)

---

## Act 1b — Trust, phone, print (4:30–6:00)

This act exists to *pre-empt the hallucination objection before it's raised*, while we're still on content that isn't even AI-made — so the trust mechanism lands without the AI baggage.

### Beat 1.4 — Per-claim trust ("Check your knowledge" source quote)
- On a module that's quizzable, click **"✎ Check your knowledge"** (`static/index.html:3069-3070`, `genQuiz`). When results render, point at the **verbatim source quote + "Source: ICN / USDA"** attached to the answer (`static/index.html:3265` for the flashcard variant; quiz footer "each verified verbatim against the source" at `:3248`).
- **Say:** *"Notice every answer carries the exact sentence it came from. Nothing is paraphrased into existence. If we can't quote the source, we drop it — you'll literally see a 'dropped' count."* (The drop behavior is real — the grounding gate keeps only items whose verbatim quote is found in a source chunk: `demo_app.py:575-593` for quiz, `:669-680` for flashcards.)
- This is the single most important trust beat. Let it breathe.

### Beat 1.5 — Phone viewport
- Resize the window narrow (or use device emulation) to cross the phone breakpoint (`static/index.html:991`, `@media (max-width:480px)`; viewport meta present at `:5`).
- **Tie to Dallas, Jun-04 [33:38]:** "if I'm on a tablet or if I'm on a phone, it converts. That's the big thing about HTML… if you open up a PDF on a phone, it looks like dog… but if we do the HTML, it converts nicely." And May-26 [35:37]: "all the content should be accessible via a phone… I don't think anybody really has that level."
- **Say:** *"Same content, reflows on a phone. A cafeteria manager can pull this up on the floor."*
- (Honest caveat to self — do NOT say aloud: phone is "needs polish, not net-new." Keep the resize gentle and on a clean content page; don't stress-test edge layouts live.)

### Beat 1.6 — Download PDF
- Return to desktop width, open a guide in the **Library** preview OR keep it simple and show PDF from a guide you can reach, then click **Download PDF** (`static/index.html:1558` lib button → `downloadResourcePdf`, wired at `:3491`; backend `demo_app.py:270-302`).
- **Say:** *"And when they want to print or email it, one click — a clean PDF."* The PDF **strips all the internal source comments** (`demo_app.py:282`, `_strip_source_comments`) and stamps a "PENDING REVIEW" banner on anything not yet human-approved (`demo_app.py:288-290`).
- **Tie to Dallas, Jun-04 [03:57]:** "give me the PDF. That's pretty cool." and the recurring "download a PDF / print it off" requirement (May-26 [20:32], [22:12]; Jun-04 [16:14], [84]).

> If the Library is your PDF source and it's empty in Customer view, instead download the PDF from the fallback tab (`demo-item-management-long-form.html` rendered) — or defer the PDF click to Act 3 on the freshly generated draft, where a guide definitely exists. **Pick one path in rehearsal; don't improvise live.**

---

## Act 2 — NOW reveal the speed (6:00–9:00)

Transition line: *"Everything you just saw, a customer experiences as a finished library. Here's how that library fills — and why your team gets leverage instead of a backlog."*

### Beat 2.1 — Switch to Trainer view
- Header toggle → **Trainer** (`static/index.html:1361`, `setViewMode('trainer')`). Create and Quality tabs reappear (`static/index.html:1821-1822`).
- **Say:** *"This half is internal — only your content team sees it. Customers never see the machinery."* (Matches Dallas's two-mode model, May-26 [54]: "have a producer mode and a directory mode"; and Jun-04 [42]: it "sidesteps Charlie" — i.e. it's a team tool, not a customer tool.)

### Beat 2.2 — Upload a transcript
- Create tab → **Upload transcript** (`static/index.html:1384`, drop zone `:1392`). Drop the prepared `.md`. Pick the **Product module** (`:1400-1401`).
- **Say:** *"I drop in a recording of one of your trainers walking through a module — the kind of thing that today goes to SharePoint and dies."* (Dallas, May-26 [26:59]: "Rather than dumping transcript on SharePoint, I want to… upload their transcript and it's stored into a database table.")

### Beat 2.3 — The source toggle (Dallas asked for this by name)
- Open **"Where claims come from"** (`static/index.html:1408-1412`): two options — **"Verified Jira tickets — behavior we can prove"** (default) and **"The transcript only — the presenter's exact words."**
- **Call it out explicitly and credit Dallas:** *"Dallas asked for exactly this — the ability to say 'use this transcript only, don't pull in Jira.'"* — Jun-04 [01:44]: *"I would add an option just for us that says… which trusted sources to look at. Just say like this document only or this transcript only… that ability to turn that off would be useful because… JIRA may add in a bunch of other stuff that we don't want."* **This is shipped.** Expand the "Why this matters" disclosure (`static/index.html:1413-1419`) to show we explain the trade-off in-product.
- Leave it on **Verified Jira tickets** for the demo (strongest trust story).

### Beat 2.4 — Generate
- Pick **Resource format** (`static/index.html:1404-1405`; options come from `demo_d.VALID_FORMATS` — `demo_app.py:713`). Choose **Micro guide** for speed (shorter = faster to watch than long-form).
- Optionally type a directive (`static/index.html:1422-1424`) — e.g. "for Houston ISD, keep it relatable" — and note the hint: *"Shapes focus, audience & tone — never the facts."* (Ties to Rahul's localization idea, Jun-04 [20:55]: "maybe the client is Houston ISD and you want to… make it more relatable.")
- Click **Create draft** (`static/index.html:1427`). Narrate the streaming stages while it runs.

> **The $3-vs-$300 line goes here.** Say: *"This run costs a few dollars. To get a comparable draft to a review-ready state by hand is hundreds."* Credit the framing to the Jun-04 open — Dallas [00:00]–[00:30]: *"to get to a point of review you'd spend hundreds of dollars at least just to get it there… if we have 100 guides and let's say it's $3 a pop, then 300 bucks to basically get an initial collection… that somebody can just validate."* **Do not invent a per-guide dollar figure beyond this** — $3/guide and "$300 for 100" are Dallas's own numbers; the only honest claim is "single-digit dollars per run." (Cost tuning was real work — Rahul, Jun-04 [06:14]–[07:49].)

> If generation is slow: switch to the fallback tab and say *"here's one I generated earlier"* — keep narrating the trust story; the speed point is already made by the cost line.

---

## Act 3 — Grounding made visible (9:00–11:00)

This is where we *answer* the hallucination fear head-on, now that we've shown AI writing.

### Beat 3.1 — "Show sources" on the fresh draft
- In the Create preview toolbar, click **"Show sources"** (`static/index.html:1489`; toggle logic `:2508-2512`). Every claim becomes a hoverable **citation chip** showing `NXT-#### · AC/RN/DESC` (`citeChipsHtml`, `static/index.html:2488-2501`). Hover one — the tooltip is the **verbatim quote** the claim traces to (`:2500-2501`).
- **Say:** *"Every sentence the AI wrote is pinned to a real, approved ticket — and tagged by how strong that evidence is: agreed acceptance criteria first, then release notes, then the original description."* (The tier hierarchy is real and surfaced in-product — `static/index.html:1416`, `:1783`.)
- **The trust moat, in one sentence:** *"The AI doesn't get to type a citation — it can only point at a source, and a deterministic check renders the exact quote and re-verifies it. If a claim has no source, it never makes it in."* (This is grounding-by-construction; the gate is the publish gate, per the project's enforcement model.)

### Beat 3.2 — The Quality dashboard
- Switch to **Quality** tab (`static/index.html:1355`, `showView('evals')`). Show the per-guide verdict table — "Verified," "Sources cited" count, and click a guide to see *which checks passed or failed* (`static/index.html:1925`). Point at the line: *"'Verified' means every claim in that guide traces to a real source at the correct trust level."* (`:1925`) and "No issues — every citation verified verbatim at the correct tier." (`:2025`).
- **Tie to Rahul's whole emphasis, Jun-04 [06:14]:** "most of my time was actually just spent on… the evaluation section just to make sure it's not hallucinating information." And the human gate: every doc still gets SME approval (Rahul, Jun-04 [20:55], [25:55]; Audienne [56] "please involve Jamie").
- **Say:** *"And nothing reaches a customer on the AI's say-so. A human approves every guide — approval is the only door into the Library, and it re-checks grounding at that moment."* (Human approval is the gate into the Library; the agent never auto-approves.)

---

## Act 4 — Learning validation (11:00–12:30)

This is the beat that turns "content tool" into "Learning Academy" — and it's exactly what Dallas told Audienne was already in scope.

### Beat 4.1 — Generate a quiz
- Easiest customer-facing version: stay on the **Content** path and use **"✎ Check your knowledge"** on a module (`static/index.html:3069`), OR (Trainer view) Create → **Study set** (`cmode-studyset`, trainer-only — `static/index.html:1386`, `:1825`), pick a **Topic** (`:1443-1444`), click **Generate quiz** (`:1448`).
- The modal streams *"Drafting and verifying each item against the source…"* (`static/index.html:3235`). Results footer: **"✓ N questions, each verified verbatim against the source · M dropped"** (`static/index.html:3248`). Endpoint: `POST /api/icn/quiz` (`demo_app.py:520`).
- **Say:** *"Every piece of learning content can carry a quiz — what Dallas called learning validation. Same trust rule: each answer is backed by a verbatim source quote, and anything we can't verify is dropped, not guessed."*
- **Tie to the record:** Dallas pitched this verbatim — May-26 [34:13]: "a proof of concept on a quiz builder where we can say… every piece of learning content, we can make what we call learning validation." And Audienne raised it as the training-team need, Jun-04 [33]: "the training team needing a way to set up learning tracks… assign, monitor"; Dallas confirmed it's in the plan ([34], [62]).

### Beat 4.2 — Show a flashcard flip (optional, 15 sec)
- If time: **Generate flashcards** (`static/index.html:1449`, `runFlashcards`), click a card to flip (`:3262`). Back shows the verbatim quote + attribution (`:3265`).

---

## Act 5 — Bonus reveal: it's not just learning content (12:30–13:30)

> Transition: *"And the same engine does more than guides."*

### Beat 5.1 — Release notes as an output format
- In Create, open the **Resource format** dropdown and select **"customer release notes."** This is a **real, built fourth format** — `demo_d.VALID_FORMATS = ("long-form", "micro-guide", "tldr", "release-notes")` (`demo_d.py:182`), labeled "customer release notes" (`demo_d.py:188`), with its own section spec (`demo_d.py:224-244`) and gate (`demo_d.py:557`).
- **Say:** *"Feed in a changelog instead of a transcript and the same engine produces standardized, professional release notes."*
- **Tie to Dallas, Jun-04 [29:38]:** *"Another thing is going to be release notes. We plug in release notes and we have that as an output… it spits out a version, release highlights… it looks professional, it looks standardized."* **Shipped.** This is a high-value "we already thought of your next ask" moment — use it to land the breadth of the platform.

> Keep this to ~60 seconds. Don't necessarily run a full generation here — selecting the format and naming the use case is enough to make the point. If you have buffer, generate; if not, move to the ask.

---

## The ask — close with a specific forward question (13:30–15:00)

**Do NOT end with "what do you think?"** Matt named that as the trap — Jun-04 [38:08]: *"If we don't set the scene that this is the beginning… what I'll hear privately later is going to be a lot of negativity."* Open-ended "thoughts?" invites the private no. Ask for *decisions*, which is also what Dallas wants out of the room (Jun-04 [29:15]: "I need your list of SMEs, I need your approval process and then we want to know the next steps").

**Say, to Jamie directly:**

> *"Two decisions I need from your team to make this yours:*
> 1. *What sections should each guide type contain? If 'Overview' should be 'Summary,' tell us — we change one template and it re-flows everywhere.*
> 2. *Should every guide end with a quiz, or is the quiz tied to a learning track instead?*
> *And operationally: who are your SMEs, and what's the approval step before something goes live?"*

Every clause above is traceable to what the room already asked for:
- Sections / "if you don't like 'Overview,' tell us 'Summary'": Dallas, Jun-04 [31:53] and [83] almost verbatim — *"I don't like overview, I think it should be summary… Cool. Tell us that, because we've been doing that to this point — it's just been a list we kick every single meeting."* This is the single most-repeated unmet ask in both calls.
- Quiz per guide vs. per learning track: Dallas, Jun-04 [77]: *"should each piece of content have… a learning validation quiz… or is learning and quizzing more around the idea of a lesson plan?"* — an open question he wants the team to weigh in on.
- SME list + approval process: Dallas, Jun-04 [39:16] and [81]; Audienne [128] (let Jamie name who's in the room / who the SME is).

**Then hand to the discovery phase** (the real reason for the 60-min slot): *"From here, I'll be working directly with you and your team — I'd love to shadow a few of you to learn the day-to-day."* (Rahul's own commitment — Jun-04 [25:26], [74]; Audienne's instruction "start setting up discovery sessions with Jamie as soon as possible" — [67].)

---

## The staffing-pain wedge (weave through, don't make it a slide)

Jamie's team is understaffed on trainers/content. The wedge is: **more leverage with the tool than without it** — it does not replace her people, it multiplies the few she has. Where to land it:

- During Act 2 (speed): *"Your team records a session they were already doing. The tool turns it into a publishable draft. That's the difference between three trainers producing like ten and three trainers producing like three."*
- Grounded in Dallas's own framing of the pain and the answer — Jun-04 [39:16]: *"I'll find somebody who does want to drive content. We'll hire a content manager. And Jamie, you stick to training and interacting with customers."* And [28:09]/[31:21]: the alternative is "replacing Word with a web-based solution… there's no value in that long term" — i.e. without the engine, it's just more manual work for an already-stretched team.
- The seat-limit jab (only if Jamie raises cost/scale): Dallas, Jun-04 [41:13]–[41:59] — purchased tools cap seats ("you can do like 200 at a time"), and the team's reflex is "we just need it during training," which Dallas calls "short sighted." Our version has no seat tax.

> Tone: the wedge is *for* Jamie, never *at* her. Audienne was explicit (Jun-04 [56], [67]): she must feel heard, and "it doesn't just seem like there is work being done in a vacuum without their input." Frame leverage as a gift to a stretched team, not a verdict on it.

---

## Objection-handling table (Jamie's likely pushback)

| Likely objection (and where it's foreshadowed) | One-line response | Backed by |
|---|---|---|
| **"This sidesteps my team / Charlie."** (Audienne, Jun-04 [44]: "It kind of sidesteps Charlie completely.") | "It doesn't replace your people — it removes the blank-page grind so they spend time on judgment: is this *right*, and does it fit *our* customers. Your SMEs are the gate; nothing publishes without them." | Human approval is the only door into the Library; agent never auto-approves. SME approval stressed by Rahul (Jun-04 [20:55], [25:55]). |
| **"We like writing manually / we'll maintain it ourselves over six years."** (Dallas paraphrasing the team, Jun-04 [20:08].) | "Totally fine to hand-edit — every draft is editable, and you lock in your wording so the AI can't overwrite it. The tool just gets you to a near-done draft in minutes instead of starting from a blank doc." | AI-assisted edit path exists (find/replace ops, can't touch citations; gate re-runs) — Rahul committed to the editor, Jun-04 [20:55]; Dallas's "preserve this / don't let AI overwrite it," May-26 [33:16]. *(Note: it's a grounding-safe assisted editor, not a raw rich-text box — say "edit and lock your wording," not "free-text editor.")* |
| **"AI will make things up — accuracy."** (The core fear: Rahul [23:06]/[25:55]; Audienne [26:37].) | "It structurally can't invent a fact. The model only points at a source; a deterministic step renders the exact quote and re-verifies it; unverifiable claims are dropped, not guessed — you saw the 'dropped' count. And a human still approves." | "Show sources" chips (`static/index.html:2488-2501`); quiz/flashcard drop gate (`demo_app.py:575-593`, `:669-680`); Quality dashboard (`:1925`, `:2025`); PDF strips internals + pending banner (`demo_app.py:282-290`). |
| **"Just tell me what to type and I'll do it."** (Dallas quoting Jamie, Jun-04 [28:09], [38:36].) | "That's exactly the loop we're breaking. Instead of a list we re-kick every meeting, the tool produces the draft and asks *you* one question: does this make sense and fit your customers?" | Dallas, Jun-04 [31:21]: "you don't need a perfect person that understands grammar… you just log in: does this guide make absolute sense?" |
| **"Is this the whole Learning Academy? Where are tracks/SSO?"** (Audienne [33], [37:07].) | "This is Phase 1 — the content engine. Tracks, SSO, assign/monitor sit on top of it next. We needed cited content to exist before any of that is possible." | Dallas, Jun-04 [15:18]: "This is the first phase… I can't have quizzes if I don't actually have content." SSO/import deferred (Audienne [96]). |

---

## Hard "do / don't" for the driver

**Do:**
- Open in **Customer view on the Content tab**. Stay in the finished experience for the first ~6 minutes.
- Keep the source toggle on **Verified Jira tickets** for the live generation.
- Say the **$3 / "$300 for 100"** numbers as *Dallas's* numbers; cap your own claim at "single-digit dollars per run."
- Use the **fallback tab** the instant anything stalls. Narrate through it.
- End on the **two-decision ask**, addressed to Jamie.

**Don't:**
- Don't open the **Library** tab in Customer view (it's empty today — `published/metadata/` is empty; the gap is owned elsewhere — don't explain or apologize for it live).
- Don't call the editor a "rich-text / raw editor" — it's a grounding-safe assisted edit. (A raw editor is intentionally out — it would break grounding.)
- Don't promise SSO, learning tracks, audio/dictation, or screenshot-scraping as built. They are discussed in transcripts as *future* (audio: May-26 [36:29]–[36:37]; SSO: Jun-04 [96]; screenshots: Jun-04 [21:33]). Say "next," never "done."
- Don't claim the published library has content. Don't claim coverage/completeness is guaranteed — the gate proves *provenance*, not that every feature is covered.
- Don't end with "what do you think?" (Matt's named trap, Jun-04 [38:08]).

---

## Grounding appendix — every code claim, by file:line (verified this session)

| Claim in this run-of-show | Evidence |
|---|---|
| Trainer/Customer view toggle; customer hides Create/Quality, locks district switch | `static/index.html:1360-1363`, `:1810-1834` |
| Source-control selector ("Verified Jira tickets" / "The transcript only") + why-disclosure | `static/index.html:1408-1419` |
| Resource formats incl. release-notes; dropdown fed from VALID_FORMATS | `demo_d.py:182,188,224-244,557`; `demo_app.py:713` |
| "Show sources" → citation chips with tier + verbatim quote tooltip | `static/index.html:1489`, `:2488-2512` |
| Quality dashboard verdicts / "every claim traces to a real source at the correct trust level" | `static/index.html:1925`, `:2022-2025` |
| Library search / module / template / status filters + live search + sort | `static/index.html:1517-1547`, `:3279-3363` |
| Library preview renders **clean** HTML (`?view=clean`) + Download PDF | `static/index.html:3392-3393`, `:3491` |
| **Library is empty today** (default "In Library (approved)" shows nothing) | `published/metadata/` empty (dir listing); default filter `static/index.html:1532` |
| ICN/USDA Content tab — populated browse/reference lane, attribution-only, "nothing here is AI-generated" | `demo_app.py:358-363`; `static/index.html:1579-1580`, `:3094-3096`; data present in `data/icn/` |
| "✎ Check your knowledge" per-module quiz button (customer-facing) | `static/index.html:3069-3070` |
| Study-set quiz/flashcards (trainer authoring) by topic | `static/index.html:1386,1443-1449`, `:1825`, `:3216-3270` |
| Quiz/flashcard endpoints with verbatim source_quote re-verify + drop | `demo_app.py:520-593` (quiz), `:615-680` (flashcards) |
| PDF export strips Source comments + pending-review banner | `demo_app.py:266-302` (strip `:282`, banner `:288-290`) |
| Responsive breakpoints 1040/760/720/480 + viewport meta | `static/index.html:974,981,991,1180,1230,1295`; meta `:5` |
| Transcript-upload modules (fixtures with ticket backing) | `data/demo/*.json` (8 modules) |

**Transcript citations** use the timestamps as printed in the two source files: `LMS-and-AI-Content-Authoring-3098b677-7503.md` (labeled May 26) and `Jun-04-01-13-PM-ecd6c74c-7b07.md` (labeled Jun 04; speakers are unlabeled — Speaker 1 = Dallas, Speaker 2 = Rahul, Speaker 3 = Audienne, inferred from content and the named participants).

> **Note on a stale doc:** `learning-agent/CLAUDE.md` ("V1 Implementation Notes") still lists quizzes/flashcards and release-notes as "not built / V1.5." The **code contradicts that** (endpoints and formats above), and the task ground-truth confirms quiz/flashcards are built. Code is authoritative for this demo. (Flagged for a doc cleanup, separately.)
