<div align="center">
  <h1>AI Agent Automations</h1>
  <p>A curated collection of 50+ ready-to-run AI agent automations for real-world workflows.</p>
  <p>
    <a href="./README.md"><strong>English</strong></a>
    <span> · </span>
    <a href="./README.zh-CN.md"><strong>简体中文</strong></a>
  </p>
</div>

<p align="center">
  <sub>For multiple agent environments and workflow platforms</sub>
</p>

<p align="center">
  <img src="./assets/github_readme_agent_provider_logo_strip@2x.png" width="160" alt="Codex, Cursor, and Claude Code logo strip">
</p>

<p align="center">
  <img src="./assets/github_readme_provider_logo_strip@2x.png" width="720" alt="Provider logo strip">
</p>

<p align="center">
  <a href="https://chmarax.github.io/ai-agent-automations/launch/codex/">
    <img src="https://img.shields.io/badge/Open%20In-Codex-111111?style=for-the-badge" alt="Open in Codex">
  </a>
  <a href="https://chmarax.github.io/ai-agent-automations/launch/cursor/">
    <img src="https://img.shields.io/badge/Open%20In-Cursor-111111?style=for-the-badge" alt="Open in Cursor">
  </a>
  <a href="https://chmarax.github.io/ai-agent-automations/launch/claude/">
    <img src="https://img.shields.io/badge/Open%20In-Claude-111111?style=for-the-badge" alt="Open in Claude Code">
  </a>
</p>

<p align="center">
  <sub>Open the catalog assessment prompt directly in your AI app and let it recommend the best automation for your repo or workflow.</sub>
</p>

## What this is

A collection of field tested and ready-to-run AI agent automations for real-world workflows.

Each automation includes a structured prompt and companion README you can run as-is, adapt to your stack, or use as inspiration for your own workflows. They cover practical tasks across code, inboxes, support, billing, observability, research, security, and team operations.

Browse by category, pick a workflow, and tune it to fit your tools, context, and use case.

<table>
  <tr>
    <td width="33%" align="center">
      <a href="./automations/github-actions-ci-cost-and-time-digest/assets/html-report-preview.html">
        <img src="./automations/github-actions-ci-cost-and-time-digest/assets/html-report-preview.png" alt="GitHub Actions CI cost and time">
      </a>
      <br>
      <sub>GitHub Actions CI</sub>
    </td>
    <td width="33%" align="center">
      <a href="./automations/crypto-market-research-digest/assets/html-report-preview.html">
        <img src="./automations/crypto-market-research-digest/assets/html-report-preview.png" alt="Crypto market research">
      </a>
      <br>
      <sub>Crypto market research</sub>
    </td>
    <td width="33%" align="center">
      <a href="./automations/stripe-failed-payment-risk-digest/assets/html-report-preview.html">
        <img src="./automations/stripe-failed-payment-risk-digest/assets/html-report-preview.png" alt="Stripe failed payment risk">
      </a>
      <br>
      <sub>Stripe failed payment risk</sub>
    </td>
  </tr>
</table>

## Automations

### Code Quality & Maintenance

Automations for repository cleanup, safer fixes, focused refactors, and recurring maintenance work.

| Automation | What it does | Surface | Links |
| --- | --- | --- | --- |
| [`branch-change-test-coverage`](./automations/branch-change-test-coverage/README.md) | Adds missing tests for a recent branch or merged change, focusing on the behavior that matters most. | ![Repo][repo-badge] ![GitHub][github-badge] | [README](./automations/branch-change-test-coverage/README.md) · [Prompt](./automations/branch-change-test-coverage/branch-change-test-coverage.md) |
| [`critical-bug-fix-pr`](./automations/critical-bug-fix-pr/README.md) | Finds one critical bug in recent code changes, applies the smallest safe fix, and opens a draft PR. | ![Repo][repo-badge] ![GitHub][github-badge] | [README](./automations/critical-bug-fix-pr/README.md) · [Prompt](./automations/critical-bug-fix-pr/critical-bug-fix-pr.md) |
| [`dead-code-sweep`](./automations/dead-code-sweep/README.md) | Removes safe dead code and validates the cleanup so small maintenance work actually sticks. | ![Repo][repo-badge] | [README](./automations/dead-code-sweep/README.md) · [Prompt](./automations/dead-code-sweep/dead-code-sweep.md) |
| [`launchdarkly-feature-flag-cleanup`](./automations/launchdarkly-feature-flag-cleanup/README.md) | Removes old temporary feature-flag code and validates that the cleanup is still safe. | ![Repo][repo-badge] ![LaunchDarkly][launchdarkly-badge] | [README](./automations/launchdarkly-feature-flag-cleanup/README.md) · [Prompt](./automations/launchdarkly-feature-flag-cleanup/launchdarkly-feature-flag-cleanup.md) |
| [`sampled-refactor`](./automations/sampled-refactor/README.md) | Applies one small safe refactor in the codebase to improve maintainability without changing behavior. | ![Repo][repo-badge] ![GitHub][github-badge] | [README](./automations/sampled-refactor/README.md) · [Prompt](./automations/sampled-refactor/sampled-refactor.md) |

### Developer Workflow

Automations for pull request routing, CI visibility, and recurring developer-experience improvements.

| Automation | What it does | Surface | Links |
| --- | --- | --- | --- |
| [`github-actions-ci-cost-and-time-digest`](./automations/github-actions-ci-cost-and-time-digest/README.md) | Shows which GitHub Actions jobs cost the most time and money, so teams know where to optimize first. | ![GitHub][github-badge] | [README](./automations/github-actions-ci-cost-and-time-digest/README.md) · [Prompt](./automations/github-actions-ci-cost-and-time-digest/github-actions-ci-cost-and-time-digest.md) |
| [`github-ci-speedup-optimizer`](./automations/github-ci-speedup-optimizer/README.md) | Tests one safe change to make GitHub Actions faster and reports whether it actually helped. | ![GitHub][github-badge] ![Repo][repo-badge] | [README](./automations/github-ci-speedup-optimizer/README.md) · [Prompt](./automations/github-ci-speedup-optimizer/github-ci-speedup-optimizer.md) |
| [`github-pr-review-router`](./automations/github-pr-review-router/README.md) | Shows what each open PR is waiting on, so reviewers and authors know where attention should go next. | ![GitHub][github-badge] | [README](./automations/github-pr-review-router/README.md) · [Prompt](./automations/github-pr-review-router/github-pr-review-router.md) |

### Security & Compliance

Automations for repository, dependency, Atlas, and external security signal review.

| Automation | What it does | Surface | Links |
| --- | --- | --- | --- |
| [`atlas-security-posture-digest`](./automations/atlas-security-posture-digest/README.md) | Checks the security setup of one MongoDB Atlas project and highlights the issues most worth reviewing. | ![MongoDB][mongodb-badge] | [README](./automations/atlas-security-posture-digest/README.md) · [Prompt](./automations/atlas-security-posture-digest/atlas-security-posture-digest.md) |
| [`brand-typosquat-monitor`](./automations/brand-typosquat-monitor/README.md) | Finds suspicious typo or lookalike domains for your brand so teams know what to investigate first. | ![Public Web][web-badge] | [README](./automations/brand-typosquat-monitor/README.md) · [Prompt](./automations/brand-typosquat-monitor/brand-typosquat-monitor.md) |
| [`cisa-kev-relevance-digest`](./automations/cisa-kev-relevance-digest/README.md) | Finds CISA known exploited vulnerabilities that may matter to your codebase and highlights the ones worth reviewing. | ![Public Web][web-badge] ![Repo][repo-badge] | [README](./automations/cisa-kev-relevance-digest/README.md) · [Prompt](./automations/cisa-kev-relevance-digest/cisa-kev-relevance-digest.md) |
| [`dependency-vulnerability-autofix`](./automations/dependency-vulnerability-autofix/README.md) | Fixes one real dependency vulnerability with a small validated change that is easy to review. | ![Repo][repo-badge] ![GitHub][github-badge] | [README](./automations/dependency-vulnerability-autofix/README.md) · [Prompt](./automations/dependency-vulnerability-autofix/dependency-vulnerability-autofix.md) |
| [`license-compliance-drift-digest`](./automations/license-compliance-drift-digest/README.md) | Shows dependency license changes that may create risk, so compliance review stays focused. | ![Repo][repo-badge] | [README](./automations/license-compliance-drift-digest/README.md) · [Prompt](./automations/license-compliance-drift-digest/license-compliance-drift-digest.md) |
| [`scan-codebase-vulnerabilities`](./automations/scan-codebase-vulnerabilities/README.md) | Finds real application security issues in a repository with a believable attack path, not just scanner noise. | ![Repo][repo-badge] | [README](./automations/scan-codebase-vulnerabilities/README.md) · [Prompt](./automations/scan-codebase-vulnerabilities/scan-codebase-vulnerabilities.md) |

### Local Security

Automations for local-host persistence checks, firewall review, network inspection, and workstation security monitoring.

| Automation | What it does | Surface | Links |
| --- | --- | --- | --- |
| [`launchagent-launchdaemon-evidence-pack`](./automations/launchagent-launchdaemon-evidence-pack/README.md) | Finds launchd items on macOS that may need investigation, with a short evidence pack for review. | ![Local Host][local-badge] | [README](./automations/launchagent-launchdaemon-evidence-pack/README.md) · [Prompt](./automations/launchagent-launchdaemon-evidence-pack/launchagent-launchdaemon-evidence-pack.md) |
| [`local-listening-service-and-firewall-audit`](./automations/local-listening-service-and-firewall-audit/README.md) | Shows which local services are exposed and how the firewall is set up, so host risk is easier to review. | ![Local Host][local-badge] | [README](./automations/local-listening-service-and-firewall-audit/README.md) · [Prompt](./automations/local-listening-service-and-firewall-audit/local-listening-service-and-firewall-audit.md) |
| [`local-network-monitor`](./automations/local-network-monitor/README.md) | Summarizes current network activity on a local machine with the signals most worth a closer look. | ![Local Host][local-badge] | [README](./automations/local-network-monitor/README.md) · [Prompt](./automations/local-network-monitor/local-network-monitor.md) |
| [`local-security-monitor`](./automations/local-security-monitor/README.md) | Runs a basic security health check on a local machine and highlights the issues most worth attention. | ![Local Host][local-badge] | [README](./automations/local-security-monitor/README.md) · [Prompt](./automations/local-security-monitor/local-security-monitor.md) |
| [`shell-history-anomaly-digest`](./automations/shell-history-anomaly-digest/README.md) | Finds unusual or risky patterns in shell history that may deserve a human follow-up. | ![Local Host][local-badge] | [README](./automations/shell-history-anomaly-digest/README.md) · [Prompt](./automations/shell-history-anomaly-digest/shell-history-anomaly-digest.md) |

### Observability & Incident Response

Automations for production error triage, latency investigation, and engineering follow-up driven by live signals.

| Automation | What it does | Surface | Links |
| --- | --- | --- | --- |
| [`new-relic-error-fixer`](./automations/new-relic-error-fixer/README.md) | Fixes one important production error from New Relic when the code path and smallest safe fix are clear. | ![New Relic][newrelic-badge] ![Repo][repo-badge] | [README](./automations/new-relic-error-fixer/README.md) · [Prompt](./automations/new-relic-error-fixer/new-relic-error-fixer.md) |
| [`new-relic-latency-hotspot-fixer`](./automations/new-relic-latency-hotspot-fixer/README.md) | Finds one important latency hotspot and prepares a small fix when the bottleneck is clear enough. | ![New Relic][newrelic-badge] ![Repo][repo-badge] | [README](./automations/new-relic-latency-hotspot-fixer/README.md) · [Prompt](./automations/new-relic-latency-hotspot-fixer/new-relic-latency-hotspot-fixer.md) |
| [`sentry-slack-triage-digest`](./automations/sentry-slack-triage-digest/README.md) | Posts a short Sentry issue digest to Slack so teams can review what matters now. | ![Sentry][sentry-badge] ![Slack][slack-badge] | [README](./automations/sentry-slack-triage-digest/README.md) · [Prompt](./automations/sentry-slack-triage-digest/sentry-slack-triage-digest.md) |
| [`sentry-triage-and-fix`](./automations/sentry-triage-and-fix/README.md) | Fixes one important Sentry issue and turns it into a focused, reviewable code change. | ![Sentry][sentry-badge] ![Repo][repo-badge] | [README](./automations/sentry-triage-and-fix/README.md) · [Prompt](./automations/sentry-triage-and-fix/sentry-triage-and-fix.md) |
| [`slack-engineering-signal-digest`](./automations/slack-engineering-signal-digest/README.md) | Summarizes the most important recent engineering Slack discussions so teams can catch up quickly. | ![Slack][slack-badge] | [README](./automations/slack-engineering-signal-digest/README.md) · [Prompt](./automations/slack-engineering-signal-digest/slack-engineering-signal-digest.md) |

### Cost & Performance

Automations for recurring cost review, infrastructure efficiency, and performance optimization opportunities.

| Automation | What it does | Surface | Links |
| --- | --- | --- | --- |
| [`atlas-cost-optimization-digest`](./automations/atlas-cost-optimization-digest/README.md) | Finds the biggest cost-saving opportunities in one MongoDB Atlas project, with the clearest places to optimize first. | ![MongoDB][mongodb-badge] | [README](./automations/atlas-cost-optimization-digest/README.md) · [Prompt](./automations/atlas-cost-optimization-digest/atlas-cost-optimization-digest.md) |
| [`atlas-performance-advisor-digest-and-pr`](./automations/atlas-performance-advisor-digest-and-pr/README.md) | Reviews Atlas Performance Advisor recommendations, explains which ones look worth testing, and can prepare one safe index PR. | ![MongoDB][mongodb-badge] ![Repo][repo-badge] | [README](./automations/atlas-performance-advisor-digest-and-pr/README.md) · [Prompt](./automations/atlas-performance-advisor-digest-and-pr/atlas-performance-advisor-digest-and-pr.md) |
| [`new-relic-cost-and-ingest-hygiene-audit`](./automations/new-relic-cost-and-ingest-hygiene-audit/README.md) | Finds telemetry waste and cost drivers in New Relic, with the clearest cleanup opportunities first. | ![New Relic][newrelic-badge] | [README](./automations/new-relic-cost-and-ingest-hygiene-audit/README.md) · [Prompt](./automations/new-relic-cost-and-ingest-hygiene-audit/new-relic-cost-and-ingest-hygiene-audit.md) |

### Database Reliability

Automations for MongoDB query health and production data-contract drift detection.

| Automation | What it does | Surface | Links |
| --- | --- | --- | --- |
| [`mongodb-query-anti-pattern-scout`](./automations/mongodb-query-anti-pattern-scout/README.md) | Finds risky MongoDB query patterns in code, backed by the Atlas signals most worth fixing. | ![MongoDB][mongodb-badge] ![Repo][repo-badge] | [README](./automations/mongodb-query-anti-pattern-scout/README.md) · [Prompt](./automations/mongodb-query-anti-pattern-scout/mongodb-query-anti-pattern-scout.md) |
| [`production-data-contract-change-watch`](./automations/production-data-contract-change-watch/README.md) | Finds differences between live data and your expected data shape before the drift turns into bugs. | ![MongoDB][mongodb-badge] ![Repo][repo-badge] | [README](./automations/production-data-contract-change-watch/README.md) · [Prompt](./automations/production-data-contract-change-watch/production-data-contract-change-watch.md) |

### Inbox & Calendar

Automations for inbox triage, meeting-response drafting, and sent-mail follow-up.

| Automation | What it does | Surface | Links |
| --- | --- | --- | --- |
| [`gmail-inbox-triage`](./automations/gmail-inbox-triage/README.md) | Sorts new inbox email and archives low-value messages so the inbox stays focused on what matters. | ![Gmail][gmail-badge] | [README](./automations/gmail-inbox-triage/README.md) · [Prompt](./automations/gmail-inbox-triage/gmail-inbox-triage.md) |
| [`gmail-meeting-request-draft-assistant`](./automations/gmail-meeting-request-draft-assistant/README.md) | Drafts replies to meeting requests based on calendar availability, without automatically booking anything. | ![Gmail][gmail-badge] ![Calendar][calendar-badge] | [README](./automations/gmail-meeting-request-draft-assistant/README.md) · [Prompt](./automations/gmail-meeting-request-draft-assistant/gmail-meeting-request-draft-assistant.md) |
| [`gmail-sent-email-follow-up-watcher`](./automations/gmail-sent-email-follow-up-watcher/README.md) | Finds sent emails that may need a follow-up, so important conversations do not go quiet. | ![Gmail][gmail-badge] | [README](./automations/gmail-sent-email-follow-up-watcher/README.md) · [Prompt](./automations/gmail-sent-email-follow-up-watcher/gmail-sent-email-follow-up-watcher.md) |

### Research & Trends

Automations for recurring market, ecosystem, newsletter, and machine-learning research digests.

| Automation | What it does | Surface | Links |
| --- | --- | --- | --- |
| [`crypto-market-research-digest`](./automations/crypto-market-research-digest/README.md) | Summarizes the most important recent crypto market developments in a quick research brief. | ![Public Web][web-badge] | [README](./automations/crypto-market-research-digest/README.md) · [Prompt](./automations/crypto-market-research-digest/crypto-market-research-digest.md) |
| [`github-trending-digest`](./automations/github-trending-digest/README.md) | Summarizes the top projects on GitHub Trending and explains why each one stands out. | ![GitHub][github-badge] ![Public Web][web-badge] | [README](./automations/github-trending-digest/README.md) · [Prompt](./automations/github-trending-digest/github-trending-digest.md) |
| [`gmail-newsletter-intel-brief`](./automations/gmail-newsletter-intel-brief/README.md) | Turns newsletters into one short brief with the main takeaways worth reading. | ![Gmail][gmail-badge] ![Public Web][web-badge] | [README](./automations/gmail-newsletter-intel-brief/README.md) · [Prompt](./automations/gmail-newsletter-intel-brief/gmail-newsletter-intel-brief.md) |
| [`huggingface-model-digest`](./automations/huggingface-model-digest/README.md) | Summarizes notable new Hugging Face models with quick context on what they do and why they matter. | ![Hugging Face][huggingface-badge] | [README](./automations/huggingface-model-digest/README.md) · [Prompt](./automations/huggingface-model-digest/huggingface-model-digest.md) |
| [`huggingface-weekly-papers-digest`](./automations/huggingface-weekly-papers-digest/README.md) | Summarizes recent Hugging Face paper activity in a compact weekly research brief. | ![Hugging Face][huggingface-badge] | [README](./automations/huggingface-weekly-papers-digest/README.md) · [Prompt](./automations/huggingface-weekly-papers-digest/huggingface-weekly-papers-digest.md) |

### Customer Success

Automations for customer voice analysis, renewal-risk detection, and support-driven documentation improvements.

| Automation | What it does | Surface | Links |
| --- | --- | --- | --- |
| [`plain-customer-voice-digest`](./automations/plain-customer-voice-digest/README.md) | Summarizes what customers are saying in support conversations, grouped into the signals that matter most. | ![Plain][plain-badge] | [README](./automations/plain-customer-voice-digest/README.md) · [Prompt](./automations/plain-customer-voice-digest/plain-customer-voice-digest.md) |
| [`plain-renewal-risk-digest`](./automations/plain-renewal-risk-digest/README.md) | Finds customers showing signs of renewal or churn risk, so success teams can review the right accounts first. | ![Plain][plain-badge] ![Stripe][stripe-badge] | [README](./automations/plain-renewal-risk-digest/README.md) · [Prompt](./automations/plain-renewal-risk-digest/plain-renewal-risk-digest.md) |
| [`support-docs-gap-drafter`](./automations/support-docs-gap-drafter/README.md) | Drafts a small docs improvement from repeated support questions, so the same tickets happen less often. | ![Docs][docs-badge] ![Repo][repo-badge] | [README](./automations/support-docs-gap-drafter/README.md) · [Prompt](./automations/support-docs-gap-drafter/support-docs-gap-drafter.md) |

### Revenue & Billing

Automations for billing mail handling, subscription risk review, payment recovery, and Stripe operational health.

| Automation | What it does | Surface | Links |
| --- | --- | --- | --- |
| [`gmail-billing-organizer`](./automations/gmail-billing-organizer/README.md) | Organizes billing emails like invoices, receipts, and renewals so important finance messages are easier to track. | ![Gmail][gmail-badge] | [README](./automations/gmail-billing-organizer/README.md) · [Prompt](./automations/gmail-billing-organizer/gmail-billing-organizer.md) |
| [`stripe-cancel-at-period-end-watch`](./automations/stripe-cancel-at-period-end-watch/README.md) | Finds subscriptions scheduled to cancel that deserve attention, ranked by who looks most worth saving. | ![Stripe][stripe-badge] | [README](./automations/stripe-cancel-at-period-end-watch/README.md) · [Prompt](./automations/stripe-cancel-at-period-end-watch/stripe-cancel-at-period-end-watch.md) |
| [`stripe-failed-payment-risk-digest`](./automations/stripe-failed-payment-risk-digest/README.md) | Finds failed payments most likely to become churn, cash collection, or support risk, so teams can act first. | ![Stripe][stripe-badge] | [README](./automations/stripe-failed-payment-risk-digest/README.md) · [Prompt](./automations/stripe-failed-payment-risk-digest/stripe-failed-payment-risk-digest.md) |
| [`stripe-webhook-health-watch`](./automations/stripe-webhook-health-watch/README.md) | Checks whether Stripe webhooks are healthy and highlights delivery failures or setup problems worth fixing. | ![Stripe][stripe-badge] | [README](./automations/stripe-webhook-health-watch/README.md) · [Prompt](./automations/stripe-webhook-health-watch/stripe-webhook-health-watch.md) |

### Marketing

Automations that turn shipped engineering work into product-facing launch copy.

| Automation | What it does | Surface | Links |
| --- | --- | --- | --- |
| [`backlink-opportunity-finder`](./automations/backlink-opportunity-finder/README.md) | Finds unlinked mentions of your brand, drafts polite outreach in Gmail, and tracks what was already handled so backlink follow-up stays focused. | ![Public Web][web-badge] ![Gmail][gmail-badge] | [README](./automations/backlink-opportunity-finder/README.md) · [Prompt](./automations/backlink-opportunity-finder/backlink-opportunity-finder.md) |
| [`github-product-post-drafts`](./automations/github-product-post-drafts/README.md) | Turns shipped GitHub work into draft product posts that are easier to publish and refine. | ![GitHub][github-badge] | [README](./automations/github-product-post-drafts/README.md) · [Prompt](./automations/github-product-post-drafts/github-product-post-drafts.md) |

### Work Triage

Automations that create, route, sync, or prioritize follow-up engineering work in a backlog system.

| Automation | What it does | Surface | Links |
| --- | --- | --- | --- |
| [`dependency-major-upgrade-planner`](./automations/dependency-major-upgrade-planner/README.md) | Turns major dependency upgrades into concrete migration tasks so teams can plan the work clearly. | ![Repo][repo-badge] ![Linear][linear-badge] | [README](./automations/dependency-major-upgrade-planner/README.md) · [Prompt](./automations/dependency-major-upgrade-planner/dependency-major-upgrade-planner.md) |
| [`linear-triage-router`](./automations/linear-triage-router/README.md) | Routes new Linear issues to the right team and priority when the signal is strong enough. | ![Linear][linear-badge] | [README](./automations/linear-triage-router/README.md) · [Prompt](./automations/linear-triage-router/linear-triage-router.md) |
| [`sentry-linear-backlog-sync`](./automations/sentry-linear-backlog-sync/README.md) | Turns actionable Sentry issues into Linear backlog items so recurring production problems get tracked. | ![Sentry][sentry-badge] ![Linear][linear-badge] | [README](./automations/sentry-linear-backlog-sync/README.md) · [Prompt](./automations/sentry-linear-backlog-sync/sentry-linear-backlog-sync.md) |
| [`todo-linear-sync-and-fix`](./automations/todo-linear-sync-and-fix/README.md) | Fixes easy TODOs and turns the rest into Linear tasks so loose notes become real follow-up. | ![Repo][repo-badge] ![Linear][linear-badge] | [README](./automations/todo-linear-sync-and-fix/README.md) · [Prompt](./automations/todo-linear-sync-and-fix/todo-linear-sync-and-fix.md) |

[repo-badge]: https://img.shields.io/badge/Repo-0f172a?style=flat-square
[github-badge]: https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white
[gmail-badge]: https://img.shields.io/badge/Gmail-EA4335?style=flat-square&logo=gmail&logoColor=white
[calendar-badge]: https://img.shields.io/badge/Calendar-4285F4?style=flat-square&logo=googlecalendar&logoColor=white
[slack-badge]: https://img.shields.io/badge/Slack-4A154B?style=flat-square&logo=slack&logoColor=white
[sentry-badge]: https://img.shields.io/badge/Sentry-362D59?style=flat-square&logo=sentry&logoColor=white
[linear-badge]: https://img.shields.io/badge/Linear-5E6AD2?style=flat-square&logo=linear&logoColor=white
[stripe-badge]: https://img.shields.io/badge/Stripe-635BFF?style=flat-square&logo=stripe&logoColor=white
[mongodb-badge]: https://img.shields.io/badge/MongoDB-47A248?style=flat-square&logo=mongodb&logoColor=white
[newrelic-badge]: https://img.shields.io/badge/New%20Relic-1CE783?style=flat-square&logo=newrelic&logoColor=04103B
[huggingface-badge]: https://img.shields.io/badge/Hugging%20Face-FFD21E?style=flat-square&logo=huggingface&logoColor=black
[plain-badge]: https://img.shields.io/badge/Plain-111827?style=flat-square
[launchdarkly-badge]: https://img.shields.io/badge/LaunchDarkly-4050FF?style=flat-square&logo=launchdarkly&logoColor=white
[docs-badge]: https://img.shields.io/badge/Docs-0F766E?style=flat-square
[local-badge]: https://img.shields.io/badge/Local%20Host-334155?style=flat-square
[web-badge]: https://img.shields.io/badge/Public%20Web-2563EB?style=flat-square
