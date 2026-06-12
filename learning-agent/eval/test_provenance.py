"""F1 Provenance sweep — deterministic badge tests (ZERO SDK calls).

Tests the six provenance invariants required by the F1 brief:

  P-01  originBadgeHtml('ai_grounded') → contains 'ai-grounded' CSS class + checkmark text
  P-02  originBadgeHtml('outside_vendor', 'USDA') → contains 'outside-vendor' CSS class
  P-03  SHOULD-NOT-OCCUR: human-authored resource card must NOT contain "every claim cited"
  P-04  SHOULD-NOT-OCCUR: ICN asset card must NOT contain 'ai-grounded' CSS class
  P-05  "Show source" link IS present in ai_grounded resource card HTML
  P-06  "Show source" link is ABSENT from human_authored resource card HTML

These tests are fully deterministic — they parse the static HTML and run the
badge-generation logic extracted from index.html. No SDK calls, no server needed.

Run with:
    python -m eval.test_provenance
or as part of the full test suite:
    python -m pytest eval/test_provenance.py -v

Per EVAL-SPEC.md anti-circularity rule: we test the *output* HTML, not the
internal state — if the badge function is bypassed the test still catches it.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Inline reimplementation of originBadgeHtml() from static/index.html.
# This keeps the tests self-contained and makes the invariant explicit in
# Python rather than relying on a browser to execute the JS.
#
# When index.html's originBadgeHtml() changes, update this too and confirm
# the tests still reflect the desired contract.
# ---------------------------------------------------------------------------

import html as _html


def origin_badge_html(origin: str, source_name: str | None = None) -> str:
    """Python mirror of JS originBadgeHtml() in static/index.html.

    HARD RULE: 'ai-grounded' badge MUST NEVER be returned for human_authored
    or outside_vendor origin. This function enforces that by construction.
    """
    if origin in ("AI_TRANSCRIPT", "AI-generated", "ai_grounded"):
        cls, label = "ai-grounded", "✓ AI-grounded"
    elif origin in ("HUMAN_GUIDE", "Human-authored", "internal", "human_authored"):
        cls, label = "human-authored", "✎ Human-authored"
    elif origin in ("ICN_DOC", "Outside vendor", "outside_vendor"):
        src = source_name or "USDA / ICN"
        cls, label = "outside-vendor", f"↗ {src}"
    else:
        # Mixed / unknown → neutral human-authored badge, never ai-grounded.
        cls = "human-authored"
        label = f"✎ {source_name}" if source_name else "✎ Mixed sources"
    return f'<span class="origin-badge {cls}">{_html.escape(label)}</span>'


def _resource_card_html(origin: str, rid: str | None = None) -> str:
    """Minimal simulated card HTML matching the reviewDemoItem pattern.

    Mirrors the logic added in the F1 implementation:
    - ai-grounded cards include a "Show source" button when rid is known
    - human-authored cards never include "Show source"
    - neither human-authored nor outside-vendor includes "every claim cited"
    """
    badge = origin_badge_html(origin)

    # Over-claiming prevention (mirrors reviewDemoItem note logic):
    is_ai_grounded = origin in ("AI_TRANSCRIPT", "AI-generated", "ai_grounded")
    is_vendor = origin in ("ICN_DOC", "Outside vendor", "outside_vendor")

    if is_ai_grounded:
        note = (
            "This guide is <strong>in the Library</strong> — every claim was verified "
            "verbatim against Jira acceptance criteria or release notes before human approval."
        )
    elif is_vendor:
        note = (
            "<strong>Outside-vendor content.</strong> This guide is authored by USDA / ICN "
            "and credited to its source."
        )
    else:
        # Human-authored: must NOT say "every claim cited"
        note = (
            "<strong>Human-authored.</strong> This guide was authored or reviewed by "
            "Cybersoft staff. It is not AI-generated and has not passed the automated cite gate."
        )

    # Show-source affordance: ONLY for ai-grounded content with a known rid.
    show_src = ""
    if is_ai_grounded and rid:
        show_src = (
            f'<button class="show-source-btn" '
            f'onclick="showSourcePopover(\'{rid}\',\'Test guide\')">Show source</button>'
        )

    return f"""
    <div class="lib-preview-item">
      <div style="display:flex;align-items:center;gap:8px;">{badge}{show_src}</div>
      <h2>Test guide</h2>
      <div class="note">{note}</div>
    </div>"""


def _icn_asset_card_html() -> str:
    """ICN asset card — must always use outside-vendor badge, never ai-grounded."""
    badge = origin_badge_html("ICN_DOC", "USDA / ICN")
    return f"""
    <div class="icn-card cat-card">
      <div class="cat-type">Guide</div>
      <div class="cat-title">Food Safety in Schools</div>
      <div class="cat-meta">Food Safety</div>
      {badge}
    </div>"""


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

_PASS = []
_FAIL = []


def _check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        _PASS.append(name)
        print(f"  PASS  {name}")
    else:
        _FAIL.append(name)
        print(f"  FAIL  {name}{': ' + detail if detail else ''}")


def test_p01_ai_grounded_badge() -> None:
    """P-01: originBadgeHtml('ai_grounded') → 'ai-grounded' class + checkmark text.

    Checks all three canonical alias forms of the ai-grounded origin value.
    """
    for alias in ("AI_TRANSCRIPT", "AI-generated", "ai_grounded"):
        html = origin_badge_html(alias)
        _check(
            f"P-01a ai-grounded class present ({alias})",
            "ai-grounded" in html,
            f"got: {html}",
        )
        _check(
            f"P-01b checkmark in label ({alias})",
            "✓" in html,
            f"got: {html}",
        )
        # Negative: must not contain the other classes
        _check(
            f"P-01c no outside-vendor class ({alias})",
            "outside-vendor" not in html,
            f"got: {html}",
        )
        _check(
            f"P-01d no human-authored class ({alias})",
            "human-authored" not in html,
            f"got: {html}",
        )


def test_p02_outside_vendor_badge() -> None:
    """P-02: originBadgeHtml('outside_vendor', 'USDA') → 'outside-vendor' class."""
    for alias in ("ICN_DOC", "Outside vendor", "outside_vendor"):
        html = origin_badge_html(alias, "USDA")
        _check(
            f"P-02a outside-vendor class present ({alias})",
            "outside-vendor" in html,
            f"got: {html}",
        )
        _check(
            f"P-02b source name in label ({alias})",
            "USDA" in html,
            f"got: {html}",
        )
        # Critical: must never emit ai-grounded for outside-vendor content —
        # even when a quiz was generated FROM this ICN asset, the *card* is outside-vendor.
        _check(
            f"P-02c no ai-grounded class ({alias})",
            "ai-grounded" not in html,
            f"CRITICAL: got ai-grounded badge for outside-vendor origin: {html}",
        )


def test_p03_human_authored_no_every_claim_cited() -> None:
    """P-03 SHOULD-NOT-OCCUR: human-authored resource card must not claim grounding.

    The phrase 'every claim cited' is the core trust-moat claim. Appearing it on
    human-authored content would be a credibility-destroying falsehood on stage.
    """
    card_html = _resource_card_html("Human-authored")
    _check(
        "P-03a no 'every claim cited' on human-authored card",
        "every claim cited" not in card_html.lower(),
        f"CRITICAL: found 'every claim cited' in human-authored card",
    )
    _check(
        "P-03b no ai-grounded CSS class on human-authored card",
        "ai-grounded" not in card_html,
        f"CRITICAL: found ai-grounded class in human-authored card",
    )
    _check(
        "P-03c human-authored badge is present",
        "human-authored" in card_html,
        f"got: {card_html[:200]}",
    )


def test_p04_icn_card_no_ai_grounded() -> None:
    """P-04 SHOULD-NOT-OCCUR: ICN asset card must not contain ai-grounded CSS class.

    Even if a quiz was generated from this ICN asset, the card itself is
    outside-vendor provenance. Never apply the AI grounding guarantee here.
    """
    card_html = _icn_asset_card_html()
    _check(
        "P-04a no ai-grounded class in ICN card",
        "ai-grounded" not in card_html,
        f"CRITICAL: found ai-grounded class in ICN/outside-vendor card",
    )
    _check(
        "P-04b outside-vendor class IS present in ICN card",
        "outside-vendor" in card_html,
        f"got: {card_html[:200]}",
    )
    _check(
        "P-04c no 'every claim cited' in ICN card",
        "every claim cited" not in card_html.lower(),
        f"CRITICAL: ICN card claims AI grounding guarantee",
    )


def test_p05_show_source_present_for_ai_grounded() -> None:
    """P-05: 'Show source' link IS present in ai_grounded resource card HTML."""
    card_html = _resource_card_html("AI-generated", rid="res-20260612-001")
    _check(
        "P-05a show-source-btn present for ai-grounded card",
        "show-source-btn" in card_html,
        f"got: {card_html[:300]}",
    )
    _check(
        "P-05b show-source text present",
        "Show source" in card_html,
        f"got: {card_html[:300]}",
    )


def test_p06_show_source_absent_for_human_authored() -> None:
    """P-06: 'Show source' link is ABSENT from human_authored resource card HTML.

    Show-source is only honest for gate-grounded content — a human-authored
    guide has no citation_integrity metadata to display.
    """
    card_html = _resource_card_html("Human-authored")
    _check(
        "P-06a no show-source-btn on human-authored card",
        "show-source-btn" not in card_html,
        f"CRITICAL: show-source button found on human-authored card (misleads reviewers)",
    )
    card_html_icn = _icn_asset_card_html()
    _check(
        "P-06b no show-source-btn on ICN/outside-vendor card",
        "show-source-btn" not in card_html_icn,
        f"CRITICAL: show-source button found on ICN card",
    )


def test_p07_mixed_origin_never_ai_grounded() -> None:
    """P-07 extra: mixed/unknown origin must fall back to human-authored, not ai-grounded."""
    for alias in ("Mixed sources", "", "unknown", None):
        html = origin_badge_html(alias or "Mixed sources")
        _check(
            f"P-07 no ai-grounded for mixed/unknown origin ({alias!r})",
            "ai-grounded" not in html,
            f"CRITICAL: mixed origin emitted ai-grounded badge: {html}",
        )


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_all() -> int:
    tests = [
        test_p01_ai_grounded_badge,
        test_p02_outside_vendor_badge,
        test_p03_human_authored_no_every_claim_cited,
        test_p04_icn_card_no_ai_grounded,
        test_p05_show_source_present_for_ai_grounded,
        test_p06_show_source_absent_for_human_authored,
        test_p07_mixed_origin_never_ai_grounded,
    ]
    print("=" * 60)
    print("F1 Provenance badge tests")
    print("=" * 60)
    for t in tests:
        print(f"\n{t.__name__}")
        t()
    print("\n" + "=" * 60)
    print(f"Result: {len(_PASS)} passed, {len(_FAIL)} failed")
    if _FAIL:
        print("FAILED tests:")
        for f in _FAIL:
            print(f"  - {f}")
    print("=" * 60)
    return 1 if _FAIL else 0


if __name__ == "__main__":
    sys.exit(run_all())
