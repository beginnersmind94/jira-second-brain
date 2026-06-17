# Evidence Basis — what makes training stick (retention + completion)

**Purpose:** Ground the guided-lesson design choices and the frontier feature roadmap in learning science + behavioral economics, for (a) internal build-priority validation and (b) the ANC July-13 pitch.
**Produced:** 2026-06-13, via a fan-out deep-research pass — 22 sources fetched, 106 candidate claims extracted, 25 put through 3-vote adversarial verification, **22 confirmed / 3 refuted**, synthesized to 8 findings.
**Discipline:** mirrors the product's own grounding rule — every claim is graded, cited, and tagged by source type; over-claims that failed verification are listed explicitly so they never reach a slide.

---

## 1. The headline: the evidence is asymmetric

The evidence for what makes training **stick (retention)** is far stronger than for what drives **completion**. And **none** of the confirmed studies were run on our actual audience — reluctant, hourly, non-desk, low-autonomy compliance learners on a phone. Every population is K-12, university, consumer-loyalty, or government-benefits. **Transfer to cafeteria staff is a hypothesis, not a finding** — and the one directly-relevant data point (low-autonomy goal-gradient) suggests a motivation-based effect could *weaken or reverse* under our conditions.

Strategically: **the features with the strongest evidence are the cheapest ones, largely already built** (paced lesson, per-segment check, remediation re-check) — not the flagship.

---

## 2. Findings, graded and mapped to build items

| Build item | Mechanism | Grade | Verified number | Source (type) |
|---|---|---|---|---|
| Per-segment check · remediation re-check (LX-3, FB-LRN3) | Retrieval practice | **Strong** | 1 of only 2 "high-utility" of 10 techniques; **d=0.74** (meta, N=152,952); far-transfer **d=0.97** @1wk | Dunlosky 2013 (peer-reviewed); Donoghue & Hattie 2021 (meta) |
| Verbatim source line on wrong answer | Corrective feedback | **Strong** (beats bare "wrong" + restudy) | corrective **d=0.46**; high-info **d=0.99** vs reinforcement **d=0.24** (~4×) | Wisniewski/Zierer/Hattie 2020 (meta, 435 studies) |
| Cross-session spacing (across days) | Distributed practice | **Strong** | **d=0.85**, ranked #1 of 10 | Donoghue & Hattie 2021 (meta) |
| End-of-lesson recap (same session) | Distributed practice | **Weak / extrapolated** | within-session ≈ massed end of spectrum | (extrapolation from spacing evidence) |
| Frictionless mandatory path (mobile, few taps) | Sludge reduction | **Moderate** (direction robust) | "sludge reduces program take-up" | Behavioural Public Policy (peer-reviewed) |
| Test-out / default-enroll framing (FB-BLD2) | Default effects | **Moderate** (mechanism only) | works via **endorsement b=0.32** + **endowment b=0.31**; ease **n.s. (b=−0.05)** | Jachimowicz 2019 (meta, 73,675) |
| Progress bar / "Part 2 of 5" | Goal-gradient / endowed progress | **Weak / extrapolated here** | ~20% acceleration — **voluntary settings only** | Kivetz 2006 (peer-reviewed) |
| Landmark-timed assignment (week/month start) | Fresh-start effect | **Moderate** (authors *suggest* training) | gym +47% @new semester; authors name "attending training" | Dai/Milkman/Riis 2014 (peer-reviewed) |
| XP / badges / streaks (D3, already built) | Gamification | **Weakest lever** | cognitive g=0.49 (small, stable); **motivation g=0.36, behavior g=0.25 — did NOT survive rigorous studies** | Sailer & Homner 2020 (meta) |

---

## 3. Detailed findings

**Retrieval practice — Strong.** Practice testing and distributed practice were the *only two* of ten study techniques rated HIGH utility in the canonical review (Dunlosky et al. 2013, *Psychological Science in the Public Interest*; peer-reviewed). A meta-analysis of N=152,952 ranks practice testing among the top two at **d=0.74** (Donoghue & Hattie 2021, *Frontiers in Education*; meta-analysis). Far-transfer beat rereading at a 1-week delay, **d=0.97** (Van Eersel et al. 2016, PMC5183614; peer-reviewed). *Scope caveat:* strongest for recall of just-read material — exactly what the per-segment check and remediation re-check do. *Audience caveat:* all samples K-12/university.

**Distributed / spaced practice — Strong (across sessions).** The other HIGH-utility technique; **d=0.85**, ranked #1 of ten (Donoghue & Hattie 2021). Applied-classroom meta found **d=0.54** on curriculum-relevant material, larger at longer retention intervals (Mawson & Kang 2025, *Behavioral Sciences*; meta-analysis). *Key extrapolation:* all evidence is spacing across **days**; the same-session end-of-lesson recap is closer to massed — treat it as a hypothesis, pitch cross-session spacing as the evidenced design.

**Corrective feedback — Strong.** Informative corrective feedback (right/wrong + the correct answer) **d=0.46**; high-information feedback **d=0.99** vs. bare reinforcement **d=0.24** — roughly 4× (Wisniewski, Zierer & Hattie 2020, *Frontiers in Psychology*; meta-analysis, 435 studies). *Caveats:* (1) **immediate** timing is contested — delayed feedback can beat immediate for ~1-week retention; robustness is from the *presence* of feedback, so grade "immediate" as Moderate. (2) Showing only the correct line = "knowledge of correct response," which sits *between* the d=0.24 and d=0.99 poles — **do not market the d=0.99 number.**

**Goal-gradient / endowed progress — Strong (voluntary) / Weak here.** People accelerate toward a reward (~20% in a café-loyalty field study); pre-given progress accelerates identical work (Kivetz, Urminsky & Zheng 2006, *JMR*; peer-reviewed). **Direct counter-evidence on our audience:** under LOW autonomy the effect did not hold and the low-self-concordance group's performance *decreased* in the final segment (Bobková & Lovaš 2021, *Current Psychology*; peer-reviewed). Mandatory compliance is the canonical low-autonomy setting — the progress bar could underperform or backfire.

**Fresh-start effect — Moderate.** Aspirational behavior spikes after temporal landmarks across three archival datasets (Dai, Milkman & Riis 2014, *Management Science*; peer-reviewed); the authors explicitly suggest employers reframe workplace transition points to lift "attending training." *Caveat:* every measured behavior is voluntary self-improvement; the training application is author-suggested, not tested.

**Sludge / friction — Moderate.** Reducing friction is a documented causal lever on program take-up (Behavioural Public Policy, Cambridge; peer-reviewed; corroborated by SNAP/Medicaid natural experiments). Direction (less friction → more completion) is safe to assert; specific magnitudes don't transfer.

**Defaults — mechanism Strong.** Defaults work through **endorsement** (seen as a recommendation, b=0.32) and **endowment** (seen as status quo, b=0.31), *not* through ease of opting out (b=−0.05, n.s.) — Jachimowicz et al. 2019 (Behavioural Public Policy; meta-analysis, 58 studies / 73,675). *Implication:* a test-out path should be framed "recommended / this is the standard path," not merely made easy.

**Gamification — Weakest.** Cognitive/learning outcome **g=0.49** (small, and the *only* effect stable under high-rigor studies); motivational **g=0.36**, behavioral **g=0.25** (CI nearly touches zero) — and the motivation/behavior effects did **not** survive methodologically rigorous studies (Sailer & Homner 2020, *Educational Psychology Review*; meta-analysis). Keep XP/streaks as a small learning-support layer; do **not** pitch as a completion or motivation driver. *(This validates the §F D3 rescope decision already made: XP invisible to managers, completion-vs-deadline as the metric.)*

---

## 4. What adversarial review KILLED — on-stage guardrails

Three plausible claims **failed** verification. Saying any of them is the exact over-claim a skeptic punishes:

1. **"Opt-out defaults give a ~27pp / d=0.68 completion lift."** Refuted 1-2. Cite the *mechanism* (endorsement + status-quo), never the magnitude.
2. **"Rewards undermine intrinsic motivation."** Refuted 0-3 (unanimous). The strong-form crowding-out story is not settled — present streak-breakage disengagement only as a *risk to monitor*.
3. **"Most of retrieval practice's benefit is just re-exposure to the answer."** Refuted 1-2 — which *strengthens* the check feature: the gain is from the act of retrieval, not just seeing the answer again.

---

## 5. What we can honestly say on stage vs. what we cannot

**✅ Defensible (peer-reviewed/meta, mechanism-level):**
- "Retrieval practice and spacing are the two best-evidenced learning techniques in the field — the only two rated high-utility across ten, and the top two in a 153,000-person meta-analysis. Our per-segment check and remediation re-check are built directly on them."
- "Informative corrective feedback beats both a bare 'incorrect' and simple re-reading, and gets stronger the more information it carries — that's why a wrong answer shows the verbatim source line."
- "Reducing friction is a documented causal lever on completion; landmark-timed assignment is supported, and the original researchers themselves name workplace training as an application."

**🚫 Overreach to avoid:**
- Do **not** attach any effect size to "cashiers / hourly staff" — no study used this population. Say "we expect this to transfer; we're validating post-launch via the E3 funnel."
- Do **not** pitch XP/badges/streaks as a proven completion or motivation driver.
- Do **not** use the d=0.68 default magnitude or "rewards kill motivation" — both refuted.
- Do **not** call the same-session recap "distributed practice" unqualified.
- Do **not** claim the progress bar drives completion in a mandatory setting — low-autonomy evidence says it may not.

---

## 6. Build-priority implication

- **Tier 0 lesson uplift + FB-LRN3 remediation are the evidence-darlings AND the cheapest.** Retrieval + corrective feedback + a re-check (itself retrieval practice) is the best-supported combination in the field. Build-first is now evidence-backed, not just pragmatic.
- **Flagship tutor (FB-LRN1) has an evidence gap** — see §7. Build it (it's the differentiator), but frame its value as *trust/safety*, not "it teaches better," until the gap is filled.
- **Gamification:** keep small, never over-claim. Evidence ratifies the D3 rescope.

---

## 7. Evidence gaps — targeted follow-up before the flagship anchors the pitch

1. **Algorithm aversion / trust of automated advice (FB-LRN1):** *no* confirmed claim addressed whether a tutor that says "I don't know" earns more compliance than one that always answers. Sources were fetched (Dietvorst, Simmons & Massey 2018 "Overcoming Algorithm Aversion"; VanLehn tutoring meta showing ITS ≈ human tutoring) but didn't survive into the verified top-25 on this budget. This is the academic backbone of the refusal beat — fill it.
2. **Psychological reactance to forced redundant training (FB-BLD2):** the reactance-reduction rationale for test-out is plausible but unsourced in this batch.
3. **Not covered as standalone findings:** loss aversion, commitment devices, IKEA/effort-justification, present bias; formative-check low-stakes framing ("won't affect your certificate") and test anxiety.
4. **Central open question — audience transfer:** does any of this hold for reluctant, hourly, low-autonomy learners on a phone? The single highest-value follow-up is a post-launch study on the actual population, measuring retention (delayed checks) and completion (with/without each nudge).

---

## 8. Sources (confirmed claims only; tagged by type)

- Dunlosky, Rawson, Marsh, Nathan & Willingham (2013), *Psychological Science in the Public Interest* — **peer-reviewed**. https://journals.sagepub.com/doi/abs/10.1177/1529100612453266
- Donoghue & Hattie (2021), *Frontiers in Education* — **meta-analysis** (N=152,952). https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2021.581216/full
- Van Eersel et al. (2016), PMC5183614 — **peer-reviewed**. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5183614/
- Mawson & Kang (2025), *Behavioral Sciences* (MDPI), PMID 40564553 — **meta-analysis**. https://pmc.ncbi.nlm.nih.gov/articles/PMC12189222/
- Wisniewski, Zierer & Hattie (2020), *Frontiers in Psychology*, PMID 32038429 — **meta-analysis** (435 studies). https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6987456/
- Kivetz, Urminsky & Zheng (2006), *Journal of Marketing Research* — **peer-reviewed**. https://home.uchicago.edu/ourminsky/Goal-Gradient_Illusionary_Goal_Progress.pdf
- Dai, Milkman & Riis (2014), *Management Science* — **peer-reviewed**. https://faculty.wharton.upenn.edu/wp-content/uploads/2014/06/Dai_Fresh_Start_2014_Mgmt_Sci.pdf
- Sailer & Homner (2020), *Educational Psychology Review* — **meta-analysis**. https://link.springer.com/article/10.1007/s10648-019-09498-w
- Jachimowicz, Duncan, Weber & Johnson (2019), *Behavioural Public Policy* — **meta-analysis** (58 studies). https://www.cambridge.org/core/journals/behavioural-public-policy/article/when-and-why-defaults-influence-decisions-a-metaanalysis-of-default-effects/67AF6972CFB52698A60B6BD94B70C2C0
- "Sludge and Transaction Costs," *Behavioural Public Policy* (Cambridge) — **peer-reviewed**. https://www.cambridge.org/core/journals/behavioural-public-policy/article/sludge-and-transaction-costs/D09206BF9B36C129F40A27A9E749074B
- Deci, Koestner & Ryan (2001), SDT (context for crowding-out risk) — **peer-reviewed**. https://www.selfdeterminationtheory.org/SDT/documents/2001_DeciKoestnerRyan.pdf

*Relevant but fetched-not-verified (for the §7 follow-up):* Dietvorst, Simmons & Massey (2018), "Overcoming Algorithm Aversion" (Wharton); VanLehn, "Relative Effectiveness of Human Tutoring, ITS, and Other Tutoring Systems."

**No vendor-marketing source underpins any confirmed claim.** Core learning-science findings (testing effect, spacing) are decades-stable; the behavioral-econ transfer to mandatory low-autonomy mobile contexts is genuinely open.
