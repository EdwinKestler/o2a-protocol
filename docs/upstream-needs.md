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
