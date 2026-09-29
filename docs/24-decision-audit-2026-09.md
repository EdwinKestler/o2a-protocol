# 24 — Decision audit, September 2026

**Status:** supporting record, 2026-09-28. This document introduces no
protocol rule. Accepted ADRs and the [normative specifications](DOCUMENT-AUTHORITY.md)
win if a summary here is incomplete or inconsistent.

## Summary

| ID | Decision | Date | Authority / change | Status | Reversal cost |
| --- | --- | --- | --- | --- | --- |
| D1 | Retain RGB as the identity-state carrier; reject Lightning for identity ordering | 2026-09-25 | Maintainer review; no dedicated commit or PR recorded | Retained; line/carrier selected by D15 | High |
| D2 | Add dedicated role-4 seal keys and the deterministic P2TR seal script | 2026-09-25 | `4b1c99e`; PR #1 merge `c7b0871` | Draft v0.1 rule | High |
| D3 | Measure recovery delay from the seal-creating transaction | 2026-09-25 | `4b1c99e`; PR #1 | Draft v0.1 rule; exercised on regtest | High |
| D4 | Bind every seal key to its authorizing key ID | 2026-09-25 | `4b1c99e`; PR #1 | Draft v0.1 rule | High |
| D5 | Require a sourced unspent observation for `CURRENT` | 2026-09-25 | `4b1c99e`; PR #1 | Draft v0.1 rule; exercised on regtest | High |
| D6 | Remove wallet knowledge from canonical validity | 2026-09-25 | `4b1c99e`; PR #1 | Draft v0.1 rule | Medium |
| D7 | Freeze Palimnex v1 and publish v2 without ranking tricks | 2026-09-25–28 | Dropped `0d93ccd`; retained `d72a017` in PR #2 | Repository evaluation policy | Low |
| D8 | Adopt genesis-payload hash option G as ADR-0008 | 2026-09-27 | `38d9bd5`; PR #2 merge `0ef16c2` | Accepted | Very high |
| D9 | Add `PENDING_CONFIRMATION`, RBF invalidation, and CPFP preservation | 2026-09-28 | ADR-0008 in `38d9bd5`; PR #2 | Accepted | High |
| D10 | Adopt a scoped genesis freeze and signer-independent O2A state ID | 2026-09-28 | `cabae9b`; PR #3 merge `b622c98`; maintainer acceptance | Accepted | Prohibitive after use |
| D11 | Gate a first mainnet identity on ADR-0009 after a signet rehearsal | 2026-09-28 | `cabae9b`; signet rehearsals 2 and 3 | Accepted; no mainnet identity authorized | High |
| D12 | Record two non-blocking `bp-std` finalization findings | 2026-09-25 | `4b1c99e`; PR #1 | Open upstream candidates; non-blocking | Low for O2A |
| D13 | Start a new demo lineage for each spec change; never migrate evidence | 2026-09-26 | Demo PR #1 merge `02b9430` retains `bce2b58` | Demonstration policy | Medium |
| D14 | Treat dependency licenses as assessed findings rather than a rigid development gate | 2026-09-28 | Maintainer decision; [license assessment](22-license-and-adoption-assessment.md) | Accepted policy | Medium before distribution |
| D15 | Use rgb-protocol v0.11.1 with Opret for the first identity transitions | 2026-09-28 | Accepted [ADR-0010](../adr/0010-rgb-carrier-line.md); demo `31dc5df`, `a86421f` | Accepted | High after first transition |
| D16 | Accept ADR-0009 and ADR-0010 after evidence and license review | 2026-09-28 | Maintainer decision; demo main `48fd5db` | Accepted; Phase 0 remains open | High |

## D1 — Identity carrier

- **Question:** Should O2A replace RGB with a native Bitcoin seal carrier, or
  use Lightning as the identity-state rail?
- **Options considered:** retain RGB; use a simpler native Bitcoin carrier;
  use Lightning.
- **Evidence:** [the payment analysis](16-artist-authorized-use-payments.md)
  assigns Lightning the payment role, while
  [the dependency gate](phase0-dependency-gate.md) and
  [compatibility record](23-stack-compatibility-and-security-readiness.md)
  identify RGB 0.12 release maturity as a schedule gate. The maintainer source
  pack records that Lightning's bilateral, private, revocable channel states
  are not third-party-verifiable identity ordering.
- **Decision:** the maintainer retained RGB to preserve shared RGB ecosystem
  tooling, including SplitNight integration. Lightning remains a payment rail,
  not identity authority. No dedicated decision commit or PR was found.
- **Status and reversal:** retained architecture; D15 now selects the
  v0.11.1/Opret line and carrier while concrete program and production-lock
  gates remain open. Reversal is high-cost because it changes the identity
  lifecycle, proof model, and downstream documentation.

## D2 — Seal custody and role 4

- **Question:** Can ordinary payment keys safely control identity seals?
- **Options considered:** keep BIP86 payment-account seals; add dedicated seal
  keys and deterministic script recovery.
- **Evidence:** the review found that payment-key compromise or wallet error
  could close the identity seal outside the recovery policy. The resulting
  rule is in [canonical encoding](../specs/canonical-encoding.md), the
  [RGB identity contract](../specs/rgb-identity-contract.md), and the
  [key-derivation profile](../specs/key-derivation-profile.md).
- **Decision / who:** maintainer; role 4 is `seal`, and the output uses the
  fixed NUMS internal key, controller leaves, and delayed threshold-recovery
  leaf.
- **Commit / status:** specification commit `4b1c99e`, merged by protocol PR
  #1 as `c7b0871`; Draft v0.1. Reversal cost is high because scripts, vectors,
  custody, and already-created outputs would change.

## D3 — Recovery-delay clock

- **Question:** Does `not_before_height` start at the prior RGB anchor or at
  confirmation of the output being spent?
- **Options considered:** prior-anchor height; seal-output creation height.
- **Evidence:** the disposable smoke funded the seal at height 102, anchored
  at 103, and Bitcoin allowed inclusion at 112; the old anchor-plus-delay rule
  predicted 113. See
  `../o2a-testnet-demo/evidence/regtest-seal-tapscript-smoke-2026-09-25/bip68.txt`
  and [BIP68 use in the contract](../specs/rgb-identity-contract.md).
- **Decision / who:** maintainer; measure from confirmation of the transaction
  that created the current seal, matching BIP68.
- **Commit / status:** `4b1c99e`, PR #1; Draft v0.1 and regtest-observed.
  Reversal cost is high because it changes spend eligibility.

## D4 — Seal-key bindings

- **Question:** Are equal controller/recovery and seal-key counts sufficient?
- **Options considered:** count-only sets; exact sorted pairs of authorizing
  key ID and seal x-only key.
- **Evidence:** count-only validation allowed a rotated-out controller's seal
  key to remain. The exact coverage rule is in
  [canonical encoding](../specs/canonical-encoding.md) and
  [the entity schema](../specs/entity-schema.md); demo F2 rejects a stale
  binding in
  `../o2a-testnet-demo/evidence/regtest-seal-policy-lineage-2026-09-26/RUN.md`.
- **Decision / who:** maintainer; sorted bindings cover each authorizing set
  exactly, with no omission or extra key.
- **Commit / status:** `4b1c99e`, PR #1; Draft v0.1. Reversal cost is high
  because canonical state bytes and authorization change.

## D5 — Current-seal observation

- **Question:** Can RGB validation or a proof package alone establish that a
  seal is current?
- **Options considered:** trust RGB's current cell; require an evaluator's
  sourced Bitcoin-view observation.
- **Evidence:** smoke S6 left RGB reporting the cell after a plain spend; see
  `../o2a-testnet-demo/evidence/regtest-seal-tapscript-smoke-2026-09-25/plain-and-s6.txt`.
  The rule is in [verification policy](../specs/verification-policy.md) and
  [the RGB identity contract](../specs/rgb-identity-contract.md).
- **Decision / who:** maintainer; `CURRENT` requires the current seal observed
  unspent with source and height. A confirmed spend without a valid transition
  yields `SEAL_CLOSED_WITHOUT_VALID_TRANSITION` at the normal depth and reorg
  rule.
- **Commit / status:** `4b1c99e`, PR #1; Draft v0.1. Reversal cost is high
  because it would weaken the lifecycle safety boundary.

## D6 — Wallet-independent canonical validity

- **Question:** May canonical validity depend on whether a wallet knows a
  payment key?
- **Options considered:** retain wallet membership as validity; use only state
  and history data and keep payment-key separation as wallet behavior.
- **Evidence:** [canonical encoding](../specs/canonical-encoding.md) no longer
  depends on wallet knowledge, while
  [the key-derivation profile](../specs/key-derivation-profile.md) forbids a
  wallet from placing payment keys in seal scripts.
- **Decision / who:** maintainer; canonical validity is wallet-independent.
- **Commit / status:** `4b1c99e`, PR #1; Draft v0.1. Reversal cost is medium,
  but would make verification implementation-dependent.

## D7 — Palimnex evaluation fixtures

- **Question:** Should specification wording or the frozen v1 query be tuned
  to force ADR-0005 into broad conceptual results?
- **Options considered:** rewrite v1's query; rewrite indexed sources; freeze
  v1 and publish a truthful v2.
- **Evidence:** dropped commit `0d93ccd` rewrote v1. Retained commit `d72a017`
  keeps the original broad query, records that README and four supporting
  documents outrank ADR-0005, expects README in v2, and adds a dedicated
  ADR-0008 query. [Palimnex documentation](PALIMNEX.md) records the known
  ADR-0005 ranking limitation.
- **Decision / who:** maintainer; v1 is frozen, indexed protocol text is not
  reworded to influence ranking, and v2 is the active fixture.
- **Commit / status:** `d72a017`, included in PR #2 / `0ef16c2`; repository
  evaluation policy. Reversal cost is low, but historical comparability would
  be lost.

## D8 — Genesis equivocation and ADR-0008

- **Question:** How can the EntityID prevent the root from authoring parallel
  genesis histories?
- **Options considered:** A, root-only plus equivocation proof; B, hash root
  plus genesis seal; B plus activation; C, first root-address commitment; G,
  hash the complete genesis payload.
- **Evidence:** the pinned [genesis-options harness](../tests/vectors/genesis-options/README.md)
  shows that A can burn the legitimate identity, B permits same-seal
  impersonation, B plus activation lets a root-and-seal thief take the ID, and
  C requires a complete index and permits front-running and keyless denial of
  service. G gives every distinct genesis a distinct ID.
- **Decision / who:** maintainer; accept G as
  [ADR-0008](../adr/0008-genesis-bound-entity-id.md).
- **Commit / status:** `38d9bd5`, PR #2 merge `0ef16c2`; Accepted. Reversal
  cost is very high because every EntityID-bearing history and fixture changes.

## D9 — Pending confirmation

- **Question:** When is a signed genesis or successor seal stable enough to be
  `CURRENT`?
- **Options considered:** final immediately; require the profile depth for
  every seal-creating transaction and distinguish pending from absent.
- **Evidence:** ADR-0008 Decision 4, the
  [verification policy](../specs/verification-policy.md), regression R5, and
  the demo genesis-bound lineage exercise depth, RBF, and CPFP behavior.
- **Decision / who:** maintainer; below-depth histories are
  `PENDING_CONFIRMATION`, absent creating transactions are `INCOMPLETE`, RBF
  invalidates the pending outpoint and EntityID, and CPFP preserves it.
- **Commit / status:** `38d9bd5`, PR #2; Accepted through ADR-0008. Reversal
  cost is high because wallets and verifier outcomes change.

## D10 — Scoped genesis freeze and O2A state ID

- **Question:** What minimum surface can remain verifiable indefinitely, and
  how should one resulting state be identified independently of its signer?
- **Options considered:** freeze all Draft v0.1; freeze only genesis plus one
  `official_name` claim; hash the state-establishing signed payload; hash the
  EntityID plus exact canonical resulting state.
- **Evidence:** two recovery signers have distinct headers and signing-key IDs,
  so a payload hash would split one state. The accepted proposal from the
  agent review is the uniform formula in
  [ADR-0009](../adr/0009-scoped-genesis-freeze.md); the convergence and reject
  controls are in `tests/vectors/entity-id-v0.1.json`. The 63-output manifest
  is `tests/vectors/genesis-freeze-v0.1.json`, SHA-256
  `915187a825ff0ffc6ae13dcb8f8d3d153bef7f7438c64711a42f861eace69244`.
- **Decision / who:** maintainer; accept the scoped freeze and
  `TaggedHash("O2A/v0.1/state-id", entity_id || resulting_state)`.
- **Commit / status:** `cabae9b`, PR #3 merge `b622c98`; Accepted by
  maintainer decision on 2026-09-28. Reversal is incompatible with the
  promised indefinite verification of frozen-format identities.

## D11 — Path to a first mainnet identity

- **Question:** What gates precede a first mainnet genesis?
- **Options considered:** mint directly; rehearse on signet and accept the
  scoped freeze first.
- **Evidence:** [Phase 0 status](phase0closure.md), the
  [roadmap](13-roadmap.md), ADR-0009's not-frozen boundary, and the clean
  signet rehearsal records summarized in the [scenario matrix](25-scenario-matrix.md).
- **Decision / who:** maintainer; complete a signet rehearsal, accept ADR-0009,
  and only then consider mainnet genesis. A frozen-format identity may not
  transition until the concrete RGB program and remaining transition gates
  close; before its first transition its RGB contract may be re-issued only
  with the same O2A genesis bytes and seal.
- **Commit / status:** restated in `cabae9b`, PR #3; Accepted on 2026-09-28
  after the signet evidence. No mainnet identity is authorized or running, and
  the project is not mainnet-ready. Reversal cost is high after any public
  genesis exists.

## D12 — Non-blocking `bp-std` findings

- **Question:** Must O2A wait for generic RGB wallet finalization support for
  its seal scripts?
- **Options considered:** block on upstream changes; own seal tracking and
  script-path finalization while recording candidates upstream.
- **Evidence:** the disposable smoke observed first-Merkle-sibling leaf
  selection at `psbt/src/data.rs:890-891` and an `extract()` panic without
  `final_script_sig` at line 793. See [upstream needs](upstream-needs.md) and
  the smoke manifest
  `59f80970be1de88a642cd2345386ba7e12b903caf9b48f9ced5c39288c7e4b01`.
- **Decision / who:** maintainer; both are non-blocking candidates because O2A
  owns seal records and script-path finalization.
- **Commit / status:** `4b1c99e`, PR #1; open upstream candidates. Reversal
  cost is low for O2A if upstream behavior improves.

## D13 — Disposable demo lineage

- **Question:** Should a changed specification migrate prior demo state?
- **Options considered:** migrate old state; start a new disposable lineage and
  preserve old evidence.
- **Evidence:** demo merge `02b9430` keeps smoke commit `bce2b58` reachable;
  later evidence directories name their applicable protocol commit and retain
  correction bundles rather than editing old evidence.
- **Decision / who:** maintainer; each spec change starts a new demo lineage,
  never a migration.
- **Commit / status:** demo PR #1 merge `02b9430`; active demonstration policy.
  Reversal cost is medium because migration would destroy evidence provenance.

## D14 — Dependency licenses are an assessment

- **Question:** Must every non-allowlisted dependency license block development,
  or should it be recorded and assessed before distribution?
- **Options considered:** retain the rigid 2026-09-24 license gate; split
  supply-chain enforcement from a report-only license assessment.
- **Evidence:** the RGB 0.11.1 compatibility graph passed advisory, ban, and
  source checks but its license check reported `hex_lit 0.1.1` under MITNFA,
  pulled through `bitcoin 0.32.102` by `rgb-consensus 0.11.1`. The original
  output is retained at demo commit `2ddfe8c` in
  `evidence/regtest-rgb011-compat-2026-09-28/raw/deny-mitnfa.txt`.
- **Decision / who:** maintainer; cargo-deny advisories, bans, and sources stay
  blocking. Licenses are report-only and every non-allowlisted result enters
  the [license register](22-license-and-adoption-assessment.md) as `accepted`
  or `review-before-distribution`. GPL, AGPL, and SSPL require maintainer review
  before public distribution or mainnet release, not before development.
- **Status and reversal:** accepted repository policy, superseding the
  2026-09-24 rigid license rule. Reversal cost is medium because release
  review and validation automation depend on the classification.

## D15 — RGB carrier line

- **Question:** Which RGB line and commitment carrier should O2A use for its
  first identity transitions while keeping genesis independent of that choice?
- **Options considered:** continue the RGB-WG 0.12 RC3 experiment; use
  `rgb-protocol` v0.11.1 with Opret; select Tapret from the incomplete report.
- **Evidence:** demo commit `2ddfe8c`, the 22-file
  `evidence/regtest-rgb011-compat-2026-09-28/` bundle, and
  `docs/rgb-0.11.1-compat-memo.md`. C1–C7 pass, C8 passes under D14, and C9
  limits the proposal to Opret. C6 and C7 confirm that O2A must retain its
  sourced current-seal observation independently of RGB validity. Commit
  `31dc5df` records the verdict addendum. Commit `a86421f` supplies the
  maintained adapter, 47-file regtest lineage, and 26-file v0.11.1/Opret
  signet rehearsal; both commits are ancestors of demo main `48fd5db`.
- **Decision / who:** maintainer in
  [ADR-0010](../adr/0010-rgb-carrier-line.md); the first transitions use
  v0.11.1 with Opret, `rgb-lib` does not own seal custody, incompatible RGB
  lines stay in separate workspaces, and duplicate secp256k1 types cross by
  bytes.
- **Status and reversal:** Accepted on 2026-09-28 after the adapter, regtest,
  signet, and license-review requirements were satisfied. Reversal is high
  after the first transition but does not change the RGB-line-agnostic O2A
  genesis.

## D16 — Maintainer acceptance of ADR-0009 and ADR-0010

- **Question:** Have the scoped-freeze and RGB carrier proposals met their
  acceptance requirements without overstating Phase 0 or mainnet readiness?
- **Evidence:** the ADR-0009 63-output freeze manifest remains unchanged;
  `31dc5df` and `a86421f` are reachable from `o2a-testnet-demo` main
  `48fd5db`; the addendum, 47-file regtest lineage, and 26-file signet
  rehearsal manifests verify; and the maintainer reviewed the accepted
  `hex_lit 0.1.1` MITNFA register entry.
- **Decision / who:** maintainer; accept ADR-0009 and ADR-0010 on 2026-09-28.
- **Status and boundary:** Accepted. The frozen genesis/`official_name` surface
  and v0.11.1/Opret carrier selection are settled. Concrete O2A RGB program
  bytes, the production dependency lock, remaining transition/custody,
  restore/discovery, broader conformance, and every production or mainnet
  operational gate remain open.
