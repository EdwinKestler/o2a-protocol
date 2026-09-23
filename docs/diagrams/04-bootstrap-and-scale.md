# 04 — Bootstrap and Scale

## Bootstrap / how to start

```mermaid
flowchart LR
    S1["1. Define v0.1 schemas<br/>Entity · Claim · Attestation<br/>Challenge · Policy"]
    S2["2. Freeze kernel interfaces<br/>issue · validate · anchor<br/>export proof"]
    S3["3. Create first EntityIDs<br/>artists · venues · promoters"]
    S4["4. Publish signed claims<br/>official name · aliases · roles"]
    S5["5. Collect third-party attestations<br/>venue confirms performance<br/>promoter confirms booking"]
    S6["6. Run first catalog<br/>deterministic verification<br/>portable proof package"]

    S1 --> S2 --> S3 --> S4 --> S5 --> S6
```

## Scale roadmap

```mermaid
flowchart LR
    P1["Phase 1 — Pilot<br/>10–50 entities<br/>1 city / 1 venue network<br/>manual trust policy<br/>simple registry API"]
    P2["Phase 2 — Network<br/>100–1,000 entities<br/>multiple venues/promoters<br/>event registry<br/>reusable proof packages"]
    P3["Phase 3 — Products<br/>GatePass<br/>SplitNight<br/>sponsor / merch modules<br/>analytics dashboards"]
    P4["Phase 4 — Ecosystem<br/>many applications share identity layer<br/>federated registries<br/>policy versioning<br/>graph reputation after sufficient evidence<br/>optional cross-chain adapters"]

    P1 --> P2 --> P3 --> P4
```

## Scaling principle

```text
Scale by adding modules and evidence,
not by rewriting the identity layer.
```
