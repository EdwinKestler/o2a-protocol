#!/usr/bin/env python3
# SPDX-License-Identifier: CC0-1.0
"""Empirical comparison of Nostr key strategies for ADR-0016 (one-shot).

A  O2A role 3' below xprv_o2a (current profile), exported as NIP-19 nsec /
   NIP-49 ncryptsec or used behind a NIP-46 remote signer.
B  NIP-06 m/44'/1237'/<entity>'/0/0 from the wallet master.
C  NIP-06 with a reserved high account per entity (2^30 + entity).

Checks run on published test material only:
1. our BIP39/BIP32 code reproduces both NIP-06 test vectors (private key,
   public key, nsec, npub);
2. overlap between O2A role-3' keys and NIP-06 accounts 0..999;
3. conflation of entity 0 with the default NIP-06 account 0 under B;
4. escalation: NIP-06 account xpub + leaked leaf key -> account private key
   (non-hardened `/0/0`), which does not apply to an all-hardened role-3' path.

    python3 scripts/evaluate_nostr_derivation.py <output-dir>
"""

from __future__ import annotations

import hashlib
import hmac
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests" / "vectors"))

from derive_route_b import (  # noqa: E402
    CURVE_N,
    CURVE_P,
    O2A_INDEX,
    UNSAFE_SEED_HEX,
    _point_add,
    bip32_child,
    bip32_master,
    bip39_seed,
    bip85_xprv,
    compressed_pub,
    derive_path,
    hardened,
    public_point,
)

CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
NIP06_VECTORS = [
    {"mnemonic": "leader monkey parrot ring guide accident before fence cannon height naive bean",
     "private": "7f7ff03d123792d6ac594bfa67bf6d0c0ab55b6b1fdb6249303fe861f1ccba9a",
     "nsec": "nsec10allq0gjx7fddtzef0ax00mdps9t2kmtrldkyjfs8l5xruwvh2dq0lhhkp",
     "public": "17162c921dc4d2518f9a101db33695df1afb56ab82f5ff3e5da6eec3ca5cd917",
     "npub": "npub1zutzeysacnf9rru6zqwmxd54mud0k44tst6l70ja5mhv8jjumytsd2x7nu"},
    {"mnemonic": "what bleak badge arrange retreat wolf trade produce cricket blur garlic valid "
                 "proud rude strong choose busy staff weather area salt hollow arm fade",
     "private": "c15d739894c81a2fcfd3a2df85a0d2c0dbc47a280d092799f144d73d7ae78add",
     "nsec": "nsec1c9wh8xy5eqdzln7n5t0ctgxjcrdug73gp5yj0x03gntn67h83twssdfhel",
     "public": "d41b22899549e1f3d335a31002cfd382174006e166d3e658e3a5eecdb6463573",
     "npub": "npub16sdj9zv4f8sl85e45vgq9n7nsgt5qphpvmf7vk8r5hhvmdjxx4es8rq74h"},
]


def _polymod(values: list[int]) -> int:
    gen = [0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]
    chk = 1
    for v in values:
        top = chk >> 25
        chk = (chk & 0x1FFFFFF) << 5 ^ v
        for i in range(5):
            chk ^= gen[i] if (top >> i) & 1 else 0
    return chk


def bech32(hrp: str, data: bytes) -> str:
    acc, bits, five = 0, 0, []
    for byte in data:
        acc = (acc << 8) | byte
        bits += 8
        while bits >= 5:
            bits -= 5
            five.append((acc >> bits) & 31)
    if bits:
        five.append((acc << (5 - bits)) & 31)
    expanded = [ord(c) >> 5 for c in hrp] + [0] + [ord(c) & 31 for c in hrp]
    poly = _polymod(expanded + five + [0] * 6) ^ 1
    checksum = [(poly >> 5 * (5 - i)) & 31 for i in range(6)]
    return hrp + "1" + "".join(CHARSET[d] for d in five + checksum)


def xonly(secret: int) -> bytes:
    return public_point(secret)[0].to_bytes(32, "big")


def nip06(master, account: int):
    return derive_path(master, [hardened(44), hardened(1237), hardened(account), 0, 0])


def lift_compressed(pub: bytes) -> tuple[int, int]:
    x = int.from_bytes(pub[1:], "big")
    y = pow((pow(x, 3, CURVE_P) + 7) % CURVE_P, (CURVE_P + 1) // 4, CURVE_P)
    if y % 2 != pub[0] % 2:
        y = CURVE_P - y
    return x, y


def ser_point(point: tuple[int, int]) -> bytes:
    return bytes([2 | (point[1] & 1)]) + point[0].to_bytes(32, "big")


def escalate(account_pub: bytes, account_chain: bytes, leaf_secret: int) -> int:
    """Recover the NIP-06 account private key from its xpub and the /0/0 leaf."""
    i0 = hmac.new(account_chain, account_pub + (0).to_bytes(4, "big"), hashlib.sha512).digest()
    tweak0 = int.from_bytes(i0[:32], "big")
    child_pub = ser_point(_point_add(lift_compressed(account_pub), public_point(tweak0)))
    i00 = hmac.new(i0[32:], child_pub + (0).to_bytes(4, "big"), hashlib.sha512).digest()
    tweak00 = int.from_bytes(i00[:32], "big")
    return (leaf_secret - tweak00 - tweak0) % CURVE_N


def main() -> None:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "artifacts/nostr-derivation-evaluation")
    out.mkdir(parents=True, exist_ok=True)
    report: dict = {}

    vectors = []
    for vec in NIP06_VECTORS:
        key = nip06(bip32_master(bip39_seed(vec["mnemonic"], "")), 0)
        priv = key.secret.to_bytes(32, "big")
        vectors.append({
            "private": priv.hex() == vec["private"], "public": xonly(key.secret).hex() == vec["public"],
            "nsec": bech32("nsec", priv) == vec["nsec"], "npub": bech32("npub", xonly(key.secret)) == vec["npub"]})
    report["nip06_vectors_reproduced"] = vectors

    master = bip32_master(bytes.fromhex(UNSAFE_SEED_HEX))
    o2a = bip85_xprv(master, O2A_INDEX)
    role3 = {(c, e, i): xonly(derive_path(o2a, [hardened(c), hardened(e), hardened(3), hardened(i)]).secret)
             for c in (0, 1) for e in range(10) for i in range(3)}
    nip06_keys = {a: xonly(nip06(master, a).secret) for a in range(1000)}
    report["overlap_role3_vs_nip06_accounts_0_999"] = len(set(role3.values()) & set(nip06_keys.values()))
    report["role3_keys_checked"] = len(role3)
    report["option_b_entity0_equals_default_nip06_account0"] = True  # B maps entity e to account e
    report["option_b_entity0_npub"] = bech32("npub", nip06_keys[0])
    report["option_a_entity0_mainnet_role3_npub"] = bech32("npub", role3[(0, 0, 0)])

    account = derive_path(master, [hardened(44), hardened(1237), hardened(5)])
    leaf = nip06(master, 5)
    recovered = escalate(compressed_pub(account.secret), account.chain_code, leaf.secret)
    report["nip06_xpub_plus_leaf_recovers_account_key"] = recovered == account.secret
    sibling = bip32_child(bip32_child(account, 0), 1)
    report["escalation_exposes_sibling_m_44_1237_5_0_1"] = (
        bip32_child(bip32_child(type(account)(recovered, account.chain_code), 0), 1).secret == sibling.secret)
    report["role3_path_all_hardened"] = True

    report["options"] = {
        "A_role3_plus_export": {
            "conflicts_with_personal_nip06_account0": False,
            "generic_client_mnemonic_restore": "no; import nsec/ncryptsec or use a NIP-46 signer",
            "rotation": "yes, index' per entity", "under_bip85_child_not_master": True,
            "leaf_plus_xpub_escalation": False, "o2a_restore": "ADR-0015 manifest/scan"},
        "B_nip06_account_eq_entity": {
            "conflicts_with_personal_nip06_account0": True,
            "generic_client_mnemonic_restore": "entity 0 only (clients default to account 0)",
            "rotation": "no; /0/0 fixed per account", "under_bip85_child_not_master": False,
            "leaf_plus_xpub_escalation": True, "o2a_restore": "needs a second allocation scheme"},
        "C_nip06_reserved_high_account": {
            "conflicts_with_personal_nip06_account0": False,
            "generic_client_mnemonic_restore": "no (custom account)",
            "rotation": "no", "under_bip85_child_not_master": False,
            "leaf_plus_xpub_escalation": True, "o2a_restore": "needs a second allocation scheme"},
    }
    report["ecosystem"] = ("NIP-06 is marked draft/unrecommended ('prefer a single nsec'); "
                           "NIP-49 ncryptsec and NIP-46 remote signing are the portable paths.")
    report["decision"] = "A"
    (out / "results.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    ok = (all(all(v.values()) for v in vectors) and report["overlap_role3_vs_nip06_accounts_0_999"] == 0
          and report["nip06_xpub_plus_leaf_recovers_account_key"])
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
