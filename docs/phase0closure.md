# Phase 0 status report

**Status:** open. This is not a closure declaration. A coordinator review
reopened the encoding, RGB-contract, evidence-serialization, proof-package,
and vector tracks. The dependency gate also remains open, so Phase 0 is not
finished.

The initial report was recorded 2026-09-23 by coordinator session
`c90dc0f10822efb30fe0b17394dfa707`. The remediation is recorded by session
`e4bf06a0addf7a2abaae8d1f4521b829`. Nothing in either pass was committed,
pushed, or deployed. No wallet crate was created and no RGB lock was adopted.

## What the six agents did

The runtime allowed three workers at a time. Batch one was encoding, the
RGB contract, and evidence. Batch two was the proof package, the dependency
gate, and the vectors. `phase0.encoding` was `ready` before the vector agent
wrote fixture bytes.

| Track | Ledger subject | Result |
| --- | --- | --- |
| Encoding | `phase0.encoding` | Candidate grammar and all twelve signed-object layouts remediated. Open on the identity derivation allocation and complete independent vectors. |
| RGB contract | `phase0.rgb-contract` | State, seals, threshold recovery, delay, cancellation, confirmation, and reorg rules remediated. Open on concrete RGB program/schema bytes, commitment carrier, and executable lifecycle evidence. |
| Evidence | `phase0.evidence` | Canonical layouts and role/capability separation remediated. Open on executable fixtures for all evidence families. |
| Proof package | `phase0.package` | Non-circular manifest and complete signed-envelope package identity remediated and exercised by one fixture. Open with the incomplete conformance suite. |
| Vectors | `phase0.vectors` | Claim and proof-package fixtures pass a locked rust-secp256k1 verifier. Open because most roadmap cases remain prose. |
| Dependency | `phase0.dependency` | Resolved open. No lock is adopted. |

Palimnex session ids are 32 hex characters. The logical names
`phase0-encoding`, `phase0-rgb`, `phase0-evidence`, `phase0-package`,
`phase0-dependency`, and `phase0-vectors` were hashed to those ids. Recall
`phase0` to read the decisions.

## Accepted foundations retained during remediation

- EntityID is the tagged hash of version, network, and the BIP340 root.
  Recovery does not change it.
- Identity, controller, recovery, discovery, and payment keys remain separate.
  Proposed Route B derives an independent `xprv_o2a` with BIP85 and keeps its
  identity subtree outside the BIP43 purpose slot. Payment keys do not sign O2A
  objects. Pubky keys stay independent Ed25519 keys.
- Every signed object requires canonical bytes. Key role and authorization
  capability are separate signed fields. The same payload under two tags is
  two messages.
- Confirmation depth is 1 off mainnet and 6 on mainnet. A missing anchor or
  a missing consignment is not a current identity state.
- Human names remain competing claims. Challenges and evidence revocations
  stay optional. Rebinding leaves the previous binding visible.
- `tests/vectors/` is CC0-1.0. The rest of the repository stays
  `MIT OR Apache-2.0`. Existing fixture results are retained as partial
  evidence and do not close the vector gate.

## Remediation completed in this pass

- O2A-CANON-1 now bounds primitives, separates key role from authorization
  capability, and defines payload bytes for genesis, transitions, recovery,
  claims, attestations, challenges, evidence revocations, control challenges,
  observations, discovery bindings, music manifests, and proof packages.
- The RGB identity contract now fixes state sequence and seal linkage,
  threshold recovery, block delay, cancellation by a competing current-state
  spend, custody acceptance, confirmation depth, and best-chain reorg rules.
- The proof-package signature commits to `manifest_payload || manifest_id`.
  `package_id` hashes the complete transmitted signed envelope, so the package
  identifier includes the signature without creating a cycle.
- The vector checker performs no local curve arithmetic. A locked
  rust-secp256k1 helper verifies valid, mutated, and cross-domain signatures.
  The fixture also exercises manifest ID, complete-envelope package ID,
  truncation, and mutation.
- The [identity path note](phase0-derivation-allocation.md) records Route B,
  the completed conformance gates, and the separate maintainer decision still
  required before the profile is frozen.

These corrections replace the earlier ready results. They do not convert an
open conformance track into a closed one.

## Why Phase 0 stays open

`docs/phase0-dependency-gate.md` records three decisions:

- The three-line RGB CLI patch is a disposable dev overlay, not an upstream
  fix and not a production pin.
- The full RC3 lock still has 15 vulnerability advisories. Compatible
  updates leave three `rustls-webpki` 0.101.7 advisories. The Electrum-only
  graph has no vulnerability advisories, and it still depends on
  unmaintained `paste` 1.0.15, an unreleased source patch, and unreviewed
  extra licenses. No lock is adopted.
- `rust-bitcoin` 0.32.102 stays off consensus-sensitive signing. No later
  stable 0.32 release is recorded.

Until a lock is adopted, the RGB 0.12 program bytes stay unbound and
implementation code stays unauthorized.

A follow-up pass rejected an unassigned BIP43 purpose and selected Route B's
BIP85-derived independent root. The derivation evidence gates now pass, but
the profile is not frozen. The commitment carrier is the 32-byte tagged hash
inside the consignment that closes the seal. No script template is frozen. A same-day
upstream recheck found no adoptable RGB release. Protocol-only fixtures now
also cover a wrong capability, a wrong network, duplicate name bytes, and a
recovery-policy hash. RGB execution fixtures remain open.

## Checks

- `python3 tests/vectors/check_vectors.py` exited 0.
- `cargo test --locked` passed for the scoped vector helper.
- In the pinned Rust 1.98.1 toolchain container, cargo-audit 0.22.2 found no
  advisories in the 21-package vector-helper lock. With development
  dependencies excluded, its executable plus build graph has ten packages.
  Cargo-deny 0.20.2 passed advisories, bans, licenses, and sources. This result
  applies only to the vector helper, not the rejected RGB RC3 graph.
- The vector-helper lock SHA-256 is
  `ca8019a81488103cd345edccb4865a487c5e97ee393bff045005d36214eb6a8f`.
- Palimnex deep validation passed.
- All 21 evaluation cases passed.
- Palimnex ledger integrity is `ok`, and the latest remediation outcomes are
  verified. Superseded or earlier events may remain stale when their cited
  files changed or disappeared during remediation; the ledger retains that
  history instead of rewriting it.
- No site deployment was performed.
