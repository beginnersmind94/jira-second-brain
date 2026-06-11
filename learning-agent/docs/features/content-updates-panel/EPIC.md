# Epic: Content updates panel — subscribed content event feed

**Status:** In progress
**Component:** Home view · side column
**Persona:** Jaime (implementation manager / CS team)
**Last updated:** 2026-06-11

## Problem statement

Jaime manages district implementation. Her job starts *after* a PO approves a guide — she assigns it to districts and tracks their progress. Before this feature, her Home view had a "My day" personal to-do panel that gave her no signal about the content pipeline she depends on.

She had no way to know:
- when new guides were approved and ready to assign
- when a guide she'd already deployed to districts was revised by a PO
- when a downstream user flagged an issue with content she's running
- when guide content was aging past the point where it should be reviewed

## Solution

Replace "My day" with a **Content updates panel** — a subscribed event feed on content Jaime has assigned. Mental model: *assigning content = subscribing to it.* Any event on that content surfaces here automatically. She is a signal router, not a fixer; her action is always to assign, review, or route the issue to the right PO.

## Event types

| Type | Signal | Jaime's action |
|---|---|---|
| `approved` | PO approved a new guide — ready to assign | Assign → opens assignment modal |
| `updated` | PO revised + re-approved a guide Jaime has assigned | Review → opens guide in Library |
| `flagged` | Anyone flagged an issue with a guide Jaime has assigned | Notify [PO name] → routes to the module's responsible PO |
| `aging` | A guide Jaime has assigned hasn't been PO-reviewed in 90+ days | Nudge [PO name] → prompts the PO to review |

## Design decisions

- **Sorted by urgency:** `flagged` floats to top; `approved` and `updated` sorted by date desc; `aging` at bottom
- **PO name derived from `_DEMO.smes[module]`** — the system knows which PO owns each module; "Notify" buttons are pre-addressed
- **Flagged rows get amber highlight** — trust is the non-negotiable; a content quality event must be unmissable
- **Panel header badge turns red when flagged items exist** — reinforces urgency without a modal
- **Jaime does not approve content** — POs (PM team) are the approval gate; any design that surfaces an approval queue to Jaime is a wrong persona assignment

## User stories

- [STORY-001: Newly approved content](STORY-001-new-approvals.md)
- [STORY-002: Updated content notification](STORY-002-updated-content.md)
- [STORY-003: Flagged content routing](STORY-003-flagged-content.md)
- [STORY-004: Aging content nudge](STORY-004-aging-content.md)

## Implementation notes

- **`_DEMO.inbox`** — enriched with `type`, `note`, `flaggedBy`, `assignedDistricts` fields
- **CSS classes:** `.afeed-row.row-flagged`, `.afeed-ico.ico-{type}`, `.afeed-btn.btn-flag`, `.afeed-btn.btn-nudge`
- **`notifyPO(module, title, reason)`** — demo alert; production: creates a PO review task
- **`renderHome()`** — feed rendering is type-aware; each type has its own meta, note, and action button
- **Overflow:** shows 4 items, "View N more" opens the existing notifications drawer
