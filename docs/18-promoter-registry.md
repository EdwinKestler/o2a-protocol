# 18 — Promoter Registry

**Status:** supporting projection note. The normative identity, evidence, and
verification rules remain in the accepted ADRs and `specs/`.

## Purpose

A promoter has its own BIP340-rooted EntityID and RGB lifecycle. Its public
name, represented artists, venue relationships, and booking relationships are
claims or attestations about that ID. They are not part of the identifier.

The Promoter Registry is a rebuildable view over validated identity histories,
signed evidence, and named-policy results. It is not an authority that creates
or owns promoter identities.

## Suggested projection

- promoter EntityID;
- root public key and validated RGB state reference;
- current controller and lifecycle status;
- public proof-package reference;
- display-name, organization-name, and alternate-name claims;
- DNS, HTTPS, or social channel-control evidence;
- artist representation or booking relationships;
- venue and event relationships;
- supporting and conflicting attestations;
- named verification policy and explained result;
- active challenges and evidence revocations; and
- competing name claims and Bitcoin-established chronology.

## Relationship evidence

A promoter may sign a scoped statement such as:

```text
Promoter P booked Artist A for Event E at Venue V
```

The artist, venue, and event may issue separate attestations over the exact
relationship or manifest reference. Those statements remain independently
signed evidence. A promoter signature proves authorship under its authorized
key and signing domain; by itself it does not prove that the booking was
accepted, the event occurred, or settlement completed.

## Names and authority

Promoter and organization names remain non-exclusive claims. A registry shows
the EntityID, evidence, conflicts, policy, and explanation rather than awarding
permanent ownership of a spelling. No registry row, search rank, follower
count, or payment balance replaces the validated RGB identity history.

## Rebuildability

Deleting the Promoter Registry must not destroy a promoter identity or change
verification of the same bounded inputs. A conforming projection can be rebuilt
from retained public proof packages, validated RGB consignments, Bitcoin proof
data, signed evidence, and the named policy and evaluation context.
