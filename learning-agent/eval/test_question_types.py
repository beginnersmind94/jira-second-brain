"""test_question_types.py — deterministic regression tests for B1 question types.

Tests the _gate_tf, _gate_fitb, and _gate_ordering functions in qbank_gate.py,
plus quiz_store.score_quiz for the three new types.

Design follows EVAL-SPEC.md conventions:
  - Deterministic, ZERO SDK calls.
  - Includes balanced SHOULD-OCCUR and SHOULD-NOT-OCCUR (negative) cases per type.
  - Exits non-zero if any test fails (same contract as eval/regression.py).
  - Run: python -m eval.test_question_types

Grounded in EVAL-SPEC.md guidance: "must include negative cases" (the SHOULD-NOT-OCCUR
cases act like the balanced-pair negatives in the guide graders — a test suite with
only positive cases can't detect a gate that always passes).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from qbank_gate import _gate_tf, _gate_fitb, _gate_ordering
import quiz_store

# ── Shared fixture content ────────────────────────────────────────────────────
CONTENT = (
    "The minimum charge for a reimbursable meal is $2.50 per student. "
    "Site managers must verify eligibility before serving a free meal. "
    "To process a return: first locate the transaction, then select Refund, "
    "then confirm the amount, and finally print the receipt. "
    "All adjustments require a supervisor approval code."
)

RESULTS: list[tuple[str, bool, str]] = []


def _check(name: str, got: dict, expected_pass: bool) -> bool:
    ok = bool(got["pass"]) == expected_pass
    status = "PASS" if ok else "FAIL"
    RESULTS.append((name, ok, f"gate={got['pass']!r} reason={got['reason']!r}"))
    print(f"  [{status}] {name}: {got['reason']}")
    return ok


# ── TRUE/FALSE gate ───────────────────────────────────────────────────────────

def test_tf_true_span_in_content():
    """TF TRUE: source_span IS verbatim in content → passes."""
    q = {
        "type": "tf",
        "stem": "The minimum charge for a reimbursable meal is $2.50 per student.",
        "correct": True,
        "source_span": "minimum charge for a reimbursable meal is $2.50 per student",
        "distractor_basis": {},
    }
    return _check("TF-TRUE verbatim span in content", _gate_tf(q, CONTENT), True)


def test_tf_true_span_not_in_content():
    """TF TRUE: source_span NOT in content → fails/drops (SHOULD-NOT-OCCUR case)."""
    q = {
        "type": "tf",
        "stem": "The minimum charge is $5.00.",
        "correct": True,
        "source_span": "minimum charge is $5.00",
        "distractor_basis": {},
    }
    return _check("TF-TRUE span not in content → DROP", _gate_tf(q, CONTENT), False)


def test_tf_false_valid_negation():
    """TF FALSE: source_span in content, distractor_basis.transform='negation' → passes."""
    q = {
        "type": "tf",
        "stem": "Site managers do NOT need to verify eligibility before serving a free meal.",
        "correct": False,
        "source_span": "Site managers must verify eligibility before serving a free meal",
        "distractor_basis": {"transform": "negation", "span": "Site managers must verify eligibility before serving a free meal"},
    }
    return _check("TF-FALSE valid negation", _gate_tf(q, CONTENT), True)


def test_tf_false_missing_negation_transform():
    """TF FALSE: distractor_basis.transform is not 'negation' → fails/drops
    (guards against non-mechanical distractors that could introduce uncited claims)."""
    q = {
        "type": "tf",
        "stem": "A supervisor code is optional.",
        "correct": False,
        "source_span": "All adjustments require a supervisor approval code",
        "distractor_basis": {"transform": "invention"},   # <-- wrong, should be rejected
    }
    return _check("TF-FALSE non-negation transform → DROP", _gate_tf(q, CONTENT), False)


def test_tf_missing_source_span():
    """TF: no source_span at all → fails/drops."""
    q = {"type": "tf", "stem": "Some claim.", "correct": True, "distractor_basis": {}}
    return _check("TF missing source_span → DROP", _gate_tf(q, CONTENT), False)


# ── FILL-IN-THE-BLANK gate ────────────────────────────────────────────────────

def test_fitb_verbatim_blank():
    """FITB: stem.replace('___', answer) reassembles verbatim → passes."""
    q = {
        "type": "fitb",
        "stem": "The minimum charge for a reimbursable meal is ___ per student.",
        "answer": "$2.50",
        "source_sentence": "The minimum charge for a reimbursable meal is $2.50 per student.",
    }
    return _check("FITB verbatim blank", _gate_fitb(q, CONTENT), True)


def test_fitb_paraphrased_blank_not_verbatim():
    """FITB: blank is paraphrased, reconstructed string not in content → fails/drops
    (SHOULD-NOT-OCCUR: blank must be verbatim, not a synonym or reformulation)."""
    q = {
        "type": "fitb",
        "stem": "Site managers must check ___ before serving a free meal.",  # 'check' ≠ 'verify eligibility'
        "answer": "eligibility",
        "source_sentence": "Site managers must check eligibility before serving a free meal.",  # paraphrase, not in CONTENT
    }
    return _check("FITB paraphrased sentence → DROP", _gate_fitb(q, CONTENT), False)


def test_fitb_missing_blank_marker():
    """FITB: stem lacks '___' → fails/drops."""
    q = {"type": "fitb", "stem": "The charge is $2.50.", "answer": "$2.50", "source_sentence": "..."}
    return _check("FITB missing blank marker → DROP", _gate_fitb(q, CONTENT), False)


def test_fitb_empty_answer():
    """FITB: answer is empty → fails/drops."""
    q = {"type": "fitb", "stem": "The charge is ___.", "answer": "", "source_sentence": "The charge is ."}
    return _check("FITB empty answer → DROP", _gate_fitb(q, CONTENT), False)


# ── STEP-ORDERING gate ────────────────────────────────────────────────────────

STEPS_VERBATIM = [
    "first locate the transaction",
    "then select Refund",
    "then confirm the amount",
    "and finally print the receipt",
]
SOURCE_QUOTE_ORDERING = (
    "To process a return: first locate the transaction, then select Refund, "
    "then confirm the amount, and finally print the receipt."
)


def test_ordering_all_steps_verbatim():
    """ORDERING: all steps verbatim in source_quote, source_quote in content → passes."""
    q = {
        "type": "ordering",
        "prompt": "Put these steps in the correct order:",
        "steps": STEPS_VERBATIM,
        "correct_order": [0, 1, 2, 3],
        "source_quote": SOURCE_QUOTE_ORDERING,
    }
    return _check("ORDERING all steps verbatim", _gate_ordering(q, CONTENT), True)


def test_ordering_invented_step():
    """ORDERING: one invented step not in source_quote → fails/drops
    (SHOULD-NOT-OCCUR: every step must come from the cited section verbatim)."""
    q = {
        "type": "ordering",
        "prompt": "Put these steps in the correct order:",
        "steps": [
            "first locate the transaction",
            "enter your manager PIN",          # <-- invented, not in source
            "then confirm the amount",
            "and finally print the receipt",
        ],
        "correct_order": [0, 1, 2, 3],
        "source_quote": SOURCE_QUOTE_ORDERING,
    }
    return _check("ORDERING invented step → DROP", _gate_ordering(q, CONTENT), False)


def test_ordering_source_quote_not_in_content():
    """ORDERING: source_quote is not in content → fails/drops."""
    q = {
        "type": "ordering",
        "steps": ["step one", "step two"],
        "correct_order": [0, 1],
        "source_quote": "step one and step two are required procedures",  # not in CONTENT
    }
    return _check("ORDERING source_quote not in content → DROP", _gate_ordering(q, CONTENT), False)


def test_ordering_too_few_steps():
    """ORDERING: only one step → fails/drops (minimum 2 required for ordering to make sense)."""
    q = {
        "type": "ordering",
        "steps": ["first locate the transaction"],
        "correct_order": [0],
        "source_quote": SOURCE_QUOTE_ORDERING,
    }
    return _check("ORDERING single step → DROP", _gate_ordering(q, CONTENT), False)


# ── quiz_store.score_quiz — per-type scoring ─────────────────────────────────

def test_score_tf_correct():
    """score_quiz TF: correct answer → correct=True, source_quote populated."""
    quiz = {"questions": [{
        "type": "tf", "stem": "True/false: $2.50",
        "correct": True, "source_span": "minimum charge for a reimbursable meal is $2.50",
        "distractor_basis": {}, "grounded": True,
    }]}
    result = quiz_store.score_quiz(quiz, [True])
    r = result["results"][0]
    ok = r["correct"] is True and result["correct"] == 1
    status = "PASS" if ok else "FAIL"
    RESULTS.append(("SCORE TF correct", ok, str(r)))
    print(f"  [{status}] SCORE TF correct: correct={r['correct']}, source_quote={r['source_quote']!r}")
    return ok


def test_score_tf_wrong():
    """score_quiz TF: wrong answer → correct=False, source_quote still populated."""
    quiz = {"questions": [{
        "type": "tf", "stem": "True/false?",
        "correct": True, "source_span": "the verbatim span",
        "distractor_basis": {}, "grounded": True,
    }]}
    result = quiz_store.score_quiz(quiz, [False])
    r = result["results"][0]
    ok = r["correct"] is False and result["correct"] == 0 and bool(r.get("source_quote"))
    status = "PASS" if ok else "FAIL"
    RESULTS.append(("SCORE TF wrong returns source", ok, str(r)))
    print(f"  [{status}] SCORE TF wrong returns source: correct={r['correct']}, sq={r['source_quote']!r}")
    return ok


def test_score_fitb_correct():
    """score_quiz FITB: case-insensitive strip match → correct=True."""
    quiz = {"questions": [{
        "type": "fitb", "stem": "The charge is ___.",
        "answer": "$2.50", "source_sentence": "The charge is $2.50.", "grounded": True,
    }]}
    result = quiz_store.score_quiz(quiz, ["$2.50"])
    r = result["results"][0]
    ok = r["correct"] is True
    RESULTS.append(("SCORE FITB correct", ok, str(r)))
    print(f"  [{'PASS' if ok else 'FAIL'}] SCORE FITB correct: {r['correct']}")
    return ok


def test_score_fitb_case_insensitive():
    """score_quiz FITB: case-insensitive comparison."""
    quiz = {"questions": [{
        "type": "fitb", "stem": "Approval is ___.",
        "answer": "Required", "source_sentence": "Approval is Required.", "grounded": True,
    }]}
    result = quiz_store.score_quiz(quiz, ["required"])
    r = result["results"][0]
    ok = r["correct"] is True
    RESULTS.append(("SCORE FITB case-insensitive", ok, str(r)))
    print(f"  [{'PASS' if ok else 'FAIL'}] SCORE FITB case-insensitive: {r['correct']}")
    return ok


def test_score_ordering_correct():
    """score_quiz ORDERING: correct submitted order → correct=True."""
    steps = ["Step A", "Step B", "Step C"]
    quiz = {"questions": [{
        "type": "ordering", "prompt": "Order these:",
        "steps": steps, "correct_order": [0, 1, 2],
        "source_quote": "Step A ... Step B ... Step C", "grounded": True,
    }]}
    result = quiz_store.score_quiz(quiz, [[0, 1, 2]])
    r = result["results"][0]
    ok = r["correct"] is True
    RESULTS.append(("SCORE ORDERING correct", ok, str(r)))
    print(f"  [{'PASS' if ok else 'FAIL'}] SCORE ORDERING correct: {r['correct']}")
    return ok


def test_score_ordering_wrong():
    """score_quiz ORDERING: wrong order → correct=False, source_quote still present."""
    steps = ["Step A", "Step B", "Step C"]
    quiz = {"questions": [{
        "type": "ordering", "prompt": "Order these:",
        "steps": steps, "correct_order": [0, 1, 2],
        "source_quote": "Step A Step B Step C is the workflow", "grounded": True,
    }]}
    result = quiz_store.score_quiz(quiz, [[2, 0, 1]])
    r = result["results"][0]
    ok = r["correct"] is False and bool(r.get("source_quote"))
    RESULTS.append(("SCORE ORDERING wrong returns source", ok, str(r)))
    print(f"  [{'PASS' if ok else 'FAIL'}] SCORE ORDERING wrong: correct={r['correct']}, sq={r['source_quote']!r}")
    return ok


# ── validate_shape round-trip ─────────────────────────────────────────────────

def test_validate_shape_tf_ok():
    """validate_shape passes a well-formed TF question with no errors."""
    q = {
        "type": "tf", "stem": "A stem.", "correct": True,
        "source_span": "A stem.", "distractor_basis": {},
    }
    errs = quiz_store.validate_shape(q)
    ok = len(errs) == 0
    RESULTS.append(("validate_shape TF ok", ok, str(errs)))
    print(f"  [{'PASS' if ok else 'FAIL'}] validate_shape TF ok: {errs}")
    return ok


def test_validate_shape_fitb_ok():
    """validate_shape passes a well-formed FITB question."""
    q = {
        "type": "fitb", "stem": "The charge is ___.",
        "answer": "$2.50", "source_sentence": "The charge is $2.50.",
    }
    errs = quiz_store.validate_shape(q)
    ok = len(errs) == 0
    RESULTS.append(("validate_shape FITB ok", ok, str(errs)))
    print(f"  [{'PASS' if ok else 'FAIL'}] validate_shape FITB ok: {errs}")
    return ok


def test_validate_shape_ordering_ok():
    """validate_shape passes a well-formed ordering question."""
    q = {
        "type": "ordering", "steps": ["A", "B", "C"],
        "correct_order": [0, 1, 2], "source_quote": "A B C",
    }
    errs = quiz_store.validate_shape(q)
    ok = len(errs) == 0
    RESULTS.append(("validate_shape ORDERING ok", ok, str(errs)))
    print(f"  [{'PASS' if ok else 'FAIL'}] validate_shape ORDERING ok: {errs}")
    return ok


def test_validate_shape_tf_missing_correct():
    """validate_shape rejects TF without a boolean 'correct' field."""
    q = {"type": "tf", "stem": "A stem.", "source_span": "A stem.", "distractor_basis": {}}
    errs = quiz_store.validate_shape(q)
    ok = any("correct" in e for e in errs)
    RESULTS.append(("validate_shape TF missing correct", ok, str(errs)))
    print(f"  [{'PASS' if ok else 'FAIL'}] validate_shape TF missing correct: {errs}")
    return ok


# ── Runner ─────────────────────────────────────────────────────────────────────

TESTS = [
    # TF gate
    test_tf_true_span_in_content,
    test_tf_true_span_not_in_content,
    test_tf_false_valid_negation,
    test_tf_false_missing_negation_transform,
    test_tf_missing_source_span,
    # FITB gate
    test_fitb_verbatim_blank,
    test_fitb_paraphrased_blank_not_verbatim,
    test_fitb_missing_blank_marker,
    test_fitb_empty_answer,
    # ORDERING gate
    test_ordering_all_steps_verbatim,
    test_ordering_invented_step,
    test_ordering_source_quote_not_in_content,
    test_ordering_too_few_steps,
    # Scoring
    test_score_tf_correct,
    test_score_tf_wrong,
    test_score_fitb_correct,
    test_score_fitb_case_insensitive,
    test_score_ordering_correct,
    test_score_ordering_wrong,
    # validate_shape
    test_validate_shape_tf_ok,
    test_validate_shape_fitb_ok,
    test_validate_shape_ordering_ok,
    test_validate_shape_tf_missing_correct,
]


def main():
    print("=" * 60)
    print("B1 Question Types — deterministic regression tests")
    print("=" * 60)

    sections = [
        ("TF gate", TESTS[:5]),
        ("FITB gate", TESTS[5:9]),
        ("ORDERING gate", TESTS[9:13]),
        ("Scoring (score_quiz)", TESTS[13:19]),
        ("validate_shape", TESTS[19:]),
    ]

    passed = 0
    failed = 0
    for section_name, tests in sections:
        print(f"\n{section_name}")
        for t in tests:
            try:
                ok = t()
            except Exception as e:
                ok = False
                name = t.__name__
                RESULTS.append((name, False, f"EXCEPTION: {e}"))
                print(f"  [FAIL] {name}: EXCEPTION: {e}")
            if ok:
                passed += 1
            else:
                failed += 1

    total = passed + failed
    print(f"\n{'=' * 60}")
    print(f"Results: {passed}/{total} passed{', ' + str(failed) + ' failed' if failed else ''}")
    if failed:
        print("\nFailed tests:")
        for name, ok, detail in RESULTS:
            if not ok:
                print(f"  FAIL  {name}: {detail}")
    print("=" * 60)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
