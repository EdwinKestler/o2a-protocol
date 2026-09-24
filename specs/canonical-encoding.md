# Canonical Encoding — O2A-CANON-1

## Status

Draft remediation profile for v0.1. The byte grammar and object payloads below
replace the incomplete first draft. They do not adopt an RGB implementation,
freeze RGB program bytes, or close Phase 0. The identity derivation purpose is
also still provisional pending an interoperable allocation decision.

This document defines the only bytes that v0.1 signs, hashes, or commits. JSON,
YAML, database rows, URLs, and UI models are views and MUST NOT be signed as
substitutes for these bytes.

## Primitive grammar

- `u8`, `u16`, `u32`, and `u64` are unsigned little-endian integers of exactly
  1, 2, 4, and 8 bytes.
- `hash32`, `entity_id`, `state_id`, and `key_id` are exactly 32 bytes.
- `xonly` is exactly 32 bytes and MUST parse as a BIP340 x-only public key.
- `signature64` is exactly 64 bytes and MUST pass BIP340 verification.
- `bool` is one `u8`: `0` is false and `1` is true. Other values are invalid.
- `bytes` is `u32(length) || value`. Length MUST be at most 1,048,576 bytes.
- `text` is a `bytes` value that is well-formed UTF-8, contains no NUL, and is
  at most 4,096 bytes. Its bytes are preserved exactly; verifiers MUST NOT
  apply Unicode normalization while verifying a signature.
- `option<T>` is `u8(0)` for absent or `u8(1) || T` for present.
- `list<T>` is `u32(count) || item[0] || ... || item[count-1]`, with at most
  4,096 items. A schema that calls a list a set requires strict bytewise sort
  order and rejects duplicates.
- `unix_time` is `u64` seconds since 1970-01-01T00:00:00Z. Evaluation uses the
  explicit time in the evaluation context, never an implicit system clock.
- `outpoint` is the transaction hash's 32 serialized bytes followed by its
  `u32` output index. Display-endian hexadecimal is not canonical input.

Every payload is exactly the stated concatenation. Truncation, trailing bytes,
unknown enum values, an invalid option marker, excessive lengths or counts,
and duplicate entries in a set are invalid. Unknown versions have no extension
semantics in O2A-CANON-1.

## Tagged hashes

```text
tag_hash = SHA256(utf8(tag))
TaggedHash(tag, payload) = SHA256(tag_hash || tag_hash || payload)
```

The tag is exact UTF-8 with no length prefix or trailing NUL. The BIP340
message is the 32-byte tagged hash. The same payload under two tags is two
messages; a signature valid in one domain MUST be rejected in every other
domain.

## Version, network, and identifiers

Protocol version is `u16(1)`. Network is one `u8`:

| Value | Network | BIP32 coin type |
| ---: | --- | --- |
| 0 | mainnet | `0'` |
| 1 | testnet | `1'` |
| 2 | testnet4 | `1'` |
| 3 | signet | `1'` |
| 4 | regtest | `1'` |

```text
EntityID = TaggedHash(
  "O2A/v0.1/entity-id",
  u16(1) || network || root_xonly
)

key_id = TaggedHash(
  "O2A/v0.1/key-id",
  key_role || xonly
)
```

The EntityID preimage is 35 bytes. Controller rotation, recovery, custody
transfer, and revocation do not change it. A different root or network produces
a different EntityID.

### Key roles

Key role describes what kind of key it is. It is not authorization.

| `u8` | Role |
| ---: | --- |
| 0 | root identity |
| 1 | controller |
| 2 | recovery |
| 3 | Nostr publication |

Payment and Pubky keys have no O2A key role and no O2A `key_id`. Pubky keys are
independent Ed25519 keys. Payment keys MUST NOT sign O2A objects.

### Authorization capabilities

Capability describes what the authorizing RGB state permits a key to do. It is
encoded separately from key role.

| `u16` | Capability |
| ---: | --- |
| 1 | entity genesis |
| 2 | identity transition |
| 3 | recovery |
| 4 | claim |
| 5 | attestation |
| 6 | challenge |
| 7 | evidence revocation |
| 8 | control challenge |
| 9 | observation |
| 10 | discovery binding |
| 11 | music manifest |
| 12 | proof-package publication |

A key may hold multiple capabilities in an authorizing state. Possessing the
right key role does not imply a capability. A verifier MUST confirm both.

## Derivation status

Identity key derivation remains a Phase 0 gate under the
[allocation note](../docs/phase0-derivation-allocation.md). The previous draft's
`m/827'/coin'/account'/role'/index'` hierarchy is a proposal, not a registered
interoperability allocation, and MUST NOT be presented as frozen. Its intended
shape is retained for allocation review:

```text
m/purpose'/coin'/account'/0'/0'       root
m/purpose'/coin'/account'/1'/index'   controller
m/purpose'/coin'/account'/2'/index'   recovery
m/purpose'/coin'/account'/3'/index'   Nostr publication
```

Payment keys use BIP86 `m/86'/coin'/account'/0/index`. The identity `purpose'`
will be frozen only after an allocation decision prevents collision with other
BIP43 applications. Existing `827'` fixtures are retained as provisional test
data and MUST be regenerated after that decision.

## Object types and domains

| `u16` | Object | Required tag | Required capability |
| ---: | --- | --- | ---: |
| 1 | entity genesis | `O2A/v0.1/entity-genesis` | 1 |
| 2 | identity transition | `O2A/v0.1/identity-transition` | 2 |
| 3 | recovery authorization | `O2A/v0.1/recovery` | 3 |
| 4 | claim | `O2A/v0.1/claim` | 4 |
| 5 | attestation | `O2A/v0.1/attestation` | 5 |
| 6 | challenge | `O2A/v0.1/challenge` | 6 |
| 7 | evidence revocation | `O2A/v0.1/revocation` | 7 |
| 8 | control challenge | `O2A/v0.1/control-challenge` | 8 |
| 9 | observation | `O2A/v0.1/observation` | 9 |
| 10 | discovery binding | `O2A/v0.1/discovery-binding` | 10 |
| 11 | music manifest | `O2A/v0.1/music-manifest` | 11 |
| 12 | proof-package manifest | `O2A/v0.1/proof-package` | 12 |

Unknown values and any object/domain/capability mismatch are invalid.

## Common signed header

Every signed payload starts with:

```text
version || network || object_type || signer_entity || authorizing_state
        || signing_key_id || key_role || capability
```

| Field | Encoding |
| --- | --- |
| version | `u16(1)` |
| network | network `u8` |
| object_type | object-type `u16` |
| signer_entity | `entity_id` |
| authorizing_state | `option<state_id>` |
| signing_key_id | `key_id` |
| key_role | key-role `u8` |
| capability | capability `u16` |

Genesis MUST use an absent `authorizing_state`, the root role, and capability
1. Every other object MUST name the validated prior or current authorizing
state. The header's object type, capability, key role, and domain must be
authorized together; none can be inferred from a filename or API route.

## Shared compound values

### Controller

```text
key_id || xonly || key_role || list<u16>(capabilities)
```

The role MUST be controller. Capabilities are a nonempty strictly increasing
set. Controllers are a nonempty set sorted by `key_id`.

### Recovery policy

```text
policy_version || policy_sequence || threshold || recovery_key_ids
               || delay_blocks || cancellation_rule
```

`policy_version` is `u16(1)`. `policy_sequence` is `u64`. `threshold` is a
nonzero `u16` no larger than the count of `recovery_key_ids`. Recovery key IDs
are a nonempty strictly sorted set of at most 16 entries. `delay_blocks` is a
`u32`. `cancellation_rule` is `u8(1)`, meaning a currently authorized
controller may cancel a pending recovery by confirming a valid competing spend
of the prior seal before the recovery's `not_before_height`. Other values are
invalid in v0.1.

```text
recovery_policy_hash = TaggedHash(
  "O2A/v0.1/recovery-policy",
  canonical recovery policy
)
```

### Resulting identity state

```text
sequence || previous_state || previous_seal || next_seal || controllers
         || recovery_policy || custodian || lifecycle_status
         || custody_acceptance || profile_commitment
```

`sequence` is `u64`. `previous_state` is `option<state_id>` and
`previous_seal` is `option<outpoint>`; both are absent only at genesis.
`next_seal` is an `outpoint`. `controllers` is the sorted controller set.
`custodian` is `option<entity_id>`. Lifecycle status is `u8(1)` ACTIVE or
`u8(2)` REVOKED. `custody_acceptance` and `profile_commitment` are
`option<hash32>`. Custody transfer requires the acceptance-claim object ID;
other operations require it to be absent.

### Content reference

```text
media_type || byte_length || content_hash
```

`media_type` is `text` of at most 127 bytes, `byte_length` is `u64`, and
`content_hash` is `hash32`. Content-reference sets sort first by content hash,
then media type, then byte length.

## Object payloads

The signature is never part of its signed payload.

### 1. Entity genesis

```text
common_header || entity_type || root_xonly || resulting_state
```

Entity type is `u16`: 1 PERSON, 2 ARTIST, 3 BAND, 4 VENUE, 5 PROMOTER,
6 LABEL, 7 ORGANIZATION, 8 EVENT, or 9 ALBUM. The resulting state has sequence
0 and an absent previous state. `signer_entity` MUST equal the EntityID derived
from `root_xonly`, and `signing_key_id` MUST identify that root.

### 2. Identity transition

```text
common_header || operation || resulting_state
```

Operation is `u8`: 1 controller rotation, 2 recovery-policy change, 4 custody
transfer, or 5 revocation. Operation 3 is reserved for recovery authorization
and is invalid in this domain. The resulting sequence MUST equal the previous
state sequence plus one. Revocation MUST produce lifecycle status REVOKED.

### 3. Recovery authorization

```text
common_header || operation || policy_hash || not_before_height
              || resulting_state
```

Operation MUST be `u8(3)`. `policy_hash` is the recovery-policy hash committed
by the prior state. `not_before_height` is `u32` and MUST equal the prior
state's confirmed anchor height plus that policy's `delay_blocks`. Each
recovery signer signs its own payload header over the same recovery body.
Recovery authorization entries are sorted by `signing_key_id`, contain no
duplicate keys, and must meet the committed threshold.

### 4. Claim

```text
common_header || subject || predicate || object || context || nonce
              || supersedes || checkpoint
```

`subject` is an `entity_id`; `predicate` is `text`; `object` is `bytes`;
`context`, `supersedes`, and `checkpoint` are `option<hash32>`; `nonce` is
`hash32`.

### 5. Attestation

```text
common_header || subject_kind || subject || predicate || object
              || evidence || context || nonce
```

`subject_kind` is `u8(1)` EntityID or `u8(2)` object ID. `subject` is `hash32`.
`predicate` is `text`; `object` is `bytes`; `evidence` is a strictly sorted set
of `hash32`; `context` is `option<hash32>`; `nonce` is `hash32`.

### 6. Challenge

```text
common_header || target || reason || evidence || context || nonce
```

`target` is `hash32`; `reason` is versioned `text`; `evidence` is a strictly
sorted set of `hash32`; `context` is `option<hash32>`; `nonce` is `hash32`.

### 7. Evidence revocation

```text
common_header || target || reason || context || nonce
```

`target` is `hash32`; `reason` is versioned `text`; `context` is
`option<hash32>`; `nonce` is `hash32`. This object cannot revoke an EntityID.

### 8. Control challenge

```text
common_header || resource_type || resource || control_purpose || nonce
              || issued_at || expires_at || policy_hash
```

`resource_type` is `u8`: 1 DNS TXT, 2 HTTPS, 3 social account, 4 Pubky, or
5 Nostr. `resource` is `text`; `control_purpose` is `u16(1)` NAME_CONTROL;
`nonce` is `hash32`; times are `unix_time`; `policy_hash` is `hash32`.
`expires_at` MUST be later than `issued_at`. The challenge ID is the tagged
hash of this payload and is not a self-referential payload field.

### 9. Observation

```text
common_header || challenge_id || method || observed_resource
              || observed_value_hash || observed_at || expires_at || result
              || transport_evidence
```

`challenge_id` is `hash32`; method is `u8`: 1 DNS TXT, 2 DNSSEC, 3 HTTPS,
4 social API/page, 5 Pubky, or 6 Nostr. `observed_resource` is `text`;
`observed_value_hash` is `hash32`; times are `unix_time`; result is `u8`:
1 MATCH, 2 MISMATCH, 3 UNAVAILABLE, or 4 ERROR. `transport_evidence` is
`option<content reference>`. Expiry MUST be later than observation time.

### 10. Discovery binding

```text
common_header || adapter || adapter_key_scheme || adapter_public_key
              || binding_purpose || issued_at || expires_at || supersedes
              || nonce
```

Adapter is `u8(1)` PUBKY or `u8(2)` NOSTR. Key scheme is `u8(1)` ED25519 or
`u8(2)` BIP340. PUBKY requires ED25519; NOSTR requires BIP340.
`adapter_public_key` is a 32-byte `bytes` value. Binding purpose is `u16(1)`
PUBLIC_PROFILE_PUBLICATION. `expires_at` is `option<unix_time>`;
`supersedes` is `option<hash32>`; `nonce` is `hash32`.

### 11. Music manifest

```text
common_header || manifest_kind || manifest_version || title_claim
              || temporal_claims || place_claims || participants
              || track_manifest || content_commitments || custodian
              || previous_manifest
```

Manifest kind is `u8(1)` EVENT or `u8(2)` ALBUM; `manifest_version` is `u32`;
`title_claim` is `hash32`; temporal and place claims are sorted sets of
`hash32`. Each participant is `entity_id || role`, where role is versioned
`text`; participants sort by EntityID then role. `track_manifest` is
`option<hash32>` and MUST be present for ALBUM. `content_commitments` is a
sorted set of content references. `custodian` is `entity_id` and
`previous_manifest` is `option<hash32>`. `signer_entity` MUST be the EVENT or
ALBUM EntityID whose validated state authorizes the signing key.

### 12. Proof-package manifest and signed envelope

The manifest payload is:

```text
common_header || subject || subject_state || identity_profile
              || rgb_contract_id || rgb_schema_id || identity_history
              || bitcoin_proofs || evidence || omissions || policy
              || evaluation_context || previous_manifest
```

`subject` is `entity_id`; `subject_state`, `rgb_contract_id`, and
`rgb_schema_id` are `hash32`; `identity_profile` is versioned `text`;
`identity_history`, `policy`, and `evaluation_context` are content references;
`bitcoin_proofs` and `evidence` are sorted content-reference sets.

Each omission is:

```text
object_id || disclosure_class || reason
```

`object_id` is `hash32`; disclosure class is `u8`: 1 PRIVATE, 2 WITHHELD, or
3 UNAVAILABLE; reason is versioned `text` of at most 256 bytes. Omissions sort
by object ID. `previous_manifest` is `option<hash32>`.

The non-circular identifiers are:

```text
manifest_id = SHA256(manifest_payload)
signature_payload = manifest_payload || manifest_id
message = TaggedHash("O2A/v0.1/proof-package", signature_payload)
signed_envelope = manifest_payload || manifest_id || signature64
package_id = SHA256(signed_envelope)
```

The complete local-file, direct-transfer, or HTTPS package body is exactly
`signed_envelope`. Its SHA-256 MUST equal `package_id`. `package_id` and
locators are advertised outside the envelope and are not signed fields.
Changing the manifest, manifest ID, or signature changes `package_id`.

## Verifier requirements

A verifier MUST:

1. parse one exact bounded payload and reject trailing bytes;
2. reject unknown versions, networks, enums, types, roles, or capabilities;
3. match object type, capability, and tagged-hash domain;
4. validate `signing_key_id` against key role and public key;
5. validate the stated capability in the authorizing RGB state;
6. verify BIP340 over the exact tagged-hash message;
7. reject cross-domain replay and a payment or adapter key used as an O2A
   identity signer; and
8. for a proof package, verify `package_id`, `manifest_id`, publisher
   authorization, and the manifest signature before evaluating contents.

Semantic state-transition and policy requirements remain in their respective
normative specs. Concrete RGB program bytes and the dependency lock remain
open.
