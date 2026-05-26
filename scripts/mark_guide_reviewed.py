#!/usr/bin/env python3
"""Mark a guide as reviewed against the current .raw.md.

This is the SME's "I've looked at the drift and updated the curated file"
button. It does three things:

  1. Copies the current .raw.md to raw/guides/snapshots/<id>.raw.md
     (this becomes the new "last reviewed" baseline).
  2. Updates the curated <id>.md frontmatter:
       - curated_against_raw_sha -> current raw hash
       - curated_against_raw_at  -> now
       - last_reviewed_by        -> --by argument (if provided)
       - status                  -> "reviewed" (was "needs_initial_review")
  3. Updates the manifest row's drift_status to "clean".

Stale diff files (raw/guides/diffs/<id>.diff.html) are deleted automatically
by the next run of lint_guide_drift.py.
"""

import argparse
import csv
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GUIDES_DIR = REPO / "raw" / "guides"
MANIFEST_PATH = GUIDES_DIR / "manifest.csv"
SNAPSHOT_ROOT = GUIDES_DIR / "snapshots"
DIFFS_DIR = GUIDES_DIR / "diffs"

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def yaml_quoted(value: str) -> str:
    safe = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{safe}"'


def read_manifest():
    with open(MANIFEST_PATH, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []
    return rows, fieldnames


def write_manifest(rows, fieldnames):
    fd, tmp = tempfile.mkstemp(prefix=MANIFEST_PATH.name + ".", dir=str(MANIFEST_PATH.parent), text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({field: row.get(field, "") for field in fieldnames})
        os.replace(tmp, MANIFEST_PATH)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def read_frontmatter_and_body(path: Path):
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None, text
    return match.group(1), text[match.end():]


def update_frontmatter_fields(frontmatter: str, updates: dict) -> str:
    """Replace existing keys in YAML frontmatter and append missing ones.

    This is intentionally minimal — only single-line scalar keys are
    handled. The curated file's frontmatter is bot-seeded with this shape,
    so we don't need to worry about complex YAML structures.
    """
    lines = frontmatter.splitlines()
    seen = set()
    for i, line in enumerate(lines):
        if ":" not in line:
            continue
        key = line.split(":", 1)[0].strip()
        if key in updates:
            lines[i] = f"{key}: {updates[key]}"
            seen.add(key)
    for key, value in updates.items():
        if key not in seen:
            lines.append(f"{key}: {value}")
    return "\n".join(lines)


def write_text_atomic(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent), text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def main():
    parser = argparse.ArgumentParser(description="Mark a guide as reviewed against its current .raw.md.")
    parser.add_argument("guide_id", help="Guide ID, e.g. GUIDE-013")
    parser.add_argument("--by", default="", help="SME name/email to record in last_reviewed_by.")
    args = parser.parse_args()

    rows, fieldnames = read_manifest()
    row = next((r for r in rows if r.get("id") == args.guide_id), None)
    if row is None:
        print(f"No manifest row for {args.guide_id}", file=sys.stderr)
        return 1

    raw_rel = row.get("raw_markdown_path", "")
    curated_rel = row.get("curated_markdown_path", "")
    if not raw_rel or not curated_rel:
        print(f"{args.guide_id}: manifest row is missing raw/curated paths", file=sys.stderr)
        return 1

    raw_path = REPO / raw_rel
    curated_path = REPO / curated_rel
    snapshot_path = SNAPSHOT_ROOT / f"{args.guide_id}.raw.md"
    diff_path = DIFFS_DIR / f"{args.guide_id}.diff.html"

    if not raw_path.exists():
        print(f"{args.guide_id}: raw markdown missing at {raw_rel}", file=sys.stderr)
        return 1
    if not curated_path.exists():
        print(f"{args.guide_id}: curated markdown missing at {curated_rel}", file=sys.stderr)
        return 1

    raw_sha = row.get("raw_text_sha256", "")
    reviewed_at = now_iso()

    # 1) Refresh snapshot
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(raw_path, snapshot_path)

    # 2) Update curated frontmatter
    frontmatter, body = read_frontmatter_and_body(curated_path)
    if frontmatter is None:
        print(f"{args.guide_id}: curated file has no frontmatter; aborting", file=sys.stderr)
        return 1
    updates = {
        "curated_against_raw_sha": yaml_quoted(raw_sha),
        "curated_against_raw_at": yaml_quoted(reviewed_at),
        "status": yaml_quoted("reviewed"),
    }
    if args.by:
        updates["last_reviewed_by"] = yaml_quoted(args.by)
    new_frontmatter = update_frontmatter_fields(frontmatter, updates)
    write_text_atomic(curated_path, f"---\n{new_frontmatter}\n---\n{body}")

    # 3) Update manifest row
    row["drift_status"] = "clean"
    row["updated_at"] = reviewed_at
    write_manifest(rows, fieldnames)

    # 4) Remove stale diff if present
    if diff_path.exists():
        diff_path.unlink()

    print(f"{args.guide_id}: marked reviewed (sha={raw_sha[:8]}, by={args.by or '-'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
