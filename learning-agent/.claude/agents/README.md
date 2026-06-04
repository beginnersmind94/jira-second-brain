# Learning Library Producer — Agent Team

A lean team of Claude Code subagents that runs the content production pipeline from transcript to published guide.

## The team

```
  🩷 Mapper       →   🩵 PM          →   💚 SME         →   💙 Writer      →   🧡 Reviewer
  Parse transcript    Plan content       Fact-check          Generate HTML      Evaluate draft
  Match to Jira       Pick template      Verify claims       Follow template    Pass or route failure
  (Task 1)            (Task 2)           (Task 3)            (Task 4)           (Task 5)
                                                                                    │
                                                                          ┌─────────┴─────────┐
                                                                         PASS              FAIL
                                                                          │            Route to origin
                                                                      published/        (max 3 retries)
```

**💜 Designer** works in parallel on the learning library UI (directory + producer surfaces).

**❤️ Eval** runs automated evaluations against any pipeline output. See `../eval-framework.md`.

## Data source: live Jira via Atlassian MCP (no CSV)

These agents read **live Jira** (project **NXT**) through the account-level Atlassian MCP connector — never a CSV or local mirror. The agent frontmatter no longer pins a `tools:` allowlist; the Jira-touching agents inherit MCP from the session (read-only agents use `disallowedTools: Write, Edit` to stay read-only while keeping MCP). If you ever see an agent reach for `data/*.csv`, the frontmatter regressed.

**Prerequisite:** the session must have the Atlassian MCP connector available (it's account-level — confirm with `/mcp` or by checking that Jira tools are listed). Without it, the Jira-touching agents have no data source and the pipeline cannot ground content.

## Quick start

The seven `.md` agent files are already in this directory. They auto-load when Claude Code starts in `learning-agent/`. Edits to these files take effect only on a fresh session. Just:

1. **Restart Claude Code** (close + reopen, OR start a new session in `learning-agent/`).
2. Run `/agents` — you should see all seven in the Library tab.
3. Run `/mcp` — confirm the Atlassian connector is connected.
4. Use the one-shot pipeline prompt below.

## How to run the pipeline

### One-shot (Claude coordinates all 5 agents)

```
Run the full producer pipeline on
raw/transcripts/20260529-070600-item-management-2026-05-28-item-management-create-items-training.md
as a long-form guide for Item Management. Use the mapper, pm, sme, writer, and reviewer
agents in sequence, pulling tickets from live Jira (project NXT) via the Atlassian MCP.
Then repeat for micro-guide and tldr.
```

All three template types in one go — long-form, micro-guide, tldr — against the same
Item Management transcript. Each Jira citation must come from live Jira via `getJiraIssue`,
labeled with the correct field tier (`AC:` only for Acceptance Criteria text).

### Per-stage invocation

```
Use the mapper agent to parse
raw/transcripts/20260529-070600-item-management-2026-05-28-item-management-create-items-training.md
and match features to live Jira tickets (project NXT) in the Item Management module
```

Then `pm`, then `sme`, then `writer`, then `reviewer`.

### UI work (parallel)

```
Use the designer agent to add a verdict badge column to the Library card view
```

### Eval runs

```
Use the eval agent to grade this writer output against the citation_coverage grader
```

## Why this is faster than the FastAPI Generator + Evaluator

The original `agent_sdk.py` + `evaluator_sdk.py` approach packed Tasks 1-4 into one big `query()`. That call has to do everything sequentially in a single agent's context — read the transcript, search Jira, plan, verify, write. Hard to parallelize, harder to interrupt.

Subagents are isolated `query()` calls per task. Claude Code can spawn them in parallel where the pipeline allows, and each one starts with a clean focused context. The whole point: smaller jobs, less per-turn reasoning, better parallelism.

## What's on the filesystem when this runs

- Transcripts: `raw/transcripts/`
- Drafts: `drafts/<DATE>-<module>-<template>-draft.html`
- Published: `published/`
- Per-job logs: `logs/`
- Pipeline state (PM-tracked): `logs/pipeline-status.md`

The existing FastAPI UI (`app.py` at port 8000) reads from the same filesystem. So drafts produced by these subagents show up in the Library tab automatically.

## Key rules (from CLAUDE.md)

- **Generator ≠ Evaluator.** Writer and Reviewer are intentionally separate agents.
- **Cite or cut.** Every factual claim needs a named source. No source = delete the claim.
- **Transcript is voice, Jira is truth.** When they conflict, flag the discrepancy.
- **Max 3 retries.** After 3 evaluation failures, exit with the best draft + unresolved issues log.
- **Status gating.** Content starts as `draft`, moves to `review`, then `published`. No agent auto-publishes.

## Agent memory

All agents use `memory: project` scope. Memory files accumulate at `.claude/agent-memory/<agent-name>/MEMORY.md` and can be checked into version control so the team shares institutional knowledge.
