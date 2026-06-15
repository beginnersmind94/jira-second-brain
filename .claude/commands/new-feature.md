# /new-feature <slug> <"Epic title">

Create the epic and linked user stories for a new feature, then wire up the standing tracking rule so
they stay updated as code changes.

**Stories are written to the Story Spec Standard:** [`docs/STORY-SPEC-STANDARD.md`](../../docs/STORY-SPEC-STANDARD.md).
Read it first. The templates below are that standard in scaffold form — do not fall back to a
one-line user story + free-text checklist (that shape is what lets façade through). Every story
carries all seven parts and is held to the Definition of Done before it is marked `Done ✓`.

> This command lives at the jira-brain root and applies to every sub-project (`learning-agent/`,
> FIN/Jira work, etc.). Use the right `docs/features/` path for the project the feature belongs to —
> e.g. `learning-agent/docs/features/<slug>/`.

## Steps

### 1. Create the docs directory
```
<project>/docs/features/<slug>/
```

### 2. Write EPIC.md
```markdown
# Epic: <title>

**Status:** In progress
**Component:** <view or area>   ·   **Persona:** <primary user>   ·   **Last updated:** <YYYY-MM-DD>
**Depends on:** <ticket ids / upstream work, or "nothing">

## Problem statement
<What the persona can't do today. Concrete, not aspirational.>

## Solution
<What the feature does and the mental model. One paragraph.>

## Scope
**In scope:** <the vertical slice this epic delivers>
**Out of scope:** <what a reader might assume is included but isn't — fences gold-plating>

## Design decisions
- <decision → rationale>

## User stories
- [ ] [STORY-001: …](STORY-001-….md)
- …

## Implementation notes
- Key files / functions / data fields changed (filled as code lands)
```

### 3. Write one STORY-NNN.md per behavior cluster — the seven-part contract
```markdown
# Story NNN: <title>

**Epic:** [<Epic title>](EPIC.md)
**Status:** Pending | In progress | Done ✓
**Points:** <n>   ·   **Persona:** <user>   ·   **Depends on:** <ids, or "nothing">

## TL;DR
<2–3 sentences: what ships and the one thing that makes it real.>

## Scope
**In scope:** <…>
**Out of scope:** <… — mandatory; "N/A — <reason>" if truly none>

## Requirements
1.1 <exact behavior — name exact fields / columns / formats / mappings>
1.2 <…>           <!-- use [TO VERIFY at <when>] for anything not yet known; never guess -->
2.1 <…>

## Edge / Empty / Error states
| Case | Behavior |
|---|---|
| <empty input> | <exact behavior> |
| <max scale / boundary> | <…> |
| <user did the dangerous thing> | <…> |

## Defaults
- <value chosen when the user specifies nothing>

## Acceptance criteria  (Given / When / Then — each an executable test on real data)
- [ ] **AC1** — *Given* <real precondition>, *When* <action>, *Then* <exact observable outcome, with a concrete example value>.
- [ ] **AC2** — …

## Future option (deferred — nothing built now is thrown away)
<what we are deliberately not building yet, and why it's additive later>

## Notes
<production-vs-demo delta; any spike with its expiry>
```

### 4. Cross-link everything
- Each STORY links back to EPIC.md; EPIC.md lists all stories.
- If a GitHub/Jira issue id is known, add `**Tracking:** <id>` to each header.

### 5. After each code change that affects this feature
- Update the story's `**Status:**`.
- Check off an AC **only with a one-line evidence note** (command run / observed output / test name).
  A bare `- [x]` with no evidence is not done.
- Add implementation notes to EPIC.md.
- Mark a story `Done ✓` **only when it passes the full Definition of Done** in the standard:
  every AC demonstrated green on real data, out-of-scope untouched, every edge row exercised,
  cross-surface consistency, machine-checkable ACs tested, no new façade.

## Standing rule
**Every new feature gets an epic + stories before or immediately after the first working code lands.
No exception.** Tracking docs are part of the feature and are updated in the same commit as the code
they describe. Stories are written to — and closed against — [`docs/STORY-SPEC-STANDARD.md`](../../docs/STORY-SPEC-STANDARD.md).
