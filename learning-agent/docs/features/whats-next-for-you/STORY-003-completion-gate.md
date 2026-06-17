# STORY-003: Completion gate + entry points

**Epic:** [What's Next for You](EPIC.md)
**Status:** Done ✓

## Story
As a **cashier**, I want the "what's next" offer to appear when I've *earned* it — after I finish
my Summer Refresher — reachable from where I'd naturally look (my home, my certificate), so it
feels like a reward, not a banner ad.

## Acceptance criteria
- [x] Completion is read from existing state: `GET /api/tracks/{id}` → `progress.certified`
      (no new completion/assessment logic; pure UI over existing state).
- [x] The gating track is the **Cashier Summer Refresher** (`track-20260614-summer-cashier`),
      configured in `whats-next.json` `gate` — not hardcoded in the renderer.
- [x] Learn-home entry card (`_renderRefresherCard`) renders **only** when the gating track is
      certified for the current learner; before that the slot is empty (no teaser).
- [x] The certificate screen (real cert + façade fallback) shows a "What's next for you →" CTA
      that routes to the shelf via `goToWhatsNext()`.
- [x] The tab's header framing is completion-aware and honest: neutral "BEYOND THIS TRAINING"
      preview before certification, celebratory "TRACK COMPLETE · …" after — never a false
      completion claim.

## Notes
Because the gate is honest, the demo cashier sees the celebratory state only after actually
completing the Summer Refresher. To demo the post-completion state, finish that track for
`john-cashier`; the preview state is visible on the tab at any time.
