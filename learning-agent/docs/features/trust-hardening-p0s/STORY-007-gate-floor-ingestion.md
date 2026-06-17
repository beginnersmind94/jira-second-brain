# Story 007: Gate floor + ingestion sanitization

**Epic:** [Trust hardening](EPIC.md)
**Status:** Not started
**Severity:** P1 · **Audit ref:** P1-4 (Agent 2 F-03, Agent 4 F-03/F-04)

## Requirement

> Content can't reach the Library through a gap in the gate or through unsanitized/injected ingestion.

## Why

Three related gaps the audit surfaced:
1. **Zero-citation pass-through:** `validate_citations` only checks that *existing* citations are correct; an HTML doc with **no** `<!-- Source -->` comments returns `violations=0` and can be approved. Guarded for the AI generator (always emits citations) but not for direct file placement / import.
2. **Import doesn't sanitize:** `import_guides.py` runs python-markdown with `extra`, which passes raw HTML through verbatim — feeding the XSS sinks in STORY-001.
3. **Filename → prompt injection:** the transcript path/filename is embedded unsanitized into the LLM user prompt (`agent_sdk.py:193-202`).

## Acceptance criteria

- [ ] Approval of AI-generated content requires `verified > 0` (a minimum-citation floor); explicitly `grounded:false` imports remain a sanctioned, separately-labeled exception.
- [ ] `import_guides.py` sanitizes HTML (allowlist) before storing.
- [ ] The transcript path is quoted/stripped before the prompt; the model receives only the filename, not a free-text injection surface.
- [ ] A test for each: zero-citation AI doc blocked; injected `<script>` in an imported `.md` stored inert; adversarial filename neutralized.

## Notes

Lower exploitability than the P0s (import is offline; the generator always cites), but each is a real floor the gate currently lacks. Detail in audit report P1-4.
