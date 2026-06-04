"""One-shot: carve a small Eligibility ticket CSV from jira-brain/raw/tickets/."""
import csv
import glob
import os
import re

import yaml

TICKETS_DIR = r"C:\Users\rahul.mehta\Downloads\Financials-Documentation-KT\jira-brain\raw\tickets"
OUT = os.path.join(os.path.dirname(__file__), "data", "tickets.csv")
TARGET_COMPONENT = "Eligibility"
MAX_TICKETS = 100


def parse_ticket(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.S)
    if not m:
        return None
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except Exception:
        return None
    body = m.group(2)

    desc = ac = ""
    desc_match = re.search(r"## Description\s*\n(.*?)(?=\n## |\Z)", body, re.S)
    if desc_match:
        desc = desc_match.group(1).strip()
    ac_match = re.search(r"## Acceptance Criteria\s*\n(.*?)(?=\n## |\Z)", body, re.S)
    if ac_match:
        ac = ac_match.group(1).strip()

    return {
        "key": fm.get("key", ""),
        "summary": fm.get("summary", ""),
        "components": fm.get("components") or [],
        "status": fm.get("status", ""),
        "description": desc,
        "acceptance_criteria": ac,
    }


def main():
    files = sorted(glob.glob(os.path.join(TICKETS_DIR, "*.md")))
    rows = []
    for fp in files:
        parsed = parse_ticket(fp)
        if not parsed:
            continue
        if not any(TARGET_COMPONENT in (c or "") for c in parsed["components"]):
            continue
        if parsed["status"] not in ("Done Done", "Done", "Closed", "Resolved"):
            continue
        if not parsed["description"] and not parsed["acceptance_criteria"]:
            continue
        rows.append(parsed)
        if len(rows) >= MAX_TICKETS:
            break

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["Key", "Summary", "Release Notes", "Acceptance Criteria",
             "Priority", "Module", "Epic"]
        )
        for r in rows:
            writer.writerow([
                r["key"],
                r["summary"],
                "",
                r["acceptance_criteria"][:2000],
                "",
                ", ".join(r["components"]),
                "",
            ])

    print(f"wrote {len(rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
