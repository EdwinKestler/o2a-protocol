# 02 — End-to-End Protocol Flow

The first diagram is dependency order. A lower layer must not import an upper layer. A challenge is not a mandatory hop before every policy run; when a challenge or revocation exists, it stays in the evidence the policy has to explain.

```mermaid
flowchart LR
    B["Bitcoin<br/>order · anchors · seals"]
    K["RGB Identity Kernel<br/>genesis · state · transitions<br/>consignments · validation"]
    I["Entity Identity<br/>BIP340 root · controller keys<br/>rotation · recovery · revocation"]
    C["Claims<br/>self-attestation<br/>signed assertions"]
    A["Attestations<br/>venue · promoter · artist<br/>independent evidence"]
    X["Challenges / Revocation<br/>disputes · conflicts<br/>corrections"]
    P["Trust Policy<br/>deterministic rules<br/>verification status"]
    R["Registries<br/>Artist Catalog<br/>Venue Registry<br/>Event Registry"]
    M["Application Modules<br/>GatePass · SplitNight<br/>Sponsors · Merch/F&B"]

    B --> K --> I --> C --> A --> X --> P --> R --> M
```

## Operational Hello World

This is the first complete scenario. It matches the [roadmap](../13-roadmap.md) and the [vision](../00-vision.md). Booking, performance, and settlement remain distinct claims. A promoter statement is additional evidence, not a requirement for creating an EntityID.

```mermaid
flowchart LR
    E["1 Identity genesis<br/>BIP340 root · RGB state<br/>anchored to Bitcoin"] --> C["2 Name + channel claims<br/>non-exclusive · signed<br/>DNS / social evidence"]
    C --> V["3 Event EntityID<br/>its own key + manifest hash<br/>held by venue or promoter"]
    V --> A["4 Relationship attestations<br/>artist · venue · promoter"]
    A --> X["5 Challenges + competing names<br/>remain visible"]
    X --> P["6 Same result<br/>same package + policy<br/>independent wallets"]
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
