#!/usr/bin/env python3
"""Tests for scripts/x402_wire.py (x402 v1 + v2 wire helpers).

Golden vectors in x402_golden.json were produced by the official @x402/core 2.32.0 encoders
(monorepo packages/x402-kit/gen-golden.mjs), so these tests prove our base64 JSON is
byte-identical to what official v2 clients and servers produce.

Run: python3 -m unittest discover -s tests -v   (from the skill folder)
"""

import base64
import copy
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.environ.get("X402_WIRE_SCRIPTS") or os.path.join(HERE, "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPTS))

import x402_wire as w  # noqa: E402

with open(os.path.join(HERE, "x402_golden.json"), encoding="utf-8") as fh:
    GOLDEN = json.load(fh)

SOLANA_CAIP2 = "solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp"


class _Headers(dict):
    """Case-insensitive header lookup, like requests' CaseInsensitiveDict."""

    def get(self, key, default=None):
        for k, v in self.items():
            if k.lower() == str(key).lower():
                return v
        return default


class _Response:
    def __init__(self, status_code=402, body=None, headers=None):
        self.status_code = status_code
        self._body = body
        self.headers = _Headers(headers or {})

    def json(self):
        if self._body is None:
            raise ValueError("no json")
        return self._body


V1_BODY = {
    "x402Version": 1,
    "error": "Payment required",
    "accepts": [
        {
            "scheme": "exact",
            "network": "base",
            "maxAmountRequired": "2010000",
            "payTo": "0x1111111111111111111111111111111111111111",
            "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
            "extra": {"name": "USD Coin", "version": "2"},
        },
        {
            "scheme": "exact",
            "network": "solana",
            "maxAmountRequired": "1",
            "payTo": "9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin",
            "asset": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            "extra": {"feePayer": "2wKupLR9q6wXYppw8Gr2NvWxKBUqm4PPJKkQfoxHDBg4"},
        },
    ],
    "singularity": {"quote_id": "q-1"},
}


def _pr_header(mutate=None):
    value = copy.deepcopy(GOLDEN["paymentRequired"]["value"])
    if mutate:
        mutate(value)
    return w.encode_header(value)


class GoldenEncoding(unittest.TestCase):
    def test_every_golden_vector_encodes_byte_identical(self):
        for key in ("paymentRequired", "evmPayload", "svmPayload", "settleOk", "settlePending"):
            with self.subTest(key=key):
                self.assertEqual(w.encode_header(GOLDEN[key]["value"]), GOLDEN[key]["header"])

    def test_every_golden_vector_decodes(self):
        for key in ("paymentRequired", "evmPayload", "svmPayload", "settleOk", "settlePending"):
            with self.subTest(key=key):
                self.assertEqual(w.decode_header(GOLDEN[key]["header"]), GOLDEN[key]["value"])

    def test_v2_evm_payment_header_matches_official(self):
        def strip_ext(v):
            v.pop("extensions", None)

        resp = _Response(body=V1_BODY, headers={"payment-required": _pr_header(strip_ext)})
        challenge = w.read_challenge(resp)
        self.assertEqual(challenge[w.WIRE_KEY], "v2")
        base = next(o for o in challenge["accepts"] if o["network"] == "base")
        inner = GOLDEN["evmPayload"]["value"]["payload"]
        name, value = w.v2_payment_header(challenge, base, inner)
        self.assertEqual(name, "PAYMENT-SIGNATURE")
        self.assertEqual(value, GOLDEN["evmPayload"]["header"])

    def test_v2_svm_payment_header_matches_official(self):
        def strip(v):
            v.pop("extensions", None)
            v.pop("resource", None)

        resp = _Response(body=V1_BODY, headers={"PAYMENT-REQUIRED": _pr_header(strip)})
        challenge = w.read_challenge(resp)
        sol = next(o for o in challenge["accepts"] if o["network"] == "solana")
        name, value = w.v2_payment_header(challenge, sol, GOLDEN["svmPayload"]["value"]["payload"])
        self.assertEqual(name, "PAYMENT-SIGNATURE")
        self.assertEqual(value, GOLDEN["svmPayload"]["header"])

    def test_v2_payment_echoes_extensions_and_accepted_unchanged(self):
        resp = _Response(body=V1_BODY, headers={"PAYMENT-REQUIRED": GOLDEN["paymentRequired"]["header"]})
        challenge = w.read_challenge(resp)
        base = next(o for o in challenge["accepts"] if o["network"] == "base")
        _, value = w.v2_payment_header(challenge, base, {"signature": "0x00", "authorization": {}})
        sent = w.decode_header(value)
        pr = GOLDEN["paymentRequired"]["value"]
        self.assertEqual(list(sent.keys()), ["x402Version", "resource", "accepted", "payload", "extensions"])
        self.assertEqual(sent["accepted"], pr["accepts"][0])
        self.assertEqual(sent["extensions"], pr["extensions"])
        self.assertEqual(sent["resource"], pr["resource"])
        self.assertNotIn(w.ACCEPTED_KEY, json.dumps(sent))


class ReadChallenge(unittest.TestCase):
    def test_v2_header_wins_and_maps_fields(self):
        resp = _Response(body=V1_BODY, headers={"PAYMENT-REQUIRED": GOLDEN["paymentRequired"]["header"]})
        challenge = w.read_challenge(resp)
        self.assertEqual(challenge[w.WIRE_KEY], "v2")
        nets = [o["network"] for o in challenge["accepts"]]
        self.assertEqual(nets, ["base", "solana"])
        sol = challenge["accepts"][1]
        self.assertEqual(sol["maxAmountRequired"], "1")
        self.assertEqual(sol["payTo"], "9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin")
        self.assertEqual(sol["extra"]["feePayer"], "2wKupLR9q6wXYppw8Gr2NvWxKBUqm4PPJKkQfoxHDBg4")
        # Body-only fields survive.
        self.assertEqual(challenge["singularity"], {"quote_id": "q-1"})

    def test_no_header_is_v1_exactly(self):
        challenge = w.read_challenge(_Response(body=V1_BODY))
        self.assertEqual(challenge[w.WIRE_KEY], "v1")
        self.assertEqual(challenge["accepts"], V1_BODY["accepts"])
        self.assertFalse(w.uses_v2(challenge, challenge["accepts"][0]))

    def test_env_forces_v1(self):
        os.environ["X402_WIRE"] = "v1"
        try:
            resp = _Response(body=V1_BODY, headers={"PAYMENT-REQUIRED": GOLDEN["paymentRequired"]["header"]})
            challenge = w.read_challenge(resp)
            self.assertEqual(challenge[w.WIRE_KEY], "v1")
            self.assertEqual(challenge["accepts"], V1_BODY["accepts"])
        finally:
            del os.environ["X402_WIRE"]

    def test_garbage_header_falls_back_to_v1(self):
        for bad in ("not base64!!", base64.b64encode(b"[1,2]").decode(), w.encode_header({"x402Version": 1, "accepts": [{}]}),
                    w.encode_header({"x402Version": 2, "accepts": []}), "", "A" * (w.MAX_HEADER_CHARS + 4)):
            with self.subTest(bad=bad[:20]):
                challenge = w.read_challenge(_Response(body=V1_BODY, headers={"PAYMENT-REQUIRED": bad}))
                self.assertEqual(challenge[w.WIRE_KEY], "v1")

    def test_lowercased_solana_caip2_is_not_paid(self):
        def lower_sol(v):
            v["accepts"][1]["network"] = SOLANA_CAIP2.lower()

        challenge = w.read_challenge(_Response(body=V1_BODY, headers={"PAYMENT-REQUIRED": _pr_header(lower_sol)}))
        self.assertEqual([o["network"] for o in challenge["accepts"]], ["base"])

    def test_unknown_network_and_bad_amounts_are_dropped(self):
        def bad(v):
            v["accepts"] = [
                dict(v["accepts"][0], network="eip155:1"),
                dict(v["accepts"][0], amount="1.5"),
                dict(v["accepts"][0], amount=2010000),
                dict(v["accepts"][0], amount="-1"),
                dict(v["accepts"][0], amount="007"),
                dict(v["accepts"][0], scheme="variable"),
                dict(v["accepts"][0], network="base"),
                dict(v["accepts"][0], payTo=""),
            ]

        # No usable v2 offer: fall back to the v1 body rather than guess.
        challenge = w.read_challenge(_Response(body=V1_BODY, headers={"PAYMENT-REQUIRED": _pr_header(bad)}))
        self.assertEqual(challenge[w.WIRE_KEY], "v1")

    def test_no_body_still_reads_v2(self):
        challenge = w.read_challenge(_Response(body=None, headers={"PAYMENT-REQUIRED": GOLDEN["paymentRequired"]["header"]}))
        self.assertEqual(challenge[w.WIRE_KEY], "v2")
        self.assertEqual(challenge["extensions"], GOLDEN["paymentRequired"]["value"]["extensions"])

    def test_v2_payment_header_refuses_v1_challenge(self):
        challenge = w.read_challenge(_Response(body=V1_BODY))
        with self.assertRaises(ValueError):
            w.v2_payment_header(challenge, challenge["accepts"][0], {})


class Helpers(unittest.TestCase):
    def test_network_names_exact_case(self):
        self.assertEqual(w.network_name(SOLANA_CAIP2), "solana")
        self.assertIsNone(w.network_name(SOLANA_CAIP2.lower()))
        self.assertEqual(w.network_name("BASE"), "base")
        self.assertEqual(w.network_name("eip155:8453"), "base")
        self.assertIsNone(w.network_name("eip155:1"))
        self.assertIsNone(w.network_name(""))
        self.assertEqual(w.caip2_for("solana"), SOLANA_CAIP2)

    def test_same_address(self):
        self.assertTrue(w.same_address("evm", "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"))
        self.assertFalse(w.same_address("svm", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "epjfwdd5aufqssqem2qn1xzybapc8g4wegGkzwytdt1v"))
        self.assertTrue(w.same_address("svm", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"))

    def test_parse_atomic(self):
        self.assertEqual(w.parse_atomic("2010000"), 2010000)
        self.assertEqual(w.parse_atomic("0"), 0)
        for bad in ("01", "1.0", "1e6", "-1", "", " 1", 1, None, str(1 << 256)):
            with self.subTest(bad=bad):
                self.assertIsNone(w.parse_atomic(bad))

    def test_payment_response_v2_then_v1(self):
        ok = GOLDEN["settleOk"]
        self.assertEqual(w.read_payment_response(_Response(200, headers={"payment-response": ok["header"]})), ok["value"])
        self.assertEqual(w.read_payment_response(_Response(200, headers={"X-PAYMENT-RESPONSE": ok["header"]})), ok["value"])
        self.assertIsNone(w.read_payment_response(_Response(200)))

    def test_ambiguous_statuses_are_pending(self):
        for code in (202, 500, 502, 503, 504):
            self.assertTrue(w.is_ambiguous_status(code))
        for code in (200, 201, 400, 402, 409):
            self.assertFalse(w.is_ambiguous_status(code))
        pending = w.pending_result(503, "boom")
        self.assertTrue(pending["pending"])
        self.assertIn("Do NOT sign or pay again", pending["next_step"])


if __name__ == "__main__":
    unittest.main()
