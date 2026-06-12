# HANDOFF — Learning Studio (read this first, next Claude)

Context + operating instructions for picking up this project. Pair with:
`CLAUDE.md` (product rules), `docs/REPO-WORKFLOW.md` (how to push), `docs/NEXT-EVALS-PLAN.md`
(what's next). User auto-memory also has: project-learning-studio, reference-learning-agent-windows-server,
feedback-minimize-permission-prompts, feedback-git-push-scope.

## What this is
Learning Studio turns sources into learning content (guides, quizzes, flashcards) where
**every claim is verbatim-cited to a real source at a trust tier** — "grounding by
construction." The product's whole value is trust, so the gates below are the spine.

## ⚠️ CRITICAL environment gotchas (Windows) — each one cost hours; don't relearn them
1. **Run the demo server as `python demo_app.py` — NOT `python -m uvicorn …`.** The Claude
   Agent SDK spawns the `claude` CLI as a subprocess, which on Windows needs asyncio's
   **ProactorEventLoop**; the Selector loop can't spawn subprocesses and you get a
   misleading `planning failed: Claude Code not found at …\_bundled\claude.exe`.
   `demo_app.py:__main__` forces the Proactor policy.
2. **Never inline large text into `ClaudeAgentOptions.system_prompt`.** The SDK passes it as
   a CLI arg (`--system-prompt`), which blows Windows' ~32 KB command-line limit → the same
   bogus "not found". Put transcripts/ticket dumps/chunks in the **user prompt** (stdin).
3. **Killing servers:** `powershell -NoProfile -Command "Get-Process python | Stop-Process -Force"`.
   git-bash `taskkill //PID` gets mangled. Find the port holder with `netstat -ano | grep :8001`.
4. **The preview screenshot tool frequently TIMES OUT.** Verify via DOM (`preview_eval`) +
   `curl`/API instead. Don't `location.reload()` *inside* a `preview_eval` — it aborts the eval.
5. **git:** `git config --global --add safe.directory <repo-path>` (folders are owned by Administrators).

## Where things live — there are TWO copies (this caused a real mess)
- **Repo:** `…/Financials-Documentation-KT/jira-brain/` → remote `github.com/beginnersmind94/jira-second-brain`, branch `main`. Learning Studio is **vendored at `jira-brain/learning-agent/`** (that's what's on GitHub).
- **Live working copy + server:** the **sibling** `…/Financials-Documentation-KT/learning-agent/` — NOT a git repo. Edits and the running server live here.
- **Always sync sibling → repo before pushing.** Flow: `claude/<topic>-<date>` branch → PR → merge to `main`. `gh` is NOT installed → open/merge the PR in the browser. Full steps in `docs/REPO-WORKFLOW.md`.
- **Open PR (unmerged as of handoff):** `claude/learning-studio-icn-quizzes-roster-2026-06-05`.

## Architecture (the trust spine)
- **Tenant isolation:** `tenancy.py` enforces district-level access at the API layer — not by seed data. Every district-scoped route calls `assert_district_access(user, isd)` before returning data; a 403 with `{"error": "district_access_denied"}` is raised on a cross-district read. Trainers are scoped to `user.districts` (their book of business); learners/directors to `user.district_id`. **Do not add a district-scoped route without calling `assert_district_access()` — see `tenancy.py` for the three public helpers.** Tests: `tests/test_tenancy.py` (18 cases).
- **Grounding by construction:** a registry of verbatim source spans is built deterministically; the model emits only `[CITE:<id>]` markers; a deterministic assembler renders the exact quote + tier; `validate_citations` re-checks every quote is a verbatim substring of its source. Mis-citation is structurally impossible.
- **Two source LANES that must never cross-cite:** **Product** (jira-brain Jira NXT tickets at tiers AC > RN > Description, + curated guides) and **Compliance** (the ICN/USDA pack in `data/icn/`: 85 assets, ~1,970 chunks, 30 ingestible). Lane is the first segment of every `span_id`; the gate refuses a cross-lane citation.
- **Three gate checks:** *verify* (deterministic, quote∈source) → *lane-match* (deterministic) → *support* (semantic LLM-judge — **needs calibration**, see eval plan). Distractors are exempt from grounding.
- **Question-bank curation gate** (`qbank_curation.py` + `qbank_gate_hooks.py`): state machine `pending_review → {auto_approved | needs_human} → human_approved → committed` (`rejected` terminal). `commit_to_bank` is the only writer; a **PreToolUse hook** denies it unless status is approved; a `canUseTool` callback handles human approval; `score_candidate` is pure + unit-tested.

## What was built this session
Transcript-only grounding mode · ICN **Content** tab (catalog of 85 assets, license-aware
cards, filters/sort, DataCamp-style course-path detail view, source/attribution) · grounded
**quizzes + flashcards** by topic (`/api/icn/quiz`, `/api/icn/flashcards`; verbatim-cited,
unverifiable items dropped) · the **question-bank curation gate** + tests
(`test_qbank_gate.py`, `test_qbank_gate_enforcement.py`) · lane-purity + semantic-support gate
(`qbank_gate.py`) + `data/qbank/adversarial_fixture.json` · `curator_walkthrough.py` (timed
cold-start → cited quiz probe) · **ISD roster/login simulation** (`/api/roster`, mock data) ·
**Trainer vs Customer two-view toggle** · **`EXTERNAL_LEARNING` on/off feature flag** ·
warm/terracotta redesign with design tokens + SchoolCafé branding (all in `static/index.html`).

## Norms & boss constraints (honor these)
- **External-learning (ICN content + roster + study sets) stays behind the `EXTERNAL_LEARNING` flag** until an ICN **fair-use agreement** is signed. Always **credit ICN** (attribution travels with every card/quiz). Respect `link_only` assets — link out, never reproduce.
- **Don't get too far down the rabbit hole.** Endorsed scope = basic quizzes + a customer content view. Bigger features (full question-bank UI, learning paths, drift) are explored but parked.
- **Two audiences:** Customer view (consume) vs internal **Trainer** view (author/ops). The Trainer is the curator; learners never author.
- **Verify by DOM/API, not screenshots.** Broad `Bash(*)`/`PowerShell(*)` permissions are set — don't add narrow rules; keep prompts minimal.

## Run it
`cd <sibling>/learning-agent && ./.venv/Scripts/python.exe demo_app.py` → http://127.0.0.1:8001.
Tabs: Create · Library · Content · Quality · Roster · How it works. Trainer/Customer toggle top-right.
`EXTERNAL_LEARNING=0` hides the whole external layer.

## What's next
1. **Compliance export scaffolded** — wire to real roster once SSO + multi-tenant isolation land (Tasks 11-13). Endpoints: GET /api/districts/{isd}/compliance-report + /pdf. Tests: tests/test_compliance_export.py (9 cases).
2. **Build #1 from `docs/NEXT-EVALS-PLAN.md`:** the semantic-support judge gold set + calibration (measure false-negative rate — the dangerous direction).
2. Then: lane-purity battery, triage balanced set, coverage/omission, drift/bank-freshness, canonical harness + `gate_log` (raise k to ≥3).
3. Merge the open PR. Draft the **ICN fair-use one-pager** for the ICN meeting. **Consolidate the two `learning-agent` copies** (root cause of drift).
4. External eval-expert brief lives at `~/Downloads/Learning-Studio-eval-context.md`.

## Key files
`completion_store.py` (disk-backed per-learner completion records; keyed by user_id; feeds /api/tracks/{id} progress + /api/tracks/{id}/progress + /api/certificates) · `auth.py` (identity interface: `CurrentUser` + `get_current_user` FastAPI dependency; demo stub until Task 11 SSO) · `demo_app.py` (FastAPI server, all routes incl. /generate, /api/icn*, /api/roster, /api/config) ·
`demo_d.py` (registry / assemble / section writers) · `demo.py` (offline tools + `validate_citations`) ·
`qbank_curation.py`, `qbank_gate_hooks.py`, `qbank_gate.py` (gates) · `static/index.html` (the entire UI — one large file) ·
`data/icn/` (ICN pack) · `data/demo/*-fixture.json` (Jira fixtures) · `eval/` (regression + capability) ·
`docs/` (ADR-001, STATE-OF-EVAL, CASE-STUDY, REPO-WORKFLOW, NEXT-EVALS-PLAN).
