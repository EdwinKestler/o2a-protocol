# ADR-0008 — Genesis-Bound EntityID

**Status:** Proposed, 2026-09-27. Amends [ADR-0005](0005-bitcoin-rooted-self-custodial-identity.md).
Until this ADR is accepted, it changes no normative specification, and nothing
here freezes an encoding or claims readiness for production.

## Context

Draft v0.1 (`c7b0871`) derives the EntityID from the root key alone:

```text
EntityID = TaggedHash("O2A/v0.1/entity-id", u16(1) || network || root_xonly)
```

After genesis, every authority comes from keys listed in the validated state,
and the root cannot fill a controller role. The root's only remaining power is
signing another genesis for the same EntityID. Adversarial fixtures
(`tests/vectors/option-b/`, `tests/vectors/genesis-options/`), executed with
the repository's own evaluators and the Rust verifier, show that a root holder
can:

- sign a second valid genesis for the same EntityID on a seal it funds itself;
- sign a second valid genesis on the **same** seal, either by adding a
  claim-only controller (capability 4 needs no seal binding) or by re-keying
  the controller while keeping the seal x-only key (the seal script depends
  only on seal keys). The seal policy and scriptPubKey stay byte-identical;
- have both histories evaluate as `CURRENT` against the same Bitcoin view; and
- get a `settlement_endpoint` claim from its own controller accepted by a
  verifier that holds only the attacker's package.

ADR-0005 therefore overstates one property: lifecycle non-equivocation
inherits Bitcoin security only after genesis and within one history.

Five candidate rules were run against the same attacks:

| Rule | Stolen root, own seal | Stolen root, same seal | Artist harmed when a verifier holds both packages | Stolen root plus seal key | Extra cost |
|---|---|---|---|---|---|
| A: root-only ID plus equivocation proof | Attacker paid | Attacker paid | Yes: both histories rejected | Attacker paid | none |
| B: ID = H(root, genesis seal) | Different ID | **Attacker paid** | No | Attacker paid | none |
| B+activation: B, plus PENDING until the genesis seal is spent | Different ID | Rejected | No | **Attacker gets the artist's ID** | 2nd tx, activation wait |
| C: first commitment at a root-derived address | Rejected only in strict mode, as INCOMPLETE | Rejected (strict) | No | Front-running wins | 2nd tx, a permanent UTXO, a complete indexer; keyless denial of service |
| **G: ID = H(genesis payload)** | Different ID | **Different ID** | No | Artist's seal closed (denial of service); **artist's ID never obtained** | none |

## Decision

1. **EntityID derivation.**

   ```text
   EntityID = TaggedHash("O2A/v0.1/entity-id", genesis_payload)
   ```

   `genesis_payload` is the exact O2A-CANON-1 entity-genesis payload, without
   its signature. The tagged-hash construction is the one already defined in
   canonical encoding. The genesis contains the protocol version, network,
   entity type, `root_xonly`, genesis seal (`next_seal`) and complete initial
   state. The EntityID therefore commits to all of them.

2. **No self-reference.** In the genesis payload, `signer_entity` MUST be 32
   zero bytes; any other value is invalid. `signing_key_id` still identifies
   the root, and the root still signs the genesis. Every other object MUST name
   the EntityID computed from its own history's genesis. A verifier recomputes
   the EntityID from the genesis it validated and never trusts an ID supplied
   alongside the package.

3. **Uniqueness.**
   - Identical genesis payloads give identical EntityIDs.
   - Any byte difference, including a different seal or controller set, gives
     a different EntityID.
   - Each EntityID therefore has exactly one genesis, up to SHA-256 collision
     resistance.
   - The genesis seal is single-use, so at most one history can continue past
     its first transition. Every other history on that seal becomes
     `SEAL_CLOSED_WITHOUT_VALID_TRANSITION` once the seal is spent.

4. **PENDING_CONFIRMATION.** A new identity-history outcome:
   - `CURRENT` requires every seal-creating transaction named by the history
     (genesis seal included) to be at the identity-anchor confirmation depth
     in the evaluation context's Bitcoin view (1 on test networks, 6 on
     mainnet).
   - If such a transaction is present but below depth, the result is
     `PENDING_CONFIRMATION`. If it is absent, the result is `INCOMPLETE`.
   - A wallet MUST NOT present an EntityID as final while its history is
     `PENDING_CONFIRMATION`.
   - Replacing the genesis seal's creating transaction by fee bump (RBF)
     invalidates that genesis, because its outpoint no longer exists; the
     wallet must discard the pending EntityID. CPFP preserves it.

5. **Root authority.** The root has no protocol authority after genesis. A
   root compromised after genesis cannot impersonate the EntityID. It can only
   sign new, distinct identities, which the non-exclusive name policy of
   ADR-0004 already handles. The root may be kept offline indefinitely.
   Deterministic derivation (ADR-0006) means it remains re-derivable from the
   seed; destroying one copy of the key does not remove it.

6. **Unchanged from ADR-0005:**
   - a dedicated root per entity;
   - the root signs genesis;
   - controller rotation, recovery-policy change, recovery, custody transfer
     and revocation preserve the EntityID;
   - a different root means a different genesis and therefore a different
     EntityID.

## Consequences

Positive:

- Genesis non-equivocation holds by construction. ADR-0005's statement that
  non-equivocation inherits Bitcoin security becomes true from genesis onward.
- A stolen root, even with a stolen seal key, can never obtain an existing
  EntityID. The worst outcome is closure of the artist's seal (denial of
  service), which the artist can detect.
- No activation transaction, extra output or address-history index is needed.
- The design matches RGB's own model, where a contract ID is the hash of its
  genesis.

Costs and limits:

- **Restore.** EntityIDs cannot be recomputed from the seed plus a chain scan.
  Restore needs the genesis payloads, which the consignment backups required by
  ADR-0005 already contain. Losing consignments already means losing the
  ability to prove an identity.
- **When the ID is final.** An EntityID exists once the genesis is signed. It
  is final only when the genesis seal's creating transaction reaches the
  required depth, about six blocks on mainnet.
- **Rework.**
  - every EntityID in every vector changes;
  - genesis vectors get a zero `signer_entity`;
  - the demo lineage is regenerated;
  - `PENDING_CONFIRMATION` is added to outcome vocabularies.
- **Denial of service remains possible.** A holder of the seal spending key can
  still close a seal without a valid transition. Seal-key custody remains as
  important as controller-key custody.
- **Names stay non-exclusive.** A root holder can create new identities that
  reuse an artist's name. That is a name-policy question, not an identity
  forgery.

## Relationship to earlier decisions

- **[ADR-0005](0005-bitcoin-rooted-self-custodial-identity.md), amended.**
  - Its statement that the EntityID is "deterministically rooted in that
    public key, the protocol profile, and the network context" is now met
    through the root-signed genesis, which contains all three.
  - Its statement that the "root public key is immutable because the EntityID
    is derived from it" still holds.
  - Its non-equivocation consequence now holds at genesis.
- **[ADR-0006](0006-route-b-key-derivation-via-bip85.md), unchanged.** Key
  derivation paths and outputs do not change.
- **[ADR-0002](0002-entity-id-over-artist-id.md) and
  [ADR-0004](0004-consensus-as-policy-not-blockchain.md), unchanged.**

## Specification changes on acceptance

Each change must be copied downward, per `docs/DOCUMENT-AUTHORITY.md`.

- `specs/canonical-encoding.md`:
  - replace the EntityID block and the "35-byte preimage" paragraph;
  - in "1. Entity genesis", require `signer_entity` to be 32 zero bytes and
    define the EntityID as the tagged hash of the genesis payload;
  - note the genesis exception in "Common signed header".
- `specs/entity-schema.md`: `entity_id` becomes the genesis-bound ID; update
  the JSON example and requirements.
- `specs/rgb-identity-contract.md`:
  - genesis uniqueness (Decision 3);
  - seal-creating transactions at the anchor depth, with the reorg and RBF
    rules (Decision 4).
- `specs/verification-policy.md`: add the `PENDING_CONFIRMATION` outcome and
  make the CURRENT precondition include seal-creating depth.
- `specs/proof-package-schema.md`: the verifier recomputes the EntityID from
  the included genesis; a mismatch with any named EntityID is INVALID.
- `specs/key-derivation-profile.md`: add a restore note (EntityIDs are not
  derivable from the seed alone).
- Downward restatements: README, docs 01/03/14, the derivation-allocation note
  if it names EntityIDs, and diagrams/site copy that state "EntityID from the
  root".
- Vectors:
  - regenerate every EntityID-bearing vector;
  - add genesis-bound EntityID vectors;
  - wire `tests/vectors/entity-id-regression/` to the normative
    implementation.

## Required acceptance evidence

- `tests/vectors/entity-id-regression/check_entity_id_regression.py` passes
  with its rule seam pointing at the normative implementation in
  `check_protocol_objects.py`, not at the candidate. Its negative controls must
  still show that the previous rule (root-only) and Option B admit the
  attacks.
- Python and Rust agree on genesis-bound EntityID vectors.
- A regtest demo lineage, with two-validator agreement, shows:
  - genesis with a zero `signer_entity`;
  - `PENDING_CONFIRMATION` below depth, then `CURRENT`;
  - rotation and recovery preserving the EntityID;
  - a second genesis on the same seal getting a distinct EntityID and ending
    `SEAL_CLOSED_WITHOUT_VALID_TRANSITION` after the artist's first
    transition.
- The standard vector suite and Palimnex validation are green.
