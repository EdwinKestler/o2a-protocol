# 10 — Event Registry

## Purpose

Events are key-rooted O2A identities and high-value evidence junctions because
multiple independent participants can attest to the same canonical manifest
and real-world occurrence.

## Suggested projection

- event EntityID;
- event root public key, custodian, and validated RGB state reference;
- venue EntityID;
- artist EntityIDs;
- promoter EntityID(s);
- time/context;
- event commitment;
- supporting attestations;
- verification state.

## Multi-party evidence

```text
Artist ── performed_at ──► Event
Venue  ── hosted ────────► Event
Promoter ─ booked ───────► Artist + Event
```

Agreement across independently controlled identities increases usable evidence without requiring one central issuer.

The event key is normally held in the responsible venue, promoter, or
organizer's wallet, with its own derivation path and recovery policy. It signs
the canonical manifest hash. Participant signatures remain separate evidence;
the event's self-signature does not prove that the event occurred.

## Scope

Ticket inventory, pricing, sales forecasts, and settlement are application data. They are not required for Event Registry identity.
