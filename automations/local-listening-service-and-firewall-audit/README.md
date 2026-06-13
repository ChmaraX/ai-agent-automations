# Local Listening Service And Firewall Audit

## Overview

This automation checks listening services and firewall settings on a local machine. It gives a short report of what is exposed and what may need attention.
## How It Works

1. Detects the local platform and available read-only tooling, preferring `osquery` when available.
2. Builds a listener inventory with process ownership, port, protocol, and bind address.
3. Reads local firewall posture from the best native source available.
4. Ranks the meaningful exposure findings and returns a short report with a compact technical summary.

## When To Use It

- You want to know what the current machine is exposing inbound.
- You want a narrower hardening view than `local-network-monitor`.
- You want a read-only audit before making firewall or service changes.

## Prerequisites

- The automation must run on the host being inspected, or in a shell attached to it
- Read access to local socket state and firewall posture
- Optional `osquery` for cleaner process and listener mapping

## Setup

Use [local-listening-service-and-firewall-audit.md](/Users/adamchmara/projects/ai-agent-automations/automations/local-listening-service-and-firewall-audit/local-listening-service-and-firewall-audit.md) as the automation prompt.

### Cursor Cloud

1. Open [Cursor Automations](https://cursor.com/automations/new).
2. Create a new automation and paste the prompt.
3. Make sure the runner is attached to the machine you actually want to inspect.
4. Optional: install `osquery` for more consistent listener output.
5. Save and schedule the automation.

### Codex App

1. Click `Automation` > `New Automation`.
2. Paste the prompt and run it only where the environment has shell access to the target host.
3. Optional: install `osquery`.
4. Save the automation.

### Claude Code

1. Start the session on the host you want to inspect, or in a shell that can read that host's local state.
2. For repeated runs in one session, use:

```text
/loop 1d Follow the instructions in automations/local-listening-service-and-firewall-audit/local-listening-service-and-firewall-audit.md
```

3. For durable automation, use `/schedule` or a Routine.

## Recommended Defaults

| Setting | Default |
| --- | --- |
| Host scope | `current machine only` |
| Listener scope | `all readable TCP and UDP listeners` |
| Exposure emphasis | `non-loopback and wildcard binds first` |
| Firewall mode | `inspect only` |
| Allowlist mode | `none unless explicitly provided` |
| Output | `plain-language Markdown report with compact technical summary` |

If firewall state is partial, return the listener report anyway and call out the gap. Prefer short explanations over large tables and keep exposure language concrete.

## Useful Inputs

Example expected-service rule:

```text
Expected non-loopback listeners: ssh on 22/tcp, Tailscale on 41641/udp, local file sharing disabled, no VNC, no AirPlay receiver.
```

Example risk priority:

```text
Treat remote-access services, admin panels, SMB, printer services, and anything bound to 0.0.0.0 as higher priority than developer-only loopback listeners.
```

Example verification rule:

```text
For any non-loopback listener that is not obviously expected, include one manual verification command before suggesting a hardening change.
```

## Docs

- [Codex Automations](https://openai.com/academy/codex-automations)
