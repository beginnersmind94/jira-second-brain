"""Step 4 ingest: CSV -> one Markdown file per ticket, resumable."""
import csv
import json
import os
import sys
import tempfile
from pathlib import Path

csv.field_size_limit(10**9)

VAULT = Path(__file__).resolve().parent.parent
STATE_PATH = VAULT / ".brain-state.json"
TICKETS_DIR = VAULT / "raw" / "tickets"
IMPORTS_DIR = VAULT / "raw" / "_imports"
PROCESSED_DIR = IMPORTS_DIR / "processed"


def load_state():
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    tmp = STATE_PATH.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE_PATH)


def yaml_escape(s):
    if s is None:
        return ""
    s = str(s).replace('"', '\\"').replace("\n", " ").strip()
    return s


def yaml_list(vals):
    if not vals:
        return "[]"
    return "[" + ", ".join(f'"{yaml_escape(v)}"' for v in vals) + "]"


def build_markdown(key, summary, status, resolution, components, sprints, description, acceptance, low_signal):
    fm = [
        "---",
        f'key: {key}',
        f'summary: "{yaml_escape(summary)}"',
        f'status: "{yaml_escape(status)}"',
        f'resolution: "{yaml_escape(resolution)}"',
        f"components: {yaml_list(components)}",
        f"sprints: {yaml_list(sprints)}",
        f"low_signal: {str(low_signal).lower()}",
        "---",
        "",
        f"# {key} — {summary}",
        "",
        "## Description",
        description.strip() if description else "_(none)_",
        "",
        "## Acceptance Criteria",
    ]
    if acceptance:
        fm.append(acceptance.strip())
    else:
        fm.append("_(none)_")
    fm.append("")
    return "\n".join(fm)


def main():
    state = load_state()
    step = state["steps"]["4"]

    # Discover imports
    import_files = sorted(
        p for p in IMPORTS_DIR.iterdir()
        if p.is_file() and p.suffix.lower() == ".csv"
    )
    if not import_files:
        # "done" with no new imports is a clean no-op (incremental routines hit this).
        if step["status"] == "done":
            print("Step 4 already done; no new CSVs in raw/_imports/. Nothing to do.")
            sys.exit(0)
        print("No CSV files in raw/_imports/", file=sys.stderr)
        sys.exit(1)

    # Re-entry from "done": treat new imports as a fresh run.
    # Cumulative counters (tickets_written, tickets_skipped, tickets_low_signal)
    # persist across runs and reflect lifetime totals; total_tickets is per-run.
    if step["status"] == "done":
        prior_runs = step.get("prior_runs", [])
        prior_runs.append({
            "completed_at": step.get("completed_at"),
            "imports": step.get("imports_discovered", []),
            "tickets_written_at_completion": step.get("tickets_written", 0),
        })
        step["prior_runs"] = prior_runs
        step["status"] = "pending"
        step["completed_at"] = None
        save_state(state)

    # First-run setup (also runs on re-entry)
    if step["status"] == "pending":
        # Count total tickets across all CSVs
        total = 0
        for fp in import_files:
            with open(fp, "r", encoding="utf-8", newline="") as f:
                r = csv.reader(f)
                next(r, None)
                for _ in r:
                    total += 1
        step["status"] = "in_progress"
        step["total_tickets"] = total
        step["imports_discovered"] = [
            {"filename": p.name, "bytes": p.stat().st_size} for p in import_files
        ]
        save_state(state)
        print(f"Total tickets to process: {total}")

    resumed_new = step.get("tickets_written", 0)
    resumed_updated = step.get("tickets_updated", 0)
    resumed_unchanged = step.get("tickets_unchanged", step.get("tickets_skipped", 0))
    resumed_low = step.get("tickets_low_signal", 0)

    print(f"Starting/resuming: new={resumed_new} updated={resumed_updated} unchanged={resumed_unchanged} low={resumed_low}")

    new_count = resumed_new
    updated = resumed_updated
    unchanged = resumed_unchanged
    low = resumed_low
    processed_since_flush = 0

    TICKETS_DIR.mkdir(parents=True, exist_ok=True)

    for fp in import_files:
        with open(fp, "r", encoding="utf-8", newline="") as f:
            r = csv.reader(f)
            header = next(r)

            def idxs(name):
                return [i for i, h in enumerate(header) if h == name]

            key_i = idxs("Issue key")[0]
            sum_i = idxs("Summary")[0]
            status_i = idxs("Status")[0]
            res_i = idxs("Resolution")[0]
            desc_i = idxs("Description")[0]
            comp_i = idxs("Components")
            sprint_i = idxs("Sprint")
            ac_i = idxs("Custom field (Acceptance Criteria)")

            for row in r:
                key = row[key_i].strip()
                if not key:
                    continue

                out_path = TICKETS_DIR / f"{key}.md"

                summary = row[sum_i]
                status = row[status_i]
                resolution = row[res_i]
                description = row[desc_i]
                components = [row[i].strip() for i in comp_i if row[i].strip()]
                sprints = [row[i].strip() for i in sprint_i if row[i].strip()]
                acceptance_parts = [row[i].strip() for i in ac_i if row[i].strip()]
                acceptance = "\n\n".join(acceptance_parts)

                ls_resolution = resolution.strip().lower() in ("duplicate", "won't do", "wont do", "won't fix", "wontfix")
                ls_empty = not description.strip()
                low_signal = ls_resolution or ls_empty

                md = build_markdown(
                    key, summary, status, resolution,
                    components, sprints, description, acceptance,
                    low_signal,
                )

                # Mirror semantics: write new, overwrite if changed, skip if identical.
                if out_path.exists():
                    existing = out_path.read_text(encoding="utf-8")
                    if existing == md:
                        unchanged += 1
                    else:
                        tmp = out_path.with_suffix(".md.tmp")
                        with open(tmp, "w", encoding="utf-8") as out:
                            out.write(md)
                        os.replace(tmp, out_path)
                        updated += 1
                        if low_signal:
                            low += 1
                else:
                    tmp = out_path.with_suffix(".md.tmp")
                    with open(tmp, "w", encoding="utf-8") as out:
                        out.write(md)
                    os.replace(tmp, out_path)
                    new_count += 1
                    if low_signal:
                        low += 1

                processed_since_flush += 1
                if processed_since_flush >= 100:
                    step["tickets_written"] = new_count
                    step["tickets_updated"] = updated
                    step["tickets_unchanged"] = unchanged
                    # keep legacy alias so older state files / readers don't break
                    step["tickets_skipped"] = unchanged
                    step["tickets_low_signal"] = low
                    step["last_processed_key"] = key
                    save_state(state)
                    processed_since_flush = 0
                    print(f"... new={new_count} updated={updated} unchanged={unchanged} low={low} (last: {key})")

    # Final flush
    step["tickets_written"] = new_count
    step["tickets_updated"] = updated
    step["tickets_unchanged"] = unchanged
    step["tickets_skipped"] = unchanged  # legacy alias
    step["tickets_low_signal"] = low
    save_state(state)

    # Move imports to processed/
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    for fp in import_files:
        dest = PROCESSED_DIR / fp.name
        if dest.exists():
            dest.unlink()
        fp.rename(dest)

    step["status"] = "done"
    from datetime import date
    step["completed_at"] = str(date.today())
    state["current_step"] = 4
    save_state(state)
    print(f"DONE: new={new_count} updated={updated} unchanged={unchanged} low_signal={low}")


if __name__ == "__main__":
    main()
