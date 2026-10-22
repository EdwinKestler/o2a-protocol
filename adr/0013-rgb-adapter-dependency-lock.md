# ADR-0013 — Dependency Lock for the rgb-protocol 0.11.1 Adapter

**Status:** Proposed, 2026-10-22. Not accepted. Closes Phase 0 open item 2
only after the acceptance checklist below is complete and the maintainer
accepts it.

## Context

Phase 0 item 2 requires adopting the exact dependency lock of the workspace
that performs O2A transitions ([phase0closure.md](../docs/phase0closure.md)).
The 0.12 RC3 locks were never adopted
([dependency gate](../docs/phase0-dependency-gate.md), now historical).
[ADR-0010](0010-rgb-carrier-line.md) selects rgb-protocol 0.11.1 with Opret and
requires that adapter to live in its own Cargo workspace, separate from every
0.12 experiment.

That workspace is `o2a-testnet-demo/spikes/rgb-0.11.1`. Its `Cargo.lock` has
been unchanged since demo commit `2ddfe8c`, the ADR-0010 compatibility
evidence.

## Decision

If accepted:

1. The adopted lock for the O2A RGB adapter is the 139-package
   `spikes/rgb-0.11.1/Cargo.lock` with SHA-256
   `f110a9292dd5fd57e71951133b5781869bc0778cdba7330412e6d93e1d1c515e`, built
   with Rust 1.98.1. All `rgb-*` crates are pinned at exactly `=0.11.1`, and
   `rgb-strict-encoding`/`rgb-strict-types` at `=1.0.4`, as in the workspace
   manifest.
2. Builds of the adapter MUST use `--locked`. Any lock change is a new
   decision: rerun the review below and record the new hash in a successor
   ADR or an acceptance addendum to this one.
3. The O2A program built against this lock is ADR-0012's; this ADR does not
   adopt the archived 0.12 RC3 locks or the demo schema.
4. **rust-bitcoin 0.32.102 is admitted only in the scoped use recorded here.**
   It arrives through `rgb-consensus 0.11.1`. O2A seal signing on this lock
   MUST use only BIP341 `SIGHASH_DEFAULT` (script-path for seals, key-path for
   fee inputs). It MUST NOT be used for SegWit-v0 signing or as a consensus
   validator; depth, inclusion, and script validity remain checked against a
   Bitcoin Core node. The standing exclusion in
   [doc 23](../docs/23-stack-compatibility-and-security-readiness.md) is
   otherwise unchanged.
5. The two `secp256k1` versions (0.29.1 and 0.33.1) are crossed only by
   validated byte encodings (ADR-0010 item 7).
6. License results follow the 2026-09-28 policy: report-only, with the
   `hex_lit 0.1.1` MITNFA entry already accepted in the
   [license register](../docs/22-license-and-adoption-assessment.md).

## Evidence

`o2a-testnet-demo` commit `5ffc48a` (branch `feat/o2a-program-v0.1`), bundle
`evidence/lock-review-rgb011-2026-10-22/` (manifest SHA-256
`1b465771fea0b1c8239a28e0755e590b2d93ab3ada5f77c55157a5a3b875ef28`):

| Check | Result |
| --- | --- |
| `cargo audit` (0.22.2, 1348 advisories) | exit 0, no vulnerabilities or warnings across 139 crates |
| `cargo deny check advisories bans sources` (0.20.2) | all three ok |
| `cargo deny check licenses` (report-only) | only `hex_lit 0.1.1` MITNFA |
| `paste` / `RUSTSEC-2024-0436` | absent from this graph |
| Adapter test suite on this lock | 22 unit + 5 integration tests pass |

## Required evidence before acceptance

1. The ADR-0012 acceptance lineage and signet rehearsal are built from this
   exact lock hash with `--locked`.
2. The review is rerun within 14 days of acceptance against the then-current
   RustSec database, with the same results or a recorded disposition.
3. ~~The maintainer reviews decision item 4 (scoped rust-bitcoin admission).~~
   Done 2026-10-22.

## Consequences

- Phase 0 item 2 closes on acceptance for the transition adapter. A production
  wallet, UI, or service built later declares its own lock and inherits this
  one for the adapter crate only.
- The adapter remains in the demo repository until a maintained module is
  created; moving it changes no pin.
- `docs/phase0-dependency-gate.md` and `docs/upstream-needs.md` remain
  historical 0.12 records.

## Maintainer decisions — 2026-10-22

- Decision item 4 is approved as written: rust-bitcoin 0.32.102 is admitted
  only for BIP341 `SIGHASH_DEFAULT` Taproot signing in the adapter, and
  Bitcoin Core remains the consensus validator for depth, inclusion, and
  script validity. Any other use needs a new decision. The ADR stays Proposed
  until checklist items 1 and 2 are met.
