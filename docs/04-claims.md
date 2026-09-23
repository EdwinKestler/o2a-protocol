# 04 — Claims

## Definition

A Claim is a signed assertion by an EntityID controller that was authorized by
a specific validated RGB identity state.

Conceptually:

[
C = H(issuer || subject || predicate || object || context || nonce)
]

[
signature = BIP340Sign(SK_{authorized-controller}, C)
]

Exact serialization is defined in the claim schema.

## Examples

Possible predicates include:

- official_name
- alias
- controls_domain
- represented_by
- performed_at
- booked_by
- hosted_event
- settlement_endpoint
- controls_social_account
- album_manifest
- event_manifest
- custodied_by

The predicate vocabulary must be versioned.

## Immutability

A signed claim is historical evidence and must not be silently rewritten.

Corrections use:

- superseding claims;
- revocations;
- challenges;
- newer entity state.

## Self-claims

A self-claim is valid evidence that an authorized controller made the
assertion. It is not equivalent to independent verification. For EVENT and
ALBUM, a key-authorized manifest is still a self-claim; artist, venue,
promoter, label, or observer evidence remains separate.

```text
SELF-CLAIM ≠ VERIFIED IDENTITY
```

## Name claims and checkpoints

Human-readable names and titles are non-exclusive claims. Two EntityIDs may
claim the same spelling. Wallets retain both, show their signed channel proofs
and attestations, and may use Bitcoin chronology as one policy input. Earlier
anchoring does not grant permanent ownership of the name.

Ordinary claims remain client-side data. Important claim or package hashes may
be checkpointed on Bitcoin, but the checkpoint proves commitment and order,
not the social truth of the claim.
