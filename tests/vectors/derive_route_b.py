# SPDX-License-Identifier: CC0-1.0
"""Independent Route B derivation for permanently unsafe CC0 test material.

This module implements BIP39 seed generation, BIP32 child derivation, BIP85,
and the secp256k1 public-point operation with the Python standard library only.
The published mnemonic, seed, extended keys, and every derived key are
permanently unsafe for funds.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import sys
import unicodedata
from dataclasses import dataclass

HARDENED = 1 << 31
CURVE_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
CURVE_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
GENERATOR = (
    0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
    0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
)

UNSAFE_MNEMONIC = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
UNSAFE_PASSPHRASE = "TREZOR"
UNSAFE_SEED_HEX = (
    "c55257c360c07c72029aebc1b53c05ed0362ada38ead3e3e9efa3708e5349553"
    "1f09a6987599d18264c1e1c92f2cf141630c7a3c4ab7c81b2f001698e7463b04"
)
O2A_INDEX = 998_536_622

BIP32_VECTOR_SEED = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
BIP32_VECTOR_M_0H = (
    "edb2e14f9ee77d26dd93b4ecede8d16ed408ce149b6cd80b0715a2d911a0afea"
    "47fdacbd0f1097043b78c63c20c34ef4ed9a111d980047ad16282c7ae6236141"
)
BIP85_VECTOR_MASTER = (
    "3f15e5d852dc2e9ba5e9fe189a8dd2e1547badef5b563bbe6579fc6807d80ed9"
    "1b67969d1ec69bdfeeae43213da8460ba34b92d0788c8f7bfcfa44906e8a589c"
)
BIP85_VECTOR_XPRV = (
    "ead0b33988a616cf6a497f1c169d9e92562604e38305ccd3fc96f2252c177682"
    "52405cd0dd21c5be78314a7c1a3c65ffd8d896536cc7dee3157db5824f0c92e2"
)


@dataclass(frozen=True)
class TestXprv:
    secret: int
    chain_code: bytes

    @classmethod
    def parse(cls, value: str) -> "TestXprv":
        raw = bytes.fromhex(value)
        if len(raw) != 64:
            raise ValueError("xprv must be 64 bytes encoded as k || c")
        secret = int.from_bytes(raw[:32], "big")
        if not 0 < secret < CURVE_N:
            raise ValueError("invalid xprv private key")
        return cls(secret, raw[32:])

    def encode(self) -> str:
        return (self.secret.to_bytes(32, "big") + self.chain_code).hex()


def hmac_sha512(key: bytes, data: bytes) -> bytes:
    return hmac.new(key, data, hashlib.sha512).digest()


def _point_add(
    left: tuple[int, int] | None, right: tuple[int, int] | None
) -> tuple[int, int] | None:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % CURVE_P == 0:
        return None
    if left == right:
        slope = (3 * x1 * x1) * pow(2 * y1, -1, CURVE_P) % CURVE_P
    else:
        slope = (y2 - y1) * pow(x2 - x1, -1, CURVE_P) % CURVE_P
    x3 = (slope * slope - x1 - x2) % CURVE_P
    y3 = (slope * (x1 - x3) - y1) % CURVE_P
    return x3, y3


def public_point(secret: int) -> tuple[int, int]:
    if not 0 < secret < CURVE_N:
        raise ValueError("invalid secp256k1 private key")
    result = None
    addend = GENERATOR
    scalar = secret
    while scalar:
        if scalar & 1:
            result = _point_add(result, addend)
        addend = _point_add(addend, addend)
        scalar >>= 1
    if result is None:
        raise ValueError("point at infinity")
    return result


def compressed_pub(secret: int) -> bytes:
    x, y = public_point(secret)
    return bytes([2 | (y & 1)]) + x.to_bytes(32, "big")


def xonly_pub(secret: int) -> str:
    return public_point(secret)[0].to_bytes(32, "big").hex()


def bip39_seed(mnemonic: str, passphrase: str) -> bytes:
    password = unicodedata.normalize("NFKD", mnemonic).encode("utf-8")
    salt = unicodedata.normalize("NFKD", "mnemonic" + passphrase).encode("utf-8")
    return hashlib.pbkdf2_hmac("sha512", password, salt, 2048, 64)


def bip32_master(seed: bytes) -> TestXprv:
    digest = hmac_sha512(b"Bitcoin seed", seed)
    secret = int.from_bytes(digest[:32], "big")
    if not 0 < secret < CURVE_N:
        raise ValueError("invalid BIP32 master private key")
    return TestXprv(secret, digest[32:])


def bip32_child(parent: TestXprv, index: int) -> TestXprv:
    if not 0 <= index <= 0xFFFFFFFF:
        raise ValueError("BIP32 child index outside u32")
    if index >= HARDENED:
        key_data = b"\x00" + parent.secret.to_bytes(32, "big")
    else:
        key_data = compressed_pub(parent.secret)
    digest = hmac_sha512(parent.chain_code, key_data + index.to_bytes(4, "big"))
    left = int.from_bytes(digest[:32], "big")
    if left >= CURVE_N:
        raise ValueError("BIP32 child tweak is greater than or equal to curve order")
    secret = (left + parent.secret) % CURVE_N
    if secret == 0:
        raise ValueError("BIP32 child private key is zero")
    return TestXprv(secret, digest[32:])


def hardened(index: int) -> int:
    if not 0 <= index < HARDENED:
        raise ValueError("hardened input index must fit in 31 bits")
    return index | HARDENED


def derive_path(root: TestXprv, path: list[int]) -> TestXprv:
    key = root
    for index in path:
        key = bip32_child(key, index)
    return key


def bip85_xprv(master: TestXprv, index: int) -> TestXprv:
    application = derive_path(
        master, [hardened(83_696_968), hardened(32), hardened(index)]
    )
    digest = hmac_sha512(
        b"bip-entropy-from-k", application.secret.to_bytes(32, "big")
    )
    secret = int.from_bytes(digest[32:], "big")
    if not 0 < secret < CURVE_N:
        raise ValueError("invalid BIP85 BIP32-XPRV private key")
    return TestXprv(secret, digest[:32])


def self_test() -> None:
    child = bip32_child(bip32_master(BIP32_VECTOR_SEED), HARDENED)
    if child.encode() != BIP32_VECTOR_M_0H:
        raise ValueError("BIP32 test vector 1 m/0H mismatch")
    if bip85_xprv(TestXprv.parse(BIP85_VECTOR_MASTER), 0).encode() != BIP85_VECTOR_XPRV:
        raise ValueError("BIP85 BIP32-XPRV test vector mismatch")
    if bip39_seed(UNSAFE_MNEMONIC, UNSAFE_PASSPHRASE).hex() != UNSAFE_SEED_HEX:
        raise ValueError("published BIP39 seed mismatch")


def derive_route_b(network: str, entity: int) -> dict[str, object]:
    self_test()
    if network not in {"mainnet", "regtest"}:
        raise ValueError("fixture network must be mainnet or regtest")
    if not 0 <= entity < HARDENED:
        raise ValueError("entity index must fit in 31 bits")
    coin = 0 if network == "mainnet" else 1
    seed = bytes.fromhex(UNSAFE_SEED_HEX)
    master = bip32_master(seed)
    o2a = bip85_xprv(master, O2A_INDEX)

    roles: dict[str, dict[str, str]] = {}
    for name, role in (
        ("root_identity", 0),
        ("controller_0", 1),
        ("recovery_0", 2),
        ("nostr_0", 3),
    ):
        role_key = derive_path(
            o2a, [hardened(coin), hardened(entity), hardened(role), hardened(0)]
        )
        roles[name] = {
            "path": f"m/{coin}'/{entity}'/{role}'/0'",
            "xonly": xonly_pub(role_key.secret),
        }

    for index in range(6):
        seal_key = derive_path(
            o2a, [hardened(coin), hardened(entity), hardened(4), hardened(index)]
        )
        roles[f"seal_{index}"] = {
            "path": f"m/{coin}'/{entity}'/4'/{index}'",
            "xonly": xonly_pub(seal_key.secret),
        }

    payment = derive_path(
        master, [hardened(86), hardened(coin), hardened(0), 0, 0]
    )
    return {
        "network": network,
        "coin_type": coin,
        "entity": entity,
        "xprv_o2a": o2a.encode(),
        "bip85_path": f"m/83696968'/32'/{O2A_INDEX}'",
        "keys": roles,
        "payment": {
            "path": f"m/86'/{coin}'/0'/0/0",
            "xonly": xonly_pub(payment.secret),
        },
    }


def main() -> int:
    try:
        if sys.argv[1:] == ["self-test"]:
            self_test()
            print("BIP32 vector 1 m/0H: ok")
            print("BIP85 BIP32-XPRV app 32 index 0: ok")
            print("BIP39 abandon-about/TREZOR seed: ok")
            return 0
        if len(sys.argv) == 4 and sys.argv[1] == "derive-route-b":
            print(json.dumps(derive_route_b(sys.argv[2], int(sys.argv[3])), sort_keys=True))
            return 0
    except (IndexError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1
    print(
        "usage: derive_route_b.py self-test | derive-route-b NETWORK ENTITY",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
