# Bitcoin-Rooted Entity Schema — Draft v0.1

## Status

Draft. This document defines semantic fields. The candidate exact EntityID
encoding is specified in [canonical encoding](canonical-encoding.md); Phase 0
has not frozen the full wallet profile.

## Object

```json
{
  "protocol_version": "0.1",
  "object_type": "entity",
  "network": "<bitcoin-network>",
  "entity_id": "<id-derived-from-network-and-root-identity-key>",
  "entity_type": "ARTIST",
  "root_identity_key": {
    "scheme": "bip340-secp256k1",
    "public_key": "<32-byte-x-only-public-key>"
  },
  "rgb_identity": {
    "contract_id": "<rgb-contract-id>",
    "state_id": "<rgb-state-id>",
    "sequence": 0,
    "previous_state": null,
    "seal": "<bitcoin-outpoint>",
    "anchor": "<bitcoin-anchor-reference>"
  },
  "controllers": [{
    "key_id": "<controller-key-id>",
    "scheme": "bip340-secp256k1",
    "public_key": "<32-byte-x-only-public-key>",
    "key_role": "controller",
    "capabilities": ["claim", "attestation", "identity_transition"]
  }],
  "recovery_policy": {
    "version": 1,
    "sequence": 0,
    "threshold": 2,
    "recovery_key_ids": ["<sorted-recovery-key-id>"],
    "delay_blocks": 144,
    "cancellation_rule": "CONTROLLER_SPENDS_PRIOR_SEAL_BEFORE_NOT_BEFORE",
    "policy_hash": "<canonical-recovery-policy-hash>"
  },
  "seal_policy": {
    "version": 1,
    "controller_seal_bindings": [{
      "controller_key_id": "<capability-2-controller-key-id>",
      "seal_xonly": "<role-4-x-only-seal-key>"
    }],
    "recovery_seal_bindings": [{
      "recovery_key_id": "<recovery-policy-key-id>",
      "seal_xonly": "<role-4-x-only-seal-key>"
    }],
    "derived_display": {
      "internal_key": "50929b74c1a04954b78b4b6035e97a5e078a5a0f28ec96d547bfee9ace803ac0",
      "output_type": "P2TR",
      "script_pubkey": "<deterministically-recomputed-scriptPubKey>"
    }
  },
  "profile_commitment": null,
  "status": "ACTIVE",
  "signing_key_id": "<root-identity-key-id>",
  "signing_key_role": "root_identity",
  "signing_capability": "entity_genesis",
  "signature_domain": "O2A/v0.1/entity-genesis",
  "genesis_signature": "<root-key-signature>"
}
```

## Requirements

- every entity MUST have its own dedicated BIP340/secp256k1 root identity key;
- root, controller, recovery, and Nostr-publication keys MUST be separate from
  Bitcoin spending keys;
- seal keys MUST use role 4, hold no O2A capability, and be separate from
  payment keys and every O2A-signing key;
- key role and authorization capability MUST be encoded and validated as
  separate values;
- `entity_id` MUST be deterministically rooted in the protocol profile,
  Bitcoin network, and root identity public key;
- genesis MUST be signed by the root key and represented by an RGB state
  anchored to Bitcoin;
- genesis, transitions, and recovery authorizations MUST use their respective
  tagged-hash domains from the
  [cryptographic profile](cryptographic-profile.md);
- the validated RGB history MUST bind the current state to the correct contract,
  previous state, Bitcoin seal, witness transaction, and commitment;
- `sequence` MUST monotonically advance for mutable identity state;
- transitions MUST reference the previous valid RGB state;
- controller, recovery-policy, and revocation changes MUST be authorized by the
  previous valid state and anchored through a new RGB transition;
- the recovery policy MUST commit its version, sequence, threshold, sorted key
  IDs, block delay, and cancellation rule using O2A-CANON-1;
- the resulting state MUST commit the canonical seal policy, and the outpoint
  named by `seal` MUST contain the deterministic P2TR scriptPubKey derived from
  that policy;
- controller and recovery seal bindings MUST cover exactly the corresponding
  capability-2 controller and recovery-policy key-ID sets, with no stale,
  missing, or extra binding, and x-only reuse across roles is invalid;
- `internal_key`, `output_type`, and `script_pubkey` in the JSON example are
  derived display fields, not canonical state fields; verifiers MUST recompute
  them from the canonical policy rather than trust serialized display values;
- the root identity key MUST NOT remain an unconditional controller unless the
  current valid state grants it the required capability;
- `entity_id` MUST remain stable across operational-controller rotation and
  authorized recovery;
- the root public key MUST remain immutable. A replacement root produces a new
  EntityID rather than a recovery transition;
- canonical serialization MUST exclude transport-only metadata;
- human-readable profiles SHOULD remain separable from identity-critical state;
- the exact EntityID encoding and O2A state payload grammar are specified in
  [canonical encoding](canonical-encoding.md); the identity derivation purpose,
  RGB program/schema bytes, and Bitcoin commitment carrier remain open until
  the Phase 0 dependency gate passes.

## Initial entity types

```text
PERSON
ARTIST
BAND
VENUE
PROMOTER
LABEL
ORGANIZATION
EVENT
ALBUM
```

Unknown future types require version-aware handling rather than silent coercion.

For EVENT and ALBUM, the root key may be derived in the responsible
participant's self-custodial wallet. The entity still has an independent
EntityID. Canonical event manifests, album metadata, and media hashes are
signed claims about that entity; the public key alone does not prove that an
event occurred or establish copyright ownership.
