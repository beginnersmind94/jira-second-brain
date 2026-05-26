# Jira Second Brain — Operating Instructions

## Purpose
Turn every Jira ticket into institutional knowledge that new hires can learn from.
The wiki is the deliverable. Tickets are the raw material.

## Directory Rules
- `raw/tickets/` — one file per issue, filename = issue key (FIN-1234.md). **Filename is stable; field contents mirror Jira.** Each ingestion run rewrites a ticket file when its Jira fields differ from what's on disk; identical content is a no-op.
- `raw/comments/` — comments grouped by issue key. Append-only.
- `raw/_imports/` — drop zone for Jira exports. Move to `_imports/processed/` after ingestion.
- `raw/guides/` — public SchoolCafé / Family Hub guide PDFs and their cleaned Markdown extractions. Two files per guide (`.raw.md` bot-owned, `.md` SME-curated); see [Guide Layer](#guide-layer-rawguides) below.
- `raw/guides/snapshots/` — `.raw.md` at last SME review; the drift baseline.
- `raw/guides/diffs/` — side-by-side HTML diffs written by the drift linter when a guide drifts. Auto-removed when drift clears.
- `wiki/` — you own this. Compile, link, and lint it.

### Mirror semantics caveat for wiki citations
Because ticket field contents track Jira (status, sprint, resolution, description, AC, components), wiki text that *paraphrases* a ticket's description can drift if Jira edits that description later. The wikilink target is always live — but the wiki page's prose may no longer match the ticket it cites. When citing, prefer naming what the ticket *did* (shipped behavior, decisions, scope) over quoting how it *was described*. Re-verify wiki claims against tickets if a major Jira edit pass happens.

## Guide Layer (`raw/guides/`)

Public, human-authored SchoolCafé / Family Hub guides. PDF sources and structured Markdown extractions live here, separate from Jira ticket ingestion.

### Layout
- `raw/guides/pdf/<Platform>/<Module>/<Content-Type>/<GUIDE-ID>-<slug>.pdf` — original PDF
- `raw/guides/markdown/.../<GUIDE-ID>-<slug>.raw.md` — bot-owned cleaned extraction; regenerated whenever the PDF or cleanup pipeline produces different content. Hash recorded in frontmatter (`raw_text_sha256`).
- `raw/guides/markdown/.../<GUIDE-ID>-<slug>.md` — SME-curated copy; seeded from `.raw.md` on first sight, then hand-edited. Tracks `curated_against_raw_sha`.
- `raw/guides/markdown/.../<GUIDE-ID>-<slug>.md.legacy` — archived single-file output from the pre-two-file extractor. Safe to delete once verified unneeded.
- `raw/guides/snapshots/<GUIDE-ID>.raw.md` — `.raw.md` at last SME review; the drift comparison baseline.
- `raw/guides/diffs/<GUIDE-ID>.diff.html` — side-by-side HTML diff (snapshot vs current raw), only present while a guide is drifted.
- `raw/guides/manifest.csv` — canonical index. Tracks `drift_status` (`clean` / `drifted` / `initial`), `raw_text_sha256`, both md paths, hoisted footer fields (`software_version`, `source_updated`), and extraction warnings via the `error` column.

### Authority rule
Guides are authoritative for **navigation only**: menu paths, page names, tabs, buttons, UI labels, task sequence, customer-facing procedure steps.

Jira tickets/specs remain authoritative for **behavior**: business rules, validations, permissions, accounting, backend behavior, edge cases, import behavior, duplicate handling, product strategy.

When guides and Jira conflict, prefer the guide for navigation and Jira for behavior, then flag the conflict for human review.

### Which Jira fields drive guide edits
When applying a ticket to a guide, read these fields in this order. **Description is the lowest-trust source** — it usually states the problem, not the agreed workflow.

1. **`Custom field (Acceptance Criteria)`** — the agreed workflow. This is what the guide should reflect.
2. **`Custom field (Release Notes)` + `Custom field (Release Notes Title)`** — the customer-facing voice. Captures warnings, conditional behaviors, sibling features, and the framing customers were actually told.
3. **`Custom field (Release Notes (Internal))`** — internal context when populated.
4. **`Description`** — supporting context only. Often a problem statement or pre-scope brainstorming; specifics may have changed before AC was finalized.

If AC is empty (`-` or blank), say so explicitly in the inline `<!-- Source: ... -->` citation. Do not silently fall back to Description.

A prior pass on the Accountability guides made the mistake of reading Description only; six of twelve edits had material gaps (wrong conditional logic, missing customer-facing warnings, missing workflow side effects) until AC + RN were consulted. See `raw/guides/ticket-updates/2026-05-18.md` for the failure modes that surfaced.

### Verbatim-citation rule for guide edits
Every proposed claim in a guide edit must trace to a **verbatim quote** from Acceptance Criteria or Release Notes. The rules:

- **Quote, don't paraphrase.** Use blockquotes (`>`) for source quotes in the changelog/review doc and within `<!-- Source: ... -->` citation comments in the guide files. Reproduce the source text exactly, including odd wiki-markup like `**` or `→`.
- **Distinguish quote from interpretation.** Any necessary bridging (combining quotes, applying them to the guide's section structure, naming product features) is labeled "Interpretation" or surfaced as a question. Never present interpretation as if it came from a source.
- **Do not invent specifics.** If AC and RN do not state an exact label, menu path, value, error string, or icon name, do not insert one. State the gap as an **Open question**.
- **Surface source contradictions; do not pick silently.** If AC says one thing and RN says another, quote both and let the SME decide.
- **If a claim cannot be supported by a verbatim quote, do not propose it.** No "best-practice" insertions, no "industry-standard" framing, no plausible-sounding bridges. If AC is empty and RN is empty, the edit is withheld — even when Description seems to describe a real feature; flag it for the product owner to backfill AC instead.
- **Internal jargon is translated, not quoted into guide text.** AC sometimes contains dev-team shorthand (system-setting codes like `BABECL`, abbreviations like `CRUD` in "Delete CRUD permission"). Verbatim copying of these into a customer-facing guide is wrong — a site manager doesn't know what `BABECL` is. Treat such tokens as Interpretation: render them in user-facing language in the proposed text (e.g., "the district's charge-limit setting"), preserve the original code in the Interpretation note inside the `<!-- Source: ... -->` comment, and add an Open question for the customer-facing label so the SME can fill it in. Verbatim ≠ appropriate-for-audience.

This standard was adopted after a pass where claims sourced from Description leaked into guide content as if they came from AC. The strict re-pass is documented in `raw/guides/ticket-updates/2026-05-18.md` (and `2026-05-18-review.md` for the per-edit evidence chain).

### Scripts
- `python scripts/ingest_guides.py "<masterlist.csv>"` — download PDFs from the public masterlist, organize by platform/module/content-type, assign stable `GUIDE-NNN` ids, write `manifest.csv`.
- `python scripts/extract_guides_markdown.py` — re-extract any guide whose PDF or cleanup output produces a different `raw_text_sha256`. Updates `.raw.md`, seeds missing `.md`/snapshot, sets `drift_status`. Pass `--force` to regenerate everything (useful when the cleanup pipeline itself changes).
- `python scripts/lint_guide_drift.py` — find guides with `drift_status: drifted` and write a side-by-side HTML diff for each into `raw/guides/diffs/`. Stale diff files (drift cleared) are removed.
- `python scripts/mark_guide_reviewed.py <GUIDE-ID> --by "name@org"` — SME closes the review loop. Refreshes the snapshot to current `.raw.md`, stamps the curated file's frontmatter (`curated_against_raw_sha`, `curated_against_raw_at`, `last_reviewed_by`, `status: reviewed`), clears `drift_status` in the manifest, deletes the diff file.

### Drift workflow when Cybersoft updates a PDF
1. Drop the new PDF into the existing path (or re-run `ingest_guides.py`).
2. Run `extract_guides_markdown.py` — any guide whose cleaned content changed gets `drift_status: drifted`.
3. Run `lint_guide_drift.py` — diff files appear in `raw/guides/diffs/`.
4. SME opens each `<GUIDE-ID>.diff.html` in a browser (red = removed, green = added, yellow = changed; frontmatter and H1 are excluded so only substantive content shows).
5. SME updates the matching `<GUIDE-ID>-<slug>.md` to reflect what changed.
6. SME runs `mark_guide_reviewed.py <GUIDE-ID> --by "name@org"`. Drift cleared.

### Citation caveat for wiki use of guides
Same shape as the ticket mirror caveat: a wiki page that cites a curated `.md` is citing the SME's last-reviewed understanding of that guide. The `.raw.md` is the current PDF. If the manifest shows `drift_status: drifted` for a cited guide, treat wiki claims sourced from it as potentially stale and re-check after SME review. The hash in the curated file's `curated_against_raw_sha` is what the citation is anchored to.

### Multi-column / orphan layouts
Quick Cards (two-column reference cards with image-anchored icons) are flagged with `extraction_warnings: ["possible_multi_column_layout"]` in the `.raw.md` frontmatter and as `error: possible_multi_column_layout` in the manifest. These need manual curation — the icon descriptions are orphan paragraphs without their anchor labels, and the cleanup pipeline cannot recover what was carried by the image alone.

## Page Types in wiki/

### concepts/
Domain or product concepts that recur across tickets. Each page:
- What the concept is, in plain language
- How it shows up in our product
- Tickets that shaped current behavior (wikilinks to raw/)
- Open questions or known edge cases

### workflows/
How we do things. Each workflow cites 3–8 example tickets.

### entities/
People, teams, modules, customers. Cross-linked everywhere relevant.

### decisions/
Architectural or product decisions. Format: Context → Options → Decision →
Consequences → Source tickets.

### onboarding/
Role-specific starter guides, DERIVED from concepts + workflows + decisions.

### training/
Training documents for specific skills/topics.

## Wiki-Writing Rules
1. Every factual claim must wikilink back to a source ticket in `raw/tickets/`.
2. Use plain language. Assume the reader is a new hire who joined yesterday.
3. When two tickets contradict, flag with `> [!warning] Contradiction` listing both.
4. Prefer concepts/ and workflows/ over ticket-by-ticket summaries.
5. Redact customer PII (names, emails, phones). Use role labels like `<District A>`.
   PII may remain in raw/.
6. Update `wiki/index.md` and append to `wiki/log.md` on every ingestion run.

## Low-Signal Tickets
Tickets resolved as Duplicate or Won't Do, OR with no description AND <2 comments,
are low-signal. Create the raw/ file with `low_signal: true` in frontmatter.
Do NOT create wiki pages from them unless they demonstrate an otherwise-invisible
workflow pattern.

## Linting Rules
- Every wiki page must have ≥1 source ticket link.
- Every entity mentioned by name must have an entities/ page.
- Scan for broken wikilinks.
- Flag concept pages with <3 source tickets as merge candidates.
- Flag pages with no new tickets in 90+ days as stale.

## Anti-Hallucination Rules (for customer-facing and onboarding docs)

These exist because customer-facing writing ("plain English, reads well") creates
pressure to smooth over gaps in source evidence. Every rule below is a specific
guard against a failure mode that has actually occurred.

### 1. Persona-first, always
Before writing a single sentence of a customer-facing doc, grep every source
ticket for `^As a` / `^As an` and list the personas. The actor in the doc's verbs
must match one of those personas. If your sentence says "the district admin does X"
but every ticket says "the Cybersoft Implementation team does X," the sentence is
wrong regardless of how natural it sounds.

**Failure mode guarded:** fluency-over-grounding. When doc tone pushes toward
customer-friendly voice, "As a Cybersoft Implementation team member" silently
becomes "As a district user" — and the doc now claims agency the product doesn't give.

### 2. Cite or cut
Every non-obvious claim — whether backed by a Jira ticket, an external article,
or a research paper — needs a named source before it ships. If you can't name
the source, delete the claim. Pattern-matching ("the product probably supports X
because other modules do") is not evidence.

**Failure mode guarded:** ghost references / fabricated features. E.g. inventing
cross-district form sharing because other multi-tenant features allow it.

### 3. No cross-feature pattern matching
Do not import capability claims from one feature area into another without
source-ticket evidence in the target area. Audit trails in Accountability tickets
do NOT imply audit trails in Forms. Each feature gets grounded independently.

**Failure mode guarded:** context contamination. E.g. writing an "audit trail"
FAQ entry for Forms because it was a real feature of Accountability.

### 4. Tag ownership on every action
In onboarding docs, every step has an owner tag: `Cybersoft`, `Your team`,
`Cybersoft + Your input`, or `Parent/applicant`. If you can't assign ownership
from source tickets, the step is unresearched — stop and research before shipping.

**Failure mode guarded:** implied-agency drift. Customers read unqualified verbs
as "we do this ourselves" by default.

### 5. Verify before ready
Before any artifact is marked ready (customer-facing draft, citation, claim, output):
- (a) Each claim traces to its source.
- (b) Each source has been read directly — not surfaced from search snippets.
- (c) "Reads well" is not the standard; "matches what it cites" is.

When a capability is ambiguous, the safe default is "not supported today" — never
invent a feature to close a gap.

**Failure modes guarded:** the "helpful yes" hallucination (inventing capabilities
to produce smoother answers), knowledge-saying disconnect (reading the right
tickets but writing contradictory output), citation unfaithfulness (a
real-but-misapplied citation is still a hallucination), and missing verification
("reads well" ≠ "is accurate").

---

## Sources that informed these rules (verified by direct read)
Each entry tagged by `source_type` so the incentive structure is visible at the
point of citation: `peer-reviewed` · `independent` · `vendor-marketing` · `other`.

- Alansari, A. & Luqman, H. *Large Language Models Hallucination: A Comprehensive Survey.* arXiv:2510.06265v3 (2025). `source_type: peer-reviewed-adjacent` (arXiv preprint). https://arxiv.org/html/2510.06265v3
- Tay, A. *Why Ghost References Still Haunt Us in 2025 — And Why It's Not Just About LLMs.* Substack, Dec 22, 2025. `source_type: independent`. https://aarontay.substack.com/p/why-ghost-references-still-haunt
- Lema, C. *AI Context Failures: Nine Ways Your AI Agent Breaks.* Feb 9, 2026. `source_type: independent`. https://chrislema.com/ai-context-failures-nine-ways-your-ai-agent-breaks/
- MindStudio Team. *AI Agent Failure Modes: 4 Ways Your Agent Knows the Answer But Says the Wrong Thing.* Mar 19, 2026. `source_type: vendor-marketing` (MindStudio sells AI agent infra). https://www.mindstudio.ai/blog/ai-agent-failure-modes-reasoning-action-disconnect
- Glean Team. *Understanding LLM hallucinations in enterprise applications.* Nov 6, 2025. `source_type: vendor-marketing` (Glean sells enterprise RAG). https://www.glean.com/perspectives/when-llms-hallucinate-in-enterprise-contexts-and-how-contextual-grounding

---

## On expanding this rule set
If a new failure mode appears in a future session, first check whether an existing
rule already covers it and just wasn't applied. Five rules produce more careful
behavior than eight. Resist the urge to add Rule 6.

---

## Resource & Template Rules (customer-facing content engine)

These rules govern `templates/`, `resources/`, and `catalog/resources.json`. The
five anti-hallucination rules above apply unchanged — customer-facing tone
demands the strictest grounding, not the loosest.

### 1. Templates define shape, not knowledge
A template in `templates/` is a scaffold: required frontmatter, required
sections, target length. When authoring a resource, fill the template's
sections. Do **not** invent new sections to accommodate material that doesn't
fit — that's a sign the content type is wrong for what you're writing. If
you genuinely need a new content type, add a new template AND extend
`catalog/resources.json`'s `content_types` array in the same change.

### 2. Every resource cites at least one wiki page or ticket
Same standard as wiki pages. No exceptions for "obvious" material. If the
claim is obvious, finding a citation costs nothing; if you can't find one,
the claim was less obvious than you thought. Anti-hallucination rule 2.

### 3. A resource doesn't exist until it's in the catalog
Adding a resource file without adding the matching entry to
`catalog/resources.json` is a half-finished change. The dashboard reads the
catalog; an uncatalogued resource is invisible. Adding the file and the
catalog entry is **one** unit of work — don't split it across commits.

### 4. Status field is gated
- `draft` — newly authored, not SME-reviewed. Default.
- `review` — sent to an SME or Charlie for review.
- `published` — SME-approved. Only `published` content goes to customer-facing
  builds. Do not flip to `published` without an explicit human decision.

### 5. `raw/transcripts/` is reserved, not active
Do not write scripts or resources that depend on transcripts being present.
The directory exists to reserve the name for a future ingestion path. If
the user mentions transcripts as a current input, ask before assuming any
file is there.

### 6. The five anti-hallucination rules apply with full force
Persona-first, cite or cut, no cross-feature pattern matching, ownership
tags, verify before ready. Resources are the customer-facing deliverable;
the failure modes those rules guard against are most likely to manifest
here. In particular: an "obvious" capability claim that hasn't been
sourced from a ticket is the single most likely failure mode for AI-drafted
resource content.

### 7. Resources draft against citation packets, not stubs
Customer-facing resources in `resources/` must NOT draft directly against
a thin wiki concept stub even if the stub has ticket links. Generate the
per-module citation packet at `wiki/packets/<module-slug>.md` first
(template: `templates/citation-packet.md`), then draft the resource
against the packet.

Packets carry `visibility: internal` in frontmatter and are excluded
from any customer-facing output. A published resource may have been
*drafted* against a packet, but its citations must trace to the
underlying ticket / wiki source chain, not the packet itself. The packet
is a drafting control — a workbench for separating safe claims from
unsafe ones, and for surfacing SME questions before they reach the
customer — not the final authority.

**Failure mode guarded:** citation theater. A resource cites a wiki
concept stub, the stub indexes 8 tickets, and the citation pointer is
mistaken for ticket-level evidence. Packets force claim-level grounding
before the resource is written, so each published claim has a real
chain to a directly-read ticket rather than a chain of redirects.
