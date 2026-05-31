# TODO Linear Sync And Fix

## Overview

`todo-linear-sync-and-fix` scans repo TODO-style comments, fixes the easy ones directly, turns the harder ones into Linear issues, updates the source comments, and opens one draft PR for the run.

Use it when you want TODO comments to become either finished work or clearly tracked backlog instead of accumulating silently.

## How It Works

1. Scans the repository for `TODO`, `FIXME`, `XXX`, and similar markers.
2. Skips comments that already include a ticket key, URL, or other tracking reference.
3. Takes a bounded set of untracked candidates.
4. Fixes the simple ones immediately when the code and validation path are clear.
5. Creates one Linear issue for each remaining non-trivial item.
6. Rewrites ticketed comments to reference the created Linear work.
7. Opens one draft PR containing direct fixes, comment updates, or both.

## When To Use It

- You want TODO cleanup tied directly to Linear.
- You want simple fixes handled automatically and harder items tracked.
- You want comment rewrites to make future triage easier.

## Prerequisites

- Linear access that can create issues
- Repository write access
- GitHub or equivalent PR tooling if you want automatic draft PR creation

## Setup

Use [todo-linear-sync-and-fix.md](/Users/adamchmara/projects/awesome-agent-automations/automations/todo-linear-sync-and-fix/todo-linear-sync-and-fix.md) as the automation prompt.

### Cursor Cloud

1. Open [Cursor Automations](https://cursor.com/automations/new).
2. Create a new automation and paste the prompt.
3. Add Linear access with issue creation enabled.
4. Add repository and PR tooling access.
5. Save and start with a low-frequency schedule.

### Codex App

1. Add Linear MCP access.
2. Click `Automation` > `New Automation` and paste the prompt.
3. Add GitHub or other PR tooling if needed.
4. Save the automation.

### Claude Code

1. Add and authenticate Linear MCP.
2. Make sure the runtime can edit the repo, validate changes, and open draft PRs if needed.
3. For repeated runs in one session, use:

```text
/loop weekdays at 11am Follow the instructions in automations/todo-linear-sync-and-fix/todo-linear-sync-and-fix.md
```

4. For durable automation, use `/schedule` or a Routine.

## Recommended Defaults

| Setting | Default |
| --- | --- |
| Candidate markers | `TODO`, `FIXME`, `XXX` |
| Max items per run | `5` |
| Duplicate handling | `skip only when the comment already has tracking` |
| Direct fix behavior | `fix immediately when simple enough` |
| Ticket behavior | `create one Linear issue and rewrite the comment` |
| PR mode | `Draft` |

Prefer small, obvious fixes over cleanup sweeps, and keep rewritten comments compact so later runs can spot tracked work quickly.

## Useful Inputs

Example comment format:

```text
When creating a ticket, rewrite comments as:
TODO(linear: ENG-123): original comment text
```

Example fix threshold:

```text
Treat one-file edits with obvious nearby validation as simple enough to fix immediately.
Treat multi-file refactors, migrations, or API redesigns as ticket-only.
```
