# 03 — Entity Identity

## EntityID

EntityID is the canonical, self-custodied subject identifier. It is
deterministically rooted in:

```text
O2A protocol profile + Bitcoin network + dedicated BIP340 root public key
```

O2A-CANON-1 specifies the candidate EntityID bytes. A human-readable display
encoding and the seed-to-root derivation allocation remain open. The root key
is an identity key, never a Bitcoin spending key. Each entity uses a different
root key even when one wallet holds several of them.

Initial entity types are:

- PERSON
- ARTIST
- BAND
- VENUE
- PROMOTER
- LABEL
- ORGANIZATION
- EVENT
- ALBUM

Domain categories are entity types, not incompatible identifier systems.

## RGB identity lifecycle

The root key signs genesis. Genesis creates the first RGB identity state and
anchors it to a Bitcoin single-use seal. Later valid transitions can change:

- operational controller keys and their allowed capabilities;
- the committed recovery policy;
- custodian or representative bindings;
- optional profile commitments; and
- ACTIVE or REVOKED lifecycle status.

Every transition references the previous valid state, closes the expected
seal, commits the successor state, and is authorized by the previous state.
Wallets validate the complete supplied client-side history against Bitcoin.
The newest profile document or database row is never sufficient.

## Root and controller keys

The root public key gives the EntityID its stable cryptographic root and signs
genesis. Day-to-day controller keys sign claims, attestations, and
administrative transitions according to explicit capabilities in the current
RGB state. Key role and authorization capability are separate. The root is not
an unconditional forever-controller unless the current state says so.

The root public key never changes: it is part of the EntityID derivation.
Replacing it creates a new EntityID. Recovery rotates controller authority
under an earlier committed policy while preserving that immutable root.

Operational-key rotation does not change EntityID. Historical signatures are
checked against the state that authorized their key at issuance time. Losing a
working key therefore need not erase identity.

## Recovery

Recovery without a current controller is valid only when an earlier valid RGB
state committed the applicable recovery rule. A later collection of social
attestations can support recognition of a successor identity, but cannot
silently invent authorization for the existing EntityID.

After genesis, the normal profile should remove unilateral routine control from
the root. Any continuing root authority must be explicit in current RGB state.
The specification must define root compromise, recovery thresholds, delay,
cancellation, stale-state, fork, and reorg behavior before implementation.

If a stolen root or controller remains authorized and produces the next valid
transition first, a wallet follows the valid RGB/Bitcoin history. Social
attestations cannot reverse it. Recovery can continue only through a path that
the applicable prior state already authorized. Otherwise the participant must
create a new EntityID and publish explicit successor and compromise evidence;
the protocol does not pretend the old EntityID was cryptographically recovered.

## Event and album identities

EVENT and ALBUM each have an independent root public key and RGB lifecycle.
The responsible venue, promoter, organizer, artist, or label can hold those
keys in the same wallet as its own identity, using separated derivation paths.

An event-key signature authorizes a canonical event-manifest claim. An
album-key signature authorizes canonical album metadata and content-hash
claims. Participant attestations remain separate. The keys do not alone prove
that an event occurred, that audio is authentic, or that the custodian owns
copyright.

## Human-facing names

An O2A ID is unique because its root key is unique. Artist names, venue names,
promoter names, album titles, and event names are non-exclusive claims.
Wallets show their evidence, Bitcoin chronology, conflicts, challenges, and
policy result. The core protocol does not award permanent ownership of a
spelling to its first claimant.

## Discovery and payment bindings

Pubky Ed25519 and Nostr publication keys use capability-authorized
[`discovery_key_binding`](../specs/discovery-binding-schema.md) objects.
Those objects are claim evidence in the policy model, but have their own
canonical type and `O2A/v0.1/discovery-binding` signature domain. DNS names,
social accounts, Lightning offers, and public payment endpoints use their
applicable capability-authorized claim or proof types. All can expire, rotate, or be
revoked without replacing the root identity when the validated RGB state
authorizes the controller that signs the update.

```text
O2A ID (product-facing encoding)
        ↓
EntityID (BIP340-rooted protocol identifier)
        ↓
validated RGB state (current controllers and recovery rules)
```
