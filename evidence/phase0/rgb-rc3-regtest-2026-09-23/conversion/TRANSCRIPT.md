# Disposable public-key conversion smoke — 2026-09-23

This is an evidence copy of source and terminal results. It contains only a
well-known public generator key. No wallet, secret, target, Cargo cache, or
upstream source checkout is retained here.

## Upstream lineage and lock

RGB-WG runtime/CLI tag `v0.12.0-rc.3` was cloned at commit
`a1e6b41524131f6d6f183b2235fdaacb5c1abb31`. Its committed `Cargo.lock`
SHA256 was
`3103095dac0a9f7aaa3d72c16770e833765b588d2f124b4b718f92398257dda1`.
That lockfile records `rgb-core 0.12.0`, `rgb-std 0.12.0-rc.3`,
`secp256k1 0.30.0`, and `secp256k1-sys 0.10.1`. The conversion test did not
build or execute the RGB runtime. It used BP Core 0.12.0, which is part of the
RC3 lineage, plus stable rust-bitcoin 0.32.102.

## Conversion test

The source is `src/main.rs` with dependencies in `Cargo.toml`. It was run in an
isolated temporary Cargo home and target directory with host Rust/Cargo
1.96.1. The standalone test's generated `Cargo.lock` SHA256 was
`870d4a9c637ad9f399086bed82828ab18323e0d7d1af126ba0f278fd5a34f094`.
The earlier full RC3 build used Rust/Cargo 1.98.1; this narrow conversion
smoke did not reinstall that toolchain.

Passing command:

```text
CARGO_HOME=<disposable>/cargo CARGO_TARGET_DIR=<disposable>/target cargo run --locked
```

Output:

```text
Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.17s
Running `target/debug/o2a-secp-boundary-smoke`
bitcoin secp -> serialized bytes -> BP CompressedPk/XOnlyPk -> bitcoin secp: pass
malformed compressed/x-only public key rejection: pass
```

The program converts a `bitcoin::secp256k1::PublicKey` to compressed bytes,
validates those bytes as `bp::CompressedPk`, converts back, and checks equality.
It also converts an x-only BIP340 public key through `bp::XOnlyPk` and back.
BP and rust-bitcoin independently reject malformed compressed and x-only
representations in the tested cases. This proves byte-level type conversion
for public keys only. It does not prove O2A authorization, private-key custody,
signatures, RGB state transitions, wire encoding, or consensus behavior.

## Resolved secp256k1 versions

`cargo tree --locked -i secp256k1@0.29.1`:

```text
secp256k1 v0.29.1
└── bitcoin v0.32.102
    └── o2a-secp-boundary-smoke v0.0.0
```

`cargo tree --locked -i secp256k1@0.30.0`:

```text
secp256k1 v0.30.0
├── bp-consensus v0.12.0
│   ├── bp-core v0.12.0
│   │   └── o2a-secp-boundary-smoke v0.0.0
│   ├── bp-dbc v0.12.0
│   │   └── bp-core v0.12.0
│   └── bp-seals v0.12.0
│       └── bp-core v0.12.0
└── bp-dbc v0.12.0
```

The two `secp256k1` Rust types are distinct. Cross the boundary through
canonical public-key bytes and validate on receipt. Never transmute types or
assume a Bitcoin spending key can authorize an O2A identity.
