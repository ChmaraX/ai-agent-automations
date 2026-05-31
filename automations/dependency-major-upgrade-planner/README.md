# Dependency Major Upgrade Planner

## Overview

`dependency-major-upgrade-planner` scans the current repository for direct dependencies that have newer stable major versions, reads the official migration guidance for the best candidates, and turns only the high-confidence ones into Linear migration tasks.

It is planning-focused, not code-changing. Each run stays bounded, prefers official maintainer guidance over community chatter, and falls back to report-only output when the migration path is too ambiguous or write access is unavailable.

## How It Works

1. Detects manifests, lockfiles, workspaces, and package-manager files in the current repository.
2. Finds direct dependencies with newer stable major releases using read-only package-manager or registry metadata.
3. Chooses a small candidate set for deep review instead of trying to analyze every outdated package.
4. Reads official changelogs, release notes, migration guides, and upgrade docs for the selected packages.
5. Inspects the local codebase for likely affected usage surfaces such as imports, config files, scripts, plugins, adapters, and framework integration points.
6. Creates Linear issues only for candidates with a clear major target, credible official guidance, and concrete repo-specific action items.
7. Uses a deterministic title, dedupe key, and standard label so later runs can find equivalent open work before creating new issues.
8. Reports prepared-but-not-created candidates when the evidence is incomplete, the docs are weak, or writes are blocked.

## When To Use It

- you want a recurring shortlist of major dependency upgrades that are worth planning
- the repository has standard manifests and lockfiles
- the dependencies in scope publish usable migration docs or release notes
- the team tracks upgrade work in Linear

## Prerequisites

- repository read access
- package-manager or registry read access for outdated-version discovery
- web or GitHub access to official package documentation and release notes
- Linear access if you want issue creation instead of report-only output

## Cursor Cloud Usage

1. Open [Cursor Automations](https://cursor.com/automations/new).
2. Name your automation and paste [dependency-major-upgrade-planner.md](/Users/adamchmara/projects/ai-agent-automations/automations/dependency-major-upgrade-planner/dependency-major-upgrade-planner.md) as the automation prompt.
3. Add repository access for manifest and code inspection.
4. Add web, GitHub, or equivalent read access so the runner can read official migration guides and release notes.
5. Add Linear access through the official MCP server or managed connector if you want issue creation.
6. Save the automation and start with a low-frequency schedule until the issue quality looks right.

## Codex App Usage

1. Install the official Linear MCP server in Codex if you want issue creation:
   ```bash
   codex mcp add linear --url https://mcp.linear.app/mcp
   codex mcp login linear
   codex mcp list
   ```
2. Click `Automation` > `New Automation`.
3. Name your automation and paste [dependency-major-upgrade-planner.md](/Users/adamchmara/projects/ai-agent-automations/automations/dependency-major-upgrade-planner/dependency-major-upgrade-planner.md) as the automation prompt.
4. Make sure the runtime can inspect the repository and read official package docs, release notes, and migration guides.
5. Add Linear access only if you want the run to create issues instead of producing a report.
6. Set the schedule or run manually and save the automation.

## Claude Code Usage

1. Add the official Linear MCP server in Claude Code if you want issue creation:
   ```bash
   claude mcp add --transport http linear https://mcp.linear.app/mcp
   claude mcp list
   ```
2. Open Claude Code and run `/mcp` to authenticate with Linear in your browser.
3. Make sure the runtime can inspect the repository and read official release or migration documentation.
4. For repeated checks in an open Claude Code session, use `/loop`, for example:

```text
/loop 1w Follow the instructions in automations/dependency-major-upgrade-planner/dependency-major-upgrade-planner.md
```

5. For durable Claude-managed automation, use `/schedule` or create a Routine in `claude.ai/code/routines`.

## Recommended Defaults

| Setting | Default |
| --- | --- |
| Repository scope | `current repository` |
| Dependency scope | `direct dependencies only` |
| Update type | `stable major versions only` |
| First-pass candidate cap | `15 packages` |
| Deep-review cap | `3 packages` |
| Issue creation policy | `high-confidence candidates only` |
| Source priority | `official maintainer docs first` |
| Duplicate handling | `search Linear first using title pattern, dedupe key, and label; skip equivalent open work` |
| Fallback mode | `report-only when evidence or writes are blocked` |

Keep the run conservative: prefer framework, runtime, and build-critical packages over low-impact tooling, use official migration docs to justify the work, and keep created Linear issues concrete and dedupe-friendly.

## Prompt Inputs

Add context only when priority or scope cannot be inferred cleanly, for example:

```text
Prioritize framework, runtime, database, auth, API client, and build-tool majors ahead of testing or lint-only packages.
Focus on the web and api workspaces.
Ignore internal playgrounds, example apps, and archived packages.
Create Linear issues only when official migration guidance exists and at least two repo-specific action items can be named.
```

## Docs

- [Linear MCP](https://mcp.linear.app/mcp)
- [Codex Automations](https://openai.com/academy/codex-automations)
