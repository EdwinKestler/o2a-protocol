# ADR-0006 — Route B Key Derivation via BIP85

**Status:** Accepted

## Context

The earlier candidate identity path used BIP43 purpose `827'`, but that value
has no BIP or SLIP allocation. O2A needs collision-safe separation between
identity keys and payment keys without claiming an unassigned BIP43 purpose.
Third-party hardware-wallet derivation is not required in the near term.

All seven derivation evidence gates are satisfied. Three independent
implementations agree on the defined outputs. Every identity created during
the demonstration is disposable, so no persistent identity depends on the
profile already being immutable.

## Decision

O2A Route B v0.1 uses BIP85's BIP32-XPRV application `32'` with
`O2A_INDEX = 998536622`. The index is computed as
`tagged_hash("O2A/v0.1/wallet-root", empty)[0..4]`, interpreted as a
big-endian `u32` and shifted right by one bit. The resulting independent
`xprv_o2a` carries the fully hardened identity subtree specified in
[`specs/key-derivation-profile.md`](../specs/key-derivation-profile.md).
Bitcoin payment keys remain BIP86 keys below the wallet master tree; they are
not derived below `xprv_o2a` and never sign O2A objects.

The Route B profile is designated **demo-stable v0.1**. Its mainnet freeze is
deferred. The defined v0.1 outputs do not change without a deliberate,
versioned decision. Freeze remains a maintainer action, recorded by ADR, when
a mainnet-capable release is in scope.

## Consequences

- Generic hardware wallets do not derive O2A keys unaided. A compatible
  signer must explicitly implement the BIP85 application, O2A index, network
  mapping, and hardened identity subtree.
- Route A—requesting a BIP or SLIP allocation—remains available later without
  changing EntityIDs for any identity not yet derived persistently.
- Outputs for every path defined by v0.1 remain stable within v0.1.
- A change to any defined path or to the index derivation requires a new
  profile version and a new tagged-hash label, such as
  `O2A/v0.2/wallet-root`; that change produces a distinct `xprv_o2a`.
- Demo identities remain disposable. This decision does not authorize
  persistent production identities, adopt an RGB lock, or close Phase 0.
