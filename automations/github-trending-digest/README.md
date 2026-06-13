# GitHub Trending Digest

## Overview

This automation reads the current GitHub Trending list and gives quick summaries of the most notable repos. It keeps the original ranking and focuses on why each project matters.
## How It Works

1. Opens the GitHub Trending page for the selected period.
2. Takes the top repositories in GitHub's order.
3. Reads each repo description plus the start of the README.
4. Writes one short TL;DR for each repo.
5. Returns a simple Markdown digest.

## When To Use It

- You want a daily or weekly digest of GitHub Trending.
- You want short summaries, not just repo names and star counts.
- You do not want custom ranking or filtering layered on top.

## Prerequisites

- A runtime that can execute `curl` and reach public GitHub pages

## Setup

Use [github-trending-digest.md](/Users/adamchmara/projects/ai-agent-automations/automations/github-trending-digest/github-trending-digest.md) as the automation prompt.

### Cursor Cloud

1. Open [Cursor Automations](https://cursor.com/automations/new).
2. Create a new automation and paste the prompt.
3. Make sure the runtime can execute `curl`.
4. Save and schedule the automation.

### Codex App

1. Click `Automation` > `New Automation`.
2. Paste the prompt and make sure the runtime can execute `curl`.
3. Save the automation.

### Claude Code

1. Make sure the runtime can execute `curl` and reach public GitHub pages.
2. For repeated runs in one session, use:

```text
/loop mondays at 9am Follow the instructions in automations/github-trending-digest/github-trending-digest.md
```

3. For durable automation, use `/schedule` or a Routine.

## Recommended Defaults

| Setting | Default |
| --- | --- |
| Period | `weekly` |
| Language scope | `all languages` |
| Digest size | `top 10 repositories` |
| Discovery source | `native GitHub Trending only` |
| Delivery | `Markdown report` |

Keep the ranking exactly as Trending presents it, read only as deep as needed to summarize safely, and stop with a blocked report if Trending cannot be parsed reliably.

## Useful Inputs

Example scope:

```text
Use the weekly Trending page and limit the digest to the top 8 repositories.
```

Example language rule:

```text
Use the Rust Trending page for the monthly slice and keep the digest to 12 repositories.
```
