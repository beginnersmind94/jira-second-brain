# STORY-001: Tab takeover + three-tier shelf

**Epic:** [What's Next for You](EPIC.md)
**Status:** Done ✓

## Story
As a **cashier who just finished training**, I want a single calm place that shows me what's
next — for my life and my career — so the completion moment feels like an investment in me, not a
dead end.

## Scope
The retired **Daily Practice** tab becomes **What's next**. It renders a data-driven shelf of
three visually distinct tiers (financial wellness · professional development · career credentials),
each with a pictographic icon, a short emotional framing line, and simple resource cards.

## Acceptance criteria
- [x] The "Practice" learner-nav tab is relabeled "What's next" and renders the shelf.
- [x] Daily Practice UI is removed (section markup, taker overlay, practice JS); no dead UI remains.
- [x] The shelf is rendered from `data/whats-next.json` via `loadWhatsNext()` — no hardcoded HTML content.
- [x] Three tiers render in order with distinct Isotype icons (`shelter` / `grow` / `horizon`)
      and distinct color variants (green / stamp / warn), via `isoIconHtml()`.
- [x] Header shows eyebrow + heading + subhead + the external-partner badge.
- [x] Mobile-first at 375px: cards stack to one column, no horizontal scroll, tap targets ≥44px.
- [x] All `.wnx-*` styling is token-based (dark-mode + reduced-motion safe).

## Notes
The internal view key stays `practice` (id `view-practice` / `tab-practice`) so the nav wiring,
`CUSTOMER_OK` guard, and mobile tab logic are untouched — only the label and content changed.
