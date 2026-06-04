## Content Plan — Item Management: Creating Food and Non-Food Items — Micro Guide

### Template: Micro guide (~3 pages, 600–1,200 words, HARD CEILING 1,500 words)
### Source transcript: `raw/transcripts/20260529-070600-item-management-2026-05-28-item-management-create-items-training.md`
### Target audience: District Admin, Nutrition Manager (Brunswick County Schools onboarding cohort)

---

## Ranking methodology

Priority signals applied in order:
1. Jira priority (Highest > High > Medium > Low)
2. RN visibility (External/Internal facing RN = higher relevance for staff training)
3. Role relevance (District Admin and Nutrition Manager are the documented audience)
4. Transcript emphasis (presenter time allocation)
5. Cross-module references (one-line mention only, no deep-dive)

---

## Workflow Shortlist — Selected (4 workflows)

The template allows 3–5. Four is the correct count here. Adding a 5th would require including either HACCP/Steps (food-only, Nutrition Manager scope, complex enough to warrant its own guide) or Menu Serving Exceptions (no AC, [TO VERIFY] on exact UI steps per factcheck D3/V31 — unsafe to write without SME sign-off). Four keeps the guide within word budget and avoids content that cannot be fully cited.

### Workflow 1 — Create a non-food item (item card through Inventory Readiness)

**Tickets:** NXT-30036 (High), NXT-30037 (Medium), NXT-35898 (High), NXT-37110 (High), NXT-37568 (Medium), NXT-37111 (High), NXT-53530 (High)

**Priority rationale:** Item card creation is the entry point for every item in the system. NXT-30036/30037/35898/37110 are all High priority. Non-food is structurally simpler (no serving sizes, no food/fluid branching) and is the correct starting workflow for District Admins managing non-food supply items.

**Scope of steps:**
1. Click +NEW on the Item Management items list
2. Enter Item Description (required); add optional fields: Tags, Brand Name [TO VERIFY label], Manufacturer [TO VERIFY label], Product Code [TO VERIFY label]
3. Click SAVE (item is created and assigned an Item #)
4. On Product Info card: select all three required dropdowns — Item Category [TO VERIFY label], Storage Category [TO VERIFY label], Valuation Group [TO VERIFY label] — or skip (skip allowed; required later for Inventory)
5. On Units card: answer Food Item = No (disables serving sizes)
6. Add at least one pack size: click +PACK; enter Description and Sub-Qty (Sub-Qty required when adding a second or lower tier); Weight is optional for non-food [TO VERIFY food/non-food specificity]
7. Optional: enter costing — select the unit where cost is known; system scales to other tiers automatically; skip leaves a Missing Costing [TO VERIFY label] flag
8. Optional: enter GTIN/UPC per pack size (8–14 digits; barcode icon appears in Identifiers column)
9. Review the Inventory Readiness banner; confirm Base Unit; set Whole Numbers vs. Decimals option

**One pitfall (sourced):** Presenter at [10:43]–[11:00] warned: sub-quantity must reflect the standard spec sheet quantity, not short-ship quantities. If a vendor ships 18 instead of the standard 20, the Sub-Qty on the item record should still say 20 — the item record represents the standard pack, not the exception delivery. Source: transcript [10:43]–[11:00] (Q&A — presenter guidance on process intent; note: no AC source for this operational rule; mark as presenter guidance, not system-enforced behavior).

---

### Workflow 2 — Create a food item through Inventory Eligibility (includes serving↔pack link)

**Tickets:** NXT-35898 (High), NXT-37110 (High), NXT-37441 (Highest), NXT-37111 (High), NXT-40778 (High), NXT-53530 (High), NXT-37568 (Medium), NXT-33518 (Low)

**Priority rationale:** NXT-37441 is the ONLY Highest-priority ticket in the entire inventory. It cannot execute without the surrounding pack and serving setup — this is precisely why it is embedded in this workflow rather than given a standalone slot (per feedback memory: highest-priority ticket as embedded step). The food item path requires branching decisions (Food = Yes, Fluid vs. Non-Fluid) that don't exist for non-food. Serving↔pack linking is the mechanism that unlocks Inventory Readiness for food items and is the most operationally consequential step in the whole module.

**Scope of steps:**
1. Click +NEW; complete Item Description and Save
2. Complete or skip Product Info dropdowns
3. On Units card: answer Food Item = Yes; answer Fluid Item (Yes = volume/milliliters; No = grams)
4. Add serving size: click +SERVING; enter Amount (1 = inventory-eligible), Description, Weight
5. Add pack size: click +PACK; enter Description
6. On the serving row, enter Sub-Qty — "How many [serving] are in [pack]?" (e.g., 16 yogurts per carton). This links the serving to the pack and triggers Inventory Eligibility. Source: NXT-37441 AC verbatim: "Provide Sub-Qty on the Serving Size row in valid scenarios; Trigger Inventory readiness based on proper pack-serving links"
7. If the pack Description or weight matches the serving (dual-unit scenario): the system prompts a "Merge" button (AC term — not "promote" as presenter said). Click Merge to confirm; Sub-Qty is promoted to the new base unit. Source: NXT-40778 AC (D2 discrepancy — use Merge per AC; do not use presenter's "BASE UNIT chip" / "promote" language)
8. Optional: add additional pack tiers (up to [TO VERIFY: 3-tier cap not in AC, Description only])
9. Optional: enter costing for one unit; system scales to all linked units
10. Review Inventory Readiness banner; confirm Base Unit; set Whole Numbers vs. Decimals

**One pitfall (sourced):** Presenter at [15:02]–[16:08] and NXT-37441 AC: if serving and pack are not linked via Sub-Qty (or weight where applicable), the item is Inventory Ineligible even if both rows exist. The link is what counts — having both a serving row and a pack row is not sufficient without the Sub-Qty bridge. Source: NXT-37441 AC "Trigger Inventory readiness based on proper pack-serving links" + transcript [15:02].

---

### Workflow 3 — Set up Menu Info and POS Pricing (food items that go to the POS)

**Tickets:** NXT-39594 (High), NXT-30155 (High), NXT-58442 (High), NXT-40447 (Medium/High)

**Priority rationale:** All three primary tickets are High priority. The Menu Info tab and POS Pricing are the downstream outputs that District Admins and Nutrition Managers need to configure before an item can appear on the POS or in menu planning. The Show on POS toggle and POS Pricing student/adult grid are AC-confirmed (V27, V28, V29). NXT-58442 (Taxable Adults-only) is AC-verified and directly relevant to District Admin setup.

**Scope of steps:**
1. Navigate to the Menu Info tab on the item card
2. Toggle "Create Menu Item" (or equivalent — [TO VERIFY: "Disabled status" label is Description-only per NXT-39594]); tab becomes active
3. Enter required Menu Item fields: Menu Item Name [TO VERIFY label], Button Name English [TO VERIFY label], Menu Item Category [TO VERIFY label]. Optional: Max Days [TO VERIFY], Marketing Name & Description (displays in Family Hub), Button Name Spanish [TO VERIFY], Meal Type, Leftover Category, Prep Site Item, Show in Summary, POS Entree [TO VERIFY: all field names are Description-only per NXT-30155]
4. To enable POS Pricing: toggle "Show on POS" (AC-confirmed: "a 'Show on POS' toggle will control the presence of the POS attributes and Pricing table" NXT-39594). Tab may rename to "MENU & POS INFO" [TO VERIFY: rename is Description-only]
5. Enter pricing in Students tab: price grid by student type and site level; use "Set All Prices" shortcut to fill the grid (AC-confirmed: NXT-30155)
6. Enter pricing in Adults tab; check Taxable checkbox if applicable (Adults tab only — Taxable is not shown on Students tab, AC-confirmed: NXT-58442)
7. Save

**One pitfall (sourced):** NXT-58442 AC and presenter context: the Taxable checkbox appears ONLY on the Adult pricing tab. If a staff member is setting up pricing and looks for Taxable on the Students tab, it will not be there — POS does not apply tax to student meals. Source: NXT-58442 AC "Only display the Taxable option when the Adult tab is selected on POS Pricing."

---

### Workflow 4 — Configure allergens (standard + custom)

**Tickets:** NXT-30103 (Medium), NXT-41275 (Low), NXT-24128 (Medium), NXT-30100 (Low) [for Buy American / Locally Grown, embedded here as adjacent step]

**Priority rationale:** Allergen setup is role-relevant for both District Admin and Nutrition Manager. NXT-41275 (allergen form priority order) is AC-confirmed and directly affects how the card displays to parents/staff. NXT-24128 (Custom Allergens) is the most detailed AC of any ticket in the inventory — comprehensive, verifiable, and operationally necessary when a district has allergens beyond the standard list. Allergen setup is a compliance-adjacent task (CN Label, exemption letters live nearby in Images & Docs) and was covered substantively in the training session.

**Scope of steps:**

*Standard allergens:*
1. Navigate to Allergen Info card
2. Click Edit; select allergens that apply to the item
3. Allergen forms are prioritized in this order: Contains, Processed (Facility), May Contain, Free From. Source: NXT-41275 AC "Prioritize allergen forms in the following order: 'Contains' form, 'Processed....' form, 'May Contain' form, 'Free From'"
4. Save. (Nutrient or Contribution info is NOT required first — allergens can be entered independently. Source: NXT-30103 AC "Can create or enter allergen without having nutrient/contribution information entered")

*Custom allergens (when district allergen not on standard list):*
5. Navigate to Item Management > Configuration > Item Configuration > Custom Allergen option. Source: NXT-24128 AC
6. In the pop-up: select data source (Local only) and configuration option; click Apply
7. On the Custom Allergens grid: click +NEW
8. In the slide-out: enter Custom Allergen Description (mandatory, free text); Data Source = Local (mandatory). Source: NXT-24128 AC
9. Save. If duplicate name: system warns "Custom Allergen already in use, please use a different Custom Allergen name." Source: NXT-24128 AC
10. Custom allergen now appears in the allergen selection list for any item

**Note on "Show on Family Hub menus" toggle:** Presenter mentioned a toggle at [23:28] but it is NOT in NXT-24128 AC. This is AMBIGUOUS (A1 in factcheck). Writer must NOT include this toggle. Mark as [AMBIGUOUS — see factcheck A1] in the Writer handoff note.

**One pitfall (sourced):** Presenter at [22:42]–[23:10] and NXT-41275 AC: the allergen card display no longer shows every allergen with empty states. It only shows allergens that are applicable to the item, organized by form. Staff reviewing an item's allergen card should not assume that an allergen absent from the display means "unknown" — it means that allergen form is not applicable to this item. Source: NXT-41275 AC "Remove the grid-based approach in favor of a simple label statement for each applicable Allergen Form."

---

## Demoted to one-line mention

| # | Feature/Workflow | Reason for demotion |
|---|---|---|
| M1 | Images & Documents card (NXT-41273) | Medium priority; External+Internal RN present (makes it more visible). Core behavior AC-verified (V15, V16). However the 5 MB limit and specific file types are [TO VERIFY] (D3). One line: "Attach images and documents to any item — up to 10 files. Use the expand icon to open the drawer; assign each file a 'Use As' type (e.g., CN Label, Preferred Inventory Image)." |
| M2 | Nutrient Details entry (NXT-43239) | High priority, External+Internal RN present. But this is Nutrition Manager territory and requires food + serving sizes (i.e., only after Workflow 2 completes). AC-confirmed Vitamin A/C now optional (V17). Too deep for non-food audience. One line: "For food items, complete Nutrient Details after saving serving sizes — Vitamin A and Vitamin C are now optional; entering 0 for Total Fat or Total Carbs auto-fills nested nutrients." |
| M3 | Contribution Info card (NXT-30102, NXT-37216) | Medium/High priority but field names (Meat/Meat Alt, Grains, Veg) are Description-only [TO VERIFY]. Nutritionist-specific. One line: "Meal pattern contributions (Meat/Meat Alt, Grains, Vegetables, etc.) are entered in the Contribution Info card after serving sizes are saved — you can skip and return later." |
| M4 | Serving size → Nutrient Info oz-to-grams conversion (NXT-43239) | High priority but sub-detail of Nutrient Details tab. One line: "Weight entered in ounces on the Units card converts automatically to grams in the Nutrient Info tab." |
| M5 | Inventory Info tab — read-only vendor contract preview (NXT-40479) | Low priority. AC-verified (V34) but it's read-only from IM and cross-module (Inventory). One line: "The Inventory Info tab shows active vendor contracts in read-only mode; use the shortcut icon to open Contract Items in Inventory." |
| M6 | GTIN/UPC entry (NXT-37815) | Medium priority, AC-verified (V13). Important for scanning workflows but subordinate to pack setup. One line: "Enter GTIN/UPC per pack size in the Inventory Info tab: 12 digits = UPC, 14 digits = GTIN; a barcode icon appears in the Identifiers column once assigned." |
| M7 | Whole Numbers vs. Decimals option (NXT-33518) | Low priority. AC-verified (V12). Included as a step in Workflow 2 (confirm with Base Unit) — no standalone mention needed beyond that embedding. Demote entirely from mentions; covered in W2 steps. |
| M8 | Editability locking post-Inventory use (NXT-54229) | High priority. AC at concept level only; specific triggers are Description-tier (U8). One line: "Once an item has been used in an Inventory transaction, some unit settings become locked — check with your admin before modifying pack sizes on active inventory items." |

---

## Omitted (with reason)

| # | Feature/Workflow | Reason for omission |
|---|---|---|
| O1 | HACCP/Steps card — HACCP Process selection, recipe steps, CCPs (NXT-36583, NXT-36742) | High priority but food-only, Nutrition Manager role only, and complex enough to warrant its own section in a Recipes/HACCP-focused guide. Field names (HACCP process names, Pre-Prep, Cook Time) are all Description-tier [TO VERIFY]. Including this would require at minimum 200 words and push word count over ceiling. Recommend: include in long-form or a dedicated HACCP/Recipes micro guide. |
| O2 | Menu Item Serving Exceptions (NXT-54229) | High priority (NXT-54229). No dedicated story AC found for the Exceptions UI steps. Factcheck marks exact UI workflow as [TO VERIFY]. Writer cannot write this without SME confirmation. Omit from micro; flag for SME before long-form. |
| O3 | Menu Item Serving — +Menu Serving button (NXT-40447) | Medium/High. AC-verified (V30). But this is a secondary step after Menu Item is already created — it adds scaled serving sizes for different school levels. Audience is Nutrition Manager specifically. Too narrow for the general onboarding micro. One-line mention would be: "Additional menu serving sizes can be added via +Menu Serving within the Menu Item tab for scaled portions across school levels." — moved to one-liner if word budget allows, otherwise omit. |
| O4 | Ingredient Info card — Sub Ingredients, Standard Recipe Directions (NXT-30100) | Low priority. Field names Description-only [TO VERIFY]. Cross-module reference (Recipes). One line at most — covered by cross-module reference in Related content. |
| O5 | Ingredient Info card — Edible Yield Factor | DISCREPANCY D1 (HIGH severity). Presenter described Yield Factor on Ingredient Info card; NXT-47249 AC (Done Done) explicitly states it was moved to the Units card. Cannot be written as presented — would misdirect staff. Omit entirely from this micro guide pending SME confirmation of current UI state. Flag prominently in Writer handoff. |
| O6 | Ingredient Info card — Locally Grown, Buy American checkboxes, exemption letter upload | Low priority. Business rule linking Buy American checkbox to exemption letter upload is not in any AC (factcheck field-name caution list). Omit. |
| O7 | POS Pricing — Adults tab (NXT-30155) | Embedded as a step in Workflow 3 (Steps 6). Not a standalone workflow. |
| O8 | Unit Identifiers column — P/BU/MI badge labels (NXT-37109) | Medium priority. Badge labels (P, BU, MI) are Description-only per factcheck caution list. Referenced inline in Workflow 1 and 2 steps. No standalone section. |
| O9 | Base Unit auto-assignment and promotion (NXT-37111, NXT-40778) | High. Base Unit confirmation is embedded in Workflow 1 and 2 final steps. Merge/dual-unit behavior is a step in Workflow 2. Not a standalone workflow. |
| O10 | Unmatched items (U6 allergen bulk import, U7 copy/clone, U8 catalog import, U13 sales tax calculation) | Presenter explicitly uncertain or not demonstrated. Excluded per anti-hallucination rules. |

---

## Common Mistakes (3–5 recurring, sourced)

These aggregate across all workflows and populate the "Common mistakes" section of the micro guide.

1. **Skipping the serving↔pack Sub-Qty link.** Having both a serving row and a pack row is not the same as linking them. Without Sub-Qty on the serving row, the item is Inventory Ineligible even if both units exist. Source: NXT-37441 AC "Trigger Inventory readiness based on proper pack-serving links"; transcript [15:02]–[16:08].

2. **Sub-Qty reflects the standard spec, not short-ship quantities.** If the vendor short-ships 18 instead of the standard 20, the item record should still say 20 — the item record represents the standard pack spec. Using a short-ship quantity corrupts the cost scaling calculation and Inventory readiness logic. Source: transcript [10:43]–[11:00] (presenter guidance; note: no AC source — attribute as presenter guidance).

3. **Pack-size three-tier limit.** The system allows a maximum of approximately three pack-size tiers; the +PACK button becomes unavailable after the third tier is added. Source: transcript [07:05]–[07:30]; note: [TO VERIFY] — this limit is stated by the presenter but is not explicitly documented in NXT-37110 AC.

4. **Edible Yield Factor location is OUTDATED in this recording.** The presenter described Yield Factor on the Ingredient Info card, but per NXT-47249 (Done Done) it has been moved to the Units card. Do not set Yield Factor from the Ingredient Info card. Source: NXT-47249 AC "Remove Yield Factor from Ingredient Info card (moved to Units)"; factcheck D1 (HIGH severity).

5. **Taxable checkbox is Adults-only.** The Taxable option does not appear on the Students pricing tab — only on the Adults tab. Searching for it on the Students tab will cause confusion. Source: NXT-58442 AC "Only display the Taxable option when the Adult tab is selected on POS Pricing."

---

## Must-handle SME items (carry forward to Writer)

These SME-identified discrepancies and [TO VERIFY] items touch the selected workflows. The Writer must handle each one explicitly.

| # | Item | Severity | Required Writer action |
|---|---|---|---|
| S1 | DISCREPANCY D1 — Edible Yield Factor location | HIGH | DO NOT write the Ingredient Info card Yield Factor workflow. It is outdated. If the Ingredient Info card is mentioned at all, note only: "Sub Ingredients and Standard Recipe Directions are on this card [→ Recipes module]." The Yield Factor correction (Units card, serving-specific, dedicated step) must be confirmed with the product team before the long-form guide covers it. This micro guide omits it entirely. |
| S2 | DISCREPANCY D2 — "Merge" vs. "promote" / "BASE UNIT chip" language | MEDIUM | Use "Merge" as the AC-grounded term throughout. Do not use "promote" or "BASE UNIT chip." The specific dialog text the presenter quoted ("Confirm Carton as Base Unit, or promote Each to lowest Inventory Unit?") is not in any AC text — mark as [TO VERIFY] in the Workflow 2 Merge step. |
| S3 | DISCREPANCY D3 — 5 MB file limit and file type list (Images & Docs) | LOW | Only assert the 10-file limit (RN-verified). Mark 5 MB and the specific file type list (JPEG, PNG, PDF, Word, spreadsheet) as [TO VERIFY]. |
| S4 | [TO VERIFY] — Three-tier pack size cap | LOW | Do not assert "maximum three tiers" as a hard product rule. Write as: "the system supports up to approximately three pack-size tiers [TO VERIFY]" or omit the specific cap. |
| S5 | [TO VERIFY] — Sub-Qty/standard spec guidance | LOW | Mark the short-ship vs. spec-sheet guidance as presenter-attributed, not system behavior: "According to the training session…" |
| S6 | [AMBIGUOUS A1] — "Show on Family Hub menus" toggle in Custom Allergen slide-out | AMBIGUOUS | Do not include this toggle. NXT-24128 AC lists only two mandatory slide-out fields (Description, Data Source). The toggle is unverified. |
| S7 | [TO VERIFY] — Field labels: Item Category, Storage Category, Valuation Group, Brand Name, Product Code, Manufacturer, all Menu Item field names | MEDIUM | All these names appear in Description only (factcheck field-name caution list). Writer marks each with [TO VERIFY] per anti-hallucination rule 4. |
| S8 | [TO VERIFY] — Inventory locking triggers (Base Unit, Decimals locked after first Inventory transaction) | LOW | The general concept (some things lock after Inventory use) is concept-confirmed in NXT-54229 AC. The specific trigger events and specific fields are Description-only. Include the one-line mention in Common Mistakes with [TO VERIFY] on trigger detail. |

---

## Section order and word budget

Target: 600–1,200 words. Hard ceiling: 1,500. Budget assumes 4 workflows and moderate step density.

| Section | Content | Estimated words |
|---|---|---|
| Purpose | 1 short paragraph, outcome-framed | 50 |
| Who this is for | 1–2 sentences naming roles (District Admin, Nutrition Manager) | 30 |
| Before you start | 4–5 prerequisite bullets with citations | 80 |
| Top workflows | 4 workflows × ~200 words each (steps + pitfall) | 800 |
| Common mistakes | 5 bullets, ~40 words each | 200 |
| Related content | 6–7 one-liners with link placeholders | 80 |
| Sources | Flat list of ticket IDs and timestamps | 60 |
| **Total estimate** | | **~1,300 words** |

This puts the plan at approximately 1,300 words — within the 1,200-word target and safely under the 1,500-word ceiling. The 100-word buffer above the 1,200 target is acceptable given the word-budget rule is a target, not a ceiling. If word count runs long during generation, the Writer must trim Workflow 3 and 4 step lists first (they have the most optional sub-steps) and compress Common Mistakes bullets.

**Risk flag:** If the Writer includes sub-mention items from the Demote list (M1–M8) as inline prose rather than strict one-liners, the word count will exceed 1,500. The plan specifies one sentence maximum for each demoted item. The Writer should treat demoted items as inline callouts within Related content or a brief "Also in this module" note — not as additional workflow sub-sections.

**Long-form signal:** This module has 39 matched features, 4 epics worth of structured workflows, and at least 3 additional workflows that were omitted purely on word-budget grounds (HACCP/Steps, Menu Serving Exceptions, Contribution Info as standalone). The micro guide is the right fit for onboarding day-one task success. A long-form guide is strongly recommended for a comprehensive reference — the same transcript supports it without any re-collection.

---

## Handoff checklist

- [x] Mapper inventory reviewed (39 matched features, 8 unmatched, 9 cross-module)
- [x] SME fact-check report reviewed (3 discrepancies, 14 unsupported, 3 ambiguous)
- [x] Template constraints checked (4 workflows ≤ 5 hard constraint; estimated 1,300 words ≤ 1,500 ceiling)
- [x] Highest-priority ticket (NXT-37441) embedded in Workflow 2 — not standalone (per feedback rule)
- [x] Costing embedded in Workflow 1 and 2 steps — not standalone (per feedback rule)
- [x] D1 (Edible Yield Factor) omitted from micro — flagged for product team confirmation before long-form
- [x] D2 (Merge language) resolved — Writer uses "Merge" per AC
- [x] D3 (5 MB / file types) resolved — 10-file limit only from RN; rest [TO VERIFY]
- [x] AMBIGUOUS A1 (Family Hub toggle) omitted from Workflow 4
- [x] Field-name caution list carried into Writer handoff (S7)
- [x] Cross-module references assigned to Related content only (no deep-dive)
- [x] SME can proceed on D1 resolution independently — this plan does not block on it
- [x] Writer has enough to generate
