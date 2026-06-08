"""Source-quality grader — a claim can be grounded yet grounded in the WRONG shelf.

Implements the wiki's single-dimension source-quality grader (EVAL-WIKI.md
in-body §11.2 / TOC §13.2; gate row in §11.3; checklist case in §12.2). It is one
of the §8.5 / §4.5.6 "beyond groundedness" dimensions: groundedness asks *did the
AI invent anything*; source-quality asks *did it cite the most authoritative source
it had*. Per the §8 / §11.3 "do not merge" rule this is a SEPARATE single-dimension
grader — it does NOT touch the §10 should-FAIL (FNR) scorer (eval/judge_eval.py) and
must not be folded into it.

What it does (adapted from the wiki's §11.2 pandas reference to pure stdlib):
  • Map each cited source's `source_type` to an authority tier:
        usda_primary 5 > state_cn 4 > vendor_docs 3 > cybersoft_sop 2
        > freshdesk 1 > vendor_blog 0
  • Per-claim average authority, then per-guide average across its claims (0–5).
  • Negative class (§4.5.6): a low-authority citation chosen when a HIGHER-authority
    source existed for the SAME claim (`higher_available=true`) → the claim is FLAGGED.
  • Gate (§6 stricter default): a guide stays in DRAFT if it has ANY flagged claim
    OR its average authority is below MIN_AUTHORITY. MIN_AUTHORITY and the tier
    integers are SME-OWNED starting values (§11.2.1) — start strict, relax on
    calibration evidence; they are not fixed policy.
  • Unmapped `source_type` → WARN + EXCLUDE (NOT silently scored 0, §11.2.1), so a
    missing tier entry cannot quietly deflate a guide's authority score.

This is a deterministic grader (§9.3 "authority tier scoring = table lookup +
average" belongs in code, not an agent). There is no LLM judge here and no `--live`
model path — both `higher_available` (from the upstream retrieval-audit step) and
`source_type` are INPUTS to this layer (§4: the audit is an input, the grader scores
it). `--live` is accepted only as a no-op alias so the runner CLI matches its
siblings; the scoring is identical with or without it.

Usage:
    python -m eval.source_quality          # OFFLINE: validate fixture + grader via
                                            #   an ORACLE (known-correct authority math
                                            #   + gate decisions) and degenerate
                                            #   baselines (stdlib only — NO SDK/auth)
    python -m eval.source_quality --live    # same scoring (no model path exists);
                                            #   exit non-zero if any guide is DRAFT
    python -m eval.source_quality --min-authority 2.0   # tune the SME-owned floor

Dataset: data/qbank/source_fixture.jsonl  (SYNTHETIC, `source` tags every row).
Rows: {guide_id, claim_id, source_type, higher_available}.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FIXTURE_PATH = (Path(__file__).resolve().parent.parent
                / "data" / "qbank" / "source_fixture.jsonl")

# ── Authority tiers (§11.2 / §4.5.6). Higher = more authoritative. SME-owned map.
# USDA primary > state CN office > vendor docs > Cybersoft SOP > Freshdesk > blog.
AUTHORITY_TIER = {
    "usda_primary":  5,
    "state_cn":      4,
    "vendor_docs":   3,   # Oracle, Tyler
    "cybersoft_sop": 2,
    "freshdesk":     1,   # historical tickets
    "vendor_blog":   0,   # blogs, forums, Stack Overflow, informal notes
}

# §6 stricter default: average authority must clear this for a guide to PUBLISH.
# SME-tunable (§11.2.1), overridable via --min-authority; not fixed policy.
MIN_AUTHORITY = 3.0   # ≥ vendor_docs average


# ── data ──────────────────────────────────────────────────────────────────────
def load_rows(path: Path = FIXTURE_PATH) -> list[dict]:
    """Load + validate the source fixture. One row per cited source backing a claim.

    Skips the leading `{"_comment": ...}` synthetic-label record. Asserts each
    scored row carries the §11.2 schema (guide_id, claim_id, source_type,
    higher_available). `source_type` is NOT asserted to be mapped here — an
    unmapped type is a real, handled case (WARN + exclude, §11.2.1).
    """
    assert path.exists(), f"source fixture not found: {path}"
    rows: list[dict] = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        if "_comment" in r:        # synthetic-label header record
            continue
        rid = f"{r.get('guide_id', '?')}/{r.get('claim_id', f'line{i}')}"
        for field in ("guide_id", "claim_id", "source_type"):
            assert r.get(field), f"{rid}: missing/empty required field {field!r}"
        assert isinstance(r.get("higher_available"), bool), \
            f"{rid}: higher_available must be a bool, got {r.get('higher_available')!r}"
        rows.append(r)
    assert rows, "source fixture is empty"
    return rows


# ── scoring ─────────────────────────────────────────────────────────────────
def grade(rows: list[dict], min_authority: float = MIN_AUTHORITY) -> dict:
    """Score cited sources by authority and flag low-authority-when-better-existed.

    Pure stdlib re-implementation of the wiki §11.2 pandas grader:
      tier            = AUTHORITY_TIER[source_type]   (unmapped → WARN + EXCLUDE)
      per-claim       = mean tier over that claim's cited sources
      per-guide score = mean per-claim authority across the guide's claims
      flagged claim   = any cited source with higher_available=true (§4.5.6)
      gate            = DRAFT if any flagged claim OR avg authority < min_authority
                        (§6 stricter default), else PUBLISH

    Returns per-guide grades + the corpus-level dashboard numbers (§11.2, §12.3).
    Unmapped rows are returned separately so the caller can WARN (not score 0).
    """
    # Split mapped vs unmapped; unmapped is WARNed + EXCLUDED (§11.2.1), never 0.
    mapped, unmapped = [], []
    for r in rows:
        (mapped if r["source_type"] in AUTHORITY_TIER else unmapped).append(r)

    # Group mapped rows by guide → claim → list of tiers (+ any flag on the claim).
    guides: dict[str, dict[str, dict]] = {}
    for r in mapped:
        g = guides.setdefault(r["guide_id"], {})
        c = g.setdefault(r["claim_id"], {"tiers": [], "flagged": False})
        c["tiers"].append(AUTHORITY_TIER[r["source_type"]])
        if r["higher_available"]:
            c["flagged"] = True

    per_guide: dict[str, dict] = {}
    for gid, claims in guides.items():
        claim_avgs, flagged_ids = [], []
        for cid, c in claims.items():
            claim_avgs.append(sum(c["tiers"]) / len(c["tiers"]))   # per-claim avg
            if c["flagged"]:
                flagged_ids.append(cid)
        authority_score = sum(claim_avgs) / len(claim_avgs)        # per-guide avg
        # §6 stricter default: any flagged claim OR below the floor → DRAFT.
        below_floor = authority_score < min_authority
        gate = "PUBLISH" if (not flagged_ids and not below_floor) else "DRAFT"
        reasons = []
        if flagged_ids:
            reasons.append(f"flagged low-authority claim(s): {', '.join(sorted(flagged_ids))}")
        if below_floor:
            reasons.append(f"avg authority {authority_score:.2f} < MIN_AUTHORITY {min_authority:.2f}")
        per_guide[gid] = {
            "authority_score": round(authority_score, 4),
            "claims": len(claims),
            "flagged_claims": len(flagged_ids),
            "flagged_claim_ids": sorted(flagged_ids),
            "gate": gate,
            "draft_reasons": reasons,
        }

    # Corpus dashboard line (§11.2, §12.3): 0–5 average across all mapped sources.
    all_tiers = [AUTHORITY_TIER[r["source_type"]] for r in mapped]
    overall_authority = (sum(all_tiers) / len(all_tiers)) if all_tiers else 0.0
    draft = [g for g, v in per_guide.items() if v["gate"] == "DRAFT"]
    return {
        "n_rows": len(rows),
        "n_mapped": len(mapped),
        "n_unmapped": len(unmapped),
        "unmapped_rows": [f"{r['guide_id']}/{r['claim_id']} ({r['source_type']})" for r in unmapped],
        "unmapped_types": sorted({r["source_type"] for r in unmapped}),
        "n_guides": len(per_guide),
        "overall_authority": round(overall_authority, 4),
        "min_authority": min_authority,
        "per_guide": per_guide,
        "draft_guides": draft,
        "publish_guides": [g for g in per_guide if g not in draft],
        "total_flagged_claims": sum(v["flagged_claims"] for v in per_guide.values()),
    }


def print_report(title: str, rep: dict) -> None:
    print(f"\n── {title} ──")
    print(f"  rows={rep['n_rows']}  (mapped={rep['n_mapped']}, unmapped={rep['n_unmapped']})  "
          f"guides={rep['n_guides']}")
    print(f"  Authority score: {rep['overall_authority']:.1f}/5 average across cited sources "
          f"(MIN_AUTHORITY={rep['min_authority']:.1f})")
    print(f"  Flagged claims (lower-authority cited when better source existed): {rep['total_flagged_claims']}")
    if rep["n_unmapped"]:
        print(f"  ⚠ WARNING: {rep['n_unmapped']} citation(s) have an unmapped source_type "
              f"{rep['unmapped_types']} — extend AUTHORITY_TIER (SME-owned, §4.5.6). "
              f"EXCLUDED from scores (not scored 0). Rows: {', '.join(rep['unmapped_rows'])}")
    for gid, v in sorted(rep["per_guide"].items()):
        mark = "DRAFT " if v["gate"] == "DRAFT" else "PUBLISH"
        line = (f"  [{mark}] {gid}: authority={v['authority_score']:.2f}/5  "
                f"claims={v['claims']}  flagged={v['flagged_claims']}")
        if v["draft_reasons"]:
            line += f"  ← {'; '.join(v['draft_reasons'])}"
        print(line)
    if rep["draft_guides"]:
        print(f"  Guides held in DRAFT on source quality: {', '.join(sorted(rep['draft_guides']))}")


# ── predictors / synthetic baselines (offline self-test only) ───────────────────
# This grader has no model path: source_type + higher_available are INPUTS (§4),
# scored deterministically. So the offline self-test proves the SCORER, not a model:
# an ORACLE row-set with hand-computed authority + known gate decisions, plus two
# degenerate inputs that must move the gate in the obvious directions — the same
# oracle + degenerate-baseline discipline the triage/judge/scope evals use.
def oracle_rows() -> list[dict]:
    """A tiny self-contained row-set whose authority math + gates are known by hand.

    g_pub : c1=mean(5,4)=4.5, c2=mean(3)=3.0 → guide avg 3.75, 0 flags → PUBLISH
    g_flag: c1=mean(3)=3.0,  c2=mean(1)=1.0 flagged → 1 flag        → DRAFT
    g_low : c1=mean(2)=2.0,  c2=mean(1)=1.0 → guide avg 1.5 < 3.0   → DRAFT
    g_unmap: c1=mean(5)=5.0, c2=UNMAPPED(excluded) → avg 5.0, 0 flag → PUBLISH
            (proves exclusion ≠ score-0; scoring 0 would wrongly DRAFT it)
    """
    def row(g, c, st, hi=False):
        return {"guide_id": g, "claim_id": c, "source_type": st, "higher_available": hi}
    return [
        row("g_pub",   "c1", "usda_primary"), row("g_pub",   "c1", "state_cn"),
        row("g_pub",   "c2", "vendor_docs"),
        row("g_flag",  "c1", "vendor_docs"),  row("g_flag",  "c2", "freshdesk", hi=True),
        row("g_low",   "c1", "cybersoft_sop"), row("g_low",  "c2", "freshdesk"),
        row("g_unmap", "c1", "usda_primary"), row("g_unmap", "c2", "made_up_blog_type"),
    ]


# ── main ────────────────────────────────────────────────────────────────────────
def main() -> int:
    ap = argparse.ArgumentParser(description="Source-quality grader (wiki §11.2 / §13.2).")
    ap.add_argument("--live", action="store_true",
                    help="no-op alias (this grader has no model path; scoring is "
                         "identical). Accepted so the CLI matches the sibling evals.")
    ap.add_argument("--min-authority", type=float, default=MIN_AUTHORITY,
                    help=f"SME-owned average-authority floor for PUBLISH (default {MIN_AUTHORITY}).")
    args = ap.parse_args()

    if not args.live:
        # OFFLINE: prove the FIXTURE loads + the SCORER is correct, using an oracle
        # with hand-computed authority/gates and degenerate baselines. Stdlib only —
        # no SDK, no auth. These assertions guard the grader itself so a real-data
        # mistake can't hide behind a broken scorer.
        oracle = oracle_rows()
        rep_o = grade(oracle, min_authority=MIN_AUTHORITY)
        print_report("ORACLE (hand-computed authority + known gates; scorer sanity floor)", rep_o)
        pg = rep_o["per_guide"]
        # Authority math is exactly as hand-computed above.
        assert pg["g_pub"]["authority_score"] == 3.75, "g_pub avg must be 3.75 (mean of 4.5, 3.0)"
        assert pg["g_low"]["authority_score"] == 1.5,  "g_low avg must be 1.5 (mean of 2.0, 1.0)"
        assert pg["g_unmap"]["authority_score"] == 5.0, \
            "g_unmap must score 5.0 after EXCLUDING the unmapped row (not 0 — §11.2.1)"
        # §12.2 case: a higher_available=true row → flagged claim → DRAFT.
        assert rep_o["n_unmapped"] == 1 and rep_o["unmapped_types"] == ["made_up_blog_type"], \
            "exactly one unmapped source_type must be detected"
        assert pg["g_flag"]["flagged_claims"] == 1 and pg["g_flag"]["gate"] == "DRAFT", \
            "§12.2: higher_available=true → flagged claim → DRAFT"
        # §12.2 case: unmapped source_type → excluded, and exclusion must NOT sink the guide.
        assert pg["g_unmap"]["gate"] == "PUBLISH", \
            "§12.2: unmapped row EXCLUDED (warned), remaining authority high → PUBLISH"
        # Gates land where the hand math says.
        assert pg["g_pub"]["gate"] == "PUBLISH", "g_pub (3.75, 0 flags) must PUBLISH"
        assert pg["g_low"]["gate"] == "DRAFT", "g_low (1.5 < 3.0) must DRAFT on the floor alone"
        assert pg["g_low"]["flagged_claims"] == 0, "g_low DRAFTs on AVERAGE, not on a flag"
        assert sorted(rep_o["draft_guides"]) == ["g_flag", "g_low"], \
            "exactly g_flag (flag) and g_low (floor) held in DRAFT"

        # Degenerate baseline 1 — every claim flagged (higher_available everywhere):
        # the strict gate must hold EVERY guide in DRAFT (exposes a no-op flag check).
        all_flagged = [{**r, "higher_available": True} for r in oracle]
        rep_f = grade(all_flagged, min_authority=MIN_AUTHORITY)
        print_report("BASELINE all-flagged (every claim higher_available=true)", rep_f)
        assert rep_f["draft_guides"] and not rep_f["publish_guides"], \
            "all-flagged must DRAFT every guide (flag gate must bite)"

        # Degenerate baseline 2 — floor set above the ceiling (5): even a spotless,
        # unflagged corpus must all DRAFT (exposes a no-op floor check).
        rep_hi = grade(oracle, min_authority=5.01)
        print_report("BASELINE floor>5 (MIN_AUTHORITY above the max tier)", rep_hi)
        assert not rep_hi["publish_guides"], \
            "with the floor above tier-5, NOTHING can clear it → all DRAFT"

        # And the mirror: floor at 0 with no flags → the unflagged guides PUBLISH.
        rep_lo = grade([{**r, "higher_available": False} for r in oracle], min_authority=0.0)
        assert set(rep_lo["publish_guides"]) >= {"g_pub", "g_low", "g_unmap"}, \
            "floor 0 + no flags → authority can't block; only flags would"

        # Now actually exercise the shipped synthetic fixture end-to-end.
        rows = load_rows()
        assert all(r.get("source") == "synthetic" for r in rows), \
            "every shipped fixture row must be labeled source=synthetic"
        rep = grade(rows, min_authority=args.min_authority)
        print_report(f"FIXTURE data/qbank/source_fixture.jsonl  (MIN_AUTHORITY={args.min_authority})", rep)
        assert rep["n_unmapped"] >= 1, \
            "fixture must include the §12.2 unmapped-source_type case"
        assert rep["total_flagged_claims"] >= 1, \
            "fixture must include the §12.2 higher_available=true (flagged) case"
        print("\n  NOTE: fixture rows are SYNTHETIC (labeled source=synthetic). Replace with "
              "SME-owned retrieval-audit rows (real source_type + higher_available) before "
              "trusting the authority score on real traffic.")

        print("\nOFFLINE OK — fixture well-formed; grader correct "
              "(authority math, unmapped WARN+exclude, flag/floor gates all verified).")
        print("Run `python -m eval.source_quality --live` for the same scoring "
              "(this grader has no model path — source_type/higher_available are inputs).")
        return 0

    # --live: identical scoring (no model path). Gate on the shipped fixture.
    rows = load_rows()
    rep = grade(rows, min_authority=args.min_authority)
    print_report("source-quality grade (shipped fixture)", rep)
    if rep["draft_guides"]:
        print(f"\nFAIL — {len(rep['draft_guides'])} guide(s) held in DRAFT on source quality "
              f"(flagged low-authority citation, or avg authority below the SME floor): "
              f"{', '.join(sorted(rep['draft_guides']))}.")
        return 1
    print(f"\nPASS — every guide cleared source quality "
          f"(no flagged low-authority citation; avg authority ≥ {args.min_authority:.1f}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
