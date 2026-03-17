#!/usr/bin/env node
/**
 * Generate a social media post based on portfolio data.
 *
 * Usage: node generate-post.js --type daily-brief|weekly-recap|trade-alert|thesis-update
 */

const fs = require('fs');

function parseArgs() {
  const args = process.argv.slice(2);
  for (let i = 0; i < args.length; i += 2) {
    if (args[i] === '--type') return args[i + 1];
  }
  return 'daily-brief';
}

async function main() {
  const postType = parseArgs();
  const postsDir = '/data/posts/pending';
  fs.mkdirSync(postsDir, { recursive: true });

  const tokenFile = '/data/agent-token.json';
  const tokenData = fs.existsSync(tokenFile) ? JSON.parse(fs.readFileSync(tokenFile, 'utf8')) : { tokenName: 'Fund', tokenSymbol: 'TOKEN' };

  const snapshotsDir = '/data/snapshots';
  let latest = null;
  if (fs.existsSync(snapshotsDir)) {
    const files = fs.readdirSync(snapshotsDir).sort();
    if (files.length > 0) {
      latest = JSON.parse(fs.readFileSync(`${snapshotsDir}/${files[files.length - 1]}`, 'utf8'));
    }
  }

  const trades = fs.existsSync('/data/trade-history.json')
    ? JSON.parse(fs.readFileSync('/data/trade-history.json', 'utf8'))
    : [];

  const thesisFile = '/data/strategy/thesis.md';
  const thesis = fs.existsSync(thesisFile) ? fs.readFileSync(thesisFile, 'utf8').slice(0, 200) : '';

  let content = '';

  switch (postType) {
    case 'daily-brief':
      if (latest) {
        const sign = latest.pnl24hPct >= 0 ? '+' : '';
        content = `Portfolio: $${latest.totalValueUsd.toFixed(0)} (${sign}${latest.pnl24hPct.toFixed(1)}% today)\n\n`;
        content += `Top holdings: ${(latest.holdings || []).slice(0, 3).map(h => `$${h.symbol}`).join(', ')}\n\n`;
        if (thesis) content += `Thesis: ${thesis.split('\n')[0]}`;
      } else {
        content = `Fund launched: ${tokenData.tokenName} ($${tokenData.tokenSymbol}). Ready for investors.`;
      }
      break;

    case 'weekly-recap':
      if (latest) {
        const sign7d = latest.pnl7dPct >= 0 ? '+' : '';
        content = `Weekly recap for $${tokenData.tokenSymbol}:\n\n`;
        content += `NAV: $${latest.totalValueUsd.toFixed(0)} (${sign7d}${latest.pnl7dPct.toFixed(1)}% this week)\n`;
        content += `Trades this week: ${trades.filter(t => {
          const d = new Date(t.timestamp);
          return d > new Date(Date.now() - 7 * 86400000);
        }).length}\n\n`;
        content += `Share price: $${latest.sharePrice.toFixed(4)}`;
      }
      break;

    case 'trade-alert':
      if (trades.length > 0) {
        const lastTrade = trades[trades.length - 1];
        content = `Trade executed: ${lastTrade.amountIn} ${lastTrade.tokenIn} -> ${lastTrade.tokenOut}\n\n`;
        if (lastTrade.reason) content += `Reason: ${lastTrade.reason}`;
      }
      break;

    case 'thesis-update':
      if (thesis) {
        content = `Updated investment thesis for $${tokenData.tokenSymbol}:\n\n${thesis.slice(0, 250)}`;
      }
      break;
  }

  if (!content) {
    console.log('No data available for post generation.');
    return;
  }

  const post = {
    type: postType,
    content,
    generatedAt: new Date().toISOString(),
    fund: tokenData.tokenSymbol,
  };

  const filename = `${Date.now()}-${postType}.json`;
  fs.writeFileSync(`${postsDir}/${filename}`, JSON.stringify(post, null, 2));
  console.log(`Post generated: ${postsDir}/${filename}`);
  console.log(`Content: ${content}`);
}

main().catch((err) => {
  console.error('Post generation failed:', err.message);
  process.exit(1);
});
