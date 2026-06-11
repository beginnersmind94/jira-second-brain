# Story 004: Aging content nudge

**Epic:** [Content updates panel](EPIC.md)
**Status:** Done ✓ (demo)
**Type:** `aging`

## User story

> As Jaime, when a guide I've assigned to districts hasn't been PO-reviewed in 90+ days, I want a nudge so I can prompt the right PO to review it and ensure content is current.

## Acceptance criteria

- [ ] Panel surfaces `aging` events at the bottom of the feed (lowest urgency)
- [ ] Row shows: guide title, module, date of last PO review, number of districts affected
- [ ] "Nudge [PO name]" button is pre-addressed to the module's responsible PO (from `smes` map)
- [ ] Button styling is muted (`.btn-nudge`) — lower urgency than flagged/updated
- [ ] Clicking "Nudge [PO name]" sends a review reminder to the PO (demo: alert)

## Design decisions

- **90 days** is the default threshold; in production this could be configurable per module
- **Jaime's exposure, not abstract content age** — the signal is "you have N districts running a guide that's overdue for review", not "this guide is old"
- Jaime does not fix stale content. She routes. The nudge creates a task in the PO's queue.
- If the PO reviews + re-approves without changes, the aging event clears and no `updated` event fires

## Future: smarter staleness

Instead of calendar age alone, the staleness signal could trigger on:
- A Jira ticket shipping a change to the module after the guide was published (grounding drift)
- A pattern of district help requests mentioning the same guide
