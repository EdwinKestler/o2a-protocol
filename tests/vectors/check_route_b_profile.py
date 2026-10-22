#!/usr/bin/env python3
# SPDX-License-Identifier: CC0-1.0
"""Proposed Route B completion vectors (ADR-0016).

Extends the frozen roles 0, 1, 2, and 4 to role 3 (Nostr publication), to
non-zero operational indexes, to a second entity index, and to the BIP86
payment path. Python derives every key; the independent Rust
`crypto-checker` re-derives each one by hardened CKD from `xprv_o2a`.
Unsafe public test seed only.

    python3 tests/vectors/check_route_b_profile.py          # check
    python3 tests/vectors/check_route_b_profile.py --emit   # regenerate
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from derive_route_b import (  # noqa: E402
    HARDENED,
    O2A_INDEX,
    UNSAFE_SEED_HEX,
    bip32_master,
    bip85_xprv,
    derive_path,
    hardened,
    xonly_pub,
)
from check_protocol_objects import crypto  # noqa: E402

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "route-b-profile-v0.1.json"
ROLES = {0: "root", 1: "controller", 2: "recovery", 3: "nostr", 4: "seal"}
COIN = {"mainnet": 0, "regtest": 1}


def valid_path(components: list[int]) -> bool:
    """O2A identity path below xprv_o2a: coin'/entity'/role'/index', all hardened."""
    if len(components) != 4 or any(c < HARDENED or c > 0xFFFFFFFF for c in components):
        return False
    coin, _entity, role, index = (c - HARDENED for c in components)
    if coin not in (0, 1) or role not in ROLES:
        return False
    return role != 0 or index == 0


def build() -> dict:
    master = bip32_master(bytes.fromhex(UNSAFE_SEED_HEX))
    o2a = bip85_xprv(master, O2A_INDEX)
    rows = []
    for network, coin in COIN.items():
        for entity in (0, 1):
            for role in ROLES:
                for index in ((0,) if role == 0 else (0, 1)):
                    path = [hardened(coin), hardened(entity), hardened(role), hardened(index)]
                    rows.append({
                        "network": network, "entity": entity, "role": role, "index": index,
                        "path": f"m/{coin}'/{entity}'/{role}'/{index}'",
                        "xonly": xonly_pub(derive_path(o2a, path).secret),
                    })
        for index in (0, 1):
            payment = derive_path(master, [hardened(86), hardened(coin), hardened(0), 0, index])
            rows.append({"network": network, "payment": True, "index": index,
                         "path": f"m/86'/{coin}'/0'/0/{index}", "xonly": xonly_pub(payment.secret)})
    rejects = {
        "unhardened_index": [hardened(0), hardened(0), hardened(1), 0],
        "unknown_role_5": [hardened(0), hardened(0), hardened(5), hardened(0)],
        "root_nonzero_index": [hardened(0), hardened(0), hardened(0), hardened(1)],
        "unknown_coin_2": [hardened(2), hardened(0), hardened(1), hardened(0)],
        "extra_component": [hardened(0), hardened(0), hardened(1), hardened(0), hardened(0)],
    }
    return {
        "spdx": "CC0-1.0",
        "status": "proposed (ADR-0016); roles 0, 1, 2, 4 at index 0 already frozen by ADR-0009",
        "unsafe_for_funds": True,
        "xprv_o2a": o2a.encode(),
        "keys": rows,
        "rejected_paths": {k: [hex(c) for c in v] for k, v in rejects.items()},
        "rejected_results": {k: valid_path(v) for k, v in rejects.items()},
    }


def rust_derive(xprv: str, components: list[int]) -> str:
    for component in components:
        result = crypto(["bip32-ckd-hard", xprv, str(component)])
        if result.returncode != 0:
            raise SystemExit(f"rust ckd failed: {result.stderr.strip()}")
        xprv = result.stdout.strip()
    result = crypto(["xonly-pub", xprv])
    if result.returncode != 0:
        raise SystemExit(f"rust xonly failed: {result.stderr.strip()}")
    return result.stdout.strip()


def main() -> None:
    data = build()
    if "--emit" in sys.argv:
        FIXTURE.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
        print(f"wrote {FIXTURE.name}")
        return
    if json.loads(FIXTURE.read_text()) != json.loads(json.dumps(data, sort_keys=True)):
        print("route b profile: regenerated vectors differ from fixture", file=sys.stderr)
        sys.exit(1)
    if any(data["rejected_results"].values()):
        print("route b profile: an invalid path was accepted", file=sys.stderr)
        sys.exit(1)
    frozen = json.loads((HERE / "derivation-v0.1.json").read_text())["positives"]
    frozen_keys = {(p["network"], p["entity"], k["path"]): k["xonly"]
                   for p in frozen for k in p["keys"].values()}
    overlap = 0
    for row in data["keys"]:
        key = (row["network"], row.get("entity"), row["path"])
        if key in frozen_keys:
            overlap += 1
            if frozen_keys[key] != row["xonly"]:
                print(f"route b profile: frozen output changed at {key}", file=sys.stderr)
                sys.exit(1)
    checked = 0
    if "--no-rust" not in sys.argv:
        for row in data["keys"]:
            if row.get("payment"):
                continue
            components = [int(p.rstrip("'")) | HARDENED for p in row["path"].split("/")[1:]]
            if rust_derive(data["xprv_o2a"], components) != row["xonly"]:
                print(f"route b profile: rust disagrees at {row['path']}", file=sys.stderr)
                sys.exit(1)
            checked += 1
    print(f"route b profile: {len(data['keys'])} keys, {overlap} match existing derivation vectors, "
          f"{checked} rust re-derivations, {len(data['rejected_results'])} invalid paths rejected")


if __name__ == "__main__":
    main()
