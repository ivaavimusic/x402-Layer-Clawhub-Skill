# x402-Layer ClawHub Skill

⚡ **x402 Singularity Layer** - Agentic payment infrastructure for AI agents.

[![ClawHub](https://img.shields.io/badge/ClawHub-x402--layer-blue)](https://clawhub.ai/skills/x402-layer)
[![Version](https://img.shields.io/badge/version-1.0.0-green)](./SKILL.md)

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
clawhub install x402-layer
```

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
| `topup_endpoint.py` | Recharge endpoint credits |
| `list_on_marketplace.py` | List/unlist from marketplace |
| `consume_product.py` | Purchase digital products |

## License

MIT © [EventHorizon Labs](https://ehlabs.xyz)
