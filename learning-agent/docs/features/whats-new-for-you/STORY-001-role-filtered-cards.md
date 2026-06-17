# Story 001: Role-filtered freshness cards

**Status:** In progress
**Epic:** [What's New for You](EPIC.md)

## As a learner (Cashier / Site Manager / CN Director)
I want to see newly published training relevant to my role on my Learn home
so I can quickly discover and start new content without having to browse.

## Acceptance criteria

- [ ] AC1: Cards appear on Learn home in customer view for all three learner roles
- [ ] AC2: Each card links to an approved, published artifact (track or guide)
- [ ] AC3: A role sees only content whose role_tags includes their role, or empty/"All staff"
- [ ] AC4: Cards are sorted newest-first by real published_at
- [ ] AC5: Maximum 5 cards shown; strip collapses silently when 0 items qualify
- [ ] AC6: Each card shows: freshness_label chip, title, provenance badge, ≤3 topic chips

## Notes

- Demo users: john-cashier (Cashier), dana-director (CN Director)
- Provenance badge via originBadgeHtml() only — no hardcoded badge text
- Trust test: T1 (approved items only) and T2 (role isolation) in eval/test_whats_new.py
