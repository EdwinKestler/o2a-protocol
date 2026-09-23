# O2A Protocol

**Open2Artist (O2A)** is a modular identity, attestation, verification, and registry protocol for artists and the wider live-music ecosystem.

The protocol is designed around a generic **EntityID** primitive so the same trust layer can represent artists, venues, promoters, events, and later other ecosystem participants without redefining identity for each application.

Start with the [project vision and rationale](docs/00-vision.md) for the main
goal, the problems O2A addresses, the proposed solutions, and why this timing
and technology are appropriate to test them.

The [project website draft](docs/WEBSITE.md) has an owner-private Sites review
deployment and a local preview. Public release and GitHub Pages deployment
remain on hold pending authorization. Examples use generic participants.

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

Registries and databases are projections, not authority. Public profiles are
discoverable application data; signed evidence and its validation determine
protocol results. RGB/Bitcoin proofs contribute only when a policy explicitly
requires and verifies them.

```text
signed evidence + optional RGB/Bitcoin proof + versioned policy
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

Local source discovery and historical memory use Palimnex. See
[the O2A Palimnex setup](docs/PALIMNEX.md) for installation and validation.
See [code references](codereference.md) for RGB upstream sources and the
independent local project knowledge available for research.
The [identity/discovery assessment](docs/14-identity-discovery-assessment.md)
records how the original Pubky, claim-recognition, and event ideas affect the
[roadmap](docs/13-roadmap.md).
The [control-proof and verification-bond assessment](docs/17-control-proofs-and-verification-bonds.md)
evaluates DNS/social proofs, independent endorsements, optional satoshi
deposits, and Internet Identity/id.ai against the same protocol boundaries.

No production implementation code should be introduced until the v0.1 schemas, canonical serialization rules, and deterministic Hello-World test vectors are agreed.

## First milestone

The first complete protocol scenario is:

1. An artist creates an EntityID.
2. The artist publishes a signed self-claim.
3. The artist and a venue sign the same canonical event manifest through separate evidence objects.
4. A promoter may add independent booking evidence. Booking, performance, and settlement stay distinct claims.
5. Known challenges and revocations remain visible in the package.
6. Independent clients apply the same versioned trust policy to that evidence.
7. Each client derives the same verification result.

```text
same evidence + same policy + same protocol version + same evaluation context
                         =
                 same verification result
```

## Status

**Design / specification phase.**  
Network targets, cryptographic primitives, serialization rules, and RGB integration remain subject to implementation validation before v1.0.
