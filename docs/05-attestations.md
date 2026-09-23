# 05 — Attestations

## Definition

An Attestation is signed evidence issued by an authorized controller of one
validated O2A identity about another entity, claim, relationship, album, event,
or online observation.

Examples:

- a venue attests that an artist performed at an event;
- a promoter attests that it booked an artist;
- an artist attests that a venue hosted the performance;
- an organization attests that a controller represents a legal entity.
- an artist or label attests that an ALBUM manifest describes a particular work;
- an observer attests that a key-bound DNS or social token was visible during
  a specified interval.

## Evidence graph

Attestations naturally form a directed graph:

[
G=(V,E)
]

where V are entities and E are signed attestations.

An edge conceptually contains:

[
e_{ij}=(issuer_i, subject_j, predicate, object, context, signature)
]

## No automatic authority

An attestation is evidence, not truth by itself.

Verification occurs only when a named policy evaluates the complete applicable evidence set.

The issuer's EntityID, RGB state, controller purpose, and Bitcoin anchor must
validate before its attestation can be considered. This establishes who signed
the statement, not whether the statement is true.

## Independence

Policies may distinguish:

- self-attestation;
- related-party attestation;
- independent attestation;
- previously verified attester;
- conflicting attestation.

These relationships must be explicit rather than inferred invisibly.

Several wallets observing the same DNS record or social post provide redundant
observations of one source. They do not automatically become several
independent endorsements of the claimed real-world identity.
