# 08 — O2A Ecosystem and Namespace Map

This diagram captures the later Open2Artist naming/architecture concept without changing the generic EntityID protocol design.

```mermaid
flowchart TB
    O2A["Open2Artist / O2A"]
    PROTO["O2A Protocol"]
    ID["O2A ID<br/>product-facing representation"]
    ENTITY["EntityID<br/>BIP340 root + RGB lifecycle<br/>anchored to Bitcoin"]

    ART["Artist"]
    VEN["Venue"]
    PROM["Promoter"]
    EVT["Event"]
    ALB["Album"]
    LAB["Label / Organization"]

    CL["Claims"]
    AT["Attestations"]
    PF["O2A Proof"]
    TP["Trust Policy"]

    AR["Artist Registry"]
    VR["Venue Registry"]
    ER["Event Registry"]

    GP["GatePass"]
    SN["SplitNight"]

    O2A --> PROTO --> ID --> ENTITY
    ENTITY --> ART
    ENTITY --> VEN
    ENTITY --> PROM
    ENTITY --> EVT
    ENTITY --> ALB
    ENTITY --> LAB

    ART --> CL
    VEN --> AT
    PROM --> AT
    EVT --> AT
    ALB --> CL
    LAB --> AT

    CL --> PF
    AT --> PF
    PF --> TP

    TP --> AR
    TP --> VR
    TP --> ER

    AR --> GP
    VR --> GP
    ER --> GP

    AR --> SN
    VR --> SN
    ER --> SN
```

## Naming boundary

```text
O2A ID    = human/product-facing identity
EntityID  = public-key-rooted protocol primitive with a Bitcoin/RGB lifecycle
```

This preserves an artist-focused go-to-market without restricting the protocol to artists only.
