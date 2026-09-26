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
recovery and seal policies. Later operations reference that state or a valid
successor. Every resulting state commits a seal policy for the `next_seal` it
names.

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

`delay_blocks` MUST be in `1..=65535`. Operation 3 names the committed policy
hash and a `not_before_height` equal to the confirmation height of the
transaction that created the current seal output plus `delay_blocks`. The
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

The height basis MUST be the seal-creating transaction rather than the prior
state's anchor. [BIP68](https://github.com/bitcoin/bips/blob/master/bip-0068.mediawiki)
measures a relative block lock from confirmation of the
output being spent. Those transactions can differ, including for genesis or a
pre-funded successor seal. If the tapscript matured before O2A's signed
`not_before_height`, recovery seal keys could close the outpoint with a
transaction whose O2A recovery transition the verifier rejects, permanently
freezing the identity. Matching both clocks makes the Bitcoin and O2A delay
conditions become eligible at the same height.

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

## Seal output script

Every genesis seal and every successor `next_seal` MUST be a native P2TR
output whose output key is recomputed from the state that names that outpoint.
The policy bytes are defined in [O2A-CANON-1](canonical-encoding.md). The
internal key is the BIP341 NUMS point

```text
H = lift_x(50929b74c1a04954b78b4b6035e97a5e078a5a0f28ec96d547bfee9ace803ac0)
```

which is the concrete example published in
[BIP341](https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki).
Implementations MUST use that exact even-Y lifted point and MUST NOT produce or
accept a key-path authorization. All spending paths are tapscript leaves with
leaf version `0xc0`.

Validate that the seal bindings exactly cover the authorizing controller and
recovery key-ID sets before constructing a script. Then extract the controller
seal keys and sort them by raw x-only bytes. For each sorted controller seal
key `C`, create one controller leaf whose script bytes are:

```text
0x20 || C || OP_CHECKSIG
```

Extract the recovery seal keys and sort them by raw x-only bytes. Create one
recovery leaf from those keys `R1..Rn` in that order, threshold `k`, and
`delay_blocks` value `d`:

```text
and_v(v:multi_a(k,R1,...,Rn),older(d))

<R1> OP_CHECKSIG
<R2> OP_CHECKSIGADD
...
<Rn> OP_CHECKSIGADD
<k> OP_NUMEQUALVERIFY
<d> OP_CHECKSEQUENCEVERIFY
```

`<key>` is the minimal 32-byte direct push (`0x20 || xonly`). `<k>` and `<d>`
use the minimally encoded Bitcoin `CScriptNum` push; values 1 through 16 use
`OP_1` through `OP_16`. The `multi_a` and `older` translations are those in
[BIP379](https://github.com/bitcoin/bips/blob/master/bip-0379.md), using the
Schnorr `OP_CHECKSIG` and `OP_CHECKSIGADD` semantics in
[BIP342](https://github.com/bitcoin/bips/blob/master/bip-0342.mediawiki).

Compute each leaf hash as BIP341
`TaggedHash("TapLeaf", 0xc0 || CompactSize(script_length) || script)`. Order
the leaves as all controller leaves in canonical controller-seal-key order,
followed by the recovery leaf. In each round, pair adjacent nodes from left to
right. Hash each pair as
`TaggedHash("TapBranch", min(left,right) || max(left,right))`, comparing the
32-byte hashes lexicographically as required by BIP341. Carry an unpaired final
node unchanged into the next round. Repeat until one Merkle root remains.

Compute `t = TaggedHash("TapTweak", H_x || merkle_root)`, reject `t` at or
above the secp256k1 group order, and compute `Q = H + int(t)G`. The required
seal scriptPubKey is exactly `OP_1 || 0x20 || x(Q)`. This left-to-right
pairwise reduction is the v0.1 choice because it is deterministic for every
allowed leaf count, needs no probability metadata, and leaves BIP341's
consensus sibling sorting intact. Two implementations given the same state
must therefore derive the same output key.

The O2A commitment carrier MUST NOT modify this seal output script. In
particular, a seal output MUST NOT also host a Tapret commitment. Tapret,
Opret, and the concrete RGB carrier remain otherwise unbound; any carrier
commitment belongs in another transaction output.

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
The O2A commitment carrier is that 32-byte digest inside the consignment for
the transition that closes the seal. A verifier recomputes the digest from the
canonical payload and checks that the consignment names the same outpoint. A
digest that exists only in a registry row is not a commitment. This profile
does not freeze an OP_RETURN, Taproot annex, or Tapret template. RGB 0.12
abstracts the seal protocol, and the program bytes that place the digest in a
particular RGB transition stay unbound until the dependency gate adopts a lock.
Genesis uses the same seal shape and its commitment domain remains
`O2A/v0.1/entity-genesis`.

Spending the seal closes it. The next transition requires a new seal. A
transaction id or a public key alone is not an identity proof. The tapleaf
revealed by the anchor's seal-spending input is not an O2A operation-validity
input: Bitcoin validates that the spend satisfied one committed branch, while
the O2A signatures and prior-state capabilities independently authorize the
operation. Treating the revealed leaf as O2A authorization would collapse
Bitcoin spending authority into O2A controller authorization.

The verifier needs all of the following for the claimed state:

- the consignment from genesis through that state;
- every transaction that created a seal output named by that history, with
  its inclusion and header proof;
- the seal and its exact scriptPubKey;
- the anchor; and
- the header proof that places the anchor in the named best chain.

For every named seal, the verifier MUST recompute the P2TR scriptPubKey from
the seal policy in the state that names it and reject the history if the
creating transaction's output does not match. This check applies to genesis
and every successor seal.

Missing consignments cannot be rebuilt from the anchor, from a transaction id,
or from a registry row.

## Seal closed without a valid transition

`CURRENT` requires an explicit observation from the evaluation context's
named Bitcoin view that the current seal is unspent. A proof package can carry
historical transactions and inclusion proofs, but it cannot prove global
non-spend; the result MUST therefore report the Bitcoin-view source, observed
best-block hash, and height. RGB validation alone never establishes
`CURRENT`.

A current-seal spend is proven by the spending transaction plus its inclusion
and header proof in that same Bitcoin view. Only after the spend reaches the
identity-anchor confirmation depth does it close the seal for evaluation. The
same reorg rule applies: if a reorg removes the qualifying spend or drops it
below the required depth, the terminal result no longer follows from that
view.

If such a confirmed transaction spends the current seal but carries no valid
O2A transition, the identity remains at its last valid state and can never
transition again. Verification MUST report
`SEAL_CLOSED_WITHOUT_VALID_TRANSITION`; it MUST NOT report the identity as
REVOKED or silently treat its last ACTIVE state as transition-capable.
Continuity requires a new EntityID plus explicit successor and compromise
evidence under ADR-0005.

Compromise of a seal key can therefore freeze an identity but cannot forge an
O2A transition without the separate O2A authorization. Seal-key custody is in
the same operational-risk class as controller-key custody and requires the
same backup, isolation, and incident planning.

## Informational wallet notes

These notes are non-normative. A recovery-leaf spending transaction needs
`nVersion >= 2` and a block-based `nSequence` matching `delay_blocks`. Fees may
come from additional payment-key inputs, but those keys do not enter the seal
script. Seal outputs should be above the applicable dust threshold, and wallet
coin selection must never use a seal output for an ordinary payment.

Disposable demo-lineage smoke evidence at `o2a-testnet-demo` commit
`bce2b58`, manifest
`59f80970be1de88a642cd2345386ba7e12b903caf9b48f9ced5c39288c7e4b01`,
observed that generic RGB 0.12 descriptors neither tracked these custom
tapscript seal outputs nor finalized their inputs. Implementations therefore
keep their own seal records and finalize the seal input through its script
path; an RGB wallet may still supply ordinary payment inputs for fees. This is
disposable regtest evidence, not an adopted dependency, production result, or
Phase 0 closure claim.

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
