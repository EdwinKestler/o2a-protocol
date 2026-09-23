# 06 — Development-to-Public-Release Pipeline

The proposed deployment progression adds two controlled environments between local development and production.

```mermaid
flowchart LR
    DEV["Local Development<br/>Docker Compose<br/>Bitcoin regtest"]
    CI["CI Regtest<br/>unit + integration tests<br/>fixed test vectors"]
    SHR["Shared Regtest<br/>team integration<br/>seeded synthetic network"]
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
Claim
Attestation
Challenge
Revocation
Trust Policy
Artist Registry
Venue Registry
Event Registry
```

GatePass and SplitNight should follow protocol stability rather than block the first public identity release.
