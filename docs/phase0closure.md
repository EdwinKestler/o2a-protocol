# Phase 0 status report

## Status — 2026-09-28

**Phase 0 remains open.** This is a current status report, not a closure
declaration. The demonstration lineage is now the intended path for producing
the remaining disposable RGB evidence without turning demo artifacts into
normative program bytes, persistent identities, or an adopted dependency lock.
[ADR-0008](../adr/0008-genesis-bound-entity-id.md) is accepted.
[ADR-0009](../adr/0009-scoped-genesis-freeze.md) and
[ADR-0010](../adr/0010-rgb-carrier-line.md) are accepted. The scoped genesis
format is frozen, and rgb-protocol v0.11.1 with Opret is the accepted carrier
line for first transitions while O2A genesis stays RGB-line-agnostic. The
required v0.11.1 regtest lineage and signet rehearsal are complete. No
production or mainnet identity network is running, and these acceptances are
not a mainnet-readiness claim.

## Settled

- Route B v0.1 key derivation is **demo-stable** under
  [ADR-0006](../adr/0006-route-b-key-derivation-via-bip85.md). All seven
  derivation evidence gates are satisfied; mainnet freeze is deferred.
- O2A-CANON-1 defines the canonical primitive and container encoding.
- ADR-0008 fixes the Draft v0.1 EntityID as the tagged hash of the canonical
  root-signed genesis payload; it does not close the mainnet or RGB gates.
- ADR-0009 freezes the canonical genesis/`official_name` surface, the
  signer-independent O2A state ID, mainnet network byte and confirmation depth,
  and Route B format for roles 0, 1, 2, and 4.
- ADR-0010 selects rgb-protocol v0.11.1 and Opret. Its acceptance evidence
  includes the maintained adapter, a 47-file regtest lineage, and a 26-file
  signet rehearsal.
- Canonical layouts and signing domains exist for all twelve signed objects.
- The Python protocol/vector checker and the independent locked Rust
  cryptographic checker exercise the retained conformance fixtures.
- O2A-authored work is `MIT OR Apache-2.0`; conformance vectors are CC0-1.0;
  the accepted dependency-license policy and reviewed `hex_lit 0.1.1` entry
  are recorded in [the license assessment](22-license-and-adoption-assessment.md).
- The accepted first-transition consumer is the isolated rgb-protocol v0.11.1
  adapter. It uses Opret, bridges duplicate secp256k1 types through bytes, and
  does not use `rgb-lib` for seal custody.
- The live demonstration network is the default public Bitcoin signet under
  [ADR-0007](../adr/0007-signet-for-demonstration.md). Regtest remains the
  development and evidence network.

## Open items

1. Concrete O2A RGB program/codex/schema bytes and identifiers.
2. Adoption of the exact production-workspace dependency lock.
3. Transition and recovery payload freeze, custody-transfer operation 4, and
   the remaining lifecycle and adversarial conformance cases beyond the
   accepted bounded regtest/signet evidence.
4. Restore/discovery rules for allocated entity and role indexes.
5. The derivation profile outside frozen Route B roles 0, 1, 2, and 4.
6. Wider evidence, discovery, music-object, package, and chain conformance.
7. Production wallet, release, and mainnet operational readiness.

## Gates closed by ADR-0009 and ADR-0010

ADR-0009 closes the canonical genesis/`official_name` compatibility surface,
the signer-independent O2A-native
`TaggedHash(state-id, EntityID || resulting_state)` rule, the mainnet network
byte and depth, and the Route B mainnet derivation-format gate for roles 0, 1,
2, and 4. Its frozen manifest makes those exact outputs regression-testable.

ADR-0010 closes the RGB-line and commitment-carrier choice for first
transitions: rgb-protocol v0.11.1 with Opret. Its pre-acceptance gates are also
closed: the maintained adapter is merged in the demo repository, the named
regtest lineage and signet rehearsal pass, and the maintainer reviewed the
license register.

Neither ADR closes the concrete O2A program/codex/schema bytes, transition or
recovery payload formats, operations 2 or 4, custody-transfer acceptance,
restore/discovery, the production dependency lock, wider conformance, a
production wallet, or mainnet operations. Until the concrete program and
remaining transition rules are adopted, no frozen-format identity may make a
transition. Re-issuing its pre-transition RGB contract with the same O2A
genesis and seal preserves the EntityID and state 0 ID.

The accepted adapter, regtest lineage, and signet rehearsal were produced as
disposable evidence by `../o2a-testnet-demo` under the
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

The archived 0.12 RC3 evidence remains part of the historical decision record;
it is not the selected first-transition line under ADR-0010.

The restore/discovery item is separate from deterministic key derivation. A
mnemonic can reproduce keys only after the wallet knows which `entity'` and
per-role indexes to derive, and it cannot reproduce genesis-bound EntityIDs
without retained genesis payloads or consignments. The source and verification
rule for rebuilding that material remain unspecified.

## Current checks

- `python3 tests/vectors/check_vectors.py` prints `ok`.
- `python3 tests/vectors/check_protocol_objects.py` prints
  `protocol objects ok`.
- `python3 tests/vectors/check_genesis_freeze.py` reports all 63 frozen outputs
  unchanged. The manifest's original status label is itself frozen vector data.
- Palimnex deep validation and the evaluation suite must pass after document
  updates. Ledger integrity must remain healthy; stale historical verification
  records are reported rather than treated as current evidence.
