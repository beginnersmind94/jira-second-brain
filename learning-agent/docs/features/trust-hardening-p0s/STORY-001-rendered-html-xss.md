# Story 001: Sanitize rendered guide/quiz HTML (stop innerHTML XSS)

**Epic:** [Trust hardening](EPIC.md)
**Status:** Not started
**Severity:** P0 · **Audit ref:** P0-1 (Agent 4 F-01)

## Requirement

> Guide and quiz HTML rendered into the learner view must be sanitized so that injected `<script>`, event-handler attributes (`onerror`, `onload`, `on*`), and `javascript:` URIs cannot execute in a learner's browser session.

## Why

The app injects generated/imported HTML into the DOM via `innerHTML` at three sinks. `<script>` won't run via `innerHTML`, but `<img onerror=…>` and `javascript:` hrefs **do** — confirmed live: a scratch atom with these payloads returned them unescaped from `/resources/{rid}/html`. Any guide body (AI-generated, imported, or planted in `drafts/`) containing an event handler executes for the learner. This is the single highest-likelihood real exploit in the stack.

## Acceptance criteria

- [ ] Server sanitizes HTML before returning it on `/resources/{rid}/html`, `/resources/{rid}`, and `?view=clean` (allowlist via `bleach` or equivalent — strip `<script>`, `on*` attributes, `javascript:`/`data:` URIs).
- [ ] Client stops assigning untrusted HTML through `innerHTML` at `static/index.html:10852` (`_cpLoadGuideHtml`), `:10447` (`_loadLessonGuide`), `:14172` (`selectLibResource`) — render through the sanitizer.
- [ ] Regression test: a draft atom containing `<script>`, `<img src=x onerror=…>`, and a `javascript:` link renders **inert** (assert payload stripped/escaped).

## Notes

Sinks + server paths (`demo_app.py:1337-1376`, `app.py:415-426`) and the live repro are in the audit report under P0-1.
