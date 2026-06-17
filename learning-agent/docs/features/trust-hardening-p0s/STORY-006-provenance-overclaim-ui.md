# Story 006: Gate the "sources cited & credited" claim on real grounding

**Epic:** [Trust hardening](EPIC.md)
**Status:** Not started
**Severity:** P1 · **Audit ref:** P1-2 (Agent 1 F-03/F-04)

## Requirement

> The UI must never imply machine-grounding ("every claim cited" / "sources cited & credited") on content that is human-authored or outside-vendor.

## Why

`openCourse()` hardcodes a `✓ sources cited & credited` chip for **every** course regardless of content (`index.html:10344`) — it shows on a course of imported guides + an ICN video, none gate-grounded. Separately, the course builder's client-side `cbPickGuide` assigns `ai_grounded` to any guide whose `origin` isn't the exact string `internal`, so a Cybersoft guide can flash `AI-grounded · every claim cited` in unsaved preview. (The saved/served badges are correct — server recomputes them.)

## Acceptance criteria

- [ ] The `✓ sources cited & credited` chip renders only for courses with ≥1 `ai_grounded` lesson, or is reworded to make no grounding claim (e.g. "from approved sources").
- [ ] `cbPickGuide` (`index.html:6743`) aligns with server `lesson_origin_badge` (origin/method check), and the `_badgeHtml` fallback (`:7181`) does not default unknown badges to `ai_grounded`.
- [ ] Builder preview shows the same badge the server will serve.

## Notes

Latent today (the active learner path recomputes badges correctly), but a one-way trust risk if `openCourse()` is reached. Detail in audit report P1-2.
