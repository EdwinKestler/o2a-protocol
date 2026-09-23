# O2A Protocol

**Open2Artist (O2A)** is a decentralized, Bitcoin-native identity,
attestation, verification, and registry protocol for the music ecosystem.

Each artist, venue, promoter, label, live event, and album has a public O2A
EntityID rooted in its own dedicated BIP340/secp256k1 identity key. The owner
holds that key and its proof data in a self-custodial wallet/node. Identity
genesis, controller changes, recovery-policy changes, and revocation are RGB
client-side state transitions anchored to Bitcoin. Identity keys are never
Bitcoin spending keys.

Human-readable names remain evidence-backed claims rather than globally locked
usernames. Wallets can show DNS and social control proofs, attestations from
other O2A IDs, challenges, competing claims, and Bitcoin-established chronology
without pretending that the first claimant owns a spelling forever.

Start with the [project vision and rationale](docs/00-vision.md) and the
accepted
[Bitcoin-rooted identity decision](adr/0005-bitcoin-rooted-self-custodial-identity.md).

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
BIP340 key-rooted EntityID
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

- BIP340-rooted EntityID genesis on RGB/Bitcoin;
- controller rotation, committed recovery rules, and revocation;
- signed claims and third-party attestations;
- DNS, HTTPS, Pubky, Nostr, and social channel-control observations;
- challenges and evidence revocation;
- deterministic trust policies;
- artist, venue, promoter, album, and event identity profiles;
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
[Bitcoin-rooted entity](specs/entity-schema.md),
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

No production implementation code should be introduced until the v0.1 RGB
identity schema, canonical serialization, Bitcoin commitment and reorg rules,
key-derivation profile, and deterministic test vectors are agreed.

This repository and the future official reference wallet and node are licensed
under the [Apache License 2.0](LICENSE), with copyright held by Edwin Kestler.
Anyone may inspect, build, run, modify, and distribute them under that license.
The license decision is closed; the remaining specification and conformance
gates still apply before implementation code is accepted.

## First milestone

The first complete protocol scenario is:

1. An artist, a venue, and a live event create distinct key-rooted EntityIDs
   through RGB genesis transitions on Bitcoin regtest.
2. Their wallets validate the RGB histories and current controller keys.
3. The artist signs a name claim and publishes a fresh DNS or social control
   proof; a competing name claim remains visible.
4. The event key signs a canonical event manifest. The artist and venue sign
   separate attestations over its exact hash; a promoter may add booking
   evidence.
5. Known challenges and revocations remain visible in the package. Booking,
   performance, and settlement stay distinct claims.
6. Independent clients apply the same versioned trust policy to the same
   Bitcoin/RGB history and evidence.
7. Each client derives the same verification result and explanation.

```text
same Bitcoin/RGB history + same evidence + same policy
             + same protocol version + same evaluation context
                              =
                 same verification result
```

## Status

**Design / specification phase.**  
The BIP340 root and required Bitcoin/RGB identity lifecycle are accepted design
constraints. The exact EntityID encoding, RGB schema, commitment method,
confirmation/reorg policy, key-derivation profile, serialization rules, and
compatible dependency set remain subject to specification and regtest
validation before v0.1 implementation is accepted.
