# Inline tagging conventions (working notes)

Established across batches 1–3. Re-anchor here if context gets compacted.

## Edge-case routing decisions

- **Item Substitution feature** → Other (per-item relationship setup, not in taxonomy). Examples: NXT-19131, NXT-24050, NXT-26260.
- **Item-level file/attachment (exemption letters, etc.)** → Other (per-item document upload not in taxonomy). Example: NXT-22616.
- **Item history (Item Detail / General Info)** → #1 Wizard (item-edit lifecycle). Confidence: low.
- **Item history (Nutrient Info / Contributions / Allergens)** → #5 Nutrients.
- **Item history (Serving Measure)** → #6 Units.
- **Recipe history (any subsection: Steps & Ingredients, Nutrient Details, Yield Factors)** → #3 Recipe Authoring.
- **Menu Item / VMI / CMI / POS history** → #4 Menu Items.
- **Split view tickets (filters, columns, thumbnails, sort)** → #7 List Pages.
- **Global Catalog list-page features (history, columns, search by manufacturer)** → #7 with secondary #10 (cross-module captured by `touches_other_modules`).
- **IM↔Inventory image/data sync, GC import flows, vendor contracts** → #10 Inventory Sync & Publishing.
- **Configuration sub-pages (HACCP, brands, manufacturers, valuation, item categories, recipe categories, custom allergens, serving measure config, data sources, multi-tenant)** → #11 Configuration.
- **USDA / CN25 / CNDB / Sesame / FDA-driven** → #12 USDA & Regulatory Updates.
- **CN database scripts / CN data import infrastructure** → #12 (driver is regulatory content updates).
- **Tooltips, color, alignment, copy/spelling fixes, "UI only" tickets** → #8 UI/UX Polish.
- **Generic item create/edit form (pre-modern-wizard era)** → #1 Wizard.
- **Item Onboarding via Excel import (pre-modern-wizard era)** → #1 Wizard (Excel-to-Wizard handoff).
- **Recipe step search / circular-recipe prevention** → #3 Recipe Authoring.
- **Reports launched from list-page dropdowns (Item List Export, etc.)** → #9 Reports.

## Story-shape vs. Bug-shape

- Bugs about UI-only visual issues → #8.
- Bugs that produce a 500/400 error in a specific flow → host feature category, not #8.
- Stories proposing a new feature → category that matches the feature's user surface.

## #4 vs #11 reminder

- #4 = per-item config (configuring one menu item, one VMI, one POS item).
- #11 = system-level admin (configuring the platform-wide list, e.g. all available HACCP processes, the brand reference list).

## #11 vs #12 reminder

- #12 wins when driver is a named/implied regulatory mandate.
- #11 if it's just admin-page improvement with no regulatory framing.

## Batches 1–3 cumulative distribution

| primary_category | count |
| --- | ---: |
| List Pages, Search, Filters & Navigation | 31 |
| UI/UX Polish, Copy & Visual Defects | 18 |
| Menu Items, VMI & POS Configuration | 18 |
| Recipe Authoring | 19 |
| Reports & Data Exports | 15 |
| Configuration | 10 |
| Item Onboarding — Wizard | 14 |
| Nutrients, Contributions & Allergens | 10 |
| USDA & Regulatory Updates | 9 |
| Inventory Sync & Publishing | 3 |
| Units, Pack Sizes & Serving Measures | 3 |
| Other | 4 |
| Item Onboarding — Bulk Tools | 0 |

PCS-*: 0 so far. Expected to start appearing in later batches as the issue_key range crosses into PCS-* territory.

Other rate so far: 4/150 = 2.7%.
