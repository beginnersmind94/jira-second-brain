---
name: unsupported-custom-allergen-family-hub-toggle
description: Presenter claimed a "Show on Family Hub menus" toggle exists on the Custom Allergen creation slide-out. NXT-24128 AC (confirmed live) has no such field — only Custom Allergen Description and Data Source fields. Ambiguous/unsupported.
metadata:
  type: project
---

Sarah Chen [23:28]: "you can toggle on whether it shows on Family Hub menus" when describing Custom Allergen creation at Item Management > Configuration > Item Configuration > Custom Allergens.

NXT-24128 AC (confirmed live 2026-05-29) lists only two fields on the slide-out card: Custom Allergen Description (mandatory, free text) and Data Source (mandatory, Local only). No "Show on Family Hub" toggle is present in AC, RN, or RN Internal (all empty).

**Why:** This may be a feature added after NXT-24128 shipped, a separate unreferenced ticket, or a misremembering. Family Hub is a separate module (C5 cross-module).

**How to apply:** In any Item Management or Family Hub fact-check involving custom allergen configuration, flag the "Show on Family Hub" toggle as unsupported/ambiguous. If a separate ticket covering Family Hub display of custom allergens is found, link it here.
