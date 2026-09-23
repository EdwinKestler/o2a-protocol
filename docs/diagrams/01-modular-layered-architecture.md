# 01 — Modular Layered Architecture

This is the foundational modular architecture proposed for O2A.

```mermaid
flowchart TB
    APP["Application Modules<br/>Artist Catalog · Venue Registry · Event Registry<br/>GatePass · SplitNight · Sponsors · Merch/F&B"]
    TRUST["Trust / Policy Modules<br/>Claims · Attestations · Endorsements<br/>Challenges · Revocation · Reputation"]
    ID["Identity Module<br/>EntityID · Keys · Profiles · Controllers<br/>Relationships · Key Rotation"]
    KERNEL["Protocol Kernel<br/>Schema · Genesis · State · Transition<br/>Consignment · Client-side Validation · Proofs"]
    SETTLE["Settlement / Anchoring Adapters<br/>Bitcoin UTXO · RGB · optional Liquid / cross-chain adapters"]

    APP --> TRUST
    TRUST --> ID
    ID --> KERNEL
    KERNEL --> SETTLE
```

## Dependency invariant

```text
applications → registries/trust → identity → kernel → settlement adapters
```

The reverse direction is forbidden. The kernel must never import Artist, Venue, Ticket, or SplitNight semantics.
