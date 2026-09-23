# 06 — Development-to-Public-Release Pipeline

The proposed deployment progression adds two controlled environments between local development and production. The project is still in specification, so these stages are design targets rather than a running deployment.

```mermaid
flowchart LR
    DEV["Local Development<br/>self-custodial wallet/node<br/>Bitcoin + RGB regtest"]
    CI["CI Regtest<br/>lifecycle + recovery tests<br/>fixed conformance vectors"]
    SHR["Shared Regtest<br/>independent wallets<br/>portable consignments + proofs"]
    TEST["Public Testnet<br/>public API<br/>attack simulation<br/>registry rebuild tests"]
    BETA["Public Beta<br/>SDK<br/>independent verifier<br/>external integrations"]
    MAIN["Mainnet / Public Release<br/>Identity + Evidence + Verification"]

    DEV --> CI --> SHR --> TEST --> BETA --> MAIN
```

## Promotion model

```mermaid
flowchart LR
    GIT["Git commit SHA"] --> IMG["Signed container / binary artifact"]
    IMG --> D["dev"]
    D --> T["testnet"]
    T --> P["production"]
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
