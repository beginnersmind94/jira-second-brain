"""Fetch Freshdesk conversations for the Ingredients ticket set and render a
lossless digest. Mirrors fetch_conversations.py (Menu Cycles) but for the
Ingredients CSV. Raw bodies are preserved; the LLM parses the digest itself.

Outputs (next to this script):
  - conversations_ingredients.jsonl   (one record per ticket, raw bodies kept)
  - conversations_ingredients_digest.txt  (human/LLM-readable, lossless text)
"""
import os, json
import requests

# Reuse the proven client + lossless text renderer from the Menu Cycles fetcher.
from fetch_conversations import (
    FRESHDESK_DOMAIN, FRESHDESK_API_KEY, FreshdeskClient,
    build_record, full_text,
)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_JSONL = os.path.join(HERE, "conversations_ingredients.jsonl")
OUT_DIGEST = os.path.join(HERE, "conversations_ingredients_digest.txt")

TICKET_IDS = [
    "290768","294367","294719","294965","295021","295733","295941","296061",
    "297295","298870","299089","299668","300604","300961","301629","302221",
    "304096","304228","304346","304911","305369","305518","305525","305626",
    "305896","306125","306166","306236","306396","306400","306591","306632",
    "307347","307681","308078","308099","308247","308457","308605","308695",
    "309006","309277","309288","309341","309390","309869","310141","310433",
    "311797","311854","312024","312257","312848","312982","313237","313596",
    "313612","313704","313942","314306","314317","314572","314610","314911",
    "315204","315348","315360","315399","315439","315461","316753","317124",
    "317589","317596","317725","318086","318454","318587","318917","319087",
    "320442","320746",
]


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
    client = FreshdeskClient(FRESHDESK_DOMAIN.strip(), FRESHDESK_API_KEY.strip())
    records, fetched, skipped, errors = [], 0, 0, []
    with open(OUT_JSONL, "w", encoding="utf-8") as fh:
        for i, tid in enumerate(TICKET_IDS, 1):
            try:
                ticket = client.get_ticket(tid)
                conversations, pages = client.get_conversations(tid)
                rec = build_record(tid, ticket, conversations, pages, include_description=True)
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                records.append(rec)
                fetched += 1
                print(f"[{i}/{len(TICKET_IDS)}] {tid} -> {rec['turn_count']} turns")
            except requests.HTTPError as exc:
                code = exc.response.status_code if exc.response is not None else None
                reason = "not_found" if code == 404 else f"http_{code}"
                skipped += 1; errors.append({"ticket_id": tid, "reason": reason})
                print(f"[{i}/{len(TICKET_IDS)}] {tid} skipped: {reason}")
            except Exception as exc:
                skipped += 1; errors.append({"ticket_id": tid, "reason": str(exc)})
                print(f"[{i}/{len(TICKET_IDS)}] {tid} skipped: {exc}")

    with open(OUT_DIGEST, "w", encoding="utf-8") as fh:
        fh.write(render_digest(records))

    print(json.dumps({"total": len(TICKET_IDS), "fetched": fetched, "skipped": skipped,
                      "jsonl": OUT_JSONL, "digest": OUT_DIGEST, "errors": errors}, indent=2))


if __name__ == "__main__":
    main()
