# ADR-0016 — Route B Derivation Profile Completion

**Status:** Proposed, 2026-10-22. Not accepted. Closes Phase 0 open item 5
only after the acceptance checklist below is complete and the maintainer
accepts it.

## Context

[ADR-0009](0009-scoped-genesis-freeze.md) froze the Route B application index,
path grammar, mainnet coin type, entity allocation, and roles `0'` root, `1'`
controller, `2'` recovery, and `4'` seal for the scoped genesis format. The
[key-derivation profile](../specs/key-derivation-profile.md) leaves role `3'`
(Nostr publication), payment paths, restore/discovery, and "the rest of the
wallet profile" outside that freeze ([phase0closure.md](../docs/phase0closure.md),
item 5). Restore/discovery is handled by
[ADR-0015](0015-index-restore-and-discovery.md).

## Decision

If accepted, the remaining v0.1 profile is frozen as follows and
[`tests/vectors/route-b-profile-v0.1.json`](../tests/vectors/route-b-profile-v0.1.json)
pins it:

1. **Role `3'` Nostr publication** uses the same grammar,
   `m/coin'/entity'/3'/index'` below `xprv_o2a`, with monotonically allocated,
   never-reused indexes. The key's BIP340 x-only public key is the Nostr
   public key. O2A does not use the NIP-06 path; a Nostr client must import
   the key or implement this profile. The O2A side of the binding remains a
   discovery-binding object signed by a controller.
2. **Operational indexes** for roles `1'`–`4'` are frozen for every index in
   `0..2^31`, not only index `0'`; index allocation follows the profile and
   ADR-0015.
3. **Payment keys** are frozen as BIP86 `m/86'/coin'/account'/0/index` from
   the wallet master, not from `xprv_o2a`. They have no O2A role and never
   sign O2A objects or appear in seal scripts. `account'` is wallet-local.
4. **Path validity.** Exactly four hardened components below `xprv_o2a`;
   coin `0'` or `1'` matching the declared network; role in `0'..4'`; root
   index exactly `0'`. Anything else is invalid, including unhardened
   components and role `5'` or higher. Future roles need a new profile
   version.
5. **ADR-0015 key material** (`wallet_tag`, `mac_key`) is derived from
   `xprv_o2a` and is part of this profile.
6. Change control is unchanged: a change to any defined output requires a new
   profile version and a new wallet-root tag.

## Evidence

`tests/vectors/check_route_b_profile.py` derives 40 keys: 36 identity keys
(roles 0–4 for entities 0 and 1, indexes 0 and 1, mainnet and regtest) and 4
BIP86 payment keys. All 36 identity keys are re-derived independently by the
Rust `crypto-checker` through hardened CKD from `xprv_o2a`; the 24 that
overlap `derivation-v0.1.json` (which contains the ADR-0009 set) match it;
five invalid path shapes are rejected.

## Required evidence before acceptance

1. Maintainer confirmation that no NIP-06 compatibility is required for v0.1.
2. The demo wallet derives a role `3'` key and publishes one discovery binding
   on regtest that verifies against these vectors.

## Consequences

- Phase 0 item 5 closes on acceptance; the profile status line becomes
  "frozen v0.1". Route A (a BIP/SLIP allocation) stays available only as a new
  profile version.
- Hardware signers must implement this profile explicitly, as before.
