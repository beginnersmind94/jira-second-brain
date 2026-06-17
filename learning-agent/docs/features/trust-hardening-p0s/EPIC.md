# Epic: Trust hardening — close the audit P0s before real users

**Status:** In progress — STORY-003 done (code+test); STORY-004 partial (course-level swap). STORY-001 (XSS) + STORY-002 (tenant) still open.
**Component:** platform (`demo_app.py`, `static/index.html`, `course_store.py`, `import_guides.py`) + content
**Persona / lens:** Matt (BRD-grade foundation; trust *enforced*, not hoped)
**Last updated:** 2026-06-15
**Source:** [Summer-refresher audit report](../../summer-refresher-audit-report.md) (2026-06-14, 5-agent adversarial audit)

## Problem statement

The adversarial audit of the "Summer Line-Up: POS Refresher" build found the **content moat held** — no invented product facts, correct server-side provenance badges, REG-01…16 green, the grounding gate deterministic/offline. But it surfaced **pre-existing platform security & provenance debt** that has nothing to do with that build and everything to do with whether the product can be *honestly* presented as trustworthy.

Trust is the entire pitch — *"you make one mistake with AI and it loses credibility very quickly."* These findings are the kind of mistake that kills it: content that can execute script in a learner's browser, one district reading another's staff data, a learner able to approve content, and an `ai_grounded` badge on a quiz whose citations don't substantiate its answers. On a controlled, trusted-content stage demo several are *latent*, but none can be open when real districts and real PII are behind the login.

> The demo-path blocker the audit also found (a standalone Course is unreachable by learners — the learner UI is Track-driven) was **already fixed** by wrapping the course in `track-20260614-summer-cashier` and verified end-to-end (home → player → certificate). It is not part of this epic.

## Solution

Close each gate the audit named. The bar: every P0 has a fix **and** a regression test so the invariant can't silently reopen (the audit's re-test trigger).

## Findings → stories

| Story | Sev | Invariant | Owner |
|---|---|---|---|
| [001 — Sanitize rendered HTML (XSS)](STORY-001-rendered-html-xss.md) | P0 | Rendered guide/quiz content cannot execute script | platform |
| [002 — Tenant isolation on compliance endpoints](STORY-002-compliance-tenant-isolation.md) | P0 | A district can never read another district's data | platform |
| [003 — Authorize approval/edit endpoints](STORY-003-approval-authorization.md) | P0 ✅ done | Only an authorized PO/trainer can approve, not "any human" | platform |
| [004 — Fix quiz citation chain + honest badge](STORY-004-quiz-citation-chain.md) | P0 ◑ partial | `ai_grounded` ⇒ every answer traces to a verbatim source span | content + platform |
| [005 — Re-validate lessons at publish](STORY-005-publish-revalidation.md) | P1 | A published course never contains a demoted/unapproved atom | platform |
| [006 — Gate the "cited & credited" claim](STORY-006-provenance-overclaim-ui.md) | P1 | UI never implies machine-grounding on human/ICN content | platform |
| [007 — Gate floor + ingestion sanitization](STORY-007-gate-floor-ingestion.md) | P1 | Zero-citation/raw-HTML/filename-injection can't slip through | platform / build |

## Design decisions

- **Fix + test, together.** Per `CLAUDE.md`, a guarantee lives in code and its test — every P0 story ships with a regression test in `eval/` or `tests/`, in the same change.
- **Don't weaken the moat to ship fast.** Sanitization and authorization are additive guards; they must not touch `validate_citations` or the `<!-- Source -->` invariants.
- **Re-run the full 5-agent audit after fixes**, and again immediately before July 13 — a fix can reopen a closed invariant.

## Implementation notes (context for whoever picks this up)

- Audit subject: course `course-20260614-7fe9279c`, wrapped in track `track-20260614-summer-cashier`.
- The XSS sinks, the tenant-leak repro, and the approval-bypass repro are all in the audit report with `file:line` + live command output.
- `api_publish_course` already checks `is_trainer` — use it as the pattern for STORY-003. `/api/roster` already calls `assert_district_access` — use it as the pattern for STORY-002.
