# Story 002: Updated content notification

**Epic:** [Content updates panel](EPIC.md)
**Status:** Done ✓
**Type:** `updated`

## User story

> As Jaime, when a guide I've assigned to districts is edited and re-approved by a PO, I want to see the update so I can decide if districts need to re-train.

## Acceptance criteria

- [ ] Panel shows `updated` events when a guide Jaime has assigned is re-approved after an edit
- [ ] Row shows: guide title, module, PO who updated it, update date
- [ ] Row shows a one-line note summarising what changed (e.g. "Step 3 revised")
- [ ] "Review" button navigates to the guide in the Library (filtered view)
- [ ] Jaime can decide: keep the assignment running, or prompt districts to re-train

## Notes

The edit → re-approve flow goes through `revise.py` + `demo_app.revise_resource`. The `updated` event should be triggered by the same approval gate that triggers `approved` events, but on a guide with an existing assignment.
