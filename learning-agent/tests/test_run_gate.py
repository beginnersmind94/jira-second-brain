import os
import demo
from citation_gate import run_gate

CLEAN = '<h1>T</h1>\n<p>Alpha claim.<!-- Source: [[NXT-1001:AC]] "Alpha." --></p>'
# tier_lie: the span "Alpha." lives in AC, but this comment claims DESC.
DIRTY = '<h1>T</h1>\n<p>Bad.<!-- Source: [[NXT-1001:DESC]] "Alpha." --></p>'


def _fix():
    demo._FIX = {"tickets": {"NXT-1001": {"ac": "Alpha.", "rn": "", "rn_internal": "", "desc": "Delta."}},
                 "epics": {}}


def test_substring_mode_is_byte_identical():
    _fix(); os.environ.pop("GATE_MODE", None)
    g = run_gate(CLEAN)
    assert g["citations"] is None
    assert g["substring"] == demo.validate_citations(CLEAN)
    assert g["passed"] is True


def test_tier_lie_fails():
    _fix(); os.environ.pop("GATE_MODE", None)
    g = run_gate(DIRTY)
    assert g["passed"] is False
    assert g["substring"]["tier_lie"] == 1


def test_both_mode_coverage_flags_uncited_claim():
    _fix(); os.environ["GATE_MODE"] = "both"
    try:
        html = CLEAN + "\n<p>An uncited overreaching claim with no source.</p>"
        g = run_gate(html)
        assert g["citations"]["uncited_claims"] == 1
        assert g["passed"] is False
    finally:
        os.environ.pop("GATE_MODE", None)
