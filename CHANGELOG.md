# Changelog

All notable changes to x402-layer skill will be documented in this file.

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

#### Scripts Updated
- `pay_base.py` - AWAL payment support
- `create_endpoint.py` - AWAL support for $5 endpoint creation fee
- `topup_endpoint.py` - AWAL support for endpoint credit recharging
- `recharge_credits.py` - AWAL support for credit pack purchases
- `consume_product.py` - AWAL support for digital product consumption

#### SKILL.md Updates
- Added AWAL to skill description for discovery
- Added all environment variables to metadata frontmatter
- Added "Option B: Coinbase Agentic Wallet (AWAL)" setup section
- Added "Security Notice" section with best practices
- Updated environment reference table

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
- No breaking changes

## [1.0.0] - 2026-02-02

### 🎉 Initial Release

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

#### Scripts (11)
- `pay_base.py`, `pay_solana.py` - Direct payments
- `consume_credits.py`, `check_credits.py`, `recharge_credits.py` - Credit operations
- `consume_product.py` - Digital product purchases
- `discover_marketplace.py` - Marketplace browsing
- `create_endpoint.py`, `manage_endpoint.py`, `topup_endpoint.py` - Provider operations
- `list_on_marketplace.py` - Marketplace listing management

#### References
- `pay-per-request.md` - EIP-712 signing guide with Python examples
- `credit-based.md` - Credit system workflow
- `agentic-endpoints.md` - Endpoint creation flow
- `payment-signing.md` - Signature format reference
- `marketplace.md` - Marketplace API endpoints

#### Networks
- **Base (EVM)** - Recommended, 100% reliable
- **Solana** - ~75% success rate (retry logic included)

#### Known Issues
- Solana payments may require retries due to facilitator infrastructure
- Endpoint stops working when credits reach 0 (use `topup_endpoint.py`)
