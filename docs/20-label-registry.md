# 20 — Label Registry

**Status:** supporting projection note. The normative identity, claim,
attestation, proof-package, and verification rules remain in the accepted ADRs
and `specs/`.

## Purpose

A label has its own BIP340-rooted EntityID and RGB lifecycle. It remains
distinct from its parent organization, represented artists, released albums,
distributors, and payment accounts. Its public and legal names, organizational
relationships, catalog associations, and asserted rights are claims or
attestations about that ID rather than parts of the identifier.

The Label Registry is a rebuildable projection over validated identity
histories, signed evidence, and named-policy results. It is not an authority
that creates a label identity or decides ownership of music rights.

## Suggested projection

- label EntityID;
- root public key and validated RGB state reference;
- current controller and lifecycle status;
- public proof-package reference;
- display-name, legal-name, imprint, and alternate-name claims;
- DNS, HTTPS, or social channel-control evidence;
- parent-organization, distributor, and imprint relationships;
- artist representation and album-release relationships;
- scoped rights, license, or territory claims where disclosed;
- supporting and conflicting attestations;
- named verification policy and explained result;
- active challenges and evidence revocations; and
- competing name or relationship claims with Bitcoin-established chronology.

## Relationship evidence

A label may sign scoped statements such as:

```text
Label L released Album B
Label L represents Artist A for Purpose P during Interval T
```

The artist, album custodian, distributor, or parent organization may issue
separate attestations over the exact relationship, purpose, interval, or
manifest reference. Those statements remain independently signed evidence. A
label signature proves authorship under its authorized key and signing domain;
by itself it does not prove the counterparty agreed, that a release occurred,
or that the label owns copyright.

## Organization and rights boundary

A label brand, imprint, company, and parent organization may be different
entities. The registry preserves their identifiers and scoped relationships
instead of silently merging them. Rights, licenses, royalties, territories,
and distribution terms require explicit versioned claims or downstream
contracts; controlling a label key does not create those rights.

## Rebuildability

Deleting the Label Registry must not destroy the label identity or change
verification of the same bounded inputs. A conforming projection can be rebuilt
from retained public proof packages, validated RGB consignments, Bitcoin proof
data, signed evidence, and the named policy and evaluation context.
