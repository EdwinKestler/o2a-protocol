# RGB RC3 Regtest Resolver Evidence — 2026-09-23

**Result:** bounded resolver and public-key conversion checks passed, while the
locked dependency audit failed. This evidence does not select the RGB lineage,
adopt a dependency graph, create an O2A contract, or authorize production use.

No O2A identity or real-value key was created. Bitcoin Core, electrs, RGB
wallet, source, Cargo cache, and build directories were deleted after the run.
Only the sanitized evidence in this directory remains.

## Immutable inputs

| Component | Revision or artifact |
| --- | --- |
| RGB runtime/CLI | `v0.12.0-rc.3`, `a1e6b41524131f6d6f183b2235fdaacb5c1abb31` |
| RGB Core | `v0.12.0`, `388d9c386117cf74f67f185b65adf946e775091c` |
| RGB standard library | `v0.12.0-rc.3`, `e183bebfed9ffd0ba8c6f7110fe3e097f23cd70b` |
| RGB upstream lock | [`rgb-runtime-Cargo.lock`](rgb-runtime-Cargo.lock), SHA256 `3103095dac0a9f7aaa3d72c16770e833765b588d2f124b4b718f92398257dda1` |
| electrs | `d975dd03f2a410c4473116d5a2be950a205e0443`, the then-current `master` commit; this run incorrectly labeled it `v0.12.0` |
| electrs lock | [`electrs-Cargo.lock`](electrs-Cargo.lock), SHA256 `2fc62ab317822f7435a732662ba6cb187568fd781765aea9c492c27d32fad53e` |
| Bitcoin Core | 31.1 x86_64 Linux archive, SHA256 `b80d9c3e04da78fb6f0569685673418cf686fadba9042d926d13fb87ff503f9e` |
| Rust used by resolver run | rustc/cargo 1.96.1; the earlier isolated 1.98.1 check was not repeated |

RGB Core and the standard library were crates.io packages selected by the
runtime lockfile. Their Git hashes above identify the corresponding inspected
upstream tags; they were not Git dependencies in that lock.

## Bitcoin Core provenance

The archive hash matched the published `SHA256SUMS`. GPG validated 11
signatures on `SHA256SUMS.asc` using builder keys from the Bitcoin Core
`guix.sigs` repository. Fanquake's primary fingerprint
`E777299FC265DD04793070EB944D35F9AC3DB76A` matches the fingerprint published
on Bitcoin Core's download verification page.

The imported keys had `TRUST_UNDEFINED` in the isolated GPG home. The result
therefore establishes cryptographically valid signatures and a published
fingerprint match, not independent Web-of-Trust certification. See
[`bitcoin-core-31.1-signatures-sanitized.txt`](bitcoin-core-31.1-signatures-sanitized.txt).

## Local resolver result

Bitcoin Core ran with zero peers on regtest and mined 101 blocks. electrs
0.12.0 indexed that same node through local cookie-authenticated RPC and served
Electrum on `127.0.0.1:19546`. Its header response reported height 101.

The RGB RC3 debug CLI required two disposable workarounds:

1. remove nonexistent `mempool` from the Clap `ResolverOpt` argument group;
2. move the wallet directory from `test` to `test.wallet`, because `rgb create`
   writes the former while `rgb sync` reads the latter.

The `ELECRTUM_SERVER` source typo was not patched; the run supplied
`--electrum=tcp://127.0.0.1:19546` explicitly. The resulting `rgb sync` exited
0, persisted 101 regtest UTXOs, and caused 40
`blockchain.scripthash.listunspent` calls in [`electrs.log`](electrs.log).
This proves a bounded resolver path after documented workarounds, not
unmodified CLI readiness or RGB client-side contract validation.

The later [Rust 1.98.1 remediation run](../rgb-rc3-remediation-2026-09-23/RUN.md)
corrected the electrs provenance error: the annotated `v0.12.0` tag peels to
`37501cc4b94aea99e50670a6524fa3ad4ac9aabb`, and that exact tag was used in
the later run. The retained lock in this historical bundle belongs to the
`d975dd03` checkout and must not be represented as the tag's lock.

The exact enabled graph is preserved in
[`rgb-feature-tree.txt`](rgb-feature-tree.txt). Absolute temporary paths were
replaced with `<temporary_workspace>`; package names, versions, and features
were not changed.

## Dependency audit result

`cargo audit 0.22.2`, using RustSec database revision
`1e640cd56d7604993e3a9ec392060666e3b95ccc`, scanned the 342-package RGB lock
and exited 1 with 15 vulnerability findings and five warnings. The findings
include affected versions of `aws-lc-sys`, `bytes`, `rustls`, two
`rustls-webpki` versions, `slab`, and `time`. Warnings cover unmaintained,
unsound, or yanked versions of `paste`, `anyhow`, `rand`, and `slab`.

The complete result and upgrade floors are in
[`cargo-audit-output.txt`](cargo-audit-output.txt). This is an adoption blocker
for the exact lock, even though not every advisory is necessarily reachable in
the resolver path exercised here.

`cargo deny 0.20.2` reported only crates.io sources. Its license inventory
contained these 16 identifiers or expressions:

```text
Apache-2.0
Apache-2.0 WITH LLVM-exception
BSD-2-Clause
BSD-3-Clause
BSL-1.0
CC0-1.0
CDLA-Permissive-2.0
ISC
LGPL-2.1-or-later
MIT
MIT-0
MPL-2.0
MPL-2.0-no-copyleft-exception
OpenSSL
Unicode-3.0
Unlicense
```

The intentionally minimal Apache-2.0/MIT/CC0-1.0 allowlist rejected 34
license findings. That does not make every additional license incompatible;
it means each must be reviewed before the dependency policy expands. See the
full [license inventory](cargo-deny-license-list.txt), [strict check](cargo-deny-license-check.txt),
and [source result](cargo-deny-source-check.txt).

## secp256k1 conversion boundary

The upstream RGB lock has `secp256k1 0.30.0` and no rust-bitcoin package. A
separate disposable manifest combined `bp-core 0.12.0` with rust-bitcoin
0.32.102, which resolved secp256k1 0.30.0 and 0.29.1 respectively.

The test passed a well-known public compressed key and BIP340 x-only key
through canonical bytes into `bp::CompressedPk` and `bp::XOnlyPk`, parsed them
back with rust-bitcoin's secp256k1 type, confirmed equality, and confirmed both
libraries rejected malformed examples. The retained [source and transcript](conversion/TRANSCRIPT.md)
prove only this public-key byte boundary. They do not prove signatures,
spending authorization, O2A controller authorization, RGB transition
validity, or consensus behavior. rust-bitcoin 0.32.102 remains excluded from
consensus-sensitive validation.

## Remaining gates

- select or produce a dependency graph without unresolved applicable
  advisories and review every additional license;
- fix or update past both RC3 CLI defects and repeat the resolver run without
  source or wallet-path workarounds;
- repeat the run with the pinned Rust 1.98.1 toolchain;
- test signature conversion separately without using a spending key as an O2A
  identity key; and
- only after the RGB lineage is accepted, exercise the O2A identity lifecycle,
  client-side validation, negative cases, reorg behavior, and independent
  package import.
