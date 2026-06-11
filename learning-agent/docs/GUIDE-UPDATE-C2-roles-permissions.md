<!--
GUIDE UPDATE — Cluster C2 (Roles & permissions)
Target: "Financials 2.0 — Onboarding, Without the Yawn" (financials-guide.txt, April 2026 Edition)
Maps to: NEW section. The guide currently has ZERO roles/permissions content.
Status: ALL THREE source tickets are Jira status "New" → entire section is UPCOMING / (Coming).
  Nothing here describes shipped behavior. Do not flip to present tense until the tickets reach Done Done.
Source tickets: NXT-66927 (Finance Coordinator), NXT-66928 (Director / Central Office / SchoolCafe Administrator),
  NXT-66929 (Cafeteria Manager). RN empty for all three → AC is the highest-trust (and only) source; desc is persona/intent only.
Jargon note: AC calls the product the "Financial Oversight module"; the guide calls it Financials 2.0. AC module labels
  (Transaction Management, GL Code Structure, etc.) are preserved in citations; see Open Questions for the label-reconciliation gaps.
-->

# Job 11 (Coming) — "Decide who can touch the ledger, and what they'll see"

> **(Coming)** — Roles & permissions for Financials 2.0 are **in development** (Jira: NXT-66927, NXT-66928, NXT-66929, all *New*). Build your access plan now, but treat every behavior below as the **specified** design, not something you can click today. Nothing in this section is live yet.

**TL;DR:** Three access tiers ship with Financials 2.0 — **full-access admins**, a **Finance Coordinator** who configures everything but is fenced out of a few transaction and period actions, and a **read-only Cafeteria Manager**. Pick the tier per person before go-live; the lower two tiers are *not* "admin with a few boxes unchecked."

**When this is your job:** Week 0–1, during environment setup — right alongside registering imports and confirming site codes. "What will my cafeteria managers actually see?" is a go-live-gating question, and the answer is fixed by role.

**Who this is for:** Everyone the guide already addresses — the CN Director, Finance Manager/Director, Business Administrator, accountants who touch the ledger, *and* the Cafeteria Managers who only need to look. Each maps to exactly one of the three tiers below.

🔧 **Implementer:** This is a real onboarding decision, not a checkbox sweep. The three tiers behave differently *by design* — selecting a role pre-sets its permission boxes, and two of the three tiers have a default master toggle state that tells you at a glance what kind of role you picked. Walk the customer through "who is each person, and which tier do they need" before anyone logs in.

---

## The three tiers at a glance

Each tier below is the permission set Financials 2.0 will apply when that role accesses the module. <!-- Source: NXT-66928:AC "*When* I access the Financial Oversight module / *Then* I should have the following permissions:" --> Read down the column that matches the person you're setting up.

| Area | **Director / Central Office / SchoolCafe Admin** | **Finance Coordinator** | **Cafeteria Manager** |
|---|---|---|---|
| Dashboard | Full — view, edit, add, delete, configure layout | View only | View only |
| Configuration (GL structure, Account Mapping, Import/Export templates, Version History) | Full — view, edit, add, delete | **Full** — view, edit, add, delete | **View only** — cannot change anything |
| Manual journal entries | Full — view, edit, add, delete | View, edit, add (**no delete**) | View only |
| Posting from POS / Inventory | Full | View only | **No access** |
| Void / Reverse a transaction | Full | Can void/reverse (edit) | **No access** |
| Reports (P&L, Balance Sheet, Site-Level Analysis) | Full | View only | View only |
| Export reports to ERP | Full | View only | **No access** |
| Period management (open/close periods, fiscal year) | Full | **Edit only** | **No access** |
| Default master toggle when role is selected | "Disable All" (everything already on) | (not specified — see Open Questions) | "Enable All" (most things off) |

> The three tiers are deliberately different shapes — a full admin, a configuration-heavy coordinator who is fenced out of deletes and most of period/report management, and a look-but-don't-touch manager. Match the person to the shape, not to a count of checkboxes.

---

## Tier 1 — Director, Central Office, SchoolCafe Administrator: full access

These three roles get the keys to everything, and they all get the **same** keys. <!-- Source: NXT-66928:AC "All three roles (Director, Central Office, SchoolCafe Administrator) have identical permissions" --> There are no restrictions on any feature. <!-- Source: NXT-66928:AC "I have FULL access to ALL modules and features" --> <!-- Source: NXT-66928:AC "No restrictions apply to any feature or capability" -->

What "full access" covers for these roles:

- **Everything is view, edit, add, and delete** across all Financials functions. <!-- Source: NXT-66928:AC "I can VIEW, EDIT, ADD, and DELETE across all Financial Oversight functions" -->
- **The dashboard** — view, edit, add, delete, and configure layouts and settings. <!-- Source: NXT-66928:AC "FULL access to Financial Oversight dashboard" --> <!-- Source: NXT-66928:AC "I can configure dashboard layouts and settings" -->
- **Configuration** — full access to GL structure (the Account Code Structure in this guide's terms), Account Mapping, Import/Export templates, and Version History. <!-- Source: NXT-66928:AC "GL Code Structure: FULL access (VIEW, EDIT, ADD, DELETE)" --> <!-- Source: NXT-66928:AC "Account Mapping: FULL access (VIEW, EDIT, ADD, DELETE)" --> <!-- Source: NXT-66928:AC "Import/Export Templates: FULL access (VIEW, EDIT, ADD, DELETE)" --> <!-- Source: NXT-66928:AC "Version History: FULL access (VIEW, EDIT, ADD, DELETE)" -->
- **Transactions** — full access to manual entries, posting from POS/Inventory, transaction search, and void/reverse. <!-- Source: NXT-66928:AC "Manual Entries: FULL access (VIEW, EDIT, ADD, DELETE)" --> <!-- Source: NXT-66928:AC "Post from POS/Inventory: FULL access (VIEW, EDIT, ADD, DELETE)" --> <!-- Source: NXT-66928:AC "Void/Reverse: FULL access (VIEW, EDIT, ADD, DELETE)" -->
- **Period management** — full control, including opening and closing financial periods and managing fiscal-year configurations (the same Periods work covered in Job 4). <!-- Source: NXT-66928:AC "I can open/close financial periods" --> <!-- Source: NXT-66928:AC "I can manage fiscal year configurations" -->
- **Reports** — full access to every report, including Export to ERP. <!-- Source: NXT-66928:AC "Export to ERP: FULL access (VIEW, EDIT, ADD, DELETE)" -->

What it looks like when this role is selected: every permission box is turned on automatically, and the master toggle reads **"Disable All"** by default — because there's nothing left to enable. <!-- Source: NXT-66928:AC "All permission checkboxes are automatically enabled when any of these three roles is selected" --> <!-- Source: NXT-66928:AC "Master toggle shows \"Disable All\" by default (since all permissions are enabled)" --> A full-access user also sees every saved configuration, no matter who created it. <!-- Source: NXT-66928:AC "All saved configurations are accessible regardless of who created them" -->

🔧 **Implementer:** Use the master-toggle state as your sanity check. If you select a Director-tier role and the toggle does **not** read "Disable All" with everything on, the role mapping is wrong — stop before you hand the environment over.

⚠️ **Watch out:** "Full access" really is full — including delete. These three roles can delete configuration, delete transactions, and delete dashboard elements. Reserve the Director tier for the people who genuinely need that reach; use the Finance Coordinator tier (below) for day-to-day configuration work that shouldn't include deleting posted-ledger data.

---

## Tier 2 — Finance Coordinator: configure everything, but fenced out of deletes, reports, and most of periods

This is the tier for the Finance Manager / accountant who *runs* the configuration but shouldn't have a delete-everything key. It's the most granular of the three. <!-- Source: NXT-66927:AC "*Given* I am logged in as a Finance Coordinator / *When* I access the Financial Oversight module / *Then* I should have the following permissions:" -->

**Where the Finance Coordinator has full power — Configuration.** They get full access to the Configuration module: GL structure, Account Mapping, Import/Export templates, and Version History, all view/edit/add/delete. <!-- Source: NXT-66927:AC "I have FULL access to the Configuration module" --> <!-- Source: NXT-66927:AC "GL Code Structure: FULL access (VIEW, EDIT, ADD, DELETE)" --> <!-- Source: NXT-66927:AC "Account Mapping: FULL access (VIEW, EDIT, ADD, DELETE)" --> <!-- Source: NXT-66927:AC "Import/Export Templates: FULL access (VIEW, EDIT, ADD, DELETE)" --> <!-- Source: NXT-66927:AC "Version History: FULL access (VIEW, EDIT, ADD, DELETE)" --> In practice that means a Finance Coordinator can own Jobs 1 and 2 (chart of accounts, account mapping) end to end.

**Where they're fenced in — transactions.** They can view, edit, and add transaction-management functions, but they **cannot delete** transactions and do not get full access. <!-- Source: NXT-66927:AC "I can VIEW, EDIT, and ADD transaction management functions" --> <!-- Source: NXT-66927:AC "I cannot DELETE transactions or have FULL access" --> Specifically:

- **Manual entries** — view, edit, and add (the Job 6 flow), but no delete. <!-- Source: NXT-66927:AC "Manual Entries: I can VIEW, EDIT, and ADD manual entries" -->
- **Posting from POS/Inventory** — view only. <!-- Source: NXT-66927:AC "Post from POS/Inventory: I can VIEW only" -->
- **Void / Reverse** — they *can* do this. The reverse-a-bad-posting flow from Job 7 is available to the Finance Coordinator. <!-- Source: NXT-66927:AC "Void/Reverse: I can EDIT transactions (void/reverse capability)" -->

**Reports — view only.** A Finance Coordinator can read every report but cannot edit, add, delete, or export them. P&L, Balance Sheet, and Site-Level Analysis are all view-only, including Export to ERP. <!-- Source: NXT-66927:AC "I can VIEW all reports but cannot modify them" --> <!-- Source: NXT-66927:AC "I cannot EDIT, ADD, DELETE, or have FULL access to reports" --> <!-- Source: NXT-66927:AC "Export to ERP: VIEW only" -->

**Period management — edit only.** This is the narrowest slice: the Finance Coordinator can **edit** period settings, but cannot view (as a separate permission), add, delete, or hold full access to period management. <!-- Source: NXT-66927:AC "I can EDIT period settings" --> <!-- Source: NXT-66927:AC "I cannot VIEW, ADD, DELETE, or have FULL access to period management" -->

**Dashboard — view only**, with no edit/add/delete and no dashboard-configuration rights. <!-- Source: NXT-66927:AC "I can VIEW the Financial Oversight dashboard" --> <!-- Source: NXT-66927:AC "I cannot EDIT, ADD, or DELETE dashboard elements" -->

How the permission screen behaves for this tier: the parent-module **"FULL access" toggle is a shortcut** — turning it on for a module flips on all of that module's child permissions at once; if you then change an individual box, the "FULL access" indicator updates to match. <!-- Source: NXT-66927:AC "When I click FULL access on a parent module, all child permissions are automatically enabled" --> <!-- Source: NXT-66927:AC "When I modify individual permissions, the FULL access indicator updates accordingly" --> The Finance Coordinator can also save a permission configuration for reuse in future sessions. <!-- Source: NXT-66927:AC "I can save my permission configurations for future sessions" -->

⚠️ **Watch out — "edit periods" is not "open/close periods" in the AC.** The Finance Coordinator AC grants *edit* on period settings and explicitly withholds full access; the open/close-periods and fiscal-year wording lives only in the Director tier. Don't assume a Finance Coordinator can close a period the way an admin can until the exact period actions are confirmed (see Open Questions). This matters because period close is what releases posting in Job 4 / Job 10.

🔧 **Implementer:** The Finance Coordinator is the right default for "the person who sets up and maintains Financials but isn't the district's top admin." They can do all of Job 1 and Job 2, make and reverse journal entries (Jobs 6–7), and read every report — but they can't delete transactions or export to the ERP, and their period control is limited to editing settings. If your customer needs that person to also close periods or push exports, they need the Director tier, or you flag the gap to the product owner.

---

## Tier 3 — Cafeteria Manager: read-only / limited

This is the "look, don't touch" tier. A Cafeteria Manager can see relevant financial information but cannot change financial data. <!-- Source: NXT-66929:AC "*Given* I am logged in as a Cafeteria Manager / *When* I access the Financial Oversight module / *Then* I should have the following permissions:" -->

What a Cafeteria Manager **can** see:

- **The dashboard** — view only; no edit, add, delete, or full access. <!-- Source: NXT-66929:AC "I can VIEW the Financial Oversight dashboard" --> <!-- Source: NXT-66929:AC "I cannot EDIT, ADD, DELETE, or have FULL access to dashboard elements" -->
- **Configuration — view only.** They can look at configuration settings (GL structure, Account Mapping, Import/Export templates, Version History) but cannot modify any of them. <!-- Source: NXT-66929:AC "I can VIEW configuration settings but cannot modify them" --> <!-- Source: NXT-66929:AC "GL Code Structure: VIEW only" --> <!-- Source: NXT-66929:AC "Account Mapping: VIEW only" --> <!-- Source: NXT-66929:AC "I cannot EDIT, ADD, or DELETE any configuration items" -->
- **Manual entries and transaction search — view only.** <!-- Source: NXT-66929:AC "Manual Entries: VIEW only" --> <!-- Source: NXT-66929:AC "Transaction Search: VIEW only" -->
- **Reports — view only**, including P&L, Balance Sheet, and Site-Level Analysis. <!-- Source: NXT-66929:AC "I can VIEW all reports but cannot modify them" --> <!-- Source: NXT-66929:AC "Profit & Loss: VIEW only" --> <!-- Source: NXT-66929:AC "Balance Sheet: VIEW only" --> <!-- Source: NXT-66929:AC "Site-Level Analysis: VIEW only" -->

What a Cafeteria Manager **cannot reach at all** (not even view):

- **Posting from POS/Inventory** — no access. <!-- Source: NXT-66929:AC "Post from POS/Inventory: No access (cannot VIEW, EDIT, ADD, or DELETE)" -->
- **Void / Reverse** — no access; the Job 7 fix-a-bad-posting flow is not available to this tier. <!-- Source: NXT-66929:AC "Void/Reverse: No access (cannot VIEW, EDIT, ADD, or DELETE)" -->
- **Export to ERP** — no access. <!-- Source: NXT-66929:AC "Export to ERP: No access (cannot VIEW, EDIT, ADD, or DELETE)" -->
- **Period management** — no access of any kind. <!-- Source: NXT-66929:AC "I have no access to period management" --> <!-- Source: NXT-66929:AC "I cannot VIEW, EDIT, ADD, DELETE, or have FULL access to period settings" -->

How the permission screen behaves for this tier: most boxes start **unchecked** when Cafeteria Manager is selected, only the view permissions for reachable modules are enabled, and the master toggle reads **"Enable All"** by default — the mirror image of the Director tier. <!-- Source: NXT-66929:AC "Most permission checkboxes remain unchecked when Cafeteria Manager role is selected" --> <!-- Source: NXT-66929:AC "Only VIEW permissions are enabled for accessible modules" --> <!-- Source: NXT-66929:AC "Master toggle shows \"Enable All\" by default (since most permissions are disabled)" -->

⚠️ **Watch out:** When a Cafeteria Manager tries something they're not allowed to do, they get an **"Access Denied"** message rather than a silent no-op — so "I clicked it and nothing happened" is usually a sign the action was blocked, not broken. <!-- Source: NXT-66929:AC "I receive appropriate \"Access Denied\" messages when attempting restricted actions" -->

🔧 **Implementer:** This is the answer to "what will my cafeteria managers see?" — the dashboard, configuration, manual entries, transaction search, and reports, all read-only; and nothing at all for posting, void/reverse, ERP export, or periods. Set this expectation with the customer's site staff up front so a Cafeteria Manager isn't surprised by an "Access Denied" on day one.

---

## How role switching behaves

Where AC specifies it, a tier's permission set is sticky: switching away from a role and back restores that role's permissions rather than leaking the previous role's access. This is stated for two of the three tiers:

- A **Cafeteria Manager's** limited set is maintained when switching between roles and returning. <!-- Source: NXT-66929:AC "My limited permission set is maintained when switching between roles and returning to Cafeteria Manager" -->
- The **Director tier** maintains full permissions across switches between Director, Central Office, and SchoolCafe Administrator. <!-- Source: NXT-66928:AC "Role switching between Director, Central Office, and SchoolCafe Administrator maintains full permissions" -->

⚠️ **Watch out:** The "permission set is maintained on role switch" guarantee is stated per-tier in the Cafeteria Manager and Director ACs. The Finance Coordinator AC does not restate it in those words — do not assume identical switch behavior for the Coordinator tier beyond what its own AC covers (see Open Questions).

---

## What gets logged

Permission and configuration changes are auditable — consistent with the rest of Financials 2.0, where the ledger and configuration history keep a trail (Jobs 1, 2, 7, 8).

- For the Finance Coordinator tier, **all permission changes are logged and auditable**. <!-- Source: NXT-66927:AC "All permission changes are logged and auditable" -->
- For the Director tier, **permission changes are logged with an audit trail for each role**. <!-- Source: NXT-66928:AC "Permission changes are logged with appropriate audit trail for each role" -->

(No audit-logging line appears in the Cafeteria Manager AC — unsurprising, since that tier can't change permissions. Don't infer the absence of an audit trail for that role; it simply isn't specified there.)

---

## What this is renamed from / where it sits relative to the rest of the guide

This is a **new** capability area, not a renamed legacy one — there's no legacy→2.0 glossary row for it yet. Two framing notes so it lines up with the rest of the guide:

- The AC for all three tiers calls the product the **"Financial Oversight module."** This guide calls it **Financials 2.0**. Treat those as the same module until a customer-facing module name is confirmed. <!-- Source: NXT-66928:AC "*When* I access the Financial Oversight module" -->
- The permission areas in the AC line up with the Jobs you already know: *Configuration* = Jobs 1–3 (chart of accounts, mapping, posting settings); *Transaction Management* = Jobs 6–7 (manual entries, reversals) plus posting; *Reports* = Job 9; *Period Management* = Job 4; *Dashboard* = the (separately upcoming) Financial Dashboard. The AC module **labels** ("Transaction Management," "GL Code Structure") are quoted from the tickets and may not be the exact on-screen labels in this guide's wording — see Open Questions.

---

## Open Questions (for the SME / product owner — do not invent answers)

These are gaps the AC does **not** resolve. Per the no-invented-specifics rule, they're surfaced rather than filled.

1. **Where does the roles/permissions screen live?** No AC states a menu path (no `Configuration › …` location) or the page name for managing roles/permissions. *Needs a confirmed navigation path before this section can tell a user where to click.*
2. **What is the exact role-picker label and the canonical role names in the UI?** AC names the roles ("Finance Coordinator," "Director," "Central Office," "SchoolCafe Administrator," "Cafeteria Manager") but not the on-screen selector label or whether these are exactly how they appear in the role dropdown. The Finance Coordinator desc field says "Finance Manager"; AC says "Finance Coordinator" — *confirm which is the product term.*
3. **Do the AC module labels match this guide's labels?** AC uses "Transaction Management," "GL Code Structure," "Import/Export Templates." The guide uses "Journal & Ledger," "Account Code Structure," and the Imports & Exports area. *Confirm the permission-screen labels so prose can use the real ones instead of straddling both.*
4. **What is the Finance Coordinator's default master-toggle state?** AC gives the default toggle state for the Director tier ("Disable All") and the Cafeteria Manager tier ("Enable All") but is silent for the Finance Coordinator. *Left blank in the table on purpose — needs confirmation.*
5. **"Edit periods" vs. "open/close periods" for the Finance Coordinator.** AC grants the Coordinator "EDIT period settings" and withholds full access; the open/close-periods and fiscal-year wording appears only in the Director AC. *Confirm exactly which period actions the Coordinator can perform — this gates who can release posting.*
6. **Does the Coordinator's permission set persist on role switch?** Stated explicitly for the Cafeteria Manager and Director tiers; not stated for the Finance Coordinator. *Confirm before claiming identical behavior.*
7. **Exact restricted-action message strings.** AC quotes "Access Denied" for the Cafeteria Manager. *Confirm whether the same string is used for blocked actions in the other tiers, and whether it varies by action.*
