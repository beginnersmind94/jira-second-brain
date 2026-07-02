# Epic: Cross-module combined guide (one doc, each section grounded in its own module)

**Status:** In progress — STORY-001 (deterministic combiner) `Done ✓` (verified keyless: unit test + real cross-module combine, 125 citations clean against the union, valid PDF). STORY-002/003 next.
**Component:** Content pipeline (assemble / grounding)   ·   **Persona:** Product Owner / trainer producing a cross-module rollup (e.g. "June 2026 release notes across all modules")   ·   **Last updated:** 2026-07-02
**Depends on:** `demo.validate_citations` + `demo._load_fixture` (exist), `demo_d.assemble` output shape (exist), the single-module Cell-D pipeline (exist, proven), `pdf_export.render_html_to_pdf` (exist).

## Problem statement
The intent agent **refuses** a cross-module request ("release notes across all modules") because the
pipeline loads **one module's fixture per run** and the grounding gate validates against that single
fixture. That refusal conflated an *implementation* limit with a *grounding* limit — and they're not
the same. **Grounding is per-claim, not per-document:** each claim just has to trace to a verbatim span
in the *correct module's* tickets. Putting several modules' sections in one doc doesn't break that.

So a combined cross-module doc **is** groundable; we just never built the path. And the subscription
session cap makes a single-shot N-module *generation* infeasible anyway.

## Solution
**Decouple generation from combination.**
- **Generation stays single-module** (the proven, cap-bound path) — produce each module's doc whenever
  there's capacity (or via the paid API).
- **Combination is a new, deterministic, keyless, instant step:** stitch N single-module drafts into one
  document (a section per module) and validate the whole thing against the **union** of the source
  modules' fixtures. Ticket keys (`NXT-####`) are globally unique, so the union is collision-free and
  every citation resolves to its real ticket — cross-module grounding is exact, not approximate.

Result: one combined doc, every claim still grounded in its own module's verbatim spans, produced with
zero extra model calls.

## Scope
**In scope (STORY-001):** `multi_doc.py` — `union_fixture(modules)` + `combine(parts, title, fixture)`;
a CLI that combines existing single-module drafts into one grounded doc (+ PDF); a deterministic keyless
test; a real-draft end-to-end proof.
**Out of scope (later stories):** the intent agent *offering* the combined doc instead of refusing
(STORY-002); a one-command "generate the N per-module docs then combine" orchestration (STORY-003,
cap/paid-key bound); the general "regenerate a whole template's guide set" workflow.

## Design decisions
- **Combine assembled drafts, not mid-pipeline state.** The combiner takes finished single-module HTML
  (each already grounded + gate-clean against its own module) and stitches bodies under per-module
  headers with one merged Sources list. Reuses everything; adds no model calls.
- **Validate against the union fixture.** Since each source draft was clean against its own module and
  ticket keys are globally unique, the same `<!-- Source -->` comments validate against the union with
  zero tier/quote drift. The combined doc passes the *same* `validate_citations` gate — no weakening.
- **Generation is not part of this slice.** The cap-bound part is left to the existing single-module
  path; the combiner is instant and keyless, which is also the right separation for the paid-key future.

## User stories
- [x] [STORY-001: Deterministic cross-module combiner + grounding](STORY-001-combiner.md) — `Done ✓`
- [ ] STORY-002: Intent agent offers a combined doc instead of refusing "all modules" (next)
- [ ] STORY-003: One-command generate-N-modules-then-combine orchestration (cap/paid-key bound)

## Implementation notes
- `multi_doc.py`: `union_fixture`, `combine`, CLI. Combined drafts written with
  `method: "combined-multi-module"` + `modules: [...]` in meta.
- Verified: `tests/test_multi_doc.py` (deterministic) + a real-draft combine (Inventory + Item
  Management existing clean drafts) validating clean against the union.
