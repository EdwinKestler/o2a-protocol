# Entity Schema — Draft v0.1

## Status

Draft. This document defines semantic fields; canonical binary encoding is still TBD.

## Object

```json
{
  "protocol_version": "0.1",
  "object_type": "entity",
  "entity_id": "<derived-or-committed-id>",
  "entity_type": "ARTIST",
  "controller": {
    "scheme": "<scheme>",
    "key": "<public-controller-material>"
  },
  "sequence": 0,
  "previous_state": null,
  "profile_commitment": null,
  "status": "ACTIVE",
  "context": "<network-or-anchor-context>"
}
```

## Requirements

- `entity_id` MUST be stable across controller rotation.
- `sequence` MUST monotonically advance for mutable state.
- transitions MUST reference the previous valid state.
- controller changes MUST be authorized by the previous controller state.
- canonical serialization MUST exclude transport-only metadata.
- human-readable profiles SHOULD remain separable from identity-critical state.

## Initial entity types

```text
PERSON
ARTIST
BAND
VENUE
PROMOTER
ORGANIZATION
EVENT
```

Unknown future types require version-aware handling rather than silent coercion.
