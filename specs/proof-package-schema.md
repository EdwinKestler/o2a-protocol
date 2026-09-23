# Public Identity Proof Package — Draft v0.1

## Purpose

A public O2A identity is independently verifiable only when another wallet can
obtain the client-side data needed to validate it. A Bitcoin transaction or
public key alone is insufficient. This profile defines a content-addressed,
portable package that a stranger wallet can fetch or receive directly.

The package deliberately discloses the public identity-history shard selected
for the O2A public-identity profile. It does not make every wallet consignment,
private attestation, or application record public.

## Conceptual manifest

```json
{
  "protocol_version": "0.1",
  "bitcoin_network": "<bitcoin-network>",
  "object_type": "public_identity_proof_package",
  "package_id": "<hash-of-canonical-package-manifest>",
  "subject": "<EntityID>",
  "subject_state": "<validated-rgb-identity-state-id>",
  "identity_profile": "o2a-bitcoin-rgb-v0.1",
  "rgb_contract": "<contract-and-schema-identifiers>",
  "identity_history": "<public-identity-consignment-reference>",
  "bitcoin_proofs": ["<anchor-witness-and-header-proof-reference>"],
  "evidence": ["<included-object-or-content-addressed-reference>"],
  "policy": "<policy-id-and-hash>",
  "evaluation_context": "<explicit-context>",
  "previous_package": null,
  "publisher": "<EntityID>",
  "publisher_state": "<authorizing-rgb-state-id>",
  "signing_key": "<authorized-controller-key-id>",
  "signing_key_purpose": "proof_package_publisher",
  "signature_domain": "O2A/v0.1/proof-package",
  "signature": "<authorized-controller-bip340-signature>"
}
```

## Package identity and signature

`package_id` is the hash of the versioned canonical manifest with
`package_id`, `signature`, and transport-only locator metadata omitted. The
publisher signs that same digest in the proof-package signing domain. The
declared `signing_key` MUST be authorized for the declared purpose by
`publisher_state` on the declared `bitcoin_network`. The final canonical
encoding and hash algorithm MUST be frozen with positive, mutation, truncation,
wrong-network, wrong-key-purpose, and cross-domain test vectors before
implementation.

Every content-addressed reference contributes its media type, byte length, and
content hash to the signed manifest. Implementations MUST reject ambiguous
encodings, duplicate logical fields, hash cycles, and a package whose declared
ID does not match its canonical manifest.

## Minimum public identity material

The package, or content-addressed objects it references, MUST provide enough
data for a conforming wallet to validate:

- the EntityID derivation from network, profile, and immutable root public key;
- the O2A RGB contract/schema and identity history from genesis to
  `subject_state`;
- each relevant seal, witness, commitment, anchor, confirmation, and stated
  reorg assumption;
- current controller, recovery-policy commitment, and lifecycle status;
- signatures and signing domains on included public claims and attestations;
  and
- the exact policy, evidence boundary, and evaluation context for any included
  verification result.

Missing required history, an unavailable referenced object, or a hash mismatch
MUST produce an incomplete or invalid result. A verifier MUST NOT reconstruct
missing client-side state from a transaction ID, registry row, or profile badge.

## Publication and retrieval

The owner wallet MUST be able to export the package directly to another wallet.
For public discovery, an authorized O2A claim SHOULD advertise the package ID,
media type, size, expiry or supersession information, and one or more locators.
Locators may use HTTPS, a bound Pubky profile, a Nostr event containing a
content-addressed pointer, or another explicitly versioned transport.

The package ID, not a mutable URL, is the integrity reference. Wallets SHOULD
replicate public packages across at least two independently administered
retrieval paths and MUST verify the package ID after every fetch. No transport,
indexer, relay, or homeserver becomes identity authority by hosting the bytes.

Every update creates a new immutable package with `previous_package` pointing
to the earlier package where applicable. Removing a locator does not erase a
package already retained by another wallet.

## Privacy boundary

Public packages MUST NOT contain:

- seeds, private keys, recovery secrets, or Bitcoin spending descriptors;
- private RGB state unrelated to the public identity-history shard;
- private attestations or undisclosed evidence; or
- access tokens, private API responses, or unnecessary personal data.

The package manifest MUST identify omitted evidence and disclosure class where
the policy needs to distinguish absent data from intentionally private data.
Selective disclosure and encrypted peer-to-peer packages may extend this
profile, but they cannot be treated as public availability.
