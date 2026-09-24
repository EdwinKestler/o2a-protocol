# Phase 0 accept and reject cases

SPDX-License-Identifier: CC0-1.0

This directory tracks the Phase 0 roadmap gate. `v0.1.json` contains the
current executable O2A-CANON-1 claim and proof-package fixtures.
`check_vectors.py` recomputes their bytes and hashes and delegates BIP340 to
the pinned rust-secp256k1 helper in `crypto-checker/`. It is a vector tool, not
a wallet, and it does not use the network. The helper's lock hash, audit, and
license result are recorded in [DEPENDENCIES.md](DEPENDENCIES.md).

The vector track remains **OPEN**. This directory has no adopted RGB
consignment, anchor/header proof, recovery transition, control observation,
discovery transcript, or music manifest fixture. Those cases remain expected
results only and are not made executable by the passing claim/package checker.

`v0.1.json` uses the published BIP340 public test key for scalar 3, permanently
unsafe for funds. It contains no wallet seed. It publishes one regtest
EntityID, a role-bound controller key ID, one claim with a separately encoded
claim capability, and one non-circular proof-package envelope. Identity BIP32
purpose `827'` is no longer treated as frozen and is not recomputed by the
checker.

| Area | Current executable evidence |
| --- | --- |
| Entity/key boundary | EntityID and controller-role key ID |
| Claim | Canonical payload, tagged hash, valid signature, mutated signature rejection |
| Cross-domain replay | Claim signature rejected under the attestation tag |
| Proof package | Manifest ID, signature, signed-envelope package ID, truncation and mutation hashes |
| Wrong capability and wrong network | Mutations of the claim fixture; digests must change |
| Duplicate names | Two EntityIDs, one name string, unequal claim payloads |
| Recovery-policy hash | Canonical threshold policy under `O2A/v0.1/recovery-policy` |
| RGB/evidence/discovery/music execution | Open; prose cases only |

## Distinct root vs payment key

Accept a root identity key and a payment key that are different public keys.
The intended identity hierarchy uses a still-unallocated BIP43 purpose. The
payment key is the BIP32 x-only key at the BIP86 path
`m/86'/coin'/account'/0/index`. The payment key has no O2A purpose byte and
no O2A key identifier. Controller, recovery, and Nostr publication keys are
separate hardened identity keys and are not payment keys.

Reject a payment key used as the root, as an EntityID input, or as the signer
of an O2A object. Reject `O2A/v0.1/key-id` for a payment key. Reject one key
filling both roles.

No payment or derivation fixture is current while the identity purpose remains
unallocated. This case cannot become ready from the older `827'` data.

## Duplicate names

Accept two EntityIDs that use the same human-readable name. Each name is a
claim signed in `O2A/v0.1/claim` by a controller-role key the issuer state
authorizes for capability `claim`. Both claims stay visible. Anchor order is chronology, not
ownership of the spelling.

Reject a first-claim registry, a merge of the two EntityIDs, hiding either
claim, a name claim signed outside `O2A/v0.1/claim`, and a name claim signed
by a key the stated state does not authorize for `claim`.

No second name claim is in the byte fixture. The one claim payload there is
only the canonical layout for a single self-name claim.

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

The executable claim uses network byte 4. A mainnet/wrong-network fixture and
anchor check remain open.

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

Not executed on regtest. The byte fixture publishes the recovery x-only key
and its key identifier only.

## Recovery when no path remains (new EntityID)

Accept continuity only as a new root and a new EntityID, with successor and
compromise claims that are evidence about the new entity.

Reject those claims as a transition of the old EntityID. Reject keeping the
old EntityID while replacing its root. The protocol does not treat the old
EntityID as cryptographically recovered.

Not executed on regtest.

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

Not executed on regtest.

## Expired control proof

Accept a DNS, HTTPS, or social observation whose expiry input is present and
whose evaluation time is inside that window. It is channel-control evidence
for that window, not entitlement to a name.

Reject an expired observation. It fails the control check and is not current
channel control. Reject a missing expiry. Policies report missing, expired,
conflicting, or unverifiable evidence instead of inferring a positive
result.

Not executed on regtest.

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

Not executed on regtest. Pubky keys are not derived on the secp256k1 paths
in `v0.1.json`.

## Nostr rebinding

Accept the same shape for a Nostr key in `O2A/v0.1/discovery-binding`, with
the previous Nostr binding still visible. The O2A root and the EntityID do
not change.

Reject the Nostr key as the O2A root or as a new EntityID. Reject the
binding in the generic claim domain or any other O2A domain. A Nostr event
signature follows Nostr's rules and does not replace the O2A binding
signature.

Not executed on regtest. No current rebinding transcript is present.

## Album custody

Accept an album manifest signed by that album entity's own key in
`O2A/v0.1/music-manifest`.

Reject another entity's key as that manifest signature. Reject the manifest
hash as proof of copyright ownership.

Not executed. No album-manifest fixture is present.

## Event custody

Accept an event manifest signed by that event entity's own key in
`O2A/v0.1/music-manifest`.

Reject another entity's key as that manifest signature. Reject the manifest
hash as proof the event occurred.

Not executed. No event-manifest fixture is present.

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
one-byte mutation changes the package ID. Missing-object evaluation remains a
separate open fixture.

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

Not executed on regtest.
