# GitHub CI Speedup Optimizer

## Overview

`github-ci-speedup-optimizer` looks at recent GitHub Actions history, chooses one safe CI bottleneck to test, applies one focused change, waits for a comparable run, and reports the result.

Each run is intentionally narrow: either a validated improvement, an inconclusive result, or a suggestion-only outcome when a safe automated patch is not justified.

## How It Works

1. Reads recent successful CI runs and the workflow files that define current behavior.
2. Finds the slowest recurring workflow or job with a safe validation path.
3. Applies one bounded improvement on a branch.
4. Waits for one comparable CI run and compares it to a recent baseline.
5. Returns `validated improvement`, `inconclusive`, `not validated`, or `suggestion only`.
6. Opens a draft PR only when the improvement is validated.

## When To Use It

- You want a repeatable way to speed up CI without broad refactors.
- You want one tested improvement per run, not a pile of speculative edits.
- You want proof from an actual comparable CI run before opening a PR.

## Prerequisites

- GitHub access with permission to read Actions runs
- A runtime that can execute `git`, push one branch, and observe CI results

## Setup

Use [github-ci-speedup-optimizer.md](/Users/adamchmara/projects/awesome-agent-automations/automations/github-ci-speedup-optimizer/github-ci-speedup-optimizer.md) as the automation prompt.

### Cursor Cloud

1. Open [Cursor Automations](https://cursor.com/automations/new).
2. Create a new automation and paste the prompt.
3. Add GitHub access.
4. Make sure the runtime can run `git` and watch GitHub Actions.
5. Save and schedule the automation.

### Codex App

1. Click `Automation` > `New Automation`.
2. Paste the prompt and add GitHub access.
3. Make sure the environment can push one experimental branch and read CI runs.
4. Save the automation.

### Claude Code

1. Add GitHub access and make sure the runtime can run `git`.
2. For repeated runs in one session, use:

```text
/loop 1w Follow the instructions in automations/github-ci-speedup-optimizer/github-ci-speedup-optimizer.md
```

3. For durable automation, use `/schedule` or a Routine.

## Recommended Defaults

| Setting | Default |
| --- | --- |
| Repository scope | `current repository` |
| Discovery window | `last 14 days of successful CI runs` |
| Candidate count | `1` |
| Branch | `codex-ci-speedup-YYYY-MM-DD` |
| Commit message | `ci: test targeted speedup` |
| Validation path | `branch push first, workflow_dispatch only when needed` |
| Wait timeout | `45 minutes` |
| PR behavior | `open draft PR only after validated improvement` |

Prefer workflow and CI configuration changes over risky product-code edits. If branch CI cannot be observed confidently, or the best patch is too broad, stop with `suggestion only`.

## Useful Inputs

Example workflow scope:

```text
Treat ci.yml and test.yml as the only workflows in scope.
Ignore release and deploy workflows even if they are slower.
```

Example guardrails:

```text
Do not edit application code to make CI faster.
Limit edits to workflow files, composite actions, setup scripts, Dockerfiles used by CI, test runner config, and package-manager config.
```

Example validation rule:

```text
Require at least a 10 percent improvement in the targeted workflow or job before calling the change validated.
If the result is within normal noise, report not validated.
```
