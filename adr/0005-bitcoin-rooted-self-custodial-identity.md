# ADR-0005 — Bitcoin-Rooted Self-Custodial Identity

**Status:** Accepted for v0.1 design

## Context

O2A exists to give participants in the music ecosystem a public identifier
that they control in their own wallet rather than rent from a catalog or
platform. Artists, venues, promoters, labels, live events, and albums need
unique cryptographic references, portable evidence, and histories that cannot
be quietly rewritten by one service.

A public key can identify a signer and authorize protocol actions. It does not
by itself prove that a human-readable name belongs to a real-world artist,
that a venue hosted an event, or that an album contains a particular recording.
Those statements require signed claims, channel-control proofs, attestations,
content commitments, and an explicit verification policy.

## Decision

### Bitcoin-native root identity

Every O2A entity has a dedicated BIP340/secp256k1 root identity public key.
The root is separate from every Bitcoin spending key and MUST NOT be reused as
a payment key. The O2A EntityID is deterministically rooted in that public key,
the protocol profile, and the network context. The final human-readable and
binary encodings remain to be frozen by the specification.

Each entity uses a distinct root key, including:

```text
ARTIST · BAND · VENUE · PROMOTER · LABEL · ORGANIZATION · EVENT · ALBUM
```

Album and event keys may be derived and held in the responsible participant's
self-custodial wallet, but they are independent entity keys. Their signed
metadata also commits to canonical content or manifest hashes.

### Controllers, recovery, and RGB lifecycle

The root key signs the identity genesis. Day-to-day controller keys are
delegated under the current identity state and can rotate without changing the
EntityID. The root key is an identifier and genesis authority; it is not an
unconditional forever-controller after later state transitions.

Identity creation, controller changes, recovery-policy changes, and revocation
are RGB client-side state transitions anchored to Bitcoin single-use seals.
The current valid controller and recovery policy come from the validated RGB
history and Bitcoin anchor, not from the newest database row or profile file.
Recovery without a currently authorized key is valid only when a recovery rule
committed in an earlier valid state authorizes it.

### Claims, names, and public evidence

Human-readable artist names, venue names, promoter names, album titles, and
event names are signed claims, not globally allocated usernames. The core
protocol has no first-claim ownership rule for a spelling. Competing claims
remain visible, including their Bitcoin-established ordering, supporting
evidence, challenges, and revocations.

Wallets evaluate name claims using explicit policies. Evidence may include:

- a fresh, key-bound DNS TXT or HTTPS publication;
- a key-bound post or profile field on a recognized social account;
- confirmations from other O2A identities;
- canonical album, event, or media hashes;
- signed observations of online evidence; and
- optional Bitcoin checkpoints for important evidence packages.

Ordinary profile edits and evidence objects remain signed client-side data and
do not each require a Bitcoin transaction. A Bitcoin timestamp or RGB anchor
establishes commitment, ordering, and state-transition validity. It does not
decide which claimant is the real-world owner of a name.

### Discovery and transport keys

Pubky/PKARR and Nostr are discovery or publication adapters, not replacements
for the O2A root identity:

- a Pubky Ed25519 key may be bound to an EntityID by a signed, versioned claim;
- a Nostr BIP340 public key may be separately bound for signed event
  publication; and
- adapter keys can rotate or disappear without changing the O2A EntityID when
  the valid RGB identity state authorizes a replacement.

Public discovery data must not contain private RGB consignments, private
attestations, wallet seeds, recovery secrets, or Bitcoin spending keys.

### Consensus and verification

O2A does not introduce a validator set that votes on identity truth.

```text
Bitcoin consensus
    validates ordering, confirmations, commitments, and spent seals

RGB client-side validation
    validates the supplied identity state history against those anchors

O2A deterministic verification
    validates controllers, signatures, evidence, conflicts, and a named policy
```

Wallets that receive the same bounded evidence package, validated RGB history,
policy, protocol version, and evaluation context MUST return the same result.
An online wallet may additionally collect fresh DNS, HTTPS, social, Bitcoin,
or discovery observations. Those observations become explicit evidence; live
network responses are never hidden inputs to the deterministic evaluator.

### Self-custodial client

The minimum O2A client is a wallet-like local application that stores the
owner's seed, identity and controller keys, RGB consignments, attestations,
challenges, and portable proof packages. Identity keys use their own hardened
derivation domain and remain separate from payment keys.

The client may validate Bitcoin through a full node or a clearly labeled light
mode with explicit trust and privacy assumptions. It can publish and discover
public data through Pubky and optional Nostr adapters, check fresh channel
proofs while online, and verify retained proof packages while offline.

## Consequences

Positive:

- the participant, not a catalog operator, controls the cryptographic ID;
- identity lifecycle order and non-equivocation inherit Bitcoin security;
- operational keys can rotate without erasing the ID;
- events and albums are independently addressable and self-attested;
- registries and discovery services remain replaceable; and
- wallets can explain both supporting and competing name claims.

Costs and limits:

- v0.1 now requires a compatible, pinned RGB/Bitcoin implementation profile;
- identity creation and lifecycle changes require Bitcoin fees and confirmation
  policy;
- client-side validation requires durable consignment and proof availability;
- a lost or compromised root requires a previously committed recovery path;
- Pubky and O2A use different key schemes and require an explicit binding; and
- Bitcoin cannot resolve the social oracle problem of who is entitled to a
  human-readable name.

## Relationship to earlier decisions

- [ADR-0001](0001-modular-protocol-architecture.md) keeps the layered dependency
  rule, but Bitcoin/RGB identity lifecycle is now a required foundation rather
  than an optional settlement adapter.
- [ADR-0002](0002-entity-id-over-artist-id.md) keeps generic EntityID and entity
  types, while this ADR defines the public-key root and adds ALBUM.
- [ADR-0003](0003-catalog-is-not-source-of-truth.md) remains unchanged.
- [ADR-0004](0004-consensus-as-policy-not-blockchain.md) still governs the
  meaning of social evidence; this ADR makes Bitcoin consensus mandatory for
  lifecycle ordering without turning it into a vote on name ownership.

## Required acceptance evidence

Before v0.1 implementation claims completion, the repository must contain
version-pinned regtest vectors for genesis, controller rotation, recovery-rule
change, authorized recovery, revocation, invalid/forked RGB history, missing
consignments, reorg handling, duplicate names, album/event custody, Pubky and
Nostr bindings, and offline deterministic verification by independent clients.
