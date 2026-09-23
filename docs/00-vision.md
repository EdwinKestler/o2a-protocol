# 00 — Vision and project rationale

**O2A — Open2Artist.** Design/specification phase. Rationale reviewed on
2026-09-23. The benefits below are intended outcomes to test with a pilot;
they are not claims of established adoption or measured fraud reduction.

## Main goal

O2A is an open protocol for portable identity and independently verifiable
trust in the music ecosystem. Its goal is to let artists, venues, and promoters
carry evidence of who they represent and how they have worked together across
applications, without making one catalog operator the authority over that
history.

The participant should be able to originate and sign its own identity claims,
and explicitly authorize representatives. Existing platform IDs can be linked
to that identity without making a platform account the permanent root of its
authority. This applies to artists, promoters, venue operators, and event
organizers as well as to the relationships between them.

An artist should be able to present a signed, portable evidence package to a
new venue. The venue should be able to inspect the claims, verify who signed
them, see known conflicts, and apply its own explicit acceptance policy. A
compatible application should reproduce the same result from the same
evidence, policy, protocol version, and evaluation context.

The first vertical is artists, venues, promoters, and events. The underlying
EntityID is intentionally generic: one participant can have multiple roles
without creating a separate identity for each application. The long-term
opportunity is a shared foundation for catalogs, booking, ticketing, and
payments that can reuse that evidence.

An early application hypothesis is direct remuneration for artist-authorized
uses: approved links, promotional mentions, catalog references, or tour-date
integrations could carry a signed permission and a payment in satoshis. The
artist could choose the terms and payment destination, with optional USDt
conversion and RGB contracts considered as later settlement/rights adapters.
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
| Different services assign different IDs, and mappings do not establish the subject's authorization. | Signed claims that bind a stable EntityID to namespaced external references, with explicit issuer, evidence, and dispute history. | Existing IDs can be reused while distinguishing a catalog's association from an artist's own assertion. |
| Identity and profile access depend on the issuing service's rules. | Participant-originated identity claims and controller-authorized transitions that compatible clients can verify. | Artists, promoters, venues, and organizers can carry their own signed statements between applications. Platform permissions remain separate. |
| Identical names, aliases, and multiple roles make record matching ambiguous. | Stable EntityID; names, roles, and external identifiers expressed as versioned claims. Competing name claims remain visible. | A name change or duplicate stage name need not merge unrelated histories or erase a participant. |
| Creating a profile or controlling a key is confused with representing a real artist or venue. | Separate controller authorization from self-claims and independent attestations. | Anyone can create an identity; recognition requires evidence under a stated policy. |
| Work history is difficult to carry between services. | Portable signed claims and event evidence, with immutable references and proof export/import. | A counterparty can inspect previous evidence without accepting a catalog's unexplained badge. |
| Participants describe the same event differently. | A canonical EventManifest with separate participant attestations referencing the same manifest. | Verifiers can detect agreement, missing signatures, and conflicting details. Booking, performance, and settlement remain distinct claims. |
| Corrections, impersonation claims, and revocations can disappear behind mutable records. | Signed challenges, supersession, and authorized revocation that preserve history. | A verifier can explain how a dispute changes a result and reproduce earlier decisions. |
| Keys, representatives, and payment endpoints change. | Controller rotation preserving EntityID, historical authorization checks, and separate expiring/revocable payment bindings. | Continuity does not require retaining a compromised spending key. Recovery without prior authorization remains a separate policy problem. |
| Verification rules are hidden or inconsistent. | Deterministic, versioned policies with evidence references and explanations. | Communities can choose different rules while identifying exactly why results differ. |
| A catalog outage or provider change puts discovery and evidence at risk. | Rebuildable registries plus independently retained proof packages; optional public-profile discovery adapters. | Replacing an index should preserve protocol results. Backups and evidence availability still have to be demonstrated. |
| Approved promotional use and remuneration are separate workflows, with no portable record connecting consent to payment. | An optional application binds a specific permitted use, signed terms, an authorized recipient, and a payment receipt. | Artists could approve selected integrations and receive direct payment when authorization is fulfilled. This is a pilot hypothesis, not a fee on every public mention. |

## How the solution works

O2A separates three concerns:

1. **Identity** — who controls an EntityID and can authorize its transitions.
2. **Evidence** — what signed claims, attestations, challenges, and revocations
   exist about that entity or its relationships.
3. **Verification** — what a named, versioned policy concludes from the supplied
   evidence and evaluation context.

```text
EntityID + signed claims + independent attestations
          + challenges/revocations
                       ↓
              portable evidence package
                       ↓
       versioned policy + explicit evaluation context
                       ↓
         reproducible result and explanation
                       ↓
           catalogs and other applications
```

The first scenario is deliberately concrete: an artist creates an EntityID
and a self-claim; the artist and a venue sign evidence referring to the same
event manifest; a promoter can add booking evidence. Two independent clients
evaluate the package under the same policy. Variants introduce a competing
name claim, a revoked attestation, and conflicting event details.

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

**Discovery can be tested locally.** Pubky documents a local development stack
for public-key discovery and homeserver storage. This makes it possible to
evaluate user-controlled public profiles without depending on a public
deployment. Its current storage and recovery constraints are reasons for an
optional adapter and a migration test, rather than an assumed production fit.
[Pubky developer guide](https://pubky.org/explore/pubky-protocol/getting-started/),
[Homeserver capabilities](https://pubky.org/explore/pubky-protocol/homeserver/).

**The first useful experiment is small.** One artist, one venue, a mutually
evidenced event, and two verifiers can test the central promise before ticketing,
financial settlement, or a large reputation network exists. Existing local
RGB and swap work provides engineering references; compatibility and reuse
still require the checks in [the code reference map](../codereference.md).

The timing case is therefore a testable combination of an active problem,
available components, and a bounded pilot. It does not depend on a token
launch, speculative adoption, or production USDt availability on RGB.

## Why these technologies

| Technology or design choice | Purpose and reason | Boundary or cost |
| --- | --- | --- |
| Public-key signatures and controller history | Make authorship and authorization independently checkable across services. | Key custody, rotation, and recovery must be usable; signatures do not establish real-world truth. |
| Canonical encoding and immutable evidence identifiers | Give independent implementations the same bytes to hash and verify; make changes detectable. | The encoding and cryptographic profile still need to be frozen and tested. |
| Deterministic, versioned trust policy | Make recognition explainable and reproducible without requiring one global verifier. | Policies need explicit trust assumptions, conflict handling, and bounded inputs. |
| Proposed Rust protocol core | Keep validation logic strongly typed and reusable behind APIs and a CLI. | Rust does not guarantee protocol correctness; independently implemented verification remains an acceptance gate. |
| Conventional API and rebuildable PostgreSQL read models | Make search and application integration practical while keeping evidence portable. | Fast queries do not make the database authoritative. Rebuild tests are required. |
| Optional Pubky/PKARR adapter | Explore user-controlled public-profile storage and discovery across homeservers. | O2A EntityID remains stable independently of the Pubky key. Public profiles cannot store private evidence by default. |
| Optional RGB with Bitcoin anchors | Later support client-side validation of digital rights or asset transitions using UTXO seals and commitments, while retaining contract data off-chain. | Requires a compatible RGB stack and the actual validation data; a transaction ID alone is insufficient. It adds no automatic authority to a real-world identity claim. |
| Optional Lightning payments and client-controlled swap adapters | Explore sat-denominated payment for an approved use, with a later option to receive a supported USDt asset. | Payment, authorization, and conversion are separate states. Routing, fees, liquidity, asset identity, and failure recovery must be tested; immediate completion is not guaranteed. |

RGB's specific contribution is its commitment and state-transition model:
the spending transaction closes a UTXO seal around a commitment, while clients
validate the associated off-chain data. That is useful when an application
needs those properties. Basic self-claims and event attestations do not need
to become blockchain transactions.
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

Technical success means independent verifiers agree on valid, invalid,
conflicting, and incomplete evidence under fixed inputs; controller rotation
preserves identity and historical checks; and a catalog can be rebuilt from
retained packages. Optional discovery outages must not change the result for
the same available package. These are acceptance gates in the
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
- **Minimal on-chain footprint:** use blockchain commitments only where they add integrity or settlement value.
