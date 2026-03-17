#!/usr/bin/env node
/**
 * Fetch current token prices from CoinGecko.
 */

const COINGECKO_IDS = {
  USDC: 'usd-coin',
  WETH: 'ethereum',
  cbBTC: 'coinbase-wrapped-btc',
  AERO: 'aerodrome-finance',
};

async function main() {
  const ids = Object.values(COINGECKO_IDS).join(',');
  const url = `https://api.coingecko.com/api/v3/simple/price?ids=${ids}&vs_currencies=usd`;

  const response = await fetch(url);
  const data = await response.json();

  console.log('Current Prices (USD):');
  for (const [symbol, cgId] of Object.entries(COINGECKO_IDS)) {
    const price = data[cgId]?.usd ?? 'N/A';
    console.log(`  ${symbol}: $${price}`);
  }

  // Output as JSON for other scripts to consume
  const priceMap = {};
  for (const [symbol, cgId] of Object.entries(COINGECKO_IDS)) {
    priceMap[symbol] = data[cgId]?.usd ?? 0;
  }

  const fs = require('fs');
  fs.writeFileSync('/data/prices.json', JSON.stringify(priceMap, null, 2));
  console.log('\nSaved to /data/prices.json');
}

main().catch((err) => {
  console.error('Price feed failed:', err.message);
  process.exit(1);
});
