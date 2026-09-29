# ADR-0009 — Scoped Genesis Freeze

**Status:** Accepted, 2026-09-28 (maintainer decision). It builds on accepted
[ADR-0008](0008-genesis-bound-entity-id.md) as merged in `0ef16c2`.

## Context

The first mainnet O2A identity is intended to be created live on stage as
"block 0". Its genesis and first self-attested `official_name` claim must
remain verifiable indefinitely even though the complete protocol, RGB program,
dependency lock, recovery flow, discovery system, and other signed objects are
still Draft v0.1.

Freezing all of Draft v0.1 would overstate the implementation evidence. Freezing
too little would allow a later serialization, identifier, derivation, or seal
change to invalidate the first identity. This decision therefore isolates the
smallest byte and verification surface needed by one genesis plus one
`official_name` claim.

The current schema also lets `state_id` be read as an RGB-defined identifier.
That is unsafe for the scoped freeze: the block-0 RGB contract may need to be
re-issued under the final RGB release before its first transition, and an RGB
state identifier could then change even when the O2A genesis bytes do not.

## Decision

### 1. O2A-native state ID

O2A defines:

```text
state_id = TaggedHash(
  "O2A/v0.1/state-id",
  entity_id || resulting_state
)
```

`entity_id` is the ADR-0008 EntityID recomputed from the history's canonical
genesis payload. `resulting_state` is the exact canonical resulting-state byte
sequence, beginning with `sequence` and ending with `profile_commitment`, that
the genesis, identity transition, or recovery authorization establishes.

The rule is uniform and signer-independent. In particular, multiple recovery
signers have different common headers and `signing_key_id` values but compute
one state ID when they authorize the same resulting state for the same entity.
The rejected construction `TaggedHash("O2A/v0.1/state-id", object_payload)`
would instead create multiple IDs for that one recovery state and MUST NOT be
used.

The state ID is independent of an RGB contract ID, schema ID, assignment ID,
consignment encoding, commitment carrier, operation encoding, and signatures.
A verifier MUST recompute it and MUST reject any `authorizing_state`,
`previous_state`, package field, or display field that names a different
value. This construction is not circular: the genesis EntityID does not
contain state 0's ID, and every successor resulting state names only the prior
state ID.

### 2. Frozen set

If this ADR is accepted, the following Draft v0.1 subset becomes the
**FROZEN genesis format**. These bytes and rules are immutable for every
frozen-format identity, including block 0.

1. **Primitive grammar used by genesis and `official_name`:** little-endian
   `u8`, `u16`, `u32`, and `u64`; fixed 32-byte `hash32`, `entity_id`,
   `state_id`, `key_id`, and `xonly`; fixed 64-byte `signature64`; `bytes`,
   UTF-8 `text`, `option<T>`, `list<T>`, and internal-byte-order `outpoint`,
   with the O2A-CANON-1 bounds, ordering, duplicate, and rejection rules.
2. **Protocol and network values:** protocol version `u16(1)`, mainnet network
   byte `u8(0)`, and mainnet Route B coin type `0'`.
3. **Common signed header:** its field order and encoding, the all-zero genesis
   `signer_entity`, absent genesis `authorizing_state`, and the requirement for
   every non-genesis object to name the genesis-derived EntityID and a
   recomputed O2A state ID.
4. **Entity genesis:** object type 1; entity-type encoding; root x-only key;
   and the complete `common_header || entity_type || root_xonly ||
   resulting_state` payload.
5. **Initial resulting state and nested values:** sequence 0; absent
   `previous_state` and `previous_seal`; `next_seal`; sorted controllers;
   recovery policy; seal policy; optional custodian; ACTIVE lifecycle value 1;
   absent custody acceptance and profile commitment. The exact controller,
   recovery-policy, seal-binding, sorting, threshold, delay, and key-separation
   encodings are included.
6. **Key roles and capabilities touched by this subset:** role 0 root, role 1
   controller, role 2 recovery, and role 4 seal; capability 1 entity genesis,
   capability 2 identity transition as committed in the initial controller,
   and capability 4 claim. Freezing capability 2 as an initial-state number
   does not freeze the transition payload or permit a transition yet.
7. **Identifiers and tags:** the exact tagged-hash construction and the UTF-8
   tags `O2A/v0.1/wallet-root`, `O2A/v0.1/key-id`,
   `O2A/v0.1/recovery-policy`, `O2A/v0.1/entity-id`,
   `O2A/v0.1/state-id`, `O2A/v0.1/entity-genesis`, and
   `O2A/v0.1/claim`. The BIP341 `TapLeaf`, `TapBranch`, and `TapTweak` tags
   used by seal output construction, and the BIP340 `BIP0340/aux`,
   `BIP0340/nonce`, and `BIP0340/challenge` tags used by the signing and
   verification algorithm, are included as external cryptographic dependencies.
8. **ADR-0008 EntityID:** the tagged hash of the exact canonical genesis
   payload, including the zero genesis signer.
9. **State ID:** the O2A-native `entity_id || resulting_state` rule in
   Decision 1. Freezing it freezes only the already-frozen EntityID and
   resulting-state encodings; it does not freeze transition or recovery
   payloads.
10. **Seal output:** the NUMS internal key, controller `pk` leaves, delayed
    threshold recovery leaf, lexicographic key order, TapLeaf hashing,
    left-to-right pairwise tree reduction with an odd final node carried
    unchanged, BIP341 sibling sorting, TapTweak, and P2TR scriptPubKey.
11. **Confirmation rule:** mainnet identity-anchor depth 6 and ADR-0008
    `PENDING_CONFIRMATION` semantics for every seal-creating transaction named
    by the valid history, including the RBF-invalidates and CPFP-preserves
    rules.
12. **Official-name claim:** object type 4, controller role 1, capability 4,
    claim-domain signature, exact claim payload field order, self-issued
    subject, exact predicate text `official_name`, bytes value, nonce, and
    optional context, supersedes, and checkpoint encodings.
13. **Route B for the frozen roles:** BIP39 seed input, BIP85 BIP32-XPRV
    application `32'`, O2A index `998536622'`, `xprv_o2a`, fully hardened
    `m/coin'/entity'/role'/index'` derivation, mainnet `coin = 0'`, entity
    allocation rule, and roles 0, 1, 2, and 4 including their no-reuse rules.

The frozen set includes BIP340 verification and SHA-256 as used by those exact
rules. It does not make the published conformance-vector secrets safe for
funds.

### 3. Not frozen

This decision does **not** freeze or adopt:

- the RGB program, codex, schema bytes, dependency lock, or Bitcoin commitment
  carrier;
- identity-transition payloads, recovery-authorization payloads, recovery
  execution, or operations 2 (recovery-policy change) and 4 (custody transfer);
- attestations, challenges, observations, manifests, proof packages, or claim
  predicates other than exact `official_name`; or
- discovery, publication, restore, Pubky, or Nostr behavior.

No transition may be made from a frozen-format identity until the RGB stack,
program, and commitment carrier are final and adopted. Before its first
transition, an RGB contract for that identity MAY be re-issued under the final
RGB release only with the exact same O2A genesis bytes and same genesis seal.
That re-issuance does not change the EntityID or O2A state 0 ID and MUST NOT be
presented as a new O2A genesis.

### 4. Compatibility promise

Conforming verifiers MUST validate frozen-format genesis payloads and their
`official_name` claims indefinitely. A future protocol change MUST use a new
version, a new tagged-hash tag, or both. It MUST NOT reinterpret frozen bytes,
change their identifier results, or require their owners to remint an identity.

Unknown future versions remain unsupported rather than inheriting v0.1
semantics. Compatibility means preserving verification, not treating every
future feature as available to a frozen identity.

### 5. Enforcement

`tests/vectors/genesis-freeze-v0.1.json` is the CC0 manifest of every frozen
mainnet vector output and the SHA-256 of each output. It uses only the published
unsafe Route B seed and derives entity 0 under mainnet coin type `0'`.

`tests/vectors/check_genesis_freeze.py` rebuilds those outputs, checks every
manifest hash, verifies the genesis and claim signatures, cross-checks EntityID
and state ID with the locked Rust checker, and fails on any byte change. It is
part of the standard vector suite. The vector is not a real identity and its
keys MUST NEVER receive funds or authorize a live identity.

## Consequences

- Block 0 can retain stable O2A identity and claim bytes while RGB integration
  remains replaceable before the first transition.
- The scoped promise is narrower than a v0.1 protocol freeze and does not close
  Phase 0 as a whole.
- Acceptance would close the mainnet derivation-format gate only for roles 0,
  1, 2, and 4 used by genesis, and the canonical genesis/official-name vector
  gate. It would not close the RGB, transition, recovery execution,
  restore/discovery, dependency-lock, custody, or broader conformance gates.
- Before acceptance and before minting, the maintainer must review the fixed
  vector manifest and its independent validation output.
