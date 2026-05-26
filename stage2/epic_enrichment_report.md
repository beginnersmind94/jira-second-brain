# Epic enrichment report (Stage 2 / Workstream 0)

_Generated 2026-05-01T17:58:34.882337+00:00_

- Source: `cleaned/tickets_clean.csv` + `ticket_links_long.csv`
- Working corpus (Bug + Story): **2,051** rows

## Coverage

### Stories

- With `parent_key` set: **667** / 673 (**99.1%**)
- With Epic name resolved (parent Epic also in this export): **633** / 673 (**94.1%**)
- Stories whose `parent_key` points outside this export: **34**

### Bugs

- With at least one Story linked via Relates/Blocks/Cloners: **508** / 1378 (**36.9%**)
- With Epic name resolved: **506** / 1378 (**36.7%**)

Bug→Epic coverage exceeds the 20% load-bearing threshold (36.7%). Epic context is genuinely useful for Bugs.

### Combined

- Tickets in working corpus with any Epic association (`associated_epic_key` set): **1,175** (57.3%)

### Link path distribution

| epic_link_path | count |
| --- | ---: |
| none | 876 |
| direct_parent | 667 |
| via_linked_story | 508 |

## Top 10 Epics by associated-ticket count

| epic_name | tickets |
| --- | ---: |
| IM - Bulk Item Onboarding - Ingredient Info | 91 |
| IM - List Page & Nav Updates | 85 |
| IM - Bulk Item - Local Updates | 80 |
| IM/INV - Business Rule & Validation Enhancements | 70 |
| IM - Usability & UX Enhancements (8.X) | 60 |
| IM - Item Onboarding- Excel Import/Export & Local Publishing | 59 |
| IM - UI Improvements | 51 |
| IM - Bulk Inventory & Direct Menu Item Onboarding | 47 |
| IM - Units Card Overhaul | 45 |
| IM - Item Units & Sub-types | 41 |

## Bugs with multiple linked Stories (top 10)

Originating Story is picked as the earliest-created. The full linked-Story list is preserved in the count column for traceability.

| bug | linked_story_count | originating_story (earliest) | epic_name |
| --- | ---: | --- | --- |
| NXT-60361 | 5 | NXT-41562 | IM - Bulk Item Onboarding - Ingredient Info |
| NXT-60820 | 4 | NXT-41658 | IM - Bulk Item Onboarding - Ingredient Info |
| NXT-59279 | 3 | NXT-41658 | IM - Bulk Item Onboarding - Ingredient Info |
| NXT-48826 | 3 | NXT-41623 | IM/MP - Find & Replace |
| NXT-70017 | 2 | NXT-67596 | IM - Bulk Item - Local Updates |
| NXT-50478 | 2 | NXT-46863 | IM - List Page & Nav Updates |
| NXT-44398 | 2 | NXT-41273 | IM - Production Usability Enhancements (2023) |
| NXT-44400 | 2 | NXT-41273 | IM - Production Usability Enhancements (2023) |
| NXT-44436 | 2 | NXT-41273 | IM - Production Usability Enhancements (2023) |
| NXT-45772 | 2 | NXT-34237 | IM - List Page & Nav Updates |

## How `epic_link_path` is assigned

- `direct_parent` — Story's `parent_key` resolves to an Epic
- `via_linked_story` — Bug has at least one Story linked through Relates/Blocks/Cloners (earliest-created Story wins on ties)
- `none` — neither path produced an Epic association

## Definition-of-done for Workstream 0

- `tickets_in_scope.csv` exists with 2051 rows: **True**
- `epic_enrichment.csv` exists with one row per in-scope ticket: **True**
- Story→Epic coverage acknowledged: **99.1%** of Stories carry parent_key
- Bug→Epic coverage acknowledged: **36.7%** of Bugs resolve to a named Epic (threshold: 20%; status: **load-bearing**)
