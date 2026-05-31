# Sentry Triage And Fix

## Overview

`sentry-triage-and-fix` selects one strong Sentry issue candidate, validates the repository and code evidence, attempts the smallest safe fix, runs validation, and opens a draft PR or prepares PR-ready output.

Use it when you want one high-value production issue turned into reviewable engineering work, not an unattended batch autofix pipeline.

## How It Works

1. Queries Sentry for a bounded set of high-signal unresolved issues.
2. Ranks candidates and selects at most one issue with clear repository mapping, in-app stack evidence, and available validation commands.
3. Verifies the root-cause hypothesis in the local codebase, implements the smallest safe fix, and adds a targeted regression test when feasible.
4. Runs validation and opens a draft PR, or stops with a reviewable report if the fix cannot be validated safely.

```mermaid
sequenceDiagram
    participant Agent
    participant Sentry
    participant Repo
    participant PR as Git Provider

    Agent->>Sentry: Query bounded high-signal issues
    Sentry-->>Agent: Issue details, events, and links
    Agent->>Repo: Verify mapped code evidence and implement minimal fix
    Agent->>Repo: Run targeted validation
    Agent->>PR: Open draft PR
    Note over Agent: No Sentry status changes, no merge, no ready-for-review
```

## Prerequisites

- Sentry access through MCP or [`sentry-cli`](#cli-alternative)
- Repository access in the workspace where the fix will be made
- Validation commands for the affected app, package, or service
- GitHub or equivalent PR tooling if you want automatic draft PR creation

## Cursor Cloud Usage

1. Open [Cursor Automations](https://cursor.com/automations/new).
2. Name your automation and paste [sentry-triage-and-fix.md](/Users/adamchmara/projects/awesome-agent-automations/automations/sentry-triage-and-fix/sentry-triage-and-fix.md) as the automation prompt.
3. Add trigger conditions.
4. Click `Add tools or MCP` > `MCP server`.
5. Add the hosted Sentry MCP server at `https://mcp.sentry.dev/mcp` and complete the connection flow.
  - CLI alternative: use [`sentry-cli`](#cli-alternative) in the agent environment instead of steps 4-5.
6. Add the `Open Pull Request` tool, or let the agent use an existing GitHub CLI or plugin in the environment.
7. Make sure the runtime can execute the validation commands required for the mapped repository.
8. Click `Create`.

## Codex App Usage

1. Install the hosted Sentry MCP server in Codex:
  ```bash
  codex mcp add sentry --url https://mcp.sentry.dev/mcp
  codex mcp login sentry
  codex mcp list
  ```
  - CLI alternative: use [`sentry-cli`](#cli-alternative) in the agent environment instead of MCP.
2. Click `Automation` > `New Automation`.
3. Name your automation and paste [sentry-triage-and-fix.md](/Users/adamchmara/projects/awesome-agent-automations/automations/sentry-triage-and-fix/sentry-triage-and-fix.md) as the automation prompt.
4. Set schedule or run manually and save the automation.
5. Add the GitHub plugin to Codex, or let Codex use an existing GitHub CLI/tool in the agent environment.

## Claude Code Usage

1. Add the hosted Sentry MCP server in Claude Code:
  ```bash
  claude mcp add --transport http sentry https://mcp.sentry.dev/mcp
  claude mcp list
  ```
  - To share the MCP configuration through the repo, use `--scope project`.
  - CLI alternative: use [`sentry-cli`](#cli-alternative) in the agent environment instead of MCP.
2. Open Claude Code and run `/mcp` to authenticate with Sentry in your browser.
3. Make sure the runtime can work in the affected repository and run the required validation commands.
4. For repeated checks in an open Claude Code session, use `/loop`, for example:

```text
/loop weekdays at 11am Follow the instructions in automations/sentry-triage-and-fix/sentry-triage-and-fix.md
```

5. For durable Claude-managed automation that survives outside the current session, use `/schedule` or create a Routine in `claude.ai/code/routines`.
6. Make sure the runtime has repository write access and PR creation access if you want automatic draft PRs.

## CLI Alternative

If you prefer not to use MCP, `sentry-cli` is a strong portable fallback for this automation.

Install and authenticate it first:

```bash
brew install getsentry/tools/sentry-cli
sentry-cli login
```

Useful examples:

```bash
sentry issue list <org>/<project> --query "is:unresolved issue.priority:high" --json
sentry issue view <issue-id> --json
sentry issue events <issue-id> --json
```

If you use this path, make sure the agent runtime can authenticate with `sentry-cli` and that the token has the issue and event scopes you need.

## Recommended Defaults

| Setting | Default |
| --- | --- |
| Query window | `24h` |
| Candidate pool size | `10` |
| Max issues fixed per run | `1` |
| Signals | `is:regressed`, `is:escalating`, `issue.priority:high`, `is:unresolved is:for_review` |
| PR mode | `draft-pr` |
| Branch | `fix/sentry-triage-and-fix-YYYY-MM-DD` |
| Commit message | `fix: address mapped Sentry issue` |

Keep the run conservative: prefer a local evidence-backed fix over speculative cleanup, stop when repository mapping or validation is unclear, and keep every PR as a draft.

## Prompt Inputs

Add context only when Sentry state alone is not enough, for example:

```text
Organization: acme
Projects: api, web
Environments: production
Map Sentry project `api` to `/workspace/services/api` and project `web` to `/workspace/apps/web`.
Do not touch auth, billing, migrations, data backfills, or infrastructure code.
```

## Docs

- [Sentry MCP](https://mcp.sentry.dev)
- [Sentry CLI Installation](https://docs.sentry.dev/cli/installation/)
- [Codex Automations](https://openai.com/academy/codex-automations)
