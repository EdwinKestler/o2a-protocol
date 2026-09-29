# 28 — References

**Status:** supporting bibliography, 2026-09-28. A reference explains or
constrains an adopted rule only where an ADR or normative specification says
so. Listing a project here does not adopt its protocol, implementation, or
governance.

## Bitcoin standards

| Reference | Relevance to O2A |
| --- | --- |
| [BIP340 — Schnorr signatures for secp256k1](https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki) | Defines the x-only keys, Schnorr verification, and tagged-hash construction used by O2A signing domains. |
| [BIP341 — Taproot](https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki) | Defines tapleaf, branch, tweak, output-key, control-block, and P2TR rules used by the deterministic seal output. |
| [BIP342 — Tapscript](https://github.com/bitcoin/bips/blob/master/bip-0342.mediawiki) | Defines execution of the controller and delayed threshold-recovery tapscript leaves. |
| [BIP379 — Miniscript](https://github.com/bitcoin/bips/blob/master/bip-0379.md) | Supplies the canonical meaning of the recovery expression `and_v(v:multi_a(k,...),older(d))`. |
| [BIP68 — relative lock time](https://github.com/bitcoin/bips/blob/master/bip-0068.mediawiki) | Makes the recovery delay relative to confirmation of the current seal output's creating transaction. |
| [BIP125 — opt-in full-RBF signaling](https://github.com/bitcoin/bips/blob/master/bip-0125.mediawiki) | Provides background for replacing a pending seal-funding transaction, which changes its outpoint and pending EntityID. |
| [BIP174 — PSBT](https://github.com/bitcoin/bips/blob/master/bip-0174.mediawiki) | Defines the transaction container used while O2A supplies seal-input metadata and finalizes the script-path witness. |

The governing O2A uses of these standards are in
[canonical encoding](../specs/canonical-encoding.md), the
[cryptographic profile](../specs/cryptographic-profile.md), the
[RGB identity contract](../specs/rgb-identity-contract.md), and
[ADR-0009's accepted frozen subset](../adr/0009-scoped-genesis-freeze.md).

## RGB ecosystem (rgb-protocol v0.11.1 line, ADR-0010)

The repository URLs below resolved to their canonical GitHub projects on
2026-09-28. They are implementation references for the line selected by
[ADR-0010](../adr/0010-rgb-carrier-line.md), not an adopted O2A production
dependency lock. Pin exact revisions and re-check licenses, dependency graphs,
and network support before adoption. Standard RGB wallets handle standard
schemas; they do not automatically display or validate O2A's custom identity
contract.

| Category and repository | Role | Version line | Fit for O2A | Maturity note |
| --- | --- | --- | --- | --- |
| Tool — [RGB-Tools/faucet-rgb](https://github.com/RGB-Tools/faucet-rgb) | Flask faucet that distributes RGB assets through `rgb-lib-python`. | Tag `0.1.0`; follows the `rgb-lib` wallet line rather than defining RGB consensus. | Useful for disposable test assets and application-flow testing, not identity authority or seal custody. | Maintained utility with no GitHub release; treat as test infrastructure. |
| Tool — [rgb-protocol/rgb-sandbox](https://github.com/rgb-protocol/rgb-sandbox) | Self-contained RGB issuance and transfer demonstration using `rgb-cmd` and `bp-wallet`. | README targets RGB `0.11.1 RC6` on Bitcoin regtest. | Useful for learning the accepted family and constructing disposable integration exercises. | Demonstration environment, not production infrastructure; its scripts manage disposable local data. |
| Tool / protocol library — [rgb-protocol/rgb-strict-types](https://github.com/rgb-protocol/rgb-strict-types) | Strict Types AST, schema, compilation, and serialization support used by the RGB libraries. | Release `1.0.4` for the v0.11.1 family; individual consumers may pin an earlier compatible 1.0.x release. | Required serialization infrastructure for a future O2A RGB program; it does not define O2A canonical bytes. | Released library, not an application or wallet. |
| Wallet — [RGB-Tools/iris-wallet-android](https://github.com/RGB-Tools/iris-wallet-android) | Android RGB asset wallet built through `rgb-lib-kotlin`. | Release `v0.3.1-73`; Signet, Testnet, and Testnet4 variants are documented. | UI and application-flow reference for an artist wallet; an O2A identity contract and its dedicated seals require O2A-specific handling. | Maintained mobile wallet; network variants and release targets must be evaluated before reuse. |
| Wallet — [RGB-Tools/iris-wallet-desktop](https://github.com/RGB-Tools/iris-wallet-desktop) | Desktop RGB asset wallet using `rgb-lightning-node`. | Release `0.2.0`; follows its RGB Lightning Node dependency line. | Desktop UX and RGB/Lightning integration reference for artist-wallet or SplitNight work, not an O2A verifier or seal custodian. | Early application release; validate its node, packaging, license, and network assumptions separately. |
| Protocol library — [rgb-protocol/rgb-consensus](https://github.com/rgb-protocol/rgb-consensus) | Consensus data, client-side validation, seals, commitments, owned state, and witness resolution. | Release `0.11.1`, selected by ADR-0010. | Core validation layer for the future isolated O2A adapter; O2A still performs controller authorization and current-seal observation. | Released accepted-line library; O2A's concrete program and production lock remain open. |
| Protocol library — [rgb-protocol/rgb-schemas](https://github.com/rgb-protocol/rgb-schemas) | Standard NIA, CFA, UDA, IFA, and PFA schemas. | Release `0.11.1`. | Shows how to package schemas and proves a custom O2A identity schema is feasible; the standard schemas are not the O2A program. | Released library whose repository marks relevant schemas as not production-ready. |
| Protocol library — [rgb-protocol/rgb-ops](https://github.com/rgb-protocol/rgb-ops) | Standard operations, contract construction, and consignment tooling. | Release `0.11.1`. | Preferred lower-level surface, with `rgb-api`, for an O2A-owned adapter and externally supplied seal input. | Released library; integration remains subject to O2A's program, lock, and conformance gates. |
| Protocol library — [rgb-protocol/rgb-api](https://github.com/rgb-protocol/rgb-api) | Application-facing runtime and wallet APIs, including BDK and generic PSBT support. | Release `0.11.1`. | Candidate adapter surface for application integration; generic PSBT support does not replace O2A script-path finalization. | Released API; not O2A's proposed public HTTP API and not an O2A custody implementation. |
| Protocol library — [rgb-protocol/rgb-aluvm](https://github.com/rgb-protocol/rgb-aluvm) | AluVM deterministic validation and contract-computation infrastructure. | Release `0.11.1`. | Dependency-level reference for RGB validation; O2A applications should consume it through the selected RGB stack rather than invent VM behavior. | Released infrastructure library, not a wallet-facing SDK. |
| Ecosystem SDK — [kaleidoswap/kaleido-sdk](https://github.com/kaleidoswap/kaleido-sdk) | TypeScript and Python clients for RGB/Lightning swap and wallet services. | `v0.1.x` line; repository tag `v0.1.19`. | Candidate SplitNight integration reference for test flows; it does not define O2A identity or custody rules. | Explicit beta, testnet/signet only, and not safe for mainnet or production. |
| Ecosystem SDK — [UTEXO-Protocol/rgb-sdk-web](https://github.com/UTEXO-Protocol/rgb-sdk-web) | Browser-first TypeScript/WASM SDK for RGB assets and Lightning through RGB Lightning Node. | Beta release line; published repository release `v1.0.0-beta.12`. | Browser-wallet research reference; O2A signing, state validation, and seal records still require an explicit adapter. | Explicit beta with changeable APIs; endpoint and browser-custody assumptions require review. |
| Ecosystem SDK — [UTEXO-Protocol/wdk-wallet-rgb](https://github.com/UTEXO-Protocol/wdk-wallet-rgb) | Tether WDK wallet module wrapping RGB wallet, signer, UTXO, issuance, transfer, and backup flows. | Release `v2.0.4`; built around `rgb-lib` and a single BIP86 account model. | Application-wallet reference only. Its UTXO orchestration must not control O2A's dedicated seal outputs. | Repository explicitly labels the package beta and calls for development-environment testing before production. |
| Recommended wallet starting point — [RGB-Tools/rgb-lib](https://github.com/RGB-Tools/rgb-lib) | Cross-platform Rust wallet library with Bitcoin walleting, RGB issuance/transfers, persistence, and language bindings. | `0.3.0-beta.7`, pinning the `0.11.1-rc.11` RGB family. | Recommended starting point for artist-wallet and SplitNight application work. It exclusively manages all UTXOs in its wallet, so it is **not** suitable for O2A seal custody; O2A must retain separate seal records and script-path finalization. | Beta API with breaking changes permitted throughout `0.*`; its single-instance UTXO-management warning is a material architecture constraint. |

For application wallets, `rgb-lib` is the preferred starting point because it
already covers Bitcoin/RGB wallet operations and has mobile bindings. That
recommendation is deliberately limited: an `rgb-lib` wallet owns and manages
all of its UTXOs, while ADR-0010 requires O2A to own the identity seal record,
construct the controller-or-delayed-recovery script, and finalize the seal
input through the O2A script path. Artist-wallet and SplitNight integrations
therefore keep O2A seal custody outside `rgb-lib`.

The RGB-WG v0.12 repositories and pins retained below are neutral, archived
historical evidence from the earlier compatibility work. They are a separate
line from ADR-0010's v0.11.1 selection and must not share its Cargo dependency
graph; archival status is not a judgment on their usefulness to other
projects.

## Pinned implementation evidence

These are evidence inputs, not adopted production dependencies.

| Component | Repository-recorded pin | Relevance |
| --- | --- | --- |
| RGB standard library | `v0.12.0-rc.3`, commit `e183bebfed9ffd0ba8c6f7110fe3e097f23cd70b` | The inspected RC3 standard-library lineage; recorded in `evidence/phase0/rgb-rc3-regtest-2026-09-23/README.md`. |
| RGB runtime / CLI | `v0.12.0-rc.3`, commit `a1e6b41524131f6d6f183b2235fdaacb5c1abb31` | The disposable compatibility, dependency-graph, and demo lineage inspected by O2A. |
| `bp-std` | crate `v0.12.0-rc.3`, crates.io checksum `6c69f38f9656b94b7241a9219523306fd3ed1aaefe5bd931da079a86dfeda025` | Supplies the RC3 PSBT and descriptor stack in which the two non-blocking finalization findings were observed. The retained lock pins this crate artifact; an upstream Git commit is **unverified** because neither repository nor the maintainer source pack records one. |
| [Bitcoin Core 31.1](https://bitcoincore.org/en/releases/31.1/) | daemon `v31.1.0`; Linux archive SHA-256 `b80d9c3e04da78fb6f0569685673418cf686fadba9042d926d13fb87ff503f9e` | Independent descriptor/address/script oracle and isolated regtest chain backend. |

The RGB and Core provenance is recorded in
[the compatibility record](23-stack-compatibility-and-security-readiness.md),
the compiled-graph `RUN.md`, and the remediation `RUN.md`. The `bp-std`
artifact checksum appears in both retained Cargo locks. The observed upstream
candidates are listed in [upstream needs](upstream-needs.md).

## Prior art considered, not adopted

| Prior art | Relevance |
| --- | --- |
| `did:btcr` / `did:btcr2` | Considered as Bitcoin-anchored decentralized-identifier background; O2A did not adopt either DID method or reinterpret its own EntityID through one. |
| KERI self-addressing identifiers | The self-addressing idea informed the genesis-bound EntityID comparison: the identifier commits to the canonical genesis bytes; O2A did not adopt KERI's event, witness, or governance model. |

The prior-art classification comes from the maintainer review source pack. No
repository source pins a release, commit, or canonical URL for these items, so
none is invented here.
