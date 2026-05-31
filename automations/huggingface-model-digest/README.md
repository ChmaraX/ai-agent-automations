# Hugging Face Model Digest

## Overview

`huggingface-model-digest` turns recent public Hugging Face activity into one short Markdown digest.

It looks at a bounded recent window, shortlists only a few notable models, and reads model-card intro context before summarizing. The goal is signal, not a raw newest-upload feed.

## How It Works

1. Searches a recent Hugging Face window.
2. Builds a bounded candidate pool of recent or newly-rising models.
3. Uses lightweight signals such as recency, likes, downloads, and card completeness to shortlist candidates.
4. Reads each shortlisted model card or `README.md` intro before writing the digest.
5. Returns concise per-model summaries with compact supporting signals and confidence.

## When To Use It

- You want a quick digest of notable recent models on the Hub.
- You want model-card-backed summaries rather than a popularity list.
- You want a compact report, not a broad ecosystem scan.

## Prerequisites

- Access to public Hugging Face metadata through MCP or the `hf` CLI
- Ability to read model-card intro text or repository `README.md`
- Optional authentication if your environment needs higher limits

## Setup

Use [huggingface-model-digest.md](/Users/adamchmara/projects/ai-agent-automations/automations/huggingface-model-digest/huggingface-model-digest.md) as the automation prompt.

### Cursor Cloud

1. Open [Cursor Automations](https://cursor.com/automations/new).
2. Create a new automation and paste the prompt.
3. Add Hugging Face access through MCP or make `hf` available.
4. Authenticate if needed and save the automation.

### Codex App

1. Make sure the runtime has Hugging Face access through MCP or `hf`.
2. Click `Automation` > `New Automation` and paste the prompt.
3. Authenticate if needed and save the automation.

### Claude Code

1. Add Hugging Face MCP or make `hf` available.
2. For repeated runs in one session, use:

```text
/loop mondays at 9am Follow the instructions in automations/huggingface-model-digest/huggingface-model-digest.md
```

3. For durable automation, use `/schedule` or a Routine.

## Recommended Defaults

| Setting | Default |
| --- | --- |
| Time window | `last 7 days` |
| Scope | `global public Hub` |
| Candidate pool | `up to 30 models` |
| Final shortlist | `up to 6 models` |
| Output | `Markdown digest` |
| Delivery mode | `report-only` |

Prefer fewer well-supported picks over padded coverage, treat likes and downloads as ranking clues rather than proof, and skip items with thin or unreadable cards.

## Useful Inputs

Example scope:

```text
Keep the default weekly window, but limit discovery to multimodal and agents-related models.
```

Example audience:

```text
Write the digest for product-minded engineers. Keep it concrete and explain why each model matters in practice.
```

Example noise control:

```text
Down-rank obvious repackagings, mirrors, and quantization-only reposts unless the model card explains a meaningful new use case.
```
