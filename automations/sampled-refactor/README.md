# Sampled Refactor

## Overview

`sampled-refactor` inspects a real random slice of a JavaScript or TypeScript repository, applies at most one coherent behavior-preserving refactor, validates it, and opens a draft PR or prepares PR-ready output.

Use it for recurring maintainability work when you want small automated improvements instead of a report-only scout.

## How It Works

1. Searches the repository for source files while excluding obvious non-source paths.
2. Runs one explicit random sampling command and records the sampled output.
3. Chooses a small subset of sampled files for inspection and selects at most one coherent refactor.
4. Expands scope only when needed to complete that refactor safely.
5. Runs targeted validation and opens a draft PR, or returns a short no-change summary.

## When To Use It

- You want recurring small refactors without hand-picking targets.
- You want one reviewable refactor per run, not a broad cleanup sweep.
- You want no-op behavior when nothing sampled is safe enough.

## Prerequisites

- Shell access for file discovery and random sampling
- Validation commands for the touched surface
- PR tooling if you want automatic draft PR creation

## Setup

Use [sampled-refactor.md](/Users/adamchmara/projects/awesome-agent-automations/automations/sampled-refactor/sampled-refactor.md) as the automation prompt.

### Cursor Cloud

1. Open [Cursor Automations](https://cursor.com/automations/new).
2. Create a new automation and paste the prompt.
3. Add PR tooling if needed.
4. Make sure the runtime can run sampling and validation commands.
5. Save and schedule the automation.

### Codex App

1. Click `Automation` > `New Automation`.
2. Paste the prompt and add PR tooling if needed.
3. Make sure the environment can run sampling and validation commands.
4. Save the automation.

### Claude Code

1. Make sure the runtime can execute discovery, randomization, and validation commands.
2. For repeated runs in one session, use:

```text
/loop 1d Follow the instructions in automations/sampled-refactor/sampled-refactor.md
```

3. For durable automation, use `/schedule` or a Routine.

## Recommended Defaults

| Setting | Default |
| --- | --- |
| Candidate files sampled | `8` |
| Final chosen slice | `3-5` files |
| Default languages | `js`, `jsx`, `ts`, `tsx` |
| Implemented refactors per run | `1` |
| Preferred randomizer | `shuf`, fallback `sort -R` |
| Branch | `refactor/sampled-refactor-YYYY-MM-DD` |
| Commit message | `refactor(code-health): apply sampled refactor` |
| PR mode | `Draft` |

If safe random sampling cannot run, no candidate has a credible validation path, or nothing sampled is strong enough, stop without edits.

## Useful Inputs

Example guardrails:

```text
Do not edit generated files directly.
Skip migrations, seeds, infrastructure config, and files under vendor/.
```

Example validation rule:

```text
For validation, run the actual repo commands for the affected package or app, for example:
pnpm --filter api exec tsc --noEmit
pnpm --filter worker test
```

Example scope rule:

```text
Replace `find .` with a narrower root such as `find apps/web` or add exclusions like `! -path "*/legacy/*"` if needed.
```
