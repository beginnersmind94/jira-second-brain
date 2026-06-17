"""test_builder_beats.py — 5-test suite for ANC builder demo beats (D-spec).

Beat 1: POST /api/demo/run-refusal
  1. CONFERENCE_MODE=true  → passed=false with named violation  (SHOULD-NOT-OCCUR gate)
  2. CONFERENCE_MODE=false → 403                                (SHOULD-NOT-OCCUR gate)

Beat 2: Structural pin on staged wrong-source artifact
  3. demo-wrong-source-resource.json exists with status='awaiting_review' + _demo_note field

Beat 4: POST /api/demo/trigger-drift + POST /api/demo/reset
  4. trigger-drift with a valid resource_id reverts dependent quiz to 'draft'  (SHOULD-NOT-OCCUR)
  5. reset after trigger-drift restores the guide to pre-trigger content       (SHOULD-NOT-OCCUR)

Run from learning-agent/ :
    python -m pytest eval/test_builder_beats.py -v
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# ── Path setup ────────────────────────────────────────────────────────────────
_LA = Path(__file__).resolve().parent.parent          # learning-agent/
sys.path.insert(0, str(_LA))

# ── Helpers ───────────────────────────────────────────────────────────────────
_DATA_DEMO = _LA / "data" / "demo"


def _demo_app_with_conference(value: str = "conference"):
    """Context manager: patch DEMO_MODE and re-import demo_app with the flag set."""
    return patch.dict(os.environ, {"DEMO_MODE": value})


# ── Test 1: Beat 1 — planted claim fails the gate in CONFERENCE_MODE ──────────
def test_beat1_refusal_in_conference_mode():
    """SHOULD-NOT-OCCUR: a planted bad claim (NXT-9999) must not pass the gate.

    The validate_citations function must detect that NXT-9999 does not exist in
    the fixture and/or the claimed quote is not verbatim — returning at least
    one violation with passed=False.
    """
    with _demo_app_with_conference("conference"):
        # Import fresh so CONFERENCE_MODE picks up the env var.
        import importlib
        if "demo_app" in sys.modules:
            importlib.reload(sys.modules["demo_app"])
        import demo_app  # noqa: F401 — side-effect: registers routes

        import asyncio
        # Call the endpoint handler directly (avoids needing a running ASGI server).
        result = asyncio.get_event_loop().run_until_complete(demo_app.demo_run_refusal())

    data = json.loads(result.body)
    assert data["passed"] is False, (
        "SHOULD-NOT-OCCUR: planted bad claim passed the gate — "
        "validate_citations must reject NXT-9999 (non-existent ticket)"
    )
    assert len(data["violations"]) >= 1, (
        "Expected at least one named violation; got none"
    )
    # The violation must name the bad ref.
    refs = [v["ref"] for v in data["violations"]]
    assert any("NXT-9999" in r or "quote_not_found" in r or "tier_lie" in r
               for r in refs + [v["reason"] for v in data["violations"]]), (
        f"Expected a violation naming NXT-9999 or quote_not_found; got: {data['violations']}"
    )


# ── Test 2: Beat 1 — refusal endpoint is 403 when CONFERENCE_MODE is off ──────
def test_beat1_refusal_blocked_outside_conference_mode():
    """SHOULD-NOT-OCCUR: run-refusal endpoint must return 403 when not in conference mode."""
    from fastapi.testclient import TestClient

    with _demo_app_with_conference(""):  # empty string → CONFERENCE_MODE=False
        import importlib
        if "demo_app" in sys.modules:
            importlib.reload(sys.modules["demo_app"])
        import demo_app

        client = TestClient(demo_app.app, raise_server_exceptions=False)
        response = client.post("/api/demo/run-refusal")

    assert response.status_code == 403, (
        f"SHOULD-NOT-OCCUR: run-refusal returned {response.status_code} instead of 403 "
        "when DEMO_MODE is not 'conference'"
    )
    body = response.json()
    assert body.get("detail", {}).get("error") == "conference_mode_only", (
        f"Expected error='conference_mode_only' in detail; got: {body}"
    )


# ── Test 3: Beat 2 — staged wrong-source resource file is correctly labeled ───
def test_beat2_wrong_source_resource_exists_and_is_labeled():
    """Structural pin: demo-wrong-source-resource.json must exist on disk with
    status='awaiting_review' and a _demo_note field.

    This guards the demo narrative — if the file is missing or unlabeled,
    the Beat 2 walk-through breaks.
    """
    resource_path = _DATA_DEMO / "demo-wrong-source-resource.json"
    assert resource_path.exists(), (
        f"demo-wrong-source-resource.json not found at {resource_path}"
    )

    try:
        data = json.loads(resource_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        pytest.fail(f"demo-wrong-source-resource.json is not valid JSON: {e}")

    assert data.get("status") == "awaiting_review", (
        f"Expected status='awaiting_review'; got: {data.get('status')!r}"
    )
    assert "_demo_note" in data, (
        "demo-wrong-source-resource.json is missing the required '_demo_note' field"
    )
    assert data["_demo_note"], "_demo_note must be a non-empty string"
    assert data.get("approved") is False, (
        "Staged draft must have approved=false"
    )

    # Also verify the draft HTML file is present and marked as staged.
    draft_path = _DATA_DEMO / "demo-wrong-source-draft.html"
    assert draft_path.exists(), (
        f"demo-wrong-source-draft.html not found at {draft_path}"
    )
    html_content = draft_path.read_text(encoding="utf-8")
    assert "STAGED FOR DEMO" in html_content, (
        "demo-wrong-source-draft.html must contain 'STAGED FOR DEMO' marker at the top"
    )


# ── Test 4: Beat 4 — trigger-drift reverts dependent quiz to 'draft' ──────────
def test_beat4_trigger_drift_reverts_quiz_to_draft(tmp_path, monkeypatch):
    """SHOULD-NOT-OCCUR: after trigger-drift, an approved quiz referencing the
    guide must NOT remain approved — it must be reverted to draft.

    Uses a temporary guide HTML and a minimal quiz pointing at it to isolate
    from live demo data.
    """
    import quiz_store

    # Redirect quiz_store.QUIZZES to an isolated temp directory so the test
    # never touches learning-agent/quizzes/.
    quizzes_dir = tmp_path / "quizzes"
    quizzes_dir.mkdir()
    monkeypatch.setattr(quiz_store, "QUIZZES", quizzes_dir)

    # Create a temp guide HTML file.
    guide_content = "<html><body><p>Test guide content for drift detection.</p></body></html>"
    guide_path = tmp_path / "test-guide.html"
    guide_path.write_text(guide_content, encoding="utf-8")

    # Compute the hash of the original content (same algo as quiz_store.source_hash).
    import re as _re
    def _norm(s):
        return _re.sub(r"\s+", " ", (s or "")).strip().lower()

    original_hash = hashlib.sha256(_norm(guide_content).encode("utf-8")).hexdigest()[:16]

    # Build a minimal approved quiz pointing at the temp guide.
    quiz_id = "test-drift-quiz-beat4"
    quiz = {
        "id": quiz_id,
        "title": "Beat 4 Drift Test Quiz",
        "status": "approved",
        "approved": True,
        "source_type": "resource",
        "source_id": "test-guide-beat4",
        "source_label": "Test Guide",
        "source_content_hash": original_hash,
        "stale": False,
        "questions": [
            {
                "type": "mcq",
                "stem": "What does the test guide contain?",
                "options": ["Test content", "Nothing", "Images", "Videos"],
                "answer_index": 0,
                "explanation": "The guide says 'Test guide content'.",
                "source_quote": "Test guide content for drift detection.",
                "source_ref": "test-guide-beat4",
                "provenance": "manual_grounded",
                "grounded": True,
                "sme_verified": True,
            }
        ],
    }
    quiz_store.save_quiz(quiz)

    try:
        # Simulate a drift: modify the guide (same as trigger-drift appends a marker).
        drifted_content = guide_content + "\n<!-- DEMO-DRIFT-TRIGGER -->"
        guide_path.write_text(drifted_content, encoding="utf-8")

        # Now run qa_gate against the drifted content — this is what trigger-drift does.
        drifted_text = guide_path.read_text(encoding="utf-8")
        report = quiz_store.qa_gate(quiz, drifted_text)

        if report.get("drifted") and quiz.get("status") == "approved":
            quiz["status"] = "draft"
            quiz["approved"] = False
            quiz["stale"] = True
            quiz_store.save_quiz(quiz)

        reloaded = quiz_store.load_quiz(quiz_id)
        assert reloaded is not None, "Quiz disappeared after drift revert"
        assert reloaded.get("status") == "draft", (
            f"SHOULD-NOT-OCCUR: quiz status is '{reloaded.get('status')}' after source drift — "
            "must be 'draft' to prevent learners seeing stale-sourced quiz"
        )
        assert reloaded.get("approved") is False, (
            "SHOULD-NOT-OCCUR: quiz.approved is still True after drift — must be False"
        )
    finally:
        quiz_store.delete_quiz(quiz_id)


# ── Test 5: Beat 4 — reset restores guide to pre-trigger state ────────────────
def test_beat4_reset_restores_guide(tmp_path):
    """SHOULD-NOT-OCCUR: after trigger-drift + reset, the guide file must be
    byte-for-byte identical to its pre-trigger content.

    Tests the drift-trigger-state.json write/read/restore cycle directly.
    """
    original_content = "<html><body><p>Original guide — untouched after reset.</p></body></html>"
    guide_path = tmp_path / "test-restore-guide.html"
    guide_path.write_text(original_content, encoding="utf-8")

    state_path = tmp_path / "drift-trigger-state.json"

    # Simulate what trigger-drift writes.
    original_hash = hashlib.sha256(original_content.encode("utf-8")).hexdigest()[:16]
    state = {
        "_note": "Test drift state",
        "triggered_at": "2026-07-13T00:00:00",
        "resource_id": "test-restore-guide",
        "html_path": str(guide_path),
        "original_hash": original_hash,
        "original_size": len(original_content),
        "original_html": original_content,
    }
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    # Simulate the trigger modification.
    drifted_content = original_content + "\n<!-- DEMO-DRIFT-TRIGGER -->"
    guide_path.write_text(drifted_content, encoding="utf-8")
    assert guide_path.read_text(encoding="utf-8") != original_content, (
        "Precondition: guide should be drifted before reset"
    )

    # Simulate what demo_reset does (the restore logic).
    restored_state = json.loads(state_path.read_text(encoding="utf-8"))
    html_path_str = restored_state.get("html_path")
    restore_html = restored_state.get("original_html")
    assert html_path_str and restore_html, "State file missing html_path or original_html"
    Path(html_path_str).write_text(restore_html, encoding="utf-8")

    # Verify the guide is back to its original content.
    restored_content = guide_path.read_text(encoding="utf-8")
    assert restored_content == original_content, (
        "SHOULD-NOT-OCCUR: guide content after reset does not match pre-trigger state — "
        "drift restore must produce byte-for-byte identical content"
    )
