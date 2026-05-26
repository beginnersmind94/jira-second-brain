#!/usr/bin/env python3
"""Surface guides whose .raw.md has drifted from the SME-reviewed snapshot.

Reads the manifest, finds rows where drift_status is "drifted", and writes a
side-by-side HTML diff to raw/guides/diffs/<id>.diff.html for each one. The
HTML diff compares the snapshot (text at last SME review) against the current
.raw.md (text from the latest PDF extraction).

The diff file deliberately omits frontmatter and the seeded H1 so the SME
sees only the substantive guide content that changed.

After the SME reviews a diff and updates the curated .md to match, they run
`mark_guide_reviewed.py <id>` to refresh the snapshot and clear drift.
"""

import argparse
import csv
import difflib
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GUIDES_DIR = REPO / "raw" / "guides"
MANIFEST_PATH = GUIDES_DIR / "manifest.csv"
DIFFS_DIR = GUIDES_DIR / "diffs"
SNAPSHOT_ROOT = GUIDES_DIR / "snapshots"

FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)


def repo_rel(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_csv_dicts(path: Path):
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def strip_frontmatter_and_h1(text: str) -> str:
    """Return just the substantive body — drop frontmatter and the seeded H1.

    The H1 is generated from the manifest title and is reflected in every
    .raw.md, so including it in the diff would add noise on every title
    tweak. Frontmatter likewise carries hashes/timestamps that diff
    constantly and don't reflect content change.
    """
    no_frontmatter = FRONTMATTER_RE.sub("", text, count=1)
    lines = no_frontmatter.splitlines()
    out = []
    saw_h1 = False
    for line in lines:
        if not saw_h1 and line.startswith("# "):
            saw_h1 = True
            continue
        if not saw_h1 and not line.strip():
            continue
        out.append(line)
    return "\n".join(out).strip() + "\n"


def render_html_diff(old: str, new: str, guide_id: str, title: str,
                     snapshot_path: str, raw_path: str) -> str:
    """Render a side-by-side HTML diff suitable for SME review.

    Uses difflib.HtmlDiff for the side-by-side body, then wraps it in a
    standalone HTML document with a header that names the guide and the
    files being compared. No external CSS/JS dependencies.
    """
    old_lines = old.splitlines()
    new_lines = new.splitlines()

    differ = difflib.HtmlDiff(wrapcolumn=80, tabsize=4)
    body_table = differ.make_table(
        old_lines,
        new_lines,
        fromdesc="Reviewed snapshot",
        todesc="Current raw extraction",
        context=False,
    )

    style = """
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
           margin: 24px; color: #1f2328; }
    header { border-bottom: 1px solid #d0d7de; padding-bottom: 16px; margin-bottom: 16px; }
    h1 { font-size: 20px; margin: 0 0 4px 0; }
    .meta { color: #57606a; font-size: 13px; }
    .meta code { background: #eaeef2; padding: 1px 4px; border-radius: 3px; }
    table.diff { border-collapse: collapse; font-family: ui-monospace, SFMono-Regular,
                 "SF Mono", Menlo, monospace; font-size: 12.5px; width: 100%;
                 table-layout: fixed; }
    table.diff td { padding: 1px 6px; vertical-align: top; word-wrap: break-word; }
    table.diff td.diff_header { background: #f6f8fa; color: #57606a;
                                font-family: -apple-system, sans-serif; font-size: 12px;
                                width: 36px; text-align: right; }
    table.diff th { background: #eaeef2; padding: 6px; text-align: left;
                    font-family: -apple-system, sans-serif; font-size: 13px; }
    table.diff td.diff_next { display: none; }
    table.diff .diff_add { background: #dafbe1; }
    table.diff .diff_chg { background: #fff8c5; }
    table.diff .diff_sub { background: #ffebe9; }
    .legend { margin: 12px 0; font-size: 13px; color: #57606a; }
    .legend span { padding: 2px 6px; border-radius: 3px; margin-right: 8px; }
    .legend .add { background: #dafbe1; }
    .legend .chg { background: #fff8c5; }
    .legend .sub { background: #ffebe9; }
    """

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Drift: {guide_id} — {title}</title>
<style>{style}</style>
</head><body>
<header>
  <h1>{guide_id} — {title}</h1>
  <p class="meta">
    Snapshot: <code>{snapshot_path}</code><br>
    Current:  <code>{raw_path}</code><br>
    Generated: {now_iso()}
  </p>
  <p class="legend">
    <span class="sub">removed</span>
    <span class="add">added</span>
    <span class="chg">changed</span>
  </p>
</header>
{body_table}
</body></html>
"""


def write_diff_for(row, snapshot_path: Path, raw_path: Path, out_path: Path) -> bool:
    """Write the HTML diff for one guide. Returns True if anything was written."""
    if not snapshot_path.exists() or not raw_path.exists():
        return False
    old = strip_frontmatter_and_h1(snapshot_path.read_text(encoding="utf-8"))
    new = strip_frontmatter_and_h1(raw_path.read_text(encoding="utf-8"))
    if old == new:
        return False
    html = render_html_diff(
        old,
        new,
        guide_id=row["id"],
        title=row.get("title", ""),
        snapshot_path=repo_rel(snapshot_path),
        raw_path=repo_rel(raw_path),
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=out_path.name + ".", dir=str(out_path.parent), text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(html)
        os.replace(tmp, out_path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    return True


def cleanup_stale_diffs(active_ids):
    """Remove diff files for guides that are no longer drifted."""
    if not DIFFS_DIR.exists():
        return 0
    removed = 0
    for diff_file in DIFFS_DIR.glob("*.diff.html"):
        guide_id = diff_file.name.split(".")[0]
        if guide_id not in active_ids:
            diff_file.unlink()
            removed += 1
    return removed


def main():
    parser = argparse.ArgumentParser(description="Surface drifted guides and write SME-facing diff files.")
    parser.add_argument("--id", help="Only check this guide ID.")
    parser.add_argument("--quiet", action="store_true", help="Suppress per-guide output for clean guides.")
    args = parser.parse_args()

    rows = read_csv_dicts(MANIFEST_PATH)
    if not rows:
        print(f"No manifest rows at {MANIFEST_PATH}", file=sys.stderr)
        return 1

    drifted_ids = set()
    written = 0
    skipped_clean = 0

    for row in rows:
        if args.id and row.get("id") != args.id:
            continue
        guide_id = row.get("id", "")
        title = row.get("title", "")
        drift = row.get("drift_status", "")
        if drift not in ("drifted", "initial"):
            if not args.quiet:
                print(f"{guide_id}: {drift or 'unknown'} — skipped")
            skipped_clean += 1
            continue

        snapshot_path = SNAPSHOT_ROOT / f"{guide_id}.raw.md"
        raw_md_rel = row.get("raw_markdown_path", "")
        raw_path = REPO / raw_md_rel if raw_md_rel else None

        if not raw_path or not raw_path.exists():
            print(f"{guide_id}: missing raw markdown at {raw_md_rel}", file=sys.stderr)
            continue
        if not snapshot_path.exists():
            print(f"{guide_id}: no snapshot yet ({drift}) — will be created on next extraction")
            continue

        out_path = DIFFS_DIR / f"{guide_id}.diff.html"
        if write_diff_for(row, snapshot_path, raw_path, out_path):
            drifted_ids.add(guide_id)
            written += 1
            print(f"{guide_id}: drift detected — {title}")
            print(f"         diff: {repo_rel(out_path)}")
        elif not args.quiet:
            print(f"{guide_id}: manifest says drifted but content matches snapshot")

    stale_removed = cleanup_stale_diffs(drifted_ids)

    print("")
    print("Drift lint summary")
    print(f"  drift reports written: {written}")
    print(f"  clean guides skipped: {skipped_clean}")
    print(f"  stale diff files removed: {stale_removed}")
    if drifted_ids:
        print("")
        print(f"Open {DIFFS_DIR.relative_to(REPO).as_posix()}/<id>.diff.html in a browser to review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
