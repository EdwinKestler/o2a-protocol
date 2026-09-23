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
  "object_type": "control_challenge",
  "challenge_id": "<canonical-object-id>",
  "subject": "<EntityID>",
  "subject_state": "<validated-rgb-identity-state-id>",
  "resource_type": "DNS_TXT",
  "resource": "_o2a-challenge.artist.example",
  "purpose": "NAME_CONTROL",
  "nonce": "<at-least-128-bits-of-randomness>",
  "issued_at": "<explicit-time>",
  "expires_at": "<explicit-time>",
  "policy_hash": "<policy-hash>",
  "signature": "<authorized-controller-bip340-signature>"
}
```

## Observation object

```json
{
  "protocol_version": "0.1",
  "object_type": "control_observation",
  "challenge_id": "<control-challenge-id>",
  "observer": "<EntityID-or-versioned-observer-key>",
  "method": "DNSSEC_OR_DNS_TXT",
  "observed_resource": "<canonical-resource>",
  "observed_value_hash": "<hash-of-exact-observed-bytes>",
  "observed_at": "<explicit-time>",
  "expires_at": "<explicit-time>",
  "result": "MATCH",
  "transport_evidence": "<portable-evidence-reference>",
  "signature": "<observer-signature>"
}
```

## Requirements

- challenges MUST be resource-specific, single-use, controller-bound, and
  expire;
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
  silently re-fetching the network; and
- policies MUST report missing, expired, conflicting, or unverifiable evidence
  rather than infer a positive result.
