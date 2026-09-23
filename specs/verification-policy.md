# Verification Policy — Draft v0.1

## Purpose

A verification policy maps a normalized evidence set to a deterministic result.

## Conceptual object

```json
{
  "protocol_version": "0.1",
  "policy_version": "artist-basic-v1",
  "subject_type": "ARTIST",
  "accepted_evidence": [],
  "rules": [],
  "conflict_rules": [],
  "result_states": [
    "UNVERIFIED",
    "SELF_ATTESTED",
    "ENDORSED",
    "VERIFIED",
    "CHALLENGED",
    "DISPUTED"
  ]
}
```

## Determinism

For evidence E, policy P, and protocol version V:

[
Verify(E,P,V)=R
]

Implementations MUST NOT depend on database row order, wall-clock time unless explicitly supplied as evaluation context, network availability, hidden reputation state, or implementation-specific floating-point behavior.

## Explainability

Result R MUST expose sufficient information to reproduce the decision:

- policy ID/hash;
- accepted evidence IDs;
- rejected/inapplicable evidence IDs where relevant;
- conflict state;
- rule path that produced the result.

## Versioning

Policy modifications create a new policy version/hash. Historical verification can therefore be reproduced under the policy originally used.
