---
name: tier-caution-ac-thin-tickets-item-management
description: List of Item Management tickets where AC is thin and key field-level specifics are in Description (TIER 3) only. Writer must use [TO VERIFY] for any specific labels derived from these tickets.
metadata:
  type: reference
---

These tickets have AC that confirms a feature exists but does NOT enumerate field names, labels, or workflow details. Any specific field names cited in learning content must be marked [TO VERIFY] unless sourced from RN (TIER 1).

| Ticket | What AC confirms | What is Description-only (TIER 3 — must [TO VERIFY]) |
|---|---|---|
| NXT-30036 | Description required; Tags and global info fields present | 250-char limit on Item Description; specific field labels (Brand Name, Product Code, Manufacturer) |
| NXT-30037 | 3 dropdowns required if not skipping | Field names: Item Category, Storage Category, Valuation Group |
| NXT-37110 | Pack size add ability; Sub-Qty and Weight concepts | Three-tier maximum hard cap; Higher/Lower prompt behavior |
| NXT-37568 | Optional costing step; FMV required | Auto-scaling calculation formula (divide-down); "Manage Costing" button label |
| NXT-30100 | 1/3-width card exists; does not block next section | Sub Ingredients, Standard Recipe Directions fields; Buy American/Locally Grown checkboxes; Yield Factor (moved per NXT-47249) |
| NXT-30102 | Contributions section loads after serving saved; skip allowed | Specific meal pattern component names (Meat/Meat Alt, Grains, Vegetables, etc.) |
| NXT-39594 | Menu Item tab created; Show on POS toggle controls POS attributes | "Disabled" status label before configuration; tab rename to "MENU & POS INFO" |
| NXT-30155 | POS Info tab enabled; Students/Adults tabs; Set All Prices option | Individual Menu Item fields (Menu Item Name, Button Name, Category, Max Days, Marketing Name, etc.) |
| NXT-36583 | HACCP Process selection exists on Steps | Process names: No Cook, Same Day Service, Complex Food; Pre-Prep Instructions, Prep Time, Cook Time fields |
| NXT-54229 | Long-term editing restrictions exist; Menu Serving and Exceptions gated | Base Unit + Decimal locking trigger (first Inventory transaction) — exact locking rule in Description only |
| NXT-41273 | Images & Docs slideout; Use As dropdown for images and documents | 5 MB file size limit (not in AC or RN); specific file types (JPEG, PNG, Word, spreadsheet — not listed) |

**How to apply:** Before asserting a specific label or field name from these tickets in a learning guide, check whether it appeared in AC or RN. If it only appears in Description, write [TO VERIFY] in the draft for the human editor to confirm against the live product.
