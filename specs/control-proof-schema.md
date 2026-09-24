# Channel-Control Proof Schema — Draft v0.1

## Purpose

A channel-control proof binds an O2A EntityID and a short-lived challenge to a
DNS, HTTPS, Pubky, Nostr, or supported social resource. It proves publication
control during an observation window; it does not by itself prove entitlement
to an artist, venue, promoter, album, or event name.

## Challenge object

```json
{
  "protocol_version": "0.1",
  "bitcoin_network": "mainnet|testnet|signet|regtest",
  "object_type": "control_challenge",
  "challenge_id": "<derived-canonical-object-id; display-only>",
  "subject": "<EntityID>",
  "subject_state": "<validated-rgb-identity-state-id>",
  "controller_key_id": "<authorized-controller-key-id>",
  "controller_key_role": "controller",
  "authorization_capability": "control_challenge",
  "resource_type": "DNS_TXT",
  "resource": "_o2a-challenge.artist.example",
  "purpose": "NAME_CONTROL",
  "nonce": "<at-least-128-bits-of-randomness>",
  "issued_at": "<explicit-time>",
  "expires_at": "<explicit-time>",
  "policy_hash": "<policy-hash>",
  "signature_domain": "O2A/v0.1/control-challenge",
  "signature": "<authorized-controller-bip340-signature>"
}
```

`challenge_id` is derived from the canonical challenge payload. It is not a
field inside the signed payload and therefore cannot create a hash cycle.

## Observation object

```json
{
  "protocol_version": "0.1",
  "bitcoin_network": "mainnet|testnet|signet|regtest",
  "object_type": "control_observation",
  "challenge_id": "<control-challenge-id>",
  "observer": "<EntityID>",
  "observer_state": "<validated-rgb-identity-state-id>",
  "observer_key_id": "<authorized-observer-key-id>",
  "observer_key_role": "controller",
  "authorization_capability": "observation",
  "method": "DNSSEC_OR_DNS_TXT",
  "observed_resource": "<canonical-resource>",
  "observed_value_hash": "<hash-of-exact-observed-bytes>",
  "observed_at": "<explicit-time>",
  "expires_at": "<explicit-time>",
  "result": "MATCH",
  "transport_evidence": "<portable-evidence-reference>",
  "signature_domain": "O2A/v0.1/observation",
  "signature": "<observer-signature>"
}
```

## Requirements

- challenges MUST be resource-specific, single-use, controller-bound, and
  expire;
- challenge signatures MUST use the control-challenge tagged-hash domain;
- observer signatures MUST use the observation tagged-hash domain;
- the public token MUST be derived from the canonical challenge and MUST never
  be a wallet seed, spending secret, or payment preimage;
- social proofs SHOULD bind stable platform account IDs rather than only mutable
  handles;
- observers MUST sign exact normalized results and failure categories;
- multiple observations of the same publication source MUST remain
  distinguishable from independent endorsements;
- online collection MUST defend against SSRF, DNS rebinding, redirect abuse,
  oversized responses, ambiguous encodings, and stale cached data;
- offline verification MUST validate retained observation objects without
  silently re-fetching the network;
- DNS, HTTPS, and social observations are channel-control evidence and MUST
  carry an expiry input;
- an expired observation fails the control check; and
- policies MUST report missing, expired, conflicting, or unverifiable evidence
  rather than infer a positive result.

## Vector obligations

Canonical bytes are defined in O2A-CANON-1. Executable fixtures must cover the
expired-control-proof case:

- accept a DNS, HTTPS, or social observation whose expiry input is present and
  whose evaluation time is inside that window; and
- reject an expired observation. It fails the control check and MUST NOT be
  treated as current channel control.
