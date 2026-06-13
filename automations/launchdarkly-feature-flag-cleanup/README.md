# LaunchDarkly Feature Flag Cleanup

## Overview

This automation looks for stale LaunchDarkly flag code that can likely be removed, makes the cleanup, and validates the result. It is for keeping temporary flag paths from lingering.
## How It Works

1. Finds stale temporary flags that look safe to remove.
2. Confirms a stable served value in LaunchDarkly.
3. Removes flag-specific code paths and clearly orphaned references.
4. Runs repo validation and prepares a draft PR or PR-ready output.

## When To Use It

- You have old temporary flags that should have been cleaned up after rollout.
- You want LaunchDarkly evidence before removing code.
- You want code cleanup automated, but LaunchDarkly mutation kept manual.

## Prerequisites

- LaunchDarkly access through MCP or `ldcli`
- Repo access and validation commands for the affected codebase
- GitHub or equivalent PR tooling if you want automatic PR creation

## Setup

Use [launchdarkly-feature-flag-cleanup.md](/Users/adamchmara/projects/ai-agent-automations/automations/launchdarkly-feature-flag-cleanup/launchdarkly-feature-flag-cleanup.md) as the automation prompt.

### Cursor Cloud

1. Open [Cursor Automations](https://cursor.com/automations/new).
2. Create a new automation and paste the prompt.
3. Add LaunchDarkly feature management MCP or provide `ldcli`.
4. Add PR tooling if you want automatic draft PR creation.
5. Save and schedule the automation.

### Codex App

1. Add LaunchDarkly access through MCP or `ldcli`.
2. Click `Automation` > `New Automation` and paste the prompt.
3. Add GitHub or other PR tooling if needed.
4. Save the automation.

### Claude Code

1. Add LaunchDarkly MCP or make `ldcli` available and authenticated.
2. Make sure the runtime can access the repository and run validation.
3. For repeated runs in one session, use:

```text
/loop 1d Follow the instructions in automations/launchdarkly-feature-flag-cleanup/launchdarkly-feature-flag-cleanup.md
```

4. For durable automation, use `/schedule` or a Routine.

## CLI Alternative

If you prefer not to use MCP, install and authenticate `ldcli`:

```bash
brew tap launchdarkly/homebrew-tap
brew install ldcli
ldcli login
```

Make sure the automation runtime can execute `ldcli` and access its auth state.

## Recommended Defaults

| Setting | Default |
| --- | --- |
| Max flags per run | `3` |
| Branch | `chore/launchdarkly-flag-cleanup-YYYY-MM-DD` |
| Commit message | `chore(flags): remove stale LaunchDarkly flags` |
| PR mode | `Draft` |

Keep runs conservative: skip unclear candidates, avoid generated files and infrastructure changes, and keep LaunchDarkly changes manual after merge.

## Useful Inputs

Example validation rule:

```text
Run the repo validation commands for the affected package or app.
If the changed package is unclear, run the root typecheck and test commands.
```

Example guardrails:

```text
Do not edit generated files directly.
Skip migrations, seeds, infrastructure config, and files under vendor/.
```

Example monorepo rule:

```text
Keep changes inside the package where the flag is used unless adjacent shared tests or fixtures are clearly flag-specific.
```

## Docs

- [LaunchDarkly Hosted MCP Server](https://launchdarkly.com/docs/home/getting-started/mcp-hosted)
- [LaunchDarkly CLI](https://launchdarkly.com/docs/home/getting-started/ldcli)
- [Codex Automations](https://openai.com/academy/codex-automations)
