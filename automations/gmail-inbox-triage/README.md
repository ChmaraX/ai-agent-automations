# Gmail Inbox Triage

## Overview

`gmail-inbox-triage` is a short Gmail cleanup automation with a fixed opinionated policy.

It looks only at new unread inbox mail, assigns one semantic label, archives low-value categories by default, keeps high-risk categories in inbox, and returns a short summary only for messages that still need attention.

This is not a reply bot and not a delete workflow.

## Policy

Fixed labels:

- `Newsletter`
- `Receipt`
- `Invoice`
- `Shipment`
- `Security`
- `Account`
- `Personal`
- `Work`
- `Event`
- `Other`

Default archive behavior:

- archive: `Newsletter`, `Receipt`
- conditional archive: `Shipment`, `Event`, some low-value `Account` or `Work` notifications
- keep by default: `Security`, `Invoice`, `Personal`, `Other`

The automation prefers existing matching Gmail labels when they already fit. Otherwise it creates only from the fixed set above.

## How It Works

1. Reads memory first.
2. Uses the last successful run timestamp to decide what counts as new unread mail.
3. Reuses matching Gmail labels when possible.
4. Classifies each message into one label and one action state.
5. Labels every confidently classified message.
6. Archives low-value categories when the archive rule is clearly satisfied.
7. Marks archived messages read by default.
8. Returns a short summary only for items that still need attention.

## Prerequisites

- Gmail access through a supported connector, a Google Workspace MCP server, or the `gws` CLI.
- Permission to apply labels, archive messages, and optionally mark archived messages read.

Memory is optional but strongly recommended.

## Codex / Cursor / CLI Usage

Use [gmail-inbox-triage.md](/Users/adamchmara/projects/awesome-agent-automations/automations/gmail-inbox-triage/gmail-inbox-triage.md) as the automation prompt and enable Gmail plus Memory.

Useful overrides:

```text
Gmail scope override: label:inbox is:unread newer_than:14d -category:promotions
Protected labels or senders: VIP, Important, customer, finance, family
Mark archived messages read: false
```

## Why This Shape

This automation is intentionally opinionated:

- labels describe what the email is
- actions decide what to do with it
- archive is native Gmail archive, not a label
- only low-value categories are auto-archived
- the report is short and focused on exceptions
