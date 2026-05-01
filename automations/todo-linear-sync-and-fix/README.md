# TODO Linear Sync And Fix

## Overview

`todo-linear-sync-and-fix` scans repo TODO-style comments, fixes the easy ones directly, turns the harder ones into Linear issues, updates the source comments, and opens one draft PR for the run.

Use it when you want TODO comments to become either finished work or clearly tracked backlog without manually triaging each one.

## How It Works

1. Scans the current repository for `TODO`, `FIXME`, `XXX`, and similar inline work markers.
2. Skips comments that already include a ticket key, URL, or other explicit tracking reference.
3. Takes up to 5 untracked candidates per run.
4. Fixes the simple ones immediately when the local code and validation path are clear.
5. Creates one Linear issue for each remaining non-trivial item.
6. Rewrites ticketed comments so they reference the created Linear work.
7. Opens one draft PR containing direct fixes, comment updates, or both.

Use the runtime prompt at [todo-linear-sync-and-fix.md](/Users/adamchmara/projects/awesome-agent-automations/automations/todo-linear-sync-and-fix/todo-linear-sync-and-fix.md).

## Prerequisites

- Linear access that can create issues
- Repository write access for code and comment edits
- Git provider access that can open draft PRs

## Cursor Cloud Usage

1. Open [Cursor Automations](https://cursor.com/automations/new).
2. Name your automation and paste [todo-linear-sync-and-fix.md](/Users/adamchmara/projects/awesome-agent-automations/automations/todo-linear-sync-and-fix/todo-linear-sync-and-fix.md) as the automation prompt.
3. Add Linear access through the official MCP server or managed connector with issue creation enabled.
4. Add repository access plus draft PR creation access.
5. Save the automation and start with a low-frequency schedule until the behavior looks right in your repo.

## Codex App Usage

1. Install the official Linear MCP server in Codex:
   ```bash
   codex mcp add linear --url https://mcp.linear.app/mcp
   codex mcp login linear
   codex mcp list
   ```
2. Click `Automation` > `New Automation`.
3. Name your automation and paste [todo-linear-sync-and-fix.md](/Users/adamchmara/projects/awesome-agent-automations/automations/todo-linear-sync-and-fix/todo-linear-sync-and-fix.md) as the automation prompt.
4. Make sure the runtime also has repository write access and draft PR creation access.
5. Set the schedule or run manually and save the automation.

## Claude Code Usage

1. Add the official Linear MCP server in Claude Code:
   ```bash
   claude mcp add --transport http linear https://mcp.linear.app/mcp
   claude mcp list
   ```
2. Open Claude Code and run `/mcp` to authenticate with Linear in your browser.
3. Make sure the runtime can edit the target repository, run validation commands, and open draft PRs.
4. For repeated runs in an open session, use `/loop`, for example:

```text
/loop weekdays at 11am Follow the instructions in automations/todo-linear-sync-and-fix/todo-linear-sync-and-fix.md
```

5. For durable Claude-managed automation, use `/schedule` or create a Routine in `claude.ai/code/routines`.

## Recommended Defaults

| Setting | Default |
| --- | --- |
| Candidate markers | `TODO`, `FIXME`, `XXX` |
| Max items per run | `5` |
| Duplicate handling | `skip only when the comment already has a tracking reference` |
| Direct fix behavior | `fix immediately when simple enough` |
| Ticket behavior | `create one Linear issue and rewrite the comment` |
| PR mode | `draft` |

Additional guidance:

- Keep the first version repo-local and bounded.
- Prefer small, obvious fixes over cleanup passes.
- Keep the comment rewrite compact so future runs can spot tracked work quickly.
- If the repo has a preferred tracking format, use that format consistently in the rewritten comments.

## Useful Workspace-Specific Inputs

Tell the runner anything it cannot infer reliably from the repo alone.

Comment format example:

```text
When creating a ticket, rewrite comments as:
TODO(linear: ENG-123): original comment text
```

Simple-fix threshold example:

```text
Treat one-file edits with obvious nearby validation as simple enough to fix immediately.
Treat multi-file refactors, migrations, or API redesigns as ticket-only.
```

Validation example:

```text
For frontend packages run:
pnpm test --filter web -- --runInBand

For backend packages run:
pnpm test --filter api -- --runInBand
```
