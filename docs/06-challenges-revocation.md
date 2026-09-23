# 06 — Challenges and Revocation

## Purpose

A decentralized identity system must represent disagreement without deleting inconvenient history.

## Challenge

A Challenge is a signed assertion disputing an existing claim, attestation, entity relationship, or verification premise.

Suggested fields:

- challenge_id;
- challenger;
- target;
- reason code;
- evidence references;
- issued_at/context;
- signature;
- status.

## Revocation

A Revocation explicitly invalidates or withdraws an earlier evidence object
when the revoking party is authorized to do so.

Suggested fields:

- revocation_id;
- issuer;
- target;
- reason;
- context;
- signature.

## Lifecycle

```text
UNVERIFIED → SELF_ATTESTED → ENDORSED → VERIFIED
                       \
                        → CHALLENGED → DISPUTED → RESOLVED
```

Status is derived from evidence and policy; it is not a mutable label controlled by a registry administrator.

Entity lifecycle status is different: revoking an EntityID, changing its
controllers, or changing its recovery policy requires a valid RGB state
transition anchored to Bitcoin. A registry flag or evidence-level revocation
cannot replace that transition.

## Collision example

If two EntityIDs claim the same stage name, both claims remain visible. Wallets
show their Bitcoin chronology, DNS/social control proofs, attestations,
challenges, and policy results. The earlier claim does not own the spelling by
core-protocol rule.
