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
  "controller_key_role": "controller",
  "authorization_capability": "claim",
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

The BIP340 signature signs `C`. The exact payload bytes are defined by
[O2A-CANON-1](canonical-encoding.md). Conformance fixtures remain a Phase 0
gate.

## Requirements

- issuer MUST resolve through a valid RGB identity history anchored to Bitcoin;
- `issuer_state` MUST identify the state that authorized the signing key;
- the controller key role and claim capability MUST be authorized by that
  state;
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
- human-readable names stay competing claims. Two EntityIDs MAY use the same
  name, and there is no first-claim registry. Competing claims and their
  anchor order MUST remain available to policy evaluation; and
- a name claim MUST use domain `O2A/v0.1/claim` and a key authorized for the
  claim capability.

The root identity key SHOULD authorize genesis rather than routine claims.
Wallets SHOULD use delegated controller keys with narrowly scoped
capabilities for day-to-day signing. Recovery uses recovery-role keys named by
the previously committed recovery policy.

## Vector obligations

Canonical bytes are defined in O2A-CANON-1. Executable signature fixtures still
need to cover the duplicate-names case:

- accept two EntityIDs that use the same human-readable name, each signed in
  `O2A/v0.1/claim` by a key authorized for `claim`, with both claims remaining
  visible; and
- reject a first-claim registry, a merge of those EntityIDs, and a name claim
  signed outside the claim domain or by a key not authorized for `claim`.
