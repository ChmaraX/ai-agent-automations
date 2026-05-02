# GitHub CI Speedup Optimizer

## Overview

`github-ci-speedup-optimizer` reads recent GitHub Actions history across the repository, starts with the slowest recurring workflow or job pattern it can safely validate, picks one bounded speedup to test, creates one branch, applies one change, waits for one CI run, and reports what happened.

Each run attempts at most one change. If the improvement validates and PR tooling is available, it should open a draft PR. If the best idea is too risky, too broad, too hard to apply cleanly, or too hard to verify, it falls back to `suggestion only` instead of forcing a patch.

## How It Works

1. Reads recent successful CI runs across the repository and the files that define the current CI behavior.
2. Starts from the slowest recurring workflow or job pattern with a safe comparable validation path, then chooses one bounded improvement to test.
3. Creates one branch and applies the smallest patch needed to test that idea.
4. Pushes the branch and waits for one comparable CI run, using normal branch-triggered CI when possible and `workflow_dispatch` only when that is the safer supported path.
5. Compares the branch run to the recent baseline and returns `validated improvement`, `inconclusive`, `not validated`, or `suggestion only`.
6. Opens a draft PR only when the improvement is validated. Otherwise it reports the outcome without opening a PR.

## When To Use It

- you want to make a repository's CI meaningfully faster
- you want the automation to find one real bottleneck, test one focused improvement, and prove whether it helped
- you want a bounded result: either a validated draft PR or a clear report explaining why no safe automatic change was made

## Prerequisites

- GitHub access with enough permission to read Actions runs and observe branch CI

## Cursor Cloud Usage

1. Open [Cursor Automations](https://cursor.com/automations/new).
2. Name your automation and paste [github-ci-speedup-optimizer.md](/Users/adamchmara/projects/awesome-agent-automations/automations/github-ci-speedup-optimizer/github-ci-speedup-optimizer.md) as the automation prompt.
3. Add GitHub access through the official GitHub integration, GitHub MCP, or make `gh` available in the runtime.
4. Make sure the runtime can execute `git` and `gh`, push one branch, and observe GitHub Actions runs.
5. Set the schedule or run manually, then save the automation.

## Codex App Usage

1. Click `Automation` > `New Automation`.
2. Name your automation and paste [github-ci-speedup-optimizer.md](/Users/adamchmara/projects/awesome-agent-automations/automations/github-ci-speedup-optimizer/github-ci-speedup-optimizer.md) as the automation prompt.
3. Add the GitHub plugin to Codex, a GitHub MCP server, or make `gh` available in the runtime.
4. Make sure the environment can execute `git`, push one experimental branch, and read or watch GitHub Actions runs.
5. Set the schedule or run manually and save the automation.

## Claude Code Usage

1. Add GitHub access through MCP or make `gh` available in the runtime.
2. Make sure the runtime can execute `git` and `gh`, push one branch, and observe GitHub Actions runs.
3. For repeated checks in an open Claude Code session, use `/loop`, for example:

```text
/loop 1w Follow the instructions in automations/github-ci-speedup-optimizer/github-ci-speedup-optimizer.md
```

4. For durable Claude-managed automation that survives outside the current session, use `/schedule` or create a Routine in `claude.ai/code/routines`.

## Recommended Defaults

| Setting | Default |
| --- | --- |
| Repository scope | `current repository` |
| Discovery window | `recent successful CI runs across the repository from the last 14 days` |
| Validation baseline | `recent comparable runs for the same workflow and trigger path` |
| Candidate count | `1` |
| Branch | `codex-ci-speedup-YYYY-MM-DD` |
| Commit message | `ci: test targeted speedup` |
| Validation path | `branch push first, workflow_dispatch only when needed and safe` |
| Wait timeout | `45 minutes` |
| PR behavior | `open draft PR only after validated improvement` |

- Prefer workflow and CI-adjacent config changes over speculative product-code edits.
- Prefer cache, setup, artifact, and obvious CI-configuration wins before riskier changes such as sharding or runner-class changes.
- If branch CI cannot be observed confidently, stop with `suggestion only` instead of pretending validation happened.
- If the best patch is too difficult or broad to apply as one focused experiment, stop with `suggestion only` and explain the best next manual step.
- If the change validates and trusted PR tooling is available, open a draft PR. Otherwise prepare PR-ready output.

## Useful Repo-Specific Inputs

Tell the runner anything it cannot reliably infer from the repo.

Validation example:

```text
Treat these workflows as the only relevant CI paths for optimization:
- ci.yml
- test.yml

Ignore release and deploy workflows even if they are slower.
```

Guardrails example:

```text
Do not edit application code to make CI faster.
Limit edits to workflow files, composite actions, test runner config, setup scripts, Dockerfiles used by CI, and package-manager config.
```

Benchmark example:

```text
Require at least a 10 percent improvement in the targeted workflow or job before calling the change validated.
If the workflow succeeds but the result is within normal noise, report not validated.
```

Delivery example:

```text
If the improvement validates and trusted PR tooling is available, open a draft PR and include the PR link in the output.
```
