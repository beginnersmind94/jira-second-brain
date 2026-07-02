# STORY-003 — Version B: the Citations-API section writer

**Status:** **In progress** — keyless invariants `Done ✓`; the live-generation AC is **blocked on a
paid `ANTHROPIC_API_KEY`** (project decision 2026-06-16: use a key when the project is approved, not
now). This is a named dependency, not a façade — the writer code exists and byte-compiles, but its
live behavior is *unverified*, so the story is not `Done ✓`.
**Points:** 5  ·  **Persona:** platform maintainer (Version B) / SME reviewer (consumes the output)
**Depends on:** STORY-001 (`citations_enabled`), `demo_d.write_section`/`assemble` (exist),
`demo._FIELD_BY_TIER`/`demo._FIX` (exist), Anthropic Citations API + a paid key (**not present**).
**Epic:** [Two-version Citations-API grounding](EPIC.md)

## Scope
**In scope:** `citations_client.py` — `build_ticket_documents` (one document per non-empty (ticket,tier),
one cache breakpoint), `parse_citation_response` (extract `cited_text`/`document_title`),
`segments_to_html` (section-namespaced `[CITE:id]` + registry entries), `write_section_citations` (raw
Messages API, citations enabled, no temperature); the `demo_d._write_section_via_citations` seam and the
`write_section` branch that routes **only Jira-grounded sections** (with `ticket_keys`) to it.
**Out of scope:** transcript-only sections (they carry `span_ids`, not `ticket_keys` → fall through to
the SDK writer, identical to Version A); changing `assemble` (it renders the synthetic registry entries
unchanged); the Batch API; a live key setup (deferred).

## Requirements
1.1 `build_ticket_documents(keys)` emits one `{type:document, source:{type:text}, title:"KEY:TIER",
citations:{enabled:true}}` per non-empty field, ordered by sorted key then tier `AC,RN,RNINT,DESC`.
1.2 Exactly **one** `cache_control:{type:ephemeral}` breakpoint total, on the **last** document (API cap
is 4/request; a section can cite >4 documents).
1.3 `segments_to_html(segments, sid)` produces `[CITE:KEY:TIER:<sid>:Cnnn]` markers + a
`{cid: {issue,tier,span}}` map; the span is stored **raw** (unsanitized).
1.4 Cite-ids are **section-unique**: two sections citing the same (key,tier) yield disjoint cid sets
(no shared-registry collision).
1.5 `write_section_citations` calls `client.messages.create` with `model=CITATIONS_MODEL`
(default `claude-sonnet-4-6`, bare id), `max_tokens=4096`, **no** `temperature`/`top_p`, citations
enabled per document; parses `.citations` itself (incompatible with structured outputs).
2.1 In `write_section`, when `citations_enabled() and sec.get("ticket_keys")`, route to
`_write_section_via_citations`; otherwise the existing SDK path runs (Version A behavior).
2.2 The returned section shape matches the SDK writer (`{title, html, stop_reason:"citations", secs,
errored, attempts, usage}`) so `assemble` renders it unchanged.

## Edge / Empty / Error
| Case | Behavior |
|---|---|
| No `ANTHROPIC_API_KEY` | `citations_enabled()` False → SDK writer runs (Version A); no import of `anthropic` |
| Transcript-only guide (`span_ids`, no `ticket_keys`) | every section falls through to SDK writer |
| Structural section with empty `ticket_keys` | falls through to SDK writer |
| Section cites 5+ (ticket,tier) documents | still one cache breakpoint (no 400) |
| `cited_text` spans multiple field lines | stored raw; `_norm(quote) in _norm(field)` still holds → gate passes |
| Writer emits an uncited sentence | draft fails the coverage gate at approve (409) — surfaces as "tighten the writer prompt" |

## Defaults
`CITATIONS_MODEL=claude-sonnet-4-6` (matches the SDK writer tier); no temperature; one cache breakpoint.

## Acceptance criteria
- [x] **AC1** — *Given* a fixture with AC/RN/DESC on NXT-1001, *When* `build_ticket_documents`, *Then*
  titles == `[NXT-1001:AC, NXT-1001:RN, NXT-1001:DESC]`, every doc `citations.enabled True`, and exactly
  one `cache_control` (on the last).
      ✓ `tests/test_citations_client.py::test_build_ticket_documents_one_block_per_nonempty_tier`.
- [x] **AC2** — *Given* the same segments rendered for sections `s1` and `s2`, *When* `segments_to_html`,
  *Then* their cid sets are disjoint (`[CITE:NXT-1001:AC:s1:C000]` vs `...:s2:C000]`).
      ✓ `tests/test_citations_client.py::test_segments_to_html_namespaces_cite_ids_by_section`.
- [x] **AC3** — *Given* SDK-shaped response blocks with a citation, *When* `parse_citation_response`,
  *Then* the segment's `cites == [{span, key, tier}]` and prose is preserved.
      ✓ `tests/test_citations_client.py::test_parse_citation_response_extracts_span_and_tier`.
- [ ] **AC4 (BLOCKED — needs a paid key)** — *Given* `GATE_MODE=both` + `ANTHROPIC_API_KEY`, *When* a
  long-form guide is generated for Item Management, *Then* each Jira-grounded section's spans come from
  the Citations API (`stop_reason:"citations"`), the assembled draft passes `run_gate` (substring **and**
  coverage clean), and `approve` returns 200.
      ⛔ Not demonstrated — no key in this environment. Proxy evidence only: `scripts/smoke_citations.py`
        prints `SKIP` without a key (asserts `PASS` with one). Do not mark this AC done until it is run
        live with a key.
- [ ] **AC5 (BLOCKED — needs a paid key)** — *Given* Version B, *When* the writer emits an uncited
  sentence, *Then* `approve` returns 409 with `citations.uncited_claims > 0` (the coverage gate holds
  the writer to account).
      ⛔ Coverage side proven keyless (STORY-002 AC1); the live writer→409 path needs generation.

## Definition-of-Done status
Keyless invariants (AC1–3) demonstrated green. AC4–5 require a paid key and are the **only** thing
between this story and `Done ✓` — tracked as a hard dependency, expiry = "when the project is approved
and a key is added to `learning-agent/.env`." No part is stubbed to look finished: the writer runs the
real API when a key is present; without one it is inert and the SDK writer runs.

## Future option
Route the Version B writers through the **Message Batches API** (§8 of the runbook) for ~50% eval cost —
additive; `write_section_citations` already returns a `usage` dict the batch path can reuse, and the
grounding is downstream (unchanged).
