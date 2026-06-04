# Learning Content Producer — Operating Instructions

## Purpose
Turn training transcripts into structured, fact-checked learning content that staff can use on day one.
The published learning library is the deliverable. Transcripts are the raw material.

## Architecture

Two models, clear roles:
- **Generator agent** — maps, plans, verifies, writes. Owns Tasks 1–4.
- **Evaluator** — separate model. Grades the output and routes failures. Owns Task 5.

The generator decides HOW to produce. The evaluator decides IF it's good enough.

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

- `draft` — generated by the agent, not yet human-reviewed. Default.
- `review` — sent to SME or team member for review.
- `published` — human-approved. Only `published` content appears in the directory and feeds quiz/flashcard generation.

Do not flip to `published` without an explicit human decision. The agent never publishes autonomously.

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
- **Rich text editor is a textarea.** V1.5 swaps in Tiptap or Quill.
