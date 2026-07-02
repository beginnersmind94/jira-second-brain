"""INFORMATIONAL (never fails): show how the coverage layer would score REAL drafts, so the team
can see whether GATE_MODE=both would false-positive on legitimately-structured content BEFORE
Version B relies on it. Fixture-free — it calls only the coverage layer.
Run: python -m eval.coverage_report [file1.html file2.html ...]  (defaults to drafts\\*.html)"""
import glob
import os
import sys
from citation_gate import _uncited_claim_blocks


def main() -> int:
    files = sys.argv[1:] or sorted(glob.glob(os.path.join("drafts", "*.html")))
    if not files:
        print("no draft html found (looked in drafts\\*.html)")
        return 0
    for f in files:
        try:
            html = open(f, encoding="utf-8").read()
        except OSError as e:
            print(f"  skip {f}: {e}")
            continue
        total, uncited = _uncited_claim_blocks(html)
        print(f"{uncited:>3} uncited / {total:>3} claim blocks   {os.path.basename(f)}")
    print("\n(informational only — nonzero 'uncited' shows where GATE_MODE=both would flag a draft)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
