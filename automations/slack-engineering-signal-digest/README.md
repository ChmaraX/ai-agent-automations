# Slack Engineering Signal Digest

## Overview

`slack-engineering-signal-digest` reads a defined set of Slack engineering channels, pulls out the highest-signal recent threads, verifies linked system state when possible, and returns one concise digest.

Use it when important engineering discussion starts in Slack but the source of truth may still live in GitHub, Jira, Linear, or Sentry.

## How It Works

1. Searches only the channels you explicitly allow and only within a bounded time window.
2. Shortlists the most important messages and threads before reading deeper.
3. Verifies linked GitHub, Jira, Linear, or Sentry state when those links exist.
4. Produces a digest with `TL;DR`, `Highlights`, and optional `Decisions`, `Needs Attention`, or `Action Items`.
5. Defaults to preview or draft output rather than broad posting.

## When To Use It

- Slack is your engineering coordination layer, but status is spread across other tools.
- You want a short daily or recurring digest from a few channels.
- You need downstream verification before calling something fixed, shipped, or resolved.
- You want a draft digest first, not automatic posting.

## Prerequisites

- Slack access through Slack MCP
- An explicit channel allowlist in the prompt
- Optional GitHub, Jira, Linear, or Sentry access for linked-state verification

## Setup

Use [slack-engineering-signal-digest.md](/Users/adamchmara/projects/awesome-agent-automations/automations/slack-engineering-signal-digest/slack-engineering-signal-digest.md) as the automation prompt.

### Cursor Cloud

1. Open [Cursor Automations](https://cursor.com/automations/new).
2. Paste the prompt into a new automation.
3. Add Slack MCP and set the real channel allowlist in the prompt.
4. Optional: add GitHub, Jira, Linear, or Sentry if you want verification.
5. Save and schedule the automation.

### Codex App

1. Add Slack access through MCP or a managed connector.
2. Click `Automation` > `New Automation` and paste the prompt.
3. Set the channel allowlist in the prompt.
4. Optional: add downstream connectors for verification.
5. Save the automation.

### Claude Code

1. Add Slack access and authenticate.
2. Set the real channel allowlist in the prompt.
3. Optional: add downstream connectors for verification.
4. For repeated runs in one session, use:

```text
/loop weekdays at 9am Follow the instructions in automations/slack-engineering-signal-digest/slack-engineering-signal-digest.md
```

5. For durable automation, use `/schedule` or a Routine.

## Recommended Defaults

| Setting | Default |
| --- | --- |
| Slack scope | `explicit channel allowlist required` |
| Query window | `24h` |
| Candidate pool | `30 messages or threads` |
| Max digest items | `6` |
| Delivery | `preview or draft` |
| Downstream verification | `only when links are present` |
| Empty-run behavior | `no heartbeat post` |

Keep the scope narrow, prefer public channels unless private access is explicitly approved, and use a Slack canvas when the digest is too long for a clean message.

## Useful Inputs

Example scope:

```text
Slack channels: #eng-infra, #incidents-api, #releases, #support-escalations
Window: 24h
```

Example verification rule:

```text
When a Slack thread links to GitHub, Jira, Linear, or Sentry, verify the current state before calling something fixed, shipped, resolved, or assigned.
If there is no linked system, keep the item as Slack-only.
```

Example delivery rule:

```text
Produce preview output first.
If the digest is too long for a normal channel message, create a canvas instead.
```

## Docs

- [Slack MCP Server](https://docs.slack.dev/ai/slack-mcp-server/)
- [Codex Automations](https://openai.com/academy/codex-automations)
