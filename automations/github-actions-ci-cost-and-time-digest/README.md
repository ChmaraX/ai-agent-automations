# GitHub Actions CI Cost And Time Digest

## Overview

`github-actions-ci-cost-and-time-digest` reads recent GitHub Actions history, finds the workflows and jobs consuming the most CI time, highlights likely cost drivers, and turns that into a recurring digest.

It is read-only. Each run shows where CI time is going now, what got slower recently, and which hotspots are worth human attention first.

## Preview

![HTML report preview](./assets/html-report-preview.png)

## How It Works

1. Reads recent successful and failed CI runs across the repository.
2. Groups runtime data by workflow, job, and trigger path.
3. Compares the current window with a recent prior window when enough history exists.
4. Highlights the workflows, jobs, and regressions most worth attention.
5. Returns one compact digest.

## When To Use It

- You want a recurring view of where CI time and likely cost are going.
- You want to spot newly slow workflows before optimizing them.
- You want one digest instead of manually inspecting Actions history.

## Prerequisites

- GitHub access with permission to read Actions runs, jobs, and timing data

## Setup

Use [github-actions-ci-cost-and-time-digest.md](/Users/adamchmara/projects/ai-agent-automations/automations/github-actions-ci-cost-and-time-digest/github-actions-ci-cost-and-time-digest.md) as the automation prompt.

### Cursor Cloud

1. Open [Cursor Automations](https://cursor.com/automations/new).
2. Create a new automation and paste the prompt.
3. Add GitHub access.
4. Save and schedule the automation.

### Codex App

1. Click `Automation` > `New Automation`.
2. Paste the prompt and add GitHub access.
3. Save the automation.

### Claude Code

1. Make sure the runtime can read GitHub Actions history.
2. For repeated runs in one session, use:

```text
/loop 1w Follow the instructions in automations/github-actions-ci-cost-and-time-digest/github-actions-ci-cost-and-time-digest.md
```

3. For durable automation, use `/schedule` or a Routine.

## Recommended Defaults

| Setting | Default |
| --- | --- |
| Repository scope | `current repository` |
| Current window | `last 7 days` |
| Comparison window | `previous 7 days when enough history exists` |
| First-pass workflow cap | `top 20 workflows by total runtime` |
| Final spotlight count | `top 5 workflows or jobs` |
| Trigger grouping | `separate by workflow and trigger path` |
| Delivery | `Markdown digest` |

Prefer actual Actions timing and billable data when available. If exact cost data is unavailable, report likely cost drivers from runtime, runner class, and run frequency rather than inventing precise numbers.

## Useful Inputs

Example scope:

```text
Ignore deploy, release, and one-off migration workflows. Focus only on developer-facing CI.
```

Example priority rule:

```text
Weight pull request workflows above scheduled maintenance workflows when choosing the final spotlight list.
```
