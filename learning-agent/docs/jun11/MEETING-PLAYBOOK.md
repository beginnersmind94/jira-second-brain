# Meeting Playbook — Jamie Demo (Thu Jun 11) + Matt Pre-Walk (Mon Jun 8)

**Audience:** Rahul (builder/presenter) and Dallas (sponsor, opens the room).
**Purpose:** Lock the political framing and logistics so the Jun 11 demo lands as
"Phase 1 of the learning-academy roadmap goal," surfaces the right next-step
feedback from Jamie, and does not read as a tool that sidesteps her team.

**Sourcing rules for this doc.** Every meeting claim cites a timestamp. Unless
marked `[May-26]`, timestamps are from `Jun-04-01-13-PM-ecd6c74c-7b07.md` (the
Jun 4 call; meeting header says 6:13 PM, file is named 01-13-PM). `[May-26]`
timestamps are from `LMS-and-AI-Content-Authoring-3098b677-7503.md` (May 26
Dallas/Rahul 1:1). Code claims cite `file:line`. Where the transcript and the
current code disagree, that is flagged explicitly as an open item — not smoothed
over.

**Speaker mapping (Jun 4 transcript is anonymized as Speaker 1/2/3):**
- **Speaker 1 = Dallas.** Drives the vision; refers to "Mine was maybe" about his
  own earlier demo [09:34]; says "I am out of pocket on Wednesday" [30:22] which
  Matt corroborates as "Dallas is out Wednesday" [42:29].
- **Speaker 2 = Rahul.** Built the POC ("that's just how the agent is designed"
  [00:47]); "I've been moving everything to my own personal GitHub... no PII"
  [46:01]; "if we're able to meet on Monday, Matt, for a one one" [37:28].
- **Speaker 3 = Matt.** Raises Jamie-as-stakeholder repeatedly; "let me be
  completely blunt here" [38:05]; named by Rahul at [37:28] as the Monday 1:1
  partner. (Confirms the Mon Jun 8 1:1 is **Rahul + Matt**, not Dallas.)

> One read-the-room note before everything else: the Jun 11 invite is **Thursday
> Jun 11** at **10:30–11:30**, capped at one hour [44:50, 45:10, 45:16]. Dallas
> kicks it off and hands to Rahul [42:48–43:29]. Rahul then "works directly with
> you" (Jamie) from that point on [43:20]. Dallas is out Wednesday Jun 10
> [42:29], so the Mon Jun 8 pre-walk is the last clean checkpoint before any
> pivot [42:32–42:38].

---

## 1. Monday Jun 8 — Dallas/Matt Pre-Walk Agenda (the 1:1 is Rahul + Matt)

Rahul proposed this 1:1 himself: *"if we're able to meet on Monday, Matt, for a
one one I can just use all the feedback I got in this meeting, just quickly run
it by you and then if you approve it... I'm walking in with more confidence"*
[37:28]. Matt agreed and tied it to schedule risk: *"If we're meeting Monday and
there's any need to do a big pivot... it gives you more time"* [42:32]. So the
Monday meeting's job is **approve the framing and catch any pivot before Dallas
goes dark Wednesday.**

### What to lock on Monday (decision list)

**1a. The Phase-1 framing — get Matt to bless the exact sentence.**
The framing Dallas already articulated, and the one to repeat verbatim Thursday:
*"This is the first phase of it"* [15:18]; the academy goal is alive, this is
*"the foundation to doing the next steps"* [42:48, said as "this is kind of where
everything was culminating. We feel like this is the foundation to doing the next
steps"]. The Phase-1
scope is **content authoring + a searchable library**, with interactive learning
(tracks, quizzes, lesson plans) explicitly named as the *next* phase, not cut:
*"let's focus on content authoring... and being able to search. And then the next
thing would be the more interactive elements of learning"* [11:42–12:17].
- **Lock:** Matt confirms we lead with "Phase 1 of the academy roadmap goal," and
  that we say the next phase (tracks/quizzes/SSO) out loud so it doesn't read as
  the whole deliverable. Matt's warning is that if we *don't* set that scene, the
  feedback dries up (see §2).

**1b. Demo from PRE-GENERATED cached state. Nobody clicks Generate live.**
This is a hard logistics rule, and it is grounded in two facts:
- **Cost/latency per live run is real.** Dallas: *"hundreds of dollars at least
  just to get it there... if we have 100 guides and... $3 a pop, then 300"*
  [00:00]. Rahul spent most of his build time *"keeping the cost down... you
  don't want something that takes an hour to run"* [06:14–07:49]. A live
  generation in front of Jamie risks both a long pause and a visible dollar
  figure.
- **The keys are personal.** Rahul: *"the main thing really is the Claude API key
  and... the Jira API key. How do we make that something that is a common API key
  for everyone? ... I have been moving everything to my own personal GitHub"*
  [46:01]. Running live spends Rahul's personal API budget in front of
  stakeholders — avoid.
- **The product already supports showing finished state without generating.**
  Resources render from stored clean HTML and export to PDF with no model call:
  `GET /resources/{rid}/pdf` renders the resource's already-stored HTML to PDF
  via pymupdf (`demo_app.py:270`), stripping `<!-- Source -->` comments first
  (`demo_app.py:282`). So the demo path is: open a pre-built resource → show the
  rendered guide → export PDF. No Generate click required.
- **Lock:** Pre-generate every guide we intend to show **before Monday**, confirm
  each opens and exports, and rehearse a no-Generate path. If we must show the
  authoring flow, show it on a guide that is already cached, or narrate it
  without hitting the button. Decide Monday which 1–3 modules we open live.
  - Honesty note for Matt: the cost number Dallas used ("$3 a pop", "$300 for
    100") is his back-of-envelope figure from [00:00], not a measured per-guide
    cost from the code. If anyone asks the real number Thursday, we say it's an
    estimate, not a benchmark. Don't present it as measured.

**1c. Who opens.** Dallas opens the room and frames; Rahul drives the product.
Dallas volunteered this: *"Why don't I kick off this meeting? I'll set up with
Jamie and you and Matt and Audin... we introduce what is there and then... from
this point forward, Rahul's going to be working directly with you"* [42:48–43:20].
- **Lock:** Dallas does the first ~3–5 minutes (why we did a POC, Phase-1 framing,
  the "we're not buying a $100K tool" line — see §4 Dallas win). Then hands to
  Rahul for the walkthrough. Confirm Dallas is comfortable delivering the reframe
  in §2 if Jamie tenses up, since it's his relationship to manage with Jamie and
  Matt's prediction is about *private* fallout.

**1d. Confirm the two views we toggle between, and default to the right one.**
The product has a Trainer/Customer toggle (`static/index.html:1360-1362`,
`setViewMode` at `:1811`). Customer view hides the author tab and the evals tab
(`:1821-1822`), locks the district switcher (`:1830`), and hides run cost
(`:1940`). This matters because Jamie's mental model shifted *during* the Jun 4
call: Rahul built for an **internal** customer (Jamie's team) [35:51], but Matt
and Dallas corrected that the paying **district** customer is the end user
[36:03–36:18: Matt "that was always the intent... our paying customers can log in
self learn"]. The toggle lets us show both audiences without a rebuild.
- **Lock:** Decide the open. Recommend opening in **Trainer** view (to show
  authoring + the trust machinery), then flipping to **Customer** view to show
  what a district user sees (cost/evals/author hidden). This visually answers
  Matt's "this is for paying customers" point and Jamie's "what does my team
  touch" question in one move.

### Monday output
A one-paragraph "approved framing" Rahul can paste into the Thursday open, the
locked list of modules to pre-generate, and a yes/no from Matt on whether the
reframe language in §2 is the one to use.

---

## 2. The Framing Risk Matt Named — and the Reframe That Defuses It

**The risk, in Matt's exact words.** Matt asked to be blunt and then said:

> [38:08] *"If we don't set the scene that this is the beginning and at the end
> product is more geared towards shaping training classes and the like for users,
> we're probably not going to get much feedback from Jamie. And what I'll hear
> privately later is going to be a lot of negativity."*

The negativity is **private and post-meeting** — Matt hears it afterward [38:23,
"what I'll hear privately later"]. So the room may look fine and the damage still
lands later. The trigger is the tool reading as something that **sidesteps her
team / cuts them out.** Matt circled this fear three times:
- [10:18] *"yours is more aligned with what Jamie needs. If our intent is not to
  go in that direction, then we need to let Jamie know."*
- [18:40] *"Are we planning on involving Jamie as a stakeholder... or are we
  cutting them out? I've got her asking about it."*
- [19:42] *"Rahul, please involve Jamie. The primary stakeholder in my opinion...
  if her team balks at this... then we're wasting our money."*

There is also a **Charlie-shaped** version of the same fear. Matt floated that in
its current form *"this is a tool for Charlie to use"* [13:05] and that *"it kind
of sidesteps Charlie completely"* [13:18]. Dallas's answer reframes Charlie's
role rather than denying the sidestep (see §3d).

**The reframe that defuses it.** Dallas already supplied the language; the job is
to lead with it, not let Jamie infer the opposite. Three moves, all
transcript-grounded:

1. **"This maintains and creates content for you — it's the tool we'd otherwise
   buy."** Dallas: *"this is a way for you to maintain and create content really
   quickly, to review and approve... Just like the tools we built / pay a lot of
   money for, we're essentially replacing that. This is our content tool"*
   [39:16]. Frame the tool as *infrastructure that serves Jamie's team*, not a
   replacement for it. The verbs land on her team: **they** review, **they**
   approve, **they** localize.

2. **"You keep editorial control. We draft; you decide the words."** Dallas:
   *"we're not telling her our content should be done... you need a repeatable
   format. And here's what out of the box. If you don't like it... 'I don't like
   overview. I think it should be summary.' Cool. Tell us that"* [31:53–32:39].
   And: *"you still give control to them to say... you don't like that word... just
   modify it, save that and lock that in as your thing"* [40:36]. The control
   message is backed by product: every guide is gated behind SME approval — Rahul:
   *"every document should be approved by an SME"* [20:55] — and a draft →
   SME-approved → Jamie final-review status ladder exists in the framing
   [31:21–31:51].

3. **"The end state is training classes for your users — name the next phase out
   loud."** This is the literal cure Matt prescribed [38:08]: say the academy is
   about shaping training for users (tracks, quizzes, lesson plans, SSO), and that
   this phase is the prerequisite. Dallas's "I can't have quizzes if I don't
   actually have content... without the prerequisites, it's kind of dead" [15:18,
   10:36] is the one-liner for *why* authoring came first.

**What NOT to say.** Do not let the room hear "this replaces your team" or "this
makes documentation hands-off." Matt's drift is exactly that an unqualified tool
demo *implies* the team is being cut out. Keep ownership verbs on Jamie's people.

**Internal-only caution — do not say this to Jamie.** Dallas's candid fallback
plan ("I'll find somebody who does want to drive content. We'll hire a content
manager. And Jamie, you stick to training" [38:36]; "they're not the ones calling
the final shots" [40:00, 39:16]) is **internal posture, not demo language.**
Saying any of it in the room is the fastest way to manufacture the private
negativity Matt is warning about. Dallas already flagged he'll *"be tactful"*
[40:00]. Keep it tactful.

---

## 3. Open Questions to Resolve (before or during Thursday)

These are genuinely unresolved in the transcript. Each notes who owns it and what
the answer signals.

### 3a. Who are the SMEs? — Jamie owns the list.
Dallas: *"I need your list of SMEs, I need your approval process"* [39:16]. The
whole trust model depends on named humans approving each guide (§2 move 2;
[20:55, 25:55]). Right now we don't have the list.
- **Resolve:** This is an explicit Thursday *ask* of Jamie, framed as input we
  need from her (reinforces "you're the stakeholder"). Do not name SMEs ourselves.
- **Signal:** Who Jamie names — and whether she names herself — tells us how much
  she's claiming ownership vs. delegating.

### 3b. Does launch require quizzes, or is authoring + library enough for v1?
**Dallas said both, and did not resolve it.** Pin this Monday.
- For "authoring + library is enough to start": *"This is just the first. Can we
  get here and... start building"* [12:29]; *"this is the first phase"* [15:18];
  the May-26 framing is explicitly "V1 = builder + directory, quizzes later"
  [21:03 May-26, 21:58 May-26].
- For "we won't launch without quizzes/learning": *"We may say we're not going to
  launch without the... we don't want to launch without the quizzes or learning
  aspect. But this gives us at least we can start"* [12:29].
- **Note the product reality:** grounded quizzes and flashcards already exist
  (`/api/icn/quiz`, `/api/icn/flashcards`, per ground truth), so a quiz *can* be
  shown Thursday as proof the next phase is reachable — but whether quizzes
  **gate launch** is a roadmap decision, not a build gap.
- **Resolve (Monday):** Get Matt/Dallas to state the v1 launch bar in one
  sentence. Recommended: "v1 ships authoring + library; quizzes are demoed
  Thursday as the next phase, not a launch blocker." Confirm before we imply
  either to Jamie.

### 3c. Hosting / shared API keys — flagged, owned by dev team, not us to answer.
Rahul: *"the main thing really is the Claude API key and... the Jira API key. How
do we make that something that is a common API key for everyone? I think that is a
more technical discussion that... someone from the dev team. It would be nice to
have some input from"* [46:01]. Today it runs only on Rahul's local on personal
keys [46:01; Dallas confirms "this is only available on your local, right?" at
46:01]. May-26 deferred the same to "Bonnie / the team" for hosting [29:15
May-26, 30:07 May-26].
- **Resolve:** Out of scope for Thursday's demo content, but have a one-liner
  ready if asked: "It runs locally today; production hosting and shared keys are a
  dev-team discussion we've already flagged." Do **not** promise a hosting date.
  Reinforces why we demo from cached state (§1b).

### 3d. Is Charlie on the invite — and what does that signal?
This is deliberately being **left to Jamie**, and that is the point. Dallas asked
*"Should I include Charlie or just have Jamie say...?"* and Matt answered: *"let
her include who she thinks should be there and that'll be... a little telling for
us... whether she's christening [him] as an SME for this"* [44:24–44:41]. Dallas
agreed [44:50].
- **The signal:** If Jamie brings Charlie, she's positioning him as an SME/owner;
  if she doesn't, she's signaling a different ownership map. Either way it's
  intel, so **we don't pre-load the invite with Charlie.**
- **Role framing if Charlie is present:** Dallas's stated view is the tool is *not*
  Charlie's to own — *"Not really for Charlie. I don't think Charlie's the right..."*
  [13:14] and *"Charlie's just kind of doing what he's told right now"* [13:21] —
  but Charlie *can coordinate* creation/validation and could upload content [13:21,
  14:19]. Keep Charlie framed as a coordinator/contributor, not the engine, and let
  the SME ownership question route through Jamie (§3a).
- Note: Charlie is already real in the workflow — Rahul has been building FAQ docs
  from Charlie's Freshdesk/Jira ticket lists and Charlie manually reviews them for
  hallucinations [02:26–03:19]. So "Charlie is involved" is true today; the open
  question is only his *ownership* role going forward.

### 3e. (Watch item, not for Jamie) PM team / Audienne / accredited trainer.
- Rahul: *"I don't want to include PM just yet. It's only if I get super
  pushback"* [44:50]. **Keep PM off the Thursday invite.**
- Dallas floated including **Audienne** ("Audin"/"Audienne") in the kickoff
  [40:36, 42:48]. Confirm Monday whether Audienne is on the Thursday invite or a
  later one.
- Matt wondered whether Jamie's team has an **accredited trainer** (named Taylor,
  ex-software trainer) who'd be more useful for structured learning design
  [40:19–40:36]. Treat as a discovery follow-up *after* Thursday, not a Thursday
  agenda item.

---

## 4. Stakeholder Map + Each Person's Win Condition

| Stakeholder | Role in this | What "win" looks like for them | Source |
|---|---|---|---|
| **Dallas** (sponsor / vision) | Opens the room, owns the "don't buy a $100K tool" thesis, manages the Jamie relationship politically | Demo proves we can build/house/customize this in-product and **avoid a $50K–$100K/yr third-party documentation tool** with seat limits | *"we don't want to purchase a hundred thousand dollar documentation solution for something that we could build and house"* [27:17]; *"removed the hook of paying 50 to $100,000 a year... they have very limited... seats... 200 at a time"* [41:17–41:59] |
| **Matt** (BRD owner / blunt truth-teller) | Pressure-tests stakeholder management; will hear Jamie's private reaction | Jamie feels **heard as the primary stakeholder**, the academy roadmap goal is visibly intact, and he does **not** get private negativity afterward | *"please involve Jamie... the primary stakeholder"* [19:42]; *"so that she feels heard, for one"* [24:18]; the [38:08] private-negativity warning |
| **Rahul** (builder / presenter, post-demo lead) | Drives the walkthrough; becomes Jamie's direct contact after Thursday | Gets Jamie's **SME list + approval process**, sets up discovery/shadowing, and protects the trust story (no AI mistakes in front of stakeholders) | *"I need your list of SMEs... your approval process"* [39:16, said by Dallas as the ask Rahul carries]; *"I can definitely set up calls... shadow them"* [25:26]; trust-is-everything thread [03:19, 20:05, 25:55] |
| **Jamie** (training lead / primary stakeholder) | Target of the demo; her buy-in unblocks the money | Sees a tool that **serves her team and keeps her editorial control**, and gets to shape the guide format/sections she's been asked about "for meetings and meetings" | *"the only answer I get from Jamie is just tell me what I need to do"* [28:09]; format questions *"have been asked for meetings and meetings... no movement"* [28:09]; she's *"asking about it"* [18:40] |
| **Charlie** (content coordinator / Freshdesk-FAQ collaborator) | Possible SME/coordinator; presence-on-invite is a signal (§3d) | Stays a **contributor/coordinator**, not displaced; his FAQ-review work continues | *"Charlie can coordinate... the creation of the content, the validation"* [13:21]; FAQ review collaboration [02:26] |
| **Audienne** (optional kickoff attendee) | Possibly in the kickoff to show this came from ongoing AI-content discussions | Sees this as a credible outcome of prior strategy conversations | *"we can even include Audienne just to say... this is an outcome of things that we've been discussing"* [40:36] |
| **Dev team / Bonnie** (hosting, shared keys) | Not in Thursday meeting; owns the hosting/keys question (§3c) | Clear, scoped technical ask later — not a surprise | hosting deferred to team [29:15 May-26]; shared-keys flagged for dev input [46:01] |

**The cross-cutting win nobody will say out loud but everyone shares:** the trust
moat. Rahul stated it as the thing that makes or breaks adoption — *"the main
thing is really just being able to establish trust in the content... if an AI
makes [a mistake] it immediately kills trust"* [25:55, 03:19], and Matt agreed
*"there's a much stricter lead to distrust once the human element is taken out"*
[26:37]. The product answers this by construction: guides carry source citations
at trust tiers (the source selector exposes "Verified Jira tickets — behavior we
can prove" with AC-first / release-notes / description tiering, vs. "The
transcript only — the presenter's exact words", `static/index.html:1410-1411,
1416-1417`), and the PDF export strips those `<!-- Source -->` comments so the
customer artifact stays clean (`demo_app.py:282`). **If trust comes up, demo the
source selector and the citations — that's the differentiator.**

---

## 5. The Explicit Win / Lose Test

**Win.** From the tracker (per workflow ground truth): the demo wins if **Jamie
leaves saying "I want SSO and learning tracks next."** That sentence means she has
(a) accepted Phase 1 as the foundation rather than the finished product, and (b)
started pulling on the *next* phase herself — which is precisely the feedback Matt
said we'd otherwise fail to get [38:08]. It maps directly to what Matt named as
the polish path: *"things like SSO, automatic user import... will likely be key"*
[37:07], and to Dallas's roadmap arc of authoring → library → tracks/quizzes/SSO
[16:14–17:26, 23:28].

**Concrete win signals to listen for Thursday (all transcript-anchored):**
- Jamie asks about **SSO / user import / learning tracks** as *next steps* — the
  win sentence [37:07, 33:38, 23:28].
- Jamie engages on **guide format/sections** ("it should say Summary not
  Overview") — exactly the input Dallas has been unable to get [31:53–32:39].
- Jamie commits to **sending training videos/transcripts** so the library can fill
  — Dallas's standing ask: *"When am I going to get my training videos, my
  transcripts?... Jamie said she was going to be driving that"* [42:48].
- Jamie names **SMEs / an approval process** (§3a) [39:16].

**Lose.** The demo loses if it triggers Matt's predicted outcome: Jamie gives
little feedback in the room and **private negativity lands afterward** [38:08],
because the tool read as cutting her team out [18:40] or as "a tool for Charlie"
[13:05–13:18]. The other lose mode is self-inflicted and avoidable: **an AI
mistake visible in front of stakeholders**, which Rahul and Matt both say
*"immediately kills trust"* [25:55, 26:37] — the single strongest argument for the
pre-generated/cached demo path in §1b. A third, milder lose: Jamie defaults to
*"just tell me what I need to do"* [28:09] and stays passive — recoverable by
pushing the format question back to her live (§5 win signal 2).

**Lose-prevention checklist (Monday → Thursday):**
- [ ] Framing sentence approved by Matt; "next phase = tracks/quizzes/SSO" said
      out loud in the open (kills the sidesteps-my-team read). [38:08]
- [ ] Demo runs entirely from pre-generated/cached resources; no live Generate on
      personal keys; PDF export pre-tested. [00:00, 06:14, 46:01; `demo_app.py:270`]
- [ ] Ownership verbs stay on Jamie's team throughout (review/approve/localize).
      [39:16, 40:36]
- [ ] Charlie not pre-added to invite; left to Jamie as a signal. [44:24–44:41]
- [ ] PM team not invited unless pushback forces it. [44:50]
- [ ] Internal fallback posture (hire a content manager / "not their final call")
      stays out of the room. [38:36, 40:00]
- [ ] Trust story rehearsed: source selector + citations + clean-PDF export ready
      to show if accuracy is questioned. [25:55; `index.html:1410-1411`,
      `demo_app.py:282`]

---

## Appendix A — One open contradiction to settle internally (do not surface to Jamie)

**Rich-text editing of drafts.** In the room, Rahul committed to building a
free-form editor: when Dallas asked whether the team can *"go in and have a rich
text and kind of modify this,"* Rahul answered *"No, no. I will build something
like that"* [20:55], and Dallas reinforced the rich-text-edit expectation at
[21:33] and [63:00-range May-26: *"we can build in a simple HTML editor... a rich
text editor"* at 33:16 May-26].

**But the current architecture intentionally does NOT expose a raw rich-text
editor** (per workflow ground truth): a RAW editor would break
grounding-by-construction, so AI edits route through a constrained find/replace
(`revise.py`) that cannot touch `<!-- Source -->` comments and re-runs the gate.

This is a real tension between what was verbally promised and what's built. It is
**not a Thursday topic** — Jamie shouldn't hear "we promised an editor and don't
have it." For Monday, the recommended internal line is: "Editing exists, but it's
*controlled* editing (find/replace that preserves citations and re-validates),
because a raw editor would break the trust guarantee that is the product's whole
point." If Dallas/Matt want a true rich-text editor, that's a roadmap decision to
make knowingly — flag it Monday, don't discover it live. *(Recorded here per the
'cite or cut / surface contradictions' rule; I did not invent a resolution.)*

## Appendix B — Things asserted in the meeting that I could NOT verify in code (flagged, not assumed)

- **"$3 a pop / $300 for 100 guides"** [00:00] — Dallas's verbal estimate. Not a
  measured per-guide cost in the code I read. Present as an estimate only.
- **Screenshots / image scraping into guides** [21:33] — discussed as a
  low-effort future add ("scrape and stuff and put that in"); I did not verify any
  screenshot-insertion feature exists. Treat as future, not built.
- **Audio / dictation ("microphone button," listen while driving)** [May-26
  35:37, 36:37] — floated as a cheap ANC-demo extra; no evidence in code I read.
  Do not imply it exists.
- **Skoolie/"Schooly" bot tie-in to the guide knowledge base** [22:28, May-26
  34:55] — described as the vision (install the bot on top of the library); I did
  not verify an integration. Roadmap, not built.
- **"Approved/grounded" labels a content manager sees** [06:25–06:48] — Rahul
  confirms this is the *content-manager* (Trainer) view, consistent with the
  Trainer/Customer toggle (`index.html:1360-1362`), but I did not trace the exact
  "approved/grounded" badge strings to a line; verify before claiming the wording
  on screen.
