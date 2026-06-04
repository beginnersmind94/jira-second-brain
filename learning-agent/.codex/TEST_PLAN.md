# learning-agent - Codex Multi-Agent Test Plan

Run these four diagnostic agents before demos or after non-trivial changes to
`agent_sdk.py`, `evaluator_sdk.py`, `tools_sdk.py`, or `app.py`.

The custom agents live in `.codex/agents/*.toml` and follow the documented Codex
custom-agent schema: top-level `name`, `description`, `sandbox_mode`, and
`developer_instructions`.

## The Four Agents

| Agent | What it answers | Needs server? | Needs Jira creds? |
|---|---|---|---|
| `runtime-auditor` | Is the SDK wired correctly? Built-ins blocked? Evaluator separated? | No | No |
| `publish-gate-tester` | Does the verdict actually hard-gate publish? | Yes | No |
| `source-grounding-auditor` | Are the citations real? Does the quoted AC/RN appear in Jira verbatim? | No | Yes |
| `fresh-clone-runner` | Can someone else clone this and run it? | No | Optional |

## Invocation

From the `learning-agent/` directory:

```text
Static audit:
Ask Codex: "Spawn the runtime-auditor custom agent and report its verdict."

Fresh clone:
Ask Codex: "Spawn the fresh-clone-runner custom agent and report its verdict."

Live tests:
1. Start the server:
   python -m uvicorn app:app --host 127.0.0.1 --port 8000
2. Ask Codex: "Spawn publish-gate-tester against http://127.0.0.1:8000 and report its verdict."
3. Ask Codex: "Spawn source-grounding-auditor for resource_id=<some-rid-from-library> and report its verdict."
```

To fan all four out in parallel:

```text
Ask Codex: "Spawn runtime-auditor, publish-gate-tester,
source-grounding-auditor, and fresh-clone-runner in parallel. Wait for all four
and summarize each verdict."
```

If your local Codex CLI has a direct custom-agent runner, you can use it instead,
but verify the exact command first. The current official subagents documentation
describes custom agents as `.codex/agents/*.toml` files spawned by Codex, not as
a guaranteed `codex agent run ...` command surface.

## Expected Verdicts

| Agent | Pass line | Fail line |
|---|---|---|
| runtime-auditor | `ARCHITECTURE OK` | `ARCHITECTURE HAS GAPS` |
| publish-gate-tester | `GATE INTEGRITY OK` | `GATE INTEGRITY BROKEN` |
| source-grounding-auditor | `GROUNDING OK` | `GROUNDING DEGRADED` or `GROUNDING BROKEN` |
| fresh-clone-runner | `FRESH CLONE OK` | `FRESH CLONE BROKEN` |

A clean run shows four `OK` lines. Anything else is an investigation.

## Guardrails

- They never modify `learning-agent/` application files.
- `fresh-clone-runner` may write only under `.codex/tmp/` and must clean up.
- They never touch `published/` artifacts intentionally.
- They never commit, push, or branch.
- They never run more than four in parallel (`[agents].max_threads = 4`).
- Only `fresh-clone-runner` may invoke the smoke test, and only when credentials
  are available; expect model/API cost when that optional step runs.

These agents catch structural failures. They do not replace human review of
generated drafts. The Evaluator grades quality per run; these agents grade
whether the architecture and gates are being honored.

## Adding A New Test Agent

Drop a new `.toml` in `agents/` following the same pattern:

- top-level `name`, `description`, and `developer_instructions`
- `sandbox_mode = "read-only"` unless it truly needs scratch writes
- numbered checks and a one-line verdict format
- no registration needed; Codex auto-discovers `.codex/agents/*.toml`

Keep the agent count under six total. Fewer narrow agents applied consistently
beats more agents applied haphazardly.

## Known Limitations

1. **Codex command-surface drift.** The agent files follow the documented
   custom-agent schema. The exact CLI command for spawning a named custom agent
   may vary by Codex release; when in doubt, use a natural-language Codex prompt
   and inspect active agents with `/agent`.

2. **No `template-compliance-tester` yet.** The Evaluator already checks template
   fit per run; a separate agent would be redundant unless the Evaluator itself
   becomes suspect.

3. **Source-grounding sample size is 5.** Statistical confidence is weak. For a
   high-stakes demo, raise it to 10 or 15 in
   `agents/source-grounding-auditor.toml`.
