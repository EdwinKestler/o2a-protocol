# 03 — Entity Identity

## EntityID

EntityID is the canonical subject identifier.

Domain categories such as ARTIST and VENUE are entity types, not independent identity systems.

Suggested initial types:

- PERSON
- ARTIST
- BAND
- VENUE
- PROMOTER
- ORGANIZATION
- EVENT

## Minimal state

An entity contains:

- protocol version;
- entity type;
- controller or controller set;
- creation commitment/time reference;
- optional profile commitment;
- status;
- previous-state reference when updated.

## Controller authorization

A controller is authorized to create state transitions for the entity. A valid transition must prove authorization under the previous valid controller state.

## Key rotation

Controller rotation MUST NOT change EntityID.

Historical signatures remain verifiable against the controller state valid at their issuance point.

## Human-facing identity

O2A may expose a friendly O2A ID while internally retaining EntityID as the generic protocol type.

```text
O2A ID (product-facing)
        ↓
EntityID (protocol primitive)
```

This allows the artist-focused go-to-market to coexist with generic protocol semantics.
