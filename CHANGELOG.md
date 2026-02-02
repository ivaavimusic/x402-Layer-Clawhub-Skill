# Changelog

All notable changes to x402-layer skill will be documented in this file.

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
