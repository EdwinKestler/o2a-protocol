# RGB RC3 lock remediation experiment

Status: isolated, temporary experiment only. No O2A protocol or implementation
crate was changed; this directory retains only the sanitized evidence.

## Source and toolchain

- Repository: `RGB-WG/rgb`, tag `v0.12.0-rc.3`, commit `a1e6b41524131f6d6f183b2235fdaacb5c1abb31`.
- Toolchain: `rustc 1.98.1 (48a229cea 2026-09-01)`; `cargo 1.98.1 (797e8a9bc 2026-08-05)`.
- Audit tool: `cargo-audit 0.22.2`, installed inside the isolated temporary Cargo home.

## Baseline and targeted updates

The tagged lock had 342 package entries and SHA-256 `3103095dac0a9f7aaa3d72c16770e833765b588d2f124b4b718f92398257dda1`. Baseline `cargo audit --json` reported 15 advisories, plus warnings for `paste 1.0.15` (unmaintained), `anyhow 1.0.98` and both `rand` versions (unsoundness advisories), and yanked `slab 0.4.10`.

The following compatible updates were attempted with Rust 1.98.1:

```text
cargo update -p aws-lc-rs          # aws-lc-rs 1.13.1 -> 1.18.1; aws-lc-sys 0.29.0 -> 0.45.0
cargo update -p bytes              # 1.10.1 -> 1.12.1
cargo update -p rustls@0.21.12     # no compatible update available
cargo update -p rustls@0.23.28     # 0.23.28 -> 0.23.45; webpki 0.103.3 -> 0.103.15
cargo update -p slab               # 0.4.10 -> 0.4.12
cargo update -p time               # 0.3.41 -> 0.3.55
cargo update -p anyhow             # 1.0.98 -> 1.0.104
cargo update -p rand@0.8.5         # 0.8.5 -> 0.8.8
cargo update -p rand@0.9.1         # 0.9.1 -> 0.9.5
cargo update -p rustls-webpki@0.101.7 # no compatible update available
cargo update -p minreq             # 2.14.0 -> 2.14.1
```

The resulting targeted lock had 313 package entries and SHA-256 `57c8284b18fd6878c451cd6427d0249adb215712c9d20136e0d3d84a07c46cc2`. Audit dropped to three advisories, all on `rustls-webpki 0.101.7` (`RUSTSEC-2026-0104`, `RUSTSEC-2026-0099`, `RUSTSEC-2026-0098`), plus the unmaintained `paste` warning.

The reachable feature path is `rgb-wallet -> rgb-runtime/resolvers-all -> resolver-esplora -> bp-esplora/blocking-https -> minreq HTTPS/Rustls -> rustls 0.21.12 -> rustls-webpki 0.101.7`. RC3's `minreq 2.14.1` still selects the Rustls 0.21 line; the lock offers no compatible patch for the vulnerable `0.101.7` release.

## Electrum plus filesystem feature-minimized check

To test whether the vulnerable Esplora path can be removed while keeping the local Electrum resolver and filesystem persistence, the throwaway clone was edited to remove the `bp-esplora` dependency from the runtime/CLI graph, remove Esplora from `resolvers-all`, and make the CLI's Esplora selection fail explicitly. This is an experiment-only source patch to the upstream RC3 tag, not an upstream-compatible dependency change.

The resulting lock had 213 package entries and SHA-256 `29302f64c33735957b8be2eeca5bc3e3292759b8e3b713923a013c05988d2522`. It contains no `bp-esplora`, `minreq`, `rustls 0.21.12`, or `rustls-webpki 0.101.7` entries. The Electrum and `fs` feature paths remain enabled.

Results:

- `cargo check --workspace --locked`: passed.
- `cargo test --workspace --locked`: passed; 5 unit tests passed, with zero failures.
- `cargo audit --json`: zero vulnerability advisories; one warning remains, `paste 1.0.15` (`RUSTSEC-2024-0436`, unmaintained).
- Cargo metadata license scan found 25 distinct expressions. Notable review items include `base85 2.0.0` under `MPL-2.0-no-copyleft-exception`, `webpki-roots 0.26.11` and `1.0.1` under `CDLA-Permissive-2.0`, and several `Unlicense`/LGPL alternative expressions. This was metadata triage, not a `cargo-deny` compliance run.

This shows an Electrum-only graph can remove the three advisories, but it requires removing Esplora support and still has an unmaintained dependency warning. It is therefore not a clean, adoptable dependency graph. No local Electrum network sync was run in this subtask; only the workspace check and tests were run. No O2A identity, schema, or crate was created.

## Preserved evidence

- Reconstructed patch for the temporary source changes:
  `electrum-only-experiment.patch`, SHA-256
  `dbf29ad34ec7e10fb1470ae4f153500ae3a299b0e394a4ca6f31cff546c82040`.
  It was reconstructed from the recorded edits after the original temporary
  clone was deleted, then corrected and successfully apply-checked against a
  fresh checkout of exact RC3 commit `a1e6b415`.
- `baseline-Cargo.lock`, `baseline-audit.json`
- `targeted-updates-Cargo.lock`, `remediated-audit.json`
- `electrum-only-Cargo.lock`, `electrum-only-audit.json`
- Dependency paths in `tree-*.txt`, `updated-webpki-path.txt`, `updated-minreq-path.txt`, `electrum-only-paste-path.txt`, and `electrum-only-electrum-path.txt`
- License expression summaries in `electrum-only-license-expressions.txt` and `electrum-only-license-review.txt`
