# STORY-002: Link-out trust posture

**Epic:** [What's Next for You](EPIC.md)
**Status:** Done ✓

## Story
As the **PM responsible for trust**, I need this screen to be unmistakably a set of credited
external links — never reproduced vendor content and never an implied product capability — because
one over-claim kills credibility, and ICN/USDA content must stay link-out + credited.

## Acceptance criteria
- [x] Every resource opens via `<a href target="_blank" rel="noopener noreferrer">` to an external https URL.
- [x] No iframe, no API call, no embedded vendor content; the config carries no
      `content`/`html`/`body`/`embed` field (pinned by `test_whats_next.py` WN4).
- [x] The "Offered by external partners · not provided by CN Learning Studio" badge is present (WN3).
- [x] No resource URL points at our own product or localhost (WN4b).
- [x] `ask_district` appears on exactly the two cost-bearing items (SmartDollar, SNA); free
      resources never carry it (WN5) — product stays the pipe, not the payer.
- [x] Each card's link has a descriptive `aria-label` ending "— opens in a new tab".

## Notes
This screen makes **zero claims about our product**, so the grounding gate doesn't apply. The
honesty bar here is different: don't paint a guarantee we don't carry onto content we don't own.
The test enforces the link-out posture so a later edit can't quietly reproduce vendor content.
