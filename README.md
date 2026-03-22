# x402-Layer ClawHub Skill

⚡ **x402 Singularity Layer** - Agentic payment infrastructure for AI agents.

[![Distribution](https://img.shields.io/badge/distribution-self--hosted-blue)](https://api.x402layer.cc/skill/x402-layer)
[![Version](https://img.shields.io/badge/version-1.5.0-green)](./SKILL.md)
[![License](https://img.shields.io/badge/license-MIT-purple)](./LICENSE)

## What is x402-Layer?

x402 is a **Web3 payment layer** enabling AI agents to:
- 💰 **Pay** for API access using USDC
- 🚀 **Deploy** monetized endpoints  
- 🔍 **Discover** services via marketplace
- 📊 **Manage** endpoints and credits
- 🔔 **Webhooks** — receive payment notifications
- 🤖 **Register and manage** ERC-8004 / Solana-8004 agents with wallet-first ownership

**Networks:** Base • Ethereum • Polygon • BSC • Monad • Solana  
**Currency:** USDC  
**Protocol:** HTTP 402 Payment Required

## Installation

### Self-Hosted
```bash
curl -fsSL https://api.x402layer.cc/skill/x402-layer/install | bash
```

> `v1.5.0` adds a first-class payments integration guide, plus the PayAI-safe Solana signer limit used by the current live flow.

### Manual
```bash
git clone https://github.com/ivaavimusic/x402-Layer-Clawhub-Skill.git ~/.agent/skills/x402-layer
pip install -r ~/.agent/skills/x402-layer/requirements.txt
```

## Quick Start

```bash
# Set up wallet
export WALLET_ADDRESS="0x..."
export PRIVATE_KEY="0x..."

# Pay for an API
python ~/.agent/skills/x402-layer/scripts/pay_base.py https://api.x402layer.cc/e/weather-data

# Browse marketplace
python ~/.agent/skills/x402-layer/scripts/discover_marketplace.py
```

## Documentation

📖 [Full Documentation](https://studio.x402layer.cc/docs/agentic-access/openclaw-skill)

## Scripts

| Script | Purpose |
|--------|---------|
| `pay_base.py` | Pay for endpoint on Base network |
| `pay_solana.py` | Pay for endpoint on Solana network |
| `consume_credits.py` | Use pre-purchased credits |
| `check_credits.py` | Check credit balance |
| `recharge_credits.py` | Buy credit packs |
| `discover_marketplace.py` | Browse marketplace |
| `create_endpoint.py` | Deploy monetized endpoint ($1) |
| `manage_endpoint.py` | View/update endpoints |
| `topup_endpoint.py` | Recharge endpoint credits |
| `list_on_marketplace.py` | List/unlist from marketplace |
| `consume_product.py` | Purchase digital products |
| `manage_webhook.py` | Set/update/remove endpoint webhooks |
| `verify_webhook_payment.py` | Verify webhook signature + payment receipt genuineness (PyJWT/JWKS) |
| `register_agent.py` | Register ERC-8004 / Solana-8004 agent with wallet-first flow and rich metadata |
| `list_my_endpoints.py` | List platform endpoints available for ERC-8004 agent binding |
| `list_agents.py` | List wallet-owned ERC-8004 / Solana-8004 agents |
| `update_agent.py` | Update ERC-8004 / Solana-8004 metadata, visibility, and endpoint bindings |
| `submit_feedback.py` | Submit on-chain reputation feedback |

> **Security Note:** When you create an endpoint, you will receive an **API Key**. You **must** save this key and configure your origin server to verify the `x-api-key` header in incoming requests. This ensures only paying users (proxied via x402) can access your API.

## Tags

`web3` `payments` `api` `usdc` `base` `solana` `agentic` `monetization` `marketplace` `credits` `webhooks` `x402` `x402-protocol` `x402-singularity-layer` `SGL`

## Resources

- 📦 **Skill Manifest:** [api.x402layer.cc/skill/x402-layer](https://api.x402layer.cc/skill/x402-layer)
- 📖 **Documentation:** [studio.x402layer.cc/docs](https://studio.x402layer.cc/docs/agentic-access/openclaw-skill)
- 🌐 **x402 Studio:** [studio.x402layer.cc](https://studio.x402layer.cc)
- 🐦 **OpenClaw:** [@openclaw](https://x.com/openclaw)

## License

MIT © [EventHorizon Labs](https://ehlabs.xyz)

## Changelog
### v1.5.0
- **Payments:** Added a first-class "integrate crypto payments into my app/platform" intent to the skill router
- **Payments:** Added `references/payments-integration.md` covering direct endpoints, credits, products, hosted pages, custom UI, and webhook-backed fulfillment
- **Solana:** Fixed `solana_signing.py` to cap the exact-payment compute limit at `40000` for the live PayAI-backed flow
- **Docs:** Refreshed runbooks and payment references so agents can understand the full integration path instead of isolated scripts

### v1.4.0
- **ERC-8004:** `register_agent.py` now uses wallet-first challenge/verify plus prepare/finalize registration by default
- **ERC-8004:** Removed the legacy x402-paid registration fallback; wallet-first is now the only registration path
- **ERC-8004:** Added `list_my_endpoints.py`, `list_agents.py`, and `update_agent.py` for full lifecycle discovery and management
- **ERC-8004:** Registration now supports `image`, `version`, `tags`, `endpointIds`, and `customEndpoints`
- **Docs:** Synced skill routing, references, README, and install surfaces to the wallet-first agent flow

### v1.3.3
- **Metadata:** Added `PRIVATE_KEY`/`SOLANA_SECRET_KEY` back to `requires.env` (scripts use them; omitting triggered under-declaration warning)
- **Metadata:** Removed `WORKER_REGISTRATION_API_KEY` from `requires.env` (no script uses it)

### v1.3.2
- **Stack:** Ported `verify_webhook_payment.js` → `verify_webhook_payment.py` — all 20 scripts are now pure Python
- **Stack:** Removed `node`/`npm`/`x402sgl` dependency; receipt JWT verified with PyJWT + JWKS
- **Security:** Removed `WORKER_REGISTRATION_API_KEY` fallback in `submit_feedback.py` (least-privilege)
- **Metadata:** Removed `PRIVATE_KEY`/`SOLANA_SECRET_KEY` from `requires.env` (only needed for specific payment modes)
- **Worker:** Synced embedded `SKILL_MD` with source, added env-only security note

### v1.3.1
- **Security:** Removed implicit `.env` loading from skill scripts; credentials are read only from explicit process env
- **Security:** Removed AWAL `npx` fallback; AWAL now requires local `awal` binary or `AWAL_BIN`
- **Metadata:** Aligned required env declarations with sensitive vars actually used (`PRIVATE_KEY`, `SOLANA_SECRET_KEY`, worker registration/feedback keys)
- **Deps:** Removed `python-dotenv` from requirements

### v1.3.0
- **Feature:** Added `register_agent.py` for worker-based ERC-8004/Solana-8004 registration
- **Feature:** Added `submit_feedback.py` for worker-based on-chain reputation feedback
- **Feature:** Added `verify_webhook_payment.js` for webhook payment genuineness verification via `x402sgl`
- **DX:** Refactored `SKILL.md` with an intent router + reference-first structure to keep one skill comprehensive but easier to navigate
- **DX:** Added dedicated references for webhook verification and ERC-8004/Solana-8004 registry/reputation workflows
- **Security:** AWAL wrapper hardening (`awal_cli.py` now uses validated `awal_bridge.py` path)
- **Security:** AWAL execution hardened (no implicit remote package execution in default flow)
- **Metadata:** Tightened required env declarations to reduce false-positive security flags

### v1.2.1
- **Updated:** Webhook support expanded to 4 event types (payment.succeeded, credits.depleted, credits.low, credits.recharged)
- **Updated:** SKILL.md with event type table and example payloads

### v1.2.0
- **Feature:** Endpoint-level webhooks — receive `payment.succeeded` events at your own HTTPS URL
- **New Script:** `manage_webhook.py` — set, update, or remove webhooks via API
- **Updated:** `create_endpoint.py` — new `--webhook-url` flag for webhook at creation
- **Updated:** SKILL.md — webhook section with event schema and signature verification

### v1.1.2
- **Security:** Added input validation to awal_bridge.py to prevent shell injection
- **Security:** Added filename sanitization to consume_product.py to prevent path traversal
- **Fix:** Ensure 0x prefix on EVM signatures for compatibility


### v1.1.1
- **Fix:** AWAL CLI command updated from `pay` to `x402 pay`
- **Fix:** AWAL URL handling now passes full URL
- **Fix:** Backend includes EIP-712 domain params for AWAL compatibility

### v1.1.0
- **Feature:** Coinbase Agentic Wallet (AWAL) integration for Base payments
- **Feature:** No private key mode using AWAL
- **Feature:** Auto-detection of authentication mode

### v1.0.1
- **Security:** Added strict `x-api-key` verification for marketplace listing/unlisting
- **Docs:** Updated `README.md` with critical API Key security note
- **Script:** Updated `list_on_marketplace.py` to support `X_API_KEY` env var
