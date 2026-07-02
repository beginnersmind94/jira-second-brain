"""Proves the capability Version B adds over Version A: catching an over-claim (a substantive
sentence with NO citation). Runs without an API key."""
import os
import demo
from citation_gate import run_gate


def _fix():
    demo._FIX = {"tickets": {"NXT-1001": {"ac": "Alpha.", "rn": "", "rn_internal": "", "desc": ""}},
                 "epics": {}}


# One properly-cited claim + one invented, uncited claim.
OVERREACH = (
    "<h1>Guide</h1>\n"
    '<p>Alpha is required.<!-- Source: [[NXT-1001:AC]] "Alpha." --></p>\n'
    "<p>The system also emails the district superintendent automatically.</p>"
)


def test_version_b_catches_overreach():
    _fix(); os.environ["GATE_MODE"] = "both"
    try:
        g = run_gate(OVERREACH)
        assert g["passed"] is False
        assert g["citations"]["uncited_claims"] >= 1
    finally:
        os.environ.pop("GATE_MODE", None)


def test_version_a_passes_overreach_through():
    _fix(); os.environ.pop("GATE_MODE", None)   # substring / Version A
    g = run_gate(OVERREACH)
    assert g["citations"] is None
    assert g["passed"] is True   # substring only checks present citations
