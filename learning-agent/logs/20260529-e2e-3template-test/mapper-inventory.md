# Feature Inventory — Item Management

**Source transcript:** `raw/transcripts/20260529-070600-item-management-2026-05-28-item-management-create-items-training.md`
**Presenter:** Sarah Chen (Implementation Specialist) | **Training date:** 2026-05-15 | **Recording:** REC-2026-0515-IM-001
**Audience:** Brunswick County Schools onboarding cohort (~12 staff)
**Mapped:** 2026-05-29 (Task 1, mapper agent, live NXT Jira)

---

## Matched Features

| # | Feature / Workflow | Transcript [MM:SS] | Ticket | Epic | Priority | RN Visibility | Confidence |
|---|---|---|---|---|---|---|---|
| 1 | Item card — required and optional fields (Item Description 250-char limit, Item Category, Storage Category, Valuation Group required for Inventory; Tags, Brand, Manufacturer, Product Code optional) | [02:01]–[03:10] | NXT-30036 / NXT-30037 | NXT-30027 | High | None | Medium — AC minimal; field detail in Description only |
| 2 | Food vs. Non-Food selection on Units card | [04:15]–[04:30] | NXT-35898 | NXT-36067 | High | None | High |
| 3 | Fluid vs. Non-Fluid question (food only; grams vs milliliters) | [13:10]–[13:25] | NXT-35898 | NXT-36067 | High | None | High |
| 4 | Adding pack sizes with Higher/Lower prompt | [05:18]–[06:52] | NXT-37110 | NXT-36067 | High | None | High |
| 5 | Three-tier maximum pack size limit | [07:05]–[07:30] | NXT-37110 | NXT-36067 | High | None | Medium — cap not stated verbatim in AC |
| 6 | Unit identifiers column (P / BU / MI badges) | [07:30]–[07:52] | NXT-37109 | NXT-36067 | Medium | None | High |
| 7 | Base Unit auto-assignment (lowest level) | [07:52]–[08:08] | NXT-37111 | NXT-36067 | High | None | High |
| 8 | Costing / Missing Costing — one-unit entry + auto-scale; Manage Costing | [08:08]–[09:05] | NXT-37568 | NXT-36067 | Medium | None | High (formula in Description) |
| 9 | Inventory Ready flag / Publish toggle | [09:05]–[09:18] | NXT-53530 + NXT-37068 | NXT-45562 + NXT-36067 | High | None | High |
| 10 | GTIN/UPC barcode entry (8–14 digits) | [09:18]–[09:48] | NXT-37815 | NXT-37500 | Medium | None | High |
| 11 | Whole Numbers vs Decimals setting (locks once used in Inventory) | [09:48]–[10:20] | NXT-33518 | NXT-36067 | Low | None | High |
| 12 | Images & Documents card (5 MB/file; Use As dropdown; food + non-food) | [10:28]–[11:55] | NXT-41273 | NXT-40487 | Medium | External/Internal | High |
| 13 | Adding serving sizes (food); oz→g auto-conversion | [13:52]–[14:12] | NXT-35898 | NXT-36067 | High | None | High |
| 14 | Serving↔Pack linking for Inventory Eligibility | [15:02]–[16:08] | NXT-37441 | NXT-36067 | Highest | None | High |
| 15 | Base Unit promotion / Dual Unit (food only) | [16:48]–[17:42] | NXT-40778 | NXT-45562 | High | None | High |
| 16 | Inventory-eligibility lock behavior (Base Unit + Decimals lock post-use) | [37:35]–[38:05] | NXT-54229 | NXT-45562 | High | None | High |
| 17 | Nutrient Info — Nutrient Details card (USDA nutrients; Missing Value; Per-100g + %DV auto) | [18:55]–[20:42] | NXT-43239 | NXT-40487 | High | External/Internal | High |
| 18 | Ingredient Info — Edible Yield Factor | [20:42]–[21:00] | NXT-47249 / NXT-30100 | NXT-45562 / NXT-30027 | Medium | Ext/Int (NXT-47249) | Medium — version conflict, see notes |
| 19 | Ingredient Info — Sub Ingredients + Standard Recipe Directions | [21:00]–[21:22] | NXT-30100 | NXT-30027 | Low | None | Medium |
| 20 | Ingredient Info — Locally Grown + Buy American (exemption letter logic) | [21:22]–[21:42] | NXT-30100 | NXT-30027 | Low | None | Medium |
| 21 | Contribution Info — Meal Pattern contribution | [21:52]–[22:20] | NXT-30102 + NXT-37216 | NXT-30027 + NXT-51260 | Med + High | None | Low — field names from Description; mark [TO VERIFY] |
| 22 | Allergen Info — standard allergens + status forms | [22:20]–[23:10] | NXT-30103 + NXT-41275 | NXT-30027 + NXT-40487 | Med + Low | None | High |
| 23 | Allergen Feature Disclaimer | [22:20]–[22:42] | NXT-30103 | NXT-30027 | Medium | None | High |
| 24 | Custom Allergens — adding to an item | [23:10]–[24:02] | NXT-30103 + NXT-24128 | NXT-30027 + NXT-13780 | Medium | None | High |
| 25 | Custom Allergens — Configuration page (IM > Configuration > Item Configuration) | [23:28]–[23:55] | NXT-24128 | NXT-13780 | Medium | None | High |
| 26 | Menu Info — Direct Menu Item creation (food only) | [24:30]–[27:22] | NXT-39594 | NXT-29833 | High | None | High |
| 27 | Menu Item card — required + optional fields | [25:28]–[27:12] | NXT-30155 + NXT-39594 | NXT-30027 + NXT-29833 | High | None | Medium |
| 28 | Show on POS toggle (reveals POS attributes + POS Pricing tab) | [27:12]–[27:32] | NXT-39594 | NXT-29833 | High | None | High |
| 29 | Menu Item Serving — add scaled servings (+ MENU SERVING) | [27:32]–[27:55] | NXT-40447 | NXT-29833 | Medium | None | High |
| 30 | Menu Item Serving Exceptions (NOT SERVED by group) | [27:55]–[28:18] | NXT-54229 | NXT-45562 | High | None | Low — no dedicated story; mark [TO VERIFY] |
| 31 | HACCP / Steps — Enable Recipe + HACCP Process (Step 0) | [28:18]–[29:10] | NXT-36583 | NXT-26823 | High | None | High |
| 32 | HACCP / Steps — Add Recipe Steps + Control Points (CCP) | [29:10]–[29:55] | NXT-36742 | NXT-26823 | High | None | High |
| 33 | POS Pricing — Student grid (Set All Prices, Allow Sale) | [29:55]–[30:55] | NXT-30155 | NXT-30027 | High | None | Medium |
| 34 | POS Pricing — Adults grid + Taxable checkbox | [31:08]–[31:48] | NXT-58442 | NXT-51260 | High | None | High |
| 35 | Inventory Info tab — vendor contract display (read-only) | [32:05]–[32:40] | NXT-40479 | NXT-37500 | Low | None | High |

## Unmatched Items (cataloged, not dropped)

| # | Reference | [MM:SS] | Reason |
|---|---|---|---|
| 1 | Item Description 250-char limit | [02:01] | No ticket specifies limit; presenter said "I think". [TO VERIFY] |
| 2 | Item/Storage/Valuation required-for-Inventory guidance | [02:22]–[02:50] | Presenter recommendation, not a ticketed feature |
| 3 | Sub-qty = standard spec; short-ships handled in receiving | [10:43]–[11:02] | Implementation advice (process opinion) |
| 4 | Tabs grayed out until Units card saved | [14:12]–[14:30] | UI state; in NXT-35898 desc, not AC |
| 5 | "Don't fix costing until all packs added" banner | [05:45]–[05:55] | Sequencing UX; NXT-37568 desc, not AC |
| 6 | Nutrient save-block + item usable in Inventory while Incomplete | [35:02]–[35:35] | Partially NXT-43239; specific claim not in AC |
| 7 | Missing Value "(M)" report marker | [35:35]–[36:05] | NXT-43239 covers checkbox, not "(M)" report semantics |
| 8 | Costing auto-scale formula (80/20=4; 4/25=0.16) | [08:32]–[08:52] | Demonstrated; algorithm not in any AC |
| 9 | Bulk allergen import | [24:02]–[24:30] | **Presenter-uncertain** — exclude from content |
| 10 | Copy item feature | [33:11]–[33:35] | **Presenter-uncertain** — exclude (NXT-56820 bug exists; unverified) |
| 11 | Catalog/corporate DB item import | [33:35]–[34:00] | **Presenter-uncertain** — exclude |
| 12 | 4th-tier receiving workaround | [36:48]–[37:00] | Cross-module (Inventory) + presenter-uncertain |
| 13 | Sales tax rate configuration | [31:20]–[31:48] | Presenter-uncertain; scoped to business office |

## Cross-Module References (flag, do not import)

| # | Topic | Module | [MM:SS] |
|---|---|---|---|
| 1 | Item used in Inventory; lock on Base Unit/Decimals | Inventory | [03:50], [37:35]–[38:05] |
| 2 | Vendor contracts created/managed in Inventory | Inventory | [32:05]–[32:40] |
| 3 | Short-ship handled in receiving | Inventory | [10:43]–[11:02] |
| 4 | Serving sizes basis for Recipe ingredient usage | Recipes | [13:25]–[13:52] |
| 5 | Sub Ingredients / Recipe Directions flow to recipes | Recipes | [21:00]–[21:22] |
| 6 | Nutrient analysis runs in Menu Planning | Menu Planning | [35:02]–[35:35] |
| 7 | Marketing Name & Description → Family Hub | Family Hub | [26:15]–[26:48] |
| 8 | Bulk allergen import (PrimeroEdge legacy ref) | PrimeroEdge | [24:02]–[24:30] |
| 9 | Copy item (PrimeroEdge legacy ref) | PrimeroEdge | [33:11]–[33:35] |
| 10 | Pallet / 4th-tier receiving workaround (Justin, Inv PM) | Inventory | [36:48]–[37:00] |
| 11 | "Items → recipes & menu planning" next session | Recipes + Menu Planning | [37:00] |

## Tickets Touched (for prefetch)

**Epics:** NXT-45562, NXT-36067, NXT-30027, NXT-26823, NXT-29833, NXT-40487, NXT-40775, NXT-51260, NXT-13780, NXT-37500
**Stories:** NXT-37441, NXT-37110, NXT-35898, NXT-33518, NXT-37568, NXT-37109, NXT-37111, NXT-40778, NXT-54229, NXT-53530, NXT-37068, NXT-37815, NXT-41273, NXT-43239, NXT-47249, NXT-30100, NXT-30102, NXT-30103, NXT-24128, NXT-41275, NXT-37216, NXT-39594, NXT-39663, NXT-40447, NXT-36583, NXT-36742, NXT-30155, NXT-58442, NXT-40479

## Mapping notes for downstream agents

1. **Contribution Info (#21)** — weakest grounding. Meal-pattern field names from Description only → mark [TO VERIFY].
2. **Edible Yield Factor (#18)** — version conflict: NXT-47249 AC moves it to the Units card; presenter showed it in Ingredient Info at [20:58]. Mark [AMBIGUOUS], verify current UI placement.
3. **Menu Item Serving Exceptions (#30)** — no dedicated story AC; transcript is primary voice; mark field names [TO VERIFY].
4. **Three-tier maximum (#5)** — stated as hard constraint; not verbatim in AC; flag for editor cross-check.
5. **Roles & permissions (long-form §2)** — not demonstrated in transcript. NXT-53316 "IM - Configuration - Roles & Permissions" governs the Configuration page permission structure. Its AC is the permission list; its Description ("As a district admin I want permissions for the Configuration page…") is TIER 3 — do NOT cite that line as AC. See evidence cache.
