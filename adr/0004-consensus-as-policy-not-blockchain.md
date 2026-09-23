# ADR-0004 — Consensus as Policy, Not a New Blockchain

**Status:** Accepted for v0.1 design; Bitcoin lifecycle role clarified by
[ADR-0005](0005-bitcoin-rooted-self-custodial-identity.md)

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

Bitcoin/RGB MUST secure identity genesis and lifecycle transitions under the
v0.1 Bitcoin-native profile. Trust policy evaluates the social meaning of
signed evidence. Bitcoin consensus establishes anchor order and spent seals;
it does not vote on who owns a human-readable name.

## Consequences

Different communities may adopt different policies while sharing the same underlying evidence.

A result must always identify the policy used so two differing results can be explained rather than hidden behind a global mutable status.
