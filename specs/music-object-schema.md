# Music Object Identity Profiles — Draft v0.1

## Purpose

EVENT and ALBUM are public-key-rooted O2A entities. They are uniquely
referenceable, can self-attest through keys held by their custodian, and can
receive attestations from artists, venues, promoters, labels, and organizers.

Event and album manifests are signed by that entity's own key in domain
`O2A/v0.1/music-manifest`. The manifest hash does not prove that the event
occurred or that anyone owns the copyright.

## Event identity profile

An EVENT entity has its own root identity key and RGB lifecycle. Its canonical
manifest claim includes at least:

```text
event EntityID
Bitcoin network
authorizing RGB state
signing key identifier, controller role, and music_manifest capability
manifest version
title/name claim
time and place claims
participant EntityIDs and roles
canonical manifest hash
custodian EntityID
event-key signature
signature domain: O2A/v0.1/music-manifest
```

The responsible venue, promoter, or organizer may hold the event key in the
same wallet as its own identity keys. Participant signatures remain separate
attestations over the exact manifest hash. Creating or signing the event does
not prove that it occurred; occurrence and settlement are separate claims.

## Album identity profile

An ALBUM entity has its own root identity key and RGB lifecycle. Its canonical
metadata claim includes at least:

```text
album EntityID
Bitcoin network
authorizing RGB state
signing key identifier, controller role, and music_manifest capability
metadata version
title/name claim
artist and contributor EntityIDs
track-manifest hash
artwork and media commitments where disclosed
custodian EntityID
album-key signature
signature domain: O2A/v0.1/music-manifest
```

The responsible artist or label may hold the album key in the same wallet as
its own identity keys. An album key identifies the work and authorizes its O2A
state; it does not by itself prove copyright ownership, contributor consent,
or authenticity of undisclosed media.

## Custody and recovery

- each EVENT and ALBUM MUST use a distinct identity key;
- each manifest signer MUST be a controller-role key that the event or album's
  named RGB state authorizes for the music-manifest capability;
- manifest signatures MUST use the music-manifest tagged-hash domain and MUST
  NOT validate as ordinary claims, identity transitions, or Bitcoin spends;
- wallet derivation MUST separate entity keys from payment keys and from one
  another;
- custody transfer, controller rotation, recovery-policy change, and revocation
  are RGB state transitions anchored to Bitcoin;
- content changes create new versioned claims and hashes rather than rewriting
  signed history; and
- wallets MUST show the controlling custodian, supporting attestations,
  challenges, and competing name or metadata claims.

## Vector obligations

Canonical bytes are defined in O2A-CANON-1. Executable fixtures must cover:

- event custody: accept an event manifest signed by that event entity's own
  key in `O2A/v0.1/music-manifest`. Reject another entity's key as that
  manifest signature, and reject the manifest hash as proof the event
  occurred; and
- album custody: accept an album manifest signed by that album entity's own
  key in `O2A/v0.1/music-manifest`. Reject another entity's key as that
  manifest signature, and reject the manifest hash as proof of copyright
  ownership.
