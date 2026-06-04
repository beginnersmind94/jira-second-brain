"""Generate workflow-langchain.jpg — explainable to a fresh reader.

Iterated for clarity:
  - Title + one-line explanation at top
  - Plain-English labels throughout
  - Only ONE explanatory sub-box (quality-check criteria) — the trust mechanism
  - Short artifact labels (no overlap)
  - Retry loop label moved well above the node row
"""
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch

OUT = Path(__file__).resolve().parents[1] / "workflow-langchain.jpg"

INK = "#1f2933"
MUTED = "#5b6470"
ORANGE_FILL = "#fbe4cf"
ORANGE_EDGE = "#d27c3a"
ORANGE_INK = "#9a4a14"
GREEN_FILL = "#d2efd6"
GREEN_EDGE = "#5da06a"
BEIGE_FILL = "#e9e1d3"
BEIGE_EDGE = "#a09786"
SCRATCH_FILL = "#f5efe4"
GROUP_EDGE = "#b9c0c9"
BLUE_FILL = "#dde6f5"
BLUE_EDGE = "#5b7bb3"
BLUE_INK = "#2a3f6b"
PURPLE_FILL = "#ece0f0"
PURPLE_EDGE = "#7a4e8c"
RED_EDGE = "#b21f2d"

W, H = 110.0, 95.0
fig, ax = plt.subplots(figsize=(17.5, 15))
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor("#ffffff")


def group_box(x, y, w, h, title, subtitle):
    rect = mpatches.FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.6,rounding_size=1.2",
        linewidth=1.4, edgecolor=GROUP_EDGE, facecolor="none", linestyle=(0, (5, 4)),
    )
    ax.add_patch(rect)
    ax.text(x + 1.8, y + h - 1.5, title, fontsize=14, fontweight="bold",
            color=INK, va="top", ha="left")
    ax.text(x + 1.8, y + h - 4.0, subtitle, fontsize=9.5, color=MUTED, va="top",
            ha="left", style="italic")


def tile(x, y, w, h, label, sublabel, fill, edge, text_color=INK,
         title_size=12, sub_size=9, weight="bold"):
    rect = mpatches.FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.0",
        linewidth=1.8, edgecolor=edge, facecolor=fill,
    )
    ax.add_patch(rect)
    if sublabel:
        ax.text(x + w / 2, y + h / 2 + 1.3, label, fontsize=title_size, fontweight=weight,
                color=text_color, ha="center", va="center")
        ax.text(x + w / 2, y + h / 2 - 1.5, sublabel, fontsize=sub_size, color=text_color,
                ha="center", va="center")
    else:
        ax.text(x + w / 2, y + h / 2, label, fontsize=title_size, fontweight=weight,
                color=text_color, ha="center", va="center")


def arrow(x1, y1, x2, y2, label=None, dx=0, dy=0, curve=0.0, color=MUTED, lw=1.6,
          label_color=INK):
    style = "arc3,rad=" + str(curve) if curve else "arc3"
    a = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="-|>", mutation_scale=18, linewidth=lw, color=color,
        connectionstyle=style, shrinkA=4, shrinkB=4,
    )
    ax.add_patch(a)
    if label:
        mx, my = (x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy
        ax.text(
            mx, my, label, fontsize=10, color=label_color, ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor="none"),
        )


# ────────── TITLE ──────────
ax.text(W / 2, 92, "How a Jira-driven guide update works",
        fontsize=20, fontweight="bold", color=INK, ha="center", va="center")
ax.text(W / 2, 88.5,
        "User drops a PDF guide. The system finds Jira tickets that affected it, drafts edits, "
        "self-checks them, and the user approves each one. Out: a revised PDF.",
        fontsize=10.5, color=MUTED, ha="center", va="center", style="italic")


# ────────── TOP: Inputs ──────────
group_box(4, 70, W - 8, 15, "Inputs",
          "What the system reads in to do its job")

tile(8, 73, 28, 8, "Past Jira tickets",
     "All modules · all shipped work", GREEN_FILL, GREEN_EDGE,
     title_size=12, sub_size=9.5)

tile(42, 73, 28, 8, "Searchable ticket index",
     "Built once across all modules", PURPLE_FILL, PURPLE_EDGE,
     title_size=12, sub_size=9.5)

tile(76, 73, 28, 8, "Source guide (PDF)",
     "Dropped by the user", GREEN_FILL, GREEN_EDGE,
     title_size=12, sub_size=9.5)

arrow(36, 77, 42, 77, "indexed", dx=0, dy=1.2)

# Structured metadata inventory — three buckets — hanging off "Past Jira tickets" (left-aligned, narrow)
ax.annotate(
    "Ticket metadata\n"
    "──────────────\n"
    "Today:    module · resolution · date · RN req\n"
    "Next * :  linked tickets · components\n"
    "Unused:   sprint · story type · priority · labels",
    xy=(15, 73), xytext=(2.5, 66),
    fontsize=8, color=MUTED, ha="left", va="top", family="monospace",
    bbox=dict(boxstyle="round,pad=0.45", facecolor="#fffaf0", edgecolor=GREEN_EDGE,
             linewidth=1, linestyle=(0, (3, 3))),
    arrowprops=dict(arrowstyle="-", color=GREEN_EDGE, linestyle=(0, (2, 2)), lw=1),
)
# Footnote for the asterisk on Find tickets node + the metadata callout
ax.text(W / 2, 0.5,
        "*  proposed engineering work — diagram shows the design, code not yet built",
        fontsize=8.5, color=MUTED, ha="center", va="bottom", style="italic")


# ────────── MIDDLE: User · Pipeline · Output ──────────
user_x, user_y, user_w, user_h = 4, 32, 15, 14
out_x, out_y, out_w, out_h = 91, 32, 15, 14

# Pipeline tile
backend_x, backend_y, backend_w, backend_h = 23, 18, 65, 45
rect = mpatches.FancyBboxPatch(
    (backend_x, backend_y), backend_w, backend_h,
    boxstyle="round,pad=0.4,rounding_size=1.2",
    linewidth=2.2, edgecolor=ORANGE_EDGE, facecolor=ORANGE_FILL,
)
ax.add_patch(rect)
ax.text(backend_x + backend_w / 2, backend_y + backend_h - 2.5, "AI pipeline",
        fontsize=14, fontweight="bold", color=ORANGE_INK, ha="center", va="top")
ax.text(backend_x + backend_w / 2, backend_y + backend_h - 5.0,
        "Four stages, plus a retry loop if a draft fails the quality check",
        fontsize=9.5, color=ORANGE_INK, ha="center", va="top", style="italic")

# Four stages — give them more room, fuller sublabels (no companion sub-box anymore)
node_h = 8
node_w = 13.5
node_gap = 2.0
node_y = backend_y + backend_h - 21
nodes = [
    ("1. Find tickets", "4 filters · search index\n· follow links*", BLUE_FILL, BLUE_EDGE),
    ("2. Draft edits", "AI proposes\nbefore / after edits", ORANGE_FILL, ORANGE_EDGE),
    ("3. Quality check", "verify each edit\nbefore it's shown", PURPLE_FILL, PURPLE_EDGE),
    ("4. Build new doc", "apply approved edits,\nrender PDF", BEIGE_FILL, BEIGE_EDGE),
]
total_node_w = 4 * node_w + 3 * node_gap
node_x_start = backend_x + (backend_w - total_node_w) / 2
draft_node_x = node_x_start + 1 * (node_w + node_gap)
check_node_x = node_x_start + 2 * (node_w + node_gap)
for i, (name, sub, fill, edge) in enumerate(nodes):
    nx = node_x_start + i * (node_w + node_gap)
    tile(nx, node_y, node_w, node_h, name, sub, fill, edge,
         title_size=11, sub_size=8.5, weight="bold")
    if i < 3:
        ax.annotate("", xy=(nx + node_w + node_gap, node_y + node_h / 2),
                    xytext=(nx + node_w, node_y + node_h / 2),
                    arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.3))
        if i == 2:
            ax.text((nx + node_w + (nx + node_w + node_gap)) / 2,
                    node_y + node_h / 2 + 1.6, "pass", fontsize=9, color=INK,
                    ha="center", va="bottom",
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none"))

# RETRY EDGE — label is well above the node row to avoid overlap
check_cx = check_node_x + node_w / 2
draft_cx = draft_node_x + node_w / 2
back_arrow = FancyArrowPatch(
    (check_cx, node_y + node_h),
    (draft_cx, node_y + node_h),
    arrowstyle="-|>", mutation_scale=20, linewidth=1.8, color=RED_EDGE,
    connectionstyle="arc3,rad=-0.55", shrinkA=4, shrinkB=4,
)
ax.add_patch(back_arrow)
ax.text((check_cx + draft_cx) / 2, node_y + node_h + 5.6,
        "if check fails → AI retries with the failure reason for each edit (≤ 3 tries)",
        fontsize=9.5, fontweight="bold", color=RED_EDGE, ha="center", va="center",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor=RED_EDGE, linewidth=1))

# After-3-tries branch: dropped + logged
drop_arrow = FancyArrowPatch(
    (check_node_x + node_w, node_y + 1.5),
    (check_node_x + node_w + 5, node_y - 1),
    arrowstyle="-|>", mutation_scale=14, linewidth=1.3, color=RED_EDGE,
    connectionstyle="arc3,rad=-0.2", shrinkA=2, shrinkB=2,
)
ax.add_patch(drop_arrow)
ax.text(check_node_x + node_w + 5.5, node_y - 1.5,
        "after 3 fails →\ndropped + logged",
        fontsize=8.5, color=RED_EDGE, ha="left", va="top", style="italic",
        bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="none"))

# ONE sub-box: quality-check criteria (the novel trust mechanism) — stacked single column
sub_y = backend_y + 2
sub_h = 12
sub_w = backend_w - 8
sub_x = backend_x + 4
sub = mpatches.FancyBboxPatch(
    (sub_x, sub_y), sub_w, sub_h,
    boxstyle="round,pad=0.3,rounding_size=0.6",
    linewidth=1.2, edgecolor=PURPLE_EDGE, facecolor="white", linestyle=(0, (3, 3)),
)
ax.add_patch(sub)
ax.text(sub_x + sub_w / 2, sub_y + sub_h - 0.7,
        "What the quality check verifies (for every proposed edit)",
        fontsize=10, fontweight="bold", color=PURPLE_EDGE, va="top", ha="center")
checks = [
    "Quote is real — the AI's 'before' text exists verbatim in the source",
    "Nothing fabricated — every claim traces to a ticket or guide section",
    "Nothing important dropped — the AI didn't silently remove a step",
    "Cited the right source type — guide → changelog → ticket precedence",
]
for i, c in enumerate(checks):
    cx = sub_x + 3
    cy = sub_y + sub_h - 3.2 - i * 1.95
    ax.text(cx, cy, "·  " + c, fontsize=9.5, color=INK, va="top", ha="left")

# Arrow from Quality-check node down to its sub-box — thicker so the link reads clearly
arrow(check_cx, node_y, check_cx, sub_y + sub_h,
      label="criteria below ↓", dx=0, dy=0.2,
      color=PURPLE_EDGE, lw=2.2, label_color=PURPLE_EDGE)

# User tile
tile(user_x, user_y, user_w, user_h, "User",
     "drops PDF\npicks module\nreviews edits",
     BEIGE_FILL, BEIGE_EDGE, title_size=13, sub_size=9.5)
# Output tile
tile(out_x, out_y, out_w, out_h, "Output",
     "revised PDF\nready to download",
     BEIGE_FILL, BEIGE_EDGE, title_size=13, sub_size=9.5)


# ────────── BOTTOM: Files saved during a run ──────────
group_box(4, 1, W - 8, 14, "Files saved during a run",
          "Persisted to disk so you can audit or debug what happened")
artifacts = [
    "Uploaded PDF", "Guide as text", "Candidate tickets",
    "Proposed edits", "User decisions", "Revised text",
    "Revised PDF", "AI step trace", "Per-edit log",
]
tw2 = 10.5
th2 = 4.2
gap2 = 0.8
total_arts_w = len(artifacts) * tw2 + (len(artifacts) - 1) * gap2
ax_x = (W - total_arts_w) / 2
y2 = 3.5
for i, name in enumerate(artifacts):
    x = ax_x + i * (tw2 + gap2)
    tile(x, y2, tw2, th2, name, "", SCRATCH_FILL, BEIGE_EDGE, title_size=9.5, weight="bold")


# ────────── USER-FACING ARROWS ──────────

arrow(user_x + user_w, user_y + user_h - 2.5,
      backend_x, backend_y + backend_h - 6,
      "1. drops PDF + picks module", dx=-1.5, dy=2.8, curve=-0.18)

arrow(90, 73, node_x_start + node_w / 2 + 27, node_y + node_h,
      "2. PDF in", dx=4, dy=2.5)

arrow(56, 73, node_x_start + node_w / 2, node_y + node_h,
      "3. relevant tickets pulled", dx=-2, dy=2.5)

arrow(backend_x, backend_y + 20,
      user_x + user_w, user_y + 9,
      "4. proposed edits", dx=-0.5, dy=2.8, curve=0.18)

arrow(user_x + user_w, user_y + 3,
      backend_x, backend_y + 13,
      "5. approve → applied  ·  reject → discarded (logged)",
      dx=-0.5, dy=-2.8, curve=-0.18)

arrow(backend_x + backend_w, backend_y + backend_h - 12,
      out_x, out_y + out_h / 2,
      "6. revised PDF", dx=0, dy=2.4, curve=0.12)

arrow(backend_x + 8, backend_y,
      backend_x + 8, 15,
      "saves intermediate files", dx=13, dy=0)


plt.savefig(str(OUT), dpi=130, bbox_inches="tight", facecolor="white", format="jpg")
print(f"wrote {OUT}  ({OUT.stat().st_size} bytes)")
print(f"file:// URL: {OUT.as_uri()}")
