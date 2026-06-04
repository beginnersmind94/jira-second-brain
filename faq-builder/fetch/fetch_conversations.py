import os, re, json, time, html, logging, unicodedata
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import requests
from bs4 import BeautifulSoup, Comment

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOGGER = logging.getLogger("fetch_conversations")

# ---- config (HARDCODE THESE) ----
FRESHDESK_DOMAIN = "primeroedge.freshdesk.com"
FRESHDESK_API_KEY = "B8kSOvDwcS2a5rd64EA"

# Output written next to this script.
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "conversations.jsonl")

TICKET_IDS = [
    "306062","306464","306678","306944","306994","307000","307187","307374",
    "307691","307818","308535","308584","308648","308920","309206","309710",
    "309868","310324","310448","310869","310886","311098","311736","311904",
    "312195","312230","312260","312514","312896","313394","313841","313847",
    "313883","314325","314982","315242","315310","315380","315470","315496",
    "315508","315656","315731","315773","315804","315888","315936","315997",
    "316013","316219","316257","316832","317107","317524","318576","318634",
    "318670","319808","319849","319963","320105","320315","320367","320383",
    "320731",
]

PER_PAGE = 100
TIMEOUT = 30.0
MAX_RETRIES = 5
REQUEST_SPACING = 0.3
TRANSIENT = {500, 502, 503, 504}


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _retry_after(value):
    if not value:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        pass
    try:
        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return max(0.0, (dt - datetime.now(timezone.utc)).total_seconds())
    except (TypeError, ValueError):
        return None


def _next_link(link_header):
    if not link_header:
        return None
    for link in requests.utils.parse_header_links(link_header.rstrip(">").replace(">,", ">,")):
        if link.get("rel") == "next" and link.get("url"):
            return link["url"]
    return None


class FreshdeskClient:
    def __init__(self, domain, api_key):
        self.base = f"https://{domain.strip().strip('/')}/api/v2"
        self.session = requests.Session()
        self.session.auth = (api_key, "X")
        self.session.headers.update({"Accept": "application/json"})

    def _url(self, p):
        return p if p.startswith("http") else f"{self.base}/{p.lstrip('/')}"

    def get(self, p, params=None):
        url = self._url(p)
        for attempt in range(MAX_RETRIES + 1):
            time.sleep(REQUEST_SPACING)
            resp = self.session.get(url, params=params, timeout=TIMEOUT)
            if resp.status_code == 429:
                wait = _retry_after(resp.headers.get("Retry-After")) or min(60.0, 2 ** attempt)
                LOGGER.warning("429; sleeping %.1fs", wait); time.sleep(wait); continue
            if resp.status_code in TRANSIENT:
                wait = min(60.0, 2 ** attempt)
                LOGGER.warning("%d transient; sleeping %.1fs", resp.status_code, wait); time.sleep(wait); continue
            if resp.status_code == 401:
                raise RuntimeError("401 Unauthorized -- check FRESHDESK_API_KEY.")
            resp.raise_for_status()
            return resp.json(), resp
        raise RuntimeError(f"Exhausted retries for {url}")

    def get_ticket(self, tid):
        data, _ = self.get(f"/tickets/{tid}", params={"include": "requester"})
        return data if isinstance(data, dict) else {}

    def get_conversations(self, tid):
        endpoint = f"/tickets/{tid}/conversations"
        url, params = self._url(endpoint), {"per_page": PER_PAGE, "page": 1}
        out, pages, seen = [], 0, set()
        while url:
            key = f"{url}|{params}"
            if key in seen:
                break
            seen.add(key)
            data, resp = self.get(url, params=params)
            if not isinstance(data, list):
                break
            out.extend(x for x in data if isinstance(x, dict))
            pages += 1
            nxt = _next_link(resp.headers.get("Link") or resp.headers.get("link"))
            if nxt:
                url, params = nxt, None
            elif len(data) == PER_PAGE and params is not None:
                params = {"per_page": PER_PAGE, "page": params["page"] + 1}
                url = self._url(endpoint)
            else:
                url = None
        return out, pages


QUOTE_CLASS_RE = re.compile(r"(gmail_quote|gmail_attr|yahoo_quoted|moz-cite-prefix|freshdesk_quote|blockquote)", re.I)
BLOCK_TAGS = {"address","article","aside","blockquote","div","footer","h1","h2","h3","h4","h5","h6",
              "header","li","ol","p","pre","section","table","td","th","tr","ul"}
QUOTE_START_RE = re.compile(
    r"^\s*(On .{1,220}? wrote:|-{2,}\s*Original Message\s*-{2,}|"
    r"Begin forwarded message:|-{2,}\s*Forwarded message\s*-{2,})\s*$", re.I)
DISCLAIMER_RE = re.compile(
    r"(confidentiality notice|privileged and confidential|intended only for|"
    r"if you are not the intended recipient|this e-?mail and any attachments|"
    r"this message and any attachments|do not distribute|unsubscribe|tracking pixel)", re.I)
ATTACHMENT_RE = re.compile(
    r"^\s*(\[cid:.*?\]|\[image:.*?\]|\[inline image.*?\]|cid:[^\s]+|image\d+\.(png|jpe?g|gif|bmp))\s*$", re.I)


def _strip_non_printing(text):
    return "".join(c for c in text if c in "\n\t" or not unicodedata.category(c).startswith("C"))


def html_to_text(value):
    if not value:
        return ""
    soup = BeautifulSoup(str(value), "html.parser")
    for tag in soup(["script","style","noscript","meta","head","title","svg","img"]):
        tag.decompose()
    for c in soup.find_all(string=lambda t: isinstance(t, Comment)):
        c.extract()
    for tag in soup.find_all(True):
        attrs = " ".join(" ".join(v) if isinstance(v, list) else str(v) for v in tag.attrs.values())
        if tag.name == "blockquote" or QUOTE_CLASS_RE.search(attrs):
            tag.decompose()
    for br in soup.find_all("br"):
        br.replace_with("\n")
    for tag in soup.find_all(BLOCK_TAGS):
        tag.insert_before("\n"); tag.insert_after("\n")
    return html.unescape(soup.get_text("\n"))


def _strip_quote_history(text):
    kept = []
    for line in text.splitlines():
        s = line.strip()
        if QUOTE_START_RE.match(s):
            break
        if re.match(r"^\s*From:\s+.+", s, re.I):
            break
        if s.startswith(">"):
            continue
        kept.append(line)
    return "\n".join(kept)


def _drop_junk_lines(text):
    kept = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            kept.append(""); continue
        if DISCLAIMER_RE.search(s):
            break
        if ATTACHMENT_RE.match(s):
            continue
        if re.fullmatch(r"[{}\[\];:,.#\-\s]+", s):
            continue
        kept.append(line)
    return "\n".join(kept)


def _collapse_ws(text):
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return "\n".join(l.rstrip() for l in text.splitlines()).strip()


def clean_body(body_html, body_text):
    base = body_text if (body_text and body_text.strip()) else html_to_text(body_html)
    base = _strip_non_printing(base)
    base = _strip_quote_history(base)
    base = _drop_junk_lines(base)
    return _collapse_ws(base)


def full_text(body_html, body_text):
    """Lossless plain text: strips HTML structure only. No quote removal, no
    truncation, no junk-line dropping. Guarantees nothing is dropped."""
    if body_html:
        soup = BeautifulSoup(str(body_html), "html.parser")
        for tag in soup(["script", "style", "noscript", "meta", "head", "title", "svg"]):
            tag.decompose()
        for c in soup.find_all(string=lambda t: isinstance(t, Comment)):
            c.extract()
        for br in soup.find_all("br"):
            br.replace_with("\n")
        for tag in soup.find_all(BLOCK_TAGS):
            tag.insert_before("\n"); tag.insert_after("\n")
        base = html.unescape(soup.get_text("\n"))
    else:
        base = body_text or ""
    base = _strip_non_printing(base)
    return _collapse_ws(base)


def requester_label(ticket):
    r = ticket.get("requester") if isinstance(ticket.get("requester"), dict) else {}
    name, email = r.get("name"), r.get("email") or ticket.get("email")
    if name and email:
        return f"{name} <{email}>"
    return str(name or email or ticket.get("requester_id") or "customer")


def conversation_turn(entry, requester):
    private = bool(entry.get("private"))
    if private:
        role, ctype = "agent", "private_note"
    elif entry.get("incoming") is True:
        role, ctype = "customer", "reply"
    else:
        role, ctype = "agent", "reply"
    author = requester if role == "customer" else (
        entry.get("from_email") or entry.get("support_email") or f"agent:{entry.get('user_id')}")
    return {
        "role": role, "type": ctype, "author": str(author),
        "timestamp": entry.get("created_at"),
        "body_text": entry.get("body_text"),
        "body_html": entry.get("body"),
    }


def build_record(tid, ticket, conversations, pages, include_description=True):
    requester = requester_label(ticket)
    turns = []
    if include_description and ticket:
        turns.append({
            "role": "customer", "type": "description", "author": requester,
            "timestamp": ticket.get("created_at"),
            "body_text": ticket.get("description_text"),
            "body_html": ticket.get("description"),
        })
    convo = [conversation_turn(e, requester) for e in conversations]
    convo.sort(key=lambda t: str(t.get("timestamp") or ""))
    turns.extend(convo)
    return {"ticket_id": tid, "subject": (ticket or {}).get("subject"),
            "turns": turns, "turn_count": len(turns), "pages_fetched": pages}


def main():
    domain = FRESHDESK_DOMAIN.strip()
    api_key = FRESHDESK_API_KEY.strip()
    assert domain and "PASTE_YOUR" not in api_key and api_key, \
        "Set FRESHDESK_DOMAIN and FRESHDESK_API_KEY at the top of this script."

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    client = FreshdeskClient(domain, api_key)
    fetched, skipped, errors = 0, 0, []

    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        for i, tid in enumerate(TICKET_IDS, 1):
            try:
                ticket = client.get_ticket(tid)
                conversations, pages = client.get_conversations(tid)
                rec = build_record(tid, ticket, conversations, pages, include_description=True)
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
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

    print(json.dumps({"total": len(TICKET_IDS), "fetched": fetched, "skipped": skipped,
                      "output": OUT_PATH, "errors": errors}, indent=2))


if __name__ == "__main__":
    main()
