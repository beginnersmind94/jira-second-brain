# Story 002: Provenance and honest freshness

**Status:** In progress
**Epic:** [What's New for You](EPIC.md)

## As a learner
I want to know where each training item came from and when it was published
so I can trust the content and understand what is genuinely new.

## Acceptance criteria

- [ ] AC1: Every card has a provenance badge (originBadgeHtml)
- [ ] AC2: "Why this?" affordance shows: "Published {date} · grounded in the {module} knowledge base"
- [ ] AC3: freshness_label is one of: "New" (≤30d) / "Recently added" (≤90d) / "In library"
- [ ] AC4: _sources.jira_incremental_changes_since_bulk_import == 0 in every response
- [ ] AC5: No raw wiki paths, .md paths, or NXT- ticket IDs in any learner-facing string

## Notes

- "Every claim cited" badge text must NOT appear on human_authored or outside_vendor cards
- Wiki prose must never be surfaced directly — only the artifact's own title/summary
- Trust tests: T3 (provenance complete), T4 (no future dates), T5 (honest sources), T6 (no internal IDs) in eval/test_whats_new.py
