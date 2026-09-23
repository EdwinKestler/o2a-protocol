# 13 — Roadmap

## Phase 0 — Specification

- freeze terminology;
- define canonical schemas;
- define canonical serialization;
- define authorization transitions;
- define portable proof package;
- create deterministic test vectors;
- specify separate identity-controller and payment-key binding/revocation;
- specify competing human-name claims without first-claim priority;
- assess the proposed channel-control evidence profile: resource-specific,
  controller-bound challenges; signed observer records; independent
  recognition; issuer bootstrap; freshness and explicit failure reasons;
- specify event-manifest identity, canonical encoding, signer roles, and
  challenge/revocation behavior (the event manifest is an application evidence
  object, not a required sixth kernel primitive);
- specify proof retrieval and evaluation-context rules so independent verifiers
  operate on the same explicitly bounded evidence set and report unknown or
  missing evidence without claiming global completeness.

Gate: include vectors for duplicate names, controller rotation and compromise,
missing or conflicting event signatures, revoked evidence, expired payment
bindings, and unavailable optional discovery. Decisions about recovery without
the old key must state the trust policy and must not impersonate controller
authorization.

The [control-proof and bond assessment](17-control-proofs-and-verification-bonds.md)
adds proposed vectors for token replay, compromised or transferred channels,
related-party issuers, and unavailable providers. Define these as an evidence
profile above the kernel. No deposit is required to create an EntityID.

## Phase 1 — Local / regtest

Release sequence:

```text
0.0.1 Entity
0.0.2 Claim
0.0.3 Attestation
0.0.4 Challenge + Revocation
0.0.5 Policy Engine
0.1.0 Complete Hello World
```

Hello World: one artist and one venue create distinct EntityIDs; the artist
publishes a self-claim; both sign the same canonical event manifest through
separate evidence objects; a promoter may add independent evidence; a competing
name claim and challenge remain visible; two independent clients verify the
same portable package under the same named policy. RGB/Bitcoin anchoring is an
optional, separately verified evidence variant, not a prerequisite for a
valid identity result.

Exit condition: multiple independent verifier implementations produce identical
outputs from fixed vectors, including conflicts and missing optional services.

After core acceptance, test the control-proof profile using local DNS/HTTPS
fixtures and signed observations. Independent clients must reproduce results
from the retained package without querying live websites. Then optionally test
a refundable native-BTC deposit on regtest, with cooperative success and
unilateral timeout recovery. This is not a forfeiture or slashing mechanism.

## Phase 2 — Test network

- Artist Catalog;
- Venue Registry;
- Event Registry;
- shared test environment;
- adversarial identity collisions;
- registry destruction/rebuild tests;
- key rotation and revocation tests;
- evaluate Pubky/PKARR as an optional public-profile and discovery adapter on
  an isolated local testnet: publish/read, move homeserver, backup/restore,
  rebuild the registry, and verify proofs while the homeserver is unavailable;
- document the mapping between a Pubky key and stable O2A EntityID, including
  what happens when that Pubky key changes or is compromised.

Gate: Pubky integration must not make a public profile, homeserver, or Pubky key
the sole source of O2A verification or defeat EntityID controller rotation.
Do not publish private attestations or RGB consignments to public storage.

Optional application experiment, after Phase 1 acceptance: one artist and one
publisher exchange a signed permission for an approved metadata link and a
test Lightning payment. The grant identifies the allowed use, recipient,
content/version, terms, and payment. Test unpaid requests, altered terms,
duplicate callbacks, payment success followed by service failure, and grant
expiry. This measures a potential immediate artist benefit without making
payment a requirement for identity creation or ordinary evidence verification.
See [the paid-use proposal](16-artist-authorized-use-payments.md).

Separately evaluate Internet Identity/id.ai as an optional authentication or
credential adapter: confirm component licenses, origin and subject binding,
canister-signature verification, privacy, recovery, and offline proof limits.
Keep O2A controller authority and EntityID independent of the login provider.
Before any fraud-bond pilot, specify enforceable payout and refund paths,
adjudication authority, appeal deadlines, and economic/false-rejection metrics.
Public release of the website remains on hold as recorded in [WEBSITE.md](WEBSITE.md).

## Phase 3 — Public test release

- public API;
- CLI verifier;
- SDK;
- portable proof package exchange;
- external integrator testing;
- schema/policy compatibility matrix;
- optional Pubky discovery interoperability report and recovery limitations;
- portable event-manifest examples with matching independent signatures and
  explicit evidence provenance.

## Phase 4 — Mainnet v1

Initial public release should prioritize:

```text
Identity + Evidence + Verification
```

Do not require GatePass, SplitNight, or financial settlement for v1.

## Phase 5 — Applications

After protocol stability:

- GatePass;
- artist-authorized mentions, catalog/tour-date links, and content integrations
  with signed grants and sat payments, if the local pilot supports adoption;
- sponsorship/merchandise integrations;
- SplitNight;
- optional RGB/Bitcoin-backed event or settlement evidence, only with a
  version-matched client-side proof and independently checked anchor;
- payment-endpoint discovery after signed binding, expiration, and revocation
  semantics are specified; evaluate Paykit when its interface stabilizes;
- additional registry applications.

Potential extensions include RGB contracts for scoped digital-use rights and
optional client-controlled BTC/USDt swaps. Before promotion, verify the exact
asset/network and recipient, prove both swap legs and timeout recovery, and
separately demonstrate payment-to-grant delivery. RGB client-side validation
alone does not establish atomic exchange or grant-delivery fairness.

An RGB asset transfer proves the validated asset transition, not that a
performance happened, a person controls an artist name, or a payment was
received by an authorized counterparty. Application policy must check those
separate claims. Live USDt on RGB is not a v0.1 or v1 dependency.

## Phase 6 — Federation and reputation

Only after sufficient real evidence:

- federated registries;
- policy diversity;
- graph reputation and Sybil-resistance research, with empirical evidence
  before adopting scores, namespace leases, or automatic social recovery;
- optional cross-chain settlement adapters.
