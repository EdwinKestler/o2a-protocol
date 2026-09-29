# 22 — License and Adoption Assessment

**Status:** accepted licensing policy, updated 2026-09-28. This is a practical
open-source licensing record and assessment, not legal advice. The root
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

## Dependency license assessment policy — 2026-09-28

The maintainer decided that dependency-license compliance is an evaluated
assessment, not a rigid development gate. Security and provenance checks stay
separate from the license assessment:

- `cargo deny check advisories bans sources` is **BLOCKING**. A failing
  advisory, ban, or source check stops the validation run.
- `cargo deny check licenses` is **REPORT-ONLY**. Its complete output and exit
  code are recorded, but its exit code does not block development.
- Every dependency whose license expression is not on the routine allowlist
  MUST be entered in the license register below with an assessment and either
  `accepted` or `review-before-distribution` status.

The routine allowlist remains `CC0-1.0`, `MIT`, `MIT-0`, `Apache-2.0`,
`BSD-2-Clause`, `BSD-3-Clause`, `ISC`, `Zlib`, `Unicode-3.0`, and
`CDLA-Permissive-2.0`, including SPDX `OR` expressions composed only of those
licenses. It is a reporting baseline, not a claim that every other license is
prohibited. Review runtime, build, and development dependencies, Git
dependencies, bundled native libraries, fonts, icons, and installers.

Strong-copyleft dependencies under GPL, AGPL, or SSPL are
`review-before-distribution`. The maintainer MUST review their obligations
before any public distribution or mainnet release, but their presence does not
block development. Other non-allowlisted, unknown, or missing license metadata
is assessed and registered the same way; the register may conclude that a
dependency must be replaced before distribution.

### License register

| Package | License and path | Assessment | Status |
| --- | --- | --- | --- |
| `hex_lit 0.1.1` | MITNFA; pulled in through `bitcoin 0.32.102` by `rgb-consensus 0.11.1` | MIT plus a no-false-attribution clause on modified distributions. Negligible risk for the recorded compatibility use: O2A does not modify or redistribute `hex_lit`. | accepted |

An `accepted` entry records the assessed use and facts above; it is not a
global allowlist addition for unrelated packages or changed distribution
behavior. `review-before-distribution` means the dependency can be used for
development, but public artifacts and mainnet release remain held until the
maintainer records the review.

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

## Superseded 2026-09-24 rule

The 2026-09-24 rule treated non-allowlisted licenses as rigid blockers:
`MITNFA` was disallowed, MPL required a narrow exception, and GPL/LGPL/AGPL
expressions stopped work. The maintainer's 2026-09-28 decision supersedes that
rule. The earlier measurements and deny outputs remain historical evidence,
but current decisions use the report-only check and license register above.

`RUSTSEC-2024-0436` for `paste 1.0.15` is ignored as a maintenance advisory
for the measured graph because `paste` is a proc macro used at compile time and
has no runtime code path. This is not a claim that unmaintained dependencies
are generally acceptable. The replacement request—migrate from `paste` to the
drop-in maintained fork `pastey`—is tracked in
[upstream needs](upstream-needs.md). Every ignore entry must cite this dated
decision.

Repository `deny.toml` files retain the routine allowlist so the license check
can identify register candidates. The scoped checker policy under
`tests/vectors/crypto-checker/` carries that allowlist and the dated advisory
ignore; its advisory, ban, and source checks are blocking, while its license
check is report-only.

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
