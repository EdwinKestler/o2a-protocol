# O2A Protocol

**Open2Artist (O2A)** is a modular identity, attestation, verification, and registry protocol for artists and the wider live-music ecosystem.

The protocol is designed around a generic **EntityID** primitive so the same trust layer can represent artists, venues, promoters, events, and later other ecosystem participants without redefining identity for each application.

## Design principle

```text
Protocol Kernel
    ↓
Entity Identity
    ↓
Claims
    ↓
Attestations
    ↓
Challenges / Revocation
    ↓
Trust Policy
    ↓
Registries
    ↓
Applications
```

Dependencies flow downward only. Application modules consume protocol primitives; lower layers never depend on application-specific concepts.

## Source of truth

Registries and databases are projections, not authority.

```text
RGB/client-side validated state + signed evidence + policy
                            ↓
                    rebuildable registry
```

Given identical evidence, policy, and protocol version, independent verifiers MUST produce the same result.

## Initial scope

O2A v0.1 specifies:

- Entity identity and controller rotation
- Signed claims
- Third-party attestations
- Challenges and revocation
- Deterministic trust policies
- Artist, venue, and event registry projections
- Portable proof packages
- Module boundaries for GatePass and SplitNight

## Repository structure

```text
docs/   Narrative protocol design
specs/  Canonical data and verification contracts
adr/    Architecture decision records
```

No production implementation code should be introduced until the v0.1 schemas, canonical serialization rules, and deterministic Hello-World test vectors are agreed.

## First milestone

The first complete protocol scenario is:

1. An artist creates an EntityID.
2. The artist publishes a signed self-claim.
3. A venue attests that the artist performed at an event.
4. A promoter independently attests that the artist was booked for the event.
5. Independent clients validate the same evidence.
6. Each client applies the same versioned trust policy.
7. Each client derives the same verification result.

```text
same evidence + same policy + same protocol version
                         =
                 same verification result
```

## Status

**Design / specification phase.**  
Network targets, cryptographic primitives, serialization rules, and RGB integration remain subject to implementation validation before v1.0.
