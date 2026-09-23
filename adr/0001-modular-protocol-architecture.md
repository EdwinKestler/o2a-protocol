# ADR-0001 — Modular Protocol Architecture

**Status:** Accepted for v0.1 design

## Context

O2A is intended to support identity, registries, ticketing, settlement, and future applications without creating a monolith.

## Decision

Use a layered architecture with downward-only dependencies:

```text
Applications
→ Registries
→ Trust
→ Evidence
→ Identity
→ Kernel
```

Lower layers MUST NOT depend on upper-layer domain concepts.

## Consequences

Positive:

- identity remains reusable outside ticketing;
- modules can evolve independently;
- testing boundaries are explicit;
- alternative storage and settlement adapters remain possible.

Cost:

- more explicit contracts/interfaces;
- duplicated convenience logic may need façade APIs rather than cross-layer imports.
