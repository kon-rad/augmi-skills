#!/usr/bin/env node
/**
 * Check token/vault status for this agent.
 */

const { createPublicClient, http } = require('viem');
const { base, baseSepolia } = require('viem/chains');
const fs = require('fs');

const VAULT_ABI = [
  { type: 'function', name: 'totalAssets', inputs: [], outputs: [{ type: 'uint256' }], stateMutability: 'view' },
  { type: 'function', name: 'totalSupply', inputs: [], outputs: [{ type: 'uint256' }], stateMutability: 'view' },
  { type: 'function', name: 'exitFeeBps', inputs: [], outputs: [{ type: 'uint256' }], stateMutability: 'view' },
];

async function main() {
  const tokenFile = '/data/agent-token.json';
  if (!fs.existsSync(tokenFile)) {
    console.log('No vault deployed yet.');
    console.log('Run: node /data/skills/agent-token-launch/scripts/launch-token.js');
    return;
  }

  const data = JSON.parse(fs.readFileSync(tokenFile, 'utf8'));
  const networkName = data.network || process.env.NETWORK || 'base';
  const chain = networkName === 'baseSepolia' ? baseSepolia : base;
  const client = createPublicClient({ chain, transport: http() });

  console.log(`Vault: ${data.vaultAddress}`);
  console.log(`Token: ${data.tokenName} ($${data.tokenSymbol})`);
  console.log(`Exit Fee: ${data.exitFeeBps / 100}%`);

  const [totalAssets, totalSupply, exitFeeBps] = await Promise.all([
    client.readContract({ address: data.vaultAddress, abi: VAULT_ABI, functionName: 'totalAssets' }),
    client.readContract({ address: data.vaultAddress, abi: VAULT_ABI, functionName: 'totalSupply' }),
    client.readContract({ address: data.vaultAddress, abi: VAULT_ABI, functionName: 'exitFeeBps' }),
  ]);

  const nav = Number(totalAssets) / 1e6;
  const shares = Number(totalSupply) / 1e18;
  const sharePrice = shares > 0 ? nav / shares : 1.0;

  console.log(`\nOn-chain status:`);
  console.log(`  NAV: $${nav.toFixed(2)} USDC`);
  console.log(`  Total Shares: ${shares.toFixed(4)}`);
  console.log(`  Share Price: $${sharePrice.toFixed(6)}`);
  console.log(`  Exit Fee: ${Number(exitFeeBps) / 100}%`);
}

main().catch((err) => {
  console.error('Check failed:', err.message);
  process.exit(1);
});
