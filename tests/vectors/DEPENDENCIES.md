# Vector-checker dependency record

SPDX-License-Identifier: CC0-1.0

This record applies only to the small cryptographic helper under
`crypto-checker/`. It does not adopt the RGB RC3 lock or authorize an O2A
implementation crate.

Recorded 2026-09-23:

- Rust `1.98.1`, Cargo `1.98.1`, cargo-audit `0.22.2`, and cargo-deny `0.20.2`
  ran in the pinned repository toolchain container;
- `Cargo.lock` SHA-256 is
  `749cbb90ab97ec334adbb7891f1b0bc7e5b8bbb9dd32193ab6a6e273f60e506b`;
- the locked graph contains seven packages, including the local package;
- `cargo audit --file tests/vectors/crypto-checker/Cargo.lock` reported no
  vulnerability advisories;
- `cargo deny check` passed the scoped source and license policy; and
- the only license expressions in the graph are `CC0-1.0` and
  `MIT OR Apache-2.0`.

The helper uses maintained libsecp256k1-backed BIP340 verification. Its
deterministic signing command exists only to regenerate public CC0 fixtures
with the published scalar-3 test key. It is not a wallet or production signer.
