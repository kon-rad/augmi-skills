#!/usr/bin/env node
/**
 * Risk check before executing a trade.
 * Exit code 0 = OK, 1 = blocked.
 *
 * Usage: node risk-check.js --amountIn 100 --tokenOut WETH
 */

const fs = require('fs');

function parseArgs() {
  const args = process.argv.slice(2);
  const result = { amountIn: '0', tokenOut: '' };
  for (let i = 0; i < args.length; i += 2) {
    if (args[i] === '--amountIn') result.amountIn = args[i + 1];
    if (args[i] === '--tokenOut') result.tokenOut = args[i + 1];
  }
  return result;
}

async function main() {
  const { amountIn, tokenOut } = parseArgs();

  const configFile = '/data/agent-trading-config.json';
  const config = fs.existsSync(configFile) ? JSON.parse(fs.readFileSync(configFile, 'utf8')) : {
    maxPositionPct: 20,
    maxDrawdownPct: 25,
    dailyTradeLimit: 10,
    allowedTokens: ['USDC', 'WETH', 'cbBTC', 'AERO'],
    peakNAV: 0,
  };

  // Check allowed tokens
  if (tokenOut && !config.allowedTokens.includes(tokenOut)) {
    console.log(`BLOCKED: ${tokenOut} not in allowed tokens`);
    process.exit(1);
  }

  // Check daily trade count
  const historyFile = '/data/trade-history.json';
  const history = fs.existsSync(historyFile) ? JSON.parse(fs.readFileSync(historyFile, 'utf8')) : [];
  const today = new Date().toISOString().slice(0, 10);
  const todayTrades = history.filter(t => t.timestamp?.startsWith(today));

  if (todayTrades.length >= config.dailyTradeLimit) {
    console.log(`BLOCKED: Daily trade limit reached (${todayTrades.length}/${config.dailyTradeLimit})`);
    process.exit(1);
  }

  // Check drawdown (if we have snapshots)
  const snapshotsDir = '/data/snapshots';
  if (fs.existsSync(snapshotsDir)) {
    const files = fs.readdirSync(snapshotsDir).sort();
    if (files.length > 0) {
      const latest = JSON.parse(fs.readFileSync(`${snapshotsDir}/${files[files.length - 1]}`, 'utf8'));
      const currentNAV = latest.totalValueUsd || 0;
      const peakNAV = config.peakNAV || currentNAV;

      if (peakNAV > 0) {
        const drawdown = ((peakNAV - currentNAV) / peakNAV) * 100;
        if (drawdown >= config.maxDrawdownPct) {
          console.log(`BLOCKED: Drawdown ${drawdown.toFixed(1)}% exceeds max ${config.maxDrawdownPct}%`);
          process.exit(1);
        }
      }
    }
  }

  console.log('PASS: All risk checks passed');
  console.log(`  Daily trades: ${todayTrades.length}/${config.dailyTradeLimit}`);
  process.exit(0);
}

main().catch((err) => {
  console.error('Risk check error:', err.message);
  process.exit(1);
});
