# 05 — Software Stack Architecture

This is the proposed implementation stack. It is not a running system, and it
does not choose a web framework or an HTTP library. Bitcoin anchoring and RGB
client-side validation are required for the EntityID lifecycle. DNS, social,
Pubky, Nostr, databases, and application services have narrower roles. See
[the architecture](../01-architecture.md) and [the roadmap](../13-roadmap.md).

```mermaid
flowchart TB
    subgraph CLIENT["Self-custodial client — proposed"]
        UX["Wallet UI · CLI · future SDK"]
        VAULT["Encrypted local vault<br/>seed · identity/controller/event/album keys<br/>consignments · evidence · proof packages"]
        CORE["Deterministic protocol core<br/>canonical codec · BIP340 domain checks<br/>RGB validation · policy evaluator"]
        UX --> VAULT --> CORE
    end

    subgraph REQUIRED["Required identity foundation"]
        RGB["RGB identity profile<br/>genesis · transition · recovery · revocation<br/>client-side consignments"]
        BTC["Bitcoin data access<br/>anchors · seals · order · confirmations<br/>full node or explicitly labeled light mode"]
        RGB --> BTC
    end

    subgraph EDGE["Evidence and discovery adapters"]
        DNS["DNS · HTTPS · social collectors<br/>signed bounded observations"]
        PUB["Pubky / PKARR · optional Nostr<br/>bound publication keys + package locators"]
        P2P["Direct wallet exchange<br/>content-addressed proof packages"]
    end

    subgraph SERVICES["Replaceable services — never authority"]
        API["Protocol / registry API"]
        SQL["PostgreSQL / search projection"]
        CACHE["Redis disposable cache"]
        OBJ["Replicated object storage"]
    end

    CORE --> RGB
    DNS --> CORE
    PUB --> CORE
    P2P --> CORE
    CORE --> API --> SQL
    SQL --> CACHE
    P2P -.-> OBJ
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

No application framework, database, API, relay, indexer, or homeserver is
part of consensus. A future implementation may replace those components while
preserving canonical bytes, verification behavior, and wallet-held state.
