# Verification Policy — Draft v0.1

## Purpose

A verification policy maps validated RGB identity histories and a normalized
evidence set to a deterministic result.

## Conceptual object

```json
{
  "protocol_version": "0.1",
  "policy_version": "artist-basic-v1",
  "subject_type": "ARTIST",
  "required_identity_profile": "o2a-bitcoin-rgb-v0.1",
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

For validated identity histories I, evidence E, policy P, protocol version V,
and explicit evaluation context C:

[
Verify(I,E,P,V,C)=R
]

Implementations MUST NOT depend on database row order, wall-clock time unless explicitly supplied as evaluation context, network availability, hidden reputation state, or implementation-specific floating-point behavior.

The evaluator MUST NOT perform hidden live DNS, social, Pubky, Nostr, Bitcoin,
or indexer requests. Online collectors normalize those results into signed,
bounded observations. Bitcoin headers, confirmations, reorg assumptions, and
RGB consignments used by evaluation are explicit inputs.

## Explainability

Result R MUST expose sufficient information to reproduce the decision:

- policy ID/hash;
- accepted identity-state and Bitcoin-anchor references;
- accepted evidence IDs;
- rejected/inapplicable evidence IDs where relevant;
- conflict state;
- rule path that produced the result.

## Versioning

Policy modifications create a new policy version/hash. Historical verification can therefore be reproduced under the policy originally used.

Policy may rank the strength of competing human-name claims, but the result
MUST identify the evidence and MUST NOT create a core-protocol first-claim
ownership rule. Bitcoin ordering is evidence about chronology, not automatic
ownership of a spelling.
