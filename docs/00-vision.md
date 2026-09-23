# 00 — Vision

## Purpose

O2A (Open2Artist) is an open protocol for portable identity and independently verifiable trust in the music ecosystem.

The first vertical is artists, venues, promoters, and events. The underlying identity primitive is intentionally generic so applications can reuse the same protocol without creating incompatible identity silos.

## Problem

Artist identity is fragmented across ticketing systems, DSPs, promoters, venues, social platforms, and private CRMs. An identifier issued by one platform normally proves only that the platform created a record.

O2A separates three concerns:

1. **Identity** — who controls an EntityID.
2. **Evidence** — what signed claims and attestations exist about that entity.
3. **Verification** — what a versioned policy concludes from that evidence.

## Goal

A verifier should be able to receive a portable evidence package and reproduce the same verification result without trusting the operator of a central artist database.

```text
EntityID
  + signed claims
  + independent attestations
  + challenges/revocations
  + versioned policy
           ↓
deterministic verification
```

## Non-goals

O2A v0.1 is not:

- a social network;
- a DSP identifier replacement;
- a KYC provider;
- a global reputation score;
- a new blockchain consensus mechanism;
- a ticketing or settlement product.

Those may consume O2A primitives later.

## Core principles

- **Portable:** evidence can move between compatible clients.
- **Client-verifiable:** validity is reproducible outside the registry operator.
- **Modular:** applications depend on protocol primitives, never the reverse.
- **Rebuildable:** registries are indexes over evidence, not sources of truth.
- **Explainable:** a verification result identifies the exact policy and evidence used.
- **Versioned:** schemas and policies have explicit versions and hashes.
- **Minimal on-chain footprint:** use blockchain commitments only where they add integrity or settlement value.
