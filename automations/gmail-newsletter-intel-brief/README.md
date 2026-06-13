# Gmail Newsletter Intel Brief

## Overview

This automation pulls useful signals from recent newsletter emails and combines them into one concise digest. It is for people who want the takeaways without reading every newsletter.
## How It Works

1. Looks back over a bounded recent Gmail window and discovers likely recurring newsletter senders.
2. Reuses the automation memory file to remember confirmed newsletter senders, recurring non-newsletter senders, and compact sender notes from prior runs.
3. Reads the current in-window issues from the detected senders instead of opportunistically sampling a noisy Gmail category.
4. Extracts the main items, claims, entities, and links from each issue without trying to summarize the whole email thread universe.
5. Clusters overlapping items into a short list of recurring themes.
6. Merges repetitive coverage across newsletters and keeps the clearest, most evidence-backed source links.
7. Produces one Markdown brief with both coverage accounting and high-signal items.

```mermaid
sequenceDiagram
    participant Agent
    participant Gmail as Gmail Scope
    participant Links as Source Links

    Agent->>Gmail: Read bounded newsletter slice
    Gmail-->>Agent: In-scope messages and metadata
    Agent->>Links: Optionally confirm highest-signal links
    Links-->>Agent: Human-readable article context
    Note over Agent: Read-only, no replies, labels, archive, or deletes
```

## Prerequisites

- Gmail access through a configured Google Workspace MCP server or the `gws` CLI

It can run with no extra configuration. It works best when you later narrow the scope with a label, sender set, or Gmail query that already isolates the newsletters you trust.

## Cursor Cloud Usage

1. Open [Cursor Automations](https://cursor.com/automations/new).
2. Name your automation and paste [gmail-newsletter-intel-brief.md](/Users/adamchmara/projects/ai-agent-automations/automations/gmail-newsletter-intel-brief/gmail-newsletter-intel-brief.md) as the automation prompt.
3. Add Google Workspace access through a Workspace MCP server or the `gws` CLI.
4. Optionally customize the scope or audience notes near the top of the prompt.
5. Allow memory so the automation can remember confirmed newsletter senders and recurring non-newsletter senders between runs.
6. Set the schedule or run manually, then save the automation.

## Codex App Usage

1. Set up Gmail access in Codex using a Google Workspace MCP server or the `gws` CLI.
2. Click `Automation` > `New Automation`.
3. Name your automation and paste [gmail-newsletter-intel-brief.md](/Users/adamchmara/projects/ai-agent-automations/automations/gmail-newsletter-intel-brief/gmail-newsletter-intel-brief.md) as the automation prompt.
4. Optionally customize the scope or audience notes near the top of the prompt.
5. Let the automation reuse its persistent `memory.md` between runs for sender allow and ignore hints.
6. Set schedule or run manually and save the automation.

## Claude Code Usage

1. Add a Google Workspace MCP server to Claude Code if you want MCP-backed runs, or make `gws` available in the runtime.
2. Make sure the runtime can read Gmail messages, message metadata, and links from the selected newsletter scope.
3. Use the prompt as-is for the default behavior, or add a short override note before using `/loop` or `/schedule`. For example:

```text
Newsletter Gmail scope: label:newsletters newer_than:7d
Topic priorities: competitors, product launches, tooling, market moves
Audience: product and strategy leads
Output emphasis: keep only items that are new, repeated across sources, or materially actionable
```

4. For durable Claude-managed automation outside the current session, use `/schedule` or create a Routine in `claude.ai/code/routines`.

## Recommended Defaults

| Setting | Default |
| --- | --- |
| Discovery window | `last 30 days` |
| Brief window | `last 7 days` |
| Message scope | `bounded Gmail discovery, then detected recurring newsletter senders` |
| Sender discovery budget | `up to 150 candidate messages` |
| Full issue reads | `up to 3 recent issues per detected sender, up to 60 total issue reads` |
| Final theme count | `up to 6 themes` |
| Final item count | `up to 12 items` |
| Output | `Markdown intelligence brief` |
| Delivery mode | `report-only` |

Keep the run conservative: prefer recurring-sender detection over one-pass category sampling, use memory to reduce false positives, prefer deduplicated themes over sender-by-sender summaries, and narrow scope rather than expanding into the full inbox when discovery is noisy.

## Prompt Inputs

Add context only when you want tighter scope or a different audience, for example:

```text
Newsletter Gmail scope: label:market-newsletters newer_than:7d
Topic priorities: competitors, product launches, tooling, market moves
Audience: founder and product leads
Output emphasis: prefer concrete launches, funding moves, pricing changes, and tooling announcements
```

## Docs

- [Codex Automations](https://openai.com/academy/codex-automations)
