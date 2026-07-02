"""eval/test_showcase_library.py — G1 Demo content library: showcase tracks.

Six tests that verify the three ANC showcase tracks are correctly structured
and all lesson refs resolve to existing files on disk.

Test IDs
--------
G1-T1  All 3 showcase tracks exist with status "published"
G1-T2  Track 1 (Cashier Onboarding) has 2 courses with >= 4 total lessons
G1-T3  Track 3 (Food Safety booth) total duration_est <= 4 min (SHOULD-NOT-OCCUR gate)
G1-T4  Every lesson ref in every showcase track resolves to an existing file on disk
G1-T5  Track 1 has an ICN video lesson with embed_only or download_allowed posture
G1-T6  Cashier persona (john-cashier/Cashier role) gets Track 1 in GET /api/tracks
         role-filtering

These tests are deterministic — they read JSON files on disk, never call the LLM.
They run with: python -m pytest eval/test_showcase_library.py -v
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# ── Path bootstrap (mirrors eval/__init__.py pattern) ────────────────────────
_LEARNING_AGENT = Path(__file__).resolve().parent.parent
if str(_LEARNING_AGENT) not in sys.path:
    sys.path.insert(0, str(_LEARNING_AGENT))

# ── Directories ───────────────────────────────────────────────────────────────
_TRACKS_DIR = _LEARNING_AGENT / "data" / "tracks"
_COURSES_DIR = _LEARNING_AGENT / "data" / "courses"
_QUIZZES_DIR = _LEARNING_AGENT / "quizzes"
_FLASHCARDS_DIR = _LEARNING_AGENT / "data" / "flashcards"
_ASSESSMENTS_DIR = _LEARNING_AGENT / "data" / "assessments"
_DRAFTS_DIR = _LEARNING_AGENT / "drafts"
_PUB_META_DIR = _LEARNING_AGENT / "published" / "metadata"
_ICN_MANIFEST = _LEARNING_AGENT / "data" / "icn" / "data" / "asset_manifest.json"

# ── Showcase track IDs (canonical) ────────────────────────────────────────────
_TRACK_CASHIER = "track-g1-cashier-onboarding"
_TRACK_MANAGER = "track-g1-manager-essentials"
_TRACK_FOOD_SAFETY = "track-g1-food-safety-booth"

_SHOWCASE_TRACK_IDS = [_TRACK_CASHIER, _TRACK_MANAGER, _TRACK_FOOD_SAFETY]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _load_track(tid: str) -> dict | None:
    return _load_json(_TRACKS_DIR / f"{tid}.json")


def _load_course(cid: str) -> dict | None:
    return _load_json(_COURSES_DIR / f"{cid}.json")


def _load_icn_catalog() -> dict[str, dict]:
    """Return a dict of asset_id -> asset for every ICN asset in the manifest."""
    if not _ICN_MANIFEST.exists():
        return {}
    try:
        entries = json.loads(_ICN_MANIFEST.read_text(encoding="utf-8"))
        return {a["asset_id"]: a for a in entries if a.get("asset_id")}
    except (json.JSONDecodeError, OSError):
        return {}


def _all_showcase_lessons() -> list[tuple[str, str, dict]]:
    """Yield (track_id, course_id, lesson) for every lesson in all showcase tracks."""
    out = []
    for tid in _SHOWCASE_TRACK_IDS:
        track = _load_track(tid)
        if track is None:
            continue
        for cid in (track.get("course_ids") or []):
            course = _load_course(cid)
            if course is None:
                continue
            for lesson in (course.get("lessons") or []):
                out.append((tid, cid, lesson))
    return out


def _ref_exists_on_disk(lesson: dict) -> tuple[bool, str]:
    """Return (ok, explanation) for whether lesson.ref resolves to a real file."""
    lesson_type = (lesson.get("type") or "").strip()
    ref = (lesson.get("ref") or "").strip()

    if not ref:
        return False, "ref is empty"

    if lesson_type == "guide":
        # Try published/metadata/ then drafts/
        if (_PUB_META_DIR / f"{ref}.json").exists():
            return True, "found in published/metadata/"
        if (_DRAFTS_DIR / f"{ref}.json").exists():
            return True, "found in drafts/"
        return False, f"guide '{ref}' not found in published/metadata/ or drafts/"

    if lesson_type in ("quiz",):
        p = _QUIZZES_DIR / f"{ref}.json"
        if p.exists():
            return True, "quiz found"
        return False, f"quiz '{ref}' not found in quizzes/"

    if lesson_type == "flashcards":
        p = _FLASHCARDS_DIR / f"{ref}.json"
        if p.exists():
            return True, "flashcard deck found"
        return False, f"flashcard deck '{ref}' not found in data/flashcards/"

    if lesson_type == "assessment":
        p = _ASSESSMENTS_DIR / f"{ref}.json"
        if p.exists():
            return True, "assessment found"
        return False, f"assessment '{ref}' not found in data/assessments/"

    if lesson_type in ("video", "external_icn"):
        catalog = _load_icn_catalog()
        if ref in catalog:
            return True, "ICN asset found in manifest"
        return False, f"ICN asset '{ref}' not found in asset_manifest.json"

    if lesson_type == "exercise":
        return True, "exercise (always valid placeholder)"

    return False, f"unknown lesson type '{lesson_type}'"


# ── Tests ─────────────────────────────────────────────────────────────────────


class TestG1ShowcaseLibrary:
    """G1 — Demo content library: showcase tracks (6 tests)."""

    def test_g1_t1_all_three_tracks_published(self):
        """G1-T1: All 3 showcase tracks exist in data/tracks/ with status 'published'."""
        missing = []
        not_published = []
        for tid in _SHOWCASE_TRACK_IDS:
            track = _load_track(tid)
            if track is None:
                missing.append(tid)
            elif track.get("status") != "published":
                not_published.append(f"{tid} (status={track.get('status')!r})")

        assert not missing, (
            f"Missing showcase tracks: {missing}. "
            f"Expected files: {[f'data/tracks/{t}.json' for t in missing]}"
        )
        assert not not_published, (
            f"Tracks not published: {not_published}"
        )

    def test_g1_t2_track1_has_two_courses_and_four_lessons(self):
        """G1-T2: Track 1 (Cashier Onboarding) has 2 courses with >= 4 total lessons."""
        track = _load_track(_TRACK_CASHIER)
        assert track is not None, f"Track {_TRACK_CASHIER!r} not found in data/tracks/"

        course_ids = track.get("course_ids") or []
        assert len(course_ids) == 2, (
            f"Expected 2 courses in {_TRACK_CASHIER}, got {len(course_ids)}: {course_ids}"
        )

        total_lessons = 0
        for cid in course_ids:
            course = _load_course(cid)
            assert course is not None, f"Course {cid!r} referenced by {_TRACK_CASHIER} not found"
            total_lessons += len(course.get("lessons") or [])

        assert total_lessons >= 4, (
            f"Track 1 has {total_lessons} total lessons across 2 courses — expected >= 4. "
            f"Courses: {course_ids}"
        )

    def test_g1_t3_food_safety_track_duration_under_4min(self):
        """G1-T3: Track 3 (3-Min Food Safety) total duration_est <= 4 min (SHOULD-NOT-OCCUR).

        The booth track must complete in <= 3:30. We gate at 4 min (240 s) to give
        a safety margin while still catching accidental over-stuffing.
        """
        track = _load_track(_TRACK_FOOD_SAFETY)
        assert track is not None, f"Track {_TRACK_FOOD_SAFETY!r} not found in data/tracks/"

        total_minutes = 0
        lesson_breakdown = []
        for cid in (track.get("course_ids") or []):
            course = _load_course(cid)
            if course is None:
                continue
            for lesson in (course.get("lessons") or []):
                dur = lesson.get("duration_est") or 0
                total_minutes += dur
                lesson_breakdown.append(
                    f"  {lesson.get('type')} '{lesson.get('ref')}' = {dur} min"
                )

        assert total_minutes <= 4, (
            f"SHOULD-NOT-OCCUR: 3-min booth track total duration = {total_minutes} min (must be <= 4 min). "
            f"Breakdown:\n" + "\n".join(lesson_breakdown)
        )

    def test_g1_t4_no_dangling_refs(self):
        """G1-T4: Every lesson ref in every showcase track resolves to an existing file on disk.

        SHOULD-NOT-OCCUR: dangling refs must not exist.
        """
        failures = []
        for tid, cid, lesson in _all_showcase_lessons():
            ok, reason = _ref_exists_on_disk(lesson)
            if not ok:
                failures.append(
                    f"  track={tid!r} course={cid!r} "
                    f"type={lesson.get('type')!r} ref={lesson.get('ref')!r}: {reason}"
                )

        assert not failures, (
            f"SHOULD-NOT-OCCUR: {len(failures)} dangling lesson ref(s):\n"
            + "\n".join(failures)
        )

    def test_g1_t5_track1_has_icn_embed_video(self):
        """G1-T5: Track 1 has an ICN video lesson with embed_only or download_allowed posture."""
        track = _load_track(_TRACK_CASHIER)
        assert track is not None, f"Track {_TRACK_CASHIER!r} not found"

        catalog = _load_icn_catalog()
        assert catalog, "ICN asset_manifest.json is empty or missing"

        embed_postures = {"embed_only", "download_allowed"}
        found_embeddable_video = False
        video_refs_seen = []

        for cid in (track.get("course_ids") or []):
            course = _load_course(cid)
            if course is None:
                continue
            for lesson in (course.get("lessons") or []):
                if lesson.get("type") not in ("video", "external_icn"):
                    continue
                ref = lesson.get("ref") or ""
                video_refs_seen.append(ref)
                asset = catalog.get(ref)
                if asset and asset.get("license_posture") in embed_postures:
                    found_embeddable_video = True
                    break

        assert found_embeddable_video, (
            f"Track 1 ({_TRACK_CASHIER}) has no ICN video lesson with embed_only or "
            f"download_allowed license posture. Video refs found: {video_refs_seen}. "
            f"Each must exist in asset_manifest.json with a permissive license posture."
        )

    def test_g1_t6_cashier_role_filtering(self):
        """G1-T6: Cashier persona gets Track 1 in role-filtered track list.

        Simulates the GET /api/tracks role-filtering logic:
        - Cashier role sees tracks where role_tags is empty OR contains 'Cashier'.
        - Track 1 (Cashier Onboarding) must appear.
        """
        all_tracks = []
        for p in sorted(_TRACKS_DIR.glob("track-*.json")):
            t = _load_json(p)
            if t is not None:
                all_tracks.append(t)

        cashier_role = "Cashier"
        visible_to_cashier = [
            t for t in all_tracks
            if t.get("status") == "published"
            and (not t.get("role_tags") or cashier_role in (t.get("role_tags") or []))
        ]

        visible_ids = [t["id"] for t in visible_to_cashier]
        assert _TRACK_CASHIER in visible_ids, (
            f"Cashier persona does not see Track 1 ({_TRACK_CASHIER!r}) in role-filtered results. "
            f"Visible track ids: {visible_ids}. "
            f"Check that track has status='published' and role_tags contains 'Cashier'."
        )
