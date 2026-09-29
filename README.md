# O2A Protocol

**Open2Artist (O2A)** is a decentralized, Bitcoin-native identity,
attestation, verification, and registry protocol for the music ecosystem.

Each artist, venue, promoter, label, live event, and album has a public O2A
EntityID derived from its complete canonical genesis payload. That payload is
signed by its own dedicated BIP340/secp256k1 identity key. The owner holds the
key and proof data in a self-custodial wallet/node. Identity
genesis, controller changes, recovery-policy changes, and revocation are RGB
client-side state transitions anchored to Bitcoin. O2A-signing keys are never
Bitcoin spending keys; dedicated role-4 seal keys spend the identity's
deterministic P2TR seal outputs and remain separate from payment keys.

Human-readable names remain evidence-backed claims rather than globally locked
usernames. Wallets can show DNS and social control proofs, attestations from
other O2A IDs, challenges, competing claims, and Bitcoin-established chronology
without pretending that the first claimant owns a spelling forever.

Start with the [project vision and rationale](docs/00-vision.md) and the
accepted
[Bitcoin-rooted identity decision](adr/0005-bitcoin-rooted-self-custodial-identity.md).
Its EntityID derivation is amended by the accepted
[genesis-bound identity decision](adr/0008-genesis-bound-entity-id.md).
The accepted [scoped genesis freeze](adr/0009-scoped-genesis-freeze.md)
preserves a frozen-format mainnet genesis and its `official_name` claim indefinitely
with a signer-independent O2A-native state ID over
`EntityID || resulting_state`, without freezing the unfinished RGB stack or
the rest of Draft v0.1. The accepted RGB line and carrier are rgb-protocol
v0.11.1 and Opret; concrete program bytes and the remaining transition gates
must still close before any identity transition.

The accepted [network-configuration decision](adr/0011-network-as-configuration.md)
makes regtest, signet, and mainnet profiles of one implementation selected by
`O2A_NETWORK`, with regtest as the default. Development and networked tests
stay on regtest and signet. Mainnet additionally requires a session-local flag
and typed confirmation, and ADR-0009 still limits it to the frozen genesis plus
one `official_name` claim until the RGB program is final.

The [project website draft](docs/WEBSITE.md) has a public Sites deployment and
a local preview. Public access is the default Sites policy; GitHub Pages remains
a separate, currently disabled publication route. Examples use generic
participants.

## Design principle

```text
Bitcoin consensus
    ↓
RGB identity state
    ↓
Genesis-bound EntityID signed by its BIP340 root
    ↓
Claims and attestations
    ↓
Optional challenges / evidence revocation when present
    ↓
Trust Policy
    ↓
Registries and Applications
```

Dependencies flow downward only. Applications consume protocol primitives;
lower layers never depend on application-specific behavior. Bitcoin validates
anchors and spent seals; it does not decide who is the real-world owner of an
artist or venue name.

## Source of verification

Registries and databases are projections, not authority. The portable source
of verification is the validated RGB identity history, its Bitcoin anchors,
and the signed evidence package retained by clients. Public profiles are
discoverable application data.

```text
Bitcoin anchor + validated RGB identity history + signed evidence
                    + versioned policy
                              ↓
          reproducible result + rebuildable registry
```

Given identical inputs, independent conforming wallets MUST produce the same
result. Online DNS, social, Pubky, Nostr, and Bitcoin observations become
explicit evidence rather than hidden verifier inputs.

A public identity is useful only when another wallet can obtain its validation
data. The owner publishes or directly transfers a content-addressed public
proof package containing the deliberately public RGB identity-history shard,
Bitcoin proofs, and disclosed evidence. Discovery URLs are locators, never
authority; private wallet state remains excluded.

## Initial scope

O2A v0.1 specifies:

- genesis-bound EntityIDs signed by dedicated BIP340 roots on RGB/Bitcoin;
- controller rotation, committed recovery rules, and revocation;
- signed claims and third-party attestations;
- DNS, HTTPS, Pubky, Nostr, and social channel-control observations;
- challenges and evidence revocation;
- deterministic trust policies;
- artist, venue, promoter, label, album, and event identity profiles;
- rebuildable registry projections and portable proof packages; and
- module boundaries for GatePass and SplitNight.

## Repository structure

```text
docs/   Narrative protocol design
specs/  Canonical data and verification contracts
adr/    Architecture decision records
```

When two documents disagree, follow
[document authority](docs/DOCUMENT-AUTHORITY.md). Accepted ADRs prevail over
normative specs, specs prevail over explanations, and explanations prevail
over diagrams, the website, and application proposals. This README is the
index and status summary.

The current schema set defines the
[canonical byte encoding and signed payload layouts](specs/canonical-encoding.md),
[Bitcoin-rooted entity](specs/entity-schema.md),
[RGB identity state machine](specs/rgb-identity-contract.md),
[claims](specs/claim-schema.md),
[attestations](specs/attestation-schema.md),
[challenges](specs/challenge-schema.md),
[channel-control proofs](specs/control-proof-schema.md),
[discovery-key bindings](specs/discovery-binding-schema.md),
[event and album identities](specs/music-object-schema.md),
[cryptographic signing domains](specs/cryptographic-profile.md),
[public proof packages](specs/proof-package-schema.md), and
[verification policy](specs/verification-policy.md).

Local source discovery and historical memory use Palimnex. See
[the O2A Palimnex setup](docs/PALIMNEX.md) for installation and validation.
See [code references](codereference.md) for RGB upstream sources and the
independent local project knowledge available for research.
The [identity/discovery assessment](docs/14-identity-discovery-assessment.md)
maps Pubky, Nostr, DNS/social proofs, and wallet custody into the architecture.
The [control-proof assessment](docs/17-control-proofs-and-verification-bonds.md)
defines the channel-proof and independent-observation boundary.
The [proposed technology stack and initial development environment](docs/21-proposed-tech-stack-and-development-environment.md)
turns the accepted architecture into a CLI-first Rust and Bitcoin Core regtest
plan while keeping the concrete RGB program and dependency lock behind Phase 0
gates.
The supporting [license/adoption assessment](docs/22-license-and-adoption-assessment.md)
and [compatibility/security record](docs/23-stack-compatibility-and-security-readiness.md)
record the accepted dual-license policy, the dependency-license assessment
register, the disposable compatibility evidence, blockers, and required
mitigations without adopting a dependency graph.
The [containerized Phase 0 development environment](dev/README.md) supplies a
pinned Rust toolchain, isolated Bitcoin Core regtest, and an opt-in disposable
RGB compatibility profile without adding an O2A implementation crate.
Supporting projection notes cover the
[artist catalog](docs/08-artist-catalog.md),
[venue registry](docs/09-venue-registry.md),
[event registry](docs/10-event-registry.md),
[promoter registry](docs/18-promoter-registry.md),
[album registry](docs/19-album-registry.md), and
[label registry](docs/20-label-registry.md).

## Status and audit trail

The supporting [decision audit](docs/24-decision-audit-2026-09.md) records the
reviewed choices without replacing their ADRs or specifications. The
[scenario matrix](docs/25-scenario-matrix.md),
[test catalog](docs/26-test-catalog.md),
[artifact inventory](docs/27-artifact-inventory.md), and
[reference index](docs/28-references.md) connect each claim to its fixture,
evidence path, command, hash, or upstream standard.

No production implementation code should be introduced until the candidate
v0.1 encoding and lifecycle rules are completed by a concrete adopted RGB
program, the remaining identity derivation allocation, a compatible dependency
lock, and complete deterministic conformance vectors. ADR-0010 has selected
the RGB line and Opret carrier, but it does not close those remaining gates.

O2A-authored specifications, documentation, and future official reference
software are licensed, at the recipient's option, under
[`MIT OR Apache-2.0`](LICENSE), with copyright held by Edwin Kestler. The
[Apache-2.0](LICENSE-APACHE) option retains its express patent grant; the
[MIT](LICENSE-MIT) option minimizes downstream license friction. Future
conformance vectors are separately offered under CC0-1.0 only within their
explicitly marked directory. Third-party material retains its own license.
The remaining specification and conformance gates still apply before
implementation code is accepted.

## First milestone

The first complete protocol scenario is:

1. An artist, venue, promoter, label, live event, and album create distinct
   genesis-bound EntityIDs through RGB genesis transitions on Bitcoin regtest.
2. Their wallets validate the RGB histories and current controller keys.
3. Day-to-day controller keys sign typed objects while root and Bitcoin
   spending keys remain separate.
4. The artist publishes a fresh DNS or social name-control proof; a competing
   EntityID claiming the same name remains visible.
5. The event and album keys sign canonical manifest and content hashes.
6. Counterparties issue separate attestations. Any challenge or evidence
   revocation that exists remains visible; none is a mandatory verification
   hop.
7. The owner exports a content-addressed public proof package containing the
   required RGB history, Bitcoin proofs, signing domains, disclosed evidence,
   named policy, protocol version, and evaluation context.
8. Two independent clients validate that same bounded package and derive the
   same explained result.

```text
same Bitcoin/RGB history + same evidence + same policy
             + same protocol version + same evaluation context
                              =
                 same verification result
```

## Status

**Design / specification phase.**  
The BIP340 root and required Bitcoin/RGB identity lifecycle are accepted design
constraints. O2A-CANON-1 now specifies the candidate EntityID and object bytes,
and the RGB identity-contract draft specifies candidate lifecycle, recovery,
confirmation, and reorg behavior. The Route B key-derivation profile is
**demo-stable v0.1** under [ADR-0006](adr/0006-route-b-key-derivation-via-bip85.md).
[ADR-0009](adr/0009-scoped-genesis-freeze.md) is accepted and freezes the
genesis, one `official_name` claim, and Route B format for roles 0, 1, 2, and
4. [ADR-0010](adr/0010-rgb-carrier-line.md) is accepted and selects
rgb-protocol v0.11.1 with Opret for the first identity transitions. Phase 0
remains open for concrete O2A RGB program bytes, the production dependency
lock, transition and custody gates outside the accepted evidence,
restore/discovery, the remaining derivation profile, and broader conformance.
[ADR-0011](adr/0011-network-as-configuration.md) supports mainnet as a guarded
configuration of the same code path; it does not relax those gates. No
production or mainnet identity network is running, and this repository makes
no general mainnet-readiness claim.
