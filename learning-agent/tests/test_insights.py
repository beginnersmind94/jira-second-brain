"""Tests for E3-lite — Educator insight panel (seeded).

Run from learning-agent/ with:
    python -m pytest eval/test_insights.py -v

Test inventory (5 cases):

  TC-E3-01: GET /api/analytics/tracks/<tid>/insights returns funnel and
            question_difficulty arrays.
  TC-E3-02: SHOULD-NOT-OCCUR — response must include _data_notice field.
            Missing data notice is a honesty violation (non-negotiable).
  TC-E3-03: SHOULD-NOT-OCCUR — response funnel and question_difficulty rows
            must not contain user_id or user_ids fields (aggregate-only rule).
  TC-E3-04: Cashier persona gets 403 (aggregate analytics are trainer/director only).
  TC-E3-05: data/analytics/ seeded file exists on disk (structural — ensures
            the demo has data to show).

All tests are deterministic and offline — no SDK, no LLM calls.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Make learning-agent/ importable regardless of cwd.
_LA = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_LA))

_ANALYTICS_DIR = _LA / "data" / "analytics"
_SEEDED_FILE   = _ANALYTICS_DIR / "track-insights-demo.json"


# ── Fixture: isolated completion store ───────────────────────────────────────

@pytest.fixture(autouse=True)
def isolated_completion_store(tmp_path, monkeypatch):
    """Redirect completion_store file I/O to tmp_path for test isolation."""
    import completion_store as cs
    monkeypatch.setattr(cs, "_COMPLETION_DIR", tmp_path / "completion")
    return tmp_path / "completion"


# ── Helpers ───────────────────────────────────────────────────────────────────

TRACK_ID = "track-cashier-onboard"


def _make_app():
    """Build a minimal FastAPI test client with the insights route registered."""
    from fastapi.testclient import TestClient
    import demo_app
    return TestClient(demo_app.app, raise_server_exceptions=True)


# ─────────────────────────────────────────────────────────────────────────────
# TC-E3-01: Endpoint returns funnel and question_difficulty arrays
# ─────────────────────────────────────────────────────────────────────────────

class TestInsightsReturnsArrays:
    """GET /api/analytics/tracks/<tid>/insights returns funnel and question_difficulty."""

    def test_funnel_and_question_difficulty_present(self):
        client = _make_app()
        resp = client.get(
            f"/api/analytics/tracks/{TRACK_ID}/insights",
            headers={"X-Demo-User": "sam-trainer"},
        )
        assert resp.status_code == 200, (
            f"Expected 200 from insights endpoint for trainer, got {resp.status_code}: {resp.text}"
        )
        data = resp.json()
        assert "funnel" in data, (
            f"Response missing 'funnel' array: {list(data.keys())}"
        )
        assert "question_difficulty" in data, (
            f"Response missing 'question_difficulty' array: {list(data.keys())}"
        )
        assert isinstance(data["funnel"], list), (
            f"'funnel' must be a list, got {type(data['funnel'])}"
        )
        assert isinstance(data["question_difficulty"], list), (
            f"'question_difficulty' must be a list, got {type(data['question_difficulty'])}"
        )
        # Confirm data from the seeded file is actually present (visual fullness check).
        assert len(data["funnel"]) > 0, (
            "funnel array is empty — seeded data should populate at least one row"
        )
        assert len(data["question_difficulty"]) > 0, (
            "question_difficulty array is empty — seeded data should populate at least one row"
        )


# ─────────────────────────────────────────────────────────────────────────────
# TC-E3-02: SHOULD-NOT-OCCUR — _data_notice must be present
# ─────────────────────────────────────────────────────────────────────────────

class TestDataNoticePresent:
    """SHOULD-NOT-OCCUR: missing _data_notice is a honesty violation."""

    def test_data_notice_present_for_trainer(self):
        client = _make_app()
        resp = client.get(
            f"/api/analytics/tracks/{TRACK_ID}/insights",
            headers={"X-Demo-User": "sam-trainer"},
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert "_data_notice" in data, (
            "SHOULD-NOT-OCCUR: '_data_notice' field is missing from insights response. "
            "This field is required — the panel must always inform viewers that data "
            "includes seeded demonstration figures. Omitting it is a honesty violation."
        )
        notice = data["_data_notice"]
        assert isinstance(notice, str) and len(notice) > 0, (
            "SHOULD-NOT-OCCUR: '_data_notice' is empty — must be a non-empty string."
        )

    def test_data_notice_present_for_director(self):
        client = _make_app()
        resp = client.get(
            f"/api/analytics/tracks/{TRACK_ID}/insights",
            headers={"X-Demo-User": "dana-director"},
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert "_data_notice" in data, (
            "SHOULD-NOT-OCCUR: '_data_notice' missing for director persona. "
            "Every consumer of the insights panel must see the seeded-data notice."
        )


# ─────────────────────────────────────────────────────────────────────────────
# TC-E3-03: SHOULD-NOT-OCCUR — no per-learner user_id fields
# ─────────────────────────────────────────────────────────────────────────────

class TestNoPerLearnerData:
    """SHOULD-NOT-OCCUR: funnel and question_difficulty must not expose user_id."""

    def test_no_user_id_in_funnel_rows(self):
        client = _make_app()
        resp = client.get(
            f"/api/analytics/tracks/{TRACK_ID}/insights",
            headers={"X-Demo-User": "sam-trainer"},
        )
        assert resp.status_code == 200
        data = resp.json()
        forbidden = ("user_id", "user_ids", "learners")
        for row in data.get("funnel", []):
            for field in forbidden:
                assert field not in row, (
                    f"SHOULD-NOT-OCCUR: per-learner field '{field}' found in funnel row {row}. "
                    "The insight panel must be aggregate-only — no individual user records."
                )

    def test_no_user_id_in_question_difficulty_rows(self):
        client = _make_app()
        resp = client.get(
            f"/api/analytics/tracks/{TRACK_ID}/insights",
            headers={"X-Demo-User": "sam-trainer"},
        )
        assert resp.status_code == 200
        data = resp.json()
        forbidden = ("user_id", "user_ids")
        for row in data.get("question_difficulty", []):
            for field in forbidden:
                assert field not in row, (
                    f"SHOULD-NOT-OCCUR: per-learner field '{field}' found in "
                    f"question_difficulty row {row}. Aggregate-only rule violated."
                )


# ─────────────────────────────────────────────────────────────────────────────
# TC-E3-04: Cashier persona gets 403 (trainer/director only)
# ─────────────────────────────────────────────────────────────────────────────

class TestCashierForbidden:
    """Cashier persona must receive 403 — aggregate analytics are not for learners."""

    def test_cashier_gets_403(self):
        client = _make_app()
        resp = client.get(
            f"/api/analytics/tracks/{TRACK_ID}/insights",
            headers={"X-Demo-User": "john-cashier"},
        )
        assert resp.status_code == 403, (
            f"Expected 403 for cashier persona on insights endpoint, got {resp.status_code}. "
            "Aggregate analytics (completion funnel, question difficulty) must only be "
            "accessible to trainers and directors — not to individual learners."
        )


# ─────────────────────────────────────────────────────────────────────────────
# TC-E3-05: Seeded data file exists on disk (structural)
# ─────────────────────────────────────────────────────────────────────────────

class TestSeededFileExists:
    """data/analytics/track-insights-demo.json must exist for the demo to have data."""

    def test_seeded_file_on_disk(self):
        assert _SEEDED_FILE.exists(), (
            f"Seeded analytics file not found at {_SEEDED_FILE}. "
            "This file is required for the E3-lite demo panel to display data. "
            "Create it at learning-agent/data/analytics/track-insights-demo.json."
        )

    def test_seeded_file_has_valid_json(self):
        assert _SEEDED_FILE.exists(), f"File missing: {_SEEDED_FILE}"
        try:
            data = json.loads(_SEEDED_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            pytest.fail(f"Seeded file is not valid JSON: {exc}")

        assert "funnel" in data, f"Seeded file missing 'funnel' key: {list(data.keys())}"
        assert "question_difficulty" in data, (
            f"Seeded file missing 'question_difficulty' key: {list(data.keys())}"
        )
        assert "_note" in data, (
            "Seeded file missing '_note' key — the internal documentation that this is "
            "seeded demo data is required. Add a '_note' field explaining it is not live data."
        )
        note = data["_note"]
        assert "SEEDED" in note.upper() or "seeded" in note.lower(), (
            f"'_note' field does not mention that data is seeded: '{note}'. "
            "The note must make clear this is seeded demo data, not live learner events."
        )
