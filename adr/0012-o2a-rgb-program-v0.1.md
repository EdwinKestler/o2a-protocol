# ADR-0012 — O2A RGB Program v0.1 on rgb-protocol 0.11.1

**Status:** Proposed, 2026-10-22. Not accepted. Closes Phase 0 open item 1
only after the acceptance checklist below is complete and the maintainer
accepts it.

## Context

[ADR-0010](0010-rgb-carrier-line.md) selects rgb-protocol v0.11.1 and Opret for
first transitions but leaves the concrete O2A program/schema bytes open
([phase0closure.md](../docs/phase0closure.md), item 1). Under
[ADR-0009](0009-scoped-genesis-freeze.md) no frozen-format identity may
transition until that program is adopted.

The only 0.11.1 schema so far is the disposable demo schema `O2aIdentity`
(`o2a-testnet-demo/spikes/rgb-0.11.1/check/src/schema.rs`, schema id
`rgb:sch:oqE1HKzG_NrzhV2M0tn~mkfJfic5ztF6iUr8s8YbdDE#ivan-robin-exotic`).
Review for this ADR found two defects that rule out adopting it unchanged:

1. **Its transitions carry no O2A digest.** Genesis records the 32-byte
   genesis digest as global state, but the `rotate`, `recover`, and `revoke`
   transitions declare no global state. The signed O2A transition object
   travels beside the consignment. The anchor therefore does not commit to
   which O2A payload closes the seal, contrary to the
   [identity contract](../specs/rgb-identity-contract.md) ("Seal and anchor"):
   a controller that signs two different successors for the same prior state
   could pair either one with the same mined anchor.
2. **Its `revoke` transition has no owned output,** while every O2A resulting
   state, including REVOKED, names a mandatory `next_seal`
   ([O2A-CANON-1](../specs/canonical-encoding.md), "Resulting identity state").
   The RGB history and the O2A state would then disagree about the current
   seal.

## Decision

If accepted, the O2A RGB program v0.1 is exactly the following, built by
`program_v01.rs` in the demo repository and pinned by
[`tests/vectors/rgb-program-v0.1.json`](../tests/vectors/rgb-program-v0.1.json):

| Item | Value |
| --- | --- |
| RGB line / close method | rgb-protocol 0.11.1 / Opret (`opret1st`), per ADR-0010 |
| Type library | `O2AIdentityV01`, id `stl:97gbFI0s-rEf6LLT-HHm3fnw-iN9kack-y0azYjy-QpNSjSU#everest-meteor-student` |
| Strict type | `O2aDigest([u8; 32])` |
| Schema name | `O2aIdentityV01` |
| Schema id | `rgb:sch:0c4GOQpl9wgzWtkBQqf4ULj~1Xp~TkJj0Ger~0CLB6A#subway-october-region` |
| Schema strict bytes | 228 bytes, SHA-256 `ee097382b2de46bfd406d63fd7114cffe368ecea0ab747412540fb0596d9536e` |
| Type system | id `sts:HXgdkDPU-LhVdKYi-jTAirsR-M3zmamx-jL76eBD-jyonuV8#mobile-version-chant`, 170 bytes, SHA-256 `1d78ee0d71eb9291b70eef4458042029b994327f72f0ead63efc2c649e2c8489` |
| Global `3101` `genesisDigest` | `Once` in genesis only |
| Global `3102` `transitionDigest` | `Once` in every transition |
| Owned `4101` `identity` | `Declarative`, default transition `8101`, `Once` in genesis and every transition output |
| Transition `8101` `transition` | O2A operations 1, 2, 4, and 5 |
| Transition `8102` `recover` | O2A operation 3 |
| Validators | none (genesis and transitions) |

Normative rules:

1. `genesisDigest` MUST equal `TaggedHash("O2A/v0.1/entity-genesis",
   genesis_payload)` for the history's canonical genesis payload.
2. Every transition MUST carry exactly one `transitionDigest` equal to the
   anchor digest of the O2A object it carries: for type `8101`,
   `TaggedHash("O2A/v0.1/identity-transition", transition payload)`; for type
   `8102`, the recovery anchor digest defined by ADR-0014. An O2A verifier MUST
   recompute it and reject the history on absence, duplication, or mismatch,
   whatever RGB validation reports. The 0.11.1 transition builder does not
   enforce the `Once` occurrence itself (recorded in the evidence below).
3. The transition type MUST match the O2A domain: `8101` with
   `O2A/v0.1/identity-transition` (operation 1, 2, 4, or 5); `8102` with
   `O2A/v0.1/recovery` (operation 3). Any other pairing is invalid.
4. Every transition, including revocation, MUST assign `identity` to the
   blinded output that is the O2A `next_seal`. REVOKED is terminal in the O2A
   layer: after a valid revocation reaches the required depth, verification
   reports REVOKED and no later spend of that seal changes the result.
5. RGB identifiers (contract, schema, operation, assignment, consignment)
   MUST NOT replace or enter an O2A EntityID or state ID (ADR-0010 item 2).
6. ADR-0010's C6/C7 rule stands: `CURRENT` still requires the evaluation
   context's current-seal observation.

The demo schema `O2aIdentity` stays disposable evidence and MUST NOT be used
for a frozen-format identity transition.

## Options considered

- **Adopt the demo schema as is.** Rejected for the two defects above; existing
  evidence would carry over, but the digest gap is a commitment-binding flaw.
- **One transition type per O2A operation (five types).** Adds no RGB-level
  check while validators are unset, and enlarges the schema. Rejected for v0.1.
- **Two types split by signing domain (selected).** Keeps the recovery path
  distinguishable in RGB tooling and matches the two O2A anchor domains.

## Evidence (candidate, disposable)

`o2a-testnet-demo` commit `5ffc48a` (branch `feat/o2a-program-v0.1`), bundle
`evidence/program-v01-candidate-2026-10-22/`:

- `program-dump.json`: output of `rgb011-check program-dump`, byte-identical
  across two runs;
- `cargo-test-program_v01.txt`: five unit tests pass — determinism, distinct
  from the demo schema id, genesis plus both transition types carry digests,
  unknown transition names refused before the upstream panic, and the
  builder-without-digest outcome (`is_err=false`) recorded.

These are offline build results. No transition on this program has been mined.

## Required evidence before acceptance

1. A disposable regtest lineage on this exact schema id: genesis, operations
   1, 2, 3, 4, and 5, consignment validation after each, and a negative case
   whose transition omits or alters `transitionDigest` that the O2A verifier
   rejects (and a record of what RGB validation reports for it).
2. A signet rehearsal of genesis plus one operation-1 transition on this
   schema id.
3. ADR-0013 (dependency lock) and ADR-0014 (transition formats, including the
   recovery anchor digest) accepted or accepted together.
4. Maintainer review of this ADR and of the vector file.

## Consequences

- Phase 0 item 1 closes on acceptance; the frozen-format transition ban in
  ADR-0009 lifts only when ADR-0013 and ADR-0014 are also accepted.
- The 0.11.1 demo schema evidence remains valid history for ADR-0010 but is
  not evidence for this program.
- Upstream note: rgb-consensus 0.11.1 panics on an unknown transition name
  instead of returning an error (`schema/schema.rs:357`).
