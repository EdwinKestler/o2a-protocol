# Claim Schema — Draft v0.1

## Object

```json
{
  "protocol_version": "0.1",
  "object_type": "claim",
  "issuer": "<EntityID>",
  "subject": "<EntityID>",
  "predicate": "<versioned-predicate>",
  "object": "<canonical-value-or-reference>",
  "context": "<optional-context>",
  "nonce": "<replay-protection>",
  "supersedes": null,
  "signature": {
    "scheme": "<scheme>",
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

- issuer MUST resolve to an applicable controller state;
- signature MUST validate against that state;
- predicate semantics MUST be versioned;
- nonce/state semantics MUST prevent unintended replay;
- signed historical claims MUST NOT be edited in place;
- corrected claims SHOULD reference superseded objects.
