"""eval/test_flashcard_store.py — Deterministic tests for flashcard_store.py

Test coverage per the B2 spec:
  1. create_deck() with all cards verbatim in guide HTML -> deck saved, all cards present
  2. create_deck() with one paraphrased card -> that card dropped, others kept
     (SHOULD-NOT-OCCUR: paraphrased card must not survive the gate)
  3. approve_deck() -> status flips to "approved"
  4. check_drift() when guide HTML has changed -> drifted: True, deck reverts to "draft"
     (SHOULD-NOT-OCCUR: drifted deck must not stay approved)
  5. Fewer than 3 surviving cards -> ValueError raised (endpoint returns 422)
  6. Round-trip: create -> approve -> reload from disk -> fields intact

Run with:
    python -m pytest eval/test_flashcard_store.py -v
or from the learning-agent/ directory:
    python eval/test_flashcard_store.py
"""
from __future__ import annotations

import json
import sys
import tempfile
import shutil
from pathlib import Path

# Allow running directly from the learning-agent/ dir or via pytest from project root.
_HERE = Path(__file__).resolve().parent
_LA = _HERE.parent
if str(_LA) not in sys.path:
    sys.path.insert(0, str(_LA))

import flashcard_store as _fs


# ── Minimal guide HTML for testing ───────────────────────────────────────────

_GUIDE_HTML = """
<html><body>
<h2>Item Creation Workflow</h2>
<p>Use the add button to insert a new row in the Units grid for each pack size you need.</p>
<p>Cost and value fields are completed during the final finish tasks, not during initial setup.</p>
<h2>Inventory Readiness</h2>
<p>An Inventory Readiness banner is always displayed and operates as a live status indicator.</p>
<p>To achieve Inventory Readiness a serving size with Amount = 1 must be linked to a pack size.</p>
</body></html>
"""

# Verbatim quotes that exist in _GUIDE_HTML (after strip + normalise).
_QUOTE_A = "Use the add button to insert a new row in the Units grid for each pack size you need."
_QUOTE_B = "Cost and value fields are completed during the final finish tasks, not during initial setup."
_QUOTE_C = "An Inventory Readiness banner is always displayed and operates as a live status indicator."

# A paraphrased quote that does NOT appear verbatim.
_QUOTE_PARAPHRASE = "Click the plus button to add more rows to the pack size grid."

_GOOD_CARDS = [
    {"front": "What do you do to add a pack size?", "back": "Use the add button.",
     "source_quote": _QUOTE_A, "section": "Item Creation Workflow", "card_type": "procedural"},
    {"front": "When do you complete cost fields?", "back": "During finish tasks.",
     "source_quote": _QUOTE_B, "section": "Item Creation Workflow", "card_type": "procedural"},
    {"front": "What does the Inventory Readiness banner indicate?", "back": "Live status.",
     "source_quote": _QUOTE_C, "section": "Inventory Readiness", "card_type": "definitional"},
]


def _with_tmp_store(fn):
    """Decorator: run fn with a temporary FLASHCARDS_DIR so tests don't touch real data."""
    def wrapper(*args, **kwargs):
        orig = _fs.FLASHCARDS_DIR
        tmp = Path(tempfile.mkdtemp()) / "flashcards"
        tmp.mkdir(parents=True)
        _fs.FLASHCARDS_DIR = tmp
        try:
            return fn(*args, **kwargs)
        finally:
            _fs.FLASHCARDS_DIR = orig
            shutil.rmtree(str(tmp.parent), ignore_errors=True)
    return wrapper


# ── Test 1: create_deck with all verbatim cards -> all kept ──────────────────

@_with_tmp_store
def test_create_deck_all_verbatim():
    """All 3 cards have verbatim source_quote -> deck saved with all 3 cards."""
    deck = _fs.create_deck(
        source_rid="test-guide-001",
        title="Test Deck",
        cards=list(_GOOD_CARDS),
        guide_html=_GUIDE_HTML,
    )
    assert deck["status"] == "draft", "New deck must start as draft"
    assert deck["kept"] == 3, f"Expected 3 cards kept, got {deck['kept']}"
    assert deck["dropped"] == 0, f"Expected 0 dropped, got {deck['dropped']}"
    assert len(deck["cards"]) == 3

    # Verify persisted to disk
    loaded = _fs.get_deck(deck["id"])
    assert loaded is not None, "Deck should be persisted to disk"
    assert loaded["id"] == deck["id"]
    assert loaded["source_resource_id"] == "test-guide-001"
    assert loaded["provenance"] == "ai_grounded"

    print("PASS test_create_deck_all_verbatim")


# ── Test 2: paraphrased card dropped, others kept ────────────────────────────
# SHOULD-NOT-OCCUR gate: a card with a paraphrased source_quote must not survive.

@_with_tmp_store
def test_create_deck_paraphrased_card_dropped():
    """One card with a paraphrased source_quote -> dropped; the other 3 kept."""
    mixed = list(_GOOD_CARDS) + [
        {"front": "How do you add a pack size row?", "back": "Click the plus button.",
         "source_quote": _QUOTE_PARAPHRASE,   # NOT verbatim in guide
         "section": "Item Creation Workflow", "card_type": "procedural"},
    ]
    deck = _fs.create_deck(
        source_rid="test-guide-001",
        title="Mixed Deck",
        cards=mixed,
        guide_html=_GUIDE_HTML,
    )
    assert deck["kept"] == 3, f"Expected 3 kept, got {deck['kept']}"
    assert deck["dropped"] == 1, f"Expected 1 dropped, got {deck['dropped']}"

    # Verify no card has the paraphrased quote
    quotes = [c["source_quote"] for c in deck["cards"]]
    assert _QUOTE_PARAPHRASE not in quotes, "Paraphrased card must not survive the gate"

    print("PASS test_create_deck_paraphrased_card_dropped")


# ── Test 3: approve_deck flips status to approved ────────────────────────────

@_with_tmp_store
def test_approve_deck():
    """approve_deck() re-runs the gate and flips status to 'approved'."""
    deck = _fs.create_deck(
        source_rid="test-guide-002",
        title="Approvable Deck",
        cards=list(_GOOD_CARDS),
        guide_html=_GUIDE_HTML,
    )
    assert deck["status"] == "draft"

    approved = _fs.approve_deck(deck["id"], guide_html=_GUIDE_HTML)
    assert approved["status"] == "approved", f"Expected 'approved', got {approved['status']!r}"
    assert approved["approved_at"] is not None, "approved_at should be set"

    # Verify persisted
    reloaded = _fs.get_deck(deck["id"])
    assert reloaded["status"] == "approved"

    print("PASS test_approve_deck")


# ── Test 4: check_drift reverts approved deck to draft ───────────────────────
# SHOULD-NOT-OCCUR gate: a drifted approved deck must not stay approved.

@_with_tmp_store
def test_check_drift_reverts_to_draft():
    """When guide HTML changes, check_drift detects it and reverts deck to draft."""
    deck = _fs.create_deck(
        source_rid="test-guide-003",
        title="Drift Test Deck",
        cards=list(_GOOD_CARDS),
        guide_html=_GUIDE_HTML,
    )
    # Approve it first
    _fs.approve_deck(deck["id"], guide_html=_GUIDE_HTML)
    assert _fs.get_deck(deck["id"])["status"] == "approved"

    # Simulate guide HTML change
    changed_html = _GUIDE_HTML + "\n<p>New section added after deck was built.</p>"
    result = _fs.check_drift(deck["id"], guide_html=changed_html)

    assert result["drifted"] is True, "Should detect drift when guide HTML changed"
    assert result["hash_was"] != result["hash_now"], "Hashes should differ"
    assert result["status_after"] == "draft", "Drifted deck must revert to draft"

    # Verify persisted reversion
    reloaded = _fs.get_deck(deck["id"])
    assert reloaded["status"] == "draft", "Drifted deck must not stay approved on disk"
    assert reloaded["approved_at"] is None, "approved_at must be cleared on drift"

    print("PASS test_check_drift_reverts_to_draft")


# ── Test 5: fewer than 3 surviving cards raises ValueError (-> 422) ──────────

@_with_tmp_store
def test_insufficient_cards_raises():
    """Only 2 verbatim cards -> ValueError (endpoint should return 422)."""
    two_cards = _GOOD_CARDS[:2]  # Only 2 valid cards
    try:
        _fs.create_deck(
            source_rid="test-guide-004",
            title="Too Few Cards",
            cards=list(two_cards),
            guide_html=_GUIDE_HTML,
        )
        raise AssertionError("Expected ValueError but no exception was raised")
    except ValueError as e:
        assert "insufficient verifiable cards" in str(e).lower() or "need at least" in str(e).lower(), \
            f"Wrong error message: {e}"

    print("PASS test_insufficient_cards_raises")


# ── Test 6: round-trip create -> approve -> reload from disk ─────────────────

@_with_tmp_store
def test_round_trip_fields_intact():
    """Full round-trip: create, approve, reload — all key fields survive."""
    deck = _fs.create_deck(
        source_rid="test-guide-round",
        title="Round-Trip Deck",
        cards=list(_GOOD_CARDS),
        guide_html=_GUIDE_HTML,
    )
    deck_id = deck["id"]

    # Approve
    _fs.approve_deck(deck_id, guide_html=_GUIDE_HTML)

    # Reload from disk
    reloaded = _fs.get_deck(deck_id)
    assert reloaded is not None

    # Check schema fields
    assert reloaded["id"] == deck_id
    assert reloaded["title"] == "Round-Trip Deck"
    assert reloaded["source_resource_id"] == "test-guide-round"
    assert reloaded["status"] == "approved"
    assert reloaded["approved_at"] is not None
    assert reloaded["provenance"] == "ai_grounded"
    assert isinstance(reloaded["source_content_hash"], str) and len(reloaded["source_content_hash"]) == 16
    assert len(reloaded["cards"]) == 3

    # Each card has required fields
    for card in reloaded["cards"]:
        assert "id" in card
        assert "front" in card and card["front"]
        assert "back" in card and card["back"]
        assert "source_quote" in card and card["source_quote"]
        assert "section" in card
        assert "card_type" in card
        assert card["grounded"] is True

    print("PASS test_round_trip_fields_intact")


# ── Test 7: check_drift returns not-drifted when HTML unchanged ───────────────

@_with_tmp_store
def test_no_drift_when_html_unchanged():
    """check_drift returns drifted=False when HTML is the same."""
    deck = _fs.create_deck(
        source_rid="test-guide-nodrift",
        title="No Drift Deck",
        cards=list(_GOOD_CARDS),
        guide_html=_GUIDE_HTML,
    )
    _fs.approve_deck(deck["id"], guide_html=_GUIDE_HTML)

    result = _fs.check_drift(deck["id"], guide_html=_GUIDE_HTML)
    assert result["drifted"] is False
    assert result["status_after"] == "approved", "Undrifted deck must stay approved"

    print("PASS test_no_drift_when_html_unchanged")


# ── Runner ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        test_create_deck_all_verbatim,
        test_create_deck_paraphrased_card_dropped,
        test_approve_deck,
        test_check_drift_reverts_to_draft,
        test_insufficient_cards_raises,
        test_round_trip_fields_intact,
        test_no_drift_when_html_unchanged,
    ]
    passed = failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"FAIL {t.__name__}: {e}")
            failed += 1
    print(f"\n{'='*40}")
    print(f"Results: {passed} passed, {failed} failed")
    if failed:
        sys.exit(1)
