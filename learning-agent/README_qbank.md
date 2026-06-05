# Question-bank curation agent — the gate

Generates candidate questions, **auto-approves the safe ones**, routes the risky/low-confidence
ones to a **human**, and lets **nothing** reach the bank without passing the gate.

## State machine

```
                       ┌── triage clean ──────────────▶ auto_approved ──┐
 pending_review ───────┤                                                 ├── commit_to_bank ──▶ committed ✦
                       └── triage flags ─▶ needs_human ─┬─ human approve ─▶ human_approved ──┘
                                                        └─ human deny ───▶ rejected ✦
✦ = terminal
```

- **pending_review** — generation deposited a candidate. Never touches the bank.
- **auto_approved** — passed triage cleanly (system transition).
- **needs_human** — triage flagged it; carries the reason(s). *Only* a human can move it forward.
- **human_approved / rejected** — set exclusively by the human callback.
- **committed** — written to the append-only bank by `commit_to_bank`.

## Three stages

1. **Generate** → candidates land as `pending_review`. Generation alone never writes to the bank.
2. **Triage** → `score_candidate()` (pure, unit-tested) routes to `auto_approved` or `needs_human`. A
   candidate is flagged if **any** hold: confidence < threshold, sensitive topic, weak source-support
   (cited quote doesn't support stem+answer), or statistical outlier vs. the batch. Reasons are attached.
3. **Commit** → `commit_to_bank` is the **only** writer, and it refuses any status that isn't
   `auto_approved`/`human_approved`.

## Enforcement (SDK, not prompt text)

- `commit_to_bank` is a custom MCP tool; the **PreToolUse hook** (`commit_gate_hook`) **denies** the call
  unless status is committable — the hard layer, fires even if the model calls the tool directly, in any
  permission mode.
- `permission_mode="dontAsk"` + a tight `allowed_tools` → anything unexpected is denied, not run.
- The **`canUseTool`** callback surfaces `needs_human` items to a human approver at runtime
  (approve → `human_approved`, deny → `rejected`).
- The bank guard inside `commit_to_bank()` is a second, deterministic check (defense in depth).

> `commit_to_bank` *is* in `allowed_tools` so the agent can call it for already-approved items, but the
> allowlist is **not** the security boundary — the hook is. Status decides whether a write happens.

## Hard rules

- Append-only bank; only `commit_to_bank` writes to it.
- `needs_human` → `human_approved` only via the human callback; never auto-promoted by the model.
- Every decision (auto-approved, sent-to-human, human-approved, rejected, committed, hook-denied) is in
  an append-only audit log with timestamp + reason + triggering rule.
- Model output is untrusted: generated text can never flip a status or trigger a commit.

## Files

| File | What |
|---|---|
| `qbank_curation.py` | state machine, stores (pending/bank/audit), `score_candidate`, `commit_to_bank` guard |
| `qbank_gate_hooks.py` | `commit_to_bank` tool, PreToolUse hook, `canUseTool` callback, options builder |
| `test_qbank_gate_enforcement.py` | proves a `needs_human` item can't reach the bank (run this first) |

## Run

```bash
python test_qbank_gate_enforcement.py     # gate proof — should print "All gate checks passed"
```

## Status

Gate + triage + human callback: **built and proven**. Generation: **not yet built** (deliberately —
the gate ships and is verified first).
