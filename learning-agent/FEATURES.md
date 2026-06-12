# Learning Studio — Feature Inventory (state of the build)

**Last updated:** 2026-06-09 · **Branch:** `claude/learning-studio-icn-quizzes-roster-2026-06-05`
**This is the canonical "what exists" doc.** It is meant to be read by a human OR handed to another LLM
for consultation. **Update it whenever a feature lands, changes status, or is parked** — it is the single
source of truth, ahead of memory or chat history.

> Companion docs: `CLAUDE.md` (operating rules + enforcement vs. convention), `HANDOFF.md` (run gotchas +
> next steps), `docs/` (eval reports), and the plan at `~/.claude/plans/splendid-forging-rossum.md`.

---

## What Learning Studio is
An LMS for K-12 child-nutrition staff. Two halves: a **content factory** (turn transcripts/PDFs/Jira into
fact-checked learning content) and an **LMS / fulfillment engine** (assemble content into tracks, assign to
learners, measure completion). The deliverable is the published, *trustworthy* learning library.

## The one non-negotiable principle (the moat)
**Grounding by construction.** Every product-fact claim must trace to a verbatim source span, or it is cut.
The model emits citation ids; a deterministic assembler renders the verbatim quote + trust tier; a gate
re-checks. This holds for guides AND quizzes. **Manual control = manual *assembly* of curated content; it
never means hand-authoring product claims.** A feature that lets a human type an un-cited product claim is a
moat violation and does not ship. The header badge "✓ every claim cited" is this promise, made visible.

## How to run (demo)
- Server: from `jira-brain/learning-agent`, run `python demo_app.py` with the **sibling** `.venv`
  (`Financials-Documentation-KT/learning-agent/.venv/Scripts/python.exe`) — Windows ProactorEventLoop, port
  **8001**. Static `index.html` is served fresh from disk (frontend edits are live; **backend edits need a
  restart**). Auth is via the `claude` CLI, not `.env`.
- Evals: `python -m eval.report` (offline dashboard); `--live` variants need `claude` auth.

---

## Status legend
**Built** = real & working · **Façade** = seeded demo data, no real persistence/identity (fine for demo) ·
**In progress** = being built now · **Planned** = specced, not built · **Parked** = deliberately deferred ·
**Out of scope** = different project.

## BUILT
| Area | What | Real vs Façade | Where |
|---|---|---|---|
| SCORM 1.2 export + xAPI emission | `GET /api/tracks/{id}/scorm` returns a zip containing `imsmanifest.xml`, SCO launch page with SCORM API shim, per-module HTML content, and quiz JSON. xAPI `completed`/`progressed` statements emitted on cert + module-done; stub mode logs to `logs/xapi-stub.jsonl`; production POSTs to LRS when `LRS_ENDPOINT`+`LRS_KEY` set. Trainer view has "Export as SCORM" button. All non-fatal: LRS/zip errors never block cert issuance. | **Real (scaffold — stub LRS by default)** | `scorm_export.py`, `xapi_client.py`, `demo_app.py`, `index.html` `tbExportSCORM`, `tests/test_scorm_xapi.py` |
| Auth / SSO scaffold | `CurrentUser` dataclass + `get_current_user()` FastAPI dependency; demo bypass via `X-Demo-User` header (john-cashier · dana-director · sam-trainer); production SSO hook stubbed per ADR-001 §Auth; `/api/roster`, `/api/certificates`, `/api/tracks` wired through identity | **Real (interface + demo bypass; production JWT pending)** | `auth.py`, `demo_app.py`, `tests/test_auth.py` |
| SCORM export + xAPI | SCORM 1.2 package export (`imsmanifest.xml` + SCO launch page + module HTML + quiz JSON). xAPI stub logs to `logs/xapi-stub.jsonl`; production writes to LRS when `LRS_ENDPOINT` + `LRS_KEY` are set. "Export as SCORM" button in track builder (trainer view). | **Built (V2)** | `scorm_export.py`, `xapi_client.py`, `demo_app.py` `/api/tracks/{id}/scorm` + `/api/xapi/status`, `index.html` `tbExportSCORM` |
| Generation | Transcript/PDF → grounded guide (Tasks 1–4, one SDK call) | **Real** | `demo_app.py` `/generate`, `demo_d.py`, `agent_sdk.py` |
| Grounding gate | Verbatim citation + correct tier; deterministic publish gate; pinned by REG-01…16 | **Real (enforced)** | `demo.validate_citations`, `eval/regression.py` |
| Human review + AI edit + approve | Grounding-safe find/replace edits; approve re-validates live; audit log | **Real (enforced)** | `revise.py`, `demo_app.approve_resource` |
| Quiz builder + player + gate | Generate **MCQ, True/False, Fill-in-the-blank, Step-ordering** questions — all gate-grounded to verbatim source spans; drop any question whose span isn't found verbatim; take + score all types with per-question source feedback | **Real** | `qbank_gate.py` (`_gate_tf`, `_gate_fitb`, `_gate_ordering`, `gate_question_by_type`), `quiz_store.py` (type registry, per-type `validate_shape`/`score_quiz`), `/api/quizzes/*`, `openTaker`/`takerPickTF`/`takerCheckFITB`/`takerOrderMove`/`takerSubmitOrdering` in `index.html` |
| Quiz-from-guide | Generate a grounded quiz from a published guide | **Real** | `demo_app.py` `/api/resources/{rid}/quiz` |
| Library assistant | Grounded Q&A over all guides — verbatim-cited answer or "not in the library"; never invents | **Real** | `demo_app.py` `/api/library/ask`, rail in `index.html` |
| Learn (3-level) | DataCamp-style **Track → Courses → Lessons** (guide PDF / grounded quiz / video / certify); per-track seeded progress, complete → certify; Customer lands here. **Real published tracks built+assigned this session now appear here, filtered by a "Viewing as <role>" selector** (role_tags ∋ role, untagged = everyone); opening one lists its real mixed modules (AI guide opens PDF · Cybersoft guide · ICN links out) + grounded quiz | **Real player; real tracks; durable per-user completion (disk-backed); seeded fallback for demo users** | `index.html` `loadLearn`/`renderLearnGrid`/`openRealTrack`/`openTrack` · `completion_store.py` · `/api/tracks/{id}/progress` |
| Trainer Home / day-view | 4 KPI tiles, 5 district project cards (Aldine "raised hand" flag + Respond), "N approved by PM team" inbox → open PDF / send to Catalog. Post-demo role audit: all content-event actor/action pairs verified consistent with PO-as-approver / Jaime-as-router model. | **Façade data** | `index.html` `loadHome`/`renderHome`/`respondHelp` |
| Manage (Trainer) | All-6-districts roll-up: completion %, logins, status, Aldine help banner, expandable per-district rows → Roster | **Façade data** | `index.html` `loadManage`; `demo_app.py` `/api/roster` + `_district_stats` |
| My Team (CN-Director) | Customer-scoped staff compliance by site/role vs deadline; nudge one / nudge-all-overdue; self-assign a track | **Façade data** | `index.html` `loadMyTeam`/`nudgeOne`/`doAssign` |
| Compliance export (My Team) | Download compliance report (PDF) button (Customer view only); GET /api/districts/{isd}/compliance-report (JSON) + /pdf (PDF with DEMO DATA watermark); seeded data, 9-test suite. Wire to real roster once SSO + roster sync land (V1.5, Tasks 11-13). BRD FR-RP-03. | **Built (seeded data, PDF export)** | demo_app.py _build_compliance_report + 2 routes; index.html downloadComplianceReport; tests/test_compliance_export.py |
| Tracks + Courses builder | Trainer assembles **courses** from approved guides + auto-grounded quizzes + video, reorder, Save → builds **tracks** from courses; appears in Learn. No free claim-authoring (moat-safe) | **Real — server-persisted JSON in data/courses/; CRUD + publish endpoints; lesson ref validation against approved content only; legacy tracks auto-shim to implicit Course 1** | `course_store.py`, `demo_app.py` `/api/courses/*`, `data/courses/*.json`, `eval/test_course_store.py`, `index.html` `openCourseBuilder`/`cbSave`/`openTrackBuilder`/`tbkSave` |
| Library vs Catalog (IA) | **Studio** = review worklist over the real `/resources` set (drafts + approved) + published tracks; **Catalog** = ready-to-use shelf over real `/api/modules` (AI + Cybersoft guides + ICN) + published tracks. Origin/status badges; Source filter; ICN claim is now TRUE (wired in), not over-claimed | **Real backend** (adapters reuse existing filter/render) | `index.html` `loadLibraryDemo`/`loadCatalogDemo` |
| ICN into tracks | ICN_DOC modules are addable in the track builder and expand inside a track (learner can open the credited ICN reference; never reproduced) | **Real** | `demo_app.py` `/api/modules`+`/api/tracks/{id}` pass `icn_dir`; `modules_store._load_icn_modules` |
| Quality (top-level) | Eval/quality strip + per-item rubric scores (Grounding=deterministic gate, Coverage/Clarity/Structure=`scorers.py` heuristics), SME verdict states, cited-claim drill-down | **Real (scorer-based) + Façade fallback** | `scorers.py`, `index.html` `loadQuality`/`qualityDetail`/`_qlScoreArray` |
| Persona nav + provenance | Avatar "Viewing as" dropdown toggles Trainer/Customer tab sets + safe-to-share banner; origin badges (AI-grounded · human · outside-vendor) everywhere | **Façade** | `index.html` `setViewMode`/`applyViewMode`/`_originBadge` |
| Multi-tenant isolation | API-layer district-access enforcement via `tenancy.py` `assert_district_access()` on all district-scoped routes (`/api/roster`, `/api/modules`, `/api/tracks`). Trainers scoped to their book-of-business; learners/directors to their own district. 403 on any cross-district read. Seed data is no longer the only tenant boundary. | **Built (API-layer enforcement)** | `tenancy.py`, `auth.py`, `demo_app.py`, `tests/test_tenancy.py` (18 tests) |
| Roster / multi-tenant | 6 districts + per-learner progress/status; ISD switcher reconciled to demo universe | **Façade data** | `demo_app.py` `/api/roster`, `loadRoster`, `_demoISDInit` |
| Roster sync + completion writeback | `RosterSyncClient`: seeded roster in demo mode; writes completion records to `logs/writeback-stub.jsonl`. Production: set `SCHOOLCAFE_API_URL` + `SCHOOLCAFE_API_KEY`. `/api/tracks/{id}/progress` fires `sync_completion()` after progress update; `/api/certificates` fires with `certified=True`. Non-fatal: failures log and continue. `/api/sync/status` shows live vs stub. | **Built (stub mode)** | `roster_sync.py`, `tests/test_roster_sync.py` (17 tests) |
| Imported guide library | 86 SchoolCafé/ICN guides as approved Library items, honest provenance (human-authored, **not** gate-grounded); Source filter | **Real content, not gate-grounded** | `import_guides.py`, Library view |
| PDF → markdown upload | Server-side transcript conversion (header/footer strip, multi-column warning, 80pp cap) | **Real** | `pdf_to_md.py`, `app.upload_transcript` |
| Eval suite | See **Evals** below | **Real** | `eval/*` |
| Conference demo mode | `DEMO_MODE=conference` env flag (NEVER set in production — suppresses honest labels). When set: (1) watermarks / "DEMO DATA" banners suppressed on seeded artifacts (compliance PDF, resource PDF pending-review banner); (2) boot pre-warm loads all library docs + ICN catalog so first load is instant; (3) `POST /api/demo/reset` (conference-mode-only, 403 otherwise) clears all demo user completion records + certs + leads log in <10s; (4) operator-only reset UI in the browser — invisible to visitors, activated by `?operator=1` URL param or triple-R keyboard chord on a hidden anchor; (5) generation-theater replay: if `data/demo/generation-replay-<rid>.jsonl` exists, `/generate` streams it line-by-line instead of hitting the LLM; (6) `/api/config` exposes `conferenceMode: true` + `window._config` set globally. Default (flag off) = today's honest-watermark behaviour — unchanged. | **Real** | `demo_app.py` (`CONFERENCE_MODE`, `demo_reset`, `_conference_prewarm`, `_stream_replay`); `completion_store.reset_demo_users`; `static/index.html` (`_initOperatorReset`, `_showToast`); `.env.example`; `eval/test_demo_mode.py` (5 test cases) |
| Production readiness docs | Env vars, integration checklist, stub→real activation steps for all 7 V1.5 modules (auth/SSO, roster sync, xAPI/LRS, completion store, tenancy, SCORM, ICN flag), zero-to-prod checklist, honest stub-vs-real summary table, and remaining code-change requirements (SSO JWT, DB backend, demo-seed removal) | **Docs** | `docs/PRODUCTION.md` |

## Evals (what's measured + latest, with honesty caveats)
- **Regression (REG-01…16):** pins the grounding guarantees. `eval/regression.py`. **Gating, deterministic.**
- **Support judge calibration:** `eval/judge_eval.py` — 34-case gold set. After the `c05` prompt fix, **live FNR 0% / FPR 6.67%** (`docs/JUDGE-CALIBRATION-2026-06-08.md`). *Caveat: model-prompted, advisory — the deterministic gate is the floor; the 2 held-out generalization cases are same-author, not a blind holdout.*
- **Source-faithfulness:** `eval/source_faithfulness.py` — guide-claim ⊆ cited span. Caught the **real Q4 guide↔transcript drift** live (FN 0% on the fixture). Catches what the verbatim gate + quiz gate structurally can't.
- **Quiz reliability sweep:** `docs/QUIZ-RELIABILITY-INV-DISTRIBUTION.md` — 10× on one guide: 59/60 kept, **0/10 fully-clean runs**, ~2–3 real wrong-keys after triage. The verbatim gate passed all; only the support judge caught them.
- **Trace-back audit:** `docs/TRACE-BACK-AUDIT-INV-DISTRIBUTION.md` — a **standing manual SME gate** (the backstop for the judge's residual FN). **Scaffolded, NOT yet SME-run.** "0 automated flags ≠ safe until trace-back runs."
- **Scorer unit tests:** `tests/test_scorers.py` — 42 cases for `score_coverage`, `score_clarity`, `score_structure`, `compute_scores`, `_extract_headings`, `_count_words`. All deterministic, no SDK deps. Runs with `python -m pytest tests/test_scorers.py -v`.
- Also: triage classifier (`eval/triage_eval.py`), scope/lane-purity (`eval/scope_eval.py`), coverage, source-quality, `eval/report.py` (Jaime dashboard).

## IN PROGRESS
Nothing open. The **complete end-to-end seeded demo** shipped this session — all 7 surfaces (Home, Learn,
My Team, Manage, Quality, Tracks/Courses builder, Library/Catalog) are fully populated on a client-side
`_DEMO` universe (6 districts, seeded learners, courses, tracks, inbox, quality items) and walk-through-ready.
The 4 prior to-dos (nav re-carve + provenance · projects/allocation · builder · day-view/inbox) all landed.
Next: the Thursday live walkthrough + whatever the user flags.

## PLANNED / PARKED (deliberately deferred, post-Thursday)
- Full **Studio / Deployments / Insights** IA rebrand (use as a grouping model, not a rename).
- Full-page **deep-authoring editor** (moat risk — only a *sequencing + grounded-generate* surface, never a free canvas).
- Drag-and-drop reordering; background "Selection Mode" click-to-append; comms/broadcast hub; multi-select floating action bars; heavy tactile visual polish.
- Real infra (V1.5+): SSO / district rostering, real per-learner persistence + completion-of-record, Chroma vector retrieval (today retrieval is JQL/keyword), the LLM Evaluator (Task 5) + routing, flashcards, template-regeneration workflow, Word (`.docx`) upload.

## OUT OF SCOPE (different project — do not build here)
- **Financials Ledger export** (Oracle / Tyler Munis via custom-reports). Separate project.

## Honesty notes for any consulting LLM
- "Built" rows tagged **Façade** have **no real persistence/identity** — they reset and use seeded data. Do not represent them as production-ready.
- Imported guides are human-authored and **not gate-grounded**; only AI-generated guides carry the verbatim-citation guarantee.
- Eval numbers above are real measurements with stated caveats; the support judge is **advisory**, the deterministic gate + human approval are the floors.
