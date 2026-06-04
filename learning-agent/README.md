# Learning Content Producer

Internal POC. Upload an SME training transcript, get back a structured HTML
learning resource with verbatim citations to live Cybersoft Jira (project NXT).

The architecture is in [CLAUDE.md](CLAUDE.md). This README is the runbook.

## What it does

```
.md transcript
      │
      ▼
┌─────────────────────────────┐
│ Generator agent             │   Tasks 1→4 in one Claude Agent SDK
│   1. Map (parse + Jira)     │   query(). Pulls live NXT tickets,
│   2. Plan                   │   walks parent epics for full context.
│   3. Verify (AC + KB)       │
│   4. Generate HTML          │
└──────────────┬──────────────┘
               │
               ▼
       drafts/<id>.html  (with inline <!-- Source: --> comments)
               │
               ▼
┌─────────────────────────────┐
│ Evaluator                   │   Separate query() call. Grades
│   • template fit            │   template, length, citations.
│   • length budget           │   Spot-checks 2-3 ticket quotes
│   • source grounding        │   by calling read_ticket. Does NOT
│   • citation spot-check     │   rewrite.
│   • discrepancy handling    │
│   • unsourced specifics     │
└──────────────┬──────────────┘
               │
               ▼
       drafts/<id>.eval.json   (deterministic grounding gate: pass / fail)
               │
               ▼
┌─────────────────────────────────────────────┐
│ Human review  (the gate INTO the Library)    │
│   • read the grounded draft                   │
│   • Request edits (AI-assisted) ──┐           │
│       edit agent → find/replace ops           │   loops back
│       (NEVER touches <!-- Source -->)         │   until approved
│       → grounding gate re-runs (free)         │
│       → triage router: stylistic | substantive│  (advisory only)
│   • Approve  ─────────────────────┘           │
└──────────────┬──────────────────────────────┘
               │ approve  (grounding must be clean)
               ▼
       Library — approved only   (source comments stripped on download/PDF)
       + metadata { status: approved, approved_at }
```

Two floors, in order: the **deterministic grounding gate** is the machine floor (a
draft can't be reviewed until every citation is verbatim and correctly-tiered); a
**human approval** is the floor INTO the Library. Unapproved drafts never appear in
the Library — they live in its "Awaiting review" queue. See "Review & approve" below.

## Review & approve (human-in-the-loop)

After a draft passes the grounding gate, a human reviews it and either approves it
into the Library or requests changes. This is implemented in the demo server
(`demo_app.py`); the production port is specced in `docs/ADR-001`.

- **Approve is the only gate into the Library.** `POST /resources/{id}/approve`
  re-validates grounding **live** against the module fixture, then marks the
  resource `approved` / `available`. Only approved resources show in the Library;
  approved downloads/PDFs drop the "pending review" banner.
- **Request edits is AI-assisted, not a raw editor.** `POST /resources/{id}/revise`
  takes a plain-English instruction. An **edit agent** (`revise.py`) emits targeted
  find/replace ops — it is structurally barred from touching `<!-- Source: ... -->`
  citation comments or inventing uncited facts (it refuses, or inserts a
  `[TO VERIFY]` marker). The deterministic grounding gate **re-runs after every
  edit** (free), so a bad edit that breaks a citation is caught and blocks approval.
- **The triage router is advisory, never a gate.** A lightweight classifier tags
  each edit `stylistic` (wording/format — fast-path to approve) or `substantive`
  (a claim/number/label/step may have changed — read it closely), defaulting to
  `substantive` when unsure. It can only *route to an extra check*; it can never
  skip the grounding gate. (Pattern: Anthropic's "routing" workflow + a "validating"
  approval gate — keep it a classifier, not another agent.)
- An edit re-opens review: an approved guide drops back to draft until re-approved.
  Pre-edit versions are kept under `drafts/_pre_edit/` as an audit trail.
- **Every decision is logged** to `logs/review-decisions.jsonl` — edit applied,
  refused (with `refusal_kind`), no-change, approved, approve-blocked — with the
  instruction, the ops, the triage verdict, and the grounding result. Read it via
  `GET /review-log` (filter `?rid=`). This is how you audit whether a refusal was
  appropriate or the editor over-reached, and it's the real-traffic corpus for the
  triage/scope evals.

## Prerequisites

- **Python 3.11+** on Windows / macOS / Linux
- **Claude Code** installed and logged in (provides OAuth auth — see Auth below)
- **A Jira API token** for the Cybersoft Atlassian Cloud (https://id.atlassian.com/manage-profile/security/api-tokens)
- **The sibling `jira-brain/` repo** cloned next to `learning-agent/` (the `search_kb` tool reads its curated guides + wiki)

Layout expected:
```
<parent>/
├── jira-brain/         ← knowledge base (curated guides, wiki, raw tickets)
└── learning-agent/     ← this app
```

## First-run setup

```powershell
# 1. From <parent>/learning-agent/
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # Windows
# source .venv/bin/activate          # macOS / Linux

# 2. Install deps
pip install -r requirements.txt

# 3. Create .env from the template
copy .env.example .env               # Windows
# cp .env.example .env                # macOS / Linux

# 4. Fill in .env (see below)

# 5. Smoke test (~4 minutes, runs the full pipeline against the sample transcript)
python smoke_test.py

# 6. Start the server
python -m uvicorn app:app --host 127.0.0.1 --port 8000

# 6b. For the offline demo WITH the review/approve + AI-edit UI, run the demo
#     server instead (pre-cached Jira fixtures, no network, port 8001):
#         python -m uvicorn demo_app:app --host 127.0.0.1 --port 8001

# 7. Open http://127.0.0.1:8000/ (or :8001 for the demo) in Chrome
```

## .env configuration

```dotenv
# Anthropic auth is handled by Claude Code subscription OAuth.
# For local use, run Claude Code interactively and use /login.
# For scripts/CI, set CLAUDE_CODE_OAUTH_TOKEN from `claude setup-token`.
# Leave ANTHROPIC_API_KEY unset unless you want direct Anthropic API billing.

# Live Jira (REST) — required for match_tickets / read_ticket / read_epic
JIRA_BASE_URL=https://primeroedgenext.atlassian.net
JIRA_EMAIL=your-cybersoft-email@cybersoft.net
JIRA_API_TOKEN=ATATT...                     # from id.atlassian.com

# Path to the sibling jira-brain repo (for search_kb)
# Defaults to ../jira-brain relative to this folder
JIRA_BRAIN_PATH=C:\Users\<you>\<...>\Financials-Documentation-KT\jira-brain
```

## Auth — using your Claude Code subscription instead of an API key

The Claude Agent SDK runs through Claude Code authentication. You don't need an
`ANTHROPIC_API_KEY` for subscription auth.

For normal local use, start Claude Code and run `/login` if you are not already
signed in. Claude Code manages `.credentials.json` under your user profile.

For non-interactive scripts or CI where browser login is unavailable, generate a
long-lived token:

```powershell
& "$env:APPDATA\Claude\claude-code\<version>\claude.exe" setup-token
```

That prints an OAuth token; it does not save it for you. Copy it into the
environment as `CLAUDE_CODE_OAUTH_TOKEN`. This token is tied to your Claude
subscription. Leave `ANTHROPIC_API_KEY` unset unless you intentionally want to
bill against a direct Anthropic API key.

## Directory layout

```
learning-agent/
├── app.py                       # FastAPI server (upload, generate, library, publish, evaluate)
├── agent_sdk.py                 # Generator — Tasks 1-4 in one query()
├── evaluator_sdk.py             # Evaluator — Task 5, separate query() call
├── tools_sdk.py                 # MCP tools: parse_transcript, match_tickets,
│                                # search_kb, read_ticket, read_epic, read_pdf
├── smoke_test.py                # End-to-end CLI test (uses sample transcript)
├── templates/                   # Three generator system-prompt templates
│   ├── long-form.md             #   20-page comprehensive reference
│   ├── micro-guide.md           #   3-page task-success guide
│   └── tldr.md                  #   1-page at-a-glance summary
├── static/index.html            # Single-page UI (Author + Library modes)
├── raw/transcripts/             # Uploaded transcripts (immutable once saved)
│   └── metadata/                # JSON: {filename, module, uploaded_at}
├── drafts/                      # Generated HTML drafts + .eval.json verdicts
├── published/                   # Final HTML (after human Publish)
│   └── metadata/                # Catalog entries (status: published)
├── logs/                        # Per-job JSONL traces
├── data/                        # Sample data
│   └── sample-eligibility-income-survey-training.md
├── CLAUDE.md                    # Operating instructions (the spec)
└── README.md                    # You are here
```

## Smoke test

`smoke_test.py` runs the full Generator pipeline against
`data/sample-eligibility-income-survey-training.md` with module=Eligibility,
template=micro-guide. Outputs to `smoke_test_output.html` and prints timing,
tool-call counts, and cost.

Expected result on a clean run: ~4 minutes, ~$0.30 cost, 14-18 tool calls,
~17 KB HTML draft with verbatim NXT ticket citations.

If it fails, check:
1. Is `.env` filled in?
2. Is Claude Code logged in? Start Claude Code and check `/status` or run
   `/login` interactively.
3. Is `JIRA_BRAIN_PATH` pointing to a real directory?

## Architecture notes

- **Generator and Evaluator are SEPARATE `query()` calls.** The Generator
  decides HOW to produce the content. The Evaluator decides IF it's good
  enough. This is structural separation, not just prompt convention.
- **Built-in Claude Code tools (Read, Glob, Bash, etc.) are explicitly
  disabled** via `disallowed_tools`. The agent has access ONLY to the six
  MCP tools registered in `tools_sdk.py`.
- **Source citations are inline HTML comments** preserved in `drafts/` and
  stripped on publish. They're the audit trail for verbatim AC quotes.
- **JQL `text ~` is phrase-literal** — `match_tickets` queries should be
  2-4 words. The system prompt warns the agent; the tool docstring repeats it.
- **Epic context comes from `read_epic`** — one call returns the epic +
  every sibling child story. Cheaper than fanning out many `match_tickets`
  searches when you have a known feature theme.

## Identifier handling at ingestion

Rules for handling Jira identifiers when importing tickets into a fixture. These are
**directive** — follow them; the hard guarantees are enforced in code (see *Enforcement*
below), and this section documents that enforcement.

- **Resolve at the boundary.** Resolve every Jira parent reference to a real issue key
  (e.g. `NXT-64788`) at ingestion, *before persisting*. Never store a bare internal
  numeric id (e.g. `105530`) as `epic_key`. Bind to the key the live API returns; treat
  CSV / non-API imports as untrusted and normalize at the door.
  *(Principle: "Writing effective tools for AI agents" — resolve identifiers to a
  canonical form inside the tool, not in the agent.)*
- **Fail loud, don't mask.** If a parent reference does not resolve to an existing epic,
  drop the reference (`epic_key = "-"`) — or fail the import under `--strict` — with a
  clear message. **Never mint a stub epic and never persist a bare id.** A `read_epic`
  bare-number normalize-and-retry is a temporary noise-killer, never the fix.
  *(Principle: "How we built our multi-agent research system" — errors compound; pair
  adaptable agents with deterministic safeguards.)*
- **Actionable errors.** A tool advertises a parent lookup only when the parent resolves
  to a real key; on a miss it returns a clear, actionable, non-blocking message — not a
  silent dead end. *(Principle: "Writing effective tools for AI agents".)*
- **Grounding stays deterministic and code-owned.** Identifier resolution and the
  grounding gate live in code, not in prose. Agent judgment is reserved for the
  open-ended parts (intent, search, what-to-build) — never for resolving references or
  grounding. *(Principle: "How we built our multi-agent research system" — a dedicated,
  deterministic attribution/citation step.)*

**Enforcement (in code — this README documents these, it does not replace them):**
- `build_fixtures_from_csv.py` — resolves `Parent` (internal id) → real key via an
  `Issue id` join, then a unique-epic-`summary` fallback; otherwise drops to `"-"`. Never
  mints a stub. Post-build it asserts no bare parent key survives, flags duplicate-summary
  epics (the duplicate-identity fingerprint), and fails the build under `--strict`.
- `demo.py` — `read_epic` canonicalizes `NXT-<n>` ⇄ `<n>` and returns an actionable note
  on a true miss; `read_ticket` advertises `read_epic` only when the parent resolves.
- `eval/regression.py` **REG-16** — every ticket's parent reference resolves (no
  `read_epic` dead-end), gated in the suite.
- `test_ingestion.py` — feeds a ticket whose parent is a bare internal number and asserts
  the pipeline resolves it to a real key or drops it, and never mints a phantom; also
  covers `--strict` and the duplicate-summary check.

> These guarantees are enforced in the pipeline and tests above. This README only
> *documents* them — **editing this README cannot weaken or disable them.** If you change
> a rule here, change the enforcing code and its test in the same commit, or the doc is lying.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `UnicodeEncodeError: 'charmap' codec can't encode` | Windows PowerShell default cp1252 | `$env:PYTHONIOENCODING = 'utf-8'` before running, or rely on the `sys.stdout.reconfigure()` at the top of each script |
| `401 Invalid authentication credentials` | Claude Code is not logged in, or a stale API key/token is taking precedence | Run `/login` in Claude Code for local use, or set a fresh `CLAUDE_CODE_OAUTH_TOKEN` from `claude setup-token` for scripts/CI |
| `match_tickets` returns "No tickets matched" for everything | Phrase is too specific | Use 2-4 word queries: "Income Survey wizard", not "Income Survey wizard with 7 steps" |
| Agent uses `Read` / `Glob` / `Bash` mid-run | `disallowed_tools` regression | Verify `agent_sdk.py:build_options()` still passes `tools=[]` + `disallowed_tools=[...]` |
| Server fails to bind on port 8000 | Orphan uvicorn from previous run | `netstat -ano \| findstr :8000`, then `Stop-Process -Id <pid> -Force` |
| Draft HTML starts with planning preamble instead of `<h1>` | Server-side strip in `app.py:_stream_generation` not running | Confirm the `re.search(r"<h[1-2]\b", ...)` block is in `app.py` |
| Evaluator says "Could not parse evaluator output as JSON" | Model emitted prose around the JSON | Re-run; if recurring, tighten `evaluator_sdk.py:EVALUATOR_PROMPT` |

## What's NOT in V1 (deferred to V1.5)

Documented in `CLAUDE.md`. Short version:
- Evaluator retry routing (current Evaluator runs once, no retry)
- Vector similarity for `match_tickets` (current is JQL `text ~`)
- PDF / Word transcript upload (text-only for V1)
- Draft edits are **AI-assisted** (describe the change → edit agent revises). A raw
  rich-text/markdown editor is deferred — the AI-edit path keeps citations safe by
  construction, which a free-form editor would not.
- The **edit-triage classifier eval** exists (`python -m eval.triage_eval` — 24
  balanced cases + a deterministic FPR/FNR scorer; offline mode needs no auth).
  Still pending: a `--live` calibration run, **real** (non-synthetic) reviewer-edit
  cases, and the two-stage fast-filter optimization.
- **Translate mode (multilingual output, deferred).** The editor declines whole-doc
  translation by design. When built, a translation is a *rendering layer* over the one
  canonical English guide — citation comments stay verbatim English (so the grounding
  gate still audits them) — **not** a separate, drift-prone artifact. See `docs/ADR-001`.
- **TODO (bridge with an expiry date):** the current on-disk fixtures predate the
  builder's ID→key resolution and lean on `read_epic`'s runtime normalization (covered by
  `eval/regression.py` REG-16). That's a temporary masking layer. When a Jira CSV with an
  `Issue id` column is available, **rebuild fixtures with `--strict`** to get canonical
  parents at ingestion, and stop relying on runtime normalization as the permanent fix.
- Quizzes & flashcards from published content
- Template-prompt editor + regeneration of dependent resources
- SSO / role-based access
