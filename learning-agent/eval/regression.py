"""Deterministic regression suite (REG-01..15) — ZERO SDK calls.

Pins every historical failure of the grounding pipeline against the REAL grading
functions, using constructed/fixture HTML. Runs in seconds; safe to run on every
pipeline change. Exits non-zero if any regression FAILs.

    python -m eval.regression [--module "Item Management"]

Per the eval spec's anti-circularity rule: we grade the RAW artifact and test
enforce_citations separately (it's the backstop, not part of the grade path).
Test data (quotes/spans) is derived live from the fixture so the suite is robust
to whatever tickets exist — no hard-coded ticket contents.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import demo
import demo_d

PARA = 'zzqq this paraphrase string appears in no source field whatsoever qqzz'


# ── fixture-derived test-data helpers ─────────────────────────────────────────
def _span_of_tier(key: str, tier: str):
    reg, by = demo_d.build_registry([key])
    for cid in by.get(key, []):
        if reg[cid]["tier"] == tier:
            return cid, reg[cid]["span"]
    return None, None


def _ticket_with_tier(tier: str, limit: int = 600):
    for k in list(demo._FIX["tickets"])[:limit]:
        cid, span = _span_of_tier(k, tier)
        if cid:
            return k, cid, span
    return None, None, None


def _ticket_empty_ac_with_desc(limit: int = 1200):
    for k in list(demo._FIX["tickets"])[:limit]:
        ac_cid, _ = _span_of_tier(k, "AC")
        desc_cid, desc_span = _span_of_tier(k, "DESC")
        if ac_cid is None and desc_cid is not None:
            return k, desc_cid, desc_span
    return None, None, None


def _cite(key: str, tier: str, span: str) -> str:
    return f'<p>A claim.<!-- Source: [[{key}:{tier}]] "{span}" --></p>'


# ── checks: each returns (passed: bool | None, detail). None = SKIP ────────────
def reg_01_enforce_relabels_tier_lie():
    k, _, span = _ticket_with_tier("DESC")
    if not k:
        return None, "no ticket with a DESC span in fixture"
    html = _cite(k, "AC", span)  # DESC text mislabeled as AC = the cardinal sin
    v0 = demo.validate_citations(html)
    fixed, counts = demo.enforce_citations(html)
    v1 = demo.validate_citations(fixed)
    ok = (v0["tier_lie"] >= 1 and counts["relabeled"] >= 1
          and f"[[{k}:DESC]]" in fixed and v1["tier_lie"] == 0)
    return ok, f"{k}: raw tier_lie={v0['tier_lie']} relabeled={counts['relabeled']} fixed tier_lie={v1['tier_lie']}"


def reg_02_verbatim_ac_is_ok():
    k, _, span = _ticket_with_tier("AC")
    if not k:
        return None, "no ticket with an AC span"
    v = demo.validate_citations(_cite(k, "AC", span))
    ok = v["ok"] == 1 and v["tier_lie"] == 0 and v["quote_not_found"] == 0 and v["tokened"] == 1
    return ok, f"{k}: ok={v['ok']} tier_lie={v['tier_lie']} not_found={v['quote_not_found']} tokened={v['tokened']}"


def reg_03_paraphrase_is_not_found():
    k, _, _ = _ticket_with_tier("AC")
    if not k:
        return None, "no ticket with an AC span"
    v = demo.validate_citations(_cite(k, "AC", PARA))
    ok = v["quote_not_found"] == 1 and v["ok"] == 0
    return ok, f"{k}: not_found={v['quote_not_found']} ok={v['ok']}"


def reg_04_assemble_valid_and_invalid_ids():
    k, _, _ = _ticket_with_tier("AC")
    if not k:
        return None, "no ticket with an AC span"
    reg, by = demo_d.build_registry([k])
    valid = by[k][0]
    sections = [{"title": "X", "html": f"<h2>X</h2><p>a [CITE:{valid}] b [CITE:NXT-99999:AC:99]</p>"}]
    html, rep = demo_d.assemble("Item Management", sections, reg)
    ok = rep["rendered"] >= 1 and rep["invalid_cite_id"] == 1 and "INVALID_CITE_ID" in html
    return ok, f"rendered={rep['rendered']} invalid_cite_id={rep['invalid_cite_id']}"


def reg_05_enforce_leaves_correct_untouched():
    k, _, span = _ticket_with_tier("AC")
    if not k:
        return None, "no ticket with an AC span"
    html = _cite(k, "AC", span)
    fixed, counts = demo.enforce_citations(html)
    ok = counts["relabeled"] == 0 and fixed == html
    return ok, f"{k}: relabeled={counts['relabeled']} byte_identical={fixed == html}"


def reg_06_enforce_no_fabricate_for_not_found():
    k, _, _ = _ticket_with_tier("AC")
    if not k:
        return None, "no ticket with an AC span"
    html = _cite(k, "AC", PARA)
    fixed, counts = demo.enforce_citations(html)
    v = demo.validate_citations(fixed)
    ok = counts["relabeled"] == 0 and v["quote_not_found"] == 1
    return ok, f"{k}: relabeled={counts['relabeled']} not_found_after={v['quote_not_found']}"


def reg_07_registry_tier_binding():
    keys = [k for k, *_ in [_ticket_with_tier("AC"), _ticket_with_tier("DESC")] if k]
    if not keys:
        return None, "no usable tickets"
    reg, _ = demo_d.build_registry(keys)
    bad = []
    for cid, e in reg.items():
        rec = demo._FIX["tickets"].get(e["issue"]) or demo._FIX["epics"].get(e["issue"]) or {}
        field = demo._FIELD_BY_TIER[e["tier"]]
        if demo._norm(e["span"]) not in demo._norm(rec.get(field, "")):
            bad.append(cid)
    return len(bad) == 0, f"{len(reg)} spans checked, {len(bad)} mis-bound"


def reg_08_format_constants():
    want = ("long-form", "micro-guide", "tldr", "release-notes")
    ok = demo_d.VALID_FORMATS == want
    return ok, f"VALID_FORMATS={demo_d.VALID_FORMATS}"


def reg_09_format_spec_budget_keys():
    want = set(demo_d.VALID_FORMATS)
    ok = (set(demo_d._FORMAT_SPEC) == want and set(demo_d._FORMAT_BUDGET) == want
          and set(demo_d._FORMAT_LABEL) == want)
    return ok, f"spec={set(demo_d._FORMAT_SPEC)} budget={set(demo_d._FORMAT_BUDGET)} label={set(demo_d._FORMAT_LABEL)}"


def reg_10_transcript_counted_separately():
    v = demo.validate_citations("<p>Voice.<!-- Source: transcript [02:01] --></p>")
    ok = v["transcript"] == 1 and v["tokened"] == 0 and v["tier_lie"] == 0 and v["quote_not_found"] == 0
    return ok, f"transcript={v['transcript']} tokened={v['tokened']} tier_lie={v['tier_lie']}"


def reg_11_assemble_appends_sources():
    k, _, _ = _ticket_with_tier("AC")
    if not k:
        return None, "no ticket with an AC span"
    reg, by = demo_d.build_registry([k])
    html, rep = demo_d.assemble("Item Management", [{"title": "X", "html": f"<h2>X</h2><p>a [CITE:{by[k][0]}]</p>"}], reg)
    ok = "<h2>Sources</h2>" in html and all(f"<code>{i}</code>" in html for i in rep["issues"])
    return ok, f"sources_present={'<h2>Sources</h2>' in html} issues={sorted(rep['issues'])}"


def reg_12_empty_field_no_spans():
    k, _, _ = _ticket_empty_ac_with_desc()
    if not k:
        return None, "no ticket with empty AC + non-empty DESC"
    ac_cid, _ = _span_of_tier(k, "AC")
    return ac_cid is None, f"{k}: empty-AC produced AC span? {ac_cid is not None}"


def reg_13_words_excludes_comments_and_tags():
    html = '<h2>Title</h2><p>one two three<!-- Source: [[X:AC]] "y z" --></p>'
    n = demo._words(html)
    return n == 4, f"_words={n} (expected 4: Title one two three)"


def reg_14_assemble_tolerates_whitespace_marker():
    k, _, _ = _ticket_with_tier("AC")
    if not k:
        return None, "no ticket with an AC span"
    reg, by = demo_d.build_registry([k])
    cid = by[k][0]
    html, rep = demo_d.assemble("Item Management", [{"title": "X", "html": f"<h2>X</h2><p>a [CITE: {cid} ]</p>"}], reg)
    return rep["rendered"] >= 1, f"rendered={rep['rendered']} (whitespace marker)"


def reg_15_empty_fix_no_false_ok():
    k, _, span = _ticket_with_tier("AC")
    if not k:
        return None, "no ticket with an AC span"
    html = _cite(k, "AC", span)
    saved = demo._FIX
    try:
        demo._FIX = {"module": "x", "tickets": {}, "epics": {}}
        v = demo.validate_citations(html)
    finally:
        demo._FIX = saved
    ok = v["ok"] == 0  # quote resolves against an empty/missing field → never a false ok
    return ok, f"ok_with_empty_FIX={v['ok']} (must be 0)"


CHECKS = [
    ("REG-01 enforce relabels tier-lie", reg_01_enforce_relabels_tier_lie),
    ("REG-02 verbatim AC = ok", reg_02_verbatim_ac_is_ok),
    ("REG-03 paraphrase = not_found", reg_03_paraphrase_is_not_found),
    ("REG-04 assemble valid + invalid id", reg_04_assemble_valid_and_invalid_ids),
    ("REG-05 enforce leaves correct untouched", reg_05_enforce_leaves_correct_untouched),
    ("REG-06 enforce no-fabricate not_found", reg_06_enforce_no_fabricate_for_not_found),
    ("REG-07 registry tier-binding", reg_07_registry_tier_binding),
    ("REG-08 format constants", reg_08_format_constants),
    ("REG-09 format spec/budget keys", reg_09_format_spec_budget_keys),
    ("REG-10 transcript counted separately", reg_10_transcript_counted_separately),
    ("REG-11 assemble appends Sources", reg_11_assemble_appends_sources),
    ("REG-12 empty field -> 0 spans", reg_12_empty_field_no_spans),
    ("REG-13 _words excludes comments/tags", reg_13_words_excludes_comments_and_tags),
    ("REG-14 assemble tolerates whitespace", reg_14_assemble_tolerates_whitespace_marker),
    ("REG-15 empty _FIX -> no false ok", reg_15_empty_fix_no_false_ok),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--module", default="Item Management")
    args = ap.parse_args()

    demo._FIX = demo._load_fixture(args.module)
    print(f"Regression suite — module '{args.module}' "
          f"({len(demo._FIX['tickets'])} tickets) — deterministic, no SDK\n")

    passed = failed = skipped = 0
    for name, fn in CHECKS:
        try:
            ok, detail = fn()
        except Exception as e:
            ok, detail = False, f"EXCEPTION: {e}"
        if ok is None:
            mark, _s = "SKIP", skipped
            skipped += 1
        elif ok:
            mark = "PASS"
            passed += 1
        else:
            mark = "FAIL"
            failed += 1
        print(f"  [{mark}] {name:<42} {detail}")

    print(f"\n{passed} passed, {failed} failed, {skipped} skipped of {len(CHECKS)}")
    if failed:
        print("REGRESSION FAILURE — the grounding pipeline changed behavior.")
        return 1
    print("All regressions green.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
