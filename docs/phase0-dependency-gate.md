# Phase 0 RGB dependency gate

**Status:** recorded 2026-09-23 from retained evidence only. This decision does
not start a new experiment, regtest, crate, or lock adoption. The RGB
dependency gate remains **OPEN**. An open dependency gate does not finish
Phase 0.

Three questions are decided from the
[third disposable remediation run](../evidence/phase0/rgb-rc3-remediation-2026-09-23/RUN.md)
and its
[lock review](../evidence/phase0/rgb-rc3-remediation-2026-09-23/lock-review/SUMMARY.md).
This page does not select an RGB lineage, vendor RGB, or close the
[Phase 0 roadmap](13-roadmap.md).

## Recheck — 2026-09-23

The published RGB-WG `rgb` tag list still ends at `v0.12.0-rc.3` from
15 July 2025. RGB Core `v0.12.0` remains the latest consensus tag. A separate
`v0.11.1` line is in production use and must not be mixed with the 0.12
family. Neither line meets the adoption checklist: the 0.12 standard library
and runtime remain release candidates with the retained audit findings, and
`v0.11.1` is a different protocol. No new lock was built. The gate stays open.

## 1. CLI overlay

**Decision:** the three-line patch in
[rgb-rc3-cli.patch](../evidence/phase0/rgb-rc3-remediation-2026-09-23/rgb-rc3-cli.patch)
is a disposable compatibility overlay for dev checks. It is not an upstream
fix and not a production pin.

The retained patch changes three lines in the RGB-WG `v0.12.0-rc.3` CLI. It
drops the nonexistent `mempool` member from the Clap resolver group, and it
makes `create` write the `.wallet` path that `sync` loads. The unmodified tag
still fails `rgb sync --help` with exit 101. A read-only check of upstream
`master` at `275382240ae1b8a56beb120e926e60d86f49785b`, recorded in that same
run, still found the `mempool` group entry, the `create` path mismatch, and
the `ELECRTUM_SERVER` name. The overlay does not change that environment-name
typo.

The dev check that synced 101 regtest UTXOs used this overlay on the tagged
lock. That result shows a disposable dev path. It does not adopt the patch or
the lock.

## 2. Lock adoption

**Decision:** no lock is adopted. The RGB dependency gate remains **OPEN**.

The full RC3 lock has 15 vulnerability advisories. The tagged 342-package lock,
SHA-256 `3103095dac0a9f7aaa3d72c16770e833765b588d2f124b4b718f92398257dda1`,
failed `cargo audit` with 15 vulnerabilities and five warnings, including
unmaintained `paste` 1.0.15. That scan used `cargo-audit` 0.22.2 against
RustSec database revision `1e640cd56d7604993e3a9ec392060666e3b95ccc`. The lock
remains unadopted.

Compatible updates under Rust 1.98.1 left three `rustls-webpki` 0.101.7
advisories (`RUSTSEC-2026-0104`, `RUSTSEC-2026-0099`, and `RUSTSEC-2026-0098`)
on the resulting 313-package lock. No compatible update was available for
`rustls` 0.21.12 or `rustls-webpki` 0.101.7. The reachable path is:

```text
rgb-wallet -> rgb-runtime/resolvers-all -> resolver-esplora
  -> bp-esplora/blocking-https -> minreq HTTPS/Rustls
  -> rustls 0.21.12 -> rustls-webpki 0.101.7
```

The unmaintained `paste` warning remained after those updates.

The Electrum-only experiment reaches zero vulnerability advisories but keeps
unmaintained `paste` 1.0.15 (`RUSTSEC-2024-0436`), needs an unreleased source
patch, and has unreviewed extra license expressions. Removing Esplora produced
a 213-package lock that passed locked workspace checks and five tests. That
subtask did not sync it against a local Electrum network. The source change is
the retained `electrum-only-experiment.patch`, an experiment-only patch to the
RC3 tag, not an upstream-compatible dependency update. Its license scan was
metadata triage, not a `cargo-deny` run: 25 expressions, including
`MPL-2.0-no-copyleft-exception`, `CDLA-Permissive-2.0`, and `Unlicense`/LGPL
alternatives, were not accepted. Neither candidate lock is adopted.

## 3. rust-bitcoin 0.32.102

**Decision:** `rust-bitcoin` 0.32.102 stays excluded from consensus-sensitive
signing. No later stable 0.32 release was recorded. Do not substitute
`0.33.0-beta`.

The retained registry check on 2026-09-23, using crates.io through
`cargo info` and `cargo search`, found `0.32.102` published as a stable
release. It did not find `0.32.103`, `0.32.104`, or `0.32.105`. The registry
latest it recorded was `0.33.0-beta` only. The checked decision keeps 0.32.102
off the affected consensus-sensitive validation and signing path and does not
substitute a beta without a separate review. This gate does not perform that
review.

The standing exclusion, which that check left in force, is the one in the
[compatibility record](23-stack-compatibility-and-security-readiness.md):
stable 0.32.102 predates the merged fix for a SegWit-v0 nonstandard-sighash
correctness gap, and rust-bitcoin warns against using the crate as a consensus
validator. The registry note is
[rust-bitcoin-release-check.txt](../evidence/phase0/rgb-rc3-remediation-2026-09-23/rust-bitcoin-release-check.txt).

## Phase 0

An open dependency gate does not finish Phase 0. The roadmap still requires a
selected and pinned compatible RGB stack. This decision does not close Phase 0
and does not authorize a production RGB crate.

## Feature-aware measurement — 2026-09-24

This entry does not change the criteria above and does not adopt a lock.
Evidence: [rgb-rc3-compiled-graph-2026-09-24](../evidence/phase0/rgb-rc3-compiled-graph-2026-09-24/RUN.md).

1. `bp-esplora` on `rgb-runtime` is optional (`resolver-esplora`); the default feature set does not reach it, `minreq`, or `rustls` 0.21. Measurement artifact. The CLI package `rgb-wallet` still depends on it directly.
2. `rustls-webpki` 0.101.7 is absent from the `resolver-electrum` + `fs` tree. The three lock-wide advisories are a measurement artifact. `paste` 1.0.15 remains in that tree, and feature-aware `cargo deny` still fails on it.
3. An unmodified library consumer synced 101 regtest UTXOs through electrs. The CLI patch blocker is a measurement artifact for a library consumer.
4. License failures on the compiled graph are a real allowlist blocker: ISC, MIT-0, Unicode-3.0, CDLA-Permissive-2.0, and copyleft `MPL-2.0-no-copyleft-exception`. This is triage, not an accepted exception list.

## Consumer dependency shape — 2026-09-24

O2A consumes `rgb-runtime` as a library with `default-features = false` and
features `resolver-electrum` and `fs`. It does not depend on `rgb-wallet`, the
CLI package. The retained feature-aware consumer manifest and compiled tree
demonstrate that this shape excludes the CLI's direct Esplora dependency and
the lock-wide `rustls-webpki` advisories. This statement fixes the consumer
boundary only; it does not adopt the RC3 lock, define an O2A RGB program, or
close the dependency gate.

## Gate restatement — 2026-09-24

The dependency gate remains **OPEN**. After the feature-aware measurement and
the maintainer's license and advisory decisions, these blockers remain:

1. The matching RGB 0.12 application/runtime stack is not a final release.
   RGB Core 0.12.0 is final, but the standard library and runtime used by this
   consumer remain at `v0.12.0-rc.3`; their contract shape may change before a
   mainnet-capable O2A release.
2. The concrete O2A RGB program bytes and identifiers are not yet defined or
   bound to the semantic identity contract.
3. RGB execution fixtures have not run for genesis, rotation, recovery,
   cancellation, revocation, bad seals, forked history, reorgs, or independent
   package import.

A disposable regtest or testnet consumer pinned to RGB-WG `rgb`
`v0.12.0-rc.3` commit `a1e6b415` is permitted as the 2026-09-24 demo lineage
for evidence and demonstration only. It must remain isolated from production
custody and use disposable test identities and test-value bitcoin. Nothing
derived from that consumer enters normative specifications or persistent O2A
identities. This permission does not adopt an RGB lock, authorize a production
crate, or close Phase 0.
