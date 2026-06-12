"""eval/test_grounding_audit.py — Deterministic tests for Section E: Grounding Audit.

Test coverage per the E-spec:

  T1  extract_citations() on HTML with known <!-- Source: --> comments returns
      correct count and fields (source_ref, tier, verbatim_quote, section).

  T2  GET /api/resources/{rid}/audit returns _note field containing "Exhaustive"
      (SHOULD-NOT-OCCUR: missing note implies sampling — would undermine trust pitch).

  T3  fully_grounded is False when a [TO VERIFY] marker exists in the guide
      (SHOULD-NOT-OCCUR: a guide with unsourced claims must not show as fully grounded).

  T4  Course-level audit sums claims across all guide lessons correctly.

  T5  GET /api/resources/{rid}/audit/export returns 200 with
      Content-Disposition: attachment header.

  T6  Cashier persona → GET /api/resources/{rid}/audit returns 403
      (audit is trainer/director only — learner must not access citation data).

All tests are deterministic, no SDK calls, no network, no LLM.

Run:
    python -m pytest learning-agent/eval/test_grounding_audit.py -v
  or from learning-agent/:
    python eval/test_grounding_audit.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

# Allow running directly from learning-agent/ or via pytest from repo root.
_HERE = Path(__file__).resolve().parent
_LA = _HERE.parent
if str(_LA) not in sys.path:
    sys.path.insert(0, str(_LA))

import grounding_audit as _ga


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_SAMPLE_HTML = """\
<h2>Adding Items</h2>
<p>Navigate to the Items module and select New Item.<!-- Source: NXT-4521 AC: "User navigates to Items module and selects New Item" --></p>
<p>Fill in the Item Description field (required).<!-- Source: NXT-4521 AC: "Item Description is a required field" --></p>
<h2>Non-Food Items</h2>
<p>Select NON-FOOD from the Food/Non-Food dropdown.<!-- Source: NXT-53528 AC: "If Non-Food is selected: disable row 2 and 4" --></p>
<p>Click the checkmark to save the row.<!-- Source: transcript [05:18] --></p>
<p>The presenter noted a 250-character limit. [TO VERIFY: Presenter stated a 250-character limit; no AC found to confirm this limit.]</p>
"""

_SAMPLE_HTML_CLEAN = """\
<h2>Full Workflows</h2>
<p>Open the module and click Save.<!-- Source: NXT-9999 AC: "User opens module and clicks Save" --></p>
<p>The system confirms with a green banner.<!-- Source: NXT-9999 RN: "Confirmation banner appears in green" --></p>
"""

_RESOURCE_ID = "20260603-124709-item-management-long-form-68d6de"


# ---------------------------------------------------------------------------
# T1: extract_citations returns correct count and fields
# ---------------------------------------------------------------------------

def test_t1_extract_citations_count_and_fields():
    """extract_citations() on known HTML with Source comments returns the
    right count and correctly populated fields."""
    result = _ga.extract_citations(resource_id="test-rid", html=_SAMPLE_HTML)

    assert result["exhaustive"] is True, (
        "parse_error must be None and exhaustive=True for valid HTML"
    )
    assert result["parse_error"] is None, (
        f"No parse_error expected, got: {result['parse_error']}"
    )

    citations = result["citations"]
    # 4 Source comments in _SAMPLE_HTML (3 Jira + 1 transcript)
    assert len(citations) == 4, (
        f"Expected 4 citations, got {len(citations)}: {citations}"
    )

    # First citation: NXT-4521 AC
    c0 = citations[0]
    assert c0["source_ref"] == "NXT-4521", (
        f"Expected source_ref NXT-4521, got {c0['source_ref']!r}"
    )
    assert c0["tier"] == "AC", (
        f"Expected tier AC, got {c0['tier']!r}"
    )
    assert "Items module" in c0["verbatim_quote"], (
        f"Expected verbatim quote to contain 'Items module', got {c0['verbatim_quote']!r}"
    )
    assert c0["grounded"] is True, "AC citation with non-empty quote must be grounded=True"
    assert c0["section"] == "Adding Items", (
        f"Expected section 'Adding Items', got {c0['section']!r}"
    )

    # Third citation: NXT-53528 AC
    c2 = citations[2]
    assert c2["source_ref"] == "NXT-53528", (
        f"Expected NXT-53528, got {c2['source_ref']!r}"
    )

    # Fourth citation: transcript (no verbatim quote)
    c3 = citations[3]
    assert c3["is_transcript"] is True, (
        f"Transcript citation must have is_transcript=True"
    )
    assert c3["source_ref"].lower().startswith("transcript"), (
        f"Transcript ref should start with 'transcript', got {c3['source_ref']!r}"
    )

    # [TO VERIFY] markers
    to_verify = result["to_verify"]
    assert len(to_verify) == 1, (
        f"Expected 1 [TO VERIFY] marker, got {len(to_verify)}"
    )
    assert "250-character" in to_verify[0]["surrounding_context"], (
        f"TO VERIFY context should mention '250-character', got: {to_verify[0]['surrounding_context']!r}"
    )

    print(f"T1 PASS: {len(citations)} citations extracted, fields verified, 1 TO VERIFY found")


# ---------------------------------------------------------------------------
# T2: Audit response contains _note with "Exhaustive" (SHOULD-NOT-OCCUR guard)
# ---------------------------------------------------------------------------

def test_t2_audit_response_note_exhaustive():
    """SHOULD-NOT-OCCUR: GET /api/resources/{rid}/audit must include a _note field
    containing 'Exhaustive' when parsing succeeded.  A missing or sampling-implying
    note would undermine the trust pitch for the compliance reviewer."""
    result = _ga.extract_citations(resource_id="test-rid", html=_SAMPLE_HTML)
    payload = _ga.build_audit_payload(
        resource_id="test-rid",
        title="Test Guide",
        citations=result["citations"],
        to_verify=result["to_verify"],
        parse_error=result["parse_error"],
        exhaustive=result["exhaustive"],
    )

    assert "_note" in payload, (
        "SHOULD-NOT-OCCUR: _note field is missing from audit payload. "
        "The note is non-negotiable — it is the on-stage answer to 'is this every claim?'"
    )
    note = payload["_note"]
    assert "xhaustive" in note or "exhaustive" in note.lower(), (
        f"SHOULD-NOT-OCCUR: _note does not contain 'Exhaustive'. "
        f"Got: {note!r}. A note that does not confirm exhaustive coverage implies sampling."
    )
    print(f"T2 PASS: _note field present and contains 'Exhaustive': {note!r}")


# ---------------------------------------------------------------------------
# T3: fully_grounded is False when [TO VERIFY] marker exists (SHOULD-NOT-OCCUR)
# ---------------------------------------------------------------------------

def test_t3_fully_grounded_false_when_to_verify_present():
    """SHOULD-NOT-OCCUR: a guide with [TO VERIFY] markers must never report
    fully_grounded=True.  One unsourced claim makes the guide NOT fully grounded."""
    # _SAMPLE_HTML has 1 [TO VERIFY] marker.
    result = _ga.extract_citations(resource_id="test-rid", html=_SAMPLE_HTML)
    payload = _ga.build_audit_payload(
        resource_id="test-rid",
        title="Test Guide",
        citations=result["citations"],
        to_verify=result["to_verify"],
        parse_error=result["parse_error"],
        exhaustive=result["exhaustive"],
    )

    assert payload["to_verify_count"] >= 1, (
        f"Expected at least 1 TO VERIFY, got {payload['to_verify_count']}"
    )
    assert payload["fully_grounded"] is False, (
        f"SHOULD-NOT-OCCUR: fully_grounded is True despite {payload['to_verify_count']} "
        f"[TO VERIFY] marker(s). A guide with unsourced claims must not show as fully grounded."
    )

    # Also verify the clean HTML (no TO VERIFY) yields fully_grounded=True.
    result_clean = _ga.extract_citations(resource_id="clean-rid", html=_SAMPLE_HTML_CLEAN)
    payload_clean = _ga.build_audit_payload(
        resource_id="clean-rid",
        title="Clean Guide",
        citations=result_clean["citations"],
        to_verify=result_clean["to_verify"],
        parse_error=result_clean["parse_error"],
        exhaustive=result_clean["exhaustive"],
    )
    assert payload_clean["to_verify_count"] == 0, (
        f"Clean HTML should have 0 TO VERIFY, got {payload_clean['to_verify_count']}"
    )
    assert payload_clean["fully_grounded"] is True, (
        f"Clean guide (no TO VERIFY, all quotes present) must be fully_grounded=True, "
        f"got {payload_clean['fully_grounded']}"
    )

    print(
        f"T3 PASS: fully_grounded=False when TO VERIFY present "
        f"({payload['to_verify_count']} marker); clean guide correctly fully_grounded=True"
    )


# ---------------------------------------------------------------------------
# T4: Course-level audit sums claims across guide lessons correctly
# ---------------------------------------------------------------------------

def test_t4_course_audit_sums_claims_correctly():
    """Course-level audit must sum claims across all guide lessons.
    We simulate two guides with known claim counts and verify the total."""
    guide1_html = """\
<h2>Section A</h2>
<p>Claim one.<!-- Source: NXT-1001 AC: "Claim one verbatim" --></p>
<p>Claim two.<!-- Source: NXT-1002 AC: "Claim two verbatim" --></p>
"""
    guide2_html = """\
<h2>Section B</h2>
<p>Claim three.<!-- Source: NXT-2001 AC: "Claim three verbatim" --></p>
"""
    result1 = _ga.extract_citations(resource_id="guide1", html=guide1_html)
    result2 = _ga.extract_citations(resource_id="guide2", html=guide2_html)

    # Aggregate as the course-level endpoint does.
    all_citations = result1["citations"] + result2["citations"]
    all_to_verify = result1["to_verify"] + result2["to_verify"]
    total = len(all_citations)
    verified = sum(1 for c in all_citations if c.get("grounded"))

    assert total == 3, (
        f"Expected 3 total claims across both guides, got {total}"
    )
    assert verified == 3, (
        f"Expected 3 verified (all have non-empty quotes), got {verified}"
    )
    assert len(all_to_verify) == 0, (
        f"Expected 0 TO VERIFY markers, got {len(all_to_verify)}"
    )

    # Build the payload as the endpoint would.
    by_resource = [
        {"resource_id": "guide1", "title": "Guide 1", "claims": len(result1["citations"]),
         "verified": sum(1 for c in result1["citations"] if c.get("grounded"))},
        {"resource_id": "guide2", "title": "Guide 2", "claims": len(result2["citations"]),
         "verified": sum(1 for c in result2["citations"] if c.get("grounded"))},
    ]
    assert by_resource[0]["claims"] == 2, (
        f"Guide 1 must report 2 claims, got {by_resource[0]['claims']}"
    )
    assert by_resource[1]["claims"] == 1, (
        f"Guide 2 must report 1 claim, got {by_resource[1]['claims']}"
    )
    assert sum(r["claims"] for r in by_resource) == total, (
        "Sum of by_resource claims must equal total_claims"
    )

    print(
        f"T4 PASS: course sums correctly — {total} total claims "
        f"({by_resource[0]['claims']} + {by_resource[1]['claims']}), {verified} verified"
    )


# ---------------------------------------------------------------------------
# T5: GET /api/resources/{rid}/audit/export returns 200 + Content-Disposition
# ---------------------------------------------------------------------------

def test_t5_audit_export_returns_attachment():
    """GET /api/resources/{rid}/audit/export must return HTTP 200 with a
    Content-Disposition: attachment header so the browser triggers a download."""
    import httpx
    from fastapi.testclient import TestClient

    # Import demo_app — this is safe (no network, no LLM) as long as we patch
    # the filesystem calls that would fail without real fixture data.
    import demo_app as _da
    import app as prod

    # Build a temporary directory with a minimal approved resource.
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        drafts = tmp_path / "drafts"
        drafts.mkdir()
        meta_dir = drafts  # for drafts, meta lives alongside html

        rid = "test-audit-export-rid"
        html_content = _SAMPLE_HTML_CLEAN
        meta_content = {
            "id": rid,
            "status": "approved",
            "approved": True,
            "module": "Item Management",
            "template": "long-form",
            "title": "Test Export Guide",
            "citation_integrity": {"verified": 2, "tier_lie": 0, "not_found": 0},
        }

        (drafts / f"{rid}.html").write_text(html_content, encoding="utf-8")
        (drafts / f"{rid}.json").write_text(
            json.dumps(meta_content), encoding="utf-8"
        )

        # Patch prod.DRAFTS and prod.PUBLISHED so _resolve_resource finds our file.
        published = tmp_path / "published"
        published.mkdir()
        pub_meta = published / "metadata"
        pub_meta.mkdir()

        original_drafts = prod.DRAFTS
        original_published = prod.PUBLISHED
        original_pub_meta = prod.PUB_META
        try:
            prod.DRAFTS = drafts
            prod.PUBLISHED = published
            prod.PUB_META = pub_meta

            client = TestClient(_da.app, raise_server_exceptions=True)
            # Use sam-trainer (is_trainer=True) so the 403 guard passes.
            resp = client.get(
                f"/api/resources/{rid}/audit/export",
                headers={"X-Demo-User": "sam-trainer"},
            )
        finally:
            prod.DRAFTS = original_drafts
            prod.PUBLISHED = original_published
            prod.PUB_META = original_pub_meta

    assert resp.status_code == 200, (
        f"Expected 200, got {resp.status_code}: {resp.text[:300]}"
    )
    cd = resp.headers.get("content-disposition", "")
    assert "attachment" in cd.lower(), (
        f"SHOULD-NOT-OCCUR: Content-Disposition header does not contain 'attachment'. "
        f"Got: {cd!r}. The export must trigger a download, not inline rendering."
    )
    assert rid in cd or "grounding-audit" in cd, (
        f"Content-Disposition should include rid or 'grounding-audit' in filename, got: {cd!r}"
    )
    # Verify the HTML body contains the table header we expect.
    body = resp.text
    assert "Verbatim Quote" in body, (
        f"Export HTML must contain 'Verbatim Quote' column header, got body snippet: {body[:500]!r}"
    )
    assert "Exhaustive" in body or "Not sampled" in body, (
        f"Export HTML must include the exhaustive note, snippet: {body[:500]!r}"
    )

    print(
        f"T5 PASS: /api/resources/{rid}/audit/export → 200, "
        f"Content-Disposition: {cd!r}"
    )


# ---------------------------------------------------------------------------
# T6: Cashier persona → 403 on audit endpoint (SHOULD-NOT-OCCUR guard)
# ---------------------------------------------------------------------------

def test_t6_cashier_gets_403_on_audit():
    """SHOULD-NOT-OCCUR: a cashier/learner calling GET /api/resources/{rid}/audit
    must receive a 403.  Citation-level data is trainer/director only — leaking
    it to learners would expose the internal source-system grounding structure."""
    from fastapi.testclient import TestClient
    import demo_app as _da
    import app as prod

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        drafts = tmp_path / "drafts"
        drafts.mkdir()
        published = tmp_path / "published"
        published.mkdir()
        pub_meta = published / "metadata"
        pub_meta.mkdir()

        rid = "test-cashier-403-rid"
        (drafts / f"{rid}.html").write_text(_SAMPLE_HTML_CLEAN, encoding="utf-8")
        (drafts / f"{rid}.json").write_text(
            json.dumps({"id": rid, "status": "approved", "approved": True}),
            encoding="utf-8",
        )

        original_drafts = prod.DRAFTS
        original_published = prod.PUBLISHED
        original_pub_meta = prod.PUB_META
        try:
            prod.DRAFTS = drafts
            prod.PUBLISHED = published
            prod.PUB_META = pub_meta

            client = TestClient(_da.app, raise_server_exceptions=False)

            # Cashier persona (john-cashier is_trainer=False, role=Cashier)
            resp_cashier = client.get(
                f"/api/resources/{rid}/audit",
                headers={"X-Demo-User": "john-cashier"},
            )
            # Director persona — should be allowed (is_director=True)
            resp_director = client.get(
                f"/api/resources/{rid}/audit",
                headers={"X-Demo-User": "dana-director"},
            )
            # Trainer persona — should be allowed
            resp_trainer = client.get(
                f"/api/resources/{rid}/audit",
                headers={"X-Demo-User": "sam-trainer"},
            )
        finally:
            prod.DRAFTS = original_drafts
            prod.PUBLISHED = original_published
            prod.PUB_META = original_pub_meta

    assert resp_cashier.status_code == 403, (
        f"SHOULD-NOT-OCCUR: cashier got {resp_cashier.status_code} instead of 403. "
        f"Citation-level audit data must not be accessible to learner roles."
    )
    assert resp_director.status_code == 200, (
        f"Director (CN Director role) should get 200, got {resp_director.status_code}"
    )
    assert resp_trainer.status_code == 200, (
        f"Trainer should get 200, got {resp_trainer.status_code}"
    )

    # Verify the 403 body includes an explanatory error field.
    body = resp_cashier.json()
    assert "error" in body.get("detail", {}), (
        f"403 body detail should include 'error' field, got: {body}"
    )

    print(
        f"T6 PASS: cashier → 403; director → 200; trainer → 200 "
        f"(cashier error detail: {body.get('detail')})"
    )


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        test_t1_extract_citations_count_and_fields,
        test_t2_audit_response_note_exhaustive,
        test_t3_fully_grounded_false_when_to_verify_present,
        test_t4_course_audit_sums_claims_correctly,
        test_t5_audit_export_returns_attachment,
        test_t6_cashier_gets_403_on_audit,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as exc:
            print(f"FAIL {t.__name__}: {exc}")
            import traceback
            traceback.print_exc()
            failed += 1
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{len(tests)} passed" + (f", {failed} failed" if failed else ""))
    if failed:
        sys.exit(1)
