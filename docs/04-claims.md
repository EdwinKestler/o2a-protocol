# 04 — Claims

## Definition

A Claim is a signed assertion by an issuer about a subject.

Conceptually:

[
C = H(issuer || subject || predicate || object || context || nonce)
]

[
signature = Sign(SK_{issuer}, C)
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

The predicate vocabulary must be versioned.

## Immutability

A signed claim is historical evidence and must not be silently rewritten.

Corrections use:

- superseding claims;
- revocations;
- challenges;
- newer entity state.

## Self-claims

A self-claim is valid evidence that the entity controller made the assertion. It is not equivalent to independent verification.

```text
SELF-CLAIM ≠ VERIFIED IDENTITY
```
