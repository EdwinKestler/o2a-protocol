# 01 — Architecture

## Layer model

```text
Applications
    ↑
Registries
    ↑
Trust Policy
    ↑
Challenges / Revocation
    ↑
Attestations
    ↑
Claims
    ↑
Entity Identity
    ↑
Protocol Kernel
    ↑
RGB / Bitcoin adapters
```

Dependencies point downward. The kernel MUST NOT import artist, venue, event, ticket, or settlement-specific behavior.

## Layers

### Protocol Kernel

Provides state transitions, commitments, proof packaging, validation hooks, and anchoring adapters.

### Entity Identity

Defines EntityID, controller authorization, status, and controller/key rotation.

### Claims

Defines signed assertions from an issuer about a subject.

### Attestations

Defines independent evidence issued by one entity about another entity, claim, or event.

### Challenges and revocation

Represents disputes, corrections, supersession, and explicit invalidation without deleting history.

### Trust Policy

Consumes normalized evidence and deterministically derives a verification result.

### Registries

Artist, venue, and event registries are rebuildable projections for discovery and query performance.
An optional public-profile discovery adapter (for example Pubky) may provide
mutable profile data. Its availability or contents cannot silently change a
protocol verification result; signed claims and proof packages remain portable.

### Applications

GatePass, SplitNight, sponsorship, merchandise, and future modules consume identifiers and verification results.

Proposed channel-control verification uses online DNS/HTTPS/platform collectors
to produce signed observations for the evidence layer. The deterministic core
consumes preserved observations, not live network responses. Internet Identity
may be evaluated as an optional authentication/credential adapter. Native-BTC
verification deposits are downstream financial experiments, with their own
funding/refund state; neither login nor funding establishes artist recognition.
See [the assessment](17-control-proofs-and-verification-bonds.md).

## Storage model

```text
authoritative protocol/evidence state
              ↓
       projection builder
              ↓
          PostgreSQL
              ↓
      API / search / UI
```

Redis may cache derived results. Object storage may hold portable proof packages. Neither is authoritative.

## Determinism invariant

For protocol version V, evidence set E, and policy P:

[
Verify(E,P,V) = R
]

Every conforming implementation MUST produce the same result R.
