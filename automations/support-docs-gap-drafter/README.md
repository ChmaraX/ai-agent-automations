# Support Docs Gap Drafter

## Overview

`support-docs-gap-drafter` reads a bounded slice of recent support conversations, finds repeated questions or confusion that look fixable with documentation, checks the current docs, and drafts one small docs improvement for the strongest gap.

It is not a generic support summary. The job is to find fix-worthy documentation gaps: missing docs, stale docs, hard-to-find answers, or technically correct docs that are still confusing in practice.

Use it when support keeps answering the same question, explaining the same workaround, or escalating the same onboarding or integration confusion, and you want one concrete docs fix instead of another dashboard of complaints.

## How It Works

1. Starts from an explicit support source and bounded support scope from the prompt's required run-configuration block.
2. Reads only the support slice needed to identify repeated questions, confusion, workaround requests, or escalation patterns.
3. Clusters recurring issues by product area, feature, setup step, error, integration, billing concept, or user goal.
4. Checks the docs repo, local docs tree, and optional published docs site for existing coverage.
5. Classifies each strong cluster as `missing doc`, `outdated`, `hard to find`, `unclear`, or `not docs-related`.
6. Ranks the best documentation opportunities and drafts one small docs change for the top gap.
7. Stays preview-first by default. If the run configuration explicitly allows draft PR creation and the selected gap is high-confidence, local, and clearly docs-related, it may open a draft PR for the selected docs fix.

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
- support and docs teams need a weekly docs-gap sweep
- onboarding, setup, integration, or billing confusion is creating avoidable support load
- existing docs might be present but customers still cannot find or use the answer
- you want one reviewable docs improvement grounded in real support evidence

## Prerequisites

- one connected support source with readable conversation history, such as Plain, Zendesk, Intercom, Help Scout, Gmail, or Slack
- one readable docs source:
  - a local docs tree in the current repo or mounted workspace;
  - a connected GitHub or GitLab docs repo; or
  - a published docs site when repo access is unavailable
- optional git provider write access only if you want the automation to open a draft PR
- a completed required run-configuration block in the prompt with one real support scope and one real primary docs source

This automation works best when the support source is explicit and the docs source is stable. If either side is vague, the run should stop instead of guessing.

## Cursor Cloud Usage

1. Open [Cursor Automations](https://cursor.com/automations/new).
2. Name your automation and paste [support-docs-gap-drafter.md](/Users/adamchmara/projects/awesome-agent-automations/automations/support-docs-gap-drafter/support-docs-gap-drafter.md) as the automation prompt.
3. Add the support system you actually use through MCP, a connector, or an approved workspace integration.
4. Add docs access through the current repo, a connected GitHub or GitLab integration, or a readable published docs site. If site inspection matters, also allow browser or search access.
5. Replace the required run-configuration block near the top of the prompt before saving the automation.
6. Start in `preview_only` mode until the gap quality is stable. Enable `draft_pr_if_writable` only after you trust the selected changes.

## Codex App Usage

1. Connect the support source you actually use.
   - Plain: add the Plain MCP server when Plain is your source of truth.
   - Gmail or Slack: enable the matching plugin or connector.
   - Other support platforms: use the MCP or connector path your environment already trusts.
2. Make the docs source readable in the runtime.
   - local docs repo or mounted workspace;
   - GitHub or GitLab integration for a docs repository; or
   - browser access for a published docs site.
3. Click `Automation` > `New Automation`.
4. Paste [support-docs-gap-drafter.md](/Users/adamchmara/projects/awesome-agent-automations/automations/support-docs-gap-drafter/support-docs-gap-drafter.md) as the automation prompt.
5. Replace the required run-configuration block before saving the automation.
6. Keep the first runs in `preview_only` mode. Only switch to `draft_pr_if_writable` after reviewing a few outputs and confirming the repo path and voice are correct.

## Claude Code / Codex CLI / Copilot Usage

1. Make one support source available through MCP, a connector, or the environment's trusted CLI path.
2. Make the docs source readable through the current repo, a mounted docs repo, GitHub or GitLab access, or a published docs site.
3. Replace the required run-configuration values at the top of the prompt before using `/loop` or `/schedule`. For example:

```text
Support source and bounded scope: Plain workspace Acme; external customer threads from the last 14 days; exclude spam, test tenants, and internal dogfooding
Primary docs source: current repo under docs/
Secondary docs source: https://docs.acme.dev
Docs change mode: preview_only
```

4. Keep this automation review-first. If you later want issue creation, Slack delivery, or multi-gap backlog filing, split those into separate automations.
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

Additional prompt behavior:

- Use the support system as the source of truth for what customers actually asked and where support effort is going.
- Use the docs repo or docs site as the source of truth for current published guidance.
- Cluster semantically similar questions even when the wording differs.
- Prefer repeated gaps over one-off complaints.
- Down-rank issues that are really bugs, account-specific exceptions, contractual edge cases, or policy decisions that docs alone cannot fix.
- Prefer the smallest docs change that would materially reduce future support effort.
- If docs coverage cannot be checked reliably, return a partial result instead of pretending the gap is confirmed.
- Open a draft PR only for a `high` confidence gap with a clear, local docs patch. Otherwise keep the run preview-only even when the repo is writable.

## Useful Workspace-Specific Inputs

Replace the required run-configuration block in the prompt with content like this before scheduling runs.

Plain scope example:

```text
Support source and bounded scope: Plain workspace Acme; last 14 days; external customer conversations only; exclude spam, internal dogfooding, and test tenants
Primary docs source: current repo under docs/
Secondary docs source: https://docs.acme.dev
Docs change mode: preview_only
```

Zendesk scope example:

```text
Support source and bounded scope: Zendesk tickets tagged onboarding or api from the last 7 days; exclude billing disputes and abuse reports
Primary docs source: github.com/acme/docs
Secondary docs source: https://docs.acme.dev
Docs change mode: draft_pr_if_writable
```

Slack support example:

```text
Support source and bounded scope: Slack channels #support-api and #support-onboarding from the last 10 days; exclude internal-only debugging threads
Primary docs source: current repo under handbook/docs/
Secondary docs source: OPTIONAL_NONE
Docs change mode: preview_only
```

Change policy example:

```text
Only draft changes that stay inside existing docs sections, FAQs, troubleshooting, setup steps, or cross-links.
Do not invent new product behavior, roadmap promises, or pricing policy.
```

Sensitive-handling example:

```text
Never copy customer email addresses, API keys, billing identifiers, or long private message excerpts into the report or patch.
Keep representative wording to short excerpts only.
```
