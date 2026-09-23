# 05 — Attestations

## Definition

An Attestation is signed evidence issued by an entity about another entity, claim, relationship, or event.

Examples:

- a venue attests that an artist performed at an event;
- a promoter attests that it booked an artist;
- an artist attests that a venue hosted the performance;
- an organization attests that a controller represents a legal entity.

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

## Independence

Policies may distinguish:

- self-attestation;
- related-party attestation;
- independent attestation;
- previously verified attester;
- conflicting attestation.

These relationships must be explicit rather than inferred invisibly.
