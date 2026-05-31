# Hugging Face Weekly Papers Digest

## Overview

`huggingface-weekly-papers-digest` turns a recent Hugging Face Daily Papers slice into one short paper-first digest.

It is for staying current without reading the whole feed. The automation uses the official `hf` CLI as its source of truth and can optionally add linked Hugging Face artifacts when they clearly help.

## How It Works

1. Uses `hf papers ls` with a defined date window.
2. Builds a bounded candidate set from that slice.
3. Reads the strongest papers with `hf papers info` and `hf papers read`.
4. Optionally checks linked models, datasets, or Spaces when they add useful context.
5. Returns one concise digest, or a short blocked brief if the CLI cannot produce a trustworthy window.

## When To Use It

- You want a weekly paper digest from Hugging Face Daily Papers.
- You want a compact brief, not a broad literature review.
- You prefer a CLI-based workflow over MCP or general web search.

## Prerequisites

- The official `hf` CLI available in the runtime
- Optional Hugging Face authentication if your environment needs it

## CLI Setup

Install the CLI:

```bash
curl -LsSf https://hf.co/cli/install.sh | bash
hf --help
hf papers --help
```

If your environment needs authenticated access:

```bash
hf auth login
```

## Setup

Use [huggingface-weekly-papers-digest.md](/Users/adamchmara/projects/ai-agent-automations/automations/huggingface-weekly-papers-digest/huggingface-weekly-papers-digest.md) as the automation prompt.

### Cursor Cloud

1. Open [Cursor Automations](https://cursor.com/automations/new).
2. Create a new automation and paste the prompt.
3. Authenticate with `hf auth login` if needed.
4. Save and schedule the automation.

### Codex App

1. Make sure the runtime can run `hf`.
2. Click `Automation` > `New Automation` and paste the prompt.
3. Authenticate if needed and save the automation.

### Claude Code

1. Make sure the runtime can run `hf`.
2. For repeated runs in one session, use:

```text
/loop every friday at 9am Follow the instructions in automations/huggingface-weekly-papers-digest/huggingface-weekly-papers-digest.md
```

3. For durable automation, use `/schedule` or a Routine.

## Recommended Defaults

| Setting | Default |
| --- | --- |
| Time window | `current or most recent week` |
| Candidate pool | `up to 20 papers` |
| Final shortlist | `up to 5 papers` |
| Output | `Markdown digest` |
| Delivery mode | `report-only` |
| Retrieval path | `hf CLI only` |

Use `hf papers ls` as the source of truth for the window, treat popularity as a clue rather than a substitute for reading, and skip papers with thin summaries or unclear practical value.

## Useful Inputs

Example topic focus:

```text
Keep the weekly window, but focus on multimodal, agents, and speech papers.
```

Example audience:

```text
Write the brief for applied ML engineers. Emphasize what is new, what is interesting, and what they might want to read first.
```

Example selection rule:

```text
Prefer agent systems, multimodal reasoning, and practical tooling papers over more theoretical items this week.
```
