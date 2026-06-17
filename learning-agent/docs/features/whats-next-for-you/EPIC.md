# Epic: What's Next for You — post-completion benefits shelf

**Status:** In progress
**Component:** Learner view · the (former) Practice tab + Learn home + Certificate
**Persona:** John Doe (Cashier) — the $13/hr learner who just passed a compliance assessment
**Last updated:** 2026-06-15

> Distinct from **What's *New* for You** (`whats-new-for-you/`, the role-filtered freshness
> strip of newly-published *internal* training). This is **What's *Next***: a post-completion
> page of curated *external* resources. Code prefix `wnx` vs `wn`; route `/api/whats-next`
> vs `/api/whats-new`. Don't conflate them.

## Problem statement

When a learner finishes their assigned track and passes the assessment, the product goes quiet.
The system has just asked a cafeteria cashier to prove competence on food safety and compliance —
and then offers nothing back. The completion moment is the one time the learner is paying full
attention and feeling capable; spending it on a dead-end ("you're done, bye") wastes the only
moment the district gets to say "we see you as a whole person."

## Solution

A "What's Next for You" screen — a calm, dignified, on-brand page of **external links** organized
into three tiers, shown after completion:

1. **Build confidence at home** — financial wellness (SmartDollar). Dignity-first, never "you're bad with money."
2. **Grow in school nutrition** — USDA / ICN / SNA professional development (hours they need anyway, framed as growth).
3. **Build what comes next** — Google / IBM / Meta career credentials + Coursera financial aid (the hope tier).

**The links are the entire feature.** No vendor integration, no embedded content, no API calls,
no content to maintain. PrimeroEdge / CN Learning Studio is the *trigger and the pipe, not the
provider*. If a partner changes a URL, someone edits one line in `data/whats-next.json`.

### Placement decision (differs from the original brief §5)
The original brief specced a brand-new screen reachable only post-completion. The PM chose to
**take over the retired Daily Practice tab** instead ("practice only makes sense for self-directed
learning"). So:
- The **What's next** tab is always in the learner nav (it replaced Practice; Daily Practice
  retired — UI removed, JS deleted; the `/api/users/{uid}/practice*` server routes are left inert).
- The tab content is **completion-aware but never dishonest**: before the gating track is
  certified it shows the shelf under a neutral "BEYOND THIS TRAINING" eyebrow + a "when you finish"
  subhead; after certification it upgrades to "TRACK COMPLETE · Cashier Summer Refresher" + the
  "you finished your training" subhead. No screen ever falsely claims completion.
- The **Learn-home entry card** and the **celebratory framing** are gated specifically on
  completing the **Cashier Summer Refresher** track (PM's explicit choice) — earned, never a teaser.
- The **certificate screen** carries a "What's next for you →" CTA (the perfect moment).

## Design decisions

- **Trust = link-out, never reproduce.** Every resource is `<a target="_blank" rel="noopener noreferrer">`.
  No `content`/`html`/`embed` field is permitted in the config (pinned by `test_whats_next.py`).
  This honours the moat: ICN/USDA content is credited and linked, never shown inline.
- **No product claims → nothing to ground.** The shelf makes zero claims about *our* product, so
  the grounding gate doesn't apply; instead the honesty bar is "don't paint a guarantee we don't
  carry." The partner badge ("Offered by external partners · not provided by CN Learning Studio")
  is load-bearing and asserted in the test.
- **Data-driven from day one.** `data/whats-next.json` is the single source of truth; the renderer
  reads it; a district can later customise which resources appear by editing one file.
- **"Ask your district" only on cost items.** SmartDollar + SNA carry the note (keeps the product
  as the pipe, not the payer). Free resources (USDA / ICN / Coursera aid) never add that friction.
- **Isotype pictograms, reused not reinvented.** Three new icons (`shelter`, `grow`, `horizon`)
  added to the existing `_ISO_ICONS` registry; emitted only via `isoIconHtml()`. Tier colors map
  to the disciplined palette: green (primary/grounded) · stamp-blue (official/credential) ·
  marigold (the single aspirational "win" moment, used once).
- **Token-only styling.** Every `.wnx-*` rule uses CSS variables, so dark mode + reduced-motion
  come for free.

## Trust rules (each has a test in eval/test_whats_next.py)

1. Three tiers, in the brief's order (WN2)
2. Header credits external partners + disclaims provider (WN3)
3. Every resource is an external https link-out; no content-reproduction keys (WN4 / WN4b)
4. `ask_district` is exactly the two cost items; free items never ask (WN5)
5. Distinct, valid pictographic icons + variants per tier (WN6)
6. Every brief-named resource present at the right domain; SmartDollar marks Spanish (WN7)
7. Live `/api/whats-next` matches the config (WN8, skips if server down)

## User stories

- [STORY-001: Tab takeover + three-tier shelf](STORY-001-tab-takeover-shelf.md)
- [STORY-002: Link-out trust posture](STORY-002-linkout-trust.md)
- [STORY-003: Completion gate + entry points](STORY-003-completion-gate.md)

## Implementation notes

- `data/whats-next.json` — the shelf config (single source of truth).
- `demo_app.py` — `GET /api/whats-next` route (pure config read; no LLM).
- `static/index.html`:
  - `#view-practice` repurposed → `#whatsnext-body` container; tab label "Practice" → "What's next".
  - `loadWhatsNext()` / `_wnxShelfHtml()` / `_wnxHeaderHtml()` / `_wnxTierHtml()` /
    `_wnxResourceHtml()` / `_wnxGetConfig()` / `_wnxIsCertified()` / `goToWhatsNext()`.
  - `_renderRefresherCard()` repurposed → the Summer-Refresher-gated Learn-home entry card.
  - `_ISO_ICONS` / `_ISO_LABELS` extended (`shelter`, `grow`, `horizon`); `.wnx-*` CSS block.
  - showView('practice') rewired from `loadPractice()` → `loadWhatsNext()`.
  - Certificate footers (real + façade ×2) gained the "What's next for you →" CTA.
- `eval/test_whats_next.py` — deterministic config-integrity + trust suite (WN1–WN8).
- **Removed:** the Daily Practice UI (section markup, taker overlay, ~440 lines of practice JS).
