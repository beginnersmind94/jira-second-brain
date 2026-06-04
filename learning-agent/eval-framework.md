# Eval Framework — Learning Content Producer

## Overview

This framework defines the evaluation suite for the learning content producer pipeline. It covers five pipeline stages (Mapper, PM, SME, Writer, Reviewer) with deterministic and model-based graders.

Start here. Run these before every pipeline change. Read the transcripts.

## Principles (from Anthropic's eval guidance)

1. **Start with 20–50 tasks from real failures.** Don't wait for a perfect suite.
2. **Grade outcomes, not paths.** Don't check tool call sequences.
3. **Build in partial credit.** A draft with 80% citation coverage is better than 0%.
4. **Combine grader types.** Deterministic where possible, model-based where necessary, human for calibration.
5. **Test both directions.** If you only test "did the agent search when it should," you'll get an agent that searches for everything.
6. **Read the transcripts.** You won't know if graders work unless you read the outputs.

## Directory structure

```
evals/
├── framework.md              # This file
├── tasks/
│   ├── mapper/               # Mapper eval tasks
│   ├── planner/              # PM eval tasks
│   ├── factcheck/            # SME eval tasks
│   ├── writer/               # Writer eval tasks
│   └── reviewer/             # Reviewer eval tasks
├── rubrics/
│   ├── citation-quality.md   # Model-based rubric for citation grading
│   ├── voice-match.md        # Model-based rubric for voice fidelity
│   ├── hallucination-check.md # Model-based rubric for invented specifics
│   └── review-accuracy.md    # Model-based rubric for reviewer verdict quality
├── fixtures/
│   ├── transcripts/          # Test transcripts (including the Item Management one)
│   ├── guides/               # Reference guides (GUIDE-068, GUIDE-069)
│   ├── drafts-clean/         # Known-good drafts for false-fail testing
│   └── drafts-defective/     # Drafts with injected defects for false-pass testing
├── results/
│   └── YYYY-MM-DD-run-N.md   # Eval run results
└── baselines/
    └── YYYY-MM-DD-baseline.md # Baseline scores for regression tracking
```

---

## Task format

Each task is a YAML file:

```yaml
id: "mapper-completeness-001"
stage: mapper
type: capability            # capability | regression
description: "Mapper identifies all features in Item Management training transcript"
input:
  transcript: fixtures/transcripts/2026-05-28-item-management-create-items-training.md
  module: "Item Management"
  reference_guides:
    - fixtures/guides/GUIDE-068-create-non-food-items-quick-guide.pdf
    - fixtures/guides/GUIDE-069-create-food-items-quick-guide.pdf
graders:
  - id: completeness
    type: deterministic
    weight: 0.3
    check: "count features in transcript >= count features in inventory (matched + unmatched + cross-module)"
  - id: no_silent_drops
    type: deterministic
    weight: 0.2
    check: "no feature from expected_features is absent from all output tables"
  - id: cross_module_flagging
    type: deterministic
    weight: 0.2
    check: "references to Inventory module, POS module, Menu Planning, Recipes are in Cross-Module table"
  - id: unmatched_flagging
    type: deterministic
    weight: 0.15
    check: "presenter claims that can't be verified are in Unmatched table"
  - id: field_priority
    type: model-based
    weight: 0.15
    rubric: rubrics/citation-quality.md
    check: "matched features cite AC first, not Description"
pass_threshold: 0.85
trials: 3
```

---

## Initial task suite

35 tasks total: 21 capability + 14 regression, distributed across the five pipeline stages. The full table of task IDs and key checks lives in the version of this file that ships with the agent team (see the original eval-framework.md handoff).

Stages and counts:
- Mapper: 8 tasks
- PM / Planner: 6 tasks
- SME / Fact-check: 7 tasks
- Writer: 8 tasks
- Reviewer: 6 tasks

---

## Grader rubrics

### rubrics/citation-quality.md

```
Score each claim on citation quality (0–5):

5 — Claim cites specific ticket ID + AC verbatim quote, or transcript timestamp + verbatim quote
4 — Claim cites ticket ID or timestamp but paraphrases instead of quoting verbatim
3 — Claim cites a source but the citation is vague ("per the guide" without specifics)
2 — Claim is probably correct based on context but has no citation
1 — Claim is plausible but unsupported and not marked [TO VERIFY]
0 — Claim appears fabricated or contradicts known sources

Overall score = mean across all claims, normalized to 0.0–1.0.
Pass threshold: ≥ 0.8 (mean score ≥ 4.0)
```

### rubrics/voice-match.md

```
Score the content on voice fidelity (0–5):

5 — Reads like a well-edited version of the training session. Uses presenter's examples, tone is conversational but professional. Teaching flow matches transcript order.
4 — Professional and clear. Uses some presenter examples. Tone is slightly more formal than the training but still accessible.
3 — Correct but reads like documentation, not a training guide. Presenter's voice is not recognizable.
2 — Reads like a database dump with headers. No teaching flow. Dry enumeration of features.
1 — Reads like a Jira ticket export. Internal jargon present. Not suitable for customer staff.
0 — Incoherent or contradicts the transcript's teaching approach.

Pass threshold: ≥ 0.7 (score ≥ 3.5)
```

### rubrics/hallucination-check.md

```
For each factual claim in the draft, check:

1. Is a specific menu path stated? (e.g., "Item Management > Configuration > Item Configuration")
   → Verify against transcript timestamp or guide page. If not found, flag as HALLUCINATED.

2. Is a specific field name stated? (e.g., "Edible Yield Factor")
   → Verify against transcript or guide. If not found, flag as HALLUCINATED.

3. Is a specific number or limit stated? (e.g., "maximum 3-tier pack sizes")
   → Verify against transcript or guide. If not found, flag as HALLUCINATED.

4. Is a specific behavior described? (e.g., "the system automatically enables the Publish toggle")
   → Verify against transcript or guide. If not found, flag as HALLUCINATED.

Score = (total claims - hallucinated claims) / total claims
Pass threshold: 1.0 (zero hallucinations)
```

### rubrics/review-accuracy.md

```
For each PASS/FAIL judgment in the review:

1. Is the judgment supported by specific evidence from the draft? (not vague)
2. If FAIL, is the failure type correctly categorized? (template, plan, source, mapping)
3. If FAIL, is the routing destination correct? (Mapper, PM, SME, Writer)
4. If PASS, would a human reviewer also pass this draft?

Score per judgment: 1.0 if correct, 0.5 if partially correct (right verdict, wrong routing), 0.0 if wrong.
Overall score = mean across all judgments.
Pass threshold: ≥ 0.9
```

---

## Defect injection templates

For testing the Reviewer, create defective drafts by injecting specific problems:

### Template violation defects
- `overcoverage`: Add 8 full workflow sections to a micro guide
- `overflow`: Make a TLDR exceed 5000 chars of visible text
- `missing_section`: Remove the "Common mistakes" section from a micro guide

### Source grounding defects
- `uncited_claim`: Add 3 factual statements without `<!-- Source: -->` comments
- `hallucinated_path`: Insert a menu path that doesn't exist ("Item Management > Advanced > Batch Import")
- `hallucinated_limit`: Insert a false limit ("maximum 5-tier pack sizes")

### Mapping defects
- `wrong_module`: Include a detailed section on Inventory receiving (not in the transcript's module)
- `phantom_feature`: Include a feature the presenter never mentioned

### Plan alignment defects
- `priority_inversion`: Give full depth to a low-priority feature while briefly mentioning a high-priority one

---

## Running evals

### One-shot (single task)

```
Use the eval agent to grade this mapper output against task mapper-completeness-001
```

### Full suite

```
Use the eval agent to run the full mapper eval suite (8 tasks, 3 trials each)
and report pass@1 and pass^3
```

### Regression check before pipeline change

```
Run all 14 regression tasks (3 trials each) and compare against the latest baseline.
Flag any score drops > 0.05.
```

### Capability hill-climb

```
Run all 21 capability tasks (3 trials each).
Report overall scores per stage and highlight the 3 lowest-scoring tasks.
```

---

## Baseline tracking

After each significant pipeline change (prompt update, template change, agent definition change), run the full suite and save results:

```
evals/baselines/2026-05-29-baseline.md
```

---

## Eval health checks

### Saturation watch
When any capability eval hits >95% pass@1 across 3 consecutive runs, graduate it to the regression suite and write a harder replacement.

### False signal watch
When a task has 0% pass@100 (fails every single time across many trials), it's probably a broken task or grader. Investigate before blaming the agent.

### Grader calibration
Every 2 weeks, have a human review 10 random model-based grader outputs. If human and model disagree on >20% of judgments, recalibrate the rubric.
