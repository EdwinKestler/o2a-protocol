# Claim Schema — Draft v0.1

## Object

```json
{
  "protocol_version": "0.1",
  "object_type": "claim",
  "issuer": "<EntityID>",
  "issuer_state": "<validated-rgb-identity-state-id>",
  "controller_key_id": "<authorized-controller-key-id>",
  "subject": "<EntityID>",
  "predicate": "<versioned-predicate>",
  "object": "<canonical-value-or-reference>",
  "context": "<optional-context>",
  "nonce": "<replay-protection>",
  "supersedes": null,
  "checkpoint": null,
  "signature": {
    "scheme": "bip340-secp256k1",
    "value": "<signature>"
  }
}
```

## Claim commitment

Conceptually:

[
C=H(version || issuer || subject || predicate || object || context || nonce)
]

The signature signs C or the canonical claim payload defined by the final cryptographic profile.

## Requirements

- issuer MUST resolve through a valid RGB identity history anchored to Bitcoin;
- `issuer_state` MUST identify the state that authorized the signing key;
- the controller key and purpose MUST be authorized by that state;
- the BIP340 signature MUST validate against the canonical claim bytes;
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
