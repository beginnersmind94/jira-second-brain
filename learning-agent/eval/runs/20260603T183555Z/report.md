# Capability Eval — 20260603T183555Z

- Module: `Item Management`
- Transcript: `raw/transcripts/20260529-070600-item-management-2026-05-28-item-management-create-items-training.md`

## Per-format summary

| Format | Trials | pass@k | pass^k | pass_rate | mean partial | cost (USD) |
|---|---|---|---|---|---|---|
| long-form | 2 | True | True | 1.00 | 1.000 | $2.0070 |
| micro-guide | 2 | True | True | 1.00 | 1.000 | $1.4292 |
| tldr | 2 | False | False | 0.00 | 0.833 | $0.9935 |
| **TOTAL** | | | | | | **$4.4297** |

## Per-grader rollup

### long-form

| Grader | Passed/Trials | Mean score |
|---|---|---|
| G1_tier_lie | 2/2 | 1.000 |
| G2_not_found | 2/2 | 1.000 |
| G3_invalid_id | 2/2 | 1.000 |
| G4_density | 2/2 | 1.000 |
| G5_section_fit | 2/2 | 1.000 |
| G6_length | 2/2 | 1.000 |

### micro-guide

| Grader | Passed/Trials | Mean score |
|---|---|---|
| G1_tier_lie | 2/2 | 1.000 |
| G2_not_found | 2/2 | 1.000 |
| G3_invalid_id | 2/2 | 1.000 |
| G4_density | 2/2 | 1.000 |
| G5_section_fit | 2/2 | 1.000 |
| G6_length | 2/2 | 1.000 |

### tldr

| Grader | Passed/Trials | Mean score |
|---|---|---|
| G1_tier_lie | 2/2 | 1.000 |
| G2_not_found | 2/2 | 1.000 |
| G3_invalid_id | 2/2 | 1.000 |
| G4_density | 2/2 | 1.000 |
| G5_section_fit | 2/2 | 1.000 |
| G6_length | 0/2 | 0.000 |

## Regression checks (deterministic, no SDK)

15 passed, 0 failed, 0 skipped of 15

| Check | Status | Detail |
|---|---|---|
| REG-01 enforce relabels tier-lie | PASS | NXT-1780: raw tier_lie=1 relabeled=1 fixed tier_lie=0 |
| REG-02 verbatim AC = ok | PASS | NXT-1780: ok=1 tier_lie=0 not_found=0 tokened=1 |
| REG-03 paraphrase = not_found | PASS | NXT-1780: not_found=1 ok=0 |
| REG-04 assemble valid + invalid id | PASS | rendered=1 invalid_cite_id=1 |
| REG-05 enforce leaves correct untouched | PASS | NXT-1780: relabeled=0 byte_identical=True |
| REG-06 enforce no-fabricate not_found | PASS | NXT-1780: relabeled=0 not_found_after=1 |
| REG-07 registry tier-binding | PASS | 36 spans checked, 0 mis-bound |
| REG-08 format constants | PASS | VALID_FORMATS=('long-form', 'micro-guide', 'tldr') TEMPLATES=('long-form', 'micro-guide', 'tldr') |
| REG-09 format spec/budget keys | PASS | spec={'long-form', 'micro-guide', 'tldr'} budget={'long-form', 'micro-guide', 'tldr'} (min_sections 5/6/8 inline in run_cell_d) |
| REG-10 transcript counted separately | PASS | transcript=1 tokened=0 tier_lie=0 |
| REG-11 assemble appends Sources | PASS | sources_present=True issues=['NXT-1780'] |
| REG-12 empty field -> 0 spans | PASS | NXT-3033: empty-AC produced AC span? False |
| REG-13 _words excludes comments/tags | PASS | _words=4 (expected 4: Title one two three) |
| REG-14 assemble tolerates whitespace | PASS | rendered=1 (whitespace marker) |
| REG-15 empty _FIX -> no false ok | PASS | ok_with_empty_FIX=0 (must be 0) |
