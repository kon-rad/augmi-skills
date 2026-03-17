#!/usr/bin/env node
/**
 * Generate a human-readable portfolio report.
 */

const fs = require('fs');

async function main() {
  const snapshotsDir = '/data/snapshots';
  const files = fs.readdirSync(snapshotsDir).sort();

  if (files.length === 0) {
    console.log('No snapshots yet. Run snapshot.js first.');
    return;
  }

  const latest = JSON.parse(fs.readFileSync(`${snapshotsDir}/${files[files.length - 1]}`, 'utf8'));
  const tokenData = fs.existsSync('/data/agent-token.json')
    ? JSON.parse(fs.readFileSync('/data/agent-token.json', 'utf8'))
    : { tokenName: 'Fund', tokenSymbol: 'TOKEN' };

  let report = `\n=== ${tokenData.tokenName} ($${tokenData.tokenSymbol}) Portfolio Report ===\n`;
  report += `Date: ${latest.snapshotAt}\n`;
  report += `NAV: $${latest.totalValueUsd.toFixed(2)}\n`;
  report += `Share Price: $${latest.sharePrice.toFixed(6)}\n`;
  report += `Total Shares: ${latest.totalShares.toFixed(4)}\n\n`;

  report += `Performance:\n`;
  report += `  24h: ${latest.pnl24hPct >= 0 ? '+' : ''}${latest.pnl24hPct.toFixed(2)}%\n`;
  report += `  7d:  ${latest.pnl7dPct >= 0 ? '+' : ''}${latest.pnl7dPct.toFixed(2)}%\n`;
  report += `  30d: ${latest.pnl30dPct >= 0 ? '+' : ''}${latest.pnl30dPct.toFixed(2)}%\n\n`;

  report += `Holdings:\n`;
  for (const h of latest.holdings || []) {
    const pct = latest.totalValueUsd > 0 ? ((h.valueUsd / latest.totalValueUsd) * 100).toFixed(1) : '0';
    report += `  ${h.symbol}: ${h.amount.toFixed(4)} ($${h.valueUsd.toFixed(2)}, ${pct}%)\n`;
  }

  console.log(report);

  // Save report file for broadcast skill
  fs.writeFileSync('/data/portfolio-report.txt', report);
}

main().catch((err) => {
  console.error('Report failed:', err.message);
  process.exit(1);
});
