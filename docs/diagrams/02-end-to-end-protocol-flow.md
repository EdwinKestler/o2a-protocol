# 02 — End-to-End Protocol Flow

The first diagram is dependency order. A lower layer must not import an upper layer. A challenge is not a mandatory hop before every policy run; when a challenge or revocation exists, it stays in the evidence the policy has to explain.

```mermaid
flowchart LR
    B["Bitcoin<br/>order · anchors · seals"]
    K["RGB Identity Kernel<br/>genesis · state · transitions<br/>consignments · validation"]
    I["Entity Identity<br/>BIP340 root · controller keys<br/>rotation · recovery · revocation"]
    C["Claims<br/>self-attestation<br/>signed assertions"]
    A["Attestations<br/>venue · promoter · artist<br/>independent evidence"]
    X["Optional Challenges / Revocation<br/>disputes · conflicts<br/>corrections when present"]
    P["Trust Policy<br/>deterministic rules<br/>verification status"]
    R["Registries<br/>Artist · Venue · Promoter<br/>Label · Event · Album"]
    M["Application Modules<br/>GatePass · SplitNight<br/>Sponsors · Merch/F&B"]

    B --> K --> I
    I --> C --> P
    I --> A --> P
    I --> X
    X -. "when present" .-> P
    P --> R --> M
```

## Operational Hello World

This is the first complete scenario. It matches the [roadmap](../13-roadmap.md) and the [vision](../00-vision.md). Booking, performance, and settlement remain distinct claims. A promoter statement is additional evidence, not a requirement for creating an EntityID.

```mermaid
flowchart TB
    subgraph OWNER["Owner wallet / node"]
        E["1 Create EntityID<br/>immutable BIP340 root<br/>separate from spending keys"]
        L["2 Evolve identity<br/>controller rotation · recovery<br/>revocation under RGB state"]
        S["3 Sign typed evidence<br/>name · DNS/social control<br/>event/album manifests · relationships"]
        PKG["4 Export public proof package<br/>identity-history shard · Bitcoin proofs<br/>evidence · policy · context"]
        E --> L --> S --> PKG
    end

    BTC["Bitcoin consensus<br/>order · anchors · seals"] --> L
    RGB["RGB client-side validation<br/>schema · transitions · consignments"] --> L
    TAG["BIP340 signing domains<br/>purpose-specific tagged hashes"] --> S

    PKG --> X["5 Publish / transfer<br/>direct wallet exchange<br/>HTTPS · Pubky · optional Nostr locators"]
    X --> V1["6 Verifier wallet A"]
    X --> V2["6 Verifier wallet B"]
    V1 --> R1["Same explained result"]
    V2 --> R2["Same explained result"]

    LOC["Locator or host<br/>transport, never authority"] -.-> X
```

Both verifier wallets check the package hash, Bitcoin proofs, RGB history,
signatures and domains, evidence boundary, named policy, protocol version, and
evaluation context. Missing history or unavailable referenced content produces
an incomplete or invalid result. Registries are rebuildable projections over
the validated packages. GatePass, SplitNight, and payment modules consume the
result; they do not redefine identity.

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
