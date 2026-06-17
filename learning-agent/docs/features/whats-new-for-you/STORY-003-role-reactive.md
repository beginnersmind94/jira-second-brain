# Story 003: Role-reactive re-fetch

**Status:** In progress
**Epic:** [What's New for You](EPIC.md)

## As a trainer previewing the learner experience
I want the "What's New for You" strip to update when I change the "Previewing as" role
so I can see what each role will see without reloading the page.

## Acceptance criteria

- [ ] AC1: Strip is empty/absent in trainer view (_viewMode !== 'customer')
- [ ] AC2: Flipping "Previewing as" dropdown triggers a re-fetch and re-render of the strip
- [ ] AC3: Strip shows only in customer view (customer-view chrome, safe to screen-share)
- [ ] AC4: Re-fetch is non-blocking; the rest of the home continues to render if the request fails

## Notes

- The strip must never show a "nothing to show" empty state — silent collapse (wrap.innerHTML = '') on zero items or non-customer view
- Re-fetch must use the new role from the dropdown, not a cached value
