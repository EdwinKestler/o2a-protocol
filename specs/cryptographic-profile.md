# Cryptographic Domain-Separation Profile — Draft v0.1

## Status

Draft. This document fixes the requirement for separate signing domains. The
remediated byte grammar and object payloads are specified in
[canonical encoding](canonical-encoding.md). Identity-key derivation,
conformance vectors, and RGB-dependent fixtures remain Phase 0 gates.

## Rule

Every O2A BIP340 signature MUST sign a 32-byte digest produced from an
object-specific tagged hash over the canonical payload. Implementations MUST
NOT accept a signature created for one domain as authorization in another
domain, even when the underlying payload fields happen to be identical.

Conceptually:

```text
message = SHA256(SHA256(tag) || SHA256(tag) || canonical_payload)
signature = BIP340Sign(authorized_key, message)
```

The canonical payload MUST include the protocol version, Bitcoin network,
object type, signer EntityID, authorizing RGB state or the canonical genesis
absence marker, key identifier, key role, authorization capability, and every
domain-specific field. Key role and authorization capability are distinct.
The payload MUST NOT rely on an HTTP route, filename, database table, or other
transport metadata for domain separation.

## Reserved v0.1 domains

The v0.1 profile MUST keep at least these domains distinct:

| Purpose | Reserved textual tag |
| --- | --- |
| Entity genesis | `O2A/v0.1/entity-genesis` |
| Identity state transition | `O2A/v0.1/identity-transition` |
| Recovery authorization | `O2A/v0.1/recovery` |
| Claim | `O2A/v0.1/claim` |
| Attestation | `O2A/v0.1/attestation` |
| Evidence challenge | `O2A/v0.1/challenge` |
| Evidence revocation | `O2A/v0.1/revocation` |
| Channel-control challenge | `O2A/v0.1/control-challenge` |
| Signed online observation | `O2A/v0.1/observation` |
| Discovery-key binding | `O2A/v0.1/discovery-binding` |
| Event or album manifest claim | `O2A/v0.1/music-manifest` |
| Public proof-package manifest | `O2A/v0.1/proof-package` |

The exact UTF-8 tag bytes and canonical payload grammar are specified in
[canonical encoding](canonical-encoding.md). A verifier MUST reject
unknown tags, wrong object types, wrong networks, wrong authorizing states, and
tags or capabilities that do not match the key authorization in that state.

## External signing domains

- Bitcoin transactions use separate spending keys and Bitcoin's transaction
  signature-hash rules. An O2A identity signature is never a Bitcoin spend.
- A Nostr event follows the Nostr event-signing rules and uses a separately
  bound publication key. The O2A binding itself uses the discovery-binding
  domain above.
- Pubky uses its own Ed25519 key. Its reciprocal binding is verified in Pubky's
  signing context, while the O2A side uses the discovery-binding domain.

Key separation remains mandatory even when domain separation would otherwise
make a replay fail. Both protections are required.

## Source basis

BIP340 defines tagged hashing to prevent hashes used in one context from being
reinterpreted in another. O2A applies that mechanism at its protocol-object
boundary; this document does not modify BIP340 itself.
