# Attestation Schema — Draft v0.1

## Object

```json
{
  "protocol_version": "0.1",
  "object_type": "attestation",
  "issuer": "<EntityID>",
  "subject": "<EntityID-or-object-id>",
  "predicate": "<versioned-predicate>",
  "object": "<canonical-value-or-reference>",
  "evidence": ["<object-id>"],
  "context": "<optional-event-or-domain-context>",
  "nonce": "<replay-protection>",
  "signature": {
    "scheme": "<scheme>",
    "value": "<signature>"
  }
}
```

## Requirements

- attestation identity is distinct from the target claim;
- issuer authorization MUST be independently verifiable;
- evidence references MUST be immutable identifiers;
- policy evaluation MUST be able to identify attester independence and conflicts from explicit evidence;
- an attestation MUST NOT directly mutate verification status.

Verification status is derived by policy.
