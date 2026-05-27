"""Smoke test the core POC functions without spinning up the HTTP server or calling claude.

  - Imports server + review modules (catches syntax errors and import-time failures).
  - Runs PDF→MD extraction on a real Eligibility PDF.
  - Filters the CSV for Eligibility.
  - Fabricates a tiny proposals dict and runs apply_edits + md_to_pdf.

If this all passes, the only piece not exercised is the live `claude -p` call. Run the server
with `python app/server.py` to test that interactively.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
REPO = APP_DIR.parent
sys.path.insert(0, str(APP_DIR))

# Imports
from server import (  # noqa: E402
    DEFAULT_CSV,
    MODULES,
    extract_pdf_to_md,
    filter_csv_for_module,
    guess_module_from_filename,
)
from review import apply_edits, inline_diff_html, md_to_pdf  # noqa: E402


def step(name):
    print(f"\n== {name} ==")


def main():
    step("1. Module list discovered")
    print(MODULES)

    step("2. guess_module_from_filename heuristic")
    for fn in [
        "GUIDE-036-add-applications-quick-guide.pdf",
        "Eligibility_Sampling.pdf",
        "Random_filename.pdf",
        "AccountManagement_quick.pdf",
    ]:
        print(f"  {fn:50} -> {guess_module_from_filename(fn)}")

    step("3. PDF→MD extraction on a real Eligibility PDF")
    sample_pdf = REPO / "raw" / "guides" / "pdf" / "SC" / "Eligibility" / "Quick-Guide" / "GUIDE-042-sampling-quick-guide.pdf"
    if not sample_pdf.exists():
        print(f"  SKIP: {sample_pdf} not found")
        return 1
    md = extract_pdf_to_md(sample_pdf)
    print(f"  extracted {len(md)} chars, first 200:")
    print("  " + md[:200].replace("\n", "\n  "))

    step("4. CSV filter for Eligibility (using repo-default CSV)")
    if not DEFAULT_CSV.exists():
        print(f"  SKIP: {DEFAULT_CSV} not found")
        return 1
    tickets = filter_csv_for_module(DEFAULT_CSV, "Eligibility")
    print(f"  filtered {len(tickets)} eligibility tickets")
    if tickets:
        print(f"  first ticket: {tickets[0]['key']} — {tickets[0]['summary'][:80]}")

    step("5. apply_edits on a fabricated proposals list")
    fake_md = "# Test guide\n\n## Steps\n1. First step\n2. Second step\n"
    fake_proposals = [
        {
            "id": "e1",
            "ticket": "NXT-1",
            "operation": "insert_after",
            "before": "1. First step",
            "after": "   - New sub-note added by approval.",
        },
        {
            "id": "e2",
            "ticket": "NXT-2",
            "operation": "replace",
            "before": "## Steps",
            "after": "## Steps (revised)",
        },
        {
            "id": "e3",
            "ticket": "NXT-3",
            "operation": "insert_after",
            "before": "2. Second step",
            "after": "3. Rejected step — should not appear",
        },
    ]
    final_md, applied_list, skipped_list = apply_edits(fake_md, fake_proposals, approved_ids={"e1", "e2"})
    print("  applied result:")
    print("  " + final_md.replace("\n", "\n  "))
    assert "New sub-note" in final_md
    assert "## Steps (revised)" in final_md
    assert "Rejected step" not in final_md
    assert len(applied_list) == 2 and [a["id"] for a in applied_list] == ["e1", "e2"]
    assert skipped_list == []
    print("  OK approve/reject semantics correct (applied={}, skipped={})".format(len(applied_list), len(skipped_list)))

    # Also test the "skipped because prior edit ate the anchor" case
    fake2 = "alpha\nbeta\ngamma\n"
    props2 = [
        {"id": "x1", "ticket": "NXT-A", "operation": "replace", "before": "beta", "after": "BETA"},
        {"id": "x2", "ticket": "NXT-B", "operation": "insert_after", "before": "beta", "after": "new line"},
    ]
    md2, app2, skip2 = apply_edits(fake2, props2, approved_ids={"x1", "x2"})
    assert app2[0]["id"] == "x1"
    assert skip2 and skip2[0]["id"] == "x2"
    print("  OK skipped-edit detection: applied={} skipped={}".format(len(app2), len(skip2)))

    step("6. inline_diff_html renders without error")
    html = inline_diff_html("foo\nbar\nbaz", "foo\nBAR\nbaz", "replace")
    print(f"  rendered {len(html)} chars of HTML")
    assert "diff-table" in html

    step("7. md_to_pdf produces a real PDF with styled markdown")
    out_md = APP_DIR / "jobs" / "_smoke.md"
    out_pdf = APP_DIR / "jobs" / "_smoke.pdf"
    out_md.parent.mkdir(exist_ok=True)
    rich = """---
id: TEST
title: "Smoke test"
---

# Sampling Quick Guide

The Sampling function allows users to generate sample applications used in the **verification process**.

## Schedule Verification Samples

1. Click the SCHEDULE SAMPLE button in the top right corner of the page.
2. Pick a date.
3. Click Save.

## Verification Type

- A single sample (Standard)
- Multiple smaller samples (Rolling)

> Note: rolling samples require additional dates.

The Sampling page shows the selected application date and the student count date for each scheduled sample.
"""
    out_md.write_text(rich, encoding="utf-8")
    md_to_pdf(out_md, out_pdf)
    size = out_pdf.stat().st_size
    print(f"  wrote {out_pdf.name} ({size} bytes)")
    assert out_pdf.exists() and size > 1000, f"PDF too small ({size}b)"
    # Sanity-check the raw PDF for header glyph presence (Helvetica-Bold instead of mono dump)
    pdf_bytes = out_pdf.read_bytes()
    assert b"Helvetica-Bold" in pdf_bytes, "PDF didn't embed Helvetica-Bold — heading style likely broken"
    assert b"## " not in pdf_bytes, "Raw markdown `## ` leaked into PDF text — rendering didn't strip header markers"
    print("  OK PDF embeds Helvetica-Bold (real headers, not raw `##` markers)")

    print("\nALL SMOKE CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
