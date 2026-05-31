# Scan Codebase Vulnerabilities

## Overview

`scan-codebase-vulnerabilities` is a scheduled or manual application-security reviewer for a repository. It looks for validated medium, high, or critical vulnerabilities with a real attack path and returns a concise Slack summary or preview.

It is for exploitable code-path review, not dependency version remediation. If you want package upgrade PRs, use `dependency-vulnerability-autofix` instead.

## How It Works

1. Maps the repository's key trust boundaries and exposed entry points.
2. Searches high-signal attack surfaces such as auth, request handlers, raw SQL, shell execution, file access, templating, webhooks, and secret handling.
3. Verifies exploitability with concrete code tracing.
4. Reports only validated medium+ findings with a reachable sink, attacker-controlled input, and clear impact.
5. Sends a concise digest or returns preview output when delivery is unavailable.

## When To Use It

- You want recurring repository-level appsec review.
- You want only validated medium+ findings, not speculative lint-style output.
- You want reporting, not code changes.

## Setup

Use [scan-codebase-vulnerabilities.md](/Users/adamchmara/projects/awesome-agent-automations/automations/scan-codebase-vulnerabilities/scan-codebase-vulnerabilities.md) as the automation prompt.

### Cursor Cloud

1. Open [Cursor Automations](https://cursor.com/automations/new).
2. Create a new automation and paste the prompt.
3. Add Slack or another messaging connector if you want delivery outside preview output.
4. Save and schedule the automation.

### Codex App

1. Click `Automation` > `New Automation`.
2. Paste the prompt and add Slack or another messaging connector if needed.
3. Save the automation.

### Claude Code

1. For repeated runs in one session, use:

```text
/loop 1d Follow the instructions in automations/scan-codebase-vulnerabilities/scan-codebase-vulnerabilities.md
```

2. For durable automation, use `/schedule` or a Routine.

## Recommended Defaults

| Setting | Default |
| --- | --- |
| Review mode | `full repository` |
| Severity threshold | `medium and above` |
| Max findings in final digest | `5` |
| Delivery | `Slack or preview output` |
| Code changes | `never` |

Skip anything that cannot be defended with a concrete attack path. If nothing qualifies, return a short no-findings summary instead of padding the report.

## Useful Inputs

Example scope:

```text
Prioritize the API gateway, auth services, background webhook workers, and admin surfaces.
Ignore test fixtures, local scripts, and generated clients unless they are reachable in production.
```

Example threat model:

```text
Treat anonymous users, authenticated users, tenant admins, and external webhook senders as separate attacker classes.
Assume the most sensitive assets are account takeover paths, secrets, billing actions, and cross-tenant data access.
```
