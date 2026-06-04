# Repo Structure

A reference for what lives where, why it lives there, and how the pieces talk to each other. The README is the pitch; this is the map.

## Top-level layout

```
jira-brain/
├── README.md                # Elevator pitch + quick start
├── REPO_STRUCTURE.md        # You are here
├── CLAUDE.md                # Operating rules for Claude inside this repo
├── AGENTS.md                # Agent-facing operating notes (parallels CLAUDE.md)
├── WIKI_STRATEGY_CASE.md    # Strategic case for the wiki-as-citation-backbone approach
├── .brain-state.json        # Pipeline state (resumable checkpoints)
├── runs.log.json            # Per-script run history (timestamps, args, outcomes)
├── .gitignore               # Excludes raw CSVs, cleaned/ data, Claude scratch, output/
├── .claude/
│   └── commands/            # Slash command prompts (e.g. /apply-jira-to-guides)
├── raw/                     # Source-of-truth: Jira tickets + Cybersoft guide PDFs / extractions
├── wiki/                    # Compiled, human-curated knowledge (concepts, packets, guides, training)
├── templates/               # Boilerplate shapes for resource content types
├── resources/               # Publishable customer-facing entries (catalog-indexed)
├── catalog/                 # resources.json — the index the resource center filters against
├── scripts/                 # Pipeline (ingest → analyze → compile → guide-extract → categorize → render)
├── stage2/                  # Ticket categorization workspace (sample / propose / curate / tag)
├── reports/                 # Per-module dry-runs and filter outputs for guide-update workflows
├── app/                     # Flask POC: drop a PDF, apply Jira edits, review inline, export PDF
├── learning-agent/          # FastAPI POC: turn an SME transcript into a cited HTML learning resource
├── check_links.py           # Standalone wikilink validator
├── cleaned/                 # Cleaned Jira CSV + thresholds + data dictionary (gitignored)
├── cleaned_private/         # PII audit + district map (gitignored, never committed)
└── output/                  # Generated static site (gitignored)
```

Five load-bearing principles:

1. **`raw/tickets/` mirrors Jira and is ground-truth for behavior.** Filenames (`<KEY>.md`) are stable and never deleted. Field contents track Jira on each ingestion — `ingest.py` rewrites a file when its row differs from disk and no-ops when identical. Wiki pages cite raw tickets, never the other way around.
2. **`raw/guides/` mirrors Cybersoft's public guides and is authoritative for navigation only.** Menu paths, page names, tabs, button labels, customer-facing procedure order. When a guide and a ticket conflict, the guide wins on navigation and the ticket wins on behavior (see CLAUDE.md's "Guide Layer" rules).
3. **`wiki/` is the internal deliverable.** Concepts, workflows, entities, decisions, training, packets, and module guide drafts live here. Wiki citations resolve to `raw/`.
4. **`resources/` is the customer-facing deliverable.** Each resource follows one of the templates in `templates/`, cites at least one wiki page or ticket via a `wiki/packets/<module>.md` citation packet, and is indexed in `catalog/resources.json`. Drafts stay `status: draft` until SME-reviewed.
5. **`output/` is disposable.** Anything in it can be regenerated from `raw/` + `wiki/` + `resources/` + `catalog/`.

## Detailed structure

### `CLAUDE.md`
The operating manual Claude reads at the start of every session in this repo. Contains:
- Directory rules
- Wiki-writing rules (citations, plain language, PII handling)
- Low-signal ticket policy
- Linting rules
- The 5 anti-hallucination rules added after a real-session failure

This file is the highest-priority document in the repo. If anything in this doc contradicts CLAUDE.md, CLAUDE.md wins.

### `.brain-state.json`
Pipeline checkpoint file. Tracks which step of the ingestion/compilation pipeline is `pending`, `in_progress`, or `done`, plus per-step counters (tickets written, pages compiled, last key processed). Updated atomically (temp file + rename) so a crash never leaves it corrupt. Re-running any script reads this first and resumes where it left off.

Schema is documented in the script that writes it (`scripts/ingest.py` for steps 3-4, `scripts/compile_wiki.py` for step 5).

### `raw/`
Source data. Two parallel mirrors: Jira tickets (behavior) and Cybersoft guides (navigation). **Never write to `tickets/` by hand** unless you're correcting a ticket export error — `ingest.py` is the only writer there. The guide layer is partially bot-written (`.raw.md`) and partially SME-curated (`.md`); see the `raw/guides/` section below.

```
raw/
├── tickets/         # 8,849 markdown files, one per Jira issue
│   ├── NXT-100.md
│   ├── NXT-101.md
│   └── ...
├── comments/        # (reserved — empty for now)
├── attachments/     # (reserved — empty for now)
├── guides/          # Public Cybersoft guide PDFs + cleaned markdown extractions (see below)
├── transcripts/     # Reserved for future SME transcripts; README.md only
└── _imports/
    ├── *.csv        # Drop new exports here (gitignored)
    └── processed/   # Imported exports moved here after ingest
```

Each `raw/tickets/<KEY>.md` follows this shape:

```markdown
---
key: NXT-1234
summary: "Inv - Add filter to vendor list"
status: "Done Done"
resolution: ""
components: ["Inventory"]
sprints: ["Release 9.13"]
low_signal: false
---

# NXT-1234 — Inv - Add filter to vendor list

## Description
<original Jira description, markdown>

## Acceptance Criteria
<acceptance criteria from custom field>
```

Filename = issue key. Parsing the frontmatter gives every script a structured view. The body is preserved as-is for full-text search.

#### Low-signal tickets
Tickets resolved as `Duplicate` / `Won't Do`, or with no description and no acceptance criteria, get `low_signal: true`. They still get a `raw/tickets/` file (so wikilinks resolve), but `compile_wiki.py` skips them when generating concept pages.

#### `raw/_imports/`
Drop zone for new Jira exports. After ingestion, `scripts/ingest.py` moves the file into `raw/_imports/processed/`. Both directories ignore `*.csv` and `*.xml` in `.gitignore` — original exports never go to GitHub because they contain customer-facing language and may include PII.

#### `raw/guides/`
The public-guide mirror. Cybersoft publishes SchoolCafé and Family Hub PDFs at `docs.schoolcafe.com`. This subtree downloads them, organizes them by platform/module/content-type, and produces two parallel markdown files per guide — one bot-owned (`.raw.md`) and one SME-curated (`.md`).

```
raw/guides/
├── pdf/                            # Downloaded PDFs, organized by Platform/Module/Content-Type (gitignored)
│   ├── SC/Eligibility/Quick-Guide/GUIDE-NNN-<slug>.pdf
│   └── FH/Family-Hub/Quick-Guide/...
├── markdown/
│   └── <Platform>/<Module>/<Content-Type>/
│       ├── GUIDE-NNN-<slug>.raw.md         # Bot-owned cleaned extraction
│       ├── GUIDE-NNN-<slug>.md             # SME-curated copy
│       └── GUIDE-NNN-<slug>.md.legacy      # Archive of pre-two-file extractor output
├── snapshots/
│   └── GUIDE-NNN.raw.md                    # `.raw.md` at last SME review — drift baseline
├── diffs/
│   ├── GUIDE-NNN.diff.html                 # Side-by-side diff while a guide is drifted
│   └── proposed/all-<module>-diffs.html    # Combined diff from /apply-jira-to-guides
├── ticket-updates/
│   ├── <DATE>-<module>.md                  # Per-run changelog of edits applied to guides
│   └── <DATE>-<module>-review.md           # Per-edit verbatim-citation review doc (when used)
├── manifest.csv                            # Canonical index: GUIDE-ID, paths, sha256, drift_status, hoisted footer fields
└── failures.csv                            # Guides the extractor couldn't process (weak extraction, multi-column, etc.)
```

**Authority rule:** Guides are authoritative for navigation only (menu paths, page names, button labels, task order). Jira tickets remain authoritative for behavior (business rules, validations, permissions, edge cases). See CLAUDE.md → *Guide Layer* for the conflict-resolution rule and verbatim-citation requirements.

**Workflow:**
1. `python scripts/ingest_guides.py "<masterlist.csv>"` — pulls PDFs from the public masterlist, assigns stable `GUIDE-NNN` ids, populates `manifest.csv`.
2. `python scripts/extract_guides_markdown.py` — re-extracts any guide whose PDF or cleanup output changed; updates `.raw.md`, seeds missing `.md`, sets `drift_status`.
3. `python scripts/lint_guide_drift.py` — generates side-by-side HTML diffs into `diffs/` for guides where `drift_status: drifted`.
4. SME reviews `diffs/<GUIDE-ID>.diff.html`, updates the curated `.md`, then runs `python scripts/mark_guide_reviewed.py <GUIDE-ID> --by "name@org"` to refresh the snapshot and clear drift.

**Citation caveat:** A wiki page citing a curated `.md` is citing the SME's last-reviewed understanding of that guide. If the manifest shows `drift_status: drifted`, claims sourced from it may be stale until SME re-review.

#### `raw/transcripts/`
Reserved for future SME audio/video transcripts. Empty today; `raw/transcripts/README.md` documents the intent. **Nothing in the current pipeline depends on this folder** — do not write scripts that require it to be non-empty.

### `wiki/`
Compiled knowledge. **You own this.** Hand-edit freely; the auto-compiler only writes pages that don't already exist (write-if-absent).

```
wiki/
├── index.md                 # Top-level navigable map
├── log.md                   # Append-only compilation history
├── concepts/                # 22 pages — one per product module
├── workflows/               # Recurring cross-module patterns
├── entities/                # Team / module groupings
├── decisions/               # Explicit architecture/product decisions (1 page so far)
├── onboarding/              # (empty — derived role-specific guides)
├── training/                # Interactive learning artifacts + drafting workspace
├── packets/                 # Per-module citation packets (internal-only drafting control)
└── guides/                  # Internal SME-facing guide drafts (parallel to raw/guides/)
```

Page-type rules:

- **`concepts/<Slug>.md`** — one product concept (typically a Jira component). Each page must cite ≥3 source tickets via wikilinks. Filename slug is dash-separated (`Item-Management.md`, not `ItemManagement.md`).
- **`workflows/<slug>.md`** — how-we-do-things. Each cites 3-8 example tickets that shaped the flow.
- **`entities/<slug>.md`** — people, teams, modules, customer types. Cross-linked from anywhere they're mentioned.
- **`decisions/<YYYY-MM-DD>-<slug>.md`** — architecture/product decisions. Format: Context → Options → Decision → Consequences → Source tickets. Date-prefixed so the latest decision sorts last.
- **`onboarding/<slug>.md`** — role-specific starter guides, derived from concepts + workflows + decisions. Don't write these until the underlying material is solid.
- **`training/<slug>.html`** or **`.md`** — standalone interactive learning artifacts and drafting helpers. HTML files are single self-contained pages (no external CSS/JS) so they can be emailed or shared without dependencies. Python helpers prefixed with `_` (e.g. `_embed_md.py`) are local drafting tools, not part of the pipeline.
- **`packets/<module-slug>.md`** — citation packets. Internal-only (`visibility: internal` in frontmatter, excluded from any customer-facing output). Customer-facing resources in `resources/` must be drafted against a packet, not directly against a thin concept stub — see CLAUDE.md's *Resources draft against citation packets* rule.
- **`guides/<module-slug>/*.md`** — internal-facing guide drafts that the SME maintains alongside the Cybersoft mirror in `raw/guides/`. Used for drafting customer-facing edits that haven't yet been applied to a public PDF.

#### Training files (current)

| File | Audience | Type |
|---|---|---|
| `training/accountability-expert.html` | New PMs | 10-chapter interactive guide |
| `training/forms-onboarding.html` | Internal / leadership | Forms workstream summary |
| `training/forms-customer-onboarding.html` | Customers | Customer-shareable one-pager |
| `training/decision-trail.html` | Internal | Decision-history walkthrough |
| `training/whats-new.html` | Customers | What's-new digest |
| `training/wiki-tour.html` | New hires | Guided tour of the wiki |
| `training/resource-center.html`<br>`training/resource-center-v2.html`<br>`training/resource-center-v3.html` | Internal | Resource-center prototypes (filterable dashboard over `catalog/resources.json`) |
| `training/meeting-decision-1-pager.md` | Internal | Meeting decision template |
| `training/CHAT_HANDOFF.md` | Internal | Working handoff doc between Claude sessions |
| `training/_*.py` | — | Local drafting helpers (not pipeline scripts) |

#### Wikilink convention

Wikilinks use `[[path|label]]` syntax:

- From `wiki/concepts/Inventory.md` → ticket: `[[raw/tickets/NXT-1234|NXT-1234 — short summary]]`
- From `wiki/index.md` → concept: `[[concepts/Inventory|Inventory]]`
- From `wiki/entities/platform-team.md` → concept: `[[concepts/Platform-System|Platform - System]]`

The static-site builder (`scripts/build_site.py`) resolves these against multiple base paths so both vault-root-relative and section-relative links work.

### `templates/`
Boilerplate shapes for the five content types the resource center publishes. Each file is a markdown skeleton with required frontmatter, required sections, and target length. Templates are scaffolds, not knowledge — they define *shape*; `resources/` provides the *substance*.

```
templates/
├── long-form-guide.md       # 2,500–6,000 words, 30–60 min read
├── micro-guide.md           # 600–1,200 words, 5–10 min read
├── quick-reference.md       # ≤350 words, one-page printable
├── faq.md                   # 8–15 Q&A pairs, each source-cited
└── sop-how-to.md            # 400–900 words, step-by-step procedure
```

A new content type means a new template here, plus a matching entry in `catalog/resources.json`'s `content_types` array.

### `resources/`
Publishable, customer-facing entries. Each file:
- Frontmatter declares `id`, `title`, `platform`, `module`, `page`, `content_type`, `roles`, `tags`, `status`, `template`, `source_refs`, `updated`.
- Body follows the matching `templates/<content_type>.md` section structure.
- Every non-obvious claim cites a `wiki/` page or `raw/tickets/` ticket (CLAUDE.md anti-hallucination rules apply unchanged).

```
resources/
└── <module-slug>/                          # e.g. eligibility/
    └── <page-or-topic>-<content-type>.md
```

A resource doesn't exist for the dashboard until it is *also* registered in `catalog/resources.json`. The file alone is not enough; the catalog entry is what makes it filterable.

### `catalog/`
The index the resource-center UI filters against.

```
catalog/
└── resources.json
```

Required fields per resource entry:

| Field | Type | Notes |
|---|---|---|
| `id` | string | stable slug; matches the frontmatter `id` in the resource file |
| `title` | string | display title |
| `platform` | string | one of `platforms[]` (currently `schoolcafe` only) |
| `module` | string | product module name (e.g. `Eligibility`) |
| `page` | string | product page or workflow name |
| `content_type` | string | one of `content_types[]` |
| `roles` | string[] | subset of `roles[]` |
| `tags` | string[] | free-form, includes `frequency:daily/weekly/...` and topic tags |
| `status` | string | one of `statuses[]`: `draft`, `review`, `published` |
| `path` | string | repo-relative path to the markdown file |
| `source_refs` | string[] | repo-relative paths to the wiki pages / tickets cited |
| `updated` | string | ISO date |

Top-level vocabulary lists (`platforms`, `content_types`, `roles`, `statuses`) are the allowed values. The dashboard reads them to populate filter controls.

### `scripts/`
The pipeline. All resumable, all idempotent. Three roughly-independent tracks: ticket ingestion (the original), guide ingestion (added when guides became a first-class source), and stage2 categorization (a one-off-ish workspace for tagging the ticket corpus).

```
scripts/
├── ingest.py                          # Ticket track: CSV → raw/tickets/*.md
├── analyze.py                         # Ticket track: corpus frequency analysis
├── compile_wiki.py                    # Ticket track: generate concept/workflow/entity pages
├── build_site.py                      # Render wiki + raw as static HTML in output/site/
├── render_changelog.py                # Render ticket-update markdown to PDF
├── clean_im_data.py                   # Clean a Jira CSV into cleaned/tickets_clean.csv + reports
├── sample_narrative.py                # Sample tickets and emit a narrative summary
├── analysis_summary.json              # Frequency counts (written by analyze.py)
├── component_tickets.json             # Tickets grouped by component
├── phrase_tickets.json                # Tickets grouped by recurring phrase
├── sprint_tickets.json                # Tickets grouped by sprint
├── ingest_guides.py                   # Guide track: download PDFs + populate manifest
├── extract_guides_markdown.py         # Guide track: PDF → .raw.md (+ seed .md)
├── guide_text_cleanup.py              # Guide track: cleanup pipeline used by the extractor
├── lint_guide_drift.py                # Guide track: side-by-side HTML diffs for drifted guides
├── mark_guide_reviewed.py             # Guide track: SME closes the drift loop
├── stage2_sample_for_categorization.py  # Stage2: sample tickets for category proposal
├── stage2_emit_batch.py               # Stage2: emit a batch for LLM categorization
├── stage2_append_batch.py             # Stage2: append a tagged batch to the running file
├── stage2_categorization_report.py    # Stage2: report on categorization coverage
├── stage2_tag_tickets.py              # Stage2: apply curated categories back to tickets
└── stage2_epic_enrichment.py          # Stage2: enrich epics from categorized tickets
```

#### Data flow

```
  Jira CSV
     │
     ▼
  raw/_imports/*.csv   ──ingest.py────────▶   raw/tickets/*.md   +   .brain-state.json
                                                    │
                                                    ▼
                                              analyze.py          ──▶   scripts/*.json
                                                    │
                                                    ▼
                                              compile_wiki.py     ──▶   wiki/concepts/, workflows/, entities/, index.md
                                                    │
                                                    ▼ (optional)
                                              clean_im_data.py    ──▶   cleaned/*.csv + data dictionary

  Jira CSV
     │
     ▼
  stage2_sample_for_categorization.py  ──▶  stage2/sample_*.{json,txt}
            │
            ▼
  stage2_emit_batch.py / stage2_append_batch.py  ──▶  stage2/_batch_*.{json,txt}, ticket_categories_raw.csv
            │
            ▼
  stage2_categorization_report.py / stage2_tag_tickets.py / stage2_epic_enrichment.py
                                                                ──▶  stage2/curated_categories.md, epic_enrichment*

  Cybersoft masterlist CSV
     │
     ▼
  ingest_guides.py        ──▶   raw/guides/pdf/**, raw/guides/manifest.csv
                                              │
                                              ▼
                                        extract_guides_markdown.py    ──▶   raw/guides/markdown/**/*.raw.md (+ seed .md), snapshots/, manifest update
                                              │
                                              ▼
                                        lint_guide_drift.py           ──▶   raw/guides/diffs/<GUIDE-ID>.diff.html (when drifted)
                                              │
                                              ▼ (SME reviews + edits curated .md)
                                        mark_guide_reviewed.py        ──▶   refreshes snapshot, clears drift, stamps curated frontmatter

  All tracks feed:
  templates/ + wiki/ + raw/tickets/ + raw/guides/ + stage2/
                                              │
                                              ▼
                                        resources/<module>/*.md   +   catalog/resources.json
                                              │
                                              ▼
                                        build_site.py             ──▶   output/site/**/*.html
```

The ticket track writes `.brain-state.json` after meaningful units of work. None of the scripts require the others to have just run — each reads from the filesystem and picks up wherever the previous step finished. The guide track is similarly idempotent; re-running `extract_guides_markdown.py` is a no-op for guides whose `raw_text_sha256` hasn't changed.

#### What each script reads/writes (selected)

| Script | Reads | Writes |
|---|---|---|
| `ingest.py` | `raw/_imports/*.csv`, existing `raw/tickets/*.md` (for diff) | `raw/tickets/*.md` (new + changed), moves CSV to `processed/`, updates `.brain-state.json` |
| `analyze.py` | `raw/tickets/*.md` (frontmatter only) | `scripts/analysis_summary.json`, `scripts/component_tickets.json`, `scripts/phrase_tickets.json`, `scripts/sprint_tickets.json` |
| `compile_wiki.py` | `raw/tickets/*.md`, `scripts/*.json` | `wiki/concepts/*.md`, `wiki/workflows/*.md`, `wiki/entities/*.md`, `wiki/index.md`, appends to `wiki/log.md`, updates `.brain-state.json` |
| `build_site.py` | All `*.md` in `wiki/` and `raw/` | `output/site/**/*.html` |
| `ingest_guides.py` | Cybersoft masterlist CSV | `raw/guides/pdf/**`, `raw/guides/manifest.csv`, `raw/guides/failures.csv` |
| `extract_guides_markdown.py` | `raw/guides/pdf/**`, `raw/guides/manifest.csv` | `raw/guides/markdown/**/*.raw.md` (+ seeds missing `.md` and `snapshots/`), updates manifest `drift_status` and `raw_text_sha256` |
| `lint_guide_drift.py` | `raw/guides/manifest.csv` + paired `snapshots/` and `.raw.md` | `raw/guides/diffs/<GUIDE-ID>.diff.html` (creates when drifted, deletes when clear) |
| `mark_guide_reviewed.py` | `raw/guides/markdown/**/*.{raw.md,md}` | refreshes `raw/guides/snapshots/`, stamps curated frontmatter (`curated_against_raw_sha`, `last_reviewed_by`), clears `drift_status`, deletes the diff file |
| `clean_im_data.py` | a Jira CSV | `cleaned/tickets_clean.csv`, `cleaned/data_dictionary.md`, `cleaned/type_thresholds.json`, validation reports |

### `stage2/`
Workspace for tagging the ticket corpus with a curated category vocabulary. Generated artifacts, not hand-edited content. The pipeline samples tickets, proposes categories via LLM, an SME curates the vocabulary, then `stage2_tag_tickets.py` applies it back.

```
stage2/
├── tickets_in_scope.csv              # The ticket subset under categorization
├── sample_for_categories.json        # Sampled tickets used to propose categories
├── sample_compact.txt                # Human-readable view of the sample
├── proposed_categories.md            # LLM-proposed categories (input to curation)
├── curated_categories.md             # SME-curated category vocabulary (authoritative)
├── _tagging_conventions.md           # Tagging rules / conventions doc
├── _batch_text.txt                   # Current batch text being processed
├── _batch_buffer.json                # Current batch buffer state
├── ticket_categories_raw.csv         # Raw LLM-tagged output, batch by batch
├── epic_enrichment.csv               # Per-epic enrichment derived from tagged tickets
└── epic_enrichment_report.md         # Narrative report on epic enrichment
```

### `reports/`
Per-module dry-run outputs and filter results from guide-update workflows (notably `/apply-jira-to-guides`). These are intermediate artifacts — useful for review, not authoritative.

```
reports/
└── guide-updates/
    └── <Module>/                      # e.g. Eligibility/
        ├── _filter.py                 # Filter logic used for this module
        ├── _filtered_tickets.json     # Tickets selected after filtering
        ├── _digest.py                 # Digest builder
        ├── _digest.md                 # Human-readable digest
        ├── filtered_ticket_index.md   # Index of filtered tickets with links
        └── dry_run.md                 # Dry-run output before edits land
```

### `app/`
Internal Flask POC for the guide-edit-and-review flow. Drop a PDF, pick a module, the app runs the `/apply-jira-to-guides` pipeline via a subprocess call to `claude -p`, then renders an inline diff review UI; approved edits are applied and exported back as PDF.

```
app/
├── server.py            # Single-file Flask app — routes, templates inline
├── review.py            # Edit-review logic (approve / reject per edit)
├── smoke.py             # Smoke test
├── requirements.txt     # flask, pypdf, reportlab
└── jobs/<job-id>/       # Per-job scratch (uploaded PDF, extracted MD, proposed edits, output PDF)
```

**Internal only.** Not deployed; runs locally for SME review sessions. Per-job scratch is keyed by job id and not committed.

### `learning-agent/`
A second POC, vendored as a subproject. FastAPI server that takes an SME training transcript (markdown), runs a Generator → Evaluator pipeline via Claude Agent SDK + custom MCP tools, and produces a structured HTML learning resource with verbatim citations to live Jira (NXT) tickets pulled from the Cybersoft Atlassian Cloud.

```
learning-agent/
├── README.md                       # Runbook
├── CLAUDE.md                       # Operating instructions / architecture spec
├── eval-framework.md               # Evaluation framework
├── .env.example                    # Auth + Jira + jira-brain path config
├── .gitignore                      # .venv, __pycache__, .env, data/chroma_db, data/*.pdf
├── requirements.txt
├── app.py                          # FastAPI server (upload, generate, library, publish, evaluate)
├── agent_sdk.py                    # Generator — Tasks 1-4 in one query()
├── evaluator_sdk.py                # Evaluator — Task 5, separate query() call
├── tools.py / tools_sdk.py         # MCP tools: parse_transcript, match_tickets, search_kb,
│                                   #   read_ticket, read_epic, read_pdf
├── smoke_test.py                   # End-to-end CLI test
├── build_fixtures_from_csv.py      # Turn a raw Jira CSV into a curated fixture
├── build_stub_csv.py               # Build the smaller curated tickets.csv
├── pdf_export.py / pricing.py / prefetch_tickets.py
├── demo*.py / demo*.html           # Demo runners + per-template demo outputs
├── _discover_fields.py             # Inspection helpers (probing Jira fields, MCP options, etc.)
├── templates/                      # Generator system-prompt templates
│   ├── long-form.md                #   20-page comprehensive reference
│   ├── micro-guide.md              #   3-page task-success guide
│   └── tldr.md                     #   1-page at-a-glance summary
├── static/index.html               # Single-page UI (Author + Library modes)
├── data/
│   ├── 25_26-roadmap-tickets.csv   # Raw Jira CSV (full export, 130K rows) — input for build_fixtures_from_csv.py
│   ├── tickets.csv                 # Curated ticket fixture (623 rows) — used by stub mode
│   ├── sample-*.md                 # Sample transcripts
│   ├── demo/*.json                 # Per-module fixture data (eligibility, accountability, etc.)
│   └── uploads/                    # User-uploaded transcripts (runtime; empty in repo)
├── raw/transcripts/                # Saved SME transcripts (immutable once saved) + metadata/
├── drafts/                         # Generated HTML drafts (with inline <!-- Source: --> comments) + .eval.json
├── published/                      # Final HTML (source comments stripped) + metadata/ catalog entries
├── eval/                           # Evaluation framework
│   ├── EVAL-SPEC.md                # Spec
│   ├── capability.py / graders.py / pipeline.py / regression.py
│   └── runs/                       # Per-run eval artifacts
├── docs/                           # ADRs, case studies, eval state snapshots
├── logs/                           # Per-job JSONL traces (one per generation run)
├── .claude/                        # Project-specific Claude agent memory + settings
└── .codex/                         # Codex tooling config (test plan, agents, config.toml)
```

**Relationship to jira-brain:** This subproject's `search_kb` tool reads markdown from the parent jira-brain repo (`raw/guides/markdown/`, `wiki/concepts/`, `wiki/workflows/`). The `.env.example` defaults to `JIRA_BRAIN_PATH=../jira-brain` for the original sibling layout; when running from inside this monorepo, override that to `JIRA_BRAIN_PATH=..` (the parent of `learning-agent/`).

**Authority:** learning-agent is authoritative for the generation pipeline (transcript → cited HTML). jira-brain remains authoritative for ticket data (`raw/tickets/`), guides (`raw/guides/`), and curated wiki content. The CLAUDE.md anti-hallucination rules apply equally here — the verbatim-citation pattern in learning-agent's templates is the same shape as the guide-edit citation rule in jira-brain.

### `cleaned/` and `cleaned_private/`
Outputs from `scripts/clean_im_data.py` and PII auditing — both **gitignored**. They live on disk so the analyst can iterate, but they don't go to GitHub because the cleaned data still carries internal employee names (assignee/reporter/creator) and `cleaned_private/` carries district→label mappings.

```
cleaned/
├── tickets_clean.csv               # Cleaned ticket data
├── ticket_comments_long.csv        # Comments in long form
├── ticket_links_long.csv           # Inter-ticket links in long form
├── data_dictionary.md              # Per-field documentation of the cleaned schema
├── type_thresholds.json            # Linger thresholds by issue type (P75/P90/P95)
├── component_inventory.txt         # Distinct components observed
├── candidate_artifact_flags.csv    # Flags for cleanup-pipeline artifacts
├── cleaning_validation_report.md   # QA report on the cleaning pass
└── sample_narrative.md             # Narrative summary of a sample

cleaned_private/
├── district_map.json               # District code → district label
└── pii_audit_report.md             # PII audit findings
```

If you need to share aggregates derived from these, do it via a wiki page that redacts per CLAUDE.md's PII rules — never check `cleaned/` or `cleaned_private/` files in.

### `.claude/commands/`
Slash command prompts. Each `.md` file in this directory becomes an invokable `/command-name` in a Claude session. The filename (sans `.md`) is the command name; the file contents are the prompt body, with `$1`, `$2`, `$ARGUMENTS` substituted from invocation args.

```
.claude/commands/
└── apply-jira-to-guides.md   # /apply-jira-to-guides <csv-path> <module> [platform=SC]
```

`apply-jira-to-guides` runs a 4-pass workflow: (1) edit `.md` files with inline `<!-- Source: -->` citations, (2) strip those citations into a sidecar changelog at `raw/guides/ticket-updates/<DATE>-<module>.md` and regenerate the combined diff at `raw/guides/diffs/proposed/all-<module>-diffs.html`, (3) claim drift check (Pass 1 vs Pass 2 minus stripped comments), (4) voice & jargon spot-check. See CLAUDE.md → *Repeatable workflows* for the full spec.

Add new workflows by dropping a `.md` file here. The rest of `.claude/` (worktrees, scratch, caches) is gitignored.

### `output/`
Generated static site. Gitignored — regenerate from source any time with `python scripts/build_site.py`.

```
output/site/
├── index.html               # Rendered from wiki/index.md
├── concepts.html            # Auto-generated listing
├── workflows.html
├── entities.html
├── tickets.html             # Listing of all 8,849 tickets
├── wiki/                    # Mirrors wiki/ structure
└── raw/tickets/             # 8,849 rendered ticket pages
```

Open `output/site/index.html` in any browser. The header navigation works; broken wikilinks render in red strikethrough.

## Conventions

### Filenames
- Ticket files: `<KEY>.md` (e.g. `NXT-1234.md`)
- Concept files: `<Title-Case-Slug>.md` matching the component name with non-alphanumerics → `-`
- Workflow / entity files: `<lowercase-slug>.md`
- Training files: `<lowercase-slug>.html`

### Frontmatter
Every wiki page should have a YAML frontmatter block with at least `title` and `type`. Concept pages add `source_component` and `ticket_count`.

### PII
Customer PII (names, emails, phone numbers) may exist in `raw/` because the source tickets contain it. **Wiki pages must redact** — use role labels like `<District A>`. CLAUDE.md enforces this.

### Append-only log
`wiki/log.md` gets a new dated entry every time `compile_wiki.py` runs. Don't edit historical entries.

## Resumability contract

Every script must:
1. Read `.brain-state.json` first and resume from the last incomplete step
2. Write `.brain-state.json` atomically after every meaningful unit of work (every 100 tickets, every wiki page)
3. Treat file existence as a fallback truth — never overwrite an existing wiki page; never re-process an existing ticket

This contract is what lets the whole pipeline survive crashes, sleep cycles, and interrupted sessions.

## What's intentionally NOT in this repo

- **The original Jira CSV.** Customer data, gitignored.
- **Cleaned Jira data.** `cleaned/` and `cleaned_private/` are gitignored — they still carry employee names and district labels even after de-identification of customer PII.
- **Cybersoft guide PDFs.** `raw/guides/pdf/` is gitignored (42M+ of public PDFs) — the markdown extractions, manifest, snapshots, diffs, and ticket-update changelogs are committed instead.
- **Claude local scratch.** `.claude/tmp_*`, `.claude/worktrees/`, `.claude/__pycache__/`, `.claude/md_to_pdf.py`, and `scripts/__pycache__/` are gitignored.
- **Comments and attachments.** Reserved directories exist (`raw/comments/`, `raw/attachments/`); not yet ingested.
- **SME transcripts.** `raw/transcripts/` reserves the name; no transcripts exist yet, and nothing in the current pipeline depends on them. Resources today are grounded in `raw/tickets/`, `raw/guides/`, and `wiki/`.
- **A production resource-center UI.** The dashboard that reads `catalog/resources.json` exists as prototype HTML in `wiki/training/resource-center*.html`; a deployed version is a follow-up.
- **An auto-compiler for `resources/`.** Authoring is manual for the pilot module (Eligibility); a `compile_resources.py` may follow once the templates stabilize.
- **Onboarding pages.** `wiki/onboarding/` is empty by design — derived material; write only after concepts/workflows are stable and SME-reviewed.
