#!/usr/bin/env python3
# SPDX-License-Identifier: CC0-1.0
"""Proposed transition/recovery/custody-transfer freeze vectors (ADR-0014).

One regtest lineage exercises every operation: genesis, 1 controller
rotation, 2 recovery-policy change, 4 custody transfer, 3 delayed 2-of-2
recovery, and 5 revocation. The evaluator below checks the semantic rules of
ADR-0014 on decoded bytes; the adversarial cases (ADR-0014 / Phase 0 item 6)
each change one rule and are re-signed so that only that rule can reject.

Every key here is a small published scalar and permanently unsafe for funds.

    python3 tests/vectors/check_transition_freeze.py           # check
    python3 tests/vectors/check_transition_freeze.py --emit    # regenerate
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_protocol_objects import (  # noqa: E402
    CURVE_N,
    DecodeError,
    Reader,
    crypto,
    decode_payload,
    entity_id,
    key_id,
    list_items,
    option,
    public_point,
    state_id,
    tagged_hash,
    text_field,
    bytes_field,
    u16,
    u32,
    u64,
)

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "transition-freeze-v0.1.json"
NETWORK = 4  # regtest
TRANSITION_TAG = "O2A/v0.1/identity-transition"
RECOVERY_TAG = "O2A/v0.1/recovery"
RECOVERY_ANCHOR_TAG = "O2A/v0.1/recovery-anchor"
CLAIM_TAG = "O2A/v0.1/claim"
GENESIS_TAG = "O2A/v0.1/entity-genesis"
POLICY_TAG = "O2A/v0.1/recovery-policy"
CUSTODY_PREDICATE = "o2a/custody-acceptance/v1"
CAPS = [2, 4, 5, 6, 7, 8, 9, 10, 11, 12]
RGB_TYPE = {1: 8101, 2: 8101, 3: 8102, 4: 8101, 5: 8101}

SCALARS = {
    "root_a": 101, "c0": 111, "c1": 112, "c2": 113,
    "r0": 121, "r1": 122, "r2": 123,
    "s_c0": 131, "s_c1": 132, "s_c2": 133, "s_r0": 141, "s_r1": 142, "s_r2": 143,
    "root_b": 201, "cb": 211, "rb": 221, "s_cb": 231, "s_rb": 241,
}


def xonly(name: str) -> bytes:
    return public_point(SCALARS[name])[0].to_bytes(32, "big")


# ---------------------------------------------------------------- BIP340 ----

def _bip_tag(tag: str, data: bytes) -> bytes:
    return tagged_hash(tag, data)


def bip340_sign(secret: int, message: bytes) -> bytes:
    point = public_point(secret)
    d = secret if point[1] % 2 == 0 else CURVE_N - secret
    px = point[0].to_bytes(32, "big")
    t = bytes(a ^ b for a, b in zip(d.to_bytes(32, "big"), _bip_tag("BIP0340/aux", bytes(32))))
    k0 = int.from_bytes(_bip_tag("BIP0340/nonce", t + px + message), "big") % CURVE_N
    if k0 == 0:
        raise ValueError("nonce is zero")
    r_point = public_point(k0)
    k = k0 if r_point[1] % 2 == 0 else CURVE_N - k0
    rx = r_point[0].to_bytes(32, "big")
    e = int.from_bytes(_bip_tag("BIP0340/challenge", rx + px + message), "big") % CURVE_N
    return rx + ((k + e * d) % CURVE_N).to_bytes(32, "big")


def bip340_verify(public_key: bytes, message: bytes, signature: bytes) -> bool:
    """Accept only signatures produced for a known fixture scalar.

    The independent Rust verifier (`crypto-checker verify`) is the general
    BIP340 check; it runs over every signature in check mode.
    """
    for scalar in SCALARS.values():
        if public_point(scalar)[0].to_bytes(32, "big") == public_key:
            return bip340_sign(scalar, message) == signature
    return False


# -------------------------------------------------------------- encoding ----

def outpoint(marker: int, index: int = 1) -> bytes:
    return bytes([marker]) * 32 + u32(index)


def header(object_type: int, capability: int, signer: bytes, state: bytes | None,
           signing_key_id: bytes, role: int, network: int = NETWORK) -> bytes:
    return (u16(1) + bytes([network]) + u16(object_type) + signer + option(state)
            + signing_key_id + bytes([role]) + u16(capability))


def controller_entry(name: str) -> bytes:
    pub = xonly(name)
    return key_id(1, pub) + pub + b"\x01" + list_items([u16(c) for c in CAPS])


def policy_bytes(recovery: list[str], threshold: int, sequence: int, delay: int = 144) -> bytes:
    ids = sorted(key_id(2, xonly(name)) for name in recovery)
    return u16(1) + u64(sequence) + u16(threshold) + list_items(ids) + u32(delay) + b"\x01"


def seal_policy_bytes(controllers: list[tuple[str, str]], recovery: list[tuple[str, str]]) -> bytes:
    def bindings(pairs, role):
        return sorted(key_id(role, xonly(a)) + xonly(s) for a, s in pairs)
    return u16(1) + list_items(bindings(controllers, 1)) + list_items(bindings(recovery, 2))


def state_bytes(s: dict) -> bytes:
    controllers = sorted(controller_entry(name) for name in s["controllers"])
    return b"".join((
        u64(s["sequence"]), option(s["previous_state"]), option(s["previous_seal"]),
        s["next_seal"], list_items(controllers),
        policy_bytes(s["recovery"], s["threshold"], s["policy_sequence"], s.get("delay", 144)),
        seal_policy_bytes(s["controller_seals"], s["recovery_seals"]),
        option(s.get("custodian")), bytes([s.get("status", 1)]),
        option(s.get("custody_acceptance")), option(None),
    ))


def genesis_payload(root: str, entity_type: int, state: dict) -> bytes:
    return (header(1, 1, bytes(32), None, key_id(0, xonly(root)), 0)
            + u16(entity_type) + xonly(root) + state_bytes(state))


def claim_payload(signer: bytes, auth: bytes, key: str, subject: bytes, obj: bytes,
                  predicate: str = CUSTODY_PREDICATE) -> bytes:
    return (header(4, 4, signer, auth, key_id(1, xonly(key)), 1) + subject
            + text_field(predicate) + bytes_field(obj) + option(None)
            + tagged_hash("O2A/v0.1/fixture-nonce", subject + obj) + option(None) + option(None))


def recovery_body(op: int, policy_hash: bytes, not_before: int, state: bytes) -> bytes:
    return bytes([op]) + policy_hash + u32(not_before) + state


def recovery_anchor_digest(entity: bytes, body: bytes) -> bytes:
    return tagged_hash(RECOVERY_ANCHOR_TAG, entity + body)


# --------------------------------------------------------------- lineage ----

BASE_A = {
    "controllers": ["c0"], "recovery": ["r0", "r1", "r2"], "threshold": 2,
    "policy_sequence": 1, "controller_seals": [("c0", "s_c0")],
    "recovery_seals": [("r0", "s_r0"), ("r1", "s_r1"), ("r2", "s_r2")],
}
SEAL_HEIGHTS = {0: 200, 1: 210, 2: 220, 4: 230, 3: 380, 5: 390}


def build(case: str = "valid") -> dict:
    """Return the lineage, with exactly one rule broken for an adversarial case."""
    state_b = {"sequence": 0, "previous_state": None, "previous_seal": None,
               "next_seal": outpoint(0xB0, 0), "controllers": ["cb"], "recovery": ["rb"],
               "threshold": 1, "policy_sequence": 1, "controller_seals": [("cb", "s_cb")],
               "recovery_seals": [("rb", "s_rb")]}
    gen_b = genesis_payload("root_b", 6, state_b)
    entity_b = entity_id(gen_b)
    state_b_id = state_id(entity_b, state_bytes(state_b))

    s0 = dict(BASE_A, sequence=0, previous_state=None, previous_seal=None,
              next_seal=outpoint(0xA0, 0))
    gen_a = genesis_payload("root_a", 2, s0)
    ent = entity_id(gen_a)
    steps = [{"kind": "genesis", "payload": gen_a, "signatures": [
        [xonly("root_a"), bip340_sign(SCALARS["root_a"], tagged_hash(GENESIS_TAG, gen_a))]],
        "anchor_digest": tagged_hash(GENESIS_TAG, gen_a), "rgb_type": None,
        "seal_height": SEAL_HEIGHTS[0], "anchor_height": None}]
    prior, prior_bytes = s0, state_bytes(s0)

    def successor(**changes) -> dict:
        nonlocal prior, prior_bytes
        nxt = dict(prior)
        nxt.update(sequence=prior["sequence"] + 1, previous_state=state_id(ent, prior_bytes),
                   previous_seal=prior["next_seal"], custody_acceptance=None)
        nxt.update(changes)
        return nxt

    def transition(op: int, signer_key: str, nxt: dict, anchor_height: int,
                   network: int = NETWORK, auth: bytes | None = None) -> None:
        nonlocal prior, prior_bytes
        auth = state_id(ent, prior_bytes) if auth is None else auth
        body = state_bytes(nxt)
        payload = header(2, 2, ent, auth, key_id(1, xonly(signer_key)), 1, network) + bytes([op]) + body
        digest = tagged_hash(TRANSITION_TAG, payload)
        sig = bip340_sign(SCALARS[signer_key], digest)
        if case == "signature_invalid" and op == 1:
            sig = sig[:-1] + bytes([sig[-1] ^ 1])
        anchor = digest
        if case == "anchor_digest_mismatch" and op == 1:
            anchor = tagged_hash(TRANSITION_TAG, payload + b"\x00")
        if case == "anchor_missing" and op == 1:
            anchor = None
        steps.append({"kind": "transition", "payload": payload,
                      "signatures": [[xonly(signer_key), sig]], "anchor_digest": anchor,
                      "rgb_type": RGB_TYPE[op] if not (case == "rgb_type_mismatch" and op == 1) else 8102,
                      "seal_height": SEAL_HEIGHTS[op], "anchor_height": anchor_height})
        prior, prior_bytes = nxt, body

    # Operation 1: controller rotation c0 -> c1.
    s1 = successor(next_seal=outpoint(0xA1), controllers=["c1"], controller_seals=[("c1", "s_c1")])
    if case == "sequence_skip":
        s1["sequence"] = 2
    if case == "previous_seal_mismatch":
        s1["previous_seal"] = outpoint(0xEE, 0)
    if case == "rotation_changes_policy":
        s1["threshold"] = 1
    if case == "custodian_changed_outside_op4":
        s1["custodian"] = entity_b
    if case == "stale_seal_binding":
        s1["controller_seals"] = [("c0", "s_c0")]
    if case == "next_seal_reused":
        s1["next_seal"] = s1["previous_seal"]
    transition(3 if case == "op3_in_transition_domain" else 1, "c0", s1, 210,
               network=0 if case == "cross_network" else NETWORK)

    # Operation 2: recovery-policy change to 2-of-2 {r0, r1}, sequence 2.
    stale_auth = None
    if case == "stale_previous_state":
        stale_auth = state_id(ent, state_bytes(s0))
    s2 = successor(next_seal=outpoint(0xA2), recovery=["r0", "r1"], threshold=2,
                   policy_sequence=1 if case == "policy_sequence_not_incremented" else 2,
                   recovery_seals=[("r0", "s_r0"), ("r1", "s_r1")])
    if stale_auth is not None:
        s2["previous_state"] = stale_auth
    transition(2, "c0" if case == "rotated_out_signer" else "c1", s2, 220, auth=stale_auth)

    # Operation 4: custody transfer to entity B with B's acceptance claim.
    s4 = successor(next_seal=outpoint(0xA4), custodian=entity_b)
    claim_next_seal = outpoint(0xEE, 4) if case == "custody_wrong_next_seal" else s4["next_seal"]
    claim_prior = state_id(ent, state_bytes(s0)) if case == "custody_wrong_prior_state" \
        else state_id(ent, prior_bytes)
    claim_custodian = ent if case == "custody_signer_mismatch" else entity_b
    claim = claim_payload(entity_b, state_b_id, "cb", ent,
                          claim_prior + claim_custodian + claim_next_seal,
                          "official_name" if case == "custody_wrong_predicate" else CUSTODY_PREDICATE)
    claim_id = tagged_hash(CLAIM_TAG, claim)
    claim_sig = bip340_sign(SCALARS["cb"], claim_id)
    s4["custody_acceptance"] = None if case == "custody_without_acceptance" else claim_id
    transition(4, "c1", s4, 230)
    steps[-1]["custody_claim"] = {"payload": claim, "signer": xonly("cb"), "signature": claim_sig}

    # Operation 3: delayed 2-of-2 recovery replacing the controller with c2.
    policy_hash = tagged_hash(POLICY_TAG, policy_bytes(
        ["r0", "r1", "r2"] if case == "recovery_stale_policy_hash" else ["r0", "r1"],
        2, 1 if case == "recovery_stale_policy_hash" else 2))
    not_before = SEAL_HEIGHTS[4] + 144
    s3 = successor(next_seal=outpoint(0xA3), controllers=["c2"], controller_seals=[("c2", "s_c2")])
    body3 = state_bytes(s3)
    rbody = recovery_body(3, policy_hash, not_before, body3)
    signers = {"recovery_insufficient_threshold": ["r0"],
               "recovery_duplicate_signer": ["r0", "r0"],
               "recovery_key_not_in_prior_policy": ["r0", "r2"]}.get(case, ["r0", "r1"])
    auth = state_id(ent, prior_bytes)
    rpayloads, rsigs = [], []
    for name in sorted(signers, key=lambda n: key_id(2, xonly(n))):
        p = header(3, 3, ent, auth, key_id(2, xonly(name)), 2) + rbody
        rpayloads.append(p)
        rsigs.append([xonly(name), bip340_sign(SCALARS[name], tagged_hash(RECOVERY_TAG, p))])
    steps.append({"kind": "recovery", "payload": rpayloads[0], "payloads": rpayloads,
                  "signatures": rsigs, "anchor_digest": recovery_anchor_digest(ent, rbody),
                  "rgb_type": 8102, "seal_height": SEAL_HEIGHTS[4],
                  "anchor_height": not_before - 1 if case == "recovery_below_not_before" else 380})
    prior, prior_bytes = s3, body3

    # Operation 5: revocation.
    s5 = successor(next_seal=outpoint(0xA5), status=1 if case == "revocation_status_active" else 2)
    transition(5, "c2", s5, 390)

    if case == "transition_after_revocation":
        s6 = successor(next_seal=outpoint(0xA6), status=2, controllers=["c2"])
        transition(1, "c2", s6, 400)
    return {"entity": ent, "custodian_entity": entity_b, "custodian_genesis": gen_b,
            "custodian_state_id": state_b_id, "steps": steps}


# ------------------------------------------------------------- evaluator ----

class Reject(Exception):
    pass


def require(condition: bool, code: str) -> None:
    if not condition:
        raise Reject(code)


def decode_claim(payload: bytes) -> dict:
    r = Reader(payload)
    h = {"version": r.u16(), "network": r.u8(), "object_type": r.u16(),
         "signer_entity": r.take(32), "authorizing_state": r.option_fixed(32),
         "signing_key_id": r.take(32), "key_role": r.u8(), "capability": r.u16()}
    body = {"subject": r.take(32), "predicate": r.text(), "object": r.bytes(),
            "context": r.option_fixed(32), "nonce": r.take(32),
            "supersedes": r.option_fixed(32), "checkpoint": r.option_fixed(32)}
    r.done()
    return {"header": h, "body": body}


def cap2_ids(state: dict) -> set:
    return {c["key_id"] for c in state["controllers"] if 2 in c["capabilities"]}


def check_state_shape(state: dict) -> None:
    seal = state["seal_policy"]
    require(seal["controller_seal_bindings"] == sorted(seal["controller_seal_bindings"]), "SEAL_BINDINGS_UNSORTED")
    require({k for k, _ in seal["controller_seal_bindings"]} == cap2_ids(state), "STALE_SEAL_BINDING")
    require({k for k, _ in seal["recovery_seal_bindings"]} == set(state["recovery_policy"]["recovery_key_ids"]),
            "STALE_SEAL_BINDING")
    xs = [c["public_key"] for c in state["controllers"]] + \
         [x for _, x in seal["controller_seal_bindings"] + seal["recovery_seal_bindings"]]
    require(len(xs) == len(set(xs)), "XONLY_REUSE")
    require(state["lifecycle_status"] in (1, 2), "UNKNOWN_STATUS")


def evaluate(lineage: dict) -> list[str]:
    """Return per-step results; raise Reject(code) at the first invalid step."""
    ent = lineage["entity"]
    custodian_state = lineage["custodian_state_id"]
    custodian_genesis = decode_payload(lineage["custodian_genesis"])["body"]["state"]
    results = []
    prior = prior_bytes = None
    for step in lineage["steps"]:
        payload = step["payload"]
        try:
            decoded = decode_payload(payload)
        except DecodeError as error:
            raise Reject(f"DECODE:{error}")
        h, body = decoded["header"], decoded["body"]
        require(h["version"] == 1, "VERSION")
        require(h["network"] == NETWORK, "WRONG_NETWORK")
        start, end = decoded["spans"]["resulting_state"]
        new_bytes = payload[start:end]
        new = body["state"]
        check_state_shape(new)
        if step["kind"] == "genesis":
            require(h["object_type"] == 1 and entity_id(payload) == ent, "GENESIS")
            pub, sig = step["signatures"][0]
            require(bip340_verify(pub, tagged_hash(GENESIS_TAG, payload), sig), "BAD_SIGNATURE")
            prior, prior_bytes = new, new_bytes
            results.append("GENESIS_OK")
            continue
        require(prior["lifecycle_status"] == 1, "TRANSITION_AFTER_REVOKED")
        prior_id = state_id(ent, prior_bytes)
        require(h["signer_entity"] == ent, "WRONG_ENTITY")
        require(h["authorizing_state"] == prior_id, "STALE_AUTHORIZING_STATE")
        require(new["sequence"] == prior["sequence"] + 1, "SEQUENCE")
        require(new["previous_state"] == prior_id, "STALE_PREVIOUS_STATE")
        require(new["previous_seal"] == prior["next_seal"], "PREVIOUS_SEAL_MISMATCH")
        require(new["next_seal"] != prior["next_seal"], "NEXT_SEAL_REUSED")
        op = body["operation"]
        same_policy = new["recovery_policy"]["canonical"] == prior["recovery_policy"]["canonical"]
        same_controllers = new["controllers"] == prior["controllers"]
        if step["kind"] == "transition":
            require(h["object_type"] == 2 and h["capability"] == 2 and h["key_role"] == 1, "DOMAIN")
            require(op in (1, 2, 4, 5), "OPERATION_NOT_IN_DOMAIN")
            require(h["signing_key_id"] in cap2_ids(prior), "SIGNER_NOT_AUTHORIZED")
            pub, sig = step["signatures"][0]
            require(key_id(1, pub) == h["signing_key_id"], "KEY_ID")
            require(bip340_verify(pub, tagged_hash(TRANSITION_TAG, payload), sig), "BAD_SIGNATURE")
            anchor = tagged_hash(TRANSITION_TAG, payload)
            require(step["rgb_type"] == 8101, "RGB_TYPE_DOMAIN_MISMATCH")
        else:
            require(h["object_type"] == 3 and h["capability"] == 3 and h["key_role"] == 2, "DOMAIN")
            require(op == 3, "OPERATION_NOT_IN_DOMAIN")
            policy = prior["recovery_policy"]
            require(body["policy_hash"] == tagged_hash(POLICY_TAG, policy["canonical"]), "STALE_POLICY_HASH")
            require(body["not_before_height"] == step["seal_height"] + policy["delay_blocks"], "NOT_BEFORE")
            require(step["anchor_height"] >= body["not_before_height"], "RECOVERY_BEFORE_NOT_BEFORE")
            rbody = payload[decoded["spans"]["operation"][0]:]
            keys = []
            for p, (pub, sig) in zip(step["payloads"], step["signatures"]):
                d = decode_payload(p)
                require(d["header"]["authorizing_state"] == prior_id, "STALE_AUTHORIZING_STATE")
                require(p[decoded["spans"]["operation"][0]:] == rbody, "RECOVERY_BODY_MISMATCH")
                require(key_id(2, pub) == d["header"]["signing_key_id"], "KEY_ID")
                require(d["header"]["signing_key_id"] in policy["recovery_key_ids"], "SIGNER_NOT_IN_POLICY")
                require(bip340_verify(pub, tagged_hash(RECOVERY_TAG, p), sig), "BAD_SIGNATURE")
                keys.append(d["header"]["signing_key_id"])
            require(keys == sorted(keys) and len(keys) == len(set(keys)), "DUPLICATE_OR_UNSORTED_SIGNER")
            require(len(keys) >= policy["threshold"], "INSUFFICIENT_THRESHOLD")
            anchor = recovery_anchor_digest(ent, rbody)
            require(step["rgb_type"] == 8102, "RGB_TYPE_DOMAIN_MISMATCH")
            require(same_policy or new["recovery_policy"]["policy_sequence"]
                    == policy["policy_sequence"] + 1, "POLICY_SEQUENCE")
        require(step["anchor_digest"] is not None, "ANCHOR_DIGEST_MISSING")
        require(step["anchor_digest"] == anchor, "ANCHOR_DIGEST_MISMATCH")
        if op != 4:
            require(new["custodian"] == prior["custodian"], "CUSTODIAN_CHANGED_OUTSIDE_OP4")
            require(new["custody_acceptance"] is None, "UNEXPECTED_ACCEPTANCE")
        if op != 5:
            require(new["lifecycle_status"] == 1, "STATUS")
        if op == 1:
            require(same_policy, "ROTATION_CHANGES_POLICY")
            require(not same_controllers, "ROTATION_WITHOUT_CHANGE")
        elif op == 2:
            require(same_controllers, "POLICY_CHANGE_CHANGES_CONTROLLERS")
            require(new["recovery_policy"]["policy_sequence"]
                    == prior["recovery_policy"]["policy_sequence"] + 1, "POLICY_SEQUENCE")
        elif op == 4:
            require(same_controllers and same_policy, "CUSTODY_CHANGES_AUTHORITY")
            require(new["custody_acceptance"] is not None, "CUSTODY_WITHOUT_ACCEPTANCE")
            claim = step["custody_claim"]
            require(tagged_hash(CLAIM_TAG, claim["payload"]) == new["custody_acceptance"], "ACCEPTANCE_ID")
            c = decode_claim(claim["payload"])
            ch, cb = c["header"], c["body"]
            require(ch["object_type"] == 4 and ch["capability"] == 4 and ch["key_role"] == 1, "ACCEPTANCE_DOMAIN")
            require(cb["predicate"] == CUSTODY_PREDICATE, "ACCEPTANCE_PREDICATE")
            require(ch["signer_entity"] == new["custodian"] and new["custodian"] != ent
                    and new["custodian"] != prior["custodian"], "ACCEPTANCE_SIGNER")
            require(ch["authorizing_state"] == custodian_state, "ACCEPTANCE_AUTHORIZING_STATE")
            require(ch["signing_key_id"] in cap4_ids(custodian_genesis), "ACCEPTANCE_KEY")
            require(key_id(1, claim["signer"]) == ch["signing_key_id"], "KEY_ID")
            require(bip340_verify(claim["signer"], new["custody_acceptance"], claim["signature"]),
                    "BAD_SIGNATURE")
            require(cb["subject"] == ent, "ACCEPTANCE_SUBJECT")
            obj = cb["object"]
            require(len(obj) == 100, "ACCEPTANCE_OBJECT")
            require(obj[:32] == prior_id, "ACCEPTANCE_PRIOR_STATE")
            require(obj[32:64] == ch["signer_entity"], "ACCEPTANCE_SIGNER")
            require(obj[64:] == new["next_seal"], "ACCEPTANCE_NEXT_SEAL")
        elif op == 5:
            require(new["lifecycle_status"] == 2, "REVOCATION_NOT_REVOKED")
            require(same_controllers and same_policy, "REVOCATION_CHANGES_AUTHORITY")
        prior, prior_bytes = new, new_bytes
        results.append({1: "ROTATED", 2: "POLICY_CHANGED", 3: "RECOVERED",
                        4: "CUSTODY_TRANSFERRED", 5: "REVOKED"}[op])
    return results


def cap4_ids(state: dict) -> set:
    return {c["key_id"] for c in state["controllers"] if 4 in c["capabilities"]}


ADVERSARIAL = {
    "op3_in_transition_domain": "OPERATION_NOT_IN_DOMAIN",
    "sequence_skip": "SEQUENCE",
    "stale_previous_state": "STALE_AUTHORIZING_STATE",
    "previous_seal_mismatch": "PREVIOUS_SEAL_MISMATCH",
    "next_seal_reused": "NEXT_SEAL_REUSED",
    "rotated_out_signer": "SIGNER_NOT_AUTHORIZED",
    "signature_invalid": "BAD_SIGNATURE",
    "cross_network": "WRONG_NETWORK",
    "rotation_changes_policy": "ROTATION_CHANGES_POLICY",
    "custodian_changed_outside_op4": "CUSTODIAN_CHANGED_OUTSIDE_OP4",
    "stale_seal_binding": "STALE_SEAL_BINDING",
    "policy_sequence_not_incremented": "POLICY_SEQUENCE",
    "custody_without_acceptance": "CUSTODY_WITHOUT_ACCEPTANCE",
    "custody_wrong_next_seal": "ACCEPTANCE_NEXT_SEAL",
    "custody_wrong_prior_state": "ACCEPTANCE_PRIOR_STATE",
    "custody_signer_mismatch": "ACCEPTANCE_SIGNER",
    "custody_wrong_predicate": "ACCEPTANCE_PREDICATE",
    "recovery_stale_policy_hash": "STALE_POLICY_HASH",
    "recovery_below_not_before": "RECOVERY_BEFORE_NOT_BEFORE",
    "recovery_insufficient_threshold": "INSUFFICIENT_THRESHOLD",
    "recovery_duplicate_signer": "DUPLICATE_OR_UNSORTED_SIGNER",
    "recovery_key_not_in_prior_policy": "SIGNER_NOT_IN_POLICY",
    "anchor_digest_mismatch": "ANCHOR_DIGEST_MISMATCH",
    "anchor_missing": "ANCHOR_DIGEST_MISSING",
    "rgb_type_mismatch": "RGB_TYPE_DOMAIN_MISMATCH",
    "revocation_status_active": "REVOCATION_NOT_REVOKED",
    "transition_after_revocation": "TRANSITION_AFTER_REVOKED",
}


def outcome(case: str) -> str:
    try:
        evaluate(build(case))
    except Reject as reject:
        return str(reject)
    return "ACCEPT"


def serialize(lineage: dict) -> dict:
    ent = lineage["entity"]
    steps = []
    for step in lineage["steps"]:
        decoded = decode_payload(step["payload"])
        start, end = decoded["spans"]["resulting_state"]
        row = {
            "kind": step["kind"],
            "operation": decoded["body"].get("operation", 0),
            "rgb_transition_type": step["rgb_type"],
            "payload_hex": [p.hex() for p in step.get("payloads", [step["payload"]])],
            "signatures": [{"xonly": p.hex(), "bip340": s.hex()} for p, s in step["signatures"]],
            "anchor_digest": step["anchor_digest"].hex(),
            "state_id": state_id(ent, step["payload"][start:end]).hex(),
            "seal_creation_height": step["seal_height"],
            "anchor_height": step["anchor_height"],
        }
        if "custody_claim" in step:
            claim = step["custody_claim"]
            row["custody_acceptance_claim"] = {
                "payload_hex": claim["payload"].hex(),
                "claim_id": tagged_hash(CLAIM_TAG, claim["payload"]).hex(),
                "xonly": claim["signer"].hex(), "bip340": claim["signature"].hex()}
        steps.append(row)
    return {
        "spdx": "CC0-1.0",
        "status": "proposed (ADR-0014); not frozen until accepted",
        "unsafe_for_funds": True,
        "network": "regtest",
        "scalars": SCALARS,
        "entity_id": ent.hex(),
        "custodian_entity_id": lineage["custodian_entity"].hex(),
        "custodian_genesis_hex": lineage["custodian_genesis"].hex(),
        "valid_lineage": steps,
        "valid_results": evaluate(lineage),
        "adversarial": {case: code for case, code in ADVERSARIAL.items()},
    }


def main() -> None:
    lineage = build()
    data = serialize(lineage)
    if "--emit" in sys.argv:
        FIXTURE.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
        print(f"wrote {FIXTURE.name}")
        return
    stored = json.loads(FIXTURE.read_text())
    if stored != json.loads(json.dumps(data, sort_keys=True)):
        print("transition freeze: regenerated vectors differ from fixture", file=sys.stderr)
        sys.exit(1)
    if data["valid_results"] != ["GENESIS_OK", "ROTATED", "POLICY_CHANGED",
                                 "CUSTODY_TRANSFERRED", "RECOVERED", "REVOKED"]:
        print(f"unexpected valid results {data['valid_results']}", file=sys.stderr)
        sys.exit(1)
    failures = [(case, code, outcome(case)) for case, code in ADVERSARIAL.items()
                if outcome(case) != code]
    if failures:
        for case, want, got in failures:
            print(f"adversarial {case}: want {want} got {got}", file=sys.stderr)
        sys.exit(1)
    if "--no-rust" not in sys.argv:
        checks = 0
        for row in data["valid_lineage"]:
            sigs = [(s["xonly"], s["bip340"]) for s in row["signatures"]]
            payloads = row["payload_hex"]
            tag = {"genesis": GENESIS_TAG, "transition": TRANSITION_TAG, "recovery": RECOVERY_TAG}[row["kind"]]
            for payload, (pub, sig) in zip(payloads, sigs):
                msg = tagged_hash(tag, bytes.fromhex(payload)).hex()
                if crypto(["verify", pub, msg, sig]).returncode != 0:
                    print(f"rust verify failed for {row['kind']}", file=sys.stderr)
                    sys.exit(1)
                checks += 1
            claim = row.get("custody_acceptance_claim")
            if claim:
                if crypto(["verify", claim["xonly"], claim["claim_id"], claim["bip340"]]).returncode != 0:
                    print("rust verify failed for custody claim", file=sys.stderr)
                    sys.exit(1)
                checks += 1
        print(f"rust bip340 cross-check ok ({checks} signatures)")
    print(f"transition freeze: {len(data['valid_results'])} steps valid, "
          f"{len(ADVERSARIAL)}/{len(ADVERSARIAL)} adversarial rejections as expected")


if __name__ == "__main__":
    main()
