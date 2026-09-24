# RGB Identity Contract — Draft v0.1

## Status

The O2A state machine is specified. Concrete RGB 0.12 program bytes and the
dependency lock remain open. This document does not adopt RGB-WG RC3.

## Same machine, fixed root

Artist, venue, promoter, label, event, and album identities use this same
state machine. The machine is not specialized by entity type. Person, band,
and organization identities use it as well, and each entity still has its own
root.

The root public key is fixed at genesis. Operations 1 through 5 do not change
the root or the EntityID. A different root is a different EntityID. See
[ADR-0005](../adr/0005-bitcoin-rooted-self-custodial-identity.md) and the
[entity schema](entity-schema.md).

## Operations

Genesis is signed by the root identity key under `O2A/v0.1/entity-genesis`.
It creates the first state, including the initial controllers and the initial
recovery policy. Later operations reference that state or a valid successor.

| Code | Operation | Authorization |
| --- | --- | --- |
| 1 | Controller rotation | A current controller with the identity-transition capability |
| 2 | Recovery-policy change | A current controller with the identity-transition capability |
| 3 | Authorized recovery | A recovery key named in the already committed policy |
| 4 | Custody transfer | A current controller plus a signed acceptance claim from the new custodian |
| 5 | Revocation | A current controller with the identity-transition capability |

Operations 1, 2, 4, and 5 MUST be authorized by a current controller with the
identity-transition capability. Their BIP340 signatures use
`O2A/v0.1/identity-transition`. Operation 3 MUST be authorized by a recovery
key named in the recovery policy already committed by a prior valid state.
Its BIP340 signature uses `O2A/v0.1/recovery`. A recovery-policy change does
not authorize itself, and the replacement policy cannot authorize operation 3
until that change is itself a prior valid state. These domains are the tags
reserved in the [cryptographic profile](cryptographic-profile.md). An identity
signature is not a Bitcoin spend.

Controller rotation replaces operational controller keys, their roles, and
their capabilities. Custody transfer changes the custodian or representative
binding in identity state and MUST reference a claim signed by the incoming
custodian in `O2A/v0.1/claim` with predicate
`o2a/custody-acceptance/v1`. The claim identifies the EntityID, prior state,
next custodian, and proposed next seal. A transfer without that exact acceptance
is invalid. Both operations keep the same root public key and EntityID.
Revocation marks the identity revoked. After any operation, a key can publish
the next transition only while the resulting state still authorizes it.

A stolen key can publish the next transition only while current state still
authorizes it. A wallet follows that valid history. It MUST NOT erase the
transition by social vote or by editing a profile. If no recovery path
remains, continuity is a new root and a new EntityID. Successor and compromise
claims are evidence about that new entity. They are not a transition of the
old one.

## Recovery policy

The canonical recovery-policy bytes are defined in
[O2A-CANON-1](canonical-encoding.md). A policy commits:

- policy version and monotonically increasing policy sequence;
- a strictly sorted set of at most 16 recovery-key IDs;
- a nonzero signature threshold no larger than that set;
- a block delay; and
- cancellation rule 1,
  `CONTROLLER_SPENDS_PRIOR_SEAL_BEFORE_NOT_BEFORE`.

Operation 3 names the committed policy hash and a `not_before_height` equal to
the confirmed height of the prior state's anchor plus `delay_blocks`. The
recovery anchor is invalid below that height. Each threshold signer uses a
recovery-role key named by the prior policy, capability `recovery`, and domain
`O2A/v0.1/recovery`. Signature entries are sorted by key ID; duplicates do not
count. The resulting state may replace controllers and recovery policy but
MUST keep the root and EntityID.

Until `not_before_height`, a current controller may cancel the pending recovery
by confirming a different valid operation that spends the same prior seal.
Bitcoin best-chain order resolves the competing spends. Once a valid recovery
anchor is current at the required depth, a later controller action against the
old seal cannot cancel it. Social evidence cannot cancel either branch.

A policy change increments `policy_sequence`. It becomes usable only after the
change is itself the current confirmed state. A recovery referring to an older
policy, a non-current prior state, an already closed seal, an insufficient
threshold, a duplicate signer, or an anchor below `not_before_height` is
invalid. If no committed recovery path remains usable, continuity requires a
new root and EntityID.

Each transition MUST reference the previous valid state, previous seal, and a
new seal, and MUST advance `sequence` by exactly one. The full resulting state
is signed using the canonical payload for its operation; a stale-state
transition is invalid even if its signing key remains known.

## Seal and anchor

The seal is one Bitcoin single-use outpoint:

- the 32-byte transaction id in internal byte order, the order used inside a
  Bitcoin outpoint, not the reversed hexadecimal display order; and
- the u32 output index in Bitcoin outpoint encoding, an unsigned 32-bit
  little-endian integer.

Each state names one current seal. The anchor is the spending transaction that
closes that seal. For operations 1, 2, 4, and 5 it commits to:

```text
TaggedHash("O2A/v0.1/identity-transition", transition payload)
```

Operation 3 commits to:

```text
TaggedHash("O2A/v0.1/recovery", recovery payload)
```

`TaggedHash` is the purpose-specific tagged hash in the cryptographic profile.
Transition, recovery, and genesis payloads are the exact O2A-CANON-1 bytes.
The script or RGB structure that carries the digest is part of the unbound RGB
program bytes. Genesis uses the same seal shape and its commitment domain
remains `O2A/v0.1/entity-genesis`.

Spending the seal closes it. The next transition requires a new seal. A
transaction id or a public key alone is not an identity proof.

The verifier needs all of the following for the claimed state:

- the consignment from genesis through that state;
- the seal;
- the anchor; and
- the header proof that places the anchor in the named best chain.

Missing consignments cannot be rebuilt from the anchor, from a transaction id,
or from a registry row.

## Confirmation and reorg

Required confirmation depth is 1 on regtest, signet, testnet, and testnet4,
and 6 on mainnet. Any other Bitcoin network has no depth in this profile, and
an anchor on that network is not current.

The evaluation context names the best block hash, the height of that best
chain, and the required depth. The named depth MUST be the depth this profile
assigns to that network. An anchor absent from that best chain at the required
depth is not current. A reorg that removes the anchor drops dependent
transitions. Whether an anchor is current is decided only against the named
evaluation context and the supplied consignment. If two candidate anchors
spend the same seal, only a candidate present in that best chain at the
required depth can be current.

## Outside this contract

This contract does not decide stage-name ownership, whether an event occurred,
or copyright. Those questions belong to signed claims, evidence, and a named
[verification policy](verification-policy.md).

## Unbound

Concrete RGB 0.12 program bytes and the dependency lock remain open. This
document does not adopt RGB-WG RC3 or any other RGB stack.
