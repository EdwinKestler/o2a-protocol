# SPDX-License-Identifier: CC0-1.0
"""Cross-check O2A seal vectors with Bitcoin Core descriptor RPCs."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SEAL_FIXTURE = HERE / "seal-script-v0.1.json"
CORE_FIXTURE = HERE / "seal-script-core-v0.1.json"
CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def core_rpc(*args: str) -> object:
    command = [
        "docker",
        "compose",
        "--file",
        str(ROOT / "dev/compose.yaml"),
        "exec",
        "--no-TTY",
        "bitcoin",
        "bitcoin-cli",
        "-regtest",
        "-datadir=/var/lib/bitcoin",
        *args,
    ]
    environment = dict(os.environ)
    environment.setdefault("DOCKER_CONTEXT", "default")
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(result.stderr.strip() or result.stdout.strip() or "Bitcoin Core RPC failed")
    return json.loads(result.stdout)


def pairwise_tree(expressions: list[str]) -> str:
    current = list(expressions)
    if not current:
        raise ValueError("empty descriptor tree")
    while len(current) > 1:
        next_round = []
        for index in range(0, len(current), 2):
            if index + 1 == len(current):
                next_round.append(current[index])
            else:
                next_round.append(f"{{{current[index]},{current[index + 1]}}}")
        current = next_round
    return current[0]


def descriptor(case: dict, internal_key: str) -> str:
    controller_keys = sorted(
        binding["seal_xonly"] for binding in case["controller_seal_bindings"]
    )
    recovery_keys = sorted(
        binding["seal_xonly"] for binding in case["recovery_seal_bindings"]
    )
    leaves = [f"pk({key})" for key in controller_keys]
    recovery = (
        f"and_v(v:multi_a({case['threshold']},{','.join(recovery_keys)}),"
        f"older({case['delay_blocks']}))"
    )
    leaves.append(recovery)
    return f"tr({internal_key},{pairwise_tree(leaves)})"


def polymod(values: list[int]) -> int:
    generators = (0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3)
    checksum = 1
    for value in values:
        top = checksum >> 25
        checksum = ((checksum & 0x1FFFFFF) << 5) ^ value
        for index, generator in enumerate(generators):
            if (top >> index) & 1:
                checksum ^= generator
    return checksum


def hrp_expand(hrp: str) -> list[int]:
    return [ord(character) >> 5 for character in hrp] + [0] + [
        ord(character) & 31 for character in hrp
    ]


def convert_bits(values: list[int], from_bits: int, to_bits: int) -> bytes:
    accumulator = 0
    bits = 0
    result = bytearray()
    maximum = (1 << to_bits) - 1
    for value in values:
        accumulator = (accumulator << from_bits) | value
        bits += from_bits
        while bits >= to_bits:
            bits -= to_bits
            result.append((accumulator >> bits) & maximum)
    if bits and ((accumulator << (to_bits - bits)) & maximum):
        raise ValueError("nonzero bech32 padding")
    return bytes(result)


def address_script_pubkey(address: str) -> str:
    if address.lower() != address or "1" not in address:
        raise ValueError("noncanonical bech32 address")
    hrp, encoded = address.rsplit("1", 1)
    values = [CHARSET.index(character) for character in encoded]
    if hrp != "bcrt" or polymod(hrp_expand(hrp) + values) != 0x2BC830A3:
        raise ValueError("invalid regtest bech32m address")
    witness_version = values[0]
    program = convert_bits(values[1:-6], 5, 8)
    if witness_version != 1 or len(program) != 32:
        raise ValueError("address is not P2TR")
    return (bytes([0x50 + witness_version, len(program)]) + program).hex()


def collect() -> dict:
    fixture = json.loads(SEAL_FIXTURE.read_text(encoding="utf-8"))
    network = core_rpc("getnetworkinfo")
    output = {
        "spdx": "CC0-1.0",
        "profile": "O2A seal output Bitcoin Core oracle Draft v0.1",
        "bitcoin_core_subversion": network["subversion"],
        "cases": {},
    }
    for name, case in fixture["cases"].items():
        raw_descriptor = descriptor(case, fixture["internal_key"])
        info = core_rpc("getdescriptorinfo", raw_descriptor)
        addresses = core_rpc("deriveaddresses", info["descriptor"])
        if len(addresses) != 1:
            fail(f"{name}: Core returned an unexpected address count")
        script_pubkey = address_script_pubkey(addresses[0])
        expected = case["expected"]["script_pubkey"]
        if script_pubkey != expected:
            fail(f"{name}: Bitcoin Core scriptPubKey mismatch")
        output["cases"][name] = {
            "input_descriptor": raw_descriptor,
            "getdescriptorinfo": info,
            "deriveaddresses": addresses,
            "script_pubkey": script_pubkey,
        }
    return output


def main() -> None:
    actual = collect()
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(actual, indent=2, sort_keys=True))
        return
    if sys.argv[1:]:
        fail("usage: check_seal_core.py [--emit]")
    expected = json.loads(CORE_FIXTURE.read_text(encoding="utf-8"))
    if actual != expected:
        fail("Bitcoin Core seal oracle fixture mismatch")
    print("bitcoin core seal oracle ok")


if __name__ == "__main__":
    main()
