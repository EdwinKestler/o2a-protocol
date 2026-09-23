# 22 — License and Adoption Assessment

**Status:** supporting policy assessment, 2026-09-23. This is a practical
open-source licensing review, not legal advice and not a license grant. The
root [LICENSE](../LICENSE) file remains authoritative.

## Outcome

Apache-2.0 is a sound permissive license for O2A. It allows commercial and
closed-source use, modification, and redistribution, and it includes an
explicit contributor patent grant. It is compatible with using MIT-licensed
Bitcoin Core and Pubky components and CC0-1.0 rust-bitcoin components as
separate dependencies, subject to every upstream license's own conditions.

If the overriding goal is the least possible downstream friction, the
recommended future policy is:

- license O2A-authored specifications, documentation, reference software, and
  crates under `MIT OR Apache-2.0`;
- offer public conformance vectors additionally under `CC0-1.0`, so wallet and
  node implementers can copy fixtures without license ambiguity; and
- keep every upstream dependency and bundled executable under its own license,
  with the required notices shipped alongside distributions.

This recommendation does not relicense the repository. The current grant is
Apache-2.0 only until the copyright holder explicitly approves the change and
adds both canonical license texts. A recipient choosing the MIT alternative
would not receive Apache-2.0's express patent grant through that choice. Teams
that value the patent terms can choose Apache-2.0.

## Why this minimizes friction

| Policy | Adoption effect | Cost or limitation |
| --- | --- | --- |
| Apache-2.0 only — current | Permissive, commercial-friendly, explicit patent grant. | Some Rust projects and corporate intake systems prefer an MIT alternative. |
| `MIT OR Apache-2.0` — recommended | Familiar Rust ecosystem convention; downstream chooses the accepted path while Apache remains available. | Two license texts and precise contribution language are required; an MIT-only recipient does not obtain Apache's patent grant. |
| CC0-1.0 for vectors only | Makes test vectors easy to embed in independent implementations and follows Bitcoin BIP guidance. | No express patent grant; it should be scoped to fixtures, not silently applied to the wallet or protocol code. |
| GPL or AGPL | Stronger reciprocal terms for copies of this implementation. | Does not stop a separate closed implementation of a public protocol and adds integration friction, contrary to the adoption goal. |

## Adoption-safe implementation checklist

If dual licensing is approved:

1. inventory existing contributions and confirm that every relevant
   rightsholder consents to relicensing; Git authorship alone is not proof of
   copyright ownership or authority to relicense;
2. preserve the canonical Apache text as `LICENSE-APACHE` and add the canonical
   MIT text as `LICENSE-MIT`;
3. state the exact SPDX expression `MIT OR Apache-2.0` in the README, package
   metadata, source headers or a documented directory-level mapping;
4. add a `CONTRIBUTING.md` saying contributions are submitted under both
   alternatives and require [Developer Certificate of Origin 1.1](https://developercertificate.org/)
   sign-off; do not require copyright assignment merely for convenience;
5. add an explicit CC0-1.0 scope marker and license text under
   `tests/vectors/` when those fixtures exist;
6. generate third-party notices and a dependency license bundle for release
   artifacts, especially when Bitcoin Core or another executable is bundled;
   and
7. update every current Apache-only statement, the pipeline source and SVG,
   and the public site in the same reviewed change.

Do not change only the Cargo manifest or only the README. A partial dual-license
conversion creates the ambiguity this policy is meant to remove.

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
