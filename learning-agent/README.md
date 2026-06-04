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
       drafts/<id>.eval.json   (verdict: pass / warn / fail)
               │
               ▼
       [human reviews + clicks Publish]
               │
               ▼
       published/<id>.html  (source comments stripped)
       + published/metadata/<id>.json  (catalog entry)
```

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

# 7. Open http://127.0.0.1:8000/ in Chrome
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
- Rich text editor for draft edits (textarea for V1)
- Quizzes & flashcards from published content
- Template-prompt editor + regeneration of dependent resources
- SSO / role-based access
