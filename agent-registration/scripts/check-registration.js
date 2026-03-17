#!/usr/bin/env node
/**
 * Check if this agent is registered on ERC-8004 Identity Registry.
 */

const { createPublicClient, http } = require('viem');
const { base, baseSepolia } = require('viem/chains');
const fs = require('fs');

const IDENTITY_REGISTRY = {
  base: '0x8004A169FB4a3325136EB29fA0ceB6D2e539a432',
  baseSepolia: '0x8004A818BFB912233c491871b3d84c89A494BD9e',
};

const ABI = [
  {
    type: 'function',
    name: 'balanceOf',
    inputs: [{ name: 'owner', type: 'address' }],
    outputs: [{ name: '', type: 'uint256' }],
    stateMutability: 'view',
  },
];

async function main() {
  const walletAddress = process.env.AGENT_WALLET_ADDRESS;
  const networkName = process.env.NETWORK || 'base';

  if (!walletAddress) {
    console.error('AGENT_WALLET_ADDRESS required');
    process.exit(1);
  }

  // Check local registration file
  const registrationFile = '/data/agent-registration.json';
  if (fs.existsSync(registrationFile)) {
    const data = JSON.parse(fs.readFileSync(registrationFile, 'utf8'));
    console.log('Local registration found:');
    console.log(`  Agent ID: ${data.agentId}`);
    console.log(`  TX: ${data.txHash}`);
    console.log(`  Registered: ${data.registeredAt}`);
    console.log(`  Network: ${data.network}`);
  } else {
    console.log('No local registration file found.');
  }

  // Check on-chain
  const chain = networkName === 'baseSepolia' ? baseSepolia : base;
  const client = createPublicClient({ chain, transport: http() });

  const balance = await client.readContract({
    address: IDENTITY_REGISTRY[networkName],
    abi: ABI,
    functionName: 'balanceOf',
    args: [walletAddress],
  });

  if (balance > 0n) {
    console.log(`\nOn-chain: REGISTERED (${balance.toString()} token(s))`);
  } else {
    console.log('\nOn-chain: NOT REGISTERED');
    console.log('Run: node /data/skills/agent-registration/scripts/register.js');
  }
}

main().catch((err) => {
  console.error('Check failed:', err.message);
  process.exit(1);
});
