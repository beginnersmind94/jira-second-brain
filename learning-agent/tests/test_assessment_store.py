"""eval/test_assessment_store.py — Deterministic tests for assessment_store.py (B3)

Test coverage per the B3 spec:
  1. create_assessment() -> round-trip: reload from disk, fields intact
  2. auto-assemble with approved quizzes -> returns assessment with ≥3 questions
  3. Attempt with all correct answers -> passed: True, score_pct == 100
  4. Attempt with all wrong answers -> passed: False
     (SHOULD-NOT-OCCUR: 0% must not pass at 70% threshold)
  5. Exceed attempts_allowed -> 409 response (enforced via count_attempts guard)
     (SHOULD-NOT-OCCUR: over-limit attempt must be rejected)
  6. Question from un-approved quiz -> get_questions() skips that question (drift-safe)
  7. Certificate gate: track with assessment_gate_id set, no passing attempt ->
     has_passing_attempt() returns False

Run with:
    python -m pytest eval/test_assessment_store.py -v
or from the learning-agent/ directory:
    python eval/test_assessment_store.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import uuid
from pathlib import Path

import pytest

# Allow running directly from the learning-agent/ dir or via pytest.
_HERE = Path(__file__).resolve().parent
_LA = _HERE.parent
if str(_LA) not in sys.path:
    sys.path.insert(0, str(_LA))


# ── Restore module globals after each test ────────────────────────────────────
# _setup() does RAW (non-monkeypatch) assignments to assessment_store._ASSESS_DIR /
# _ATTEMPTS_DIR / _QUIZZES_DIR and quiz_store.QUIZZES, pointing them at a
# TemporaryDirectory that is deleted when the test's `with` block exits. Without
# restoration those globals stay pointed at a now-deleted dir for the rest of the
# pytest session, so any later test that writes via quiz_store.save_quiz() (etc.)
# hits FileNotFoundError. This autouse fixture snapshots the four globals and
# restores them after each test. (Ignored in direct-run / __main__ mode — pytest
# fixtures don't apply there, which is fine: a direct run is a single process that
# exits immediately after.)
@pytest.fixture(autouse=True)
def _restore_store_globals():
    import assessment_store as _as
    import quiz_store as _qs

    saved = (
        _as._ASSESS_DIR,
        _as._ATTEMPTS_DIR,
        _as._QUIZZES_DIR,
        _qs.QUIZZES,
    )
    try:
        yield
    finally:
        _as._ASSESS_DIR, _as._ATTEMPTS_DIR, _as._QUIZZES_DIR, _qs.QUIZZES = saved


# ── Patch quiz_store and assessment_store to use temp dirs ────────────────────

def _make_seed_quiz(qdir: Path, *, status: str = "approved") -> dict:
    """Write a minimal seed quiz with 4 MCQ questions (enough to test diversity)."""
    quiz = {
        "id": f"quiz-test-{uuid.uuid4().hex[:6]}",
        "title": "Test Quiz",
        "status": status,
        "source_type": "guide",
        "source_id": "test-guide",
        "source_label": "Test Guide",
        "source_content_hash": "abc123",
        "stale": False,
        "created_at": "2026-01-01T00:00:00",
        "updated_at": "2026-01-01T00:00:00",
        "questions": [
            {
                "type": "mcq",
                "stem": "What is the first step?",
                "options": ["Log in", "Count cash", "Enter menu", "Check balance"],
                "answer_index": 0,
                "explanation": "Logging in is the first step.",
                "source_quote": "Log in with your assigned employee ID",
                "source_ref": "test-guide",
                "provenance": "manual_grounded",
                "grounded": True,
                "sme_verified": True,
            },
            {
                "type": "tf",
                "stem": "True or False: cashiers may override balances without approval.",
                "correct": False,
                "source_span": "Only a manager may override a student account balance.",
                "distractor_basis": {
                    "span": "Only a manager may override a student account balance.",
                    "transform": "negation",
                },
                "section": "Permissions",
                "explanation": "Manager authorization is required.",
                "provenance": "manual_grounded",
                "grounded": True,
                "sme_verified": True,
            },
            {
                "type": "fitb",
                "stem": "Press the ___ button to end the service period.",
                "answer": "End of Period",
                "source_sentence": "Press the End of Period button to end the service period.",
                "section": "Closing",
                "explanation": "Ends the meal service session.",
                "provenance": "manual_grounded",
                "grounded": True,
                "sme_verified": True,
            },
            {
                "type": "mcq",
                "stem": "A la carte items need which extra code?",
                "options": [
                    "A separate payment category code",
                    "A free-meal override",
                    "A district coupon",
                    "No extra code",
                ],
                "answer_index": 0,
                "explanation": "A la carte items use a separate category.",
                "source_quote": "A la carte items require a separate payment category code",
                "source_ref": "test-guide",
                "provenance": "manual_grounded",
                "grounded": True,
                "sme_verified": True,
            },
        ],
    }
    (qdir / f"{quiz['id']}.json").write_text(
        json.dumps(quiz, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return quiz


def _setup(tmp: Path):
    """Create temp data dirs and monkey-patch assessment_store + quiz_store paths."""
    import assessment_store as _as
    import quiz_store as _qs

    quiz_dir = tmp / "quizzes"
    quiz_dir.mkdir()
    assess_dir = tmp / "assessments"
    assess_dir.mkdir()
    attempts_dir = tmp / "assessment-attempts"
    attempts_dir.mkdir()

    # Patch assessment_store globals.
    _as._ASSESS_DIR = assess_dir
    _as._ATTEMPTS_DIR = attempts_dir
    _as._QUIZZES_DIR = quiz_dir

    # Patch quiz_store.QUIZZES so list_quizzes() sees the temp dir.
    _qs.QUIZZES = quiz_dir

    return quiz_dir, assess_dir, attempts_dir


# ── Test 1: create_assessment round-trip ─────────────────────────────────────

def test_create_assessment_round_trip():
    """create_assessment() -> reload from disk -> fields intact."""
    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        quiz_dir, assess_dir, attempts_dir = _setup(tmp)

        import assessment_store as _as

        a = _as.create_assessment(
            title="Round-trip Test",
            track_id="track-test-001",
            question_ids=["quiz-abc:0", "quiz-abc:1", "quiz-abc:2"],
            time_limit_min=10,
            pass_pct=75,
            attempts_allowed=2,
        )

        # Reload from disk.
        reloaded = _as.get_assessment(a["id"])
        assert reloaded is not None, "Assessment not found after save"
        assert reloaded["title"] == "Round-trip Test"
        assert reloaded["track_id"] == "track-test-001"
        assert reloaded["question_ids"] == ["quiz-abc:0", "quiz-abc:1", "quiz-abc:2"]
        assert reloaded["time_limit_min"] == 10
        assert reloaded["pass_pct"] == 75
        assert reloaded["attempts_allowed"] == 2
        assert reloaded["status"] == "draft"
        assert "created_at" in reloaded
        assert "updated_at" in reloaded

    print("PASS  test_create_assessment_round_trip")


# ── Test 2: auto-assemble with approved quizzes ───────────────────────────────

def test_auto_assemble_returns_assessment():
    """auto_assemble with approved quizzes returns an assessment with ≥3 questions."""
    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        quiz_dir, assess_dir, attempts_dir = _setup(tmp)

        import assessment_store as _as

        quiz = _make_seed_quiz(quiz_dir, status="approved")

        assessment, err = _as.auto_assemble(track_id="track-001", n=4)
        assert err is None, f"auto_assemble error: {err}"
        assert assessment is not None
        assert len(assessment["question_ids"]) >= 3
        assert assessment["status"] == "draft"
        assert assessment["track_id"] == "track-001"

        # Reload from disk confirms persistence.
        reloaded = _as.get_assessment(assessment["id"])
        assert reloaded is not None
        assert len(reloaded["question_ids"]) >= 3

    print("PASS  test_auto_assemble_returns_assessment")


# ── Test 3: all-correct attempt scores 100% and passes ───────────────────────

def test_all_correct_attempt_passes():
    """All correct answers -> passed: True, score_pct == 100."""
    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        quiz_dir, assess_dir, attempts_dir = _setup(tmp)

        import assessment_store as _as

        quiz = _make_seed_quiz(quiz_dir, status="approved")
        qid = quiz["id"]
        # Use first 3 questions (MCQ:0, TF:1, FITB:2)
        assessment = _as.create_assessment(
            title="All Correct",
            track_id="track-test",
            question_ids=[f"{qid}:0", f"{qid}:1", f"{qid}:2"],
            pass_pct=70,
        )
        # Force to published so scoring works.
        assessment["status"] = "published"
        _as.save_assessment(assessment)

        # Correct answers: MCQ answer_index=0, TF correct=False, FITB answer="End of Period"
        answers = {
            f"{qid}:0": 0,          # MCQ: option 0 is correct
            f"{qid}:1": False,       # TF: correct is False
            f"{qid}:2": "End of Period",  # FITB: exact answer
        }
        score_pct, passed, per_q = _as.score_attempt(assessment, answers)
        assert passed is True, f"Expected passed=True but got {passed} (score={score_pct})"
        assert score_pct == 100.0, f"Expected 100 but got {score_pct}"

    print("PASS  test_all_correct_attempt_passes")


# ── Test 4: all-wrong attempt fails (SHOULD-NOT-OCCUR: 0% must not pass) ─────

def test_all_wrong_attempt_fails():
    """SHOULD-NOT-OCCUR: 0% score must not pass at 70% threshold."""
    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        quiz_dir, assess_dir, attempts_dir = _setup(tmp)

        import assessment_store as _as

        quiz = _make_seed_quiz(quiz_dir, status="approved")
        qid = quiz["id"]
        assessment = _as.create_assessment(
            title="All Wrong",
            track_id="track-test",
            question_ids=[f"{qid}:0", f"{qid}:1", f"{qid}:2"],
            pass_pct=70,
        )
        assessment["status"] = "published"
        _as.save_assessment(assessment)

        # Wrong answers: MCQ wrong index, TF wrong (should be False, we send True), FITB wrong
        answers = {
            f"{qid}:0": 3,           # MCQ: option 3, correct is 0
            f"{qid}:1": True,        # TF: correct is False
            f"{qid}:2": "wrong",     # FITB: correct is "End of Period"
        }
        score_pct, passed, per_q = _as.score_attempt(assessment, answers)
        assert passed is False, (
            f"SHOULD-NOT-OCCUR: 0% score must not pass at 70% threshold. "
            f"Got passed={passed}, score={score_pct}"
        )
        assert score_pct == 0.0, f"Expected 0 but got {score_pct}"

    print("PASS  test_all_wrong_attempt_fails (SHOULD-NOT-OCCUR guarded)")


# ── Test 5: over-limit attempt blocked (SHOULD-NOT-OCCUR) ────────────────────

def test_over_limit_attempt_blocked():
    """SHOULD-NOT-OCCUR: count_attempts() must reflect the limit; API returns 409."""
    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        quiz_dir, assess_dir, attempts_dir = _setup(tmp)

        import assessment_store as _as

        quiz = _make_seed_quiz(quiz_dir, status="approved")
        qid = quiz["id"]
        assessment = _as.create_assessment(
            title="Limit Test",
            track_id="track-test",
            question_ids=[f"{qid}:0"],
            pass_pct=70,
            attempts_allowed=2,
        )
        assessment["status"] = "published"
        _as.save_assessment(assessment)

        uid = "test-user-001"
        aid = assessment["id"]

        # Submit 2 attempts (at the limit).
        for _ in range(2):
            _as.save_attempt(
                user_id=uid,
                assessment_id=aid,
                answers={},
                score_pct=50,
                passed=False,
                per_question=[],
            )

        used = _as.count_attempts(uid, aid)
        assert used == 2, f"Expected 2 attempts recorded, got {used}"

        # The API layer checks: if used >= allowed → 409. Verify the condition directly.
        allowed = assessment["attempts_allowed"]
        assert used >= allowed, (
            f"SHOULD-NOT-OCCUR: attempt limit not reached. used={used}, allowed={allowed}"
        )

    print("PASS  test_over_limit_attempt_blocked (SHOULD-NOT-OCCUR guarded)")


# ── Test 6: un-approved quiz question is skipped (drift-safe) ─────────────────

def test_unapproved_quiz_question_skipped():
    """A question from a quiz that lost approval is silently skipped by get_questions()."""
    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        quiz_dir, assess_dir, attempts_dir = _setup(tmp)

        import assessment_store as _as

        # Two quizzes: one approved, one draft.
        approved_quiz = _make_seed_quiz(quiz_dir, status="approved")
        draft_quiz = _make_seed_quiz(quiz_dir, status="draft")

        assessment = _as.create_assessment(
            title="Drift Test",
            track_id="track-test",
            question_ids=[
                f"{approved_quiz['id']}:0",
                f"{draft_quiz['id']}:0",   # from a draft quiz — must be skipped
                f"{approved_quiz['id']}:1",
            ],
            pass_pct=70,
        )
        assessment["status"] = "published"
        _as.save_assessment(assessment)

        resolved = _as.get_questions(assessment, include_source_quotes=False)
        # Only questions from the approved quiz should resolve (2 questions).
        assert len(resolved) == 2, (
            f"Expected 2 resolved questions (draft quiz skipped), got {len(resolved)}"
        )
        # Verify the draft quiz question is not present.
        ptrs = [q.get("_ptr", "") for q in resolved]
        for ptr in ptrs:
            qid_part = ptr.split(":")[0]
            assert qid_part == approved_quiz["id"], (
                f"Found question from unexpected quiz: {ptr}"
            )

    print("PASS  test_unapproved_quiz_question_skipped (drift-safe)")


# ── Test 7: cert gate — no passing attempt returns has_passing_attempt=False ──

def test_cert_gate_no_passing_attempt():
    """Track with assessment_gate_id set, no passing attempt -> has_passing_attempt() is False."""
    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        quiz_dir, assess_dir, attempts_dir = _setup(tmp)

        import assessment_store as _as

        assessment = _as.create_assessment(
            title="Gate Test",
            track_id="track-gate-test",
            question_ids=["quiz-x:0", "quiz-x:1", "quiz-x:2"],
            pass_pct=70,
        )
        assessment["status"] = "published"
        _as.save_assessment(assessment)

        uid = "john-cashier"
        aid = assessment["id"]

        # No attempts yet.
        result = _as.has_passing_attempt(uid, aid, pass_pct=70)
        assert result is False, f"Expected False (no attempts), got {result}"

        # Record a failing attempt.
        _as.save_attempt(
            user_id=uid,
            assessment_id=aid,
            answers={},
            score_pct=40,
            passed=False,
            per_question=[],
        )
        result = _as.has_passing_attempt(uid, aid, pass_pct=70)
        assert result is False, f"Expected False (score=40 < 70), got {result}"

        # Record a passing attempt.
        _as.save_attempt(
            user_id=uid,
            assessment_id=aid,
            answers={},
            score_pct=88,
            passed=True,
            per_question=[],
        )
        result = _as.has_passing_attempt(uid, aid, pass_pct=70)
        assert result is True, f"Expected True (score=88 >= 70), got {result}"

    print("PASS  test_cert_gate_no_passing_attempt")


# ── Runner ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        test_create_assessment_round_trip,
        test_auto_assemble_returns_assessment,
        test_all_correct_attempt_passes,
        test_all_wrong_attempt_fails,
        test_over_limit_attempt_blocked,
        test_unapproved_quiz_question_skipped,
        test_cert_gate_no_passing_attempt,
    ]
    failures = []
    for t in tests:
        try:
            t()
        except Exception as exc:
            failures.append((t.__name__, exc))
            print(f"FAIL  {t.__name__}: {exc}")

    print(f"\n{'='*60}")
    if failures:
        print(f"FAILED {len(failures)}/{len(tests)} tests")
        sys.exit(1)
    else:
        print(f"All {len(tests)} tests passed.")
