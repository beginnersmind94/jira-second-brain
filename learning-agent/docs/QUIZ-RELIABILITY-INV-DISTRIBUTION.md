# Quiz reliability — Inventory Distribution guide

*Auto-generated. 10 runs of quiz-from-guide on resource `20260608-155920-inventory-long-form-af5d2c` (n=6 questions/run). Each question auto-checked two ways: the deterministic **grounding gate** (kept vs dropped — verbatim source span present?) and the semantic **support judge** (does the cited quote support the keyed answer?). Elapsed 490.8s.*

## Headline

- Runs completed: **10/10**
- Questions kept (passed grounding gate): **59** · dropped: **1**
- Keyed answers the support judge flagged as NOT supported by their quote: **14**
- **Fully-clean runs (0 dropped AND 0 key-unsupported): 0/10**

## Per-run

| run | generated | kept | dropped | key-unsupported |
|---|---|---|---|---|
| 1 | 6 | 6 | 0 | 1 |
| 2 | 6 | 5 | 1 | 1 |
| 3 | 6 | 6 | 0 | 2 |
| 4 | 6 | 6 | 0 | 2 |
| 5 | 6 | 6 | 0 | 1 |
| 6 | 6 | 6 | 0 | 2 |
| 7 | 6 | 6 | 0 | 1 |
| 8 | 6 | 6 | 0 | 1 |
| 9 | 6 | 6 | 0 | 1 |
| 10 | 6 | 6 | 0 | 2 |

## Flagged: keyed answer NOT supported by its cited quote (judge)

- **run 1** — What makes a site eligible to be linked to an internal vendor in SchoolCafé inventory distribution?
  - keyed: Being assigned the distribution site type
  - judge: NO
The source says the designation makes the site eligible to be linked to an internal vendor, but does not name what that designation is — it does not say "distribution site type.
- **run 2** — What makes a site eligible to be linked to an internal vendor in SchoolCafé Inventory?
  - keyed: The site must be assigned the distribution site type
  - judge: NO
The source says assigning "the site type" (unspecified) makes a site eligible, not specifically "the distribution site type."
- **run 3** — What makes a site eligible to be linked to an internal vendor in SchoolCafé Inventory?
  - keyed: Being assigned the distribution site type
  - judge: NO
The source states only that "that designation" makes a site eligible — it does not name or identify what "that designation" is, so the quote does not literally support "being as
- **run 3** — Which distribution preference setting updates in real time rather than being locked at the time a distribution is create
  - keyed: Available-quantity display
  - judge: NO
The source says the available-quantity display updates in real time when refreshing an order screen from an internal vendor, but it does not mention "distribution preference set
- **run 4** — What makes a site eligible to be linked to an internal vendor in SchoolCafé Inventory?
  - keyed: Being assigned the distribution site type
  - judge: NO
The quote states only that "that designation" makes the site eligible — it does not specify what the designation is (e.g., "distribution site type"); the referent of "that" is n
- **run 4** — According to the prerequisites for inventory distribution, what does assigning the distribution site type to a site acco
  - keyed: It makes the site eligible to become an internal vendor
  - judge: NO
The source says assigning the site type makes the site eligible to be **linked to** an internal vendor, not eligible to **become** an internal vendor — these are distinct relati
- **run 5** — What must happen to a site before it becomes eligible to be linked to an internal vendor?
  - keyed: It must be assigned the distribution site type
  - judge: NO
The source says the designation makes the site eligible to be linked to an internal vendor, but does not specify what that designation is — it does not literally state it must b
- **run 6** — What makes a site eligible to be linked to an internal vendor in SchoolCafé Inventory?
  - keyed: Being assigned the distribution site type
  - judge: NO
The source states only that "that designation" makes a site eligible, without specifying what that designation is — the phrase "distribution site type" does not appear in the qu
- **run 6** — What does the internal vendor contract control once a distribution site is set up?
  - keyed: The physical location and warehouse capacity of the distribution site
  - judge: NO
The quote says the contract controls item grouping, site grouping, and distribution schedule execution — it says nothing about physical location or warehouse capacity.
- **run 7** — What must be assigned to a site before it can be linked to an internal vendor?
  - keyed: The distribution site type
  - judge: NO
The source says the designation makes the site eligible to be linked to an internal vendor, but does not specify what that designation is — it does not literally name "the distr
- **run 8** — What must be assigned to a site before it becomes eligible to be linked to an internal vendor?
  - keyed: The distribution site type
  - judge: NO
The source says the "designation" makes a site eligible, but does not specify what that designation is — it does not mention "the distribution site type" at all.
- **run 9** — What makes a site eligible to be linked to an internal vendor in SchoolCafé Inventory?
  - keyed: Being assigned the distribution site type
  - judge: NO
The quote states that "that designation" makes the site eligible, but does not name what the designation is — it does not literally say "being assigned the distribution site typ
- **run 10** — What makes a site eligible to be linked to an internal vendor?
  - keyed: Being assigned the distribution site type
  - judge: NO
The source says the designation makes a site eligible to be linked to an internal vendor, but does not specify what that designation is — it does not mention "distribution site 
- **run 10** — What does the internal vendor contract control once it is configured?
  - keyed: Which staff members hold the rollback permission
  - judge: NO
The quote says the contract controls item grouping, site grouping, and distribution schedule execution — it makes no mention of staff members or rollback permissions.

## Human triage of the 14 flags (HITL — the judge is uncalibrated, so each was reviewed against the transcript)

"Flagged" ≠ "wrong answer." Triaging all 14 against what Justin actually said — and against our own
hand-curated fixture — they split into three buckets:

**10 of 14 — citation-selection weakness, NOT a wrong answer (systematic).** The *"what makes a site eligible
to link to an internal vendor?"* question appears in basically every run, and every time the generator cited an
**anaphoric span** (*"that designation" / "that site type"*) rather than the span that names it. The **answer
("distribution site type") is correct** — but the cited span doesn't prove it on its own, so the judge flags
it. **These are conservative friction, not BS.** The judge is **strictly quote-faithful**: it won't credit
*"that site type"* as *"distribution site type."* Calibration confirms this is the *judge's* behavior, not
just the generator's: it flags this exact claim as over-reach **even when handed the fully-correct span**
(`docs/JUDGE-CALIBRATION-2026-06-08.md`, faithfulness FP 2/3). So fixing the generator to cite the naming span
helps but **won't fully clear these** — Justin only ever says *"that site type,"* so a fully self-contained
span may not exist. A student still learns the right fact; the flag is the gate correctly refusing to credit
an unstated name.

**2 of 14 — genuine wrong-key the verbatim gate let through (the real catches):**
- **run 6** — *"What does the internal vendor contract control?"* keyed **"physical location and warehouse
  capacity."** Justin: the contract *"dictates how the items are grouped, how the sites are grouped, how the
  schedule is executed"* — not physical location. **Keyed answer is wrong.**
- **run 10** — same stem, keyed **"which staff members hold the rollback permission."** Same grouping/schedule
  source. **Keyed answer is wrong.**

**2 of 14 — borderline, SME to confirm:** run 4 keyed *"eligible to **become** an internal vendor"* vs the
source's *"eligible to be **linked to**"* (relationship reframed); run 3 framed available-quantity as a
*"distribution preference setting"* the cited span doesn't name.

**True wrong-key (BS) rate ≈ 2–3 / 60 (~3–5%)** — not 14/60, but **not zero**, and **0/10 runs were fully
clean**. The verbatim grounding gate passed *all* of these; only the **support-faithfulness judge caught the
wrong-keys** — exactly why this layer had to go in the evals. Note this 2–3 is a **floor**: the judge's own
measured FNR is **5.88%** (`docs/JUDGE-CALIBRATION-2026-06-08.md`), so it can miss a wrong-key — it missed one
in the gold set — meaning the sweep may contain a wrong-key the judge never flagged.

**Actionables:** (1) run the support-faithfulness gate at *publish* — it blocks the wrong-keys the verbatim
gate misses (it caught the real Q4 drift live, FN 0%); (2) have the generator **prefer the most self-contained
span**, accepting that some site-type friction is irreducible (the judge is *correctly* strict about unstated
names — see calibration); (3) **calibrate the judge — done 2026-06-08** (`docs/JUDGE-CALIBRATION-2026-06-08.md`):
quiz-framing FNR 5.88% / FPR 6.67%, faithfulness FN 0% / FP 66.7%. Verdict: a strong *second* layer, **not a
sufficient sole gate** — keep it behind the verbatim gate with a human in the loop.

## Honest caveats

- **One guide, one topic** (Inventory Distribution). Reliable here ≠ reliable everywhere.
- The **grounding gate** column (kept/dropped) is deterministic verbatim-match — hard fact.
- The **support judge is itself uncalibrated** (its own FN-rate is what `eval/judge_eval.py` measures, not yet run live). So 'key-unsupported' is the judge's opinion — a strong signal, not ground truth. **Hand-verify a sample before quoting any number to Jaime** (HITL).
- Numbers are REAL (live generation + live judge on a real guide), not synthetic fixtures.
