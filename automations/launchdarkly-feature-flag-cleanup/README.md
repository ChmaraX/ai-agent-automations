# LaunchDarkly Feature Flag Cleanup

## Overview

Removes stale temporary LaunchDarkly flag code, validates the change, and opens a draft PR or prepares PR-ready output.

The automation uses LaunchDarkly as evidence for candidate selection and to confirm the served flag value before removing code. LaunchDarkly archive/delete remains a manual post-merge step.

## How It Works

1. Finds stale temporary LaunchDarkly flags that look safe to clean up.
2. Checks LaunchDarkly state to confirm a single stable served value.
3. Removes flag-related code paths and clearly orphaned references.
4. Runs validation and opens a draft PR or prepares PR-ready output.

```mermaid
sequenceDiagram
    participant Agent
    participant LD as LaunchDarkly
    participant Repo
    participant PR as Git Provider

    Agent->>LD: Read flag state and candidate evidence
    LD-->>Agent: Stable served value and safety signals
    Agent->>Repo: Remove stale flag code
    Agent->>Repo: Run repo validation
    Agent->>PR: Open draft PR
    Note over LD: No archive/delete or other writes
```

## Prerequisites

- LaunchDarkly access through MCP or `ldcli`
- GitHub or equivalent PR tooling if you want automatic PR creation

## Cursor Cloud Usage

1. Open [Cursor Automations](https://cursor.com/automations/new).
2. Name your automation and paste [launchdarkly-feature-flag-cleanup.md](/Users/adamchmara/projects/awesome-agent-automations/automations/launchdarkly-feature-flag-cleanup/launchdarkly-feature-flag-cleanup.md) as the automation prompt.
3. Add trigger conditions.
4. Click `Add tools or MCP` > `MCP server` > `LaunchDarkly feature management` > `New connection` > `LaunchDarkly` > `Connect`.
  - CLI alternative: use [ldcli](#cli-alternative) in the agent environment instead of steps 4-5.
5. Select `LaunchDarkly feature management` from the list of MCP servers.
6. Add the `Open Pull Request` tool, or let the agent use an existing GitHub CLI or plugin in the environment.
7. Optionally add other tools, such as Slack for notifications.
8. Click `Create`.

References:

- [Cursor Automations](https://cursor.com/blog/automations)
- [LaunchDarkly hosted MCP server](https://launchdarkly.com/docs/home/getting-started/mcp-hosted)

## Codex App Usage

1. Install the hosted LaunchDarkly feature management MCP server in Codex:
  ```bash
   codex mcp add launchdarklyFeatureManagement --url https://mcp.launchdarkly.com/mcp/fm
   codex mcp login launchdarklyFeatureManagement
   codex mcp list
  ```
  - CLI alternative: use [ldcli](#cli-alternative) in the agent environment instead of MCP.
2. Click `Automation` > `New Automation`.
3. Name your automation and paste [launchdarkly-feature-flag-cleanup.md](/Users/adamchmara/projects/awesome-agent-automations/automations/launchdarkly-feature-flag-cleanup/launchdarkly-feature-flag-cleanup.md) as the automation prompt.
4. Set schedule or run manually and save the automation.
5. Add the GitHub plugin to Codex, or let Codex use an existing GitHub CLI/tool in the agent environment.

References:

- [Codex Automations](https://openai.com/academy/codex-automations)
- [LaunchDarkly hosted MCP server](https://launchdarkly.com/docs/home/getting-started/mcp-hosted)

## Claude Code / Codex CLI / Copilot Usage

For Codex CLI, Claude Code, GitHub Copilot coding agent, and similar agent tools, the usual pattern is: the agent does the work, and something else handles scheduling.

Common scheduling options:

- GitHub Actions with `schedule:`
- `cron`
- `launchd`
- `systemd` timers
- wrapper scripts that run the CLI in headless or non-interactive mode

Typical setup:

1. Set up LaunchDarkly access through MCP or [ldcli](#cli-alternative).
2. Put this prompt in the command, script, workflow, issue template, or task payload that invokes the agent.
3. Use your scheduler to run the workflow at the interval you want.
4. Make sure the runtime has repository access, GitHub access, and permission to run the validation commands you expect.

Example: scheduled GitHub Actions run with Codex

```yaml
name: LaunchDarkly flag cleanup

on:
  schedule:
    - cron: "0 9 * * 1"
  workflow_dispatch:

jobs:
  cleanup:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v5
      - uses: openai/codex-action@v1
        with:
          openai-api-key: ${{ secrets.OPENAI_API_KEY }}
          prompt-file: automations/launchdarkly-feature-flag-cleanup/launchdarkly-feature-flag-cleanup.md
```

Example: scheduled GitHub Actions run with Claude Code

```yaml
name: LaunchDarkly flag cleanup

on:
  schedule:
    - cron: "0 9 * * 1"
  workflow_dispatch:

jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: |
            Follow the instructions in automations/launchdarkly-feature-flag-cleanup/launchdarkly-feature-flag-cleanup.md
          claude_args: "--max-turns 10"
```

Example: local scheduled run

```bash
#!/usr/bin/env bash
set -euo pipefail

cd /path/to/repo

claude -p "Follow the instructions in automations/launchdarkly-feature-flag-cleanup/launchdarkly-feature-flag-cleanup.md"
```

Crontab entry:

```cron
0 9 * * 1 /path/to/run-launchdarkly-cleanup.sh >> /tmp/launchdarkly-cleanup.log 2>&1
```

For local scheduling, use `cron`, `launchd`, `systemd` timers, or Windows Task Scheduler depending on your platform.

References:

- [Codex CLI in GitHub Actions](https://cookbook.openai.com/examples/codex/autofix-github-actions)
- [Codex GitHub Action](https://github.com/openai/codex-action)
- [Claude Code GitHub Actions](https://docs.anthropic.com/en/docs/claude-code/github-actions)
- [Claude Code SDK](https://docs.anthropic.com/en/docs/claude-code/sdk)
- [Claude Code Headless Mode](https://docs.anthropic.com/en/docs/claude-code/sdk/sdk-headless)
- [GitHub Copilot coding agent](https://docs.github.com/en/copilot/concepts/coding-agent/coding-agent)

## CLI Alternative

If you prefer not to use MCP, you can install and use `ldcli` in the agent environment.

Install it with:

```bash
brew tap launchdarkly/homebrew-tap
brew install ldcli
ldcli login
```

If you use this path, make sure the agent environment can actually execute `ldcli` and access its auth state. In sandboxed runners that usually means:

- `ldcli` is on `PATH` inside the agent runtime
- required auth files or environment variables are visible to the agent
- the sandbox allows the command to run

Docs: [LaunchDarkly CLI](https://launchdarkly.com/docs/home/getting-started/ldcli), [LaunchDarkly CLI commands](https://launchdarkly.com/docs/home/getting-started/ldcli-commands), [LaunchDarkly local MCP server](https://launchdarkly.com/docs/home/getting-started/mcp-local)

## Recommended Defaults


| Setting           | Default                                         |
| ----------------- | ----------------------------------------------- |
| Max flags per run | `3`                                             |
| Branch            | `chore/launchdarkly-flag-cleanup-YYYY-MM-DD`    |
| Commit message    | `chore(flags): remove stale LaunchDarkly flags` |
| PR mode           | `Draft`                                         |


## Useful Repo-Specific Inputs

Tell the runner anything it cannot reliably infer from the repo.

Validation example:

```text
To validate code changes, run the actual repo commands for the affected package or app, for example:
pnpm --filter <package> typecheck
pnpm --filter <package> test
npm run test --workspace <package>

If the changed package is unclear, run the root typecheck and test commands.
```

Guardrails example:

```text
Do not edit generated files directly. Skip migrations, seeds, infrastructure config, and files under vendor/.
```

Monorepo example:

```text
Keep changes inside the package where the flag is used unless adjacent shared tests or fixtures are clearly flag-specific.
```

Notification example:

```text
If a chat connector is available, send a short message after opening the draft PR with the PR link, flags removed, validation result, and a reminder that LaunchDarkly was not modified.
```
