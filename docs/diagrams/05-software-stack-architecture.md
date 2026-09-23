# 05 — Software Stack Architecture

This is the proposed implementation stack.

```mermaid
flowchart TB
    WC["Web / Clients<br/>Next.js / TypeScript · CLI · future mobile SDK"]
    API["Protocol API<br/>Rust + Axum<br/><br/>/entities · /claims · /attestations<br/>/challenges · /policies · /proofs<br/>/artists · /venues · /events"]
    ENG["RGB Identity Engine<br/>RUST<br/><br/>entity · claims · attestations<br/>challenge · revocation · policy evaluator<br/>proof package / canonical serialization"]
    RGB["RGB / Bitcoin<br/>RGB Core<br/>RGB std/API<br/>BP libraries"]
    RM["Read Models<br/>PostgreSQL<br/>Redis optional<br/>S3-compatible proof storage"]
    BTC["Bitcoin<br/>Regtest · Testnet · Mainnet<br/><br/>Esplora / Electrum"]

    WC -->|"REST / JSON"| API
    API --> ENG
    ENG --> RGB
    ENG --> RM
    RGB --> BTC
```

## Authority boundary

```text
Protocol / signed evidence     AUTHORITATIVE
PostgreSQL                     REBUILDABLE PROJECTION
Redis                          DISPOSABLE CACHE
Object storage                 PORTABLE EVIDENCE STORAGE
```
