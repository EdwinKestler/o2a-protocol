# 02 — End-to-End Protocol Flow

The first diagram is dependency order. A lower layer must not import an upper layer. A challenge is not a mandatory hop before every policy run; when a challenge or revocation exists, it stays in the evidence the policy has to explain.

```mermaid
flowchart LR
    K["Protocol Kernel<br/>state · transitions · consignments<br/>proofs · anchoring"]
    I["Entity Identity<br/>EntityID · controller keys<br/>key rotation"]
    C["Claims<br/>self-attestation<br/>signed assertions"]
    A["Attestations<br/>venue · promoter · artist<br/>independent evidence"]
    X["Challenges / Revocation<br/>disputes · conflicts<br/>corrections"]
    P["Trust Policy<br/>deterministic rules<br/>verification status"]
    R["Registries<br/>Artist Catalog<br/>Venue Registry<br/>Event Registry"]
    M["Application Modules<br/>GatePass · SplitNight<br/>Sponsors · Merch/F&B"]

    K --> I --> C --> A --> X --> P --> R --> M
```

## Operational Hello World

This is the first complete scenario. It matches the [roadmap](../13-roadmap.md) and the [vision](../00-vision.md). Booking, performance, and settlement remain distinct claims. A promoter statement is additional evidence, not a requirement for creating an EntityID.

```mermaid
flowchart LR
    E["1 EntityID<br/>controller keys"] --> C["2 Self-claim<br/>signed by the participant"]
    C --> A["3 Event manifest<br/>artist and venue sign<br/>promoter may add evidence"]
    A --> X["4 Challenges<br/>remain visible"]
    X --> P["5 Named policy<br/>versioned rules"]
    P --> R["6 Same result<br/>independent verifiers"]
```

Registries are rebuildable projections over that evidence. GatePass, SplitNight, and payment modules consume the result; they do not redefine identity.

## Verification-state lifecycle

```mermaid
flowchart LR
    U["UNVERIFIED"] --> S["SELF-ATTESTED"] --> E["ENDORSED"] --> V["VERIFIED"]
    E --> CH["CHALLENGED"]
    V --> CH
    CH --> D["DISPUTED"] --> RS["RESOLVED"]
```

## Principle

Applications consume protocol primitives; they do not redefine identity or trust.
