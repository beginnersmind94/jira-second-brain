# Eval method — bank freshness / drift on ICN re-import

*Method spec for NEXT-EVALS-PLAN item #5 ("Drift / bank-freshness"). Production-observability
layer. **Plan only — nothing in this spec is built yet.** It specifies a runner that does not
exist; every "today" claim below is grounded in code that is present, every "would" / "proposed"
claim describes what must be added. Read `docs/NEXT-EVALS-PLAN.md` §5 and the dominant-risk
note in this area's audit first.*

---

## 0. The risk this measures, stated plainly

**Stale-but-green on an already-committed bank.** Once a question is banked, no code path
re-reads it and re-grades it against the source. Concretely, today:

- The bank is append-only and `committed` is terminal — `qbank_curation.py:37`
  (`TERMINAL = (REJECTED, COMMITTED)`), `append_bank` at `:86-88`, `commit_to_bank` sets
  `COMMITTED` at `:193`. There is **no** function that reads a banked item back.
- The only live re-validation is at **human approval** of a *draft* — `demo_app.py:1558`,
  `validate_citations(... transcript_text=_transcript_text_for(meta))`, re-run against the
  **current fixture/transcript**. It fires for a draft being approved, never for items already
  in the bank.
- The gate's verbatim check (`qbank_gate.py:46-48`, `nq in _norm(span['text'])`) resolves
  against an **immutable** source span: for the transcript path the registry is built from
  `transcript_text` (`demo_app.py:958` → `demo_d.build_transcript_registry`, `demo_d.py:129-141`),
  which is immutable by directory rule (`CLAUDE.md`: *"the transcript is an immutable source"*);
  for the Jira path, the captured fixture. **Neither is the re-imported ICN corpus**
  (`data/icn/chunks/chunks.jsonl`).
- Triage's `support_ok` is a **generation-time** signal (`qbank_curation.py:113` docstring,
  consumed at `:123`); it is recorded once and never recomputed.

So after the **first re-import that follows a populated bank**, every banked question stays
green — its quote is still a verbatim substring of its frozen span, and `support_ok` is whatever
it was at generation — while the meaning of the surrounding ICN content may have shifted. **A
wrong fact ships under a passing gate.**

This is not hypothetical drift in the abstract: re-imports are **silent overwrites** that
materially change the corpus. `data/icn/data/ingestion_log.md` records `chunks.jsonl` at
**723 chunks** (`:110`, `:115`, `:119`) and then **1970 chunks** (`:323`, `:327`) inside one
session. And `data/icn/data/asset_manifest.csv` has **no content-hash or version column** — its
header (`:1`) is:

```
asset_id,title,source_org,source_url,source_page_url,asset_type,file_format,license_posture,local_path,thumbnail_path,downloaded,llm_ingestion_allowed,roles,topics,attribution_text,notes
```

— so today there is not even a way to *detect* that a re-import changed an asset's content. No
`.py` reads `chunks.jsonl` or the manifest for freshness; `curator_walkthrough.py:27` reads
`chunks.jsonl` only as a *generation* source.

**Latency caveat (important for scoping):** `data/qbank/` contains only
`adversarial_fixture.json` — **`bank.jsonl` does not exist on disk yet.** So this is a *latent*
risk. It detonates on the **first re-import after the bank goes live** — precisely the moment no
one is looking. This spec should be built *before* a real bank is committed, not after the first
stale-but-green incident.

---

## 1. What the metric is (and is not)

**Primary metric: `% still true`** — the fraction of the live bank whose grounding still holds
against the **current** ICN corpus, recomputed end-to-end on each re-import.

> **Note (synthetic):** every count, rate, and threshold below that is not a code citation is a
> proposed default for an unbuilt runner. They are starting points to calibrate, not measured
> results. There are zero real drift runs to date.

The metric is **end-state meaning, not byte-equality.** A hash sitting still does not mean the
fact is still true:

- **Byte-equality is necessary but not sufficient.** A quote can remain a verbatim substring of
  *a* chunk while the chunk it was lifted from was renumbered, merged, split, or moved next to a
  contradicting sentence by the re-import. Verbatim-still-passes against a stale or relocated span
  is exactly the failure `qbank_gate.check_verbatim` cannot see — it only asks "is this string in
  this span's text," not "is this still the right span, and does it still mean what the question
  claims."
- The inversion class the semantic judge exists to catch (`qbank_gate.py:14-18`: *"held at 135°F
  or higher" is a MINIMUM; a stem asking the MAXIMUM with answer "135°F" is verbatim-true yet
  semantically false*) is **meaning-level**. Drift can introduce exactly this: a re-import adds a
  qualifier, a "maximum," an exception, or a superseding standard near the quoted text, and a
  question that was supported becomes unsupported **without its quote changing one byte**.

So `% still true` is computed from **two** recomputations, not one:

| Sub-check | Mechanism | Lane | Cost |
|---|---|---|---|
| **(a) Verbatim re-resolution** — whole bank | deterministic: re-key every banked quote to the *current* `chunks.jsonl`; confirm it is still a verbatim substring of a chunk of the **same lane** | canonical/deterministic | free |
| **(b) Semantic-support re-grade** — sampled | LLM-judge (`qbank_gate.llm_support_judge`) re-run on a sample of items that *passed* (a): does the quote still support stem+answer **given the current neighborhood**? | advisory (method = LLM-judge) | metered |

`% still true` is reported per sub-check and combined: an item is "still true" only if it passes
(a) and — if sampled — (b). Items that fail (a) are hard drift; items that pass (a) but fail (b)
are meaning drift; the sample's (b) failure rate is **extrapolated** to the un-sampled remainder
as an *estimated* meaning-drift rate (with its sampling interval), never reported as exact.

**What it is not:** it is not a generation-quality score, not a coverage score (that is item #4),
and not a pass/fail publish gate on its own. It is an **observability** signal that **triggers
human re-review** (§5). The deterministic sub-check (a) *can* be a hard gate; the LLM sub-check
(b) is advisory by the project's lane discipline (`NEXT-EVALS-PLAN.md` §framing: *"LLM-as-judge
is a method, not a metric… validate it against human labels before trusting it"*; the ADR records
the LLM grader throwing both a false-positive and a false-negative — `STATE-OF-EVAL-2026-06-03.md`
§4).

---

## 2. The snapshot / checkpoint mechanism

The drift run needs a **stable thing to diff against**. Today neither half of the diff exists as a
durable artifact: the corpus is overwritten in place (§0) and `bank.jsonl` is absent. Two
artifacts must be added.

### 2.1 Corpus checkpoint (the "what the bank was grounded against" snapshot)

On every ICN ingest/re-import, before overwriting `chunks.jsonl`, freeze the prior corpus and
record a content hash:

- **Per-chunk content hash.** Add a `text_sha256` to each chunk record (and/or an extraction-wide
  `corpus_sha256`). The current `chunk_id` (`icn-...__p001__c001`, confirmed by direct read) is a
  *position* id — page+chunk index — **not** content-derived; it stays identical when the text
  under it changes. The hash is what makes "the meaning moved" detectable at all. This directly
  parallels jira-brain's guide layer, which records `raw_text_sha256` in `.raw.md` frontmatter and
  anchors curation to `curated_against_raw_sha` (see jira-brain `CLAUDE.md` → Guide Layer).
- **Manifest version column.** Add a content-hash/version column to `asset_manifest.csv` (its
  header has none today, `:1`). This is the per-asset analog of jira-brain's manifest
  `raw_text_sha256` + `drift_status` columns.
- **Checkpoint directory.** Write `data/icn/snapshots/<import-id>/chunks.jsonl` (+ a small
  `import.json`: import-id, timestamp, chunk count, corpus hash, asset→hash map). `import-id` is a
  monotonic timestamp, e.g. `20260605T132328Z`, derived from the ingest run. This mirrors
  jira-brain's `raw/guides/snapshots/<GUIDE-ID>.raw.md` as the drift baseline.

> **Why not reuse `chunk_id`:** because it is positional. A re-import that re-paginates an asset
> (723→1970 chunks is exactly this scale of change) reshuffles `__pNNN__cNNN` wholesale. Keying
> drift to `chunk_id` would either spuriously flag everything (ids moved) or silently match the
> wrong chunk (id reused for different text). The content hash + a re-resolution step (§3) is what
> survives re-pagination.

### 2.2 Bank checkpoint (the "what we are auditing" snapshot)

Each banked item must record, at commit time, **the exact source it was grounded against** — so a
later re-import can ask "is *this specific evidence* still here and still meaning the same thing."
Extend the committed item (`commit_to_bank`, `qbank_curation.py:181-199`) to carry a frozen
provenance block:

- `cite_chunk_id` (the position id at commit time), **and** `cite_text_sha256` (content hash of
  the chunk text it was grounded against), **and** `corpus_import_id` (which import produced that
  chunk). The quote itself is already on the item (`quote`); `committed_at` already exists (`:194`).

This is the only change to the bank schema, and it is **additive** — it does not touch the
append-only / terminal-state guarantees (`qbank_curation.py:14-18`, `:37`). It records provenance;
it grants no new write path.

> **Caveat — the gate↔registry path is not the curator-walkthrough path.** `qbank_gate.gate_question`
> takes `cite_span_id` + `spans_by_id` (`qbank_gate.py:77,82`), i.e. the registry shape
> (`demo_d.build_transcript_registry`). The standalone `curator_walkthrough.py` probe keys its
> generated questions to `chunk_id` from `chunks.jsonl` (`:27`, `_load_topic_chunks` at `:71-85`)
> and does **not** go through `commit_to_bank`. The drift runner must record **both** keys so it
> works regardless of which ingestion path actually populates the live bank. Do not assume the
> ICN/chunk path and the registry/span path are interchangeable — they are two different keyings of
> "the source," and the bank's provenance block must pin whichever one was used.

---

## 3. The drift run (what executes on each re-import)

Input: the **new** `chunks.jsonl` (post-import) + its checkpoint, and the live `bank.jsonl`.

**Step A — Verbatim re-resolution across the WHOLE bank (deterministic, free).**
For every banked item:
1. Re-key its quote to the **current** corpus: find the current chunk(s) whose text contains the
   quote as a verbatim substring, using the same normalization as the gate (`qbank_gate._norm`,
   `:28-29`) so this is identical to what the gate would compute now — not a new matcher.
2. Enforce **lane** on the resolved chunk exactly as the gate does (`qbank_gate.check_lane`,
   `:37-43`; lane is the first `:`-segment of the span id, `lane_of_span_id` `:32-34`). A quote
   that now only matches a chunk of the *other* lane is a **cross-lane re-resolution** — treat as
   drift, never as a pass. This is the freshness analog of the gate's purity backstop.
3. Classify the item:
   - **`still_verbatim_same_evidence`** — re-resolves to a current chunk whose `text_sha256`
     equals the banked `cite_text_sha256`. The evidence is byte-identical and still present.
   - **`still_verbatim_moved`** — re-resolves verbatim, same lane, but the hash differs (text
     around it changed, or it landed in a renumbered/merged chunk). **This is the dangerous
     stale-but-green class** — green to the old gate, but the neighborhood moved. Must flow to (B).
   - **`broken`** — no current same-lane chunk contains the quote verbatim. Hard drift; the source
     the bank cites is gone or rewritten.

**Step B — Sampled semantic-support re-grade (LLM-judge, advisory, metered).**
Re-run `qbank_gate.llm_support_judge(quote, stem, correct_answer)` (`qbank_gate.py:51-74`) — the
**same** judge the live gate uses, so this measures the gate's own criterion, not a new one — on:
- **100%** of `still_verbatim_moved` items (these are precisely where meaning can shift silently
  — do not sample these down), **and**
- a **sample of `still_verbatim_same_evidence`** items (§4 rate). Even byte-identical evidence can
  flip if the import added a contradicting/qualifying chunk the question never cited but a reader
  would now see; the sample bounds that residual risk cheaply.

Feed the judge the quote **as re-resolved in the current corpus** (and, if a context window is
adopted, the current neighboring chunks), so it grades *today's* meaning, not the frozen span.

**Step C — Report `% still true`, sliced (§6), and route (§5).** Append every per-item verdict to
a `drift_log` (one JSON line per item per run: `import_id`, `item_id`, both cite keys, class,
verbatim_ok, support_ok|null-if-not-sampled, reason). This is the drift sibling of the planned
`gate_log` (`NEXT-EVALS-PLAN.md` §6) and lets a later run diff *trends* across imports.

**Lane order is preserved end-to-end:** deterministic re-resolution (A) gates first and runs on
everything for free; the LLM judge (B) runs only on what A surfaces. This is the same
cheap-deterministic-first / metered-LLM-second discipline as the live gate (`qbank_gate.py:20-21`)
and the canonical-vs-advisory split (`NEXT-EVALS-PLAN.md` §framing). The drift run **reuses
`graders.py` and `qbank_gate.py` unchanged** — it changes *what source the verdict is resolved
against* (current corpus, not frozen span), not *how* a verdict is computed. No trajectory or
step assertions are introduced (audit C01: keep the artifact-grading shape).

---

## 4. Sampling rate

Sub-check (a) is **100% of the bank** — it is free (no model calls) and deterministic, so there is
no reason to sample it.

Sub-check (b) is metered (one LLM call per item) and is sampled. Proposed policy (synthetic
defaults — calibrate against the first real bank + the judge-calibration work in
`JUDGE-CALIBRATION-PLAN.md`):

- **Census, not sample, of the dangerous class:** **100%** of `still_verbatim_moved` items get a
  (b) re-grade. These are the stale-but-green candidates; sampling them down defeats the purpose.
- **Stratified sample of `still_verbatim_same_evidence`:** start at **20%** per stratum, with a
  **floor of 30 items per stratum** for any stratum with ≥30 items (so a small topic isn't
  estimated from 2 items), capped by a per-run **judge-call budget** (e.g. 300 calls) so cost is
  bounded and predictable. Strata = the slices in §6 (lane × topic, and `corpus_import_id`).
  - **Sensitive topics are a forced stratum at 100%.** Any banked item whose topic matches
    `TriageConfig.sensitive_topics` (`qbank_curation.py:59-60`: allergens, anaphylaxis, medical,
    choking, religious dietary law, student PII) is re-graded in full, never sampled down — the
    same asymmetry triage already encodes (a sensitive item always routes to a human, `:121-122`).
- **Report the sampling interval, not just the point estimate.** The extrapolated meaning-drift
  rate for the un-sampled remainder carries a confidence interval; the dashboard shows it as a
  range. A point estimate from a 20% sample reported as exact would be its own small dishonesty.

The dangerous direction here is the same as the judge's everywhere in this project: **a false
negative** — the re-grade says "still supported" when meaning has drifted. So the sample is
weighted *toward* the classes most likely to have flipped (moved evidence, sensitive topics), and
(b) is explicitly **advisory** until the judge is calibrated (`JUDGE-CALIBRATION-PLAN.md`); an
un-calibrated judge passing a drifted item is exactly the failure mode that calibration must bound
before (b) is trusted to *clear* an item rather than only to *flag* one.

---

## 5. What triggers a human re-review

The drift run **flags; humans decide.** It must never auto-mutate the bank — the bank is
append-only and committed is terminal (`qbank_curation.py:37`), and there is no
un-commit/edit-in-place path by design. The correct mechanical response to drift is **flag +
quarantine-from-serving**, decided by a human, mirroring the human-approval gate that is the only
way into the Library (`demo_app.py:1545-1574`; `CLAUDE.md` status-gating: *"the agent never
approves autonomously"*).

A banked item is **flagged for human re-review** when **any** of:

1. **Verbatim broke** — class `broken` (§3 Step A). The cited source is gone or rewritten.
   *Highest severity.*
2. **Cross-lane re-resolution** — the quote now only matches the other lane (§3 A.2). A purity
   violation introduced by re-import.
3. **Evidence moved AND semantic re-grade now fails** — class `still_verbatim_moved` with
   `support_ok == False` from (b). The verbatim-true-but-meaning-false case the gate's semantic
   step exists for (`qbank_gate.py:14-18`), now arising from drift rather than generation.
4. **Sensitive-topic item with ANY (b) failure** — sensitive items (`qbank_curation.py:59-60`)
   fail closed: any support-re-grade NO routes to a human regardless of class. Same asymmetry as
   triage (`:121-122`).
5. **Slice alarm** — an import's per-slice `% still true` drops below a threshold (proposed: any
   lane/topic slice < **98%**, or whole-bank < **99.5%** — synthetic starting points). This
   catches a *systemic* re-import problem (e.g. a re-paginate that broke a whole asset) even when
   no single item looks alarming.

**Routing of a flagged item** (proposed, additive — does NOT weaken the state machine): record a
drift verdict in the existing append-only audit log (`qbank_curation.audit_log`, `:95-99`) with a
`drift_review` event, and surface the item in a **"Drift — awaiting re-review"** queue (the drift
analog of the Library's "Awaiting review" queue). A human then either re-affirms it (it stays
served, audit-logged) or supersedes it with a freshly generated, re-gated item (new candidate →
triage → gate → commit, the normal path). **Serving** of a flagged item is suppressed until a
human clears it — flag-and-quarantine, not silent auto-removal.

> The audit (C01) recommendation lands here: add a drift runner that treats each banked item's
> **current** verdict (re-resolved against the re-imported source) as the outcome to grade, reusing
> `graders.py` / `qbank_gate.py` unchanged — do **not** introduce trajectory or step assertions, and
> do **not** give the runner write access to the bank. It computes verdicts and routes; humans
> mutate state.

---

## 6. How drift slices by import

Every drift verdict is tagged with the `corpus_import_id` of the corpus it was graded against, so
the metric is never a single global number — it is sliced, per the project's
metric-per-component / diagnostic-slice discipline (`NEXT-EVALS-PLAN.md` §framing).

- **By import (primary axis).** `% still true` is reported **per re-import**, as a time series:
  `import_id → {whole-bank still-true %, broken n, moved n, cross-lane n, sample (b)-fail rate ±
  interval}`. A clean import shows ~100%; a problematic one (e.g. the 723→1970 re-pagination class
  of change) shows a step down. This is the "watch for drift on fresh data… slice metrics by
  import to catch decay" instruction made concrete (`NEXT-EVALS-PLAN.md` §data-discipline).
- **By lane** (product / compliance) — a re-import that damaged one corpus lane shows as a
  one-lane drop; pairs with the lane-purity battery (item #2).
- **By topic** (the chunk `topics` tag, e.g. `food_safety`) and **by asset** (`asset_id`) — points
  the human at *which* re-imported asset caused the decay.
- **By drift class** (`still_verbatim_same_evidence` / `still_verbatim_moved` / `broken`) — so the
  cheap-but-dangerous "moved" bucket is always visible separately from the reassuring "same
  evidence" bucket. A dashboard that collapses these would hide exactly the stale-but-green class.

Trend, not snapshot, is the point: a bank that is 100% still-true at import N and 96% at import N+1
is the signal. The `drift_log` makes that diff a query.

---

## 7. Relationship to jira-brain's guide-drift linter (analogy, not inheritance)

jira-brain already has a **working, shipped** drift mechanism for its *guide* layer — and this
spec is deliberately modeled on its shape. But it is an **analogy to adapt, not a feature that
already exists here.** Do not let the parallel imply the learning-agent has drift detection today —
it does not (§0).

What jira-brain does (verified by direct read of jira-brain `CLAUDE.md` + presence of
`scripts/lint_guide_drift.py`):

| jira-brain guide drift (exists) | learning-agent bank drift (this spec — proposed) |
|---|---|
| `raw_text_sha256` in `.raw.md` frontmatter; manifest tracks it | per-chunk `text_sha256` + a manifest version column (§2.1) — **neither exists today**; manifest header has no hash column (`asset_manifest.csv:1`) |
| `raw/guides/snapshots/<GUIDE-ID>.raw.md` = drift baseline | `data/icn/snapshots/<import-id>/chunks.jsonl` = corpus checkpoint (§2.1) — proposed |
| Curated `.md` anchored via `curated_against_raw_sha` | banked item anchored via `cite_text_sha256` + `corpus_import_id` (§2.2) — proposed |
| `lint_guide_drift.py` flips `drift_status: drifted`, writes a side-by-side HTML diff | drift runner classifies each banked item + writes `drift_log`; **no script does this yet** |
| `mark_guide_reviewed.py` — SME closes the loop, refreshes snapshot, clears drift | human clears the "awaiting re-review" queue; re-affirm or supersede (§5) — proposed |

**Two real differences, not cosmetic:**

1. **jira-brain's linter is byte/hash-level on the SME's curated copy; this spec is explicitly
   meaning-level on top of the hash.** jira-brain's "drifted" means *the PDF's raw extraction hash
   changed since last SME review* — a byte signal that prompts a human to *look*. That is correct
   for a human-curated guide. For an automatically-generated, auto-served question bank, a byte
   signal is **insufficient**: the question text never changed (it's banked), only the *world it
   cites* did, and the dangerous case (`still_verbatim_moved`) is one where the **quote's bytes are
   still present** but the meaning around them moved (§1). Hence the mandatory sampled semantic
   re-grade (§3 Step B) layered *on top of* the hash check. jira-brain's linter has no LLM step;
   this one does, because the artifact being protected is different.
2. **jira-brain's caveat is the precedent for why "green" is not "fresh."** jira-brain `CLAUDE.md`
   already warns (Guide Layer → *Citation caveat for wiki use of guides*): *"a wiki page that cites
   a curated `.md` is citing the SME's last-reviewed understanding of that guide… If the manifest
   shows `drift_status: drifted`… treat wiki claims sourced from it as potentially stale."* This
   spec is the same caveat enforced *mechanically* for the bank: a banked question cites the corpus
   as it was at `corpus_import_id`; once a newer import lands, that citation is "last-reviewed
   understanding," and `% still true` is the mechanical re-check the wiki caveat asks a human to do
   by hand.

**Do not overclaim the inheritance.** This spec borrows the *snapshot → hash → diff → human-clears*
**shape** from a sibling repo's guide pipeline. It does **not** reuse jira-brain's code (different
artifact, different corpus, an added semantic layer), and the learning-agent has **no** drift
detection of any kind until the runner in §3 is built.

---

## 8. Build order (smallest first)

1. **Provenance + checkpoint plumbing (no judge, no UI).** Add `text_sha256` to chunks; add the
   manifest version column; write `data/icn/snapshots/<import-id>/`; extend the committed-item
   schema with `cite_chunk_id` / `cite_text_sha256` / `corpus_import_id` (additive only). Until
   this exists, drift is **undetectable** (§0) — this is the prerequisite for everything else.
2. **Deterministic drift runner (Step A only) + `drift_log` + slices (§6).** Free, deterministic,
   reuses `qbank_gate._norm` / `check_lane`. Produces `% still true` from verbatim re-resolution
   alone — already enough to catch the `broken` and cross-lane classes. Can gate.
3. **Sampled semantic re-grade (Step B).** Only after the judge is calibrated
   (`JUDGE-CALIBRATION-PLAN.md`) — until then run it advisory/shadow and compare to human spot
   checks. Adds the `still_verbatim_moved` meaning-drift detection that is the whole reason a
   hash-only check is insufficient.
4. **"Awaiting re-review" queue + audit routing (§5).** The human-clears loop. Mirrors the Library
   approval queue.

A real drift number cannot exist before step 2, and the *meaning* half of "% still true" cannot be
trusted before step 3's calibration. State both honestly on any dashboard until then.
