# ADR-0002 — EntityID Over ArtistID

**Status:** Accepted for v0.1 design; identifier root amended by
[ADR-0005](0005-bitcoin-rooted-self-custodial-identity.md)

## Context

The first product vertical is artists, but verification requires venues, promoters, organizations, and events.

## Decision

Use generic EntityID as the protocol primitive. ARTIST is an entity type.
Each EntityID is rooted in its own dedicated BIP340/secp256k1 public key and
validated RGB identity history. ALBUM and EVENT are key-rooted entity types,
not only application records.

O2A ID may be used as the product-facing identity name.

## Consequences

The protocol can model:

```text
Artist
Venue
Promoter
Organization
Event
Album
```

without creating incompatible identifier systems.

Application APIs may expose artist-specific routes while resolving to EntityID internally.
