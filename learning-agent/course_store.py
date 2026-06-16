"""course_store.py — Disk-backed persistence for the Course entity (A1).

Courses are stored as JSON files in data/courses/<id>.json.

Design:
- Mirrors quiz_store.py patterns (load, save, list, delete, ID generation).
- status always defaults to "draft" — no auto-publish path exists.
- Lesson refs are validated server-side against approved published content,
  approved quizzes, or ICN catalog ids. Draft refs → 422 at the API layer.
- description is human-authored metadata; it never passes through the grounding
  gate and must never be badged with "every claim cited".

Course schema:
    {
      "id": "course-<YYYYMMDD>-<8-char-uuid>",
      "title": "string",
      "description": "",
      "product": "SchoolCafé",
      "role_tags": [],
      "lessons": [
        {
          "type": "guide|quiz|video|external_icn|flashcards|assessment|exercise|image",
          "ref": "<resource-id or quiz-id or icn-asset-id or assessment-id or image-filename>",
          "title": "string",
          "duration_est": 5,
          "alt": "string (required for image lessons — WCAG 1.1.1)",
          "caption": "string (optional short descriptive caption for image lessons)"
        }
      ],
      "status": "draft",
      "created_at": "<ISO8601>",
      "updated_at": "<ISO8601>"
    }

Lesson types:
  guide         -> published/metadata/<ref>.json must exist AND approved == true
  quiz          -> data/quizzes/<ref>.json must exist AND status == "approved"
  flashcards    -> data/flashcards/<ref>.json must exist AND status == "approved"
  video         -> ref must appear as an asset_id in the ICN manifest
  external_icn  -> same as video (ICN catalog id)
  assessment    -> data/assessments/<ref>.json must exist AND status == "published"
  exercise      -> always valid (placeholder for future interactive content)
  image         -> ref (filename) must exist in static/course-img/ AND alt must be
                   non-empty (WCAG 1.1.1). Origin badge: human_authored (never
                   ai_grounded — trainer-uploaded, INV-1). Caption is an optional
                   short label (not a product-claim body; kept to ≤200 chars).
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
COURSES_DIR = BASE / "data" / "courses"
COURSES_DIR.mkdir(parents=True, exist_ok=True)

# Ref dirs -- these are the ground-truth locations for validation.
_DRAFTS_DIR = BASE / "drafts"
_PUB_META_DIR = BASE / "published" / "metadata"
_QUIZ_DIR = BASE / "quizzes"
_FLASHCARDS_DIR = BASE / "data" / "flashcards"
_ASSESSMENTS_DIR = BASE / "data" / "assessments"
_ICN_DATA_DIR = BASE / "data" / "icn" / "data"
# Trainer-uploaded course illustration images (served at GET /course-img/<name>).
_COURSE_IMG_DIR = BASE / "static" / "course-img"


# -- ID helpers ----------------------------------------------------------------

def _new_course_id() -> str:
    date_part = datetime.now().strftime("%Y%m%d")
    return f"course-{date_part}-{uuid.uuid4().hex[:8]}"


def _course_path(cid: str) -> Path:
    return COURSES_DIR / f"{cid}.json"


# -- Low-level I/O -------------------------------------------------------------

def _read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _now_iso() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")


# -- Course CRUD ---------------------------------------------------------------

def save_course(course: dict) -> dict:
    """Persist a course dict to disk. Stamps updated_at; sets created_at on first save."""
    now = _now_iso()
    course["updated_at"] = now
    course.setdefault("created_at", now)
    # status ALWAYS defaults to draft -- never auto-published.
    course.setdefault("status", "draft")
    _course_path(course["id"]).write_text(
        json.dumps(course, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return course


def load_course(cid: str) -> dict | None:
    return _read_json(_course_path(cid))


def list_courses() -> list[dict]:
    """Return all courses sorted by updated_at descending."""
    out = []
    for p in sorted(COURSES_DIR.glob("course-*.json"), key=lambda f: f.stat().st_mtime, reverse=True):
        data = _read_json(p)
        if data is not None:
            out.append(data)
    return out


def create_course(
    title: str,
    description: str = "",
    product: str = "SchoolCafe",
    role_tags: list | None = None,
    lessons: list | None = None,
) -> dict:
    """Create and persist a new draft course. status is always 'draft'."""
    course = {
        "id": _new_course_id(),
        "title": title or "Untitled Course",
        "description": description or "",
        "product": product or "SchoolCafe",
        "role_tags": list(role_tags or []),
        "lessons": list(lessons or []),
        "status": "draft",  # NEVER auto-published
    }
    return save_course(course)


def update_course(course: dict, updates: dict) -> dict:
    """Apply allowed field updates to an existing course dict (does not save)."""
    for field in ("title", "description", "product", "role_tags"):
        if field in updates:
            course[field] = updates[field]
    if "lessons" in updates:
        course["lessons"] = list(updates["lessons"])
    return course


def delete_course(cid: str) -> bool:
    p = _course_path(cid)
    if p.exists():
        p.unlink()
        return True
    return False


# -- Lesson-ref validation (the server-side gate) ------------------------------

def _load_icn_asset_ids() -> set[str]:
    """Return the set of valid ICN asset_ids from the local manifest."""
    manifest_path = _ICN_DATA_DIR / "asset_manifest.json"
    if not manifest_path.exists():
        return set()
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        return {a.get("asset_id") for a in manifest if a.get("asset_id")}
    except (json.JSONDecodeError, OSError):
        return set()


def _resolve_guide_meta(ref: str) -> dict | None:
    """Try published/metadata/<ref>.json first, then drafts/<ref>.json."""
    meta = _read_json(_PUB_META_DIR / f"{ref}.json")
    if meta is not None:
        return meta
    return _read_json(_DRAFTS_DIR / f"{ref}.json")


def validate_lesson_ref(
    lesson: dict,
    published_dir: Path | None = None,
    quiz_dir: Path | None = None,
    icn_catalog: set[str] | None = None,
) -> tuple[bool, str | None]:
    """Validate that a lesson's ref resolves to approved content.

    Args:
        lesson: Lesson dict with 'type' and 'ref' keys.
        published_dir: Override for published/metadata/ (used in tests).
        quiz_dir: Override for quizzes/ (used in tests).
        icn_catalog: Pre-loaded set of valid ICN asset_ids (avoids re-reading disk
                     on every call when validating many lessons at once).

    Returns:
        (True, None)        -- ref is valid and approved
        (False, "reason")   -- ref is invalid; reason describes the failure
    """
    lesson_type = (lesson.get("type") or "").strip()
    ref = (lesson.get("ref") or "").strip()

    if not ref:
        return False, "lesson ref is empty"

    if lesson_type == "guide":
        # Look in published/metadata/ first; fall back to drafts/
        pub_meta_dir = published_dir or _PUB_META_DIR
        draft_dir = _DRAFTS_DIR

        # Check published metadata
        meta = _read_json(pub_meta_dir / f"{ref}.json")
        if meta is None:
            # Check drafts for any metadata file
            meta = _read_json(draft_dir / f"{ref}.json")

        if meta is None:
            return False, f"guide ref '{ref}' not found in published/metadata/ or drafts/"

        # Must be approved
        approved = meta.get("approved") is True or meta.get("status") in ("approved", "published")
        if not approved:
            return False, (
                f"guide ref '{ref}' is not approved (status={meta.get('status')!r}, "
                f"approved={meta.get('approved')!r}) -- only approved guides may be added to courses"
            )
        return True, None

    elif lesson_type == "quiz":
        q_dir = quiz_dir or _QUIZ_DIR
        quiz_path = q_dir / f"{ref}.json"
        quiz = _read_json(quiz_path)
        if quiz is None:
            return False, f"quiz ref '{ref}' not found in data/quizzes/"
        if quiz.get("status") != "approved":
            return False, (
                f"quiz ref '{ref}' is not approved (status={quiz.get('status')!r}) -- "
                "only approved quizzes may be added to courses"
            )
        return True, None

    elif lesson_type in ("video", "external_icn"):
        catalog = icn_catalog if icn_catalog is not None else _load_icn_asset_ids()
        if ref not in catalog:
            return False, (
                f"ICN ref '{ref}' not found in the ICN asset catalog -- "
                "only catalog asset_ids are valid video/external_icn refs"
            )
        return True, None

    elif lesson_type == "flashcards":
        # A flashcard ref must be an approved deck in data/flashcards/.
        deck_path = _FLASHCARDS_DIR / f"{ref}.json"
        deck = _read_json(deck_path)
        if deck is None:
            return False, f"flashcard deck ref '{ref}' not found in data/flashcards/"
        if deck.get("status") != "approved":
            return False, (
                f"flashcard deck ref '{ref}' is not approved (status={deck.get('status')!r}) -- "
                "only approved flashcard decks may be added to courses"
            )
        return True, None

    elif lesson_type == "assessment":
        # An assessment ref must resolve to a published assessment in data/assessments/.
        assessment_path = _ASSESSMENTS_DIR / f"{ref}.json"
        assessment = _read_json(assessment_path)
        if assessment is None:
            return False, f"assessment ref '{ref}' not found in data/assessments/"
        if assessment.get("status") != "published":
            return False, (
                f"assessment ref '{ref}' is not published (status={assessment.get('status')!r}) -- "
                "only published assessments may be added to courses"
            )
        return True, None

    elif lesson_type == "exercise":
        # Always valid -- placeholder for future interactive content.
        return True, None

    elif lesson_type == "image":
        # Image lessons: ref is the filename in static/course-img/.
        # Provenance: human_authored (trainer-uploaded) — NEVER ai_grounded (INV-1).
        # alt is mandatory for WCAG 1.1.1 — block save if empty.
        alt = (lesson.get("alt") or "").strip()
        if not alt:
            return False, (
                "image lesson is missing alt text — alt is required for accessibility (WCAG 1.1.1). "
                "Describe what the image shows so screen-reader users aren't excluded."
            )
        # ref must be a safe filename (basename only, no path traversal).
        safe_ref = Path(ref).name
        if safe_ref != ref:
            return False, (
                f"image ref '{ref}' contains path separators — only a bare filename is allowed"
            )
        img_path = _COURSE_IMG_DIR / safe_ref
        if not img_path.exists() or not img_path.is_file():
            return False, (
                f"image ref '{ref}' does not exist in static/course-img/ — "
                "upload the image via POST /api/courses/images before referencing it"
            )
        return True, None

    else:
        return False, f"unknown lesson type '{lesson_type}'"


def validate_all_lessons(
    lessons: list[dict],
    icn_catalog: set[str] | None = None,
) -> list[tuple[int, str]]:
    """Validate every lesson in a list. Returns a list of (index, reason) errors.

    Loads the ICN catalog once and reuses it across all lessons for efficiency.
    Empty list means all lessons passed validation.
    """
    catalog = icn_catalog if icn_catalog is not None else _load_icn_asset_ids()
    errors: list[tuple[int, str]] = []
    for i, lesson in enumerate(lessons):
        ok, reason = validate_lesson_ref(lesson, icn_catalog=catalog)
        if not ok:
            errors.append((i, reason or "unknown validation error"))
    return errors


# -- Origin badge helper -------------------------------------------------------

def lesson_origin_badge(lesson: dict) -> str:
    """Return the provenance badge string for a lesson.

    Values:
        "ai_grounded"     -- AI-generated guide or quiz grounded through the citation gate
        "human_authored"  -- Imported Cybersoft guide, or exercise (human-assembled)
        "outside_vendor"  -- ICN/USDA video or external content
    """
    lesson_type = (lesson.get("type") or "").strip()

    if lesson_type in ("video", "external_icn"):
        return "outside_vendor"

    if lesson_type in ("quiz", "flashcards", "assessment"):
        # Quizzes, flashcards, and assessments are gate-grounded from published content.
        return "ai_grounded"

    if lesson_type == "exercise":
        # Exercises are human-assembled (no AI-claim channel yet).
        return "human_authored"

    if lesson_type == "image":
        # Trainer-uploaded screenshots/diagrams — provenance is always human_authored.
        # NEVER badge as ai_grounded (INV-1): the trainer took this screenshot; it is
        # not a product claim, not AI-generated, and not ICN/USDA vendor content.
        return "human_authored"

    if lesson_type == "guide":
        ref = (lesson.get("ref") or "").strip()
        meta = _resolve_guide_meta(ref)
        if meta is not None:
            origin = meta.get("origin") or meta.get("method") or ""
            if origin in ("internal", "imported_guide"):
                return "human_authored"
        # Default for AI-generated guides (no origin field or origin not internal)
        return "ai_grounded"

    return "ai_grounded"


# -- Lesson expansion (for GET /api/courses/<cid>) ----------------------------

def expand_lesson(lesson: dict, all_module_meta: dict[str, dict] | None = None) -> dict:
    """Add 'origin_badge' and resolved 'title' to a lesson dict.

    Does NOT mutate the input; returns a new dict.

    Args:
        lesson: Lesson dict from a course.
        all_module_meta: Optional pre-loaded map of ref -> metadata dict to avoid
                         repeated disk reads when expanding many lessons.
    """
    expanded = dict(lesson)
    expanded["origin_badge"] = lesson_origin_badge(lesson)

    # Attempt to fill in title from source metadata if not already set.
    if not expanded.get("title"):
        ref = (lesson.get("ref") or "").strip()
        lesson_type = (lesson.get("type") or "").strip()

        if lesson_type == "guide":
            if all_module_meta and ref in all_module_meta:
                meta = all_module_meta[ref]
            else:
                meta = _resolve_guide_meta(ref) or {}
            expanded["title"] = (
                meta.get("title")
                or f"{meta.get('module', '')} -- {meta.get('template', '')}".strip(" --")
                or ref
            )

        elif lesson_type == "quiz":
            quiz = _read_json(_QUIZ_DIR / f"{ref}.json") or {}
            expanded["title"] = quiz.get("title") or ref

        elif lesson_type == "image":
            # Title falls back to caption, then alt text, then filename.
            expanded["title"] = (
                lesson.get("caption")
                or lesson.get("alt")
                or ref
            )

        else:
            expanded["title"] = ref

    return expanded
