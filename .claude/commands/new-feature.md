# /new-feature <slug> <"Epic title">

Create the GitHub epic and linked user stories for a new Learning Studio feature, then wire up the standing tracking rule so they stay updated as code changes.

## Steps

### 1. Create the docs directory
```
learning-agent/docs/features/<slug>/
```

### 2. Write EPIC.md
Template:
```markdown
# Epic: <title>

**Status:** In progress
**Component:** <view or area>
**Persona:** <primary user>
**Last updated:** <YYYY-MM-DD>

## Problem statement
<What Jaime / the learner / the PO can't do today>

## Solution
<What the feature does and the mental model>

## Event types / key behaviours
| … | … | … |

## Design decisions
- bullet list

## User stories
- [STORY-001: …](STORY-001-….md)
- …

## Implementation notes
- Key files changed
- New demo data fields
- New CSS classes
- New JS functions
```

### 3. Write one STORY-NNN.md per acceptance-criterion cluster
Template:
```markdown
# Story NNN: <title>

**Epic:** [<Epic title>](EPIC.md)
**Status:** Pending | In progress | Done ✓
**Type:** <feature area>

## User story
> As <persona>, <when condition>, I want <action> so that <outcome>.

## Acceptance criteria
- [ ] …

## Notes
<Edge cases, deferred items, production vs demo delta>
```

### 4. Cross-link everything
- Each STORY file links back to EPIC.md
- EPIC.md lists all story files with relative links
- If a GitHub issue number is known, add `**GitHub:** #NNN` to each file's header

### 5. After each code change that affects this feature
- Update the relevant story's `**Status:**` field
- Check off acceptance criteria that are now met
- Add implementation notes to EPIC.md (new classes, functions, data fields)
- If a story's AC is fully checked off, mark it `Done ✓`

## Standing rule
**Every new feature in `learning-agent/` gets an epic + stories before or immediately after the first working code lands. No exception.** Tracking docs are part of the feature, not optional cleanup. Update them in the same commit as the code they describe.
