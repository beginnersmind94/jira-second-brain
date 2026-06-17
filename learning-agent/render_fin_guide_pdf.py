"""Render the tightened Financials 2.0 guide markdown to a new-version PDF using
the PRODUCT's own pdf_export (pymupdf Story API + its print CSS) — same pipeline
as Learning Studio's "Download PDF". Strips internal <!-- Source --> citations
(customer-facing) and de-emojis callout markers (pymupdf fonts lack emoji glyphs;
the bold/blockquote callout labels carry the meaning).

Prepends a branded cover page matching the original Financials 2.0 Onboarding
style: dark navy gradient, letter-spaced header, large bold title, italic gold
subtitle, pill badges, and footer."""
import re
import sys
from pathlib import Path

LA = Path(r"C:/Users/rahul.mehta/Downloads/Financials-Documentation-KT/jira-brain/learning-agent")
sys.path.insert(0, str(LA))
import pdf_export  # product's renderer; imports only io/re/pymupdf
import pymupdf

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

# 3) Strip the cover block (H1 title through first ---).
#    The cover page visual handles this; we don't repeat it as body text.
clean = re.sub(r"\A.*?^---[ \t]*$\n?", "", clean, count=1, flags=re.S | re.M)

# 4) Markdown -> HTML (tables/lists/blockquotes via 'extra').
try:
    import markdown
    html = markdown.markdown(clean, extensions=["extra", "sane_lists", "toc"])
except Exception as exc:  # pragma: no cover
    raise SystemExit(f"markdown lib unavailable: {exc}")

# 5) Render content through the product's PDF export.
content_bytes = pdf_export.render_html_to_pdf(html, banner=None)


def _draw_cover(page: pymupdf.Page) -> None:
    """Draw the branded cover page matching the Financials 2.0 Onboarding style."""
    W, H = 612, 792

    # --- Background: dark navy-blue gradient, top -> teal-blue bottom ---
    # Use enough bands that each is < 1 pixel at typical viewing resolution.
    BANDS = 600
    top_c = (0x0d / 255, 0x2d / 255, 0x48 / 255)  # #0d2d48
    bot_c = (0x18 / 255, 0x51 / 255, 0x70 / 255)  # #185170
    for i in range(BANDS):
        t = i / BANDS
        r = top_c[0] + t * (bot_c[0] - top_c[0])
        g = top_c[1] + t * (bot_c[1] - top_c[1])
        b = top_c[2] + t * (bot_c[2] - top_c[2])
        y0 = i * H / BANDS
        y1 = (i + 1) * H / BANDS + 0.5  # +0.5 to close sub-pixel seams
        page.draw_rect(pymupdf.Rect(0, y0, W, y1), color=None, fill=(r, g, b))

    # --- "FINANCIALS 2.0 · INTERNAL TRAINING" (letter-spaced, small caps style) ---
    page.insert_text(
        pymupdf.Point(54, 136),
        "F I N A N C I A L S   2 . 0   ·   I N T E R N A L   T R A I N I N G",
        fontsize=8.5, fontname="helv", color=(0.68, 0.82, 0.90),
    )

    # --- "Onboarding," (large heavy bold, white) ---
    page.insert_text(
        pymupdf.Point(54, 262),
        "Onboarding,",
        fontsize=68, fontname="hebo", color=(1.0, 1.0, 1.0),
    )

    # --- "Without the Yawn" (bold italic, gold/orange) ---
    page.insert_text(
        pymupdf.Point(54, 334),
        "Without the Yawn",
        fontsize=52, fontname="hebi", color=(1.0, 0.65, 0.08),
    )

    # --- Description paragraph (em dash replaced: helv lacks U+2014) ---
    desc = [
        "A jobs-to-be-done guide for the district finance and child-nutrition",
        "staff bringing Financials 2.0 online, and for the Cybersoft",
        "implementers walking them through it.",
    ]
    for i, line in enumerate(desc):
        page.insert_text(
            pymupdf.Point(54, 410 + i * 22),
            line, fontsize=13, fontname="helv", color=(0.79, 0.89, 0.95),
        )

    # --- Pill badges ---
    def _pill(x0: float, y0: float, x1: float, y1: float, label: str) -> None:
        rect = pymupdf.Rect(x0, y0, x1, y1)
        page.draw_rect(rect, color=(0.70, 0.84, 0.92), fill=None, width=1.0, radius=0.42)
        ty = y0 + (y1 - y0) * 0.70
        page.insert_text(
            pymupdf.Point(x0 + 14, ty),
            label, fontsize=10, fontname="helv", color=(0.79, 0.89, 0.95),
        )

    _pill(54, 490, 248, 516, "12 Jobs to be Done")
    _pill(262, 490, 436, 516, "90-Day Cheat Sheet")

    # --- Footer rule ---
    page.draw_line(
        pymupdf.Point(54, 740), pymupdf.Point(558, 740),
        color=(0.40, 0.58, 0.72), width=0.5,
    )

    # --- Footer text ---
    page.insert_text(
        pymupdf.Point(54, 760),
        "SchoolCafe  ·  Cybersoft Implementation Team  ·  June 2026 Edition",
        fontsize=9, fontname="helv", color=(0.56, 0.74, 0.85),
    )


# 6) Merge: cover page + content pages.
content_doc = pymupdf.open(stream=content_bytes, filetype="pdf")
final_doc = pymupdf.open()
cover = final_doc.new_page(width=612, height=792)
_draw_cover(cover)
final_doc.insert_pdf(content_doc)

pdf = final_doc.tobytes(deflate=True)
OUT.write_bytes(pdf)

# 7) Verify (ASCII-safe terminal print).
doc2 = pymupdf.open(stream=pdf, filetype="pdf")
p1_snippet = doc2[1].get_text("text")[:200].replace("\n", " ").encode("ascii", "replace").decode()
print(f"WROTE {OUT}")
print(f"  bytes={len(pdf)}  pages={len(doc2)}")
print(f"  page2 snippet: {p1_snippet}")
hits = [i + 1 for i in range(len(doc2)) if "what's coming next" in doc2[i].get_text("text").lower()]
print(f"  'Whats Coming Next' appendix on page(s): {hits or 'NOT FOUND'}")
