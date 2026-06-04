"""Deterministic graders for the capability eval (the PUBLISH authority).

Per EVAL-SPEC.md:
  - These graders are deterministic and are the publish authority (LLM graders are
    advisory only and live elsewhere).
  - On the cell_d path, tier_lie and quote_not_found are invariants (0 by
    construction); G1/G2 report them as such.
  - NEVER call demo.enforce_citations in the grade path.
  - partial credit = mean grader score; pass^k for grounding/structure graders,
    pass@k for the capability grader (density).

Each grader has signature (art: dict, fmt: str) -> dict and returns:
  {"name": str, "passed": bool, "score": float in 0..1,
   "metric": "pass^k" | "pass@k", "detail": str}
"""
import math
import re
from statistics import mean


# Section-floor per format — mirrors the inline min_sections in demo_d.run_cell_d.
_MIN_SECTIONS = {"tldr": 5, "micro-guide": 6, "long-form": 8, "release-notes": 2}

# Word ceilings per format (spec: tldr 500 / micro 1500 / long 6000 / release-notes 2000).
_CEILING = {"tldr": 500, "micro-guide": 1500, "long-form": 6000, "release-notes": 2000}


def _count_h2(html: str) -> int:
    return len(re.findall(r"<h2[ >]", html, re.I))


def G1_tier_lie(art: dict, fmt: str) -> dict:
    """Wrong-tier citations. Invariant on cell_d path (0 by construction)."""
    n = art["integ"]["tier_lie"]
    ok = (n == 0)
    return {"name": "G1_tier_lie", "passed": ok, "score": 1.0 if ok else 0.0,
            "metric": "pass^k", "detail": f"tier_lie={n} (invariant: 0 by construction)"}


def G2_not_found(art: dict, fmt: str) -> dict:
    """Quote-not-found citations. Invariant on cell_d path (0 by construction)."""
    n = art["integ"]["quote_not_found"]
    ok = (n == 0)
    return {"name": "G2_not_found", "passed": ok, "score": 1.0 if ok else 0.0,
            "metric": "pass^k", "detail": f"quote_not_found={n} (invariant: 0 by construction)"}


def G3_invalid_id(art: dict, fmt: str) -> dict:
    """No invalid CITE ids: assembler reported zero AND none leaked into the html."""
    n = art["asm"]["invalid_cite_id"]
    leaked = "INVALID_CITE_ID" in art["html"]
    ok = (n == 0) and (not leaked)
    return {"name": "G3_invalid_id", "passed": ok, "score": 1.0 if ok else 0.0,
            "metric": "pass^k", "detail": f"invalid_cite_id={n} leaked_in_html={leaked}"}


def G4_density(art: dict, fmt: str) -> dict:
    """Citation density (the capability grader). pass@k, co-scored with G1/G2.

    Requires:
      - tokened > 0 (something was actually cited)
      - ok / max(tokened, 1) >= 0.9 (almost every tokened citation validates ok)
      - tokened >= ceil(words / 250) (at least one citation per ~250 words)
    """
    integ = art["integ"]
    tokened = integ["tokened"]
    ok_n = integ["ok"]
    words = art["words"]
    need = math.ceil(words / 250) if words else 0
    ok_ratio = ok_n / max(tokened, 1)
    passed = (tokened > 0) and (ok_ratio >= 0.9) and (tokened >= need)
    # Partial credit blends the two sub-targets, clamped to 1.0.
    ratio_score = min(ok_ratio, 1.0)
    coverage_score = min(tokened / need, 1.0) if need else (1.0 if tokened > 0 else 0.0)
    score = 1.0 if passed else min(ratio_score, coverage_score)
    return {"name": "G4_density", "passed": passed, "score": float(score),
            "metric": "pass@k",
            "detail": f"tokened={tokened} ok={ok_n} ok_ratio={ok_ratio:.2f} "
                      f"need>={need} (words={words})"}


def G5_section_fit(art: dict, fmt: str) -> dict:
    """Structure: enough <h2> sections and no failed-section placeholder."""
    n_h2 = _count_h2(art["html"])
    floor = _MIN_SECTIONS.get(fmt, 8)
    placeholder = "[ERROR: section failed" in art["html"]
    present_frac = min(n_h2 / floor, 1.0) if floor else 1.0
    ok = (n_h2 >= floor) and (not placeholder)
    score = present_frac if not placeholder else 0.0
    return {"name": "G5_section_fit", "passed": ok, "score": float(score),
            "metric": "pass^k",
            "detail": f"h2={n_h2} need>={floor} placeholder={placeholder}"}


def G6_length(art: dict, fmt: str) -> dict:
    """No section truncated (stop_reason == max_tokens) AND total words <= ceiling."""
    truncated = [s["title"] for s in art["sections"] if s.get("stop_reason") == "max_tokens"]
    ceiling = _CEILING.get(fmt, 6000)
    within = art["words"] <= ceiling
    ok = (len(truncated) == 0) and within
    return {"name": "G6_length", "passed": ok, "score": 1.0 if ok else 0.0,
            "metric": "pass^k",
            "detail": f"truncated={len(truncated)} words={art['words']} ceiling={ceiling}"}


GRADERS = [G1_tier_lie, G2_not_found, G3_invalid_id, G4_density, G5_section_fit, G6_length]


def grade_all(art: dict, fmt: str) -> dict:
    """Run all graders. trial_passed = all REQUIRED graders pass.

    Required = the pass^k graders (G1, G2, G3, G5, G6) + G4 (the pass@k capability
    grader). partial_credit = mean of all grader scores.
    """
    results = [g(art, fmt) for g in GRADERS]
    # Required = every pass^k grader plus G4 (the capability grader). Here that is
    # the full set, so "all required pass" == all graders pass.
    required = [r for r in results if r["metric"] == "pass^k" or r["name"] == "G4_density"]
    trial_passed = all(r["passed"] for r in required)
    partial = mean(r["score"] for r in results) if results else 0.0
    return {"graders": results, "trial_passed": bool(trial_passed),
            "partial_credit": float(partial)}
