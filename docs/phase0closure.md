# Phase 0 status report

## Status — 2026-09-28

**Phase 0 remains open.** This is a current status report, not a closure
declaration. The demonstration lineage is now the intended path for producing
the remaining disposable RGB evidence without turning demo artifacts into
normative program bytes, persistent identities, or an adopted dependency lock.
[ADR-0008](../adr/0008-genesis-bound-entity-id.md) is accepted.
[ADR-0009](../adr/0009-scoped-genesis-freeze.md) remains proposed. The bounded
path toward a first mainnet identity is to accept ADR-0009, complete the signet
dress rehearsal that is now **IN PROGRESS**, and only then consider a mainnet
genesis gated on that acceptance. This sequence is not a mainnet-readiness
claim.

## Settled

- Route B v0.1 key derivation is **demo-stable** under
  [ADR-0006](../adr/0006-route-b-key-derivation-via-bip85.md). All seven
  derivation evidence gates are satisfied; mainnet freeze is deferred.
- O2A-CANON-1 defines the canonical primitive and container encoding.
- ADR-0008 fixes the Draft v0.1 EntityID as the tagged hash of the canonical
  root-signed genesis payload; it does not close the mainnet or RGB gates.
- Canonical layouts and signing domains exist for all twelve signed objects.
- The Python protocol/vector checker and the independent locked Rust
  cryptographic checker exercise the retained conformance fixtures.
- O2A-authored work is `MIT OR Apache-2.0`; conformance vectors are CC0-1.0;
  the accepted dependency-license policy and narrow exceptions are recorded
  in [the license assessment](22-license-and-adoption-assessment.md).
- The RGB consumer shape is `rgb-runtime` with
  `default-features = false` and features `resolver-electrum` and `fs`.
  `rgb-wallet` is not an O2A dependency.
- The live demonstration network is the default public Bitcoin signet under
  [ADR-0007](../adr/0007-signet-for-demonstration.md). Regtest remains the
  development and evidence network.

## Open items

1. RGB 0.12 final stack for mainnet.
2. Concrete O2A RGB program bytes.
3. RGB execution fixtures.
4. Custody acceptance over real prior state.
5. Restore/discovery rule.
6. Mainnet freeze of the derivation profile.
7. Lock adoption after items 2–4.

## Proposed ADR-0009 scoped freeze

ADR-0009 is **Proposed**, not accepted. If accepted before the first mainnet
mint, it closes only the canonical genesis/`official_name` compatibility
surface, the signer-independent O2A-native
`TaggedHash(state-id, EntityID || resulting_state)` rule, the mainnet network
byte and depth, and the Route B mainnet derivation-format gate for roles 0, 1,
2, and 4. Its frozen manifest makes those exact outputs regression-testable.

It does not close the final RGB stack, concrete RGB program/codex/schema,
commitment carrier, transition or recovery execution, operations 2 or 4,
custody evidence, restore/discovery, dependency lock, or wider conformance
gates. No transition from a frozen-format identity is permitted until the RGB
stack is final. Re-issuing the pre-transition RGB contract with the same O2A
genesis and seal preserves the O2A EntityID and state 0 ID.

Items 2–4 are produced as disposable evidence by `../o2a-testnet-demo` under
the demo lineage permitted by the
[dependency gate](phase0-dependency-gate.md). This is the intended Phase 0
closure path, not a detour. Demo program bytes and identities remain
disposable; evidence from that repository informs the later normative and
dependency decisions but does not make them implicitly.

**Seal-policy lineage note:** the 2026-09-24 demonstration lineage predates the
role-4 seal policy and deterministic controller-or-delayed-recovery P2TR
script. Later disposable regtest lineages exercise that policy, matching seal
outputs, stale bindings, delay, closure, reorg, and genesis-bound identifiers;
see the supporting [scenario matrix](25-scenario-matrix.md). Those runs do not
close Phase 0, adopt program bytes, or turn demo identities into persistent
protocol state.

The restore/discovery item is separate from deterministic key derivation. A
mnemonic can reproduce keys only after the wallet knows which `entity'` and
per-role indexes to derive, and it cannot reproduce genesis-bound EntityIDs
without retained genesis payloads or consignments. The source and verification
rule for rebuilding that material remain unspecified.

## Current checks

- `python3 tests/vectors/check_vectors.py` prints `ok`.
- `python3 tests/vectors/check_protocol_objects.py` prints
  `protocol objects ok`.
- `python3 tests/vectors/check_genesis_freeze.py` reports all proposed frozen
  outputs unchanged while ADR-0009 remains proposed.
- Palimnex deep validation and the evaluation suite must pass after document
  updates, and ledger status must remain healthy with no stale verifications.
