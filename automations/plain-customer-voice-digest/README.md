# Plain Customer Voice Digest

## Overview

`plain-customer-voice-digest` reviews a bounded set of recent Plain support threads and turns them into one evidence-backed customer voice summary.

It is meant for recurring support insight: repeated pain points, confusing workflows, common objections, and customer phrasing worth preserving.

## How It Works

1. Reads a bounded slice of recent support threads from Plain.
2. Expands only the thread and tenant context needed to understand repeated themes.
3. Clusters the strongest signals into a small number of themes.
4. If persistent memory is available, compares themes against `memory.md` to mark them as new, recurring, persistent, escalating, or cooling.
5. Produces one compact digest with representative examples and useful wording.

## When To Use It

- You want a weekly or twice-weekly support insight summary.
- Product feedback is scattered across many support threads.
- You want repeated signals, not one-off anecdotes.
- You want customer language captured in a form product, support, or marketing can reuse.

## Prerequisites

- Plain access through the official MCP server
- Enough thread volume to produce repeated signals
- Optional persistent memory if you want cross-run trend detection
- Optional delivery tooling if you want the digest posted elsewhere

## Setup

Use [plain-customer-voice-digest.md](/Users/adamchmara/projects/ai-agent-automations/automations/plain-customer-voice-digest/plain-customer-voice-digest.md) as the automation prompt.

### Cursor Cloud

1. Open [Cursor Automations](https://cursor.com/automations/new).
2. Create a new automation and paste the prompt.
3. Add Plain MCP at `https://mcp.plain.com/mcp` and authenticate.
4. Optional: add delivery tools or persistent memory support.
5. Save and schedule the automation.

### Codex App

1. Add Plain MCP access.
2. Click `Automation` > `New Automation` and paste the prompt.
3. Optional: add delivery tools or persistent memory support.
4. Save the automation.

### Claude Code

1. Add and authenticate Plain MCP.
2. For repeated runs in one session, use:

```text
/loop 1w Follow the instructions in automations/plain-customer-voice-digest/plain-customer-voice-digest.md
```

3. For durable automation, use `/schedule` or a Routine.

## Recommended Defaults

| Setting | Default |
| --- | --- |
| Time window | `last 7 days` |
| Candidate pool | `up to 50 threads` |
| Final theme count | `3 to 5` |
| Examples per theme | `1 to 3` |
| Trend labels | `use memory when available; otherwise current-window only` |
| Delivery mode | `preview output` |
| Empty-run behavior | `report that no repeated themes qualified` |

Favor repeated evidence over loud anecdotes, keep excerpts short, and keep `memory.md` limited to compact theme fingerprints rather than raw customer transcripts.

## Useful Inputs

Example scope:

```text
Focus on external customer threads only.
Exclude spam, test tenants, internal dogfooding, and hiring or partnership conversations.
```

Example theme policy:

```text
Prioritize bugs, confusing setup flows, pricing objections, onboarding friction, and repeated feature gaps.
Treat one-off billing edge cases as lower priority unless they recur across multiple tenants.
```

Example delivery rule:

```text
If Slack is connected, post the final digest to #support-insights.
If Slack is not connected, keep the digest in preview output only.
```

## Docs

- [Plain MCP Server](https://help.plain.com/article/mcp-server)
- [Codex Automations](https://openai.com/academy/codex-automations)
