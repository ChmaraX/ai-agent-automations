# GitHub Actions CI Cost And Time Digest

## Overview

`github-actions-ci-cost-and-time-digest` reads recent GitHub Actions history across a repository, finds the workflows and jobs consuming the most CI time, highlights likely cost drivers, and turns that into a recurring digest.

It is read-only. Each run shows where CI time is going now, what got slower or more expensive recently, and which hotspots are worth attention first.

## How It Works

1. Reads recent successful and failed CI runs across the repository.
2. Groups the data by workflow, job, and trigger path to find the biggest current runtime and cost surfaces.
3. Compares the current window with a recent prior window when enough history exists.
4. Highlights the workflows, jobs, and regressions most worth human attention.
5. Returns one compact digest.

## When To Use It

- you want a recurring view of where CI time and likely cost are going
- you want to spot newly slow or newly expensive workflows before optimizing them
- you want one compact digest instead of manually inspecting Actions history

## Prerequisites

- GitHub access with enough permission to read Actions runs, jobs, and timing data

## Cursor Cloud Usage

1. Open [Cursor Automations](https://cursor.com/automations/new).
2. Name your automation and paste [github-actions-ci-cost-and-time-digest.md](/Users/adamchmara/projects/awesome-agent-automations/automations/github-actions-ci-cost-and-time-digest/github-actions-ci-cost-and-time-digest.md) as the automation prompt.
3. Add GitHub access through the GitHub integration, GitHub MCP, or make `gh` available in the runtime.
4. Make sure the runtime can read GitHub Actions runs and timing data.
5. Set the schedule or run manually, then save the automation.

## Codex App Usage

1. Click `Automation` > `New Automation`.
2. Name your automation and paste [github-actions-ci-cost-and-time-digest.md](/Users/adamchmara/projects/awesome-agent-automations/automations/github-actions-ci-cost-and-time-digest/github-actions-ci-cost-and-time-digest.md) as the automation prompt.
3. Add the GitHub plugin to Codex, a GitHub MCP server, or make `gh` available in the runtime.
4. Make sure the environment can read GitHub Actions runs and timing data.
5. Set the schedule or run manually and save the automation.

## Claude Code Usage

1. Add GitHub access through MCP or make `gh` available in the runtime.
2. Make sure the runtime can read GitHub Actions runs and timing data.
3. For repeated checks in an open Claude Code session, use `/loop`, for example:

```text
/loop 1w Follow the instructions in automations/github-actions-ci-cost-and-time-digest/github-actions-ci-cost-and-time-digest.md
```

4. For durable Claude-managed automation that survives outside the current session, use `/schedule` or create a Routine in `claude.ai/code/routines`.

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

- Prefer actual Actions timing and billable data when available.
- If exact cost visibility is unavailable, report likely cost drivers from runtime, runner class, and run frequency rather than inventing precise cost numbers.
- Keep the digest focused on current hotspots and meaningful regressions, not generic best practices.

## Useful Repo-Specific Inputs

Tell the runner anything it cannot reliably infer.

Scope example:

```text
Ignore deploy, release, and one-off migration workflows. Focus only on developer-facing CI.
```

Priority example:

```text
Weight pull request workflows above scheduled maintenance workflows when choosing the final spotlight list.
```

Cost example:

```text
If billable-minute data is unavailable, estimate cost pressure from run frequency, runtime, and runner size, but label it as inferred rather than measured.
```

Delivery example:

```text
Keep the digest short. Lead with the workflows that got materially slower this week and the jobs consuming the most total runtime.
```
