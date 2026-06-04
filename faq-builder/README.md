# FAQ Builder

Pipeline that turns Freshdesk customer-conversation history into per-function PrimeroEdge FAQ documents (`.docx` + `.pdf`).

> **Building a new FAQ? Follow [`SOP.md`](SOP.md)** — the step-by-step playbook (fetch → spec → coverage reconciliation → build → rejected register → verify). This README is the map; the SOP is the procedure.

## What it does

```
Freshdesk API
     │
     ▼
fetch/fetch_conversations.py   ──▶   conversations/conversations.jsonl + _digest.txt
fetch/fetch_function.py        ──▶   conversations/conversations_<function>.jsonl
fetch/fetch_ingredients.py     ──▶   conversations/conversations_ingredients.jsonl
fetch/fetch_batch.py           ──▶   conversations/conversations_batch.jsonl
     │
     ▼ (human reviews digests, drafts content spec)
build/specs/<function>_spec.py
build/apply_wiki_framing.py
build/augment_specs.py
build/patch_standalone.py
     │
     ▼
make_<function>_faq.py / make_all_faqs.py
     │
     ▼
faq_builder.py     (shared library: spec → .docx → .pdf via pywin32 + MS Word)
     │
     ▼
deliverables/PrimeroEdge-<Function>-FAQ.{docx,pdf}
```

## Directory layout

```
faq-builder/
├── README.md                   # You are here
├── faq_builder.py              # Shared builder library: build(spec) → .docx + .pdf
├── make_all_faqs.py            # Assembles every function FAQ from build/specs/*_spec.py
├── make_ingredients_faq.py     # Standalone builder for the Ingredients FAQ
├── make_menu_cycles_faq.py     # Standalone builder for the Menu Cycles FAQ
├── fetch/                      # Freshdesk fetchers
│   ├── fetch_conversations.py  # Generic: pull tickets + all conversation pages
│   ├── fetch_batch.py          # Ad-hoc list of Freshdesk tickets for analysis
│   ├── fetch_function.py       # Pull conversations for a specific function
│   └── fetch_ingredients.py    # Ingredients-specific fetch
├── build/                      # Content-spec authoring + augmentation
│   ├── specs/                  # Per-function content specs (one .py module per FAQ)
│   ├── guides/                 # Source guide material consulted by specs
│   ├── apply_wiki_framing.py   # Apply wiki framing/voice to draft specs
│   ├── augment_specs.py        # Augment specs with additional sourced content
│   └── patch_standalone.py     # Patch standalone make_*.py builders
├── conversations/              # Cached Freshdesk pulls (input data)
│   ├── conversations.jsonl                 # Combined dump
│   ├── conversations_<function>.jsonl      # Per-function dumps
│   ├── conversations_<function>_digest.txt # Human-readable digests
│   ├── conversations_batch.jsonl           # Ad-hoc batch (raw)
│   ├── conversations_batch.json            # Ad-hoc batch (structured)
│   └── conversations_digest.txt            # Top-level digest
└── deliverables/               # Final FAQ docs handed off to customers / SMEs
    └── PrimeroEdge-<Function>-FAQ.{docx,pdf}
```

## Functions covered (current)

| Function | Spec | Deliverable |
|---|---|---|
| Assign Menus | `build/specs/assign_menus_spec.py` | `deliverables/PrimeroEdge-Assign-Menus-FAQ.{docx,pdf}` |
| Ingredients | `build/specs/ingredients_spec.py` (or `make_ingredients_faq.py` standalone) | `deliverables/PrimeroEdge-Ingredients-FAQ.{docx,pdf}` |
| Menu Cycles | `build/specs/menu_cycles_spec.py` (or `make_menu_cycles_faq.py` standalone) | `deliverables/PrimeroEdge-Menu-Cycles-FAQ.{docx,pdf}` |
| Perpetual Inventory | `build/specs/perpetual_inventory_spec.py` | `deliverables/PrimeroEdge-Perpetual-Inventory-FAQ.{docx,pdf}` |
| Production Orders | `build/specs/production_orders_spec.py` | `deliverables/PrimeroEdge-Production-Orders-FAQ.{docx,pdf}` |
| Receipt w/o Order | `build/specs/receipt_wo_order_spec.py` | `deliverables/PrimeroEdge-Receipt-wo-Order-FAQ.{docx,pdf}` |
| Transfer Items | `build/specs/transfer_items_spec.py` | `deliverables/PrimeroEdge-Transfer-Items-FAQ.{docx,pdf}` |

## Prerequisites

- **Windows + Microsoft Word** — `faq_builder.py` converts `.docx` → `.pdf` via Word COM automation (`pywin32`). No cross-platform path.
- **Freshdesk API token** for fetch scripts.
- **Python 3.11+** with `pywin32`, `python-docx`, and `requests`.

## Typical workflow

1. Pull conversations for a function:
   ```
   python fetch/fetch_function.py --function "Assign Menus"
   ```
2. Review `conversations/conversations_<function>_digest.txt` and draft `build/specs/<function>_spec.py`.
3. Build the FAQ:
   ```
   python make_all_faqs.py            # all functions from specs
   python make_<function>_faq.py      # one function (standalone)
   ```
4. Hand off `deliverables/PrimeroEdge-<Function>-FAQ.{docx,pdf}` to the SME for review.

## Relationship to jira-brain

`faq-builder/` is a sibling subproject. Inputs come from Freshdesk (not Jira), so it's independent of `raw/tickets/`. Outputs are customer-facing documents, similar in spirit to `resources/` — but Word/PDF instead of catalog-indexed markdown.

CLAUDE.md anti-hallucination rules still apply: every FAQ claim should trace to a real conversation in `conversations/` or a sourced guide in `build/guides/`. Don't invent capabilities the conversations don't demonstrate.
