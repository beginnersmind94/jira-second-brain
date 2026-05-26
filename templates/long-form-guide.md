---
template: long-form-guide
content_type: long-form-guide
target_word_count: 2500-6000
target_read_time: 30-60 min
audience: ["director","manager"]
status: template
---

# {{Module}} — {{Subject}} (Full Guide)

> **One-line promise:** what the reader will be able to do after reading.
> **Audience:** which roles this is for.
> **Time:** estimated read.
> **Last updated:** YYYY-MM-DD

## At a glance

A 4–6 sentence orientation. Define the subject in plain language. Name what's *in* scope and what's *not*. State the one outcome the reader is trying to reach.

## Why this exists

Short paragraph on the business reason. Cite the regulatory, customer, or workflow driver. Avoid filler like "in today's fast-paced environment."

## Concepts

Define every term the rest of the guide depends on. One sub-heading per concept. Each definition is 1–3 sentences and cites a source — a wiki page or a ticket.

- **Term A** — definition. Source: [[wiki/concepts/...]]
- **Term B** — definition. Source: [[raw/tickets/NXT-####]]

## How it works

Walk the reader through the mechanism in the order it actually executes in the product. Use numbered steps when order matters. Each non-obvious behavior must cite a ticket.

1. Step one — what happens, who triggers it, what state changes.
2. Step two — …

## Step-by-step (the common path)

The most common user-facing flow, screen by screen or page by page. Use real page names from the product. If a screen has unique controls, name them exactly.

1. Navigate to **{Page name}**.
2. …

## Examples

2–4 concrete scenarios. Each example is a short narrative — input, what the user does, what the system shows. Use role labels (`<District A>`, never customer names).

### Example 1 — {scenario}
…

## Edge cases & known issues

Bulleted list. Each item cites the ticket that surfaced it. If there is no ticket, the item doesn't belong here.

- Behavior X when Y. Source: [[raw/tickets/NXT-####]]

## Glossary

Optional — only include terms that aren't already defined in Concepts.

## Sources

Full list of tickets and wiki pages cited in this guide. Anti-hallucination rule 2: cite or cut.

- [[wiki/concepts/{Module}]]
- [[wiki/workflows/{slug}]]
- [[raw/tickets/NXT-####]]
