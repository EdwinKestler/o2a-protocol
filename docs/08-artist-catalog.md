# 08 — Artist Catalog

## Role

The Artist Catalog is the first user-visible read model and the recommended Hello-World application.

It is a projection over protocol evidence, not an authority.

## Suggested projection

- entity_id;
- root identity public key and validated RGB state reference;
- display_name;
- aliases;
- profile references;
- claims;
- attestations;
- verification status;
- verification policy;
- related venues;
- related events;
- challenges/revocations.
- competing name claims and Bitcoin chronology;

## Rebuildability requirement

Deleting the catalog database must not destroy artist identity or proof.

A compliant implementation MUST be able to rebuild catalog state from
validated RGB identity consignments, Bitcoin proof data, and signed evidence
packages held outside the catalog.

## Initial experience

A catalog entry should make verification inspectable:

```text
Artist
O2A ID
Status
Policy
Supporting evidence
Conflicting evidence
Proof export
```

Search ranking and recommendation are application concerns and must remain separate from verification.
