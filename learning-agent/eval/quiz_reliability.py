"""eval/quiz_reliability.py — RELIABILITY sweep for quiz-from-guide generation.

The single quiz endpoint already proves grounding once. This asks the harder question:
is it RELIABLE? Generate the quiz N times on ONE guide and auto-grade EVERY question
two INDEPENDENT ways, so we measure variance instead of eyeballing a single run.

  1. GROUNDING GATE  (deterministic · HARD FACT): the server's own grounding-by-construction
     gate — a question is KEPT only if its source_quote is a verbatim substring of the guide
     text, else DROPPED. We read `kept`/`dropped` straight off the live response; nothing here
     re-judges it. This column is not an opinion.

  2. SUPPORT JUDGE   (semantic · LLM OPINION · UNCALIBRATED): for every KEPT question we ask
     `qbank_gate.llm_support_judge` whether the cited quote, read literally, actually supports
     the KEYED answer. This catches the seam the grounding gate misses — a verbatim quote that
     proves a *different* fact than the keyed option (inversion / wrong-key / number drift) — at
     scale, with no hand-grading. It REUSES the gate's judge; it does NOT add a new one.

A run is FULLY-CLEAN iff `dropped == 0` AND no kept question is key-unsupported.
The headline is `fully-clean runs / N`.

Design choices that matter:
  * Generation goes through the LIVE demo server (`POST /api/resources/{rid}/quiz`) — the exact
    production code path, so the number reflects what the product actually does, not a re-impl.
  * Judging runs IN-PROCESS via `qbank_gate` (asyncio.run gets Windows ProactorEventLoop by
    default, so the SDK judge can spawn its subprocess — same pattern as test_qbank_gate.py).
  * Runs are SEQUENTIAL (one generation at a time — one server, one auth); within a run the
    kept questions are judged in PARALLEL, bounded by a small semaphore.
  * The results JSON is written INCREMENTALLY after every run, so a crash leaves partial
    results on disk instead of nothing. (The prior inline harness died with its session and
    left zero output — this one cannot.)

CAVEAT baked into the report: column 1 is a hard deterministic fact; column 2 is an
uncalibrated judge's opinion. A human should spot-check a sample of the support verdicts
before any number from this doc is shown to a stakeholder.

Prereq: the demo server must be running (`python demo_app.py`, port 8001) and Claude auth
available for the judge.

Run:
  python -m eval.quiz_reliability                         # 10 runs, n=6, the Inventory Distribution draft
  python -m eval.quiz_reliability --runs 10 --n 6
  python -m eval.quiz_reliability --rid <rid> --server http://127.0.0.1:8001
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import qbank_gate  # imports claude_agent_sdk lazily inside llm_support_judge

DEFAULT_RID = "20260608-155920-inventory-long-form-af5d2c"
DEFAULT_SERVER = "http://127.0.0.1:8001"
DOCS = ROOT / "docs"


def _post_quiz(server: str, rid: str, n: int, timeout: float = 240.0) -> dict:
    """POST the live quiz endpoint and return the parsed JSON (one full generation)."""
    url = f"{server.rstrip('/')}/api/resources/{rid}/quiz"
    body = json.dumps({"n": n}).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


async def _judge_one(sem: asyncio.Semaphore, q: dict) -> dict:
    """Support-judge ONE kept question. A judge error -> key-unsupported (the safe direction:
    we never silently pass a question we couldn't grade)."""
    quote = (q.get("source_quote") or "").strip()
    stem = q.get("q") or ""
    opts = q.get("options") or []
    ans_i = q.get("answer")
    keyed = opts[ans_i] if isinstance(ans_i, int) and 0 <= ans_i < len(opts) else None
    rec = {"stem": stem, "keyed_answer": keyed, "cited_quote": quote,
           "excerpt_id": q.get("excerpt_id"), "supported": False, "reason": "", "judge_error": None}
    if keyed is None:
        rec["reason"] = "no resolvable keyed answer (kept question malformed)"
        return rec
    async with sem:
        try:
            verdict = await qbank_gate.llm_support_judge(quote, stem, keyed)
            rec["supported"] = bool(verdict.get("ok"))
            rec["reason"] = verdict.get("reason", "")
        except Exception as e:  # noqa: BLE001 — any judge failure is the flag (never silent pass)
            rec["supported"] = False
            rec["judge_error"] = str(e)
            rec["reason"] = f"judge error (counted unsupported): {e}"
    return rec


async def _run_once(server: str, rid: str, n: int, sem: asyncio.Semaphore, run_idx: int) -> dict:
    """One generation + judge-every-kept-question. Generation failure is non-fatal."""
    out = {"run": run_idx, "generated": None, "kept": None, "dropped": None,
           "gen_error": None, "questions": [], "key_unsupported": 0,
           "grounding_clean": False, "support_clean": False, "fully_clean": False}
    try:
        data = await asyncio.to_thread(_post_quiz, server, rid, n)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError, ValueError) as e:
        out["gen_error"] = str(e)
        print(f"  run {run_idx}: GENERATION FAILED — {e}", flush=True)
        return out

    kept = data.get("questions") or []
    out["generated"] = data.get("generated")
    out["kept"] = data.get("kept", len(kept))
    out["dropped"] = data.get("dropped")
    print(f"  run {run_idx}: generated={out['generated']} kept={out['kept']} "
          f"dropped={out['dropped']} — judging {len(kept)} kept question(s)…", flush=True)

    verdicts = await asyncio.gather(*[_judge_one(sem, q) for q in kept])
    out["questions"] = verdicts
    out["key_unsupported"] = sum(1 for v in verdicts if not v["supported"])
    out["grounding_clean"] = (out["dropped"] == 0)
    out["support_clean"] = (out["key_unsupported"] == 0)
    out["fully_clean"] = out["grounding_clean"] and out["support_clean"]
    flag = "✓ CLEAN" if out["fully_clean"] else "✗ flagged"
    print(f"  run {run_idx}: key-unsupported={out['key_unsupported']} -> {flag}", flush=True)
    return out


def _write_json(json_path: Path, summary: dict) -> None:
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")


def _aggregate(runs: list[dict], meta: dict) -> dict:
    done = [r for r in runs if r.get("gen_error") is None]
    gen_failed = [r for r in runs if r.get("gen_error") is not None]
    total_generated = sum((r["generated"] or 0) for r in done)
    total_kept = sum((r["kept"] or 0) for r in done)
    total_dropped = sum((r["dropped"] or 0) for r in done)
    total_unsupported = sum(r["key_unsupported"] for r in done)
    fully_clean = sum(1 for r in done if r["fully_clean"])
    return {**meta,
            "runs_attempted": len(runs),
            "runs_completed": len(done),
            "runs_generation_failed": len(gen_failed),
            "fully_clean_runs": fully_clean,
            "total_generated": total_generated,
            "total_kept": total_kept,
            "total_dropped": total_dropped,
            "total_key_unsupported": total_unsupported,
            "judge_errors": sum(1 for r in done for q in r["questions"] if q.get("judge_error")),
            "runs": runs}


def _md(summary: dict) -> str:
    s = summary
    L = []
    L.append("# Quiz Generation Reliability — Inventory Distribution Guide\n")
    L.append(f"- **Resource:** `{s['rid']}` (status: {s['status']}, long-form) — \"{s['title']}\"")
    L.append(f"- **Method:** {s['runs_attempted']} runs of quiz-from-guide via the live "
             f"`POST /api/resources/{{rid}}/quiz` path; every question auto-graded two independent ways.")
    L.append(f"- **Questions requested per run:** {s['n']}  ·  **Judge model:** {s['judge_model']}")
    L.append(f"- **Run date:** {s['run_date']}  ·  **Server:** {s['server']}\n")

    L.append("## Headline\n")
    L.append(f"- **Fully-clean runs: {s['fully_clean_runs']} / {s['runs_attempted']}** "
             "— a run is fully-clean iff **0 dropped** by the grounding gate **AND 0** kept "
             "questions flagged key-unsupported by the judge.")
    L.append(f"- Across all completed runs: **{s['total_generated']} generated → "
             f"{s['total_kept']} kept / {s['total_dropped']} dropped** by the deterministic grounding gate.")
    L.append(f"- Of the {s['total_kept']} kept questions, the semantic judge flagged "
             f"**{s['total_key_unsupported']} as key-unsupported**.")
    if s["runs_generation_failed"]:
        L.append(f"- ⚠ **{s['runs_generation_failed']} run(s) failed to generate** (server/network error) "
                 "— excluded from the totals above; see per-run table.")
    if s["judge_errors"]:
        L.append(f"- ⚠ {s['judge_errors']} judge call(s) errored and were counted as unsupported (safe direction).")
    L.append("")

    L.append("## The two independent checks (what each column means)\n")
    L.append("1. **Grounding gate — deterministic, HARD FACT.** The server keeps a question only "
             "if its `source_quote` is a verbatim substring of the visible guide text; otherwise it "
             "is dropped. `kept`/`dropped` are read straight off the response — not re-judged here. "
             "A non-zero `dropped` is a real, reproducible fact about that run.")
    L.append("2. **Support judge — semantic, LLM OPINION, UNCALIBRATED.** For each kept question we "
             "ask whether the cited quote, read literally, supports the *keyed* answer (catches "
             "inversions, wrong-key, number drift that the verbatim check cannot). This reuses the "
             "question-bank gate's judge.\n")
    L.append("> ⚠️ **Caveat — do not ship column 2 unread.** The grounding column is a hard "
             "deterministic fact. The support-judge column is an *uncalibrated* judge's opinion: it "
             "has not been scored against an SME-labeled gold set for this content. A human should "
             "spot-check a sample of the support verdicts (especially any flagged below) before any "
             "number from this doc is shown to a stakeholder.\n")

    L.append("## Per-run results\n")
    L.append("| Run | generated | kept | dropped | key-unsupported | verdict |")
    L.append("|----:|----------:|-----:|--------:|----------------:|:--------|")
    for r in s["runs"]:
        if r.get("gen_error") is not None:
            L.append(f"| {r['run']} | — | — | — | — | ⚠ generation failed |")
            continue
        verdict = "✅ fully-clean" if r["fully_clean"] else "⚠️ flagged"
        L.append(f"| {r['run']} | {r['generated']} | {r['kept']} | {r['dropped']} | "
                 f"{r['key_unsupported']} | {verdict} |")
    L.append("")

    flagged = [(r["run"], q) for r in s["runs"] for q in r.get("questions", []) if not q["supported"]]
    L.append("## Flagged questions — judge says the cited quote does not support the keyed answer\n")
    if not flagged:
        L.append("**None.** Across every completed run, each kept question's cited quote supported "
                 "its keyed answer (per the uncalibrated judge). The grounding gate also dropped "
                 f"{s['total_dropped']} question(s) before they reached the judge.\n")
    else:
        for run_i, q in flagged:
            tag = " · ⚙ JUDGE ERROR" if q.get("judge_error") else ""
            L.append(f"- **Run {run_i}{tag}** — excerpt `{q.get('excerpt_id')}`")
            L.append(f"  - **Stem:** {q['stem']}")
            L.append(f"  - **Keyed answer:** {q['keyed_answer']}")
            L.append(f"  - **Cited quote:** \"{q['cited_quote']}\"")
            L.append(f"  - **Judge:** {q['reason']}")
        L.append("")

    L.append("## Methodology & reproduction\n")
    L.append("- **Generation path:** the live demo server (`POST /api/resources/{rid}/quiz`) — the "
             "exact code learners would hit, not a re-implementation.")
    L.append("- **Judge:** `qbank_gate.llm_support_judge` run in-process (asyncio.run → Windows "
             "ProactorEventLoop, so the SDK judge can spawn). Runs sequential; kept questions per run "
             "judged in parallel (semaphore-bounded).")
    L.append("- **Clean definition:** `fully_clean = (dropped == 0) and (key_unsupported == 0)`.")
    L.append("- **Honest limits:** (a) the target is a *draft*, not yet SME-approved/published; "
             "(b) the support judge is uncalibrated for this content; (c) each run requested "
             f"{s['n']} questions — reliability is measured at that size, not at max(10).")
    L.append(f"- **Reproduce:** `python -m eval.quiz_reliability --rid {s['rid']} "
             f"--runs {s['runs_attempted']} --n {s['n']}`  (machine-readable results: "
             f"`{s['json_name']}`).")
    L.append("")
    return "\n".join(L)


async def main_async(args) -> int:
    DOCS.mkdir(exist_ok=True)
    out_md = Path(args.out) if args.out else DOCS / "QUIZ-RELIABILITY-INV-DISTRIBUTION.md"
    out_json = Path(args.json_out) if args.json_out else out_md.with_suffix(".json")

    # Pull title/status from the draft metadata if present (best-effort, cosmetic only).
    title, status = "Inventory: Learning Guide", "draft"
    meta_path = ROOT / "drafts" / f"{args.rid}.json"
    if meta_path.exists():
        try:
            m = json.loads(meta_path.read_text(encoding="utf-8"))
            status = m.get("status", status)
            title = m.get("title") or (f"{m.get('module','')} ({m.get('template','')})".strip() or title)
        except Exception:
            pass

    meta = {"rid": args.rid, "title": title, "status": status, "n": args.n,
            "server": args.server, "judge_model": "claude-sonnet-4-6",
            "run_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "json_name": out_json.name}
    sem = asyncio.Semaphore(args.judge_concurrency)

    print(f"Quiz reliability sweep — {args.runs} runs × n={args.n} on {args.rid}", flush=True)
    print(f"Server {args.server} · judge concurrency {args.judge_concurrency}", flush=True)
    print(f"Writing incrementally to {out_json}\n", flush=True)

    runs: list[dict] = []
    for i in range(1, args.runs + 1):
        r = await _run_once(args.server, args.rid, args.n, sem, i)
        runs.append(r)
        _write_json(out_json, _aggregate(runs, meta))  # incremental: crash leaves partial results

    summary = _aggregate(runs, meta)
    summary["runs_attempted"] = args.runs
    _write_json(out_json, summary)
    out_md.write_text(_md(summary), encoding="utf-8")

    print(f"\n── DONE ──")
    print(f"Fully-clean runs: {summary['fully_clean_runs']}/{summary['runs_attempted']}  ·  "
          f"kept {summary['total_kept']} / dropped {summary['total_dropped']}  ·  "
          f"key-unsupported {summary['total_key_unsupported']}")
    print(f"Doc : {out_md}")
    print(f"JSON: {out_json}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Reliability sweep for quiz-from-guide generation.")
    ap.add_argument("--rid", default=DEFAULT_RID, help="resource id of the guide to quiz")
    ap.add_argument("--runs", type=int, default=10, help="number of quiz generations")
    ap.add_argument("--n", type=int, default=6, help="questions requested per quiz (server clamps 3..10)")
    ap.add_argument("--server", default=DEFAULT_SERVER, help="demo server base URL")
    ap.add_argument("--judge-concurrency", type=int, default=5, help="max parallel support-judge calls")
    ap.add_argument("--out", help="output markdown path (default docs/QUIZ-RELIABILITY-INV-DISTRIBUTION.md)")
    ap.add_argument("--json-out", help="output JSON path (default: alongside the markdown)")
    args = ap.parse_args()
    return asyncio.run(main_async(args))


if __name__ == "__main__":
    sys.exit(main())
