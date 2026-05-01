# GitHub Trending Digest

## Overview

`github-trending-digest` looks at the GitHub Trending page, reads the top repositories, and turns them into a short digest.

It keeps GitHub's ranking as-is, then reads each repo's description and README intro to write a short summary.

## How It Works

1. Open the GitHub Trending page for the period you want, usually `weekly`.
2. Take the top repositories in the order GitHub shows them.
3. Visit each repo and read the description plus the start of the README.
4. Write one short TL;DR for each repo.
5. Return the result as a simple Markdown digest.

## When To Use It

Use it when:

- you want a weekly or daily digest of native GitHub Trending repositories;
- you want short summaries, not just repo names and star counts;
- you do not want custom ranking or filtering on top of GitHub Trending.

## Cursor Cloud Usage

1. Open [Cursor Automations](https://cursor.com/automations/new).
2. Name your automation and paste [github-trending-digest.md](/Users/adamchmara/projects/awesome-agent-automations/automations/github-trending-digest/github-trending-digest.md) as the automation prompt.
3. Make sure the runtime can execute `curl`.
4. Set the schedule or run manually, then save the automation.

## Codex App Usage

1. Click `Automation` > `New Automation`.
2. Name your automation and paste [github-trending-digest.md](/Users/adamchmara/projects/awesome-agent-automations/automations/github-trending-digest/github-trending-digest.md) as the automation prompt.
3. Make sure the runtime can execute `curl` to read public GitHub pages.
4. Set the schedule or run manually and save the automation.

## Claude Code Usage

1. Make sure the runtime can execute `curl` and reach public GitHub pages.
2. For repeated checks in an open Claude Code session, use `/loop`, for example:

```text
/loop mondays at 9am Follow the instructions in automations/github-trending-digest/github-trending-digest.md
```

3. For durable Claude-managed automation that survives outside the current session, use `/schedule` or create a Routine in `claude.ai/code/routines`.

## Recommended Defaults

| Setting | Default |
| --- | --- |
| Period | `weekly` |
| Language scope | `all languages` |
| Digest size | `top 10 repositories` |
| Discovery source | `native GitHub Trending only` |
| Delivery | `Markdown report` |
| Browser fallback | `none` |

Additional prompt behavior:

- Keep the ranking exactly as the Trending page presents it.
- Read repository intro content only as deep as needed to summarize safely.
- Keep the writing short and direct.
- Stop with a blocked report if Trending cannot be parsed reliably.

## Useful Inputs

Tell the runner anything it should override from the default weekly all-language slice.

Scope example:

```text
Use the weekly Trending page and limit the digest to the top 8 repositories.
```

Language example:

```text
Use the Rust Trending page for the monthly slice and keep the digest to 12 repositories.
```

Tone example:

```text
Write TL;DRs for senior engineers. Keep them neutral, concrete, and free of hype.
```
