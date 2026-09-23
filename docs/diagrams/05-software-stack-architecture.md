# 05 — Software Stack Architecture

This is the proposed implementation stack. It is not a running system, and it does not choose a web framework or an HTTP library. The protocol engine is not an RGB engine. RGB and Bitcoin are optional adapters: an identity result does not require them unless the selected policy explicitly demands that proof. See [the architecture](../01-architecture.md) and [the roadmap](../13-roadmap.md).

```mermaid
flowchart TB
    WC["Clients — proposed<br/>Web · CLI · future SDK"]
    API["Protocol API — proposed<br/>entities · claims · attestations<br/>challenges · policies · proofs<br/>registry reads"]
    ENG["Protocol engine<br/>schemas · transitions<br/>canonical proof packages<br/>policy evaluator"]
    RM["Read models — not authority<br/>PostgreSQL projection<br/>Redis disposable cache<br/>object storage for proof packages"]
    ADAPT["Optional adapter<br/>RGB client-side validation<br/>Bitcoin anchor<br/>only when a policy requires it"]
    DISC["Optional discovery<br/>for example Pubky / PKARR<br/>cannot change a verification result"]

    WC --> API --> ENG
    ENG --> RM
    ENG -.-> ADAPT
    API -.-> DISC
```

## Authority boundary

```text
Signed evidence + versioned policy     AUTHORITATIVE
PostgreSQL                             REBUILDABLE PROJECTION
Redis                                  DISPOSABLE CACHE
Object storage                         PORTABLE EVIDENCE STORAGE
RGB / Bitcoin proof                    ONLY WHEN THE POLICY REQUIRES IT
Public profile / discovery             NOT A VERIFICATION INPUT BY ITSELF
```
