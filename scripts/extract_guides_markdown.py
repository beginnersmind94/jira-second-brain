#!/usr/bin/env python3
"""Extract organized guide PDFs into structured Markdown.

Two files are written per guide:
  - <slug>.raw.md      Bot-owned. Cleanup pipeline output. Regenerated on every
                       run when the PDF (or cleanup pipeline) produces different
                       content. Hash of the cleaned text is recorded in its
                       frontmatter as raw_text_sha256.
  - <slug>.md          Curator-owned. Seeded from the raw on first run, then
                       hand-edited. Tracks which raw hash it has been reviewed
                       against (curated_against_raw_sha). When the raw drifts,
                       lint_guide_drift.py surfaces it for SME review.

A snapshot of the raw at SME review time is mirrored under
raw/guides/snapshots/<id>.raw.md so the drift diff stays self-contained
without depending on git history.
"""

import argparse
import csv
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader

REPO = Path(__file__).resolve().parent.parent
GUIDES_DIR = REPO / "raw" / "guides"
MANIFEST_PATH = GUIDES_DIR / "manifest.csv"
FAILURES_PATH = GUIDES_DIR / "failures.csv"
MARKDOWN_ROOT = GUIDES_DIR / "markdown"
SNAPSHOT_ROOT = GUIDES_DIR / "snapshots"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from guide_text_cleanup import clean as clean_pdf_text, text_hash  # noqa: E402

MANIFEST_FIELDS = [
    "id",
    "title",
    "platform",
    "module",
    "content_type",
    "source_url",
    "local_pdf",
    "status",
    "drift_status",
    "retrieved_at",
    "extracted_at",
    "sensitive_url",
    "error",
    "raw_markdown_path",
    "curated_markdown_path",
    "raw_text_sha256",
    "software_version",
    "source_updated",
    "created_at",
    "updated_at",
]

FAILURE_FIELDS = [
    "id",
    "title",
    "source_url",
    "error_type",
    "error_message",
    "attempted_at",
    "sensitive_url",
]

WINDOWS_ILLEGAL_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]+')
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


class ExtractionIssue(Exception):
    """Expected per-guide extraction issue."""


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def repo_rel(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def slugify(value, fallback):
    value = (value or "").strip() or fallback
    value = value.replace("&", " and ")
    value = WINDOWS_ILLEGAL_RE.sub(" ", value)
    value = re.sub(r"[^A-Za-z0-9._ -]+", " ", value)
    value = re.sub(r"[\s_]+", "-", value.strip())
    value = re.sub(r"-{2,}", "-", value)
    value = value.strip("-. ")
    return value or fallback


def markdown_paths_for(row):
    """Resolve the (raw_md, curated_md, snapshot) paths for a manifest row."""
    local_pdf = Path(row["local_pdf"]) if row.get("local_pdf") else None
    if local_pdf:
        try:
            rel_pdf = local_pdf.relative_to(Path("raw") / "guides" / "pdf")
            base = MARKDOWN_ROOT / rel_pdf.parent / rel_pdf.stem
        except ValueError:
            base = _fallback_base(row)
    else:
        base = _fallback_base(row)
    raw_md = base.with_name(base.name + ".raw.md")
    curated_md = base.with_name(base.name + ".md")
    snapshot = SNAPSHOT_ROOT / f"{row['id']}.raw.md"
    return raw_md, curated_md, snapshot


def _fallback_base(row):
    platform = slugify(row.get("platform"), "Unknown-Platform")
    module = slugify(row.get("module"), "Unknown-Module")
    content_type = slugify(row.get("content_type"), "Unknown-Content-Type")
    title = slugify(row.get("title"), "untitled-guide").lower()
    return MARKDOWN_ROOT / platform / module / content_type / f"{row['id']}-{title}"


def read_csv_dicts(path):
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def atomic_write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent), text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({field: row.get(field, "") for field in fieldnames})
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def atomic_write_text(path, content):
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


def yaml_string(value):
    return json.dumps(value or "", ensure_ascii=False)


def parse_frontmatter(text):
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    meta = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass
        elif value.startswith('"') and value.endswith('"'):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                value = value.strip('"')
        else:
            value = value.strip('"')
        meta[key.strip()] = value
    return meta


def existing_frontmatter(path):
    if not path.exists():
        return {}
    return parse_frontmatter(path.read_text(encoding="utf-8", errors="replace"))


def extract_pdf_pages(pdf_path):
    try:
        reader = PdfReader(str(pdf_path))
    except Exception as exc:
        raise ExtractionIssue(f"Could not open PDF: {exc}") from exc
    try:
        return [page.extract_text() or "" for page in reader.pages]
    except Exception as exc:
        raise ExtractionIssue(f"PDF text extraction failed: {exc}") from exc


def build_raw_markdown(row, body, cleanup_meta, raw_sha, extracted_at):
    """Build the bot-owned .raw.md file content."""
    title = row.get("title") or row.get("id") or "Untitled Guide"
    fm_lines = [
        "---",
        f"id: {row['id']}",
        f"title: {yaml_string(title)}",
        f"platform: {yaml_string(row.get('platform', ''))}",
        f"module: {yaml_string(row.get('module', ''))}",
        f"content_type: {yaml_string(row.get('content_type', ''))}",
        f"source_url: {yaml_string(row.get('source_url', ''))}",
        f"local_pdf: {yaml_string(row.get('local_pdf', ''))}",
    ]
    for key in ("software_version", "source_updated", "document_type", "author"):
        if cleanup_meta.get(key):
            fm_lines.append(f"{key}: {yaml_string(cleanup_meta[key])}")
    warnings = cleanup_meta.get("extraction_warnings") or []
    fm_lines.append(f"extraction_warnings: {json.dumps(warnings)}")
    fm_lines.append(f"extracted_at: {yaml_string(extracted_at)}")
    fm_lines.append(f"raw_text_sha256: {yaml_string(raw_sha)}")
    fm_lines.append("generated: true")
    fm_lines.append('status: "draft_extracted"')
    fm_lines.append("---")
    fm_lines.append("")
    fm_lines.append(f"# {title}")
    fm_lines.append("")
    fm_lines.append(body.rstrip() if body else "_(no extractable text found)_")
    fm_lines.append("")
    return "\n".join(fm_lines)


def build_curated_seed(row, body, cleanup_meta, raw_sha, seeded_at):
    """Build the initial human-curated .md file (seeded from raw)."""
    title = row.get("title") or row.get("id") or "Untitled Guide"
    fm_lines = [
        "---",
        f"id: {row['id']}",
        f"title: {yaml_string(title)}",
        f"platform: {yaml_string(row.get('platform', ''))}",
        f"module: {yaml_string(row.get('module', ''))}",
        f"content_type: {yaml_string(row.get('content_type', ''))}",
        f"source_url: {yaml_string(row.get('source_url', ''))}",
        f"local_pdf: {yaml_string(row.get('local_pdf', ''))}",
    ]
    for key in ("software_version", "source_updated", "document_type", "author"):
        if cleanup_meta.get(key):
            fm_lines.append(f"{key}: {yaml_string(cleanup_meta[key])}")
    fm_lines.append(f"curated_against_raw_sha: {yaml_string(raw_sha)}")
    fm_lines.append(f"curated_against_raw_at: {yaml_string(seeded_at)}")
    fm_lines.append('last_reviewed_by: ""')
    fm_lines.append('status: "needs_initial_review"')
    fm_lines.append("---")
    fm_lines.append("")
    fm_lines.append(f"# {title}")
    fm_lines.append("")
    fm_lines.append(
        "> Seeded from the raw extraction. Edit freely. When the raw drifts, "
        "review the diff and update this file, then mark it reviewed with "
        "`python scripts/mark_guide_reviewed.py " + row["id"] + "`."
    )
    fm_lines.append("")
    fm_lines.append(body.rstrip() if body else "_(no extractable text found)_")
    fm_lines.append("")
    return "\n".join(fm_lines)


def sort_manifest(rows):
    def key(row):
        match = re.search(r"\d+", row.get("id", ""))
        return int(match.group(0)) if match else 0
    return sorted(rows, key=key)


def upsert_failure(failures, row, error_type, message, timestamp):
    failures[row["id"]] = {
        "id": row.get("id", ""),
        "title": row.get("title", ""),
        "source_url": row.get("source_url", ""),
        "error_type": error_type,
        "error_message": message,
        "attempted_at": timestamp,
        "sensitive_url": row.get("sensitive_url", "false"),
    }


def load_failures():
    failures = {}
    for row in read_csv_dicts(FAILURES_PATH):
        key = row.get("id") or row.get("source_url") or row.get("title")
        if key:
            failures[key] = {field: row.get(field, "") for field in FAILURE_FIELDS}
    return failures


def compute_drift_status(raw_md_path, snapshot_path, new_raw_sha):
    """Determine drift_status from snapshot presence and hashes."""
    if not snapshot_path.exists():
        return "initial"
    snap_meta = existing_frontmatter(snapshot_path)
    snap_sha = snap_meta.get("raw_text_sha256")
    if snap_sha and snap_sha == new_raw_sha:
        return "clean"
    return "drifted"


def main():
    parser = argparse.ArgumentParser(description="Extract guide PDFs into structured Markdown.")
    parser.add_argument("--force", action="store_true", help="Rewrite .raw.md even if content unchanged.")
    parser.add_argument("--reseed-curated", action="store_true", help="(Re)seed curated .md from raw when missing; never overwrites existing curated files.")
    args = parser.parse_args()

    rows = read_csv_dicts(MANIFEST_PATH)
    if not rows:
        raise SystemExit(f"No manifest rows found at {MANIFEST_PATH}")

    failures = load_failures()
    run_ts = now_iso()
    processed = []
    counts = {
        "pdfs_found": 0,
        "raw_written": 0,
        "raw_unchanged": 0,
        "curated_seeded": 0,
        "snapshots_seeded": 0,
        "drifted": 0,
        "failed": 0,
        "warnings": 0,
    }

    for raw_row in rows:
        row = {field: raw_row.get(field, "") for field in MANIFEST_FIELDS}
        # Bring forward unknown columns we did not list (e.g. legacy markdown_path)
        for k, v in raw_row.items():
            row.setdefault(k, v)
        row["created_at"] = row.get("created_at") or run_ts

        raw_md, curated_md, snapshot = markdown_paths_for(row)
        row["raw_markdown_path"] = repo_rel(raw_md)
        row["curated_markdown_path"] = repo_rel(curated_md)

        local_pdf = row.get("local_pdf", "")
        pdf_path = REPO / local_pdf
        if not local_pdf or not pdf_path.exists():
            counts["failed"] += 1
            row["status"] = "extraction_failed"
            row["error"] = "Local PDF is missing"
            row["updated_at"] = run_ts
            upsert_failure(failures, row, "missing_pdf", row["error"], run_ts)
            print(f"{row['id']}: failed: missing PDF")
            processed.append(row)
            continue

        counts["pdfs_found"] += 1

        try:
            pages = extract_pdf_pages(pdf_path)
            body, cleanup_meta = clean_pdf_text(pages, frontmatter_title=row.get("title", ""))
            warnings = cleanup_meta.get("extraction_warnings") or []
            new_raw_sha = text_hash(body)

            existing_raw = existing_frontmatter(raw_md) if raw_md.exists() else {}
            existing_sha = existing_raw.get("raw_text_sha256", "")

            raw_changed = not (raw_md.exists() and existing_sha == new_raw_sha)
            if raw_changed or args.force:
                extracted_at = now_iso()
                raw_content = build_raw_markdown(row, body, cleanup_meta, new_raw_sha, extracted_at)
                atomic_write_text(raw_md, raw_content)
                counts["raw_written"] += 1
                row["extracted_at"] = extracted_at
                row["raw_text_sha256"] = new_raw_sha
                for k in ("software_version", "source_updated"):
                    if cleanup_meta.get(k):
                        row[k] = cleanup_meta[k]
            else:
                counts["raw_unchanged"] += 1
                row["extracted_at"] = existing_raw.get("extracted_at", "") or run_ts
                row["raw_text_sha256"] = new_raw_sha
                for k in ("software_version", "source_updated"):
                    if existing_raw.get(k):
                        row[k] = existing_raw[k]

            # Migrate legacy single-file extractions. The previous extractor
            # wrote everything to <slug>.md and never produced a .raw.md, so
            # the existing .md is bot output, not human curation. Detect that
            # shape (presence of 'workflow_authority' + absence of
            # 'curated_against_raw_sha') and archive once so we can seed a
            # clean curated file in its place.
            if curated_md.exists():
                existing_curated = existing_frontmatter(curated_md)
                looks_legacy = (
                    "workflow_authority" in existing_curated
                    and "curated_against_raw_sha" not in existing_curated
                )
                if looks_legacy:
                    legacy_path = curated_md.with_suffix(curated_md.suffix + ".legacy")
                    if not legacy_path.exists():
                        shutil.move(str(curated_md), str(legacy_path))
                        counts.setdefault("legacy_archived", 0)
                        counts["legacy_archived"] += 1

            # Seed curated .md on first sight (we never clobber a curated file
            # that already has the new-format frontmatter).
            if not curated_md.exists():
                seed_content = build_curated_seed(
                    row, body, cleanup_meta, new_raw_sha, row.get("extracted_at") or run_ts
                )
                atomic_write_text(curated_md, seed_content)
                counts["curated_seeded"] += 1

            # Seed snapshot on first sight too. The snapshot is the raw at
            # last SME review; on initial extraction we treat the seed as the
            # implicit "first review" so the curated starts in 'clean' status.
            if not snapshot.exists():
                snapshot.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(raw_md, snapshot)
                counts["snapshots_seeded"] += 1

            row["drift_status"] = compute_drift_status(raw_md, snapshot, new_raw_sha)
            if row["drift_status"] == "drifted":
                counts["drifted"] += 1

            row["status"] = "needs_review" if warnings else "draft_extracted"
            row["error"] = ", ".join(warnings) if warnings else ""
            row["updated_at"] = now_iso()
            if warnings:
                counts["warnings"] += 1
                upsert_failure(failures, row, "weak_extraction", row["error"], row["updated_at"])
            else:
                failures.pop(row["id"], None)

            raw_action = "written" if raw_changed or args.force else "unchanged"
            print(
                f"{row['id']}: raw={raw_action} drift={row['drift_status']}"
                + (f" warnings={row['error']}" if warnings else "")
            )

        except ExtractionIssue as exc:
            counts["failed"] += 1
            ts = now_iso()
            row["updated_at"] = ts
            row["status"] = "extraction_failed"
            row["error"] = str(exc)
            upsert_failure(failures, row, exc.__class__.__name__, str(exc), ts)
            print(f"{row['id']}: failed: {exc}")

        processed.append(row)

    failure_rows = sorted(failures.values(), key=lambda r: r.get("id", ""))
    processed = sort_manifest(processed)
    atomic_write_csv(MANIFEST_PATH, processed, MANIFEST_FIELDS)
    atomic_write_csv(FAILURES_PATH, failure_rows, FAILURE_FIELDS)

    print("")
    print("Guide Markdown extraction summary")
    for key, value in counts.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
