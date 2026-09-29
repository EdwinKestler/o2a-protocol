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
