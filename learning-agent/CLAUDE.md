# Learning Content Producer — Operating Instructions

> **New session? Read `HANDOFF.md` first** — current state, the Windows run gotchas
> (ProactorEventLoop, no big text in system_prompt), the two-copy repo layout, and what's
> next. Then `docs/REPO-WORKFLOW.md` (pushing) and `docs/NEXT-EVALS-PLAN.md` (evals).

## Purpose
Turn training transcripts into structured, fact-checked learning content that staff can use on day one.
The published learning library is the deliverable. Transcripts are the raw material.

## Architecture

Two models, clear roles:
- **Generator agent** — maps, plans, verifies, writes. Owns Tasks 1–4.
- **Evaluator** — separate model. Grades the output and routes failures. Owns Task 5.

The generator decides HOW to produce. The evaluator decides IF it's good enough.

## Enforcement vs. documentation (read first)

This file is **standing instruction surface** — an agent loads it directly. So the same discipline we apply to grounding applies here: **hard guarantees live in code, not in this prose. This file documents them; editing it cannot create, weaken, or disable a guarantee.** If you change an *enforced* rule below, change the enforcing code and its test in the same commit, or this doc is lying. Rules that are conventions or not-yet-built are labeled as such — do not treat them as guarantees.

**Enforced by construction (code is the authority — rely on these):**
- **Verbatim citations + correct tier (no Description-as-AC).** The registry builds quote spans from the real Jira fields; section writers emit only `[CITE:id]`; `demo.validate_citations` checks tier+span and is the publish gate. Pinned by `eval/regression.py` (REG-01…16). The model has no channel to type a tier or quote.
- **Approval is the only gate into the Library; the agent never auto-approves.** `demo_app.approve_resource` re-validates grounding live before allowing approval; only a human POST approves.
- **AI edits can't break grounding.** The edit agent emits find/replace ops and cannot touch `<!-- Source -->` comments; the deterministic gate re-runs after every edit (`revise.py`, `demo_app.revise_resource`).
- **Identifier resolution at ingestion.** Parents resolve to real keys or are dropped — never a bare id, never a phantom stub (`build_fixtures_from_csv.py`, `test_ingestion.py`, REG-16). See README → *Identifier handling at ingestion*.

**Conventions / model-prompted (NOT hard guarantees — do not rely on as enforced):**
- Template length/section "hard constraints" below, **especially TLDR "one page"** — these are targets the prompt asks for and the eval *measures* (length = G6), not guarantees. TLDR length is a known overrun (see `docs/STATE-OF-EVAL-*`).
- Coverage / "no major feature omitted" / "no cross-feature pattern matching" / relevance — **not deterministically checked** (coverage + semantic relevance are unmeasured; STATE-OF-EVAL). The gate proves provenance, not relevance or completeness.
- "Transcript is voice, Jira is truth" and the `[TO VERIFY]` discipline — prompt conventions; the gate enforces only that citations are verbatim + correctly tiered.

**Described target spec, NOT in V1 (see "V1 Implementation Notes" at the bottom):**
- The Evaluator Task-5 LLM grader + failure **routing** + "max 3 retries" — V1's gate is the **deterministic** `validate_citations`; the LLM evaluator/routing is not implemented.
- `published/` move + immutability — V1 flips a `status`/`approved` flag on the draft; it does not move files.
- Quizzes/flashcards and the regeneration workflow — not built.

## Directory Rules
- `raw/transcripts/` — one file per upload, filename = `<DATE>-<module>-<slug>.md`. Stored permanently. Never modified after initial save — the transcript is an immutable source.
- `raw/transcripts/metadata/` — extracted metadata JSON per transcript (matched tickets, epics, roles, priority signals). Written by Task 1; updated only if re-mapped.
- `drafts/` — generated HTML drafts, one per job. Filename = `<DATE>-<module>-<template>-draft.html`. Overwritten on retry. Moved to `published/` on publish.
- `published/` — final HTML. Immutable once published. Edits create a new version, not an overwrite.
- `published/metadata/` — catalog entry JSON per resource (module, template type, roles, status, version, source transcript, generation timestamp).
- `templates/` — prompt definitions per template type. Each file is a complete system prompt for Task 4.
- `evaluator/` — evaluator prompt and routing rules. Separate from generator templates.
- `logs/` — per-job trace: Task outputs, evaluator decisions, retry history. Retained for debugging.

## Template Definitions

Three template types. The template controls selection scope, depth, and section structure. Same transcript, same metadata — different template produces different content.

> The "Hard constraint" lines below are **targets** (prompt-asked, eval-measured), **not** code-enforced guarantees — see *Enforcement vs. documentation*. TLDR "one page" is a known overrun today.

### Long-form guide (~20 pages)
- **Goal:** Comprehensive reference. A staff member can learn the entire module from this alone.
- **Selection:** All features included. No omissions without explicit reason.
- **Depth:** Full — setup, step-by-step workflows, field definitions, edge cases, troubleshooting, cross-module references.
- **Sections:** Overview · Roles and permissions · Prerequisites · Full workflows · Key fields and statuses · Reports and outputs · Exceptions · Troubleshooting · Related content · Sources
- **Hard constraint:** No major feature omitted without an explicit reason logged in the generation trace.

### Micro guide (~3 pages)
- **Goal:** Task success. A staff member can perform the top workflows after reading this.
- **Selection:** Top 3–5 workflows by priority. Lower-priority features mentioned in one line or omitted.
- **Depth:** Moderate — key steps, one common pitfall per workflow, enough context to execute.
- **Sections:** Purpose · Who this is for · Before you start · Top workflows · Common mistakes · Related content · Sources
- **Hard constraint:** No more than 5 workflows with full steps. If the plan includes more, the template type is wrong — suggest long-form instead.

### TLDR one-pager (1 page)
- **Goal:** Scan speed. A staff member can see every feature at a glance.
- **Selection:** All features included — completeness matters because omission implies the feature doesn't exist.
- **Depth:** Surface — feature name + one sentence each. No step-by-step.
- **Sections:** What this module does · Key features (2-column layout) · Who uses it · Common workflows (bullets) · Important gotchas · Where to go next
- **Hard constraint:** One page. If the content exceeds one page, compress — do not overflow to two.

## Generator Agent — Task Sequence

Tasks run in fixed order. The generator does not skip or reorder tasks. Each task's output feeds the next.

### Task 1: Map transcript to Jira
**Tools:** `parse_transcript`, `match_tickets`

Parse the transcript to identify features and workflows mentioned. Match them to Jira tickets by vector similarity against RN + AC fields, filtered by the user-selected module.

**Outputs:**
- Feature inventory: list of features/workflows with matched ticket IDs
- Metadata per feature: epic, priority, RN visibility (External Only / External-Internal), AC text, cross-module references, roles mentioned
- Unmatched items: anything in the transcript that couldn't be matched to a ticket — flagged, not silently dropped

**Field read order (same as jira-brain):**
1. Acceptance Criteria — the agreed workflow
2. Release Notes + Release Notes Title — customer-facing voice
3. Release Notes (Internal) — internal context when populated
4. Description — supporting context only, lowest trust

If AC is empty, say so in the metadata. Do not silently fall back to Description.

### Task 2: Plan the content
**Tools:** none — reasoning only

Using the feature inventory from Task 1 and the selected template type, decide:
- Which features to include at full depth
- Which features to mention briefly (one line)
- Which features to omit (with reason)
- Section order
- Depth per feature

Priority signals for inclusion decisions:
- Jira priority field (High > Medium > Low)
- RN visibility (External-facing tickets are more relevant to staff training)
- Role relevance (does this feature apply to the audience the transcript was training?)
- Cross-module references (mention, don't deep-dive — link to the other module's content)

The plan is not a formal artifact requiring approval. It lives in the graph state as the agent's reasoning. The evaluator checks the output against the plan post-generation.

### Task 3: Fact-check against KB
**Tools:** `search_kb`, `read_ticket`

For each planned section, verify that what the transcript presenter said matches what Jira AC and the knowledge base say. This is verification, not retrieval for content — the transcript is the primary voice.

**Check for:**
- Presenter described a workflow that doesn't match current AC (could be outdated, misspoken, or describing a future release)
- Presenter mentioned a feature that can't be found in Jira (could be informal name, could be invented)
- Presenter gave specific numbers, limits, or field names that differ from AC
- Presenter described behavior from a different module (cross-feature pattern matching — flag it)

**Outputs:**
- Verified claims: transcript statement + supporting Jira source
- Flagged discrepancies: transcript says X, Jira says Y — both quoted verbatim
- Unsupported statements: no Jira match found — included in draft only if explicitly marked as unverified

Do not silently correct the presenter. Surface the discrepancy and let the human editor decide.

### Task 4: Generate learning content
**Tools:** `compose_section`

Write each section following the template structure. The transcript is the primary voice — the content should sound like it came from the training, not from a database query. Verified facts from Task 3 are incorporated. Unverified claims are either omitted or marked.

**Citation rules:**
- Every factual claim cites a source: transcript timestamp, ticket ID, or both
- Citations are inline HTML comments (`<!-- Source: NXT-4521 AC: "verbatim quote" -->`) in the draft — stripped before publish
- If a claim cannot be cited, it is cut. No "best-practice" insertions, no "industry-standard" framing.
- Transcript timestamps use format `[MM:SS]` referencing the source recording

**Generation rules:**
- Use the template's section structure exactly. Do not invent new sections.
- Match the template's length constraints. If the content exceeds the target, compress — do not add pages.
- Cross-module references get one line + a link placeholder. Do not deep-dive into another module's content.
- Internal jargon from Jira (field codes, dev shorthand) is translated to user-facing language. The original term is preserved in the citation comment.

## Evaluator — Task 5

> **V1 reality:** the publish gate is the **deterministic** `validate_citations` (a string match against ground truth), not an LLM grader. The LLM evaluator, failure **routing**, and "max 3 retries" described below are the **target spec, not implemented** — see *Enforcement vs. documentation* and "V1 Implementation Notes". The deterministic gate is the authority; an LLM grader, when added, is advisory.

Separate model from the generator. Reviews the draft against three things:

1. **Template fit** — does the draft match the expected structure, sections, and length? A TLDR that exceeds one page fails. A micro guide with 8 workflows fails.
2. **Plan alignment** — does the draft cover what the plan said to cover? Are omitted features actually omitted (not silently dropped)? Are features marked "mention briefly" actually brief?
3. **Source grounding** — does every factual claim have a citation? Are flagged discrepancies from Task 3 handled (either corrected or marked)?

### Routing on failure
The evaluator diagnoses WHERE the failure originated:

| Failure type | Route to | Example |
|---|---|---|
| Wrong features mapped | Task 1 | Draft discusses features not in the transcript |
| Bad prioritization | Task 2 | Low-priority features got full sections, high-priority features were omitted |
| Unverified claim in draft | Task 3 | Fact-check missed a presenter statement that contradicts AC |
| Template violation | Task 4 | Content is correct but too long, wrong structure, or missing sections |

Maximum 3 total retries across all routes. After 3 failures, exit with the best draft and a log of unresolved issues for the human editor.

## Anti-Hallucination Rules

Adapted from jira-brain CLAUDE.md. These apply with full force — learning content is customer-facing.

### 1. Cite or cut
Every non-obvious claim needs a named source (transcript timestamp, ticket ID, or both). If you can't name the source, delete the claim. "The product probably supports X because other modules do" is not evidence.

### 2. No cross-feature pattern matching
Do not import capability claims from one module into another without source evidence in the target module. If the transcript presenter mentioned a feature from a different module, flag it as cross-module — do not incorporate it as if it belongs to the current module.

### 3. Transcript is voice, Jira is truth
The transcript provides the teaching style, examples, and narrative flow. Jira AC provides the ground truth for what the product actually does. When they conflict, the draft flags the conflict — it does not silently pick one.

### 4. No invented specifics
If the transcript and Jira do not state an exact label, menu path, value, or error string, do not insert one. State the gap as a `[TO VERIFY]` marker in the draft for the human editor.

### 5. Verify before publish
Before any artifact moves from `draft` to `published`:
- Each claim traces to its source
- Each source has been read directly, not surfaced from search snippets
- "Reads well" is not the standard; "matches what it cites" is

## Transcript Parsing Rules

Transcripts are messy. Training recordings include crosstalk, off-topic tangents, Q&A that may not be relevant to the content, and verbal corrections ("actually, wait, that's not right — let me redo that").

### What to include
- Demonstrated workflows (presenter showing how to do something)
- Explicit tips or warnings ("watch out for this" / "common mistake is")
- Feature descriptions and explanations
- Q&A where the answer contains product information

### What to exclude
- Crosstalk and side conversations
- Scheduling logistics ("let's take a break")
- Opinions not grounded in product behavior ("I think they should change this")
- Verbal false starts that the presenter corrected — use the corrected version only

### When the transcript is ambiguous
If the presenter says something that could be interpreted multiple ways, and Jira AC doesn't clarify, mark it as `[AMBIGUOUS — presenter said "X" at MM:SS, could mean A or B]` for the human editor.

## Quiz and Flashcard Rules

Quizzes and flashcards are generated from **published content only**, never from raw transcripts or draft HTML. This ensures the learning validation tests what the approved content teaches, not what a presenter may have misspoken.

### Quiz rules
- Questions must cite the guide section they test
- Answer options must be grounded in the published content — no plausible-but-wrong distractors invented from outside the content
- Minimum 3 questions, maximum 10 per resource
- Each question tests a distinct concept or workflow — no two questions testing the same thing with different wording

### Flashcard rules
- Front: scenario, term, or question
- Back: correct procedure, definition, or answer
- Every card traces to a specific section of the published content
- Procedural cards ("What do you do when X?") preferred over definitional cards ("What is X?")

## Status Gating

Two floors, in order. The machine floor is automated; the human floor is the gate into the Library.

- `draft` — generated by the agent, not yet approved. Default.
- `approved` — a human reviewed the grounded draft and signed off. **This is the gate INTO the Library** — only approved content appears there and feeds quiz/flashcard generation. Approval re-validates grounding live before it is allowed.

**The deterministic grounding gate is the machine floor** (a draft can't be approved until every citation is verbatim and correctly-tiered). **Human approval is the floor into the Library.** Do not flip to `approved` without an explicit human decision — the agent never approves autonomously. Unapproved drafts are never shown in the Library; they sit in its "Awaiting review" queue.

(`pending_sme_review` remains as a legacy released-but-unapproved status for older items; the current flow uses `approved`.)

## Human Review & AI-Assisted Edits

After the grounding gate passes, the reviewer reads the draft and either **approves** it (into the Library) or **requests edits**. Edits are AI-assisted, not a raw editor — and they cannot weaken grounding:

1. **The edit agent emits targeted find/replace ops, never a whole-doc rewrite.** It is structurally barred from modifying, moving, or deleting any `<!-- Source: ... -->` citation comment (the server rejects any op whose text touches one), and from introducing new product claims that aren't already cited. If an instruction needs a new fact, the agent refuses or inserts a `[TO VERIFY]` marker — never a fabricated citation.
2. **The deterministic grounding gate re-runs after every edit** (free, instant). A bad edit that breaks a citation is caught and blocks approval. Grounding stays a property of the system, not a hope.
3. **The edit-triage router is a lightweight classifier, advisory only.** It tags each edit `stylistic` (wording/format — safe to approve) or `substantive` (a claim/number/label/step may have changed — read closely), defaulting to `substantive` when unsure. It can only route to an *extra* check; it can **never** skip the grounding gate. Keep it a classifier (Haiku-class or a rule), not another agent — a full agent here would re-introduce the latency and non-determinism the architecture removed.
4. An edit re-opens review: an approved guide drops back to `draft` until re-approved. Pre-edit versions are retained for audit.

This mirrors the case study's converged policy and Anthropic's guidance: a "validating" approval gate (single approver, others get visibility not approval rights) plus a "routing" classifier (simplest thing that works; only add agency where the task is genuinely open-ended).

## Regeneration Workflow (template prompt changes)

When a template prompt in `templates/` is updated:
1. Identify all published resources generated from that template (query `published/metadata/`)
2. Surface the list to the user: "N resources were built from this template. Regenerate?"
3. On confirmation, re-run Tasks 2–5 for each resource using the stored transcript and updated template
4. Regenerated content enters `draft` status — it does not auto-publish even if the previous version was published
5. Human reviews and re-publishes

This is Dallas's "16 guides attached to this template" scenario. The stored transcript table makes it possible — without persistent transcript storage, regeneration requires re-uploading every source file.

## On Expanding This Rule Set

If a new failure mode appears in a future session, first check whether an existing rule already covers it and just wasn't applied. Fewer rules applied consistently produce better behavior than more rules applied inconsistently. Resist the urge to add a rule when enforcing an existing one would suffice.

---

## V1 Implementation Notes (delta from full spec)

For the end-of-June PM demo, the following are intentionally deferred to V1.5:

- **Evaluator (Task 5) is not implemented.** Generator runs Tasks 1–4, hands draft to human editor.
- **Tasks 1–4 are one Claude Agent SDK `query()` call,** not four. The system prompt walks the agent through them in order. V1.5 refactor: split into four separate calls so the Evaluator's task-routed retries can target a specific failed task.
- **`match_tickets` uses JQL text search,** not vector similarity. V1.5 upgrade: index all NXT tickets in Chroma.
- **`search_kb` searches `jira-brain/raw/guides/markdown/<...>.md` (curated) + `jira-brain/wiki/concepts/*.md` + `jira-brain/wiki/workflows/*.md`.** Excludes `.raw.md` (noisy bot extraction) and `wiki/packets/*.md` (internal-only).
- **Quiz + Flashcards not built.** V1.5.
- **Template editor + regeneration workflow not built.** V1.5.
- **PDF/Word transcript upload not built.** V1 accepts `.md` and `.txt` only. PDF fallback per Dallas comes in V1.5.
- **Human review + AI-assisted edit + approve gate are implemented in the demo server** (`demo_app.py` + `revise.py` + `static/index.html`); the production port (`app.py`) is specced in `docs/ADR-001`. No raw rich-text editor — edits go through the grounding-safe AI-edit path.
- **The edit-triage classifier has a dedicated eval** (`eval/triage_cases.jsonl` + `python -m eval.triage_eval`): 24 balanced cases, deterministic FPR/FNR scorer, FNR (under-trigger) gated. It is advisory (can't weaken grounding). Pending: a `--live` calibration baseline, real reviewer-edit cases (synthetic-only today), and a two-stage fast-filter router. See `eval/EVAL-SPEC.md` §7.
