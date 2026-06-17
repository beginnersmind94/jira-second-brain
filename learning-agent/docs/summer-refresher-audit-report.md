# Consolidated QA Audit — "Summer Line-Up: Your POS Refresher"

**Subject:** course `course-20260614-7fe9279c` (published) + the code paths it exercises
**Date:** 2026-06-14 · **Auditors:** 5× claude-sonnet-4-6 (adversarial, read-only) · **Consolidator:** main session
**Method:** build-first, then full 5-agent audit. Findings deduped + each P0 re-verified by the consolidator.

---

## VERDICT: 🔴 NO-GO for July 13 (as-is)

Fails the brief's bar on **both** counts:
- **Not "zero P0":** a rendered-content XSS vector, a cross-tenant data leak, and approval endpoints with no role check are all live.
- **Not "no P1 on the on-stage demo path":** the course is **unreachable by a cashier** — the learner home, player, and certificate are all Track-driven, and this was built as a standalone Course in no Track.

**Kill criteria triggered** (per the brief): XSS execution vector (A4), cross-tenant leakage (A4), and an approval gate bypass / missing authorization (A2). These are not polish — they are the trust failure the product exists to prevent.

**Important framing:** the *content moat held*. The course contains **zero invented product facts** (A1: no class-(c) claims), it's assembled only from approved atoms, server-side provenance badges are correct, and the two agents that could have fabricated (quiz, exercise) correctly **refused / deferred**. The failures are (1) an **integration gap the build owns** and (2) **pre-existing platform security/provenance debt** the build surfaced. Most P0s are *latent on a controlled, trusted-content stage demo* but are hard blockers for any honest "trustworthy / production-leaning" claim — and since trust is the entire pitch, they gate the demo's credibility.

---

## Remediation status (updated 2026-06-15)

- ✅ **P1-1 fixed** — course wrapped in `track-20260614-summer-cashier`; learner home → player → certificate verified end-to-end (cert issued).
- ✅ **P0-3 fixed (code + test)** — role checks on all 6 approval/edit/publish endpoints; `tests/test_approval_authz.py` 3/3 (learner & director → 403, trainer passes). ⚠️ Live `:8001` server needs a restart (`reload=False`) to serve it.
- ◑ **P0-4 mitigated for this course** — broken `quiz-seed-cashier-demo` swapped for grounded `quiz-seed-food-safety-3q`; seed-data + badge-logic fixes still open (STORY-004).
- ⬜ **P0-1 (XSS) + P0-2 (tenant leak)** — still open; tracked in [trust-hardening-p0s](features/trust-hardening-p0s/EPIC.md).

Net: the on-stage learner path now works and the most demo-reachable trust risk (P0-4) is removed. **Still NO-GO under the strict "zero P0" bar until P0-1/P0-2 close or are explicitly accepted as out-of-demo-scope.**

## What works (so the picture is fair)
- **Regression green:** REG-01…16 all pass (16/16). The grounding gate (`demo.validate_citations`, demo.py:662) is **deterministic + offline** — no network/model in the gate path. REG-16 holds; no phantom identifiers.
- **Grounding/content (the moat):** no invented product facts in the framing copy; course built only from approved atoms; `[TO VERIFY]` discipline respected; ICN video is embed + attributed, not reproduced.
- **Server-side provenance + role-gating:** badges recompute correctly server-side (guides→`human_authored`, ICN→`outside_vendor`, quiz→`ai_grounded`); a CN Director does **not** receive the Cashier-tagged content.
- **Honest agent behavior:** quiz-gen failed → agent refused to fabricate; exercise was ungroundable → agent deferred. Scratch artifacts cleaned.

---

## P0 — ship-blockers (deduped, re-verified)

| # | Finding | Evidence | Build-introduced? | Owner |
|---|---|---|---|---|
| **P0-1** | **Rendered-content XSS.** Guide/quiz HTML is injected raw via `innerHTML` at ≥3 sinks; `<img onerror>` and `javascript:` payloads execute (not `<script>`, but the others do). | sinks index.html:10852, 10447, 14172; server returns unsanitized `/resources/{rid}/html` (demo_app.py:1337-1376). Payloads confirmed present unescaped in live response. | No (platform) | platform |
| **P0-2** | **Cross-tenant data leak.** `/api/districts/{isd}/compliance-report` (+`/pdf`) has no `current_user` / `assert_district_access`. A Houston director pulled **Dallas ISD** staff names. | demo_app.py:6632 / ~7288 (no auth dep); live: `dana-director` → `dallas-isd` report → 200 + 24 names. Contrast `/api/roster` which correctly 403s. | No (platform) | platform |
| **P0-3** | **Approval gate has no authorization.** `approve_resource` (and quiz/flashcard/track-publish/revise) take only `rid` — no role check. A **learner** approved a guide live. The "human approves" invariant holds; "an *authorized* human" does not. | demo_app.py:4697 `approve_resource(rid)` — no `Depends`; live: `X-Demo-User: john-cashier` POST `/resources/GUIDE-002/approve` → 200 `approved:true`. (Idempotent — GUIDE-002 was already approved; no state change.) | No (platform) | platform |
| **P0-4** | **Quiz provenance chain broken.** `quiz-seed-cashier-demo` is badged `ai_grounded`, but its `source_id` points to a course with **no POS content**; 3–4 of 8 questions are `grounded:true` with **empty `source_quote`**; `source_content_hash` is a placeholder. "Show source" would not substantiate the answers. | quizzes/quiz-seed-cashier-demo.json:5,8; source course lessons are Item-Mgmt/System; course_store.py:314-316 returns `ai_grounded` for *any* quiz unconditionally. | Surfaced by build (selected this seed quiz); data is pre-existing/`manual_grounded` | content + platform |

> P0-1/-2/-3 are platform debt (not created by this build). P0-4 is pre-existing seed data the build *exposed* by putting it in a published, learner-facing course with an `ai_grounded` badge.

---

## P1 — demo-breaking

| # | Finding | Evidence | Build-introduced? | Owner |
|---|---|---|---|---|
| **P1-1** | **Course unreachable by the learner (the on-stage blocker).** Learner home/player/cert are **Track-driven**; this is a standalone Course in no Track. Cashier sees nothing; player & cert 404 on the course id. | renderLearnHome → `/api/tracks` only (index.html:9631); `/api/tracks/course-…` → 404; `POST /api/certificates {track_id:course-…}` → 404 (demo_app.py:3074). | **YES — build owns this** | build (me) |
| **P1-2** | **Provenance over-claim in UI render paths.** A hardcoded `✓ sources cited & credited` chip (index.html:10344) shows on any course regardless of content; the builder's client-side badge can show `ai_grounded` on a human guide in unsaved preview. (Saved/served badges are correct.) | index.html:10344, 6743, 7181 | No (platform) | platform |
| **P1-3** | **Publish doesn't re-validate lessons (TOCTOU).** `api_publish_course` checks only "≥1 lesson," not `validate_all_lessons`. An atom demoted after assembly stays live in the published course. | demo_app.py:~897 (no `validate_all_lessons`); validation runs at create/update only. | No (platform) | platform |
| **P1-4** | **Gate/ingestion injection surfaces.** Zero-citation HTML passes the gate (violations=0); `import_guides.py` stores raw HTML unsanitized; the transcript *filename* flows unsanitized into the LLM prompt. | demo.py:662 + demo_app.py:4754; import_guides.py:56-64; agent_sdk.py:193-202 | No (platform) | platform / build |

---

## P2 — polish
- **REG docstring drift:** `eval/regression.py` header says "REG-01..15" but defines 16 (A5 flagged P0; it's a doc nit → **P2**). Suite itself is green.
- **a11y:** progress bar lacks `role="progressbar"`/`aria-valuenow`; completed rail rows render duplicate `✓` (needs `aria-hidden`). (Status is *not* color-only — pct label present.)
- **Encoding non-issue:** A1 read `SchoolCafÃ©` on disk; A3 confirmed the bytes are valid UTF-8 (0xC3 0xA9) and it was a terminal display artifact. **No defect.**

---

## Drift log (named mechanic vs reality)
- ✅ `validate_citations` (demo.py:662), `approve_resource` (demo_app.py:4697), `revise.py` Source-comment guard (revise.py:96-100, deterministic, server-side), `build_fixtures_from_csv.py`, REG-01…16 — all **present and matching**.
- ⚠️ `eval/regression.py` docstring says "REG-01..15"; actual = 16 (REG-16 present and passing).

## Coverage gaps (P0 invariant with no guarding test)
- `validate_all_lessons` is **not** re-run at publish (P1-3) — no test asserts publish is blocked on a demoted ref.
- No test asserts `quiz question.grounded==true ⇒ non-empty source_quote` (P0-4).

---

## Remediation routing
- **Build-owned (small, makes the demo work):** P1-1 — wrap the course in a **Track** (mirror `track-g1-cashier-onboarding`: `course_ids:[course-20260614-7fe9279c]`, role Cashier, due date, publish), after confirming the player renders `course_ids`. Re-verify learner home → player → cert end-to-end.
- **Platform (must-fix before real users; substantial):** P0-1 sanitize rendered HTML (server-side bleach + stop raw `innerHTML`); P0-2 add `assert_district_access` to compliance endpoints; P0-3 add role checks (`is_trainer`/PO) to approve/revise/quiz-approve/flashcard-approve/track-publish; P1-3 re-validate at publish; P1-4 sanitize import + quote the transcript path; P1-2 gate the "cited & credited" chip on real `ai_grounded` content.
- **Content:** P0-4 re-ground or replace `quiz-seed-cashier-demo` (fix `source_id` + fill `source_quote`s) before it appears in any published course.

## Re-test triggers
- Re-run this full audit after any fix (a fix can reopen a closed invariant), and again immediately before July 13.
