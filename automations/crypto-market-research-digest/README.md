# Crypto Market Research Digest

## Overview

`crypto-market-research-digest` turns public crypto market, DeFi, SEC, and OFAC data into one daily research digest.

It uses a fixed source set, keeps the output report-only, and produces an HTML companion artifact for easier review. The goal is a market-structure and compliance snapshot, not trading advice.

## Preview

![HTML report preview](./assets/html-report-preview.png)

## How It Works

1. Resolves the current UTC run date and loads prior normalized state when available.
2. Fetches public Binance, DeFiLlama, SEC, and OFAC data.
3. Normalizes the data into a compact working snapshot and compares it against prior state when persistent state exists.
4. Builds a digest covering market pulse, DeFi structure, liquidity moves, yield outliers, SEC watchlist filings, and OFAC screening signals.
5. Returns one Markdown digest and writes one HTML artifact.

## When To Use It

- You want a recurring crypto market and compliance snapshot.
- You want a fixed-source digest rather than loose web-search summaries.
- You want report-only output with an HTML companion.

## Prerequisites

- A runtime that can execute `python3`
- Optional persistent state if you want change detection across runs

## Setup

Use [crypto-market-research-digest.md](./crypto-market-research-digest.md) as the automation prompt and make sure the runtime can execute:

```bash
python3 automations/crypto-market-research-digest/run_digest.py --workspace .
```

### Cursor Cloud

1. Open [Cursor Automations](https://cursor.com/automations/new).
2. Create a new automation and paste the prompt.
3. Make sure the runtime can run the digest script.
4. Save and schedule the automation.

### Codex App

1. Click `Automation` > `New Automation`.
2. Paste the prompt and make sure the workspace contains this repo.
3. Save the automation.

### Claude Code

1. Run from the repo root with the digest script.
2. For repeated runs in one session, use:

```text
/loop weekdays at 8am Follow the instructions in automations/crypto-market-research-digest/crypto-market-research-digest.md
```

3. For durable automation, use `/schedule` or a Routine.

## Recommended Defaults

| Setting | Default |
| --- | --- |
| Run date | `current UTC date` |
| Market slice | `Binance 24h snapshot for BTC, ETH, SOL, BNB, XRP, DOGE, ADA, AVAX, LINK` |
| SEC lookback | `last 7 calendar days` |
| Yield outlier threshold | `APY above 25%` |
| Preferred yield TVL floor | `at least $5M` |
| Delivery | `Markdown digest + static HTML artifact` |
| Mode without state | `snapshot-only` |

Treat Binance data as exchange-level activity, mark unavailable source fields as unavailable, and keep SEC and OFAC sections review-oriented rather than legal or investment conclusions.

## Useful Inputs

Example coverage rule:

```text
Keep the default digest structure, but expand the Binance tracked pair set to include TONUSDT and SUIUSDT.
```

Example risk filter:

```text
Raise the yield outlier threshold to 40% APY and ignore pools below $10M TVL.
```
