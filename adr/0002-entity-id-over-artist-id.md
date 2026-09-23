# ADR-0002 — EntityID Over ArtistID

**Status:** Accepted for v0.1 design

## Context

The first product vertical is artists, but verification requires venues, promoters, organizations, and events.

## Decision

Use generic EntityID as the protocol primitive. ARTIST is an entity type.

O2A ID may be used as the product-facing identity name.

## Consequences

The protocol can model:

```text
Artist
Venue
Promoter
Organization
Event
```

without creating incompatible identifier systems.

Application APIs may expose artist-specific routes while resolving to EntityID internally.
