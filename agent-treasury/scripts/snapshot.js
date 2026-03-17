#!/usr/bin/env node
/**
 * Take a NAV snapshot of the agent's vault.
 * Posts to platform API and saves locally.
 */

const { createPublicClient, http, formatUnits } = require('viem');
const { base, baseSepolia } = require('viem/chains');
const fs = require('fs');
const path = require('path');

const TOKENS = {
  USDC: { address: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913', decimals: 6, cgId: 'usd-coin' },
  WETH: { address: '0x4200000000000000000000000000000000000006', decimals: 18, cgId: 'ethereum' },
  cbBTC: { address: '0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf', decimals: 8, cgId: 'coinbase-wrapped-btc' },
  AERO: { address: '0x940181a94A35A4569E4529A3CDfB74e38FD98631', decimals: 18, cgId: 'aerodrome-finance' },
};

const ERC20_ABI = [
  { type: 'function', name: 'balanceOf', inputs: [{ type: 'address' }], outputs: [{ type: 'uint256' }], stateMutability: 'view' },
];

const VAULT_ABI = [
  { type: 'function', name: 'totalAssets', inputs: [], outputs: [{ type: 'uint256' }], stateMutability: 'view' },
  { type: 'function', name: 'totalSupply', inputs: [], outputs: [{ type: 'uint256' }], stateMutability: 'view' },
];

async function getPrices() {
  const ids = Object.values(TOKENS).map(t => t.cgId).join(',');
  try {
    const resp = await fetch(`https://api.coingecko.com/api/v3/simple/price?ids=${ids}&vs_currencies=usd`);
    return await resp.json();
  } catch {
    return {};
  }
}

async function main() {
  const tokenFile = '/data/agent-token.json';
  if (!fs.existsSync(tokenFile)) {
    console.error('No vault deployed.');
    process.exit(1);
  }

  const data = JSON.parse(fs.readFileSync(tokenFile, 'utf8'));
  const networkName = data.network || 'base';
  const chain = networkName === 'baseSepolia' ? baseSepolia : base;
  const client = createPublicClient({ chain, transport: http() });
  const vaultAddress = data.vaultAddress;

  // Get on-chain data
  const [totalAssets, totalSupply] = await Promise.all([
    client.readContract({ address: vaultAddress, abi: VAULT_ABI, functionName: 'totalAssets' }),
    client.readContract({ address: vaultAddress, abi: VAULT_ABI, functionName: 'totalSupply' }),
  ]);

  // Get prices
  const prices = await getPrices();

  // Get token balances in vault
  const holdings = [];
  let totalValueUsd = 0;

  for (const [symbol, token] of Object.entries(TOKENS)) {
    try {
      const balance = await client.readContract({
        address: token.address, abi: ERC20_ABI, functionName: 'balanceOf', args: [vaultAddress],
      });
      const amount = Number(formatUnits(balance, token.decimals));
      const price = prices[token.cgId]?.usd || (symbol === 'USDC' ? 1 : 0);
      const valueUsd = amount * price;

      if (amount > 0) {
        holdings.push({ token: token.address, symbol, amount, priceUsd: price, valueUsd });
        totalValueUsd += valueUsd;
      }
    } catch (e) { /* skip */ }
  }

  const shares = Number(totalSupply) / 1e18;
  const sharePrice = shares > 0 ? totalValueUsd / shares : 1.0;

  // Compare to previous snapshots for PnL
  const snapshotsDir = '/data/snapshots';
  fs.mkdirSync(snapshotsDir, { recursive: true });
  const files = fs.readdirSync(snapshotsDir).sort();

  let pnl24hPct = 0, pnl7dPct = 0, pnl30dPct = 0;

  if (files.length > 0) {
    const prev = JSON.parse(fs.readFileSync(`${snapshotsDir}/${files[files.length - 1]}`, 'utf8'));
    if (prev.totalValueUsd > 0) {
      pnl24hPct = ((totalValueUsd - prev.totalValueUsd) / prev.totalValueUsd) * 100;
    }
  }

  if (files.length >= 7) {
    const prev7d = JSON.parse(fs.readFileSync(`${snapshotsDir}/${files[Math.max(0, files.length - 7)]}`, 'utf8'));
    if (prev7d.totalValueUsd > 0) {
      pnl7dPct = ((totalValueUsd - prev7d.totalValueUsd) / prev7d.totalValueUsd) * 100;
    }
  }

  if (files.length >= 30) {
    const prev30d = JSON.parse(fs.readFileSync(`${snapshotsDir}/${files[Math.max(0, files.length - 30)]}`, 'utf8'));
    if (prev30d.totalValueUsd > 0) {
      pnl30dPct = ((totalValueUsd - prev30d.totalValueUsd) / prev30d.totalValueUsd) * 100;
    }
  }

  const snapshot = {
    totalValueUsd,
    sharePrice,
    totalShares: shares,
    holdings,
    pnl24hPct: Math.round(pnl24hPct * 100) / 100,
    pnl7dPct: Math.round(pnl7dPct * 100) / 100,
    pnl30dPct: Math.round(pnl30dPct * 100) / 100,
    snapshotAt: new Date().toISOString(),
  };

  // Save locally
  const today = new Date().toISOString().slice(0, 10);
  fs.writeFileSync(`${snapshotsDir}/${today}.json`, JSON.stringify(snapshot, null, 2));
  console.log(`Snapshot saved: $${totalValueUsd.toFixed(2)} NAV, ${holdings.length} tokens`);

  // Post to platform
  const augmiApiUrl = process.env.AUGMI_API_URL;
  const agentId = process.env.AGENT_ID;
  const containerApiKey = process.env.CONTAINER_API_KEY;
  if (augmiApiUrl && agentId && containerApiKey) {
    try {
      await fetch(`${augmiApiUrl}/api/agents/${agentId}/portfolio`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${containerApiKey}` },
        body: JSON.stringify(snapshot),
      });
      console.log('Snapshot posted to platform');
    } catch (e) { console.warn('Platform post failed:', e.message); }
  }
}

main().catch((err) => {
  console.error('Snapshot failed:', err.message);
  process.exit(1);
});
