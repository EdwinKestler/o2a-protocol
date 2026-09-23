# Claim Schema — Draft v0.1

## Object

```json
{
  "protocol_version": "0.1",
  "bitcoin_network": "<bitcoin-network>",
  "object_type": "claim",
  "issuer": "<EntityID>",
  "issuer_state": "<validated-rgb-identity-state-id>",
  "controller_key_id": "<authorized-controller-key-id>",
  "controller_key_purpose": "claim",
  "subject": "<EntityID>",
  "predicate": "<versioned-predicate>",
  "object": "<canonical-value-or-reference>",
  "context": "<optional-context>",
  "nonce": "<replay-protection>",
  "supersedes": null,
  "checkpoint": null,
  "signature": {
    "scheme": "bip340-secp256k1",
    "domain": "O2A/v0.1/claim",
    "value": "<signature>"
  }
}
```

## Claim commitment

Conceptually:

```text
C = TaggedHash("O2A/v0.1/claim", Canonical(claim-without-signature))
```

The BIP340 signature signs `C`. The final canonical bytes are defined by the
[cryptographic profile](cryptographic-profile.md) and its conformance vectors.

## Requirements

- issuer MUST resolve through a valid RGB identity history anchored to Bitcoin;
- `issuer_state` MUST identify the state that authorized the signing key;
- the controller key and purpose MUST be authorized by that state;
- the BIP340 signature MUST validate against the canonical claim bytes;
- the signature MUST use the claim tagged-hash domain and MUST be rejected in
  every other O2A signing domain;
- predicate semantics MUST be versioned;
- nonce/state semantics MUST prevent unintended replay;
- signed historical claims MUST NOT be edited in place;
- corrected claims SHOULD reference superseded objects;
- ordinary claims do not require their own Bitcoin transaction;
- an optional checkpoint MUST commit to the exact claim or evidence-package
  hash and MUST NOT be interpreted as proof that the claim is socially true;
- human-readable names are non-exclusive claims. Competing claims and their
  anchor order MUST remain available to policy evaluation.

The root identity key SHOULD authorize genesis and exceptional recovery rather
than routine claims. Wallets SHOULD use delegated, purpose-bound controller
keys for day-to-day signing.
