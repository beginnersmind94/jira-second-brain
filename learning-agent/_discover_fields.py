"""Hit /rest/api/3/field and surface only the fields we care about."""
import base64
import os
import sys

import httpx
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
load_dotenv()

BASE = os.getenv("JIRA_BASE_URL", "").rstrip("/")
EMAIL = os.getenv("JIRA_EMAIL", "")
TOKEN = os.getenv("JIRA_API_TOKEN", "")
auth = "Basic " + base64.b64encode(f"{EMAIL}:{TOKEN}".encode()).decode()

r = httpx.get(
    f"{BASE}/rest/api/3/field",
    headers={"Authorization": auth, "Accept": "application/json"},
    timeout=30,
)
r.raise_for_status()
fields = r.json()

INTERESTING = ["release notes", "module", "acceptance criteria", "epic", "uat", "root cause", "story points", "freshdesk", "district"]

hits = []
for f in fields:
    name = f.get("name") or ""
    fid = f.get("id") or ""
    custom = f.get("custom", False)
    if any(needle in name.lower() for needle in INTERESTING):
        hits.append((name, fid, custom, f.get("schema", {}).get("type", "?")))

hits.sort()
print(f"--- {len(hits)} matching fields out of {len(fields)} total ---\n")
for name, fid, custom, ftype in hits:
    tag = "[custom]" if custom else "[system]"
    print(f"  {tag} {fid:30s} type={ftype:15s} name={name}")
