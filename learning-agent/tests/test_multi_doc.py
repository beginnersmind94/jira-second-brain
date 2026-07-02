"""Deterministic tests for the cross-module combiner (multi_doc). No SDK/network.
Proves a combined doc grounds against the UNION fixture and never hides a violation."""
import demo
import multi_doc as md


def _union():
    # A union fixture: tickets from two different modules, globally-unique keys.
    return {"module": "A + B", "epics": {},
            "tickets": {
                "NXT-1001": {"ac": "Alpha requires a PIN.", "rn": "", "rn_internal": "",
                             "desc": "Delta.", "summary": "Alpha"},
                "NXT-2002": {"ac": "Bravo needs approval.", "rn": "", "rn_internal": "",
                             "desc": "Echo detail.", "summary": "Bravo"},
            }}


DRAFT_A = ('<h1>Inventory: Learning Guide</h1>\n'
           '<h2>What\'s New</h2>\n<p>Alpha requires a PIN.<!-- Source: [[NXT-1001:AC]] "Alpha requires a PIN." --></p>\n\n'
           '<h2>Sources</h2>\n<ul>\n<li><code>NXT-1001</code> — Alpha</li>\n</ul>')
DRAFT_B = ('<h1>Eligibility: Learning Guide</h1>\n'
           '<h2>What\'s New</h2>\n<p>Bravo needs approval.<!-- Source: [[NXT-2002:AC]] "Bravo needs approval." --></p>\n\n'
           '<h2>Sources</h2>\n<ul>\n<li><code>NXT-2002</code> — Bravo</li>\n</ul>')


def test_ac1_combined_validates_across_modules():
    fx = _union(); demo._FIX = fx
    combined = md.combine([("Inventory", DRAFT_A), ("Eligibility", DRAFT_B)], "Combined RN", fx)
    v = demo.validate_citations(combined)
    assert v["tier_lie"] == 0 and v["quote_not_found"] == 0
    assert v["ok"] == 2   # both modules' citations validated against the union


def test_ac2_violation_not_hidden():
    fx = _union(); demo._FIX = fx
    # cite NXT-2002's DESC span ("Echo detail.") but label it AC -> tier_lie, must surface
    bad = DRAFT_B.replace('[[NXT-2002:AC]] "Bravo needs approval."', '[[NXT-2002:AC]] "Echo detail."')
    combined = md.combine([("Inventory", DRAFT_A), ("Eligibility", bad)], "Combined RN", fx)
    v = demo.validate_citations(combined)
    assert v["tier_lie"] >= 1


def test_ac3_structure():
    fx = _union(); demo._FIX = fx
    combined = md.combine([("Inventory", DRAFT_A), ("Eligibility", DRAFT_B)], "Combined RN", fx)
    assert combined.count("<h1>") == 1
    assert "<h2>Inventory</h2>" in combined and "<h2>Eligibility</h2>" in combined
    assert combined.count("<h2>Sources</h2>") == 1     # ONE merged Sources, not per-module
    assert "NXT-1001" in combined and "NXT-2002" in combined


def test_union_fixture_merges_without_dropping(monkeypatch):
    def fake_load(m):
        return {"Inventory": {"tickets": {"NXT-1001": {"summary": "a"}}, "epics": {}},
                "Eligibility": {"tickets": {"NXT-2002": {"summary": "b"}}, "epics": {}}}[m]
    monkeypatch.setattr(md, "_load_fixture", fake_load)
    u = md.union_fixture(["Inventory", "Eligibility"])
    assert set(u["tickets"]) == {"NXT-1001", "NXT-2002"}
