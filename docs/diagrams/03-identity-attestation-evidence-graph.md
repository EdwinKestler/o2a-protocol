# 03 — Identity and Attestation Evidence Graph

The protocol does not create verification from a single centralized registrar. Verification emerges from independently signed evidence evaluated by policy.

```mermaid
graph TD
    ART["Artist EntityID"]
    VEN["Venue EntityID"]
    PRO["Promoter EntityID"]
    EVT["Event EntityID"]
    OTHER["Other verified Artist / Organization"]

    ART -->|"self claim: official_name"| ART
    VEN -->|"attests: performed_at"| ART
    VEN -->|"hosted"| EVT
    PRO -->|"booked"| ART
    PRO -->|"organized"| EVT
    ART -->|"performed_at"| EVT
    OTHER -->|"endorsement / relationship attestation"| ART

    POL["Trust Policy"]
    RES["Verification Result<br/>status + policy hash + evidence refs"]

    ART --> POL
    VEN --> POL
    PRO --> POL
    EVT --> POL
    OTHER --> POL
    POL --> RES
```

## Identity collision example

```mermaid
graph LR
    A1["Entity A1<br/>claims Artist X"]
    A2["Entity A2<br/>also claims Artist X"]
    V1["Verified Venue"]
    P1["Verified Promoter"]
    B1["Verified Artist"]

    V1 -->|"attests A1"| A1
    P1 -->|"attests A1"| A1
    B1 -->|"attests A1"| A1

    A2 -->|"self claim only"| A2
```

The protocol preserves both claims. A verification policy determines how the available evidence is interpreted.
