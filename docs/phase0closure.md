# Phase 0 status report

## Status — 2026-09-24

**Phase 0 remains open.** This is a current status report, not a closure
declaration. The demonstration lineage is now the intended path for producing
the remaining disposable RGB evidence without turning demo artifacts into
normative program bytes, persistent identities, or an adopted dependency lock.

## Settled

- Route B v0.1 key derivation is **demo-stable** under
  [ADR-0006](../adr/0006-route-b-key-derivation-via-bip85.md). All seven
  derivation evidence gates are satisfied; mainnet freeze is deferred.
- O2A-CANON-1 defines the canonical primitive and container encoding.
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

Items 2–4 are produced as disposable evidence by `../o2a-testnet-demo` under
the demo lineage permitted by the
[dependency gate](phase0-dependency-gate.md). This is the intended Phase 0
closure path, not a detour. Demo program bytes and identities remain
disposable; evidence from that repository informs the later normative and
dependency decisions but does not make them implicitly.

**2026-09-25 seal-policy note:** the existing demonstration lineage predates
the role-4 seal policy and deterministic controller-or-delayed-recovery P2TR
script. It must adopt that policy and prove matching seal outputs before its
RGB execution or custody-acceptance artifacts count as evidence for items 3
and 4. This note does not close Phase 0, adopt program bytes, or modify the
demo repository.

The restore/discovery item is separate from deterministic key derivation. A
mnemonic can reproduce keys only after the wallet knows which `entity'` and
per-role indexes to derive. The source and verification rule for rebuilding
that allocation set remain unspecified.

## Current checks

- `python3 tests/vectors/check_vectors.py` prints `ok`.
- `python3 tests/vectors/check_protocol_objects.py` prints
  `protocol objects ok`.
- Palimnex deep validation and the evaluation suite must pass after document
  updates, and ledger status must remain healthy with no stale verifications.
