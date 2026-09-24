# 04 — Claims

## Definition

A Claim is a signed assertion by an EntityID controller that was authorized by
a specific validated RGB identity state.

Conceptually:

```text
claim_payload = Canonical(claim without signature)
claim_message = TaggedHash("O2A/v0.1/claim", claim_payload)
signature = BIP340Sign(authorized_controller_key, claim_message)
```

The canonical payload includes the protocol version, Bitcoin network, object
type, issuer EntityID, authorizing RGB state, key identifier, key role,
authorization capability, and the domain-specific claim fields. Exact
serialization is defined in the
[claim schema](../specs/claim-schema.md) and
[cryptographic profile](../specs/cryptographic-profile.md). A plain untagged
hash is not a valid O2A claim-signing message.

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
