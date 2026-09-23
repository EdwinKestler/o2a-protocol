# 15 — Identifier fragmentation and participant control

**Status:** illustrative research supporting the [project rationale](00-vision.md).
General sources reviewed on 2026-09-23. All artist examples and identifiers are
fictional placeholders, not O2A registrations or artist-signed endorsements.

## One artist, many identifiers

The same artist can have a Spotify artist ID, an Apple Music artist ID, a
MusicBrainz identifier, and several other references. Each system identifies
its own record. Even when records describe the same participant, their IDs
are not interchangeable inputs to each other's APIs. An integration needs
namespaces, mappings, and a way to evaluate the evidence for those mappings.

Consider a world-class superstar, referred to only as **a recognized music
artist**. The following values deliberately do not identify or link to any
real person or account; they illustrate different identifier namespaces.

| System | Non-resolving placeholder | Reference type |
| --- | --- | --- |
| Spotify | `<spotify-artist-id>` | Platform artist record |
| Apple Music | `<apple-music-artist-id>` | Platform artist record |
| Amazon Music | `<amazon-music-artist-id>` | Platform artist record |
| Deezer | `<deezer-artist-id>` | Platform artist record |
| TIDAL | `<tidal-artist-id>` | Platform artist record |
| YouTube | `<youtube-channel-id>` | Channel, distinct from an artist catalog record |
| MusicBrainz | `<musicbrainz-artist-id>` | Community music metadata record |
| Wikidata | `<wikidata-item-id>` | General knowledge-base item, not government identity |
| ISNI | `<isni-public-identity-id>` | Standard public-identity reference |
| X | `<x-numeric-user-id>` | Platform account reference |

A real integration would retain the source, verification method, and time of
each association. Reading a profile would establish what that service
publishes, not that the subject signed the association with every other record.
Removing a name while retaining real IDs or profile URLs would still identify
the artist, so this example retains neither.

## Compatibility and authority are separate problems

The issue is not that these IDs can never be connected. Metadata services
already maintain links, and industry formats can carry several identifiers
for one party. DDEX explicitly supports ISNI, IPN, IPI, proprietary IDs, and
other party identifiers. O2A should consume useful mappings while preserving
who asserted them and what they establish.
[DDEX party identifiers](https://pie.ddex.net/party-identification-and-enrichment/6-identifying-and-describing-parties-and-names/6.2-identifying-and-describing-parties/).

The separate authority question is: **did the artist or an authorized
representative make this claim, or did an external service associate the
records?** Both can be useful evidence, but they are different statements.

| Model | Who governs the record or access? | What the identifier alone does not establish |
| --- | --- | --- |
| Commercial platform ID | The platform administers its namespace and profile-access process. | A portable signature by the artist or representative authorizing a cross-platform claim. |
| Open community catalog ID | Contributors and the project's governance maintain shared records. | Exclusive subject control or a subject-signed assertion about the record. |
| Standard identifier such as ISNI | The standard and its registration/assignment system govern issuance. | Control of a signing key or authorization of a particular claim or representative. |
| Proposed O2A EntityID and claims | Controller authorization governs protocol transitions; claims remain challengeable and policies govern recognition. | Automatic truth about the artist's name, legal identity, history, or ownership of an external account. |

MusicBrainz describes itself as a community-maintained music encyclopedia;
Wikidata describes a collaborative knowledge base. Their openness and reuse
are valuable and should not be confused with proprietary platform control.
They still serve a different function from an identity whose controller
signs portable statements.
[MusicBrainz](https://musicbrainz.org/doc/About),
[Wikidata](https://www.wikidata.org/wiki/Wikidata:Introduction).

Artists also can claim existing platform profiles. Spotify and Apple Music
document access requests, identity checks, and team administration. O2A's
proposed benefit is that the participant can originate its protocol identity
and sign evidence without waiting for a particular platform to grant that
identity. It does not grant access to or override ownership rules for those
external profiles.
[Spotify for Artists](https://support.spotify.com/us/artists/article/getting-access-to-spotify-for-artists/),
[Apple Music for Artists](https://artists.apple.com/support/1101-claim-your-account).

ISNI is an established international standard for identifying public
identities across creative fields. Universal-ID initiatives address the
useful question of common references; participant authorization still needs
its own mechanism. ISNI's registration agencies illustrate that an artist can
apply for an identifier while its assignment remains within a registry
system. O2A should interoperate where practical rather than invent a new
number and assume the governance problem is solved.
[ISO 27729:2024](https://www.iso.org/standard/87177.html),
[ISNI registration agency FAQ](https://isni.bowker.com/faqs).

## The same design requirement beyond artists

O2A must also represent promoters, venue operators, and live events across
ticketing, discovery, contractual, and internal business records. Their
identifiers may come from different organizations, and the entity described
may differ: a physical venue is not necessarily its current operator; a
festival brand is not one specific year's event; a promoter's staff account
is not the promoter organization.

The proposed model therefore requires an explicit subject and relationship.
A venue operator can assert its role for a venue; an organizer can assert its
role for an event; artists and counterparties can attest to the same event
manifest. No participant gains authority over all these entities merely by
creating a matching name or importing a platform record.

## What O2A should add

An external-identifier claim should retain the EntityID, external namespace,
identifier value, exact relationship being claimed, issuer authorization,
supporting evidence, and relevant time/context. These are design requirements
for the draft claim vocabulary, not a frozen encoding. A claim that a catalog
record describes an artist is different from proof that the artist controls
the associated account.

The controller signs the statement. Counterparties may endorse or challenge
it. A named policy determines whether the evidence supports the asserted
relationship. Exported evidence preserves the assertion and its provenance
even if the discovery service changes; it does not guarantee that an external
profile remains available or under the same control forever.

The intended result is **an identity the participant can state and authorize,
with portable evidence linking it to the ecosystem's existing records**.
It remains open to independent verification, disagreement, and correction.
