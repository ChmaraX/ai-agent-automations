# Support Docs Gap Drafter

## Overview

This automation looks for repeated support friction and turns it into a draft documentation update. It helps teams close small docs gaps that keep creating tickets.
## How It Works

1. Starts from an explicit support source and bounded support scope from the prompt's required run-configuration block.
2. Reads only the support slice needed to identify repeated questions, confusion, workaround requests, or escalation patterns.
3. Clusters recurring issues by product area, feature, setup step, error, integration, billing concept, or user goal.
4. Checks the docs repo, local docs tree, and optional published docs site for existing coverage.
5. Classifies each strong cluster as `missing doc`, `outdated`, `hard to find`, `unclear`, or `not docs-related`.
6. Ranks the best documentation opportunities and drafts one small docs change for the top gap.
7. Opens a draft PR only when the run configuration explicitly allows it and the fix is high-confidence and clearly local to the docs source.

```mermaid
sequenceDiagram
    participant Agent
    participant Support
    participant Docs
    participant Git as Docs Repo

    Agent->>Support: Read bounded recent support scope
    Support-->>Agent: Threads, messages, tags, account context
    Agent->>Docs: Search current docs coverage
    Docs-->>Agent: Matching pages, repo hits, site pages
    Agent->>Git: Draft one small docs fix when allowed
    Note right of Agent: Preview-first; PRs only in explicit draft-PR mode
```

## When To Use It

- repeated support questions keep landing on the team
- onboarding, setup, integration, or billing confusion is creating avoidable support load
- docs exist but customers still cannot find or use the answer
- you want one reviewable docs improvement grounded in real support evidence

## Prerequisites

- One connected support source with readable conversation history, such as Plain, Zendesk, Intercom, Help Scout, Gmail, or Slack
- One readable docs source: a local docs tree, a docs repo, or a published docs site
- Optional git provider write access if you want the draft PR path
- A completed run-configuration block with one real support scope and one real primary docs source

If the support source or docs source is vague, the run should stop instead of guessing.

## Cursor Cloud Usage

1. Open [Cursor Automations](https://cursor.com/automations/new).
2. Name your automation and paste [support-docs-gap-drafter.md](/Users/adamchmara/projects/ai-agent-automations/automations/support-docs-gap-drafter/support-docs-gap-drafter.md) as the automation prompt.
3. Add the support system you actually use through MCP, a connector, or an approved workspace integration.
4. Add docs access through the current repo, a connected GitHub or GitLab integration, or a readable published docs site. If site inspection matters, also allow browser or search access.
5. Replace the required run-configuration block near the top of the prompt before saving the automation.
6. Start in `preview_only` mode. Enable `draft_pr_if_writable` only after you trust the selected changes.

## Codex App Usage

1. Connect the support source you actually use.
2. Make the docs source readable in the runtime through the current repo, a docs repo, or a published docs site.
3. Click `Automation` > `New Automation`.
4. Paste [support-docs-gap-drafter.md](/Users/adamchmara/projects/ai-agent-automations/automations/support-docs-gap-drafter/support-docs-gap-drafter.md) as the automation prompt.
5. Replace the required run-configuration block before saving the automation.
6. Keep the first runs in `preview_only` mode. Only switch to `draft_pr_if_writable` after confirming the repo path and voice are correct.

## Claude Code / Codex CLI / Copilot Usage

1. Make one support source available through MCP, a connector, or the environment's trusted CLI path.
2. Make the docs source readable through the current repo, a mounted docs repo, GitHub or GitLab access, or a published docs site.
3. Replace the run-configuration values at the top of the prompt before using `/loop` or `/schedule`. For example:

```text
Support source and bounded scope: Plain workspace Acme; external customer threads from the last 14 days; exclude spam, test tenants, and internal dogfooding
Primary docs source: current repo under docs/
Secondary docs source: https://docs.acme.dev
Docs change mode: preview_only
```

4. Keep this automation review-first. If you later want issue creation, Slack delivery, or backlog filing, split those into separate automations.
5. For repeated checks in an open Claude Code session, use `/loop`, for example:

```text
/loop mondays at 9am Follow the instructions in automations/support-docs-gap-drafter/support-docs-gap-drafter.md
```

## Recommended Defaults

| Setting | Default |
| --- | --- |
| Support window | `last 14 days` |
| First-pass support pool | `up to 60 conversations` |
| Final gap count | `up to 5 ranked gaps` |
| Representative examples per gap | `1 to 3` |
| Drafted docs fix | `1 primary gap only` |
| Write mode | `preview_only` |
| Delivery | `markdown report with one docs change draft and optional PR link` |

Keep the run conservative: prefer repeated gaps over one-off complaints, down-rank issues that docs alone cannot fix, and open a draft PR only for a high-confidence local docs patch.

## Prompt Inputs

Replace the run-configuration block with something like:

```text
Support source and bounded scope: Plain workspace Acme; last 14 days; external customer conversations only
Primary docs source: current repo under docs/
Secondary docs source: https://docs.acme.dev
Docs change mode: preview_only
```

Add policy only when needed, for example: keep changes inside existing docs sections, and never copy sensitive customer data into the report or patch.

## Docs

- [Codex Automations](https://openai.com/academy/codex-automations)
