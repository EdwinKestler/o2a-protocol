# Disposable RGB RC3 CLI remediation and regtest check — 2026-09-23

## Result

The **unmodified** `RGB-WG/rgb` `v0.12.0-rc.3` debug CLI still fails `rgb sync --help` with exit 101: Clap's `ResolverOpt` group names a nonexistent `mempool` argument. A disposable three-line [patch](rgb-rc3-cli.patch) fixes that group and makes `create` use the same `.wallet` path that `sync` loads. With this patch, the CLI built under Rust 1.98.1 and synced against local Bitcoin Core 31.1 through local electrs 0.12.0. The run created no O2A identity or contract.

| Check | Exit/result |
| --- | --- |
| Patched `cargo build --locked -p rgb-wallet` | 0, debug profile |
| Patched `rgb sync --help` | 0 |
| Patched `rgb create --wpkh test2 <disposable public descriptor>` | 0; created `test2.wallet` directly |
| Patched `rgb sync --electrum=tcp://127.0.0.1:19546 test2` | 0; 101 UTXOs stored |
| electrs resolver calls | 80 `blockchain.scripthash.listunspent` calls across two successful syncs |
| Unmodified `cargo build --locked -p rgb-wallet` | 0 |
| Unmodified `rgb sync --help` | 101; Clap assertion |
| RGB locked dependency audit | Exit 1; 15 vulnerabilities and 5 warnings across 342 packages |

Bitcoin Core reported `regtest`, 101 blocks, and zero peers in [core-status.json](core-status.json) and [core-peer-count.txt](core-peer-count.txt). electrs indexed 102 blocks including genesis and served Electrum on `127.0.0.1:19546`; see [sanitized log](electrs.sanitized.log). The RGB wallet's 101 UTXOs and 80 resolver calls are captured as counts in [rgb-utxo-count.txt](rgb-utxo-count.txt) and [electrs-listunspent-count.txt](electrs-listunspent-count.txt). The public descriptor, wallet, chain database, and build directories are not retained.

## Inputs and provenance

| Component | Exact input |
| --- | --- |
| RGB RC3 tag | `a1e6b41524131f6d6f183b2235fdaacb5c1abb31` |
| RGB lock | [RGB-Cargo.lock](RGB-Cargo.lock), SHA256 `3103095dac0a9f7aaa3d72c16770e833765b588d2f124b4b718f92398257dda1` |
| CLI patch | [rgb-rc3-cli.patch](rgb-rc3-cli.patch), SHA256 `0c3cba049efd7919aa188ea7ab70e92192bb0e1c6f770fd8cdc01bc44f48cf38` |
| electrs `v0.12.0` annotated tag object | `7d2aec6cc60f0f67c9bf518d180fb55105935344` |
| electrs `v0.12.0` peeled commit | `37501cc4b94aea99e50670a6524fa3ad4ac9aabb` |
| electrs lock | [electrs-Cargo.lock](electrs-Cargo.lock), SHA256 `2fc62ab317822f7435a732662ba6cb187568fd781765aea9c492c27d32fad53e` |
| Bitcoin Core archive | `bitcoin-31.1-x86_64-linux-gnu.tar.gz`, SHA256 `b80d9c3e04da78fb6f0569685673418cf686fadba9042d926d13fb87ff503f9e` |
| Compiler and build tool | rustc 1.98.1 `48a229cea`; cargo 1.98.1 `797e8a9bc` |
| RGB `secp256k1` | 0.30.0 in the retained lock |

The Bitcoin archive matched the published SHA256. This run reused the repository's earlier checksum-signature evidence; it did not repeat GPG verification. Rustup reported exit 1 after downloading the isolated toolchain because its temporary `CARGO_HOME` lacked the rustup proxy. Direct binaries from that installed 1.98.1 toolchain compiled both RGB and electrs successfully.

The earlier evidence mislabeled electrs commit `d975dd03f2a410c4473116d5a2be950a205e0443` as `v0.12.0`. That commit is the current upstream `master` tip, while the dereferenced `v0.12.0` tag is `37501cc4…`. This run used the exact tag.

## Reproduction outline

All temporary paths were under one disposable workspace. `PATH` led with the installed Rust 1.98.1 toolchain `bin`, `CARGO_HOME` and `CARGO_TARGET_DIR` pointed inside that workspace, and both builds used `--locked`.

```text
git clone --depth 1 --branch v0.12.0-rc.3 https://github.com/RGB-WG/rgb.git <temporary_workspace>/rgb
git clone --depth 1 --branch v0.12.0 https://github.com/romanz/electrs.git <temporary_workspace>/electrs
cd <temporary_workspace>/rgb
git apply <evidence_staging>/rgb-rc3-cli.patch
cargo build --locked -p rgb-wallet
rgb sync --help
rgb --network regtest --data-dir <temporary_workspace>/rgb-data --no-network-prefix init
rgb --network regtest --data-dir <temporary_workspace>/rgb-data --no-network-prefix create --wpkh test2 '<disposable Core public tpub descriptor>'
rgb --network regtest --data-dir <temporary_workspace>/rgb-data --no-network-prefix sync --electrum=tcp://127.0.0.1:19546 test2
git apply -R <evidence_staging>/rgb-rc3-cli.patch
cargo build --locked -p rgb-wallet
rgb sync --help # exit 101
```

Bitcoin Core ran with `-regtest -server -rest=1 -txindex=1 -listen=0 -dnsseed=0 -maxconnections=0`, bound RPC to `127.0.0.1:19543`, and used cookie authentication. electrs ran with `--network regtest --daemon-rpc-addr 127.0.0.1:19543 --electrum-rpc-addr 127.0.0.1:19546` against the same Core data directory. The CLI supplied `--electrum` explicitly; RC3's `ELECRTUM_SERVER` environment-name typo remains unchanged.

The first electrs startup returned HTTP 404 for Core's REST endpoint because Core had been started without `-rest=1`. Restarting that same node with `-rest=1` allowed electrs to index it. This option is required for this electrs release's local Core integration.

The [feature tree](rgb-feature-tree.txt), [patched build log](rgb-build.sanitized.log), [unmodified build log](rgb-upstream-build.sanitized.log), [patched help output](rgb-patched-sync-help.sanitized.log), and [unmodified failure](rgb-upstream-sync-help.sanitized.log) are retained. Path strings in logs were replaced with `<temporary_workspace>`.

## Audit and upstream state

`cargo-audit 0.22.2` was run afresh against the retained RGB lock, using RustSec advisory database revision `1e640cd56d7604993e3a9ec392060666e3b95ccc` with `--no-fetch`. The [complete output](cargo-audit.txt) reports 15 vulnerabilities and five allowed warnings. The audit database was copied read-only from the earlier Phase 0 run after a fresh network fetch stalled; this records a scan against that precise revision, not a newer database snapshot. The lock is still unadopted.

Read-only inspection of the upstream RGB default branch on 2026-09-23 found `master` at `275382240ae1b8a56beb120e926e60d86f49785b`. It still has the `mempool` group entry, `ELECRTUM_SERVER`, and `create` writing `self.data_dir().join(name)` while `runtime` loads `wallet_dir(...).with_extension("wallet")`. Neither CLI defect has been fixed there as of this snapshot.
The exact source-line check is retained in [upstream-master-defects.txt](upstream-master-defects.txt).

This bounded check proves a working resolver path for the patched candidate. It does not test RGB contract genesis, identity authorization, signatures, transition validity, recovery, revocation, or a released upstream fix. The patch is not a dependency selection and is not an O2A production crate.

## Bounded lock remediation

The accompanying [lock review](lock-review/SUMMARY.md) tested conservative
dependency updates under the same Rust 1.98.1 toolchain. Compatible updates
reduced the full RC3 graph from 15 advisories to three. The remaining findings
all come through the Esplora HTTPS path:

```text
rgb-wallet -> rgb-runtime/resolvers-all -> resolver-esplora
  -> minreq -> rustls 0.21.12 -> rustls-webpki 0.101.7
```

A separate experiment removed Esplora from the runtime and CLI graph while
preserving Electrum plus filesystem support. That 213-package lock passed
locked workspace checks and five tests and reported zero vulnerability
advisories, but it still contains the unmaintained `paste 1.0.15` dependency
and requires an unreleased source patch. Its license inventory also remains to
be reviewed. Neither candidate lock is adopted.

The [registry check](rust-bitcoin-release-check.txt) found 0.32.102 still to be
the newest stable 0.32 release; 0.33.0 was available only as a beta. The
existing exclusion of 0.32.102 from the affected consensus-sensitive path
therefore remains in force.
