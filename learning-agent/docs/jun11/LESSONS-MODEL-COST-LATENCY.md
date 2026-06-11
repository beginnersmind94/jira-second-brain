# Model, Cost & Latency — Lessons for PMs Integrating This Engine

**Audience:** PMs putting the grounding engine into their own products.
**Status:** draft for the Jun 11 stakeholder review. ~1.5 pages.
**Author:** Rahul (the short doc promised to the PM team).

> **Sourcing note (read first — no invented numbers).** Every number below is pulled
> from a real run artifact or a `file:line`, cited inline. The promised-doc reference
> ("Jun4 [08:34]") points at a PM meeting transcript that is **not in this repo** — I
> searched `raw/transcripts/` and the whole tree; the only transcripts present are
> *training-content* recordings (Item Management, Eligibility, Inventory), not a record
> of the PM meeting, and none contain an `[08:34]` mark. So I cannot cite the meeting
> verbatim and have not fabricated a timestamp. The closest meeting artifact,
> `jira-brain/wiki/training/meeting-decision-1-pager.md`, is a decision-framework aid,
> not a transcript. Everything here is grounded in the code and run logs instead.

All cost/latency figures come from one measured run unless noted:
`eval/runs/20260603T183555Z/report.json` — module **Item Management**, **k=2 trials/format**,
fixture `item-management-fixture.json` (**4,977 tickets**, per `demo_run_D.log:1`),
model `claude-sonnet-4-6`.

---

## 1. Model selection: we run one model, on purpose

The whole pipeline runs **`claude-sonnet-4-6`** — planner, section writers, and the
single-query path alike (`demo_d.py:330`, `demo_d.py:489`; `demo.py:431`, `:486`, `:532`).
`pricing.py:7-11` carries rate cards for **Opus 4.8** and **Haiku 4.5** too, but **neither
is wired into a generation path today** — they exist so cost math is ready if we tier later.

**Lesson for your product:** you do **not** need a frontier-tier model on the hot path here.
The differentiator is the *architecture* (Section 4), not raw model horsepower — so default to
the mid-tier (Sonnet) and reserve Opus for a measured reason. The one place a cheaper model is
already designed in is the **edit-triage router**, which CLAUDE.md specs as **"Haiku-class or a
rule"** precisely because it is a classifier, not an author (`learning-agent/CLAUDE.md`, Human
Review section, point 3). Match model cost to task openness: author with Sonnet, route with Haiku,
validate with code (free).

## 2. "Max effort isn't always best" — the finding that shaped the design

This is the counter-intuitive lesson worth carrying into your own integration. Two measured data
points, both grounded:

- **More reasoning made it *slower without helping*.** Bounding output made derivations faster but
  made the long-form *slower* (582s); telemetry showed the long-form emitted **31,428 output tokens
  of which only ~6,000 were visible text** — the other ~25,000 were invisible reasoning
  (`docs/CASE-STUDY-learning-studio.md:79`). "Slow" was not "writes too much," it was "thinks a lot,
  invisibly." You cannot fix what you mis-measure.
- **Lower effort *broke grounding*.** Dropping to `effort=medium` cut the long-form to 412s **but
  introduced paraphrasing, which broke verbatim citations** (`CASE-STUDY:81`; ladder row
  "+ enforce + medium effort," 671s, "0 verbatim / paraphrase leaked," `CASE-STUDY:197`). Speed and
  grounding were in **direct conflict** at that point.

The resolution was **not** a better effort setting — it was removing the model's ability to get the
quote wrong at all (Section 4). The shipping config sits at `effort="medium"` everywhere
(`demo_d.py:331`, `:489`; `demo.py:434`) **because** the architecture, not the effort dial, now
guarantees fidelity. The section writer comment says it outright: *"reshape-only; tokens carry the
grounding"* (`demo_d.py:487`).

**Lesson for your product:** treat reasoning-effort as a latency/quality knob you must *measure per
task*, not crank. If correctness depends on the effort setting, you have a fragile design — move the
correctness guarantee into code so you can run lower effort safely.

## 3. Cost & latency — the real measured numbers

**Cost per guide (one run, k=2 trials each):**

| Format | mean cost/guide | per-trial range | mean words (ceiling) | gate result |
|---|---|---|---|---|
| long-form | **$1.0035** | $0.9621 / $1.0449 | 2,953 (6,000) | PASS |
| micro-guide | **$0.7146** | $0.7266 / $0.7026 | 1,055 (1,500) | PASS |
| tldr | **$0.4968** | $0.4807 / $0.5128 | 835 (500) | **FAIL (length only)** |
| **Run total (6 generations)** | | | | **$4.4297** |

Source: `report.json:191-192, 406-407, 621-622, 658`. This is the "$4.43 two-trial run" — it is
**six generations** (3 formats × 2 trials), so the headline single-guide figure is **~$1 for a
full long-form** (CASE-STUDY Outcomes row: "~$1/long-form," `CASE-STUDY:186`).

**Where the cost actually goes — cache, not fresh input.** Long-form trial 1:
**input 43 tokens, output 28,659, cache_read 357,856, cache_write 113,262** (`report.json:90-94`).
Output and cache dominate; raw input is a rounding error. The pipeline is **decode-bound and
cache-heavy**, which is the single most important fact for anyone forecasting cost at scale.

**Latency — the planner is the long pole, not the writing.** Per-stage, from the same run:

| | plan (research) | sections (write) | total |
|---|---|---|---|
| long-form t1 | 133.5s | 117.6s | **251.2s** (`report.json:67-69`) |
| long-form t2 | 113.9s | 148.0s | **261.9s** (`report.json:152-154`) |
| micro t1 | 112.0s | 85.0s | 197.0s (`report.json:282-284`) |
| tldr t1 | 97.4s | 40.1s | 137.5s (`report.json:497-499`) |

A separate run log shows the plan stage as high as **197s** of a 343s total (`demo_run_D.log:7`).
The ADR names this explicitly: *"planner research is now the long pole (~115–197s) — cache ticket
reads next"* (`ADR-001:70`). Sectioned + parallel writing is what killed the old truncation/slowness
(829s baseline → ~260s, `ADR-001:20`, `CASE-STUDY:198`).

**Two latency caveats your integration must plan for, both flagged by the team, neither yet built:**
- These timings ran against a **frozen fixture, not live Jira.** Live Jira "adds latency, rate
  limits, failures the fixture hid (needs cache + retry)" (`ADR-001:69`). Budget for it.
- A ~4-minute generation **must become an async job** (queue + status), not a blocking request
  (`ADR-001:69, :83`). Don't put this behind a synchronous HTTP call in your product.

**Lessons for your product:** (1) budget **~$1/long-form, ~$0.70/micro, ~$0.50/tldr** as a Sonnet
baseline, and recheck once live Jira and any retries are added. (2) Your **cost lever is caching**,
not prompt trimming — input tokens are already negligible. (3) Your **latency lever is the
research/planning stage**; cache ticket reads before you optimize the writer. (4) Design the UX for
a multi-minute async job from day one.

## 4. The architecture lesson: deterministic gate over LLM judge (cheaper *and* more correct)

The trust guarantee is **not** a smarter or more expensive model — it's that the section writer
**emits only `[CITE:id]` markers with `tools=[]`** and a deterministic assembler renders the exact
quote + tier from a registry built from Jira (`demo_d.py:333-335`; CASE-STUDY DP6, `:91-98`).
Mis-citation is **structurally impossible**, verified 0/0/0 across all six trials in the run
(`report.json` G1/G2/G3, e.g. `:24, :31, :38`).

Critically for cost: we **tried an LLM evaluator and demoted it.** It threw a **false negative and a
false positive** while the deterministic check was right both times (`ADR-001:39`;
`CASE-STUDY:106-110`; `STATE-OF-EVAL:58`). The decision: *"For provenance — an exact, checkable
property — a string match against ground truth beats an LLM, and is cheaper and reproducible"*
(`CASE-STUDY:110`). The deterministic gate is the **publish authority**; the LLM judge is
**advisory only** (`ADR-001:39, :84`). The regression suite that pins this is **15/15, zero LLM,
runs in seconds** (`report.json:736-741`).

**Lesson for your product:** for any property you can check exactly (provenance, schema, format
limits), a **deterministic check is the gate** — it is free, reproducible, and was empirically more
correct than the model judge here. Spend LLM calls only on the genuinely open-ended part. This also
*removes* a recurring per-run cost (no judge call) instead of adding one.

## 5. What is NOT yet measured (so you don't over-claim)

- **Live-Jira cost & latency** — every figure here is against a cached fixture; live adds
  latency/retries (`ADR-001:69`). **To be measured.**
- **Multi-module cost** — only **Item Management** has been run; a second-module fixture doesn't
  exist yet (`STATE-OF-EVAL:81`, open-q #5). Cost may vary with module size. **To be measured.**
- **Opus/Haiku in practice** — rate cards exist (`pricing.py:9-10`) but **no generation path uses
  them**; any "Opus would cost X" is a projection, not a measurement.
- **k=2 is thin** — the spec default is **3 trials** (`EVAL-SPEC.md:44`); these costs are 2-trial
  means and will shift slightly at higher k.
- **Edit-triage router cost/latency** — specced, advisory, **no `--live` calibration run yet**
  (`EVAL-SPEC.md:102`; CASE-STUDY DP11). Its whole point is to keep latency *off* the common
  stylistic path — unmeasured today.

---

### One-paragraph takeaway for the PM team

Run the mid-tier model (Sonnet), not a frontier one — the moat is the **ground-by-construction**
architecture, not horsepower. **Max effort isn't best**: more reasoning was slower-and-invisible and
*lower* effort broke citations, so we moved the correctness guarantee into deterministic code and run
a modest effort setting safely. A full long-form costs **~$1** and takes **~260s** today, the cost
is **cache- and decode-dominated** (input tokens are negligible), and the **planning stage is the
latency long pole**. A **deterministic gate beat the LLM judge on both correctness and cost** — use
exact checks wherever the property is exactly checkable, and reserve model calls for the open-ended
part. Everything is measured on a cached single module at k=2; **live Jira, multi-module, and higher
k are still to be measured** — don't quote scale-readiness yet.
