# 06 — Development-to-Public-Release Pipeline

The proposed deployment progression adds two controlled environments between local development and production. The project is still in specification, so these stages are design targets rather than a running deployment.

```mermaid
flowchart LR
    P0["Phase 0 — freeze specification<br/>canonical encoding · signing domains<br/>RGB stack/commitment method · vectors<br/>Apache-2.0 accepted"]
    P1["Phase 1 — deterministic core<br/>Bitcoin/RGB regtest lifecycle<br/>positive + adversarial vectors"]
    P2["Phase 2 — wallet/node<br/>local custody · backup/recovery<br/>proof export/import · full/light modes"]
    P3["Phase 3 — discovery/testnet<br/>DNS/social observations · Pubky/Nostr<br/>collisions · registry rebuild · interop"]
    P4["Phase 4 — beta/mainnet v1<br/>version-pinned wallet · CLI · SDK<br/>security review · reproducible releases"]
    P5["Phase 5+ — applications/research<br/>GatePass · paid-use · SplitNight<br/>federation · reputation"]

    P0 -->|"spec gate"| P1
    P1 -->|"conformance gate"| P2
    P2 -->|"custody + recovery gate"| P3
    P3 -->|"interop + discovery gate"| P4
    P4 -->|"identity v1 stable"| P5
```

Each gate is evidence-based. A later phase does not retroactively make an
earlier local test, simulation, or design document a deployed protocol.

## Promotion model

```mermaid
flowchart LR
    GIT["Reviewed Git commit SHA"] --> BUILD["Reproducible build"]
    BUILD --> SBOM["Signed artifact + provenance / SBOM"]
    SBOM --> D["dev / regtest"]
    D --> T["public testnet"]
    T --> P["mainnet release"]
```

The intended discipline is to promote the same tested artifact rather than rebuilding a different production binary.

## First mainnet scope

```text
Entity
RGB identity lifecycle
Bitcoin anchors and seals
Claim
Attestation
Challenge
Revocation
Trust Policy
Artist Registry
Venue Registry
Event Registry
Album Registry
```

GatePass and SplitNight should follow protocol stability rather than block the first public identity release.
