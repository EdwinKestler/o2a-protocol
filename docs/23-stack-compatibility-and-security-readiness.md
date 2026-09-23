# 23 — Stack Compatibility and Security Readiness

**Status:** supporting evidence record, 2026-09-23. The run was disposable,
regtest-only, and used no O2A or real-value keys. It does not select the RGB
lineage, freeze a dependency graph, or demonstrate an O2A identity lifecycle.

## Verdict

The proposed development baseline is feasible, but the exact stack is **not
ready to adopt**. Rust 1.98.1, the RGB-WG RC3 libraries, and Bitcoin Core 31.1
regtest passed their bounded checks. The debug-built RGB CLI has a reproducible
argument-parser assertion, Bitcoin Core RPC is not an implemented RGB RC3
resolver, and the conversion boundary between different secp256k1 crate types
is untested. A rust-bitcoin correctness fix also landed after the latest stable
release.

| Check | Result | Meaning |
| --- | --- | --- |
| Rust 1.98.1 isolated toolchain | Partial pass | Direct `rustc` and `cargo` worked. The isolated `rustup` wrapper exited 1 after installation because its temporary Cargo home lacked the proxy. A checked-in setup script must avoid that layout mistake. |
| Bitcoin Core 31.1 archive and regtest | Pass with provenance gap | SHA256 matched the published checksum; daemon/RPC, a disposable wallet, 101 blocks, and a 50 BTC mature regtest balance worked with zero peers. The checksum file's signature was not verified. |
| RGB runtime and wallet RC3 compile | Pass | Locked checks/builds passed with exact RC3 tags and Rust 1.98.1. Four runtime library tests passed. |
| RGB CLI debug-build invocation | Fail | `rgb sync --help` exited 101 because Clap group `ResolverOpt` names nonexistent argument `mempool`. Release-build and `cargo install` behavior were not tested, so this establishes a debug-build defect rather than every distribution path. Compile success is not CLI readiness. |
| RGB chain resolver | Blocked | Electrum and Esplora paths exist. The Bitcoin RPC resolver is a commented TODO, so the local resolver profile still needs implementation and proof. |
| Bitcoin/RGB type conversion | Untested | RGB RC3 locks secp256k1 0.30.0; stable rust-bitcoin 0.32.102 specifies secp256k1 0.29.0. Multiple versions can coexist, but their Rust key types do not directly interoperate; the adapter's serialization and validation boundary remains unproven. |
| O2A RGB lifecycle and independent import | Not run | No genesis, rotation, recovery-policy change, authorized recovery, revocation, consignment exchange, or second-client verification was performed. |
| Locked advisory and license scan | Not run | The disposable upstream lockfile was not retained, and no O2A lockfile exists. Run the scanners on the graph proposed for adoption. |

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

## Compatibility gates for the next run

1. Start from the exact RC3 tags, then check for a newer matching release
   family before testing. Never mix the RGB-WG 0.12 family with an unrelated
   `rgb-protocol` 0.11.1 API by name alone.
2. Patch or update past the CLI parser defect and prove that the chosen CLI
   and library operations work, not merely compile.
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
7. Preserve the candidate lockfile, its hash, enabled-feature inventory, Cargo
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
