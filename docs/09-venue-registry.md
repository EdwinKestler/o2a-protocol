# 09 — Venue Registry

## Purpose

Venue identities provide an independent evidence source for artist and event relationships.
Each venue has its own BIP340-rooted EntityID and RGB lifecycle; a location or
business name is a claim about that ID, not the identifier itself.

## Suggested projection

- entity_id;
- root key and validated RGB state reference;
- official and alternate names;
- controller;
- location claims;
- hosted events;
- artist attestations;
- promoter relationships;
- verification status;
- active challenges/revocations.

## Reciprocal evidence

A venue may attest:

```text
Venue V hosted Event E
Event E included Artist A
```

An artist may independently attest:

```text
Artist A performed at Venue V during Event E
```

A promoter may independently attest:

```text
Promoter P booked Artist A at Venue V for Event E
```

These statements can cross-validate while remaining separate signed objects.

## Location

Physical location metadata is a claim. The protocol should not hard-code one geocoding provider or registry.
