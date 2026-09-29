# O2A code references

This is a research and source-discovery map for the O2A protocol. O2A's own
[README](README.md), [specifications](specs/), and [accepted decisions](adr/)
define its requirements. External code and sibling repositories are references;
their implementation choices do not become O2A rules without an explicit
design decision, compatibility check, and local tests.

## RGB source repositories

### Current O2A line — rgb-protocol v0.11.1

[ADR-0010](adr/0010-rgb-carrier-line.md) selects the rgb-protocol v0.11.1
family with Opret for O2A's first transitions. The complete application,
wallet, SDK, and library map is in
[the reference inventory](docs/28-references.md#rgb-ecosystem-rgb-protocol-v0111-line-adr-0010).

| Reference | What to inspect for O2A | Current boundary |
| --- | --- | --- |
| [`rgb-protocol` API](https://github.com/rgb-protocol/rgb-api) | Client-facing Rust API and wallet/indexer integration maintained for the 0.11.1 family. | This is not O2A's proposed HTTP API and is not evidence of compatibility with RGB-WG Core 0.12. Its current graph includes pre-release BP components. |
| [RGB Sandbox](https://github.com/RGB-Tools/rgb-sandbox) ([current location](https://github.com/rgb-protocol/rgb-sandbox)) | Docker regtest layout, indexer, external wallet, issuance, consignment, and transfer demonstrations. | Its README describes an RGB 0.11.1 RC6 demo. Use it to learn and test that line; do not treat it as proof of a Core 0.12 integration. Some demo scripts remove local data. |
| [RGB Documentation](https://github.com/RGB-Tools/RGB-Documentation) ([current location](https://github.com/rgb-protocol/RGB-Documentation)) | Single-use seals, proof of publication, commitment and anchor structure, client-side validation, and contract operations. | Check the documented version and the matching source before treating an example as a current API or wire contract. |

The `RGB-Tools` sandbox and documentation links redirect to `rgb-protocol` as
checked on 2026-09-23. Repository organization, versions, and APIs can change.
Pin exact revisions and follow the selection boundary recorded in the
[technology-stack brief](docs/21-proposed-tech-stack-and-development-environment.md)
and its [compatibility and security record](docs/23-stack-compatibility-and-security-readiness.md).

### Historical — RGB-WG v0.12 evidence

The RGB-WG v0.12 family remains archived as neutral compatibility evidence.
It is not the ADR-0010 line and must not share a dependency graph with the
v0.11.1 adapter.

| Reference | What the archived review inspected | Historical boundary |
| --- | --- | --- |
| [RGB Core](https://github.com/RGB-WG/rgb-core) | Consensus validation, client-side state, single-use seals, commitments, and Strict Types integration. | Core `v0.12.0` was final in the recorded review; that fact alone did not establish a complete O2A application stack. |
| [RGB-WG standard library](https://github.com/RGB-WG/rgb-std) | High-level contract API, consignments, persistence, and the application-facing 0.12 type graph. | The archived evidence pins `v0.12.0-rc.3` at `e183bebf`; it remains evidence rather than O2A's selected line. |
| [RGB-WG runtime and CLI](https://github.com/RGB-WG/rgb) | Runtime, CLI, import/export, backup, resolver, and application integration behavior. | The archived evidence pins `v0.12.0-rc.3` at `a1e6b415` and records both passing library work and bounded CLI/resolver findings. See the historical compatibility record for details. |

### Cryptographic reference

| Reference | What to inspect for O2A | Current boundary |
| --- | --- | --- |
| [BIP340](https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki) | Schnorr public-key and signature requirements for the dedicated O2A root and controller authorization profile. | O2A's key derivation, domain separation, message framing, and EntityID encoding are defined by its own accepted ADRs, specs, and frozen vectors. Identity keys remain separate from spending keys. |

For O2A, distinguish four checks: the Bitcoin outpoint identifies the seal;
the spending transaction closes it and commits to a transition; an RGB client
validates the off-chain identity transition and proof under the O2A schema;
and the O2A verifier validates BIP340 authorization plus signed external
evidence and trust policy. Bitcoin/RGB is required for EntityID lifecycle
validity, but a Bitcoin public key or UTXO spend alone is not a real-world
identity verification result.

## Authentication and external control-proof references

Reviewed 2026-09-23. These are research candidates, not O2A dependencies.
The assessment and proposed local gates are in
[control proofs and verification bonds](docs/17-control-proofs-and-verification-bonds.md).

| Reference | What to inspect for O2A | Boundary |
| --- | --- | --- |
| [DFINITY Internet Identity](https://github.com/dfinity/internet-identity), revision `2cc9efbb9e2b19af2064e365fa71ef5cb28c0b0c` | Passkey onboarding, scoped sessions, controller/account separation, Rust implementation references. | ICP authentication does not attest an artist name. The [root license](https://github.com/dfinity/internet-identity/blob/2cc9efbb9e2b19af2064e365fa71ef5cb28c0b0c/LICENSE) has an ICP platform limitation; review each component before code reuse. |
| [id.ai](https://id.ai/) and [product explanation](https://id.ai/about) | User journey and privacy-oriented identity management. | User-facing Internet Identity service, not an additional independent witness. |
| [II specification](https://docs.internetcomputer.org/references/internet-identity-spec/) and [ICP credentials](https://docs.internetcomputer.org/guides/authentication/verifiable-credentials/) | Origin-scoped principals, delegations, issuer/subject binding and canister-signature validation. | Requires a distinct adapter and explicit trust roots; do not replace stable EntityID or import a decoded JWT as verified evidence. |
| [ACME DNS-01, RFC 8555 §8.4](https://datatracker.ietf.org/doc/html/rfc8555#section-8.4) | Random, key-bound proof of DNS publication. | Proves domain control for that challenge, not the artist's identity or name ownership. Proposed O2A token format needs its own specification. |
| [Bitcoin BIP 65](https://github.com/bitcoin/bips/blob/master/bip-0065.mediawiki) and [DLC specifications](https://github.com/discreetlogcontracts/dlcspecs) | Timelocked recovery and oracle-dependent contract settlement research. | Reference only: no implemented O2A bond, slashing, or DNS-reading Bitcoin contract is claimed. |

## Local sibling projects

The paths below are machine-local references, not O2A dependencies. Inspect
their current `AGENTS.md`, Git state, memory status, and source before reuse.
Do not copy their runtime state, wallets, keys, consignments, credentials,
private evidence, or Redis records into O2A.

### `/home/kestl/rgbmvp`

This is an independent RGB-on-Liquid Testnet lab. Its
`docs/ARCHITECTURE.md` separates native Liquid issued assets from RGB
client-side contracts and explains the seal/commitment boundary. Its
`crates/lab-rgb/src/seal.rs` and `docs/S3_RGB_WRAP.md` are concrete references
for seal closure, commitment verification, successor seals, consignments, and
the distinction between a value claim and a valid RGB claim. Those files cover
a Liquid/Bitcoin testnet lab, not O2A's identity semantics or a proven Core
0.12 stack. Its `docs/SCENARIOS.md` and `docs/PROJECT_MEMORY.md` show how the
lab ties implementation claims to scenario evidence and source discovery.

Read-only memory workflow from that repository root:

```bash
cd /home/kestl/rgbmvp
python3 project-memory.py status
python3 project-memory.py validate --deep
python3 project-memory.py search "RGB consignment seal commitment validation" --limit 5
```

Open the returned files. The cache was fresh and deep-valid when checked on
2026-09-23; this is a time-bound observation, not a permanent guarantee.

### `/home/kestl/btc-usdt-atomic-swap`

This independent native-BTC-to-token swap lab deliberately excludes RGB as a
settlement leg. It is useful for generic engineering patterns: a chain-free
Rust `crates/protocol-model`, adapter boundaries, deterministic vectors,
Bitcoin Core regtest RPC, persistent intent before a chain action, fail-closed
recovery, and scoped delivery gates. Read `docs/ARCHITECTURE.md`,
`docs/REUSE_PLAN.md`, and `docs/DELIVERY_GATES.md`; the reuse plan also records
why RGBMVP code was adapted as concepts rather than copied. Swap HTLC rules,
mock-token behavior, wallet state, and network approvals do not define O2A.

Read-only memory workflow from that repository root:

```bash
cd /home/kestl/btc-usdt-atomic-swap
python3 palimnex.py status
python3 palimnex.py validate --deep
python3 palimnex.py search "regtest chain independent protocol model recovery" --limit 5
```

Its Redis service returned `Connection refused` on 2026-09-23, so
`cache_consulted: false` for this review. Use current files when that cache is
unavailable; do not start, clear, or point O2A's Redis at the sibling namespace
merely to obtain a reference.

## Reuse rule for O2A

For any external or sibling implementation detail proposed for O2A, record the
source URL or local path and revision, its license, the exact behavior being
adapted, the version compatibility result, O2A-specific semantic differences,
and tests against O2A's own specifications. O2A's first gates remain the
BIP340-rooted EntityID encoding, a compatible Bitcoin/RGB identity profile,
canonical serialization, authorization and recovery transitions, portable
consignments/proof packages, and independent deterministic Hello-World vectors
before production code, as specified in [the roadmap](docs/13-roadmap.md).
