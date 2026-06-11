"""eval/quiz_qa_agent.py — QA & drift monitor for the Quiz Builder.

The builder's APPROVE gate prevents an ungrounded/drifted quiz from going live in the
first place. This agent is the MONITOR that runs after the fact: it sweeps every saved
quiz and, for each, re-derives the live source and re-checks it — so a quiz that was
approved yesterday but whose source guide was edited/regenerated today is caught.

Two layers, mirroring the rest of the eval suite:
  1. Deterministic (hard fact) — calls GET /api/quizzes/{id}/qa, which re-grounds every
     question against the CURRENT source, detects DRIFT (source_content_hash mismatch), and
     ENFORCES policy server-side: an approved quiz that drifted or lost grounding is dropped
     back to `draft` (stale). So running this sweep doesn't just observe drift — it prevents
     drifted quizzes from staying live.
  2. Semantic (advisory, uncalibrated) — with --check, calls POST /api/quizzes/{id}/check,
     which runs the question-bank support judge on every grounded question (does the cited
     quote actually support the keyed answer?). Catches wrong-key the verbatim gate can't.

Prereq: the demo server running (`python demo_app.py`, port 8001).

Run:
  python -m eval.quiz_qa_agent                 # deterministic drift + grounding sweep
  python -m eval.quiz_qa_agent --check         # + LLM support-faithfulness pass (live calls)
  python -m eval.quiz_qa_agent --server http://127.0.0.1:8001 --out docs/QUIZ-QA-REPORT.md
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

DEFAULT_SERVER = "http://127.0.0.1:8001"
DOCS = ROOT / "docs"


def _get(server: str, path: str, timeout: float = 30.0):
    with urllib.request.urlopen(f"{server.rstrip('/')}{path}", timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _post(server: str, path: str, body: dict | None = None, timeout: float = 240.0):
    data = json.dumps(body or {}).encode("utf-8")
    req = urllib.request.Request(f"{server.rstrip('/')}{path}", data=data, method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def sweep(server: str, run_check: bool) -> dict:
    listing = _get(server, "/api/quizzes").get("quizzes", [])
    rows = []
    for item in listing:
        qid = item.get("id")
        if not qid:
            continue
        try:
            qa = _get(server, f"/api/quizzes/{qid}/qa")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError, ValueError) as e:
            rows.append({"id": qid, "title": item.get("title"), "error": str(e)})
            print(f"  {qid}: QA fetch FAILED — {e}", flush=True)
            continue
        rep = qa.get("qa", {})
        row = {
            "id": qid, "title": item.get("title"), "status": qa.get("status"),
            "total": rep.get("total"), "grounded": rep.get("grounded"),
            "manual_unverified": rep.get("manual_unverified"),
            "drifted": rep.get("drifted"), "reopened": qa.get("reopened"),
            "stale": qa.get("stale"), "blocking": rep.get("blocking", []),
            "warnings": rep.get("warnings", []), "flagged": [],
        }
        tags = []
        if row["drifted"]:
            tags.append("DRIFTED")
        if row["reopened"]:
            tags.append("REOPENED→draft")
        if row["blocking"]:
            tags.append(f"{len(row['blocking'])} blocking")
        print(f"  {qid}: {row['status']} · {row['grounded']}/{row['total']} grounded"
              f"{(' · ' + ', '.join(tags)) if tags else ' · clean'}", flush=True)
        if run_check:
            try:
                chk = _post(server, f"/api/quizzes/{qid}/check")
                row["flagged"] = chk.get("flagged", [])
                if row["flagged"]:
                    print(f"      support-judge flagged {len(row['flagged'])} question(s)", flush=True)
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError, ValueError) as e:
                row["check_error"] = str(e)
        rows.append(row)

    done = [r for r in rows if "error" not in r]
    return {
        "run_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "server": server, "checked_faithfulness": run_check,
        "quizzes": len(rows),
        "drifted": sum(1 for r in done if r.get("drifted")),
        "reopened": sum(1 for r in done if r.get("reopened")),
        "with_blocking": sum(1 for r in done if r.get("blocking")),
        "support_flagged": sum(len(r.get("flagged", [])) for r in done),
        "rows": rows,
    }


def _md(s: dict) -> str:
    L = ["# Quiz QA & Drift Report\n",
         f"*Auto-generated {s['run_date']} · {s['quizzes']} quiz(zes) swept via the live QA gate. "
         "Deterministic grounding/drift is hard fact; the support-judge column (if run) is the "
         "uncalibrated judge's opinion — spot-check before quoting.*\n",
         "## Headline\n",
         f"- Quizzes scanned: **{s['quizzes']}**",
         f"- **Drifted (source changed under the quiz): {s['drifted']}**"
         f"  ·  auto-reopened to draft: **{s['reopened']}**",
         f"- Quizzes with blocking QA issues: **{s['with_blocking']}**"]
    if s["checked_faithfulness"]:
        L.append(f"- Support-judge flagged questions (wrong-key risk): **{s['support_flagged']}**")
    else:
        L.append("- Support-faithfulness pass: *not run* (pass `--check` to include it).")
    L.append("\n## Per-quiz\n")
    L.append("| Quiz | Status | Grounded | Manual⚠ | Drift | Notes |")
    L.append("|---|---|---:|---:|:--:|---|")
    for r in s["rows"]:
        if "error" in r:
            L.append(f"| {r['id']} | — | — | — | — | ⚠ fetch error: {r['error']} |")
            continue
        notes = []
        if r.get("reopened"):
            notes.append("reopened→draft")
        for b in r.get("blocking", []):
            notes.append(b)
        for f in r.get("flagged", []):
            notes.append(f"wrong-key? Q{f['index'] + 1}: {f['reason'][:60]}")
        drift = "⚠" if r.get("drifted") else "·"
        L.append(f"| {r.get('title') or r['id']} | {r.get('status')} | "
                 f"{r.get('grounded')}/{r.get('total')} | {r.get('manual_unverified')} | {drift} | "
                 f"{'; '.join(notes) if notes else 'clean'} |")
    L.append("")
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(description="QA & drift monitor for saved quizzes.")
    ap.add_argument("--server", default=DEFAULT_SERVER)
    ap.add_argument("--check", action="store_true", help="also run the LLM support-faithfulness pass (live)")
    ap.add_argument("--out", help="markdown report path (default docs/QUIZ-QA-REPORT.md)")
    args = ap.parse_args()

    print(f"Quiz QA & drift sweep — {args.server}", flush=True)
    try:
        summary = sweep(args.server, args.check)
    except (urllib.error.URLError, OSError) as e:
        print(f"Could not reach the server ({e}). Is `python demo_app.py` running on 8001?", file=sys.stderr)
        return 2

    out_md = Path(args.out) if args.out else DOCS / "QUIZ-QA-REPORT.md"
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(_md(summary), encoding="utf-8")
    out_md.with_suffix(".json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n── DONE ── {summary['quizzes']} quiz(zes) · drifted {summary['drifted']} "
          f"· reopened {summary['reopened']} · blocking {summary['with_blocking']}"
          + (f" · support-flagged {summary['support_flagged']}" if args.check else ""))
    print(f"Report: {out_md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
