# Feature-aware RGB RC3 graph measurement — 2026-09-24

Disposable evidence only. Nothing was adopted: no crate, lock, feature set,
or patch entered the O2A implementation tree. The dependency-gate criteria
are unchanged.

## Inputs

| Item | Value |
| --- | --- |
| Tag | `a1e6b41524131f6d6f183b2235fdaacb5c1abb31` (`v0.12.0-rc.3`) |
| Lock | [targeted-updates-Cargo.lock](targeted-updates-Cargo.lock), SHA-256 `57c8284b18fd6878c451cd6427d0249adb215712c9d20136e0d3d84a07c46cc2` |
| Compiler | rustc 1.98.1 `48a229cea`; cargo 1.98.1 `797e8a9bc` |
| Audit tools | cargo-audit 0.22.2; cargo-deny 0.20.2 |
| Source patch | none |

The consumer crate depends on `rgb-runtime` with `default-features = false`
and `features = ["resolver-electrum", "fs"]`. `rgb-wallet` was not added as a
dependency. Its manifest unconditionally requests `resolvers-all`, which would
enable Esplora. That is the CLI package, not the library feature set O2A
would compile.

## Question 1

`bp-esplora` is optional on `rgb-runtime`. The feature that enables it is
`resolver-esplora` (`bp-esplora/blocking-https`). The default feature set is
`std`. A tree of that default set contains neither `bp-esplora`, `minreq`,
nor `rustls`. `paste` is still present through the non-optional amplify path.

`rgb-wallet` declares `bp-esplora` as a required dependency and enables
`rgb-runtime` features `resolvers-all`, `fs`, and `serde`. Quoted lines are in
[q1-manifest-quotes.txt](q1-manifest-quotes.txt).

## Question 2

`cargo tree -p rgb-runtime --no-default-features --features resolver-electrum,fs -e normal,build --locked` is [cargo-tree-runtime.txt](cargo-tree-runtime.txt).

| Crate | In electrum+fs tree |
| --- | --- |
| bp-esplora | absent |
| minreq | absent |
| rustls 0.21.12 | absent |
| rustls-webpki 0.101.7 | absent |
| rustls 0.23.45 | present, through `bp-electrum` |
| rustls-webpki 0.103.15 | present, through that rustls |
| paste 1.0.15 | present |

`cargo check -p rgb-runtime --no-default-features --features resolver-electrum,fs --locked` finished successfully. The separate consumer crate also compiled with `--locked` after its own offline lock was written. See [cargo-check-runtime.txt](cargo-check-runtime.txt).

`cargo audit --file` on the targeted-updates lock reported three
`rustls-webpki` 0.101.7 advisories and exited 1. That version is not in the
electrum+fs tree. See [cargo-audit-lock.txt](cargo-audit-lock.txt).

`cargo deny check advisories licenses sources` on the consumer graph exited 5.
Advisories failed on unmaintained `paste` 1.0.15 (`RUSTSEC-2024-0436`).
Licenses failed. Sources passed. The allowlist was not widened. Verbatim
output is [cargo-deny-consumer.txt](cargo-deny-consumer.txt).

## Question 3

The unmodified library API created a wallet directory, derived an address,
and `update_utxos` against local electrs returned `utxos 101` with exit 0.
No CLI patch was applied. The three-line patch remains a CLI blocker only.
The sanitized result is [sync-log.sanitized.txt](sync-log.sanitized.txt).
No O2A identity or contract was created. The wallet, chain, and checkout were
deleted after this record.

## Question 4

Feature-aware license triage, not an adoption decision:

| Class | Expression | Packages seen |
| --- | --- | --- |
| Allowed | CC0-1.0, MIT, Apache-2.0, MIT OR Apache-2.0, BSD-3-Clause | the rest of the graph that deny did not reject |
| Permissive, not allowed by this pass | ISC | `aws-lc-rs` 1.18.1, `rustls-webpki` 0.103.15, `untrusted` 0.9.0 |
| Permissive, not allowed by this pass | MIT-0 | `borrow-or-share` 0.2.2, and inside the `aws-lc-sys` 0.45.0 expression |
| Permissive, not allowed by this pass | Unicode-3.0 | `unicode-ident` 1.0.26, combined with MIT OR Apache-2.0 |
| Permissive, not allowed by this pass | CDLA-Permissive-2.0 | `webpki-roots` 0.26.11 and 1.0.1 |
| Copyleft | MPL-2.0-no-copyleft-exception | `base85` 2.0.0 |

No unknown license was reported. Deny classified the MPL expression as
copyleft.
