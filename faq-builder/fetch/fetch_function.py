"""
Generic Freshdesk fetcher for a single PrimeroEdge function.

Reads a ticket CSV (first column = Ticket ID, with a header row), pulls each
ticket + its conversations from Freshdesk, and writes a lossless JSONL plus a
human/LLM-readable digest. Reuses the proven client and renderers from
fetch_conversations.py / fetch_ingredients.py (raw body_text + body_html kept;
no regex cleaning — the LLM parses the digest).

Usage:
    python fetch_function.py "<tickets.csv>" <out_prefix>

Outputs (next to this script):
    <out_prefix>.jsonl
    <out_prefix>_digest.txt
"""
import os
import csv
import json
import sys

import requests

from fetch_conversations import (
    FRESHDESK_DOMAIN, FRESHDESK_API_KEY, FreshdeskClient,
    build_record, full_text,
)

HERE = os.path.dirname(os.path.abspath(__file__))


def read_ticket_ids(csv_path):
    ids = []
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.reader(fh)
        header = next(reader, None)  # skip header row
        for row in reader:
            if not row:
                continue
            tid = (row[0] or "").strip()
            if tid and tid.isdigit():
                ids.append(tid)
    # de-dupe, preserve order
    seen, out = set(), []
    for t in ids:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def render_digest(records):
    bar = "=" * 90
    out = []
    for rec in records:
        out.append(bar)
        out.append(f"TICKET {rec['ticket_id']}  |  {rec.get('subject') or '(no subject)'}")
        out.append(bar)
        out.append("")
        for i, t in enumerate(rec.get("turns", [])):
            text = full_text(t.get("body_html"), t.get("body_text"))
            header = (f"--- turn {i} [{t.get('role')}/{t.get('type')}] "
                      f"{t.get('author')}  {t.get('timestamp')} ---")
            out.append(header)
            out.append(text if text.strip() else "(empty)")
            out.append("")
        out.append("")
    return "\n".join(out)


def main():
    if len(sys.argv) < 3:
        print("Usage: python fetch_function.py <tickets.csv> <out_prefix>", file=sys.stderr)
        sys.exit(2)
    csv_path, prefix = sys.argv[1], sys.argv[2]
    out_jsonl = os.path.join(HERE, f"{prefix}.jsonl")
    out_digest = os.path.join(HERE, f"{prefix}_digest.txt")

    ticket_ids = read_ticket_ids(csv_path)
    client = FreshdeskClient(FRESHDESK_DOMAIN.strip(), FRESHDESK_API_KEY.strip())
    records, fetched, skipped, errors = [], 0, 0, []

    with open(out_jsonl, "w", encoding="utf-8") as fh:
        for i, tid in enumerate(ticket_ids, 1):
            try:
                ticket = client.get_ticket(tid)
                conversations, pages = client.get_conversations(tid)
                rec = build_record(tid, ticket, conversations, pages, include_description=True)
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                records.append(rec)
                fetched += 1
                print(f"[{i}/{len(ticket_ids)}] {tid} -> {rec['turn_count']} turns")
            except requests.HTTPError as exc:
                code = exc.response.status_code if exc.response is not None else None
                reason = "not_found" if code == 404 else f"http_{code}"
                skipped += 1; errors.append({"ticket_id": tid, "reason": reason})
                print(f"[{i}/{len(ticket_ids)}] {tid} skipped: {reason}")
            except Exception as exc:  # noqa: BLE001
                skipped += 1; errors.append({"ticket_id": tid, "reason": str(exc)})
                print(f"[{i}/{len(ticket_ids)}] {tid} skipped: {exc}")

    with open(out_digest, "w", encoding="utf-8") as fh:
        fh.write(render_digest(records))

    print(json.dumps({"csv": csv_path, "total": len(ticket_ids), "fetched": fetched,
                      "skipped": skipped, "jsonl": out_jsonl, "digest": out_digest,
                      "errors": errors}, indent=2))


if __name__ == "__main__":
    main()
