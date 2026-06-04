"""Build offline demo fixtures from the Perseus Jira "all fields" CSV export.

Produces data/demo/<module-slug>-fixture.json (the SAME schema demo_capture.py
writes from live Jira) for each requested module — so the demo can run every
module offline, no live Jira needed.

Honors the CSV gotchas (see jira-brain/raw/jira-csv-reference.md):
  - read utf-8-sig (BOM); raise csv field-size limit (big AC/Description)
  - match columns by HEADER NAME, not index; multi-value fields repeat under the
    same header (Components, Comment, ...) -> collect all
  - Acceptance Criteria is the 2nd of two AC columns (the 1st is empty) -> pick
    the AC column with content
  - Module comes from `Custom field (Module)` (more reliable than the Summary)
  - clean common mojibake (utf-8 text mis-decoded as cp1252)

Usage:
    python build_fixtures_from_csv.py "C:\\path\\Perseus Jira (5).csv"
"""
import argparse
import csv
import json
import sys
from pathlib import Path

csv.field_size_limit(10**7)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

APP_DIR = Path(__file__).parent
OUT_DIR = APP_DIR / "data" / "demo"

TARGET_MODULES = ["Accountability", "Account Management", "Eligibility", "Item Management",
                  "Menu Planning", "Insights", "Inventory"]

# Mojibake markers (as ASCII unicode escapes so the source can't be mangled):
#   "â€" == "â€"  (smart punctuation), "Ã" == "Ã", "Â" == "Â"
_MOJI_MARKERS = ("â€", "Ã", "Â")


def _clean(s: str) -> str:
    """Strip + repair mojibake (utf-8 bytes that were decoded as cp1252)."""
    if not s:
        return ""
    if any(m in s for m in _MOJI_MARKERS):
        try:
            s = s.encode("cp1252", "ignore").decode("utf-8", "ignore")
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
    return s.strip()


def _name_index(header: list[str]) -> dict[str, list[int]]:
    idx: dict[str, list[int]] = {}
    for i, h in enumerate(header):
        idx.setdefault(h, []).append(i)
    return idx


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv_path")
    ap.add_argument("--modules", default=",".join(TARGET_MODULES),
                    help="comma-separated module names")
    args = ap.parse_args()
    modules = [m.strip() for m in args.modules.split(",") if m.strip()]

    with open(args.csv_path, encoding="utf-8-sig", newline="") as f:
        rdr = csv.reader(f)
        header = next(rdr)
        rows = list(rdr)
    idx = _name_index(header)

    def first(name):
        return idx.get(name, [None])[0]

    # Acceptance Criteria: pick the AC column that actually carries content.
    ac_cols = idx.get("Custom field (Acceptance Criteria)", [])
    ac_col = (max(ac_cols, key=lambda c: sum(1 for r in rows if c < len(r) and r[c].strip()))
              if ac_cols else None)

    COMP_COLS = idx.get("Components", [])
    C = {
        "key": first("Issue key"), "summary": first("Summary"), "status": first("Status"),
        "issuetype": first("Issue Type"), "priority": first("Priority"),
        "module": first("Custom field (Module)"),
        "rn": first("Custom field (Release Notes)"),
        "rn_internal": first("Custom field (Release Notes (Internal))"),
        "rn_title": first("Custom field (Release Notes Title)"),
        "rn_required": first("Custom field (Release Notes Required)"),
        "desc": first("Description"), "epic_key": first("Parent"),
        "epic_summary": first("Parent summary"),
    }

    def cell(row, col):
        return _clean(row[col]) if (col is not None and col < len(row)) else ""

    def record(row) -> dict:
        comps = [_clean(row[c]) for c in COMP_COLS if c < len(row) and row[c].strip()]
        return {
            "key": cell(row, C["key"]), "summary": cell(row, C["summary"]),
            "status": cell(row, C["status"]) or "?", "issuetype": cell(row, C["issuetype"]) or "?",
            "priority": cell(row, C["priority"]) or "-", "components": comps,
            "module": cell(row, C["module"]) or "-",
            "rn_required": cell(row, C["rn_required"]) or "-",
            "rn_title": cell(row, C["rn_title"]),
            "ac": _clean(row[ac_col]) if (ac_col is not None and ac_col < len(row)) else "",
            "rn": cell(row, C["rn"]), "rn_internal": cell(row, C["rn_internal"]),
            "desc": cell(row, C["desc"]),
            "epic_key": cell(row, C["epic_key"]) or "-",
            "epic_summary": cell(row, C["epic_summary"]),
        }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = []
    for module in modules:
        recs = [record(r) for r in rows if cell(r, C["module"]) == module]
        tickets, epics = {}, {}
        for rec in recs:
            if not rec["key"]:
                continue
            if rec["issuetype"] == "Epic":
                epics[rec["key"]] = {**rec, "children": []}
            else:
                tickets[rec["key"]] = rec
        for k, t in tickets.items():
            ek = t.get("epic_key")
            if ek and ek != "-":
                epics.setdefault(ek, {
                    "key": ek, "summary": t.get("epic_summary", ""), "status": "?",
                    "issuetype": "Epic", "priority": "-", "components": [], "module": module,
                    "rn_required": "-", "rn_title": "", "ac": "", "rn": "", "rn_internal": "",
                    "desc": "", "epic_key": "-", "epic_summary": "", "children": [],
                })
                epics[ek]["children"].append(k)

        fixture = {"module": module, "captured_at": "from-csv:" + Path(args.csv_path).name,
                   "tickets": tickets, "epics": epics}
        slug = module.lower().replace(" ", "-")
        out = OUT_DIR / f"{slug}-fixture.json"
        out.write_text(json.dumps(fixture, indent=2), encoding="utf-8")
        with_ac = sum(1 for t in tickets.values() if t["ac"])
        summary.append((module, len(tickets), len(epics), with_ac, out.name))

    print(f"{'module':22}{'tickets':>8}{'epics':>7}{'w/AC':>6}  file")
    for m, nt, ne, ac, fn in summary:
        print(f"{m:22}{nt:>8}{ne:>7}{ac:>6}  {fn}")


if __name__ == "__main__":
    main()
