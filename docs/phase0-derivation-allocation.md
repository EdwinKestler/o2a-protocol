# Phase 0 identity derivation allocation

**Status:** open decision record, 2026-09-23. This note does not allocate or
freeze a BIP32 purpose.

O2A needs deterministic wallet separation between root identity, controller,
recovery, Nostr-publication, and Bitcoin payment keys. The path shape in
O2A-CANON-1 records those roles, but the earlier literal purpose `827'` has no
accepted interoperability allocation in this repository. It is provisional
test data and must not ship as a frozen wallet convention.

## Candidate shape

```text
m/purpose'/coin'/account'/0'/0'       root identity
m/purpose'/coin'/account'/1'/index'   controller
m/purpose'/coin'/account'/2'/index'   recovery
m/purpose'/coin'/account'/3'/index'   Nostr publication
m/86'/coin'/account'/0/index          Bitcoin payment
```

Pubky remains outside this hierarchy because its key is Ed25519. A payment key
has no O2A key role or O2A key identifier and must never sign an O2A object.

## Acceptance gate

The identity `purpose'` becomes normative only after all of these are recorded:

1. a collision review against existing BIP43 application purposes;
2. the allocation or standards mechanism used by independent wallets;
3. two independent derivations from the same public, unsafe test mnemonic;
4. distinct expected public keys for root, controller, recovery, Nostr, and
   BIP86 payment paths on mainnet and test networks;
5. invalid-case vectors for unhardened identity roles, cross-role key use,
   wrong coin type, and payment-key use in an O2A signature; and
6. regeneration of every provisional `827'` fixture.

If a collision-safe shared allocation cannot be obtained, Phase 0 must choose
and document another interoperable derivation mechanism before freezing the
wallet profile. Local use of `827'` is not sufficient evidence.

## Collision review — 2026-09-23

BIP43 says a new scheme should use its BIP number as the hardened purpose so
wallet trees do not overlap. Purposes `10001'` through `19999'` are reserved
for SLIPs. Deployed Bitcoin purposes that this profile must not reuse include
`44'`, `45'`, `48'`, `49'`, `84'`, and `86'`. Payment keys already use `86'`.

Purpose `827'` is not an assigned BIP. No BIP or SLIP number was requested or
granted in this pass. The allocation gate therefore stays **open**. `827'`
remains provisional test data and is not an interoperable wallet convention.

## Effect on current work

EntityID derivation from an already supplied root public key is specified and
testable. Seed-to-root wallet derivation is not. Implementations may use
explicit public test keys while working on canonical bytes, but must not create
persistent identities whose recovery depends on the provisional path.
