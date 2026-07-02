"""Gate-parity report: on KNOWN-clean drafts (every claim block cited), Version B's coverage
layer must not fail anything the substring layer passes. PASS when divergences == 0.
Run: python -m eval.parity"""
import os
import sys
import demo
from citation_gate import run_gate

CLEAN_DRAFTS = [
    ('<h1>A</h1>\n<p>Alpha.<!-- Source: [[NXT-1001:AC]] "Alpha." --></p>\n\n'
     "<h2>Sources</h2>\n<ul>\n<li><code>NXT-1001</code> — x</li>\n</ul>"),
    ('<h1>B</h1>\n<p>Bravo.<!-- Source: [[NXT-1001:RN]] "Bravo." --></p>\n'
     '<ul>\n<li>Point.<!-- Source: [[NXT-1001:AC]] "Alpha." --></li>\n</ul>'),
]


def main() -> int:
    demo._FIX = {"tickets": {"NXT-1001": {"ac": "Alpha.", "rn": "Bravo.",
                                          "rn_internal": "", "desc": ""}},
                 "epics": {}}
    os.environ["GATE_MODE"] = "both"
    divergences = 0
    try:
        for i, html in enumerate(CLEAN_DRAFTS):
            g = run_gate(html)
            sub_ok = (g["substring"]["tier_lie"] == 0 and g["substring"]["quote_not_found"] == 0)
            if sub_ok and not g["passed"]:
                divergences += 1
                print(f"  draft {i}: substring PASS but gate FAIL -> {g['citations']}")
    finally:
        os.environ.pop("GATE_MODE", None)
    print(f"divergences: {divergences}")
    return 0 if divergences == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
