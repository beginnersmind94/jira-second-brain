# Epic: Two-version Citations-API grounding (subscription + paid API)

**Status:** In progress — 3 of 4 stories `Done ✓` (STORY-001/002/004); STORY-003 (live Version B generation) blocked on a paid `ANTHROPIC_API_KEY`.
**Component:** Content pipeline (Cell-D generate → gate → approve)   ·   **Persona:** Product Owner / SME reviewer (approves into the Library) + platform maintainer (runs the two versions)   ·   **Last updated:** 2026-07-02
**Depends on:** `demo.validate_citations` (exists — the substring grounding gate), `demo_d.py` Cell-D pipeline (exists), `eval/regression.py` REG-01..16 (baseline), Anthropic Citations API (docs verified 2026-07-02). Commits: `0dad1e2` (feat), `4d7e7bd` (pre-existing demo WIP swept along).

## Problem statement
The pipeline that ships content grounds Version A by *construction*: the section writer emits only
`[CITE:id]` and a deterministic assembler renders the verbatim span + tier from a registry built from
the Jira fixture, so wrong-tier and non-verbatim are impossible. Two gaps remain:

1. **No coverage check.** `validate_citations` only validates the citations that are *present* — it
   never asks whether every claim *has* one. An invented, uncited sentence passes the gate. (Real
   Cell-D drafts today carry 0→199 uncited claim blocks; `eval/coverage_report.py`.)
2. **The subscription writer can't use the Citations API.** Citations is a paid-API feature, so a
   customer on enterprise/subscription auth can't get the API's verbatim-span guarantee or write
   natural prose that the API grounds.

We want the Citations API where a paid key is available, **without changing what the subscription
user runs today**, and without adding a second codebase.

## Solution
One codebase, two versions selected by a `GATE_MODE` env var, on **two independent switches**:

- `gate_mode()` — a *policy* (keyless). When `citations`/`both`, the gate additionally enforces that
  every claim-bearing `<p>/<li>` carries a citation (coverage). Deterministic — the whole gate + eval
  layer is testable with no key.
- `citations_enabled()` — `gate_mode ∈ {citations,both}` **AND** a key present. Only this flips the
  *writer* to the Citations API.

Version A (`substring`/unset, no key) = today's writer + substring gate, byte-identical. Version B
(`both` + key) = Citations-API writer (guaranteed-verbatim `cited_text`) + substring **and** coverage
gate. Enforcement is narrowed to the two live re-validating gates (`publish_pending`,
`approve_resource`); every other call site is a pure rename `run_gate(...)["substring"]`.

## Scope
**In scope:** the `GATE_MODE` switch (`config.py`); the unified gate (`citation_gate.run_gate`,
wrapping `demo.validate_citations` unchanged under `["substring"]`) + coverage layer; the Citations
writer seam (`citations_client.py` + `demo_d._write_section_via_citations`); enforcement wiring at the
two live gates; eval coverage for both versions; a decision-free execution runbook.
**Out of scope:** an LLM evaluator/Task-5 grader (still deferred — coverage is deterministic, not an
LLM); transcript-only mode via Citations (transcript sections fall through to the SDK writer by
design); the Batch API path (optional appendix, not a gate); replacing Version A's construction-based
grounding (it stays the default and strongest structural guarantee); any Jira write.

## Design decisions
- **Two switches, not one.** The coverage gate is deterministic and needs no key; only the writer
  does. Splitting them makes Version B's gate fully unit-testable offline and scopes keys to
  generation. This is what lets a subscription-only machine test the entire gate/eval layer.
- **`run_gate(...)["substring"]` preserves the old dict byte-for-byte** at every reporting site, so
  Version A behavior is provably unchanged (REG-01..16 identical) and the blast radius is two
  enforcement points.
- **Store the RAW `cited_text` span** (never sanitized). `validate_citations` checks
  `_norm(quote) in _norm(field)` with the same `_norm` on both sides; a Citations `cited_text` is a
  verbatim substring of the field, so it passes — sanitizing would change bytes on one side and break
  the check. (Matches how the Jira registry already stores raw spans.)
- **Section-namespaced cite-ids** (`KEY:TIER:<sid>:Cnnn`): two sections citing the same (key,tier)
  must not collide in the shared registry (last-writer-wins would silently render the wrong span,
  invisible to the gate). Reassembly is a pure, unit-tested `segments_to_html()`.
- **One cache breakpoint per section** (last document only): the API caps `cache_control` breakpoints
  at 4/request; a well-sourced section cites >4 (ticket,tier) documents.
- **No `temperature`** on the writer: rejected with a 400 on Opus 4.8/4.7/Fable 5, so `CITATIONS_MODEL`
  stays free to point at any current model (pinned `claude-sonnet-4-6`; bare ids only).
- **Version B ≠ strictly better than A.** A makes wrong-tier/non-verbatim impossible by construction;
  B makes non-verbatim impossible (API guarantee) + adds coverage + natural prose, but its tier
  depends on the API attributing the span to the right document. They guard different failure modes;
  A stays the keyless default.

## User stories
- [x] [STORY-001: Two-version policy switch + unified grounding gate](STORY-001-two-version-switch-and-gate.md) — `Done ✓`
- [x] [STORY-002: Coverage layer + enforcement at the two live gates](STORY-002-coverage-and-enforcement.md) — `Done ✓`
- [ ] [STORY-003: Version B — the Citations-API section writer](STORY-003-citations-writer.md) — **In progress** (keyless invariants done; live generation blocked on a paid key)
- [x] [STORY-004: Eval coverage for the two-version split](STORY-004-eval-coverage.md) — `Done ✓`

## Implementation notes
- New files: `config.py`, `citation_gate.py`, `citations_client.py`,
  `eval/{test_overreach,parity,coverage_report}.py`, `scripts/smoke_citations.py`,
  `tests/{test_run_gate,test_citations_client}.py`, `docs/citations-migration-runbook.md` (the
  decision-free execution spec).
- Edits: `demo_app.py` (1 import + 6 reporting renames + `publish_pending`/`approve_resource`
  enforcement blocks), `demo_d.py` (1 import + 1 rename + `_write_section_via_citations` seam),
  `requirements.txt` (`anthropic>=0.49.0`), `.env.example` (`GATE_MODE`, `CITATIONS_MODEL`).
- **Verified 2026-07-02:** REG 16/16 (baseline match after wiring); `test_run_gate` +
  `test_citations_client` + `test_overreach` green; `parity` divergences 0; full suite collects 524;
  live server (`:8001`) drive of the edited enforcement path — clean draft → 200 `approved`, dirty
  (quote_not_found) → 409 `grounding_not_clean`, non-trainer → 403.
- **Known blocker:** Version B *generation* needs a paid `ANTHROPIC_API_KEY` (deferred per project
  decision 2026-06-16). Everything else runs keyless. See STORY-003.
