---
title: "Inventory"
type: concept
source_component: "Inventory"
ticket_count: 850
---

# Inventory

> **Activity pulse** · 850 tickets ingested in the bulk import (Apr 20, 2026). No incremental Jira changes to this component since — the daily sync routine is in place; this section will start to move once Inventory tickets get edited in Jira. Recent themes from the corpus: *orders & receipts*, *physical inventory reconciliation*. See the live changelog at [What's new](../training/whats-new.html).

## What it is

Inventory is where the goods physically are. Orders placed against vendors. Receipts when those orders arrive. Transfers between sites. Periodic counts of what's actually on the shelf. The adjustments that fall out of all of it. The 850 tickets in this module break into three layers that work on different time scales: the daily flow of orders and receipts, the vendor-and-contract structure underneath, and the periodic reckoning when someone walks the storeroom with a clipboard.

## What the tickets reveal

### 1. Orders aren't one-shot — receipts stay editable until the period locks

Roughly half of all Inventory tickets touch orders, receipts, and the lifecycle that connects them. The shape that emerges from the corpus: an order isn't done when goods arrive. The receipt against it stays editable for a long window after — through invoice corrections, charge and discount allocations, partial-shipment edits, and order-was-closed-but-period-isn't-yet adjustments. From [[raw/tickets/NXT-19432|NXT-19432 — Allow Receipts to be edited after Order is Closed]], paraphrased: *let me keep editing receipts after the order is closed — until the accounting period locks, anyway.*

The corpus shows this as a deliberate stance rather than a stretched-too-thin permission. The team built editable headers (invoice number, invoice amount) on previously-saved receipts ([[raw/tickets/NXT-15379|NXT-15379 — Edit Receipt Details: Header Validations]]), kept the receipt edit-history visible after period checks were applied ([[raw/tickets/NXT-19328|NXT-19328 — Apply Period check to transactions]]), removed broken-unit handling out of receipt edits ([[raw/tickets/NXT-19259|NXT-19259 — Receipts tab: Remove Broken Units]]), and built a full history record on every order change so the audit trail follows the receipt forward ([[raw/tickets/NXT-18137|NXT-18137 — Save history record when order changes]]). Receipts here are accounting objects: editable, but every edit is recorded.

### 2. Vendor structure is a layered engineering problem

The vendor model isn't a flat list. The corpus shows continuous work on a layered hierarchy: external vs. internal vendor types, commodity contracts, seasonal contracts that come and go through the year, shipping schedules, and ordering conditions that have to navigate all of those layers. The introduction of internal vendors ([[raw/tickets/NXT-1840|NXT-1840 — Add Vendor: Internal Vendor Type]]) opened a structural change — vendors can now be linked to a site for warehouse functionality, not only to commercial suppliers.

From [[raw/tickets/NXT-66911|NXT-66911 — Internal Vendors, Seasonal Contract: Inherit Item List]], paraphrased: *the seasonal contract should inherit the main contract's item list — managing two parallel item lists is the part nobody wants.* The pattern in the corpus is consistent: every time a new vendor or contract layer is added, the team has to thread it through ordering conditions ([[raw/tickets/NXT-66944|NXT-66944 — Ordering Conditions: Handle seasonal contracts for internal vendors]]), through item-list inheritance, through shipping groups ([[raw/tickets/NXT-59611|NXT-59611 — Vendors, Contracts: Configure Shipping Groups]]), and through commodity contract configuration ([[raw/tickets/NXT-1839|NXT-1839 — Commodity Contract Configuration]]). The vendor hierarchy is layered, which means each layer's setting has to know about the others — and most ordering bugs trace back to one of those layers not propagating cleanly.

### 3. Physical inventory is where operations meet accounting

A hundred-plus tickets cover the periodic reckoning: a count freeze, the count itself, variance review, and the reconciliation that posts adjustments forward. The corpus shows this as a workflow that lives in the seams between two roles. From [[raw/tickets/NXT-13933|NXT-13933 — Physical Inventory: Use static grouping]], paraphrased: *let me reorder the count list to match the order I actually walked the shelves — counting in storage-category order is a fight every time.*

That's the operations side. From [[raw/tickets/NXT-52772|NXT-52772 — Review Completed Inventory: Reconcile]], paraphrased: *give me one consolidated screen to reconcile a site's whole period count, not one variance at a time.* That's the supervisor / accounting side. The corpus shows continuous investment on both ends: filtering and grouping for the warehouse manager doing the count ([[raw/tickets/NXT-10482|NXT-10482 — Filter out Storage & Item Categories]], [[raw/tickets/NXT-10483|NXT-10483 — Filter Storage & Item Category]]), and a consolidated review-and-reconcile screen for the inventory supervisor closing the period ([[raw/tickets/NXT-52157|NXT-52157 — Review Completed Inventory: Items]], [[raw/tickets/NXT-53252|NXT-53252 — Review Completed Inventory: Report updates]]). Adjustments out of the reconcile flow are what eventually post into Financials.

## How it connects

Inventory sits between three other modules. Items defined in [[concepts/Item-Management|Item Management]] flow in via receipts; recipes from there consume them in [[concepts/Production|Production]]. Physical-count adjustments roll forward into [[concepts/Financials|Financials]] for GL postings and trial balance. The two workflows on top of this concept are [[workflows/orders-purchasing|Create & Receive Orders]] (the daily flow) and [[workflows/physical-inventory|Physical Inventory Count]] (the periodic reckoning).

## Open questions

- **Internal vendors are an open build-out.** The vendor-type change ([[raw/tickets/NXT-1840|NXT-1840]]) introduced internal vendors and the warehouse direction; the corpus shows continuing engineering on the seasonal-contract and ordering-condition implications. It does not show how many districts have actually configured an internal vendor end-to-end versus how many are still on the external-vendor model.
- **Hotshot Distributions is shipping but undocumented as a workflow.** Recent tickets ([[raw/tickets/NXT-67614|NXT-67614 — Hotshot Distributions: Pre-generate Order & Receipt]], [[raw/tickets/NXT-67615|NXT-67615 — Cancel Orders on Revert Shipment]], [[raw/tickets/NXT-67617|NXT-67617 — Assign through Ship]]) trace a deliberate evolution from manual to assignment-based distribution. It deserves its own workflow page; the corpus has the material, the wiki doesn't yet.
- **Receipt-edit-after-close is intentional, but its trade-offs aren't quantified.** The corpus shows the rule (edit until the period closes); it doesn't show how often the rule lets a real correction through versus how often it lets a stale edit slip in.

---

*Compiled from 850 tickets across 106 sprints. Last refreshed 2026-05-01. Source tickets are listed in [the ticket index](../../tickets.html).*
