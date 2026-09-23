# 21 — Proposed Technology Stack and Initial Development Environment

**Status:** supporting implementation brief, reviewed 2026-09-23. This page
does not freeze the wire format, RGB lineage, dependency set, or wallet
security design. Accepted ADRs and the normative specs remain authoritative.

## Recommendation

Build the reference implementation as a CLI-first Rust workspace with a
deterministic, network-free verification core. Put Bitcoin access, RGB
validation, storage, discovery, and user interfaces behind explicit adapters.
Use a pinned Bitcoin Core regtest node for the first integration environment,
SQLite plus content-addressed files for local wallet data, and no public
network or real-value keys.

The RGB ecosystem requires more than a version pin. Two active, incompatible
lineages currently exist. The first engineering deliverable is therefore a
time-boxed compatibility and lineage decision that compiles and tests one
complete dependency family end to end. Production implementation remains
behind the Phase 0 gates in the [roadmap](13-roadmap.md).

## Proposed stack

| Layer | Proposed choice | Decision state |
| --- | --- | --- |
| Reference language | Rust 2024 edition, exact toolchain pin, committed `Cargo.lock` | Adopt for the reference implementation after Phase 0 authorizes code. |
| Deterministic core | Pure Rust library: typed O2A objects, canonical codec boundary, BIP340 domains, controller authorization, policy evaluation, and proof-package verification | Required shape. No DNS, HTTP, clock, database, or hidden chain reads during evaluation. |
| Bitcoin | Bitcoin Core 31.1 regtest as the chain source, reached through a narrow O2A RPC adapter and, if the selected RGB runtime requires it, a local Electrum/Esplora resolver backed by that same node | Initial reference backend. Full-node mode comes first; light mode is a later, separately labeled adapter. |
| Bitcoin types and signatures | Maintained libsecp256k1-backed BIP340 bindings, with one secp256k1 type family inside each crate and explicit byte-level validation at version boundaries | Strong recommendation. Current stable `rust-bitcoin` and RGB RC3 resolve different secp256k1 crate versions; do not assume their Rust key types interoperate. Never implement curve arithmetic or Schnorr signing locally. |
| RGB | Dedicated adapter over one tested RGB Core, standard-library/runtime, BP, and Strict Types dependency family | Phase 0 blocker. Select the lineage and exact revisions only after the compatibility spike passes. |
| Local wallet storage | SQLite for metadata and rebuildable indexes; content-addressed files for consignments, Bitcoin proofs, evidence, and packages | Strong recommendation. The encrypted secret-store format and backup design remain security decisions. |
| First interface | CLI for create, transition, sign, package, import, verify, and explain operations | Initial interface. It exposes deterministic behavior before GUI concerns. |
| Discovery | Pubky/PKARR Rust adapter in Phase 3; optional Nostr adapter in a separate crate | Planned. Adapter keys and records never replace the O2A root or validated RGB history. |
| Registry service | Rust service, PostgreSQL projection, replicated object storage; Redis only as a disposable measured cache | Deferred until a registry/API is required. Axum is a reasonable candidate, not a protocol dependency. |
| Desktop wallet | Tauri 2 shell over the Rust client core | Optional Phase 2 candidate. Keep its platform and web dependencies out of the base environment until selected. |
| Browser/SDK | TypeScript or WASM facade over stable protocol interfaces | Deferred. It must not create a second signing or serialization rule. |
| License | `MIT OR Apache-2.0` for O2A-authored specifications, documentation, and reference software; CC0-1.0 for explicitly marked conformance vectors | Accepted. Apache-2.0 and its patent grant remain available as an option. Dependency licenses remain separate. |

JSON, YAML, SQL rows, and UI models may be used as human-readable views. They
must not become signing bytes by accident. Signed and hashed O2A objects use
only the canonical encoding and tagged domains frozen by the normative specs
and conformance vectors.

## Proposed Rust workspace boundaries

```text
crates/o2a-core       typed objects, authorization rules, policy, explanations
crates/o2a-codec      canonical encoding and golden vectors
crates/o2a-crypto     BIP340 tagged hashes, signing and verification interfaces
crates/o2a-rgb        RGB identity lifecycle and consignment validation adapter
crates/o2a-bitcoin    network, headers, anchors, seals, confirmations and RPC
crates/o2a-store      SQLite indexes and content-addressed local object store
crates/o2a-cli        orchestration only; no duplicate protocol rules
crates/o2a-testkit    fixtures, adversarial vectors and regtest harness
```

This is a target layout, not permission to create the production crates. The
first RGB experiment is disposable and must live outside `crates/o2a-rgb`. It
may prove genesis, rotation, recovery-policy changes, authorized recovery, and
revocation on regtest, but it does not freeze an O2A RGB contract. Create the
production adapter only after Phase 0 accepts the exact RGB lineage and test
evidence.

Discovery collectors and registry services should be separate workspace
members added in their roadmap phases. The core accepts explicit observations,
validated RGB histories, policies, protocol versions, and evaluation contexts;
it never fetches the live Internet while evaluating a package.

The boundaries preserve three checks that must not be collapsed:

1. Bitcoin establishes transaction order and whether the referenced seal was
   spent.
2. RGB validates the supplied client-side transition history against its
   contract and Bitcoin anchors.
3. O2A validates controller authorization, typed signatures, evidence, and the
   named policy.

A Bitcoin outpoint, spend, or public key alone is not a verified O2A identity
or attestation.

## RGB lineage decision

The research snapshot found these two candidate families:

| Candidate | Current evidence | O2A consequence |
| --- | --- | --- |
| RGB-WG 0.12 | RGB Core `v0.12.0` is final. The latest tagged standard-library and runtime releases checked on 2026-09-23 are both `v0.12.0-rc.3`. The 0.12 model is not wire-compatible with earlier RGB contracts. | Preferred direction for a new protocol because the consensus layer is final, but not selectable until the matching high-level stack passes O2A's regtest flow. The RC3 libraries compiled in the first disposable smoke, but the debug-built CLI and resolver path did not pass; release CLI behavior was not tested. See the compatibility record. O2A language such as “schema” must also be checked against the 0.12 issuer/program model. |
| `rgb-protocol` 0.11.1 | The maintained API uses the 0.11.1 family and the sandbox demonstrates 0.11.1 RC6. Its dependency graph still includes pre-release BP components. | Useful as a reproducible integration comparison, not something to mix with RGB-WG Core 0.12 or silently make the O2A profile. |

The proposal is to test RGB-WG 0.12 first and keep 0.11.1 as the comparison
spike. The final choice is a protocol-project decision, not a conclusion that
can be inferred from repository names. Record the chosen upstream organization,
repositories, revisions, dependency lockfile, minimum Rust version, fixture
provenance, and known incompatibilities in the Phase 0 profile.

## Initial development environment

### Base prerequisites

- Linux is the first supported development host; CI should also exercise
  macOS and Windows before wallet release.
- Install Rust through `rustup`. When the workspace is created, check in a
  `rust-toolchain.toml` with an exact stable version plus `rustfmt` and
  `clippy`. Rust 1.98.1 is the current stable candidate at this review date,
  subject to the RGB compatibility run.
- Track `Cargo.lock` for the workspace and use locked builds in CI.
- Install Git, a C/C++ build toolchain, `clang`, `cmake`, `pkg-config`, SQLite
  development headers, `jq`, and Docker Compose or an equivalent rootless
  container runtime. Require SQLite 3.53.4 or a newer patched release for a
  bundled client; do not accept the current workstation's older system SQLite
  as a production dependency.
- Install a verified Bitcoin Core 31.1 build, or build the pinned tag from
  source. Run it only in an isolated regtest data directory with local RPC.
- Use a repository task runner such as `just` only as a convenience layer;
  every task must remain reproducible as documented commands.

### Repository artifacts to add when implementation begins

```text
rust-toolchain.toml        exact compiler plus rustfmt/clippy
Cargo.toml / Cargo.lock    workspace and locked dependency graph
deny.toml                  advisories, sources and license policy
justfile                   bootstrap, lint, unit, vectors and regtest tasks
dev/compose.yaml           isolated regtest and optional adapter profiles
dev/bitcoin.conf           regtest-only defaults; no reusable credentials
.env.example               names and safe placeholders only
tests/vectors/             public positive and adversarial fixtures
```

The initial `deny.toml` license allowlist must include `Apache-2.0`, `MIT`, and
`CC0-1.0`; rust-bitcoin is currently CC0-1.0. Add other licenses only after
they appear in the reviewed lockfile, and use narrow, explained exceptions
instead of a permissive catch-all. License scanning must include build and
development dependencies as well as runtime dependencies.

Generated data directories, wallet files, seeds, RPC cookies, private keys,
private RGB consignments, databases, and `.env` files stay ignored. Test
fixtures use deterministic, publicly documented test keys that are visibly
unsafe for real funds.

The pre-RGB default service profile should start only Bitcoin Core regtest and
the test harness. The compatibility spike must determine whether the selected
RGB runtime can use the O2A Core RPC adapter or needs a local Electrum/Esplora
resolver backed by that same Core node; the resulting resolver becomes part of
the RGB test profile. Optional profiles may add a Pubky local testnet or a
later PostgreSQL registry. Redis, Nostr relays, object storage, GUI tooling,
and public endpoints are not base requirements.

Containers are process-isolation and reproducibility tools, not protocol trust
boundaries. Pin image digests or build from reviewed source. Bind RPC to
localhost, use repository-specific data directories and credentials, and make
cleanup target only those explicit paths.

### Current workstation readiness snapshot

The development host checked on 2026-09-23 has Rust/Cargo 1.96.1, Docker, and
SQLite available. `bitcoind`, `bitcoin-cli`, and `just` were not found on
`PATH`. This is a host observation, not a repository guarantee; checked-in
environment files must become the reproducible setup source.

## First engineering gate: compatibility spike

Produce a short compatibility record before creating production crates:

1. list exact repositories, tags, or commit hashes for the selected RGB Core,
   standard library/API, runtime/CLI, BP libraries, Strict Types,
   `rust-bitcoin`, and `secp256k1`;
2. record the Rust toolchain, features, license, and source for every item;
3. compile the full graph from a clean checkout using a committed lockfile and
   prove its chain-resolver path against the pinned Bitcoin Core node;
4. on Bitcoin Core regtest, create an identity genesis and exercise controller
   rotation, recovery-policy change, authorized recovery, and revocation;
5. export/import the required consignment and public proof-package material,
   then validate it in a second clean client state;
6. test missing history, wrong network, wrong contract/profile, stale state,
   forked history, mismatched seal/anchor, and a simulated reorg; and
7. publish the passing matrix and fixtures before selecting the dependency set
   in the Phase 0 specification.

The first disposable run is recorded in
[the stack compatibility and security assessment](23-stack-compatibility-and-security-readiness.md).
It is a partial pass: Rust 1.98.1, the RGB RC3 libraries, and Bitcoin Core 31.1
regtest worked, but the debug-built RGB CLI, resolver integration, Bitcoin type
conversion boundary, full O2A lifecycle, dependency advisory scan, and
independent import remain open. Release CLI behavior was not tested. The run
therefore does not select the stack.

A [second disposable run](../evidence/phase0/rgb-rc3-regtest-2026-09-23/README.md)
retained the exact lock and proved a local electrs-backed sync plus a bounded
public-key conversion after temporary RC3 workarounds. It also found 15
vulnerabilities and five warnings in the locked 342-package graph. That result
closes the earlier evidence gaps but fails the dependency-adoption gate; it
still does not select the stack or authorize `crates/o2a-rgb`.

A [third disposable run](../evidence/phase0/rgb-rc3-remediation-2026-09-23/RUN.md)
converted the parser and wallet-path workarounds into a reproducible three-line
patch and reran the resolver under Rust 1.98.1 against the exact electrs
`v0.12.0` tag. The patched CLI synced 101 regtest UTXOs without a manual wallet
rename. Unmodified RC3 and current upstream `master` still contain the defects.
Compatible dependency updates leave three Esplora-path advisories; removing
Esplora yields an Electrum-only graph with zero vulnerability advisories but an
unmaintained dependency warning and unreviewed license expressions. These are
useful compatibility results, not an adopted fork, lock, or identity crate.

## Quality and security gates

The initial CI proposal is:

```text
format → clippy with warnings denied → unit tests → property tests
       → canonical golden vectors → cross-domain rejection vectors
       → regtest lifecycle tests → package export/import → independent verifier
       → dependency advisory and license checks
```

Tests must separate deterministic core tests from adapter and network tests.
Wall-clock time, DNS, social platforms, remote relays, and chain tips enter as
explicit fixtures or adapter outputs. A second conformance verifier must not
reuse the Rust validation implementation merely through WASM or FFI.

Before any real key custody, add a wallet threat model covering seed creation,
memory handling, encryption at rest, unlock policy, backup, recovery testing,
OS key stores, logs, crash dumps, and migration. Until that review passes,
development uses only disposable test identities and regtest bitcoin.

The first locked graph must also pass `cargo audit`, `cargo deny check`, source
allowlisting, duplicate-dependency review, and a manual review of
consensus-sensitive APIs. A clean scanner result is necessary but is not proof
that an RGB release candidate or a Bitcoin parsing/signing path is correct.

## Deferred from the initial setup

- mainnet, public testnet broadcasts, real bitcoin, and production custody;
- a light-client backend and its privacy/trust model;
- Pubky homeserver deployment and Nostr relay operation;
- PostgreSQL, Redis, public APIs, and object-storage operations;
- Axum, Tauri, Next.js, or another UI/application framework as a required
  dependency;
- GatePass, SplitNight, bonds, Lightning, USDt, payments, and rights contracts;
  and
- release signing, SBOM/provenance, installers, and mobile builds beyond their
  design gates.

## Re-evaluation result

The existing [software-stack diagram](diagrams/05-software-stack-architecture.md)
has the correct authority boundaries and needs no structural rewrite. The
main change from this review is operational: Rust, CLI-first development,
Bitcoin Core regtest, SQLite, and a local content store are the proposed
baseline; RGB lineage and dependency selection become a documented Phase 0
gate; and the service/UI stack remains deferred and replaceable.

## Primary sources checked

- [Rust release announcements](https://blog.rust-lang.org/releases/) and
  [rustup toolchain files](https://rust-lang.github.io/rustup/overrides.html).
- [Bitcoin Core 31.1](https://bitcoincore.org/en/releases/31.1/) and the
  [regtest example](https://developer.bitcoin.org/examples/testing.html).
- [BIP340](https://bips.dev/340/),
  [`rust-bitcoin`](https://docs.rs/bitcoin/latest/bitcoin/), and
  [`secp256k1`](https://docs.rs/secp256k1/latest/secp256k1/).
- [RGB-WG Core](https://github.com/RGB-WG/rgb-core/releases),
  [standard library](https://github.com/RGB-WG/rgb-std/releases), and
  [runtime](https://github.com/RGB-WG/rgb/releases).
- [`rgb-protocol` organization](https://github.com/rgb-protocol),
  [0.11.1 API](https://github.com/rgb-protocol/rgb-api), and
  [sandbox](https://github.com/rgb-protocol/rgb-sandbox).
- [Pubky Core](https://github.com/pubky/pubky-core),
  [PKARR](https://github.com/pubky/pkarr), and
  [Nostr NIP-01](https://github.com/nostr-protocol/nips/blob/master/01.md).
- [SQLite appropriate uses](https://www.sqlite.org/whentouse.html) and
  [PostgreSQL versioning](https://www.postgresql.org/support/versioning/).
- [License and adoption assessment](22-license-and-adoption-assessment.md) and
  [stack compatibility and security assessment](23-stack-compatibility-and-security-readiness.md).
