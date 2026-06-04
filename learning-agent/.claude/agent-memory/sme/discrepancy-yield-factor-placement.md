---
name: discrepancy-yield-factor-placement
description: Edible Yield Factor was moved from Ingredient Info card to Units card per NXT-47249 AC. Presenter Sarah Chen still describes it on Ingredient Info — this is a known recurring discrepancy in Item Management training.
metadata:
  type: project
---

Edible Yield Factor is NOT on the Ingredient Info card. Per NXT-47249 AC: "Remove Yield Factor from Ingredient Info card (moved to Units)" and "Make Yield Factor configurable on each serving in the Units card." Status: Done Done.

Presenter Sarah Chen (REC-2026-0515-IM-001, [20:42]) described it on Ingredient Info — this reflects older product behavior before NXT-47249 shipped.

**Why:** NXT-47249 moved Yield Factor to be serving-specific (per serving on the Units card) rather than a single item-level field on Ingredient Info. Training materials predating this ticket will have the old location.

**How to apply:** In every Item Management fact-check, flag any presenter claim that Edible Yield Factor is on the Ingredient Info card. The correct current location is the Units card (serving-specific, with a dedicated Yield Factor column per NXT-47249 AC). Severity: High — directly affects how staff set up items for recipe calculations.
