# 13 — Roadmap

## Phase 0 — Freeze the Bitcoin-native specification

- freeze the EntityID encoding rooted in a dedicated BIP340 public key;
- freeze distinct tagged-hash signing domains and cross-domain rejection
  vectors for genesis, transitions, recovery, evidence, discovery bindings,
  proof packages, and music manifests;
- freeze separated root, controller, recovery, discovery, and payment key
  purposes and wallet derivation rules;
- define the RGB identity contract/schema for genesis, controller rotation,
  recovery-policy change, authorized recovery, custody transfer, and revocation;
- select and pin a compatible RGB stack and Bitcoin commitment method;
- define network, confirmation, reorg, seal, witness, and consignment rules;
- define canonical schemas and serialization for entities, claims,
  attestations, challenges, observations, EVENT manifests, and ALBUM manifests;
- define the public, content-addressed proof package, privacy boundary,
  publication locators, direct exchange, and offline verification inputs;
- define Pubky Ed25519 and Nostr key bindings to the O2A root;
- define DNS, HTTPS, and social channel-control challenges and signed
  observations;
- specify competing human-name claims without first-claim ownership;
- specify bounded evidence retrieval and explicit evaluation context;
- create deterministic positive and adversarial test vectors; and
- retain the accepted Apache-2.0 repository and reference wallet/node license.

Gate: the vectors cover distinct root/payment keys, duplicate names, invalid
BIP340 signatures, cross-domain signature replay, wrong Bitcoin network, wrong
RGB contract/schema/asset, forked or missing consignments, mismatched seals and
anchors, reorgs,
controller compromise, recovery, revocation, expired control proofs, Pubky and
Nostr rebinding, album/event custody, and unavailable discovery.

No production implementation code is accepted before this gate closes.

## Phase 1 — Deterministic core and Bitcoin regtest

Release sequence:

```text
0.0.1 BIP340 EntityID + canonical encoding
0.0.2 RGB identity genesis + Bitcoin anchor
0.0.3 Controller rotation + recovery + revocation
0.0.4 Claims + attestations + control observations
0.0.5 Policy engine + proof packages
0.0.6 EVENT + ALBUM identity profiles
0.1.0 Complete self-custodial Hello World
```

Hello World:

1. an artist, venue, promoter, event, and album use distinct root public keys;
2. their RGB identity histories are created and validated on Bitcoin regtest;
3. day-to-day controller keys sign claims while root and spending keys remain
   separated;
4. the artist publishes a DNS or social name-control proof;
5. a competing EntityID claims the same name and remains visible;
6. the event and album keys sign canonical content hashes;
7. counterparties issue separate attestations and a challenge; and
8. two independent verifier implementations return the same explained result
   from the same bounded package.

Exit condition: fixed vectors pass in independent implementations, including
invalid and incomplete cases. A catalog can be destroyed and rebuilt from RGB
consignments, Bitcoin proof data, and retained evidence packages.

## Phase 2 — Self-custodial wallet/node

- encrypted local seed and backup/recovery workflow;
- separate hardened derivation domains for root, controller, EVENT, ALBUM, and
  payment keys;
- controller delegation and rotation UX;
- RGB consignment, proof-package, and evidence storage;
- public proof-package export, content-addressed retrieval, hash validation,
  locator failover, and direct wallet-to-wallet exchange;
- full Bitcoin node mode;
- clearly labeled light mode with documented trust, privacy, and availability
  assumptions;
- online DNS/HTTPS/social collection producing signed observations;
- offline proof-package verification with no hidden network inputs;
- export/import between two independently developed wallets;
- reproducible source builds of the licensed open-source reference client; and
- fail-closed behavior for missing history, reorgs, stale observations, and
  unsupported schema versions.

Gate: losing an operational key is recoverable under a previously committed
policy without changing EntityID; losing required RGB data is detected rather
than reconstructed from a transaction ID; identity and payment keys never
cross purposes.

## Phase 3 — Public discovery and test network

- Artist, Venue, Promoter, Event, and Album registry projections;
- shared Bitcoin test network and adversarial identity collisions;
- Pubky/PKARR public-profile publication, independent read, homeserver
  migration, backup/restore, and key rebinding;
- optional Nostr signed-publication adapter and relay diversity tests;
- public control-proof collectors with SSRF, redirect, size, freshness, and
  stable-account-ID defenses;
- registry destruction and rebuild while discovery services are unavailable;
- explicit display of competing name claims, chronology, supporting evidence,
  and policy differences; and
- external wallet and verifier interoperability.

Gate: discovery data can disappear or move without changing verification of a
retained package. Pubky, Nostr, indexers, or APIs cannot replace the Bitcoin
root or RGB lifecycle. Private consignments and secrets never enter public
profile storage.

An optional adoption experiment can pair an artist-authorized grant with a
test Lightning payment. Payment, identity, permission delivery, and optional
asset conversion remain separate states. See
[the paid-use proposal](16-artist-authorized-use-payments.md).

The website's audience and deployment record live in
[WEBSITE.md](WEBSITE.md). A public site draft does not release the protocol.

## Phase 4 — Public beta and mainnet v1

- version-pinned wallet, CLI verifier, SDK, and proof-package format;
- public interoperability and recovery report;
- schema and policy compatibility matrix;
- mainnet fee, confirmation, reorg, backup, and incident procedures;
- independent security review of key separation and RGB validation;
- signed reproducible releases; and
- an explicit migration path for every supported pre-mainnet identity.

Initial mainnet release prioritizes:

```text
Bitcoin-rooted Identity + Evidence + Deterministic Verification
```

GatePass, SplitNight, rights contracts, swaps, and settlement integrations do
not block identity v1.

## Phase 5 — Applications

After protocol stability:

- GatePass;
- artist-authorized catalog, tour-date, and content grants with sats payments;
- sponsorship and merchandise integrations;
- SplitNight;
- additional RGB rights contracts for albums or permitted uses;
- payment-endpoint discovery with signed, expiring, revocable bindings; and
- optional client-controlled BTC/USDt conversion after independent test gates.

An RGB asset transition validates the supplied contract history against
Bitcoin. It does not prove that a performance occurred, that audio is authentic,
that a claimant owns a name, or that payment reached an authorized recipient.
Applications verify those as separate claims.

## Phase 6 — Federation and reputation research

Only after sufficient real evidence:

- federated and user-selected registry/index views;
- policy diversity and comparison;
- graph reputation and Sybil-resistance research;
- recovery-policy usability studies; and
- optional settlement adapters that do not weaken the Bitcoin identity root.

Human-readable global namespace leases remain outside the core unless a future
ADR defines their governance, transfer, dispute, and failure model.
