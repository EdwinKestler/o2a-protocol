# ADR-0003 — Catalog Is Not the Source of Truth

**Status:** Accepted for v0.1 design

## Context

Fast discovery requires an indexed database, but making that database authoritative would re-centralize identity.

## Decision

Artist, venue, and event catalogs are rebuildable projections over signed protocol evidence.

## Required test

A deployment MUST be able to destroy its registry/index and regenerate equivalent protocol-relevant projections from valid evidence/proof packages.

## Consequences

PostgreSQL, Redis, and search infrastructure can be replaced without changing identity validity.

Catalog ranking and moderation may exist, but they must not be confused with cryptographic validity or policy verification.
