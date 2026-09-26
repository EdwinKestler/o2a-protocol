# SPDX-License-Identifier: CC0-1.0
"""Cross-check permanently unsafe Route B fixtures in Python and Rust."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from derive_route_b import UNSAFE_SEED_HEX, derive_route_b, self_test

HERE = Path(__file__).resolve().parent
CRYPTO_MANIFEST = HERE / "crypto-checker" / "Cargo.toml"
CASES = (("mainnet", 0), ("mainnet", 1), ("regtest", 0), ("regtest", 1))
KEY_NAMES = (
    "root_identity",
    "controller_0",
    "recovery_0",
    "nostr_0",
    "seal_0",
    "seal_1",
    "seal_2",
    "seal_3",
    "seal_4",
    "seal_5",
)


def rust_route_b(network: str, entity: int) -> dict[str, object]:
    result = subprocess.run(
        [
            "cargo",
            "run",
            "--quiet",
            "--locked",
            "--manifest-path",
            str(CRYPTO_MANIFEST),
            "--",
            "derive-route-b",
            UNSAFE_SEED_HEX,
            network,
            str(entity),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ValueError(result.stderr.strip() or "Rust Route B derivation failed")
    fields = dict(line.split("=", 1) for line in result.stdout.strip().splitlines())
    keys = {
        name: {
            "path": fields[f"{name}_path"],
            "xonly": fields[f"{name}_xonly"],
        }
        for name in KEY_NAMES
    }
    return {
        "network": fields["network"],
        "coin_type": int(fields["coin_type"]),
        "entity": int(fields["entity"]),
        "xprv_o2a": fields["xprv_o2a"],
        "bip85_path": fields["bip85_path"],
        "keys": keys,
        "payment": {
            "path": fields["payment_path"],
            "xonly": fields["payment_xonly"],
        },
    }


def cross_check() -> list[dict[str, object]]:
    self_test()
    rows = []
    for network, entity in CASES:
        python_result = derive_route_b(network, entity)
        rust_result = rust_route_b(network, entity)
        if python_result != rust_result:
            raise ValueError(f"Route B mismatch for {network} entity {entity}")
        rows.append(
            {
                "network": network,
                "entity": entity,
                "python": python_result,
                "rust": rust_result,
            }
        )
    return rows


def main() -> int:
    try:
        rows = cross_check()
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 1
    if sys.argv[1:] == ["--json"]:
        print(json.dumps(rows, sort_keys=True))
    elif sys.argv[1:]:
        print("usage: check_derivation_cross.py [--json]", file=sys.stderr)
        return 2
    else:
        print("route b cross-check ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
