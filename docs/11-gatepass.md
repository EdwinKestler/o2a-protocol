# 11 — GatePass

## Status

Downstream application module; not part of the v0.1 identity kernel.

## Dependency

GatePass consumes:

- the participant EntityID;
- the key-rooted EVENT EntityID and validated RGB state;
- the venue EntityID;
- protocol validation and proof-package interfaces.

It must not implement a parallel identity system.

## Conceptual lifecycle

```text
ISSUED → TRANSFERRED → VALID → REDEEMED
```

The ticket/application layer may add class, ownership, transfer, redemption, and admission semantics.

## Architectural rule

```text
GatePass → O2A Protocol

O2A Protocol ✗→ GatePass
```

This keeps the identity protocol reusable by applications unrelated to ticketing.
