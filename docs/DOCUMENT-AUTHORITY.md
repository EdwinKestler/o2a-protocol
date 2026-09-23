# Document authority

**Status:** repository convention, 2026-09-23. This page records which documents
govern when two O2A texts disagree. It does not add protocol rules.

The project is in the specification phase. The normative specs below are Draft
v0.1. Exact byte encoding, RGB contract identifiers, Bitcoin commitment and
reorg rules, key-derivation paths, and conformance vectors remain Phase 0
gates. Until those gates close, a draft schema controls other documents, and
it is not yet a frozen wire format.

## Precedence

```text
Accepted ADRs
    ↓
Normative specs
    ↓
Master explanations
    ↓
Supporting explanations
    ↓
Diagrams, website, examples, and application proposals
```

The higher document wins. Edit the lower document to match. A new protocol
rule is introduced in an ADR or a normative spec, then copied downward. The
[README](../README.md) is the index and status summary. It does not introduce
protocol rules. The [Apache License 2.0](../LICENSE) governs reuse of this
repository. It is not a protocol rule.

Among accepted ADRs,
[ADR-0005](../adr/0005-bitcoin-rooted-self-custodial-identity.md) is the
primary design authority. Its amendments take precedence over
[ADR-0001](../adr/0001-modular-protocol-architecture.md),
[ADR-0002](../adr/0002-entity-id-over-artist-id.md),
[ADR-0003](../adr/0003-catalog-is-not-source-of-truth.md), and
[ADR-0004](../adr/0004-consensus-as-policy-not-blockchain.md). Those four
remain accepted.

ADR-0005 establishes the dedicated BIP340 root, the RGB identity lifecycle
anchored to Bitcoin, self-custodial wallet ownership, non-exclusive
human-readable names, separate entity identities for the types it names,
deterministic verification without a privileged validator set, and Pubky and
Nostr as replaceable discovery adapters.

## Normative specs

These contracts control implementations, schemas, examples, and diagrams.

| Document | Governs |
| --- | --- |
| [Cryptographic profile](../specs/cryptographic-profile.md) | Signature domains, tagged hashes, and network and key-purpose binding |
| [Entity schema](../specs/entity-schema.md) | EntityID, root key, RGB state, controllers, recovery, and revocation |
| [Claim schema](../specs/claim-schema.md) | Self-attested claims and competing names |
| [Attestation schema](../specs/attestation-schema.md) | Evidence issued by other identities |
| [Challenge schema](../specs/challenge-schema.md) | Disputes and evidence-level revocation |
| [Channel-control proof schema](../specs/control-proof-schema.md) | DNS, HTTPS, and social control evidence |
| [Discovery-binding schema](../specs/discovery-binding-schema.md) | Pubky and Nostr key bindings |
| [Music-object profiles](../specs/music-object-schema.md) | Event and album identities and manifests |
| [Proof-package schema](../specs/proof-package-schema.md) | Portable public history, content addressing, and the publisher signature |
| [Verification policy](../specs/verification-policy.md) | The required verification sequence and deterministic results |

## Master explanations

These explain the decisions and specs. They do not override them.

- [Vision and project rationale](00-vision.md) — goals, benefits, non-goals, and the social model.
- [Architecture](01-architecture.md) — layers, authority boundaries, and replaceable components.
- [Protocol kernel](02-protocol-kernel.md) — the minimum deterministic core.
- [Entity identity](03-entity-identity.md) — EntityID and custody.
- [Claims](04-claims.md) — claim semantics.
- [Roadmap](13-roadmap.md) — specification, regtest, wallet, discovery, and release gates.
- [Identity and discovery assessment](14-identity-discovery-assessment.md) — technology roles and feasibility gates.

Supporting explanations, including attestations, challenges, trust policy,
registries, and identifier notes, follow those masters and the specs.

## Derived material

Diagrams, public SVG illustrations, website copy, the guide, examples,
registry writeups, GatePass, SplitNight, payment proposals, verification-bond
proposals, and future wallet or node documentation must match the documents
above. They do not redefine the protocol.

## Update checklist

1. Name the rule and the highest document that already states it.
2. If that document is wrong, change it there: amend or supersede an ADR, or
   edit the normative spec. Then update every lower document that repeats the
   old rule.
3. If a diagram, website sentence, or example needs a rule that no ADR or spec
   states, add the rule upward first. Then draw or publish it.
4. When a signature rule changes, update the cryptographic profile and every
   schema whose signature domain, payload fields, or verification step is
   affected.
5. When an entity, recovery, or name rule changes, update ADR-0005 or the
   entity and claim specs first, then the entity and claims explanations.
6. After editing indexed files, reindex and validate the local Palimnex cache
   and run its evaluation fixture.
7. Leave both wordings in force only while a documented conflict is being
   fixed. The open conflict must cite the higher document that wins.
