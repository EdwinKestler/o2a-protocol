# ADR-0004 — Consensus as Policy, Not a New Blockchain

**Status:** Accepted for v0.1 design

## Context

Bitcoin can establish ordering/commitment properties, but it cannot determine whether a stage-name claim corresponds to the real-world artist.

Creating a new blockchain consensus mechanism for this social fact would add complexity without solving the oracle problem.

## Decision

Identity verification is a deterministic policy evaluation over signed evidence.

```text
signed evidence
      +
versioned policy
      ↓
verification result
```

Bitcoin/RGB may secure commitments and state transitions; trust policy evaluates the meaning of evidence.

## Consequences

Different communities may adopt different policies while sharing the same underlying evidence.

A result must always identify the policy used so two differing results can be explained rather than hidden behind a global mutable status.
