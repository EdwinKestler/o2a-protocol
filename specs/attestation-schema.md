# Attestation Schema — Draft v0.1

## Object

```json
{
  "protocol_version": "0.1",
  "object_type": "attestation",
  "issuer": "<EntityID>",
  "issuer_state": "<validated-rgb-identity-state-id>",
  "controller_key_id": "<authorized-controller-key-id>",
  "subject": "<EntityID-or-object-id>",
  "predicate": "<versioned-predicate>",
  "object": "<canonical-value-or-reference>",
  "evidence": ["<object-id>"],
  "context": "<optional-event-or-domain-context>",
  "nonce": "<replay-protection>",
  "signature": {
    "scheme": "bip340-secp256k1",
    "value": "<signature>"
  }
}
```

## Requirements

- attestation identity is distinct from the target claim;
- issuer identity and controller authorization MUST be independently
  verifiable from the issuer's RGB identity history and Bitcoin anchor;
- evidence references MUST be immutable identifiers;
- policy evaluation MUST be able to identify attester independence and conflicts from explicit evidence;
- an attestation MUST NOT directly mutate verification status.

Verification status is derived by policy.

Attestations may confirm a name association, domain or social-account control,
album relationship, event relationship, or observation. They do not vote an
identity into existence. Multiple observers reading one underlying source are
multiple observations of one source, not automatically independent social
endorsements.
