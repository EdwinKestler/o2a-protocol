# ADR-0007 — Signet for the Live Demonstration

**Status:** Accepted

## Context

The live demonstration exercises an O2A wallet, an RGB identity contract, and
a dApp together. It needs public Bitcoin chain behavior with predictable,
timely confirmations. Regtest is isolated and remains the development and
evidence network. Testnet3 is being retired, and testnet4 has shown instability.
Mainnet introduces real value and operational risk and is outside the scope of
the demonstration.

## Decision

The live demonstration network is the default public Bitcoin signet using
Bitcoin Core's built-in `signetchallenge`. O2A represents it with network byte
`3` and BIP32 coin type `1'`, as specified in
[`specs/canonical-encoding.md`](../specs/canonical-encoding.md).

The demonstration uses confirmation depth `1`, as already recorded in
[`docs/phase0-agents.md`](../docs/phase0-agents.md). It operates an O2A-owned
signet Bitcoin Core node and an `electrs` instance. Public Electrum servers are
fallbacks only; they are not the primary demonstration infrastructure or a
source of protocol authority.

Regtest remains the development and evidence network. Mainnet remains out of
scope for the demonstration. A custom signet is not used unless a later ADR
names its exact challenge and records the resulting interoperability and
migration consequences.

## Consequences

- The demonstration gets public-chain behavior and timely confirmations while
  avoiding mainnet value and custody risk.
- Signet identities and their keys, state, and proofs are disposable. They do
  not become mainnet identities.
- The demonstration must operate and monitor its own signet Bitcoin Core node
  and `electrs` service. Public Electrum fallback use carries external
  availability and privacy dependencies.
- Any move to a custom signet requires a later accepted ADR that identifies its
  challenge.
- This decision does not adopt an RGB dependency lock, define the concrete O2A
  RGB program bytes, execute the outstanding RGB fixtures, or close Phase 0.
