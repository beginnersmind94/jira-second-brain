# Jira Second-Brain

A Karpathy-style LLM wiki built from a Jira ticket export. Every claim links back to a source ticket; the wiki is the deliverable, the tickets are the raw material.

Built end-to-end inside Claude Code from one CSV export.

## What's in here

```
jira-brain/
├── CLAUDE.md                # Operating rules + anti-hallucination guardrails
├── .brain-state.json        # Resumable pipeline state
├── raw/
│   ├── tickets/             # 8,847 individual ticket markdown files
│   ├── _imports/            # Drop zone for new Jira exports
│   └── _imports/processed/  # Imported exports (CSVs gitignored)
├── wiki/
│   ├── concepts/            # 22 module pages (Accountability, Inventory, etc.)
│   ├── workflows/           # 8 cross-module workflows
│   ├── entities/            # 5 team / module-group pages
│   ├── training/            # Interactive HTML training + customer onboarding
│   ├── index.md             # Navigable top-level map
│   └── log.md               # Compilation history
├── scripts/
│   ├── ingest.py            # CSV → per-ticket markdown (resumable)
│   ├── analyze.py           # Frequency-mine the corpus
│   ├── compile_wiki.py      # Auto-generate concept/workflow/entity pages
│   └── build_site.py        # Render the whole vault as static HTML
└── output/                  # Generated static site (gitignored)
```

## Pipeline

1. **Ingest** — drop a Jira CSV in `raw/_imports/`, run `python scripts/ingest.py`. Writes one markdown file per ticket with frontmatter (key, summary, status, components, sprints, low-signal flag) and a body for description + acceptance criteria. Resumable on crash.
2. **Analyze** — `python scripts/analyze.py` counts components, sprints, and n-gram phrases; writes JSON summaries to `scripts/`.
3. **Compile** — `python scripts/compile_wiki.py` builds concept pages (one per major component), workflow pages (recurring patterns from phrase analysis), entity pages (team/module groupings), `index.md`, and an entry in `log.md`. Resumable.
4. **Render** — `python scripts/build_site.py` renders the whole vault (wiki + raw tickets) as a browsable static HTML site in `output/site/`. Wikilinks resolve correctly across folders; broken links are styled red.

## What the wiki captures (current state)

- **22 concept pages** — one per product module with ≥25 tickets (Accountability, Inventory, Item Management, Menu Planning, etc.)
- **8 workflow pages** — Physical Inventory, Orders, Menu Cycle, Student Import, Direct Certification, Post-Production Analysis, Data Exchange, Item Onboarding
- **5 entity pages** — Platform Team, Nutrition Operations, Meal Service & Accountability, Reporting & Insights, Emerging Surfaces
- **3 training/onboarding artifacts** — see below

## Training & onboarding mockups

Three self-contained HTML files in `wiki/training/`, each demonstrating a different audience pattern:

| File | Audience | What it does |
|---|---|---|
| `accountability-expert.html` | New PMs | 10-chapter interactive guide on the Accountability module — POS simulator, claims calculator, drag-and-drop triage exercise, spaced-repetition flashcards. Cites real USDA NSLP figures from EIB-279. |
| `forms-onboarding.html` | Internal / leadership | Forms workstream summary with sprint timeline and shipped-scope metrics. |
| `forms-customer-onboarding.html` | Customers | Polished onboarding one-pager for the Forms feature — interactive go-live checklist, ownership-tagged setup steps, FAQ, full-width responsive layout, printable. |

## CLAUDE.md — anti-hallucination guardrails

After a real session-level failure (a customer-facing draft overstated district agency on a feature owned by Implementation), `CLAUDE.md` was extended with five rules:

1. **Persona-first, always** — grep `^As a` from source tickets before drafting; the actor in your sentence must match a ticket persona
2. **Cite or cut** — no claim without a named source (ticket, article, paper)
3. **No cross-feature pattern matching** — capabilities don't transfer between features without per-instance evidence
4. **Tag ownership on every action** — `Cybersoft` / `Your team` / `Cybersoft + your input` / `Parent`
5. **Verify before ready** — claim-to-source trace, direct read of every cited URL, "matches what it cites" beats "reads well"

Each rule names a specific failure mode it guards against. Rule list is intentionally small; new failures get checked against existing rules before adding a sixth.

## Privacy

- `raw/_imports/*.csv` and `raw/_imports/processed/*.csv` are **gitignored** — the original Jira export contains customer-facing language, persona names, and product details, and never goes to GitHub.
- The 8,847 ticket markdown files in `raw/tickets/` are committed because they're the source of truth for every wiki claim.

## Resumability

Every step writes `.brain-state.json` after each unit of work (every 100 tickets ingested, every wiki page written). Re-running any script picks up exactly where it left off. The state file is the source of truth; file existence is a fallback.
