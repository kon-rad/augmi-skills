---
name: agent-token-launch
user-invocable: true
description: Deploy an ERC-4626 investment vault for this agent via the AgentTokenFactory on Base. Investors deposit USDC and receive ERC-20 vault shares. The agent trades with vault funds. Use this skill to launch your investment fund.
allowed-tools: Bash, Read, Write
---

# Agent Token Launch Skill

Deploy your agent's investment vault on Base via the AgentTokenFactory contract. This creates an ERC-4626 vault where investors can deposit USDC and receive your agent's ERC-20 shares.

## Prerequisites

- Agent must be registered on ERC-8004 (run `agent-registration` first)
- `AGENT_WALLET_PRIVATE_KEY` and `AGENT_WALLET_ADDRESS` set
- `AGENT_TOKEN_FACTORY_ADDRESS` — Factory contract address
- `AGENT_CREATOR_WALLET` — Creator wallet (receives exit fee share)
- Agent wallet must have ETH on Base for gas

## Usage

### Launch Token

```bash
node /data/skills/agent-token-launch/scripts/launch-token.js \
  --name "Alpha Fund" \
  --symbol "ALPHA" \
  --exitFee 200
```

### Check Token Status

```bash
node /data/skills/agent-token-launch/scripts/check-token.js
```

## How It Works

1. Calls `createAgentVault()` on AgentTokenFactory
2. Factory deploys an ERC-4626 vault with your agent as the trader
3. Vault is pre-approved for Uniswap V3 and Aerodrome routers
4. Saves vault address to `/data/agent-token.json`
5. Reports to Augmi platform

## Exit Fee

When investors withdraw, an exit fee (default 2%, max 5%) is deducted and split:
- 50% to creator wallet
- 50% to Augmi platform wallet
