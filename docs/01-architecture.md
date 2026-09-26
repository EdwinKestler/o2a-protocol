# 01 — Architecture

## Layer model

```text
Applications
    ↑
Registries and discovery views
    ↑
Trust policy and conflict evaluation
    ↑
Claims · attestations · observations · challenges
    ↑
BIP340 key-rooted EntityID and controller authorization
    ↑
RGB identity state and client-side validation
    ↑
Bitcoin anchors, ordering, and single-use seals
```

Dependencies point downward. The protocol kernel MUST NOT import ticket,
catalog-ranking, payment, or application-specific behavior. Bitcoin/RGB is a
required identity-lifecycle foundation, not an optional settlement plugin.

## Authority model

O2A deliberately separates three kinds of authority:

1. **Bitcoin consensus** establishes transaction order, confirmations,
   commitments, and whether a single-use seal was spent.
2. **RGB client-side validation** establishes whether the supplied identity
   history follows the O2A identity schema and its Bitcoin anchors.
3. **O2A policy evaluation** establishes what the supplied signed evidence
   supports about names, relationships, albums, or events.

Bitcoin and RGB cannot determine whether a stage name belongs to a real-world
artist. A policy cannot override an invalid RGB transition. A registry cannot
override either one.

## Layers

### Bitcoin foundation

Provides the consensus-ordered witness transactions and spent seals used by
the RGB identity lifecycle. Each state commits a dedicated role-4 seal policy;
the named outpoint must contain its deterministic controller-or-delayed-
recovery P2TR script. Network, confirmation depth, seal-creating transaction,
header source, current-seal spent/unspent observation, reorg handling,
commitment method, outpoint, and witness data are explicit verifier inputs.

### RGB identity state

Defines and validates identity genesis, controller rotation, recovery-policy
changes, authorized recovery, custody transfer, and revocation. Consignments
and the client-side history remain with interested parties; a transaction ID
alone is not an identity proof.

For the public O2A identity profile, the owner deliberately exports the
identity-history shard and Bitcoin proofs needed by another wallet as a
content-addressed public proof package. This is a disclosure choice defined by
the profile, not a claim that all RGB state is globally public.

### Entity identity

Defines a generic EntityID rooted in a dedicated BIP340/secp256k1 public key.
Every ARTIST, BAND, VENUE, PROMOTER, LABEL, ORGANIZATION, EVENT, and ALBUM uses
its own root key. Root, controller, recovery, discovery, seal, and payment keys
have separate purposes. Seal keys spend only the identity seal and hold no O2A
object-signing capability.

### Claims and attestations

Claims are controller-authorized statements. Attestations are independently
authorized evidence from another identity or versioned observer. Names remain
non-exclusive claims. EVENT and ALBUM keys sign their canonical manifests and
content commitments; participant attestations remain separate.

### Online observations

DNS, HTTPS, social, Pubky, and Nostr collectors create signed, bounded
observation objects. The deterministic core consumes those objects, not hidden
live network responses. Re-fetching produces new evidence rather than silently
changing an old result.

### Challenges and revocation

Evidence challenges, corrections, supersession, and revocations preserve
history. Entity revocation is an RGB state transition; revoking a claim is a
signed evidence object.

### Trust policy

Consumes validated identity histories and normalized evidence to derive an
explainable result. A policy may compare competing name claims, including
their supporting evidence and Bitcoin chronology, but the core protocol has no
first-claim global username rule.

### Registries and discovery

Artist, venue, promoter, label, album, and event registries are rebuildable
projections. Pubky/PKARR can publish public profiles and discovery pointers
through a signed Ed25519-key binding. Nostr can publish BIP340-signed events
through a separate binding. Both use the canonical
[`discovery_key_binding`](../specs/discovery-binding-schema.md) object and its
dedicated O2A signature domain; neither adapter key replaces the O2A root.

Discovery records advertise signed package hashes and transport locators.
Another wallet verifies the retrieved bytes; the locator or hosting service is
never authority. Direct wallet-to-wallet export remains required, and public
packages should be replicated across independent retrieval paths.

### Applications

GatePass, SplitNight, catalogs, sponsorship, merchandise, and paid permissions
consume identities and verification results. They do not redefine the root
identity model.

## Self-custodial wallet/node

The reference client is wallet-like software on the participant's machine. It
stores:

- the seed and separated identity/controller derivation domains;
- root and operational identity keys, never reused as spending keys;
- RGB identity consignments and Bitcoin proof data;
- claims, attestations, challenges, and proof packages;
- EVENT and ALBUM keys held for the responsible custodian; and
- signed bindings for Pubky, Nostr, DNS, social, and payment endpoints.

The client supports a full Bitcoin node and a clearly labeled light mode. Light
mode MUST disclose its header, inclusion-proof, indexer, privacy, and
availability assumptions. Offline mode verifies retained packages without
pretending to know about evidence it has not received.

O2A-authored specifications, documentation, and future official reference
wallet/node software use `MIT OR Apache-2.0`. Recipients may select MIT for
minimal downstream friction or Apache-2.0 for its express patent grant and
NOTICE terms. Explicitly marked conformance vectors use CC0-1.0. This closes
the source-license decision; it does not close the remaining protocol,
dependency, conformance, or security gates.

## Storage model

```text
Bitcoin headers and anchors + RGB consignments + signed evidence packages
                              ↓
                     client-side validation
                              ↓
                    deterministic evaluator
                              ↓
                       projection builder
                              ↓
         PostgreSQL / search / Pubky index / application API
```

PostgreSQL, Redis, object storage, Pubky homeservers, Nostr relays, and search
indexes are replaceable transport or projection infrastructure. Durable client
backups are still required: Bitcoin commitments cannot reconstruct a missing
RGB consignment or undisclosed evidence package.

## Determinism invariant

For validated identity histories I, evidence E, policy P, protocol version V,
and explicit evaluation context C:

[
Verify(I,E,P,V,C)=R
]

Every conforming implementation MUST produce the same result R. Online wallets
can collect new evidence, but must show that the input set changed.
