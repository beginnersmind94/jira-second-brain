<!--
Cluster: C4 — Module placement, navigation & licensing
Source report: docs/FINANCIALS-2.0-COVERAGE-REPORT.md §3 C4
Tickets: NXT-66966 (nav), NXT-66965 (licensing), NXT-66930 (module architecture naming)
Status of all three: New → entire section is UPCOMING. Tagged "(Coming)" throughout.
Grounding: RN is empty in this fixture; AC is the highest-trust source. Every product-behavior
sentence carries an inline <!-- Source: NXT-####:AC "verbatim quote" -->. Backend/internal notes
(e.g. "done through System", "moved to platform") are translated or kept implementer-side; the raw
phrasing stays inside the citation comment. No exact icon/label is invented — gaps are Open questions.
Placement: NEW preface, sits immediately after "Before you touch the product" (page 3) and before Job 1.
Voice: matches the guide — TL;DR, "When this is your job", 🔧 Implementer, ⚠️ watch-outs, legacy→2.0 glossary.
-->

# Finding Financials — getting to the module, and turning it on (Coming)

> **Heads-up — this whole section is upcoming.** Module navigation (NXT-66966), the License Management toggle (NXT-66965), and the module's internal structure (NXT-66930) are all **New** in Jira — not yet shipped. Everything below describes the *planned* setup behavior so implementers can scope it. Do not promise a customer these screens exist today; tag every reference **(Coming)** until the stories are Done Done.

**TL;DR:** Before anyone can do Job 1, two things have to be true — the module has to be **turned on for your district** (a one-time license toggle the implementer flips), and the right people have to be able to **see it in the left sidebar**. This section is the "how do I even get in?" preface to the ten jobs that follow. *(All Coming.)*

**When this is your job:** Week 0 / Day 0 — before login is useful. This pairs with *Before you touch the product*: it's the same "lock it down before the customer logs in" work, just for getting *into* the module instead of getting your data ready.

---

## Step 1 — Turn the module on (License Management) (Coming)

Financials is licensed at the **district level** — it's on or off for the whole district, not per site and not per user. <!-- Source: NXT-66965:AC "License type is \"District\" (district-wide access)" --> Turning it on is a one-time toggle in the platform's licensing screen, the same place every other SchoolCafe module is switched on. <!-- Source: NXT-66965:AC "Module can be activated/deactivated via toggle (like other modules)" -->

**Where (planned):** the module shows up as a product option under **System › Management › License Management**, listed by its module name. <!-- Source: NXT-66965:AC "\"Financial Oversight\" appears as a product option in System > Management > License Management" --> *Interpretation: AC names the menu path System > Management > License Management verbatim; we render the SchoolCafe 2.0 breadcrumb separator (›) to match the rest of this guide.*

Two things follow from how the license works, and both matter for go-live timing:

- **The license honors your renewal dates.** When the license lapses, access goes with it. <!-- Source: NXT-66965:AC "Module respects license renewal dates" --> Translation for the customer: this isn't a permanent switch you flip once and forget — it's tied to the same renewal cycle as the rest of your SchoolCafe contract.
- **No license = no entry, for everyone.** Until the toggle is on, nobody in the district can open the module — not even a full-access director. <!-- Source: NXT-66965:AC "Users without active license cannot access Financial Oversight module" -->

> ⚠️ **License is the floor, not the whole door.** Turning the license on does **not** by itself put the module in front of a given user. The license is necessary but not sufficient — a user also needs the right role permissions before the module appears for *them* (see Step 2). Flipping the toggle and assuming "everyone can see it now" is the trap. <!-- Source: NXT-66966:AC "Module only visible to users with active license AND appropriate role permissions" -->

🔧 **Implementer:** Flip this during environment stand-up, the same week you register the import types (*Before you touch the product*, step 4) — not on the first onboarding call. It's plumbing, not training. Treat "license the module" and "register the imports" as one Week-0 checklist so the customer's first real login already has the module lit up and the GL Accounts Import on the picklist.

> 🔧 **Implementer note — where the switch actually lives.** AC flags that this may not stay in the district-level admin area: the licensing entry may be promoted to the platform tier rather than the per-district screen. <!-- Source: NXT-66965:AC "Note: May need to be moved to platform" --> If you don't find the toggle under System › Management › License Management, check the platform-level licensing area before assuming it's missing. **Open question:** confirm the final home of the toggle (district admin vs. platform) before this ships — do not document one as the canonical path until it's locked.

---

## Step 2 — Find it in the sidebar (Coming)

Once the district is licensed, the module appears in the **left sidebar navigation** for users who are allowed to see it. <!-- Source: NXT-66966:AC "Financial Oversight appears in left sidebar navigation" --> Click it and you land on the module's home / landing page. <!-- Source: NXT-66966:AC "Clicking Financial Oversight navigates to module home/landing page" -->

**Who sees it:** the sidebar entry is gated on **both** conditions at once — an active district license **and** the right role permissions for that user. <!-- Source: NXT-66966:AC "Module only visible to users with active license AND appropriate role permissions" --> A licensed district whose cafeteria manager has the wrong role simply won't see the entry; that's expected, not a bug. *(For who gets which permission tier, see the Roles & permissions section — also Coming.)*

**Where in the menu it sits:** Financials lives in the **Front Office** group of the navigation, not Back Office. <!-- Source: NXT-66966:AC "Module belongs to Front Office group (not Back Office)" --> Within that group the planned slot is **below Account Management and above Item Management** — but treat the exact position as not-yet-final. <!-- Source: NXT-66966:AC "Financial Oversight appears in left sidebar navigation positioned below Account Management and above Item Management (Position may be changed)" --> *Interpretation: AC's own parenthetical "(Position may be changed)" is why this guide describes the neighborhood (Front Office, near Account Management / Item Management) rather than a fixed rank — don't teach a customer to look for the 3rd item from the top.*

**Knowing where you are:** as you move through the module, the breadcrumb trail reads **Financial Oversight › [current page]**, so you can always see the module name plus the page you're on. <!-- Source: NXT-66966:AC "Breadcrumbs display correctly: Financial Oversight > [Current Page]" --> *Interpretation: AC writes the separator as ">"; rendered as "›" here to match the SchoolCafe 2.0 breadcrumb style used elsewhere in this guide.*

> ⚠️ **The module is called "Financial Oversight" in the product — not "Financials."** This guide and your kickoff deck say *Financials 2.0*, but the sidebar label, the breadcrumb root, and the License Management product option all read **Financial Oversight**. <!-- Source: NXT-66966:AC "Financial Oversight appears in left sidebar navigation" --> <!-- Source: NXT-66965:AC "\"Financial Oversight\" appears as a product option in System > Management > License Management" --> Tell customers what to look for by the on-screen name so they aren't hunting for a "Financials" entry that isn't labeled that way.

**Open question (icon):** AC says the module's icon and visual treatment follow the SchoolCafe 2.0 design system but does **not** name a specific glyph. <!-- Source: NXT-66966:AC "Module icon/visual design matches SchoolCafe 2.0 design system" --> Do not describe the icon to customers (e.g. "look for the dollar-sign icon") until design confirms it — flag for SME to fill in the exact icon at release.

---

## How the module is laid out (the map behind the ten jobs) (Coming)

This guide is organized by *jobs*, not menus — but it helps to know the cabinet the jobs live in. The planned module is built from five top-level areas — Dashboard, Configuration, Transaction Management, Reports, and Settings. <!-- Source: NXT-66930:AC "* Dashboard subcomponent" --> <!-- Source: NXT-66930:AC "* Configuration subcomponent" --> <!-- Source: NXT-66930:AC "* Transaction Management subcomponent" --> <!-- Source: NXT-66930:AC "* Reports subcomponent" --> <!-- Source: NXT-66930:AC "* Settings" --> Here's the map, with the Job each area connects to:

| Module area (Coming) | What lives here | Maps to |
|---|---|---|
| **Dashboard** | The at-a-glance landing view. <!-- Source: NXT-66930:AC "*Dashboard Subcomponent Features:*" --> <!-- Source: NXT-66930:AC "* View dashboard" --> | the Financial Dashboard (separate section) |
| **Configuration** | GL code structure, account mapping, import/export templates, and version history. <!-- Source: NXT-66930:AC "*Configuration Subcomponent Features:*" --> <!-- Source: NXT-66930:AC "* GL Code Structure feature" --> <!-- Source: NXT-66930:AC "* Account Mapping feature" --> <!-- Source: NXT-66930:AC "* Import/Export Templates feature" --> <!-- Source: NXT-66930:AC "* Version History feature" --> | Job 1 (chart of accounts), Job 2 (mapping) |
| **Transaction Management** | Manual entries, postings from POS/Inventory, transaction search, and void/reverse. <!-- Source: NXT-66930:AC "*Transaction Management Subcomponent Features:*" --> <!-- Source: NXT-66930:AC "* Manual Entries feature" --> <!-- Source: NXT-66930:AC "* Post from POS/Inventory feature" --> <!-- Source: NXT-66930:AC "* Transaction Search feature" --> <!-- Source: NXT-66930:AC "* Void/Reverse feature" --> | Job 6 (manual entries), Job 7 (fixing a bad posting) |
| **Reports** | Profit & Loss, Balance Sheet, site-level analysis, and Export to ERP. <!-- Source: NXT-66930:AC "*Reports Subcomponent Features:*" --> <!-- Source: NXT-66930:AC "* Profit & Loss feature" --> <!-- Source: NXT-66930:AC "* Balance Sheet feature" --> <!-- Source: NXT-66930:AC "* Site-Level Analysis feature" --> <!-- Source: NXT-66930:AC "* Export to ERP feature" --> | Job 9 (pull a report) |
| **Settings** | Fund balance, budget, and KPIs. <!-- Source: NXT-66930:AC "*Settings Subcomponent Features:*" --> <!-- Source: NXT-66930:AC "* Fund balance" --> <!-- Source: NXT-66930:AC "* Budget" --> <!-- Source: NXT-66930:AC "* Key Performance Indicators (KPIs)" --> | — |

A few things worth flagging from this map, because they line up with what later sections cover:

- **"Fix a posting that went out wrong" lives under Transaction Management as Void/Reverse.** <!-- Source: NXT-66930:AC "* Void/Reverse feature" --> When Job 7 says you'll reverse a posting, this is the area it's in.
- **Reports will include a Balance Sheet and an Export to ERP path.** <!-- Source: NXT-66930:AC "* Balance Sheet feature" --> <!-- Source: NXT-66930:AC "* Export to ERP feature" --> If you've seen the Reports section enumerate a fixed set of tiles, note that the planned architecture lists Balance Sheet alongside P&L — consistent with the new report tiles called out elsewhere as (Coming).

> ⚠️ **This is the architecture, not a feature inventory of what's live today.** NXT-66930 is the *base structure* story (New) — it names where things will sit, not that each one is built and working. Use it to orient ("Void/Reverse is under Transaction Management"), not to promise a customer a finished Balance Sheet or ERP export. Each of those features is tracked, and tagged, in its own section.

🔧 **Implementer:** All three pieces of this section — the license toggle, the sidebar/permission gating, and the module structure — are owned by the *Roles and Permissions* epic and are all still **New**. <!-- Source: NXT-66965:AC "Module can be activated/deactivated via toggle (like other modules)" --> When you brief a district on Financials 2.0 before release, frame this as "here's how you'll get in and turn it on when it ships," and keep the **(Coming)** tag visible so nobody tries to find a License Management entry that isn't there yet.

---

### What's renamed / new vs. legacy

*Same legacy→2.0 glossary style as the Jobs. All entries below are (Coming) — they describe the planned 2.0 naming, not a live screen.*

- **The module's on-screen name** → **Financial Oversight** (what you'll see in the sidebar, breadcrumbs, and License Management — even though this guide calls the product "Financials 2.0"). <!-- Source: NXT-66966:AC "Financial Oversight appears in left sidebar navigation" -->
- **Where you switch a module on** → **System › Management › License Management**, a per-**district** toggle. <!-- Source: NXT-66965:AC "\"Financial Oversight\" appears as a product option in System > Management > License Management" --> <!-- Source: NXT-66965:AC "License type is \"District\" (district-wide access)" -->
- **Menu neighborhood** → **Front Office** group (not Back Office), near Account Management and Item Management. <!-- Source: NXT-66966:AC "Module belongs to Front Office group (not Back Office)" -->

**Open questions for SME before this section ships:**
1. **Final home of the License Management toggle** — district admin screen vs. platform tier. <!-- Source: NXT-66965:AC "Note: May need to be moved to platform" -->
2. **Final sidebar position** — AC marks the below-Account-Management / above-Item-Management slot as movable. <!-- Source: NXT-66966:AC "Financial Oversight appears in left sidebar navigation positioned below Account Management and above Item Management (Position may be changed)" -->
3. **The module icon** — not named in AC; confirm the exact glyph before describing it to customers. <!-- Source: NXT-66966:AC "Module icon/visual design matches SchoolCafe 2.0 design system" -->
