# raw/transcripts/ — placeholder

This directory is reserved for SME audio/video transcripts that may later be ingested as a second source type alongside `raw/tickets/`. **It is not used yet.** No transcripts exist; no script reads from this folder.

## Why it's here

The content-engine pivot (May 2026) anticipates that SMEs will record themselves walking through pages and workflows, and that those transcripts will become inputs to the same template + catalog pipeline that currently consumes Jira tickets and wiki pages. Creating the directory now reserves the name and signals direction.

## What goes here later

When transcripts arrive, each file will follow a shape similar to:

```
raw/transcripts/<KEY>.md
---
key: TR-2026-05-15-001
recorder: <SME name>
module: Eligibility
page: Direct Certification — Potential Matches
recorded_at: 2026-05-15
duration_sec: 480
status: raw
---
<transcript body>
```

Filename and frontmatter conventions will be finalized when the first batch lands.

## Current contract

- Do **not** write code that depends on this folder being non-empty.
- Do **not** treat absence of transcripts as a blocker for any current resource or template work.
- Resources today are grounded in `raw/tickets/` and `wiki/`; that does not change when transcripts arrive.
