"""
Fetch + clean an ad-hoc list of Freshdesk tickets for analysis.

Reuses the proven client and renderers from fetch_conversations.py. For each
ticket it pulls the ticket + all conversation pages, then renders every turn
to lossless plain text via full_text() (strips HTML structure only -- no quote
removal, no truncation, no junk-line dropping). This matches the matured
"clean for analysis" decision: nothing substantive is dropped, the LLM parses
the result.

Outputs (next to this script):
    <prefix>.json   -- CLEANED: array of records, each turn has a `text` field.
    <prefix>.jsonl  -- RAW lossless: one record per line, turns keep
                       body_text + body_html (pipeline parity / safety net).

Usage:
    python fetch_batch.py            # uses TICKET_IDS below, prefix conversations_batch
    python fetch_batch.py <prefix>   # override output prefix
"""
import os
import sys
import json

import requests

from fetch_conversations import (
    FRESHDESK_DOMAIN, FRESHDESK_API_KEY, FreshdeskClient,
    build_record, full_text,
)

HERE = os.path.dirname(os.path.abspath(__file__))

# Ad-hoc batch supplied for analysis.
TICKET_IDS = [
    "321240", "320558", "320501", "319912", "319694", "319511", "319505",
    "319142", "319079", "318890", "318874", "318729", "318682", "318653",
    "318648", "318599", "318414", "318389", "318264", "317212", "316608",
    "316604", "315980", "315737", "315535", "315525", "315178", "315109",
    "314864", "314514", "313716", "313689", "313312", "313240", "313038",
    "312950", "312922", "311759", "311738", "311634", "311583", "311415",
    "310398", "310339", "309961", "309367", "308796", "308730", "308370",
    "307844", "307774", "307775", "307330", "306656", "306404", "306217",
    "305234", "304857", "304575", "304571", "304367", "304242", "304177",
    "303897", "301377", "300122", "299245", "298909", "298216", "297884",
    "296709", "295567", "295542", "294917", "294887", "291743", "291735",
    "291477", "291385", "291257", "291201", "291200", "290930", "290925",
    "290909", "289964", "289958", "288917", "288469", "287918", "287828",
    "315146", "302460",
]


def dedupe(ids):
    seen, out = set(), []
    for t in ids:
        t = str(t).strip()
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out


def clean_record(rec):
    """Project a raw build_record() result to a cleaned, analysis-ready shape."""
    turns = []
    for i, t in enumerate(rec.get("turns", [])):
        turns.append({
            "index": i,
            "role": t.get("role"),
            "type": t.get("type"),
            "author": t.get("author"),
            "timestamp": t.get("timestamp"),
            "text": full_text(t.get("body_html"), t.get("body_text")),
        })
    return {
        "ticket_id": rec.get("ticket_id"),
        "subject": rec.get("subject"),
        "turn_count": rec.get("turn_count"),
        "pages_fetched": rec.get("pages_fetched"),
        "turns": turns,
    }


def main():
    prefix = sys.argv[1] if len(sys.argv) > 1 else "conversations_batch"
    out_json = os.path.join(HERE, f"{prefix}.json")
    out_jsonl = os.path.join(HERE, f"{prefix}.jsonl")

    ticket_ids = dedupe(TICKET_IDS)
    client = FreshdeskClient(FRESHDESK_DOMAIN.strip(), FRESHDESK_API_KEY.strip())

    cleaned, fetched, skipped, errors = [], 0, 0, []
    with open(out_jsonl, "w", encoding="utf-8") as raw_fh:
        for i, tid in enumerate(ticket_ids, 1):
            try:
                ticket = client.get_ticket(tid)
                conversations, pages = client.get_conversations(tid)
                rec = build_record(tid, ticket, conversations, pages, include_description=True)
                raw_fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                cleaned.append(clean_record(rec))
                fetched += 1
                print(f"[{i}/{len(ticket_ids)}] {tid} -> {rec['turn_count']} turns")
            except requests.HTTPError as exc:
                code = exc.response.status_code if exc.response is not None else None
                reason = "not_found" if code == 404 else f"http_{code}"
                skipped += 1
                errors.append({"ticket_id": tid, "reason": reason})
                print(f"[{i}/{len(ticket_ids)}] {tid} skipped: {reason}")
            except Exception as exc:  # noqa: BLE001
                skipped += 1
                errors.append({"ticket_id": tid, "reason": str(exc)})
                print(f"[{i}/{len(ticket_ids)}] {tid} skipped: {exc}")

    with open(out_json, "w", encoding="utf-8") as fh:
        json.dump(cleaned, fh, ensure_ascii=False, indent=2)

    print(json.dumps({
        "requested": len(TICKET_IDS), "unique": len(ticket_ids),
        "fetched": fetched, "skipped": skipped,
        "json": out_json, "jsonl": out_jsonl, "errors": errors,
    }, indent=2))


if __name__ == "__main__":
    main()
