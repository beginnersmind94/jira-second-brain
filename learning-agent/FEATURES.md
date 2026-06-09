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
| Generation | Transcript/PDF → grounded guide (Tasks 1–4, one SDK call) | **Real** | `demo_app.py` `/generate`, `demo_d.py`, `agent_sdk.py` |
| Grounding gate | Verbatim citation + correct tier; deterministic publish gate; pinned by REG-01…16 | **Real (enforced)** | `demo.validate_citations`, `eval/regression.py` |
| Human review + AI edit + approve | Grounding-safe find/replace edits; approve re-validates live; audit log | **Real (enforced)** | `revise.py`, `demo_app.approve_resource` |
| Quiz builder + player + gate | Generate MCQs grounded in a source; drop any question whose answer isn't a verbatim span; take + score | **Real** | `qbank_gate.py`, `/api/quizzes/*`, `openTaker` in `index.html` |
| Quiz-from-guide | Generate a grounded quiz from a published guide | **Real** | `demo_app.py` `/api/resources/{rid}/quiz` |
| Library assistant | Grounded Q&A over all guides — verbatim-cited answer or "not in the library"; never invents | **Real** | `demo_app.py` `/api/library/ask`, rail in `index.html` |
| Learn (tracks) | DataCamp-style tracks → lessons (guide PDF / grounded quiz / video) → complete → certify; Customer lands here | **Real player, façade tracks** | `index.html` `_TRACKS`/`loadLearn`/`openTrack` |
| Management dashboards | Persona-toggled: internal all-districts roll-up (+ "raised hand for help") / CN-Director compliance (by role, nudge) | **Façade data** | `index.html` `loadManage`; `demo_app.py` `/api/roster` + `_district_stats` |
| Roster / multi-tenant | Districts + per-learner progress/status; ISD switcher | **Façade data** | `demo_app.py` `/api/roster`, `loadRoster` |
| Imported guide library | 86 SchoolCafé/ICN guides as approved Library items, honest provenance (human-authored, **not** gate-grounded); Source filter | **Real content, not gate-grounded** | `import_guides.py`, Library view |
| PDF → markdown upload | Server-side transcript conversion (header/footer strip, multi-column warning, 80pp cap) | **Real** | `pdf_to_md.py`, `app.upload_transcript` |
| Eval suite | See **Evals** below | **Real** | `eval/*` |

## Evals (what's measured + latest, with honesty caveats)
- **Regression (REG-01…16):** pins the grounding guarantees. `eval/regression.py`. **Gating, deterministic.**
- **Support judge calibration:** `eval/judge_eval.py` — 34-case gold set. After the `c05` prompt fix, **live FNR 0% / FPR 6.67%** (`docs/JUDGE-CALIBRATION-2026-06-08.md`). *Caveat: model-prompted, advisory — the deterministic gate is the floor; the 2 held-out generalization cases are same-author, not a blind holdout.*
- **Source-faithfulness:** `eval/source_faithfulness.py` — guide-claim ⊆ cited span. Caught the **real Q4 guide↔transcript drift** live (FN 0% on the fixture). Catches what the verbatim gate + quiz gate structurally can't.
- **Quiz reliability sweep:** `docs/QUIZ-RELIABILITY-INV-DISTRIBUTION.md` — 10× on one guide: 59/60 kept, **0/10 fully-clean runs**, ~2–3 real wrong-keys after triage. The verbatim gate passed all; only the support judge caught them.
- **Trace-back audit:** `docs/TRACE-BACK-AUDIT-INV-DISTRIBUTION.md` — a **standing manual SME gate** (the backstop for the judge's residual FN). **Scaffolded, NOT yet SME-run.** "0 automated flags ≠ safe until trace-back runs."
- Also: triage classifier (`eval/triage_eval.py`), scope/lane-purity (`eval/scope_eval.py`), coverage, source-quality, `eval/report.py` (Jaime dashboard).

## IN PROGRESS (current to-dos — see plan file)
1. **Header & nav re-carve + provenance** — quiet utility row (workspace ▾ · Trainer/Customer · ✓ trust badge · avatar) vs slim primary nav; "How it works" → "?"; Library = AI-only, imported → Content, provenance badges. *Not* a Studio/Deployments/Insights rename.
2. **Projects + content allocation** — "+ New Project" in the workspace dropdown (façade); assign a track to a role/site in a project.
3. **Track builder** — right-slide drawer, **search-to-add** approved guides (pills + dedupe, no drag-drop), attach an auto-grounded quiz, optional video, Save → Learn grid. No free quiz-question authoring.
4. **Trainer day-view + approval inbox** — projects, course statuses, "N approved by PM team" inbox.

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
