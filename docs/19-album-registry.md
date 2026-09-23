# 19 — Album Registry

**Status:** supporting projection note. The normative album identity and
manifest rules remain in the accepted ADRs and
[music-object profile](../specs/music-object-schema.md).

## Purpose

An album is a key-rooted O2A entity with its own EntityID and RGB lifecycle. It
is distinct from the artist, label, or other custodian that holds its keys. The
responsible artist or label may keep the album keys in the same self-custodial
wallet as its other identities while preserving separate derivation and
authorization purposes.

The Album Registry is a rebuildable projection over validated album identity
history, signed metadata and manifest claims, participant attestations, and
named-policy results. It is not the source of album identity or rights.

## Suggested projection

- album EntityID;
- root public key, custodian, and validated RGB state reference;
- current controller, recovery policy, and lifecycle status;
- public proof-package reference;
- title and alternate-title claims;
- canonical metadata version and manifest hash;
- track-manifest and disclosed media or artwork commitments;
- artist, contributor, producer, and label EntityID relationships;
- supporting and conflicting attestations;
- named verification policy and explained result;
- active challenges and evidence revocations; and
- competing title or metadata claims with Bitcoin-established chronology.

## Manifest and participant evidence

A purpose-authorized album key signs the canonical metadata and track-manifest
commitments in the music-manifest signing domain. Artists, contributors,
labels, and other participants issue separate attestations over exact immutable
references. A new metadata or track version creates a new signed claim and
content hash rather than rewriting earlier evidence.

The album signature establishes authorship and integrity for the signed O2A
object. It does not by itself prove copyright ownership, contributor consent,
recording authenticity, or the truth of undisclosed metadata.

## Custody and rights boundary

Controller rotation, authorized recovery, custody transfer, and entity
revocation follow the album's validated RGB lifecycle. Rights, licenses,
royalties, payments, and distribution terms are separate claims or downstream
application contracts; the registry must not infer them from custody of the
album key.

## Rebuildability

Deleting the Album Registry must not destroy the album identity, manifests, or
evidence. A conforming projection can be rebuilt from retained public proof
packages, validated RGB consignments, Bitcoin proof data, signed evidence, and
the named policy and evaluation context.
