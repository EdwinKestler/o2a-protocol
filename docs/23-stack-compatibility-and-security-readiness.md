# 23 — Stack Compatibility and Security Readiness

**Status:** supporting evidence record, 2026-09-23. The run was disposable,
regtest-only, and used no O2A or real-value keys. It does not select the RGB
lineage, freeze a dependency graph, or demonstrate an O2A identity lifecycle.

## Verdict

The proposed development baseline is feasible, but the exact stack is **not
ready to adopt**. A third disposable run built the exact RGB-WG RC3 tag and
electrs tag under Rust 1.98.1. A reproducible three-line compatibility patch
fixed the CLI parser failure and wallet-path mismatch, and the patched CLI
synced 101 regtest UTXOs through local electrs and Bitcoin Core 31.1. The
unmodified tag and current upstream `master` still contain those defects.

Compatible dependency updates reduced the full RC3 graph from 15 RustSec
findings to three. Removing Esplora in a separate feature-minimized experiment
removed those three advisories and passed locked checks and tests, but required
another unreleased source patch and retained an unmaintained dependency
warning. Bitcoin Core RPC is not an implemented RGB RC3 resolver, the licenses
of the candidate graph are not approved, and no O2A lifecycle was tested.

| Check | Result | Meaning |
| --- | --- | --- |
| Rust 1.98.1 isolated toolchain | Pass with setup caveat | Direct 1.98.1 binaries built the patched RGB CLI and exact electrs tag and ran the lock-remediation checks. The isolated `rustup` wrapper still exited 1 after installation because its temporary Cargo home lacked the proxy; a checked-in setup script must avoid that layout mistake. |
| Bitcoin Core 31.1 archive and regtest | Pass | SHA256 matched the published checksum; 11 checksum signatures validated and the Fanquake fingerprint matched the official verification page. GPG trust remained undefined in the isolated keyring. Daemon/RPC, a disposable wallet, 101 blocks, and a 50 BTC mature regtest balance worked with zero peers. |
| RGB runtime and wallet RC3 compile | Pass | Locked checks/builds passed with exact RC3 tags and Rust 1.98.1. Four runtime library tests passed. |
| RGB CLI debug-build invocation | Patched pass; upstream fail | A three-line patch removes nonexistent `mempool` from the Clap group and makes `create` write the `.wallet` path that `sync` reads. Patched `sync --help` passed; unmodified RC3 still exited 101. Current upstream `master` retains both defects and the `ELECRTUM_SERVER` typo. |
| RGB chain resolver | Patched pass | Under Rust 1.98.1, the patched CLI created the correctly named wallet and synced 101 UTXOs through exact electrs 0.12.0 backed by the same Core node. No manual rename was needed. Core RPC remains a TODO. |
| Bitcoin/RGB type conversion | Bounded pass | A separate manifest resolved BP secp256k1 0.30.0 and rust-bitcoin's 0.29.1. Compressed and x-only public keys round-tripped through validated canonical bytes, and malformed keys were rejected. Signatures, authorization, and consensus behavior remain untested. |
| O2A RGB lifecycle and independent import | Not run | No genesis, rotation, recovery-policy change, authorized recovery, revocation, consignment exchange, or second-client verification was performed. |
| Locked advisory and license scan | Fail for adoption | The tagged 342-package lock has 15 vulnerabilities and five warnings. Compatible updates leave three Esplora-path advisories. An Electrum-only source-patched graph has zero vulnerability advisories but one unmaintained warning and unapproved license expressions. None is adopted. |

These results make the first RGB experiment explicitly disposable. It must not
be promoted into `crates/o2a-rgb`, and its contract shape must not enter a
normative spec, until every Phase 0 gate passes.

## Exact smoke record

The run used:

- Rust/Cargo 1.98.1 in isolated temporary homes;
- Bitcoin Core 31.1.0, Linux archive SHA256
  `b80d9c3e04da78fb6f0569685673418cf686fadba9042d926d13fb87ff503f9e`;
- RGB Core `v0.12.0` at `388d9c38`;
- RGB standard library `v0.12.0-rc.3` at `e183bebf`; and
- RGB runtime/CLI `v0.12.0-rc.3` at `a1e6b415`.

Those hashes identify the inspected upstream repository tags. The runtime
build resolved its dependency packages through the upstream committed
`Cargo.lock`; that lockfile and its hash were not retained after the disposable
directory was deleted. The build is evidence that one resolution succeeded,
not a reproducible dependency inventory or an advisory-clean graph.

The relevant passing commands were equivalent to:

```text
cargo check --locked -p rgb-runtime --features resolver-electrum,fs
cargo check --locked -p rgb-wallet
cargo build --locked -p rgb-wallet
cargo test --locked -p rgb-runtime --lib --features resolver-electrum,fs
```

The failing probe was:

```text
rgb sync --help
```

The debug build exited 101 with a Clap assertion that the `ResolverOpt` group
contains the nonexistent `mempool` argument. Release-build and `cargo install`
behavior were not tested. The source also spells one Electrum environment name
as `ELECRTUM_SERVER`; do not expose that typo as an O2A configuration contract.

The node was bound to localhost in regtest with zero peers. The disposable
wallet, chain, sources, toolchain, and build outputs were deleted with the
temporary directory after the node stopped.

## Second disposable run

The second run closed the evidence-preservation, signed-checksum, local
resolver, and public-key conversion gaps. Its exact lockfiles, feature tree,
audit output, signature fingerprints, resolver log, and conversion source are
retained in the
[Phase 0 evidence bundle](../evidence/phase0/rgb-rc3-regtest-2026-09-23/README.md).

It does not adopt the graph. The resolver required the known temporary Clap
patch plus a newly observed wallet-directory rename, and the exact lock failed
the advisory gate. No O2A contract, identity, signature, transition, or
independent package validation was performed.

## Third disposable remediation run

The third run retained the exact patch, upstream locks, feature tree, sanitized
logs, source checks, and dependency experiments in the
[remediation evidence bundle](../evidence/phase0/rgb-rc3-remediation-2026-09-23/RUN.md).
It used Rust 1.98.1 and the exact electrs `v0.12.0` tag, whose annotated tag
peels to `37501cc4b94aea99e50670a6524fa3ad4ac9aabb`. This corrects the earlier
evidence record, which mislabeled current electrs `master` commit `d975dd03` as
the release tag.

The patched CLI passed `sync --help`, created `test2.wallet` directly, and
synced 101 UTXOs through the local resolver. Unmodified RC3 failed the parser
probe, and RGB upstream `master` at `27538224` still contained the parser,
wallet-path, and environment-name defects when inspected.

The [lock-remediation experiment](../evidence/phase0/rgb-rc3-remediation-2026-09-23/lock-review/SUMMARY.md)
made two bounded attempts:

- compatible updates reduced the full graph to three advisories, all through
  Esplora's `minreq -> rustls 0.21 -> rustls-webpki 0.101.7` path; and
- removing Esplora produced a 213-package Electrum-plus-filesystem graph that
  passed locked workspace checks and five tests with zero vulnerability
  advisories, but retained the unmaintained `paste 1.0.15` warning.

The second attempt changes upstream features and was not resolver-tested in
that form. It is evidence for a possible direction, not a selected patch or
dependency graph. No production crate or O2A identity was created.

## Compatibility gates for the next run

1. Start from the exact RC3 tags, then check for a newer matching release
   family before testing. Never mix the RGB-WG 0.12 family with an unrelated
   `rgb-protocol` 0.11.1 API by name alone.
2. Obtain an upstream release or a separately reviewed, maintained patch for
   the CLI parser and wallet-path defects. The retained experimental patch
   proves the corrections but is not an adopted fork.
3. Run a local Electrum or Esplora resolver backed by the checksum- and
   signature-verified Bitcoin Core build, unless the selected runtime gains a
   tested Core-RPC resolver.
4. Keep Core as the Bitcoin chain authority. Define and test explicit
   serialization/conversion boundaries between RGB/BP and rust-bitcoin types;
   inspect `cargo tree -d` for duplicate crypto versions.
5. Use the rust-bitcoin secp256k1 re-export inside code that uses rust-bitcoin.
   Do not independently add the newest `secp256k1` crate and assume its Rust
   types match either rust-bitcoin or RGB.
6. Complete the full O2A lifecycle, negative cases, simulated reorg, package
   export, and validation from a second clean client state.
7. Remove or replace the unmaintained `paste` dependency, eliminate all
   applicable advisories, and complete the license review before adoption.
8. Preserve the candidate lockfile, its hash, enabled-feature inventory, Cargo
   metadata, and source revisions as Phase 0 evidence, even when the experiment
   itself remains disposable. Commit a lockfile only with its reviewed
   candidate graph. Run `cargo audit`, all cargo-deny checks,
   source/provenance review, license inventory, and duplicate/version review
   before accepting it.

## Known security and correctness risks

| Risk | Current evidence | Required design mitigation |
| --- | --- | --- |
| rust-bitcoin consensus-sensitive behavior | Stable 0.32.102 predates the merged fix for a SegWit-v0 nonstandard-sighash correctness gap. rust-bitcoin also warns against using the crate as a consensus validator. | Do not approve 0.32.102 for the affected validation/signing path. Confirm a released fix, keep Core authoritative, and differential-test parsing and signing behavior. |
| Rust compiler/toolchain | Rust 1.98.0 had a vtable miscompile fixed by 1.98.1. Earlier Cargo releases also had 2026 extraction and registry issues. | Pin exactly 1.98.1 or a reviewed later patch release; assert it in CI and reject the stale system toolchain. |
| Cargo supply chain | A compromised maintainer published malicious `arrayref 0.3.10` and related crate versions in August 2026. A lockfile hash can faithfully lock malicious content. | Use isolated CI Cargo homes, locked builds, source allowlists, RustSec/cargo-deny checks, reviewed lockfile diffs, provenance review, and periodic rescans. Search caches and lockfiles for withdrawn malicious versions. |
| RGB release candidates | Core is final, but standard library/runtime are RC3; their advisory pages showing no published advisories is not an audit. | Keep the adapter narrow, preserve client-side validation, fuzz hostile consignments, cap resource use, and keep the experiment disposable until complete regtest/conformance evidence passes. |
| SQLite | The workstation has SQLite 3.45.1. Upstream fixed CVE-2026-11822 and CVE-2026-11824 in 3.53.2; 3.53.4 is current at this review. | Pin a patched bundled version or verify the system version. Use prepared statements, defensive mode, `trusted_schema=OFF`, no loadable extensions, no FTS initially, bounded imports, and never open an untrusted database as authority. |
| Nostr adapter | Multiple 2026 RustSec advisories covered malformed-message denial of service, unauthenticated wallet events, and relay verification/cache failures. | Keep Nostr deferred and discovery-only. At adoption, use versions patched for every applicable advisory, verify complete event IDs and signatures before policy or caching, reject wallet/spending instructions, bound inputs, and fuzz malformed events. |
| Bitcoin Core network/RPC | 31.1 fixes a 31.0 private-broadcast IP disclosure. Bitcoin Core publishes some vulnerability details only after affected releases reach end of life. | Use 31.1 or a reviewed later maintenance release, verify signed checksums, bind RPC locally with cookie auth, isolate data directories, run zero-peer regtest by default, and never put identity secrets in a Core wallet. |
| Public evidence parsers | Proof packages, DNS/social records, Pubky records, Nostr events, and RGB consignments are attacker-controlled bytes. | Enforce canonical encodings, byte/depth/count limits, fail-closed domain/network/key checks, deterministic evaluation, timeouts outside the core, and property/fuzz/adversarial tests. |

Pubky and PKARR showed no published upstream security advisories in this review;
that is not proof of audit or safety. Their Ed25519 keys remain optional signed
discovery bindings and can never authorize the BIP340 O2A identity lifecycle.

## Primary security references

- [Rust release history](https://blog.rust-lang.org/releases/latest/) and the
  [Cargo extraction advisory](https://blog.rust-lang.org/2026/03/21/cve-2026-33056/).
- [Rust supply-chain attack report](https://blog.rust-lang.org/2026/08/20/supply-chain-attack-on-arrayref/).
- [rust-bitcoin correctness issue](https://github.com/rust-bitcoin/rust-bitcoin/issues/6647)
  and its [merged fix](https://github.com/rust-bitcoin/rust-bitcoin/pull/6755).
- [Bitcoin Core 31.1 release notes](https://github.com/bitcoin/bitcoin/blob/master/doc/release-notes/release-notes-31.1.md)
  and [security policy/advisories](https://bitcoincore.org/en/security-advisories/).
- [SQLite vulnerability catalogue](https://sqlite.org/cves.html) and
  [SQLite 3.53.4 release](https://sqlite.org/releaselog/3_53_4.html).
- RustSec Nostr advisories for [malformed NIP-44](https://rustsec.org/advisories/RUSTSEC-2026-0216.html),
  [unauthenticated wallet events](https://rustsec.org/advisories/RUSTSEC-2026-0226.html),
  and [unverified relay events](https://rustsec.org/advisories/RUSTSEC-2026-0232.html).
- [RustSec tooling guidance](https://rustsec.org/), including `cargo-audit` and
  `cargo-deny`.
