# 27 — Artifact inventory

**Status:** supporting inventory updated 2026-09-29 from protocol base
`86eb527`. It introduces no protocol rule. Git and the named files remain
authoritative; branch tips below retain their dated audit observation and may
move.

## Architecture decisions

| ADR | Status | First / governing commit | Scope |
| --- | --- | --- | --- |
| [0001](../adr/0001-modular-protocol-architecture.md) | Accepted for v0.1 design; amended | `6a95f78` | Modular architecture |
| [0002](../adr/0002-entity-id-over-artist-id.md) | Accepted for v0.1 design; amended | `a44be59` | EntityID as the cross-entity identifier |
| [0003](../adr/0003-catalog-is-not-source-of-truth.md) | Accepted for v0.1 design; amended | `57dfe3c` | Registries are projections |
| [0004](../adr/0004-consensus-as-policy-not-blockchain.md) | Accepted for v0.1 design; clarified | `423f607` | Recognition is policy, not chain consensus |
| [0005](../adr/0005-bitcoin-rooted-self-custodial-identity.md) | Accepted; amended by ADR-0008 | `cc2a35b`; amendment in `38d9bd5` | Bitcoin-rooted identity and custody |
| [0006](../adr/0006-route-b-key-derivation-via-bip85.md) | Accepted | `8b19c28` | Demo-stable Route B derivation |
| [0007](../adr/0007-signet-for-demonstration.md) | Accepted; amended by ADR-0011 | `3ca98ea` | Default public signet for disposable demonstrations |
| [0008](../adr/0008-genesis-bound-entity-id.md) | Accepted, 2026-09-28 | `38d9bd5`; merge `0ef16c2` | Genesis-bound EntityID and pending confirmation |
| [0009](../adr/0009-scoped-genesis-freeze.md) | Accepted, 2026-09-28 | `cabae9b`; merge `b622c98`; maintainer acceptance | Scoped genesis / `official_name` freeze and O2A state ID |
| [0010](../adr/0010-rgb-carrier-line.md) | Accepted, 2026-09-28 | Proposal merge `0a8d54f`; acceptance evidence at demo `48fd5db` | rgb-protocol v0.11.1 with Opret for first transitions |
| [0011](../adr/0011-network-as-configuration.md) | Accepted, 2026-09-29 | Maintainer decision, 2026-09-29 | One regtest/signet/mainnet profile with a per-session mainnet lock |

## Normative specifications changed since `c7b0871`

`git diff --name-only c7b0871..b622c98 -- specs` reports:

| Path | Reason for post-`c7b0871` change |
| --- | --- |
| `specs/attestation-schema.md` | O2A-native state-ID references |
| `specs/canonical-encoding.md` | Genesis-bound EntityID, zero genesis signer, O2A state ID |
| `specs/challenge-schema.md` | O2A-native state-ID references |
| `specs/claim-schema.md` | O2A-native authorizing state |
| `specs/control-proof-schema.md` | O2A-native state-ID references |
| `specs/cryptographic-profile.md` | State-ID tagged-hash domain |
| `specs/discovery-binding-schema.md` | O2A-native state-ID references |
| `specs/entity-schema.md` | Genesis-bound EntityID and derived display fields / O2A state ID |
| `specs/key-derivation-profile.md` | Genesis restore and proposed frozen Route B subset |
| `specs/proof-package-schema.md` | Recomputed genesis-bound EntityID and O2A state ID |
| `specs/rgb-identity-contract.md` | Genesis uniqueness, pending confirmation, and O2A state ID |
| `specs/verification-policy.md` | Pending outcome and recomputed identity/state identifiers |

## Vector artifacts

SHA-256 values are over the files as committed at `b622c98`.

| Vector file | Purpose | Producer / reproducer | SHA-256 |
| --- | --- | --- | --- |
| `tests/vectors/derivation-v0.1.json` | Route B positive and reject vectors | `check_vectors.py` validation; Route B derivation functions | `e1f911a3dd35341b0e8f786371779ec558d1969eefa90fe0835007c75d29e93e` |
| `tests/vectors/v0.1.json` | Identity, claim, semantic claim, and proof-package vectors | `check_vectors.py --emit` | `4dfe77ca54879171f7a0b95e836ea823067d18dd52bff58fec0a77dff0abd211` |
| `tests/vectors/protocol-objects-v0.1.json` | Remaining canonical signed-object vectors | `check_protocol_objects.py --emit` | `f079e297ace63e7c85ac2047d40dd66e01e64f40156b804221c76db83194737a` |
| `tests/vectors/entity-id-v0.1.json` | Genesis-payload EntityIDs, O2A state IDs, recovery-signer convergence and rejected payload hash | `check_protocol_objects.py --emit-entity-id` | `cb2a65b0c68f60f9769589df54712b2bd6876704597ad35e5187f8f9f6a542f5` |
| `tests/vectors/seal-script-v0.1.json` | Canonical seal policy/script cases including odd-leaf carry | `check_protocol_objects.py --emit-seal` | `a7d4896cf194751a7038a2977c00d48318dd8d0db8ccc00ea26edaacf68e1ff9` |
| `tests/vectors/seal-script-core-v0.1.json` | Bitcoin Core descriptor oracle outputs | `check_seal_core.py --emit` | `83b01b563e4ce0791569e00076dd3ad0d0284113683c8af1c29e61e861b2c706` |
| `tests/vectors/genesis-freeze-v0.1.json` | Accepted ADR-0009 63-output immutable manifest; original status label retained as frozen data | `check_genesis_freeze.py --emit` | `915187a825ff0ffc6ae13dcb8f8d3d153bef7f7438c64711a42f861eace69244` |
| `tests/vectors/entity-id-regression/entity-id-regression-v0.1.json` | ADR-0008 adversarial regression input | `check_entity_id_regression.py --emit` | `2851c00e3524c33bbf7eb51b054e1664a6a3944a549d9c0b85c86889adf16980` |
| `tests/vectors/option-b/option-b-v0.1.json` | Historical Option B adversarial input | `check_option_b.py --emit`, pinned to `c7b0871` | `9b49e17757b6c32bb4043eec17128e1a2af4a38d5d79ce8400598d00a29d0fb7` |
| `tests/vectors/genesis-options/genesis-options-v0.1.json` | Historical A/B/B+activation/C/G comparison | `check_genesis_options.py --emit`, pinned to `c7b0871` | `c3c997e3b49645933423d7a11352ce3c8377abd53af3b3dbd2c1f4ff3587fd9a` |

Notable fixed outputs are the unsafe mainnet-vector EntityID
`acda477be0a7e1342bb994541337e0705d9b1fe9fd9acee3080d3f294ae5f9cf`,
state ID
`17c8003335a55b5040bfc0cf3fdfc33a0b031b0b563ef50f5120337a1421a1c5`,
and two-recovery-signer convergence state ID
`ed3feb49735ba733b13ddc73e81131b92f878ca3c182473531e307b558d0259b`.
The published keys are permanently unsafe for funds.

The mainnet entries in the 63-output genesis-freeze manifest are the current
offline dry run for ADR-0011's frozen profile values and genesis bytes. They
never authorize a live identity or transaction, and the checker performs no
network connection or broadcast.

## Evidence bundles

The hash column is the SHA-256 of the bundle's `MANIFEST.sha256` file. Every
listed committed manifest passed `sha256sum -c` on 2026-09-28.

### Protocol repository

| Bundle | Manifest-file SHA-256 | Note |
| --- | --- | --- |
| `evidence/phase0/rgb-rc3-regtest-2026-09-23/` | No `MANIFEST.sha256` present | Early disposable compatibility record |
| `evidence/phase0/rgb-rc3-remediation-2026-09-23/` | `43991ee9bca8e6ab66778a36c317ed9bff9a3c6e0d264c77fe8aa7b8d8634fb0` | Patched/unpatched RC3 and dependency evidence |
| `evidence/phase0/rgb-rc3-compiled-graph-2026-09-24/` | `a90762e9974a9656f999c79777c27339131d0ff3d64e3d45c237f1c636e28380` | Feature-aware compiled dependency graph |

### Sibling `o2a-testnet-demo`

| Bundle | Manifest-file SHA-256 | Note |
| --- | --- | --- |
| `evidence/regtest-genesis-rotation-2026-09-24/` | `30af1cf74cb91b20fda56de55c6ef6aca0f0e89acf78a26f7f160553a40ddcec` | Superseded pre-seal-policy lineage |
| `evidence/signet-acceptance-2026-09-24/` | `0b1e9a1553071c01870670af72dea03753a78e34a488003af477bcf124eb1a50` | Signet stack acceptance at that date |
| `evidence/regtest-seal-tapscript-smoke-2026-09-25/` | `59f80970be1de88a642cd2345386ba7e12b903caf9b48f9ced5c39288c7e4b01` | E1–E6 and S6 disposable smoke |
| `evidence/regtest-seal-tapscript-smoke-correction-2026-09-25/` | `046afc6a798c96f6715079196ac5477562f272e0b991c2bd9ba3bac0c25b3f19` | Abandoned-first-contract correction |
| `evidence/regtest-seal-policy-lineage-2026-09-26/` | `15e8570e27227ace2339eb63d333214684c6811569111665fa8e16e0d4fe2654` | F1–F8 lineage |
| `evidence/regtest-seal-policy-lineage-correction-2026-09-28/` | `9014c7427dc7e8e98da91b88c036ab5f210b6b022e3d67fb5dedfe958edd31a1` | Shared-root correction |
| `evidence/regtest-genesis-bound-lineage-2026-09-28/` | `f01f9ee9075e150051aa62d76e41e3c33d5454c369fb6461ffa48100532aa2e1` | Twelve-case ADR-0008 lineage |
| `evidence/regtest-rgb011-compat-2026-09-28/` | `2b376eed8bb5e5640fe542fbf4b5b4cb7d63315502a4de9f7115b18e16bd2cad` | 22-file C1–C9 rgb-protocol v0.11.1 compatibility bundle at `2ddfe8c` |
| `evidence/regtest-rgb011-compat-2026-09-28-addendum/` | `e9acd79fcd911cd7d01b74ec3ffd01570bf7aa78a554db0a68f3185b2b931367` | 4-file D14 verdict addendum at `31dc5df` |
| `evidence/regtest-rgb011-lineage-2026-09-28/` | `ba5479df552f8fcea7c27e9b4ffae5ac67d40184f1043ba108b134d6e6020849` | 47-file maintained-adapter regtest lineage at `a86421f` |
| `evidence/signet-block0-rehearsal-2026-09-28/` | `ce48cda6ca83947fec2d26b91bd609718a02d962f8b98ed611e6b6bf69b0e3cc` | 46-file first rehearsal; superseded because the verifier trusted mutable seal-record script data |
| `evidence/signet-block0-rehearsal-2-2026-09-28/` | `bfc29c70fcb1be31acf147cb959d17e4f2c21f428464f2e3f68e83e45b66efde` | 46-file clean 0.12 rehearsal with corrected verifier |
| `evidence/signet-block0-rehearsal-3-2026-09-28/` | `2d98449550921243ebaec876b732bb68a3f6fbda2ca765f4b0c7cbb3c91ea91f` | 26-file clean rgb-protocol v0.11.1/Opret rehearsal at `a86421f` |

## Palimnex evaluation fixtures

| Fixture | Status | SHA-256 | Configuration |
| --- | --- | --- | --- |
| `evaluation/palimnex-v1.json` | Frozen; excluded from indexing | `6dad2baff0117d623179250ef0aab479ac328248ab39122590456e814b1264f4` | Historical only |
| `evaluation/palimnex-v2.json` | Active; excluded from indexing | `0ae56efa873c5de18b6e67dfab49828d20ceb5fa3654a4220ddc8e022d04cb4c` | `.palimnex.json` names this file and checksum |

## Merged pull requests

| PR | Merge commit | Head / specification commit | Result |
| --- | --- | --- | --- |
| Protocol #1 | `c7b0871` | `4b1c99e` | Seal key role, binding, script, spend observation, and oracle |
| Protocol #2 | `0ef16c2` | `5105632` (includes `38d9bd5`, `d72a017`) | Accepted ADR-0008 and Palimnex v2 |
| Protocol #3 | `b622c98` | `cabae9b` | Proposed ADR-0009 and O2A-native state IDs |
| Protocol #7 | `0a8d54f` | `6604dbc` | License assessment policy and proposed ADR-0010 |
| Protocol #8 | `099f706` | `69273b0` | Accepted ADR-0009 and ADR-0010; current evidence and site status |
| Protocol #9 | `86eb527` | `2cbc485` | RGB v0.11.1 repository and application reference map |
| Demo #1 | `02b9430` | smoke branch through `786dab9`; retains `bce2b58` | Preserved custom-tapscript smoke lineage |
| Demo #5 | `48fd5db` | `a86421f` | Maintained rgb-protocol v0.11.1 adapter, regtest lineage, and signet rehearsal 3 |

## Branches still present

No branch was deleted. The following refs were observed on 2026-09-28.

### Protocol repository

| Ref | Tip |
| --- | --- |
| `docs/decision-audit-2026-09` | audit working branch based on `b622c98` |
| base `main`, `origin/main`, `edwin/main` | `0a8d54f` at acceptance-branch creation |
| `draft/adr-0008-genesis-bound-entity-id`, `edwin/draft/adr-0008-genesis-bound-entity-id` | `5105632` |
| `draft/adr-0009-genesis-freeze`, `edwin/draft/adr-0009-genesis-freeze` | `cabae9b` |
| `test/option-b-adversarial` | `c7b0871` |
| `edwin/spec/seal-key-role-and-script` | `4b1c99e` |

### Demo repository

| Ref | Tip |
| --- | --- |
| `feat/block0-rehearsal` | `6edce70` at audit time; includes evidence commit `8a19439` |
| `docs/block0-runbook` | `c450616` |
| `feat/seal-policy-lineage` | `3198a7b` |
| `spike/seal-tapscript-smoke`, `origin/spike/seal-tapscript-smoke` | `786dab9` |
| refreshed local `main`, `origin/main` | `48fd5db` |
