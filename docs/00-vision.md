# 00 — Vision and project rationale

**O2A — Open2Artist.** Design/specification phase. Rationale reviewed on
2026-09-23. The benefits below are intended outcomes to test with a pilot;
they are not claims of established adoption or measured fraud reduction.

## Main goal

O2A is an open, decentralized, Bitcoin-native protocol for portable identity
and independently verifiable trust in the music ecosystem. Its central goal is
to let artists, venues, promoters, labels, live events, and albums own unique
public IDs through keys held in their own wallet rather than identifiers rented
from a catalog or platform.

Every EntityID is rooted in a dedicated BIP340/secp256k1 public identity key.
The key is separate from Bitcoin spending keys. Identity genesis, controller
changes, recovery-policy changes, and revocation are RGB client-side state
transitions anchored to Bitcoin. Day-to-day controller keys can rotate without
erasing the public ID.

The participant should be able to originate and sign identity and name claims,
publish public channel-control evidence, and explicitly authorize
representatives. Existing platform IDs can be linked without making a platform
account the permanent root of authority. Pubky and Nostr keys are signed
discovery/publication bindings rather than replacements for the Bitcoin root.

An artist should be able to present a signed, portable evidence package to a
new venue. The venue should be able to inspect the claims, verify who signed
them, see known conflicts, and apply its own explicit acceptance policy. A
compatible application should reproduce the same result from the same
evidence, policy, protocol version, and evaluation context.

A public identity must also be retrievable. The owner wallet publishes or
directly transfers a content-addressed public proof package containing the
deliberately public RGB identity-history shard, Bitcoin proofs, and disclosed
evidence needed by another wallet. Mutable discovery URLs are locators, not
authority, and private wallet state remains excluded.

The first vertical is artists, venues, promoters, labels, events, and albums.
EntityID is generic, but every entity has its own root key. An event or album
key can live in the responsible participant's wallet while remaining an
independent public identity for that event or work. Canonical content hashes
bind the ID to versioned event or album claims.

An early application hypothesis is direct remuneration for artist-authorized
uses: approved links, promotional mentions, catalog references, or tour-date
integrations could carry a signed permission and a payment in satoshis. The
artist could choose the terms and payment destination, with optional USDt
conversion and additional RGB contracts considered as later settlement/rights
profiles beyond the required RGB identity lifecycle.
The intended benefit is payment at the point of authorization in participating
services, alongside inspectable consent.

## The current problem

A name, a profile, a platform identifier, and a cryptographic key answer
different questions. None alone establishes all of the following: which
participant is being described, who is authorized to represent it, which
relationships are supported by evidence, and whether that evidence satisfies
the recipient's needs.

The music ecosystem already has substantial identifier and metadata
infrastructure. For example, DDEX's Party Identification and Enrichment
standard supports multiple identifiers for a party, including ISNI, IPN,
IPI, and proprietary IDs. O2A should preserve references to existing
identifiers where useful. Its proposed contribution is a portable record of
controller authorization, signed claims, disputes, and policy evaluation
around those references. It does not assume the industry lacks identifiers.
[DDEX: identifying and describing parties](https://pie.ddex.net/party-identification-and-enrichment/6-identifying-and-describing-parties-and-names/6.2-identifying-and-describing-parties/).

**Identifier fragmentation is a central part of the problem.** Spotify,
Apple Music, and other services assign different IDs to the same artist.
These identifiers belong to different namespaces and are not interchangeable
record identifiers in those services' APIs. Mapping them is possible, but a mapping
does not by itself prove that the artist authorized it. A world-class superstar
may have a Spotify artist ID, a different Apple Music artist ID, and a separate
MusicBrainz record. The [generic identifier example](15-identifier-fragmentation.md)
illustrates ten reference types using non-resolving placeholders. It identifies
no real artist and makes no claim of endorsement.

**Control matters as much as compatibility.** Commercial platforms administer
their own identifier namespaces and access rules. Artists can claim profiles
on Spotify and Apple Music, but through each platform's approval process.
This differs from a portable, artist-signed assertion whose authorization can
be checked outside that platform. Open community catalogs have different
governance: MusicBrainz and Wikidata are useful sources of shared metadata,
but a catalog entry does not establish the subject's cryptographic control.
[Spotify profile claims](https://support.spotify.com/us/artists/article/getting-access-to-spotify-for-artists/),
[Apple Music profile claims](https://artists.apple.com/support/1101-claim-your-account),
[MusicBrainz governance](https://musicbrainz.org/doc/About),
[Wikidata introduction](https://www.wikidata.org/wiki/Wikidata:Introduction).

Universal identifier efforts can reduce ambiguity. ISNI is already an
international standard for public identities, not merely a proposal. A common
identifier still needs a separate answer to who may assert, update, or contest
the claims around it. O2A's contribution is participant-controlled authorization
and portable evidence alongside existing identifiers. It does not require
other systems to abandon their IDs.
[ISO 27729:2024 — ISNI](https://www.iso.org/standard/87177.html).

The working problem statement is that evidence used in one booking, catalog,
or platform relationship is difficult to independently verify and reuse in
another. A new counterparty may need to repeat checks or rely on the original
service's current judgment. The pilot must establish how often this happens,
which checks are costly, and whether participants will supply reusable evidence.

## Subproblems and proposed solutions

| Subproblem | Proposed O2A solution | Why it matters |
| --- | --- | --- |
| Different services assign different IDs, and mappings do not establish the subject's authorization. | A self-custodied BIP340-rooted EntityID plus signed claims binding namespaced external references, evidence, and dispute history. | Existing IDs can be reused while the participant retains an independently controlled root. |
| Identity and profile access depend on the issuing service's rules. | RGB identity lifecycle anchored to Bitcoin, with participant-originated claims and rotatable controllers. | Artists, promoters, venues, labels, events, and albums retain portable IDs and signed histories. |
| Identical names, aliases, and multiple roles make record matching ambiguous. | Unique cryptographic EntityIDs; names and external identifiers remain versioned claims. Competing claims and Bitcoin-established chronology remain visible. | Duplicate stage names do not merge histories, and first publication does not create global ownership of a spelling. |
| Creating a profile or controlling a key is confused with representing a real artist or venue. | Separate controller authorization from self-claims and independent attestations. | Anyone can create an identity; recognition requires evidence under a stated policy. |
| Work history is difficult to carry between services. | Portable signed claims and event evidence, with immutable references and proof export/import. | A counterparty can inspect previous evidence without accepting a catalog's unexplained badge. |
| Participants describe the same event differently. | A canonical EventManifest with separate participant attestations referencing the same manifest. | Verifiers can detect agreement, missing signatures, and conflicting details. Booking, performance, and settlement remain distinct claims. |
| Corrections, impersonation claims, and revocations can disappear behind mutable records. | Signed challenges, supersession, and authorized revocation that preserve history. | A verifier can explain how a dispute changes a result and reproduce earlier decisions. |
| Keys, representatives, and payment endpoints change. | RGB controller transitions and precommitted recovery rules preserve EntityID; payment bindings use separate keys. | A lost working key need not erase identity, and identity keys never become spending keys. |
| Verification rules are hidden or inconsistent. | Deterministic, versioned policies with evidence references and explanations. | Communities can choose different rules while identifying exactly why results differ. |
| A catalog outage or provider change puts discovery and evidence at risk. | Rebuildable registries plus independently retained proof packages; optional public-profile discovery adapters. | Replacing an index should preserve protocol results. Backups and evidence availability still have to be demonstrated. |
| Approved promotional use and remuneration are separate workflows, with no portable record connecting consent to payment. | An optional application binds a specific permitted use, signed terms, an authorized recipient, and a payment receipt. | Artists could approve selected integrations and receive direct payment when authorization is fulfilled. This is a pilot hypothesis, not a fee on every public mention. |

## How the solution works

O2A separates three concerns:

1. **Identity** — the BIP340 root and Bitcoin-anchored RGB history that define
   an EntityID and its current controllers.
2. **Evidence** — what signed claims, attestations, challenges, and revocations
   exist about that entity or its relationships.
3. **Verification** — what a named, versioned policy concludes from the supplied
   evidence and evaluation context.

```text
Bitcoin anchor + validated RGB identity history
          + signed claims + independent attestations
          + challenges/revocations + explicit observations
                       ↓
              portable evidence package
                       ↓
       versioned policy + explicit evaluation context
                       ↓
         reproducible result and explanation
                       ↓
           catalogs and other applications
```

The first scenario is deliberately concrete: an artist, venue, and event each
create a key-rooted EntityID through RGB genesis on Bitcoin regtest. The artist
signs a name claim and publishes a fresh DNS or social control proof. The event
key signs a canonical manifest; the artist and venue attest to its exact hash,
and a promoter can add booking evidence. Two independent wallets validate the
same RGB histories and evidence under the same policy. Variants introduce a
competing name claim, a revoked attestation, and conflicting event details.

Cryptography establishes authorship and integrity. Policy determines what
that evidence supports. Neither a signature, a large number of attestations,
nor a Bitcoin transaction proves by itself that a performance happened or
that a name belongs to a particular person. A reproducible result is always
scoped to its evidence and context; it cannot certify the absence of
undiscovered challenges elsewhere.

## Why solving this is critical

A proposed onboarding path makes those distinctions tangible: sign a name
claim, publish a fresh control-proof token through an established domain or
social account, and collect independent representation or relationship
attestations. Labels and ticket services can endorse a specific association.
An optional satoshi deposit could support a later accountability experiment,
but money does not establish identity. The goal is to make legitimate claims
practical to verify and fraud costly to sustain. See
[control proofs and verification bonds](17-control-proofs-and-verification-bonds.md)
for the Internet Identity/id.ai comparison, trust assumptions, refund limits,
and local acceptance gates.

Identity and authorization are inputs to practical decisions: whom to book,
which history to associate with an artist, who can act for a venue, and later
which payment endpoint is authorized. An incorrect association can spread
through each application that consumes it. A shared way to inspect the
evidence gives those applications a basis for detecting and correcting errors.

For artists, the intended value is continuity and the ability to reuse a
working history. For venues and promoters, it is a more inspectable basis
for onboarding and resolving disagreements. For developers, it is a common
verification contract that can be tested without trusting a particular
database operator. For the ecosystem, it is the ability to replace discovery
services while retaining independently held evidence.

These benefits depend on usable key management, available evidence, and
credible attestors. The project must address collusion and the difficulty new
participants face when they have little history. Counting signatures or
economic activity alone would reward coordinated fake identities and could
exclude legitimate newcomers. The initial policy therefore needs explicit
trust assumptions and a clear way to report insufficient evidence.

## Why now

An additional adoption hypothesis is a concrete, early benefit for artists:
**approve a specific use and receive payment for it**. This could be easier to
evaluate than asking artists to adopt another identifier for a distant network
benefit. The proposed flow and its limits are described in
[artist-authorized uses and payments](16-artist-authorized-use-payments.md).
It is optional downstream application work after the identity core passes its
acceptance gates; its economics and artist interest still require a pilot.

**Artist identity is an active operational concern.** In August 2026, Spotify
described artist identity and trust as a major priority and listed profile
protection, verification, and AI-related transparency initiatives. That is
evidence of current industry attention, not proof of demand for O2A. Our
inference is that portable evidence deserves testing alongside platform
protections; O2A is not an AI detector.
[Spotify: artist identity and transparency](https://newsroom.spotify.com/2026-08-11/ai-persona-badges-transparency/).

**There are established models to build on.** W3C Verifiable Credentials Data
Model 2.0 became a Recommendation in May 2025. O2A can assess interoperability
with existing credential formats while concentrating on music-specific
relationships, conflict semantics, and reproducible policy evaluation. No
W3C compatibility is claimed until a concrete mapping is specified and tested.
[W3C Verifiable Credentials Data Model 2.0](https://www.w3.org/TR/vc-data-model-2.0/).

**Discovery can be tested locally.** Pubky documents public-key discovery and
homeserver storage; Nostr provides BIP340-signed public events. O2A binds these
adapter keys to the Bitcoin-rooted EntityID. Neither adapter is the identity
root, and neither stores private RGB consignments or recovery secrets.
[Pubky developer guide](https://pubky.org/explore/pubky-protocol/getting-started/),
[Homeserver capabilities](https://pubky.org/explore/pubky-protocol/homeserver/).

**The first useful experiment is small.** One artist, one venue, one key-rooted
event, an RGB identity lifecycle on Bitcoin regtest, and two independent
wallets can test the central promise before ticketing or a large reputation
network exists. Existing local RGB and swap work provides engineering
references; compatibility still requires the checks in
[the code reference map](../codereference.md).

The timing case is therefore a testable combination of an active problem,
available components, and a bounded pilot. It does not depend on a token
launch, speculative adoption, or production USDt availability on RGB.

## Why these technologies

| Technology or design choice | Purpose and reason | Boundary or cost |
| --- | --- | --- |
| Dedicated BIP340 identity keys | Give every artist, venue, promoter, label, event, and album a self-custodied public root that is distinct from spending keys. | Root custody and derivation must be safe; a public key does not establish a human-readable name. |
| Required RGB identity lifecycle on Bitcoin | Make genesis, controller rotation, recovery-policy changes, and revocation client-validatable, ordered, and resistant to quiet rewriting. | Requires compatible RGB dependencies, Bitcoin fees, confirmations, reorg handling, and durable consignments. |
| Canonical encoding and immutable evidence identifiers | Give independent implementations the same bytes to hash and verify; make changes detectable. | The encoding and cryptographic profile still need to be frozen and tested. |
| Deterministic, versioned trust policy | Make recognition explainable and reproducible without requiring one global verifier. | Policies need explicit trust assumptions, conflict handling, and bounded inputs. |
| Proposed Rust protocol core | Keep validation logic strongly typed and reusable behind APIs and a CLI. | Rust does not guarantee protocol correctness; independently implemented verification remains an acceptance gate. |
| Conventional API and rebuildable PostgreSQL read models | Make search and application integration practical while keeping evidence portable. | Fast queries do not make the database authoritative. Rebuild tests are required. |
| Pubky/PKARR and optional Nostr adapters | Publish and discover public profiles or signed posts through keys explicitly bound to the O2A ID. | Pubky uses Ed25519, adapter keys can rotate, and public transports must not contain private wallet or consignment data. |
| Optional additional RGB rights profiles | Extend the required identity lifecycle with client-side digital-rights or asset state where useful. | Each profile requires compatible schemas and full validation data; a transaction ID alone is insufficient. |
| Optional Lightning payments and client-controlled swap adapters | Explore sat-denominated payment for an approved use, with a later option to receive a supported USDt asset. | Payment, authorization, and conversion are separate states. Routing, fees, liquidity, asset identity, and failure recovery must be tested; immediate completion is not guaranteed. |

RGB's specific contribution is its commitment and state-transition model:
the spending transaction closes a UTXO seal around a commitment, while clients
validate the associated off-chain data. O2A requires those properties for
identity lifecycle state. Basic self-claims and event attestations remain
signed client-side data and do not each become blockchain transactions.
[RGB commitment and seal model](https://docs.rgb.info/commitment-layer/commitment-schemes).

A centralized database is sufficient for a directory owned and trusted by
one operator. O2A earns its additional complexity only if participants need
evidence to remain verifiable across operators. Existing industry identifiers
and credential standards should be reused or mapped where they fit; the
project's distinct work is the domain semantics and conformance behavior.
The [architecture](01-architecture.md) and
[technology assessment](14-identity-discovery-assessment.md) define these
boundaries in more detail.

## What success must demonstrate

Technical success means independent wallets validate the same Bitcoin/RGB
identity history and agree on valid, invalid, conflicting, and incomplete
evidence under fixed inputs; controller rotation and authorized recovery
preserve identity and historical checks; event and album keys remain distinct;
and a catalog can be rebuilt from retained packages. Discovery outages must
not change the result for the same available package. These are gates in the
[roadmap](13-roadmap.md), not completed capabilities.

Product success requires a separate pilot evaluation: compare the time and
manual steps needed to verify a new counterparty with and without O2A; record
which evidence participants can actually provide; measure verification errors,
unresolved disputes, and the effort of managing keys and recovery. A successful
cryptographic demo alone cannot establish that the workflow is useful.

For the optional paid-use pilot, also measure artist and publisher willingness
to participate, net revenue after fees, time from payment to usable grant,
failed deliveries, and recovery or refund effort. These observations determine
whether direct authorization and remuneration provide an adoption incentive.

## Scope and core principles

O2A v0.1 is not a social network, a DSP identifier replacement, a KYC provider,
a global reputation score, a new blockchain consensus mechanism, or a ticketing
and settlement product. GatePass and SplitNight may consume the primitives
after the identity and evidence model is stable.

- **Portable:** evidence can move between compatible clients.
- **Client-verifiable:** validity is reproducible outside the registry operator.
- **Modular:** applications depend on protocol primitives, never the reverse.
- **Rebuildable:** registries are indexes over evidence, not sources of truth.
- **Explainable:** a verification result identifies the exact policy and evidence used.
- **Versioned:** schemas and policies have explicit versions and hashes.
- **Bitcoin-rooted:** identity lifecycle state is RGB client-side state anchored
  to Bitcoin; ordinary content edits remain off-chain.
- **Self-custodial:** seeds, identity keys, consignments, and proof packages stay
  under the participant's control.
- **Open-source infrastructure:** O2A-authored specifications, documentation,
  and future official reference software use `MIT OR Apache-2.0`; recipients
  can select the low-friction MIT terms or Apache-2.0 with its express patent
  grant. Explicitly marked conformance vectors use CC0-1.0.
