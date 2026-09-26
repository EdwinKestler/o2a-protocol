# Public Identity Proof Package — Draft v0.1

## Status

Draft remediation profile. Publication locators, the privacy boundary,
omission rules, and offline checks are specified below. The exact manifest,
signed-envelope, `manifest_id`, and `package_id` bytes are defined in
[canonical encoding](canonical-encoding.md). Executable package vectors remain
a Phase 0 gate.

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
  "manifest_id": "<hash-of-canonical-manifest-payload>",
  "subject": "<EntityID>",
  "subject_state": "<validated-rgb-identity-state-id>",
  "identity_profile": "o2a-bitcoin-rgb-v0.1",
  "rgb_contract": "<contract-and-schema-identifiers>",
  "identity_history": "<public-identity-consignment-reference>",
  "bitcoin_proofs": ["<anchor-witness-and-header-proof-reference>"],
  "evidence": ["<included-object-or-content-addressed-reference>"],
  "omitted": [{
    "object_id": "<omitted-object-id>",
    "disclosure_class": "PRIVATE|WITHHELD|UNAVAILABLE",
    "reason": "<versioned-reason>"
  }],
  "policy": "<policy-id-and-hash>",
  "evaluation_context": "<explicit-context>",
  "previous_manifest": null,
  "publisher": "<EntityID>",
  "publisher_state": "<authorizing-rgb-state-id>",
  "signing_key": "<authorized-controller-key-id>",
  "signing_key_role": "controller",
  "authorization_capability": "proof_package_publication",
  "signature_domain": "O2A/v0.1/proof-package",
  "signature": "<authorized-controller-bip340-signature>"
}
```

`package_id` and locators are advertised outside the signed envelope. They are
not fields of the manifest.

## Package identity and signature

The canonical manifest payload excludes `manifest_id`, signature,
`package_id`, and locators. Its ordinary SHA-256 is `manifest_id`. The BIP340
message is the proof-package tagged hash of
`manifest_payload || manifest_id`. The transmitted signed envelope is:

```text
manifest_payload || manifest_id || signature64
```

`package_id` is SHA-256 of that complete signed envelope. This construction is
non-circular: the signature commits to the manifest and `manifest_id`, while
`package_id` content-addresses the resulting signed bytes.

Locators and the externally advertised `package_id` are not signed. The exact
signed envelope bytes are the input to `package_id`. A locator is not evidence
that the object is valid.

The declared `signing_key`, controller role, and proof-package-publication
capability MUST be authorized by `publisher_state` on the declared network. A
verifier MUST recompute both identifiers and validate the package signature
before accepting any included result.

A declared `manifest_id` or advertised `package_id` that is not its defined
digest is invalid. Implementations
MUST reject ambiguous encodings, duplicate logical fields, hash cycles, and a
package whose identifiers do not match its canonical bytes.

Every content-addressed reference contributes its media type, byte length, and
content hash to the signed manifest.

## Minimum public identity material

The package, or content-addressed objects it references, MUST provide enough
data for a conforming wallet to validate:

- the EntityID derivation from network, profile, and immutable root public key;
- the O2A RGB contract/schema and identity history from genesis to
  `subject_state`;
- each transaction that created a seal output named by the history, the output
  index and scriptPubKey, and the inclusion/header proof needed to place that
  creating transaction in the named best chain;
- each relevant seal-spending witness, commitment, anchor, confirmation, and
  stated reorg assumption;
- current controller, recovery-policy commitment, and lifecycle status;
- the publisher state and capability-authorized signing key needed to verify the
  proof-package signature in `O2A/v0.1/proof-package`;
- signatures and signing domains on included public claims and attestations;
  and
- the exact policy, evidence boundary, and evaluation context for any included
  verification result.

The manifest names omitted objects. A missing named object makes evaluation
incomplete. A named omission records an intentional absence; the missing
object is one the manifest includes or references and whose bytes are absent.
A hash mismatch is invalid. A verifier MUST NOT reconstruct missing
client-side state from a transaction ID, registry row, profile badge, or
discovery binding.

For each seal-creating transaction, the verifier recomputes the expected P2TR
scriptPubKey from the seal policy committed by the state that names the
outpoint. A missing creating transaction or proof makes evaluation incomplete;
a present output whose script does not match makes the identity history
invalid. The revealed tapleaf of a seal-spending anchor is not an O2A
operation-authorization input; O2A signatures and capabilities are verified
separately.

## Publication and retrieval

This profile has three locators:

1. a local file package, whose bytes are already retained by the verifier;
2. a direct wallet transfer, in which the owner wallet gives those bytes to
   another wallet; and
3. an HTTPS URL whose response body is the complete signed envelope and whose
   SHA-256 MUST equal the advertised `package_id`. For a referenced object, the
   response body must match the content hash named by its content reference.

These are the only locators. Locators are not signed and are not evidence that
the object is valid. A body that matches the content hash shows only that the
fetched bytes are the addressed bytes. An HTTPS body that does not match is a
failed retrieval of that object, not proof that a package already retained
from another locator is invalid.

Pubky and Nostr are discovery bindings, not the history store. A binding may
advertise `package_id` and one of the three locators. A Pubky profile, a Nostr
event or relay, a homeserver, a registry, or any other discovery host does not
hold identity history and does not become authority by advertising a pointer.
Identity history is the package and the objects the package includes.

The owner wallet MUST be able to export the package by direct wallet transfer.
For public discovery, an authorized O2A claim SHOULD advertise the package ID,
media type, size, expiry or supersession information, and one or more of these
locators.

The package ID, not a mutable URL, is the integrity reference. Wallets SHOULD
replicate public packages across at least two independently administered
retrieval paths and MUST verify the content hash after every fetch. No
transport, indexer, relay, or homeserver becomes identity authority by hosting
the bytes.

Every update creates a new immutable package whose `previous_manifest` points
to the earlier manifest where applicable. Removing a locator does not erase a
package already retained by another wallet.

## Offline checks

A verifier holding a local file package, or the bytes received by direct
wallet transfer, MUST recompute `package_id`, parse the signed envelope,
recompute `manifest_id`, and check the
`O2A/v0.1/proof-package` signature without a network request. After an HTTPS
body is retained and matched to its content hash, the same checks apply
offline.

Offline checks use only the retained bytes, the manifest, and the rules in
[canonical encoding](canonical-encoding.md). They MUST NOT call Pubky, Nostr,
a registry, an indexer, or an HTTPS host to supply history the package does
not contain. A locator is not a substitute for a missing object.

## Privacy boundary

Public packages exclude Bitcoin spending descriptors. Public packages MUST NOT
contain:

- seeds, private keys, recovery secrets, or Bitcoin spending descriptors;
- private RGB state unrelated to the public identity-history shard;
- private attestations or undisclosed evidence; or
- access tokens, private API responses, or unnecessary personal data.

The manifest names omitted objects, including a disclosure class where the
policy must distinguish absent data from intentionally private data. A named
omission is not included history. A missing named object makes evaluation
incomplete. Selective disclosure and encrypted peer-to-peer packages may
extend this profile, but they cannot be treated as public availability.
