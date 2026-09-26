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
  ],
  "identity_history_states": [
    "CURRENT",
    "REVOKED",
    "SEAL_CLOSED_WITHOUT_VALID_TRANSITION",
    "INCOMPLETE",
    "INVALID"
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

For a public identity, those inputs MUST be obtainable from a validated
[public identity proof package](proof-package-schema.md) or direct wallet
transfer. A package locator is not evidence of availability or validity: the
verifier fetches the content, checks its hash, validates the RGB history and
Bitcoin proofs, verifies the package publisher's controller authorization and
BIP340 signature in the proof-package tagged-hash domain, and reports missing
material explicitly.

Before policy evaluation, a verifier MUST:

1. recompute `package_id` from the complete signed envelope and parse exactly
   one bounded envelope with no trailing bytes;
2. recompute `manifest_id` from the canonical manifest payload and reject a
   Bitcoin-network, protocol-version, object-type, manifest-ID, or package-ID
   mismatch;
3. validate the publisher's RGB history through `publisher_state` and confirm
   that `signing_key`, key role, and proof-package-publication capability are
   authorized together;
4. reconstruct the canonical package signature payload, compute the
   `O2A/v0.1/proof-package` tagged hash, and verify the BIP340 signature;
5. reject a plain-hash signature, unknown domain, cross-domain replay, or
   signature made by a key not authorized by the stated publisher state; and
6. validate every referenced identity history, Bitcoin proof, evidence object,
   policy, and explicit evaluation context required for the result, including
   each seal-creating transaction and its state-derived P2TR scriptPubKey.

Failure at steps 1–5 makes the package invalid. Unavailable referenced content
needed at step 6 makes the evaluation incomplete unless the named policy
explicitly excludes that content from its declared evidence boundary.

## Terminal seal closure

The evaluator MUST NOT return `CURRENT` unless the explicit Bitcoin view in
evaluation context observes the current seal as unspent. The result MUST name
that view's source, observed best-block hash, and height. A proof package
cannot prove non-spend, and RGB validation alone never establishes `CURRENT`;
without the observation, the identity-history result is `INCOMPLETE`.

When that Bitcoin view contains the current-seal spending transaction and its
inclusion/header proof at the identity-anchor confirmation depth, but no valid
O2A transition closes the seal, the evaluator MUST return identity-history
state `SEAL_CLOSED_WITHOUT_VALID_TRANSITION`. The same anchor reorg rule
applies to this spend proof. The last valid state remains historical but is not
transition-capable. This outcome is distinct from `REVOKED`, `CURRENT`, an
ordinary ACTIVE lifecycle display, and missing data. Recognition policy may
still evaluate evidence about that history, but continuity requires a new
EntityID and explicit successor evidence.

## Confirmation and reorg

Identity anchors use the confirmation depth and reorg rule in the
[RGB identity contract](rgb-identity-contract.md)
(`specs/rgb-identity-contract.md`). Required depth is 1 on regtest, signet,
testnet, and testnet4, and 6 on mainnet. The evaluation context names the best
block hash, height, and required depth. An anchor absent from that best chain
at the required depth is not current. A reorg that removes the anchor drops
dependent transitions.

## Explainability

Result R MUST expose sufficient information to reproduce the decision:

- policy ID/hash;
- accepted identity-state and Bitcoin-anchor references;
- current-seal observation source, best-block hash, and height;
- public proof-package ID and any missing referenced objects;
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
