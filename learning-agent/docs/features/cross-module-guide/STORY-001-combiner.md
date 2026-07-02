# STORY-001 — Deterministic cross-module combiner + grounding

**Status:** `Done ✓` (2026-07-02) — all ACs demonstrated (unit test + real-draft combine, both keyless).  ·  **Points:** 5  ·  **Persona:** trainer/PO producing a cross-module rollup.
**Depends on:** `demo._load_fixture`, `demo.validate_citations`, `demo_d.assemble` output shape, `pdf_export.render_html_to_pdf`. **Epic:** [Cross-module combined guide](EPIC.md)

## Scope
**In:** `multi_doc.union_fixture(modules)`, `multi_doc.combine(parts, title, fixture)`, a CLI that
combines existing single-module draft HTML into one grounded doc (+ optional PDF), the combined draft's
metadata, a deterministic test, a real-draft proof.
**Out:** generating the per-module docs (reuses existing path; not this story), the intent-agent offer,
any change to `validate_citations` itself (it is *reused* unchanged on the union).

## Requirements
1.1 `union_fixture(modules)` returns `{module, tickets, epics}` = the union of each module's fixture;
ticket keys are globally unique so no key is dropped or overwritten.
1.2 `combine(parts, title, fixture)` where `parts=[(module_label, draft_html)]` returns one HTML doc:
a single `<h1>{title}`, then per part a `<h2>{module_label}</h2>` + that draft's **body** (its `<h1>` and
its trailing `Sources` section stripped, all `<!-- Source: -->` comments preserved verbatim), then one
merged `<h2>Sources</h2>` listing every cited issue key across all parts (deduped, sorted).
1.3 The combined doc, validated by `demo.validate_citations` with `_FIX = union_fixture(modules)`,
reports `tier_lie=0` and `quote_not_found=0` **iff** every source draft was itself clean.
2.1 CLI `python multi_doc.py <rid> <rid> … [--title T] [--pdf]`: reads each draft's module from its
`drafts/<rid>.json`, unions those fixtures, combines, validates, writes `drafts/<combined>.html` +
`.json` (`method:"combined-multi-module"`, `modules:[…]`), prints grounding, exits 0 iff clean.
2.2 With `--pdf`, strips `<!-- Source -->` comments and renders the combined doc via
`pdf_export.render_html_to_pdf`, writing `drafts/<combined>.pdf` (valid `%PDF`).

## Edge / Empty / Error
| Case | Behavior |
|---|---|
| One draft only | Valid combined doc with one module section (degenerate but correct) |
| A source draft has a `tier_lie`/`not_found` | Combined doc surfaces the same violation (no hiding) |
| Two modules citing different tickets | Both validate against the union; neither cross-contaminates |
| Missing `<rid>.html` / `.json` | Clear error, non-zero exit, nothing written |
| Draft with no `<!-- Source -->` (e.g. imported guide) | Combines, but Sources list is empty; grounding still computed |

## Defaults
Title defaults to `Combined guide — <modules>`; PDF off unless `--pdf`; combined rid =
`<date>-combined-<slug(modules)>-<uuid6>`.

## Acceptance criteria
- [x] **AC1** — combined 2-module fixture validates: `tier_lie=0, quote_not_found=0`, both cited.
      ✓ `tests/test_multi_doc.py::test_ac1_combined_validates_across_modules` (green; `ok==2`).
- [x] **AC2** — a DESC-span-tagged-AC citation still trips `tier_lie` after combining.
      ✓ `tests/test_multi_doc.py::test_ac2_violation_not_hidden` (green; `tier_lie>=1`).
- [x] **AC3** — combined HTML has one `<h1>`, a `<h2>` per module, one merged `Sources`.
      ✓ `tests/test_multi_doc.py::test_ac3_structure` (green).
- [x] **AC4** — real combine, Inventory + Item Management clean drafts → one grounded doc.
      ✓ ran `python multi_doc.py 20260702-130037-inventory-long-form-daaa7e 20260601-091452-item-management-micro-guide-7b2021`
        → `tier_lie=0 not_found=0 ok=125 tokened=125 -> CLEAN`, exit 0 (union = 809 tickets).
- [x] **AC5** — `--pdf` on AC4 → valid combined PDF.
      ✓ same run: `drafts/…-combined-inventory-item-management-c550c5.pdf` (863.3 kb, `%PDF-` valid).

## Future option
STORY-003 adds a `--generate --modules A,B,…` mode that first produces each per-module doc via the
existing pipeline, then calls this combiner — additive; the combiner is unchanged, generation is layered
on top (and is the cap/paid-key-bound part).
