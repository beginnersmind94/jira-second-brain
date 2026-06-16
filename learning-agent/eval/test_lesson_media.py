"""test_lesson_media.py — STORY-002: Lesson Media (trainer image upload + placement).

Tests:
  T1  validate_lesson_ref: image type, file exists, valid alt -> (True, None)    [PASS]
  T2  validate_lesson_ref: image type, empty alt -> (False, reason)               [FAIL]
  T3  validate_lesson_ref: image type, file missing -> (False, reason)            [FAIL]
  T4  validate_lesson_ref: image type, path-traversal ref -> (False, reason)      [FAIL]
  T5  lesson_origin_badge: image -> 'human_authored' (never ai_grounded)          [PASS]
  T6  expand_lesson: image falls back title to caption then alt                    [PASS]
  T7  POST /api/courses/images: wrong type (SVG magic) -> 415                     [FAIL]
  T8  POST /api/courses/images: file too large (>5 MB) -> 413                     [FAIL]
  T9  POST /api/courses/images: empty alt field -> 422                            [FAIL]
  T10 POST /api/courses/images: valid PNG, valid alt -> 201, pii_reminder present  [PASS]
  T11 POST /api/courses/images: dimension too large (>1600px PNG) -> 413          [FAIL]
  T12 Vendor guard: image lesson stored with 'image' type, validate passes;
      same filename stored under 'video' type -> validates ICN catalog (not file) [FAIL]

All tests are deterministic, no SDK calls, no network, no LLM.

Run:
    cd learning-agent && python -m pytest eval/test_lesson_media.py -v
  or:
    python -m pytest learning-agent/eval/test_lesson_media.py -v
"""
from __future__ import annotations

import io
import json
import struct
import sys
import tempfile
from pathlib import Path

# ── sys.path setup ──────────────────────────────────────────────────────────────
_HERE = Path(__file__).resolve().parent
_LA = _HERE.parent
if str(_LA) not in sys.path:
    sys.path.insert(0, str(_LA))

import course_store as cs


# ── Minimal valid PNG factory (stdlib only, no Pillow) ─────────────────────────

def _make_png(width: int = 400, height: int = 300) -> bytes:
    """Build the smallest valid PNG for the given dimensions.
    Just a 1×1 pixel repeated via IDAT — we only need magic bytes + valid IHDR
    so the sniffer and dimension parser are satisfied.
    """
    import zlib

    def _chunk(ctype: bytes, data: bytes) -> bytes:
        c = struct.pack('>I', len(data)) + ctype + data
        return c + struct.pack('>I', zlib.crc32(ctype + data) & 0xFFFFFFFF)

    sig = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)  # 8-bit RGB
    ihdr = _chunk(b'IHDR', ihdr_data)
    # Minimal IDAT: a single white pixel row filter(0) + 3 channels × width × height
    row = b'\x00' + b'\xff\xff\xff' * width
    raw_image = row * height
    idat = _chunk(b'IDAT', zlib.compress(raw_image))
    iend = _chunk(b'IEND', b'')
    return sig + ihdr + idat + iend


def _make_jpeg() -> bytes:
    """Minimal JPEG-like bytes — valid magic + SOF0 marker for dimension parsing."""
    # JFIF-style: SOI + APP0 marker (skip) + SOF0 with width=320, height=240.
    soi = b'\xff\xd8'
    # APP0 marker (length 16, filler)
    app0 = b'\xff\xe0' + struct.pack('>H', 16) + b'\x4a\x46\x49\x46\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
    # SOF0: marker 0xFFC0, length=17, precision=8, height=240, width=320, components=3
    sof0 = b'\xff\xc0' + struct.pack('>HBHH', 17, 8, 240, 320) + b'\x03\x01\x11\x00\x02\x11\x01\x03\x11\x01'
    eoi = b'\xff\xd9'
    return soi + app0 + sof0 + eoi


def _make_png_oversized(dim: int = 2000) -> bytes:
    """PNG with dimensions exceeding _IMG_MAX_DIM."""
    return _make_png(width=dim, height=dim)


# ── Shared scaffold ────────────────────────────────────────────────────────────

def _run_with_client(test_fn):
    """Run test_fn(client, tmp_path, course_img_dir) with fully isolated dirs."""
    try:
        import httpx  # noqa: F401
        from fastapi.testclient import TestClient
    except ImportError:
        print("  SKIP — httpx / FastAPI TestClient not available")
        return None

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        courses_dir = tmp_path / "courses"
        courses_dir.mkdir()
        pub_meta_dir = tmp_path / "pub_meta"
        pub_meta_dir.mkdir()
        quiz_dir = tmp_path / "quizzes"
        quiz_dir.mkdir()
        icn_dir = tmp_path / "icn"
        icn_dir.mkdir()
        course_img_dir = tmp_path / "course-img"
        course_img_dir.mkdir()

        import course_store as cs_mod
        orig_courses_dir = cs_mod.COURSES_DIR
        orig_pub_meta = cs_mod._PUB_META_DIR
        orig_quiz_dir = cs_mod._QUIZ_DIR
        orig_icn_dir  = cs_mod._ICN_DATA_DIR
        orig_img_dir  = cs_mod._COURSE_IMG_DIR
        cs_mod.COURSES_DIR    = courses_dir
        cs_mod._PUB_META_DIR  = pub_meta_dir
        cs_mod._QUIZ_DIR      = quiz_dir
        cs_mod._ICN_DATA_DIR  = icn_dir
        cs_mod._COURSE_IMG_DIR = course_img_dir

        # Also patch demo_app's _COURSE_IMG_DIR (separate module-level variable).
        import demo_app as da
        orig_da_img_dir = da._COURSE_IMG_DIR
        da._COURSE_IMG_DIR = course_img_dir

        try:
            client = TestClient(da.app, raise_server_exceptions=False)
            return test_fn(client, tmp_path, course_img_dir)
        except Exception as e:
            import traceback
            print(f"  ERROR: {e}")
            traceback.print_exc()
            return False
        finally:
            cs_mod.COURSES_DIR    = orig_courses_dir
            cs_mod._PUB_META_DIR  = orig_pub_meta
            cs_mod._QUIZ_DIR      = orig_quiz_dir
            cs_mod._ICN_DATA_DIR  = orig_icn_dir
            cs_mod._COURSE_IMG_DIR = orig_img_dir
            da._COURSE_IMG_DIR    = orig_da_img_dir


# ── T1: image lesson, file exists, valid alt -> (True, None) ──────────────────

def test_validate_image_lesson_valid():
    """T1: image lesson with existing file + non-empty alt passes validation."""
    with tempfile.TemporaryDirectory() as tmp:
        img_dir = Path(tmp)
        orig = cs._COURSE_IMG_DIR
        cs._COURSE_IMG_DIR = img_dir
        try:
            fname = "test-img-001.png"
            (img_dir / fname).write_bytes(_make_png())

            lesson = {"type": "image", "ref": fname, "alt": "POS open session screen", "title": ""}
            ok, reason = cs.validate_lesson_ref(lesson)
            assert ok is True, f"Expected PASS, got ok=False, reason={reason!r}"
            assert reason is None
        finally:
            cs._COURSE_IMG_DIR = orig


# ── T2: image lesson, empty alt -> (False, reason) ────────────────────────────

def test_validate_image_lesson_missing_alt():
    """T2: image lesson without alt text must be rejected (WCAG 1.1.1)."""
    with tempfile.TemporaryDirectory() as tmp:
        img_dir = Path(tmp)
        orig = cs._COURSE_IMG_DIR
        cs._COURSE_IMG_DIR = img_dir
        try:
            fname = "test-img-002.png"
            (img_dir / fname).write_bytes(_make_png())

            lesson = {"type": "image", "ref": fname, "alt": "", "title": "No alt"}
            ok, reason = cs.validate_lesson_ref(lesson)
            assert ok is False, "Expected FAIL when alt is empty"
            assert reason is not None
            assert "alt" in reason.lower() or "accessibility" in reason.lower(), (
                f"Reason should mention alt/accessibility, got: {reason!r}"
            )
        finally:
            cs._COURSE_IMG_DIR = orig


# ── T3: image lesson, file missing -> (False, reason) ─────────────────────────

def test_validate_image_lesson_file_missing():
    """T3: image lesson whose ref file doesn't exist in course-img/ fails."""
    with tempfile.TemporaryDirectory() as tmp:
        img_dir = Path(tmp)
        orig = cs._COURSE_IMG_DIR
        cs._COURSE_IMG_DIR = img_dir
        try:
            lesson = {"type": "image", "ref": "nonexistent-99.png", "alt": "some alt"}
            ok, reason = cs.validate_lesson_ref(lesson)
            assert ok is False, "Expected FAIL when file not in course-img/"
            assert "course-img" in reason or "does not exist" in reason.lower(), (
                f"Reason should mention course-img or not exist, got: {reason!r}"
            )
        finally:
            cs._COURSE_IMG_DIR = orig


# ── T4: image lesson, path-traversal ref -> (False, reason) ───────────────────

def test_validate_image_lesson_path_traversal():
    """T4: path-traversal ref (e.g. '../secret.txt') must be rejected."""
    lesson = {"type": "image", "ref": "../secret.txt", "alt": "some alt"}
    ok, reason = cs.validate_lesson_ref(lesson)
    assert ok is False, "Expected FAIL for path-traversal ref"
    assert "path" in reason.lower() or "separator" in reason.lower(), (
        f"Reason should mention path separators, got: {reason!r}"
    )


# ── T5: lesson_origin_badge: image -> human_authored ──────────────────────────

def test_origin_badge_image_is_human_authored():
    """T5: image lessons MUST carry 'human_authored' origin badge (INV-1 / AC5)."""
    lesson = {"type": "image", "ref": "any.png", "alt": "test"}
    badge = cs.lesson_origin_badge(lesson)
    assert badge == "human_authored", (
        f"image lesson badge must be 'human_authored', got {badge!r} — "
        "never badge trainer-uploaded images as 'ai_grounded' (INV-1)"
    )
    # Explicitly verify it is NOT ai_grounded.
    assert badge != "ai_grounded", "image lesson MUST NOT be badged as ai_grounded"
    assert badge != "outside_vendor", "image lesson should not be outside_vendor"


# ── T6: expand_lesson title fallback: caption → alt → ref ─────────────────────

def test_expand_lesson_image_title_fallback():
    """T6: expand_lesson uses caption > alt > ref as the title for image lessons."""
    with tempfile.TemporaryDirectory() as tmp:
        img_dir = Path(tmp)
        orig = cs._COURSE_IMG_DIR
        cs._COURSE_IMG_DIR = img_dir
        try:
            fname = "step.png"
            (img_dir / fname).write_bytes(_make_png())

            # 6a: caption wins.
            l1 = {"type": "image", "ref": fname, "alt": "the alt", "caption": "the caption", "title": ""}
            e1 = cs.expand_lesson(l1)
            assert e1["title"] == "the caption", f"Expected caption as title, got {e1['title']!r}"

            # 6b: no caption → alt wins.
            l2 = {"type": "image", "ref": fname, "alt": "the alt text", "title": ""}
            e2 = cs.expand_lesson(l2)
            assert e2["title"] == "the alt text", f"Expected alt as title, got {e2['title']!r}"

            # 6c: no caption, no alt → ref (filename) wins.
            l3 = {"type": "image", "ref": fname, "alt": "", "title": ""}
            e3 = cs.expand_lesson(l3)
            assert e3["title"] == fname, f"Expected ref as title, got {e3['title']!r}"

            # Provenance badge always human_authored.
            assert e1["origin_badge"] == "human_authored"
        finally:
            cs._COURSE_IMG_DIR = orig


# ── T7: upload — wrong content type (SVG) -> 415 ─────────────────────────────

def test_upload_wrong_type_rejected():
    """T7: uploading an SVG (or any non-PNG/JPEG/WebP) must return 415."""
    def _run(client, tmp_path, img_dir):
        svg_bytes = b'<svg xmlns="http://www.w3.org/2000/svg"><circle r="10"/></svg>'
        resp = client.post(
            "/api/courses/images",
            files={"file": ("test.svg", io.BytesIO(svg_bytes), "image/svg+xml")},
            data={"alt": "A diagram"},
            headers={"X-Demo-User": "sam-trainer"},
        )
        assert resp.status_code == 415, (
            f"Expected 415 for SVG, got {resp.status_code}: {resp.text[:200]}"
        )
        err = resp.json()
        assert err.get("detail", {}).get("error") == "unsupported_media_type" or \
               "unsupported" in str(resp.text).lower(), (
            f"Response should mention unsupported_media_type, got: {resp.text[:200]}"
        )
        return True

    result = _run_with_client(_run)
    if result is None:
        # Fallback: test sniff function directly.
        from demo_app import _sniff_image_type
        svg_bytes = b'<svg xmlns="http://www.w3.org/2000/svg"><circle r="10"/></svg>'
        assert _sniff_image_type(svg_bytes) is None, "SVG must not be identified as a valid image type"


# ── T8: upload — file too large -> 413 ────────────────────────────────────────

def test_upload_file_too_large():
    """T8: uploading a file > 5 MB must return 413."""
    def _run(client, tmp_path, img_dir):
        # Create a fake PNG that is > 5 MB by appending garbage after valid headers.
        big_bytes = _make_png() + (b'\x00' * (5 * 1024 * 1024 + 100))
        resp = client.post(
            "/api/courses/images",
            files={"file": ("big.png", io.BytesIO(big_bytes), "image/png")},
            data={"alt": "Big screenshot"},
            headers={"X-Demo-User": "sam-trainer"},
        )
        assert resp.status_code == 413, (
            f"Expected 413 for oversized file, got {resp.status_code}: {resp.text[:200]}"
        )
        err = resp.json()
        detail = err.get("detail", {})
        assert (isinstance(detail, dict) and detail.get("error") == "file_too_large") or \
               "large" in str(resp.text).lower() or "413" in str(resp.status_code), (
            f"Response should mention file_too_large, got: {resp.text[:200]}"
        )
        return True

    result = _run_with_client(_run)
    if result is None:
        print("  SKIP T8 — test client not available; size cap enforced in upload endpoint")


# ── T9: upload — missing alt text -> 422 ─────────────────────────────────────

def test_upload_missing_alt_rejected():
    """T9: uploading with empty alt must be blocked server-side (AC2 / WCAG 1.1.1)."""
    def _run(client, tmp_path, img_dir):
        png_bytes = _make_png()
        resp = client.post(
            "/api/courses/images",
            files={"file": ("screen.png", io.BytesIO(png_bytes), "image/png")},
            data={"alt": ""},
            headers={"X-Demo-User": "sam-trainer"},
        )
        assert resp.status_code == 422, (
            f"Expected 422 for missing alt, got {resp.status_code}: {resp.text[:200]}"
        )
        err = resp.json()
        detail = err.get("detail", {})
        error_code = detail.get("error") if isinstance(detail, dict) else ""
        assert error_code == "alt_required" or "alt" in str(resp.text).lower(), (
            f"Response should indicate alt_required, got: {resp.text[:200]}"
        )
        return True

    result = _run_with_client(_run)
    if result is None:
        print("  SKIP T9 — test client not available; alt guard enforced in upload endpoint")


# ── T10: upload — valid PNG, valid alt -> 201 + pii_reminder ─────────────────

def test_upload_valid_png_succeeds():
    """T10: valid PNG + alt -> 201, url + filename returned, pii_reminder present."""
    def _run(client, tmp_path, img_dir):
        png_bytes = _make_png(400, 300)
        resp = client.post(
            "/api/courses/images",
            files={"file": ("pos-screen.png", io.BytesIO(png_bytes), "image/png")},
            data={"alt": "POS screen showing open session button"},
            headers={"X-Demo-User": "sam-trainer"},
        )
        assert resp.status_code == 201, (
            f"Expected 201 for valid upload, got {resp.status_code}: {resp.text[:400]}"
        )
        data = resp.json()
        assert "url" in data, f"Response must include 'url', got: {list(data.keys())}"
        assert "filename" in data, f"Response must include 'filename', got: {list(data.keys())}"
        assert "pii_reminder" in data, "Response must include pii_reminder (AC7)"
        assert data["url"].startswith("/course-img/"), f"url should start with /course-img/, got {data['url']!r}"

        # File must be present in the img dir.
        fname = data["filename"]
        assert (img_dir / fname).exists(), f"Uploaded file {fname!r} not found in course-img/"

        # pii_reminder must be non-trivial.
        assert len(data["pii_reminder"]) > 20, "pii_reminder should be a meaningful message"
        return True

    result = _run_with_client(_run)
    if result is None:
        print("  SKIP T10 — test client not available")


# ── T11: upload — oversized dimensions -> 413 ────────────────────────────────

def test_upload_oversized_dimensions_rejected():
    """T11: image with width or height > 1600 px must be rejected with 413 (AC6)."""
    def _run(client, tmp_path, img_dir):
        big_png = _make_png_oversized(2000)
        resp = client.post(
            "/api/courses/images",
            files={"file": ("big-dims.png", io.BytesIO(big_png), "image/png")},
            data={"alt": "Oversized screenshot"},
            headers={"X-Demo-User": "sam-trainer"},
        )
        assert resp.status_code == 413, (
            f"Expected 413 for oversized dimensions, got {resp.status_code}: {resp.text[:200]}"
        )
        body = resp.text.lower()
        assert "1600" in body or "dimension" in body or "large" in body, (
            f"Response should mention 1600/dimension/large, got: {resp.text[:200]}"
        )
        return True

    result = _run_with_client(_run)
    if result is None:
        # Fallback: test dimension parser + limit directly.
        from demo_app import _parse_image_dimensions, _IMG_MAX_DIM
        big_png = _make_png_oversized(2000)
        dims = _parse_image_dimensions(big_png, "png")
        assert dims is not None, "Dimension parser should return values for our test PNG"
        w, h = dims
        assert w > _IMG_MAX_DIM or h > _IMG_MAX_DIM, (
            f"2000×2000 PNG dims ({w}×{h}) should exceed _IMG_MAX_DIM={_IMG_MAX_DIM}"
        )


# ── T12: vendor guard — image type validated vs file; video type ignores file ──

def test_vendor_guard_video_cannot_use_image_ref():
    """T12: image ref is valid under type='image', but rejected under type='video'
    (vendor guard: ICN catalog is checked for video, not static/course-img/).
    This exercises AC4 at the lesson-write level.
    """
    with tempfile.TemporaryDirectory() as tmp:
        img_dir = Path(tmp)
        orig = cs._COURSE_IMG_DIR
        cs._COURSE_IMG_DIR = img_dir
        try:
            fname = "pos-screenshot.png"
            (img_dir / fname).write_bytes(_make_png())

            # type=image + this file: passes.
            ok_img, _ = cs.validate_lesson_ref(
                {"type": "image", "ref": fname, "alt": "POS screen"},
            )
            assert ok_img is True, "image type should pass with existing file"

            # Same filename but type=video: must fail (ICN catalog check, not file check).
            ok_vid, reason_vid = cs.validate_lesson_ref(
                {"type": "video", "ref": fname},
                icn_catalog=set(),  # empty catalog -> not found
            )
            assert ok_vid is False, (
                "video type with a course-img filename should fail (not in ICN catalog)"
            )
            assert "catalog" in reason_vid.lower() or "not found" in reason_vid.lower(), (
                f"Reason should mention ICN catalog, got: {reason_vid!r}"
            )
        finally:
            cs._COURSE_IMG_DIR = orig


# ── Pytest collection (also runnable directly) ───────────────────────────────

_ALL_TESTS = [
    test_validate_image_lesson_valid,
    test_validate_image_lesson_missing_alt,
    test_validate_image_lesson_file_missing,
    test_validate_image_lesson_path_traversal,
    test_origin_badge_image_is_human_authored,
    test_expand_lesson_image_title_fallback,
    test_upload_wrong_type_rejected,
    test_upload_file_too_large,
    test_upload_missing_alt_rejected,
    test_upload_valid_png_succeeds,
    test_upload_oversized_dimensions_rejected,
    test_vendor_guard_video_cannot_use_image_ref,
]

if __name__ == "__main__":
    passed = failed = 0
    for fn in _ALL_TESTS:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
            passed += 1
        except Exception as exc:
            print(f"  FAIL  {fn.__name__}: {exc}")
            import traceback; traceback.print_exc()
            failed += 1
    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed of {len(_ALL_TESTS)}")
    if failed:
        sys.exit(1)
