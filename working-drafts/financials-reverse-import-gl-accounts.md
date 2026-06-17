---
key: NXT-73326   # draft
summary: "FIN — Reverse Import: GL Accounts Import"
status: "Draft"
components: ["Financials"]
sprints: []
low_signal: false
---

# FIN — Reverse Import: GL Accounts Import

## Description

Adds **Reverse import** to GL Accounts Import rows on the Import & Export Log page.

Reverse is **always available** on a Done GL Accounts Import. If all imported accounts have zero posted activity, full reversal deletes everything. If some accounts have activity, partial reversal deletes only the zero-activity accounts — accounts with posted transactions stay.

### Full reversal (no activity on any account)

BL deletes the imported accounts, their site-level sub-accounts, categories, and all non-ledger dependencies (data point mappings, sub-account mappings, template rules). No journal entries are deleted because none exist. Status → Reversed.

The drawer summarizes the totals in the warning and itemizes **only** the account categories and their associated accounts, in a **paginated table** (Category / Account). The other deleted records (sub-accounts, mappings, template rules) are summarized in the warning, not listed.

If any imported accounts are mapped to data points, the drawer shows a pointer (no per-account list): *"Some of these accounts are mapped to data points. After reversing, go to Financials > Configuration > Account Mapping to see which data points are missing a GL account, re-map them to accounts from your new import, and resume posting."*

If an imported category contains non-imported accounts (manually created after the fact), the reverse is **blocked** until those accounts are reassigned: the drawer shows the cleanup list and the message *"{Count} accounts in this category were created outside this import and need to be moved to another category first,"* and the reason field + Reverse button are hidden until it's resolved.

### Partial reversal (some accounts have activity)

The drawer itemizes the accounts in the same Category / Account table with a **Status** column (Delete = zero activity / Keep = has posted transactions); the warning summarizes the split. On confirm, BL deletes only the zero-activity accounts and their dependencies. Accounts with activity are not touched. A category is deleted only if all its accounts were deleted in the reversal; if any account in the category was kept, the category stays. Status → Partially Reversed.

After partial reversal, re-importing the correct file recreates the deleted accounts via create/update on Account Code (per NXT-69421). No duplicate conflict — the kept accounts are updated in place.

The View details drawer shows which accounts were deleted and which were kept, with guidance: *"To fix account details, re-import the correct file, then check Configuration for any mappings or rules that need to be set up again. To correct posted entries, use a manual journal entry. For larger changes, contact Support."*

### Confirmation (side-drawer)

Reverse opens in a **side-drawer** (same pattern as View details), with an entity sub-header (import name, status, type/category tags), then:

- **Full reversal warning:** *"This will permanently delete {AccountCount} accounts across {CategoryCount} categories and the records tied to them. This cannot be undone."*
- **Partial reversal warning:** *"{DeleteCount} accounts with no posted activity will be permanently deleted. {KeepCount} accounts with posted transactions will be kept. This cannot be undone."*
- The only itemized list is the **paginated Category / Account table** (with a Status column for partial).
- **Reason for reversing** (mandatory comment, min 10 chars) + the **Reverse import** button appear **only when the reverse can proceed** (no blockers). When blocked, the drawer shows the cleanup items + a footer note ("Reverse is blocked until the above is resolved") and a Close button — no reason field, no Reverse button. Otherwise: Cancel (default) / Reverse import (destructive).

On confirm, Status → Reversal In Progress → Reversed or Partially Reversed. On failure, Status → Reverse Failed with a Retry button.

### Config page impact

After reversal, the GL Configurations page reflects the deletion across all six tabs. System Accounts and Mapped GL Accounts tabs re-surface warnings for unmapped system accounts and data points. System Rules that referenced deleted accounts are flagged as broken with posting blocked until remapped. Imported GL Accounts and Account Categories tabs reflect the current state — deleted records gone, kept records remain.

## Acceptance Criteria

**AC1 — Reverse is always available.** Reverse import appears on any Done GL Accounts Import. It is never hidden based on activity. If all imported accounts have zero activity, full reversal. If some have activity, partial reversal — the zero-activity accounts are deleted, the accounts with activity stay.

**AC2 — Reverse drawer: full reversal.** When all imported accounts have zero activity, the side-drawer shows the entity sub-header, the warning ("This will permanently delete {AccountCount} accounts across {CategoryCount} categories and the records tied to them. This cannot be undone."), and the **only** itemized list — a **paginated Category / Account table** of the account categories and their accounts. The other deleted records (sub-accounts, mappings, template rules) are summarized in the warning, not listed. If any accounts are mapped to data points, a pointer (no per-account list) reads: "Some of these accounts are mapped to data points. After reversing, go to Financials > Configuration > Account Mapping to see which data points are missing a GL account, re-map them to accounts from your new import, and resume posting." Mandatory comment (min 10 chars) + Reverse import button (Cancel default).

**AC3 — Reverse drawer: partial reversal.** When some imported accounts have posted activity, the same Category / Account table includes a **Status** column (Delete for zero-activity accounts, Keep for accounts with transactions); the warning summarizes the split: "{DeleteCount} accounts with no posted activity will be permanently deleted. {KeepCount} accounts with posted transactions will be kept. This cannot be undone." Mandatory comment (min 10 chars) + Reverse import button (Cancel default).

**AC4 — Hard delete on confirm.** On confirm, Status → Reversal In Progress. BL cascade-deletes in order: data point mappings, GL entry template rules, sub-account mappings, site-level sub-accounts, then the parent accounts and categories — only for accounts with zero activity. Accounts with posted activity and their dependencies are not touched. A category is deleted only if all its accounts were deleted; if any account in the category was kept, the category stays. DE status updated to Reversed (full) or Partially Reversed (partial).

**AC5 — Atomic.** If any part fails, nothing is deleted. Status → Reverse Failed. Retry button appears.

**AC6 — Reverse Failed: Retry.** When Status = Reverse Failed, a Retry button appears. Clicking Retry re-executes without re-showing the confirmation.

**AC7 — Non-imported accounts block the reverse.** If an imported category being deleted contains accounts that were not part of the import, the reverse is **blocked** until those accounts are reassigned. The drawer shows "{Count} accounts in this category were created outside this import and need to be moved to another category first" with the list, a footer note ("Reverse is blocked until the above is resolved"), and **no reason field / no Reverse button** until it is resolved.

**AC8 — Re-import after partial reversal.** After a partial reversal, re-importing the correct file recreates the deleted accounts via create/update on Account Code (per NXT-69421). No duplicate conflict. The kept accounts are updated in place.

**AC9 — Post-reversal guidance.** After a partial reversal, the View details drawer shows which accounts were deleted and which were kept. For the kept accounts: "To fix account details, re-import the correct file, then check Configuration for any mappings or rules that need to be set up again. To correct posted entries, use a manual journal entry. For larger changes, contact Support."

**AC10 — System Accounts tab: warnings re-surface.** After reversal, if any deleted accounts were mapped as system-required accounts, those warnings re-appear on the System Accounts tab.

**AC11 — Mapped GL Accounts tab: unmapped data points.** After reversal, data points that referenced deleted accounts show as unmapped. Posting rules for those data points will not fire until remapped.

**AC12 — System Rules tab: broken rules flagged.** After reversal, any System Rule that referenced a deleted account is flagged with a validation error. Posting for that rule is blocked until the user assigns a valid account.

**AC13 — Imported GL Accounts and Account Categories tabs reflect current state.** After reversal, deleted accounts and categories no longer appear. Kept accounts remain.

**AC14 — Status after reversal.** Full reversal: Status = Reversed. Partial reversal: Status = Partially Reversed. Both remain visible in the grid with comment, user, timestamp. View details still works.

**AC15 — Reverse is permission-gated.** Users lacking the Reverse Import permission do not see Reverse import (hidden, not disabled).

**AC16 — Reason field is gated.** The "Reason for reversing" field and the Reverse import button appear only when the reverse can proceed (no blockers). When blocked (e.g., non-imported accounts in a category), they are hidden and the drawer shows a Close button with the blocking reason.
