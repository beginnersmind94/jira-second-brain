---
key: NXT-XXXXX   # draft — assign on Jira create
summary: "FIN — Import & Export Log with Reverse Import (GL Accounts Import)"
status: "Draft"
components: ["Financials"]
sprints: []
low_signal: false
---

# FIN — Import & Export Log with Reverse Import

## Description

As a district finance user, I want to see — without leaving Financials — a log of every import, export, and report download I have run, with the same monitoring detail System's Import Monitor provides, and a way to reverse an import I ran by mistake.

## TL;DR

New page under Financials > Configuration: **Import & Export Log**. One unified grid showing imports, reports (report downloads), and exports (configured export jobs — none exist yet). Category pill: All / Imports / Exports / Reports. Import rows pull from Import Monitor. Report rows pull from Document Center and Power BI export events. The Exports pill is present from day one but empty until configured exports are built.

**Reverse is a hard delete.** It permanently removes the import and every record it created, so the system returns to its pre-import state as if the import never happened. This story covers Reverse for **GL Accounts Import** — the only Financials import type that exists today.

**Reverse is entirely a Financials operation.** BL deletes the Financials-owned records. The Import Monitor row in DE is only updated to Status = Reversed. DE's log data is unaffected.

This page is a read-only log with one action (Reverse on imports). Import creation still happens in System. Report generation still happens from each report page.

**Why this matters:** Today, GL Accounts Import redirects the user to System and leaves them there (NXT-69421). Report downloads land in Document Center or are exported from Power BI. Finance users have no centralized view within Financials. This page eliminates the module hop.

## Scope

**In scope:** Import & Export Log page under Financials > Configuration. Unified grid of Financials imports, report downloads, and (future) configured exports. Four-way Category pill. Reverse import for GL Accounts Import (hard delete, cascade). View details side drawer. Download on report rows. Page header with deep-links to System Import Monitor and Export Monitor. Filterable, searchable, sortable, paginated.

**Out of scope:** Reverse for OB Import (NXT-73303) and Payroll Import (NXT-73304) — those import types are not yet developed. Creating new imports, exports, or reports from this page. Changes to System Import/Export Monitor or Document Center. Reversing or deleting a report or export.

## Requirements

### 1) Page and Navigation

1.1 Add to Financials > Configuration: Import & Export Log.

1.2 Page header copy:

> **Import & Export Log**
>
> All your Financials imports and exports in one place. View a run's summary, download a report, or reverse an import. For full run logs, open [Import Monitor]({deep-link, filtered to module = Financials, new tab}) or [Export Monitor]({deep-link, Financials report types pre-selected, new tab}).

1.3 Roles with access: Director, Central Office, SchoolCafe Admin. Customer/Technical Support always full access. Finance Coordinator: read-only (can view, cannot reverse).

### 2) Unified Activity Grid

2.1 One grid combining import, report, and export rows.

2.2 **Data sources and categories.**

**Imports (Category = Import):** from Import Monitor, filtered to Financials import types. Currently only GL Accounts Import exists. As additional Financials import types are developed and configured, their rows will appear automatically.

**Reports (Category = Report):** report downloads — files generated when a user runs a Financials report. These come from two sources:
- Document Center reports (P&L, Trial Balance, Balance Sheet): row appears when the report is generated and the file lands in Document Center.
- Power BI reports (GL Report, Journal Report): row appears when the user clicks Export in Power BI (not Generate). The download link is in the same format the user selected in Power BI (e.g., PDF, Excel, CSV).

**Exports (Category = Export):** configured export jobs (like configured imports in the System FILES tab). None exist yet. The Exports pill is present from day one but shows no rows until configured exports are built in a future story.

2.3 Columns: Name, Category (Import / Export / Report pill), Type, Date, User, Status, Actions.

**Type column:**
- Import rows: the Import Type name (e.g., "GL Accounts Import").
- Report rows: the Report name (e.g., "P&L Report", "GL Report", "Trial Balance").
- Export rows (future): the configured export name.

**Status column:** Read-only badge.

| Category | Status values |
|---|---|
| Import | Done, Error, In Progress, Reversal In Progress, Reversed |
| Export (future) | Done, Error, In Progress |
| Report | Done |

Default sort: Date descending. All rows interleave by date.

2.4 Report Types: GL Report, Journal Report, P&L Report, Trial Balance, Balance Sheet.

2.5 Category filter (dropdown **above the grid**): All (default) / Imports / Exports / Reports.

2.6 Filters. **Above the grid** (toolbar): Category, Type (cascades — shows Import Type names for Imports, Report names for Reports, configured export names for Exports), Status, and Date. Date options: **Last 24 hours**, **Last 30 days**, **Custom range** (date picker for the range). **In the grid** (Kendo): inline **search** on the text columns (Name, User) and **sortable** columns. Standard pagination.

2.7 Empty state: "No import or export activity yet."

### 3) Actions by Row Type

3.1 **Import rows — View details.** Kebab menu. Opens a side drawer:
- Drawer title: Run details — {ImportName}
- Summary stats (read from Import Monitor): Total Records, Added, Updated, Processed, Exceptions, Status, Start, End.
- Deep-link: "Open full log in System ↗" — opens Import Monitor detail view in new tab. Tooltip: "Opens the full import log in System > Import Monitor." Hidden if user lacks System access.
- Disabled while running or no log data.

3.2 **Import rows — Reverse import.** Kebab menu. Only available on GL Accounts Import in this story. See §4.

3.3 **Report rows — Download.** Re-downloads the file. Document Center reports from Document Center. Power BI reports in the format selected at export time.

3.4 **Report rows — no View details, no Reverse.**

3.5 **Export rows (future) — actions TBD** when configured exports are built.

### 4) Reverse Import (GL Accounts Import)

4.1 Reverse import appears on GL Accounts Import rows when Status = Done and not already reversed or reversal in progress.

4.2 GL Accounts Import is never blocked. No gates, no dependency checks. The confirmation dialog is the only safety net.

4.3 **Confirmation dialog. No post-confirm undo.**
- Import name, count of accounts/categories, full list of everything that will be deleted (accounts, categories, and all records built on top).
- Warning: *"This will permanently delete {AccountCount} accounts, {CategoryCount} categories, and all records listed above. This cannot be undone. If you've exported this data to your ERP, you'll need to reverse it there — Financials does not update your ERP."*
- Mandatory comment (min 10 chars).
- Buttons: Cancel (default focus) / Reverse import (destructive).

4.4 On confirm: Status immediately changes to Reversal In Progress. BL executes the hard delete (§5). View details and Reverse import are disabled while Reversal In Progress.

4.5 On success: Status changes to Reversed. Row stays visible. Comment, user, timestamp recorded. View details still works.

4.6 On failure: BL rolls back, Status returns to Done. Error surfaced.

### 5) Reverse Import: Business Logic (GL Accounts Import)

**Ownership boundary:** Reverse is entirely a Financials/BL operation. BL deletes Financials-owned records. The only interaction with DE is updating the Import Monitor row status. DE's log data is not touched.

5.1 BL receives the GL Accounts Import ID, reversal reason (comment), authenticated user.
5.2 BL identifies all accounts and categories created by the import.
5.3 BL identifies all records built on top: journal entries, sub-account mappings, GL entry template rules, and any other Financials records referencing the imported accounts.
5.4 Concurrent lock.
5.5 Hard delete (cascade). BL removes all dependent records first, then accounts and categories. Chart of Accounts returns to its pre-import state.
5.6 If the cascade deleted ledger entries, rollup recalculation runs for affected fiscal periods.
5.7 DE status update. BL marks the Import Monitor row as Reversed. Cross-service atomicity deferred to tech lead.
5.8 Atomic: all-or-nothing.
5.9 Audit trail. The reversed-import row (Status = Reversed, comment, user, timestamp), the DE log tabs (via View details deep-link), and the BL reverse-action log together constitute the audit record.

### 6) Permissions

6.1 View page: Director, Central Office, SchoolCafe Admin, Finance Coordinator. Customer/Technical Support full access.
6.2 Reverse: dedicated role permission (name TBD — resolve before exit from refinement), separate from import permission. Director, Central Office, SchoolCafe Admin eligible. Finance Coordinator cannot reverse.
6.3 Users without reverse permission: Reverse import hidden (not disabled).

## Linked Stories

- NXT-73303 — FIN — Reverse Import: Opening Balance Import
- NXT-73304 — FIN — Reverse Import: Payroll Import

## Acceptance Criteria

**AC1 — Page access.** Given a user with Financials access, when they navigate to Financials > Configuration > Import & Export Log, they see a single unified grid of import, export, and report activity.

**AC2 — Grid shows only Financials activity.** The grid shows Financials imports (from Import Monitor), Financials report downloads (from Document Center and Power BI), and Financials configured exports (none exist yet — Exports pill is present but empty). Currently the only configured import type is GL Accounts Import. When additional types are configured, their rows appear automatically.

**AC3 — Columns and Status.** Grid shows Name, Category (Import/Export/Report pill), Type, Date, User, Status, Actions. Status is a read-only badge. Import values: Done, Error, In Progress, Reversal In Progress, Reversed. Export values (future): Done, Error, In Progress. Report values: Done. Default sort: Date descending.

**AC4 — Rows interleave by date.** When Category = All, import, export, and report rows interleave by date.

**AC5 — Category filter.** Above-grid dropdown with four options: All (default), Imports, Exports, Reports. Exports is present but shows no rows until configured exports are built.

**AC6 — Type filter cascades.** When Category = Imports, Type shows Import Type names. When Category = Reports, Type shows Report names. When Category = Exports, Type shows configured export types (none yet). When Category = All, shows all.

**AC6a — Date filter presets.** The Date filter (above grid) offers Last 24 hours, Last 30 days, and Custom range. Selecting Custom range reveals a From/To date picker that bounds the rows shown.

**AC7 — Search.** Free-text search filters rows by Name, Type, or User.

**AC8 — Import row actions.** Import rows show a kebab menu with View details and Reverse import (conditional).

**AC9 — Report row actions.** Report rows show Download. No View details or Reverse.

**AC10 — Page header with deep-links.** Page header includes inline links to Import Monitor (pre-filtered to module = Financials, new tab) and Export Monitor (pre-filtered to Financials report types, new tab).

**AC11 — View details side drawer.** View details opens a side drawer titled "Run details — {ImportName}" with summary stats from Import Monitor and an "Open full log in System" deep-link (new tab). Deep-link hidden if user lacks System access. Disabled while running or no data.

**AC12 — Report event: Document Center.** For reports that go to Document Center (P&L, Trial Balance, Balance Sheet), a report row appears when the report is generated. Download retrieves the file from Document Center. Status = Done.

**AC13 — Report event: Power BI.** For Power BI reports (GL Report, Journal Report), a report row appears when the user clicks Export in Power BI (not Generate). Download link matches the format selected in Power BI. Status = Done.

**AC14 — GL Accounts Import: always reversible.** Reverse import is always available on a Done GL Accounts Import. Never blocked. Confirmation shows full deletion scope.

**AC15 — GL Accounts confirmation dialog.** Dialog shows import name, account/category counts, full list of everything that will be deleted. Warning per §4.3. Mandatory comment (min 10 chars). Buttons: Cancel (default) / Reverse import (destructive).

**AC16 — Reversal In Progress status.** While BL is executing the hard delete, the import row shows Status = Reversal In Progress. View details and Reverse import are disabled during this state.

**AC17 — Hard delete on confirm.** On confirm, BL cascade-deletes all dependent records then accounts and categories. Chart of Accounts returns to pre-import state. DE log data unaffected. DE status updated to Reversed on completion.

**AC18 — Hard delete is atomic.** If any part fails, nothing is deleted. Import returns to Done. Cross-service atomicity deferred to tech lead.

**AC19 — Rollups recalculated.** If the cascade deleted ledger entries, rollups and balances for affected fiscal periods are re-run.

**AC20 — Reversed import stays visible.** After deletion, import row shows Status = Reversed. Comment, user, timestamp recorded. View details still works.

**AC21 — Reverse is permission-gated.** Users lacking the Reverse Import permission do not see Reverse import (hidden, not disabled).

**AC22 — Download.** Report row Download retrieves the file. Document Center reports from Document Center. Power BI reports in the format selected at export time.

**AC23 — Empty state.** When no activity exists: "No import or export activity yet."
</content>
