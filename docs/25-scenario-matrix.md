# 25 — Scenario matrix

**Status:** supporting evidence index, 2026-09-28. This document introduces no
rule. Interpret results under [document authority](DOCUMENT-AUTHORITY.md), the
[accepted genesis rule](../adr/0008-genesis-bound-entity-id.md), and the
[Draft v0.1 verification policy](../specs/verification-policy.md). Synthetic
fixtures and disposable demo lineages are not production or mainnet evidence.

## Custom-tapscript smoke: E1–E6 and S6

Source: demo commit `bce2b58`, bundle
`evidence/regtest-seal-tapscript-smoke-2026-09-25/` in sibling repository
`o2a-testnet-demo`, manifest
`59f80970be1de88a642cd2345386ba7e12b903caf9b48f9ced5c39288c7e4b01`.
This is disposable demo-lineage evidence. The governing seal rules are in the
[RGB identity contract](../specs/rgb-identity-contract.md).

| Case | Expected | Observed | Result | Evidence path |
| --- | --- | --- | --- | --- |
| E1 | RGB accepts the custom-tapscript external seal | State assigned to the outpoint; two validators agreed | PASS | `../o2a-testnet-demo/evidence/regtest-seal-tapscript-smoke-2026-09-25/issue-and-wallet.txt`, `verify-a-b.txt` |
| E2 | Generic RGB wallet does not track or select the seal | Only the fee output was in wallet UTXOs; seal selection was rejected | PASS | `../o2a-testnet-demo/evidence/regtest-seal-tapscript-smoke-2026-09-25/issue-and-wallet.txt` |
| E3 | RGB can fill and complete a commitment using a foreign seal input | `rgb_fill_csv` and `complete` succeeded | PASS | `../o2a-testnet-demo/evidence/regtest-seal-tapscript-smoke-2026-09-25/anchor-a-b.txt` |
| E4 | An implementation-owned script-path witness spends the seal | Controller and recovery script-path spends were accepted by Core | PASS | `../o2a-testnet-demo/evidence/regtest-seal-tapscript-smoke-2026-09-25/anchor-a-b.txt`, `variant-c.txt` |
| E5 | Bitcoin enforces the recovery delay | Early broadcast returned `non-BIP68-final`; later spend was accepted | PASS | `../o2a-testnet-demo/evidence/regtest-seal-tapscript-smoke-2026-09-25/bip68.txt` |
| E6 | Delay starts at confirmation of the spent output | Funding at 102 allowed inclusion at 112, not anchor-plus-delay height 113 | PASS | `../o2a-testnet-demo/evidence/regtest-seal-tapscript-smoke-2026-09-25/bip68.txt` |
| S6 | Record behavior after a seal is spent without an RGB commitment | At height 114 RGB still reported the cell on seal C as current | RECORDED; not scored | `../o2a-testnet-demo/evidence/regtest-seal-tapscript-smoke-2026-09-25/plain-and-s6.txt` |

The correction bundle
`evidence/regtest-seal-tapscript-smoke-correction-2026-09-25/` records an
abandoned first contract on the same outpoint. No transaction from that failed
attempt was broadcast, and the removed contract state is not recoverable from
the retained data; the original bundle remains unchanged.

## RGB 0.11.1 compatibility: C1–C9

Source: demo commit `2ddfe8c`, bundle
`evidence/regtest-rgb011-compat-2026-09-28/` in sibling repository
`o2a-testnet-demo`, and `docs/rgb-0.11.1-compat-memo.md` at that commit. Its
22-file manifest has manifest-file SHA-256
`2b376eed8bb5e5640fe542fbf4b5b4cb7d63315502a4de9f7115b18e16bd2cad`.
This is disposable regtest evidence for proposed
[ADR-0010](../adr/0010-rgb-carrier-line.md), not production or mainnet
evidence.

| Case | Expected | Observed | Result | Evidence path |
| --- | --- | --- | --- | --- |
| C1 | A custom declarative identity schema with a 32-byte digest and no validators issues and validates | Distinct O2A schema and contract; `validators_none true`; `Consignment is valid` | PASS | `../o2a-testnet-demo/evidence/regtest-rgb011-compat-2026-09-28/cases.txt`, `A.strict` |
| C2 | The RGB right can use an external outpoint whose script matches the O2A seal policy | `o2a_script_match true`; the RGB seal has no script field; consignment valid | PASS | Same `cases.txt`; `A.strict` |
| C3 | A generic PSBT commits the transition without the PSBT layer requiring wallet ownership | External seal input committed with Opret; no `RgbWallet`; wallet selection paths were not called | PASS | Same `cases.txt`; `RUN.md` wallet-ownership lines |
| C4 | Controller script-path spend broadcasts and two independent resolvers agree | Mined at 109; validators byte-identical; consignment valid | PASS | Same `cases.txt`; `c4-validators.txt`, `c4-transfer.strict` |
| C5 | Recovery fails before BIP68 maturity and succeeds after it | `non-BIP68-final` at 109; allowed at 117; mined at 118 | PASS | Same `cases.txt`; `c5-validators.txt`, `c5-transfer.strict` |
| C6 | Record RGB behavior after a plain seal spend with no commitment | Bitcoin spent the seal at 119; RGB still reported `Consignment is valid`, right on the spent outpoint, witness `None` | PASS; O2A current-seal check required | Same `cases.txt`; `c6-plain.hex` |
| C7 | Record two contracts sharing one outpoint when only contract 2 is committed | Both valid while unspent; after the spend at 120, contract 1 still validated and listed the spent outpoint | PASS; O2A current-seal check required | Same `cases.txt`; `c7-validators.txt`, `c7-transfer.strict` |
| C8 | Blocking dependency gates pass and every license finding is assessed | Audit, advisories, bans, and sources passed; license report identified only `hex_lit 0.1.1` / MITNFA after Zlib correction | PASS under D14; register status `accepted` | `../o2a-testnet-demo/evidence/regtest-rgb011-compat-2026-09-28/raw/deny-mitnfa.txt`; [license register](22-license-and-adoption-assessment.md) |
| C9 | Determine the supported commitment carrier without broadcasting the Tapret probe | Script-tree Tapret unsupported; key-only Tapret proof built but not broadcast; Opret path passed C3–C4 | OPRET ONLY | Same `cases.txt`; `RUN.md` |

The immutable demo memo and `RUN.md` mark C8 `FAIL` and C9 `REPORT` under the
then-current 2026-09-24 license gate. D14 reclassifies C8 for protocol decision
purposes, and ADR-0010 uses C9 to select Opret; neither change rewrites the
recorded evidence.

## Option B cases 1–4

Historical, synthetic evidence pinned to `c7b0871`. Expected results describe
the candidate's behavior, including successful attacks; they are not desired
protocol behavior. Source:
[`tests/vectors/option-b/`](../tests/vectors/option-b/README.md).

| Case | Expected | Observed | Result | Evidence path |
| --- | --- | --- | --- | --- |
| 1 — different seals | Option B gives different IDs; cross-ID genesis and claim fail; old root-only rule gives one ID | All distinctions and rejects matched | PASS | `tests/vectors/option-b/check_option_b.py`, cases `[1]` |
| 2 — same seal | Added claim-only controller and re-keyed controller both remain valid, share the legitimate ID, and are `CURRENT` | Both parallel histories were valid and `CURRENT` | PASS, exposes flaw | Same checker, cases `[2]` |
| 3 — attacker payout | Attacker package accepts its claim; legitimate package rejects it; legitimate rotation closes the attacker history | `accepted`, reject, `CURRENT`, then `SEAL_CLOSED_WITHOUT_VALID_TRANSITION` | PASS | Same checker, cases `[3]` |
| 4 — commitment/reorg boundary | Missing data is incomplete, mismatch invalid, replacement changes ID; bootstrap model has ownership, pending, RBF, and circularity limits | All modelled boundaries matched | PASS | Same checker, cases `[4]` |

Verified result on 2026-09-28: `46/46 expectations met` in an isolated
`c7b0871` worktree.

## Genesis-uniqueness options

Historical, synthetic evidence pinned to `c7b0871`. Source:
[`tests/vectors/genesis-options/`](../tests/vectors/genesis-options/README.md).

| Option | Expected | Observed | Result | Evidence path |
| --- | --- | --- | --- | --- |
| A — root ID plus equivocation proof | Attacker obtains the ID; a verifier with both packages rejects both attacker and legitimate claims | Attacker-only payout accepted; both-package view returned `GENESIS_EQUIVOCATION` | PASS; unacceptable collateral | `tests/vectors/genesis-options/check_genesis_options.py`, `[A:*]` |
| B — root plus genesis seal | Own-seal attacker gets another ID, but same-seal attacker can receive a payout | Same-seal payout accepted until the legitimate rotation closes it | PASS; same-seal flaw | Same checker, `[B:*]` |
| B plus activation | Both histories wait; legitimate activation closes the parallel fork, but a root-and-seal thief can activate first | Legitimate path worked; takeover payout accepted and legitimate history closed | PASS; takeover flaw | Same checker, `[B+act:*]` |
| C — first root-address commitment | A complete strict view can pick the first known commitment, but incomplete indexes, front-running, junk commitments, and lax mode break the property | Missing-index and front-run cases admitted attacker outcomes; strict mode could become incomplete | PASS; index and denial-of-service flaws | Same checker, `[C:*]` |
| G — hash complete genesis payload | Every distinct genesis has a distinct ID; attacker cannot claim the legitimate ID; a stolen seal key can only close the seal | Immediate legitimate payout accepted; attacker claims rejected; closure reported | PASS; selected by ADR-0008 | Same checker, `[G:*]`; [ADR-0008](../adr/0008-genesis-bound-entity-id.md) |

Verified result on 2026-09-28: `76/76 expectations met` in an isolated
`c7b0871` worktree.

## ADR-0008 regression groups

Normative regression seam:
[`tests/vectors/entity-id-regression/`](../tests/vectors/entity-id-regression/README.md).

| Group | Expected | Observed | Result | Evidence path |
| --- | --- | --- | --- | --- |
| R1 | EntityID hashes exact genesis payload; genesis signer is zero; deterministic; any payload change changes the ID | Five derivation and mutation expectations matched | PASS | `check_entity_id_regression.py`, `[R1]` |
| R2 | Valid genesis accepted; non-zero genesis `signer_entity` invalid | Both outcomes matched | PASS | Same checker, `[R2]` |
| R3 | Own-seal, same-seal, and re-keyed attacker geneses have other IDs; target-ID claims fail; stolen seal can only close | Seven uniqueness, reject, and closure outcomes matched | PASS | Same checker, `[R3]` |
| R4 | Legitimate genesis can authorize immediately; rotation preserves EntityID; parallel same-seal history closes | Four lifecycle outcomes matched | PASS | Same checker, `[R4]` |
| R5 | Below-depth creators are pending, confirmed is current, absent is incomplete, pending payout rejected | Five depth and payout outcomes matched | PASS | Same checker, `[R5]` |
| N | Frozen root-only and Option B evaluators must still admit their attacks | Four negative controls admitted the attacks | PASS | Same checker, `[N]`; `legacy_evaluator.py` |

Verified result on 2026-09-28: `27/27 expectations met` using the normative
checker and its labelled legacy negative-control seam.

## Seal-policy demo lineage: F1–F8

Source: demo bundle `evidence/regtest-seal-policy-lineage-2026-09-26/`,
manifest `15e8570e27227ace2339eb63d333214684c6811569111665fa8e16e0d4fe2654`.
It is disposable regtest evidence against protocol commit `c7b0871`.

| Case | Expected | Observed | Result | Evidence path |
| --- | --- | --- | --- | --- |
| F1 | Genesis on seal A is current | Two fresh validators returned `CURRENT` | PASS | `../o2a-testnet-demo/evidence/regtest-seal-policy-lineage-2026-09-26/raw/f1-verify-a.txt`, `f1-verify-b.txt` |
| F2 | Rotation A→B is current and a stale binding is invalid | Rotation `CURRENT`; stale binding rejected for incomplete key-set coverage | PASS | `../o2a-testnet-demo/evidence/regtest-seal-policy-lineage-2026-09-26/raw/f2-verify-a.txt`, `f2-stale.txt` |
| F3 | Early recovery of B fails; controller rotation B→C wins | `non-BIP68-final`, then stale recovery input spent; C `CURRENT` | PASS | `../o2a-testnet-demo/evidence/regtest-seal-policy-lineage-2026-09-26/raw/f3-early-status.txt`, `f3-spent-status.txt`, `f3-verify-a.txt` |
| F4 | Recovery C→D succeeds after C's height plus ten | D reported `CURRENT` | PASS | `../o2a-testnet-demo/evidence/regtest-seal-policy-lineage-2026-09-26/raw/f4-before-delay.txt`, `f4-verify-a.txt` |
| F5 | Removing the rotation anchor makes the history incomplete; reconsider restores it | `CURRENT` → `INCOMPLETE` → `CURRENT` | PASS | `../o2a-testnet-demo/evidence/regtest-seal-policy-lineage-2026-09-26/raw/f5-before-a.txt`, `f5-reorg-a.txt`, `f5-restored-a.txt` |
| F6 | Plain close of seal B has no valid transition | `SEAL_CLOSED_WITHOUT_VALID_TRANSITION` | PASS | `../o2a-testnet-demo/evidence/regtest-seal-policy-lineage-2026-09-26/raw/f6-verify-a.txt`, `f6-verify-b.txt` |
| F7 | Genesis outpoint script must match the policy | Script mismatch returned `INVALID` | PASS | `../o2a-testnet-demo/evidence/regtest-seal-policy-lineage-2026-09-26/raw/f7-verify-a.txt`, `f7-verify-b.txt` |
| F8 | No current-seal observation cannot establish current | `INCOMPLETE`; Bitcoin line says seal not observed | PASS | `../o2a-testnet-demo/evidence/regtest-seal-policy-lineage-2026-09-26/raw/f8-verify-a.txt`, `f8-verify-b.txt` |

### Correction

| Expected reading | Observed | Result | Evidence path |
| --- | --- | --- | --- |
| Labels “Identity 1” and “Identity 2” might imply independent roots | Both used demo entity index 0 and the same genesis address; they are two contracts under one root | CORRECTED; bundle unchanged and not rerun | `evidence/regtest-seal-policy-lineage-correction-2026-09-28/CORRECTION.md`, manifest `9014c7427dc7e8e98da91b88c036ab5f210b6b022e3d67fb5dedfe958edd31a1` |

## Genesis-bound demo lineage

Source: demo commit `8a19439`, branch `feat/block0-rehearsal`, bundle
`evidence/regtest-genesis-bound-lineage-2026-09-28/`, manifest
`f01f9ee9075e150051aa62d76e41e3c33d5454c369fb6461ffa48100532aa2e1`.
The bundle is disposable regtest evidence against protocol merge `0ef16c2`.

| Scenario | Expected | Observed | Result | Evidence path |
| --- | --- | --- | --- | --- |
| Entity 1 at depth below six | `PENDING_CONFIRMATION` | Pending at best height 106 | PASS | `../o2a-testnet-demo/evidence/regtest-genesis-bound-lineage-2026-09-28/raw/e1-pending-a.txt` |
| Same genesis at depth six | `CURRENT`, same EntityID | Current ID `3ec753a7…fddb` | PASS | `../o2a-testnet-demo/evidence/regtest-genesis-bound-lineage-2026-09-28/raw/e1-current-a.txt` |
| Rotation to seal B | EntityID unchanged and current | `history_entity` matched; current at 114 | PASS | `../o2a-testnet-demo/evidence/regtest-genesis-bound-lineage-2026-09-28/raw/e1-after-rotate-a.txt` |
| Recovery to seal D | EntityID unchanged and current | `history_entity` matched; current at 125 | PASS | `../o2a-testnet-demo/evidence/regtest-genesis-bound-lineage-2026-09-28/raw/e1-recovered-a.txt` |
| Second genesis on same seal and root | Different ID, then closed after legitimate rotation | Fork ID `73b301b9…9c0d`; seal closed | PASS | `../o2a-testnet-demo/evidence/regtest-genesis-bound-lineage-2026-09-28/raw/e1-fork-ids.txt`, `e1-fork-closed-a.txt` |
| Fork attempts to name legitimate ID | Verifier recomputes fork ID | Fork ID reported | PASS | Same fork evidence |
| Entity 2 seal-creating-block reorg | `INCOMPLETE`, then `CURRENT` after reconsider | Incomplete at 125; current at 126 | PASS | `../o2a-testnet-demo/evidence/regtest-genesis-bound-lineage-2026-09-28/raw/e2-reorg-a.txt`, `e2-restored-a.txt` |
| Entity 2 plain close | `SEAL_CLOSED_WITHOUT_VALID_TRANSITION` | Closed at height 127 | PASS | `../o2a-testnet-demo/evidence/regtest-genesis-bound-lineage-2026-09-28/raw/e2-plain-a.txt` |
| F7 policy-script mismatch | `INVALID` | Invalid; no consignment was issued | PASS | `../o2a-testnet-demo/evidence/regtest-genesis-bound-lineage-2026-09-28/raw/e3-mismatch-a.txt` |
| F8 no current-seal observation | `INCOMPLETE` | Incomplete at height 125 | PASS | `../o2a-testnet-demo/evidence/regtest-genesis-bound-lineage-2026-09-28/raw/e1-no-observation-a.txt` |
| RBF of seal funding | EntityID changes; old transaction disappears | Old and replacement IDs differ; old tx absent | PASS | `../o2a-testnet-demo/evidence/regtest-genesis-bound-lineage-2026-09-28/raw/e4-rbf-result.txt`, `e4-id-before.txt`, `e4-id-after.txt` |
| CPFP of non-RBF funding | EntityID unchanged; parent confirms | Same ID before and after; parent reached one confirmation | PASS | `../o2a-testnet-demo/evidence/regtest-genesis-bound-lineage-2026-09-28/raw/e4-cpfp-result.txt`, `e4-cpfp-id.txt`, `e4-cpfp-id-after.txt` |

All 12 filed cases passed, with two fresh validators producing byte-identical
reports. An initial F7 read while electrs lagged is retained separately as
`e3-mismatch-electrs-lag.txt`; the filed result is the retry after heights
matched.

## Signet dress rehearsal — IN PROGRESS

Evidence workspace:
`../o2a-testnet-demo/evidence/signet-block0-rehearsal-2026-09-28/`.
This section is intentionally not summarized or scored. It will be filled only
after Gate 3.

| Scenario | Expected | Observed | Result | Evidence path |
| --- | --- | --- | --- | --- |
