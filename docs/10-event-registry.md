# 10 — Event Registry

## Purpose

Events are high-value evidence junctions because multiple independent participants can attest to the same real-world occurrence.

## Suggested projection

- event EntityID;
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

## Scope

Ticket inventory, pricing, sales forecasts, and settlement are application data. They are not required for Event Registry identity.
