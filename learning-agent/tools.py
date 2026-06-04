"""Two tools the agent can call: read a PDF, search Jira tickets."""
import csv
import os
from pathlib import Path

import pymupdf
from langchain_core.tools import tool

DATA_DIR = Path(__file__).parent / "data"
TICKETS_CSV = DATA_DIR / "tickets.csv"


@tool
def read_pdf(file_path: str) -> str:
    """Extract the full text of a PDF file.

    Use this when you are given a PDF and need to see what it says before
    you can summarize, analyze, or fact-check it. Always call this first
    when a PDF path is provided — you cannot reason about a PDF you have
    not read.

    Args:
        file_path: Absolute or relative path to the PDF on disk.

    Returns:
        The extracted text of every page concatenated, or an error string
        starting with "ERROR:" if the file can't be opened.
    """
    p = Path(file_path)
    if not p.is_absolute():
        p = (DATA_DIR / p).resolve()
    if not p.exists():
        return f"ERROR: file not found at {p}"
    try:
        doc = pymupdf.open(p)
    except Exception as e:
        return f"ERROR: could not open PDF: {e}"

    pages = []
    for i, page in enumerate(doc, start=1):
        pages.append(f"--- page {i} ---\n{page.get_text()}")
    doc.close()
    return "\n\n".join(pages)


def _load_tickets():
    if not TICKETS_CSV.exists():
        return []
    with open(TICKETS_CSV, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@tool
def search_jira(query: str) -> str:
    """Search the Jira ticket database for tickets relevant to a claim.

    Use this when you find a specific claim, feature, or behavior mentioned
    in a PDF and want to verify whether there is a Jira ticket that confirms
    it. Pass the most specific phrase from the PDF (a feature name, a
    workflow step, an exact UI label). Single keywords return noisy results.

    Args:
        query: A short phrase describing the claim you want to verify.

    Returns:
        Up to 5 matching tickets formatted as "KEY | Summary | snippet",
        or "No tickets matched." if nothing scores.
    """
    tickets = _load_tickets()
    if not tickets:
        return "ERROR: no tickets indexed (data/tickets.csv missing)."

    terms = [t.lower() for t in query.split() if len(t) > 2]
    if not terms:
        return "ERROR: query too short — pass a multi-word phrase."

    scored = []
    for row in tickets:
        haystack = " ".join([
            row.get("Summary", ""),
            row.get("Release Notes", ""),
            row.get("Acceptance Criteria", ""),
        ]).lower()
        score = sum(haystack.count(t) for t in terms)
        if score > 0:
            scored.append((score, row))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:5]
    if not top:
        return "No tickets matched."

    lines = []
    for score, row in top:
        ac = (row.get("Acceptance Criteria") or "").replace("\n", " ")[:200]
        lines.append(
            f"{row['Key']} (score {score}) | {row['Summary']}\n  AC: {ac}"
        )
    return "\n\n".join(lines)


tools = [read_pdf, search_jira]
