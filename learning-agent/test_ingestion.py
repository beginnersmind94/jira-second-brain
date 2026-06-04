"""CI regression test for identifier handling at ingestion.

Asserts the contract documented in README.md ("Identifier handling at ingestion"):
the pipeline resolves a ticket's parent to a REAL epic key or drops it — it must
NEVER persist a bare internal numeric id and NEVER mint a phantom epic stub.

Run:  python test_ingestion.py        (exit 0 = pass)
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

APP = Path(__file__).resolve().parent
OUT = APP / "data" / "demo" / "zztest-fixture.json"
TMP = APP / "_tmp_ingestion.csv"
HEADER = ["Issue Type", "Issue key", "Issue id", "Summary", "Custom field (Module)",
          "Parent", "Parent summary", "Custom field (Acceptance Criteria)"]


def _write_csv(rows):
    with TMP.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        w.writerows(rows)


def _build(strict=False):
    cmd = [sys.executable, "build_fixtures_from_csv.py", str(TMP), "--modules", "ZZTest"]
    if strict:
        cmd.append("--strict")
    return subprocess.run(cmd, capture_output=True, text=True, cwd=APP)


def _fixture():
    return json.loads(OUT.read_text(encoding="utf-8"))


def _cleanup():
    TMP.unlink(missing_ok=True)
    OUT.unlink(missing_ok=True)


def case(name):
    print(f"\n== {name} ==")


def main() -> int:
    try:
        # 1) Issue-id parent (internal id) resolves to the real epic KEY.
        case("1. Parent-by-internal-id resolves to real key")
        _write_csv([
            ["Epic", "NXT-64788", "105530", "FO - Sustenance (2025-26)", "ZZTest", "", "", ""],
            ["Story", "NXT-68256", "200001", "Verification QoL", "ZZTest", "105530", "FO - Sustenance (2025-26)", "yes"],
        ])
        r = _build(); assert r.returncode == 0, r.stderr
        fx = _fixture()
        assert fx["tickets"]["NXT-68256"]["epic_key"] == "NXT-64788", "id->key failed"
        assert "105530" not in fx["epics"], "bare-id stub was minted"
        assert "NXT-68256" in fx["epics"]["NXT-64788"]["children"]
        print("   OK: 105530 -> NXT-64788, no bare-id stub")

        # 2) No Issue-id column: bare parent resolves via UNIQUE epic summary.
        case("2. Summary-match fallback (no Issue id)")
        with TMP.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Issue Type", "Issue key", "Summary", "Custom field (Module)", "Parent", "Parent summary"])
            w.writerows([
                ["Epic", "NXT-64786", "SC - Forms Framework", "ZZTest", "", ""],
                ["Story", "NXT-70001", "Add a form field", "ZZTest", "105528", "SC - Forms Framework"],
            ])
        r = _build(); assert r.returncode == 0, r.stderr
        fx = _fixture()
        assert fx["tickets"]["NXT-70001"]["epic_key"] == "NXT-64786", "summary-match failed"
        assert "105528" not in fx["epics"], "bare-id stub minted in summary path"
        print("   OK: bare 105528 -> NXT-64786 via unique summary")

        # 3) Unresolvable parent -> dropped to '-', NO phantom epic minted.
        case("3. Unresolvable parent is dropped, never fabricated")
        with TMP.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Issue Type", "Issue key", "Summary", "Custom field (Module)", "Parent", "Parent summary"])
            w.writerows([
                ["Story", "NXT-80001", "Orphan story", "ZZTest", "999999", "Some Other-Module Epic"],
            ])
        r = _build(); assert r.returncode == 0, r.stderr
        fx = _fixture()
        assert fx["tickets"]["NXT-80001"]["epic_key"] == "-", "unresolved parent not dropped"
        assert fx["epics"] == {}, f"phantom epic minted: {list(fx['epics'])}"
        print("   OK: 999999 dropped to '-', epics empty (no phantom)")

        # 4) --strict FAILS the build when a parent can't resolve.
        case("4. --strict fails loud on unresolved parent")
        r = _build(strict=True)
        assert r.returncode != 0, "strict mode should have failed"
        assert "STRICT FAIL" in (r.stdout + r.stderr)
        print("   OK: --strict exited non-zero with STRICT FAIL")

        # 5) Duplicate-identity fingerprint (two epics, same summary) is flagged.
        case("5. Duplicate-summary epics are flagged")
        with TMP.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Issue Type", "Issue key", "Summary", "Custom field (Module)", "Parent", "Parent summary"])
            w.writerows([
                ["Epic", "NXT-1", "SC - Forms Framework", "ZZTest", "", ""],
                ["Epic", "NXT-2", "SC - Forms Framework", "ZZTest", "", ""],
                ["Story", "NXT-3", "x", "ZZTest", "", ""],
            ])
        r = _build(); assert r.returncode == 0, r.stderr
        assert "duplicate-summary" in r.stdout, "dup-summary not flagged"
        print("   OK: duplicate-summary epic group flagged")

        print("\nALL INGESTION TESTS PASSED")
        return 0
    finally:
        _cleanup()


if __name__ == "__main__":
    sys.exit(main())
