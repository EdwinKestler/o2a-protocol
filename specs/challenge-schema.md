# Challenge / Revocation Schema — Draft v0.1

## Challenge

```json
{
  "protocol_version": "0.1",
  "object_type": "challenge",
  "challenger": "<EntityID>",
  "challenger_state": "<validated-rgb-identity-state-id>",
  "target": "<object-id>",
  "reason": "<reason-code>",
  "evidence": ["<object-id>"],
  "context": "<optional-context>",
  "nonce": "<replay-protection>",
  "signature": {
    "scheme": "bip340-secp256k1",
    "domain": "O2A/v0.1/challenge",
    "value": "<signature>"
  }
}
```

## Revocation

```json
{
  "protocol_version": "0.1",
  "object_type": "revocation",
  "issuer": "<EntityID>",
  "issuer_state": "<validated-rgb-identity-state-id>",
  "target": "<object-id>",
  "reason": "<reason-code>",
  "context": "<optional-context>",
  "nonce": "<replay-protection>",
  "signature": {
    "scheme": "bip340-secp256k1",
    "domain": "O2A/v0.1/revocation",
    "value": "<signature>"
  }
}
```

## Requirements

- a challenge does not erase its target;
- revocation authority MUST be validated explicitly;
- challenge and revocation objects are themselves immutable signed evidence;
- challenge and revocation signatures MUST use distinct tagged-hash domains
  from the [cryptographic profile](cryptographic-profile.md);
- resolution SHOULD create new evidence rather than mutate old evidence;
- policies MUST state how unresolved challenges affect verification.

This evidence-level revocation object revokes or qualifies a claim,
attestation, binding, or other signed object. Revoking an EntityID itself is an
RGB identity-state transition anchored to Bitcoin under
[the entity schema](entity-schema.md); an evidence object alone cannot mutate
the identity lifecycle.
