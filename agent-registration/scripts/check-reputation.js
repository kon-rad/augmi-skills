#!/usr/bin/env node
/**
 * Check this agent's on-chain reputation from ERC-8004 Reputation Registry.
 *
 * Required env vars:
 *   AGENT_WALLET_ADDRESS
 *
 * Optional env vars:
 *   NETWORK (base|baseSepolia, default: base)
 */

const { createPublicClient, http } = require('viem');
const { base, baseSepolia } = require('viem/chains');
const fs = require('fs');

const IDENTITY_REGISTRY = {
  base: '0x8004A169FB4a3325136EB29fA0ceB6D2e539a432',
  baseSepolia: '0x8004A818BFB912233c491871b3d84c89A494BD9e',
};

const REPUTATION_REGISTRY = {
  base: '0x8004BAa17C55a88189AE136b182e5fdA19dE9b63',
  baseSepolia: '0x8004B663056A597Dffe9eCcC1965A193B7388713',
};

const IDENTITY_ABI = [
  {
    type: 'function',
    name: 'balanceOf',
    inputs: [{ name: 'owner', type: 'address' }],
    outputs: [{ name: '', type: 'uint256' }],
    stateMutability: 'view',
  },
  {
    type: 'function',
    name: 'tokenOfOwnerByIndex',
    inputs: [
      { name: 'owner', type: 'address' },
      { name: 'index', type: 'uint256' },
    ],
    outputs: [{ name: '', type: 'uint256' }],
    stateMutability: 'view',
  },
];

const REPUTATION_ABI = [
  {
    type: 'function',
    name: 'getReputation',
    inputs: [{ name: 'agentId', type: 'uint256' }],
    outputs: [
      { name: 'score', type: 'uint256' },
      { name: 'totalFeedback', type: 'uint256' },
    ],
    stateMutability: 'view',
  },
  {
    type: 'function',
    name: 'getSummary',
    inputs: [
      { name: 'agentId', type: 'uint256' },
      { name: 'clientAddresses', type: 'address[]' },
      { name: 'tag1', type: 'string' },
      { name: 'tag2', type: 'string' },
    ],
    outputs: [
      { name: 'count', type: 'uint256' },
      { name: 'summaryValue', type: 'uint256' },
      { name: 'summaryValueDecimals', type: 'uint8' },
    ],
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

  const chain = networkName === 'baseSepolia' ? baseSepolia : base;
  const client = createPublicClient({ chain, transport: http() });

  // Get agent ID from local file or on-chain
  let agentId = null;

  const registrationFile = '/data/agent-registration.json';
  if (fs.existsSync(registrationFile)) {
    const data = JSON.parse(fs.readFileSync(registrationFile, 'utf8'));
    agentId = BigInt(data.agentId);
    console.log(`Agent ID (from local): ${agentId}`);
  } else {
    // Look up on-chain
    const balance = await client.readContract({
      address: IDENTITY_REGISTRY[networkName],
      abi: IDENTITY_ABI,
      functionName: 'balanceOf',
      args: [walletAddress],
    });

    if (balance === 0n) {
      console.log('Not registered on-chain. Run register.js first.');
      process.exit(0);
    }

    agentId = await client.readContract({
      address: IDENTITY_REGISTRY[networkName],
      abi: IDENTITY_ABI,
      functionName: 'tokenOfOwnerByIndex',
      args: [walletAddress, 0n],
    });
    console.log(`Agent ID (from chain): ${agentId}`);
  }

  // Query reputation
  try {
    const [score, totalFeedback] = await client.readContract({
      address: REPUTATION_REGISTRY[networkName],
      abi: REPUTATION_ABI,
      functionName: 'getReputation',
      args: [agentId],
    });

    console.log(`\nReputation Score: ${score}`);
    console.log(`Total Feedback: ${totalFeedback}`);

    // Get summary
    const [count, summaryValue, decimals] = await client.readContract({
      address: REPUTATION_REGISTRY[networkName],
      abi: REPUTATION_ABI,
      functionName: 'getSummary',
      args: [agentId, [], '', ''],
    });

    console.log(`\nSummary:`);
    console.log(`  Feedback Count: ${count}`);
    console.log(`  Summary Value: ${summaryValue} (${decimals} decimals)`);

    if (count > 0n) {
      const avg = Number(summaryValue) / Math.pow(10, Number(decimals));
      console.log(`  Average Score: ${avg.toFixed(2)}`);
    } else {
      console.log('  No feedback received yet.');
    }
  } catch (err) {
    if (err.message.includes('revert') || err.message.includes('call')) {
      console.log('\nNo reputation data found (contract may not have data for this agent).');
    } else {
      throw err;
    }
  }
}

main().catch((err) => {
  console.error('Reputation check failed:', err.message);
  process.exit(1);
});
