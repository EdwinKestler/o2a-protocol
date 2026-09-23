# 01 — Modular Layered Architecture

This is the foundational modular architecture proposed for O2A.

```mermaid
flowchart TB
    APP["Application Modules<br/>Artist · Venue · Promoter · Event · Album registries<br/>GatePass · SplitNight · Sponsors · Merch/F&B"]
    TRUST["Trust / Policy Modules<br/>Claims · Attestations · Observations<br/>Optional challenges · evidence revocation · named policy"]
    ID["Identity Module<br/>BIP340-rooted EntityID · Controllers<br/>Recovery · Relationships · Profiles"]
    KERNEL["Required Bitcoin/RGB Identity Kernel<br/>Genesis · State · Transition · Single-use seals<br/>Consignments · Anchors · Client-side validation"]
    WALLET["Self-custodial Wallet / Node<br/>Seed · identity keys · proof packages<br/>full Bitcoin node or labeled light mode"]
    EXT["Optional Application Adapters<br/>Lightning · additional RGB rights profiles<br/>Liquid / cross-chain experiments"]

    APP --> TRUST
    TRUST --> ID
    ID --> KERNEL
    KERNEL --> WALLET
    APP -.-> EXT
```

## Dependency invariant

```text
applications → registries/trust → identity → Bitcoin/RGB identity kernel → wallet/node
```

The reverse direction is forbidden. The kernel must never import Artist,
Venue, Ticket, or SplitNight semantics. Bitcoin/RGB lifecycle validation is
mandatory for every EntityID; optional application adapters cannot redefine it.
