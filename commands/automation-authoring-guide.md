# Automation Authoring Guide

How to promote a researched idea from `ideas/` into a durable automation package in `automations/`.

This guide exists to keep promoted automations consistent in quality, safety, and packaging, without forcing every prompt into the same shape.

## Goal

Create promoted automation packages that are:

- grounded in the research inside `ideas/<topic>/`
- durable enough to reuse across teams and environments
- minimal enough for the model to execute reliably
- clear enough for humans to install and adapt

## Core Rules

1. Promote from evidence, not from taste.
   The promoted automation should come from the strongest candidate in the idea package README, synthesis notes, and drafted prompts.
2. Promote one automation per folder.
   A promoted automation is a standalone package under `automations/<automation-name>/`.
   Do not create multi-prompt suite folders in `automations/`.
3. Keep the runtime prompt self-contained.
   The prompt should not depend on external variables, forms, placeholders, or a "required inputs" section.
   It should use safe defaults, discover what it can, and stop or degrade gracefully when it cannot infer something safely.
4. Put detailed setup and customization in the README, not in the prompt.
   The README is the human-facing installation and adaptation document.
   The prompt is the runtime instruction set.
5. Be consistent in standards, not in shape.
   All promoted automations should share the same quality bar, tone, safety discipline, and README rigor.
   The prompt structure should match the task type.

## Promotion Workflow

### 1. Start from the idea package

Read, at minimum:

- `ideas/<topic>/README.md`
- `ideas/<topic>/research/synthesis-notes.md`
- the strongest relevant draft `README.md`
- the strongest relevant draft `prompt.md`

Also inspect supporting research artifacts when the choice is unclear.

### 2. Choose the exact promotion target

Promote the strongest standalone candidate, not the entire idea package.

Good promotion target:

- one clear job
- clear success condition
- clear tool surface
- clear blast radius

Bad promotion target:

- a vague orchestration suite
- one prompt that mixes triage, ticketing, notifications, and code changes without clear boundaries

### 3. Decide whether the promoted name should be simplified

Draft names are sometimes internal or overly descriptive.

Examples:

- a draft like `sentry-issue-triage-router` may promote better as `sentry-slack-triage-digest` or `sentry-issue-triage`, depending on the actual promoted behavior
- a draft like `launchdarkly-feature-flag-cleanup` is already public-ready and should stay as-is

Prefer stable, user-facing names over internal workflow labels.

### 4. Create the package

Each promoted automation should normally contain:

```text
automations/
  <automation-name>/
    README.md
    <automation-name>.md
```

Use `meta.json` only if the package truly benefits from machine-readable metadata later.

## Prompt Rules

### The prompt should be the minimum effective runtime instruction set

A good promoted prompt:

- says what the automation is
- says the goal
- gives the execution pattern
- defines the real guardrails
- defines the output shape

It should not read like a policy memo.

### The prompt must be self-contained

Do:

- use defaults like "default 24h window" or "up to 5 issues"
- discover scope when possible
- fall back to preview/report mode when writes are unavailable
- stop when safe inference is impossible
- only rely on persistent state such as cooldowns, dedupe memory, or prior-run tracking when the automation platform actually provides that state

Do not:

- require placeholders like `<org slug>` or `<channel>`
- require a "Required Inputs" section
- assume the user filled out a variable form
- depend on side instructions that are not part of the prompt
- pretend the automation can remember prior runs when it cannot

### Keep the prompt lean

Prefer:

- one short role framing
- one short goal
- one short process section or clear steps
- one guardrails section
- one exact output section

Remove:

- repeated safety rules
- duplicate fallback logic
- repeated decision gates such as the same dedupe or stop rule in multiple sections
- long tool-priority sections unless tool choice is essential
- setup instructions that belong in the README
- fake "verify tool access" ceremony when the real step can simply attempt the action and stop or fall back if it fails

### Match the prompt shape to the automation type

Use a more procedural, step-by-step prompt when the automation is:

- code-changing
- validation-heavy
- PR-building
- deterministic and repo-local

Examples:

- `dead-code-sweep`
- `launchdarkly-feature-flag-cleanup`

Use a leaner policy-plus-process prompt when the automation is:

- triage
- summarization
- routing
- digest/report oriented

Examples:

- `sentry-slack-triage-digest`

### Let the model infer the right things

Make explicit:

- scope boundaries
- safe defaults
- non-negotiable safety rules
- exact output shape

Let the model infer:

- the best phrasing of summaries
- which of several high-signal items deserve the final digest
- which evidence fields matter most in a specific run

Do not over-specify judgment-heavy ranking logic unless the automation becomes unstable without it.

For recurring automations, make the search space explicit but keep interpretation flexible:

- be fairly strict about query boundaries, time windows, and candidate pool size
- be lighter about ranking formulas unless the automation proves unstable without them
- if the automation explores a repo broadly, bound the first-pass review to a fixed number of surfaces, candidates, or findings

## README Rules

The README should be more detailed than the prompt.

Each promoted automation README should usually include:

1. Overview
2. How it works
3. Prerequisites, if they add real value
4. Cursor Cloud usage
5. Codex app usage
6. Claude Code / Codex CLI / Copilot usage
7. CLI alternative, if relevant
8. Recommended defaults
9. Useful repo-specific or workspace-specific inputs

### README expectations

- explain what the automation does in plain language
- explain when to use it
- give explicit setup steps for MCP/providers when relevant
- link the local prompt file directly
- document sane defaults and safe customization points
- make provider/tool setup at least as explicit as the strongest comparable promoted README in the repo
- omit sections that would only repeat obvious setup, especially `Prerequisites`

### README anti-patterns

Do not:

- dump generic links at the end if the rest of the promoted READMEs do not do that
- add a trailing "Useful Docs" or similar link-dump section unless those links are truly necessary for setup
- leave setup vague when another automation in the repo shows the explicit provider setup pattern
- put placeholder-heavy variable forms into the README unless the automation actually uses them
- describe runtime "automation inputs" if the automation model in this repo does not actually use input forms
- add "when not to use it" sections instead of keeping the usage guidance focused on positive fit
- pad "when to use it" sections with obvious restatements of the overview
- list obvious prerequisites such as basic repository access unless the exact permission boundary matters

## Safety Rules For Promotion

Before promoting an automation, confirm:

- the default behavior matches the safest useful version of the idea
- destructive or noisy writes are either removed or clearly gated
- the prompt does not promise capabilities the environment cannot reliably support
- the automation can stop gracefully when tool access or scope is missing

Default promotion bias:

- prefer report-only, preview, draft, or digest behavior first
- keep ticket creation, PR opening, or provider mutation in separate automations unless they are the whole point of the automation
- prefer outputs that land in a real review surface such as Slack, drafts, PRs, or generated reports rather than relying only on run logs, unless the run log itself is the intended product

## Consistency Rules

Be consistent in:

- tone
- quality bar
- safety discipline
- installation rigor
- output clarity
- naming quality

Do not force consistency in:

- prompt section names
- exact process formatting
- step count
- level of procedural detail

Different tasks need different prompt shapes.

The templates in this guide are default archetypes, not mandatory forms.
If a prompt clearly works better with a different structure, use the minimum effective structure for that task instead of forcing it into the wrong template.
Only add a new reusable template once the same prompt pattern repeats across multiple promoted automations.

## Promotion Checklist

Before considering a package done, verify all of the following:

- [ ] The promoted automation has one clear job.
- [ ] The automation name is public-ready.
- [ ] The prompt is self-contained.
- [ ] The prompt uses defaults and discovery instead of placeholders.
- [ ] The prompt does not assume nonexistent persistent state.
- [ ] The prompt only keeps necessary guardrails.
- [ ] The prompt output shape is explicit.
- [ ] The README explains setup explicitly for the relevant providers and tools.
- [ ] The README matches the tone and structure of the existing promoted packages.
- [ ] The package does not rely on undocumented environment assumptions.
- [ ] `git diff --check` is clean.

## Recommended Working Pattern

When creating a new promoted package:

1. Read the idea package README, synthesis notes, and best draft.
2. Decide the exact promoted automation and public-facing name.
3. Create `automations/<name>/README.md`.
4. Create `automations/<name>/<name>.md`.
5. Write the README first if the setup surface is complex.
6. Write the prompt second, keeping it shorter than the README.
7. Remove anything that belongs in the README rather than the prompt.
8. Compare the result against existing promoted automations for tone and package quality.
9. Run `git diff --check`.

## Short Templates

These are starting points, not strict requirements.
Use the closest template when it helps, but do not force a prompt into the wrong shape for the sake of consistency.

### Lean prompt template

```md
You are a conservative <type> automation.

## Goal

<one or two sentences>

## Process

1. <find the bounded candidate set>
2. <gather the key evidence>
3. <choose the best items or action>
4. <produce the result or fallback>

## Guardrails

- <real non-negotiable rule>
- <real non-negotiable rule>

## Output

<exact output structure>
```

### Procedural prompt template

```md
You are a conservative <type> automation.

Your goal is to <goal>. Prefer doing nothing over making a questionable change.

## Step 1 - <scan or discover>

<instructions>

## Step 2 - <choose candidates>

<instructions>

## Step 3 - <apply or produce>

<instructions>

## Step 4 - <validate>

<instructions>

## Output

<exact output structure>
```
