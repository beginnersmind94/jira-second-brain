# STORY-001 — Two-version policy switch + unified grounding gate

**Status:** `Done ✓` (2026-07-02)  ·  **Points:** 3  ·  **Persona:** platform maintainer
**Depends on:** `demo.validate_citations` (exists), `eval/regression.py` REG-01..16 (baseline).
**Epic:** [Two-version Citations-API grounding](EPIC.md)

## Scope
**In scope:** `config.py` (`gate_mode()`, `citations_enabled()`); `citation_gate.run_gate()` wrapping
`demo.validate_citations` and returning it **unchanged** under `["substring"]`; the coverage layer
computing `(claims, uncited_claims)` when `gate_mode ∈ {citations,both}`.
**Out of scope:** flipping the writer (STORY-003); wiring the enforcement sites (STORY-002); any
change to `validate_citations` itself (it is wrapped, never edited); an LLM grader.

## Requirements
1.1 `gate_mode()` reads `GATE_MODE` env (default `substring`), lower/trims, and returns one of
`{substring, citations, both}`; any other value → `substring`.
1.2 `citations_enabled()` is `True` **iff** `gate_mode() ∈ {citations,both}` **and** `ANTHROPIC_API_KEY`
is set (both conditions).
2.1 `run_gate(html, module="", *, transcript_text="")` returns a dict with keys
`passed, mode, substring, citations, violations`.
2.2 `result["substring"]` is exactly `demo.validate_citations(html, transcript_text=...)` (same object,
byte-identical dict) — no field added, removed, or renamed.
2.3 In `substring` mode `result["citations"] is None` and `passed` = (`tier_lie==0 and quote_not_found==0
and INVALID_CITE_ID count==0`).
2.4 In `citations`/`both` mode `result["citations"] = {claims, uncited_claims, nonverbatim}` and
`passed` additionally requires `uncited_claims==0`.

## Edge / Empty / Error
| Case | Behavior |
|---|---|
| `GATE_MODE` unset | `substring` (Version A) |
| `GATE_MODE=citations` but no key | coverage gate ON, `citations_enabled()` False (writer stays SDK) |
| `GATE_MODE=BOGUS` | falls back to `substring` (no crash) |
| Empty HTML | `substring` clean-ish (no tokens → passed True); coverage `(0,0)` |
| Claim block whose only content is a `<!-- Source -->` comment (no visible text) | not counted as a claim (skipped) |

## Defaults
`GATE_MODE=substring`; no key ⇒ Version A. Coverage off unless `gate_mode ∈ {citations,both}`.

## Acceptance criteria
- [x] **AC1** — *Given* no `GATE_MODE`/key, *When* `run_gate(CLEAN)`, *Then* `citations is None`,
  `substring == demo.validate_citations(CLEAN)`, `passed is True`.
      ✓ `tests/test_run_gate.py::test_substring_mode_is_byte_identical` (green).
- [x] **AC2** — *Given* substring mode and a draft whose span lives in AC but is labeled DESC, *When*
  `run_gate`, *Then* `passed is False` and `substring["tier_lie"]==1`.
      ✓ `tests/test_run_gate.py::test_tier_lie_fails` (green).
- [x] **AC3** — *Given* `GATE_MODE=both` and a clean block + one uncited `<p>`, *When* `run_gate`,
  *Then* `citations["uncited_claims"]==1` and `passed is False`.
      ✓ `tests/test_run_gate.py::test_both_mode_coverage_flags_uncited_claim` (green).
- [x] **AC4** — *Given* substring mode, *When* the full REG suite runs on the real 529-ticket Item
  Management fixture, *Then* it is 16/16 — identical to the pre-change baseline (proves 2.2 on real data).
      ✓ `python -m eval.regression` → `16 passed, 0 failed` before and after wiring.

## Future option
`gate_mode()` could gain a per-request override (header/param) so a reviewer can preview coverage on a
Version-A draft without changing the server default — additive; `run_gate` already takes the mode from
`gate_mode()`, so only the source of the mode changes.
