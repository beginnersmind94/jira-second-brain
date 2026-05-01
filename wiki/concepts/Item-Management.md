---
title: "Item Management"
type: concept
source_component: "Item Management"
ticket_count: 904
---

# Item Management

> **Activity pulse** · 904 tickets ingested in the bulk import (Apr 20, 2026). No incremental Jira changes to this component since — the daily sync routine is in place; this section will start to move once Item Management tickets get edited in Jira. Recent themes from the corpus: *recipe edits*, *bulk item operations*. See the live changelog at [What's new](../training/whats-new.html).

## What it is

Item Management is the catalog of everything the kitchen touches. A purchased can of corn is an item. The recipe that uses three cans of corn is an item. The menu line on Tuesday that serves that recipe is an item. They all live here, with their pack sizes, units, allergens, and nutrition facts attached. Most of the 904 tickets in this module aren't about defining a new item — they're about editing the thousands that already exist, and about handing those items off cleanly to Inventory, Menus, and Production.

## What the tickets reveal

### 1. Recipes are the bigger half of the catalog

Three hundred-plus tickets touch recipes — and that's not because recipes are a side concept. A recipe in this product has ingredients with quantities, a yield, a nutrient rollup, allergen flags, costing, serving sizes, and one or more menu items that present it. Every one of those facets is its own slice of work. The corpus shows continuous investment across all of them: recipe details and edit screens ([[raw/tickets/NXT-10573|NXT-10573 — Recipe Details: General Info]]), nutrient information ([[raw/tickets/NXT-10574|NXT-10574 — Recipe Nutrient Information]]), contribution information ([[raw/tickets/NXT-10575|NXT-10575 — Recipe Contribution Info]]), allergens ([[raw/tickets/NXT-10576|NXT-10576 — Recipe Allergen Information]]), menu-item linkage ([[raw/tickets/NXT-11150|NXT-11150 — Recipe View/Edit Menu Item]]), and costing ([[raw/tickets/NXT-13231|NXT-13231 — Recipe Costing Report]]). The recipe sub-product is large enough that pulling Recipes out as its own concept page is on the table — see Open Questions.

### 2. The pivot from one-at-a-time to thousands-at-once

The most active recent stream in this module is bulk editing. Forty-plus tickets show a sustained shift from item-by-item screens to bulk select / bulk apply / find-and-replace. From [[raw/tickets/NXT-56249|NXT-56249 — Bulk Item: Bulk Apply, Multi-Select R&D]], paraphrased: *as an onboarding admin, I have thousands of items to set up — let me apply the same attribute to a batch of them at once.*

The pivot is real and recent. Older tickets edit one item per screen; the recent stream adds a Bulk Apply button to summary info ([[raw/tickets/NXT-39922|NXT-39922 — Bulk Updates: Update Summary Info]]), to inventory units and pack info ([[raw/tickets/NXT-39923|NXT-39923 — Bulk Updates: Inventory Info & Pack]]), to menu-item find-and-replace ([[raw/tickets/NXT-54898|NXT-54898 — Find & Replace: Menu Items, Bulk Add]]), to local-item selection ([[raw/tickets/NXT-39918|NXT-39918 — Bulk Item: Select Local Items]]). And — this is the part that makes it more than a UI change — the corpus shows the team also adding per-item history capture for bulk edits ([[raw/tickets/NXT-69359|NXT-69359 — Bulk Item: Capture History (Update)]], [[raw/tickets/NXT-69360|NXT-69360 — Bulk Item: Capture History (Onboarding)]]), so a bulk change is still auditable change-by-change. Bulk editing without an audit trail is a problem; the team caught that and built it in.

### 3. Pack size is where Item Management hands off to Inventory

Pack size sits at the join between three modules: Item Management defines it, Inventory receives against it, recipes consume it. The constraint that runs through the corpus is that pack size *can* be modified — but only if no Inventory has been received yet. From [[raw/tickets/NXT-30168|NXT-30168 — Items: Allow Pack Size changes]], paraphrased: *let me start an item with a single unit and expand the pack-size configuration later — but only if no inventory has been received against it.*

That single rule makes pack size a recurring source of operational corner cases. The corpus shows it touched from multiple angles: initial config ([[raw/tickets/NXT-30046|NXT-30046 — Pack Size Config (Step 3)]]), config enhancements ([[raw/tickets/NXT-31281|NXT-31281 — Pack Size Config Enhancements]]), pack-size and sub-quantity in the units grid ([[raw/tickets/NXT-37110|NXT-37110 — Items, Units: Pack Sizes & Sub-Qty]]), and the on-the-Inventory-side QOH flyout that has to handle a pack-size change cleanly ([[raw/tickets/NXT-35649|NXT-35649 — INV: Update Pack Size QOH flyout]]). The dedicated workflow [[workflows/item-onboarding-pack-size|Item Onboarding & Pack-Size Changes]] traces the full handoff.

## How it connects

Item Management is upstream of almost everything else nutrition staff touch. [[concepts/Inventory|Inventory]] receives items against the pack sizes and units defined here. [[concepts/Menu-Planning|Menu Planning]] builds cycles from menu items defined here. [[concepts/Production|Production]] forecasts and produces against recipes defined here. Pack-size changes propagate through all three. The day-to-day catalog work is documented in [[workflows/item-onboarding-pack-size|Item Onboarding & Pack-Size Changes]].

## Open questions

- **Recipes may deserve their own concept page.** The recipe sub-corpus is roughly 35% of all Item Management tickets and has a distinct shape — ingredients, yield, nutrient rollup, allergen rollup, costing — that doesn't compress well into a sub-section. The decision to keep recipes inside Item Management or split them out is open.
- **Catalog integration is built but possibly under-used.** External-source integration with USDA and GDSN ([[raw/tickets/NXT-39283|NXT-39283 — GDSNConnect: Process Imported Data]], [[raw/tickets/NXT-13277|NXT-13277 — Hide Image for USDA Approval]]) shipped with 29 tickets. The corpus doesn't say which districts actually pull from those sources versus typing items in by hand.
- **Bulk-edit adoption hasn't been measured.** Bulk operations shipped fast and recently. The corpus doesn't show whether the districts that adopted the bulk tools are saving onboarding time or creating new categories of mistake.

---

*Compiled from 904 tickets across 128 sprints. Last refreshed 2026-05-01. Source tickets are listed in [the ticket index](../../tickets.html).*
