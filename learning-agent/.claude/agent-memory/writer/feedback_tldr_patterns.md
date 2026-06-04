---
name: feedback-tldr-patterns
description: HTML structure and density techniques that work for TLDR one-pager template — proven on Item Management 2026-05-29
metadata:
  type: feedback
---

Use `font-size: 11.5px`, `line-height: 1.35`, and `margin: 0.6in 0.65in` for body to achieve dense one-page layout.

Table cell `font-size: 11px`; left column `width: 34%`, `font-weight: 600`, `white-space: nowrap`; right column `width: 66%`.

Keep `thead` background `#e8e8e8` with 1px `#bbb` border. Row padding `2px 6px`.

Heading style: `h2` at `12.5px`, uppercase with `letter-spacing: 0.03em`, thin `#aaa` bottom border, `8px` top margin. No `<h3>` ever.

For `ul` bullets: `margin: 2px 0 4px 0`, `padding-left: 16px`, `li margin-bottom: 1px`. Keeps bullets tight.

Inline citation comments go immediately after the closing tag of the element they support (after `</td>`, after `</li>`) — do NOT put them inside the tag text.

**Why:** Template hard constraint is one page flat — excess whitespace triggers overflow. This density config was validated against the ~685-word Item Management TLDR without overflow.

**How to apply:** Copy these CSS values directly into every new TLDR draft. Adjust only if a module has significantly fewer features (fewer than 15 rows) and can afford more breathing room.
