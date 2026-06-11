"""Render the tightened Financials 2.0 guide markdown to a new-version PDF using
the PRODUCT's own pdf_export (pymupdf Story API + its print CSS) — same pipeline
as Learning Studio's "Download PDF". Strips internal <!-- Source --> citations
(customer-facing) and de-emojis callout markers (pymupdf fonts lack emoji glyphs;
the bold/blockquote callout labels carry the meaning)."""
import re
import sys
from pathlib import Path

LA = Path(r"C:/Users/rahul.mehta/Downloads/Financials-Documentation-KT/jira-brain/learning-agent")
sys.path.insert(0, str(LA))
import pdf_export  # product's renderer; imports only io/re/pymupdf

MD = LA / "docs" / "FINANCIALS-2.0-GUIDE-v2-TIGHT.md"
OUT = Path(r"C:/Users/rahul.mehta/Downloads/Financials_2.0_Onboarding_Training_Guide_v2.pdf")

if not MD.exists():
    raise SystemExit(f"tightened guide not found yet: {MD}")

md_text = MD.read_text(encoding="utf-8")

# 1) Strip internal grounding citations + any other HTML comments (customer-facing).
clean = re.sub(r"<!--\s*Source:.*?-->", "", md_text, flags=re.S)
clean = re.sub(r"<!--.*?-->", "", clean, flags=re.S)

# 2) De-emoji callout markers -> the bold labels / blockquote borders carry meaning.
for e in ("🔧", "⚠️", "⚠", "🔴", "🟢", "✅", "❌", "📌", "💡", "📋", "🟡"):
    clean = clean.replace(e, "")
clean = clean.replace("→", "->").replace("•", "-").replace("’", "'").replace("“", '"').replace("”", '"')

# 3) Markdown -> HTML (tables/lists/blockquotes via 'extra'); fall back to a minimal converter.
try:
    import markdown
    html = markdown.markdown(clean, extensions=["extra", "sane_lists", "toc"])
except Exception as exc:  # pragma: no cover
    raise SystemExit(f"markdown lib unavailable: {exc}")

# 4) Render through the product's PDF export.
pdf = pdf_export.render_html_to_pdf(html, banner=None)
OUT.write_bytes(pdf)

# 5) Verify.
import pymupdf
doc = pymupdf.open(OUT)
print(f"WROTE {OUT}")
print(f"  bytes={len(pdf)}  pages={len(doc)}")
print(f"  page1: {doc[0].get_text('text')[:240].replace(chr(10),' ')}")
hits = [i + 1 for i in range(len(doc)) if "what's coming next" in doc[i].get_text("text").lower()]
print(f"  'What's Coming Next' appendix on page(s): {hits or 'NOT FOUND'}")
