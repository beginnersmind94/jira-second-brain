# Story 001: Newly approved content

**Epic:** [Content updates panel](EPIC.md)
**Status:** Done ✓
**Type:** `approved`

## User story

> As Jaime, when a PO approves a new guide, I want to see it in my Content updates panel so I can assign it to districts without having to check the Library manually.

## Acceptance criteria

- [ ] Panel shows `approved` events sorted by date (newest first)
- [ ] Each row shows: guide title, module name, approver name (from `smes` map), approval date
- [ ] "Assign" button opens the assignment modal
- [ ] Approver name is the module's responsible PO — not a generic "PM team"

## Notes

Approver name comes from `_DEMO.smes[module]`. In production this will be the actual PO who clicked approve in the workflow.
