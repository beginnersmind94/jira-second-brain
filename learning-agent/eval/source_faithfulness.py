"""eval/source_faithfulness.py — SOURCE-FAITHFULNESS grader (a generated guide's CLAIM vs its CITED span).

Catches the seam the verbatim gate AND the quiz<->guide gate both MISS: a generated guide can
cite a real, VERBATIM source span and still have its PROSE CLAIM over-reach / reframe / number-drift
BEYOND what the span actually says. Caught for real in the 2026-06-08 Inventory Distribution run:
the guide rephrased Justin's order-DATE contract rule into "...started before the seasonal contract
was created..." — quote verbatim, claim drifted. "groundedness != source-faithfulness."

This does NOT add a new judge. It REUSES the semantic support judge (qbank_gate.llm_support_judge):
it is the EXTRACT-a-guide's-(claim, cited-span)-pairs + RUN-the-judge layer, with a guide-level gate.
It composes with eval/judge_eval.py (which CALIBRATES that judge on the gold set) and eval/scoring.py
(which AGGREGATES judge verdicts). Independent single-dimension gate (do-not-merge).

Convention: positive/dangerous class = `over_reach`. FN = an over_reach claim the judge calls
`faithful` (a drifted claim SHIPS) — the gated direction. FP = a faithful claim flagged over_reach
(reviewer friction) — tracked only.

Run:
  python -m eval.source_faithfulness                 # OFFLINE self-test (stdlib, no SDK): oracle + degenerate baselines
  python -m eval.source_faithfulness --live          # score the REAL judge vs SME labels (needs Claude auth)
  python -m eval.source_faithfulness --guide <draft.html|rid>   # extract a real guide's claim/cite pairs and judge them
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

FIXTURE = Path(__file__).resolve().parent.parent / "data" / "qbank" / "faithfulness_fixture.jsonl"
DRAFTS = Path(__file__).resolve().parent.parent / "drafts"
PUBLISHED = Path(__file__).resolve().parent.parent / "published"
LABELS = ("faithful", "over_reach")


def load_rows(path: Path = FIXTURE):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        if "_comment" in obj:
            continue
        assert obj.get("gold") in LABELS, f"bad gold label: {obj.get('gold')!r}"
        assert obj.get("claim") and obj.get("cited_quote"), "row needs claim + cited_quote"
        rows.append(obj)
    assert rows, "fixture is empty"
    return rows


def score(rows, predict):
    """predict(row) -> 'faithful' | 'over_reach'. over_reach is the positive (dangerous) class."""
    over = [r for r in rows if r["gold"] == "over_reach"]
    faith = [r for r in rows if r["gold"] == "faithful"]
    fn = sum(1 for r in over if predict(r) == "faithful")   # drift judged faithful -> SHIPS (dangerous)
    fp = sum(1 for r in faith if predict(r) == "over_reach")  # faithful flagged -> friction
    return {"n": len(rows), "n_over": len(over), "n_faithful": len(faith), "fn": fn, "fp": fp,
            "fn_rate": (fn / len(over)) if over else float("nan"),
            "fp_rate": (fp / len(faith)) if faith else float("nan")}


def print_report(title, m):
    print(f"\n── {title} ──")
    print(f"  rows={m['n']}  (over_reach={m['n_over']}, faithful={m['n_faithful']})")
    print(f"  FN (over-reach claim judged FAITHFUL · DANGEROUS · gated): {m['fn_rate']*100:.1f}%  [{m['fn']}/{m['n_over']}]")
    print(f"  FP (faithful claim flagged over-reach · friction · tracked): {m['fp_rate']*100:.1f}%  [{m['fp']}/{m['n_faithful']}]")


def _judge_predict(rows):
    """--live only: use the REAL semantic support judge. over_reach iff the judge says the cited
    span does NOT support the claim. Imports the SDK lazily so the offline path stays stdlib."""
    import asyncio
    import qbank_gate  # imports claude_agent_sdk lazily inside llm_support_judge

    STEM = "Is this guide statement fully supported by the cited source span (no over-reach, no added specificity)?"

    async def run():
        out = {}
        for r in rows:
            try:
                res = await qbank_gate.llm_support_judge(r["cited_quote"], STEM, r["claim"])
                out[id(r)] = "faithful" if res.get("ok") else "over_reach"
            except Exception as e:  # a judge error is the safe (flag) direction, never silent-pass
                out[id(r)] = "over_reach"
                r["_judge_error"] = str(e)
        return out

    verdicts = asyncio.run(run())
    return lambda r: verdicts[id(r)]


def extract_pairs(guide_ref: str):
    """Extract (claim, cited_quote) pairs from a generated guide. `guide_ref` is a path to a
    draft/published HTML, or a resource id resolved under drafts/ then published/."""
    p = Path(guide_ref)
    if not p.exists():
        for cand in (DRAFTS / f"{guide_ref}.html", PUBLISHED / f"{guide_ref}.html"):
            if cand.exists():
                p = cand
                break
    if not p.exists():
        raise SystemExit(f"guide not found: {guide_ref}")
    html = p.read_text(encoding="utf-8")
    pairs = []
    for m in re.finditer(r'<!--\s*Source:\s*([^"“]*?)["“](.+?)["”]\s*-->', html, re.S):
        ref = m.group(1).strip().rstrip(":").strip()
        quote = m.group(2).strip()
        pre = re.sub(r"<[^>]+>", " ", html[:m.start()])
        pre = re.sub(r"\s+", " ", pre).strip()
        claim = pre[-240:]  # the prose the citation backs (heuristic: trailing window)
        pairs.append({"claim": claim, "cited_quote": quote, "ref": ref, "gold": None, "source": str(p.name)})
    return pairs


def main() -> int:
    ap = argparse.ArgumentParser(description="Source-faithfulness gate: a guide's claim vs its cited span.")
    ap.add_argument("--live", action="store_true", help="score the REAL support judge vs SME labels (needs Claude auth)")
    ap.add_argument("--fn-gate", type=float, default=0.0, help="max allowed FN rate before exit 1 (--live)")
    ap.add_argument("--guide", help="extract a real guide's (claim, cited-span) pairs and judge them (implies live)")
    args = ap.parse_args()

    if args.guide:
        pairs = extract_pairs(args.guide)
        print(f"extracted {len(pairs)} (claim, cited-span) pair(s) from {args.guide}")
        if not pairs:
            print("no <!-- Source: ... \"quote\" --> citations found (generator may not be grounding, or wrong view)")
            return 0
        pred = _judge_predict(pairs)
        flagged = [p for p in pairs if pred(p) == "over_reach"]
        print(f"OVER-REACH flagged: {len(flagged)}/{len(pairs)} claim(s) the cited span does not fully support")
        for p in flagged:
            print(f"  ⚠ CLAIM : {p['claim'][:110]}")
            print(f"    CITES : ({p['ref']}) {p['cited_quote'][:110]}")
        return 1 if flagged else 0

    rows = load_rows()
    if args.live:
        m = score(rows, _judge_predict(rows))
        print_report("LIVE judge vs SME faithfulness labels", m)
        errs = [r for r in rows if r.get("_judge_error")]
        if errs:
            print(f"  ({len(errs)} judge error(s) counted as over_reach — safe direction)")
        return 1 if (m["fn_rate"] == m["fn_rate"] and m["fn_rate"] > args.fn_gate) else 0

    # OFFLINE self-test (stdlib, NO SDK): oracle + two degenerate baselines.
    oracle = score(rows, lambda r: r["gold"])
    print_report("ORACLE (pred = gold)", oracle)
    assert oracle["fn"] == 0 and oracle["fp"] == 0, "oracle must be perfect"
    allf = score(rows, lambda r: "faithful")
    print_report("BASELINE always-'faithful' (rubber stamp — ships every drift)", allf)
    assert allf["fn_rate"] == 1.0 and allf["fp"] == 0, "always-faithful must miss every over_reach"
    allo = score(rows, lambda r: "over_reach")
    print_report("BASELINE always-'over_reach' (reject all)", allo)
    assert allo["fn"] == 0 and allo["fp_rate"] == 1.0, "always-over_reach must flag every faithful claim"
    print("\nOFFLINE OK — faithfulness fixture well-formed; scorer correct "
          "(FN = a drifted claim shipped = the gated direction). Includes the real Q4 drift as a regression row.")
    print("Run `--live` to score the real judge; `--guide <draft.html|rid>` to trace an actual generated guide.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
