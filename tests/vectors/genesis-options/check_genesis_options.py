#!/usr/bin/env python3
"""Adversarial comparison of genesis-uniqueness options A, B, B+activation, C.

TEST-ONLY. NOT NORMATIVE. NOT FROZEN. Nothing here adopts an option.

Options as tested (pinned spec c7b0871 plus one candidate rule each):

A   EntityID = TaggedHash(entity-id, u16(1) || network || root)  (spec as written)
    + equivocation rule: two valid root-signed geneses with one EntityID and
    different digests are a portable proof; a verifier holding both treats the
    EntityID as GENESIS_EQUIVOCATION and accepts no claims for it.
B   EntityID = TaggedHash(entity-id, u16(1) || network || root || genesis_seal)
B+act  B, plus: a history whose genesis seal is unspent is PENDING_ACTIVATION,
    never CURRENT. It becomes CURRENT only after the genesis seal is closed by
    a valid committed transition at the required depth.
C   EntityID as in A, plus: a genesis takes effect only when committed by a
    confirmed transaction that pays G(root) = P2TR(NUMS, leaf OP_RETURN<root>)
    and carries the genesis digest in an OP_RETURN. The first confirmed
    commitment (height, then block position) wins. "strict" treats an earlier
    commitment with an unknown digest as INCOMPLETE; "lax" skips it.

G   EntityID = TaggedHash(entity-id, genesis payload), where the genesis
    header's signer_entity is 32 zero bytes (it cannot name its own hash).
    Every distinct genesis, including one on the same seal, gets its own ID.
    A history is not CURRENT until its seal-creating transaction is at the
    required depth (reported here as INCOMPLETE).

Every O2A rule is evaluated by the repository's own checkers; signatures are
verified by the Rust crypto checker. Transactions are synthetic but
well-formed (real txids, no headers or merkle proofs): full-chain results are
UNPROVEN.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "option-b"))

import check_protocol_objects as cpo  # noqa: E402
import check_option_b as ob  # noqa: E402
from derive_route_b import CURVE_N, _point_add, public_point  # noqa: E402

FIXTURE_PATH = HERE / "genesis-options-v0.1.json"
LABEL = "GENESIS-OPTIONS COMPARISON: disposable, test-only, not normative, not frozen"
NETWORK = ob.NETWORK
MAINNET_DEPTH = 6
CLAIM_TAG = "O2A/v0.1/claim"
SV = cpo.SEAL_VECTOR_KEYS
LEGIT_SEALS = (SV[0], SV[3])  # (controller seal key, recovery seal key)
ATTACKER_SEALS = (SV[1], SV[4])  # an attacker funding its own seal


# ------------------------------------------------------------------ builders


def bindings(transition_public: bytes, seals: tuple[bytes, bytes]) -> tuple[list, list]:
    return ([(cpo.key_id(1, transition_public), seals[0])],
            [(cpo.key_id(2, ob.RECOVERY), seals[1])])


def script_for(transition_public: bytes, seals: tuple[bytes, bytes]) -> bytes:
    c, r = bindings(transition_public, seals)
    return bytes.fromhex(cpo.seal_output(c, r, ob.THRESHOLD, ob.DELAY)["script_pubkey"])


def state(sequence, previous_state, previous_seal, next_seal, controllers, transition_public, seals):
    c, r = bindings(transition_public, seals)
    return b"".join((
        cpo.u64(sequence), cpo.option(previous_state), cpo.option(previous_seal), next_seal,
        ob.controllers_bytes(controllers), ob.recovery_policy(),
        cpo.seal_policy(c, r), cpo.option(None), b"\x01", cpo.option(None), cpo.option(None),
    ))


def entity_for(derivation: str, seal: bytes) -> bytes:
    if derivation == "genesis":
        return bytes(32)  # header placeholder; the ID is the payload hash
    return (ob.current_entity_id(ob.ROOT) if derivation == "root"
            else ob.option_b_entity_id(NETWORK, ob.ROOT, seal))


def genesis_bound_id(payload: bytes) -> bytes:
    return cpo.tagged_hash(ob.ENTITY_TAG, payload)


def evaluate_any(package) -> str:
    payload = bytes.fromhex(package["genesis"])
    if package["derivation"] == "genesis":
        original = cpo.entity_id
        cpo.entity_id = lambda root: bytes(32)
        try:
            ok = cpo.evaluate_signed_payload(payload, package["signature"], ob.ROOT,
                                             ob.GENESIS_TAG, {"expected_network": NETWORK})
        finally:
            cpo.entity_id = original
        if ok != "valid" or bytes.fromhex(package["entity_id"]) != genesis_bound_id(payload):
            return "invalid"
        return "valid"
    derivation = "current" if package["derivation"] == "root" else "option_b"
    return ob.evaluate_genesis(payload, package["signature"], derivation)


def genesis(name, derivation, seal, controllers, transition_public, seals, header_entity=None):
    entity = header_entity if header_entity is not None else entity_for(derivation, seal)
    payload = (cpo.common_header(1, 1, entity, None, cpo.key_id(0, ob.ROOT), 0) + cpo.u16(2)
               + ob.ROOT + state(0, None, None, seal, controllers, transition_public, seals))
    if derivation == "genesis":
        entity = genesis_bound_id(payload)
    return {"name": name, "derivation": derivation, "entity_id": entity.hex(),
            "genesis": payload.hex(), "signature": ob.sign("root", ob.GENESIS_TAG, payload),
            "state_id": ob.placeholder_state_id(payload).hex(),
            "consignment_genesis_digest": cpo.tagged_hash(ob.GENESIS_TAG, payload).hex()}


def transition(name, package, signer_key, signer_public, prev_seal, next_seal, controllers,
               transition_public, seals):
    prev_state = bytes.fromhex(package["state_id"])
    entity = bytes.fromhex(package["entity_id"])
    payload = (cpo.common_header(2, 2, entity, prev_state, cpo.key_id(1, signer_public), 1) + b"\x01"
               + state(1, prev_state, prev_seal, next_seal, controllers, transition_public, seals))
    return {"name": name, "payload": payload.hex(), "public_key": signer_public.hex(),
            "signature": ob.sign(signer_key, ob.TRANSITION_TAG, payload),
            "state_id": cpo.tagged_hash(ob.TRANSITION_TAG, payload).hex()}


def claim(name, package, signer_key, signer_public, value):
    spec = {"object_type": 4, "capability": 4, "predicate_utf8": "settlement_endpoint",
            "object_utf8": value, "nonce_hex": cpo.tagged_hash("fixture-nonce", name.encode()).hex()}
    payload = ob.cv.build_claim(spec, bytes.fromhex(package["entity_id"]),
                                bytes.fromhex(package["state_id"]), cpo.key_id(1, signer_public))
    return {"name": name, "package": package["name"], "payload": payload.hex(),
            "public_key": signer_public.hex(),
            "signature": ob.sign(signer_key, CLAIM_TAG, payload)}


def genesis_address(root: bytes) -> bytes:
    """Option C candidate: unspendable, deterministic, indexable per root."""
    leaf = cpo.tapleaf_hash(b"\x6a\x20" + root)
    tweak = int.from_bytes(cpo.tagged_hash("TapTweak", cpo.SEAL_INTERNAL_KEY + leaf), "big")
    if tweak >= CURVE_N:
        raise ValueError("tweak out of range")
    point = _point_add(cpo.lift_x(cpo.SEAL_INTERNAL_KEY), public_point(tweak))
    return b"\x51\x20" + point[0].to_bytes(32, "big")


def commitment_tx(marker: int, digest: bytes) -> bytes:
    return ob.tx_serialize([(bytes([marker]) * 32, 0)],
                           [(330, genesis_address(ob.ROOT)), (0, b"\x6a\x20" + digest)])


# ------------------------------------------------------------------ fixtures


def build() -> dict:
    legit_script = script_for(ob.LEGIT, LEGIT_SEALS)
    attacker_script = script_for(ob.ATTACKER, ATTACKER_SEALS)
    fund_legit = ob.tx_serialize([(bytes([0xF0]) * 32, 0)], [(1000, legit_script), (1000, legit_script)])
    fund_att = ob.tx_serialize([(bytes([0xA0]) * 32, 0)], [(1000, attacker_script), (1000, attacker_script)])
    o1, o3 = (ob.outpoint(ob.sha256d(fund_legit), i) for i in range(2))
    o2, o4 = (ob.outpoint(ob.sha256d(fund_att), i) for i in range(2))
    legit_ctrl = [(ob.LEGIT, [2, 4])]
    att_ctrl = [(ob.ATTACKER, [2, 4])]
    add_ctrl = [(ob.LEGIT, [2, 4]), (ob.ATTACKER, [4])]

    packages, transitions, claims = {}, {}, {}
    for derivation in ("root", "b"):
        tag = "A" if derivation == "root" else "B"
        legit = genesis(f"{tag}-legit", derivation, o1, legit_ctrl, ob.LEGIT, LEGIT_SEALS)
        diff = genesis(f"{tag}-attacker-own-seal", derivation, o2, att_ctrl, ob.ATTACKER, ATTACKER_SEALS)
        same = genesis(f"{tag}-attacker-same-seal", derivation, o1, add_ctrl, ob.LEGIT, LEGIT_SEALS)
        # Same seal, attacker as transition controller bound to the legit seal
        # x-only key: only useful to an attacker who also stole that seal key.
        takeover = genesis(f"{tag}-attacker-takeover", derivation, o1, att_ctrl, ob.ATTACKER, LEGIT_SEALS)
        for p in (legit, diff, same, takeover):
            packages[p["name"]] = p
        t3 = transition(f"{tag}-attacker-activation", takeover, "attacker_controller", ob.ATTACKER,
                        o1, o3, att_ctrl, ob.ATTACKER, LEGIT_SEALS)
        transitions[t3["name"]] = t3
        t1 = transition(f"{tag}-legit-rotation", legit, "legit_controller", ob.LEGIT, o1, o3,
                        legit_ctrl, ob.LEGIT, LEGIT_SEALS)
        t2 = transition(f"{tag}-attacker-rotation", diff, "attacker_controller", ob.ATTACKER, o2, o4,
                        att_ctrl, ob.ATTACKER, ATTACKER_SEALS)
        transitions[t1["name"]] = t1
        transitions[t2["name"]] = t2
        for c in (claim(f"{tag}-attacker-claim-own-seal", diff, "attacker_controller", ob.ATTACKER,
                        "fixture:attacker-endpoint"),
                  claim(f"{tag}-attacker-claim-same-seal", same, "attacker_controller", ob.ATTACKER,
                        "fixture:attacker-endpoint"),
                  claim(f"{tag}-legit-claim", legit, "legit_controller", ob.LEGIT,
                        "fixture:artist-endpoint"),
                  claim(f"{tag}-attacker-claim-takeover", takeover, "attacker_controller", ob.ATTACKER,
                        "fixture:attacker-endpoint")):
            claims[c["name"]] = c

    g_legit = genesis("G-legit", "genesis", o1, legit_ctrl, ob.LEGIT, LEGIT_SEALS)
    g_diff = genesis("G-attacker-own-seal", "genesis", o2, att_ctrl, ob.ATTACKER, ATTACKER_SEALS)
    g_same = genesis("G-attacker-same-seal", "genesis", o1, add_ctrl, ob.LEGIT, LEGIT_SEALS)
    g_take = genesis("G-attacker-takeover", "genesis", o1, att_ctrl, ob.ATTACKER, LEGIT_SEALS)
    g_forge = genesis("G-attacker-names-legit-id", "genesis", o1, add_ctrl, ob.LEGIT, LEGIT_SEALS,
                      header_entity=bytes.fromhex(g_legit["entity_id"]))
    g_forge["entity_id"] = g_legit["entity_id"]  # what the attacker claims
    for p in (g_legit, g_diff, g_same, g_take, g_forge):
        packages[p["name"]] = p
    for t in (transition("G-legit-rotation", g_legit, "legit_controller", ob.LEGIT, o1, o3,
                         legit_ctrl, ob.LEGIT, LEGIT_SEALS),
              transition("G-attacker-activation", g_take, "attacker_controller", ob.ATTACKER, o1, o3,
                         att_ctrl, ob.ATTACKER, LEGIT_SEALS)):
        transitions[t["name"]] = t
    target = dict(g_same, entity_id=g_legit["entity_id"])  # attacker state, legit ID
    for c in (claim("G-legit-claim", g_legit, "legit_controller", ob.LEGIT, "fixture:artist-endpoint"),
              claim("G-attacker-claim-same-seal", g_same, "attacker_controller", ob.ATTACKER,
                    "fixture:attacker-endpoint"),
              claim("G-attacker-claim-targets-legit-id", target, "attacker_controller", ob.ATTACKER,
                    "fixture:attacker-endpoint")):
        c["package"] = c["package"] if c["name"] != "G-attacker-claim-targets-legit-id" else "G-attacker-same-seal"
        claims[c["name"]] = c

    def digest(name):
        return bytes.fromhex(packages[name]["consignment_genesis_digest"])

    commits = {
        "legit": commitment_tx(0xC1, digest("A-legit")),
        "attacker-own-seal": commitment_tx(0xC2, digest("A-attacker-own-seal")),
        "attacker-same-seal": commitment_tx(0xC3, digest("A-attacker-same-seal")),
        "unknown": commitment_tx(0xC4, cpo.tagged_hash("fixture-unknown", b"not a known genesis")),
    }
    return {
        "label": LABEL, "spec_commit": ob.SPEC_COMMIT, "network": NETWORK,
        "funding": {"legit": fund_legit.hex(), "attacker": fund_att.hex()},
        "seals": {"o1": o1.hex(), "o2": o2.hex(), "o3": o3.hex(), "o4": o4.hex()},
        "genesis_address_c": genesis_address(ob.ROOT).hex(),
        "packages": packages, "transitions": transitions, "claims": claims,
        "commitments": {k: v.hex() for k, v in commits.items()},
    }


# ---------------------------------------------------------------- evaluation


def view(fixture, *, spends=(), depth=1, commitments=(), funding_conf=10):
    """Explicit Bitcoin view. spends: (seal, transition, confirmations).
    commitments: (commit-name, height, position, confirmations)."""
    txs = {}
    for raw in fixture["funding"].values():
        txs[ob.sha256d(bytes.fromhex(raw)).hex()] = {"raw": raw, "confirmations": funding_conf}
    return {"source": "fixture-bitcoin-view (synthetic; no headers)", "best_block_hash": "11" * 32,
            "height": 200, "required_depth": depth, "transactions": txs,
            "spends": {fixture["seals"][s]: {"transition": t, "confirmations": c} for s, t, c in spends},
            "commitments": [{"raw": fixture["commitments"][n], "height": h, "position": p,
                             "confirmations": c} for n, h, p, c in commitments]}


def seal_matches(v, seal: bytes, st: dict) -> bool:
    creating = v["transactions"].get(seal[:32].hex())
    if creating is None or creating["confirmations"] < v["required_depth"]:
        return False
    outputs = ob.tx_parse(bytes.fromhex(creating["raw"]))["outputs"]
    vout = int.from_bytes(seal[32:], "little")
    c = [(k, s) for k, s in st["seal_policy"]["controller_seal_bindings"]]
    r = [(k, s) for k, s in st["seal_policy"]["recovery_seal_bindings"]]
    expected = bytes.fromhex(cpo.seal_output(c, r, ob.THRESHOLD, ob.DELAY)["script_pubkey"])
    return vout < len(outputs) and outputs[vout][1] == expected


def history(fixture, package, v, *, activation=False) -> str:
    """Walk genesis -> transitions against one view. Returns the history state."""
    payload = bytes.fromhex(package["genesis"])
    if evaluate_any(package) != "valid":
        return "INVALID"
    st = cpo.decode_payload(payload)["body"]["state"]
    state_id = bytes.fromhex(package["state_id"])
    sequence = 0
    while True:
        seal = st["next_seal"]
        if not seal_matches(v, seal, st):
            return "INCOMPLETE"
        spend = v["spends"].get(seal.hex())
        if spend is None:
            return "PENDING_ACTIVATION" if activation and sequence == 0 else "CURRENT"
        if spend["confirmations"] < v["required_depth"]:
            return "INCOMPLETE"
        t = fixture["transitions"][spend["transition"]]
        signer = bytes.fromhex(t["public_key"])
        ctrl = next((c for c in st["controllers"] if c["public_key"] == signer), None)
        valid = ctrl is not None and cpo.evaluate_signed_payload(
            bytes.fromhex(t["payload"]), t["signature"], signer, ob.TRANSITION_TAG,
            {"expected_network": NETWORK, "prior_sequence": sequence,
             "authorization": {"entity": bytes.fromhex(package["entity_id"]), "state": state_id,
                               "key_id": ctrl["key_id"], "role": 1, "public_key": signer,
                               "capabilities": ctrl["capabilities"]}}) == "valid"
        if not valid:
            return "SEAL_CLOSED_WITHOUT_VALID_TRANSITION"
        st = cpo.decode_payload(bytes.fromhex(t["payload"]))["body"]["state"]
        state_id = bytes.fromhex(t["state_id"])
        sequence += 1


def equivocation(fixture, evidence: list[str]) -> set[str]:
    """Option A: EntityIDs with two valid, different root-signed geneses."""
    seen: dict[str, set[str]] = {}
    for name in evidence:
        p = fixture["packages"][name]
        payload = bytes.fromhex(p["genesis"])
        if (cpo.crypto_verify(ob.ROOT, cpo.tagged_hash(ob.GENESIS_TAG, payload), p["signature"])
                and ob.evaluate_genesis(payload, p["signature"], "current") == "valid"):
            seen.setdefault(p["entity_id"], set()).add(p["consignment_genesis_digest"])
    return {entity for entity, digests in seen.items() if len(digests) > 1}


def c_winner(fixture, package, v, known: set[str], *, strict=True) -> str:
    """Option C: is this package's genesis the first confirmed commitment?

    `known` holds the digests of geneses this verifier actually holds; an
    earlier commitment to any other digest cannot be classified by it.
    """
    address = bytes.fromhex(fixture["genesis_address_c"])
    ordered = sorted((c for c in v["commitments"] if c["confirmations"] >= v["required_depth"]),
                     key=lambda c: (c["height"], c["position"]))
    for c in ordered:
        outputs = ob.tx_parse(bytes.fromhex(c["raw"]))["outputs"]
        if not any(script == address for _, script in outputs):
            continue
        digest = next((s[2:].hex() for _, s in outputs if s[:2] == b"\x6a\x20"), None)
        if digest == package["consignment_genesis_digest"]:
            return "WINNER"
        if digest in known or strict:
            return "LOSES" if digest in known else "INCOMPLETE: earlier unknown commitment"
    return "INCOMPLETE: no confirmed commitment"


def payout(fixture, option, claim_name, evidence, v, *, strict=True) -> str:
    """Would a relying party holding `evidence` accept this settlement claim?"""
    c = fixture["claims"][claim_name]
    package = fixture["packages"][c["package"]]
    claim_result = ob.evaluate_claim(package, c)
    if claim_result != "accepted":
        return "reject: " + claim_result
    state = history(fixture, package, v, activation=(option == "B+act"))
    if state != "CURRENT":
        return f"reject: history {state}"
    if option == "A" and package["entity_id"] in equivocation(fixture, evidence):
        return "reject: GENESIS_EQUIVOCATION"
    if option == "C":
        known = {fixture["packages"][n]["consignment_genesis_digest"] for n in evidence}
        known.add(package["consignment_genesis_digest"])
        won = c_winner(fixture, package, v, known, strict=strict)
        if won != "WINNER":
            return f"reject: commitment {won}"
    return "ACCEPT"


# -------------------------------------------------------------------- checks


def run_checks(fixture: dict) -> list[dict]:
    rows = []

    def row(option, case, label, expected, observed):
        rows.append({"option": option, "case": case, "check": label, "expected": expected,
                     "observed": observed, "pass": expected == observed})

    for kind, items, tag in (("genesis", fixture["packages"].values(), ob.GENESIS_TAG),
                             ("transition", fixture["transitions"].values(), ob.TRANSITION_TAG),
                             ("claim", fixture["claims"].values(), CLAIM_TAG)):
        for item in items:
            public = ob.ROOT if kind == "genesis" else bytes.fromhex(item["public_key"])
            payload = bytes.fromhex(item["genesis"] if kind == "genesis" else item["payload"])
            row("all", "sig", f"Rust verify {kind} {item['name']}", True,
                cpo.crypto_verify(public, cpo.tagged_hash(tag, payload), item["signature"]))

    base = view(fixture)
    legit_rot = {"A": view(fixture, spends=[("o1", "A-legit-rotation", 1)]),
                 "B": view(fixture, spends=[("o1", "B-legit-rotation", 1)])}
    both_rot = view(fixture, spends=[("o1", "A-legit-rotation", 1), ("o2", "A-attacker-rotation", 1)])
    full_c = [("legit", 101, 0, 99), ("attacker-own-seal", 150, 0, 50), ("attacker-same-seal", 150, 1, 50)]
    c_view = view(fixture, commitments=full_c)
    c_view_rot = view(fixture, spends=[("o1", "A-legit-rotation", 1)], commitments=full_c)
    c_missing = view(fixture, commitments=full_c[1:])
    c_front = view(fixture, commitments=[("attacker-own-seal", 100, 0, 100), ("legit", 101, 0, 99)])
    c_pending = view(fixture, depth=MAINNET_DEPTH, commitments=[("legit", 197, 0, 3)])
    c_grief = view(fixture, commitments=[("unknown", 90, 0, 110)] + full_c)

    # ---- Option A
    A = "A"
    row(A, 1, "attacker on own seal gets the legit EntityID", True,
        fixture["packages"]["A-attacker-own-seal"]["entity_id"] == fixture["packages"]["A-legit"]["entity_id"])
    row(A, 1, "verifier with attacker package only: payout", "ACCEPT",
        payout(fixture, A, "A-attacker-claim-own-seal", ["A-attacker-own-seal"], base))
    row(A, 1, "verifier holding both packages: payout", "reject: GENESIS_EQUIVOCATION",
        payout(fixture, A, "A-attacker-claim-own-seal", ["A-legit", "A-attacker-own-seal"], base))
    row(A, 1, "collateral: legit claim for a verifier holding both", "reject: GENESIS_EQUIVOCATION",
        payout(fixture, A, "A-legit-claim", ["A-legit", "A-attacker-own-seal"], base))
    row(A, 1, "after legit rotation, attacker own-seal history", "CURRENT",
        history(fixture, fixture["packages"]["A-attacker-own-seal"], legit_rot["A"]))
    row(A, 1, "attacker can rotate its own-seal history", "CURRENT",
        history(fixture, fixture["packages"]["A-attacker-own-seal"], both_rot))
    row(A, 2, "same seal, verifier with attacker package only: payout", "ACCEPT",
        payout(fixture, A, "A-attacker-claim-same-seal", ["A-attacker-same-seal"], base))
    row(A, 2, "same seal, after legit rotation: attacker history", "SEAL_CLOSED_WITHOUT_VALID_TRANSITION",
        history(fixture, fixture["packages"]["A-attacker-same-seal"], legit_rot["A"]))
    row(A, 3, "equivocation proof uses no Bitcoin data (holds in every view, survives reorgs)", True,
        equivocation(fixture, ["A-legit", "A-attacker-same-seal"])
        == {fixture["packages"]["A-legit"]["entity_id"]})

    # ---- Option B (as proposed)
    B = "B"
    row(B, 1, "attacker on own seal gets a different EntityID", True,
        fixture["packages"]["B-attacker-own-seal"]["entity_id"] != fixture["packages"]["B-legit"]["entity_id"])
    row(B, 1, "own-seal attacker claim cannot target the legit EntityID", True,
        fixture["packages"]["B-attacker-own-seal"]["entity_id"] != fixture["packages"]["B-legit"]["entity_id"])
    row(B, 2, "same seal, verifier with attacker package only: payout", "ACCEPT",
        payout(fixture, B, "B-attacker-claim-same-seal", ["B-attacker-same-seal"], base))
    row(B, 2, "same seal, after legit rotation: attacker history", "SEAL_CLOSED_WITHOUT_VALID_TRANSITION",
        history(fixture, fixture["packages"]["B-attacker-same-seal"], legit_rot["B"]))

    # ---- Option B + activation
    BA = "B+act"
    row(BA, 2, "before activation: attacker same-seal history", "PENDING_ACTIVATION",
        history(fixture, fixture["packages"]["B-attacker-same-seal"], base, activation=True))
    row(BA, 2, "before activation: legit history", "PENDING_ACTIVATION",
        history(fixture, fixture["packages"]["B-legit"], base, activation=True))
    row(BA, 2, "before activation: attacker payout", "reject: history PENDING_ACTIVATION",
        payout(fixture, BA, "B-attacker-claim-same-seal", ["B-attacker-same-seal"], base))
    row(BA, 2, "after activation: attacker same-seal payout",
        "reject: history SEAL_CLOSED_WITHOUT_VALID_TRANSITION",
        payout(fixture, BA, "B-attacker-claim-same-seal", ["B-attacker-same-seal"], legit_rot["B"]))
    row(BA, 2, "after activation: legit payout", "ACCEPT",
        payout(fixture, BA, "B-legit-claim", ["B-legit"], legit_rot["B"]))
    row(BA, 3, "no collateral: legit payout while attacker package also held", "ACCEPT",
        payout(fixture, BA, "B-legit-claim", ["B-legit", "B-attacker-same-seal"], legit_rot["B"]))

    stolen = view(fixture, spends=[("o1", "B-attacker-activation", 1)])
    row(BA, 4, "attacker also holds the seal key and activates first: attacker payout", "ACCEPT",
        payout(fixture, BA, "B-attacker-claim-takeover", ["B-attacker-takeover"], stolen))
    row(BA, 4, "attacker also holds the seal key and activates first: legit history",
        "SEAL_CLOSED_WITHOUT_VALID_TRANSITION",
        history(fixture, fixture["packages"]["B-legit"], stolen, activation=True))

    # ---- Option G (genesis-bound EntityID)
    G = "G"
    P = fixture["packages"]
    g_rot = view(fixture, spends=[("o1", "G-legit-rotation", 1)])
    g_take = view(fixture, spends=[("o1", "G-attacker-activation", 1)])
    row(G, 1, "attacker on own seal gets a different EntityID", True,
        P["G-attacker-own-seal"]["entity_id"] != P["G-legit"]["entity_id"])
    row(G, 2, "attacker on the SAME seal gets a different EntityID", True,
        P["G-attacker-same-seal"]["entity_id"] != P["G-legit"]["entity_id"])
    row(G, 2, "genesis whose header names the legit EntityID is invalid", "INVALID",
        history(fixture, P["G-attacker-names-legit-id"], base))
    row(G, 2, "attacker claim targeting the legit EntityID, attacker package only",
        "reject: rejected: signer is not authorized by the stated fixture state",
        payout(fixture, G, "G-attacker-claim-targets-legit-id", ["G-attacker-same-seal"], base))
    row(G, 3, "legit payout immediately, no activation step", "ACCEPT",
        payout(fixture, G, "G-legit-claim", ["G-legit"], base))
    row(G, 3, "no collateral: legit payout while attacker package also held", "ACCEPT",
        payout(fixture, G, "G-legit-claim", ["G-legit", "G-attacker-same-seal"], base))
    row(G, 3, "after legit rotation: attacker same-seal history (its own ID)",
        "SEAL_CLOSED_WITHOUT_VALID_TRANSITION", history(fixture, P["G-attacker-same-seal"], g_rot))
    row(G, 4, "attacker holds root AND seal key, spends first: legit history",
        "SEAL_CLOSED_WITHOUT_VALID_TRANSITION", history(fixture, P["G-legit"], g_take))
    row(G, 4, "...and the attacker still cannot claim the legit EntityID",
        "reject: rejected: signer is not authorized by the stated fixture state",
        payout(fixture, G, "G-attacker-claim-targets-legit-id", ["G-attacker-same-seal"], g_take))
    row(G, 4, "seal-creating tx at 3 of 6 mainnet confirmations: legit history", "INCOMPLETE",
        history(fixture, P["G-legit"], view(fixture, depth=MAINNET_DEPTH, funding_conf=3)))

    # ---- Option C (a verifier normally holds only the package it was shown)
    C = "C"
    only = lambda name: [name]  # noqa: E731
    both = ["A-legit", "A-attacker-own-seal", "A-attacker-same-seal"]
    row(C, 1, "complete view, strict, attacker package only: own-seal payout",
        "reject: commitment INCOMPLETE: earlier unknown commitment",
        payout(fixture, C, "A-attacker-claim-own-seal", only("A-attacker-own-seal"), c_view))
    row(C, 1, "complete view, strict, verifier holds both: own-seal payout", "reject: commitment LOSES",
        payout(fixture, C, "A-attacker-claim-own-seal", both, c_view))
    row(C, 1, "complete view, LAX, attacker package only: own-seal payout", "ACCEPT",
        payout(fixture, C, "A-attacker-claim-own-seal", only("A-attacker-own-seal"), c_view, strict=False))
    row(C, 2, "complete view, strict, attacker package only: same-seal payout",
        "reject: commitment INCOMPLETE: earlier unknown commitment",
        payout(fixture, C, "A-attacker-claim-same-seal", only("A-attacker-same-seal"), c_view))
    row(C, 3, "complete view: legit payout", "ACCEPT",
        payout(fixture, C, "A-legit-claim", only("A-legit"), c_view))
    row(C, 3, "after legit rotation: own-seal attacker history still CURRENT (needs commitment check)",
        "CURRENT", history(fixture, fixture["packages"]["A-attacker-own-seal"], c_view_rot))
    row(C, 4, "indexer view missing the legit commitment: attacker payout (strict)", "ACCEPT",
        payout(fixture, C, "A-attacker-claim-own-seal", only("A-attacker-own-seal"), c_missing))
    row(C, 4, "front-run (attacker commits first), strict, legit package only: legit payout",
        "reject: commitment INCOMPLETE: earlier unknown commitment",
        payout(fixture, C, "A-legit-claim", only("A-legit"), c_front))
    row(C, 4, "front-run, verifier holds both: legit payout", "reject: commitment LOSES",
        payout(fixture, C, "A-legit-claim", both, c_front))
    row(C, 4, "front-run, attacker package only: attacker payout", "ACCEPT",
        payout(fixture, C, "A-attacker-claim-own-seal", only("A-attacker-own-seal"), c_front))
    row(C, 4, "legit commitment at 3 of 6 mainnet confirmations: legit payout",
        "reject: commitment INCOMPLETE: no confirmed commitment",
        payout(fixture, C, "A-legit-claim", only("A-legit"), c_pending))
    row(C, 4, "earlier junk commitment (no root needed), strict: legit payout",
        "reject: commitment INCOMPLETE: earlier unknown commitment",
        payout(fixture, C, "A-legit-claim", only("A-legit"), c_grief))
    row(C, 4, "earlier junk commitment, lax: legit payout", "ACCEPT",
        payout(fixture, C, "A-legit-claim", only("A-legit"), c_grief, strict=False))
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
        print(f"{'ok  ' if r['pass'] else 'FAIL'} [{r['option']}:{r['case']}] {r['check']}: observed={r['observed']}")
    failed = [r for r in rows if not r["pass"]]
    print(f"genesis-options: {len(rows) - len(failed)}/{len(rows)} expectations met")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
