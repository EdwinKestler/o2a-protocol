#!/usr/bin/env python3
"""Frozen c7b0871 identity-history rules for ADR-0008 negative controls.

This module intentionally preserves only the legacy root-only and Option B
evaluation seam needed to demonstrate that those rules admit the recorded
attacks. It is not normative and must not be imported by the standard suite.
"""

from __future__ import annotations

import check_protocol_objects as cpo

ENTITY_TAG = "O2A/v0.1/entity-id"
GENESIS_TAG = "O2A/v0.1/entity-genesis"
TRANSITION_TAG = "O2A/v0.1/identity-transition"
NETWORK = 4


def root_only_entity_id(root: bytes) -> bytes:
    return cpo.tagged_hash(ENTITY_TAG, cpo.u16(1) + bytes([NETWORK]) + root)


def option_b_entity_id(root: bytes, seal: bytes) -> bytes:
    return cpo.tagged_hash(
        ENTITY_TAG, cpo.u16(1) + bytes([NETWORK]) + root + seal
    )


def evaluate_name_claim(
    payload: bytes,
    signature: str,
    public_key: str,
    expected_network: int,
    authorization: dict,
) -> tuple[bool, str]:
    """Exact c7b0871 claim-evaluation semantics for negative controls."""
    import check_vectors as cv

    try:
        claim = cv.parse_claim(payload)
    except cv.ClaimDecodeError as error:
        return False, str(error)
    digest = cv.tagged_hash(cv.CLAIM_TAG, payload)
    if not cv.crypto_verify(public_key, digest.hex(), signature):
        return False, "invalid signature"
    if claim["network"] not in cv.KNOWN_NETWORKS or expected_network not in cv.KNOWN_NETWORKS:
        return False, "unknown Bitcoin network"
    if claim["network"] != expected_network:
        return False, "wrong verifier network"
    if claim["version"] != 1 or claim["object_type"] != 4 or claim["capability"] != 4:
        return False, "object/domain/capability mismatch"
    if claim["key_role"] != 1:
        return False, "wrong signing-key role"
    if claim["authorizing_state"] is None:
        return False, "missing authorizing state"
    try:
        public_key_bytes = bytes.fromhex(public_key)
    except ValueError:
        return False, "invalid public key encoding"
    expected_key_id = cv.tagged_hash(
        cv.KEY_TAG, bytes([claim["key_role"]]) + public_key_bytes
    )
    if claim["signing_key_id"] != expected_key_id:
        return False, "signing key ID does not match role and public key"
    if claim["signing_entity"] != claim["subject"]:
        return False, "name claim is not self-issued"
    if (
        authorization.get("entity") != claim["signing_entity"].hex()
        or authorization.get("state")
        != (claim["authorizing_state"].hex() if claim["authorizing_state"] else None)
        or authorization.get("key_id") != claim["signing_key_id"].hex()
        or authorization.get("public_key") != public_key
        or authorization.get("key_role") != claim["key_role"]
        or claim["capability"] not in authorization.get("capabilities", [])
    ):
        return False, "signer is not authorized by the stated fixture state"
    return True, "accepted"


def claim_valid(package: dict, claim: dict) -> bool:
    from check_option_b import authorization

    auth = authorization(package, bytes.fromhex(claim["public_key"]))
    if auth is None:
        return False
    accepted, _ = evaluate_name_claim(
        bytes.fromhex(claim["payload"]),
        claim["signature"],
        claim["public_key"],
        NETWORK,
        auth,
    )
    return accepted


def genesis_valid(package: dict, derivation: str) -> bool:
    payload = bytes.fromhex(package["genesis"])
    signature = package["signature"]
    try:
        decoded = cpo.decode_payload(payload)
    except cpo.DecodeError:
        return False
    header = decoded["header"]
    body = decoded["body"]
    if derivation == "root":
        expected = root_only_entity_id(body["root"])
    elif derivation == "b":
        expected = option_b_entity_id(body["root"], body["state"]["next_seal"])
    else:
        raise ValueError("legacy evaluator supports only root and Option B")
    return (
        cpo.crypto_verify(body["root"], cpo.tagged_hash(GENESIS_TAG, payload), signature)
        and header["version"] == 1
        and header["network"] == NETWORK
        and header["object_type"] == 1
        and header["signer_entity"] == expected
        and header["authorizing_state"] is None
        and header["signing_key_id"] == cpo.key_id(0, body["root"])
        and header["key_role"] == 0
        and header["capability"] == 1
        and body["root"] == cpo.ROOT_PUBLIC
        and cpo.valid_state(body["state"], genesis=True)
    )


def seal_matches(view: dict, seal: bytes, state: dict) -> bool:
    creating = view["transactions"].get(seal[:32].hex())
    if creating is None or creating["confirmations"] < view["required_depth"]:
        return False
    from check_option_b import tx_parse, THRESHOLD, DELAY

    outputs = tx_parse(bytes.fromhex(creating["raw"]))["outputs"]
    vout = int.from_bytes(seal[32:], "little")
    controller = state["seal_policy"]["controller_seal_bindings"]
    recovery = state["seal_policy"]["recovery_seal_bindings"]
    expected = bytes.fromhex(
        cpo.seal_output(controller, recovery, THRESHOLD, DELAY)["script_pubkey"]
    )
    return vout < len(outputs) and outputs[vout][1] == expected


def transition_valid(
    transition: dict, entity: bytes, prior_state: bytes, prior: dict, sequence: int
) -> bool:
    payload = bytes.fromhex(transition["payload"])
    public_key = bytes.fromhex(transition["public_key"])
    try:
        decoded = cpo.decode_payload(payload)
    except cpo.DecodeError:
        return False
    header = decoded["header"]
    body = decoded["body"]
    controller = next(
        (item for item in prior["controllers"] if item["public_key"] == public_key),
        None,
    )
    return (
        controller is not None
        and 2 in controller["capabilities"]
        and cpo.crypto_verify(
            public_key, cpo.tagged_hash(TRANSITION_TAG, payload), transition["signature"]
        )
        and header["version"] == 1
        and header["network"] == NETWORK
        and header["object_type"] == 2
        and header["signer_entity"] == entity
        and header["authorizing_state"] == prior_state
        and header["signing_key_id"] == controller["key_id"]
        and header["key_role"] == 1
        and header["capability"] == 2
        and body["operation"] == 1
        and body["state"]["previous_state"] == prior_state
        and body["state"]["sequence"] == sequence + 1
        and cpo.valid_state(body["state"], genesis=False)
    )


def identity_state(fixture: dict, package: dict, view: dict, derivation: str) -> str:
    if not genesis_valid(package, derivation):
        return "INVALID"
    state = cpo.decode_payload(bytes.fromhex(package["genesis"]))["body"]["state"]
    state_id = bytes.fromhex(package["state_id"])
    entity = bytes.fromhex(package["entity_id"])
    sequence = 0
    while True:
        seal = state["next_seal"]
        if not seal_matches(view, seal, state):
            return "INCOMPLETE"
        spend = view["spends"].get(seal.hex())
        if spend is None:
            return "CURRENT"
        if spend["confirmations"] < view["required_depth"]:
            return "INCOMPLETE"
        transition = fixture["transitions"][spend["transition"]]
        if not transition_valid(transition, entity, state_id, state, sequence):
            return "SEAL_CLOSED_WITHOUT_VALID_TRANSITION"
        state = cpo.decode_payload(bytes.fromhex(transition["payload"]))["body"]["state"]
        state_id = bytes.fromhex(transition["state_id"])
        sequence += 1
