# 14 — Bitcoin Identity and Discovery Assessment

**Status:** aligned with
[ADR-0005](../adr/0005-bitcoin-rooted-self-custodial-identity.md), 2026-09-23.
This is a design assessment, not an implemented or mainnet-tested stack.

## Conclusion

O2A is a Bitcoin-native, self-custodial identity protocol. The permanent root
is a dedicated BIP340/secp256k1 public key. The identity's lifecycle is RGB
client-side state anchored to Bitcoin. Pubky, Nostr, DNS, HTTPS, social
platforms, catalogs, and APIs help publish, discover, or support claims; none
replaces the root or the validated RGB history.

The public key makes the EntityID unique and owner-controlled. It does not make
a human-readable name unique. A wallet evaluates competing name claims using
signed channel-control proofs, attestations, challenges, chronology, and a
named policy. The core has no first-claim namespace lease.

## Technology roles

| Technology | O2A role | What it does not establish |
| --- | --- | --- |
| Dedicated BIP340 root key | Stable cryptographic root for every artist, venue, promoter, label, event, and album ID. | Ownership of a stage name, legal identity, event occurrence, copyright, or payment. |
| RGB identity contract | Client-side lifecycle for genesis, controllers, recovery rules, custody, and revocation. | Truth of DNS, social, album, or event claims without the referenced evidence. |
| Bitcoin | Orders and confirms anchors and closes single-use seals. | A social oracle or a vote on which claimant is the real artist. |
| Pubky/PKARR | Public Ed25519-key discovery pointer and public profile storage bound to an O2A ID. | The Bitcoin root, standardized O2A recovery, or private consignment storage. |
| Nostr | Optional BIP340-signed public-event transport bound to an O2A ID. | Complete evidence availability, canonical identity recovery, or relay-independent truth. |
| DNS/HTTPS/social | Public channel-control evidence collected through resource-specific challenges. | Permanent control, real-world entitlement to a name, or independent endorsement by itself. |
| Registries/indexers | Searchable projections and conflict discovery. | Authority to create, rotate, recover, or revoke an EntityID. |

## Key hierarchy and separation

One self-custodial wallet may hold many O2A identities, but every entity has a
different root key. The wallet separates:

```text
identity seed
  ├─ ARTIST root key
  │    └─ rotatable claim/admin controller keys
  ├─ ALBUM root key(s)
  ├─ EVENT root key(s)
  ├─ VENUE / PROMOTER / LABEL root keys as applicable
  ├─ Pubky Ed25519 discovery key bindings
  ├─ optional Nostr publication key bindings
  └─ payment and Bitcoin spending keys in separate purposes/domains
```

The final derivation standard is not yet specified. Implementations must not
invent incompatible paths or reuse the same secret across identity, Pubky,
Nostr, RGB seal, or payment signing contexts.

## Public discovery

Pubky provides public-key domains, PKARR records, homeserver selection, and
public application storage. O2A uses it for public profile discovery through a
signed binding:

```text
O2A EntityID
  signs → Pubky Ed25519 public key + purpose + expiry/version
Pubky key
  signs → reciprocal O2A binding and current public-profile location
```

Because Pubky key rotation is not yet standardized, O2A controller state must
authorize replacement of the binding. A lost Pubky key does not replace or
erase the Bitcoin-rooted EntityID. Public Pubky storage never contains seeds,
recovery material, private attestations, or RGB consignments.

Nostr can provide a signed public-event transport using BIP340 keys. O2A still
uses an explicit binding and O2A-specific canonical objects rather than
assuming every Nostr event is an O2A claim. Relay deletion, partial visibility,
and competing replaceable events remain availability concerns.

## Channel-control evidence

A claimant signs a short-lived challenge bound to its EntityID, current RGB
state, resource, purpose, nonce, expiry, and policy. It publishes the derived
token in one of:

- a DNS TXT record;
- a well-known HTTPS path;
- a stable account field or signed post on a recognized platform;
- a bound Pubky public path; or
- a bound Nostr event.

Collectors record and sign exact observations. Wallets can fetch fresh
observations online and verify retained observations offline. Several
collectors reading one source improve observation coverage but do not create
several independent endorsements.

## Competing names

Two O2A IDs may claim the same artist name, venue name, promoter name, album
title, or event name. Wallets show:

- each unique EntityID and current validated RGB state;
- when relevant claims or checkpoints were anchored;
- current and expired channel-control proofs;
- independent endorsements and conflicts;
- challenges, supersession, and revocations; and
- the exact policy and explanation used for the displayed result.

Stronger evidence may produce a stronger policy result. Neither the earliest
claim nor the largest economic balance automatically wins.

## Event and album identities

EVENT and ALBUM use independent root keys held by their responsible custodian.
The event key signs the event-manifest hash; the album key signs album metadata
and track/media commitments. Artists, venues, promoters, labels, and organizers
issue separate attestations. This gives each work or event a stable reference
without collapsing custody, occurrence, participation, and rights into one
signature.

## Required feasibility gates

1. **Cryptographic profile:** freeze EntityID encoding, key derivation,
   canonical bytes, and signature domains.
2. **RGB/Bitcoin profile:** pin compatible dependencies and prove genesis,
   rotation, recovery, revocation, reorg, and missing-consignment behavior on
   regtest.
3. **Wallet portability:** export the same proof package between independent
   clients and reproduce the result offline.
4. **Pubky portability:** publish/read, migrate homeservers, restore backups,
   rotate the binding, and verify retained evidence while Pubky is unavailable.
5. **Nostr portability:** publish through several relays, tolerate partial
   relay availability, and preserve canonical O2A objects outside relays.
6. **Conflict visibility:** demonstrate two IDs claiming the same name without
   accidental merging or first-claim ownership.
7. **Music objects:** demonstrate separate ARTIST, EVENT, and ALBUM keys,
   manifests, custody, recovery, and participant attestations.

## Sources checked

- [BIP340 Schnorr signatures](https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki).
- [Pubky protocol overview](https://pubky.org/explore/pubky-protocol/introduction/),
  [Pubky FAQ](https://pubky.org/faq/), and
  [PKARR](https://github.com/pubky/pkarr).
- [Nostr NIP-01](https://github.com/nostr-protocol/nips/blob/master/01.md).
- [RGB single-use seal/commitment model](https://docs.rgb.info/commitment-layer/commitment-schemes)
  and [client-side validation](https://docs.rgb.info/distributed-computing-concepts/client-side-validation).
- O2A's [code and sibling-project reference map](../codereference.md).
