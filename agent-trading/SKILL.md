---
name: agent-trading
user-invocable: true
description: Execute token swaps on Uniswap V3 on Base through the agent's ERC-4626 vault. All trades go through the vault's executeTrade() function. Includes portfolio checking, price feeds, and risk management. Use this skill when the agent needs to trade tokens.
allowed-tools: Bash, Read, Write
---

# Agent Trading Skill

Execute token swaps on Uniswap V3 on Base. All trades flow through your AgentVault's `executeTrade()` — the agent wallet never holds funds directly.

## Prerequisites

- Vault must be deployed (run `agent-token-launch` first)
- `/data/agent-token.json` must exist with vault address
- Agent wallet needs ETH for gas on Base

## Usage

### Execute a Swap

```bash
node /data/skills/agent-trading/scripts/swap.js \
  --tokenIn USDC \
  --tokenOut WETH \
  --amountIn 100 \
  --reason "Bullish on ETH after market dip"
```

### Check Portfolio

```bash
node /data/skills/agent-trading/scripts/portfolio.js
```

### Get Price Feed

```bash
node /data/skills/agent-trading/scripts/price-feed.js
```

### Run Risk Check

```bash
node /data/skills/agent-trading/scripts/risk-check.js --amountIn 100 --tokenOut WETH
```

## Supported Tokens (Base)

| Symbol | Address |
|--------|---------|
| USDC | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |
| WETH | `0x4200000000000000000000000000000000000006` |
| cbBTC | `0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf` |
| AERO | `0x940181a94A35A4569E4529A3CDfB74e38FD98631` |

## Risk Guards

Default risk limits (configurable in `/data/agent-trading-config.json`):
- Max 20% of vault NAV in any single non-USDC token
- Trading paused if vault NAV drops 25% from peak
- Max 10 trades per 24 hours
- Only whitelisted tokens allowed
