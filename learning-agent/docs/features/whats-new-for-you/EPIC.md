# Epic: What's New for You — role-filtered learner freshness strip

**Status:** In progress
**Component:** Learn home · featured section
**Persona:** John Doe (Cashier) · Alex (Site Manager) · Dana (CN Director)
**Last updated:** 2026-06-14

## Problem statement

Learners land on the Learn home and see their in-progress hero track — but they have no signal
about new training that was just published and is relevant to their role. A cashier who just
finished onboarding doesn't know that a new Item Management guide dropped last week. A CN Director
doesn't know her compliance track was updated.

The home page is sticky: once the hero track is in progress, the learner's view barely changes
even as the content library grows.

## Solution

A "What's New for You" strip below the hero: ≤5 cards, role-filtered, freshness-ranked,
each provenance-badged and one tap from the lesson. Non-blocking (never delays first paint).
Re-fetches live when the "Previewing as" role changes.

Freshness basis: **real training publish dates** (tracks + approved guides), not Jira change
dates. The wiki corpus has zero incremental Jira changes since the Apr-20 bulk import — the
strip does not imply product changes that didn't happen. Copy says "New for you," not "New in
the product."

The wiki contributes **topic context chips** only (the Activity pulse themes from each module's
concept page): they tell the learner what the training is about, never raw wiki prose.

## Design decisions

- **Honest freshness:** freshness_basis = training_publish_date; _sources.jira_incremental_changes_since_bulk_import = 0 (always 0 until a real incremental sync happens)
- **Wiki as context, not content:** wiki prose never reaches the learner; only the artifact's own title/description + neutral theme chips
- **Provenance on every card:** originBadgeHtml() (sole emitter); "Why this?" tooltip shows "Published {date} · grounded in the {module} knowledge base"
- **Role isolation:** Cashier result is a subset of CN Director; no director-only content reaches a cashier
- **Trainer view: empty slot:** _viewMode !== 'customer' → wrap cleared; trainer never sees the strip (it is for learners)
- **Zero-item: silent collapse:** wrap.innerHTML = '' — the hero owns the primary job; the strip never shows a "nothing to show" empty state

## Trust rules (each has a test in eval/test_whats_new.py)

1. Only approved artifacts surface (T1)
2. SHOULD-NOT-OCCUR: cashier sees director-only content (T2)
3. Every item: valid origin + resolvable open ref (T3)
4. SHOULD-NOT-OCCUR: future/fabricated published_at (T4)
5. Honest _sources: jira_incremental = 0 (T5)
6. SHOULD-NOT-OCCUR: internal paths/ticket IDs in learner-facing strings (T6)

## User stories

- [STORY-001: Role-filtered freshness cards](STORY-001-role-filtered-cards.md)
- [STORY-002: Provenance and honest freshness](STORY-002-honest-provenance.md)
- [STORY-003: Role-reactive re-fetch](STORY-003-role-reactive.md)

## Implementation notes

- `whats_new.py` — `build_whats_new(role)` deterministic builder
- `demo_app.py` — `GET /api/whats-new` route
- `static/index.html` — `_renderWhatsNewStrip()`, `_buildWhatsNewHtml()`, `.wn-strip` CSS
- `eval/test_whats_new.py` — 6-test trust suite (T1–T6; SHOULD-NOT-OCCUR suffix on T2, T4, T6)
