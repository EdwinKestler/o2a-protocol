#!/usr/bin/env python3
"""Adversarial fixtures for the Option B EntityID proposal (Draft v0.1).

TEST-ONLY. NOT NORMATIVE. NOT FROZEN. Option B is a *candidate* under test:

    EntityID_B = TaggedHash("O2A/v0.1/entity-id",
                            u16(1) || network || root_xonly || genesis_seal)

where genesis_seal is the canonical 36-byte outpoint (32 serialized txid bytes
|| u32 LE vout) named by the genesis state's `next_seal`.

Every rule except the EntityID derivation is evaluated by the repository's own
checkers (check_protocol_objects.py, check_vectors.py) at the pinned spec. The
only substitution is `entity_id`, swapped for the Option B candidate while a
genesis is evaluated. Signatures use published, permanently unsafe BIP340 test
keys. Bitcoin transactions are synthetic, well-formed legacy serializations:
they have real txids but no blocks, merkle proofs, or headers, so every
full-chain result is labelled UNPROVEN.

Usage (inside the dev toolchain, which provides cargo for the Rust verifier):
    python3 tests/vectors/option-b/check_option_b.py            # check
    python3 tests/vectors/option-b/check_option_b.py --emit     # regenerate
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import check_protocol_objects as cpo  # noqa: E402
import check_vectors as cv  # noqa: E402
from derive_route_b import CURVE_N, public_point  # noqa: E402

FIXTURE_PATH = HERE / "option-b-v0.1.json"
SPEC_COMMIT = "c7b08716d017d1f6125e6a728fb098673a09d433"
LABEL = "OPTION-B-CANDIDATE: disposable, test-only, not normative, not frozen"
NETWORK = 4  # regtest; required depth 1 (verification-policy.md)
MAINNET_DEPTH = 6
GENESIS_TAG = "O2A/v0.1/entity-genesis"
TRANSITION_TAG = "O2A/v0.1/identity-transition"
ENTITY_TAG = "O2A/v0.1/entity-id"

# Published BIP340 test-vector secrets (permanently unsafe). The same three
# keys are the only ones the repository's Rust signer exposes, so every
# signature below is reproduced by that independent implementation.
KEYS = {
    "root": (3, "scalar-3"),
    "legit_controller": (
        0xB7E151628AED2A6ABF7158809CF4F3C762E7160F38B4DA56A784D9045190CFEF,
        "bip340-vector-1",
    ),
    "attacker_controller": (
        0xC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B14E5C9,
        "bip340-vector-2",
    ),
}
ROOT = cpo.ROOT_PUBLIC
LEGIT = cpo.CONTROLLER_PUBLIC
ATTACKER = cpo.RECOVERY_PUBLIC  # BIP340 vector-2 key, used here as a controller
RECOVERY = cpo.ALBUM_ROOT  # BIP340 vector-3 key; never signs in these fixtures
SEAL_C = cpo.SEAL_VECTOR_KEYS[0]
SEAL_R = cpo.SEAL_VECTOR_KEYS[3]
DELAY = 6
THRESHOLD = 1


# ---------------------------------------------------------------- primitives


def xonly(secret: int) -> bytes:
    return public_point(secret)[0].to_bytes(32, "big")


def bip340_sign(secret: int, message: bytes) -> bytes:
    """BIP340 reference signing with a 32-byte all-zero aux_rand.

    libsecp256k1's sign_schnorr_no_aux_rand (used by the Rust checker) is the
    same construction, so both implementations must emit identical bytes.
    """
    point = public_point(secret)
    d = secret if point[1] % 2 == 0 else CURVE_N - secret
    px = point[0].to_bytes(32, "big")
    masked = bytes(
        a ^ b
        for a, b in zip(d.to_bytes(32, "big"), cpo.tagged_hash("BIP0340/aux", bytes(32)))
    )
    k0 = int.from_bytes(cpo.tagged_hash("BIP0340/nonce", masked + px + message), "big") % CURVE_N
    if k0 == 0:
        raise ValueError("zero nonce")
    r_point = public_point(k0)
    k = k0 if r_point[1] % 2 == 0 else CURVE_N - k0
    rx = r_point[0].to_bytes(32, "big")
    e = int.from_bytes(cpo.tagged_hash("BIP0340/challenge", rx + px + message), "big") % CURVE_N
    return rx + ((k + e * d) % CURVE_N).to_bytes(32, "big")


def sha256d(data: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def compact(value: int) -> bytes:
    return cpo.compact_size(value)


def tx_serialize(inputs: list[tuple[bytes, int]], outputs: list[tuple[int, bytes]]) -> bytes:
    """Legacy (non-witness) serialization; the txid commits to all of it."""
    out = bytearray(cpo.u32(2))
    out += compact(len(inputs))
    for prev_txid, vout in inputs:
        out += prev_txid + cpo.u32(vout) + compact(0) + cpo.u32(0xFFFFFFFD)
    out += compact(len(outputs))
    for value, script in outputs:
        out += cpo.u64(value) + compact(len(script)) + script
    out += cpo.u32(0)
    return bytes(out)


def tx_parse(raw: bytes) -> dict:
    offset = 4

    def read_compact() -> int:
        nonlocal offset
        first = raw[offset]
        offset += 1
        if first < 0xFD:
            return first
        size = {0xFD: 2, 0xFE: 4, 0xFF: 8}[first]
        value = int.from_bytes(raw[offset : offset + size], "little")
        offset += size
        return value

    inputs = []
    for _ in range(read_compact()):
        prev = raw[offset : offset + 36]
        offset += 36
        script_length = read_compact()  # read first: it advances offset
        offset += script_length + 4
        inputs.append(prev)
    outputs = []
    for _ in range(read_compact()):
        value = int.from_bytes(raw[offset : offset + 8], "little")
        offset += 8
        length = read_compact()
        outputs.append((value, raw[offset : offset + length]))
        offset += length
    if offset + 4 != len(raw):
        raise ValueError("trailing transaction bytes")
    return {"txid": sha256d(raw), "inputs": inputs, "outputs": outputs}


def outpoint(txid: bytes, vout: int) -> bytes:
    return txid + cpo.u32(vout)


# ------------------------------------------------------------- Option B rule


def option_b_preimage(network: int, root: bytes, seal: bytes) -> bytes:
    if len(root) != 32 or len(seal) != 36:
        raise ValueError("root is 32 bytes and seal outpoint is 36 bytes")
    return cpo.u16(1) + bytes([network]) + root + seal


def option_b_entity_id(network: int, root: bytes, seal: bytes) -> bytes:
    return cpo.tagged_hash(ENTITY_TAG, option_b_preimage(network, root, seal))


def current_entity_id(root: bytes) -> bytes:
    return cpo.tagged_hash(ENTITY_TAG, cpo.u16(1) + bytes([NETWORK]) + root)


# ------------------------------------------------------------ object builders


def controllers_bytes(controllers: list[tuple[bytes, list[int]]]) -> bytes:
    encoded = sorted(
        (cpo.key_id(1, public), cpo.controller(public, caps)) for public, caps in controllers
    )
    return cpo.list_items([value for _, value in encoded])


def recovery_policy() -> bytes:
    return cpo.recovery_policy([cpo.key_id(2, RECOVERY)], delay_blocks=DELAY)


def seal_bindings(controller_publics: list[bytes]) -> tuple[list, list]:
    """Bind each listed transition controller to SEAL_C (single-controller
    fixtures only) and the recovery key to SEAL_R."""
    if len(controller_publics) != 1:
        raise ValueError("fixtures bind exactly one transition controller")
    controller = [(cpo.key_id(1, controller_publics[0]), SEAL_C)]
    recovery = [(cpo.key_id(2, RECOVERY), SEAL_R)]
    return controller, recovery


def state_bytes(
    *,
    sequence: int,
    previous_state: bytes | None,
    previous_seal: bytes | None,
    next_seal: bytes,
    controllers: list[tuple[bytes, list[int]]],
    transition_controllers: list[bytes],
) -> bytes:
    controller_b, recovery_b = seal_bindings(transition_controllers)
    return b"".join(
        (
            cpo.u64(sequence),
            cpo.option(previous_state),
            cpo.option(previous_seal),
            next_seal,
            controllers_bytes(controllers),
            recovery_policy(),
            cpo.seal_policy(sorted(controller_b), sorted(recovery_b)),
            cpo.option(None),
            b"\x01",
            cpo.option(None),
            cpo.option(None),
        )
    )


def genesis_payload(entity: bytes, seal: bytes, controllers, transition_controllers) -> bytes:
    header = cpo.common_header(1, 1, entity, None, cpo.key_id(0, ROOT), 0)
    return (
        header
        + cpo.u16(2)  # ARTIST
        + ROOT
        + state_bytes(
            sequence=0,
            previous_state=None,
            previous_seal=None,
            next_seal=seal,
            controllers=controllers,
            transition_controllers=transition_controllers,
        )
    )


def expected_script(transition_controllers: list[bytes]) -> bytes:
    controller_b, recovery_b = seal_bindings(transition_controllers)
    return bytes.fromhex(cpo.seal_output(controller_b, recovery_b, THRESHOLD, DELAY)["script_pubkey"])


def sign(key: str, tag: str, payload: bytes) -> str:
    return bip340_sign(KEYS[key][0], cpo.tagged_hash(tag, payload)).hex()


def placeholder_state_id(genesis: bytes) -> bytes:
    # The RGB state ID is RGB-defined and still unbound in the spec. The
    # fixtures use the genesis commitment digest as a stand-in; any injective
    # function of the genesis payload gives the same result here.
    return cpo.tagged_hash(GENESIS_TAG, genesis)


# ---------------------------------------------------------------- evaluators


def evaluate_genesis(payload: bytes, signature: str, derivation: str,
                     bound_outpoint: bytes | None = None) -> str:
    """Run the repository's genesis evaluator; swap only the EntityID rule.

    derivation "current" uses the spec as written; "option_b" binds the
    EntityID to the genesis state's next_seal, or to `bound_outpoint` when the
    candidate bootstrap model supplies one.
    """
    decoded = cpo.decode_payload(payload)
    seal = bound_outpoint or decoded["body"]["state"]["next_seal"]
    original = cpo.entity_id
    if derivation == "option_b":
        cpo.entity_id = lambda root: option_b_entity_id(NETWORK, root, seal)
    try:
        return cpo.evaluate_signed_payload(
            payload, signature, ROOT, GENESIS_TAG, {"expected_network": NETWORK}
        )
    finally:
        cpo.entity_id = original


def authorization(package: dict, signer: bytes) -> dict | None:
    state = cpo.decode_payload(bytes.fromhex(package["genesis"]))["body"]["state"]
    for controller in state["controllers"]:
        if controller["public_key"] == signer:
            return {
                "entity": package["entity_id"],
                "state": package["state_id"],
                "key_id": controller["key_id"].hex(),
                "public_key": signer.hex(),
                "key_role": 1,
                "capabilities": controller["capabilities"],
            }
    return None


def evaluate_claim(package: dict, claim: dict) -> str:
    signer = bytes.fromhex(claim["public_key"])
    auth = authorization(package, signer)
    if auth is None:
        return "rejected: signer is not a controller in this package's history"
    accepted, reason = cv.evaluate_name_claim(
        bytes.fromhex(claim["payload"]), claim["signature"], claim["public_key"], NETWORK, auth
    )
    return "accepted" if accepted else f"rejected: {reason}"


def transition_valid_for(package: dict, transition: dict) -> bool:
    auth = authorization(package, bytes.fromhex(transition["public_key"]))
    if auth is None:
        return False
    context = {
        "expected_network": NETWORK,
        "prior_sequence": 0,
        "authorization": {
            "entity": bytes.fromhex(auth["entity"]),
            "state": bytes.fromhex(auth["state"]),
            "key_id": bytes.fromhex(auth["key_id"]),
            "role": 1,
            "public_key": bytes.fromhex(auth["public_key"]),
            "capabilities": auth["capabilities"],
        },
    }
    return (
        cpo.evaluate_signed_payload(
            bytes.fromhex(transition["payload"]),
            transition["signature"],
            bytes.fromhex(transition["public_key"]),
            TRANSITION_TAG,
            context,
        )
        == "valid"
    )


def verify_package(package: dict, view: dict, transitions: dict) -> dict:
    """Option B history evaluation against one explicit Bitcoin view."""
    payload = bytes.fromhex(package["genesis"])
    result = {"entity_id": package["entity_id"], "rule_path": []}
    if evaluate_genesis(payload, package["signature"], "option_b") != "valid":
        return dict(result, state="INVALID", rule_path=["genesis rules (Option B EntityID)"])
    result["rule_path"].append("genesis valid")
    digest = package.get("consignment_genesis_digest")
    if digest is None:
        return dict(result, state="INCOMPLETE", rule_path=result["rule_path"] + ["consignment digest missing"])
    if digest != cpo.tagged_hash(GENESIS_TAG, payload).hex():
        return dict(result, state="INVALID", rule_path=result["rule_path"] + ["consignment digest mismatch"])
    result["rule_path"].append("consignment digest matches")
    state = cpo.decode_payload(payload)["body"]["state"]
    seal = state["next_seal"]
    creating = view["transactions"].get(seal[:32].hex())
    if creating is None or creating["confirmations"] < view["required_depth"]:
        return dict(result, state="INCOMPLETE", rule_path=result["rule_path"] + ["seal-creating transaction missing from view"])
    outputs = tx_parse(bytes.fromhex(creating["raw"]))["outputs"]
    vout = int.from_bytes(seal[32:], "little")
    transition_ids = {
        controller["key_id"] for controller in state["controllers"] if 2 in controller["capabilities"]
    }
    publics = [c["public_key"] for c in state["controllers"] if c["key_id"] in transition_ids]
    if vout >= len(outputs) or outputs[vout][1] != expected_script(publics):
        return dict(result, state="INVALID", rule_path=result["rule_path"] + ["seal scriptPubKey mismatch"])
    result["rule_path"].append("seal scriptPubKey matches seal policy")
    spend = view["spends"].get(seal.hex())
    valid_transition = False
    if spend is not None:
        valid_transition = transition_valid_for(package, transitions[spend["transition"]])
    history = cpo.identity_history_outcome(
        bitcoin_view_source=view["source"],
        best_block_hash=bytes.fromhex(view["best_block_hash"]),
        observed_height=view["height"],
        seal_observation="spent" if spend else ("unspent" if seal.hex() in view["unspent"] else None),
        spend_proof=spend is not None,
        spend_confirmations=spend["confirmations"] if spend else 0,
        required_depth=view["required_depth"],
        valid_transition=valid_transition,
    )
    return dict(result, state=history["state"], rule_path=result["rule_path"] + ["identity_history_outcome"])


# ------------------------------------------------------------------ fixtures


def build() -> dict:
    transitions: dict = {}
    # One funding transaction creates two seal outputs with the same policy
    # script (legit controller transition-bound to SEAL_C).
    script = expected_script([LEGIT])
    funding = tx_serialize([(bytes([0xF0]) * 32, 0)], [(1000, script), (1000, script), (1000, script)])
    fund_txid = sha256d(funding)
    o1, o2, o3 = (outpoint(fund_txid, i) for i in range(3))

    legit_controllers = [(LEGIT, [2, 4])]
    e1 = option_b_entity_id(NETWORK, ROOT, o1)
    e2 = option_b_entity_id(NETWORK, ROOT, o2)

    def package(name, entity, seal, controllers, transition_controllers):
        payload = genesis_payload(entity, seal, controllers, transition_controllers)
        return {
            "name": name,
            "entity_id": entity.hex(),
            "genesis": payload.hex(),
            "signature": sign("root", GENESIS_TAG, payload),
            "state_id": placeholder_state_id(payload).hex(),
            "consignment_genesis_digest": cpo.tagged_hash(GENESIS_TAG, payload).hex(),
        }

    legit = package("legit-o1", e1, o1, legit_controllers, [LEGIT])
    # Baseline: the spec as written (root-only EntityID) on two seals.
    ecur = current_entity_id(ROOT)
    base_o1 = package("current-derivation-o1", ecur, o1, legit_controllers, [LEGIT])
    base_o2 = package("current-derivation-o2", ecur, o2, legit_controllers, [LEGIT])
    case1 = package("same-root-o2", e2, o2, legit_controllers, [LEGIT])
    # Case 1 impersonation: seal O2 but signer_entity claims E1.
    swapped = package("o2-claims-e1", e1, o2, legit_controllers, [LEGIT])
    # Case 2a: add a claim-only controller. Capability 4 without 2 needs no
    # seal binding, so the seal policy (and script) is byte-identical.
    attack_add = package(
        "same-seal-add-claim-controller", e1, o1, [(LEGIT, [2, 4]), (ATTACKER, [4])], [LEGIT]
    )
    # Case 2b: replace the transition controller; keep its seal x-only key.
    attack_replace = package("same-seal-replace-controller", e1, o1, [(ATTACKER, [2, 4])], [ATTACKER])

    # Legit rotation that later closes O1 (sequence 1, next seal O3).
    legit_state = bytes.fromhex(legit["state_id"])
    rotation = (
        cpo.common_header(2, 2, e1, legit_state, cpo.key_id(1, LEGIT), 1)
        + b"\x01"
        + state_bytes(
            sequence=1,
            previous_state=legit_state,
            previous_seal=o1,
            next_seal=o3,
            controllers=[(LEGIT, [2, 4])],
            transition_controllers=[LEGIT],
        )
    )
    transitions["legit-rotation"] = {
        "payload": rotation.hex(),
        "signature": sign("legit_controller", TRANSITION_TAG, rotation),
        "public_key": LEGIT.hex(),
    }

    def claim(name, entity, state_id, key, public, predicate, value):
        spec = {"object_type": 4, "capability": 4, "predicate_utf8": predicate,
                "object_utf8": value, "nonce_hex": hashlib.sha256(name.encode()).hexdigest()}
        payload = cv.build_claim(spec, entity, bytes.fromhex(state_id), cpo.key_id(1, public))
        return {"name": name, "payload": payload.hex(),
                "signature": sign(key, "O2A/v0.1/claim", payload), "public_key": public.hex()}

    attacker_claim = claim("attacker-settlement", e1, attack_add["state_id"], "attacker_controller",
                           ATTACKER, "settlement_endpoint", "fixture:attacker-endpoint")
    legit_claim = claim("legit-settlement", e1, legit["state_id"], "legit_controller",
                        LEGIT, "settlement_endpoint", "fixture:artist-endpoint")
    case1_cross_claim = claim("o2-controller-claims-e1", e1, case1["state_id"], "legit_controller",
                              LEGIT, "settlement_endpoint", "fixture:o2-endpoint")

    base_view = {"source": "fixture-bitcoin-view (synthetic; no headers)",
                 "best_block_hash": "11" * 32, "height": 200, "required_depth": 1,
                 "transactions": {fund_txid.hex(): {"raw": funding.hex(), "confirmations": 10}},
                 "unspent": [o1.hex(), o2.hex(), o3.hex()], "spends": {}}
    closed_view = json.loads(json.dumps(base_view))
    closed_view["unspent"] = [o2.hex(), o3.hex()]
    closed_view["spends"] = {o1.hex(): {"transition": "legit-rotation", "confirmations": 1}}
    reorg_view = json.loads(json.dumps(base_view))
    reorg_view["transactions"] = {}
    # RBF/double-spend of the same funding input: different fee, new txid.
    replaced = tx_serialize([(bytes([0xF0]) * 32, 0)], [(900, script), (1000, script), (1000, script)])
    replaced_view = json.loads(json.dumps(base_view))
    replaced_view["transactions"] = {sha256d(replaced).hex(): {"raw": replaced.hex(), "confirmations": 10}}
    replaced_view["unspent"] = [outpoint(sha256d(replaced), i).hex() for i in range(3)]

    # Case 4: candidate "genesis closes a bootstrap seal" model (NOT SPEC).
    bootstrap_fund = tx_serialize([(bytes([0xB0]) * 32, 0)], [(2000, script)])
    bootstrap = outpoint(sha256d(bootstrap_fund), 0)
    ec = option_b_entity_id(NETWORK, ROOT, bootstrap)
    relative_seal = bytes(32) + cpo.u32(0)  # candidate marker: vout 0 of committing tx
    cand_legit = package("candidate-legit", ec, relative_seal, legit_controllers, [LEGIT])
    cand_attack = package("candidate-attack", ec, relative_seal,
                          [(LEGIT, [2, 4]), (ATTACKER, [4])], [LEGIT])

    def commit_tx(pkg, fee_out=1000):
        digest = bytes.fromhex(pkg["consignment_genesis_digest"])
        return tx_serialize([(bootstrap[:32], 0)], [(fee_out, script), (0, b"\x6a\x20" + digest)])

    legit_commit = commit_tx(cand_legit)
    attack_commit = commit_tx(cand_attack)
    rbf_commit = commit_tx(cand_legit, fee_out=900)

    # Circularity: naive "commit the genesis digest in the seal-creating
    # transaction that the genesis itself names".
    iterations = []
    named = bytes(32)
    for _ in range(5):
        pkg = package("circular", option_b_entity_id(NETWORK, ROOT, named + cpo.u32(0)),
                      named + cpo.u32(0), legit_controllers, [LEGIT])
        tx = tx_serialize([(bytes([0xC0]) * 32, 0)],
                          [(1000, script), (0, b"\x6a\x20" + bytes.fromhex(pkg["consignment_genesis_digest"]))])
        iterations.append({"named_txid": named.hex(), "resulting_txid": sha256d(tx).hex()})
        named = sha256d(tx)

    return {
        "label": LABEL,
        "spec_commit": SPEC_COMMIT,
        "network": NETWORK,
        "keys": {"root": ROOT.hex(), "legit_controller": LEGIT.hex(),
                 "attacker_controller": ATTACKER.hex(), "recovery": RECOVERY.hex(),
                 "seal_controller": SEAL_C.hex(), "seal_recovery": SEAL_R.hex()},
        "funding_tx": funding.hex(),
        "seals": {"o1": o1.hex(), "o2": o2.hex(), "o3": o3.hex()},
        "preimages": {"option_b_o1": option_b_preimage(NETWORK, ROOT, o1).hex(),
                      "option_b_o2": option_b_preimage(NETWORK, ROOT, o2).hex(),
                      "current": (cpo.u16(1) + bytes([NETWORK]) + ROOT).hex()},
        "entity_ids": {"option_b_o1": e1.hex(), "option_b_o2": e2.hex(),
                       "current": current_entity_id(ROOT).hex(),
                       "candidate_bootstrap": ec.hex()},
        "packages": {p["name"]: p for p in (legit, case1, swapped, attack_add, attack_replace,
                                             cand_legit, cand_attack, base_o1, base_o2)},
        "claims": {c["name"]: c for c in (attacker_claim, legit_claim, case1_cross_claim)},
        "transitions": transitions,
        "views": {"base": base_view, "closed": closed_view, "reorg": reorg_view, "replaced": replaced_view},
        "candidate": {"bootstrap_funding_tx": bootstrap_fund.hex(), "bootstrap": bootstrap.hex(),
                      "legit_commit_tx": legit_commit.hex(), "attack_commit_tx": attack_commit.hex(),
                      "rbf_commit_tx": rbf_commit.hex()},
        "circularity": iterations,
    }


# -------------------------------------------------------------------- checks


def candidate_outcome(fixture: dict, name: str, confirmed_spender: str | None, confirmations: int,
                      depth: int) -> str:
    """Candidate property (NOT SPEC): the genesis is valid only if the unique
    confirmed spender of the bootstrap outpoint commits its digest."""
    pkg = fixture["packages"][name]
    cand = fixture["candidate"]
    bootstrap = bytes.fromhex(cand["bootstrap"])
    if evaluate_genesis(bytes.fromhex(pkg["genesis"]), pkg["signature"], "option_b",
                        bound_outpoint=bootstrap) != "valid":
        return "INVALID: genesis rules with the EntityID bound to the bootstrap outpoint"
    if confirmed_spender is None:
        return "INCOMPLETE: bootstrap spend not observed"
    if confirmations < depth:
        return "INCOMPLETE: bootstrap spend below required depth (pending)"
    spender = tx_parse(bytes.fromhex(cand[confirmed_spender]))
    if spender["inputs"] != [bootstrap]:
        return "INVALID: committing transaction does not spend the bootstrap outpoint"
    carrier = spender["outputs"][1][1]
    if carrier != b"\x6a\x20" + bytes.fromhex(pkg["consignment_genesis_digest"]):
        return "INVALID: bootstrap spender commits a different genesis"
    return "VALID: unique genesis for this EntityID"


def run_checks(fixture: dict) -> list[dict]:
    p = fixture["packages"]
    c = fixture["claims"]
    t = fixture["transitions"]
    v = fixture["views"]
    rows: list[dict] = []

    def row(case, label, expected, observed):
        rows.append({"case": case, "check": label, "expected": expected, "observed": observed,
                     "pass": expected == observed})

    # Independent signature verification (Rust checker) and cross-implementation
    # determinism against the Rust signer.
    for kind, items in (("genesis", p.values()), ("claim", c.values())):
        for item in items:
            public = ROOT if kind == "genesis" else bytes.fromhex(item["public_key"])
            tag = GENESIS_TAG if kind == "genesis" else "O2A/v0.1/claim"
            payload = bytes.fromhex(item["genesis"] if kind == "genesis" else item["payload"])
            ok = cpo.crypto_verify(public, cpo.tagged_hash(tag, payload), item["signature"])
            row("sig", f"Rust verify {kind} {item['name']}", True, ok)
    root_payload = bytes.fromhex(p["legit-o1"]["genesis"])
    _, rust_sig = cpo.crypto_sign("scalar-3", cpo.tagged_hash(GENESIS_TAG, root_payload))
    row("sig", "Python BIP340 == Rust signer (root, legit genesis)", p["legit-o1"]["signature"], rust_sig)

    # Case 1: different seals.
    row(1, "E(O1) != E(O2) under Option B", True,
        fixture["entity_ids"]["option_b_o1"] != fixture["entity_ids"]["option_b_o2"])
    for name in ("current-derivation-o1", "current-derivation-o2"):
        row(1, f"baseline (spec as written): {name} valid", "valid",
            evaluate_genesis(bytes.fromhex(p[name]["genesis"]), p[name]["signature"], "current"))
    row(1, "baseline (spec as written): both seals give one EntityID", True,
        p["current-derivation-o1"]["entity_id"] == p["current-derivation-o2"]["entity_id"])
    row(1, "genesis on O1 valid (Option B)", "valid",
        evaluate_genesis(bytes.fromhex(p["legit-o1"]["genesis"]), p["legit-o1"]["signature"], "option_b"))
    row(1, "genesis on O2 valid (Option B)", "valid",
        evaluate_genesis(bytes.fromhex(p["same-root-o2"]["genesis"]), p["same-root-o2"]["signature"], "option_b"))
    row(1, "genesis on O2 claiming E(O1) rejected", "invalid",
        evaluate_genesis(bytes.fromhex(p["o2-claims-e1"]["genesis"]), p["o2-claims-e1"]["signature"], "option_b"))
    row(1, "O2 history's controller cannot sign for E(O1)",
        "rejected: signer is not authorized by the stated fixture state",
        evaluate_claim(p["same-root-o2"], c["o2-controller-claims-e1"]))

    # Case 2: same seal.
    for name in ("same-seal-add-claim-controller", "same-seal-replace-controller"):
        pkg = p[name]
        row(2, f"{name}: genesis valid (Option B)", "valid",
            evaluate_genesis(bytes.fromhex(pkg["genesis"]), pkg["signature"], "option_b"))
        row(2, f"{name}: same EntityID as legit", True, pkg["entity_id"] == p["legit-o1"]["entity_id"])
        row(2, f"{name}: different genesis digest", True,
            pkg["consignment_genesis_digest"] != p["legit-o1"]["consignment_genesis_digest"])
        row(2, f"{name}: history state, same Bitcoin view", "CURRENT",
            verify_package(pkg, v["base"], t)["state"])
    row(2, "legit history state, same Bitcoin view", "CURRENT",
        verify_package(p["legit-o1"], v["base"], t)["state"])

    # Case 3: attacker payout claim.
    row(3, "attacker claim vs attacker package only", "accepted",
        evaluate_claim(p["same-seal-add-claim-controller"], c["attacker-settlement"]))
    row(3, "attacker claim vs legit package", "rejected: signer is not a controller in this package's history",
        evaluate_claim(p["legit-o1"], c["attacker-settlement"]))
    row(3, "legit claim vs legit package", "accepted", evaluate_claim(p["legit-o1"], c["legit-settlement"]))
    row(3, "after legit rotation closes O1: legit history", "CURRENT",
        verify_package(p["legit-o1"], v["closed"], t)["state"])
    row(3, "after legit rotation closes O1: attacker history", "SEAL_CLOSED_WITHOUT_VALID_TRANSITION",
        verify_package(p["same-seal-add-claim-controller"], v["closed"], t)["state"])

    # Case 4: commitment and reorg boundary.
    missing = dict(p["legit-o1"], consignment_genesis_digest=None)
    wrong = dict(p["legit-o1"], consignment_genesis_digest=p["same-seal-add-claim-controller"]["consignment_genesis_digest"])
    row(4, "consignment genesis digest missing", "INCOMPLETE", verify_package(missing, v["base"], t)["state"])
    row(4, "consignment genesis digest mismatched", "INVALID", verify_package(wrong, v["base"], t)["state"])
    row(4, "seal-creating tx reorged out", "INCOMPLETE", verify_package(p["legit-o1"], v["reorg"], t)["state"])
    row(4, "seal-creating tx replaced (RBF): old package", "INCOMPLETE",
        verify_package(p["legit-o1"], v["replaced"], t)["state"])
    new_seal = bytes.fromhex(next(iter(v["replaced"]["transactions"]))) + cpo.u32(0)
    row(4, "replacement outpoint yields a different EntityID", True,
        option_b_entity_id(NETWORK, ROOT, new_seal).hex() != p["legit-o1"]["entity_id"])
    row(4, "candidate: legit genesis, legit spender confirmed", "VALID: unique genesis for this EntityID",
        candidate_outcome(fixture, "candidate-legit", "legit_commit_tx", 1, 1))
    row(4, "candidate: attacker genesis, legit spender confirmed",
        "INVALID: bootstrap spender commits a different genesis",
        candidate_outcome(fixture, "candidate-attack", "legit_commit_tx", 1, 1))
    row(4, "candidate: attacker genesis after reorg to attacker spender (needs bootstrap key)",
        "VALID: unique genesis for this EntityID",
        candidate_outcome(fixture, "candidate-attack", "attack_commit_tx", 6, MAINNET_DEPTH))
    row(4, "candidate: legit spender at 3 of 6 mainnet confirmations",
        "INCOMPLETE: bootstrap spend below required depth (pending)",
        candidate_outcome(fixture, "candidate-legit", "legit_commit_tx", 3, MAINNET_DEPTH))
    row(4, "candidate: RBF of the committing tx keeps EntityID", "VALID: unique genesis for this EntityID",
        candidate_outcome(fixture, "candidate-legit", "rbf_commit_tx", 6, MAINNET_DEPTH))
    circular = fixture["circularity"]
    row(4, "circularity: naming the committing tx never reaches a fixed point (5 iterations)", True,
        all(i["named_txid"] != i["resulting_txid"] for i in circular))
    return rows


def main() -> int:
    if "--emit" in sys.argv:
        FIXTURE_PATH.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {FIXTURE_PATH.name}")
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    if fixture != json.loads(json.dumps(build())):
        print("fixture is not reproduced by the generator", file=sys.stderr)
        return 1
    rows = run_checks(fixture)
    for r in rows:
        mark = "ok  " if r["pass"] else "FAIL"
        print(f"{mark} [{r['case']}] {r['check']}: observed={r['observed']}")
    failed = [r for r in rows if not r["pass"]]
    print(f"option-b: {len(rows) - len(failed)}/{len(rows)} expectations met")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
