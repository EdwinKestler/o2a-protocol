# Bitcoin-Rooted Entity Schema — Draft v0.1

## Status

Draft. This document defines semantic fields; canonical binary encoding is still TBD.

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
    "purposes": ["claim", "attestation", "identity_transition"]
  }],
  "recovery_policy": {
    "policy_hash": "<canonical-recovery-policy-hash>"
  },
  "profile_commitment": null,
  "status": "ACTIVE",
  "signing_key_id": "<root-identity-key-id>",
  "signing_key_purpose": "entity_genesis",
  "signature_domain": "O2A/v0.1/entity-genesis",
  "genesis_signature": "<root-key-signature>"
}
```

## Requirements

- every entity MUST have its own dedicated BIP340/secp256k1 root identity key;
- identity and controller keys MUST be separate from Bitcoin spending keys;
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
- the root identity key MUST NOT remain an unconditional controller unless the
  current valid state grants it that purpose;
- `entity_id` MUST remain stable across operational-controller rotation and
  authorized recovery;
- the root public key MUST remain immutable. A replacement root produces a new
  EntityID rather than a recovery transition;
- canonical serialization MUST exclude transport-only metadata;
- human-readable profiles SHOULD remain separable from identity-critical state;
- the exact EntityID encoding, RGB schema, Bitcoin commitment method,
  confirmation policy, and reorg behavior MUST be frozen before implementation.

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
