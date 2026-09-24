# Phase 0 accept and reject cases

SPDX-License-Identifier: CC0-1.0

This directory tracks the Phase 0 roadmap gate. `v0.1.json` contains the
claim and proof-package fixtures. `protocol-objects-v0.1.json` contains fixed
payloads, tagged hashes, and signatures for the remaining signed-object
layouts. `check_vectors.py` runs both bounded checkers and delegates BIP340 to
the pinned rust-secp256k1 helper in `crypto-checker/`. These are vector tools,
not a wallet, and they do not use the network. The helper's lock hash, audit,
and license result are recorded in [DEPENDENCIES.md](DEPENDENCIES.md).
`derivation-v0.1.json` records Route B paths and expected keys;
`check_derivation_cross.py` requires the independent Python and Rust
implementations to produce identical results.

The vector track remains **OPEN**. This directory has no adopted RGB
consignment, Bitcoin anchor/header proof, seal execution, or reorg execution.
The new lifecycle fixtures cover canonical bytes and local authorization
inputs only; they do not execute an RGB transition.
Reciprocal discovery proofs, full rebinding-history validation, live adapter
checks, present claim optional-field branches, and general parser
interoperability also remain open.

`v0.1.json` uses published BIP340 test-vector keys that are permanently unsafe
for funds. It contains no wallet seed. It publishes two regtest EntityIDs,
role-bound controller key IDs, signed claim variants with separately encoded
capabilities and networks, and one non-circular proof-package envelope.
Wallet derivation uses the separate permanently unsafe BIP39 vector recorded
in `derivation-v0.1.json`; it is not a funding or production seed.

| Area | Current executable evidence |
| --- | --- |
| Entity/key boundary | EntityID, BIP340 x-only root parsing, invalid-root rejection, and controller-role key ID |
| Claim | Canonical payload, fixture-scoped bounded decoding, distinct bytes/text limits, tagged hash, valid signature, mutated signature rejection |
| Cross-domain replay | Claim signature rejected under the attestation tag |
| Proof package | Manifest ID, signature, signed-envelope package ID, truncation and mutation hashes |
| Wrong capability | Original signature rejection after mutation; independently re-signed payload rejected by object/domain/capability evaluation |
| Wrong role | Original signature rejection after controller-to-recovery role mutation; independently re-signed payload rejected by semantic evaluation |
| Claim header authorization | Re-signed absent-state and arbitrary-key-ID claims are rejected |
| Wrong network | Independently signed mainnet claim accepted in mainnet context and rejected in regtest context; signed unknown-network claim rejected |
| Duplicate names | Two independently signed claims from distinct EntityIDs both verify and remain separately visible |
| Recovery-policy hash | Canonical threshold policy under `O2A/v0.1/recovery-policy` |
| Genesis and identity transition | Fixed signed bytes; root/EntityID match; controller-rotation sequence checks; unsupported operations fail closed |
| Recovery authorization | Fixed one-signer bytes; committed policy hash and not-before checks; thresholds above one return incomplete until a signature bundle is verified |
| Evidence objects | Fixed signed attestation, challenge, and evidence-revocation bytes with duplicate/sort/target negatives |
| Control and discovery | Fixed signed challenge, observation, Pubky rebinding, and Nostr rebinding; explicit expiry and signed-omission evaluation |
| Music manifests | Fixed signed EVENT and ALBUM manifests; signer-entity and required album track checks |
| Object framing | Each fixed signed-object payload rejects truncation and trailing bytes before evaluation |
| Unknown state capability | Independently re-signed state with an unassigned capability value is rejected |
| Wallet derivation | Route B master, BIP85 `xprv_o2a`, identity roles, and BIP86 payment keys agree across independent Rust and Python implementations for mainnet and regtest, entities 0 and 1; all required misuse cases reject |
| Bitcoin/RGB execution | Open; no consignment, anchor, header, seal-spend, fork, or reorg fixture |

The current claim decoder fixture exercises absent `context`, `supersedes`, and
`checkpoint` forms only. Present optional-field branches, unknown enum values
other than the executable network rejection, and general parser
interoperability remain open. This bounded checker is not a general-purpose
O2A validator.

`check_protocol_objects.py` reconstructs the fixed protocol-object payloads,
checks every stored digest and signature, flips every signature for a negative
case, rejects truncated and trailing-byte payloads, and rejects every
signature under a different O2A tag. Its bounded
decoder reads the exact signed bytes before object-specific evaluation. The
well-formed invalid byte cases are independently re-signed before rejection;
fixture metadata is expected-output description, not verifier input. State
authorization, block height, observation time, and target classification are
explicit evaluation-context inputs. Its state IDs and outpoints remain
synthetic. Passing it does not prove an RGB state transition, Bitcoin
commitment, external DNS/social observation, or discovery-adapter reciprocal
signature.
Attestation, challenge, and evidence-revocation checks cover serialization,
signature authorization, sorted evidence inputs, and target classification;
they do not decide whether an assertion is socially true or satisfy a complete
trust policy.

## Primitive bounds and EntityID root parsing

Accept a claim object `bytes` field of 4,097 bytes even though that size would
be too large for `text`. Reject a `bytes` field of 1,048,577 bytes and a `text`
field of 4,097 bytes. These cases keep the one-megabyte `bytes` limit separate
from the 4,096-byte `text` limit.

Accept EntityID roots only after the 32 bytes parse as a secp256k1 BIP340
x-only public key. Reject the published BIP340 invalid public-key test-vector
bytes before EntityID hashing. This is public conformance data, not a wallet
key or seed.

## Distinct root vs payment key

Accept a root identity key and a payment key that are different public keys.
The proposed Route B identity hierarchy is rooted at a BIP85-derived
`xprv_o2a` outside the BIP43 purpose slot. The payment key is the BIP32 x-only
key at the BIP86 path
`m/86'/coin'/account'/0/index`. The payment key has no O2A purpose byte and
no O2A key identifier. Controller, recovery, and Nostr publication keys are
separate hardened identity keys and are not payment keys.

Reject a payment key used as the root, as an EntityID input, or as the signer
of an O2A object. Reject `O2A/v0.1/key-id` for a payment key. Reject one key
filling both roles.

`derivation-v0.1.json` executes the separation and rejects unhardened identity
components, role or entity reuse, path aliases, a wrong coin type, an
unsupported profile version, the retired path, and payment-key signing of an
O2A object. Passing these fixtures does not freeze the proposed profile.

## Duplicate names

Accept two EntityIDs that use the same human-readable name. Each name is a
claim signed in `O2A/v0.1/claim` by a controller-role key the issuer state
authorizes for capability `claim`. Both claims stay visible. Anchor order is
chronology, not ownership of the spelling.

Reject a first-claim registry, a merge of the two EntityIDs, hiding either
claim, a name claim signed outside `O2A/v0.1/claim`, and a name claim signed
by a key the stated state does not authorize for `claim`.

Byte fixtures contain two independently signed self-name claims from distinct
EntityIDs. The checker verifies both authorization contexts and requires an
evaluation result containing both EntityID-to-claim-digest entries. It never
selects a spelling owner or merges the entities.

## Invalid BIP340 signature

Accept a BIP340 signature over the 32-byte claim digest
`TaggedHash("O2A/v0.1/claim", payload)` that verifies with the authorized
signer.

Reject that signature when its last byte is bitwise flipped (XOR `0xFF`).
Reject any other failed BIP340 check of the 32-byte tagged-hash message,
including a truncated signature, `r` greater than or equal to the field
prime, `s` greater than or equal to the curve order, or a point `R` whose Y
coordinate is odd or whose X coordinate is not `r`.

Byte fixture: one controller-role signature of the claim digest made with the
published BIP340 test key for scalar 3, plus the same signature with its final
byte flipped. The Python checker performs no elliptic-curve arithmetic; the
pinned rust-secp256k1 helper verifies the valid, mutated, and cross-domain
cases.

## Cross-domain replay

Accept the claim payload only under the tag `O2A/v0.1/claim`.

Reject the same payload bytes under `O2A/v0.1/attestation`, or under any
other reserved tag, even when the claim signature is attached. The two
tagged digests are different messages. A signature that succeeds for one tag
is rejected for the other.

An attestation beside these cases is one identity attesting about another in
`O2A/v0.1/attestation`. Reject the attester signature as the subject's own
claim.

Byte fixture: the same claim payload is hashed under both tags. The checker
requires the digests to differ and requires the claim signature to fail
verification on the attestation digest.

## Wrong network

Accept the regtest EntityID and the mainnet EntityID of one root as two
identifiers. EntityID is
`TaggedHash("O2A/v0.1/entity-id", u16le(1) || network || root_xonly)`.
Regtest is network byte 4. Mainnet is network byte 0. The same root on two
networks produces two EntityIDs.

Reject treating those identifiers as one entity. Reject an object, signature,
or anchor whose network does not match the entity. Reject an unknown network
byte. An anchor on a Bitcoin network that has no confirmation depth in the
RGB identity contract is not current.

The fixture includes a valid, independently signed mainnet claim. The checker
accepts it when the explicit verifier context is mainnet and rejects the same
claim when that context is regtest. Bitcoin anchor/network checking remains
open until an RGB execution fixture exists.

A separately signed payload using unknown network byte 5 is rejected even when
the caller supplies 5 as the expected verifier network. Unknown networks are
also rejected before EntityID construction.

## Wrong capability

Accept a claim only when object type `claim`, the claim signing domain, the
claim capability, the controller role, and the authorizing fixture state all
agree.

Reject the original signature after the capability byte is changed. Also
reject a cryptographically valid, independently re-signed payload whose
capability is not `claim`; re-signing cannot turn an object/domain/capability
mismatch into authorization. The executable fixture covers both rejection
paths rather than treating a changed digest as sufficient evidence.

## Wrong role

Accept an ordinary name claim only when the signed key role is controller and
the stated authorizing context binds that controller-role key to capability
`claim`.

Reject the original signature after the signed role byte is changed from
controller to recovery. Also reject an independently re-signed payload that
retains the recovery role: a valid signature by the same public key does not
authorize a recovery-role header to sign an ordinary claim.

## Wrong RGB contract

Accept identity history only when the supplied consignment is for that
entity's RGB contract and schema, from genesis through the claimed state.

Reject a different contract, schema, or asset presented as this entity's
history. An unknown schema MUST fail closed.

Concrete RGB 0.12 program bytes are not frozen. This directory does not
choose a contract id, and this case was not executed.

## Forked consignment

Accept the one history that links genesis to the claimed state, each step
referencing the previous valid state and advancing `sequence`, when its
anchor is in the named best chain at the required depth.

Reject a second candidate that spends the same seal, a history that does not
connect to genesis, and a branch the named best chain does not contain at
the required depth. If two candidate anchors spend the same seal, only a
candidate present in that best chain at the required depth can be current.
Do not merge a fork by social vote or by editing a profile.

Not executed on regtest.

## Missing consignment

Accept evaluation only when the consignment from genesis through the claimed
state is supplied, together with the seal, the anchor, and the header proof
that places the anchor in the named best chain.

Reject a missing consignment. Do not rebuild it from the anchor, from a
transaction id, or from a registry row. The result is incomplete or invalid,
not a reconstructed acceptance.

Not executed on regtest.

## Mismatched seal

Accept the state whose current seal is the Bitcoin outpoint the anchor
spends. The outpoint is the 32-byte transaction id in internal byte order
and the output index as a little-endian `u32`. For operations 1 through 5
the anchor commits to
`TaggedHash("O2A/v0.1/identity-transition", transition payload)`. Genesis
uses the same seal shape and commits in `O2A/v0.1/entity-genesis`.

Reject an anchor that spends a different outpoint, a display-reversed
transaction id, a wrong output index, or a commitment that is not the tagged
hash for that operation. Reject a transaction id or a public key offered
alone as identity proof. Once spent, the seal is closed, and the next
transition needs a new seal.

Not executed on regtest.

## Reorg and confirmation

Accept an anchor that the named evaluation context includes in its best chain
at the required depth. Depth is 1 on regtest, signet, testnet, and testnet4,
and 6 on mainnet. The named depth must be the depth this profile assigns to
that network.

Reject an anchor that is absent from that best chain at the required depth.
It is not current. A reorg that removes the anchor drops dependent
transitions. Any other Bitcoin network has no depth in this profile, and an
anchor on it is not current.

Not executed on regtest. The byte fixture does not contain headers or
anchors.

## Controller compromise while still authorized

Accept, as valid history, the next otherwise valid transition published by a
compromised controller while current state still authorizes that key. A
wallet follows that RGB and Bitcoin history and keeps the compromise evidence
visible.

Reject erasing that transition by social vote, by editing a profile, or by a
later policy. Reject a further transition from a key the resulting state no
longer authorizes.

Not executed on regtest.

## Recovery when a path remains

Accept operation 3 when enough recovery keys named in the recovery policy
already committed by a prior valid state sign `O2A/v0.1/recovery`, and the
supplied signatures satisfy that committed threshold. The root public key and
the EntityID stay the same. The committed policy supplies the exact delay and
cancellation rule defined by the RGB identity contract.

Reject recovery in any other tag. Reject a key the prior policy does not
name. Reject a recovery that changes the root or the EntityID. Reject use of
a replacement policy before that replacement is itself a prior valid state.
A recovery-policy change does not authorize itself.

The protocol-only fixture now fixes recovery payload bytes, policy hash,
recovery-role key identifier, one signature, a 1-of-1 prior threshold,
six-block delay, and `not_before_height`. It accepts at the explicit eligible
height and rejects one block early and a policy hash that differs from the
prior committed input. It returns `incomplete` for a threshold above one; this
checker does not verify a multi-signer recovery bundle and does not execute or
anchor the resulting RGB transition.

## Recovery when no path remains (new EntityID)

Accept continuity only as a new root and a new EntityID, with successor and
compromise claims that are evidence about the new entity.

Reject those claims as a transition of the old EntityID. Reject keeping the
old EntityID while replacing its root. The protocol does not treat the old
EntityID as cryptographically recovered.

Not executed. The fixture does not replace a root, derive a successor key, or
claim continuity for an unrecoverable EntityID.

## Revocation

Accept identity revocation, operation 5, when a current controller with the
identity-transition capability signs `O2A/v0.1/identity-transition` and the
transition is anchored. The root and the EntityID stay the same. The
resulting state is revoked. A key can publish the next transition only while
that state still authorizes it.

Accept an evidence revocation in `O2A/v0.1/revocation` as visible
qualification of its target object. Accept a challenge in
`O2A/v0.1/challenge` as visible optional evidence.

Reject an evidence revocation as revocation of the identity root. Reject a
challenge alone as revocation of its target or of the identity root. Reject
identity revocation by a key the current state does not authorize for
identity transition. Reject an evidence object that tries to mutate the
identity lifecycle by itself.

The evidence-revocation and challenge payloads now have fixed signatures and
cross-domain negatives. The checker rejects an evidence-revocation target
classified as an EntityID. Identity lifecycle revocation and its Bitcoin/RGB
execution remain unexecuted.

## Expired control proof

Accept a DNS, HTTPS, or social observation whose expiry input is present and
whose evaluation time is inside that window. It is channel-control evidence
for that window, not entitlement to a name.

Reject an expired observation or an evaluation time before `observed_at`. It
is not current channel control. Reject a missing expiry. Policies report
missing, future-dated, expired, conflicting, or unverifiable evidence instead
of inferring a positive result.

Fixed control-challenge and observation payloads are signed in their distinct
domains. With an explicit evaluation time, the observation is current only
from `observed_at` through expiry, returns `not_yet_observed` before that time,
and `expired` after it. The checker also rejects non-increasing challenge and
observation time windows. No DNS, HTTPS, or social request is performed.

## Pubky rebinding

Accept a new discovery binding whose payload contains a Pubky Ed25519 key,
signed in `O2A/v0.1/discovery-binding` by the BIP340 identity key authorized
for that purpose. The previous Pubky binding stays visible. The O2A root and
the EntityID do not change. Rebinding is a new binding. A supersession
reference does not erase the previous one.

Reject the Pubky key as the O2A root or as a new EntityID. Reject the
binding encoded or accepted as a generic claim. Reject the binding signature
in every domain except `O2A/v0.1/discovery-binding`. The Pubky reciprocal
signature stays in Pubky's signing context and does not replace the O2A
signature.

The fixed Pubky binding contains a 32-byte Ed25519 adapter key and is signed by
the O2A BIP340 controller in the discovery-binding domain. The checker rejects
the Pubky/BIP340 scheme pairing and cross-domain replay. Its signed payload now
contains a `supersedes` object ID. Validation of the referenced earlier binding,
full rebinding history, and Pubky's reciprocal signature remain open.

## Nostr rebinding

Accept the same shape for a Nostr key in `O2A/v0.1/discovery-binding`, with
the previous Nostr binding still visible. The O2A root and the EntityID do
not change.

Reject the Nostr key as the O2A root or as a new EntityID. Reject the
binding in the generic claim domain or any other O2A domain. A Nostr event
signature follows Nostr's rules and does not replace the O2A binding
signature.

The fixed Nostr binding uses a published unsafe BIP340 test key distinct from
the issuer root, carries a signed `supersedes` object ID, and rejects an
Ed25519 scheme pairing and cross-domain replay. Validation of the referenced
earlier binding and full rebinding history remain open. The checker does not
verify a Nostr event, contact a relay, or execute a reciprocal proof.

## Album custody

Accept an album manifest signed by that album entity's own key in
`O2A/v0.1/music-manifest`.

Reject another entity's key as that manifest signature. Reject the manifest
hash as proof of copyright ownership.

The fixed ALBUM payload, hash, and signature use the album EntityID as signer,
carry a track-manifest hash, and remain distinct from the EVENT payload. The
checker rejects the album case when the required track manifest is absent.
RGB custody transfer and copyright claims are not executed or inferred.

## Event custody

Accept an event manifest signed by that event entity's own key in
`O2A/v0.1/music-manifest`.

Reject another entity's key as that manifest signature. Reject the manifest
hash as proof the event occurred.

The fixed EVENT payload, hash, and signature use the event EntityID as signer.
The checker rejects a mismatched signing entity. RGB custody transfer and proof
that the event occurred are not executed or inferred.

## Proof-package envelope

Accept a complete signed envelope only when `manifest_id` is SHA-256 of the
canonical manifest payload, the publisher signature verifies over
`TaggedHash("O2A/v0.1/proof-package", manifest_payload || manifest_id)`, and
`package_id` is SHA-256 of the complete
`manifest_payload || manifest_id || signature64` response body.

Reject a manifest-ID mismatch, package-ID mismatch, invalid publisher
capability, invalid signature, truncated body, trailing bytes, or an HTTPS body
whose SHA-256 differs from the advertised package ID. The executable fixture
recomputes both identifiers and the signature and proves that truncation or a
one-byte mutation changes the package ID. A separately signed canonical
manifest names the discovery-binding digest in its omission list; parsing those
signed package bytes returns `incomplete`. This is bounded missing-object
policy evaluation, not a new proof-package wire layout.

## Unavailable discovery

Accept verification of a retained proof package, or of evidence exchanged
directly, while Pubky, Nostr, indexers, and other discovery services are
unavailable. Discovery data can disappear or move without changing that
verification and without changing the EntityID. The package id is the
integrity reference. A locator is not.

Reject a homeserver, relay, indexer, or URL as identity authority. Reject
unavailable discovery as a reason to reconstruct missing RGB history from a
transaction id, a registry row, or a profile badge. If referenced content
that the named policy requires is unavailable, the evaluation is incomplete,
not a silent acceptance.

The missing-discovery requirement case returns `incomplete` rather than
accepting silently. Verification of a complete retained package during an
actual discovery-service outage, and all live Pubky/Nostr behavior, remain
unexecuted.
