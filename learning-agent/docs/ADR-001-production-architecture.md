# ADR-001: Production architecture for the Learning Content Producer

**Status:** Proposed
**Date:** 2026-06-01
**Deciders:** PM, Eng lead, Thursday-review owner
**Constraint:** Working, credible prod story by **Thursday** (3 days). Full load/scale hardening is a fast-follow, not a Thursday item.

## Context

The product turns a training-session transcript into a Jira-grounded learning guide (user picks long-form / micro-guide / tldr), shown in a browser Library with a publish gate. The differentiator is **provable grounding**: every claim traces to the exact Jira source field with the correct trust tier (Acceptance Criteria vs. Description), machine-verified — not "the AI tried."

Five measured iterations led here:

| iteration | total time | provenance mistakes | complete? | lesson |
|---|---|---|---|---|
| baseline | 829s | systematic Description-as-AC | no (20K-word bloat) | "comprehensive" was a bug |
| bound output | 725s | systematic | truncated | decode-bound, not I/O |
| poka-yoke tokens | 1012s | near-zero verbatim | truncated | tier must be data, not model-typed |
| +enforce +effort=medium | 671s | 0 verbatim (paraphrase leaked) | truncated | low effort hurts verbatim fidelity |
| **sectioned + registry (final)** | **260s** | **0** (158/158 verified) | **yes (14 sections)** | **ground by construction** |

Breakthrough: the model **never types quote text** — it emits citation IDs, and code renders the exact quote + tier from a registry built from Jira. Mis-citation becomes structurally impossible; sectioned writing killed truncation and was fastest.

**Current state:** validated in standalone demo files. Production (`app.py`, `agent_sdk.py`, `tools_sdk.py`) is untouched and still runs the old single-query generator with the citation bug.

## Decision

Adopt the **ground-by-construction** architecture as the production design, structured around a **single injectable seam — the ticket source** — so demo (pre-cached fixture) and prod (live Jira) run the *same* pipeline, differing only in where ticket fields come from:

```
transcript → PLAN (research) → build quote registry from Jira fields
          → write sections in parallel (model emits [CITE:id] only)
          → deterministic assemble (render exact quote + tier from registry)
          → deterministic grounding gate (publish authority)
```

The LLM evaluator is **advisory only** — it produced both a false negative and a false positive in testing while the deterministic gate was right both times. The deterministic registry check is the publish gate.

## Options Considered

### Option A: Port the validated architecture to prod via a shared core (RECOMMENDED)
Extract the grounding core into shared modules with an injectable `ticket_source`. Demo injects the fixture; prod injects live Jira.

| Dimension | Assessment |
|-----------|------------|
| Complexity | Medium — mostly refactor of working code |
| Cost | Low — ~80% already exists and is tested |
| Scalability | Good — sectioned + parallel, async-friendly |
| Team familiarity | High — it's the code we just built |

**Pros:** demo *is* the prod prototype (zero throwaway); grounding guarantee carries to prod; fastest path.
**Cons:** touches prod files; live-Jira latency/retry must be added.

### Option B: Ship the demo standalone, defer prod
**Pros:** zero risk before Thursday. **Cons:** the "useless demo" risk — prod keeps the bug, work doesn't compound.

### Option C: Rebuild prod from scratch
**Pros:** clean. **Cons:** throws away tested code; not shippable by Thursday. Rejected.

## Trade-off Analysis
The real tension is **Thursday vs. true hardening.** Option A's *core* is portable in days (built + tested). *Hardening* (live-Jira latency, retries, multi-user, cost) is ~1–2 weeks. Honest split: adopt A's architecture now, phase the hardening. Don't claim full scale-readiness Thursday.

## Consequences
- **Easier:** trustworthy citations as a guarantee; truncation gone; defensible publish gate; demo work compounds into prod.
- **Harder / new:** live Jira adds latency, rate limits, failures the fixture hid (needs cache + retry); ~4-min generation needs an async-job UX; cost-per-guide must be tracked.
- **Revisit:** planner research is now the long pole (~115–197s) — cache ticket reads next; validate multi-module (only Item Management tested so far).

## Production-readiness checklist
- [ ] Live Jira data source behind the injectable seam (+ read-through cache, + retry/backoff for transient errors).
- [ ] Async generation jobs (queue + status), not a blocking 4-min request.
- [ ] Deterministic gate = publish authority; LLM eval advisory only.
- [ ] Secrets/auth out of `.env` into a secret store; revert the flagged `bypassPermissions` setting.
- [ ] Cost & observability: tokens/$ per guide, per-stage timing, structured logs.
- [ ] Multi-module validation (2–3 modules beyond Item Management).
- [ ] All three formats to the same grounding bar (micro/tldr via registry, not the weak derive path).

## Action Items (phased)
**Phase 0 — Thursday (demo + story):**
1. [ ] Close the micro/tldr grounding gap (registry-based) so all three formats are solid.
2. [ ] Rehearse the browser run; lead with the 0-mistake grounding guarantee + the evidence table.
3. [ ] Present this ADR as the prod plan.

**Phase 1 — prod core port (week 1):**
4. [ ] Extract shared grounding core with injectable `ticket_source`.
5. [ ] Add tier tokens to `tools_sdk.py`; wire the live-Jira source.
6. [ ] Move the sectioned pipeline + deterministic gate into `app.py`.

**Phase 2 — hardening (week 2):**
7. [ ] Jira cache + retry; async jobs; cost/observability; secrets; multi-module check.
