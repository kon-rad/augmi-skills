#!/usr/bin/env node
/**
 * Execute a token swap through the agent's vault on Uniswap V3 (Base).
 *
 * Usage:
 *   node swap.js --tokenIn USDC --tokenOut WETH --amountIn 100 --reason "Bullish on ETH"
 */

const { createWalletClient, createPublicClient, http, encodeFunctionData, parseUnits } = require('viem');
const { privateKeyToAccount } = require('viem/accounts');
const { base, baseSepolia } = require('viem/chains');
const fs = require('fs');

// Well-known tokens on Base
const TOKENS = {
  USDC: { address: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913', decimals: 6 },
  WETH: { address: '0x4200000000000000000000000000000000000006', decimals: 18 },
  cbBTC: { address: '0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf', decimals: 8 },
  AERO: { address: '0x940181a94A35A4569E4529A3CDfB74e38FD98631', decimals: 18 },
};

const UNISWAP_V3_ROUTER = '0x3fC91A3afd70395Cd496C647d5a6CC9D4B2b7FAD';

const VAULT_ABI = [
  {
    type: 'function', name: 'executeTrade',
    inputs: [
      { name: 'router', type: 'address' },
      { name: 'tradeCallData', type: 'bytes' },
      { name: 'tokenIn', type: 'address' },
      { name: 'amountIn', type: 'uint256' },
    ],
    outputs: [], stateMutability: 'nonpayable',
  },
  { type: 'function', name: 'totalAssets', inputs: [], outputs: [{ type: 'uint256' }], stateMutability: 'view' },
];

// Uniswap V3 SwapRouter02 exactInputSingle
const SWAP_ROUTER_ABI = [{
  type: 'function', name: 'exactInputSingle',
  inputs: [{
    name: 'params', type: 'tuple',
    components: [
      { name: 'tokenIn', type: 'address' },
      { name: 'tokenOut', type: 'address' },
      { name: 'fee', type: 'uint24' },
      { name: 'recipient', type: 'address' },
      { name: 'amountIn', type: 'uint256' },
      { name: 'amountOutMinimum', type: 'uint256' },
      { name: 'sqrtPriceLimitX96', type: 'uint160' },
    ],
  }],
  outputs: [{ name: 'amountOut', type: 'uint256' }],
  stateMutability: 'nonpayable',
}];

function parseArgs() {
  const args = process.argv.slice(2);
  const result = { tokenIn: 'USDC', tokenOut: 'WETH', amountIn: '100', slippage: 50, reason: '' };
  for (let i = 0; i < args.length; i += 2) {
    if (args[i] === '--tokenIn') result.tokenIn = args[i + 1];
    if (args[i] === '--tokenOut') result.tokenOut = args[i + 1];
    if (args[i] === '--amountIn') result.amountIn = args[i + 1];
    if (args[i] === '--slippage') result.slippage = parseInt(args[i + 1]);
    if (args[i] === '--reason') result.reason = args[i + 1];
  }
  return result;
}

async function main() {
  const { tokenIn, tokenOut, amountIn, slippage, reason } = parseArgs();

  const tokenInInfo = TOKENS[tokenIn] || { address: tokenIn, decimals: 18 };
  const tokenOutInfo = TOKENS[tokenOut] || { address: tokenOut, decimals: 18 };

  const tokenFile = '/data/agent-token.json';
  if (!fs.existsSync(tokenFile)) {
    console.error('No vault found. Run agent-token-launch first.');
    process.exit(1);
  }

  const vaultData = JSON.parse(fs.readFileSync(tokenFile, 'utf8'));
  const vaultAddress = vaultData.vaultAddress;
  const networkName = vaultData.network || 'base';
  const chain = networkName === 'baseSepolia' ? baseSepolia : base;

  const account = privateKeyToAccount(process.env.AGENT_WALLET_PRIVATE_KEY);
  const publicClient = createPublicClient({ chain, transport: http() });
  const walletClient = createWalletClient({ account, chain, transport: http() });

  // Risk check
  const configFile = '/data/agent-trading-config.json';
  const config = fs.existsSync(configFile) ? JSON.parse(fs.readFileSync(configFile, 'utf8')) : {
    maxPositionPct: 20, maxDrawdownPct: 25, dailyTradeLimit: 10,
    allowedTokens: ['USDC', 'WETH', 'cbBTC', 'AERO'],
  };

  if (!config.allowedTokens.includes(tokenOut) && !Object.keys(TOKENS).includes(tokenOut)) {
    console.error(`Token ${tokenOut} not in allowed list`);
    process.exit(1);
  }

  // Check daily trade count
  const historyFile = '/data/trade-history.json';
  const history = fs.existsSync(historyFile) ? JSON.parse(fs.readFileSync(historyFile, 'utf8')) : [];
  const today = new Date().toISOString().slice(0, 10);
  const todayTrades = history.filter(t => t.timestamp?.startsWith(today));
  if (todayTrades.length >= config.dailyTradeLimit) {
    console.error(`Daily trade limit reached (${config.dailyTradeLimit})`);
    process.exit(1);
  }

  const amountInParsed = parseUnits(amountIn, tokenInInfo.decimals);

  console.log(`Swapping ${amountIn} ${tokenIn} → ${tokenOut}`);
  console.log(`Vault: ${vaultAddress}`);

  // Encode Uniswap V3 swap calldata
  const swapCalldata = encodeFunctionData({
    abi: SWAP_ROUTER_ABI,
    functionName: 'exactInputSingle',
    args: [{
      tokenIn: tokenInInfo.address,
      tokenOut: tokenOutInfo.address,
      fee: 3000, // 0.3% pool
      recipient: vaultAddress, // tokens go back to vault
      amountIn: amountInParsed,
      amountOutMinimum: 0n, // TODO: use quote for slippage protection
      sqrtPriceLimitX96: 0n,
    }],
  });

  // Execute via vault
  const hash = await walletClient.writeContract({
    address: vaultAddress,
    abi: VAULT_ABI,
    functionName: 'executeTrade',
    args: [UNISWAP_V3_ROUTER, swapCalldata, tokenInInfo.address, amountInParsed],
  });

  console.log(`TX: ${hash}`);
  const receipt = await publicClient.waitForTransactionReceipt({ hash });
  console.log(`Confirmed block: ${receipt.blockNumber}`);

  // Log trade
  const trade = {
    tokenIn, tokenOut, amountIn, txHash: hash,
    timestamp: new Date().toISOString(), reason, network: networkName,
  };
  history.push(trade);
  fs.writeFileSync(historyFile, JSON.stringify(history, null, 2));

  // Report to platform
  const augmiApiUrl = process.env.AUGMI_API_URL;
  const agentId = process.env.AGENT_ID;
  const containerApiKey = process.env.CONTAINER_API_KEY;
  if (augmiApiUrl && agentId && containerApiKey) {
    try {
      await fetch(`${augmiApiUrl}/api/agents/${agentId}/trades`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${containerApiKey}` },
        body: JSON.stringify({
          tokenIn: tokenInInfo.address, tokenInSymbol: tokenIn,
          tokenOut: tokenOutInfo.address, tokenOutSymbol: tokenOut,
          amountIn, amountOut: '0', txHash: hash, thesisReason: reason,
        }),
      });
    } catch (e) { console.warn('Platform notify failed:', e.message); }
  }

  console.log('Trade complete.');
}

main().catch((err) => {
  console.error('Swap failed:', err.message);
  process.exit(1);
});
