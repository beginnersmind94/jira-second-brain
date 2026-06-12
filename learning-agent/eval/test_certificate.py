"""eval/test_certificate.py — D7 Certificate polish + exam linkage tests.

5-test suite per the D7 spec:

  1. issue_certificate() with score_pct=88, passed_assessment=True
       → cert JSON includes score_pct: 88 and passed_assessment: True
  2. verification_code is deterministic — same cert_id produces the same code on
       every call (SHOULD-NOT-OCCUR: code must not change between calls)
  3. GET /api/certificates/verify/<code> with valid code
       → {found: True, user_display_name, track_title, issued_at}
       response contains NO user_id or district field
       (SHOULD-NOT-OCCUR: PII beyond name/track/date must not appear)
  4. GET /api/certificates/verify/<bad-code> → {found: false}
  5. GET /api/certificates/<cert_id>/pdf returns 200 with Content-Type
       application/pdf or text/html (functional test — endpoint exists,
       doesn't 500)

Run with:
    python -m pytest eval/test_certificate.py -v
or:
    python eval/test_certificate.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import uuid
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_LA = _HERE.parent
if str(_LA) not in sys.path:
    sys.path.insert(0, str(_LA))


# ── Helpers ───────────────────────────────────────────────────────────────────

def _patch_completion_store(tmp: Path):
    """Redirect completion_store's data dir to *tmp* for test isolation."""
    import completion_store as cs  # type: ignore[import]
    cs._COMPLETION_DIR = tmp / "completion"
    cs._BASE = tmp
    return cs


def _make_cert(cs, *, user_id: str = "test-user", track_id: str = "t-1",
               score_pct: float | None = None, passed_assessment: bool = False,
               assessment_title: str = "") -> dict:
    return cs.issue_certificate(
        user_id,
        track_id,
        "John Test",
        track_title="Cashier Onboarding",
        product="SchoolCafé",
        score_pct=score_pct,
        passed_assessment=passed_assessment,
        assessment_title=assessment_title,
        user_display_name="John",
    )


# ── Test 1 — score_pct + passed_assessment stored in cert JSON ────────────────

def test_cert_schema_with_score():
    """issue_certificate() with score_pct=88, passed_assessment=True
    must persist both fields in the cert JSON."""
    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        cs = _patch_completion_store(tmp)

        cert = _make_cert(cs, score_pct=88, passed_assessment=True,
                          assessment_title="Cashier Onboarding Exam")

        assert cert.get("score_pct") == 88, (
            f"Expected score_pct=88, got {cert.get('score_pct')!r}"
        )
        assert cert.get("passed_assessment") is True, (
            f"Expected passed_assessment=True, got {cert.get('passed_assessment')!r}"
        )
        assert cert.get("assessment_title") == "Cashier Onboarding Exam", (
            f"assessment_title not stored: {cert.get('assessment_title')!r}"
        )
        assert "verification_code" in cert, "verification_code missing from cert"
        print("PASS test_cert_schema_with_score")


# ── Test 2 — verification_code is deterministic ───────────────────────────────

def test_verification_code_deterministic():
    """Same cert_id must always produce the same verification_code.

    SHOULD-NOT-OCCUR: code must not change between calls.
    """
    from completion_store import _verification_code  # type: ignore[import]

    # Generate the same cert_id twice and confirm code is identical.
    cert_id = f"cert-20260613-120000-{uuid.uuid4().hex[:6]}"
    code_a = _verification_code(cert_id)
    code_b = _verification_code(cert_id)

    assert code_a == code_b, (
        f"SHOULD-NOT-OCCUR: verification_code changed between calls: "
        f"{code_a!r} vs {code_b!r}"
    )
    assert code_a.startswith("CYB-"), (
        f"Expected code to start with 'CYB-', got {code_a!r}"
    )
    assert len(code_a) == 12, (  # "CYB-" (4) + 8 chars
        f"Expected 12-char code, got {len(code_a)}: {code_a!r}"
    )
    print("PASS test_verification_code_deterministic")


# ── Test 3 — verify endpoint returns no PII beyond name/track/date ────────────

def test_verify_endpoint_no_pii():
    """GET /api/certificates/verify/<code> with a valid code must return
    {found: True, user_display_name, track_title, issued_at} and must NOT
    include user_id or any district field.

    SHOULD-NOT-OCCUR: PII beyond name/track/date must not appear in the response.
    """
    from fastapi.testclient import TestClient  # type: ignore[import]

    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        cs = _patch_completion_store(tmp)

        # Issue a cert to look up.
        cert = _make_cert(cs, user_id="john-cashier", score_pct=88,
                          passed_assessment=True)
        vcode = cert["verification_code"]

        # Import demo_app after patching the store.
        import demo_app  # type: ignore[import]
        demo_app._cs = cs  # wire patched store into the running app

        client = TestClient(demo_app.app, raise_server_exceptions=True)
        resp = client.get(f"/api/certificates/verify/{vcode}")

        assert resp.status_code == 200, (
            f"Expected 200, got {resp.status_code}: {resp.text}"
        )
        data = resp.json()
        assert data.get("found") is True, f"Expected found=True, got {data}"
        assert "user_display_name" in data, f"user_display_name missing: {data}"
        assert "track_title" in data, f"track_title missing: {data}"
        assert "issued_at" in data, f"issued_at missing: {data}"

        # SHOULD-NOT-OCCUR checks.
        assert "user_id" not in data, (
            f"SHOULD-NOT-OCCUR: user_id must not appear in verify response: {data}"
        )
        assert "district" not in data, (
            f"SHOULD-NOT-OCCUR: district must not appear in verify response: {data}"
        )
        assert "email" not in data, (
            f"SHOULD-NOT-OCCUR: email must not appear in verify response: {data}"
        )
        print("PASS test_verify_endpoint_no_pii")


# ── Test 4 — verify endpoint returns found:false for unknown code ─────────────

def test_verify_endpoint_not_found():
    """GET /api/certificates/verify/<bad-code> must return {found: false}."""
    from fastapi.testclient import TestClient  # type: ignore[import]

    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        cs = _patch_completion_store(tmp)

        import demo_app  # type: ignore[import]
        demo_app._cs = cs

        client = TestClient(demo_app.app, raise_server_exceptions=True)
        resp = client.get("/api/certificates/verify/CYB-NOTEXIST")

        assert resp.status_code == 200, (
            f"Expected 200 for not-found, got {resp.status_code}: {resp.text}"
        )
        data = resp.json()
        assert data.get("found") is False, (
            f"Expected found=False for unknown code, got {data}"
        )
        print("PASS test_verify_endpoint_not_found")


# ── Test 5 — PDF endpoint returns 200, content-type is pdf or html ────────────

def test_cert_pdf_endpoint_200():
    """GET /api/certificates/<cert_id>/pdf must return 200 with Content-Type
    application/pdf or text/html — never a 500."""
    from fastapi.testclient import TestClient  # type: ignore[import]

    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        cs = _patch_completion_store(tmp)

        cert = _make_cert(cs, score_pct=88, passed_assessment=True)
        cert_id = cert["id"]

        import demo_app  # type: ignore[import]
        demo_app._cs = cs

        client = TestClient(demo_app.app, raise_server_exceptions=True)
        resp = client.get(f"/api/certificates/{cert_id}/pdf")

        assert resp.status_code == 200, (
            f"Expected 200, got {resp.status_code}: {resp.text[:200]}"
        )
        ct = resp.headers.get("content-type", "")
        assert "application/pdf" in ct or "text/html" in ct, (
            f"Expected pdf or html content-type, got {ct!r}"
        )
        assert len(resp.content) > 100, "Response body is suspiciously short"
        print("PASS test_cert_pdf_endpoint_200")


# ── Runner ────────────────────────────────────────────────────────────────────

def _run_all():
    tests = [
        test_cert_schema_with_score,
        test_verification_code_deterministic,
        test_verify_endpoint_no_pii,
        test_verify_endpoint_not_found,
        test_cert_pdf_endpoint_200,
    ]
    passed = failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"FAIL {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed}/{len(tests)} passed" + (f", {failed} failed" if failed else ""))
    return failed == 0


if __name__ == "__main__":
    ok = _run_all()
    sys.exit(0 if ok else 1)
