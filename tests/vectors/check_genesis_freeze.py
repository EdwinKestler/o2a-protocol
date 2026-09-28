#!/usr/bin/env python3
# SPDX-License-Identifier: CC0-1.0
"""Lock the proposed ADR-0009 mainnet genesis and official-name outputs.

All private material comes from the published BIP39 conformance mnemonic and
is permanently unsafe. This program constructs a vector, never an identity.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import check_protocol_objects as cpo
import check_vectors as cv
import derive_route_b as route_b

HERE = Path(__file__).resolve().parent
FIXTURE_PATH = HERE / "genesis-freeze-v0.1.json"
NETWORK = 0
COIN_TYPE = 0
MAINNET_DEPTH = 6
ENTITY_INDEX = 0
ENTITY_TYPE_ARTIST = 2
RECOVERY_DELAY = 144

O2A_TAGS = (
    "O2A/v0.1/wallet-root",
    "O2A/v0.1/key-id",
    "O2A/v0.1/recovery-policy",
    "O2A/v0.1/entity-id",
    "O2A/v0.1/state-id",
    "O2A/v0.1/entity-genesis",
    "O2A/v0.1/claim",
)
TAPROOT_TAGS = ("TapLeaf", "TapBranch", "TapTweak")
BIP340_TAGS = ("BIP0340/aux", "BIP0340/nonce", "BIP0340/challenge")


def _role_key(o2a: route_b.TestXprv, role: int, index: int) -> route_b.TestXprv:
    return route_b.derive_path(
        o2a,
        [
            route_b.hardened(COIN_TYPE),
            route_b.hardened(ENTITY_INDEX),
            route_b.hardened(role),
            route_b.hardened(index),
        ],
    )


def _schnorr_sign(secret: int, message: bytes) -> bytes:
    """BIP340 signing with zero auxiliary randomness for unsafe fixtures."""
    if len(message) != 32 or not 0 < secret < route_b.CURVE_N:
        raise ValueError("invalid BIP340 fixture input")
    public_x, public_y = route_b.public_point(secret)
    normalized = secret if public_y % 2 == 0 else route_b.CURVE_N - secret
    auxiliary = bytes(32)
    masked = bytes(
        left ^ right
        for left, right in zip(
            normalized.to_bytes(32, "big"),
            cpo.tagged_hash("BIP0340/aux", auxiliary),
        )
    )
    nonce = int.from_bytes(
        cpo.tagged_hash(
            "BIP0340/nonce", masked + public_x.to_bytes(32, "big") + message
        ),
        "big",
    ) % route_b.CURVE_N
    if nonce == 0:
        raise ValueError("zero BIP340 fixture nonce")
    nonce_x, nonce_y = route_b.public_point(nonce)
    normalized_nonce = nonce if nonce_y % 2 == 0 else route_b.CURVE_N - nonce
    challenge = int.from_bytes(
        cpo.tagged_hash(
            "BIP0340/challenge",
            nonce_x.to_bytes(32, "big")
            + public_x.to_bytes(32, "big")
            + message,
        ),
        "big",
    ) % route_b.CURVE_N
    return nonce_x.to_bytes(32, "big") + (
        normalized_nonce + challenge * normalized
    ).__mod__(route_b.CURVE_N).to_bytes(32, "big")


def _state(
    next_seal: bytes,
    controller_public: bytes,
    recovery_public: bytes,
    controller_seal: bytes,
    recovery_seal: bytes,
) -> tuple[bytes, list[tuple[bytes, bytes]], list[tuple[bytes, bytes]]]:
    controller_id = cpo.key_id(1, controller_public)
    recovery_id = cpo.key_id(2, recovery_public)
    controller_bindings = [(controller_id, controller_seal)]
    recovery_bindings = [(recovery_id, recovery_seal)]
    recovery = cpo.recovery_policy(
        [recovery_id], delay_blocks=RECOVERY_DELAY, sequence=0
    )
    encoded = b"".join(
        (
            cpo.u64(0),
            cpo.option(None),
            cpo.option(None),
            next_seal,
            cpo.list_items([cpo.controller(controller_public, [2, 4])]),
            recovery,
            cpo.seal_policy(controller_bindings, recovery_bindings),
            cpo.option(None),
            b"\x01",
            cpo.option(None),
            cpo.option(None),
        )
    )
    return encoded, controller_bindings, recovery_bindings


def _entry(raw: bytes, *, encoding: str = "hex") -> dict[str, object]:
    return {
        "encoding": encoding,
        "length": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "value": raw.decode("utf-8") if encoding == "utf8" else raw.hex(),
    }


def build() -> dict[str, object]:
    route_b.self_test()
    master = route_b.bip32_master(bytes.fromhex(route_b.UNSAFE_SEED_HEX))
    o2a = route_b.bip85_xprv(master, route_b.O2A_INDEX)
    root = _role_key(o2a, 0, 0)
    controller = _role_key(o2a, 1, 0)
    recovery = _role_key(o2a, 2, 0)
    controller_seal_key = _role_key(o2a, 4, 0)
    recovery_seal_key = _role_key(o2a, 4, 1)

    root_public = bytes.fromhex(route_b.xonly_pub(root.secret))
    controller_public = bytes.fromhex(route_b.xonly_pub(controller.secret))
    recovery_public = bytes.fromhex(route_b.xonly_pub(recovery.secret))
    controller_seal = bytes.fromhex(route_b.xonly_pub(controller_seal_key.secret))
    recovery_seal = bytes.fromhex(route_b.xonly_pub(recovery_seal_key.secret))
    next_seal = bytes.fromhex("a9" * 32) + cpo.u32(0)
    state, controller_bindings, recovery_bindings = _state(
        next_seal,
        controller_public,
        recovery_public,
        controller_seal,
        recovery_seal,
    )
    seal = cpo.seal_output(
        controller_bindings, recovery_bindings, threshold=1, delay=RECOVERY_DELAY
    )
    genesis = b"".join(
        (
            cv.common_header(
                1,
                1,
                bytes(32),
                None,
                cpo.key_id(0, root_public),
                network=NETWORK,
                key_role=0,
            ),
            cpo.u16(ENTITY_TYPE_ARTIST),
            root_public,
            state,
        )
    )
    entity = cpo.entity_id(genesis)
    state_identifier = cpo.state_id(entity, state)
    genesis_digest = cpo.tagged_hash("O2A/v0.1/entity-genesis", genesis)
    genesis_signature = _schnorr_sign(root.secret, genesis_digest)

    claim_spec = {
        "object_type": 4,
        "capability": 4,
        "predicate_utf8": "official_name",
        "object_utf8": "Unsafe Mainnet Vector Artist",
        "nonce_hex": hashlib.sha256(b"O2A ADR-0009 unsafe vector nonce").hexdigest(),
    }
    claim = cv.build_claim(
        claim_spec,
        entity,
        state_identifier,
        cpo.key_id(1, controller_public),
        network=NETWORK,
        key_role=1,
    )
    claim_digest = cpo.tagged_hash("O2A/v0.1/claim", claim)
    claim_signature = _schnorr_sign(controller.secret, claim_digest)

    outputs: dict[str, dict[str, object]] = {
        "parameters.protocol_version": _entry(cpo.u16(1)),
        "parameters.network_byte_mainnet": _entry(bytes([NETWORK])),
        "parameters.coin_type_mainnet": _entry(cpo.u32(COIN_TYPE)),
        "parameters.mainnet_confirmation_depth": _entry(cpo.u32(MAINNET_DEPTH)),
        "route_b.bip85_path": _entry(
            f"m/83696968'/32'/{route_b.O2A_INDEX}'".encode(), encoding="utf8"
        ),
        "route_b.bip39_seed": _entry(bytes.fromhex(route_b.UNSAFE_SEED_HEX)),
        "route_b.o2a_index": _entry(route_b.O2A_INDEX.to_bytes(4, "big")),
        "route_b.wallet_root_tagged_hash": _entry(
            cpo.tagged_hash("O2A/v0.1/wallet-root", b"")
        ),
        "route_b.xprv_o2a": _entry(bytes.fromhex(o2a.encode())),
    }
    for role, index, name, key, public in (
        (0, 0, "root_0", root, root_public),
        (1, 0, "controller_0", controller, controller_public),
        (2, 0, "recovery_0", recovery, recovery_public),
        (4, 0, "seal_0", controller_seal_key, controller_seal),
        (4, 1, "seal_1", recovery_seal_key, recovery_seal),
    ):
        path = f"m/{COIN_TYPE}'/{ENTITY_INDEX}'/{role}'/{index}'"
        outputs[f"route_b.{name}.path"] = _entry(path.encode(), encoding="utf8")
        outputs[f"route_b.{name}.xprv"] = _entry(bytes.fromhex(key.encode()))
        outputs[f"route_b.{name}.xonly"] = _entry(public)
    for tag in O2A_TAGS + TAPROOT_TAGS + BIP340_TAGS:
        outputs[f"tag.{tag}"] = _entry(tag.encode(), encoding="utf8")
    for name, raw in (
        ("key_id.root", cpo.key_id(0, root_public)),
        ("key_id.controller", cpo.key_id(1, controller_public)),
        ("key_id.recovery", cpo.key_id(2, recovery_public)),
        ("key_id.controller_seal", cpo.key_id(4, controller_seal)),
        ("key_id.recovery_seal", cpo.key_id(4, recovery_seal)),
        ("next_seal", next_seal),
        ("resulting_state", state),
        ("entity_genesis.payload", genesis),
        ("entity_genesis.digest", genesis_digest),
        ("entity_genesis.signature", genesis_signature),
        ("entity_id", entity),
        ("state_id", state_identifier),
        ("official_name.payload", claim),
        ("official_name.digest", claim_digest),
        ("official_name.signature", claim_signature),
        ("seal.internal_key", cpo.SEAL_INTERNAL_KEY),
        ("seal.policy", bytes.fromhex(seal["policy_hex"])),
        ("seal.merkle_root", bytes.fromhex(seal["merkle_root"])),
        ("seal.output_key", bytes.fromhex(seal["output_key"])),
        ("seal.script_pubkey", bytes.fromhex(seal["script_pubkey"])),
    ):
        outputs[name] = _entry(raw)
    for index, value in enumerate(seal["scripts_hex"]):
        outputs[f"seal.script.{index}"] = _entry(bytes.fromhex(value))
    for index, value in enumerate(seal["leaf_hashes"]):
        outputs[f"seal.leaf_hash.{index}"] = _entry(bytes.fromhex(value))

    outcomes = {
        "confirmations_5": cpo.identity_history_outcome(
            bitcoin_view_source="unsafe-mainnet-vector",
            best_block_hash=bytes.fromhex("11" * 32),
            observed_height=840_000,
            seal_observation="unspent",
            spend_proof=False,
            spend_confirmations=0,
            required_depth=MAINNET_DEPTH,
            valid_transition=False,
            seal_creating_confirmations=[5],
        )["state"],
        "confirmations_6": cpo.identity_history_outcome(
            bitcoin_view_source="unsafe-mainnet-vector",
            best_block_hash=bytes.fromhex("11" * 32),
            observed_height=840_000,
            seal_observation="unspent",
            spend_proof=False,
            spend_confirmations=0,
            required_depth=MAINNET_DEPTH,
            valid_transition=False,
            seal_creating_confirmations=[6],
        )["state"],
    }
    for name, value in outcomes.items():
        outputs[f"pending_confirmation.{name}"] = _entry(
            value.encode(), encoding="utf8"
        )

    return {
        "adr": "ADR-0009 Proposed",
        "description": "Unsafe mainnet Route B vector; never a real identity",
        "spdx": "CC0-1.0",
        "unsafe_for_funds": True,
        "outputs": dict(sorted(outputs.items())),
    }


def check(fixture: dict[str, object]) -> None:
    expected = build()
    if fixture != expected:
        raise ValueError("frozen output changed; ADR-0009 manifest mismatch")
    outputs = fixture["outputs"]
    assert isinstance(outputs, dict)
    for name, value in outputs.items():
        assert isinstance(value, dict)
        raw = (
            str(value["value"]).encode()
            if value["encoding"] == "utf8"
            else bytes.fromhex(str(value["value"]))
        )
        if len(raw) != value["length"] or hashlib.sha256(raw).hexdigest() != value["sha256"]:
            raise ValueError(f"invalid recorded SHA-256 for {name}")

    genesis = bytes.fromhex(str(outputs["entity_genesis.payload"]["value"]))
    entity = bytes.fromhex(str(outputs["entity_id"]["value"]))
    state_identifier = bytes.fromhex(str(outputs["state_id"]["value"]))
    state = bytes.fromhex(str(outputs["resulting_state"]["value"]))
    root = bytes.fromhex(str(outputs["route_b.root_0.xonly"]["value"]))
    controller = bytes.fromhex(str(outputs["route_b.controller_0.xonly"]["value"]))
    if (
        cpo.rust_entity_id(genesis) != entity
        or cpo.rust_state_id(entity, state) != state_identifier
    ):
        raise ValueError("Python/Rust identifier disagreement")
    if not cpo.crypto_verify(
        root,
        bytes.fromhex(str(outputs["entity_genesis.digest"]["value"])),
        str(outputs["entity_genesis.signature"]["value"]),
    ):
        raise ValueError("genesis signature failed Rust verification")
    if not cpo.crypto_verify(
        controller,
        bytes.fromhex(str(outputs["official_name.digest"]["value"])),
        str(outputs["official_name.signature"]["value"]),
    ):
        raise ValueError("official_name signature failed Rust verification")
    if (
        cpo.evaluate_signed_payload(
            genesis,
            str(outputs["entity_genesis.signature"]["value"]),
            root,
            "O2A/v0.1/entity-genesis",
            {"expected_network": NETWORK, "authorization": None},
        )
        != "valid"
    ):
        raise ValueError("mainnet genesis failed normative evaluation")
    claim = bytes.fromhex(str(outputs["official_name.payload"]["value"]))
    claim_accepted, reason = cv.evaluate_name_claim(
        claim,
        str(outputs["official_name.signature"]["value"]),
        controller.hex(),
        NETWORK,
        {
            "entity": entity.hex(),
            "state": state_identifier.hex(),
            "key_id": cpo.key_id(1, controller).hex(),
            "public_key": controller.hex(),
            "key_role": 1,
            "capabilities": [2, 4],
            "genesis_payload": genesis.hex(),
        },
    )
    if not claim_accepted:
        raise ValueError(f"official_name failed normative evaluation: {reason}")
    seal_case = {
        "policy_version": 1,
        "controller_seal_bindings": [
            (
                cpo.key_id(1, controller),
                bytes.fromhex(str(outputs["route_b.seal_0.xonly"]["value"])),
            )
        ],
        "recovery_seal_bindings": [
            (
                cpo.key_id(
                    2,
                    bytes.fromhex(str(outputs["route_b.recovery_0.xonly"]["value"])),
                ),
                bytes.fromhex(str(outputs["route_b.seal_1.xonly"]["value"])),
            )
        ],
        "threshold": 1,
        "delay_blocks": RECOVERY_DELAY,
    }
    rust_seal = cpo.rust_seal_output(seal_case)
    for field in ("policy_hex", "merkle_root", "output_key", "script_pubkey"):
        recorded_name = "seal.policy" if field == "policy_hex" else f"seal.{field}"
        if rust_seal[field] != outputs[recorded_name]["value"]:
            raise ValueError(f"Python/Rust seal {field} disagreement")
    if outputs["pending_confirmation.confirmations_5"]["value"] != "PENDING_CONFIRMATION":
        raise ValueError("five-confirmation outcome is not pending")
    if outputs["pending_confirmation.confirmations_6"]["value"] != "CURRENT":
        raise ValueError("six-confirmation outcome is not current")


def main() -> int:
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(build(), indent=2, sort_keys=True))
        return 0
    if sys.argv[1:]:
        print("usage: check_genesis_freeze.py [--emit]", file=sys.stderr)
        return 2
    try:
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        check(fixture)
    except (AssertionError, KeyError, TypeError, ValueError, OSError) as error:
        print(f"genesis freeze failed: {error}", file=sys.stderr)
        return 1
    print(f"genesis freeze: {len(fixture['outputs'])}/{len(fixture['outputs'])} outputs unchanged")
    print("Python/Rust EntityID, state_id, and BIP340 signature cross-checks: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
