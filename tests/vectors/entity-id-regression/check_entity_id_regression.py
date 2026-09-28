#!/usr/bin/env python3
"""Regression suite for ADR-0008 (genesis-bound EntityID). CC0-1.0.

Every expectation below is the behavior ADR-0008 REQUIRES. While ADR-0008 is
Proposed, the RULE SEAM calls the candidate implementation. On acceptance,
point the seam at the normative implementation in check_protocol_objects.py
and leave every expectation unchanged: if an expectation must change, the
spec change is not the one ADR-0008 describes.

Negative controls re-run the attack rows under the previous rules (root-only
EntityID, and Option B) and require them to ADMIT the attacks. A suite that
cannot tell the old rules from the new one proves nothing.

Test-only fixtures: published unsafe BIP340 keys; synthetic transactions
(real txids, no headers); full-chain behavior is out of scope here.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "option-b"))
sys.path.insert(0, str(HERE.parent / "genesis-options"))

import check_protocol_objects as cpo  # noqa: E402
import check_option_b as ob  # noqa: E402
import check_genesis_options as go  # noqa: E402
import legacy_evaluator as legacy  # noqa: E402

FIXTURE_PATH = HERE / "entity-id-regression-v0.1.json"
ENTITY_TAG = "O2A/v0.1/entity-id"
MAINNET_DEPTH = 6

# =============================== RULE SEAM ===============================
# ADR-0008 normative implementation. Existing expectations remain unchanged.
RULE = "normative:check_protocol_objects.py:ADR-0008"


def entity_id_of(genesis_payload: bytes) -> bytes:
    return cpo.entity_id(genesis_payload)


def genesis_valid(package: dict) -> bool:
    payload = bytes.fromhex(package["genesis"])
    return cpo.evaluate_signed_payload(
        payload,
        package["signature"],
        ob.ROOT,
        ob.GENESIS_TAG,
        {"expected_network": go.NETWORK, "authorization": None},
    ) == "valid"


def identity_state(fixture: dict, package: dict, view: dict) -> str:
    """ADR-0008 Decision 4: PENDING_CONFIRMATION below depth, INCOMPLETE if absent."""
    if not genesis_valid(package):
        return "INVALID"
    genesis_payload = bytes.fromhex(package["genesis"])
    state = cpo.decode_payload(genesis_payload)["body"]["state"]
    state_id = bytes.fromhex(package["state_id"])
    sequence = 0
    creator_confirmations: list[int | None] = []
    while True:
        seal = state["next_seal"]
        creating = view["transactions"].get(seal[:32].hex())
        if creating is None:
            return "INCOMPLETE"
        if not _seal_script_matches(creating, seal, state):
            return "INVALID"
        creator_confirmations.append(creating["confirmations"])
        if creating["confirmations"] < view["required_depth"]:
            return "PENDING_CONFIRMATION"
        spend = view["spends"].get(seal.hex())
        if spend is None:
            return cpo.identity_history_outcome(
                bitcoin_view_source=view["source"],
                best_block_hash=bytes.fromhex(view["best_block_hash"]),
                observed_height=view["height"],
                seal_observation="unspent",
                spend_proof=False,
                spend_confirmations=0,
                required_depth=view["required_depth"],
                valid_transition=False,
                seal_creating_confirmations=creator_confirmations,
            )["state"]
        if spend["confirmations"] < view["required_depth"]:
            return "INCOMPLETE"
        transition = fixture["transitions"][spend["transition"]]
        signer = bytes.fromhex(transition["public_key"])
        controller = next(
            (item for item in state["controllers"] if item["public_key"] == signer),
            None,
        )
        valid = controller is not None and cpo.evaluate_signed_payload(
            bytes.fromhex(transition["payload"]),
            transition["signature"],
            signer,
            ob.TRANSITION_TAG,
            {
                "expected_network": go.NETWORK,
                "genesis_payload": genesis_payload,
                "prior_sequence": sequence,
                "authorization": {
                    "entity": bytes.fromhex(package["entity_id"]),
                    "state": state_id,
                    "key_id": controller["key_id"] if controller else bytes(32),
                    "role": 1,
                    "public_key": signer,
                    "capabilities": controller["capabilities"] if controller else [],
                },
            },
        ) == "valid"
        if not valid:
            return cpo.identity_history_outcome(
                bitcoin_view_source=view["source"],
                best_block_hash=bytes.fromhex(view["best_block_hash"]),
                observed_height=view["height"],
                seal_observation="spent",
                spend_proof=True,
                spend_confirmations=spend["confirmations"],
                required_depth=view["required_depth"],
                valid_transition=False,
                seal_creating_confirmations=creator_confirmations,
            )["state"]
        state = cpo.decode_payload(bytes.fromhex(transition["payload"]))["body"]["state"]
        state_id = bytes.fromhex(transition["state_id"])
        sequence += 1
# ========================================================================


def _seal_script_matches(creating: dict, seal: bytes, state: dict) -> bool:
    outputs = ob.tx_parse(bytes.fromhex(creating["raw"]))["outputs"]
    vout = int.from_bytes(seal[32:], "little")
    expected = bytes.fromhex(
        cpo.seal_output(
            state["seal_policy"]["controller_seal_bindings"],
            state["seal_policy"]["recovery_seal_bindings"],
            ob.THRESHOLD,
            ob.DELAY,
        )["script_pubkey"]
    )
    return vout < len(outputs) and outputs[vout][1] == expected


def normative_claim_valid(package: dict, claim: dict) -> bool:
    signer = bytes.fromhex(claim["public_key"])
    auth = ob.authorization(package, signer)
    if auth is None:
        return False
    auth["genesis_payload"] = package["genesis"]
    accepted, _ = ob.cv.evaluate_name_claim(
        bytes.fromhex(claim["payload"]),
        claim["signature"],
        claim["public_key"],
        go.NETWORK,
        auth,
    )
    return accepted


def payout(
    fixture: dict,
    claim_name: str,
    package_name: str,
    view: dict,
    state_fn=identity_state,
    claim_fn=normative_claim_valid,
) -> str:
    c = fixture["claims"][claim_name]
    package = fixture["packages"][package_name]
    if not claim_fn(package, c):
        return "REJECT"
    return "ACCEPT" if state_fn(fixture, package, view) == "CURRENT" else "REJECT"


def build() -> dict:
    fixture = go.build()
    legit = fixture["packages"]["G-legit"]
    # Mutation: same root, seal and state, entity type ARTIST -> VENUE.
    payload = bytearray(bytes.fromhex(legit["genesis"]))
    payload[73:75] = cpo.u16(4)
    mutated = bytes(payload)
    fixture["packages"]["G-mutated-entity-type"] = dict(
        legit, name="G-mutated-entity-type", genesis=mutated.hex(),
        signature=ob.sign("root", ob.GENESIS_TAG, mutated),
        entity_id=entity_id_of(mutated).hex(),
        state_id=ob.placeholder_state_id(mutated).hex(),
        consignment_genesis_digest=cpo.tagged_hash(ob.GENESIS_TAG, mutated).hex())
    fixture["label"] = "ADR-0008 regression fixtures: test-only, not normative until accepted"
    return fixture


def run(fixture: dict) -> list[dict]:
    rows = []
    P = fixture["packages"]

    def row(group, label, expected, observed):
        rows.append({"group": group, "check": label, "expected": expected,
                     "observed": observed, "pass": expected == observed})

    base = go.view(fixture)
    rot = go.view(fixture, spends=[("o1", "G-legit-rotation", 1)])
    take = go.view(fixture, spends=[("o1", "G-attacker-activation", 1)])

    # -- R1 derivation
    legit_payload = bytes.fromhex(P["G-legit"]["genesis"])
    row("R1", "EntityID is TaggedHash(entity-id, genesis payload)",
        entity_id_of(legit_payload).hex(), P["G-legit"]["entity_id"])
    row("R1", "genesis header signer_entity is 32 zero bytes", bytes(32).hex(),
        cpo.decode_payload(legit_payload)["header"]["signer_entity"].hex())
    row("R1", "determinism: rebuilding the genesis reproduces the EntityID", P["G-legit"]["entity_id"],
        go.build()["packages"]["G-legit"]["entity_id"])
    row("R1", "any payload change (entity type) changes the EntityID", True,
        P["G-mutated-entity-type"]["entity_id"] != P["G-legit"]["entity_id"])
    row("R1", "mutated genesis is itself valid (a distinct identity)", True,
        genesis_valid(P["G-mutated-entity-type"]))

    # -- R2 genesis validity
    row("R2", "legit genesis valid", True, genesis_valid(P["G-legit"]))
    row("R2", "genesis naming a non-zero signer_entity is invalid", "INVALID",
        identity_state(fixture, P["G-attacker-names-legit-id"], base))

    # -- R3 uniqueness under a stolen root
    row("R3", "different seal -> different EntityID", True,
        P["G-attacker-own-seal"]["entity_id"] != P["G-legit"]["entity_id"])
    row("R3", "same seal, added claim-only controller -> different EntityID", True,
        P["G-attacker-same-seal"]["entity_id"] != P["G-legit"]["entity_id"])
    row("R3", "same seal, re-keyed controller -> different EntityID", True,
        P["G-attacker-takeover"]["entity_id"] != P["G-legit"]["entity_id"])
    row("R3", "attacker claim naming the legit EntityID: attacker package only", "REJECT",
        payout(fixture, "G-attacker-claim-targets-legit-id", "G-attacker-same-seal", base))
    row("R3", "attacker claim naming the legit EntityID: legit package", "REJECT",
        payout(fixture, "G-attacker-claim-targets-legit-id", "G-legit", base))
    row("R3", "stolen root + seal key, attacker spends first: legit history",
        "SEAL_CLOSED_WITHOUT_VALID_TRANSITION", identity_state(fixture, P["G-legit"], take))
    row("R3", "...and the legit EntityID is still not obtainable", "REJECT",
        payout(fixture, "G-attacker-claim-targets-legit-id", "G-attacker-same-seal", take))

    # -- R4 lifecycle keeps the EntityID
    row("R4", "legit payout at genesis (no activation step)", "ACCEPT",
        payout(fixture, "G-legit-claim", "G-legit", base))
    row("R4", "rotation keeps the EntityID and the history CURRENT", "CURRENT",
        identity_state(fixture, P["G-legit"], rot))
    row("R4", "transition names the genesis-bound EntityID", P["G-legit"]["entity_id"],
        cpo.decode_payload(bytes.fromhex(fixture["transitions"]["G-legit-rotation"]["payload"]))
        ["header"]["signer_entity"].hex())
    row("R4", "after legit rotation: same-seal attacker history",
        "SEAL_CLOSED_WITHOUT_VALID_TRANSITION", identity_state(fixture, P["G-attacker-same-seal"], rot))

    # -- R5 PENDING_CONFIRMATION
    row("R5", "genesis seal-creating tx at 3 of 6 confirmations", "PENDING_CONFIRMATION",
        identity_state(fixture, P["G-legit"], go.view(fixture, depth=MAINNET_DEPTH, funding_conf=3)))
    row("R5", "genesis seal-creating tx at 6 of 6 confirmations", "CURRENT",
        identity_state(fixture, P["G-legit"], go.view(fixture, depth=MAINNET_DEPTH, funding_conf=6)))
    absent = go.view(fixture)
    absent["transactions"] = {}
    row("R5", "genesis seal-creating tx absent from the view", "INCOMPLETE",
        identity_state(fixture, P["G-legit"], absent))
    row("R5", "payout while PENDING_CONFIRMATION", "REJECT",
        payout(fixture, "G-legit-claim", "G-legit", go.view(fixture, depth=MAINNET_DEPTH, funding_conf=3)))
    row("R5", "successor seal creator below depth is PENDING_CONFIRMATION",
        "PENDING_CONFIRMATION",
        cpo.identity_history_outcome(
            bitcoin_view_source="fixture-bitcoin-view",
            best_block_hash=bytes.fromhex("11" * 32),
            observed_height=200,
            seal_observation="unspent",
            spend_proof=False,
            spend_confirmations=0,
            required_depth=MAINNET_DEPTH,
            valid_transition=False,
            seal_creating_confirmations=[10, 3],
        )["state"])

    # -- N negative controls: the previous rules must admit the attacks
    def root_only_state(fx, package, v):
        return legacy.identity_state(fx, package, v, "root")

    def option_b_state(fx, package, v):
        return legacy.identity_state(fx, package, v, "b")
    row("N", "root-only rule admits a same-seal attacker payout", "ACCEPT",
        payout(fixture, "A-attacker-claim-same-seal", "A-attacker-same-seal", base,
               root_only_state, legacy.claim_valid))
    row("N", "root-only rule admits an own-seal attacker payout", "ACCEPT",
        payout(fixture, "A-attacker-claim-own-seal", "A-attacker-own-seal", base,
               root_only_state, legacy.claim_valid))
    row("N", "Option B admits a same-seal attacker payout", "ACCEPT",
        payout(fixture, "B-attacker-claim-same-seal", "B-attacker-same-seal", base,
               option_b_state, legacy.claim_valid))
    row("N", "root-only rule gives both seals the same EntityID", True,
        P["A-attacker-own-seal"]["entity_id"] == P["A-legit"]["entity_id"])
    return rows


def main() -> int:
    if "--emit" in sys.argv:
        FIXTURE_PATH.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {FIXTURE_PATH.name}")
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    if fixture != json.loads(json.dumps(build())):
        print("fixture is not reproduced by the generator", file=sys.stderr)
        return 1
    rows = run(fixture)
    for r in rows:
        print(f"{'ok  ' if r['pass'] else 'FAIL'} [{r['group']}] {r['check']}: observed={r['observed']}")
    failed = [r for r in rows if not r["pass"]]
    print(f"entity-id-regression ({RULE}): {len(rows) - len(failed)}/{len(rows)} expectations met")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
