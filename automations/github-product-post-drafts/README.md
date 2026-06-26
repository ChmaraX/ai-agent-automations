# GitHub Product Post Drafts

## Overview

This automation looks at recently shipped work and writes simple product-facing draft posts for channels like X or LinkedIn. It is for turning engineering output into launch copy faster.
## How It Works

1. Reads the latest release up to `HEAD`, or falls back to recent merged PRs.
2. Pulls the best available source text from release notes, PR descriptions, labels, changelog entries, and linked issues.
3. Filters out maintenance noise unless the reviewed text clearly says the change was user-visible.
4. Builds one main story, with an optional backup, and writes a few post variants with a short evidence map.

## When To Use It

- You want product-facing post drafts based on shipped work.
- Raw PR lists are too noisy to turn into good posts manually.
- You want one clear angle with a few variants, not a changelog rewrite.
- You want draft copy only, not automatic posting.

## Prerequisites

- GitHub access through the app, MCP, or authenticated `gh`
- Optional Linear access if linked issues add useful product context

## Setup

Use [github-product-post-drafts.md](/Users/adamchmara/projects/ai-agent-automations/automations/github-product-post-drafts/github-product-post-drafts.md) as the automation prompt.

### Cursor Cloud

1. Open [Cursor Automations](https://cursor.com/automations/new).
2. Create a new automation and paste the prompt.
3. Add GitHub access.
4. Optional: add Linear if your GitHub work links to it cleanly.
5. Save and schedule the automation.

### Codex App

1. Click `Automation` > `New Automation`.
2. Paste the prompt and add GitHub access.
3. Optional: add Linear for linked issue context.
4. Save the automation.

### Claude Code

1. Make sure the runtime has GitHub access.
2. Optional: add Linear if you want linked context.
3. For repeated runs in one session, use:

```text
/loop fridays at 9am Follow the instructions in automations/github-product-post-drafts/github-product-post-drafts.md
```

4. For durable automation, use `/schedule` or a Routine.

## Recommended Defaults

| Setting | Default |
| --- | --- |
| Cadence | `weekly` |
| Scope | `one repository per run` |
| Source window | `latest release..HEAD`, otherwise `last 7 days of merged PRs` |
| Review limit | `up to 30 merged PRs or compared commits` |
| Story count | `1 main story, optional 1 backup` |
| Output | `draft posts with style variants` |
| External posting | `none` |

Keep the run opinionated: prefer reviewed text over commit subjects, avoid unsupported value claims, and favor one strong story over many weak rewrites.

## Useful Inputs

Add repo-specific guidance only when GitHub cannot infer it reliably.

Example scope:

```text
Run every Friday morning for the current repository and produce product post drafts from shipped work.
```

Example label policy:

```text
Treat customer-facing, launch, integration, and performance as high-signal.
Treat chore, ci, refactor, and dependencies as noise unless the PR body says otherwise.
```

Example feature-flag rule:

```text
Do not turn feature-flagged work into post drafts unless the PR description says it was enabled for users.
```
