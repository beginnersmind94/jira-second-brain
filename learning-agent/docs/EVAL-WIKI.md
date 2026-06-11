# Eval Wiki: How to Judge AI-Generated LMS Content

**Subtitle:** A human-readable guide to groundedness, coverage, source quality, abstention, agentic decomposition, and release gates for AI-generated district training content.

**Audience:** Rahul, Jaime, domain SMEs, Implementation Engineering, and Claude Code / dev implementers.  
**Status:** Final wiki draft — conceptual guide first, implementation reference second.  
**Core idea:** Train humans on the eval mental model before asking code to enforce it.

---

## Navigation

- [0. What this wiki is](#0-what-this-wiki-is)
- [1. The customer problem](#1-the-customer-problem)
- [2. Enterprise RAG mental model](#2-enterprise-rag-mental-model)
- [3. The central eval idea](#3-the-central-eval-idea)
- [4. The three gates](#4-the-three-gates)
- [5. How to train the judge like a human](#5-how-to-train-the-judge-like-a-human)
- [6. Metrics that matter](#6-metrics-that-matter)
- [7. The gold set](#7-the-gold-set)
- [8. Beyond groundedness](#8-beyond-groundedness)
- [9. Agentic decomposition](#9-agentic-decomposition)
- [10. Diagnostic slicing](#10-diagnostic-slicing)
- [11. Ownership and operating cadence](#11-ownership-and-operating-cadence)
- [12. Scoring reference implementation](#12-reference-implementation--scoring-layer)
- [13. Coverage and source-quality reference implementation](#13-reference-implementation--coverage--source-quality-graders)
- [14. Claude Code checklist](#14-implementation-checklist-for-claude-code)
- [15. Jaime communication playbook](#15-jaime-communication-playbook)
- [16. References](#16-references)

---

## 0. What this wiki is

This is a **human-training wiki** for evaluating AI-generated LMS content. It is not only an engineering specification. It should teach a smart human how to think before they write code, tune prompts, approve output, or argue about metrics.

Use it in three ways:

1. **As a concept guide** — to explain why raw accuracy lies, why false negatives matter, why coverage is separate from groundedness, and why every surprising metric requires reading examples.
2. **As an implementation guide** — to define fixtures, gates, logs, graders, and release decisions.
3. **As a stakeholder script** — to explain to Jaime why the system is safe enough to review, but not magical enough to publish without calibration.

### The rule of the wiki

When the doc is silent, do not guess silently. Make the safest assumption, write it down, and add a fixture or dashboard slice that would reveal whether the assumption was wrong.

### Real-artifact rule

This wiki names artifacts like:

```text
NEXT-EVALS-PLAN.md
gate_log
data/qbank/adversarial_fixture.json
data/qbank/judge_run.jsonl
data/qbank/coverage_fixture.jsonl
data/qbank/source_fixture.jsonl
```

If an actual repo artifact contradicts this wiki, the real artifact wins. Do not force the repo into the doc. Remap the doc to the code and log the mismatch.

---

## 1. The customer problem

The LMS exists because districts lose staff and have to train the same roles repeatedly: cashiers, cafeteria managers, bookkeepers, CN directors, and finance users. A guide is valuable only if it helps a new or rotating user do the job correctly.

### Jaime's lens

Jaime does not need an AI demo. She needs fewer repeated training calls, fewer support escalations, and a way to trust that draft content is safe for SME review.

| Jaime cares about | Eval surface |
|---|---|
| Bad guidance never reaches customers | False-negative rate on should-FAIL |
| SMEs control correctness | critique shadowing + calibration |
| New hires get useful guides | workflow coverage grader |
| Old docs do not poison answers | freshness / staleness gate |
| Wrong-role content is blocked | lane-match + role purity |
| Review is auditable | `gate_log`, citations, failed-fixture history |

### District operator lens

A cashier does not care how clever the model is. They care whether the guide tells them the right next step while a line of students waits. A bookkeeper does not care about the retrieval architecture. They care whether the guide sends a payroll import into the right period.

The content has to be:

- **grounded** — every factual claim is backed by a cited source,
- **complete enough** — no missing P0 workflow fact,
- **role-matched** — the user sees their lane, not another module's work,
- **current** — stale workflows do not ship,
- **honest** — when the system does not know, it says so.

### Scope boundary

This wiki evaluates **truth and operational safety**. It does not fully evaluate pedagogy: retention, learning order, visual design, quiz quality, or whether a guide teaches beautifully. A guide can be grounded and still pedagogically weak. Treat pedagogy as the next eval surface, not as a reason to overload the support judge.

---

## 2. Enterprise RAG mental model

Naive RAG is usually:

```text
ask question → embed question → vector search → send chunks to LLM → answer
```

That is enough for simple demos. It is not enough for enterprise training content.

The Enterprise RAG chapter you provided describes the stronger pattern:

```text
input validation
→ question triage
→ query rewriting
→ asynchronous source search
→ order/filter results
→ writer agent
→ answer with cited source context
```

This matters because the LMS is not answering one clean question against one clean manual. It is turning messy source material — transcripts, Jira tickets, Freshdesk history, product docs, ICN content, internal wikis — into content that people may act on.

### Human translation

Enterprise RAG is not “the model knows things.” Enterprise RAG is **a controlled evidence workflow**:

1. Understand what the user is really asking.
2. Decide which lane and role the question belongs to.
3. Rewrite messy language into source-specific searches.
4. Search the right sources in parallel.
5. Rank evidence by relevance, authority, freshness, and role fit.
6. Write a clear answer from evidence.
7. Block the answer if any gate fails.

The important product line:

> The writer can draft. The gates decide whether the draft lives.

---

## 3. The central eval idea

The dangerous failure is not that the AI says “I do not know.” The dangerous failure is that it gives a confident answer that is not supported.

In classifier terms, the dangerous direction is:

```text
gold = FAIL / unsupported
judge = PASS / supported
```

That is a **false negative** on the should-FAIL class.

### Why raw accuracy lies

If 85% of test rows are supported, a lazy judge that says “PASS” to everything gets 85% raw accuracy while leaking every bad claim.

So the headline is not raw accuracy. The headline is:

```text
false-negative rate on should-FAIL
```

Or in plain English:

> Of the claims that should have been blocked, how many slipped through?

### The trust asymmetry

| Failure | Customer result | Recovery |
|---|---|---|
| Over-refusal | Guide stays in draft or user asks support | Recoverable |
| False negative | User acts on bad guidance | Not safely recoverable |
| Missing P0 fact | New hire misses critical step | Costly |
| Wrong-lane content | User follows another role's workflow | Costly |
| Stale source | Guide matches old product behavior | Costly |

This is why the system should bias toward safe draft, not confident publish.

---

## 4. The three gates

The base system has three gates:

```text
Generated draft
  ↓
Gate 1: Verify
  ↓
Gate 2: Lane-match
  ↓
Gate 3: Semantic support
  ↓
Draft or publish
```

### 4.1 Verify gate

**Type:** deterministic regression check  
**Question:** Is the artifact structurally valid?

Examples:

- Markdown is valid enough to render.
- Required fields are present.
- Citations exist where required.
- No empty sections.
- No unresolved templates like `{{TODO}}`.
- No broken output schema.

Target: **~100%**. If it drops, code broke. Do not tune the semantic judge.

### 4.2 Lane-match gate

**Type:** deterministic regression check  
**Question:** Is this content in the correct role/module/system lane?

Examples:

- Cashier content does not cite accounting workflow chunks.
- Oracle content does not pull Tyler Munis instructions.
- Inventory guide does not cite Eligibility workflow unless explicitly allowed.
- Retrieved chunk metadata intersects the user's role and module.

Target: **~100%**. If it drops, metadata, routing, or retrieval filtering broke.

### 4.3 Semantic-support gate

**Type:** calibrated capability judge  
**Question:** Is each claim supported by its cited source span?

This is where an LLM judge can help. The task is semantic, not just string matching. But the judge is not ground truth. The judge must be trained against SME critiques, measured on should-FAIL recall, and recalibrated after model changes.

---

## 5. How to train the judge like a human

The goal is not to ask an LLM, “Is this good?” The goal is to teach the judge the SME's standard.

### 5.1 Principal expert

Pick one principal standard per domain: the **Trainer/Curator** persona. In practice, Jaime owns the SME list.

Do not average vague opinions from a committee. That creates criteria drift.

### 5.2 Binary verdicts

For each `(claim, cited-span)` pair, the expert gives:

```text
PASS = fully supported by the cited span
FAIL = unsupported, contradicted, overstated, or only partially supported
UNKNOWN = not enough information to decide safely
```

### 5.3 Written critiques

A critique must teach the rule.

Weak critique:

```text
Not accurate.
```

Useful critique:

```text
The cited span says PostingDate determines the accounting period. The generated claim says CreatedDate determines the accounting period. That changes the workflow and would cause the guide to send users to the wrong field. Mark FAIL.
```

### 5.4 Few-shot prompt building

Turn the critiques into judge examples. The few-shots should include:

- exact support,
- partial support,
- plausible but unsupported claim,
- wrong-lane verbatim citation,
- stale-source citation,
- should-abstain case.

### 5.5 Recalibration triggers

Recalibrate when:

- model changes,
- source types change,
- a new module launches,
- SME standard changes,
- false negatives appear in review,
- quarterly review arrives.

---

## 6. Metrics that matter

### 6.1 Should-FAIL classifier metrics

Treat unsupported claims as the positive class.

```text
TP = unsupported claim correctly blocked
FP = supported claim incorrectly blocked
FN = unsupported claim incorrectly passed
```

Use:

```text
precision_fail = TP / (TP + FP)
recall_fail    = TP / (TP + FN)
fn_rate        = FN / (TP + FN)
```

Headline:

```text
fn_rate
```

### 6.2 pass^k, not pass@k

For trust-critical content, use **pass^k**: every one of k trials must pass.

If the per-trial pass rate is 75%:

| Metric | Meaning | Result at k=3 |
|---|---|---:|
| pass@3 | at least one trial passed | 98.4% |
| pass^3 | all three trials passed | 42.2% |

The second number is the honest one for publication gates.

### 6.3 Abstention metrics

Track two rates separately:

```text
confabulation_rate = should-abstain answered anyway
over_refusal_rate  = answerable item abstained
```

Bias toward low confabulation. Over-refusal is annoying. Confabulation is dangerous.

### 6.4 Partial credit

Binary gates decide publish/draft. Partial credit explains what to fix.

Examples:

- A guide can cover 8/10 P1 facts and still be useful for diagnostics.
- A micro-guide can pass P0 and fail P1 threshold.
- Source authority can be 3.6/5 even if one claim is flagged.

Use partial credit for development signal. Use hard gates for release decisions.

---

## 7. The gold set

The gold set must be two-sided: should-PASS and should-FAIL. If you only test good cases, you train a rubber stamp.

### 7.1 Required fixture families

For each gate, include positives and targeted negatives.

| Family | Meaning | Expected behavior |
|---|---|---|
| positive | correctly supported claim | PASS |
| wrong_lane_verbatim | exact quote from wrong role/module | FAIL |
| near_miss_paraphrase | sounds close, changes meaning | FAIL |
| plausible_unsupported | likely-sounding but not in cited span | FAIL |
| stale_source | grounded in expired source | FAIL |
| cross_lane | right fact, wrong user lane | FAIL |
| should_abstain | insufficient / contradictory evidence | UNKNOWN or ABSTAIN |

### 7.2 Reference solution rule

Every task needs a known-good reference solution. If a task has 0% pass rate across many trials, suspect the task or grader before blaming the model.

### 7.3 Ambiguity rule

If two domain experts cannot independently reach the same verdict, the fixture is not ready. Rewrite it.

### 7.4 Minimal schema sketch

```json
{
  "task_id": "TASK-00001",
  "metadata": {
    "domain": "Financials",
    "target_role": "Bookkeeper",
    "target_lane": "Payroll Import",
    "guide_type": "long_form",
    "required_p0_facts": ["PostingDate determines period"]
  },
  "source_context": [
    {
      "source_id": "wiki/payroll-import.md#posting-date",
      "source_type": "cybersoft_sop",
      "authority_tier": 2,
      "last_validated_at": "2026-06-01",
      "role_scope": ["Bookkeeper"],
      "module_scope": ["Financials"],
      "content_span": "..."
    }
  ],
  "reference_solution": {
    "output_text": "...",
    "expected_citations": ["wiki/payroll-import.md#posting-date"]
  },
  "adversarial_test_cases": [
    {
      "neg_class": "plausible_unsupported",
      "input_text": "...",
      "gold_label": "FAIL",
      "expected_gate": "support"
    }
  ]
}
```

---

## 8. Beyond groundedness

Groundedness asks: **Did the AI invent anything?**

That is necessary but not enough. The Enterprise RAG system needs separate checks for each failure dimension. Do not merge these into one mega-rubric.

### 8.1 Freshness / staleness

A claim can be supported by an old source and still be wrong for the user.

Build:

- `last_validated_at` per source span,
- source-type staleness windows,
- stale-source negative class,
- dashboard tile: `% cited sources within freshness window`.

Starting windows:

| Source type | Starting window |
|---|---:|
| USDA primary / regulatory | 90 days |
| Product workflow | 180 days |
| Internal SOP | 365 days |
| Freshdesk / historical ticket | only if elevated by SME or newer source unavailable |

### 8.2 Role / lane purity

Build:

- `role_scope` and `module_scope` on every source chunk,
- retrieval filter before generation,
- citation check after generation,
- cross-lane negative class.

Target dashboard line:

```text
Cross-lane leakage rate: 0.0%
```

### 8.3 Citation verifiability

Every published claim should link to a resolvable source. This is mostly for internal SME review, not frontline users.

Build:

- source pointer check,
- section/page anchor check,
- ticket URL or internal file resolution,
- dead-link DRAFT reason.

### 8.4 Coverage

Coverage asks: **Did the guide include the facts a new hire needs?**

Required facts should be defined by role × workflow, not by feature inventory.

Thresholds:

| Guide type | P0 threshold | P1 threshold |
|---|---:|---:|
| long_form | 100% | report only |
| micro | 100% | 80% |
| tldr | 100% | report only |

Hard rule:

```text
missing any P0 fact → DRAFT
```

### 8.5 Source quality

A claim can be grounded but grounded in the wrong shelf.

Authority order:

```text
USDA primary
> state CN office
> vendor docs
> Cybersoft SOP
> Freshdesk / historical tickets
> blogs / forums / informal notes
```

Flag:

```text
low-authority citation chosen when higher-authority source existed for same claim
```

### 8.6 Production monitoring

Offline evals are one layer. Add:

- production drift monitoring,
- user feedback buttons,
- weekly SME sample review,
- broken-citation watch,
- abstention-rate trend,
- regression fixture per real bug.

This is the Swiss Cheese model: many imperfect layers, each catching what the others miss.

---

## 9. Agentic decomposition

### 9.1 The rule

Use agents for judgment. Use code for gates.

Enterprise RAG is not one chatbot call. It is a chain of specialized jobs:

```text
validate request
→ classify role/module/workflow
→ rewrite queries
→ retrieve from source-specific indexes
→ rank evidence
→ write guide
→ extract claims
→ judge support
→ grade coverage
→ grade source quality
→ decide DRAFT/PUBLISH
```

Some jobs need LLM judgment. Some jobs should be plain deterministic code.

### 9.2 Where agents help

| Agent role | Why it helps |
|---|---|
| Triage Agent | maps messy requests to role, module, workflow, guide type |
| Query Rewrite Agent | converts transcript/user phrasing into source-specific search queries |
| Retrieval Planner | decides which source indexes to search |
| Source Retrieval Agents | parallel Jira/Freshdesk/wiki/transcript/product-doc searches |
| Evidence Ranker | weighs relevance, freshness, authority, and role fit |
| Guide Writer | turns evidence into readable LMS content |
| Semantic Support Judge | checks claim ↔ cited span support |
| Coverage Judge / matcher | checks required facts present |
| Source Quality Judge / scorer | flags low-authority citation choices |

### 9.3 Where agents should not decide

Keep these as code:

| Deterministic job | Why code wins |
|---|---|
| schema validation | no judgment needed |
| lane metadata intersection | exact metadata check |
| citation link resolution | URL/file pointer either resolves or not |
| freshness threshold | timestamp math |
| coverage aggregation | count present facts |
| authority tier scoring | table lookup + average |
| final publish decision | auditable policy gate |

### 9.4 AutoGen decision

AutoGen is conceptually useful for learning multi-agent orchestration, but it should not be the default production foundation for a new build. Microsoft’s own AutoGen repository says AutoGen is in maintenance mode and recommends Microsoft Agent Framework for new users.

Recommended path:

1. **Start with a plain Python workflow/DAG** shaped like agent contracts.
2. Use LLM calls only in fuzzy steps: triage, rewriting, writing, semantic judging.
3. Keep all gates deterministic and replayable.
4. If orchestration becomes painful, evaluate Microsoft Agent Framework or LangGraph.
5. Use AutoGen only as a learning/prototype reference.

### 9.5 Agent contract

Every agent-shaped step should have:

```json
{
  "name": "QueryRewriteAgent",
  "input_schema": {},
  "output_schema": {},
  "allowed_tools": [],
  "max_iterations": 1,
  "temperature": 0,
  "trace_required": true
}
```

### 9.6 Kill criteria for agent frameworks

Stop adopting an agent framework if it:

- adds more than 20% wall-time,
- makes traces harder to read,
- prevents deterministic replay,
- hides tool calls,
- makes `gate_log` or `judge_run` ambiguous,
- blocks simple unit tests.

---

## 10. Diagnostic slicing

The Chapter 03 repo example is not a RAG eval harness. Its transferable pattern is diagnostic offline evaluation:

```text
compute metric → join metadata → slice by meaningful cohorts → inspect failures
```

Adaptation:

| Chapter 03 move | LMS eval adaptation |
|---|---|
| simulated recommendation outputs | `judge_run.jsonl`, `coverage_fixture.jsonl`, `source_fixture.jsonl` |
| user/movie metadata | `gate`, `neg_class`, `guide_type`, `role_scope`, `workflow`, `source_type` |
| aggregate metric | false-negative rate, coverage %, authority score |
| subgroup slices | `gate × neg_class`, `role_scope × workflow`, per-claim authority |
| hidden failure | which gate, workflow, role, or source class is leaking |

Examples:

```text
FN rate by gate
FN rate by negative class
P0 coverage by role × workflow
Authority score by source_type
Draft reasons by guide_type
Abstention failures by module
```

Rule:

> A metric tells you whether something is wrong. A slice tells you what to fix.

---

## 11. Ownership and operating cadence

### 11.1 Owners

| Area | Owner |
|---|---|
| Eval harness / CI | Dev team |
| Gold-set criteria | Jaime's named SMEs |
| Calibration cadence | Rahul / PM |
| Dashboard review | Rahul + Jaime |
| Fixture expansion | PM + SMEs + dev |
| Production publish policy | Product + Implementation leadership |

### 11.2 Weekly operating rhythm

```text
Monday: review dashboard and DRAFT reasons
Tuesday-Wednesday: add or repair fixtures from failures
Thursday: SME spot-check sample guides
Friday: update regression set and publish safe docs
```

### 11.3 Model-swap rhythm

Before a model swap:

- rerun full gold set,
- rerun pass^k,
- compare FN rate by negative class,
- review at least 10 changed verdicts manually,
- recalibrate few-shots if criteria drift appears.

### 11.4 Done definition for release

A guide can publish only when:

```text
verify gate passes
lane-match gate passes
semantic-support gate passes
coverage gate passes
source-quality gate passes
freshness gate passes
citation verifier passes
```

Any failed gate gives:

```text
status = DRAFT
reason = specific failure reason
trace = source row / claim id / fact id / citation id
```

---

## 12. Reference implementation — scoring layer

This section makes §§1, 4, and 4.5.3 implementation-complete. The graders described in §§4.5.5–4.5.6 are **not** folded in here — per the §4.5 "do not merge" rule they remain separate single-dimension graders.

Everything below is the **scoring** layer: it consumes judge verdicts that already exist and computes the metrics the doc mandates. It runs no model calls — the LLM-as-a-judge is an input here, consistent with §4: **LLM-as-a-judge is an evaluation method, not a metric.**

### 10.1 Input schema

One row per `(claim, cited-span)` trial.

Columns fall directly out of the spec:

```text
gate        : "verify" | "lane_match" | "support"                      (§1)
neg_class   : "positive"                                               (should-PASS, §5)
            | "wrong_lane_verbatim" | "near_miss_paraphrase"
            | "plausible_unsupported"                                  (§5)
            | "stale_source" | "cross_lane" | "should_abstain"         (§4.5)
gold_label  : "PASS" | "FAIL" | "ABSTAIN"        SME ground truth       (§3)
judge_label : "PASS" | "FAIL" | "UNKNOWN"        judge output           (§6.4 abstain)
item_id     : stable gold-item id
trial_id    : trial index, k≥3                                          (§1 pass^k)
```

If the real `data/qbank/adversarial_fixture.json`, `judge_run.jsonl`, or `gate_log` schema differs, the real artifact wins (§0). Remap the column names above and nothing else changes.

### 10.2 Headline metric + Chapter-3 diagnostic slicing

Implements §4: precision/recall on should-FAIL, with **false-negative rate** as the headline. It adapts the Chapter 03 repo notebook's diagnostic-offline-evaluation shape (§0.1): compute the metric, join/slice by meaningful metadata, then surface subgroup failures that the aggregate would hide.

```python
import pandas as pd
import numpy as np

df = pd.read_json("data/qbank/judge_run.jsonl", lines=True)

# §2: the dangerous event — judge PASSes a should-FAIL item.
df["is_should_fail"]    = df["gold_label"].eq("FAIL")
df["is_false_negative"] = df["is_should_fail"] & df["judge_label"].eq("PASS")

# §4: precision counterpart — judge FAILs a should-PASS item.
df["is_should_pass"]    = df["gold_label"].eq("PASS")
df["is_false_positive"] = df["is_should_pass"] & df["judge_label"].eq("FAIL")

def fail_class_metrics(g):
    """§4: precision + recall on the should-FAIL class. Never raw agreement."""
    sf = int(g["is_should_fail"].sum())
    fn = int(g["is_false_negative"].sum())   # leaked: said PASS, was FAIL
    tp = sf - fn                             # caught: said FAIL/UNKNOWN, was FAIL
    fp = int(g["is_false_positive"].sum())   # over-blocked should-PASS
    return pd.Series({
        "should_fail_n": sf,
        "false_neg_n":   fn,
        "fn_rate":       fn / sf if sf else np.nan,            # HEADLINE
        "recall_fail":   tp / sf if sf else np.nan,
        "precision_fail": tp / (tp + fp) if (tp + fp) else np.nan,
    })

# HEADLINE — one number for Jaime (§8.5)
overall = fail_class_metrics(df)
print(f"HEADLINE false-negative rate: {overall['fn_rate']:.1%} "
      f"[{overall['false_neg_n']:.0f}/{overall['should_fail_n']:.0f}] "
      f"recall={overall['recall_fail']:.1%} precision={overall['precision_fail']:.1%}")

# SLICE 1 — by gate (§1: separates deterministic-gate regression from judge tuning).
# verify & lane_match must sit at ~0 FN; nonzero here means something BROKE,
# not "the judge needs calibration".
print("\nFN rate by gate:")
print(df.groupby("gate").apply(fail_class_metrics, include_groups=False)
        [["should_fail_n", "false_neg_n", "fn_rate"]])

# SLICE 2 — by negative class (§5 adversarial families). Tells you WHICH family
# is leaking, so you add the right critiques (§3) instead of staring at one number.
print("\nFN rate by negative class:")
print(df[df["is_should_fail"]]
        .groupby("neg_class").apply(fail_class_metrics, include_groups=False)
        [["should_fail_n", "false_neg_n", "fn_rate"]])
```

### 10.3 pass^k consistency

Ship only if **every** one of k trials passes, with `k≥3`.

`pass@k` is computed solely to show the contrast Jaime should **not** be sold on.

```python
def passk_report(df, k_min=3):
    df = df.copy()

    # A trial passes iff the judge's verdict is correct.
    # §6 safer/stricter rule: judge UNKNOWN counts as a pass ONLY on should-FAIL
    # items (correctly declined to wave a bad claim through); on should-PASS /
    # should-ABSTAIN items UNKNOWN is a non-pass.
    df["trial_pass"] = df["judge_label"].eq(df["gold_label"])
    df.loc[df["judge_label"].eq("UNKNOWN"), "trial_pass"] = df["gold_label"].eq("FAIL")

    per_item = df.groupby("item_id").agg(
        k=("trial_id", "nunique"),
        all_pass=("trial_pass", "all"),
        any_pass=("trial_pass", "any"),
    )

    under_k = int((per_item["k"] < k_min).sum())
    if under_k:
        print(f"WARNING: {under_k} items ran < k={k_min} trials — "
              f"isolation/coverage gap (§6). Investigate before trusting the score.")

    return pd.Series({
        "items":          len(per_item),
        f"pass^{k_min}":  per_item["all_pass"].mean(),   # the number Jaime hears
        f"pass@{k_min}":  per_item["any_pass"].mean(),   # contrast only — do not ship on this
    })

print("\nConsistency (k≥3):")
print(passk_report(df, k_min=3))
```

### 10.4 Abstention quality

Turns the §4.5.3 checklist into the two separately tracked rates it asks for, weighted per the doc's trade-off: **confabulation is unrecoverable, over-refusal is recoverable.**

```python
abstain_items = df[df["gold_label"].eq("ABSTAIN")]
answerable    = df[df["gold_label"].ne("ABSTAIN")]

if len(abstain_items):
    confab = abstain_items["judge_label"].eq("PASS").mean()
    print(f"\nConfabulation rate (should-abstain answered): {confab:.1%} "
          f"← unrecoverable; defend a small number (§4.5.3)")

if len(answerable):
    over = answerable["judge_label"].eq("UNKNOWN").mean()
    print(f"Over-refusal rate (answerable abstained):     {over:.1%} ← recoverable")
```

### 10.5 Assumptions surfaced

Written down rather than guessed silently:

- **UNKNOWN = safe-fail.** Judge abstention counts as a *pass* on should-FAIL items because it correctly declined to let a bad claim through. It counts as a *non-pass* everywhere else. This follows §6's safer/stricter default and §4.5.3's recoverability asymmetry. Revisit if `gate_log` already encodes UNKNOWN handling — the real artifact wins (§0).
- **Deterministic gates share the scoring frame.** `verify` and `lane_match` are scored alongside `support` so a regression surfaces as nonzero FN, but they are sliced separately (§10.2 Slice 1) so a broken gate is never misread as judge miscalibration (§1).
- **Missing trials are a signal, not noise.** `pass^k` warns when any item ran fewer than k trials rather than silently averaging, per the §6 isolation rule.

### 10.6 Not in this layer

Per the §4.5 "do not merge" rule, these stay separate single-dimension graders:

- **Coverage grader (§4.5.5)** — required-facts-present %, P0/P1 thresholds per guide type, with partial credit (§6).
- **Source-quality grader (§4.5.6)** — average authority tier over cited sources and flagging plausible-but-low-authority citations.

---

## 13. Reference implementation — coverage & source-quality graders

Per the §4.5 "do not merge" rule, these are two independent single-dimension graders. Neither touches the §10 should-FAIL scorer. Both run on a generated guide plus its gold-set metadata; both emit a continuous score for partial credit (§6) and a binary gate decision.

### 11.1 Coverage grader

Implements:

- required-facts-present %
- P0/P1 priority
- per-guide-type thresholds
- partial credit
- the §4.5.5 gate: **any missing P0 → stays in draft**

Per-guide-type thresholds:

| Guide type | P0 threshold | P1 threshold | Gate behavior |
|---|---:|---:|---|
| `long_form` | 100% | Report only | Publish on P0 coverage alone |
| `micro` | 100% | 80% | Publish only if P0 and P1 thresholds clear |
| `tldr` | 100% | Report only | Publish on P0 coverage alone |

```python
import pandas as pd
import numpy as np

# ── Input schema (derived from §4.5.5) ───────────────────────────────────────
# Per-role × per-workflow required-coverage lists live in the gold set, owned by
# Jaime's SMEs. One row per required fact:
#   guide_id     : the generated guide under test
#   guide_type   : "long_form" | "micro" | "tldr"
#   role_scope   : role this guide serves (§4.5.2)
#   workflow     : the week-1 workflow the fact belongs to
#   fact_id      : stable id of the required fact
#   priority     : "P0" | "P1"          (P0 = job-critical; P1 = supporting)
#   is_present   : bool — did the generated guide cover this fact?
#                  (set by a fact-matching judge OR deterministic string/anchor
#                   check; coverage scoring treats it as an input, §4)
coverage = pd.read_json("data/qbank/coverage_fixture.jsonl", lines=True)

# Per-guide-type thresholds (§4.5.5). None = priority not required for that type.
COVERAGE_THRESHOLDS = {
    "long_form": {"P0": 1.00, "P1": None},   # 100% P0; P1 not gated
    "micro":     {"P0": 1.00, "P1": 0.80},   # 100% P0, 80% P1
    "tldr":      {"P0": 1.00, "P1": None},   # 100% P0 only
}

def coverage_grade(g):
    guide_type = g["guide_type"].iloc[0]
    thresholds = COVERAGE_THRESHOLDS[guide_type]
    out = {"guide_type": guide_type}
    missing_p0, gate_pass = [], True

    for prio in ("P0", "P1"):
        sub = g[g["priority"].eq(prio)]
        n = len(sub)
        present = int(sub["is_present"].sum())
        frac = present / n if n else np.nan          # partial credit (§6)
        out[f"{prio}_present"] = present
        out[f"{prio}_total"]   = n
        out[f"{prio}_frac"]    = frac

        req = thresholds[prio]
        if req is not None and n:
            if frac < req:
                gate_pass = False
            if prio == "P0":
                missing_p0 = sub.loc[~sub["is_present"], "fact_id"].tolist()

    # §4.5.5 hard rule: ANY missing P0 fact → draft, regardless of other scores.
    if missing_p0:
        gate_pass = False

    out["missing_p0_facts"] = missing_p0
    out["gate"] = "PUBLISH" if gate_pass else "DRAFT"
    return pd.Series(out)

coverage_report = coverage.groupby("guide_id").apply(coverage_grade, include_groups=False)

# Dashboard line for Jaime (§4.5.5): critical vs. supporting coverage.
crit = coverage[coverage["priority"].eq("P0")]["is_present"].mean()
supp_sub = coverage[coverage["priority"].eq("P1")]
supp = supp_sub["is_present"].mean() if len(supp_sub) else np.nan
print(f"Coverage: {crit:.0%} on critical (P0) workflows, "
      f"{supp:.0%} on supporting (P1) workflows")

# Diagnostic slice (Ch.3 pattern): coverage gaps by role × workflow, so Jaime
# sees WHICH onboarding scenario is at risk before tickets arrive.
print("\nP0 coverage by role × workflow:")
print(coverage[coverage["priority"].eq("P0")]
        .groupby(["role_scope", "workflow"])["is_present"].mean())

print("\nGuides held in DRAFT for missing P0:")
print(coverage_report[coverage_report["gate"].eq("DRAFT")]
        [["guide_type", "P0_frac", "missing_p0_facts"]])
```

#### 11.1.1 Assumptions surfaced

- `is_present` is an input, not computed here. A required fact is "present" via a fact-matching judge or a deterministic anchor/string check upstream. Coverage scoring only aggregates it (§4). If the gold set stores presence differently, the real artifact wins (§0).
- P1 with no threshold (`None`) is reported but never gates. Long-form and TLDR publish on P0 alone, per §4.5.5.
- Empty priority bucket (`n == 0`) yields `NaN` frac and never blocks the gate. Absence of P1 facts is not a failure.

### 11.2 Source-quality grader

Implements:

- per-domain authority tiers
- average authority per claim
- the §4.5.6 negative class: **plausible-but-low-authority citation when a higher-authority source exists for the same claim**

```python
# ── Authority tiers (§4.5.6). Higher = more authoritative. SME-owned map. ─────
# USDA primary > state CN office > vendor docs > Cybersoft SOP > FreshDesk > blog
AUTHORITY_TIER = {
    "usda_primary":   5,
    "state_cn":       4,
    "vendor_docs":    3,   # Oracle, Tyler
    "cybersoft_sop":  2,
    "freshdesk":      1,
    "vendor_blog":    0,   # blogs, Stack Overflow
}

# ── Input schema (derived from §4.5.6) ───────────────────────────────────────
# One row per cited source backing a claim:
#   guide_id         : guide under test
#   claim_id         : the claim this citation supports
#   source_type      : key into AUTHORITY_TIER
#   higher_available : bool — did a higher-authority source exist for THIS claim
#                      but the generator cited a lower one? (set upstream by the
#                      retrieval-audit step; input here, §4)
sources = pd.read_json("data/qbank/source_fixture.jsonl", lines=True)
sources["tier"] = sources["source_type"].map(AUTHORITY_TIER)

unmapped = sources["tier"].isna()
if unmapped.any():
    print(f"WARNING: {int(unmapped.sum())} citations have an unmapped source_type "
          f"— extend AUTHORITY_TIER (SME-owned, §4.5.6). Excluded from scores.")
    sources = sources[~unmapped]

# §4.5.6 negative class: low-authority citation chosen when a better one existed.
sources["low_authority_flag"] = sources["higher_available"].astype(bool)

# Per-claim average authority, then per-guide average across claims.
per_claim = sources.groupby(["guide_id", "claim_id"]).agg(
    avg_tier=("tier", "mean"),
    flagged=("low_authority_flag", "any"),
)
per_guide = per_claim.groupby("guide_id").agg(
    authority_score=("avg_tier", "mean"),
    flagged_claims=("flagged", "sum"),
    claims=("avg_tier", "size"),
)

# Dashboard line for Jaime (§4.5.6): 0–5 scale.
overall_auth = sources["tier"].mean()
print(f"\nAuthority score: {overall_auth:.1f}/5 average across cited sources")

# Diagnostic slice (Ch.3 pattern): where is retrieval reaching for the wrong shelf?
print("\nFlagged claims (lower-authority cited when better source existed):")
print(per_guide[per_guide["flagged_claims"] > 0]
        [["authority_score", "flagged_claims", "claims"]])

# Optional gate (§6 stricter default): block guides citing low authority when a
# higher-authority source was available. Threshold is SME-tunable, not hardcoded
# as policy — start strict and relax on calibration evidence.
MIN_AUTHORITY = 3.0   # ≥ vendor_docs average; tune with Jaime's SMEs.
per_guide["gate"] = np.where(
    (per_guide["flagged_claims"] == 0) & (per_guide["authority_score"] >= MIN_AUTHORITY),
    "PUBLISH", "DRAFT"
)

print("\nGuides held in DRAFT on source quality:")
print(per_guide[per_guide["gate"].eq("DRAFT")])
```

#### 11.2.1 Assumptions surfaced

- `higher_available` is an input from an upstream retrieval-audit step, not computed here. This grader scores citations the generator actually chose, not the full retrieval index.
- `MIN_AUTHORITY = 3.0` and the authority-tier integers are starting values, SME-owned per §4.5.6, not fixed policy. Calibrate against the gold set once it exists. Redis-style thresholds are directional only, per the doc's source-quality note.
- Unmapped `source_type` values are warned and excluded rather than silently scored as 0, so a missing tier entry cannot quietly deflate the authority score.

### 11.3 Gates are not merged

Coverage and source-quality gates are evaluated independently of each other and of the §10 should-FAIL scorer.

A guide publishes only if it clears all applicable gates:

| Gate | Primary question | Failure that forces DRAFT |
|---|---|---|
| Scoring layer / support judge (§10) | Did unsupported claims leak through? | Nonzero should-FAIL leakage above accepted threshold |
| Coverage (§11.1) | Did the guide include required workflow facts? | Any missing P0; micro also fails below 80% P1 |
| Source quality (§11.2) | Did the generator cite authoritative sources? | Flagged low-authority claim when higher-authority source existed; average tier below SME threshold |
| Freshness (§4.5.1) | Are cited sources still validated? | Source past threshold without re-validation |
| Lane purity (§4.5.2) | Is content scoped to the user's role/module? | Cross-lane retrieval or generated claim |
| Citation verifiability (§4.5.4) | Can internal reviewers resolve citations? | Dead, redirected, or unresolvable citation anchor |

Partial credit is reported for diagnostics, not as a bypass. A P0 coverage miss, a stale source, cross-lane content, or a flagged low-authority citation each independently forces DRAFT.

---

## 14. Implementation checklist for Claude Code

This is the repo-facing checklist. Use it to turn the wiki into a build.

### 12.1 Files to create or update

| File | Purpose |
|---|---|
| `data/qbank/judge_run.jsonl` | Trial-level judge outputs consumed by §10 |
| `data/qbank/adversarial_fixture.json` | Balanced positive/negative gold set across verify, lane-match, support, stale-source, cross-lane, should-abstain |
| `data/qbank/coverage_fixture.jsonl` | Required facts by guide, role, workflow, and priority |
| `data/qbank/source_fixture.jsonl` | Cited sources by guide, claim, authority tier, and higher-available flag |
| `evals/scoring.py` | §10 headline metric, diagnostic slices, pass^k, abstention metrics |
| `evals/coverage.py` | §11.1 coverage grader |
| `evals/source_quality.py` | §11.2 source-quality grader |
| `evals/report.py` | Jaime-facing dashboard rollup |
| `tests/evals/test_scoring.py` | Regression tests for metric semantics |
| `tests/evals/test_coverage.py` | Regression tests for P0/P1 gating |
| `tests/evals/test_source_quality.py` | Regression tests for authority tiers and low-authority flags |

### 12.2 Minimum test cases

- should-FAIL + judge PASS → false negative increments
- should-FAIL + judge FAIL → caught failure
- should-FAIL + judge UNKNOWN → safe-fail / pass for trial consistency
- should-PASS + judge UNKNOWN → non-pass
- should-ABSTAIN + judge PASS → confabulation increments
- item with fewer than three trials → warning emitted
- long-form guide missing P0 → DRAFT
- micro guide with 100% P0 but 70% P1 → DRAFT
- TLDR guide with 100% P0 and 0% P1 → PUBLISH
- source with unmapped `source_type` → warning and exclusion
- source with `higher_available=True` → flagged claim; DRAFT under strict default

### 12.3 Dashboard rollup Jaime should see

Keep the dashboard boring and defensible:

```text
False-negative rate on should-FAIL: 0.0% [0/N]
pass^3: 100.0%
Confabulation rate: 0.0%
Over-refusal rate: X.X%
Coverage: 100% P0 / YY% P1
Authority score: Z.Z/5
Guides held in DRAFT: N
Top draft reasons: missing P0, stale source, low-authority citation, cross-lane citation
Broken citation rate: 0.0%
```

Do **not** show raw agreement as the headline.

### 12.4 Done definition

The eval wiki is implementation-ready when:

- every gate has a fixture schema,
- every fixture schema has at least one passing and one failing reference row,
- every metric has a unit test that proves the dangerous direction is counted correctly,
- every DRAFT decision reports the reason,
- Jaime can read one dashboard line and know whether content is safe to review, and
- engineers can inspect the diagnostic slices to know whether the problem is a broken deterministic gate, a judge prompt issue, a coverage omission, stale knowledge, or retrieval reaching for the wrong shelf.

---

---

## 15. Jaime communication playbook

Do not open a stakeholder meeting with eval theory. Open with the LMS demo and the customer pain. Then use the eval system to answer the trust question.

### Three sentences

1. "Districts keep retraining new staff. The LMS only saves time if the guidance is correct enough for real work."
2. "So every guide goes through separate gates: structure, role-lane, source support, coverage, freshness, and source authority. Anything unsafe stays in draft."
3. "We do not report vague AI accuracy. We report the rate at which unsupported claims slip through, because that is the failure that creates district incidents."

### What to show

- one generated guide,
- one claim with citation,
- one should-FAIL example the judge caught,
- one missing-P0 coverage example held in draft,
- the dashboard rollup.

### What not to say

- Do not promise zero failures.
- Do not say the AI is accurate; say the eval system catches unsafe drafts.
- Do not lead with compliance.
- Do not show raw metric dumps.
- Do not merge all quality questions into one score.

---

## 16. References

- Anthropic. *Demystifying evals for AI agents.* https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- Hamel Husain. *Using LLM-as-a-judge for evaluation: A complete guide.* https://hamel.dev/blog/posts/llm-judge/
- Hamel Husain. *LLM evals: Everything you need to know.* https://hamel.dev/blog/posts/evals-faq/
- Hamel Husain. *The revenge of the data scientist.* https://hamel.dev/blog/posts/revenge/
- Lnassery. *ai-evaluations — Chapter 03 diagnostic notebook.* https://github.com/lnassery/ai-evaluations/tree/main/notebooks/chapter_03
- Microsoft AutoGen repository. https://github.com/microsoft/autogen
- Microsoft Agent Framework overview. https://learn.microsoft.com/en-us/agent-framework/overview/
- Microsoft Agent Framework workflows. https://learn.microsoft.com/en-us/agent-framework/workflows/
- Microsoft Azure Architecture Center. *Develop a RAG solution — LLM end-to-end evaluation phase.* https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/rag/rag-llm-evaluation-phase
- AI21. *RAG evaluation: Metrics, challenges & considerations.* https://www.ai21.com/knowledge/rag-evaluation/
- Redis. *RAG evaluation guide: Metrics, frameworks & infrastructure.* https://redis.io/blog/rag-system-evaluation/

---

## One-line summary

Great evals for this LMS mean: **new hires get correct, role-matched, current guidance fast; SMEs control the correctness standard; bad guidance stays in draft; every failure becomes a fixture; and every number can be traced back to the examples behind it.**
