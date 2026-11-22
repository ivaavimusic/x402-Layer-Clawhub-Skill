#!/usr/bin/env python3
"""End-to-end wire tests for the paying scripts, with the network mocked.

Every key is generated at runtime; nothing here moves money or talks to a server.
Checks, for Base AND Solana:
- a v2 PAYMENT-REQUIRED header is answered with PAYMENT-SIGNATURE (accepted echoed unchanged,
  inner payload signed for exactly `amount` to exactly `payTo`);
- no header, or X402_WIRE=v1, sends X-Payment v1 exactly as before;
- a 503 / 202 / timeout after paying is pending and nothing is signed or sent again.

Run: python3 -m unittest discover -s tests -v   (from the skill folder)
"""

import base64
import json
import os
import struct
import sys
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.abspath(os.environ.get("X402_WIRE_SCRIPTS") or os.path.join(HERE, "..", "scripts"))
sys.path.insert(0, SCRIPTS)

try:
    import requests  # noqa: F401
    from eth_account import Account
    from eth_account.messages import encode_typed_data
    from solders.keypair import Keypair
    from solders.transaction import VersionedTransaction
    HAVE_DEPS = True
except Exception:  # pragma: no cover - skill deps missing
    HAVE_DEPS = False

import x402_wire as w  # noqa: E402

SOLANA_CAIP2 = "solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp"
USDC_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
USDC_SOL = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"


class _Headers(dict):
    def get(self, key, default=None):
        for k, v in self.items():
            if k.lower() == str(key).lower():
                return v
        return default


class _Resp:
    def __init__(self, status_code, body=None, headers=None, text=None):
        self.status_code = status_code
        self._body = body
        self.headers = _Headers(headers or {})
        self.headers.setdefault("content-type", "application/json")
        self.text = text if text is not None else json.dumps(body)
        self.content = self.text.encode()

    def json(self):
        if self._body is None:
            raise ValueError("no json")
        return self._body

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(self.status_code)


def _offers(base_pay_to, sol_pay_to, fee_payer):
    v1 = [
        {"scheme": "exact", "network": "base", "maxAmountRequired": "2010000", "payTo": base_pay_to,
         "asset": USDC_BASE, "maxTimeoutSeconds": 3600, "extra": {"name": "USD Coin", "version": "2"}},
        {"scheme": "exact", "network": "solana", "maxAmountRequired": "1500000", "payTo": sol_pay_to,
         "asset": USDC_SOL, "maxTimeoutSeconds": 3600, "extra": {"feePayer": fee_payer}},
    ]
    v2 = {
        "x402Version": 2,
        "error": "Payment required",
        "resource": {"url": "https://api.x402layer.cc/e/demo", "description": "Démo ✓", "mimeType": "application/json"},
        "accepts": [
            {"scheme": "exact", "network": "eip155:8453", "asset": USDC_BASE, "amount": "2010000", "payTo": base_pay_to,
             "maxTimeoutSeconds": 3600, "extra": {"name": "USD Coin", "version": "2"}},
            {"scheme": "exact", "network": SOLANA_CAIP2, "asset": USDC_SOL, "amount": "1500000", "payTo": sol_pay_to,
             "maxTimeoutSeconds": 3600, "extra": {"feePayer": fee_payer}},
        ],
        "extensions": {"bazaar": {"info": {"input": {"type": "http", "method": "GET"}}}},
    }
    return {"x402Version": 1, "accepts": v1}, v2


@unittest.skipUnless(HAVE_DEPS, "skill dependencies (requests, eth_account, solders) not installed")
class PayScriptsWire(unittest.TestCase):
    def setUp(self):
        self.evm = Account.create()
        self.sol = Keypair()
        self.base_pay_to = Account.create().address
        self.sol_pay_to = str(Keypair().pubkey())
        self.fee_payer = str(Keypair().pubkey())
        self.body, self.required = _offers(self.base_pay_to, self.sol_pay_to, self.fee_payer)
        self.env = mock.patch.dict(os.environ, {
            "PRIVATE_KEY": self.evm.key.hex(),
            "WALLET_ADDRESS": self.evm.address,
            "SOLANA_SECRET_KEY": json.dumps(list(bytes(self.sol))),
            "X402_AUTH_MODE": "private-key",
        }, clear=False)
        self.env.start()
        for k in ("X402_WIRE", "X402_PREFER_NETWORK", "SOLANA_WALLET_ADDRESS", "WALLET_ADDRESS_SECONDARY", "OWS_WALLET"):
            os.environ.pop(k, None)
        self.sent = []

    def tearDown(self):
        self.env.stop()

    # ── mocked network ─────────────────────────────────────────────
    def _server(self, emit_v2=True, paid_status=200):
        def handler(*args, **kwargs):
            url = args[0] if args else kwargs.get("url")
            if "mainnet-beta" in str(url) or "helius" in str(url) or "rpc" in str(url):
                return _Resp(200, {"result": {"value": {"blockhash": str(Keypair().pubkey())}}})
            headers = kwargs.get("headers") or {}
            paid = {k: v for k, v in headers.items() if k.lower() in ("payment-signature", "x-payment")}
            if not paid:
                hdrs = {"PAYMENT-REQUIRED": w.encode_header(self.required)} if emit_v2 else {}
                return _Resp(402, self.body, hdrs)
            self.sent.append(paid)
            if paid_status == "timeout":
                raise requests.Timeout("read timed out")
            settle = w.encode_header({"success": True, "transaction": "0xabc", "network": "eip155:8453"})
            return _Resp(paid_status, {"ok": True, "download_url": None}, {"PAYMENT-RESPONSE": settle})
        return handler

    def _run(self, fn, emit_v2=True, paid_status=200):
        h = self._server(emit_v2, paid_status)
        with mock.patch("requests.get", side_effect=h), mock.patch("requests.put", side_effect=h), \
                mock.patch("requests.post", side_effect=h):
            return fn()

    # ── assertions ─────────────────────────────────────────────────
    def _assert_v2_base(self):
        self.assertEqual(len(self.sent), 1)
        (name, value), = self.sent[0].items()
        self.assertEqual(name, "PAYMENT-SIGNATURE")
        env = w.decode_header(value)
        self.assertEqual(env["x402Version"], 2)
        self.assertEqual(env["accepted"], self.required["accepts"][0])
        self.assertEqual(env["resource"], self.required["resource"])
        self.assertEqual(env["extensions"], self.required["extensions"])
        auth = env["payload"]["authorization"]
        self.assertEqual(auth["value"], "2010000")
        self.assertEqual(auth["to"], self.base_pay_to)
        self.assertEqual(auth["from"], self.evm.address)
        typed = {
            "types": {
                "EIP712Domain": [{"name": "name", "type": "string"}, {"name": "version", "type": "string"},
                                 {"name": "chainId", "type": "uint256"}, {"name": "verifyingContract", "type": "address"}],
                "TransferWithAuthorization": [{"name": "from", "type": "address"}, {"name": "to", "type": "address"},
                                              {"name": "value", "type": "uint256"}, {"name": "validAfter", "type": "uint256"},
                                              {"name": "validBefore", "type": "uint256"}, {"name": "nonce", "type": "bytes32"}],
            },
            "primaryType": "TransferWithAuthorization",
            "domain": {"name": "USD Coin", "version": "2", "chainId": 8453, "verifyingContract": USDC_BASE},
            "message": {"from": auth["from"], "to": auth["to"], "value": int(auth["value"]),
                        "validAfter": int(auth["validAfter"]), "validBefore": int(auth["validBefore"]),
                        "nonce": bytes.fromhex(auth["nonce"][2:])},
        }
        signer = Account.recover_message(encode_typed_data(full_message=typed), signature=env["payload"]["signature"])
        self.assertEqual(signer, self.evm.address)

    def _assert_v1_base(self):
        self.assertEqual(len(self.sent), 1)
        (name, value), = self.sent[0].items()
        self.assertEqual(name, "X-Payment")
        decoded = json.loads(base64.b64decode(value))
        self.assertEqual([decoded["x402Version"], decoded["scheme"], decoded["network"]], [1, "exact", "base"])
        self.assertEqual(decoded["payload"]["authorization"]["value"], "2010000")

    def _assert_v2_solana(self):
        self.assertEqual(len(self.sent), 1)
        (name, value), = self.sent[0].items()
        self.assertEqual(name, "PAYMENT-SIGNATURE")
        env = w.decode_header(value)
        self.assertEqual(env["accepted"], self.required["accepts"][1])
        self.assertEqual(env["accepted"]["network"], SOLANA_CAIP2)
        tx = VersionedTransaction.from_bytes(base64.b64decode(env["payload"]["transaction"]))
        msg = tx.message
        self.assertEqual(str(msg.account_keys[0]), self.fee_payer)
        transfer = msg.instructions[-1]
        self.assertEqual(bytes(transfer.data)[0], 12)
        self.assertEqual(struct.unpack("<Q", bytes(transfer.data)[1:9])[0], 1500000)

    # ── pay_base / pay_solana ──────────────────────────────────────
    def test_pay_base_v2(self):
        import pay_base
        out = self._run(lambda: pay_base.pay_for_access("https://api.x402layer.cc/e/demo", agentkit_mode="off"))
        self.assertEqual(out, {"ok": True, "download_url": None})
        self._assert_v2_base()

    def test_pay_base_v1_without_header(self):
        import pay_base
        self._run(lambda: pay_base.pay_for_access("https://api.x402layer.cc/e/demo", agentkit_mode="off"), emit_v2=False)
        self._assert_v1_base()

    def test_pay_base_env_forces_v1(self):
        import pay_base
        os.environ["X402_WIRE"] = "v1"
        self._run(lambda: pay_base.pay_for_access("https://api.x402layer.cc/e/demo", agentkit_mode="off"))
        self._assert_v1_base()

    def test_pay_base_pending_never_resigns(self):
        import pay_base
        for status in (503, 202, "timeout"):
            with self.subTest(status=status):
                self.sent = []
                out = self._run(lambda: pay_base.pay_for_access("https://api.x402layer.cc/e/demo", agentkit_mode="off"),
                                paid_status=status)
                self.assertTrue(out.get("pending"))
                self.assertEqual(len(self.sent), 1)

    def test_pay_solana_v2(self):
        import pay_solana
        self._run(lambda: pay_solana.pay_for_access("https://api.x402layer.cc/e/demo"))
        self._assert_v2_solana()

    def test_pay_solana_v1_without_header(self):
        import pay_solana
        self._run(lambda: pay_solana.pay_for_access("https://api.x402layer.cc/e/demo"), emit_v2=False)
        (name, value), = self.sent[0].items()
        self.assertEqual(name, "X-Payment")
        decoded = json.loads(base64.b64decode(value))
        self.assertEqual([decoded["x402Version"], decoded["network"]], [1, "solana"])

    def test_pay_solana_pending(self):
        import pay_solana
        out = self._run(lambda: pay_solana.pay_for_access("https://api.x402layer.cc/e/demo"), paid_status=502)
        self.assertTrue(out.get("pending"))
        self.assertEqual(len(self.sent), 1)

    # ── scripts using network_selection (Base first, then Solana preference) ──
    def _scripts(self):
        calls = []
        try:
            import topup_endpoint
            os.environ["X_API_KEY"] = "test-endpoint-key"
            calls.append(("topup", lambda: topup_endpoint.topup_endpoint("demo", 5)))
        except ImportError:
            pass
        try:
            import recharge_credits
            calls.append(("recharge", lambda: recharge_credits.recharge_credits("demo")))
        except ImportError:
            pass
        try:
            import consume_product
            calls.append(("product", lambda: consume_product.consume_product("demo-product")))
        except ImportError:
            pass
        return calls

    def test_network_selected_scripts_v2_base_and_solana(self):
        for prefer, check in (("base", self._assert_v2_base), ("solana", self._assert_v2_solana)):
            for label, call in self._scripts():
                with self.subTest(script=label, network=prefer):
                    os.environ["X402_PREFER_NETWORK"] = prefer
                    self.sent = []
                    self._run(call)
                    check()

    def test_network_selected_scripts_v1(self):
        for label, call in self._scripts():
            with self.subTest(script=label):
                self.sent = []
                self._run(call, emit_v2=False)
                self._assert_v1_base()


if __name__ == "__main__":
    unittest.main()
