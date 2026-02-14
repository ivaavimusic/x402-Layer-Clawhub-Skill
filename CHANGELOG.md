## [1.1.2] - 2026-02-15

### Bug Fixes

- **Fixed AWAL CLI command**: Updated from `pay` to `x402 pay` (Coinbase CLI change)
- **Fixed AWAL URL handling**: Pass full URL instead of split base/path
- **Added EIP-712 domain params**: Worker now includes `name` and `version` in payment requirements for AWAL compatibility

### Files Changed

- `scripts/awal_bridge.py` - Updated CLI command and URL handling
- Worker `src/handlers/agent.ts` - Added EIP-712 domain parameters

### Tested

- AWAL endpoint creation verified working ($5 payment, 20,000 credits)

# Changelog

All notable changes to x402-layer skill will be documented in this file.

## [1.1.1] - 2026-02-14

### Bug Fixes

- **Fixed AWAL endpoint creation**: Removed unsupported `-h` header flag from AWAL CLI calls
  - AWAL `pay` command does not support custom headers
  - The `-h` flag was being interpreted as `--help`, causing endpoint creation to fail
  - Wallet address is passed in POST body data, so headers are not needed
- **Added missing AWAL support scripts** to GitHub repo:
  - `awal_bridge.py` - Core AWAL payment functionality
  - `awal_cli.py` - AWAL CLI wrapper
  - `wallet_signing.py` - Wallet signing with `is_awal_mode()`
  - `network_selection.py` - Network/auth selection logic
  - `solana_signing.py` - Solana signing utilities

### Files Changed

