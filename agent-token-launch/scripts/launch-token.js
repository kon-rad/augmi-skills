#!/usr/bin/env node
/**
 * Launch agent token by deploying an ERC-4626 vault via AgentTokenFactory.
 *
 * Usage:
 *   node launch-token.js --name "Alpha Fund" --symbol "ALPHA" --exitFee 200
 *
 * Required env: AGENT_WALLET_PRIVATE_KEY, AGENT_WALLET_ADDRESS,
 *   AGENT_TOKEN_FACTORY_ADDRESS, AGENT_CREATOR_WALLET
 */

const { createWalletClient, createPublicClient, http, decodeEventLog } = require('viem');
const { privateKeyToAccount } = require('viem/accounts');
const { base, baseSepolia } = require('viem/chains');
const fs = require('fs');

const FACTORY_ABI = [
  {
    type: 'function',
    name: 'createAgentVault',
    inputs: [
      { name: 'tokenName', type: 'string' },
      { name: 'tokenSymbol', type: 'string' },
      { name: 'agentWallet', type: 'address' },
      { name: 'creatorWallet', type: 'address' },
      { name: 'exitFeeBps', type: 'uint256' },
    ],
    outputs: [{ name: 'vaultAddress', type: 'address' }],
    stateMutability: 'nonpayable',
  },
  {
    type: 'function',
    name: 'getVaultForAgent',
    inputs: [{ name: 'agentWallet', type: 'address' }],
    outputs: [{ name: '', type: 'address' }],
    stateMutability: 'view',
  },
  {
    type: 'event',
    name: 'AgentVaultCreated',
    inputs: [
      { name: 'agentWallet', type: 'address', indexed: true },
      { name: 'creator', type: 'address', indexed: true },
      { name: 'vault', type: 'address', indexed: false },
      { name: 'tokenName', type: 'string', indexed: false },
      { name: 'tokenSymbol', type: 'string', indexed: false },
    ],
  },
];

function parseArgs() {
  const args = process.argv.slice(2);
  const result = {
    name: process.env.AGENT_TOKEN_NAME || 'Agent Fund',
    symbol: process.env.AGENT_TOKEN_SYMBOL || 'AGENT',
    exitFee: parseInt(process.env.AGENT_EXIT_FEE_BPS || '200'),
  };
  for (let i = 0; i < args.length; i += 2) {
    if (args[i] === '--name') result.name = args[i + 1];
    if (args[i] === '--symbol') result.symbol = args[i + 1];
    if (args[i] === '--exitFee') result.exitFee = parseInt(args[i + 1]);
  }
  return result;
}

async function main() {
  const { name, symbol, exitFee } = parseArgs();
  const privateKey = process.env.AGENT_WALLET_PRIVATE_KEY;
  const walletAddress = process.env.AGENT_WALLET_ADDRESS;
  const factoryAddress = process.env.AGENT_TOKEN_FACTORY_ADDRESS;
  const creatorWallet = process.env.AGENT_CREATOR_WALLET;
  const networkName = process.env.NETWORK || 'base';

  if (!privateKey || !walletAddress || !factoryAddress || !creatorWallet) {
    console.error('Required env vars: AGENT_WALLET_PRIVATE_KEY, AGENT_WALLET_ADDRESS, AGENT_TOKEN_FACTORY_ADDRESS, AGENT_CREATOR_WALLET');
    process.exit(1);
  }

  // Check if already deployed
  const tokenFile = '/data/agent-token.json';
  if (fs.existsSync(tokenFile)) {
    const existing = JSON.parse(fs.readFileSync(tokenFile, 'utf8'));
    console.log(`Vault already deployed at: ${existing.vaultAddress}`);
    return;
  }

  const chain = networkName === 'baseSepolia' ? baseSepolia : base;
  const account = privateKeyToAccount(privateKey);

  const publicClient = createPublicClient({ chain, transport: http() });
  const walletClient = createWalletClient({ account, chain, transport: http() });

  // Check if vault already exists on-chain
  const existingVault = await publicClient.readContract({
    address: factoryAddress,
    abi: FACTORY_ABI,
    functionName: 'getVaultForAgent',
    args: [walletAddress],
  });

  if (existingVault !== '0x0000000000000000000000000000000000000000') {
    console.log(`Vault already exists on-chain: ${existingVault}`);
    const result = { vaultAddress: existingVault, tokenName: name, tokenSymbol: symbol, exitFeeBps: exitFee, network: networkName };
    fs.writeFileSync(tokenFile, JSON.stringify(result, null, 2));
    return;
  }

  console.log(`Deploying vault: ${name} ($${symbol}), exit fee: ${exitFee / 100}%`);

  const hash = await walletClient.writeContract({
    address: factoryAddress,
    abi: FACTORY_ABI,
    functionName: 'createAgentVault',
    args: [name, symbol, walletAddress, creatorWallet, BigInt(exitFee)],
  });

  console.log(`TX: ${hash}`);
  const receipt = await publicClient.waitForTransactionReceipt({ hash });
  console.log(`Confirmed in block: ${receipt.blockNumber}`);

  // Parse vault address from event
  let vaultAddress = null;
  for (const log of receipt.logs) {
    try {
      const decoded = decodeEventLog({ abi: FACTORY_ABI, data: log.data, topics: log.topics });
      if (decoded.eventName === 'AgentVaultCreated') {
        vaultAddress = decoded.args.vault;
        break;
      }
    } catch (e) { /* skip non-matching logs */ }
  }

  if (!vaultAddress) {
    console.error('Could not parse vault address from events');
    process.exit(1);
  }

  const result = {
    vaultAddress,
    tokenName: name,
    tokenSymbol: symbol,
    exitFeeBps: exitFee,
    deployedAt: new Date().toISOString(),
    txHash: hash,
    network: networkName,
    creatorWallet,
    agentWallet: walletAddress,
  };

  fs.writeFileSync(tokenFile, JSON.stringify(result, null, 2));
  console.log(`\nVault deployed: ${vaultAddress}`);
  console.log(`Saved to ${tokenFile}`);

  // Report to platform
  const augmiApiUrl = process.env.AUGMI_API_URL;
  const agentId = process.env.AGENT_ID;
  const containerApiKey = process.env.CONTAINER_API_KEY;
  if (augmiApiUrl && agentId && containerApiKey) {
    try {
      await fetch(`${augmiApiUrl}/api/agents/${agentId}/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${containerApiKey}` },
        body: JSON.stringify(result),
      });
      console.log('Platform notified');
    } catch (e) {
      console.warn('Platform notify failed:', e.message);
    }
  }
}

main().catch((err) => {
  console.error('Launch failed:', err.message);
  process.exit(1);
});
