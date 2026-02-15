# x402-Layer ClawHub Skill

⚡ **x402 Singularity Layer** - Agentic payment infrastructure for AI agents.

[![ClawHub](https://img.shields.io/badge/ClawHub-x402--layer-blue)](https://clawhub.ai/ivaavimusic/x402-layer)
[![Version](https://img.shields.io/badge/version-1.1.1-green)](./SKILL.md)
[![License](https://img.shields.io/badge/license-MIT-purple)](./LICENSE)

## What is x402-Layer?

x402 is a **Web3 payment layer** enabling AI agents to:
- 💰 **Pay** for API access using USDC
- 🚀 **Deploy** monetized endpoints  
- 🔍 **Discover** services via marketplace
- 📊 **Manage** endpoints and credits

**Networks:** Base (EVM) • Solana  
**Currency:** USDC  
**Protocol:** HTTP 402 Payment Required

## Installation

### ClawHub (Recommended)
```bash
clawhub install ivaavimusic/x402-layer
```

🦀 **[View on ClawHub →](https://clawhub.ai/ivaavimusic/x402-layer)**

### Self-Hosted
```bash
curl -fsSL https://api.x402layer.cc/skill/x402-layer/install | bash
```

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
| `create_endpoint.py` | Deploy monetized endpoint ($5) |
| `manage_endpoint.py` | View/update endpoints |

> **Security Note:** When you create an endpoint, you will receive an **API Key**. You **must** save this key and configure your origin server to verify the `x-api-key` header in incoming requests. This ensures only paying users (proxied via x402) can access your API.
| `topup_endpoint.py` | Recharge endpoint credits |
| `list_on_marketplace.py` | List/unlist from marketplace |
| `consume_product.py` | Purchase digital products |

## Tags

`web3` `payments` `api` `usdc` `base` `solana` `agentic` `monetization` `marketplace` `credits` `x402` `x402-protocol` `x402-singularity-layer` `SGL`

## Resources

- 🦀 **ClawHub:** [clawhub.ai/ivaavimusic/x402-layer](https://clawhub.ai/ivaavimusic/x402-layer)
- 📖 **Documentation:** [studio.x402layer.cc/docs](https://studio.x402layer.cc/docs/agentic-access/openclaw-skill)
- 🌐 **x402 Studio:** [studio.x402layer.cc](https://studio.x402layer.cc)
- 🐦 **OpenClaw:** [@openclaw](https://x.com/openclaw)

## License

MIT © [EventHorizon Labs](https://ehlabs.xyz)

## Changelog

### v1.0.1
- **Security:** Added strict `x-api-key` verification for marketplace listing/unlisting
- **Docs:** Updated `README.md` with critical API Key security note
- **Script:** Updated `list_on_marketplace.py` to support `X_API_KEY` env var
