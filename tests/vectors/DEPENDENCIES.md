# Vector-checker dependency record

SPDX-License-Identifier: CC0-1.0

This record applies only to the small cryptographic helper under
`crypto-checker/`. It does not adopt the RGB RC3 lock or authorize an O2A
implementation crate.

Recorded 2026-09-24:

- Rust `1.98.1`, Cargo `1.98.1`, cargo-audit `0.22.2`, and cargo-deny `0.20.2`
  ran in the pinned repository toolchain container;
- `Cargo.lock` SHA-256 is
  `ca8019a81488103cd345edccb4865a487c5e97ee393bff045005d36214eb6a8f`;
- the lock contains 21 packages, including the local package; with
  `exclude-dev = true`, the executable plus build graph contains ten packages;
- `cargo audit --file tests/vectors/crypto-checker/Cargo.lock` reported no
  vulnerability advisories;
- `cargo deny check` passed the scoped source and license policy; and
- the complete license-expression set in the checked executable/build graph is
  `CC0-1.0` and `MIT OR Apache-2.0`. Lock metadata for excluded development
  dependencies additionally contains `(MIT OR Apache-2.0) AND Unicode-3.0`.

Development dependencies are excluded because they are never built into or
distributed with this standalone checker. The new executable dependencies are
exactly pinned `bitcoin_hashes 0.14.101` and its normal dependencies
`bitcoin-io 0.1.101`, `hex-conservative 0.2.3`, and `arrayvec 0.7.8`.
The checker implements only the bounded BIP32 hardened and BIP85 operations
needed by the vectors. It does not depend on the `bitcoin` crate. Rust-bitcoin
was rejected because it declares the MITNFA-licensed `hex_lit` crate as a
normal dependency even though rust-bitcoin uses it only in test modules.

The helper uses maintained libsecp256k1-backed BIP340 verification. Its
deterministic signing command exists only to regenerate public CC0 fixtures
with the published scalar-3 test key. Its derivation commands consume only
permanently unsafe public test material and emit `k || c` hex, never Base58.
It is not a wallet or production signer. The fail-closed `self-test` command
passes BIP32 test vector 1 at `m/0H` and the BIP85 BIP32-XPRV application-32,
index-0 vector before derivation fixtures are accepted.
