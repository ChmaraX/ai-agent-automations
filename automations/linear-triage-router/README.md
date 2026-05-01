# Linear Triage Router

## Overview

`linear-triage-router` reviews a bounded slice of Linear Triage issues and applies only high-confidence team, label, priority, and internal-comment updates.

## How It Works

1. Reads a bounded set of new or aging Triage issues.
2. Expands Linear metadata and linked GitHub context only when useful.
3. Checks for duplicate or related work before changing routing fields.
4. Applies only high-confidence team, label, priority, and internal-comment updates.
5. Falls back to prepared output when writes are unavailable, evidence is ambiguous, or the run cap is reached.

## Prerequisites

- Linear access through the official Linear MCP server or CLI
- Optional GitHub access if linked context should influence routing

## Cursor Cloud Usage

1. Open [Cursor Automations](https://cursor.com/automations/new).
2. Name your automation and paste [linear-triage-router.md](/Users/adamchmara/projects/awesome-agent-automations/automations/linear-triage-router/linear-triage-router.md) as the automation prompt.
3. Add trigger conditions.
4. Add Linear access through the official MCP server.
  - If Cursor already exposes Linear as a managed MCP or connector, use that path.
5. Add optional GitHub read access if your Triage issues often depend on linked repository context.
6. Save the automation.

## Codex App Usage

1. Install the official Linear MCP server in Codex:
  ```bash
  codex mcp add linear --url https://mcp.linear.app/mcp
  codex mcp login linear
  codex mcp list
  ```
2. Click `Automation` > `New Automation`.
3. Name your automation and paste [linear-triage-router.md](/Users/adamchmara/projects/awesome-agent-automations/automations/linear-triage-router/linear-triage-router.md) as the automation prompt.
4. Add optional GitHub connectors only if linked reads should influence routing decisions.
5. Set the schedule or run manually and save the automation.

## Claude Code Usage

1. Add the official Linear MCP server in Claude Code:
  ```bash
  claude mcp add --transport http linear https://mcp.linear.app/mcp
  claude mcp list
  ```
2. Open Claude Code and run `/mcp` to authenticate with Linear in your browser.
3. Add optional GitHub access if linked context should influence routing.
4. For repeated checks in an open Claude Code session, use `/loop`, for example:

```text
/loop weekdays at 9am Follow the instructions in automations/linear-triage-router/linear-triage-router.md
```

5. For durable Claude-managed automation, use `/schedule` or create a Routine in `claude.ai/code/routines`.

## Recommended Defaults

| Setting | Default |
| --- | --- |
| Scope window | `24h` |
| First-pass candidate pool | `20 issues` |
| Max updates per run | `5 issues` |
| Allowed writes | `team`, `labels`, `priority`, `internal comment` |
| Duplicate handling | `search first, caution or skip, no auto-relation` |
| Description handling | `preserve original text` |
| Linked reads | `GitHub only when it materially improves routing` |
| Empty-run behavior | `report that no issues qualified` |

Additional guidance:

- Start with low-frequency scheduling until the team trusts the routing quality.
- Keep label rules tight. Favor labels with obvious, stable meaning over broad taxonomy cleanup.
- Use comments for enrichment and clarification rather than rewriting intake descriptions.
- If ownership is ambiguous, leave the issue untouched and place it in `Needs Human Triage`.

## Useful Workspace-Specific Inputs

Tell the runner anything it cannot reliably infer from Linear alone.

Team mapping example:

```text
Route repository-api, auth-service, and permission-system issues to Platform.
Route dashboard, workspace-settings, and billing-ui issues to Product Engineering.
If both platform and product cues are present, leave the issue untouched and report it for human triage.
```

Label policy example:

```text
Apply bug labels only when the issue describes a broken existing behavior with reproduction evidence.
Do not add broad process labels such as triage, needs-review, or backlog-hygiene unless the workspace already uses them deterministically.
```

Priority heuristic example:

```text
Raise priority only for clear customer impact, production breakage, repeated duplicates, or urgent support escalation.
Do not escalate vague dissatisfaction or feature requests without operational urgency.
```

Comment policy example:

```text
Keep internal comments short and structured.
Use:
- Ownership: <team and one-sentence reason>
- Changes: <labels, priority, or no field changes>
- Related history: <relevant issue links or none>
- Missing info: <one targeted question or none>
Prefer bullets over prose paragraphs.
Do not copy private requester details, account identifiers, pasted secrets, or sensitive support text into the comment.
```
