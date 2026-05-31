# Branch Change Test Coverage

## Overview

`branch-change-test-coverage` inspects the current branch or a recent merged change set, identifies the main behavior that should be covered by tests, adds the minimum meaningful missing coverage, validates it, and opens a draft PR only when the result is trustworthy.

It is not a generic coverage maximizer. The goal is to cover the important behavior in a coherent change set, not to chase percentages or generate low-signal tests.

## How It Works

1. Discovers a trustworthy diff from the current branch or default branch.
2. Identifies the main behavior changes that should be covered.
3. Updates nearby tests or adds small new tests only when local conventions are clear.
4. Runs the narrowest relevant validation for the touched area.
5. Opens a draft PR or stops with a clear blocked report.

## When To Use It

- You want missing test coverage added for a real branch change.
- You want focused, reviewable tests rather than a broad coverage campaign.
- You want report-only output when the branch is too broad or validation is unclear.

## Prerequisites

- `git`, repository test commands, and validation access
- PR tooling if you want automatic draft PR creation

## Setup

Use [branch-change-test-coverage.md](/Users/adamchmara/projects/awesome-agent-automations/automations/branch-change-test-coverage/branch-change-test-coverage.md) as the automation prompt.

### Cursor Cloud

1. Open [Cursor Automations](https://cursor.com/automations/new).
2. Create a new automation and paste the prompt.
3. Add PR tooling if needed.
4. Make sure the runtime can run the repository's targeted test commands.
5. Save and schedule the automation.

### Codex App

1. Click `Automation` > `New Automation`.
2. Paste the prompt and add PR tooling if needed.
3. Make sure the environment can run the relevant test commands.
4. Save the automation.

### Claude Code

1. Make sure the runtime has `git`, test commands, and PR tooling if needed.
2. For repeated runs in one session, use:

```text
/loop 1d Follow the instructions in automations/branch-change-test-coverage/branch-change-test-coverage.md
```

3. For durable automation, use `/schedule` or a Routine.

## Recommended Defaults

| Setting | Default |
| --- | --- |
| PR scope | `one coherent branch change set` |
| Test file count | `only what the change justifies` |
| Branch | `test/branch-change-test-coverage-YYYY-MM-DD` |
| Commit message | `test: improve branch change coverage` |
| PR mode | `Draft` |

Prefer existing nearby test files, skip snapshot-heavy or fragile test additions, and stop when the branch is too broad or conventions are unclear.

## Useful Inputs

Example validation rule:

```text
For validation, prefer:
pnpm --filter api test -- src/auth/session.test.ts
pnpm --filter web test -- src/lib/permissions.test.ts
pytest tests/auth/test_session.py
```

Example guardrails:

```text
Do not edit end-to-end tests.
Do not touch snapshot files.
Skip changes that need database setup beyond existing local test helpers.
```

Example priority rule:

```text
Prioritize auth, billing, API validation, parsing, and permission changes.
Prefer covering the main happy path plus the most meaningful edge case when both changed in the branch.
```
