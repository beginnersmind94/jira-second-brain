# Story 003: Flagged content routing

**Epic:** [Content updates panel](EPIC.md)
**Status:** Done ✓ (demo) · Pending (production feedback loop)
**Type:** `flagged`

## User story

> As Jaime, when anyone flags an issue with a guide I've assigned, I want to be notified with context so I can forward the issue to the right PO immediately.

## Acceptance criteria

- [ ] Panel surfaces `flagged` events at the top of the feed (above all other types)
- [ ] Flagged rows have amber background highlight — unmissable
- [ ] Panel header badge turns red when flagged items exist, shows count
- [ ] Row shows: who flagged it, what they said (one-line note), date
- [ ] "Notify [PO name]" button is pre-addressed to the module's responsible PO (from `smes` map)
- [ ] Clicking "Notify [PO name]" routes the issue to the PO's review queue (demo: alert)
- [ ] Jaime is a **signal router** — she does not fix content herself; the button action is always "tell the right person"

## Source of flags (current)

In V1 demo: seeded in `_DEMO.inbox` as `type:'flagged'`.

Production priority order:
1. **Cross-trainer flag** — another trainer at Cybersoft flags a guide they're also using (lowest friction, data already connected)
2. **PO revision** — PO edits a guide post-approval; the change itself is the flag that prior assignees should re-verify
3. **District admin feedback** — Dana (CN Director) or site manager flags an issue via a guide feedback widget (requires learner-side feedback loop — V1.5)
4. **Learner feedback** — cashier/staff member reports confusion in a quiz or lesson (V2)

## Trust note

This story directly protects the trust non-negotiable. One visible AI mistake kills trust. A flagged event on content Jaime has deployed is the highest-urgency signal in the panel — it must never be buried below fold.
