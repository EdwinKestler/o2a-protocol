# Discovery-Key Binding Schema — Draft v0.1

## Purpose

A discovery-key binding states that an O2A EntityID authorizes a Pubky or Nostr
publication key for a bounded purpose. It is claim evidence semantically, but
it is a distinct canonical object and MUST NOT be encoded or signed as a
generic `claim`.

## O2A binding object

```json
{
  "protocol_version": "0.1",
  "bitcoin_network": "<bitcoin-network>",
  "object_type": "discovery_key_binding",
  "issuer": "<EntityID>",
  "issuer_state": "<validated-rgb-identity-state-id>",
  "controller_key_id": "<authorized-controller-key-id>",
  "controller_key_purpose": "discovery_binding",
  "adapter": "PUBKY_OR_NOSTR",
  "adapter_key_scheme": "<ed25519-or-bip340>",
  "adapter_public_key": "<canonical-public-key>",
  "binding_purpose": "PUBLIC_PROFILE_PUBLICATION",
  "issued_at": "<explicit-time>",
  "expires_at": "<explicit-time-or-null>",
  "supersedes": null,
  "nonce": "<replay-protection>",
  "signature": {
    "scheme": "bip340-secp256k1",
    "domain": "O2A/v0.1/discovery-binding",
    "value": "<authorized-controller-signature>"
  }
}
```

Conceptually:

```text
binding_payload = Canonical(binding without signature)
binding_message = TaggedHash("O2A/v0.1/discovery-binding", binding_payload)
signature = BIP340Sign(authorized_controller_key, binding_message)
```

## Adapter-side proof

- Pubky MUST provide a reciprocal statement signed by the bound Ed25519 key in
  Pubky's signing context and referring to the immutable O2A binding ID.
- Nostr publication events follow Nostr event-signing rules with the bound
  publication key and MUST refer to the immutable O2A binding ID where the O2A
  profile requires that association.

The adapter-side signature does not replace the O2A binding signature. The O2A
signature does not prove current possession of the adapter private key without
the required reciprocal or publication proof.

## Requirements

- the issuer state and controller purpose MUST authorize discovery bindings;
- a binding signature MUST validate only in the discovery-binding domain and
  MUST be rejected in the generic claim domain and every other O2A domain;
- the Bitcoin network, adapter, key scheme, public key, purpose, expiry,
  supersession reference, and nonce MUST be inside the signed payload;
- unknown adapters, key schemes, purposes, or signature domains MUST fail
  closed;
- rotation creates a new binding that supersedes the old object; it does not
  replace the EntityID root;
- expired, revoked, conflicting, or missing reciprocal proofs MUST remain
  visible to policy; and
- discovery bindings locate signed packages or profiles but do not establish
  identity truth, package validity, or exclusive name ownership.
