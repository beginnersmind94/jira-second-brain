# Repo Structure

A reference for what lives where, why it lives there, and how the pieces talk to each other. The README is the pitch; this is the map.

## Top-level layout

```
jira-brain/
├── README.md                # Elevator pitch + quick start
├── REPO_STRUCTURE.md        # You are here
├── CLAUDE.md                # Operating rules for Claude inside this repo
├── .brain-state.json        # Pipeline state (resumable checkpoints)
├── .gitignore               # Excludes raw CSVs, output/, OS noise
├── raw/                     # Source-of-truth ticket data
├── wiki/                    # Compiled, human-curated knowledge
├── scripts/                 # Pipeline (ingest → analyze → compile → render)
└── output/                  # Generated static site (gitignored)
```

Three load-bearing principles:

1. **`raw/` is append-only and ground-truth.** Wiki pages cite raw tickets, never the other way around.
2. **`wiki/` is the deliverable.** Concepts, workflows, entities, training, and onboarding pages live here.
3. **`output/` is disposable.** Anything in it can be regenerated from `raw/` + `wiki/`.

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
Source data. **Never write here by hand** unless you're correcting a ticket export error.

```
raw/
├── tickets/         # 8,847 markdown files, one per Jira issue
│   ├── NXT-100.md
│   ├── NXT-101.md
│   └── ...
├── comments/        # (reserved — empty for now)
├── attachments/     # (reserved — empty for now)
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

### `wiki/`
Compiled knowledge. **You own this.** Hand-edit freely; the auto-compiler only writes pages that don't already exist (write-if-absent).

```
wiki/
├── index.md                 # Top-level navigable map
├── log.md                   # Append-only compilation history
├── concepts/                # 22 pages — one per product module
├── workflows/               # 8 pages — recurring cross-module patterns
├── entities/                # 5 pages — team / module groupings
├── decisions/               # (empty — for explicit architecture/product decisions)
├── onboarding/              # (empty — derived role-specific guides)
└── training/                # 3 HTML files — interactive learning + customer onboarding
```

Page-type rules:

- **`concepts/<Slug>.md`** — one product concept (typically a Jira component). Each page must cite ≥3 source tickets via wikilinks. Filename slug is dash-separated (`Item-Management.md`, not `ItemManagement.md`).
- **`workflows/<slug>.md`** — how-we-do-things. Each cites 3-8 example tickets that shaped the flow.
- **`entities/<slug>.md`** — people, teams, modules, customer types. Cross-linked from anywhere they're mentioned.
- **`decisions/<slug>.md`** — architecture/product decisions. Format: Context → Options → Decision → Consequences → Source tickets.
- **`onboarding/<slug>.md`** — role-specific starter guides, derived from concepts + workflows + decisions. Don't write these until the underlying material is solid.
- **`training/<slug>.html`** — standalone interactive learning artifacts. Each is a single self-contained HTML file (no external CSS/JS) so it can be emailed or shared without dependencies.

#### Training/onboarding files (current)

| File | Audience | Type |
|---|---|---|
| `training/accountability-expert.html` | New PMs | 10-chapter interactive guide |
| `training/forms-onboarding.html` | Internal / leadership | Forms workstream summary |
| `training/forms-customer-onboarding.html` | Customers | Customer-shareable one-pager |

#### Wikilink convention

Wikilinks use `[[path|label]]` syntax:

- From `wiki/concepts/Inventory.md` → ticket: `[[raw/tickets/NXT-1234|NXT-1234 — short summary]]`
- From `wiki/index.md` → concept: `[[concepts/Inventory|Inventory]]`
- From `wiki/entities/platform-team.md` → concept: `[[concepts/Platform-System|Platform - System]]`

The static-site builder (`scripts/build_site.py`) resolves these against multiple base paths so both vault-root-relative and section-relative links work.

### `scripts/`
The pipeline. All resumable, all idempotent.

```
scripts/
├── ingest.py            # Step 4: CSV → raw/tickets/*.md
├── analyze.py           # Step 5a: corpus frequency analysis
├── compile_wiki.py      # Step 5b: generate concept/workflow/entity pages
├── build_site.py        # Render wiki + raw as static HTML in output/site/
├── analysis_summary.json    # Frequency counts (written by analyze.py)
├── component_tickets.json   # Tickets grouped by component
├── phrase_tickets.json      # Tickets grouped by recurring phrase
└── sprint_tickets.json      # Tickets grouped by sprint
```

#### Data flow

```
  Jira CSV
     │
     ▼
  raw/_imports/*.csv   ──ingest.py──▶   raw/tickets/*.md   +   .brain-state.json
                                              │
                                              ▼
                                        analyze.py        ──▶   scripts/*.json
                                              │
                                              ▼
                                        compile_wiki.py   ──▶   wiki/concepts/, workflows/, entities/, index.md
                                              │
                                              ▼
                                        build_site.py     ──▶   output/site/**/*.html
```

Each script writes `.brain-state.json` after meaningful units of work. None of them require the others to have just run — they read from the filesystem and pick up wherever the previous step finished.

#### What each script reads/writes

| Script | Reads | Writes |
|---|---|---|
| `ingest.py` | `raw/_imports/*.csv` | `raw/tickets/*.md`, moves CSV to `processed/`, updates `.brain-state.json` |
| `analyze.py` | `raw/tickets/*.md` (frontmatter only) | `scripts/analysis_summary.json`, `scripts/component_tickets.json`, `scripts/phrase_tickets.json`, `scripts/sprint_tickets.json` |
| `compile_wiki.py` | `raw/tickets/*.md`, `scripts/*.json` | `wiki/concepts/*.md`, `wiki/workflows/*.md`, `wiki/entities/*.md`, `wiki/index.md`, appends to `wiki/log.md`, updates `.brain-state.json` |
| `build_site.py` | All `*.md` in `wiki/` and `raw/` | `output/site/**/*.html` |

### `output/`
Generated static site. Gitignored — regenerate from source any time with `python scripts/build_site.py`.

```
output/site/
├── index.html               # Rendered from wiki/index.md
├── concepts.html            # Auto-generated listing
├── workflows.html
├── entities.html
├── tickets.html             # Listing of all 8,847 tickets
├── wiki/                    # Mirrors wiki/ structure
└── raw/tickets/             # 8,847 rendered ticket pages
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
- **Comments and attachments.** Reserved directories exist; not yet ingested.
- **Onboarding pages.** Empty by design — derived material; write only after concepts/workflows are stable and SME-reviewed.
- **Decision pages.** Empty — to be written from explicit architecture/product tickets when identified.
