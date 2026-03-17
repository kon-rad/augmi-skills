#!/usr/bin/env node
/**
 * Check vault portfolio — NAV, holdings, and allocation.
 */

const { createPublicClient, http, formatUnits } = require('viem');
const { base, baseSepolia } = require('viem/chains');
const fs = require('fs');

const TOKENS = {
  USDC: { address: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913', decimals: 6 },
  WETH: { address: '0x4200000000000000000000000000000000000006', decimals: 18 },
  cbBTC: { address: '0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf', decimals: 8 },
  AERO: { address: '0x940181a94A35A4569E4529A3CDfB74e38FD98631', decimals: 18 },
};

const ERC20_ABI = [
  { type: 'function', name: 'balanceOf', inputs: [{ type: 'address' }], outputs: [{ type: 'uint256' }], stateMutability: 'view' },
];

const VAULT_ABI = [
  { type: 'function', name: 'totalAssets', inputs: [], outputs: [{ type: 'uint256' }], stateMutability: 'view' },
  { type: 'function', name: 'totalSupply', inputs: [], outputs: [{ type: 'uint256' }], stateMutability: 'view' },
];

async function main() {
  const tokenFile = '/data/agent-token.json';
  if (!fs.existsSync(tokenFile)) {
    console.log('No vault deployed.');
    process.exit(1);
  }

  const data = JSON.parse(fs.readFileSync(tokenFile, 'utf8'));
  const networkName = data.network || 'base';
  const chain = networkName === 'baseSepolia' ? baseSepolia : base;
  const client = createPublicClient({ chain, transport: http() });

  const vaultAddress = data.vaultAddress;

  // Get vault NAV and supply
  const [totalAssets, totalSupply] = await Promise.all([
    client.readContract({ address: vaultAddress, abi: VAULT_ABI, functionName: 'totalAssets' }),
    client.readContract({ address: vaultAddress, abi: VAULT_ABI, functionName: 'totalSupply' }),
  ]);

  const nav = Number(totalAssets) / 1e6;
  const shares = Number(totalSupply) / 1e18;
  const sharePrice = shares > 0 ? nav / shares : 1.0;

  console.log(`=== Portfolio: ${data.tokenName} ($${data.tokenSymbol}) ===`);
  console.log(`NAV: $${nav.toFixed(2)} USDC`);
  console.log(`Share Price: $${sharePrice.toFixed(6)}`);
  console.log(`Total Shares: ${shares.toFixed(4)}`);
  console.log('');

  // Check individual token balances in vault
  console.log('Holdings:');
  for (const [symbol, token] of Object.entries(TOKENS)) {
    try {
      const balance = await client.readContract({
        address: token.address,
        abi: ERC20_ABI,
        functionName: 'balanceOf',
        args: [vaultAddress],
      });
      const formatted = formatUnits(balance, token.decimals);
      if (Number(formatted) > 0) {
        console.log(`  ${symbol}: ${formatted}`);
      }
    } catch (e) { /* skip */ }
  }
}

main().catch((err) => {
  console.error('Portfolio check failed:', err.message);
  process.exit(1);
});
