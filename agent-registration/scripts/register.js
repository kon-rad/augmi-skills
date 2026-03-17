#!/usr/bin/env node
/**
 * Agent Registration Script
 * Registers this agent on the ERC-8004 Identity Registry on Base.
 *
 * Required env vars:
 *   AGENT_WALLET_PRIVATE_KEY, AGENT_WALLET_ADDRESS, AGENT_ID,
 *   AUGMI_API_URL, CONTAINER_API_KEY
 *
 * Optional env vars:
 *   AGENT_NAME, AGENT_DESCRIPTION, AGENT_SKILLS (comma-separated),
 *   NETWORK (base|baseSepolia, default: base)
 */

const { createWalletClient, createPublicClient, http, parseAbiItem } = require('viem');
const { privateKeyToAccount } = require('viem/accounts');
const { base, baseSepolia } = require('viem/chains');
const fs = require('fs');
const path = require('path');

const IDENTITY_REGISTRY = {
  base: '0x8004A169FB4a3325136EB29fA0ceB6D2e539a432',
  baseSepolia: '0x8004A818BFB912233c491871b3d84c89A494BD9e',
};

const REGISTER_ABI = [
  {
    type: 'function',
    name: 'register',
    inputs: [{ name: 'agentURI', type: 'string', internalType: 'string' }],
    outputs: [{ name: 'agentId', type: 'uint256', internalType: 'uint256' }],
    stateMutability: 'nonpayable',
  },
  {
    type: 'event',
    name: 'Registered',
    inputs: [
      { name: 'agentId', type: 'uint256', indexed: true },
      { name: 'owner', type: 'address', indexed: true },
      { name: 'agentURI', type: 'string', indexed: false },
    ],
  },
];

async function main() {
  const privateKey = process.env.AGENT_WALLET_PRIVATE_KEY;
  const walletAddress = process.env.AGENT_WALLET_ADDRESS;
  const agentId = process.env.AGENT_ID;
  const augmiApiUrl = process.env.AUGMI_API_URL;
  const containerApiKey = process.env.CONTAINER_API_KEY;
  const networkName = process.env.NETWORK || 'base';

  if (!privateKey || !walletAddress) {
    console.error('ERROR: AGENT_WALLET_PRIVATE_KEY and AGENT_WALLET_ADDRESS required');
    process.exit(1);
  }

  // Check if already registered
  const registrationFile = '/data/agent-registration.json';
  if (fs.existsSync(registrationFile)) {
    const existing = JSON.parse(fs.readFileSync(registrationFile, 'utf8'));
    console.log(`Already registered with agentId: ${existing.agentId}`);
    console.log(`TX: ${existing.txHash}`);
    return;
  }

  const chain = networkName === 'baseSepolia' ? baseSepolia : base;
  const registryAddress = IDENTITY_REGISTRY[networkName];
  const account = privateKeyToAccount(privateKey);

  const publicClient = createPublicClient({
    chain,
    transport: http(),
  });

  const walletClient = createWalletClient({
    account,
    chain,
    transport: http(),
  });

  // Build agent URI
  const agentURI = JSON.stringify({
    name: process.env.AGENT_NAME || 'Augmi Agent',
    description: process.env.AGENT_DESCRIPTION || 'An autonomous AI agent powered by Augmi',
    skills: (process.env.AGENT_SKILLS || 'trading,research,analysis').split(','),
    platform: 'augmi.world',
    version: '1.0',
  });

  console.log(`Registering agent on ${networkName}...`);
  console.log(`Registry: ${registryAddress}`);
  console.log(`Wallet: ${walletAddress}`);
  console.log(`URI: ${agentURI}`);

  // Check balance
  const balance = await publicClient.getBalance({ address: walletAddress });
  console.log(`Balance: ${Number(balance) / 1e18} ETH`);
  if (balance === 0n) {
    console.error('ERROR: No ETH for gas. Fund wallet with Base ETH first.');
    process.exit(1);
  }

  // Send registration transaction
  const hash = await walletClient.writeContract({
    address: registryAddress,
    abi: REGISTER_ABI,
    functionName: 'register',
    args: [agentURI],
  });

  console.log(`TX submitted: ${hash}`);
  console.log('Waiting for confirmation...');

  const receipt = await publicClient.waitForTransactionReceipt({ hash });
  console.log(`Confirmed in block: ${receipt.blockNumber}`);

  // Parse Registered event to get agentId
  let registeredAgentId = 'unknown';
  for (const log of receipt.logs) {
    try {
      if (log.topics[0] === '0x' + 'Registered'.padEnd(64, '0')) {
        // First indexed param is agentId
        registeredAgentId = BigInt(log.topics[1]).toString();
      }
    } catch (e) {
      // Try parsing numerically from first topic after event signature
      if (log.topics.length >= 2) {
        registeredAgentId = BigInt(log.topics[1]).toString();
      }
    }
  }

  const result = {
    agentId: registeredAgentId,
    txHash: hash,
    registeredAt: new Date().toISOString(),
    agentURI,
    network: networkName,
    walletAddress,
  };

  // Save locally
  fs.mkdirSync(path.dirname(registrationFile), { recursive: true });
  fs.writeFileSync(registrationFile, JSON.stringify(result, null, 2));
  console.log(`Registration saved to ${registrationFile}`);

  // Report to Augmi platform
  if (augmiApiUrl && containerApiKey && agentId) {
    try {
      const response = await fetch(`${augmiApiUrl}/api/agents/${agentId}/marketplace`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${containerApiKey}`,
        },
        body: JSON.stringify({
          erc8004Id: registeredAgentId,
          walletAddress,
        }),
      });
      console.log(`Platform notified: ${response.status}`);
    } catch (e) {
      console.warn('Failed to notify platform:', e.message);
    }
  }

  console.log(`\nAgent registered successfully!`);
  console.log(`Agent ID: ${registeredAgentId}`);
  console.log(`TX: ${hash}`);
}

main().catch((err) => {
  console.error('Registration failed:', err.message);
  process.exit(1);
});
