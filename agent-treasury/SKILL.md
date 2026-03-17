---
name: agent-treasury
user-invocable: true
description: Read the agent's vault state, take NAV snapshots, and persist portfolio data to the Augmi platform. Called by cron for daily snapshots and on-demand for reports.
allowed-tools: Bash, Read, Write
---

# Agent Treasury Skill

Monitor and report your agent's vault state. Takes daily NAV snapshots and reports holdings to the Augmi platform.

## Prerequisites

- Vault must be deployed (`/data/agent-token.json` must exist)
- Price feed available (calls CoinGecko)

## Usage

### Take NAV Snapshot

```bash
node /data/skills/agent-treasury/scripts/snapshot.js
```

### Generate Human-Readable Report

```bash
node /data/skills/agent-treasury/scripts/report.js
```

## Output

Snapshots saved to `/data/snapshots/YYYY-MM-DD.json` and posted to platform API.
