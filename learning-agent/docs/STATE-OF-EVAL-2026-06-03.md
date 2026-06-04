I have all four structured inputs (MEASURE, RIGOR, READINESS, GENERALIZATION). This is a synthesis-and-writing task; the data is self-contained, so I'll write the report directly.

# State of the Eval & Demo — PM Readiness Report

> **Addendum (2026-06-04):** A human review gate shipped after this report — the deterministic grounding gate is now the *machine* floor, and **human approval is the gate into the Library** (drafts aren't shown until approved). Reviewers can request **AI-assisted edits**; the grounding gate re-runs after every edit (so edits can't weaken grounding), and an **advisory edit-triage classifier** routes stylistic vs substantive. This sits *downstream* of the generator, so it does not change the scorecard below. New eval gap: the triage classifier needs its **own balanced eval** (under-trigger rate is the dangerous direction) — see `eval/EVAL-SPEC.md` §7 and open-q #7.

## 1. Executive Verdict

The demo is **ready to show** and the grounding architecture is genuinely well-engineered, but the eval suite proves far less than its green dashboard suggests: it validates one happy path (one module, one fixture, code-graders only) and has **no hill to climb**. The single biggest risk for the incoming transcript is **silent wrong-module grounding** — if the new transcript is *not* Item Management and the presenter doesn't capture a fixture first, the system can emit confident, verbatim-cited, all-PASS output that quotes the *wrong feature's* tickets. The gate will say green and be wrong. Treat any new-topic transcript as a different-module case until proven otherwise, and complete the pre-flight in Section 5 before showing it live.

## 2. Measured Scorecard

Run: `eval/runs/20260603T183555Z` · trials/format **k=2** · fixture: `item-management-fixture.json` (module *Item Management*, 4977 tickets).

**Regression: 15 / 15 PASS** (deterministic, zero-SDK, exit-code gated).

| Format | pass@k | pass^k | partial | tier_lie | quote_not_found | invalid_cite_id | mean words (ceiling) | cost (2 trials) |
|---|---|---|---|---|---|---|---|---|
| long-form | 1 | 1 | 1.00 | 0 | 0 | 0 | 2953 (6000) | $2.0070 |
| micro-guide | 1 | 1 | 1.00 | 0 | 0 | 0 | 1055 (1500) | $1.4292 |
| tldr | **0** | **0** | **0.833** | 0 | 0 | 0 | **835 (500)** | $0.9935 |
| **Total** | | | | | | | | **$4.4297** |

Per-trial cost means: long-form $1.0035, micro-guide $0.7146, tldr $0.4968.

**Reading the numbers honestly:**
- **tldr fails both trials on length only (G6).** G1–G5 (grounding, density, section-fit) PASS in both trials; words ran 877 and 794 vs a 500 ceiling — **~1.6–1.75× over**. This is a real, reproducible length-control regression in tldr generation, **not** a grounding failure. The run notes correctly diagnose it as such (a textbook "0% = look closer, is it the task or the grader?" call, done right).
- **Grounding invariants are 0/0/0 across all 6 trials — but "by construction."** On the cell_d path the model has no channel to type a tier or quote, so 0 here is what the architecture *forces*, not evidence the model *chose* correctly. See Section 4.
- **Two formats at 100% + 15/15 regressions = saturation signal**, not a quality trophy. No improvement signal remains.

## 3. Eval-Suite Rigor vs Anthropic's Standards

**Overall: adequate.** Strong code-grader foundation; the other two grader families and the balanced task bank don't exist yet.

**Met:**
- **pass@k vs pass^k done correctly.** Publish-blocking graders (G1/G2/G3/G5/G6) gated on pass^k; capability/density (G4) on pass@k. Both columns reported per format.
- **Grade outcomes, not path.** Graders read the final artifact dict, never the tool-call sequence.
- **Partial credit implemented** (tldr correctly scores 0.833 = 5/6, not 0).
- **0%/100% diagnosis is exemplary** — tldr's 0% correctly identified as a real length regression with grounding intact.
- **cell_d "0 by construction" labeled honestly** as an invariant, not a skill measure; anti-circularity enforced in code (enforce_citations never in the grade path).

**Partial / Missing (the gaps that matter):**
- **One-sided task set.** `capability.py` runs **no should-not-occur task**. Every balanced pair specced in EVAL-SPEC sec 2 (CAP-09 flag planted conflict, CAP-10 hedge DESC-only claim, CAP-14 drop un-citable specifics) is **TODO**. Per Anthropic: *"one-sided evals create one-sided optimization."* A grader that passes by *always emitting citations* would not be caught today.
- **The "capability" suite isn't a capability eval.** It re-runs the 3 production formats and grades happy-path quality — a saturated regression check, not a low-pass-rate "can it ever" bank that exercises model judgment.
- **Model-based (G7/G8) and human (G9) grader families are entirely deferred/uncalibrated.** No labeled calibration corpus exists. **Coverage and source-quality — the core of research-agent eval — are unmeasured.** G1–G6 only validate that *emitted* citations are well-formed; they never check what the guide **omits** or whether it covers the facts a good guide must include.
- **Task count far below the 20–50 floor:** effectively 3 formats × 1 transcript × 1 module.
- **k=2 is underpowered** for a customer-facing publish gate (spec default is 3; Anthropic recommends more). At k=2 a 75%-reliable behavior still shows clean pass^k ~56% of the time by luck.
- **No transcript-reading discipline and no saturation watcher** wired in.

**Top 3 rigor gaps:** (1) unbuilt balanced/should-not set; (2) saturated suite with no improvement signal; (3) no live, calibrated semantic/coverage grader.

## 4. System Readiness

**Grounding guarantee — PARTIALLY TRUE, with a precise boundary.** "Tier-lie and quote-not-found impossible by construction" is **real and well-engineered** for the failure mode it targets: the section writer runs with `tools=[]`, is forbidden from typing quote/tier text, and can only emit `[CITE:id]`; `assemble._render` renders tier+span from the registry, never from the model. The model has **no channel** to introduce a tier-lie or non-verbatim quote, and the only model-causable failure (invalid_cite_id) is caught by G3 (measured 0/6).

The honest caveat (the team documents it themselves, EVAL-SPEC open-q #2): **the grounding gate and the registry share one ground truth (`demo._FIX`).** The invariant proves the *plumbing* is intact — it does **not** verify the fixture's field-to-tier mapping is correct. If capture wrote AC text into the desc field, the registry would mint a confidently-wrong-but-self-consistent citation and **every grader would still pass.** So: *"the model cannot introduce a tier-lie"* — **not** *"a tier-lie cannot exist."* It is a plumbing-integrity invariant anchored to fixture trust, not an end-to-end provenance proof.

**Strengths:** grounding-by-construction is architectural (not prompt-hope); deterministic gate as publish authority with LLM correctly demoted to advisory (the ADR records the LLM grader threw both a false-pos and false-neg while the deterministic gate was right); regression suite robust; cost measured for real ($4.43); demo isolation real (prod files untouched, no Jira network at showtime).

**Weaknesses:** single-fixture generalization gap (dominant risk); invariant anchored to fixture trust; tldr length broken; G4 density floor and 0.9 ok-ratio thresholds asserted not calibrated; k=2 thin power; no live semantic check (a verbatim, correctly-tiered citation can still be **contextually misleading** and pass).

**Demo-ready: YES. Prod-ready: NO.** Production path (`tools_sdk.py`/`agent_sdk.py`) is explicitly untouched and still runs the old buggy single-query generator; none of the ADR Phase 1/2 port (shared core, live-Jira source, module filtering, async/retry/cache, secrets out of `.env`, revert bypassPermissions) is done.

## 5. ⚠️ PRE-FLIGHT FOR THE NEW-TOPIC TRANSCRIPT — READ BEFORE YOU LOAD IT

**This is the section that protects the demo. Do not skip it.**

**What will actually happen depends entirely on the module:**

- **If the new transcript is STILL Item Management** → it works as designed. `_load_fixture` finds the one present fixture, `parse_transcript` reads your new transcript for real, lexical `match_tickets` surfaces genuinely on-topic tickets, and the gate confirms verbatim spans. **This is the validated happy path.**

- **If the new transcript is a DIFFERENT module (a "new topic" almost certainly is), two outcomes:**
  - **(A) No fixture exists for that module** (today's reality — only `item-management-fixture.json` is present): the run **dies loudly** with `SystemExit` ("Run demo_capture.py first", demo.py:86–91). Nothing generates. **This is the SAFE failure** — embarrassing live, but honest.
  - **(B) ⚠️ A wrong-module fixture is loaded** — e.g. `--module` defaults to "Item Management" while you upload a Production Orders transcript: **THE DANGEROUS SILENT FAILURE.** `match_tickets` **does not filter by module** (the module arg is only cosmetically interpolated into a display-only JQL string, demo.py:186); it lexically scores across the loaded Item Management tickets. A Production Orders query returns whatever Item Management tickets share generic words ("item", "create", "save", "status"). The citations point at **real, verbatim, correctly-tiered Item Management spans about the WRONG feature.** The grounding gate **STILL PASSES** — tier_lie=0, not_found=0, invalid_cite_id=0, all-PASS — because the gate has **no notion of module relevance.** The LLM evaluator can't catch it either; it reads from the same wrong fixture. This is a citation-unfaithfulness hallucination that looks fully grounded — exactly CLAUDE.md's "cross-feature pattern matching" failure.

**The failure mode in one line:** the gate proves the quote is verbatim and correctly-tiered; it does **NOT** prove the quote is about what the sentence claims.

**EXACT setup required before a new module can ground (do this ahead of time, with LIVE Jira reachable):**

1. **Confirm the transcript's module** and get the EXACT Jira "Module" custom-field value (correct casing/spacing — the JQL is an exact match; a typo returns 0 issues and writes an empty fixture).
2. **Check for the fixture:** `ls data/demo/` — confirm a `<module-slug>-fixture.json` exists for THAT module. (Today only `item-management-fixture.json` is present.)
3. **If missing, capture it:** `python demo_capture.py --module "<Exact Jira Module value>"` — prerequisites: active venv, `.env` with valid Jira creds (`_basic_auth` not None), network to `JIRA_BASE`. Confirm it printed `wrote N tickets + M epics` with **N > 0** (N=0 means the module value was wrong).
4. **Verify the fixture:** open it; confirm top-level `"module"` equals the intended module and ticket summaries are on-topic. (Guards against empty/typo capture.)
5. **At showtime pass the flag explicitly:** `python demo.py --module "<module>" --transcript <path>` (or `demo_d.py ... --format long-form`). The `--module` MUST equal the captured module. **Never let `--module` default to "Item Management"** — that is the silent wrong-module trap.
6. **After the run, do NOT trust the all-PASS gate for module correctness** — eyeball the rendered `<!-- Source: [[NXT-####:TIER]] -->` citations and the Sources section to confirm the cited ticket keys/summaries are actually about the transcript's feature. The gate cannot detect wrong-module citations.
7. **Keep fixtures module-scoped.** `match_tickets` won't filter for you; rely on demo_capture's JQL to keep other modules out. Never hand-merge modules into one fixture.

**Bottom line for the PM:** if you cannot run the live capture in step 3 before the demo, **keep the demo on Item Management.** A new-topic transcript without a matching fixture either crashes (safe) or grounds against the wrong feature while showing all green (worst case).

## 6. Top 3 Things to Fix Next (Ranked)

1. **Add real module filtering to `match_tickets` + capture a second-module fixture.** This is the dominant risk and the one that can embarrass the demo silently. Filtering by the module arg turns the dangerous silent failure (B) into the safe loud failure (A); a second fixture is the only way to get *any* cross-module evidence. (Open-q #5, ADR Phase 2.)
2. **Build the balanced should/should-not capability tasks** (CAP-09 flag planted conflict, CAP-10 hedge DESC-only claim, CAP-14 drop un-citable specifics). These exercise model **judgment**, will start well below 100% (giving a real hill to climb), and are the only tasks that would catch a grader that passes by always citing. Fixes the one-sided-optimization gap directly.
3. **Fix tldr length control** (deterministic post-trim or tighter section budget) and **raise default trials to ≥3**. tldr is not shippable at 1.6–1.75× the ceiling; k=2 is too weak a reliability claim for a customer-facing publish gate.

*Deferred but on the radar: stand up and calibrate G7/G8 against a labeled corpus (no live semantic/coverage check exists — a fully grounded guide can still be contextually misleading), and add a transcript-review + saturation-watch discipline.*