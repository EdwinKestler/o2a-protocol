# Attestation Schema — Draft v0.1

## Object

```json
{
  "protocol_version": "0.1",
  "bitcoin_network": "mainnet|testnet|signet|regtest",
  "object_type": "attestation",
  "issuer": "<EntityID>",
  "issuer_state": "<validated-rgb-identity-state-id>",
  "controller_key_id": "<authorized-controller-key-id>",
  "controller_key_role": "controller",
  "authorization_capability": "attestation",
  "subject": "<EntityID-or-object-id>",
  "predicate": "<versioned-predicate>",
  "object": "<canonical-value-or-reference>",
  "evidence": ["<object-id>"],
  "context": "<optional-event-or-domain-context>",
  "nonce": "<replay-protection>",
  "signature": {
    "scheme": "bip340-secp256k1",
    "domain": "O2A/v0.1/attestation",
    "value": "<signature>"
  }
}
```

## Requirements

- attestation identity is distinct from the target claim;
- issuer identity and controller authorization MUST be independently
  verifiable from the issuer's RGB identity history and Bitcoin anchor;
- the controller key role and attestation capability MUST both be authorized
  by `issuer_state`;
- evidence references MUST be immutable identifiers;
- the signature MUST use the attestation tagged-hash domain from the
  [cryptographic profile](cryptographic-profile.md);
- policy evaluation MUST be able to identify attester independence and conflicts from explicit evidence;
- an attestation MUST NOT directly mutate verification status; and
- one identity attests about another. The attester signature MUST NOT become
  the subject's own claim.

Verification status is derived by policy.

Attestations may confirm a name association, domain or social-account control,
album relationship, event relationship, or observation. They do not vote an
identity into existence. Multiple observers reading one underlying source are
multiple observations of one source, not automatically independent social
endorsements.

## Vector obligations

Canonical bytes are defined in O2A-CANON-1. An executable attestation fixture
that appears beside the named cases must follow this boundary:

- accept it as one identity attesting about another in `O2A/v0.1/attestation`;
  and
- reject the attester signature as the subject's own claim.
