# 05 — Software Stack Architecture

This is the proposed implementation stack. It is not a running system, and it
does not choose a web framework or an HTTP library. Bitcoin anchoring and RGB
client-side validation are required for the EntityID lifecycle. DNS, social,
Pubky, Nostr, databases, and application services have narrower roles. See
[the architecture](../01-architecture.md) and [the roadmap](../13-roadmap.md).

```mermaid
flowchart TB
    WC["Self-custodial clients — proposed<br/>Wallet/node · CLI · future SDK<br/>local seed · keys · consignments · proofs"]
    API["Protocol API — proposed<br/>entities · claims · attestations<br/>challenges · policies · proofs<br/>registry reads"]
    ENG["Protocol engine<br/>BIP340 authorization · RGB validation<br/>canonical proof packages<br/>policy evaluator"]
    BTC["Required identity foundation<br/>Bitcoin order + anchors + seals<br/>RGB lifecycle state + consignments"]
    RM["Read models — not authority<br/>PostgreSQL projection<br/>Redis disposable cache<br/>object storage for proof packages"]
    DISC["Discovery and observations<br/>DNS · HTTPS · social<br/>Pubky / PKARR · optional Nostr"]

    WC --> API --> ENG
    ENG --> BTC
    ENG --> RM
    API -.-> DISC
```

## Authority boundary

```text
Bitcoin/RGB identity history           REQUIRED IDENTITY AUTHORITY
Signed evidence + versioned policy     REAL-WORLD CLAIM EVALUATION
PostgreSQL                             REBUILDABLE PROJECTION
Redis                                  DISPOSABLE CACHE
Object storage                         PORTABLE EVIDENCE STORAGE
Full node or labeled light mode        BITCOIN DATA ACCESS
Public profile / discovery             NOT A VERIFICATION INPUT BY ITSELF
```
