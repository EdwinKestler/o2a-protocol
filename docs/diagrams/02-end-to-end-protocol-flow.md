# 02 — End-to-End Protocol Flow

This diagram captures the proposed protocol path from generic state primitives to user-facing applications.

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
