# Upstream needs

**Status:** tracked interoperability requests, 2026-09-24. This list records
changes O2A would like upstream projects to make. It does not authorize an O2A
fork, patch, dependency adoption, or production implementation.

## RGB-WG

1. **Migrate `paste` to `pastey`.** The feature-aware `rgb-runtime` graph still
   contains `paste 1.0.15`, a compile-time proc macro covered by
   `RUSTSEC-2024-0436`. O2A accepts the advisory temporarily under the dated
   maintainer decision, but requests the maintained drop-in replacement.
   Evidence: [compiled-graph audit](../evidence/phase0/rgb-rc3-compiled-graph-2026-09-24/cargo-audit-lock.txt)
   and [runtime dependency tree](../evidence/phase0/rgb-rc3-compiled-graph-2026-09-24/cargo-tree-runtime.txt).
2. **Remove nonexistent `mempool` from the Clap `ResolverOpt` group.** The
   unmodified RC3 CLI fails `rgb sync --help`; the retained compatibility patch
   demonstrates the minimal correction. Evidence:
   [RC3 remediation run](../evidence/phase0/rgb-rc3-remediation-2026-09-23/RUN.md)
   and [CLI patch](../evidence/phase0/rgb-rc3-remediation-2026-09-23/rgb-rc3-cli.patch).
3. **Make `create` and `sync` use the same wallet path.** RC3 `create` writes a
   path without the `.wallet` suffix that the runtime later loads. The retained
   patch aligns the two paths. Evidence:
   [RC3 remediation run](../evidence/phase0/rgb-rc3-remediation-2026-09-23/RUN.md)
   and [CLI patch](../evidence/phase0/rgb-rc3-remediation-2026-09-23/rgb-rc3-cli.patch).
4. **Correct the `ELECRTUM_SERVER` environment-variable typo.** O2A supplied
   `--electrum` explicitly and did not turn this upstream spelling into an O2A
   configuration contract. Evidence:
   [RC3 remediation run](../evidence/phase0/rgb-rc3-remediation-2026-09-23/RUN.md).
5. **Correct the Electrum witness-height off-by-one calculation.** At commit
   `a1e6b415`, `rgb-runtime` computes the mined height as
   `last_height - confirmations`; Bitcoin confirmations include the containing
   block, so the conversion requires `+ 1`. With the anchor at Bitcoin height
   103, RGB reported `Mined(102)` both before and after the tip advanced from
   103 to 104. Evidence:
   `../o2a-testnet-demo/evidence/regtest-genesis-rotation-2026-09-24/WITNESS-HEIGHT.md`.

## BP-WG `bp-std`

1. **Candidate: select the actual tap leaf hash during PSBT finalization.**
   Disposable demo-lineage smoke evidence against `bp-std v0.12.0-rc.3`
   observed the finalizer using the first Merkle sibling as the tap leaf hash
   at `psbt/src/data.rs:890-891`. This is a non-blocking upstream candidate:
   O2A owns seal tracking and script-path finalization by design. Evidence:
   `../o2a-testnet-demo/evidence/regtest-seal-tapscript-smoke-2026-09-25/`,
   manifest `59f80970be1de88a642cd2345386ba7e12b903caf9b48f9ced5c39288c7e4b01`.
2. **Candidate: avoid `extract()` panic for an absent witness-input
   `final_script_sig`.** Disposable demo-lineage smoke evidence against
   `bp-std v0.12.0-rc.3` observed the panic at `psbt/src/data.rs:793`; an empty
   scriptSig allowed extraction of the finalized taproot witness. This is
   likewise non-blocking because O2A owns seal tracking and script-path
   finalization by design. Evidence is the same verified smoke manifest above.
