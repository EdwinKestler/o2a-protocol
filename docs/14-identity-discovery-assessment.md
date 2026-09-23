# 14 — Assessment of the original identity/discovery concept

**Status:** roadmap assessment, 2026-09-23. This records planned experiments;
it does not replace the accepted ADRs or finalize v0.1 wire formats.

## Conclusion

The strongest part of the two original notes is the separation between
creating a key and recognizing a real-world claim. O2A already models that
distinction with EntityID, self-claims, independent attestations, challenges,
and versioned policies. A jointly evidenced event makes the first scenario
more useful and gives the policy a concrete conflict to resolve. Pubky is a
promising *optional* discovery and public-profile adapter. RGB is valuable for
specific rights and payment evidence, but neither stack should be required to
verify a basic identity claim.

| Idea in the notes | Assessment and plan |
| --- | --- |
| Role-neutral identity with multiple roles | Keep EntityID and versioned role claims. Do not derive the permanent EntityID solely from a Pubky key: O2A requires controller rotation without changing EntityID. |
| Self-attestation and independent attestations | Keep. A valid signature proves the issuer made a statement; it does not prove the real-world name or event. |
| Competing names and challenges | Add explicit duplicate-name, first-claim, dispute, and resolution vectors. Names remain claims, never unique keys or automatic leases. |
| Mutually signed event | Add a canonical EventManifest and separate participant signatures/evidence to the local Hello World. Define who signed which exact bytes and distinguish planned/booked, occurred, and settled states. |
| Pubky public profiles and discovery | Test an adapter in Phase 2. Preserve portable claims and proof packages if a homeserver is unavailable or a key changes. Public profile JSON is mutable display data, not historical proof. |
| Payment and identity keys | Specify separate keys and purpose-bound, expiring, revocable bindings. A public payment address or endpoint does not itself prove recipient authorization. |
| RGB rights, settlement, GatePass, SplitNight | Keep downstream. Add a separately checked RGB/Bitcoin evidence example after base verification; do not make a transfer or Bitcoin anchor an automatic proof of performance or name ownership. |
| Global confidence formula, graph rank, namespace lease | Defer. The proposed weights are illustrative and can be gamed by coordinated fake identities. v0.1 uses explicit deterministic policy rules and explainable results. |
| Social key recovery | Research as a policy-mediated recognition transfer. Without an old-key signature or predefined recovery authority, third-party attestations cannot authorize a transition of the existing EntityID. |
| Extend RGBMVP as the product base | Keep O2A's specification and conformance vectors in this repository. Use RGBMVP as a read-only reference for adapters and regtest experiments; adopting its lab API or storage model would couple identity semantics to an asset lab before compatibility is established. |

## Required boundaries

The follow-up [control-proof and bond assessment](17-control-proofs-and-verification-bonds.md)
adds a proposed channel-control onboarding profile and evaluates Internet
Identity/id.ai as optional authentication references. Refundable deposits and
fraud penalties remain distinct downstream experiments; neither changes the
base evidence or controller-authority model.

The base O2A concepts remain Entity, Claim, Attestation, Challenge, Revocation,
and Policy. EventManifest is a domain evidence profile built above them. A
Pubky identifier may be bound to an EntityID by signed, versioned evidence; it
is not automatically the EntityID. A catalog document can reference evidence,
but deleting or moving that document must not alter verification from a
specified portable package. Portability alone cannot prove that no competing
claim or challenge exists elsewhere. RGB consignments and private financial material
stay out of public profile storage.

For an event, independently signed statements must refer to the *same*
canonical manifest ID and identify the asserted fact. An artist's booking
signature plus a venue's hosting signature can support a booking relationship;
they do not alone establish that the performance occurred. The policy must
state the required roles, issuer independence, evidence freshness, conflicts,
and evaluation context. An RGB contract or Bitcoin transaction may strengthen
a specifically verified economic claim, but it cannot serve as a real-world
oracle. If a required proof or issuer datum is missing, evaluation must
report incompleteness or an unverifiable result, never a silent positive result.

## Pubky feasibility gate

Pubky currently provides public-key discovery through PKARR and per-key
Homeserver storage, including public application paths. Its own documentation
says current Homeserver data is public and unencrypted, migration requires
moving data, and automatic mirroring is still planned. Its FAQ says key
rotation is not yet standardized. These facts make it a candidate for
discoverable *public* profile data, not a required O2A root or private proof
transport. A local testnet pilot must demonstrate publication, independent
read, homeserver migration and backup/restore, key-change handling, registry
rebuild, and offline verification from a portable package before an adapter is
promoted. Paykit is documented as work in progress, so its payment endpoint
format is a later interoperability question rather than a v0.1 dependency.

## Plan and acceptance evidence

1. **Phase 0 — formalize:** define event manifest bytes and IDs, identity-to-
   Pubky binding, payment-key binding, bounded evidence and conflict discovery,
   and recovery
   policy. Publish deterministic vectors for two claimants using the same
   stage name, mismatched event hashes, role spoofing, revoked signatures,
   compromised keys, and unavailable optional storage.
2. **Phase 1 — prove the core:** execute the artist/venue event package under
   two independent verifiers. They must report the same result and explain
   every accepted, rejected, conflicting, or missing evidence item. Add an
   optional regtest RGB proof only if a compatible stack and proof format are
   verified; keep the base vector independent of it.
3. **Phase 2 — prove discovery portability:** run Pubky locally, publish only
   public mutable profile data, migrate it to another homeserver, destroy and
   rebuild the O2A registry, and reproduce the previous protocol result with
   Pubky offline. Record the exact Pubky versions and interoperability gaps.
4. **Later — economic applications:** GatePass/SplitNight may consume O2A
   identities and attach verified RGB evidence. Specify asset IDs, networks,
   issuer authenticity, recipient binding, and proof availability before any
   real-asset settlement claim. Real USDt is outside the pilot.

This sequence preserves the accepted [modular dependency direction](../adr/0001-modular-protocol-architecture.md),
[stable EntityID](../adr/0002-entity-id-over-artist-id.md),
[rebuildable catalogs](../adr/0003-catalog-is-not-source-of-truth.md), and
[policy-based recognition](../adr/0004-consensus-as-policy-not-blockchain.md).

## Sources checked

- [Pubky protocol overview](https://pubky.org/explore/pubky-protocol/introduction/), [Homeserver storage and migration](https://pubky.org/explore/pubky-protocol/homeserver/), [developer guide/local testnet](https://pubky.org/explore/pubky-protocol/getting-started/), and [key-rotation FAQ](https://pubky.org/faq/).
- [Paykit status](https://docs.pubky.org/Explore/Technologies/Paykit).
- [RGB single-use seal/commitment model](https://docs.rgb.info/commitment-layer/commitment-schemes) and [client-side validation](https://docs.rgb.info/distributed-computing-concepts/client-side-validation).
- O2A's [code and sibling-project reference map](../codereference.md).
