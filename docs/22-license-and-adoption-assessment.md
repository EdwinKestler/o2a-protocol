# 22 — License and Adoption Assessment

**Status:** accepted licensing policy, 2026-09-23. This is a practical
open-source licensing record, not legal advice. The root
[LICENSE](../LICENSE) notice and its canonical license files are authoritative.

## Outcome

The copyright holder approved this policy to minimize downstream friction:

- license O2A-authored specifications, documentation, reference software, and
  crates under `MIT OR Apache-2.0`;
- license public conformance vectors separately under `CC0-1.0`, so wallet and
  node implementers can copy fixtures without license ambiguity; and
- keep every upstream dependency and bundled executable under its own license,
  with the required notices shipped alongside distributions.

The repository now carries both canonical license texts. A recipient choosing
the MIT alternative does not receive Apache-2.0's express patent grant through
that choice. Teams that value the patent terms can choose Apache-2.0.

## Why this minimizes friction

| Policy | Adoption effect | Cost or limitation |
| --- | --- | --- |
| Apache-2.0 only — superseded | Permissive, commercial-friendly, explicit patent grant. | Some Rust projects and corporate intake systems prefer an MIT alternative. |
| `MIT OR Apache-2.0` — accepted | Familiar Rust ecosystem convention; downstream chooses the accepted path while Apache remains available. | Two license texts and precise contribution language are required; an MIT-only recipient does not obtain Apache's patent grant. |
| CC0-1.0 for vectors only | Makes test vectors easy to embed in independent implementations and follows Bitcoin BIP guidance. | No express patent grant; it should be scoped to fixtures, not silently applied to the wallet or protocol code. |
| GPL or AGPL | Stronger reciprocal terms for copies of this implementation. | Does not stop a separate closed implementation of a public protocol and adds integration friction, contrary to the adoption goal. |

## Adoption-safe implementation record

- The copyright holder approved the migration for existing O2A-authored work.
- `LICENSE-APACHE` preserves the canonical Apache text; `LICENSE-MIT` contains
  the canonical MIT text; the root `LICENSE` states the scope and SPDX choice.
- `CONTRIBUTING.md` applies the same dual-license inbound policy and requires
  [Developer Certificate of Origin 1.1](https://developercertificate.org/)
  sign-off without copyright assignment.
- When `tests/vectors/` is created, it must contain an explicit CC0-1.0 scope
  marker and license text. Until then, no repository content is implicitly
  CC0-1.0.
- Release artifacts must include third-party notices and a dependency license
  bundle, especially when Bitcoin Core or another executable is bundled.
- Future Rust package metadata must use the exact SPDX expression
  `MIT OR Apache-2.0`.

## Dependency license policy

The first `deny.toml` must allow at least:

```toml
allow = ["Apache-2.0", "MIT", "CC0-1.0"]
```

That is a minimum, not a blind universal allowlist. Add another license only
after it appears in the selected, locked graph and its obligations are
reviewed. Fail unknown and unlicensed packages. Review runtime, build, and dev
dependencies, Git dependencies, bundled native libraries, fonts, icons, and
installers. Use narrow package exceptions with an owner, reason, and expiry.

The relevant upstream snapshot checked on 2026-09-23 is:

| Component | Current license evidence |
| --- | --- |
| RGB Core, RGB standard library, RGB runtime | Apache-2.0 in their Cargo manifests. |
| Bitcoin Core | MIT in `COPYING`. |
| rust-bitcoin | CC0-1.0 in the current crate manifest. A proposal about future contributions is not a current relicense. |
| Pubky Core and PKARR | MIT in their Cargo manifests. |
| rust-nostr | MIT in its workspace manifest; NIPs describe themselves as public domain. |

Recheck exact packages, features, license files, and revisions when the
dependency lockfile is selected. `cargo-deny` assists that review; it does not
replace the notices or a manual distribution audit.

## Maintainer dependency-license decision — 2026-09-24

The feature-aware RGB measurement at commit `3b9c397` separated the compiled
library graph from packages present only in the upstream lock or CLI. The
maintainer approved the following repository-wide dependency policy. This
policy does not adopt the measured RGB graph or close its Phase 0 gate.

Permissive dependencies may use `CC0-1.0`, `MIT`, `MIT-0`, `Apache-2.0`,
`BSD-2-Clause`, `BSD-3-Clause`, `ISC`, `Zlib`, `Unicode-3.0`, or
`CDLA-Permissive-2.0`. SPDX `OR` expressions composed only of those approved
licenses are also allowed. A `deny.toml` expresses this by allowing the
individual identifiers; it must continue to fail unknown or unlicensed
packages.

`MPL-2.0` and `MPL-2.0-no-copyleft-exception` are allowed only through a
package-scoped exception for an unmodified third-party dependency. O2A does
not fork or patch an MPL-licensed crate. A required modification is a stop and
requires a new maintainer and license review before work continues. The current
measured instance is unmodified `base85 2.0.0` under
`MPL-2.0-no-copyleft-exception`. MPL is intentionally absent from the global
allowlist so a newly introduced MPL package cannot pass without that review.

`MITNFA` remains disallowed. Any dependency expression containing `GPL`,
`LGPL`, or `AGPL` is a stop. An alternative disjunct does not silently waive
the review: the selected and distributed licensing path must be recorded.

`RUSTSEC-2024-0436` for `paste 1.0.15` is ignored as a maintenance advisory
for the measured graph because `paste` is a proc macro used at compile time and
has no runtime code path. This is not a claim that unmaintained dependencies
are generally acceptable. The replacement request—migrate from `paste` to the
drop-in maintained fork `pastey`—is tracked in
[upstream needs](upstream-needs.md). Every ignore entry must cite this dated
decision.

Future repository `deny.toml` files must implement this policy. The scoped
checker policy under `tests/vectors/crypto-checker/` carries the permissive
allowlist and the dated advisory ignore. A future RGB consumer must additionally
use a package-and-version-scoped MPL exception for `base85 2.0.0` after
confirming that its source is unmodified.

## Primary references

- [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0.html),
  including its patent and redistribution terms.
- [BIP-3 licensing guidance](https://github.com/bitcoin/bips/blob/master/bip-0003.md#bip-licensing),
  including its recommendation for reusable test vectors.
- [cargo-deny license configuration](https://embarkstudios.github.io/cargo-deny/checks/licenses/cfg.html).
- [Bitcoin Core licensing](https://github.com/bitcoin/bitcoin/blob/master/COPYING)
  and the current [rust-bitcoin manifest](https://github.com/rust-bitcoin/rust-bitcoin/blob/master/bitcoin/Cargo.toml).
- RGB-WG manifests for [Core](https://github.com/RGB-WG/rgb-core/blob/master/Cargo.toml),
  [standard library](https://github.com/RGB-WG/rgb-std/blob/master/Cargo.toml),
  and [runtime](https://github.com/RGB-WG/rgb/blob/master/Cargo.toml).
