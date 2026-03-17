#!/usr/bin/env node
/**
 * Update the agent's investment thesis based on current portfolio.
 * The agent (Claude) uses this data to reason about strategy.
 */

const fs = require('fs');

async function main() {
  const snapshotsDir = '/data/snapshots';
  const strategyDir = '/data/strategy';
  fs.mkdirSync(strategyDir, { recursive: true });

  // Read current state
  const tokenFile = '/data/agent-token.json';
  const tokenData = fs.existsSync(tokenFile) ? JSON.parse(fs.readFileSync(tokenFile, 'utf8')) : null;

  // Read recent snapshots
  const snapshots = [];
  if (fs.existsSync(snapshotsDir)) {
    const files = fs.readdirSync(snapshotsDir).sort().slice(-7);
    for (const f of files) {
      snapshots.push(JSON.parse(fs.readFileSync(`${snapshotsDir}/${f}`, 'utf8')));
    }
  }

  // Read recent trades
  const historyFile = '/data/trade-history.json';
  const trades = fs.existsSync(historyFile) ? JSON.parse(fs.readFileSync(historyFile, 'utf8')).slice(-10) : [];

  // Read current thesis
  const thesisFile = `${strategyDir}/thesis.md`;
  const currentThesis = fs.existsSync(thesisFile) ? fs.readFileSync(thesisFile, 'utf8') : 'No thesis established yet.';

  // Build context for thesis update
  const context = {
    fund: tokenData ? `${tokenData.tokenName} ($${tokenData.tokenSymbol})` : 'Not launched',
    currentThesis,
    recentPerformance: snapshots.length > 0 ? snapshots[snapshots.length - 1] : null,
    recentTrades: trades,
    snapshotCount: snapshots.length,
    updatedAt: new Date().toISOString(),
  };

  // Save context for the agent to read and reason about
  fs.writeFileSync(`${strategyDir}/thesis-context.json`, JSON.stringify(context, null, 2));

  console.log('Thesis context updated at /data/strategy/thesis-context.json');
  console.log('The agent should now read this context and update /data/strategy/thesis.md');

  // Post to platform
  const augmiApiUrl = process.env.AUGMI_API_URL;
  const agentId = process.env.AGENT_ID;
  const containerApiKey = process.env.CONTAINER_API_KEY;
  if (augmiApiUrl && agentId && containerApiKey && currentThesis !== 'No thesis established yet.') {
    try {
      await fetch(`${augmiApiUrl}/api/agents/${agentId}/strategy`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${containerApiKey}` },
        body: JSON.stringify({ thesisText: currentThesis }),
      });
      console.log('Thesis posted to platform');
    } catch (e) { console.warn('Platform update failed:', e.message); }
  }
}

main().catch((err) => {
  console.error('Thesis update failed:', err.message);
  process.exit(1);
});
