# Linear Triage Router

## Overview

`linear-triage-router` reviews a bounded slice of Linear Triage issues and applies only high-confidence team, label, priority, and internal-comment updates.

It is meant for safe routing, not broad backlog cleanup. When evidence is weak or writes are unavailable, it falls back to prepared output.

## How It Works

1. Reads a bounded set of new or aging Triage issues.
2. Expands Linear metadata and linked GitHub context only when useful.
3. Checks for duplicate or related work before changing routing fields.
4. Applies only high-confidence team, label, priority, and internal-comment updates.
5. Stops with prepared output when the evidence is ambiguous or the run cap is reached.

## When To Use It

- You want recurring triage help for a noisy Linear intake queue.
- You want routing fields updated only when the evidence is strong.
- You want comments used for clarification instead of rewriting issue descriptions.

## Prerequisites

- Linear access through the official MCP server or CLI
- Optional GitHub access if linked repository context should affect routing

## Setup

Use [linear-triage-router.md](/Users/adamchmara/projects/ai-agent-automations/automations/linear-triage-router/linear-triage-router.md) as the automation prompt.

### Cursor Cloud

1. Open [Cursor Automations](https://cursor.com/automations/new).
2. Create a new automation and paste the prompt.
3. Add Linear access.
4. Optional: add GitHub read access if linked context matters.
5. Save and schedule the automation.

### Codex App

1. Add Linear MCP access.
2. Click `Automation` > `New Automation` and paste the prompt.
3. Optional: add GitHub read access.
4. Save the automation.

### Claude Code

1. Add and authenticate Linear MCP.
2. Optional: add GitHub access if linked context matters.
3. For repeated runs in one session, use:

```text
/loop weekdays at 9am Follow the instructions in automations/linear-triage-router/linear-triage-router.md
```

4. For durable automation, use `/schedule` or a Routine.

## Recommended Defaults

| Setting | Default |
| --- | --- |
| Scope window | `24h` |
| Candidate pool | `20 issues` |
| Max updates per run | `5 issues` |
| Allowed writes | `team`, `labels`, `priority`, `internal comment` |
| Duplicate handling | `search first, caution or skip, no auto-relation` |
| Description handling | `preserve original text` |
| Linked reads | `GitHub only when it materially improves routing` |
| Empty-run behavior | `report that no issues qualified` |

Keep label rules tight, use comments for structured context, and leave ambiguous issues untouched in `Needs Human Triage`.

## Useful Inputs

Example team mapping:

```text
Route repository-api, auth-service, and permission-system issues to Platform.
Route dashboard, workspace-settings, and billing-ui issues to Product Engineering.
If both platform and product cues are present, leave the issue untouched and report it for human triage.
```

Example label policy:

```text
Apply bug labels only when the issue describes a broken existing behavior with reproduction evidence.
Do not add broad process labels unless the workspace already uses them deterministically.
```

Example priority rule:

```text
Raise priority only for clear customer impact, production breakage, repeated duplicates, or urgent support escalation.
Do not escalate vague dissatisfaction or feature requests without operational urgency.
```
