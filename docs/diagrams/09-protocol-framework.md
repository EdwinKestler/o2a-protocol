# 09 — Protocol Framework and Authority Boundaries

This framework view shows what each subsystem can prove and which components
remain replaceable. Solid arrows point from a dependent operation to the
prerequisite it must validate or consume; they do not transfer authority.

```mermaid
flowchart LR
    subgraph CUSTODY["Owner-controlled custody"]
        ROOT["Immutable EntityID root<br/>dedicated BIP340 key"]
        CTRL["Rotatable controllers<br/>recovery policy · revocation"]
        LOCAL["Wallet/node storage<br/>seed · keys · consignments<br/>evidence · proof packages"]
        ROOT --> CTRL
        LOCAL --> ROOT
        LOCAL --> CTRL
    end

    subgraph STATE["Consensus-ordered identity state"]
        BTC["Bitcoin<br/>order · anchors · seals"]
        RGB["RGB client-side validation<br/>identity schema + history"]
        RGB -->|"checks anchors and seals against"| BTC
    end

    subgraph EVIDENCE["Public evidence layer"]
        SIGNED["Purpose-domain signatures<br/>claims · attestations · challenges<br/>event/album manifests"]
        OBS["Signed observations<br/>DNS · HTTPS · social control"]
        PKG["Content-addressed proof package<br/>public history shard · Bitcoin proofs<br/>evidence boundary · policy · context"]
        SIGNED --> PKG
        OBS --> PKG
    end

    subgraph VERIFY["Independent verification"]
        CHECK["Check package hash<br/>Bitcoin proofs · RGB history<br/>publisher key · package signature · domain"]
        POLICY["Run named versioned policy<br/>show conflicts + missing evidence"]
        RESULT["Explained result<br/>same inputs => same output"]
        CHECK --> POLICY --> RESULT
    end

    subgraph VIEWS["Replaceable views and applications"]
        DISC["Discovery<br/>direct exchange · HTTPS<br/>Pubky · optional Nostr"]
        REG["Rebuildable registries<br/>artist · venue · promoter<br/>event · album"]
        APP["Applications<br/>GatePass · SplitNight<br/>paid-use · catalogs"]
        DISC --> REG --> APP
    end

    CTRL --> RGB
    RGB --> PKG
    CTRL --> SIGNED
    PKG --> CHECK
    DISC -. "find bytes only" .-> PKG
    RESULT --> REG
```

## What each boundary establishes

| Boundary | Establishes | Does not establish |
| --- | --- | --- |
| Bitcoin | transaction order, confirmations, commitments, spent seals | who is the real artist or owner of a spoken name |
| RGB | validity of the supplied O2A identity state transition history | truth of DNS, social, event, album, or relationship claims |
| BIP340 O2A signature | authorship and integrity in one purpose-specific domain | exclusive name ownership or signer independence |
| Evidence policy | an explained result over explicit evidence and context | authority to rewrite identity history |
| Discovery and registries | finding packages and presenting rebuildable views | identity, consensus, or verification authority |

The immutable root identifies the EntityID. Controller keys authorize ordinary
operations and can rotate under validated RGB state. Bitcoin spending keys,
Pubky Ed25519 keys, Nostr publication keys, and payment endpoints remain
separate and may only be connected through explicit signed bindings.
