# Option B adversarial fixtures (disposable)

**Test-only. Not normative. Not frozen. Not a decision to adopt Option B.**
Pinned spec: `c7b08716d017d1f6125e6a728fb098673a09d433`. CC0-1.0, like the
other files in `tests/vectors/`.

Option B is the candidate EntityID rule under test:

```text
EntityID_B = TaggedHash("O2A/v0.1/entity-id",
                        u16(1) || network || root_xonly || genesis_seal)
```

The preimage is 71 bytes: `01 00` (version, little-endian), one network byte,
the 32-byte root x-only key, then the canonical outpoint (32 serialized txid
bytes followed by a little-endian `u32` vout). The spec as written uses only
the first 35 bytes.

## What runs

`check_option_b.py` builds every fixture deterministically and evaluates it with
the repository's own code: `evaluate_signed_payload`, `decode_payload`,
`valid_state`, `seal_output` and `identity_history_outcome` from
`check_protocol_objects.py`, and `build_claim`/`evaluate_name_claim` from
`check_vectors.py`. The only substitution is the EntityID derivation, swapped
for the Option B candidate while a genesis is evaluated. Signatures are
verified by the Rust crypto checker, and the Python BIP340 signer must
reproduce the Rust signer's bytes.

```bash
docker compose --file dev/compose.yaml --profile tools run --rm toolchain \
  bash -lc 'python3 tests/vectors/option-b/check_option_b.py'
```

`--emit` regenerates `option-b-v0.1.json`. Check mode fails if the generator no
longer reproduces the file byte for byte.

## How to read "expected"

Each expectation records what the **pinned spec does**, including the
vulnerability. For example, "attacker claim vs attacker package only:
accepted" passes because the attack succeeds. A future spec fix must flip those
rows deliberately.

## Cases

1. **Different seals.** One root, seals O1 and O2 → distinct EntityIDs. A
   genesis on O2 claiming E(O1) is rejected, and so is a claim for E(O1) from
   O2's history. Baseline: under the spec as written both geneses share one
   EntityID.
2. **Same seal.** One root, one seal O1, two geneses:
   - (a) adds a claim-only controller. Capability 4 without capability 2 needs
     no seal binding, so the seal policy is byte-identical.
   - (b) replaces the transition controller but keeps its seal x-only key, so
     the script is identical.
   Both are valid with the same EntityID and are CURRENT against the same
   Bitcoin view as the legitimate history.
3. **Attacker payout claim.** A `settlement_endpoint` claim from the (a)
   attacker controller is accepted against the attacker package alone and
   rejected against the legitimate one. After the legitimate controller closes
   O1, the attacker history becomes `SEAL_CLOSED_WITHOUT_VALID_TRANSITION`.
4. **Commitment and reorg boundary.**
   - A missing consignment genesis digest gives INCOMPLETE; a mismatched one
     gives INVALID.
   - If the seal-creating transaction is reorged out or replaced, the old
     package becomes INCOMPLETE, and the replacement outpoint yields a
     different EntityID.
   - A **candidate property model (not spec)**, where the genesis closes a
     bootstrap seal, rejects the same-seal attacker. It also shows that model's
     limits: it depends on who holds the bootstrap key, it is pending below the
     required depth, and fee bumping keeps the EntityID.
   - A circularity demonstration shows that naming the committing transaction
     inside the genesis never reaches a fixed point.

## Limitations

- Transactions are synthetic legacy serializations. They have real txids but
  no blocks, headers or merkle proofs, so all full-chain results are
  **UNPROVEN**.
- The RGB state ID is RGB-defined and unbound in the spec. The fixtures use
  the genesis commitment digest as a stand-in.
- The concrete RGB program and genesis commitment carrier are unbound. The
  "consignment genesis digest" is modelled as a field, and the candidate
  model's OP_RETURN is a placeholder carrier.
- The seal-creating transaction is required at identity-anchor depth. The spec
  requires its inclusion proof but states no depth for it (see findings).
- Controller seal bindings cover single-transition-controller policies only.
