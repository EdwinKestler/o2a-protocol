# 16 — Artist-authorized uses and direct payments

**Status:** proposed downstream application and adoption experiment,
2026-09-23. No live payment, USDt swap, or rights-contract implementation is
claimed. The [Bitcoin/RGB identity core](00-vision.md) remains usable without
this module; the payment module is still optional.

## Intended artist benefit

An artist could directly approve a specific use of its identity, brand
material, work reference, catalog, or live-event material and receive payment
when that authorization is fulfilled. The artist chooses the permitted uses,
price, authorized representative if any, and receiving wallet. A publisher
gets a verifiable statement describing the approval it purchased.

The signing key is an authorized O2A controller key. The receiving wallet uses
a separately bound payment key or endpoint. Root identity, operational
controller, RGB seal, Lightning, and on-chain spending keys MUST NOT be treated
as interchangeable.

Examples include a commercial event-discovery service paying to display an
artist-approved tour card, a sponsor purchasing an approved promotional
mention, or an application purchasing access to a maintained catalog feed.
Offers may also be free. Artist interest in this workflow is a hypothesis to
test, not established demand.

Here a **metalink** means a link paired with signed metadata: the EntityID,
referenced work/catalog/event, exact approved content or version, permitted
context, terms, and authorization reference. A public identifier alone is
neither a payment request nor a permission grant.

## Control the protocol can provide

The artist or authorized representative signs the terms and permission.
Participating applications can verify that signature and enforce access,
display an approval indicator, and retain evidence of consent. The grant must
describe the issuer's asserted authority over the material; control of an
EntityID does not establish authority over every associated work or event.
Co-owned material or delegated representation needs its own authorization
evidence.

This is an opt-in commercial relationship. O2A cannot force an unrelated
website to pay for mentioning a name, prevent copied public text, establish
exclusive rights in a name or title, or make ordinary links automatically
billable. What it can make inspectable is whether a particular use has a
signed approval, on which terms, and with which payment evidence.

## First example: paid, approved tour-date link

1. An artist publishes a signed offer for a specified tour card or catalog
   link. The offer identifies the exact material/version, allowed use,
   publisher or permitted class of publishers, duration, attribution,
   payment amount, and the artist-authorized recipient.
2. A publisher accepts the offer. The payment request is bound to the offer
   hash, request ID, publisher authorization, asset/network, recipient,
   amount, and expiry. A substituted payment endpoint fails verification.
3. The publisher pays the sat-denominated Lightning invoice. The application
   checks settlement using the selected payment adapter and preserves the
   association between invoice, offer, and order.
4. The publisher obtains an artist-signed grant referencing those same terms
   and the payment receipt. An automated issuer needs explicit, bounded
   delegation from the artist. Payment alone cannot authorize a broader use.
5. The publisher displays the approved link or material within the grant's
   scope. A verifier checks issuer authority, content, context, duration, and
   payment condition before presenting the use as artist-approved.

Illustrative offer: 100 sats for one publisher's approved tour-card placement
for 30 days. This is a test value, not a recommended price or earnings forecast.
Payment is for the agreed permission/service, not automatically for every
page impression or click. Per-use metering would require a separate design
that addresses replay, bots, and accounting disputes.

"Immediate remuneration" means the intended ability to receive payment at
the authorization step rather than await a later manual payout cycle. Actual
completion depends on the wallet, route, liquidity, fees, and application
availability. Artist receipts go to the authorized destination; choosing a
custodial wallet would introduce that wallet's custody model.

## Payment, authorization, and swaps are distinct

| Component | Proposed role | Evidence needed |
| --- | --- | --- |
| Bitcoin sats over Lightning | First candidate for small payments to an approved recipient. | Invoice/order binding, recipient authorization, settled payment result, and an associated permission grant. |
| Optional USDt payment | Let the artist quote or receive a supported USDt asset if the chosen wallet/network supports it. | Exact network and asset identifier, issuer authenticity, amount/units, recipient binding, and valid settlement evidence. A ticker alone is insufficient. |
| Client-controlled BTC/USDt swap | Explore payment in one asset with artist receipt in another through a compatible peer-to-peer exchange adapter. | Agreed quote and fees, both transfer legs, verified asset proofs, deadlines, and tested refund/recovery behavior. Mark conversion pending until both legs meet the adapter's completion rules. |
| RGB smart contract | Explore representing scoped digital-use rights and their issuance, transfer restrictions, expiry conditions, or consumption where a tested schema supports them. | Matching contract schema, authorization rules, client-side history/consignment, Bitcoin commitments, and an explicit mapping to the signed use terms. |

Client-side validation describes how RGB state is verified. It does not by
itself provide a swap counterparty, liquidity, atomic exchange, or delivery of
the purchased permission. A BTC/USDt swap on another network also does not
become an RGB swap merely because O2A uses RGB elsewhere. Test assets must be
labeled as such rather than presented as genuine USDt.

O2A already uses RGB for identity lifecycle. An additional rights contract is
useful only if the application needs enforceable state-transition rules beyond
a basic signed permission receipt. Any
real-world permission remains bound to the issuer's actual authority and the
explicit terms. An RGB transition is not proof that a publisher displayed a
mention, that a live event occurred, or that a rights dispute is resolved.

## Reliability and permission lifecycle

Payment received, grant delivered, and optional conversion completed must be
separate recorded outcomes. Persist the order before payment, process repeat
notifications idempotently, and allow a paid publisher to retrieve the same
grant after a restart. If payment succeeds but a grant cannot be delivered,
the application needs a documented recovery/refund path. Do not call the
payment-to-grant exchange atomic until its actual mechanism proves that.

Terms must define expiration, cancellation, and any refund conditions. A key
rotation or new price must not silently rewrite an existing paid grant.
Withdrawal of future offers and changes to issued grants are distinct actions;
record their authority, effects, and history explicitly. Public proof views
should expose only the agreed disclosure, not wallet secrets, private contract
data, or RGB consignments.

## Pilot and promotion gates

After the core's independent-verifier gate, use one artist, one publisher,
one test offer, and local test funds. Demonstrate valid authorization and
payment, then reject altered terms, an unauthorized issuer, an unpaid order,
a substituted recipient, and reuse outside the grant's scope. Recover from
duplicate payment callbacks and a crash between payment and grant delivery.

Measure net artist receipt, fees, payment-to-grant latency, failed delivery,
and recovery effort. Interview both participants about willingness to pay or
publish offers. Start with one paid grant; add revenue splits only when their
participants and allocation have explicit authorization. Test swaps and RGB
contracts independently before combining them with the grant flow.

## Technical references

Lightning invoices provide payment parameters and signatures; L402 provides
a pattern for selling access to HTTP services with Lightning payments.
These are candidates for the paid-access mechanism, not substitutes for
O2A's artist-signed permission. L402 credentials are bearer credentials, so
a grant restricted to one publisher still needs its own publisher binding.
[Lightning invoices](https://docs.lightning.engineering/the-lightning-network/payment-lifecycle/understanding-lightning-invoices),
[L402](https://docs.lightning.engineering/the-lightning-network/l402).

RGB documents client-side state validation and Bitcoin seal commitments.
Tether announced plans for USDt on RGB in August 2025; that announcement alone
does not verify a particular asset ID, wallet, or swap route for this project.
Promotion requires a current, tested integration.
[RGB client-side validation](https://docs.rgb.info/distributed-computing-concepts/client-side-validation),
[RGB commitments](https://docs.rgb.info/commitment-layer/commitment-schemes),
[Tether announcement](https://tether.io/news/tether-to-launch-usdt-on-rgb-expanding-native-bitcoin-stablecoin-support/).

The [sibling-project reference map](../codereference.md) identifies local swap
and RGB engineering knowledge. Those repositories remain independent; their
test assets and validation results do not prove this application's behavior.
