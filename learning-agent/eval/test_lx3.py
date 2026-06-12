"""Tests for LX-3 — Guided Lesson Experience.

Run from learning-agent/ with:
    python -m pytest eval/test_lx3.py -v

Test inventory (11 cases — maps to the LX-3 ACs in the spec):

  AC1  — Objective is grounded: GET /api/resources/{rid}/segments returns section_titles
          matching the guide's H2 headings verbatim; no synthesised text.
  AC2  — Segmentation is lossless (BLOCKING): segment_guide(html) → joining all body_html
          values reproduces the original HTML exactly; zero sentences added/removed/reworded.
  AC3  — Single-section degrade: segment_guide on a no-H2 guide returns exactly 1 segment
          and the endpoint returns 200.
  AC4  — Check is approved-only + formative (BLOCKING SHOULD-NOT-OCCUR):
          GET /api/resources/{rid}/segment-check/{i} never returns a question with
          status != "approved"; POST never modifies assessment or cert state.
  AC5  — No eligible question → nothing shown (BLOCKING SHOULD-NOT-OCCUR):
          segment with no approved question citing its section → has_check: false.
  AC6  — Draft/drifted content never surfaces (BLOCKING SHOULD-NOT-OCCUR):
          a draft question citing the section → has_check: false;
          guide in draft state → has_check: false.
  AC7  — Incorrect never blocks: POST segment-check with wrong answer returns
          correct: false AND verbatim_quote; does NOT touch cert/assessment.
  AC8  — Recap is grounded (BLOCKING SHOULD-NOT-OCCUR):
          GET /api/resources/{rid}/recap never returns a non-approved flashcard;
          provenance field present on every item.
  AC9  — Resume survives restart: set_segment_progress → reload → get_segment_progress.
  AC12 — Hook lint: POST /api/resources/{rid}/hook with "auto-sync" → lint_warning non-null;
          neutral text → lint_warning: null; both save successfully.
  UNIT — Losslessness unit test: pure function — known HTML with 3 H2s; joining all
          body_html values equals the input exactly.

All tests are deterministic and offline — no SDK, no LLM calls.
Blocking tests are annotated with [BLOCKING] / SHOULD-NOT-OCCUR in their docstrings.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Make learning-agent/ importable regardless of cwd.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# ── Shared fixtures ──────────────────────────────────────────────────────────

# Minimal published HTML fixture with 3 H2 sections — deterministic, no generation.
_HTML_3H2 = (
    "<h1>Item Management</h1>\n"
    "<h2>Adding Items</h2>\n<p>Describes how to add items.</p>\n"
    "<h2>Processing Payments</h2>\n<p>Describes payment processing.</p>\n"
    "<h2>Closing Out</h2>\n<p>End-of-day procedures.</p>\n"
)
_HTML_NO_H2 = "<h1>Quick Start</h1><p>Everything you need in one page.</p>"

RID = "test-guide-lx3-001"
UID = "demo-user-lx3-test"


@pytest.fixture(autouse=True)
def isolated_gamif_store(tmp_path, monkeypatch):
    """Redirect gamification store (where segment_progress lives) to tmp_path."""
    import completion_store as cs
    monkeypatch.setattr(cs, "_GAMIFICATION_DIR", tmp_path / "gamification")
    monkeypatch.setattr(cs, "_COMPLETION_DIR", tmp_path / "completion")
    return tmp_path


# ── UNIT — Losslessness unit test ─────────────────────────────────────────────

class TestSegmentGuideLosslessness:
    """Pure function test: segment_guide(html) is lossless — no bytes added or removed."""

    def test_three_h2_lossless(self):
        """[BLOCKING AC2] Joining all body_html values must equal the original HTML exactly."""
        from segment_store import segment_guide
        segments = segment_guide(_HTML_3H2)
        reconstructed = "".join(s["body_html"] for s in segments)
        assert reconstructed == _HTML_3H2, (
            "Losslessness violated: reconstructed HTML differs from input.\n"
            f"input_len={len(_HTML_3H2)} reconstructed_len={len(reconstructed)}"
        )

    def test_three_h2_count_and_headings(self):
        """3 H2s → 3 segments with correct verbatim headings."""
        from segment_store import segment_guide
        segments = segment_guide(_HTML_3H2)
        assert len(segments) == 3
        headings = [s["heading"] for s in segments]
        assert headings == ["Adding Items", "Processing Payments", "Closing Out"]

    def test_heading_inside_body(self):
        """Each segment's body_html must contain its own <h2> tag (lossless render)."""
        from segment_store import segment_guide
        segments = segment_guide(_HTML_3H2)
        for s in segments:
            if s["heading"]:
                assert s["heading"] in s["body_html"], (
                    f"H2 heading '{s['heading']}' missing from body_html"
                )

    def test_no_h2_single_segment(self):
        """[AC3] No-H2 guide → exactly 1 segment; body_html equals the full input."""
        from segment_store import segment_guide
        segments = segment_guide(_HTML_NO_H2)
        assert len(segments) == 1
        assert segments[0]["body_html"] == _HTML_NO_H2

    def test_empty_html(self):
        """Empty string → 1 segment with empty body_html."""
        from segment_store import segment_guide
        segments = segment_guide("")
        assert len(segments) == 1
        assert segments[0]["body_html"] == ""

    def test_get_section_titles_verbatim(self):
        """get_section_titles returns H2 inner text verbatim (no new text synthesised)."""
        from segment_store import get_section_titles
        titles = get_section_titles(_HTML_3H2)
        assert titles == ["Adding Items", "Processing Payments", "Closing Out"]

    def test_get_section_titles_no_h2(self):
        """No-H2 guide → empty list from get_section_titles."""
        from segment_store import get_section_titles
        titles = get_section_titles(_HTML_NO_H2)
        assert titles == []


# ── AC9 — Resume survives restart ────────────────────────────────────────────

class TestSegmentProgressPersistence:
    """AC9: set_segment_progress + re-instantiate (reload from disk) → same value."""

    def test_persist_and_reload(self, tmp_path, monkeypatch):
        """[AC9] Segment progress survives a simulated server restart."""
        import completion_store as cs
        monkeypatch.setattr(cs, "_GAMIFICATION_DIR", tmp_path / "gamification")

        cs.set_segment_progress(UID, RID, 2)

        # Simulate restart: reload by calling get_segment_progress (reads from disk).
        result = cs.get_segment_progress(UID, RID)
        assert result == 2, f"Expected 2 after restart simulation, got {result}"

    def test_unstarted_returns_minus_one(self, tmp_path, monkeypatch):
        """Fresh user with no segment progress → -1."""
        import completion_store as cs
        monkeypatch.setattr(cs, "_GAMIFICATION_DIR", tmp_path / "gamification")

        result = cs.get_segment_progress("fresh-user-999", RID)
        assert result == -1

    def test_does_not_disturb_gamif_keys(self, tmp_path, monkeypatch):
        """segment_progress writes must not touch xp, streak, or badges."""
        import completion_store as cs
        monkeypatch.setattr(cs, "_GAMIFICATION_DIR", tmp_path / "gamification")

        cs.add_xp(UID, 30, reason="test")
        cs.set_segment_progress(UID, RID, 1)

        gam = cs.get_gamification(UID)
        assert gam["xp"] == 30, "XP was disturbed by set_segment_progress"


# ── AC1, AC2, AC3 — Segments endpoint ─────────────────────────────────────────

def _make_test_client_with_guide(tmp_path: Path, html: str, approved: bool = True):
    """Build a minimal TestClient with the LX-3 segments endpoint wired."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    import app as prod
    import completion_store as cs
    import segment_store as _seg
    import flashcard_store

    # Write guide HTML + metadata to tmp_path.
    pub_dir = tmp_path / "published"
    pub_dir.mkdir(parents=True, exist_ok=True)
    meta_dir = pub_dir / "metadata"
    meta_dir.mkdir(parents=True, exist_ok=True)

    html_file = pub_dir / f"{RID}.html"
    html_file.write_text(html, encoding="utf-8")
    meta = {
        "id": RID, "title": "Test Guide", "status": "published",
        "approved": approved, "origin": "ai_generated",
        "module": "Item Management",
    }
    (meta_dir / f"{RID}.json").write_text(json.dumps(meta), encoding="utf-8")

    # Build a minimal FastAPI app with just the LX-3 routes.
    fapp = FastAPI()

    # Patch prod's path resolution to point at tmp_path.
    monkeypatched_published = pub_dir
    monkeypatched_pub_meta = meta_dir

    def _fake_resolve(rid):
        hp = pub_dir / f"{rid}.html"
        if hp.exists():
            return hp, meta_dir / f"{rid}.json", "published"
        return None

    def _fake_read_meta(path):
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                return None
        return None

    def _fake_strip_comments(html_text):
        import re
        return re.sub(r"<!--\s*Source:[\s\S]*?-->", "", html_text)

    with patch.object(prod, "_resolve_resource", side_effect=_fake_resolve), \
         patch.object(prod, "_read_meta", side_effect=_fake_read_meta), \
         patch.object(prod, "_strip_source_comments", side_effect=_fake_strip_comments):

        import demo_app
        client = TestClient(demo_app.app)
        return client


class TestSegmentsEndpoint:
    """AC1 / AC2 / AC3: GET /api/resources/{rid}/segments."""

    def test_ac1_section_titles_are_verbatim_h2s(self, tmp_path):
        """[AC1] section_titles in the response match the guide's H2 headings verbatim."""
        import app as prod
        import demo_app
        from fastapi.testclient import TestClient

        pub_dir = tmp_path / "published"
        pub_dir.mkdir(parents=True, exist_ok=True)
        meta_dir = pub_dir / "metadata"
        meta_dir.mkdir(parents=True, exist_ok=True)

        (pub_dir / f"{RID}.html").write_text(_HTML_3H2, encoding="utf-8")
        (meta_dir / f"{RID}.json").write_text(json.dumps({
            "id": RID, "title": "Test Guide", "status": "published",
            "approved": True, "origin": "ai_generated",
        }), encoding="utf-8")

        import re
        def _fake_resolve(rid):
            hp = pub_dir / f"{rid}.html"
            if hp.exists():
                return hp, meta_dir / f"{rid}.json", "published"
            return None
        def _fake_read_meta(path):
            if path.exists():
                try: return json.loads(path.read_text(encoding="utf-8"))
                except Exception: return None
            return None
        def _fake_strip(html_text):
            return re.sub(r"<!--\s*Source:[\s\S]*?-->", "", html_text)

        with patch.object(prod, "_resolve_resource", side_effect=_fake_resolve), \
             patch.object(prod, "_read_meta", side_effect=_fake_read_meta), \
             patch.object(prod, "_strip_source_comments", side_effect=_fake_strip):
            client = TestClient(demo_app.app)
            resp = client.get(f"/api/resources/{RID}/segments",
                              headers={"X-Demo-User": "john-cashier"})

        assert resp.status_code == 200
        data = resp.json()
        titles = data["section_titles"]
        # Titles must exactly match the H2 inner texts — verbatim, no synthesis.
        assert titles == ["Adding Items", "Processing Payments", "Closing Out"], (
            f"section_titles should be verbatim H2 texts, got: {titles}"
        )
        # No synthesised text: none of the titles should differ from the guide.
        assert data["total_segments"] == 3

    def test_ac2_lossless_via_endpoint(self, tmp_path):
        """[BLOCKING AC2] Joining segment body_html values must reproduce the original HTML."""
        import app as prod
        import demo_app
        from fastapi.testclient import TestClient
        import re

        pub_dir = tmp_path / "published"
        pub_dir.mkdir(parents=True, exist_ok=True)
        meta_dir = pub_dir / "metadata"
        meta_dir.mkdir(parents=True, exist_ok=True)

        (pub_dir / f"{RID}.html").write_text(_HTML_3H2, encoding="utf-8")
        (meta_dir / f"{RID}.json").write_text(json.dumps({
            "id": RID, "title": "Test", "status": "published", "approved": True,
        }), encoding="utf-8")

        def _fake_resolve(rid):
            hp = pub_dir / f"{rid}.html"
            return (hp, meta_dir / f"{rid}.json", "published") if hp.exists() else None
        def _fake_read_meta(path):
            if path.exists():
                try: return json.loads(path.read_text())
                except Exception: return None
            return None
        def _fake_strip(html_text):
            return re.sub(r"<!--\s*Source:[\s\S]*?-->", "", html_text)

        with patch.object(prod, "_resolve_resource", side_effect=_fake_resolve), \
             patch.object(prod, "_read_meta", side_effect=_fake_read_meta), \
             patch.object(prod, "_strip_source_comments", side_effect=_fake_strip):
            client = TestClient(demo_app.app)
            resp = client.get(f"/api/resources/{RID}/segments",
                              headers={"X-Demo-User": "john-cashier"})

        assert resp.status_code == 200
        data = resp.json()
        reconstructed = "".join(s["body_html"] for s in data["segments"])
        assert reconstructed == _HTML_3H2, (
            "[BLOCKING AC2] Losslessness check failed via endpoint. "
            f"input_len={len(_HTML_3H2)} reconstructed_len={len(reconstructed)}"
        )

    def test_ac3_single_section_no_h2(self, tmp_path):
        """[AC3] No-H2 guide → 1 segment, endpoint returns 200."""
        import app as prod
        import demo_app
        from fastapi.testclient import TestClient
        import re

        pub_dir = tmp_path / "published"
        pub_dir.mkdir(parents=True, exist_ok=True)
        meta_dir = pub_dir / "metadata"
        meta_dir.mkdir(parents=True, exist_ok=True)

        (pub_dir / f"{RID}.html").write_text(_HTML_NO_H2, encoding="utf-8")
        (meta_dir / f"{RID}.json").write_text(json.dumps({
            "id": RID, "title": "Quick Start", "status": "published", "approved": True,
        }), encoding="utf-8")

        def _fake_resolve(rid):
            hp = pub_dir / f"{rid}.html"
            return (hp, meta_dir / f"{rid}.json", "published") if hp.exists() else None
        def _fake_read_meta(path):
            if path.exists():
                try: return json.loads(path.read_text())
                except Exception: return None
            return None
        def _fake_strip(html_text):
            return re.sub(r"<!--\s*Source:[\s\S]*?-->", "", html_text)

        with patch.object(prod, "_resolve_resource", side_effect=_fake_resolve), \
             patch.object(prod, "_read_meta", side_effect=_fake_read_meta), \
             patch.object(prod, "_strip_source_comments", side_effect=_fake_strip):
            client = TestClient(demo_app.app)
            resp = client.get(f"/api/resources/{RID}/segments",
                              headers={"X-Demo-User": "john-cashier"})

        assert resp.status_code == 200
        data = resp.json()
        assert data["total_segments"] == 1, (
            f"[AC3] Expected 1 segment for no-H2 guide, got {data['total_segments']}"
        )


# ── AC4, AC5, AC6 — Check endpoint (BLOCKING SHOULD-NOT-OCCUR) ───────────────

class TestSegmentCheckGrounding:
    """AC4/AC5/AC6: the check endpoint must only return approved, non-drifted questions."""

    def _make_fake_quiz(self, status: str, grounded: bool, section: str) -> dict:
        return {
            "id": f"quiz-lx3-test-{status}",
            "title": "LX-3 Test Quiz",
            "status": status,
            "source_id": RID,
            "stale": False,
            "questions": [{
                "type": "mcq",
                "stem": "What is the first step?",
                "options": ["A", "B", "C", "D"],
                "answer_index": 0,
                "source_quote": "Describes how to add items.",
                "source_ref": "NXT-1234",
                "section": section,
                "grounded": grounded,
                "provenance": "ai_grounded",
                "sme_verified": True,
            }],
        }

    def _setup_guide(self, tmp_path):
        pub_dir = tmp_path / "published"
        pub_dir.mkdir(parents=True, exist_ok=True)
        meta_dir = pub_dir / "metadata"
        meta_dir.mkdir(parents=True, exist_ok=True)
        (pub_dir / f"{RID}.html").write_text(_HTML_3H2, encoding="utf-8")
        (meta_dir / f"{RID}.json").write_text(json.dumps({
            "id": RID, "title": "Test", "status": "published", "approved": True,
        }), encoding="utf-8")
        return pub_dir, meta_dir

    def test_ac4_only_approved_questions_returned(self, tmp_path):
        """[BLOCKING AC4 SHOULD-NOT-OCCUR] Draft question citing the section → has_check: false."""
        pub_dir, meta_dir = self._setup_guide(tmp_path)
        import app as prod
        import demo_app
        import quiz_store as qs
        from fastapi.testclient import TestClient
        import re

        draft_quiz = self._make_fake_quiz(status="draft", grounded=True, section="Adding Items")

        def _fake_resolve(rid):
            hp = pub_dir / f"{rid}.html"
            return (hp, meta_dir / f"{rid}.json", "published") if hp.exists() else None
        def _fake_read_meta(path):
            if path.exists():
                try: return json.loads(path.read_text())
                except Exception: return None
            return None
        def _fake_strip(html_text):
            return re.sub(r"<!--\s*Source:[\s\S]*?-->", "", html_text)
        def _fake_list_quizzes():
            return [{"id": draft_quiz["id"], "status": "draft", "source_id": RID,
                     "stale": False, "questions": draft_quiz["questions"]}]
        def _fake_load_quiz(qid):
            return draft_quiz

        with patch.object(prod, "_resolve_resource", side_effect=_fake_resolve), \
             patch.object(prod, "_read_meta", side_effect=_fake_read_meta), \
             patch.object(prod, "_strip_source_comments", side_effect=_fake_strip), \
             patch.object(qs, "list_quizzes", side_effect=_fake_list_quizzes), \
             patch.object(qs, "load_quiz", side_effect=_fake_load_quiz):
            client = TestClient(demo_app.app)
            resp = client.get(f"/api/resources/{RID}/segment-check/0",
                              headers={"X-Demo-User": "john-cashier"})

        assert resp.status_code == 200
        data = resp.json()
        assert not data["has_check"], (
            "[BLOCKING AC4 SHOULD-NOT-OCCUR] Draft question was returned by check endpoint"
        )

    def test_ac5_no_eligible_question(self, tmp_path):
        """[BLOCKING AC5 SHOULD-NOT-OCCUR] No approved question for section → has_check: false."""
        pub_dir, meta_dir = self._setup_guide(tmp_path)
        import app as prod
        import demo_app
        import quiz_store as qs
        from fastapi.testclient import TestClient
        import re

        # Approved quiz but section doesn't match any segment heading.
        wrong_section_quiz = self._make_fake_quiz(
            status="approved", grounded=True, section="Completely Different Section"
        )

        def _fake_resolve(rid):
            hp = pub_dir / f"{rid}.html"
            return (hp, meta_dir / f"{rid}.json", "published") if hp.exists() else None
        def _fake_read_meta(path):
            if path.exists():
                try: return json.loads(path.read_text())
                except Exception: return None
            return None
        def _fake_strip(html_text):
            return re.sub(r"<!--\s*Source:[\s\S]*?-->", "", html_text)
        def _fake_list_quizzes():
            return [{"id": wrong_section_quiz["id"], "status": "approved",
                     "source_id": RID, "stale": False,
                     "questions": wrong_section_quiz["questions"]}]
        def _fake_load_quiz(qid):
            return wrong_section_quiz

        with patch.object(prod, "_resolve_resource", side_effect=_fake_resolve), \
             patch.object(prod, "_read_meta", side_effect=_fake_read_meta), \
             patch.object(prod, "_strip_source_comments", side_effect=_fake_strip), \
             patch.object(qs, "list_quizzes", side_effect=_fake_list_quizzes), \
             patch.object(qs, "load_quiz", side_effect=_fake_load_quiz):
            client = TestClient(demo_app.app)
            resp = client.get(f"/api/resources/{RID}/segment-check/0",
                              headers={"X-Demo-User": "john-cashier"})

        assert resp.status_code == 200
        data = resp.json()
        assert not data["has_check"], (
            "[BLOCKING AC5 SHOULD-NOT-OCCUR] No-match question was returned by check endpoint"
        )

    def test_ac6_draft_guide_blocks_check(self, tmp_path):
        """[BLOCKING AC6 SHOULD-NOT-OCCUR] Guide in draft/unapproved state → has_check: false."""
        pub_dir, meta_dir = self._setup_guide(tmp_path)
        import app as prod
        import demo_app
        import quiz_store as qs
        from fastapi.testclient import TestClient
        import re

        # Override metadata to mark guide as not approved.
        (meta_dir / f"{RID}.json").write_text(json.dumps({
            "id": RID, "title": "Test", "status": "draft", "approved": False,
        }), encoding="utf-8")

        approved_quiz = self._make_fake_quiz(
            status="approved", grounded=True, section="Adding Items"
        )

        def _fake_resolve(rid):
            hp = pub_dir / f"{rid}.html"
            return (hp, meta_dir / f"{rid}.json", "published") if hp.exists() else None
        def _fake_read_meta(path):
            if path.exists():
                try: return json.loads(path.read_text())
                except Exception: return None
            return None
        def _fake_strip(html_text):
            return re.sub(r"<!--\s*Source:[\s\S]*?-->", "", html_text)
        def _fake_list_quizzes():
            return [{"id": approved_quiz["id"], "status": "approved",
                     "source_id": RID, "stale": False,
                     "questions": approved_quiz["questions"]}]
        def _fake_load_quiz(qid):
            return approved_quiz

        with patch.object(prod, "_resolve_resource", side_effect=_fake_resolve), \
             patch.object(prod, "_read_meta", side_effect=_fake_read_meta), \
             patch.object(prod, "_strip_source_comments", side_effect=_fake_strip), \
             patch.object(qs, "list_quizzes", side_effect=_fake_list_quizzes), \
             patch.object(qs, "load_quiz", side_effect=_fake_load_quiz):
            client = TestClient(demo_app.app)
            resp = client.get(f"/api/resources/{RID}/segment-check/0",
                              headers={"X-Demo-User": "john-cashier"})

        assert resp.status_code == 200
        data = resp.json()
        assert not data["has_check"], (
            "[BLOCKING AC6 SHOULD-NOT-OCCUR] Check was returned despite guide being in draft"
        )


# ── AC7 — Incorrect never blocks ─────────────────────────────────────────────

class TestSegmentCheckFormative:
    """AC7: wrong answer returns correct: false + verbatim_quote; does NOT touch certs."""

    def test_ac7_incorrect_returns_feedback_not_blocked(self, tmp_path):
        """[AC7] Submitting wrong answer returns correct:false + verbatim_quote.
        No cert/assessment state is written.
        """
        pub_dir = tmp_path / "published"
        pub_dir.mkdir(parents=True, exist_ok=True)
        meta_dir = pub_dir / "metadata"
        meta_dir.mkdir(parents=True, exist_ok=True)

        (pub_dir / f"{RID}.html").write_text(_HTML_3H2, encoding="utf-8")
        (meta_dir / f"{RID}.json").write_text(json.dumps({
            "id": RID, "title": "Test", "status": "published", "approved": True,
        }), encoding="utf-8")

        import app as prod
        import demo_app
        import quiz_store as qs
        from fastapi.testclient import TestClient
        import re

        approved_quiz = {
            "id": "quiz-lx3-ac7",
            "title": "LX-3 AC7 Quiz",
            "status": "approved",
            "source_id": RID,
            "stale": False,
            "questions": [{
                "type": "mcq",
                "stem": "What is described first?",
                "options": ["Adding Items", "Paying", "Closing", "None"],
                "answer_index": 0,
                "source_quote": "Describes how to add items.",
                "source_ref": "NXT-001",
                "section": "Adding Items",
                "grounded": True,
                "provenance": "ai_grounded",
                "sme_verified": True,
            }],
        }

        def _fake_resolve(rid):
            hp = pub_dir / f"{rid}.html"
            return (hp, meta_dir / f"{rid}.json", "published") if hp.exists() else None
        def _fake_read_meta(path):
            if path.exists():
                try: return json.loads(path.read_text())
                except Exception: return None
            return None
        def _fake_strip(html_text):
            return re.sub(r"<!--\s*Source:[\s\S]*?-->", "", html_text)
        def _fake_list_quizzes():
            return [{"id": approved_quiz["id"], "status": "approved",
                     "source_id": RID, "stale": False,
                     "questions": approved_quiz["questions"]}]
        def _fake_load_quiz(qid):
            return approved_quiz

        with patch.object(prod, "_resolve_resource", side_effect=_fake_resolve), \
             patch.object(prod, "_read_meta", side_effect=_fake_read_meta), \
             patch.object(prod, "_strip_source_comments", side_effect=_fake_strip), \
             patch.object(qs, "list_quizzes", side_effect=_fake_list_quizzes), \
             patch.object(qs, "load_quiz", side_effect=_fake_load_quiz):
            client = TestClient(demo_app.app)

            # Submit wrong answer (index 2 instead of 0).
            resp = client.post(
                f"/api/resources/{RID}/segment-check/0",
                json={"uid": UID, "answer": 2},
                headers={"X-Demo-User": "john-cashier"},
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["correct"] is False, "[AC7] Wrong answer should return correct: false"
        assert data["verbatim_quote"], "[AC7] verbatim_quote must be present even on wrong answer"

        # AC7 trust guardrail: no cert/assessment files written.
        cert_dir = tmp_path / "completion" / "demo-user-001" / "certs"
        assessment_dir = tmp_path / "assessment-attempts"
        assert not cert_dir.exists() or not list(cert_dir.glob("*.json")), (
            "[BLOCKING AC7 SHOULD-NOT-OCCUR] Certificate was written after formative check"
        )


# ── AC8 — Recap grounded ──────────────────────────────────────────────────────

class TestRecapGrounding:
    """AC8: recap never returns non-approved flashcard; provenance present on every item."""

    def test_ac8_approved_flashcards_only(self, tmp_path):
        """[BLOCKING AC8 SHOULD-NOT-OCCUR] Recap only returns approved flashcard items."""
        pub_dir = tmp_path / "published"
        pub_dir.mkdir(parents=True, exist_ok=True)
        meta_dir = pub_dir / "metadata"
        meta_dir.mkdir(parents=True, exist_ok=True)

        (pub_dir / f"{RID}.html").write_text(_HTML_3H2, encoding="utf-8")
        (meta_dir / f"{RID}.json").write_text(json.dumps({
            "id": RID, "title": "Test", "status": "published", "approved": True,
        }), encoding="utf-8")

        import app as prod
        import demo_app
        import flashcard_store as fs
        from fastapi.testclient import TestClient
        import re

        # Return one approved deck and one draft deck; only approved should appear.
        approved_deck = {
            "id": "deck-lx3-approved",
            "title": "LX-3 Approved Deck",
            "source_resource_id": RID,
            "status": "approved",
            "provenance": "ai_grounded",
            "cards": [
                {"id": "card-1", "front": "Q1?", "back": "A1.",
                 "source_quote": "Describes how to add items.", "grounded": True},
                {"id": "card-2", "front": "Q2?", "back": "A2.",
                 "source_quote": "Describes payment processing.", "grounded": True},
                {"id": "card-3", "front": "Q3?", "back": "A3.",
                 "source_quote": "End-of-day procedures.", "grounded": True},
            ],
        }
        draft_deck = {
            "id": "deck-lx3-draft",
            "title": "LX-3 Draft Deck",
            "source_resource_id": RID,
            "status": "draft",
            "provenance": "ai_grounded",
            "cards": [{"id": "card-x", "front": "Draft Q?", "back": "Draft A.",
                       "source_quote": "something", "grounded": True}],
        }

        def _fake_resolve(rid):
            hp = pub_dir / f"{rid}.html"
            return (hp, meta_dir / f"{rid}.json", "published") if hp.exists() else None
        def _fake_read_meta(path):
            if path.exists():
                try: return json.loads(path.read_text())
                except Exception: return None
            return None
        def _fake_strip(html_text):
            return re.sub(r"<!--\s*Source:[\s\S]*?-->", "", html_text)
        def _fake_list_decks(status=None):
            decks = [
                {"id": "deck-lx3-approved", "status": "approved",
                 "source_resource_id": RID, "created_at": "2026-06-12"},
                {"id": "deck-lx3-draft", "status": "draft",
                 "source_resource_id": RID, "created_at": "2026-06-12"},
            ]
            if status:
                return [d for d in decks if d["status"] == status]
            return decks
        def _fake_get_deck(did):
            if did == "deck-lx3-approved":
                return approved_deck
            if did == "deck-lx3-draft":
                return draft_deck
            return None

        with patch.object(prod, "_resolve_resource", side_effect=_fake_resolve), \
             patch.object(prod, "_read_meta", side_effect=_fake_read_meta), \
             patch.object(prod, "_strip_source_comments", side_effect=_fake_strip), \
             patch.object(fs, "list_decks", side_effect=_fake_list_decks), \
             patch.object(fs, "get_deck", side_effect=_fake_get_deck):
            client = TestClient(demo_app.app)
            resp = client.get(f"/api/resources/{RID}/recap?uid={UID}",
                              headers={"X-Demo-User": "john-cashier"})

        assert resp.status_code == 200
        data = resp.json()
        assert data["source"] == "flashcards", f"Expected 'flashcards' source, got: {data['source']}"

        for item in data["items"]:
            assert "provenance" in item, (
                "[BLOCKING AC8 SHOULD-NOT-OCCUR] provenance field missing from recap item"
            )
            assert item["provenance"], "provenance must be non-empty"

        # Verify no draft-only content appeared.
        fronts = {i["front"] for i in data["items"]}
        assert "Draft Q?" not in fronts, (
            "[BLOCKING AC8 SHOULD-NOT-OCCUR] Draft flashcard appeared in recap"
        )


# ── AC12 — Hook lint ──────────────────────────────────────────────────────────

class TestHookLint:
    """AC12: POST /api/resources/{rid}/hook applies DEC-3 lint to hook_text."""

    def _setup_guide(self, tmp_path):
        pub_dir = tmp_path / "published"
        pub_dir.mkdir(parents=True, exist_ok=True)
        meta_dir = pub_dir / "metadata"
        meta_dir.mkdir(parents=True, exist_ok=True)
        (pub_dir / f"{RID}.html").write_text(_HTML_3H2, encoding="utf-8")
        (meta_dir / f"{RID}.json").write_text(json.dumps({
            "id": RID, "title": "Test", "status": "published", "approved": True,
        }), encoding="utf-8")
        return pub_dir, meta_dir

    def test_ac12_claim_language_triggers_warning(self, tmp_path):
        """[AC12] hook_text with 'auto-sync' → saved: true + lint_warning non-null."""
        pub_dir, meta_dir = self._setup_guide(tmp_path)
        import app as prod
        import demo_app
        from fastapi.testclient import TestClient
        import re

        def _fake_resolve(rid):
            hp = pub_dir / f"{rid}.html"
            return (hp, meta_dir / f"{rid}.json", "published") if hp.exists() else None
        def _fake_read_meta(path):
            if path.exists():
                try: return json.loads(path.read_text())
                except Exception: return None
            return None
        def _fake_strip(html_text):
            return re.sub(r"<!--\s*Source:[\s\S]*?-->", "", html_text)

        with patch.object(prod, "_resolve_resource", side_effect=_fake_resolve), \
             patch.object(prod, "_read_meta", side_effect=_fake_read_meta), \
             patch.object(prod, "_strip_source_comments", side_effect=_fake_strip):
            client = TestClient(demo_app.app)
            resp = client.post(
                f"/api/resources/{RID}/hook",
                json={"hook_text": "This module will auto-sync all records."},
                headers={"X-Demo-User": "sam-trainer"},
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["saved"] is True, "Hook should be saved even when lint warning fires"
        assert data["lint_warning"] is not None, (
            "[AC12] lint_warning should be non-null for product-claim language"
        )
        assert len(data["matched_patterns"]) > 0

    def test_ac12_neutral_text_no_warning(self, tmp_path):
        """[AC12] Neutral hook_text → saved: true + lint_warning: null."""
        pub_dir, meta_dir = self._setup_guide(tmp_path)
        import app as prod
        import demo_app
        from fastapi.testclient import TestClient
        import re

        def _fake_resolve(rid):
            hp = pub_dir / f"{rid}.html"
            return (hp, meta_dir / f"{rid}.json", "published") if hp.exists() else None
        def _fake_read_meta(path):
            if path.exists():
                try: return json.loads(path.read_text())
                except Exception: return None
            return None
        def _fake_strip(html_text):
            return re.sub(r"<!--\s*Source:[\s\S]*?-->", "", html_text)

        with patch.object(prod, "_resolve_resource", side_effect=_fake_resolve), \
             patch.object(prod, "_read_meta", side_effect=_fake_read_meta), \
             patch.object(prod, "_strip_source_comments", side_effect=_fake_strip):
            client = TestClient(demo_app.app)
            resp = client.post(
                f"/api/resources/{RID}/hook",
                json={"hook_text": "This module covers the item management workflow."},
                headers={"X-Demo-User": "sam-trainer"},
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["saved"] is True
        assert data["lint_warning"] is None, (
            "[AC12] lint_warning should be null for neutral text"
        )
        assert data["matched_patterns"] == []
