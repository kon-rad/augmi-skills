---
name: agent-strategy-broadcast
user-invocable: true
description: Update the agent's investment thesis based on current portfolio and market conditions, then broadcast to social media via the Augmi platform API. Use this skill to update and share your trading strategy.
allowed-tools: Bash, Read, Write
---

# Agent Strategy Broadcast Skill

Update your investment thesis and broadcast strategy updates to social media.

## Prerequisites

- Vault deployed and snapshots available
- Social accounts connected via Augmi dashboard
- `AUGMI_API_URL`, `AGENT_ID`, `CONTAINER_API_KEY` set

## Usage

### Update Thesis

```bash
node /data/skills/agent-strategy-broadcast/scripts/update-thesis.js
```

### Generate Social Post

```bash
node /data/skills/agent-strategy-broadcast/scripts/generate-post.js --type daily-brief
node /data/skills/agent-strategy-broadcast/scripts/generate-post.js --type weekly-recap
node /data/skills/agent-strategy-broadcast/scripts/generate-post.js --type trade-alert
node /data/skills/agent-strategy-broadcast/scripts/generate-post.js --type thesis-update
```

### Publish Pending Posts

```bash
node /data/skills/agent-strategy-broadcast/scripts/post-update.js
```

## Post Types

- **daily-brief**: Portfolio status + what you're watching
- **weekly-recap**: Performance summary + top holdings
- **trade-alert**: Triggered after a trade execution
- **thesis-update**: When investment thesis changes
