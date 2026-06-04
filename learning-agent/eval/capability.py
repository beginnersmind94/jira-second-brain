"""Capability eval harness for the Learning Content Producer.

Runs the cell-D pipeline across formats x trials, grades each trial with the
deterministic graders (the publish authority), aggregates pass@k / pass^k /
pass_rate / mean partial-credit / per-grader rollup, also runs the deterministic
regression CHECKS, and persists a full log under eval/runs/<utc-stamp>/.

  python -m eval.capability --formats long-form,micro-guide,tldr --trials 1

Writes:
  eval/runs/<stamp>/report.json   full machine-readable log
  eval/runs/<stamp>/report.md     human table
  eval/runs/<stamp>/<fmt>-trialN.html   each generated guide
"""
import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from statistics import mean

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import demo
import demo_d

from eval.pipeline import run_pipeline
from eval.graders import grade_all, GRADERS
from eval.regression import CHECKS as REGRESSION_CHECKS

_RUNS_DIR = Path(__file__).resolve().parent / "runs"


def _parse_formats(raw: str) -> list[str]:
    fmts = [f.strip() for f in raw.split(",") if f.strip()]
    bad = [f for f in fmts if f not in demo_d.VALID_FORMATS]
    if bad:
        raise SystemExit(f"Unknown format(s): {bad}. Valid: {demo_d.VALID_FORMATS}")
    return fmts


def _run_regressions() -> list[dict]:
    """Run the deterministic regression CHECKS (no SDK). Returns per-check results."""
    out = []
    for name, fn in REGRESSION_CHECKS:
        try:
            ok, detail = fn()
        except Exception as e:  # noqa: BLE001
            ok, detail = False, f"EXCEPTION: {e}"
        status = "SKIP" if ok is None else ("PASS" if ok else "FAIL")
        out.append({"name": name, "status": status, "detail": detail})
    return out


def _aggregate(fmt_trials: list[dict]) -> dict:
    """Aggregate the per-trial grade results for one format."""
    n = len(fmt_trials)
    passed_flags = [t["grade"]["trial_passed"] for t in fmt_trials]
    partials = [t["grade"]["partial_credit"] for t in fmt_trials]

    # per-grader rollup: how many trials each grader passed + mean score.
    per_grader: dict[str, dict] = {}
    for g in GRADERS:
        gname = g.__name__
        scores, passes = [], 0
        for t in fmt_trials:
            gr = next((x for x in t["grade"]["graders"] if x["name"] == gname), None)
            if gr is not None:
                scores.append(gr["score"])
                passes += int(gr["passed"])
        per_grader[gname] = {
            "passed_trials": passes, "trials": n,
            "mean_score": float(mean(scores)) if scores else 0.0,
        }

    costs = [(t.get("metrics", {}).get("cost") or {}).get("cost_usd", 0) or 0 for t in fmt_trials]
    return {
        "trials": n,
        "pass_at_k": any(passed_flags),         # >=1 trial fully passed
        "pass_caret_k": all(passed_flags) if n else False,  # all trials passed
        "pass_rate": (sum(passed_flags) / n) if n else 0.0,
        "mean_partial_credit": float(mean(partials)) if partials else 0.0,
        "total_cost_usd": round(float(sum(costs)), 4),
        "mean_cost_usd": round(float(mean(costs)), 4) if costs else 0.0,
        "per_grader": per_grader,
    }


def _write_md(path: Path, stamp: str, module: str, transcript: str,
              per_fmt: dict, regressions: list[dict]) -> None:
    lines = []
    lines.append(f"# Capability Eval — {stamp}")
    lines.append("")
    lines.append(f"- Module: `{module}`")
    lines.append(f"- Transcript: `{transcript}`")
    lines.append("")
    lines.append("## Per-format summary")
    lines.append("")
    lines.append("| Format | Trials | pass@k | pass^k | pass_rate | mean partial | cost (USD) |")
    lines.append("|---|---|---|---|---|---|---|")
    grand = 0.0
    for fmt, agg in per_fmt.items():
        a = agg["aggregate"]
        grand += a.get("total_cost_usd", 0.0)
        lines.append(
            f"| {fmt} | {a['trials']} | {a['pass_at_k']} | {a['pass_caret_k']} | "
            f"{a['pass_rate']:.2f} | {a['mean_partial_credit']:.3f} | ${a.get('total_cost_usd', 0):.4f} |"
        )
    lines.append(f"| **TOTAL** | | | | | | **${grand:.4f}** |")
    lines.append("")
    lines.append("## Per-grader rollup")
    lines.append("")
    for fmt, agg in per_fmt.items():
        lines.append(f"### {fmt}")
        lines.append("")
        lines.append("| Grader | Passed/Trials | Mean score |")
        lines.append("|---|---|---|")
        for gname, gr in agg["aggregate"]["per_grader"].items():
            lines.append(f"| {gname} | {gr['passed_trials']}/{gr['trials']} | {gr['mean_score']:.3f} |")
        lines.append("")
    lines.append("## Regression checks (deterministic, no SDK)")
    lines.append("")
    rp = sum(1 for r in regressions if r["status"] == "PASS")
    rf = sum(1 for r in regressions if r["status"] == "FAIL")
    rs = sum(1 for r in regressions if r["status"] == "SKIP")
    lines.append(f"{rp} passed, {rf} failed, {rs} skipped of {len(regressions)}")
    lines.append("")
    lines.append("| Check | Status | Detail |")
    lines.append("|---|---|---|")
    for r in regressions:
        detail = r["detail"].replace("|", "\\|")
        lines.append(f"| {r['name']} | {r['status']} | {detail} |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


async def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--formats", default="long-form,micro-guide,tldr")
    ap.add_argument("--trials", type=int, default=3)  # >=3 for a real pass^k publish-gate reading
    ap.add_argument("--module", default=demo_d.DEFAULT_MODULE)
    ap.add_argument("--transcript", default=demo.DEFAULT_TRANSCRIPT)
    args = ap.parse_args()

    formats = _parse_formats(args.formats)

    # Load the fixture ONCE — graders + registry read demo._FIX as ground truth.
    demo._FIX = demo._load_fixture(args.module)
    print(f"Capability eval — module '{demo._FIX['module']}' "
          f"({len(demo._FIX['tickets'])} tickets + {len(demo._FIX['epics'])} epics)")
    print(f"formats={formats} trials={args.trials}\n")

    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    run_dir = _RUNS_DIR / stamp
    run_dir.mkdir(parents=True, exist_ok=True)

    per_fmt: dict[str, dict] = {}
    for fmt in formats:
        trials = []
        for trial in range(1, args.trials + 1):
            print(f"[{fmt}] trial {trial}/{args.trials} — running pipeline…")
            art = await run_pipeline(args.module, args.transcript, fmt)
            grade = grade_all(art, fmt)

            # Persist the generated guide html.
            html_path = run_dir / f"{fmt}-trial{trial}.html"
            html_path.write_text(art["html"], encoding="utf-8")

            print(f"  trial_passed={grade['trial_passed']} "
                  f"partial={grade['partial_credit']:.3f} "
                  f"words={art['words']} secs={art['total_secs']:.0f}")
            for gr in grade["graders"]:
                print(f"    [{'PASS' if gr['passed'] else 'FAIL'}] "
                      f"{gr['name']:<16} {gr['metric']:<7} {gr['detail']}")

            trials.append({
                "trial": trial,
                "fmt": fmt,
                "grade": grade,
                "metrics": {
                    "words": art["words"], "plan_secs": art["plan_secs"],
                    "sec_secs": art["sec_secs"], "total_secs": art["total_secs"],
                    "integ": art["integ"], "asm": {k: v for k, v in art["asm"].items()
                                                   if k != "issues"},
                    "n_sections": len(art["sections"]),
                    "cost": art.get("cost"),
                },
                "html_file": html_path.name,
            })
        per_fmt[fmt] = {"trials": trials, "aggregate": _aggregate(trials)}

    # Deterministic regression checks.
    print("\nRunning deterministic regression checks…")
    regressions = _run_regressions()
    rp = sum(1 for r in regressions if r["status"] == "PASS")
    rf = sum(1 for r in regressions if r["status"] == "FAIL")
    rs = sum(1 for r in regressions if r["status"] == "SKIP")
    print(f"  regressions: {rp} passed, {rf} failed, {rs} skipped of {len(regressions)}")

    total_cost = round(sum(agg["aggregate"].get("total_cost_usd", 0.0)
                           for agg in per_fmt.values()), 4)
    report = {
        "stamp": stamp,
        "module": demo._FIX["module"],
        "transcript": args.transcript,
        "formats": formats,
        "trials": args.trials,
        "per_format": per_fmt,
        "total_cost_usd": total_cost,
        "regressions": regressions,
        "regression_summary": {"passed": rp, "failed": rf, "skipped": rs,
                               "total": len(regressions)},
    }
    json_path = run_dir / "report.json"
    json_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    md_path = run_dir / "report.md"
    _write_md(md_path, stamp, demo._FIX["module"], args.transcript, per_fmt, regressions)

    print("\n=== CONSOLE SUMMARY ===")
    for fmt, agg in per_fmt.items():
        a = agg["aggregate"]
        print(f"  {fmt:<12} pass@k={a['pass_at_k']!s:<5} pass^k={a['pass_caret_k']!s:<5} "
              f"pass_rate={a['pass_rate']:.2f} mean_partial={a['mean_partial_credit']:.3f} "
              f"cost=${a.get('total_cost_usd', 0):.4f}")
    print(f"  regressions: {rp}/{len(regressions)} passed "
          f"({rf} failed, {rs} skipped)")
    print(f"  TOTAL RUN COST: ${total_cost:.4f}")
    print(f"\nLog written to: {run_dir}")
    print(f"  {json_path.name}  {md_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
