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
