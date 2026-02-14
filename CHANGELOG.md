# Changelog

All notable changes to x402-layer skill will be documented in this file.

## [1.1.1] - 2026-02-15

### Bug Fixes

- **Fixed AWAL CLI command**: Updated from `pay` to `x402 pay` (Coinbase CLI structure changed)
- **Fixed AWAL URL handling**: Pass full URL instead of split base/path format
- **Fixed endpoint creation for AWAL**: Worker now includes EIP-712 domain parameters (`name`, `version`) in payment requirements

### Worker Changes

- `src/handlers/agent.ts` - Added EIP-712 domain params to endpoint creation 402 response for AWAL compatibility

### Skill Changes

- `scripts/awal_bridge.py` - Updated CLI command and URL handling for AWAL x402 pay

### Tested

- AWAL endpoint creation: Verified working ($5 payment, 20,000 credits granted)
- PK mode: Unaffected, continues to work as before

### Backward Compatibility

- All changes are additive only
- PK mode (private-key) unchanged and fully functional
- AWAL mode is optional, only used when `X402_USE_AWAL=1` is set

## [1.1.0] - 2026-02-14

### Coinbase Agentic Wallet (AWAL) Integration

#### New Features
- **AWAL Support**: Full Coinbase Agentic Wallet integration for Base network payments
- **No Private Key Exposure**: Use AWAL mode to make payments without exposing private keys
- **Auto-Detection**: Automatic authentication mode detection (AWAL vs private-key)

#### Environment Variables Added
| Variable | Description |
|----------|-------------|
| `X402_USE_AWAL` | Set `1` to enable Coinbase Agentic Wallet for Base |
| `X402_AUTH_MODE` | Auth selection: `auto`, `private-key`, or `awal` (default: auto) |
| `X402_PREFER_NETWORK` | Network selection: `base` or `solana` (default: base) |
| `AWAL_PACKAGE` | NPM package/version for AWAL CLI (default: `awal@1.0.0`) |
| `AWAL_BIN` | Preinstalled `awal` binary path/name |
| `AWAL_FORCE_NPX` | Set `1` to force npx even when `awal` binary exists |

#### AWAL Dependency (Optional)
To use AWAL mode, users should first install the Coinbase skill:
```bash
npx skills add coinbase/agentic-wallet-skills
export X402_USE_AWAL=1
```

#### Backward Compatibility
- Private-key mode works exactly as before
- Solana payments unchanged (private-key only)
- All existing environment variables still supported

## [1.0.0] - 2026-02-02

### Initial Release

#### Consumer Mode
- **Pay-Per-Request**: Execute USDC payments on Base (100% reliable) and Solana networks
- **Credit System**: Pre-purchase credits for zero-latency API access
- **Marketplace Discovery**: Browse, search, and filter endpoints by category
- **Digital Products**: Purchase and download files via secure storage URLs

#### Provider Mode
- **Endpoint Creation**: Deploy monetized API endpoints ($5 one-time, includes 20,000 credits)
- **Marketplace Listing**: List endpoints during creation OR update afterward
- **Endpoint Management**: View stats, update pricing, check credit balances
- **Credit Top-up**: Recharge endpoint credits ($1 = 500 credits)
- **List/Unlist**: Control marketplace visibility

#### Security
- API key verification for origin servers (`x-api-key` header)
- EIP-712 typed data signatures (Base)
- Versioned transactions with fee payer support (Solana)

#### Networks
- **Base (EVM)** - Recommended, 100% reliable
- **Solana** - ~75% success rate (retry logic included)

#### Known Issues
- Solana payments may require retries due to facilitator infrastructure
- Endpoint stops working when credits reach 0 (use `topup_endpoint.py`)
