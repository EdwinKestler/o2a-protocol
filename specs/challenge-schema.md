# Challenge / Revocation Schema — Draft v0.1

## Challenge

```json
{
  "protocol_version": "0.1",
  "object_type": "challenge",
  "challenger": "<EntityID>",
  "target": "<object-id>",
  "reason": "<reason-code>",
  "evidence": ["<object-id>"],
  "context": "<optional-context>",
  "nonce": "<replay-protection>",
  "signature": {
    "scheme": "<scheme>",
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
  "target": "<object-id>",
  "reason": "<reason-code>",
  "context": "<optional-context>",
  "nonce": "<replay-protection>",
  "signature": {
    "scheme": "<scheme>",
    "value": "<signature>"
  }
}
```

## Requirements

- a challenge does not erase its target;
- revocation authority MUST be validated explicitly;
- challenge and revocation objects are themselves immutable signed evidence;
- resolution SHOULD create new evidence rather than mutate old evidence;
- policies MUST state how unresolved challenges affect verification.
